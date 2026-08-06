"""Customer RFM, historical CLV, segmentation, and repeat analytics."""

from typing import Any

from asyncpg import Connection

from app.services.dataframes import json_safe, query_frame
from app.services.metrics import ELIGIBLE_ORDER_TOTALS_CTE

CUSTOMER_PROFILE_SQL = f"""
WITH {ELIGIBLE_ORDER_TOTALS_CTE}, customer_orders AS (
    SELECT customer_unique_id, order_id, purchase_ts, state, city, revenue
    FROM eligible_order_totals
), customer_rollup AS (
    SELECT customer_unique_id,
           MIN(purchase_ts) AS first_order_ts,
           MAX(purchase_ts) AS last_order_ts,
           COUNT(DISTINCT order_id)::integer AS order_count,
           SUM(revenue)::numeric AS total_spend
    FROM customer_orders
    GROUP BY customer_unique_id
), region_counts AS (
    SELECT customer_unique_id, state, city, COUNT(*) AS region_order_count,
           ROW_NUMBER() OVER (
               PARTITION BY customer_unique_id
               ORDER BY COUNT(*) DESC, state NULLS LAST, city NULLS LAST
           ) AS region_rank
    FROM customer_orders
    GROUP BY customer_unique_id, state, city
), scored AS (
    SELECT cr.*, rc.state AS primary_state, rc.city AS primary_city,
           LEAST(5, FLOOR(PERCENT_RANK() OVER (
               ORDER BY cr.last_order_ts ASC
           ) * 5)::integer + 1) AS recency_score,
           LEAST(5, FLOOR(PERCENT_RANK() OVER (
               ORDER BY cr.order_count ASC
           ) * 5)::integer + 1) AS frequency_score,
           LEAST(5, FLOOR(PERCENT_RANK() OVER (
               ORDER BY cr.total_spend ASC
           ) * 5)::integer + 1) AS monetary_score
    FROM customer_rollup cr
    LEFT JOIN region_counts rc
      ON rc.customer_unique_id = cr.customer_unique_id AND rc.region_rank = 1
)
INSERT INTO marts.customer_profile (
    customer_unique_id, first_order_ts, last_order_ts, order_count,
    total_spend, primary_state, primary_city, recency_score,
    frequency_score, monetary_score, rfm_segment, clv_historical
)
SELECT customer_unique_id, first_order_ts, last_order_ts, order_count,
       total_spend, primary_state, primary_city, recency_score,
       frequency_score, monetary_score,
       CASE
           WHEN recency_score >= 4 AND frequency_score >= 4
                AND monetary_score >= 4 THEN 'Champions'
           WHEN recency_score >= 3 AND frequency_score >= 4 THEN 'Loyal'
           WHEN recency_score <= 2 AND frequency_score >= 3 THEN 'At Risk'
           WHEN recency_score >= 4 AND frequency_score = 1 THEN 'New'
           WHEN frequency_score >= 2 AND monetary_score >= 4 THEN 'Big Spenders'
           WHEN recency_score <= 2 AND frequency_score <= 2 THEN 'Hibernating'
           WHEN recency_score >= 3 AND frequency_score BETWEEN 2 AND 3
                THEN 'Potential Loyalists'
           ELSE 'Promising'
       END,
       total_spend
FROM scored
"""


async def populate_customer_marts(connection: Connection) -> None:
    """Populate customer_profile and its segment-grain derivative."""
    await connection.execute(CUSTOMER_PROFILE_SQL)
    await connection.execute(
        """
        INSERT INTO marts.customer_segments (
            segment, customer_count, avg_clv, avg_order_count
        )
        SELECT rfm_segment, COUNT(*)::integer, AVG(clv_historical),
               AVG(order_count::numeric)
        FROM marts.customer_profile
        GROUP BY rfm_segment
        """
    )


async def customer_analytics() -> dict[str, Any]:
    """Return the customer analytics evidence used by reports/notebooks."""
    overview = await query_frame(
        """
        SELECT COUNT(*) AS customers,
               COUNT(*) FILTER (WHERE order_count >= 2) AS repeat_customers,
               100.0 * COUNT(*) FILTER (WHERE order_count >= 2)
                   / NULLIF(COUNT(*), 0) AS repeat_purchase_rate_pct,
               AVG(order_count::numeric) AS avg_order_count,
               AVG(clv_historical) AS avg_clv,
               percentile_cont(0.5) WITHIN GROUP (
                   ORDER BY clv_historical
               ) AS median_clv
        FROM marts.customer_profile
        """
    )
    segments = await query_frame(
        """
        SELECT segment, customer_count, avg_clv, avg_order_count
        FROM marts.customer_segments ORDER BY customer_count DESC, segment
        """
    )
    gaps = await query_frame(
        """
        WITH delivered AS (
            SELECT c.customer_unique_id, o.purchase_ts,
                   LAG(o.purchase_ts) OVER (
                       PARTITION BY c.customer_unique_id ORDER BY o.purchase_ts
                   ) AS previous_purchase_ts
            FROM curated.orders o
            JOIN curated.customers c ON c.customer_id = o.customer_id
            WHERE o.order_status = 'delivered'
        )
        SELECT COUNT(*) FILTER (WHERE previous_purchase_ts IS NOT NULL) AS gaps,
               AVG(EXTRACT(EPOCH FROM purchase_ts - previous_purchase_ts)
                   / 86400.0) AS avg_days_between_orders,
               percentile_cont(0.5) WITHIN GROUP (
                   ORDER BY EXTRACT(EPOCH FROM purchase_ts - previous_purchase_ts)
                            / 86400.0
               ) FILTER (WHERE previous_purchase_ts IS NOT NULL)
                   AS median_days_between_orders
        FROM delivered
        """
    )
    regions = await query_frame(
        """
        SELECT primary_state AS state, COUNT(*) AS customers,
               AVG(order_count::numeric) AS avg_orders,
               AVG(clv_historical) AS avg_clv
        FROM marts.customer_profile
        GROUP BY primary_state ORDER BY customers DESC NULLS LAST
        """
    )
    return {
        "overview": {key: json_safe(value) for key, value in overview.iloc[0].items()},
        "segments": segments.to_dict(orient="records"),
        "time_between_orders": {
            key: json_safe(value) for key, value in gaps.iloc[0].items()
        },
        "regional_behavior": regions.to_dict(orient="records"),
        "rfm_method": {
            "scores": "Percent-rank quintiles, 1 (lowest) through 5 (highest); recency uses last purchase timestamp, so more recent is higher.",
            "clv": "Delivered-order item price plus freight, historical to date in BRL.",
            "segmentation": "Deterministic documented RFM rules; customer_segments is GROUP BY rfm_segment only.",
        },
    }
