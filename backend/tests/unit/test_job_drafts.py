"""Saving a job as a draft (2026-09-25 audit).

The draft button's payload was rejected (422) — and had it been accepted, the
API created every job live, so a "draft" would have gone public on save.
"""
from datetime import datetime, timezone
from uuid import UUID

DESC = ("Bizning jamoamiz FastAPI va PostgreSQL bilan ishlaydigan tajribali backend "
        "dasturchini qidirmoqda.")


def _payload(**over):
    p = {"title": "Buxgalter", "location": "Toshkent", "job_type": "full_time",
         "experience_level": "junior", "description": DESC, "requirements": ["Excel"],
         "benefits": ["Tushlik"], "salary_min": 4000000, "salary_max": 6000000,
         "salary_currency": "UZS", "is_salary_visible": True}
    p.update(over)
    return p


def test_a_draft_is_saved_as_draft_and_stays_private(client, company_token):
    h = {"Authorization": f"Bearer {company_token}"}
    r = client.post("/api/v1/jobs", json=_payload(save_as_draft=True), headers=h)
    assert r.status_code == 201, r.text
    assert r.json()["status"] == "draft"
    public = client.get("/api/v1/jobs").json()
    assert not any(j["id"] == r.json()["id"] for j in public.get("jobs", []))


def test_without_the_flag_a_job_still_goes_live(client, company_token):
    h = {"Authorization": f"Bearer {company_token}"}
    r = client.post("/api/v1/jobs", json=_payload(title="Kassir"), headers=h)
    assert r.status_code == 201 and r.json()["status"] == "active"


def test_publishing_a_draft_dates_it_now(client, company_token, test_db):
    from app.models.job import Job

    h = {"Authorization": f"Bearer {company_token}"}
    jid = client.post("/api/v1/jobs", json=_payload(title="Omborchi", save_as_draft=True), headers=h).json()["id"]
    job = test_db.get(Job, UUID(jid))
    job.created_at = datetime(2026, 1, 1, tzinfo=timezone.utc)
    test_db.commit()
    r = client.post(f"/api/v1/jobs/{jid}/publish", headers=h)
    assert r.status_code == 200 and r.json()["status"] == "active"
    # Otherwise it sorts as a January listing and job alerts never announce it.
    assert r.json()["created_at"][:4] == str(datetime.now(timezone.utc).year)
    assert not r.json()["created_at"].startswith("2026-01-01")


def test_the_old_draft_payload_shape_is_what_failed(client, company_token):
    # Documents the bug: requirements as an object, benefits as a string.
    h = {"Authorization": f"Bearer {company_token}"}
    r = client.post("/api/v1/jobs", json=_payload(requirements={"text": "x"}, benefits="<p>y</p>"), headers=h)
    assert r.status_code == 422
