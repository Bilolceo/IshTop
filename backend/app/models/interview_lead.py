"""
=============================================================================
INTERVIEW LEAD MODEL
=============================================================================

Someone who finished the survey and agreed to a follow-up interview.

Deliberately NOT linked to their SurveyResponse row. The survey page promises
anonymity, and that promise has to survive this table: we learn that somebody
is willing to talk, never which set of answers was theirs. So there is no
response_id here, and none is stored on the response either.
=============================================================================
"""

from sqlalchemy import Column, String, Index

from app.models.base import Base, UUIDMixin, TimestampMixin


class InterviewLead(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "interview_leads"
    __table_args__ = (
        Index("ix_interview_leads_key_created", "survey_key", "created_at"),
    )

    survey_key = Column(String(40), nullable=False)
    # Telegram username or phone, as typed. Free text on purpose: asking for a
    # strict format loses people who write "@ali" vs "ali" vs a phone number.
    contact = Column(String(120), nullable=False)
    source = Column(String(40), nullable=True)
    status = Column(String(20), nullable=False, default="new")  # new | contacted | done
