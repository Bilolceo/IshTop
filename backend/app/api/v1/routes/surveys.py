"""
=============================================================================
SURVEY ROUTES
=============================================================================

POST /surveys/{key}             anyone (signed in or not) submits an answer
POST /surveys/{key}/interview   volunteer a contact for a follow-up interview
GET  /surveys/{key}/status      has the signed-in user already answered?
GET  /surveys/{key}/summary     admin: per-option counts + free-text answers
GET  /surveys/{key}/export      admin: every answer as CSV
GET  /surveys/{key}/leads       admin: people who agreed to an interview

Open to anonymous users on purpose — the survey is shared in university
chats, where most readers have no account. Abuse is kept down by a hidden
honeypot field, a per-IP rate limit, and one response per signed-in user.
=============================================================================
"""

import csv
import hashlib
import io
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.config import settings
from app.core.dependencies import get_db, get_optional_current_user, require_admin_permission
from app.core.rate_limiter import rate_limiter
from app.core.surveys import SOURCE_MAX_LEN, get_survey, summarize, validate_answers
from app.models import InterviewLead, SurveyResponse, User

router = APIRouter()

SUBMITS_PER_IP_PER_HOUR = 5
LEADS_PER_IP_PER_HOUR = 5


class InterviewVolunteer(BaseModel):
    contact: str = Field(max_length=120)
    source: Optional[str] = Field(None, max_length=200)


class SurveySubmit(BaseModel):
    answers: Dict[str, Any]
    source: Optional[str] = Field(None, max_length=200)
    # Honeypot: hidden in the form, so only bots fill it.
    website: Optional[str] = None


def _client_ip(request: Request) -> str:
    # Behind Railway's proxy request.client is the proxy; the first
    # X-Forwarded-For hop is the visitor. Spoofable, which is fine for a
    # soft limit on an anonymous survey.
    fwd = (request.headers.get("x-forwarded-for") or "").split(",")[0].strip()
    return fwd or (request.client.host if request.client else "unknown")


def _ip_hash(ip: str) -> str:
    return hashlib.sha256(f"{settings.SECRET_KEY}:survey:{ip}".encode()).hexdigest()[:32]


def _survey_or_404(key: str) -> Dict[str, Any]:
    survey = get_survey(key)
    if not survey:
        raise HTTPException(status_code=404, detail="Survey not found")
    return survey


@router.post("/{key}", status_code=status.HTTP_201_CREATED)
def submit_survey(
    key: str,
    body: SurveySubmit,
    request: Request,
    user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
):
    survey = _survey_or_404(key)

    if body.website:
        # Pretend success so the bot learns nothing.
        return {"success": True}

    ip = _client_ip(request)
    if settings.RATE_LIMIT_ENABLED:
        allowed, retry_after = rate_limiter.check_rate_limit(
            identifier=f"survey:{key}:{ip}", max_requests=SUBMITS_PER_IP_PER_HOUR, window_seconds=3600
        )
        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many submissions",
                headers={"Retry-After": str(retry_after)},
            )

    try:
        answers = validate_answers(survey, body.answers)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    if user is not None:
        already = (
            db.query(SurveyResponse.id)
            .filter(SurveyResponse.survey_key == key, SurveyResponse.user_id == user.id)
            .first()
        )
        if already:
            return {"success": True, "already": True}

    source = (body.source or "").strip()[:SOURCE_MAX_LEN] or None
    db.add(SurveyResponse(
        survey_key=key,
        user_id=user.id if user else None,
        answers=answers,
        source=source,
        ip_hash=_ip_hash(ip),
    ))
    db.commit()
    return {"success": True}


@router.get("/{key}/status")
def survey_status(
    key: str,
    user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
):
    _survey_or_404(key)
    answered = False
    if user is not None:
        answered = (
            db.query(SurveyResponse.id)
            .filter(SurveyResponse.survey_key == key, SurveyResponse.user_id == user.id)
            .first()
            is not None
        )
    return {"success": True, "data": {"answered": answered}}


@router.get("/{key}/summary")
def survey_summary(
    key: str,
    source: Optional[str] = Query(None, max_length=SOURCE_MAX_LEN),
    admin: User = Depends(require_admin_permission("admin.dashboard.read")),
    db: Session = Depends(get_db),
):
    survey = _survey_or_404(key)
    q = db.query(SurveyResponse).filter(SurveyResponse.survey_key == key)
    if source:
        q = q.filter(SurveyResponse.source == source)
    rows = q.order_by(SurveyResponse.created_at.desc()).all()

    sources: Dict[str, int] = {}
    ips = set()
    for r in rows:
        sources[r.source or "direct"] = sources.get(r.source or "direct", 0) + 1
        if r.ip_hash:
            ips.add(r.ip_hash)

    data = summarize(survey, [r.answers or {} for r in rows])
    data.update({
        "signed_in": sum(1 for r in rows if r.user_id),
        "distinct_ips": len(ips),
        "sources": sources,
        "first_at": rows[-1].created_at.isoformat() if rows else None,
        "last_at": rows[0].created_at.isoformat() if rows else None,
    })
    return {"success": True, "data": data}


@router.post("/{key}/interview", status_code=status.HTTP_201_CREATED)
def volunteer_for_interview(
    key: str,
    body: InterviewVolunteer,
    request: Request,
    db: Session = Depends(get_db),
):
    """Store a contact from someone willing to be interviewed.

    Written to its own table with no link back to the survey answers, so the
    anonymity the form promises still holds for the people who leave a contact.
    """
    _survey_or_404(key)

    ip = _client_ip(request)
    if settings.RATE_LIMIT_ENABLED:
        allowed, retry_after = rate_limiter.check_rate_limit(
            identifier=f"lead:{key}:{ip}", max_requests=LEADS_PER_IP_PER_HOUR, window_seconds=3600
        )
        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many submissions",
                headers={"Retry-After": str(retry_after)},
            )

    # Validated after stripping: "   " is a blank contact, not a 3-character one.
    contact = body.contact.strip()
    if len(contact) < 3:
        raise HTTPException(status_code=422, detail="contact: too short")

    source = (body.source or "").strip()[:SOURCE_MAX_LEN] or None
    db.add(InterviewLead(survey_key=key, contact=contact[:120], source=source))
    db.commit()
    return {"success": True}


@router.get("/{key}/leads")
def list_leads(
    key: str,
    admin: User = Depends(require_admin_permission("admin.dashboard.read")),
    db: Session = Depends(get_db),
):
    _survey_or_404(key)
    rows = (
        db.query(InterviewLead)
        .filter(InterviewLead.survey_key == key)
        .order_by(InterviewLead.created_at.desc())
        .all()
    )
    return {
        "success": True,
        "data": {
            "total": len(rows),
            "leads": [
                {
                    "id": str(r.id),
                    "contact": r.contact,
                    "source": r.source,
                    "status": r.status,
                    "created_at": r.created_at.isoformat() if r.created_at else None,
                }
                for r in rows
            ],
        },
    }


@router.get("/{key}/export")
def export_responses(
    key: str,
    admin: User = Depends(require_admin_permission("admin.dashboard.read")),
    db: Session = Depends(get_db),
):
    """Every answer as CSV — one row per response, one column per question.

    Multi-select answers are joined with "|" so a spreadsheet can split them;
    no user id or ip hash is exported, only the answers and where they came from.
    """
    survey = _survey_or_404(key)
    qids = [q["id"] for q in survey["questions"]]

    rows = (
        db.query(SurveyResponse)
        .filter(SurveyResponse.survey_key == key)
        .order_by(SurveyResponse.created_at.asc())
        .all()
    )

    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["created_at", "source", "signed_in", *qids])
    for r in rows:
        answers = r.answers or {}
        writer.writerow([
            r.created_at.isoformat() if r.created_at else "",
            r.source or "",
            "yes" if r.user_id else "no",
            *[
                "|".join(answers.get(q)) if isinstance(answers.get(q), list) else (answers.get(q) or "")
                for q in qids
            ],
        ])

    buf.seek(0)
    return StreamingResponse(
        iter([buf.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{key}-responses.csv"'},
    )
