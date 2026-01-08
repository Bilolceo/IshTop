"""
=============================================================================
RESUME SERVICE
=============================================================================

Handles resume business logic, CRUD operations, and validation.

FEATURES:
    - Resume creation, updating, deletion
    - Status management (draft, published, archived)
    - Analytics and statistics
    - File operations (PDF generation, etc.)

AUTHOR: SmartCareer AI Team
VERSION: 1.0.0
=============================================================================
"""

import logging
from typing import List, Dict, Any, Optional
from uuid import UUID
from datetime import datetime, timezone

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models import Resume, User, ResumeStatus, Application, ApplicationStatus
from app.core.exceptions import NotFoundError, ValidationError, AuthorizationError
from app.schemas.resume import ResumeCreate, ResumeUpdate

logger = logging.getLogger(__name__)


class ResumeService:
    """
    Service for resume business logic and operations.
    """

    def __init__(self):
        """Initialize resume service."""
        pass

    async def create_resume(
        self,
        db: Session,
        user_id: UUID,
        resume_data: ResumeCreate
    ) -> Resume:
        """
        Create a new resume for a user.

        Args:
            db: Database session
            user_id: User ID
            resume_data: Resume creation data

        Returns:
            Created resume instance
        """
        # Validate user exists
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise NotFoundError("User not found")

        # Create resume
        resume = Resume(
            user_id=user_id,
            title=resume_data.title,
            template=resume_data.template,
            status=ResumeStatus.draft,
            personal_info=resume_data.personal_info.dict() if resume_data.personal_info else {},
            summary=resume_data.summary,
            experience=[exp.dict() for exp in resume_data.experience] if resume_data.experience else [],
            education=[edu.dict() for edu in resume_data.education] if resume_data.education else [],
            skills=resume_data.skills or [],
            languages=[lang.dict() for lang in resume_data.languages] if resume_data.languages else [],
            certifications=resume_data.certifications or [],
            projects=[proj.dict() for proj in resume_data.projects] if resume_data.projects else [],
            ats_score=0,  # Will be calculated later
        )

        db.add(resume)
        db.commit()
        db.refresh(resume)

        logger.info(f"Created resume {resume.id} for user {user_id}")
        return resume

    async def get_resume(
        self,
        db: Session,
        resume_id: UUID,
        user_id: UUID = None
    ) -> Resume:
        """
        Get a resume by ID.

        Args:
            db: Database session
            resume_id: Resume ID
            user_id: User ID (for authorization, optional)

        Returns:
            Resume instance

        Raises:
            NotFoundError: If resume not found
            AuthorizationError: If user not authorized
        """
        resume = db.query(Resume).filter(Resume.id == resume_id).first()

        if not resume:
            raise NotFoundError("Resume not found")

        if user_id and resume.user_id != user_id:
            raise AuthorizationError("Not authorized to access this resume")

        return resume

    async def update_resume(
        self,
        db: Session,
        resume_id: UUID,
        user_id: UUID,
        update_data: ResumeUpdate
    ) -> Resume:
        """
        Update a resume.

        Args:
            db: Database session
            resume_id: Resume ID
            user_id: User ID
            update_data: Resume update data

        Returns:
            Updated resume instance

        Raises:
            NotFoundError: If resume not found
            AuthorizationError: If user not authorized
        """
        resume = await self.get_resume(db, resume_id, user_id)

        # Update fields
        update_dict = update_data.dict(exclude_unset=True)

        for field, value in update_dict.items():
            if hasattr(resume, field):
                setattr(resume, field, value)

        resume.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(resume)

        logger.info(f"Updated resume {resume_id}")
        return resume

    async def delete_resume(
        self,
        db: Session,
        resume_id: UUID,
        user_id: UUID
    ) -> None:
        """
        Soft delete a resume.

        Args:
            db: Database session
            resume_id: Resume ID
            user_id: User ID

        Raises:
            NotFoundError: If resume not found
            AuthorizationError: If user not authorized
        """
        resume = await self.get_resume(db, resume_id, user_id)

        resume.is_deleted = True
        resume.deleted_at = datetime.now(timezone.utc)
        db.commit()

        logger.info(f"Deleted resume {resume_id}")

    async def publish_resume(
        self,
        db: Session,
        resume_id: UUID,
        user_id: UUID
    ) -> Resume:
        """
        Publish a resume.

        Args:
            db: Database session
            resume_id: Resume ID
            user_id: User ID

        Returns:
            Published resume instance
        """
        resume = await self.get_resume(db, resume_id, user_id)

        resume.status = ResumeStatus.published
        resume.published_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(resume)

        logger.info(f"Published resume {resume_id}")
        return resume

    async def archive_resume(
        self,
        db: Session,
        resume_id: UUID,
        user_id: UUID
    ) -> Resume:
        """
        Archive a resume.

        Args:
            db: Database session
            resume_id: Resume ID
            user_id: User ID

        Returns:
            Archived resume instance
        """
        resume = await self.get_resume(db, resume_id, user_id)

        resume.status = ResumeStatus.archived
        db.commit()
        db.refresh(resume)

        logger.info(f"Archived resume {resume_id}")
        return resume

    async def get_user_resumes(
        self,
        db: Session,
        user_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[Resume]:
        """
        Get all resumes for a user.

        Args:
            db: Database session
            user_id: User ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of user's resumes
        """
        resumes = (
            db.query(Resume)
            .filter(
                Resume.user_id == user_id,
                Resume.is_deleted == False
            )
            .order_by(Resume.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

        return resumes

    async def get_resume_analytics(
        self,
        db: Session,
        resume_id: UUID,
        user_id: UUID
    ) -> Dict[str, Any]:
        """
        Get analytics for a resume.

        Args:
            db: Database session
            resume_id: Resume ID
            user_id: User ID

        Returns:
            Analytics data
        """
        resume = await self.get_resume(db, resume_id, user_id)

        # Get application statistics
        application_stats = (
            db.query(
                Application.status,
                func.count(Application.id).label('count')
            )
            .filter(Application.resume_id == resume_id)
            .group_by(Application.status)
            .all()
        )

        # Convert to dict
        stats_dict = {status.value: count for status, count in application_stats}

        analytics = {
            "resume_id": str(resume_id),
            "views_count": resume.views_count,
            "downloads_count": resume.downloads_count,
            "applications_count": sum(stats_dict.values()),
            "application_status_breakdown": stats_dict,
            "ats_score": resume.ats_score,
            "published_at": resume.published_at.isoformat() if resume.published_at else None,
        }

        return analytics

    def validate_resume_data(self, resume_data: Dict[str, Any]) -> None:
        """
        Validate resume data.

        Args:
            resume_data: Resume data to validate

        Raises:
            ValidationError: If data is invalid
        """
        if not resume_data.get('title', '').strip():
            raise ValidationError("Resume title is required")

        if not resume_data.get('personal_info', {}).get('full_name', '').strip():
            raise ValidationError("Full name is required")

        # Add more validations as needed
