"""services/job_translation — company-posted jobs get the other site language."""
import json

import pytest

from app.services import job_translation as jt


class FakeGemini:
    def __init__(self, answer, available=True):
        self.answer, self.is_available, self.prompts = answer, available, []

    async def generate(self, prompt, response_format="text"):
        self.prompts.append(prompt)
        return self.answer if isinstance(self.answer, str) else json.dumps(self.answer, ensure_ascii=False)


@pytest.fixture
def gemini(monkeypatch):
    import app.services.gemini_service as gs

    def install(answer, available=True):
        fake = FakeGemini(answer, available)
        monkeypatch.setattr(gs, "gemini_service", fake)
        return fake
    return install


FIELDS = {"title": "Sotuvchi", "description": "Sotuvchi kerak. Aloqa: @hr_shop, +998 90 111 22 33",
          "requirements": ["Tajriba", "Rus tili"]}


def test_detect_language():
    assert jt.detect_language("Sotuvchi kerak") == "uz"
    assert jt.detect_language("Требуется продавец в магазин") == "ru"
    assert jt.detect_language("Сотувчи керак, маош ойига") == "uz-cyr"


async def test_good_translation_is_kept(gemini):
    gemini({"title": "Продавец", "description": "Нужен продавец. Связь: @hr_shop, +998 90 111 22 33",
            "requirements": ["Опыт", "Русский язык"]})
    out = await jt.translate_fields(FIELDS, "ru")
    assert out["title"] == "Продавец" and out["requirements"] == ["Опыт", "Русский язык"]


async def test_a_translation_that_drops_a_contact_is_discarded(gemini):
    gemini({"title": "Продавец", "description": "Нужен продавец.", "requirements": ["Опыт", "Русский язык"]})
    assert await jt.translate_fields(FIELDS, "ru") is None


async def test_list_length_mismatch_drops_that_field(gemini):
    gemini({"title": "Продавец", "description": "Нужен продавец. Связь: @hr_shop, +998 90 111 22 33",
            "requirements": ["Опыт"]})
    out = await jt.translate_fields(FIELDS, "ru")
    assert "requirements" not in out and out["title"] == "Продавец"


async def test_no_ai_or_bad_json_means_no_translation(gemini):
    gemini({}, available=False)
    assert await jt.translate_fields(FIELDS, "ru") is None
    gemini("not json")
    assert await jt.translate_fields(FIELDS, "ru") is None


def _payload(**over):
    p = {"title": "Buxgalter", "location": "Toshkent", "job_type": "full_time", "experience_level": "junior",
         "description": "Bizning jamoamiz tajribali buxgalterni qidirmoqda, hisobot va 1C bilan ishlash.",
         "requirements": ["Excel"], "benefits": [], "salary_currency": "UZS"}
    p.update(over)
    return p


def test_create_and_text_edit_schedule_translation(client, company_token, monkeypatch):
    calls = []

    async def fake_translate(job_id):
        calls.append(str(job_id))

    monkeypatch.setattr(jt, "translate_job", fake_translate)
    h = {"Authorization": f"Bearer {company_token}"}
    jid = client.post("/api/v1/jobs", json=_payload(), headers=h).json()["id"]
    assert calls == [jid]
    client.put(f"/api/v1/jobs/{jid}", json={"salary_min": 5000000}, headers=h)
    assert calls == [jid]                      # salary only: no retranslation
    client.put(f"/api/v1/jobs/{jid}", json={"title": "Bosh buxgalter"}, headers=h)
    assert calls == [jid, jid]                 # text changed: redo it
