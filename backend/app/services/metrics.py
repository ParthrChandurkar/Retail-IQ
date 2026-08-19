"""Binding Indian Store Data business metrics shared by mart builders."""

# There is no order-status field in the source, so every curated order is eligible.
ELIGIBLE_ORDER_TOTALS_CTE = """
eligible_order_totals AS (
    SELECT
        o.order_id,
        o.customer_id,
        o.product_id,
        o.order_date,
        o.ship_mode,
        o.shipping_days,
        o.quantity,
        o.sales::numeric AS revenue,
        o.profit::numeric AS profit,
        o.discount_pct::numeric AS discount_pct,
        (o.sales * o.discount_pct / 100.0)::numeric AS discount_value,
        o.profit_margin_pct::numeric AS profit_margin_pct,
        o.discount_band,
        o.is_high_profit_order,
        o.order_month,
        o.order_year,
        o.order_dow,
        c.segment,
        c.city_type,
        c.state,
        sr.region,
        p.category,
        p.sub_category
    FROM curated.orders o
    JOIN curated.customers c ON c.customer_id = o.customer_id
    JOIN curated.products p ON p.product_id = o.product_id
    JOIN curated.state_region_reference sr ON sr.state = c.state
)
"""


def with_ctes(*ctes: str) -> str:
    """Join reusable CTE fragments into one SQL WITH clause."""
    return "WITH " + ",\n".join(cte.strip() for cte in ctes)
