"""
=============================================================================
SURVEY ROUTES
=============================================================================

POST /surveys/{key}           anyone (signed in or not) submits an answer
GET  /surveys/{key}/status    has the signed-in user already answered?
GET  /surveys/{key}/summary   admin: per-option counts + free-text answers

Open to anonymous users on purpose — the survey is shared in university
chats, where most readers have no account. Abuse is kept down by a hidden
honeypot field, a per-IP rate limit, and one response per signed-in user.
=============================================================================
"""

import hashlib
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.config import settings
from app.core.dependencies import get_db, get_optional_current_user, require_admin_permission
from app.core.rate_limiter import rate_limiter
from app.core.surveys import SOURCE_MAX_LEN, get_survey, summarize, validate_answers
from app.models import SurveyResponse, User

router = APIRouter()

SUBMITS_PER_IP_PER_HOUR = 5


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
