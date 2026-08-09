"""refactor dashboard marts to endpoint-specific grains

Revision ID: 20260809_0002
Revises: e2e0c9b8f4f2
Create Date: 2026-08-09 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260809_0002"
down_revision: str | None = "e2e0c9b8f4f2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

MARTS = (
    "revenue_daily",
    "revenue_by_category",
    "revenue_by_region",
    "seller_performance",
    "payment_method_mix",
)


def _drop_affected_marts() -> None:
    for table in reversed(MARTS):
        op.drop_table(table, schema="marts")


def _create_refactored_marts() -> None:
    op.create_table(
        "revenue_daily",
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("revenue", sa.Numeric(), nullable=False),
        sa.Column("order_count", sa.Integer(), nullable=False),
        sa.Column("customer_count", sa.Integer(), nullable=False),
        sa.Column("item_count", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("date"),
        schema="marts",
    )
    op.create_table(
        "revenue_by_category",
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("category", sa.String(), nullable=False),
        sa.Column("revenue", sa.Numeric(), nullable=False),
        sa.Column("order_count", sa.Integer(), nullable=False),
        sa.Column("customer_count", sa.Integer(), nullable=False),
        sa.Column("units", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("date", "category"),
        schema="marts",
    )
    op.create_index(
        "ix_revenue_category_date",
        "revenue_by_category",
        ["category", "date"],
        schema="marts",
    )
    op.create_table(
        "revenue_by_region",
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("state", sa.String(length=2), nullable=False),
        sa.Column("city", sa.String(), nullable=False),
        sa.Column("revenue", sa.Numeric(), nullable=False),
        sa.Column("order_count", sa.Integer(), nullable=False),
        sa.Column("customer_count", sa.Integer(), nullable=False),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint("date", "state", "city"),
        schema="marts",
    )
    op.create_index(
        "ix_revenue_region_date",
        "revenue_by_region",
        ["state", "city", "date"],
        schema="marts",
    )
    op.create_table(
        "seller_performance",
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("seller_id", sa.String(), nullable=False),
        sa.Column("revenue", sa.Numeric(), nullable=False),
        sa.Column("order_count", sa.Integer(), nullable=False),
        sa.Column("units", sa.Integer(), nullable=False),
        sa.Column("avg_review_score", sa.Numeric(), nullable=True),
        sa.PrimaryKeyConstraint("date", "seller_id"),
        schema="marts",
    )
    op.create_index(
        "ix_seller_performance_date",
        "seller_performance",
        ["seller_id", "date"],
        schema="marts",
    )
    op.create_table(
        "payment_method_mix",
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("payment_type", sa.String(), nullable=False),
        sa.Column("payment_count", sa.Integer(), nullable=False),
        sa.Column("order_count", sa.Integer(), nullable=False),
        sa.Column("payment_value", sa.Numeric(), nullable=False),
        sa.Column("avg_installments", sa.Numeric(), nullable=True),
        sa.PrimaryKeyConstraint("date", "payment_type"),
        schema="marts",
    )
    op.create_index(
        "ix_payment_mix_date",
        "payment_method_mix",
        ["payment_type", "date"],
        schema="marts",
    )


def _legacy_dimension_columns() -> list[sa.Column]:
    return [
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("state", sa.String(length=2), nullable=True),
        sa.Column("city", sa.String(), nullable=True),
        sa.Column("category", sa.String(), nullable=True),
        sa.Column("seller_id", sa.String(), nullable=True),
        sa.Column("payment_type", sa.String(), nullable=True),
        sa.Column("customer_segment", sa.String(), nullable=True),
    ]


def _create_legacy_marts() -> None:
    op.create_table(
        "revenue_daily",
        sa.Column("revenue", sa.Numeric(), nullable=False),
        sa.Column("order_count", sa.Integer(), nullable=False),
        sa.Column("customer_count", sa.Integer(), nullable=False),
        sa.Column("item_count", sa.Integer(), nullable=False),
        *_legacy_dimension_columns(),
        sa.PrimaryKeyConstraint("id"),
        schema="marts",
    )
    op.create_index(
        "ix_revenue_daily_filters",
        "revenue_daily",
        ["date", "state", "category"],
        schema="marts",
    )
    op.create_table(
        "revenue_by_category",
        sa.Column("revenue", sa.Numeric(), nullable=False),
        sa.Column("order_count", sa.Integer(), nullable=False),
        sa.Column("customer_count", sa.Integer(), nullable=False),
        sa.Column("units", sa.Integer(), nullable=False),
        *_legacy_dimension_columns(),
        sa.PrimaryKeyConstraint("id"),
        schema="marts",
    )
    op.create_index(
        "ix_revenue_category_filters",
        "revenue_by_category",
        ["category", "date"],
        schema="marts",
    )
    op.create_table(
        "revenue_by_region",
        sa.Column("revenue", sa.Numeric(), nullable=False),
        sa.Column("order_count", sa.Integer(), nullable=False),
        sa.Column("customer_count", sa.Integer(), nullable=False),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        *_legacy_dimension_columns(),
        sa.PrimaryKeyConstraint("id"),
        schema="marts",
    )
    op.create_index(
        "ix_revenue_region_filters",
        "revenue_by_region",
        ["state", "city", "date"],
        schema="marts",
    )
    op.create_table(
        "seller_performance",
        sa.Column("revenue", sa.Numeric(), nullable=False),
        sa.Column("order_count", sa.Integer(), nullable=False),
        sa.Column("units", sa.Integer(), nullable=False),
        sa.Column("avg_review_score", sa.Numeric(), nullable=True),
        *_legacy_dimension_columns(),
        sa.PrimaryKeyConstraint("id"),
        schema="marts",
    )
    op.create_index(
        "ix_seller_performance_filters",
        "seller_performance",
        ["seller_id", "date"],
        schema="marts",
    )
    op.create_table(
        "payment_method_mix",
        sa.Column("payment_count", sa.Integer(), nullable=False),
        sa.Column("order_count", sa.Integer(), nullable=False),
        sa.Column("payment_value", sa.Numeric(), nullable=False),
        sa.Column("avg_installments", sa.Numeric(), nullable=True),
        *_legacy_dimension_columns(),
        sa.PrimaryKeyConstraint("id"),
        schema="marts",
    )
    op.create_index(
        "ix_payment_mix_filters",
        "payment_method_mix",
        ["payment_type", "date"],
        schema="marts",
    )


def upgrade() -> None:
    """Replace near-fact cubes with endpoint-specific aggregate marts."""
    _drop_affected_marts()
    _create_refactored_marts()


def downgrade() -> None:
    """Restore the Phase 3 wide-cube schemas without derived data."""
    _drop_affected_marts()
    _create_legacy_marts()
