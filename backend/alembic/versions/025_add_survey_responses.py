"""Add survey_responses table for problem-validation surveys.

Revision ID: 025_add_survey_responses
Revises: 024_add_job_translations
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from app.models.types import GUID, UTCDateTime

revision = "025_add_survey_responses"
down_revision = "024_add_job_translations"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "survey_responses",
        sa.Column("id", GUID(), nullable=False),
        sa.Column("survey_key", sa.String(length=40), nullable=False),
        sa.Column("user_id", GUID(), nullable=True),
        sa.Column("answers", sa.JSON().with_variant(postgresql.JSONB(), "postgresql"), nullable=False),
        sa.Column("source", sa.String(length=40), nullable=True),
        sa.Column("ip_hash", sa.String(length=32), nullable=True),
        sa.Column("created_at", UTCDateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", UTCDateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_survey_responses_key_created", "survey_responses", ["survey_key", "created_at"])
    op.create_index("ix_survey_responses_user_id", "survey_responses", ["user_id"])
    op.create_index("ix_survey_responses_ip_hash", "survey_responses", ["ip_hash"])


def downgrade() -> None:
    op.drop_index("ix_survey_responses_ip_hash", table_name="survey_responses")
    op.drop_index("ix_survey_responses_user_id", table_name="survey_responses")
    op.drop_index("ix_survey_responses_key_created", table_name="survey_responses")
    op.drop_table("survey_responses")
