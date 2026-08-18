"""Rebuild marts for Indian Store Data and the v2.2 zero-repeat design.

Revision ID: 20260818_0007
Revises: 20260817_0006
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260818_0007"
down_revision: str | None = "20260817_0006"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

OLD_MARTS = (
    "customer_profile",
    "customer_segments",
    "delivery_performance",
    "review_summary",
    "revenue_daily",
    "revenue_by_category",
    "revenue_by_region",
    "seller_performance",
    "payment_method_mix",
    "kpi_snapshot",
)

NEW_MARTS = (
    "customer_profile",
    "customer_segments",
    "revenue_daily",
    "revenue_by_category",
    "revenue_by_region",
    "shipping_performance",
    "category_discount_profit",
    "kpi_snapshot",
)


def _drop_tables(names: tuple[str, ...]) -> None:
    for name in names:
        op.drop_table(name, schema="marts")


def _financial_columns() -> list[sa.Column[object]]:
    return [
        sa.Column("revenue", sa.Numeric(), nullable=False),
        sa.Column("total_profit", sa.Numeric(), nullable=False),
        sa.Column("total_discount_value", sa.Numeric(), nullable=False),
        sa.Column("order_count", sa.Integer(), nullable=False),
        sa.Column("customer_count", sa.Integer(), nullable=False),
        sa.Column("units", sa.Integer(), nullable=False),
        sa.Column("avg_discount_pct", sa.Numeric(), nullable=False),
        sa.Column("profit_margin_pct", sa.Numeric(), nullable=False),
    ]


def upgrade() -> None:
    """Replace all Olist marts with Indian Store Data aggregates."""
    _drop_tables(OLD_MARTS)
    op.create_table(
        "customer_profile",
        sa.Column("customer_id", sa.String(), primary_key=True),
        sa.Column("order_date", sa.Date(), nullable=False),
        sa.Column("recency_days", sa.Integer(), nullable=False),
        sa.Column("order_value", sa.Numeric(), nullable=False),
        sa.Column("profit", sa.Numeric(), nullable=False),
        sa.Column("discount_pct", sa.Numeric(), nullable=False),
        sa.Column("segment", sa.String(), nullable=False),
        sa.Column("city_type", sa.String(), nullable=False),
        sa.Column("region", sa.String(), nullable=False),
        sa.Column("state", sa.String(), nullable=False),
        sa.Column("order_value_tier", sa.String(), nullable=False),
        schema="marts",
    )
    op.create_index(
        "ix_customer_profile_dimensions",
        "customer_profile",
        ["segment", "city_type", "region"],
        schema="marts",
    )
    op.create_index(
        "ix_customer_profile_order_value",
        "customer_profile",
        ["order_value"],
        schema="marts",
    )
    op.create_table(
        "customer_segments",
        sa.Column("segment", sa.String(), primary_key=True),
        sa.Column("order_value_tier", sa.String(), primary_key=True),
        sa.Column("city_type", sa.String(), primary_key=True),
        sa.Column("customer_count", sa.Integer(), nullable=False),
        sa.Column("avg_order_value", sa.Numeric(), nullable=False),
        sa.Column("avg_profit", sa.Numeric(), nullable=False),
        sa.Column("avg_discount_pct", sa.Numeric(), nullable=False),
        schema="marts",
    )
    op.create_table(
        "revenue_daily",
        sa.Column("date", sa.Date(), primary_key=True),
        *_financial_columns(),
        schema="marts",
    )
    op.create_table(
        "revenue_by_category",
        sa.Column("date", sa.Date(), primary_key=True),
        sa.Column("category", sa.String(), primary_key=True),
        sa.Column("sub_category", sa.String(), primary_key=True),
        *_financial_columns(),
        schema="marts",
    )
    op.create_index(
        "ix_revenue_category_date",
        "revenue_by_category",
        ["category", "sub_category", "date"],
        schema="marts",
    )
    op.create_table(
        "revenue_by_region",
        sa.Column("date", sa.Date(), primary_key=True),
        sa.Column("state", sa.String(), primary_key=True),
        sa.Column("region", sa.String(), primary_key=True),
        sa.Column("city_type", sa.String(), primary_key=True),
        *_financial_columns(),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        schema="marts",
    )
    op.create_index(
        "ix_revenue_region_date",
        "revenue_by_region",
        ["region", "state", "city_type", "date"],
        schema="marts",
    )
    op.create_table(
        "shipping_performance",
        sa.Column("date", sa.Date(), primary_key=True),
        sa.Column("ship_mode", sa.String(), primary_key=True),
        sa.Column("region", sa.String(), primary_key=True),
        sa.Column("order_count", sa.Integer(), nullable=False),
        sa.Column("avg_shipping_days", sa.Numeric(), nullable=False),
        sa.Column("median_shipping_days", sa.Numeric(), nullable=False),
        sa.Column("min_shipping_days", sa.Integer(), nullable=False),
        sa.Column("max_shipping_days", sa.Integer(), nullable=False),
        schema="marts",
    )
    op.create_index(
        "ix_shipping_performance_date",
        "shipping_performance",
        ["ship_mode", "region", "date"],
        schema="marts",
    )
    op.create_table(
        "category_discount_profit",
        sa.Column("category", sa.String(), primary_key=True),
        sa.Column("sub_category", sa.String(), primary_key=True),
        sa.Column("discount_band", sa.String(), primary_key=True),
        sa.Column("order_count", sa.Integer(), nullable=False),
        sa.Column("revenue", sa.Numeric(), nullable=False),
        sa.Column("total_profit", sa.Numeric(), nullable=False),
        sa.Column("avg_discount_pct", sa.Numeric(), nullable=False),
        sa.Column("avg_profit_margin_pct", sa.Numeric(), nullable=False),
        schema="marts",
    )
    op.create_index(
        "ix_category_discount_profit",
        "category_discount_profit",
        ["category", "sub_category", "discount_band"],
        schema="marts",
    )
    op.create_table(
        "kpi_snapshot",
        sa.Column("snapshot_id", sa.SmallInteger(), primary_key=True),
        sa.Column("generated_at", sa.DateTime(), nullable=False),
        sa.Column("period_start", sa.Date(), nullable=False),
        sa.Column("period_end", sa.Date(), nullable=False),
        sa.Column("total_revenue", sa.Numeric(), nullable=False),
        sa.Column("total_profit", sa.Numeric(), nullable=False),
        sa.Column("total_orders", sa.Integer(), nullable=False),
        sa.Column("total_customers", sa.Integer(), nullable=False),
        sa.Column("average_order_value", sa.Numeric(), nullable=False),
        sa.Column("average_discount_pct", sa.Numeric(), nullable=False),
        sa.Column("profit_margin_pct", sa.Numeric(), nullable=False),
        sa.Column("latest_month_revenue", sa.Numeric(), nullable=False),
        sa.Column("latest_month_profit", sa.Numeric(), nullable=False),
        sa.Column("revenue_mom_growth_pct", sa.Numeric()),
        sa.Column("revenue_yoy_growth_pct", sa.Numeric()),
        sa.CheckConstraint("snapshot_id = 1", name="ck_kpi_singleton"),
        schema="marts",
    )
    op.execute("GRANT SELECT ON ALL TABLES IN SCHEMA marts TO powerbi_reader")


def _legacy_dimensions() -> list[sa.Column[object]]:
    return [
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("state", sa.String(length=2)),
        sa.Column("city", sa.String()),
        sa.Column("category", sa.String()),
        sa.Column("seller_id", sa.String()),
        sa.Column("payment_type", sa.String()),
        sa.Column("customer_segment", sa.String()),
    ]


def downgrade() -> None:
    """Restore the immediately preceding Olist mart contract, without data."""
    _drop_tables(NEW_MARTS)
    op.create_table(
        "customer_profile",
        sa.Column("customer_unique_id", sa.String(), primary_key=True),
        sa.Column("first_order_ts", sa.DateTime()),
        sa.Column("last_order_ts", sa.DateTime()),
        sa.Column("order_count", sa.Integer(), nullable=False),
        sa.Column("total_spend", sa.Numeric(), nullable=False),
        sa.Column("primary_state", sa.String(length=2)),
        sa.Column("primary_city", sa.String()),
        sa.Column("recency_score", sa.SmallInteger(), nullable=False),
        sa.Column("frequency_score", sa.SmallInteger(), nullable=False),
        sa.Column("monetary_score", sa.SmallInteger(), nullable=False),
        sa.Column("rfm_segment", sa.String(), nullable=False),
        sa.Column("clv_historical", sa.Numeric(), nullable=False),
        schema="marts",
    )
    op.create_index(
        "ix_customer_profile_segment",
        "customer_profile",
        ["rfm_segment"],
        schema="marts",
    )
    op.create_index(
        "ix_customer_profile_region",
        "customer_profile",
        ["primary_state", "primary_city"],
        schema="marts",
    )
    op.create_index(
        "ix_customer_profile_clv_historical",
        "customer_profile",
        ["clv_historical"],
        schema="marts",
    )
    op.create_table(
        "customer_segments",
        sa.Column("segment", sa.String(), primary_key=True),
        sa.Column("customer_count", sa.Integer(), nullable=False),
        sa.Column("avg_clv", sa.Numeric(), nullable=False),
        sa.Column("avg_order_count", sa.Numeric(), nullable=False),
        schema="marts",
    )
    op.create_table(
        "delivery_performance",
        sa.Column("review_score", sa.SmallInteger()),
        sa.Column("order_status", sa.String(), nullable=False),
        sa.Column("order_count", sa.Integer(), nullable=False),
        sa.Column("delivered_count", sa.Integer(), nullable=False),
        sa.Column("late_count", sa.Integer(), nullable=False),
        sa.Column("avg_delivery_days", sa.Numeric()),
        sa.Column("avg_delivery_delay_days", sa.Numeric()),
        *_legacy_dimensions(),
        schema="marts",
    )
    op.create_table(
        "review_summary",
        sa.Column("review_score", sa.SmallInteger(), nullable=False),
        sa.Column("review_count", sa.Integer(), nullable=False),
        sa.Column("avg_review_score", sa.Numeric(), nullable=False),
        sa.Column("comments_with_text", sa.Integer(), nullable=False),
        *_legacy_dimensions(),
        schema="marts",
    )
    op.create_table(
        "revenue_daily",
        sa.Column("date", sa.Date(), primary_key=True),
        sa.Column("revenue", sa.Numeric(), nullable=False),
        sa.Column("order_count", sa.Integer(), nullable=False),
        sa.Column("customer_count", sa.Integer(), nullable=False),
        sa.Column("item_count", sa.Integer(), nullable=False),
        schema="marts",
    )
    op.create_table(
        "revenue_by_category",
        sa.Column("date", sa.Date(), primary_key=True),
        sa.Column("category", sa.String(), primary_key=True),
        sa.Column("revenue", sa.Numeric(), nullable=False),
        sa.Column("order_count", sa.Integer(), nullable=False),
        sa.Column("customer_count", sa.Integer(), nullable=False),
        sa.Column("units", sa.Integer(), nullable=False),
        schema="marts",
    )
    op.create_table(
        "revenue_by_region",
        sa.Column("date", sa.Date(), primary_key=True),
        sa.Column("state", sa.String(length=2), primary_key=True),
        sa.Column("city", sa.String(), primary_key=True),
        sa.Column("revenue", sa.Numeric(), nullable=False),
        sa.Column("order_count", sa.Integer(), nullable=False),
        sa.Column("customer_count", sa.Integer(), nullable=False),
        sa.Column("latitude", sa.Float()),
        sa.Column("longitude", sa.Float()),
        schema="marts",
    )
    op.create_table(
        "seller_performance",
        sa.Column("date", sa.Date(), primary_key=True),
        sa.Column("seller_id", sa.String(), primary_key=True),
        sa.Column("revenue", sa.Numeric(), nullable=False),
        sa.Column("order_count", sa.Integer(), nullable=False),
        sa.Column("units", sa.Integer(), nullable=False),
        sa.Column("avg_review_score", sa.Numeric()),
        schema="marts",
    )
    op.create_table(
        "payment_method_mix",
        sa.Column("date", sa.Date(), primary_key=True),
        sa.Column("payment_type", sa.String(), primary_key=True),
        sa.Column("payment_count", sa.Integer(), nullable=False),
        sa.Column("order_count", sa.Integer(), nullable=False),
        sa.Column("payment_value", sa.Numeric(), nullable=False),
        sa.Column("avg_installments", sa.Numeric()),
        schema="marts",
    )
    op.create_table(
        "kpi_snapshot",
        sa.Column("snapshot_id", sa.SmallInteger(), primary_key=True),
        sa.Column("generated_at", sa.DateTime(), nullable=False),
        sa.Column("period_start", sa.Date(), nullable=False),
        sa.Column("period_end", sa.Date(), nullable=False),
        sa.Column("total_revenue", sa.Numeric(), nullable=False),
        sa.Column("total_orders", sa.Integer(), nullable=False),
        sa.Column("total_customers", sa.Integer(), nullable=False),
        sa.Column("average_order_value", sa.Numeric(), nullable=False),
        sa.Column("latest_month_revenue", sa.Numeric(), nullable=False),
        sa.Column("revenue_mom_growth_pct", sa.Numeric()),
        sa.Column("revenue_yoy_growth_pct", sa.Numeric()),
        sa.CheckConstraint("snapshot_id = 1", name="ck_kpi_singleton"),
        schema="marts",
    )
