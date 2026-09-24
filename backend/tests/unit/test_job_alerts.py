"""Telegram "new job" alerts — subscription rules, matching and the dispatcher.

The dispatcher's contract is what matters most and is easiest to break
quietly: a failed send must not advance the watermark (or the jobs are lost),
a blocked chat must be switched off (or it is retried forever), and a job
must be announced once, not once per alert that matched it.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from app.models.job_alert import JobAlert
from app.services import job_alert_service as svc


def _job(jid: str, minutes_ago: int, cid="it", city="toshkent", title="Python dasturchi"):
    return {
        "id": jid, "title": title, "company": "Acme", "salary_min": 8_000_000,
        "salary_max": 12_000_000, "salary_currency": "UZS", "location": "Toshkent",
        "cid": cid, "city_id": city,
        "created_at": datetime.now(timezone.utc) - timedelta(minutes=minutes_ago),
    }


def _uuid(n: int) -> str:
    return f"00000000-0000-0000-0000-{n:012d}"


# -----------------------------------------------------------------------------
# Subscriptions
# -----------------------------------------------------------------------------

class TestSubscribe:
    def test_create_then_exists(self, test_db):
        assert svc.subscribe(test_db, "1", "c", "it")[0] == "created"
        assert svc.subscribe(test_db, "1", "c", "it")[0] == "exists"

    def test_keyword_is_normalized(self, test_db):
        svc.subscribe(test_db, "1", "s", "  Flutter   DEV ")
        assert [a.value for a in svc.list_alerts(test_db, "1")] == ["flutter dev"]
        assert svc.subscribe(test_db, "1", "s", "flutter dev")[0] == "exists"

    def test_limit_per_chat(self, test_db):
        for i in range(svc.MAX_ALERTS_PER_CHAT):
            assert svc.subscribe(test_db, "1", "s", f"kw{i}")[0] == "created"
        assert svc.subscribe(test_db, "1", "s", "one more")[0] == "limit"
        # Another chat is unaffected.
        assert svc.subscribe(test_db, "2", "s", "one more")[0] == "created"

    def test_invalid_kind_or_empty_value(self, test_db):
        assert svc.subscribe(test_db, "1", "x", "it")[0] == "invalid"
        assert svc.subscribe(test_db, "1", "c", "  ")[0] == "invalid"

    def test_unsubscribe_is_scoped_to_the_chat(self, test_db):
        _, alert = svc.subscribe(test_db, "1", "c", "it")
        assert not svc.unsubscribe(test_db, "2", str(alert.id))  # someone else's
        assert not svc.unsubscribe(test_db, "1", "not-a-uuid")
        assert svc.unsubscribe(test_db, "1", str(alert.id))
        assert svc.list_alerts(test_db, "1") == []

    def test_resubscribing_restarts_the_watermark(self, test_db):
        _, alert = svc.subscribe(test_db, "1", "c", "it")
        alert.last_checked_at = datetime(2020, 1, 1, tzinfo=timezone.utc)
        test_db.commit()
        svc.unsubscribe(test_db, "1", str(alert.id))
        outcome, again = svc.subscribe(test_db, "1", "c", "it")
        assert outcome == "reactivated"
        # Not the 2020 backlog — only what is new from here on.
        assert svc._aware(again.last_checked_at) > datetime.now(timezone.utc) - timedelta(minutes=1)


# -----------------------------------------------------------------------------
# Matching
# -----------------------------------------------------------------------------

class TestCollectNewJobs:
    def _alert(self, kind, value, checked_minutes_ago=30):
        return JobAlert(chat_id="1", kind=kind, value=value, is_active=True,
                        last_checked_at=datetime.now(timezone.utc) - timedelta(minutes=checked_minutes_ago))

    def test_only_jobs_after_the_watermark(self):
        alert = self._alert("c", "it", checked_minutes_ago=30)
        found = svc.collect_new_jobs([alert], [_job("new", 5), _job("old", 60)])
        assert [j["id"] for j, _ in found] == ["new"]

    def test_one_job_announced_once_even_if_several_alerts_match(self):
        a1, a2 = self._alert("c", "it"), self._alert("t", "toshkent")
        found = svc.collect_new_jobs([a1, a2], [_job("j", 5)])
        assert len(found) == 1
        assert found[0][1] == [a1, a2]

    def test_city_and_category_must_match(self):
        alert = self._alert("t", "samarqand")
        assert svc.collect_new_jobs([alert], [_job("j", 5, city="toshkent")]) == []

    def test_keyword_uses_the_bot_search_rule(self):
        alert = self._alert("s", "python toshkent")
        assert len(svc.collect_new_jobs([alert], [_job("j", 5)])) == 1
        miss = self._alert("s", "flutter")
        assert svc.collect_new_jobs([miss], [_job("j", 5)]) == []

    def test_naive_datetimes_from_sqlite_compare(self):
        alert = self._alert("c", "it")
        alert.last_checked_at = alert.last_checked_at.replace(tzinfo=None)
        job = _job("j", 5)
        job["created_at"] = job["created_at"].replace(tzinfo=None)
        assert len(svc.collect_new_jobs([alert], [job])) == 1


class TestQuietHours:
    @pytest.mark.parametrize("utc_hour,quiet", [
        (17, False),  # 22:00 Tashkent
        (18, True),   # 23:00
        (21, True),   # 02:00
        (2, True),    # 07:00
        (3, False),   # 08:00
        (7, False),   # 12:00
    ])
    def test_tashkent_night(self, utc_hour, quiet):
        now = datetime(2026, 9, 24, utc_hour, 0, tzinfo=timezone.utc)
        assert svc.in_quiet_hours(now) is quiet


# -----------------------------------------------------------------------------
# Bot rendering
# -----------------------------------------------------------------------------

class TestBotButtons:
    def test_every_callback_fits_telegrams_64_bytes(self):
        from app.routers import telegram_bot as bot

        alert = JobAlert(chat_id="1", kind="s", value="бухгалтер ташкент", is_active=True,
                         last_checked_at=datetime.now(timezone.utc))
        found = [(_job(_uuid(i), i), [alert]) for i in range(8)]
        _, kb = bot._alert_digest(found)
        cbs = [b["callback_data"] for row in kb["inline_keyboard"] for b in row]
        # The longest subscribe button: a 20-char Cyrillic query.
        cbs.append(bot._alert_btn("s", "ж" * 20)["callback_data"])
        cbs.append(f"alx:{_uuid(1)}")
        assert all(len(cb.encode()) <= 64 for cb in cbs), cbs

    def test_digest_caps_the_list_and_says_how_many_more(self):
        from app.routers import telegram_bot as bot

        alert = JobAlert(chat_id="1", kind="c", value="it", is_active=True,
                         last_checked_at=datetime.now(timezone.utc))
        text, kb = bot._alert_digest([(_job(_uuid(i), i), [alert]) for i in range(8)])
        assert "8 ta yangi vakansiya" in text
        assert "yana 3 ta" in text
        assert len(kb["inline_keyboard"][0]) == svc.DIGEST_JOBS_SHOWN

    def test_site_deep_link_payloads(self):
        from app.routers import telegram_bot as bot

        assert bot._parse_alert_payload("alert_c_it") == ("c", "it")
        assert bot._parse_alert_payload("alert_t_toshkent") == ("t", "toshkent")
        assert bot._parse_alert_payload("alert_c_nonsense") is None
        assert bot._parse_alert_payload("alert_s_python") is None


# -----------------------------------------------------------------------------
# Dispatcher
# -----------------------------------------------------------------------------

class TestDispatch:
    @pytest.fixture
    def wired(self, test_db, monkeypatch):
        """Catalog with one fresh IT job and one old one; records every send."""
        from app.routers import telegram_bot as bot

        jobs = {_uuid(1): _job(_uuid(1), 2), _uuid(2): _job(_uuid(2), 600)}
        monkeypatch.setattr(bot, "_load_catalog", lambda force=False: {"jobs": jobs})
        monkeypatch.setattr(svc, "in_quiet_hours", lambda now=None: False)
        sent: list = []
        outcome = {"value": "ok"}

        async def fake_post(token, chat_id, text, kb):
            sent.append((chat_id, text))
            return outcome["value"]

        monkeypatch.setattr(svc, "_post", fake_post)

        _, alert = svc.subscribe(test_db, "42", "c", "it")
        alert.last_checked_at = datetime.now(timezone.utc) - timedelta(minutes=30)
        test_db.commit()
        return {"db": test_db, "alert": alert, "sent": sent, "outcome": outcome}

    async def test_sends_new_jobs_once_and_advances(self, wired):
        stats = await svc.dispatch_job_alerts(wired["db"], "t")
        assert stats["sent"] == 1 and stats["jobs"] == 1
        assert len(wired["sent"]) == 1
        assert wired["alert"].sent_count == 1
        # The next pass has nothing new to say.
        await svc.dispatch_job_alerts(wired["db"], "t")
        assert len(wired["sent"]) == 1

    async def test_failed_send_keeps_the_watermark(self, wired):
        before = wired["alert"].last_checked_at
        wired["outcome"]["value"] = "failed"
        await svc.dispatch_job_alerts(wired["db"], "t")
        assert wired["alert"].last_checked_at == before
        wired["outcome"]["value"] = "ok"
        await svc.dispatch_job_alerts(wired["db"], "t")
        assert len(wired["sent"]) == 2  # retried, not lost

    async def test_blocked_chat_is_switched_off(self, wired):
        wired["outcome"]["value"] = "blocked"
        stats = await svc.dispatch_job_alerts(wired["db"], "t")
        assert stats["blocked"] == 1
        assert wired["alert"].is_active is False

    async def test_quiet_hours_send_nothing(self, wired, monkeypatch):
        monkeypatch.setattr(svc, "in_quiet_hours", lambda now=None: True)
        before = wired["alert"].last_checked_at
        await svc.dispatch_job_alerts(wired["db"], "t")
        assert wired["sent"] == []
        assert wired["alert"].last_checked_at == before
