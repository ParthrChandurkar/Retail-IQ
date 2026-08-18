"""Cross-sectional customer mart population for the zero-repeat dataset."""

from typing import Any

from asyncpg import Connection

from app.services.dataframes import json_safe, query_frame

CUSTOMER_PROFILE_SQL = """
WITH source AS (
    SELECT c.customer_id, o.order_id, o.order_date,
           (MAX(o.order_date) OVER () - o.order_date)::integer AS recency_days,
           o.sales::numeric AS order_value, o.profit::numeric AS profit,
           o.discount_pct::numeric AS discount_pct, c.segment, c.city_type,
           sr.region, c.state,
           ntile(4) OVER (ORDER BY o.sales, o.order_id) AS value_quartile
    FROM curated.customers c
    JOIN curated.orders o ON o.customer_id = c.customer_id
    JOIN curated.state_region_reference sr ON sr.state = c.state
)
INSERT INTO marts.customer_profile (
    customer_id, order_date, recency_days, order_value, profit, discount_pct,
    segment, city_type, region, state, order_value_tier
)
SELECT customer_id, order_date, recency_days, order_value, profit, discount_pct,
       segment, city_type, region, state,
       CASE value_quartile
           WHEN 1 THEN 'Q1 - Lowest'
           WHEN 2 THEN 'Q2 - Lower-Middle'
           WHEN 3 THEN 'Q3 - Upper-Middle'
           ELSE 'Q4 - Highest'
       END
FROM source
"""


async def populate_customer_marts(connection: Connection) -> None:
    """Populate customer profiles and their real dimensional segmentation."""
    await connection.execute(CUSTOMER_PROFILE_SQL)
    await connection.execute(
        """
        INSERT INTO marts.customer_segments (
            segment, order_value_tier, city_type, customer_count,
            avg_order_value, avg_profit, avg_discount_pct
        )
        SELECT segment, order_value_tier, city_type, COUNT(*)::integer,
               AVG(order_value), AVG(profit), AVG(discount_pct)
        FROM marts.customer_profile
        GROUP BY segment, order_value_tier, city_type
        """
    )


async def customer_analytics() -> dict[str, Any]:
    """Return cross-sectional evidence without RFM or CLV claims."""
    overview = await query_frame(
        """
        SELECT COUNT(*) AS customers, AVG(order_value) AS avg_order_value,
               percentile_cont(0.5) WITHIN GROUP (ORDER BY order_value)
                   AS median_order_value,
               AVG(profit) AS avg_profit, AVG(discount_pct) AS avg_discount_pct
        FROM marts.customer_profile
        """
    )
    segments = await query_frame(
        """
        SELECT segment, order_value_tier, city_type, customer_count,
               avg_order_value, avg_profit, avg_discount_pct
        FROM marts.customer_segments
        ORDER BY segment, order_value_tier, city_type
        """
    )
    return {
        "overview": {key: json_safe(value) for key, value in overview.iloc[0].items()},
        "segments": segments.to_dict(orient="records"),
        "method": {
            "grain": "One customer equals one order in this source.",
            "segmentation": "Given segment crossed with data-derived order-value quartiles and city type.",
            "retired": "RFM Frequency, monetary-over-time, repeat purchase, and CLV are not supported.",
        },
    }
