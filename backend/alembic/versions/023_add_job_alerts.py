"""Add job_alerts table for Telegram new-job alerts.

Revision ID: 023_add_job_alerts
Revises: 022_add_refresh_tokens
"""
from alembic import op
import sqlalchemy as sa

from app.models.types import GUID, UTCDateTime

revision = "023_add_job_alerts"
down_revision = "022_add_refresh_tokens"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "job_alerts",
        sa.Column("id", GUID(), nullable=False),
        sa.Column("chat_id", sa.String(length=32), nullable=False),
        sa.Column("user_id", GUID(), nullable=True),
        sa.Column("kind", sa.String(length=1), nullable=False),
        sa.Column("value", sa.String(length=40), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("last_checked_at", UTCDateTime(), nullable=False),
        sa.Column("last_sent_at", UTCDateTime(), nullable=True),
        sa.Column("sent_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", UTCDateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", UTCDateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("chat_id", "kind", "value", name="uq_job_alerts_chat_kind_value"),
    )
    op.create_index("ix_job_alerts_chat_id", "job_alerts", ["chat_id"])
    op.create_index("ix_job_alerts_user_id", "job_alerts", ["user_id"])
    op.create_index("ix_job_alerts_active", "job_alerts", ["is_active"])


def downgrade() -> None:
    op.drop_index("ix_job_alerts_active", table_name="job_alerts")
    op.drop_index("ix_job_alerts_user_id", table_name="job_alerts")
    op.drop_index("ix_job_alerts_chat_id", table_name="job_alerts")
    op.drop_table("job_alerts")
