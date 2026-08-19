"""Atomically rebuild the Migration M2 marts from curated data."""

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
    "shipping_performance",
    "customer_profile",
    "customer_segments",
    "category_discount_profit",
    "kpi_snapshot",
)

TEMP_FACTS_SQL = f"""
CREATE TEMP TABLE order_facts ON COMMIT DROP AS
WITH {ELIGIBLE_ORDER_TOTALS_CTE}
SELECT * FROM eligible_order_totals
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
            date, revenue, total_profit, total_discount_value, order_count,
            customer_count, units, avg_discount_pct, profit_margin_pct
        )
        SELECT order_date, SUM(revenue), SUM(profit), SUM(discount_value),
               COUNT(DISTINCT order_id), COUNT(DISTINCT customer_id),
               SUM(quantity), AVG(discount_pct),
               100.0 * SUM(profit) / NULLIF(SUM(revenue), 0)
        FROM order_facts
        GROUP BY order_date
        """
    )
    await connection.execute(
        """
        INSERT INTO marts.revenue_by_category (
            date, category, sub_category, revenue, total_profit,
            total_discount_value, order_count, customer_count, units,
            avg_discount_pct, profit_margin_pct
        )
        SELECT order_date, category, sub_category, SUM(revenue), SUM(profit),
               SUM(discount_value), COUNT(DISTINCT order_id),
               COUNT(DISTINCT customer_id), SUM(quantity), AVG(discount_pct),
               100.0 * SUM(profit) / NULLIF(SUM(revenue), 0)
        FROM order_facts
        GROUP BY order_date, category, sub_category
        """
    )
    await connection.execute(
        """
        INSERT INTO marts.revenue_by_region (
            date, state, region, city_type, revenue, total_profit,
            total_discount_value, order_count, customer_count, units,
            avg_discount_pct, profit_margin_pct, latitude, longitude
        )
        SELECT f.order_date, f.state, f.region, f.city_type,
               SUM(f.revenue), SUM(f.profit), SUM(f.discount_value),
               COUNT(DISTINCT f.order_id), COUNT(DISTINCT f.customer_id),
               SUM(f.quantity), AVG(f.discount_pct),
               100.0 * SUM(f.profit) / NULLIF(SUM(f.revenue), 0),
               g.latitude, g.longitude
        FROM order_facts f
        JOIN curated.state_geocode g ON g.state = f.state
        GROUP BY f.order_date, f.state, f.region, f.city_type,
                 g.latitude, g.longitude
        """
    )
    await connection.execute(
        """
        INSERT INTO marts.shipping_performance (
            date, ship_mode, region, order_count, avg_shipping_days,
            median_shipping_days, min_shipping_days, max_shipping_days
        )
        SELECT order_date, ship_mode, region, COUNT(*)::integer,
               AVG(shipping_days::numeric),
               percentile_cont(0.5) WITHIN GROUP (ORDER BY shipping_days),
               MIN(shipping_days), MAX(shipping_days)
        FROM order_facts
        WHERE ship_mode IS NOT NULL AND shipping_days IS NOT NULL
        GROUP BY order_date, ship_mode, region
        """
    )
    await connection.execute(
        """
        INSERT INTO marts.category_discount_profit (
            category, sub_category, discount_band, order_count, revenue,
            total_profit, avg_discount_pct, avg_profit_margin_pct
        )
        SELECT category, sub_category, discount_band, COUNT(*)::integer,
               SUM(revenue), SUM(profit), AVG(discount_pct),
               AVG(profit_margin_pct)
        FROM order_facts
        GROUP BY category, sub_category, discount_band
        """
    )
    await connection.execute(
        """
        INSERT INTO marts.kpi_snapshot (
            snapshot_id, generated_at, period_start, period_end,
            total_revenue, total_profit, total_orders, total_customers,
            average_order_value, average_discount_pct, profit_margin_pct,
            latest_month_revenue, latest_month_profit,
            revenue_mom_growth_pct, revenue_yoy_growth_pct
        )
        WITH monthly AS (
            SELECT date_trunc('month', order_date)::date AS month,
                   SUM(revenue)::numeric AS revenue,
                   SUM(profit)::numeric AS profit
            FROM order_facts GROUP BY 1
        ), bounds AS (
            SELECT MIN(order_date) AS period_start, MAX(order_date) AS period_end,
                   date_trunc('month', MAX(order_date))::date AS latest_month
            FROM order_facts
        ), totals AS (
            SELECT SUM(revenue) AS revenue, SUM(profit) AS profit,
                   COUNT(DISTINCT order_id)::integer AS orders,
                   COUNT(DISTINCT customer_id)::integer AS customers,
                   AVG(discount_pct) AS avg_discount_pct
            FROM order_facts
        )
        SELECT 1, CURRENT_TIMESTAMP, b.period_start, b.period_end,
               t.revenue, t.profit, t.orders, t.customers,
               t.revenue / NULLIF(t.orders, 0), t.avg_discount_pct,
               100.0 * t.profit / NULLIF(t.revenue, 0),
               lm.revenue, lm.profit,
               100.0 * (lm.revenue - pm.revenue) / NULLIF(pm.revenue, 0),
               100.0 * (lm.revenue - ym.revenue) / NULLIF(ym.revenue, 0)
        FROM totals t CROSS JOIN bounds b
        JOIN monthly lm ON lm.month = b.latest_month
        LEFT JOIN monthly pm ON pm.month = b.latest_month - INTERVAL '1 month'
        LEFT JOIN monthly ym ON ym.month = b.latest_month - INTERVAL '1 year'
        """
    )
    for table in MART_TABLES:
        await connection.execute(f"ANALYZE marts.{table}")
    return {
        table: int(await connection.fetchval(f"SELECT COUNT(*) FROM marts.{table}"))
        for table in MART_TABLES
    }


async def build_marts() -> dict[str, int]:
    """Rebuild every M2 mart in one transaction and record the batch run."""
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
