"""
=============================================================================
SURVEY RESPONSE MODEL
=============================================================================

One submitted problem-validation survey (definitions: app.core.surveys).

Anonymous by design: `user_id` is set only when a signed-in student answers
(so we can stop asking them), and the IP is kept only as a salted hash, used
to spot one person stuffing the form — never to identify anyone.
=============================================================================
"""

from sqlalchemy import Column, String, ForeignKey, Index, JSON

from app.models.base import Base, UUIDMixin, TimestampMixin
from app.models.types import GUID


class SurveyResponse(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "survey_responses"
    __table_args__ = (
        Index("ix_survey_responses_key_created", "survey_key", "created_at"),
    )

    survey_key = Column(String(40), nullable=False)
    user_id = Column(GUID(), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    answers = Column(JSON, nullable=False)
    source = Column(String(40), nullable=True)
    ip_hash = Column(String(32), nullable=True, index=True)
