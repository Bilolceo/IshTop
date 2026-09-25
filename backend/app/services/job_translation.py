"""
=============================================================================
JOB TRANSLATION — the listing in the site's other language
=============================================================================

The site switches between Uzbek and Russian, and the job text has to switch
with it. Imported listings get their `translations` from the ingest pipeline;
a job a company posts itself is translated here, in the background, right
after it is created or its text is edited.

  * The text the company wrote stays in the job's own columns. The other
    language goes into jobs.translations[<locale>]: a job written in Uzbek
    gets "ru", one written in Russian gets "uz".
  * Never fails the request and never blocks it: it runs after the response,
    and with no AI configured (or a bad answer) the job simply stays in one
    language — the site falls back to the text as written.
  * Contacts, numbers, URLs and brand names must survive verbatim; the prompt
    says so and the result is checked, and a translation that dropped a
    phone number or @handle is thrown away rather than published.
=============================================================================
"""

from __future__ import annotations

import json
import logging
import re
from uuid import UUID

logger = logging.getLogger(__name__)

TEXT_FIELDS = ("title", "description", "requirements", "responsibilities", "benefits")
_UZ_CYR = re.compile(r"[ўқғҳЎҚҒҲ]")
_UZ_WORDS = re.compile(r"(?<![а-яё])(ва|учун|билан|керак|ойлик|маош|бор|ёш|тажриба|иш|таклиф)(?![а-яё])", re.I)
_RU_WORDS = re.compile(r"(?<![а-яё])(и|в|на|для|по|от|требуется|ищем|опыт|работы|зарплата|график|мы)(?![а-яё])", re.I)
_CONTACT = re.compile(r"@[A-Za-z0-9_.]{4,}|[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}|\+?998[\d\s\-()]{9,}")


def detect_language(text: str) -> str:
    """'ru', 'uz' (Latin) or 'uz-cyr' — which way the job must be translated."""
    text = text or ""
    cyr = len(re.findall(r"[А-Яа-яЁёЎўҚқҒғҲҳ]", text))
    lat = len(re.findall(r"[A-Za-z]", text))
    if cyr <= lat:
        return "uz"
    if _UZ_CYR.search(text) or len(_UZ_WORDS.findall(text)) > len(_RU_WORDS.findall(text)):
        return "uz-cyr"
    return "ru"


def _prompt(fields: dict, target: str) -> str:
    lang = "Russian" if target == "ru" else "Uzbek in the Latin script (O'zbek lotin alifbosi, apostrophe as ')"
    return (
        f"Translate this job listing into {lang}. Return JSON with exactly the keys "
        f"{list(fields)}; strings stay strings and lists stay lists of the same length.\n"
        "Rules: keep phone numbers, emails, @handles, URLs, amounts, times and company/brand "
        "names exactly as written. Translate meaning, not word by word; keep the line breaks. "
        "Do not add or drop information.\n\n"
        + json.dumps(fields, ensure_ascii=False)
    )


def _contacts(text: str) -> set[str]:
    return {re.sub(r"[\s\-()]", "", m) for m in _CONTACT.findall(text or "")}


async def translate_fields(fields: dict, target: str) -> dict | None:
    """The same fields in `target`, or None when there is no safe translation."""
    from app.services.gemini_service import gemini_service

    if not gemini_service.is_available:
        return None
    try:
        raw = await gemini_service.generate(_prompt(fields, target), response_format="json")
        out = json.loads(raw)
    except Exception as exc:  # noqa: BLE001
        logger.warning("job translation failed: %s", exc)
        return None
    if not isinstance(out, dict):
        return None
    clean: dict = {}
    for k, v in fields.items():
        got = out.get(k)
        if isinstance(v, list):
            if not isinstance(got, list) or len(got) != len(v):
                got = v if not v else None
            if got is None:
                continue
            clean[k] = [str(x) for x in got]
        elif isinstance(got, str) and got.strip():
            clean[k] = got.strip()
    source = " ".join([fields.get("description") or ""] + list(fields.get("requirements") or []))
    target_text = " ".join([clean.get("description") or ""] + list(clean.get("requirements") or []))
    if not _contacts(source) <= _contacts(target_text):
        logger.warning("job translation dropped a contact; discarded")
        return None
    return clean or None


async def translate_job(job_id) -> None:
    """Background task: fill jobs.translations for one job. Owns its own session."""
    from app.database import SessionLocal
    from app.models.job import Job

    db = SessionLocal()
    try:
        job = db.get(Job, job_id if isinstance(job_id, UUID) else UUID(str(job_id)))
        if not job:
            return
        fields = {k: getattr(job, k) for k in TEXT_FIELDS if getattr(job, k)}
        written = detect_language(f"{job.title or ''}\n{job.description or ''}")
        target = "uz" if written in ("ru", "uz-cyr") else "ru"
        result = await translate_fields(fields, target)
        if not result:
            return
        tr = dict(job.translations or {})
        tr[target] = result
        job.translations = tr
        db.commit()
        logger.info("job %s translated to %s", job.id, target)
    except Exception as exc:  # noqa: BLE001
        logger.warning("translate_job(%s) failed: %s", job_id, exc)
        db.rollback()
    finally:
        db.close()
