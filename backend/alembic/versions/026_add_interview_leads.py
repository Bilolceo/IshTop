"""Add interview_leads table for survey follow-up interviews.

Revision ID: 026_add_interview_leads
Revises: 025_add_survey_responses
"""
from alembic import op
import sqlalchemy as sa

from app.models.types import GUID, UTCDateTime

revision = "026_add_interview_leads"
down_revision = "025_add_survey_responses"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "interview_leads",
        sa.Column("id", GUID(), nullable=False),
        sa.Column("survey_key", sa.String(length=40), nullable=False),
        sa.Column("contact", sa.String(length=120), nullable=False),
        sa.Column("source", sa.String(length=40), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="new"),
        sa.Column("created_at", UTCDateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", UTCDateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_interview_leads_key_created", "interview_leads", ["survey_key", "created_at"])


def downgrade() -> None:
    op.drop_index("ix_interview_leads_key_created", table_name="interview_leads")
    op.drop_table("interview_leads")
