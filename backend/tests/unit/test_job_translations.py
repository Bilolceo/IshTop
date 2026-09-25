"""jobs.translations is returned as-is so the client can switch the text with the site language."""


def _payload(**over):
    p = {"title": "Buxgalter", "location": "Toshkent", "job_type": "full_time", "experience_level": "junior",
         "description": "Bizning jamoamiz tajribali buxgalterni qidirmoqda, hisobot va 1C bilan ishlash.",
         "requirements": ["Excel"], "benefits": [], "salary_currency": "UZS"}
    p.update(over)
    return p


def test_translations_come_back_on_list_and_detail(client, company_token, test_db):
    from uuid import UUID
    from app.models.job import Job

    h = {"Authorization": f"Bearer {company_token}"}
    jid = client.post("/api/v1/jobs", json=_payload(), headers=h).json()["id"]
    job = test_db.get(Job, UUID(jid))
    job.translations = {"ru": {"title": "Бухгалтер", "description": "Русский текст"}}
    test_db.commit()
    detail = client.get(f"/api/v1/jobs/{jid}").json()
    assert detail["translations"]["ru"]["title"] == "Бухгалтер"
    listed = client.get("/api/v1/jobs").json()
    item = next(j for j in (listed.get("data") or listed)["jobs"] if j["id"] == jid)
    assert item["translations"]["ru"]["description"] == "Русский текст"


def test_no_translations_is_null(client, company_token):
    h = {"Authorization": f"Bearer {company_token}"}
    jid = client.post("/api/v1/jobs", json=_payload(title="Kassir"), headers=h).json()["id"]
    assert client.get(f"/api/v1/jobs/{jid}").json()["translations"] is None
