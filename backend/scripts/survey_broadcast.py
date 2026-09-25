"""
=============================================================================
SURVEY BROADCAST
=============================================================================

Send the problem-validation survey to the Telegram chats that already asked
us for job alerts — the largest audience IshTop can reach directly.

This writes to real people, so it does nothing by default:

    python scripts/survey_broadcast.py                 # dry run, prints the plan
    python scripts/survey_broadcast.py --send          # actually sends

Telegram allows ~30 messages/second to different chats; we stay far under it.
A chat that has blocked the bot returns 403 — that is counted, not retried,
and never aborts the run.

Each recipient is messaged once: the run appends chat ids to a state file and
skips anything already in it, so re-running after a failure resumes instead of
double-messaging.
=============================================================================
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import httpx  # noqa: E402

from app.database import SessionLocal  # noqa: E402
from app.models import JobAlert  # noqa: E402

SITE_URL = "https://ishtopuz.uz"
SURVEY_URL = f"{SITE_URL}/sorovnoma?src=bot-broadcast"
STATE_FILE = Path(__file__).with_name(".survey_broadcast_sent.json")
DELAY_SECONDS = 0.2  # 5 messages/second

TEXT = (
    "🗳 <b>2 daqiqalik so'rovnoma</b>\n\n"
    "Siz IshTop botidan ish qidirasiz. Bir savolimiz bor: "
    "ish topishda sizga eng ko'p nima xalaqit beryapti?\n\n"
    "7 ta savol, taxminan 2 daqiqa. Anonim — ism, telefon, email so'ralmaydi.\n"
    "Javoblaringizga qarab botga va saytga nima qo'shishni hal qilamiz."
)


def recipients() -> list[str]:
    """Distinct chats with an active alert, oldest first."""
    db = SessionLocal()
    try:
        rows = (
            db.query(JobAlert.chat_id)
            .filter(JobAlert.is_active == True)  # noqa: E712
            .distinct()
            .all()
        )
        return sorted({r[0] for r in rows})
    finally:
        db.close()


def load_sent() -> set[str]:
    if STATE_FILE.exists():
        return set(json.loads(STATE_FILE.read_text()))
    return set()


def save_sent(sent: set[str]) -> None:
    STATE_FILE.write_text(json.dumps(sorted(sent)))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--send", action="store_true", help="actually send (default: dry run)")
    ap.add_argument("--limit", type=int, default=0, help="send to at most N chats")
    args = ap.parse_args()

    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    chats = recipients()
    sent = load_sent()
    todo = [c for c in chats if c not in sent]
    if args.limit:
        todo = todo[: args.limit]

    print(f"chats with an active alert : {len(chats)}")
    print(f"already messaged            : {len(sent)}")
    print(f"would message now           : {len(todo)}")
    print(f"link                        : {SURVEY_URL}")

    if not args.send:
        print("\nDRY RUN — nothing sent. Re-run with --send to deliver.")
        return 0
    if not token:
        print("\nTELEGRAM_BOT_TOKEN is not set; refusing to send.")
        return 1

    ok = blocked = failed = 0
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    keyboard = {"inline_keyboard": [[{"text": "📝 So'rovnomani to'ldirish", "url": SURVEY_URL}]]}

    with httpx.Client(timeout=20) as client:
        for chat_id in todo:
            try:
                res = client.post(url, json={
                    "chat_id": chat_id,
                    "text": TEXT,
                    "parse_mode": "HTML",
                    "reply_markup": keyboard,
                    "disable_web_page_preview": True,
                })
                if res.status_code == 200:
                    ok += 1
                    sent.add(chat_id)
                elif res.status_code == 403:
                    blocked += 1
                    sent.add(chat_id)  # blocked us; never retry
                else:
                    failed += 1
                    print(f"  {chat_id}: HTTP {res.status_code} {res.text[:120]}")
            except Exception as exc:  # network hiccup — leave it for the next run
                failed += 1
                print(f"  {chat_id}: {type(exc).__name__} {exc}")
            if (ok + blocked + failed) % 25 == 0:
                save_sent(sent)
            time.sleep(DELAY_SECONDS)

    save_sent(sent)
    print(f"\ndelivered {ok} · blocked {blocked} · failed {failed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
