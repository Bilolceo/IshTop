"""
=============================================================================
JOB ALERT MODEL
=============================================================================

"Yangi ish chiqsa xabar ber" — one row per subscription a Telegram chat holds.

Keyed by the Telegram chat, not by a platform user: most people who use the
bot have never linked it to a site account (14 of ~200 students when this was
written), and an alert that first demands a sign-up is an alert nobody sets.
`user_id` is filled in when the chat IS linked, for the site to show later.

A subscription is one of three kinds, matching the three ways the bot browses:
  kind="c"  value=<category id>   (app.core.job_categories.CATEGORIES)
  kind="t"  value=<city id>       (app.core.job_categories.CITIES)
  kind="s"  value=<keyword>       (same all-tokens match as the bot's search)

`last_checked_at` is a watermark on jobs.created_at: a job is news to this
alert only if it was created after the last one the alert was checked against.
=============================================================================
"""

from sqlalchemy import Column, String, Boolean, Integer, ForeignKey, Index, UniqueConstraint

from app.models.base import Base, UUIDMixin, TimestampMixin
from app.models.types import GUID, UTCDateTime


class JobAlert(Base, UUIDMixin, TimestampMixin):
    """A Telegram chat's standing request to hear about new matching jobs."""

    __tablename__ = "job_alerts"
    __table_args__ = (
        UniqueConstraint("chat_id", "kind", "value", name="uq_job_alerts_chat_kind_value"),
        Index("ix_job_alerts_active", "is_active"),
    )

    chat_id = Column(String(32), nullable=False, index=True)
    user_id = Column(
        GUID(),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    kind = Column(String(1), nullable=False)       # "c" | "t" | "s"
    value = Column(String(40), nullable=False)

    is_active = Column(Boolean, nullable=False, default=True)
    last_checked_at = Column(UTCDateTime(), nullable=False)
    last_sent_at = Column(UTCDateTime(), nullable=True)
    sent_count = Column(Integer, nullable=False, default=0)

    def __repr__(self) -> str:
        return f"<JobAlert {self.chat_id} {self.kind}:{self.value} active={self.is_active}>"
