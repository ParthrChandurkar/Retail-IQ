"""Add the Phase 8 CLV distribution performance index.

Revision ID: 20260812_0005
Revises: 20260810_0004
"""

from alembic import op

revision: str = "20260812_0005"
down_revision: str | None = "20260810_0004"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.execute(
        """CREATE INDEX IF NOT EXISTS ix_customer_profile_clv_historical
           ON marts.customer_profile (clv_historical)"""
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS marts.ix_customer_profile_clv_historical")
