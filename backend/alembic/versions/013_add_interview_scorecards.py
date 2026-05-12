"""Add interview_scorecards table.

Stores per-application interview evaluation: 5 criteria scored 1-5 each plus
notes + decision. Used by HR to standardise evaluation and reduce bias.

Revision ID: 013_add_interview_scorecards
Revises: 012_add_application_match_breakdown
Create Date: 2026-05-12
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect
from app.models.types import GUID


revision = "013_add_interview_scorecards"
down_revision = "012_add_application_match_breakdown"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    if "interview_scorecards" in inspector.get_table_names():
        return

    op.create_table(
        "interview_scorecards",
        sa.Column("id", GUID(), primary_key=True),
        sa.Column("application_id", GUID(), sa.ForeignKey("applications.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("evaluator_id", GUID(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),

        # 5 criteria, each scored 1-5
        sa.Column("technical_score", sa.Integer, nullable=True),
        sa.Column("communication_score", sa.Integer, nullable=True),
        sa.Column("cultural_fit_score", sa.Integer, nullable=True),
        sa.Column("motivation_score", sa.Integer, nullable=True),
        sa.Column("problem_solving_score", sa.Integer, nullable=True),

        # Aggregate + decision
        sa.Column("overall_score", sa.Float, nullable=True),
        sa.Column("recommendation", sa.String(length=20), nullable=True),  # hire | maybe | pass
        sa.Column("notes", sa.Text, nullable=True),

        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )

    # `index=True` on the column already creates an index; no extra call needed.


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    if "interview_scorecards" not in inspector.get_table_names():
        return
    try:
        op.drop_index("ix_interview_scorecards_application_id", table_name="interview_scorecards")
    except Exception:
        pass
    op.drop_table("interview_scorecards")
