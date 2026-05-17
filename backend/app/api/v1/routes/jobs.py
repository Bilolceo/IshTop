"""
=============================================================================
JOB ENDPOINTS
=============================================================================

Handles job listing CRUD, search, and AI-powered matching.

ENDPOINTS:
    GET    /                      - Public job listings with filters/search
    GET    /{job_id}              - Get job details (increments view count)
    POST   /                      - Create job posting [Company only]
    PUT    /{job_id}              - Update job [Company only]
    DELETE /{job_id}              - Remove job [Company only]
    GET    /{job_id}/applications - Get applications for job [Company only]
    POST   /match                 - 🔥 AI-powered job matching
    GET    /my                    - List company's own jobs
    POST   /{job_id}/publish      - Publish job
    POST   /{job_id}/close        - Close job

=============================================================================
AUTHOR: IshTop Team
VERSION: 1.0.0
=============================================================================
"""

# =============================================================================
# IMPORTS
# =============================================================================

import logging
import time
import re
from typing import Optional, List, Dict, Any
from uuid import UUID
from enum import Enum

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, or_, and_, desc, asc
from pydantic import BaseModel, Field

from app.core.dependencies import (
    get_db,
    get_current_active_user,
    get_current_company,
    get_optional_current_user,
    PaginationParams
)
from app.models import User, Job, JobStatus, UserRole, Resume, Application, ApplicationStatus, SavedJob
from app.schemas.job import (
    JobCreate,
    JobUpdate,
    JobResponse,
    JobListResponse,
    CompanyInfo,
)
from app.schemas.application import (
    ApplicationResponse,
    ApplicationListResponse,
    JobSummary,
    ResumeSummary,
    ApplicantSummary,
)
from app.schemas.auth import MessageResponse
from app.config import settings
from app.services import job_matching

# =============================================================================
# LOGGING
# =============================================================================

logger = logging.getLogger(__name__)

# =============================================================================
# ROUTER
# =============================================================================

router = APIRouter()


# =============================================================================
# ENUMS AND MODELS
# =============================================================================

class JobSortBy(str, Enum):
    """Sort options for job listings."""
    CREATED_AT = "created_at"
    SALARY = "salary"
    RELEVANCE = "relevance"
    VIEWS = "views"
    APPLICATIONS = "applications"


class SortOrder(str, Enum):
    """Sort order."""
    ASC = "asc"
    DESC = "desc"


class JobMatchRequest(BaseModel):
    """Request for AI job matching."""
    
    resume_id: str = Field(
        ...,
        description="UUID of the resume to match against"
    )
    
    location_preference: Optional[str] = Field(
        None,
        description="Preferred location (optional)"
    )
    
    remote_only: bool = Field(
        default=False,
        description="Only match remote jobs"
    )
    
    min_salary: Optional[int] = Field(
        None,
        description="Minimum salary requirement (in cents)"
    )
    
    experience_levels: Optional[List[str]] = Field(
        None,
        description="Preferred experience levels"
    )
    
    limit: int = Field(
        default=10,
        ge=1,
        le=50,
        description="Maximum number of matches to return"
    )


class JobMatchScore(BaseModel):
    """Job match with score."""
    
    job: JobResponse
    match_score: float = Field(..., description="Match score (0-100)")
    match_reasons: List[str] = Field(default_factory=list)
    skill_matches: List[str] = Field(default_factory=list)
    missing_skills: List[str] = Field(default_factory=list)


class JobMatchResponse(BaseModel):
    """Response from AI job matching."""
    
    success: bool
    message: str
    total_jobs_analyzed: int
    matches: List[JobMatchScore]
    resume_skills: List[str] = Field(default_factory=list)
    processing_time_seconds: Optional[float] = None


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def job_to_response(job: Job, include_company: bool = True) -> JobResponse:
    """Convert Job model to JobResponse."""

    def _as_list(value: Any) -> List[str]:
        if value is None:
            return []
        if isinstance(value, list):
            return [str(item) for item in value if item is not None]
        if isinstance(value, dict):
            for key in ("skills", "requirements", "items", "values"):
                nested = value.get(key)
                if isinstance(nested, list):
                    return [str(item) for item in nested if item is not None]
            return [str(item) for item in value.values() if item is not None]
        return [str(value)]

    company_info = None
    if include_company and job.company:
        company_info = CompanyInfo(
            id=str(job.company.id),
            name=job.company.company_name or job.company.full_name,
            logo=job.company.avatar_url,
            location=job.company.location,
            website=job.company.company_website,
        )
    
    return JobResponse(
        id=str(job.id),
        company_id=str(job.company_id),
        company=company_info,
        title=job.title,
        description=job.description,
        requirements=_as_list(job.requirements),
        responsibilities=_as_list(job.responsibilities),
        benefits=_as_list(job.benefits),
        salary_range=job.salary_range_display,
        salary_min=job.salary_min,
        salary_max=job.salary_max,
        salary_currency=job.salary_currency,
        is_salary_visible=job.is_salary_visible,
        location=job.location,
        is_remote_allowed=job.is_remote_allowed,
        job_type=job.job_type,
        experience_level=job.experience_level,
        status=job.status,
        views_count=job.views_count,
        applications_count=job.applications_count,
        is_featured=job.is_featured,
        is_active=job.is_active,
        is_expired=job.is_expired,
        created_at=job.created_at,
        updated_at=job.updated_at,
        expires_at=job.expires_at,
    )


def application_to_response(
    app: Application,
    include_resume: bool = False,
    include_applicant: bool = False,
    include_notes: bool = False
) -> ApplicationResponse:
    """Convert Application model to ApplicationResponse."""
    
    resume_summary = None
    if include_resume and app.resume:
        resume_summary = ResumeSummary(
            id=str(app.resume.id),
            title=app.resume.title,
            ats_score=app.resume.ats_score,
        )
    
    applicant_summary = None
    if include_applicant and app.user:
        applicant_summary = ApplicantSummary(
            id=str(app.user.id),
            full_name=app.user.full_name,
            email=app.user.email,
            avatar_url=app.user.avatar_url,
            location=app.user.location,
        )
    
    return ApplicationResponse(
        id=str(app.id),
        job_id=str(app.job_id),
        user_id=str(app.user_id),
        resume_id=str(app.resume_id) if app.resume_id else None,
        status=app.status,
        cover_letter=app.cover_letter,
        match_score=app.match_score,
        applied_at=app.applied_at,
        reviewed_at=app.reviewed_at,
        interview_at=app.interview_at,
        decided_at=app.decided_at,
        days_since_applied=app.days_since_applied,
        is_in_progress=app.is_in_progress,
        resume=resume_summary,
        applicant=applicant_summary,
        notes=app.notes if include_notes else None,
    )


# =============================================================================
# ENDPOINTS
# =============================================================================

@router.get("")
@router.get(
    "/",
    response_model=JobListResponse,
    summary="Search and filter jobs",
    description="""
    Get public job listings with powerful filtering and search.
    
    **Filters:**
    - `location`: Filter by location (partial match)
    - `job_type`: full_time, part_time, remote, hybrid, contract, internship
    - `experience_level`: intern, junior, mid, senior, lead, executive
    - `salary_min`: Minimum salary (in cents)
    - `salary_max`: Maximum salary (in cents)
    - `is_remote`: Filter for remote-friendly jobs only
    - `company_id`: Filter by specific company
    
    **Search:**
    - `query`: Search in title and description
    
    **Sorting:**
    - `sort_by`: created_at, salary, views, applications
    - `sort_order`: asc, desc
    
    **Pagination:**
    - `page`: Page number (default: 1)
    - `page_size`: Items per page (default: 20, max: 100)
    """
)
async def search_jobs(
    # Pagination
    pagination: PaginationParams = Depends(),
    
    # Search
    query: Optional[str] = Query(
        None,
        description="Search in title and description",
        min_length=2,
        max_length=100
    ),
    
    # Filters
    location: Optional[str] = Query(
        None,
        description="Filter by location (partial match)"
    ),
    job_type: Optional[str] = Query(
        None,
        description="Filter by job type"
    ),
    experience_level: Optional[str] = Query(
        None,
        description="Filter by experience level"
    ),
    salary_min: Optional[int] = Query(
        None,
        ge=0,
        description="Minimum salary (in cents)"
    ),
    salary_max: Optional[int] = Query(
        None,
        ge=0,
        description="Maximum salary (in cents)"
    ),
    is_remote: Optional[bool] = Query(
        None,
        description="Filter for remote jobs only"
    ),
    company_id: Optional[str] = Query(
        None,
        description="Filter by company ID"
    ),
    
    # Sorting
    sort_by: JobSortBy = Query(
        JobSortBy.CREATED_AT,
        description="Sort by field"
    ),
    sort_order: SortOrder = Query(
        SortOrder.DESC,
        description="Sort order"
    ),
    
    # Authentication (optional)
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    """Search and filter public job listings."""
    
    logger.info(f"Job search: query='{query}', location='{location}', type='{job_type}'")
    
    # Base query: only active, non-deleted jobs
    q = db.query(Job).filter(
        Job.is_deleted == False,
        Job.status == JobStatus.ACTIVE.value
    )
    
    # =========================================================================
    # APPLY SEARCH
    # =========================================================================
    
    if query:
        search_term = f"%{query}%"
        q = q.filter(
            or_(
                Job.title.ilike(search_term),
                Job.description.ilike(search_term)
            )
        )
    
    # =========================================================================
    # APPLY FILTERS
    # =========================================================================
    
    if location:
        q = q.filter(Job.location.ilike(f"%{location}%"))
    
    if job_type:
        q = q.filter(Job.job_type == job_type)
    
    if experience_level:
        q = q.filter(Job.experience_level == experience_level)
    
    if salary_min is not None:
        q = q.filter(
            or_(
                Job.salary_min >= salary_min,
                Job.salary_min.is_(None)  # Include jobs without salary info
            )
        )
    
    if salary_max is not None:
        q = q.filter(
            or_(
                Job.salary_max <= salary_max,
                Job.salary_max.is_(None)
            )
        )
    
    if is_remote is True:
        q = q.filter(
            or_(
                Job.is_remote_allowed == True,
                Job.job_type == "remote"
            )
        )
    
    if company_id:
        try:
            q = q.filter(Job.company_id == UUID(company_id))
        except ValueError:
            pass  # Invalid UUID, ignore filter
    
    # =========================================================================
    # GET TOTAL COUNT (before pagination)
    # =========================================================================
    
    total = q.count()
    
    # =========================================================================
    # APPLY SORTING
    # =========================================================================
    
    # Always show featured jobs first
    q = q.order_by(Job.is_featured.desc())
    
    # Then apply user's sort preference
    if sort_by == JobSortBy.CREATED_AT:
        order_col = Job.created_at
    elif sort_by == JobSortBy.SALARY:
        order_col = Job.salary_max  # Sort by max salary
    elif sort_by == JobSortBy.VIEWS:
        order_col = Job.views_count
    elif sort_by == JobSortBy.APPLICATIONS:
        order_col = Job.applications_count
    else:
        order_col = Job.created_at  # Default
    
    if sort_order == SortOrder.DESC:
        q = q.order_by(desc(order_col))
    else:
        q = q.order_by(asc(order_col))
    
    # =========================================================================
    # APPLY PAGINATION
    # =========================================================================
    
    jobs = q.options(joinedload(Job.company)).offset(pagination.skip).limit(pagination.limit).all()
    
    total_pages = (total + pagination.page_size - 1) // pagination.page_size
    
    logger.info(f"Job search returned {len(jobs)} results (total: {total})")
    
    return JobListResponse(
        jobs=[job_to_response(j) for j in jobs],
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
        total_pages=total_pages,
    )


@router.get(
    "/my",
    response_model=JobListResponse,
    summary="List my job postings",
    description="""
    List jobs posted by the current company.
    
    **Filters:**
    - `status`: Filter by job status (draft, active, paused, closed, filled)
    """
)
async def list_my_jobs(
    pagination: PaginationParams = Depends(),
    status_filter: Optional[str] = Query(None, alias="status"),
    company: User = Depends(get_current_company),
    db: Session = Depends(get_db)
):
    """List jobs posted by current company."""
    
    q = db.query(Job).filter(
        Job.company_id == company.id,
        Job.is_deleted == False
    )
    
    if status_filter:
        q = q.filter(Job.status == status_filter)
    
    total = q.count()
    
    jobs = q.order_by(Job.created_at.desc()).offset(
        pagination.skip
    ).limit(pagination.limit).all()
    
    total_pages = (total + pagination.page_size - 1) // pagination.page_size
    
    return JobListResponse(
        jobs=[job_to_response(j) for j in jobs],
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
        total_pages=total_pages,
    )


@router.post("/{job_id}/save", summary="Save a job")
async def save_job(
    job_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Save (bookmark) a job for later."""
    job = db.query(Job).filter(Job.id == job_id, Job.is_deleted == False).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    existing = db.query(SavedJob).filter(
        SavedJob.user_id == current_user.id,
        SavedJob.job_id == job_id,
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Job already saved")

    saved = SavedJob(user_id=current_user.id, job_id=job_id)
    db.add(saved)
    db.commit()
    return {"success": True, "message": "Job saved successfully"}


@router.delete("/{job_id}/save", summary="Unsave a job")
async def unsave_job(
    job_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Remove a job from saved list."""
    saved = db.query(SavedJob).filter(
        SavedJob.user_id == current_user.id,
        SavedJob.job_id == job_id,
    ).first()

    if not saved:
        raise HTTPException(status_code=404, detail="Saved job not found")

    db.delete(saved)
    db.commit()
    return {"success": True, "message": "Job removed from saved list"}


@router.get("/saved", summary="Get saved jobs")
async def get_saved_jobs(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
):
    """Get all saved (bookmarked) jobs for current user."""
    query = (
        db.query(SavedJob)
        .filter(SavedJob.user_id == current_user.id)
        .order_by(SavedJob.created_at.desc())
    )
    total = query.count()
    saved_jobs = query.offset((page - 1) * limit).limit(limit).all()

    jobs_data = []
    for saved in saved_jobs:
        job = saved.job
        if job and not job.is_deleted:
            company = job.company
            jobs_data.append({
                "id": str(job.id),
                "title": job.title,
                "description": job.description[:200] + "..." if len(job.description) > 200 else job.description,
                "location": job.location,
                "job_type": job.job_type,
                "experience_level": job.experience_level,
                "salary_min": job.salary_min,
                "salary_max": job.salary_max,
                "status": job.status,
                "applications_count": job.applications_count,
                "views_count": job.views_count,
                "created_at": job.created_at.isoformat() if job.created_at else None,
                "company": {
                    "name": company.company_name or company.full_name if company else "Unknown",
                    "logo_url": company.avatar_url if company else None,
                } if company else None,
                "saved_at": saved.created_at.isoformat() if saved.created_at else None,
            })

    return {
        "success": True,
        "data": jobs_data,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": (total + limit - 1) // limit,
    }


@router.get(
    "/recommended",
    response_model=JobMatchResponse,
    summary="Personalized job recommendations for current user",
    description="""
    Returns jobs ranked by match score against the user's most recent published resume.

    - Auto-picks the latest published resume (falls back to the most recent draft).
    - Reuses the same skill/experience/title scoring as POST /jobs/match.
    - Returns 200 with an empty `matches` list and an explanatory message when the
      user has no resume yet, so the client can render a CTA instead of an error.
    """,
)
async def recommended_jobs(
    limit: int = Query(10, ge=1, le=50, description="Maximum number of recommendations"),
    remote_only: bool = Query(False, description="Only include remote-friendly roles"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Personalized recommendations driven by the user's resume content."""
    start_time = time.time()

    # =========================================================================
    # STEP 1: Pick the user's most relevant resume
    # =========================================================================
    resume = (
        db.query(Resume)
        .filter(
            Resume.user_id == current_user.id,
            Resume.is_deleted == False,
            Resume.status == "published",
        )
        .order_by(Resume.updated_at.desc())
        .first()
    )

    if not resume:
        resume = (
            db.query(Resume)
            .filter(Resume.user_id == current_user.id, Resume.is_deleted == False)
            .order_by(Resume.updated_at.desc())
            .first()
        )

    if not resume:
        return JobMatchResponse(
            success=True,
            message="No resume found yet. Create one to unlock personalized recommendations.",
            total_jobs_analyzed=0,
            matches=[],
            resume_skills=[],
            processing_time_seconds=round(time.time() - start_time, 2),
        )

    # =========================================================================
    # STEP 2: Extract resume signals (reuse the same helpers as /match)
    # =========================================================================
    resume_skills = job_matching.extract_skills_from_resume(resume.content)
    resume_experience = job_matching.extract_experience_level(resume.content)
    resume_keywords = job_matching.extract_keywords(resume.content)

    # =========================================================================
    # STEP 3: Candidate jobs (active only; cheap pre-filter for remote_only)
    # =========================================================================
    q = db.query(Job).filter(
        Job.is_deleted == False,
        Job.status == JobStatus.ACTIVE.value,
    )
    if remote_only:
        q = q.filter(or_(Job.is_remote_allowed == True, Job.job_type == "remote"))

    jobs = q.all()

    # =========================================================================
    # STEP 4: Score & rank
    # =========================================================================
    scored: List[Dict[str, Any]] = []
    for job in jobs:
        score, skill_matches, missing_skills, reasons = job_matching.calculate_match_score(
            resume_skills=resume_skills,
            resume_experience=resume_experience,
            resume_keywords=resume_keywords,
            job=job,
        )
        scored.append(
            {
                "job": job,
                "score": score,
                "skill_matches": skill_matches,
                "missing_skills": missing_skills,
                "reasons": reasons,
            }
        )

    scored.sort(key=lambda x: x["score"], reverse=True)
    scored = scored[:limit]

    match_results = [
        JobMatchScore(
            job=job_to_response(item["job"]),
            match_score=round(item["score"], 1),
            match_reasons=item["reasons"],
            skill_matches=item["skill_matches"],
            missing_skills=item["missing_skills"][:5],
        )
        for item in scored
    ]

    processing_time = time.time() - start_time
    logger.info(
        f"🎯 Recommendations for user {current_user.id}: "
        f"{len(match_results)}/{len(jobs)} jobs in {processing_time:.2f}s"
    )

    return JobMatchResponse(
        success=True,
        message=f"Found {len(match_results)} recommended jobs",
        total_jobs_analyzed=len(jobs),
        matches=match_results,
        resume_skills=resume_skills[:20],
        processing_time_seconds=round(processing_time, 2),
    )


@router.get(
    "/{job_id}",
    response_model=JobResponse,
    summary="Get job details",
    description="""
    Get detailed information about a job posting.

    **Note:** This endpoint increments the view count (unless you're the owner).
    """
)
async def get_job(
    job_id: str,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    """Get job details and increment view count."""

    try:
        job_uuid = UUID(job_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    job = db.query(Job).filter(
        Job.id == job_uuid,
        Job.is_deleted == False
    ).first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Check if user can view (active jobs or own jobs)
    is_owner = current_user and job.company_id == current_user.id
    is_admin = current_user and current_user.role == UserRole.ADMIN
    
    if not is_owner and not is_admin and job.status != JobStatus.ACTIVE.value:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Increment view count (if not owner)
    if not is_owner and not is_admin:
        job.increment_view_count()
        db.commit()
        logger.debug(f"Job view count incremented: {job.id} -> {job.views_count}")
    
    return job_to_response(job)


@router.post(
    "",
    response_model=JobResponse,
    status_code=status.HTTP_201_CREATED,
    include_in_schema=False,
)
@router.post(
    "/",
    response_model=JobResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create job posting",
    description="""
    Create a new job posting.
    
    **Access:** Company accounts only
    
    Jobs are created as **active** by default.
    """
)
async def create_job(
    job_data: JobCreate,
    company: User = Depends(get_current_company),
    db: Session = Depends(get_db)
):
    """Create a new job posting (company only)."""
    
    job = Job(
        company_id=company.id,
        title=job_data.title,
        description=job_data.description,
        requirements=job_data.requirements,
        responsibilities=job_data.responsibilities,
        benefits=job_data.benefits,
        salary_min=job_data.salary_min,
        salary_max=job_data.salary_max,
        salary_currency=job_data.salary_currency,
        is_salary_visible=job_data.is_salary_visible,
        location=job_data.location,
        is_remote_allowed=job_data.is_remote_allowed,
        job_type=job_data.job_type.value,
        experience_level=job_data.experience_level.value,
        external_apply_url=job_data.external_apply_url,
        expires_at=job_data.expires_at,
        status=JobStatus.ACTIVE.value,
    )
    
    db.add(job)
    db.commit()
    db.refresh(job)
    
    logger.info(f"Job created: {job.id} by company: {company.id}")
    
    return job_to_response(job)


@router.put(
    "/{job_id}",
    response_model=JobResponse,
    summary="Update job",
    description="""
    Update an existing job posting.
    
    **Access:** Only the owner company or admin can update.
    
    **Note:** Partial updates are supported (only send fields to update).
    """
)
async def update_job(
    job_id: UUID,
    update_data: JobUpdate,
    current_user: User = Depends(get_current_company),
    db: Session = Depends(get_db)
):
    """Update a job posting (owner only)."""
    
    job = db.query(Job).filter(
        Job.id == job_id,
        Job.is_deleted == False
    ).first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Check ownership
    if job.company_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own job postings"
        )
    
    # Update fields
    update_dict = update_data.model_dump(exclude_unset=True)
    
    for field, value in update_dict.items():
        if value is not None:
            if hasattr(value, 'value'):  # Enum
                setattr(job, field, value.value)
            else:
                setattr(job, field, value)
    
    db.commit()
    db.refresh(job)
    
    logger.info(f"Job updated: {job.id}")
    
    return job_to_response(job)


@router.delete(
    "/{job_id}",
    response_model=MessageResponse,
    summary="Delete job",
    description="""
    Soft delete a job posting.
    
    **Access:** Only the owner company or admin can delete.
    
    **Note:** This also affects all applications for this job.
    """
)
async def delete_job(
    job_id: UUID,
    current_user: User = Depends(get_current_company),
    db: Session = Depends(get_db)
):
    """Delete a job posting (owner only)."""
    
    job = db.query(Job).filter(
        Job.id == job_id,
        Job.is_deleted == False
    ).first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Check ownership
    if job.company_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own job postings"
        )
    
    job.soft_delete()
    db.commit()
    
    logger.info(f"Job deleted: {job.id}")
    
    return MessageResponse(
        message="Job deleted successfully",
        success=True
    )


@router.get(
    "/{job_id}/applications",
    response_model=ApplicationListResponse,
    summary="Get applications for job",
    description="""
    Get all applications for a specific job.
    
    **Access:** Only the job owner (company) or admin can view.
    
    **Filters:**
    - `status`: Filter by application status
    
    **Includes:**
    - Applicant details (name, email, avatar)
    - Resume summary (title, ATS score)
    - Internal notes
    """
)
async def get_job_applications(
    job_id: UUID,
    pagination: PaginationParams = Depends(),
    status_filter: Optional[str] = Query(None, alias="status"),
    company: User = Depends(get_current_company),
    db: Session = Depends(get_db)
):
    """Get applications for a job (company only)."""
    
    # Verify job exists and ownership
    job = db.query(Job).filter(
        Job.id == job_id,
        Job.is_deleted == False
    ).first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    if job.company_id != company.id and company.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view applications for your own jobs"
        )
    
    # Query applications
    q = db.query(Application).filter(
        Application.job_id == job_id,
        Application.is_deleted == False
    )
    
    if status_filter:
        q = q.filter(Application.status == status_filter)
    
    total = q.count()
    
    # Get status counts
    pending_count = db.query(func.count(Application.id)).filter(
        Application.job_id == job_id,
        Application.status == ApplicationStatus.PENDING.value,
        Application.is_deleted == False
    ).scalar()
    
    reviewing_count = db.query(func.count(Application.id)).filter(
        Application.job_id == job_id,
        Application.status == ApplicationStatus.REVIEWING.value,
        Application.is_deleted == False
    ).scalar()
    
    interview_count = db.query(func.count(Application.id)).filter(
        Application.job_id == job_id,
        Application.status == ApplicationStatus.INTERVIEW.value,
        Application.is_deleted == False
    ).scalar()
    
    applications = q.order_by(Application.applied_at.desc()).offset(
        pagination.skip
    ).limit(pagination.limit).all()
    
    total_pages = (total + pagination.page_size - 1) // pagination.page_size
    
    return ApplicationListResponse(
        applications=[
            application_to_response(
                a,
                include_resume=True,
                include_applicant=True,
                include_notes=True
            )
            for a in applications
        ],
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
        total_pages=total_pages,
        pending_count=pending_count,
        reviewing_count=reviewing_count,
        interview_count=interview_count,
    )


@router.post(
    "/match",
    response_model=JobMatchResponse,
    summary="🔥 AI-powered job matching",
    description="""
    **CORE FEATURE** - Match a resume against available jobs using AI.
    
    This endpoint analyzes the resume content and matches it against active job listings,
    returning a ranked list of the best matches with detailed scores and insights.
    
    **How it works:**
    1. Extracts skills and experience from the resume
    2. Compares against all active job requirements
    3. Calculates match scores based on skill overlap, experience level, etc.
    4. Returns ranked list with explanations
    
    **Request:**
    ```json
    {
        "resume_id": "uuid-of-resume",
        "location_preference": "San Francisco",
        "remote_only": false,
        "min_salary": 8000000,
        "limit": 10
    }
    ```
    
    **Response includes:**
    - Match score (0-100) for each job
    - Skills that matched
    - Skills that are missing
    - Reasons for the match
    """
)
async def match_jobs(
    request: JobMatchRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """AI-powered job matching based on resume."""
    
    start_time = time.time()
    
    logger.info(f"🤖 Job matching started for user: {current_user.id}")
    logger.info(f"   Resume ID: {request.resume_id}")
    
    # =========================================================================
    # STEP 1: Get and validate resume
    # =========================================================================
    
    try:
        resume_uuid = UUID(request.resume_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid resume ID format"
        )
    
    resume = db.query(Resume).filter(
        Resume.id == resume_uuid,
        Resume.user_id == current_user.id,
        Resume.is_deleted == False
    ).first()
    
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    # =========================================================================
    # STEP 2: Extract skills from resume
    # =========================================================================
    
    resume_skills = job_matching.extract_skills_from_resume(resume.content)
    resume_experience = job_matching.extract_experience_level(resume.content)
    resume_keywords = job_matching.extract_keywords(resume.content)
    
    logger.info(f"   Extracted {len(resume_skills)} skills from resume")
    
    # =========================================================================
    # STEP 3: Get matching jobs
    # =========================================================================
    
    q = db.query(Job).filter(
        Job.is_deleted == False,
        Job.status == JobStatus.ACTIVE.value
    )
    
    # Apply filters
    if request.location_preference:
        q = q.filter(
            or_(
                Job.location.ilike(f"%{request.location_preference}%"),
                Job.is_remote_allowed == True
            )
        )
    
    if request.remote_only:
        q = q.filter(
            or_(
                Job.is_remote_allowed == True,
                Job.job_type == "remote"
            )
        )
    
    if request.min_salary:
        q = q.filter(
            or_(
                Job.salary_min >= request.min_salary,
                Job.salary_min.is_(None)
            )
        )
    
    if request.experience_levels:
        q = q.filter(Job.experience_level.in_(request.experience_levels))
    
    jobs = q.all()
    
    logger.info(f"   Analyzing {len(jobs)} jobs for matching")
    
    # =========================================================================
    # STEP 4: Calculate match scores
    # =========================================================================
    
    matches = []
    
    for job in jobs:
        score, skill_matches, missing_skills, reasons = job_matching.calculate_match_score(
            resume_skills=resume_skills,
            resume_experience=resume_experience,
            resume_keywords=resume_keywords,
            job=job,
        )
        
        matches.append({
            "job": job,
            "score": score,
            "skill_matches": skill_matches,
            "missing_skills": missing_skills,
            "reasons": reasons,
        })
    
    # Sort by score (highest first)
    matches.sort(key=lambda x: x["score"], reverse=True)
    
    # Limit results
    matches = matches[:request.limit]
    
    # =========================================================================
    # STEP 5: Build response
    # =========================================================================
    
    processing_time = time.time() - start_time
    
    match_results = [
        JobMatchScore(
            job=job_to_response(m["job"]),
            match_score=round(m["score"], 1),
            match_reasons=m["reasons"],
            skill_matches=m["skill_matches"],
            missing_skills=m["missing_skills"][:5],  # Limit to top 5 missing
        )
        for m in matches
    ]
    
    logger.info(f"✅ Job matching complete: {len(match_results)} matches in {processing_time:.2f}s")
    
    return JobMatchResponse(
        success=True,
        message=f"Found {len(match_results)} matching jobs",
        total_jobs_analyzed=len(jobs),
        matches=match_results,
        resume_skills=resume_skills[:20],  # Limit to top 20
        processing_time_seconds=round(processing_time, 2),
    )


@router.post(
    "/{job_id}/publish",
    response_model=JobResponse,
    summary="Publish job",
    description="""
    Publish a job posting (make it active and visible to job seekers).
    
    **Access:** Only the owner company can publish.
    """
)
async def publish_job(
    job_id: UUID,
    current_user: User = Depends(get_current_company),
    db: Session = Depends(get_db)
):
    """Publish a job posting."""
    
    job = db.query(Job).filter(
        Job.id == job_id,
        Job.company_id == current_user.id,
        Job.is_deleted == False
    ).first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    job.publish()
    db.commit()
    db.refresh(job)
    
    logger.info(f"Job published: {job.id}")
    
    return job_to_response(job)


@router.post(
    "/{job_id}/close",
    response_model=JobResponse,
    summary="Close job",
    description="""
    Close a job posting (stop accepting applications).
    
    **Access:** Only the owner company can close.
    """
)
async def close_job(
    job_id: UUID,
    current_user: User = Depends(get_current_company),
    db: Session = Depends(get_db)
):
    """Close a job posting."""
    
    job = db.query(Job).filter(
        Job.id == job_id,
        Job.company_id == current_user.id,
        Job.is_deleted == False
    ).first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    job.close()
    db.commit()
    db.refresh(job)
    
    logger.info(f"Job closed: {job.id}")
    
    return job_to_response(job)


