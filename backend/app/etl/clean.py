"""Transactional cleaning and canonical row features for Indian Store Data."""

import asyncpg

from app.etl.database import connect
from app.etl.feature_contract import discount_band_case

CURATED_ENTITY_TABLES = ("orders", "products", "customers")


async def _load_customers(connection: asyncpg.Connection) -> None:
    await connection.execute(
        """
        INSERT INTO curated.customers (
            customer_id, first_name, last_name, segment, postal_code,
            city_type, region_as_reported, state
        )
        SELECT DISTINCT ON (customer_id)
            customer_id, NULLIF(BTRIM(customer_name), ''),
            NULLIF(BTRIM(last_name), ''), BTRIM(segment), postal_code,
            BTRIM(city_type), BTRIM(region), BTRIM(state)
        FROM raw.store_transactions
        WHERE customer_id IS NOT NULL
          AND NULLIF(BTRIM(segment), '') IS NOT NULL
          AND NULLIF(BTRIM(city_type), '') IS NOT NULL
          AND NULLIF(BTRIM(region), '') IS NOT NULL
          AND NULLIF(BTRIM(state), '') IS NOT NULL
        ORDER BY customer_id
        """
    )


async def _load_products(connection: asyncpg.Connection) -> None:
    await connection.execute(
        """
        INSERT INTO curated.products (
            product_id, product_name, category, sub_category
        )
        SELECT DISTINCT ON (product_id)
            product_id, NULLIF(BTRIM(product_name), ''),
            BTRIM(category_of_goods), BTRIM(sub_category)
        FROM raw.store_transactions
        WHERE product_id IS NOT NULL
          AND NULLIF(BTRIM(category_of_goods), '') IS NOT NULL
          AND NULLIF(BTRIM(sub_category), '') IS NOT NULL
        ORDER BY product_id
        """
    )


async def _load_orders(connection: asyncpg.Connection) -> None:
    band_expression = discount_band_case(
        "source.discount * 100",
        "bounds.discount_q1",
        "bounds.discount_median",
        "bounds.discount_q3",
    )
    await connection.execute(
        f"""
        WITH valid_orders AS (
            SELECT DISTINCT ON (source.order_id)
                source.*,
                CASE WHEN source.ship_date IS NULL THEN NULL
                     ELSE source.ship_date - source.order_date
                END AS calculated_shipping_days
            FROM raw.store_transactions AS source
            JOIN curated.customers AS customer USING (customer_id)
            JOIN curated.products AS product USING (product_id)
            WHERE source.order_id IS NOT NULL
              AND source.order_date IS NOT NULL
              AND (source.ship_date IS NULL OR source.ship_date >= source.order_date)
              AND source.quantity IS NOT NULL AND source.quantity > 0
              AND source.sales IS NOT NULL AND source.sales > 0
              AND source.discount IS NOT NULL AND source.discount BETWEEN 0 AND 0.5
              AND source.profit IS NOT NULL
            ORDER BY source.order_id
        ), bounds AS (
            SELECT
                percentile_cont(0.25) WITHIN GROUP (ORDER BY sales) AS sales_q1,
                percentile_cont(0.75) WITHIN GROUP (ORDER BY sales) AS sales_q3,
                percentile_cont(0.25) WITHIN GROUP (ORDER BY profit) AS profit_q1,
                percentile_cont(0.75) WITHIN GROUP (ORDER BY profit) AS profit_q3,
                percentile_cont(0.25) WITHIN GROUP (
                    ORDER BY discount * 100
                ) AS discount_q1,
                percentile_cont(0.50) WITHIN GROUP (
                    ORDER BY discount * 100
                ) AS discount_median,
                percentile_cont(0.75) WITHIN GROUP (
                    ORDER BY discount * 100
                ) AS discount_q3
            FROM valid_orders
        )
        INSERT INTO curated.orders (
            order_id, customer_id, product_id, order_date, ship_date, ship_mode,
            shipping_days, quantity, sales, discount_pct, profit,
            profit_margin_pct, discount_band, is_high_profit_order,
            order_month, order_year, order_dow,
            is_sales_outlier, is_profit_outlier
        )
        SELECT
            source.order_id, source.customer_id, source.product_id,
            source.order_date, source.ship_date, NULLIF(BTRIM(source.ship_mode), ''),
            source.calculated_shipping_days, source.quantity, source.sales,
            source.discount * 100, source.profit,
            100.0 * source.profit / source.sales,
            {band_expression},
            source.profit >= bounds.profit_q3,
            EXTRACT(MONTH FROM source.order_date)::integer,
            EXTRACT(YEAR FROM source.order_date)::integer,
            EXTRACT(ISODOW FROM source.order_date)::integer,
            source.sales < bounds.sales_q1 - 1.5 * (bounds.sales_q3 - bounds.sales_q1)
              OR source.sales > bounds.sales_q3 + 1.5 * (bounds.sales_q3 - bounds.sales_q1),
            source.profit < bounds.profit_q1 - 1.5 * (bounds.profit_q3 - bounds.profit_q1)
              OR source.profit > bounds.profit_q3 + 1.5 * (bounds.profit_q3 - bounds.profit_q1)
        FROM valid_orders AS source
        CROSS JOIN bounds
        """
    )


async def clean_curated() -> dict[str, int]:
    """Atomically rebuild dataset-dependent curated entities and M4 features."""
    connection = await connect()
    try:
        async with connection.transaction():
            await connection.execute(
                "TRUNCATE TABLE curated.orders, curated.products, curated.customers"
            )
            await _load_customers(connection)
            await _load_products(connection)
            await _load_orders(connection)
            counts = {
                name: int(
                    await connection.fetchval(f'SELECT COUNT(*) FROM curated."{name}"')
                )
                for name in CURATED_ENTITY_TABLES
            }
            counts["state_geocode"] = int(
                await connection.fetchval("SELECT COUNT(*) FROM curated.state_geocode")
            )
            counts["state_region_reference"] = int(
                await connection.fetchval(
                    "SELECT COUNT(*) FROM curated.state_region_reference"
                )
            )
    finally:
        await connection.close()
    return counts
