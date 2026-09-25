"""
=============================================================================
ADMIN TRACTION METRICS
=============================================================================

GET /admin/metrics/traction — the numbers we quote to investors and grant
committees, computed the same way every time.

The rule that makes them worth quoting: staff, test and demo accounts are
left out. When this was written 12 of the 20 applications on the platform
came from such accounts; counting them would have more than doubled
"traction". An account counts as internal when its email contains test,
example, demo or ishtop (the last covers staff and the telegram-import
account that owns imported jobs).

The data is small (hundreds of rows), so weekly buckets are built in Python
from plain timestamps — portable across SQLite (tests) and PostgreSQL.
=============================================================================
"""

from collections import Counter
from datetime import datetime, timedelta, timezone
from typing import Dict, List

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, require_admin_permission
from app.models import Application, Job, JobAlert, Resume, SurveyResponse, User, UserRole
from app.models.job import visible_job_filters

router = APIRouter()

INTERNAL_EMAIL_MARKERS = ("test", "example", "demo", "ishtop")
# Statuses that mean an employer looked at the application and acted.
EMPLOYER_RESPONDED = {"reviewing", "shortlisted", "interview", "rejected", "accepted", "hired"}
HIRED = {"accepted", "hired"}
# A withdrawn application is left out of the response-rate denominator: the
# employer was never given the chance to answer it. Sixteen of ours were
# closed by a maintenance write in September 2026, not by the candidates, and
# counting those as unanswered would understate a rate nobody was asked for.
# app/api/v1/routes/applications.py uses the same rule for the company side.
WITHDRAWN = "withdrawn"


def internal_user_filter():
    email = func.lower(User.email)
    return or_(*[email.like(f"%{m}%") for m in INTERNAL_EMAIL_MARKERS])


def _week_start(dt: datetime) -> str:
    d = dt.date() - timedelta(days=dt.weekday())
    return d.isoformat()


def _weekly(stamps: List[datetime], weeks: int, now: datetime) -> List[Dict]:
    buckets = Counter(_week_start(s) for s in stamps if s)
    first = now - timedelta(weeks=weeks - 1)
    out = []
    for i in range(weeks):
        wk = _week_start(first + timedelta(weeks=i))
        out.append({"week": wk, "value": buckets.get(wk, 0)})
    return out


def _status(value) -> str:
    return (value.value if hasattr(value, "value") else str(value or "")).lower()


@router.get("/traction")
def traction(
    weeks: int = Query(12, ge=4, le=52),
    admin: User = Depends(require_admin_permission("admin.dashboard.read")),
    db: Session = Depends(get_db),
):
    now = datetime.now(timezone.utc)
    real = ~internal_user_filter()

    students = (
        db.query(User.id, User.created_at, User.last_login, User.telegram_chat_id)
        .filter(User.role == UserRole.STUDENT, User.is_deleted == False, real)  # noqa: E712
        .all()
    )
    student_ids = {s.id for s in students}

    with_resume = {
        r[0] for r in db.query(Resume.user_id).filter(Resume.is_deleted == False).distinct().all()  # noqa: E712
    } & student_ids

    apps = (
        db.query(Application.user_id, Application.status, Application.applied_at)
        .join(User, User.id == Application.user_id)
        .filter(Application.is_deleted == False, real)  # noqa: E712
        .all()
    )
    applicants = {a.user_id for a in apps}
    statuses = Counter(_status(a.status) for a in apps)
    responded = sum(c for s, c in statuses.items() if s in EMPLOYER_RESPONDED)
    hired = sum(c for s, c in statuses.items() if s in HIRED)
    answerable = sum(c for s, c in statuses.items() if s != WITHDRAWN)

    companies = (
        db.query(func.count(User.id))
        .filter(User.role == UserRole.COMPANY, User.is_deleted == False, real)  # noqa: E712
        .scalar()
    )
    live_jobs = db.query(Job.company_id).filter(*visible_job_filters()).all()
    internal_ids = {r[0] for r in db.query(User.id).filter(internal_user_filter()).all()}
    live_by_company = sum(1 for j in live_jobs if j.company_id not in internal_ids)

    cutoff_30 = now - timedelta(days=30)
    cutoff_7 = now - timedelta(days=7)

    def _aware(dt):
        return dt if dt is None or dt.tzinfo else dt.replace(tzinfo=timezone.utc)

    active_30 = sum(1 for s in students if s.last_login and _aware(s.last_login) >= cutoff_30)
    active_7 = sum(1 for s in students if s.last_login and _aware(s.last_login) >= cutoff_7)

    alerts_active = db.query(func.count(JobAlert.id)).filter(JobAlert.is_active == True).scalar()  # noqa: E712
    alert_chats = (
        db.query(func.count(func.distinct(JobAlert.chat_id))).filter(JobAlert.is_active == True).scalar()  # noqa: E712
    )
    surveys = db.query(func.count(SurveyResponse.id)).scalar()

    # Proof of the filter: a reviewer who asks "how do we know the numbers are
    # clean" gets the size of what was removed, not just a claim that it was.
    excluded_students = (
        db.query(func.count(User.id))
        .filter(User.role == UserRole.STUDENT, User.is_deleted == False, internal_user_filter())  # noqa: E712
        .scalar()
    )
    excluded_apps = (
        db.query(func.count(Application.id))
        .join(User, User.id == Application.user_id)
        .filter(Application.is_deleted == False, internal_user_filter())  # noqa: E712
        .scalar()
    )

    n = len(students)

    def pct(a, b):
        return round(100 * a / b, 1) if b else 0.0

    return {
        "success": True,
        "data": {
            "generated_at": now.isoformat(),
            "excluded_markers": list(INTERNAL_EMAIL_MARKERS),
            "excluded": {
                "students": excluded_students,
                "applications": excluded_apps,
            },
            "students": {
                "total": n,
                "active_7d": active_7,
                "active_30d": active_30,
                "telegram_linked": sum(1 for s in students if s.telegram_chat_id),
            },
            "funnel": [
                {"step": "signed_up", "value": n, "pct": 100.0 if n else 0.0},
                {"step": "resume", "value": len(with_resume), "pct": pct(len(with_resume), n)},
                {"step": "applied", "value": len(applicants), "pct": pct(len(applicants), n)},
                {"step": "employer_responded", "value": responded, "pct": pct(responded, answerable)},
                {"step": "hired", "value": hired, "pct": pct(hired, answerable)},
            ],
            "applications": {
                "total": len(apps),
                "answerable": answerable,
                "withdrawn": statuses.get(WITHDRAWN, 0),
                "by_status": dict(statuses),
            },
            "employers": {
                "companies": companies,
                "live_jobs": len(live_jobs),
                "live_jobs_posted_by_companies": live_by_company,
                "live_jobs_imported": len(live_jobs) - live_by_company,
            },
            "engagement": {
                "job_alerts_active": alerts_active,
                "job_alert_chats": alert_chats,
                "survey_responses": surveys,
            },
            "weekly": {
                "signups": _weekly([_aware(s.created_at) for s in students], weeks, now),
                "applications": _weekly([_aware(a.applied_at) for a in apps], weeks, now),
            },
        },
    }
