"""Build all Phase 3 marts atomically from curated data."""

import asyncio
import json
from datetime import UTC, datetime

from asyncpg import Connection

from app.etl.database import connect
from app.services.customer_analytics_service import populate_customer_marts
from app.services.metrics import ELIGIBLE_ORDER_TOTALS_CTE

MART_TABLES = (
    "revenue_daily",
    "revenue_by_category",
    "revenue_by_region",
    "customer_profile",
    "customer_segments",
    "seller_performance",
    "payment_method_mix",
    "delivery_performance",
    "review_summary",
    "kpi_snapshot",
)


TEMP_FACTS_SQL = """
CREATE TEMP TABLE item_facts ON COMMIT DROP AS
WITH order_review AS (
    SELECT order_id, ROUND(AVG(review_score))::smallint AS review_score
    FROM curated.reviews
    GROUP BY order_id
)
SELECT o.purchase_ts::date AS date,
       c.state, c.city, c.latitude, c.longitude,
       COALESCE(p.category_name_english, p.category_name, 'unknown') AS category,
       oi.seller_id,
       ps.primary_payment_type AS payment_type,
       cp.rfm_segment AS customer_segment,
       rv.review_score,
       o.order_id, c.customer_unique_id,
       o.order_status, o.delivery_days, o.delivery_delay_days, o.is_late,
       oi.order_item_id, oi.price, oi.freight_value,
       (oi.price + oi.freight_value)::numeric AS revenue
FROM curated.orders o
JOIN curated.customers c ON c.customer_id = o.customer_id
JOIN curated.order_items oi ON oi.order_id = o.order_id
JOIN curated.products p ON p.product_id = oi.product_id
LEFT JOIN curated.payment_summary ps ON ps.order_id = o.order_id
LEFT JOIN marts.customer_profile cp ON cp.customer_unique_id = c.customer_unique_id
LEFT JOIN order_review rv ON rv.order_id = o.order_id
"""


async def _populate_marts(connection: Connection) -> dict[str, int]:
    await connection.execute(
        "TRUNCATE "
        + ", ".join(f"marts.{table}" for table in MART_TABLES)
        + " RESTART IDENTITY"
    )
    await populate_customer_marts(connection)
    await connection.execute(TEMP_FACTS_SQL)
    await connection.execute(
        """
        INSERT INTO marts.revenue_daily (
            date, revenue, order_count, customer_count, item_count
        )
        SELECT date, SUM(revenue), COUNT(DISTINCT order_id),
               COUNT(DISTINCT customer_unique_id), COUNT(*)
        FROM item_facts
        WHERE order_status = 'delivered'
        GROUP BY date
        """
    )
    await connection.execute(
        """
        INSERT INTO marts.revenue_by_category (
            date, category, revenue, order_count, customer_count, units
        )
        SELECT date, category, SUM(revenue), COUNT(DISTINCT order_id),
               COUNT(DISTINCT customer_unique_id), COUNT(*)
        FROM item_facts
        WHERE order_status = 'delivered'
        GROUP BY date, category
        """
    )
    await connection.execute(
        """
        INSERT INTO marts.revenue_by_region (
            date, state, city, revenue, order_count, customer_count,
            latitude, longitude
        )
        WITH coordinate_points AS (
            SELECT DISTINCT state, city, latitude, longitude
            FROM curated.customers
            WHERE state IS NOT NULL AND city IS NOT NULL
              AND latitude IS NOT NULL AND longitude IS NOT NULL
        ), city_coordinates AS (
            SELECT state, city,
                   percentile_cont(0.5) WITHIN GROUP (ORDER BY latitude)
                       AS latitude,
                   percentile_cont(0.5) WITHIN GROUP (ORDER BY longitude)
                       AS longitude
            FROM coordinate_points
            GROUP BY state, city
        ), regional_revenue AS (
            SELECT date, state, city, SUM(revenue) AS revenue,
                   COUNT(DISTINCT order_id) AS order_count,
                   COUNT(DISTINCT customer_unique_id) AS customer_count
            FROM item_facts
            WHERE order_status = 'delivered'
              AND state IS NOT NULL AND city IS NOT NULL
            GROUP BY date, state, city
        )
        SELECT revenue.date, revenue.state, revenue.city, revenue.revenue,
               revenue.order_count, revenue.customer_count,
               coordinates.latitude, coordinates.longitude
        FROM regional_revenue AS revenue
        LEFT JOIN city_coordinates AS coordinates
          ON coordinates.state = revenue.state
         AND coordinates.city = revenue.city
        """
    )
    await connection.execute(
        """
        INSERT INTO marts.seller_performance (
            date, seller_id, revenue, order_count, units, avg_review_score
        )
        WITH seller_orders AS (
            SELECT date, seller_id, order_id, SUM(revenue) AS revenue,
                   COUNT(*) AS units, MAX(review_score) AS review_score
            FROM item_facts
            WHERE order_status = 'delivered'
            GROUP BY date, seller_id, order_id
        )
        SELECT date, seller_id, SUM(revenue), COUNT(*), SUM(units),
               AVG(review_score::numeric)
        FROM seller_orders
        GROUP BY date, seller_id
        """
    )
    await connection.execute(
        """
        INSERT INTO marts.payment_method_mix (
            date, payment_type, payment_count, order_count, payment_value,
            avg_installments
        )
        SELECT o.purchase_ts::date, pd.payment_type, COUNT(*),
               COUNT(DISTINCT o.order_id), SUM(pd.payment_value),
               AVG(pd.payment_installments::numeric)
        FROM curated.payment_details pd
        JOIN curated.orders o ON o.order_id = pd.order_id
        WHERE o.order_status = 'delivered'
        GROUP BY o.purchase_ts::date, pd.payment_type
        """
    )
    await connection.execute(
        """
        INSERT INTO marts.delivery_performance (
            date, state, city, category, seller_id, payment_type,
            customer_segment, review_score, order_status, order_count,
            delivered_count, late_count, avg_delivery_days,
            avg_delivery_delay_days
        )
        SELECT date, state, city, category, seller_id, payment_type,
               customer_segment, review_score, order_status,
               COUNT(DISTINCT order_id),
               COUNT(DISTINCT order_id) FILTER (WHERE order_status = 'delivered'),
               COUNT(DISTINCT order_id) FILTER (WHERE is_late),
               AVG(delivery_days::numeric), AVG(delivery_delay_days::numeric)
        FROM item_facts
        GROUP BY date, state, city, category, seller_id, payment_type,
                 customer_segment, review_score, order_status
        """
    )
    await connection.execute(
        """
        INSERT INTO marts.review_summary (
            date, state, city, category, seller_id, payment_type,
            customer_segment, review_score, review_count, avg_review_score,
            comments_with_text
        )
        WITH review_grain AS (
            SELECT DISTINCT ON (review_id)
                review_id, order_id, review_score, comment_message,
                review_creation_ts
            FROM curated.reviews
            ORDER BY review_id, order_id
        )
        SELECT o.purchase_ts::date, c.state, c.city,
               COALESCE(p.category_name_english, p.category_name, 'unknown'),
               oi.seller_id, ps.primary_payment_type, cp.rfm_segment,
               rg.review_score, COUNT(DISTINCT rg.review_id),
               AVG(rg.review_score::numeric),
               COUNT(DISTINCT rg.review_id) FILTER (
                   WHERE rg.comment_message IS NOT NULL
               )
        FROM review_grain rg
        JOIN curated.orders o ON o.order_id = rg.order_id
        JOIN curated.customers c ON c.customer_id = o.customer_id
        JOIN curated.order_items oi ON oi.order_id = o.order_id
        JOIN curated.products p ON p.product_id = oi.product_id
        LEFT JOIN curated.payment_summary ps ON ps.order_id = o.order_id
        LEFT JOIN marts.customer_profile cp
          ON cp.customer_unique_id = c.customer_unique_id
        GROUP BY o.purchase_ts::date, c.state, c.city,
                 COALESCE(p.category_name_english, p.category_name, 'unknown'),
                 oi.seller_id, ps.primary_payment_type, cp.rfm_segment,
                 rg.review_score
        """
    )
    await connection.execute(
        f"""
        INSERT INTO marts.kpi_snapshot (
            snapshot_id, generated_at, period_start, period_end,
            total_revenue, total_orders, total_customers,
            average_order_value, latest_month_revenue,
            revenue_mom_growth_pct, revenue_yoy_growth_pct
        )
        WITH {ELIGIBLE_ORDER_TOTALS_CTE}, monthly AS (
            SELECT date_trunc('month', purchase_ts)::date AS month,
                   SUM(revenue)::numeric AS revenue
            FROM eligible_order_totals GROUP BY 1
        ), bounds AS (
            SELECT MIN(purchase_ts)::date AS period_start,
                   MAX(purchase_ts)::date AS period_end,
                   date_trunc('month', MAX(purchase_ts))::date AS latest_month
            FROM eligible_order_totals
        )
        SELECT 1, CURRENT_TIMESTAMP, b.period_start, b.period_end,
               SUM(ot.revenue), COUNT(DISTINCT ot.order_id),
               COUNT(DISTINCT ot.customer_unique_id),
               SUM(ot.revenue) / NULLIF(COUNT(DISTINCT ot.order_id), 0),
               lm.revenue,
               100 * (lm.revenue - pm.revenue) / NULLIF(pm.revenue, 0),
               100 * (lm.revenue - ym.revenue) / NULLIF(ym.revenue, 0)
        FROM eligible_order_totals ot CROSS JOIN bounds b
        JOIN monthly lm ON lm.month = b.latest_month
        LEFT JOIN monthly pm ON pm.month = b.latest_month - INTERVAL '1 month'
        LEFT JOIN monthly ym ON ym.month = b.latest_month - INTERVAL '1 year'
        GROUP BY b.period_start, b.period_end, lm.revenue, pm.revenue, ym.revenue
        """
    )
    for table in MART_TABLES:
        await connection.execute(f"ANALYZE marts.{table}")
    return {
        table: int(await connection.fetchval(f"SELECT COUNT(*) FROM marts.{table}"))
        for table in MART_TABLES
    }


async def build_marts() -> dict[str, int]:
    """Rebuild every mart in one transaction and append an audit record."""
    connection = await connect()
    started_at = datetime.now(UTC).replace(tzinfo=None)
    log_id = int(
        await connection.fetchval(
            """
            INSERT INTO curated.data_refresh_log (job_name, started_at, status)
            VALUES ('marts_build', $1, 'running') RETURNING id
            """,
            started_at,
        )
    )
    try:
        async with connection.transaction():
            counts = await _populate_marts(connection)
        await connection.execute(
            """
            UPDATE curated.data_refresh_log
            SET finished_at=$1, status='success', rows_affected=$2
            WHERE id=$3
            """,
            datetime.now(UTC).replace(tzinfo=None),
            sum(counts.values()),
            log_id,
        )
        return counts
    except Exception as exc:
        await connection.execute(
            """
            UPDATE curated.data_refresh_log
            SET finished_at=$1, status='failed', error_message=$2 WHERE id=$3
            """,
            datetime.now(UTC).replace(tzinfo=None),
            str(exc),
            log_id,
        )
        raise
    finally:
        await connection.close()


async def main() -> None:
    print("MART_COUNTS=" + json.dumps(await build_marts(), sort_keys=True))


if __name__ == "__main__":
    asyncio.run(main())
