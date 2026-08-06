"""Binding business-metric SQL shared by marts and analytics services."""

ELIGIBLE_STATUS = "delivered"

ELIGIBLE_ORDER_TOTALS_CTE = """
eligible_order_totals AS (
    SELECT
        o.order_id,
        o.customer_id,
        c.customer_unique_id,
        o.purchase_ts,
        o.order_status,
        c.state,
        c.city,
        COALESCE(SUM(oi.price + oi.freight_value), 0)::numeric AS revenue,
        COUNT(oi.*)::integer AS item_count
    FROM curated.orders o
    JOIN curated.customers c ON c.customer_id = o.customer_id
    JOIN curated.order_items oi ON oi.order_id = o.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY o.order_id, o.customer_id, c.customer_unique_id,
             o.purchase_ts, o.order_status, c.state, c.city
)
"""

REVIEW_GRAIN_DEDUP_CTE = """
review_grain AS (
    SELECT DISTINCT ON (review_id)
        review_id,
        order_id,
        review_score,
        comment_title,
        comment_message,
        review_creation_ts,
        review_answer_ts
    FROM curated.reviews
    ORDER BY review_id, order_id
)
"""

ORDER_REVIEW_CTE = """
order_review AS (
    SELECT
        order_id,
        ROUND(AVG(review_score))::smallint AS review_score,
        COUNT(*)::integer AS review_links
    FROM curated.reviews
    GROUP BY order_id
)
"""


def with_ctes(*ctes: str) -> str:
    """Join reusable CTE fragments into one SQL WITH clause."""
    return "WITH " + ",\n".join(cte.strip() for cte in ctes)
