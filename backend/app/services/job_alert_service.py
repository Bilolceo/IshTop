"""
=============================================================================
JOB ALERTS — "yangi ish chiqsa xabar ber"
=============================================================================

A Telegram chat subscribes to a soha, a city or a keyword from inside the bot;
every few minutes the dispatcher looks for listings created since each alert
was last checked and sends each chat ONE message covering all of its alerts.

Matching runs against the bot's own catalog snapshot (`_load_catalog`), not a
separate query, so an alert can only announce a job the bot can then open —
same visibility rule, same soha/city classification, same keyword search.

Failure rules:
  * a send that fails for a transient reason leaves the watermark alone, so
    the next run retries the same jobs instead of silently dropping them;
  * a chat that blocked the bot (Telegram 403) has its alerts switched off —
    retrying a blocked chat forever only burns the rate limit;
  * at night (Tashkent time) nothing is sent and nothing is advanced, so the
    overnight jobs arrive together in the morning.
=============================================================================
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta, timezone

import httpx
from sqlalchemy.orm import Session

from app.config import settings
from app.models.job_alert import JobAlert

logger = logging.getLogger(__name__)

MAX_ALERTS_PER_CHAT = 10
DIGEST_JOBS_SHOWN = 5
KINDS = ("c", "t", "s")
_TASHKENT = timezone(timedelta(hours=5))  # no DST in Uzbekistan


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _aware(dt: datetime | None) -> datetime | None:
    # SQLite hands back naive datetimes; Postgres aware ones. Compare as UTC.
    if dt is None:
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


# -----------------------------------------------------------------------------
# Subscriptions
# -----------------------------------------------------------------------------

def normalize_value(kind: str, value: str) -> str:
    value = (value or "").strip()
    if kind == "s":
        value = " ".join(value.lower().replace("’", "'").split())
    return value[:40]


def subscribe(db: Session, chat_id: str, kind: str, value: str,
              user_id=None) -> tuple[str, JobAlert | None]:
    """Returns (outcome, alert); outcome is created | exists | reactivated | limit | invalid."""
    value = normalize_value(kind, value)
    if kind not in KINDS or not value:
        return "invalid", None
    chat_id = str(chat_id)

    existing = (
        db.query(JobAlert)
        .filter(JobAlert.chat_id == chat_id, JobAlert.kind == kind, JobAlert.value == value)
        .first()
    )
    if existing and existing.is_active:
        return "exists", existing

    active = (
        db.query(JobAlert)
        .filter(JobAlert.chat_id == chat_id, JobAlert.is_active.is_(True))
        .count()
    )
    if active >= MAX_ALERTS_PER_CHAT:
        return "limit", None

    # The watermark starts now: an alert announces what is NEW, not the
    # backlog the person was just looking at.
    now = _utcnow()
    if existing:
        existing.is_active = True
        existing.last_checked_at = now
        if user_id and not existing.user_id:
            existing.user_id = user_id
        db.commit()
        return "reactivated", existing

    alert = JobAlert(chat_id=chat_id, kind=kind, value=value, user_id=user_id,
                     is_active=True, last_checked_at=now, sent_count=0)
    db.add(alert)
    db.commit()
    return "created", alert


def list_alerts(db: Session, chat_id: str) -> list[JobAlert]:
    return (
        db.query(JobAlert)
        .filter(JobAlert.chat_id == str(chat_id), JobAlert.is_active.is_(True))
        .order_by(JobAlert.created_at.asc())
        .all()
    )


def unsubscribe(db: Session, chat_id: str, alert_id: str) -> bool:
    """Switch one alert off. Scoped to the chat, so a forged id cannot touch another's."""
    import uuid

    try:
        aid = uuid.UUID(str(alert_id))
    except ValueError:
        return False
    alert = (
        db.query(JobAlert)
        .filter(JobAlert.id == aid, JobAlert.chat_id == str(chat_id))
        .first()
    )
    if not alert or not alert.is_active:
        return False
    alert.is_active = False
    db.commit()
    return True


# -----------------------------------------------------------------------------
# Matching
# -----------------------------------------------------------------------------

def alert_matches(kind: str, value: str, job: dict) -> bool:
    if kind == "c":
        return job.get("cid") == value
    if kind == "t":
        return job.get("city_id") == value
    if kind == "s":
        from app.routers.telegram_bot import _matches_tokens, _search_tokens

        toks = _search_tokens(value)
        return bool(toks) and _matches_tokens(job, toks)
    return False


def collect_new_jobs(alerts: list[JobAlert], jobs: list[dict]) -> list[tuple[dict, list[JobAlert]]]:
    """Jobs newer than the alert that matched them, deduplicated across one chat's alerts.

    Keeps the catalog's order (newest first) and remembers which alerts matched
    each job, so the message can say why it was sent.
    """
    out: list[tuple[dict, list[JobAlert]]] = []
    for job in jobs:
        created = _aware(job.get("created_at"))
        if created is None:
            continue
        hits = [
            a for a in alerts
            if created > _aware(a.last_checked_at) and alert_matches(a.kind, a.value, job)
        ]
        if hits:
            out.append((job, hits))
    return out


def in_quiet_hours(now: datetime | None = None) -> bool:
    start = settings.JOB_ALERTS_QUIET_START_HOUR
    end = settings.JOB_ALERTS_QUIET_END_HOUR
    if start == end:
        return False
    hour = (now or _utcnow()).astimezone(_TASHKENT).hour
    if start > end:  # the window wraps midnight, e.g. 23 → 8
        return hour >= start or hour < end
    return start <= hour < end


# -----------------------------------------------------------------------------
# Dispatch
# -----------------------------------------------------------------------------

async def _post(token: str, chat_id: str, text: str, reply_markup: dict) -> str:
    """Send one message; returns ok | blocked | rejected | failed.

    failed   — transient (network, 429, 5xx): retry the same jobs next run.
    rejected — Telegram refused THIS message (400): resending it can only fail
               the same way, so the jobs are dropped rather than retried
               every ten minutes forever.
    """
    url = f"{settings.TELEGRAM_API_BASE_URL}/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
        "reply_markup": reply_markup,
    }
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            res = await client.post(url, json=payload)
    except Exception as exc:  # noqa: BLE001
        logger.warning("job alert send failed (chat=%s): %s", chat_id, exc)
        return "failed"
    if res.status_code == 200:
        return "ok"
    # 403: the person blocked the bot or deleted the chat. 400 "chat not
    # found" is the same thing for our purposes.
    body = res.text[:200]
    if res.status_code == 403 or "chat not found" in body:
        return "blocked"
    logger.warning("job alert send rejected (chat=%s, %s): %s", chat_id, res.status_code, body)
    if res.status_code == 400:
        return "rejected"
    return "failed"


async def dispatch_job_alerts(db: Session, token: str) -> dict:
    """One pass: every chat with news gets one message. Returns counters for the log."""
    from starlette.concurrency import run_in_threadpool

    from app.routers import telegram_bot as bot

    stats = {"chats": 0, "sent": 0, "blocked": 0, "failed": 0, "rejected": 0, "jobs": 0}
    if in_quiet_hours():
        return stats

    alerts = db.query(JobAlert).filter(JobAlert.is_active.is_(True)).all()
    if not alerts:
        return stats

    catalog = await run_in_threadpool(bot._load_catalog, True)
    jobs = list(catalog["jobs"].values())
    stamps = [_aware(j.get("created_at")) for j in jobs if j.get("created_at")]
    if not stamps:
        return stats
    newest = max(stamps)

    by_chat: dict[str, list[JobAlert]] = {}
    for a in alerts:
        by_chat.setdefault(a.chat_id, []).append(a)

    now = _utcnow()
    for chat_id, chat_alerts in by_chat.items():
        # One chat's failure must not cost every chat after it its alerts.
        try:
            await _dispatch_chat(db, token, bot, chat_id, chat_alerts, jobs, newest, now, stats)
        except Exception as exc:  # noqa: BLE001
            db.rollback()
            stats["failed"] += 1
            logger.exception("job alerts for chat %s failed: %s", chat_id, exc)

    return stats


async def _dispatch_chat(db: Session, token: str, bot, chat_id: str, chat_alerts: list,
                         jobs: list, newest: datetime, now: datetime, stats: dict) -> None:
    found = collect_new_jobs(chat_alerts, jobs)
    if found:
        stats["chats"] += 1
        text, kb = bot._alert_digest(found)
        outcome = await _post(token, chat_id, text, kb)
        if outcome == "blocked":
            stats["blocked"] += 1
            for a in chat_alerts:
                a.is_active = False
            db.commit()
            return
        if outcome == "failed":
            stats["failed"] += 1
            return  # watermark untouched: retried next run
        if outcome == "rejected":
            stats["rejected"] += 1  # watermark advances below: not retried
        else:
            stats["sent"] += 1
            stats["jobs"] += len(found)
            for a in chat_alerts:
                n = sum(1 for _, hits in found if a in hits)
                if n:
                    a.sent_count = (a.sent_count or 0) + n
                    a.last_sent_at = now
        await asyncio.sleep(0.05)  # far under Telegram's 30 msg/s

    # Advance to the newest listing seen, not to "now": a listing stamped
    # just before "now" but committed after this snapshot would otherwise
    # fall behind the watermark and never be announced.
    for a in chat_alerts:
        if newest > _aware(a.last_checked_at):
            a.last_checked_at = newest
    db.commit()
