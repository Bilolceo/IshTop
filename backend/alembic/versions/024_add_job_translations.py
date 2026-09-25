"""Add jobs.translations — the listing text in the site's other language.

Revision ID: 024_add_job_translations
Revises: 023_add_job_alerts
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "024_add_job_translations"
down_revision = "023_add_job_alerts"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "jobs",
        sa.Column("translations", sa.JSON().with_variant(postgresql.JSONB(), "postgresql"), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("jobs", "translations")
