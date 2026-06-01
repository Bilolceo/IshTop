"""add admin_notifications table

Revision ID: 016_add_admin_notifications
Revises: 015_add_audit_log
Create Date: 2026-05-31
"""

from alembic import op
import sqlalchemy as sa

revision = "016_add_admin_notifications"
down_revision = "015_add_audit_log"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "admin_notifications",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "admin_id",
            sa.String(36),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column("type", sa.String(100), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("link", sa.String(500), nullable=True),
        sa.Column("is_read", sa.Boolean(), default=False, nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_admin_notifications_admin_id", "admin_notifications", ["admin_id"])
    op.create_index("ix_admin_notifications_is_read", "admin_notifications", ["is_read"])


def downgrade():
    op.drop_index("ix_admin_notifications_is_read", "admin_notifications")
    op.drop_index("ix_admin_notifications_admin_id", "admin_notifications")
    op.drop_table("admin_notifications")
