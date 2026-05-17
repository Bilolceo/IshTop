"""
=============================================================================
JOB MODEL
=============================================================================

PURPOSE:
    Represents job postings from company users.
    Contains job details, requirements, and tracks applications.

=============================================================================
INDEX STRATEGY EXPLAINED
=============================================================================

WHY SO MANY INDEXES?
    Job listings are heavily searched and filtered. Users browse jobs by:
    - Location ("jobs in San Francisco")
    - Type ("remote jobs")
    - Experience ("senior positions")
    - Status ("active jobs only")
    
    Without indexes, PostgreSQL scans entire table for each query.
    With indexes, it jumps directly to matching rows.

INDEX TYPES USED:
    
    1. B-TREE (Default):
       - For: Equality (=) and range queries (<, >, BETWEEN)
       - Used on: title, location, job_type, status, experience_level
       - Good for: High cardinality columns
    
    2. COMPOSITE INDEXES:
       - For: Queries filtering multiple columns
       - idx_jobs_search(status, job_type, location)
       - WHY? Covers the most common search pattern
       - Order matters: put most selective first

    3. GIN (if needed for JSONB):
       - For: Array/JSON contains queries
       - Could add for requirements searching

WHEN TO ADD MORE INDEXES:
    - Check slow query logs (pg_stat_statements)
    - Use EXPLAIN ANALYZE on common queries
    - Index columns that appear in WHERE, JOIN, ORDER BY

TRADE-OFFS:
    - More indexes = slower INSERT/UPDATE
    - Each index consumes disk space
    - Rule of thumb: Index columns queried > 10% of the time

=============================================================================
AUTHOR: IshTop Team
VERSION: 1.0.0
=============================================================================
"""

# =============================================================================
# IMPORTS
# =============================================================================

from enum import Enum
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any, TYPE_CHECKING

# SQLAlchemy imports
from sqlalchemy import (
    Column, String, Text, Integer, Boolean, DateTime,
    ForeignKey, Index, CheckConstraint
)
from app.models.types import GUID
from sqlalchemy import JSON
from sqlalchemy.orm import relationship, validates

# Local imports
from app.models.base import Base, UUIDMixin, TimestampMixin, SoftDeleteMixin, utc_now

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.application import Application


# =============================================================================
# JOB ENUMS
# =============================================================================

class JobType(str, Enum):
    """
    Types of employment.
    
    WHY SEPARATE REMOTE AND HYBRID?
        Modern job seekers filter specifically for remote work.
        Having explicit types makes this easy to query.
    """
    FULL_TIME = "full_time"       # Standard 40hrs/week
    PART_TIME = "part_time"       # Less than 40hrs/week
    REMOTE = "remote"             # Fully remote position
    HYBRID = "hybrid"             # Mix of remote and office
    CONTRACT = "contract"         # Fixed-term contract
    INTERNSHIP = "internship"     # Internship position


class ExperienceLevel(str, Enum):
    """
    Required experience level.
    
    WHY THESE LEVELS?
        Industry standard classification.
        Maps roughly to years of experience.
    """
    INTERN = "intern"             # 0 years, still in school
    JUNIOR = "junior"             # 0-2 years
    MID = "mid"                   # 2-5 years
    SENIOR = "senior"             # 5-8 years
    LEAD = "lead"                 # 8+ years, team leadership
    EXECUTIVE = "executive"       # C-level or director


class JobStatus(str, Enum):
    """
    Job posting lifecycle states.
    
    WORKFLOW:
        DRAFT → ACTIVE ↔ PAUSED → CLOSED
                         ↘ FILLED
    
    WHY MULTIPLE END STATES?
        - CLOSED: Company stopped hiring (budget, etc.)
        - FILLED: Position was filled (success metric)
        Distinction matters for analytics.
    """
    DRAFT = "draft"          # Not published yet
    ACTIVE = "active"        # Accepting applications
    PAUSED = "paused"        # Temporarily not accepting
    CLOSED = "closed"        # No longer hiring
    FILLED = "filled"        # Position was filled


# =============================================================================
# JOB MODEL
# =============================================================================

class Job(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    """
    Job posting model.
    
    ==========================================================================
    SALARY HANDLING
    ==========================================================================
    
    WHY STORE AS INTEGER (CENTS)?
        - Avoids floating point precision issues
        - $75,000 stored as 7500000 (cents)
        - Math is exact: no rounding errors
        - Standard practice in financial applications
    
    DISPLAY CONVERSION:
        salary_display = salary_cents / 100
        
    WHY SEPARATE MIN/MAX?
        - Most jobs have salary ranges
        - Enables range queries: "jobs paying 100k-150k"
        - is_salary_visible controls whether to show it
    
    ==========================================================================
    JSONB FIELDS
    ==========================================================================
    
    requirements, responsibilities, benefits are stored as JSONB arrays:
    
        requirements: ["Python", "3+ years experience", "BS in CS"]
        responsibilities: ["Lead team of 5", "Design systems"]
        benefits: ["Health insurance", "401k", "Remote work"]
    
    WHY JSONB ARRAYS?
        - Variable number of items
        - Easy to display as bullet points
        - Can search: requirements @> '["Python"]'
        - No need for separate tables
    
    ==========================================================================
    RELATIONSHIP CONFIGURATION
    ==========================================================================
    
    Job → Company (Many-to-One):
        - Foreign key: company_id → users.id
        - ondelete='CASCADE': Delete job when company deleted
        - lazy='joined': Always load company with job
    
    Job → Applications (One-to-Many):
        - back_populates for bidirectional
        - cascade='all, delete-orphan': Delete apps with job
        - lazy='dynamic': Return query for pagination
    """
    
    __tablename__ = "jobs"
    
    # =========================================================================
    # TABLE CONFIGURATION
    # =========================================================================
    
    __table_args__ = (
        # =====================================================================
        # SINGLE-COLUMN INDEXES
        # =====================================================================
        
        # Index for text search on title
        # WHY? Users search by job title frequently
        Index('idx_jobs_title', 'title'),
        
        # Index for location filtering
        # WHY? "Jobs in New York" is a common filter
        Index('idx_jobs_location', 'location'),
        
        # Index for job type filtering
        # WHY? "Remote jobs only" filter
        Index('idx_jobs_type', 'job_type'),
        
        # Index for status filtering
        # WHY? Only show active jobs to users
        Index('idx_jobs_status', 'status'),
        
        # Index for experience level
        # WHY? "Senior positions only" filter
        Index('idx_jobs_experience', 'experience_level'),
        
        # Index for expiration date
        # WHY? Filter out expired jobs efficiently
        Index('idx_jobs_expires', 'expires_at'),
        
        # Index for soft delete
        Index('idx_jobs_not_deleted', 'is_deleted'),
        
        # =====================================================================
        # COMPOSITE INDEXES
        # =====================================================================
        
        # Main search index: covers the most common query pattern
        # Query: SELECT * FROM jobs WHERE status = 'active' AND job_type = 'remote' AND location = 'New York'
        # WHY this order? Most selective first (status), then job_type, then location
        Index('idx_jobs_search', 'status', 'job_type', 'location'),
        
        # Index for company's jobs
        # Query: SELECT * FROM jobs WHERE company_id = ?
        Index('idx_jobs_company', 'company_id'),
        
        # =====================================================================
        # CONSTRAINTS
        # =====================================================================
        
        # Ensure salary_max >= salary_min
        CheckConstraint(
            'salary_max >= salary_min OR salary_min IS NULL OR salary_max IS NULL',
            name='check_salary_range'
        ),
        
        {'comment': 'Job postings from company users'}
    )
    
    # =========================================================================
    # COLUMNS - RELATIONSHIPS
    # =========================================================================
    
    company_id = Column(
        GUID(),
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment="Company that posted this job (CASCADE: delete company → delete jobs)"
    )
    
    # =========================================================================
    # COLUMNS - JOB DETAILS
    # =========================================================================
    
    title = Column(
        String(255),
        nullable=False,
        index=True,
        comment="Job title (e.g., 'Senior Software Engineer')"
    )
    
    description = Column(
        Text,
        nullable=False,
        comment="Full job description (can be long, supports markdown)"
    )
    
    # JSON arrays for flexible lists
    requirements = Column(
        JSON,
        nullable=True,
        default=list,
        comment="Required skills/qualifications as JSON array"
    )
    
    responsibilities = Column(
        JSON,
        nullable=True,
        default=list,
        comment="Job responsibilities as JSON array"
    )
    
    benefits = Column(
        JSON,
        nullable=True,
        default=list,
        comment="Benefits and perks as JSON array"
    )
    
    # =========================================================================
    # COLUMNS - SALARY (stored in cents)
    # =========================================================================
    
    salary_min = Column(
        Integer,
        nullable=True,
        comment="Minimum salary in cents (e.g., 7500000 = $75,000)"
    )
    
    salary_max = Column(
        Integer,
        nullable=True,
        comment="Maximum salary in cents (e.g., 10000000 = $100,000)"
    )
    
    salary_currency = Column(
        String(3),
        default="USD",
        nullable=False,
        comment="ISO 4217 currency code (USD, EUR, GBP, etc.)"
    )
    
    is_salary_visible = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="Whether to show salary to job seekers"
    )
    
    # =========================================================================
    # COLUMNS - LOCATION
    # =========================================================================
    
    location = Column(
        String(255),
        nullable=True,
        index=True,
        comment="Job location (city, state, country)"
    )
    
    is_remote_allowed = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether remote work is allowed"
    )
    
    # =========================================================================
    # COLUMNS - CATEGORIZATION
    # =========================================================================
    
    job_type = Column(
        String(20),
        nullable=False,
        default=JobType.FULL_TIME.value,
        index=True,
        comment="Employment type: full_time, part_time, remote, hybrid, contract, internship"
    )
    
    experience_level = Column(
        String(20),
        nullable=False,
        default=ExperienceLevel.MID.value,
        index=True,
        comment="Required experience: intern, junior, mid, senior, lead, executive"
    )
    
    status = Column(
        String(20),
        nullable=False,
        default=JobStatus.DRAFT.value,
        index=True,
        comment="Posting status: draft, active, paused, closed, filled"
    )
    
    # =========================================================================
    # COLUMNS - ANALYTICS
    # =========================================================================
    
    views_count = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Number of times job listing was viewed"
    )
    
    applications_count = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Number of applications received"
    )
    
    # =========================================================================
    # COLUMNS - SETTINGS
    # =========================================================================
    
    external_apply_url = Column(
        String(500),
        nullable=True,
        comment="External URL for applications (if not using platform)"
    )
    
    is_featured = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether job is featured/promoted (shown first)"
    )
    
    expires_at = Column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
        comment="When this job posting expires"
    )
    
    # =========================================================================
    # RELATIONSHIPS
    # =========================================================================
    
    # Many-to-one: Job belongs to Company (User)
    company: "User" = relationship(
        "User",
        back_populates="jobs",
        lazy="joined",                 # Always load company with job
        foreign_keys=[company_id]
    )
    
    # One-to-many: Job has many Applications
    applications = relationship(
        "Application",
        back_populates="job",
        cascade="all, delete-orphan",  # Delete applications with job
        lazy="dynamic",                 # Return query for pagination
        order_by="Application.applied_at.desc()"
    )

    # One-to-many: Job saved by many users
    saved_by = relationship(
        "SavedJob",
        back_populates="job",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )
    
    # =========================================================================
    # VALIDATORS
    # =========================================================================
    
    @validates('job_type')
    def validate_job_type(self, key: str, value: str) -> str:
        """Ensure job_type is valid."""
        valid_types = [t.value for t in JobType]
        if value not in valid_types:
            raise ValueError(f"Invalid job_type: {value}")
        return value
    
    @validates('experience_level')
    def validate_experience_level(self, key: str, value: str) -> str:
        """Ensure experience_level is valid."""
        valid_levels = [l.value for l in ExperienceLevel]
        if value not in valid_levels:
            raise ValueError(f"Invalid experience_level: {value}")
        return value
    
    @validates('status')
    def validate_status(self, key: str, value: str) -> str:
        """Ensure status is valid."""
        valid_statuses = [s.value for s in JobStatus]
        if value not in valid_statuses:
            raise ValueError(f"Invalid status: {value}")
        return value
    
    @validates('salary_min', 'salary_max')
    def validate_salary(self, key: str, value: Optional[int]) -> Optional[int]:
        """Ensure salary is non-negative."""
        if value is not None and value < 0:
            raise ValueError(f"{key} cannot be negative")
        return value
    
    # =========================================================================
    # STATUS METHODS
    # =========================================================================
    
    def publish(self) -> None:
        """Publish the job (make it active)."""
        self.status = JobStatus.ACTIVE.value
    
    def pause(self) -> None:
        """Temporarily pause accepting applications."""
        self.status = JobStatus.PAUSED.value
    
    def close(self) -> None:
        """Close the job posting."""
        self.status = JobStatus.CLOSED.value
    
    def mark_as_filled(self) -> None:
        """Mark position as filled."""
        self.status = JobStatus.FILLED.value
    
    # =========================================================================
    # HELPER PROPERTIES
    # =========================================================================
    
    def _expires_at_aware(self):
        """Coerce expires_at to a UTC-aware datetime (SQLite returns naive)."""
        if not self.expires_at:
            return None
        if self.expires_at.tzinfo is None:
            from datetime import timezone
            return self.expires_at.replace(tzinfo=timezone.utc)
        return self.expires_at

    @property
    def is_active(self) -> bool:
        """Is this job currently accepting applications?"""
        if self.status != JobStatus.ACTIVE.value:
            return False
        if self.is_deleted:
            return False
        expires = self._expires_at_aware()
        if expires and expires < utc_now():
            return False
        return True

    @property
    def is_expired(self) -> bool:
        """Has this job posting expired?"""
        expires = self._expires_at_aware()
        if not expires:
            return False
        return expires < utc_now()
    
    @property
    def salary_range_display(self) -> Optional[str]:
        """Get formatted salary range for display."""
        if not self.is_salary_visible:
            return None
        if not self.salary_min and not self.salary_max:
            return None
        
        # Convert cents to dollars
        min_display = f"{self.salary_min // 100:,}" if self.salary_min else None
        max_display = f"{self.salary_max // 100:,}" if self.salary_max else None
        
        currency = self.salary_currency or "USD"
        
        if min_display and max_display:
            return f"{currency} {min_display} - {max_display}"
        elif min_display:
            return f"From {currency} {min_display}"
        else:
            return f"Up to {currency} {max_display}"
    
    # =========================================================================
    # ANALYTICS METHODS
    # =========================================================================
    
    def increment_view_count(self) -> None:
        """Increment view counter."""
        self.views_count = (self.views_count or 0) + 1
    
    def increment_application_count(self) -> None:
        """Increment application counter."""
        self.applications_count = (self.applications_count or 0) + 1
    
    # =========================================================================
    # SERIALIZATION
    # =========================================================================
    
    def __repr__(self) -> str:
        """String representation for debugging."""
        return (
            f"<Job("
            f"id={self.id}, "
            f"title='{self.title}', "
            f"status='{self.status}', "
            f"company_id={self.company_id}"
            f")>"
        )
    
    def to_dict(self, include_company: bool = False) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = {
            "id": str(self.id),
            "company_id": str(self.company_id),
            "title": self.title,
            "description": self.description,
            "requirements": self.requirements,
            "responsibilities": self.responsibilities,
            "benefits": self.benefits,
            "salary_range": self.salary_range_display,
            "location": self.location,
            "is_remote_allowed": self.is_remote_allowed,
            "job_type": self.job_type,
            "experience_level": self.experience_level,
            "status": self.status,
            "views_count": self.views_count,
            "applications_count": self.applications_count,
            "is_featured": self.is_featured,
            "is_active": self.is_active,
            "is_deleted": self.is_deleted,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
        }
        
        if include_company and self.company:
            data["company"] = {
                "id": str(self.company.id),
                "name": self.company.company_name or self.company.full_name,
                "logo": self.company.avatar_url,
                "location": self.company.location,
            }
        
        return data


# =============================================================================
# SAVED JOB MODEL
# =============================================================================

class SavedJob(Base, UUIDMixin, TimestampMixin):
    """
    Saved (bookmarked) jobs by students.
    
    Allows students to bookmark jobs they are interested in.
    Many-to-many relationship between users and jobs, stored as a table.
    """
    __tablename__ = "saved_jobs"
    __table_args__ = (
        Index("idx_saved_jobs_user", "user_id"),
        Index("idx_saved_jobs_job", "job_id"),
        {"comment": "Student bookmarked jobs"},
    )

    # Foreign keys
    user_id = Column(
        GUID(),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    job_id = Column(
        GUID(),
        ForeignKey("jobs.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Relationships
    user = relationship("User", back_populates="saved_jobs", lazy="select")
    job = relationship("Job", back_populates="saved_by", lazy="select")

    def __repr__(self) -> str:
        return f"<SavedJob(user={self.user_id}, job={self.job_id})>"
