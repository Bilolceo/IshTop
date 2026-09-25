"""Problem-validation survey: validation, abuse guards, admin summary, traction metrics."""

from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest

from app.core.surveys import SURVEYS, summarize, validate_answers
from app.models import Application, Resume, SurveyResponse, User, UserRole

KEY = "student-2026"
GOOD = {
    "status": "course_3_4",
    "searched": "yes_searching",
    "pains": ["experience_required", "no_reply"],
    "channels": ["telegram", "hh"],
    "pay": "no",
    "comment": "  tajriba so'rashadi  ",
}


# --- validation ---------------------------------------------------------------

def test_validate_cleans_and_drops_unknown_keys():
    out = validate_answers(SURVEYS[KEY], {**GOOD, "evil": {"x": 1}})
    assert "evil" not in out
    assert out["comment"] == "tajriba so'rashadi"
    assert "time_to_job" not in out  # optional, not given


@pytest.mark.parametrize("patch,err", [
    ({"status": None}, "status: required"),
    ({"status": "phd"}, "status: unknown option"),
    ({"pains": ["scams", "hacked"]}, "pains: unknown option"),
    ({"pains": ["scams", "resume", "no_reply", "other"]}, "pains: too many options"),
    ({"channels": "telegram"}, "channels: must be a list"),
    ({"comment": 5}, "comment: must be text"),
])
def test_validate_rejects(patch, err):
    with pytest.raises(ValueError, match=err):
        validate_answers(SURVEYS[KEY], {**GOOD, **patch})


def test_validate_dedupes_multi():
    out = validate_answers(SURVEYS[KEY], {**GOOD, "pains": ["scams", "scams"]})
    assert out["pains"] == ["scams"]


def test_summarize_multi_pct_is_of_respondents():
    rows = [{"pains": ["scams", "resume"]}, {"pains": ["scams"]}]
    q = next(q for q in summarize(SURVEYS[KEY], rows)["questions"] if q["id"] == "pains")
    scams = next(o for o in q["options"] if o["id"] == "scams")
    assert (scams["count"], scams["pct"], q["answered"]) == (2, 100.0, 2)


# --- endpoints ----------------------------------------------------------------

def test_anonymous_submit_is_stored(client, test_db):
    r = client.post(f"/api/v1/surveys/{KEY}", json={"answers": GOOD, "source": "tatu-chat"})
    assert r.status_code == 201, r.text
    row = test_db.query(SurveyResponse).one()
    assert row.user_id is None and row.source == "tatu-chat"
    assert row.ip_hash and len(row.ip_hash) == 32


def test_unknown_survey_404(client):
    assert client.post("/api/v1/surveys/nope", json={"answers": GOOD}).status_code == 404


def test_invalid_answers_422(client, test_db):
    r = client.post(f"/api/v1/surveys/{KEY}", json={"answers": {**GOOD, "pay": "million"}})
    assert r.status_code == 422
    assert test_db.query(SurveyResponse).count() == 0


def test_honeypot_pretends_success_but_stores_nothing(client, test_db):
    r = client.post(f"/api/v1/surveys/{KEY}", json={"answers": GOOD, "website": "http://spam"})
    assert r.status_code == 201
    assert test_db.query(SurveyResponse).count() == 0


def test_rate_limited_per_ip(client, test_db, monkeypatch):
    from app.config import settings
    monkeypatch.setattr(settings, "RATE_LIMIT_ENABLED", True)
    for _ in range(5):
        assert client.post(f"/api/v1/surveys/{KEY}", json={"answers": GOOD}).status_code == 201
    assert client.post(f"/api/v1/surveys/{KEY}", json={"answers": GOOD}).status_code == 429
    # another visitor behind the same proxy is not blocked
    r = client.post(f"/api/v1/surveys/{KEY}", json={"answers": GOOD},
                    headers={"X-Forwarded-For": "10.1.2.3"})
    assert r.status_code == 201


def test_signed_in_student_answers_once(client, test_db, student_headers, test_student):
    s = client.get(f"/api/v1/surveys/{KEY}/status", headers=student_headers).json()
    assert s["data"]["answered"] is False
    assert client.post(f"/api/v1/surveys/{KEY}", json={"answers": GOOD}, headers=student_headers).status_code == 201
    again = client.post(f"/api/v1/surveys/{KEY}", json={"answers": GOOD}, headers=student_headers)
    assert again.json().get("already") is True
    assert test_db.query(SurveyResponse).count() == 1
    assert test_db.query(SurveyResponse).one().user_id == test_student.id
    s = client.get(f"/api/v1/surveys/{KEY}/status", headers=student_headers).json()
    assert s["data"]["answered"] is True


def test_summary_is_admin_only(client, test_db, student_headers, super_admin_token):
    client.post(f"/api/v1/surveys/{KEY}", json={"answers": GOOD, "source": "a"})
    client.post(f"/api/v1/surveys/{KEY}", json={"answers": {**GOOD, "pay": "k10_20"}})
    assert client.get(f"/api/v1/surveys/{KEY}/summary").status_code in (401, 403)
    assert client.get(f"/api/v1/surveys/{KEY}/summary", headers=student_headers).status_code == 403
    r = client.get(f"/api/v1/surveys/{KEY}/summary",
                   headers={"Authorization": f"Bearer {super_admin_token}"})
    assert r.status_code == 200, r.text
    d = r.json()["data"]
    assert d["total"] == 2 and d["sources"] == {"a": 1, "direct": 1}
    pay = next(q for q in d["questions"] if q["id"] == "pay")
    assert {o["id"]: o["count"] for o in pay["options"]}["k10_20"] == 1
    comment = next(q for q in d["questions"] if q["id"] == "comment")
    assert comment["texts"] == ["tajriba so'rashadi"] * 2


# --- traction -----------------------------------------------------------------

def _user(db, email, role=UserRole.STUDENT, **kw):
    u = User(id=uuid4(), email=email, full_name="X", role=role, is_active_account=True, **kw)
    u.set_password("Password123!")
    db.add(u)
    db.commit()
    return u


def test_traction_excludes_internal_accounts(client, test_db, test_student, test_job,
                                             test_resume, test_application, super_admin_token):
    # fixtures above are all @example.com → internal, must not count
    real = _user(test_db, "ali@gmail.com", last_login=datetime.now(timezone.utc) - timedelta(days=2))
    _user(test_db, "vali@mail.ru")
    _user(test_db, "demo.user@gmail.com")
    test_db.add(Resume(id=uuid4(), user_id=real.id, title="R", content={}))
    test_db.add(Application(id=uuid4(), user_id=real.id, job_id=test_job.id, status="interview"))
    test_db.commit()

    r = client.get("/api/v1/admin/metrics/traction",
                   headers={"Authorization": f"Bearer {super_admin_token}"})
    assert r.status_code == 200, r.text
    d = r.json()["data"]
    assert d["students"]["total"] == 2
    assert d["students"]["active_7d"] == 1
    funnel = {f["step"]: f["value"] for f in d["funnel"]}
    assert funnel == {"signed_up": 2, "resume": 1, "applied": 1, "employer_responded": 1, "hired": 0}
    assert d["applications"]["total"] == 1
    # the fixture company is internal, so its live job counts as not company-posted
    assert d["employers"]["companies"] == 0
    assert sum(w["value"] for w in d["weekly"]["signups"]) == 2


def test_traction_requires_admin(client, student_headers):
    assert client.get("/api/v1/admin/metrics/traction", headers=student_headers).status_code == 403
