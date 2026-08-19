"""Engineer the canonical Migration M4 order features.

Revision ID: 20260819_0008
Revises: 20260818_0007
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260819_0008"
down_revision: str | None = "20260818_0007"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add only M3-supported features and retire the unsupported delay flag."""
    op.drop_column("orders", "is_delayed_shipment", schema="curated")
    op.add_column(
        "orders",
        sa.Column("profit_margin_pct", sa.Numeric(), nullable=True),
        schema="curated",
    )
    op.add_column(
        "orders",
        sa.Column("discount_band", sa.String(), nullable=True),
        schema="curated",
    )
    op.add_column(
        "orders",
        sa.Column("is_high_profit_order", sa.Boolean(), nullable=True),
        schema="curated",
    )
    op.add_column(
        "orders",
        sa.Column("order_month", sa.Integer(), nullable=True),
        schema="curated",
    )
    op.add_column(
        "orders", sa.Column("order_year", sa.Integer(), nullable=True), schema="curated"
    )
    op.add_column(
        "orders", sa.Column("order_dow", sa.Integer(), nullable=True), schema="curated"
    )
    op.execute(
        """
        WITH bounds AS (
            SELECT percentile_cont(0.25) WITHIN GROUP (ORDER BY discount_pct) AS discount_q1,
                   percentile_cont(0.50) WITHIN GROUP (ORDER BY discount_pct) AS discount_median,
                   percentile_cont(0.75) WITHIN GROUP (ORDER BY discount_pct) AS discount_q3,
                   percentile_cont(0.75) WITHIN GROUP (ORDER BY profit) AS profit_q3
            FROM curated.orders
        )
        UPDATE curated.orders AS orders
        SET profit_margin_pct = 100.0 * orders.profit / orders.sales,
            discount_band = CASE
                WHEN orders.discount_pct <= bounds.discount_q1 THEN 'low'
                WHEN orders.discount_pct < bounds.discount_median THEN 'medium_low'
                WHEN orders.discount_pct < bounds.discount_q3 THEN 'medium_high'
                ELSE 'high'
            END,
            is_high_profit_order = orders.profit >= bounds.profit_q3,
            order_month = EXTRACT(MONTH FROM orders.order_date)::integer,
            order_year = EXTRACT(YEAR FROM orders.order_date)::integer,
            order_dow = EXTRACT(ISODOW FROM orders.order_date)::integer
        FROM bounds
        """
    )
    for column in (
        "profit_margin_pct",
        "discount_band",
        "is_high_profit_order",
        "order_month",
        "order_year",
        "order_dow",
    ):
        op.alter_column("orders", column, schema="curated", nullable=False)
    op.create_check_constraint(
        "ck_orders_discount_band",
        "orders",
        "discount_band IN ('low','medium_low','medium_high','high')",
        schema="curated",
    )
    op.create_check_constraint(
        "ck_orders_order_month",
        "orders",
        "order_month BETWEEN 1 AND 12",
        schema="curated",
    )
    op.create_check_constraint(
        "ck_orders_order_dow",
        "orders",
        "order_dow BETWEEN 1 AND 7",
        schema="curated",
    )
    op.create_index(
        "ix_orders_discount_band", "orders", ["discount_band"], schema="curated"
    )
    op.create_index(
        "ix_orders_high_profit",
        "orders",
        ["is_high_profit_order"],
        schema="curated",
    )
    op.create_index(
        "ix_orders_calendar_features",
        "orders",
        ["order_year", "order_month", "order_dow"],
        schema="curated",
    )


def downgrade() -> None:
    """Restore the pre-M4 placeholder contract."""
    op.drop_index("ix_orders_calendar_features", table_name="orders", schema="curated")
    op.drop_index("ix_orders_high_profit", table_name="orders", schema="curated")
    op.drop_index("ix_orders_discount_band", table_name="orders", schema="curated")
    op.drop_constraint("ck_orders_order_dow", "orders", schema="curated", type_="check")
    op.drop_constraint(
        "ck_orders_order_month", "orders", schema="curated", type_="check"
    )
    op.drop_constraint(
        "ck_orders_discount_band", "orders", schema="curated", type_="check"
    )
    for column in (
        "order_dow",
        "order_year",
        "order_month",
        "is_high_profit_order",
        "discount_band",
        "profit_margin_pct",
    ):
        op.drop_column("orders", column, schema="curated")
    op.add_column(
        "orders",
        sa.Column("is_delayed_shipment", sa.Boolean(), nullable=True),
        schema="curated",
    )
