"""Transactional raw-to-curated cleaning for Phase 2."""

import asyncpg

from app.etl.database import connect

CURATED_ENTITY_TABLES = (
    "reviews",
    "payment_summary",
    "payment_details",
    "order_items",
    "orders",
    "products",
    "sellers",
    "customers",
)


async def _create_geolocation_medians(connection: asyncpg.Connection) -> None:
    await connection.execute(
        """
        CREATE TEMP TABLE geo_medians ON COMMIT DROP AS
        SELECT
            geolocation_zip_code_prefix AS zip_code_prefix,
            percentile_cont(0.5) WITHIN GROUP (ORDER BY geolocation_lat) AS latitude,
            percentile_cont(0.5) WITHIN GROUP (ORDER BY geolocation_lng) AS longitude
        FROM raw.geolocation
        WHERE geolocation_zip_code_prefix IS NOT NULL
          AND geolocation_lat IS NOT NULL
          AND geolocation_lng IS NOT NULL
        GROUP BY geolocation_zip_code_prefix
        """
    )
    await connection.execute(
        "CREATE UNIQUE INDEX ix_geo_medians_zip ON geo_medians (zip_code_prefix)"
    )


async def _load_customers(connection: asyncpg.Connection) -> None:
    await connection.execute(
        """
        INSERT INTO curated.customers (
            customer_id, customer_unique_id, zip_code_prefix, city, state,
            latitude, longitude
        )
        SELECT DISTINCT ON (source.customer_id)
            source.customer_id,
            source.customer_unique_id,
            source.customer_zip_code_prefix,
            source.customer_city,
            source.customer_state,
            geo.latitude,
            geo.longitude
        FROM raw.customers AS source
        LEFT JOIN geo_medians AS geo
          ON geo.zip_code_prefix = source.customer_zip_code_prefix
        WHERE source.customer_id IS NOT NULL
          AND source.customer_unique_id IS NOT NULL
        ORDER BY source.customer_id
        """
    )


async def _load_products(connection: asyncpg.Connection) -> None:
    await connection.execute(
        """
        WITH translations AS (
            SELECT DISTINCT ON (product_category_name)
                product_category_name,
                product_category_name_english
            FROM raw.product_category_translation
            WHERE product_category_name IS NOT NULL
            ORDER BY product_category_name, product_category_name_english NULLS LAST
        )
        INSERT INTO curated.products (
            product_id, category_name, category_name_english,
            weight_g, length_cm, height_cm, width_cm
        )
        SELECT DISTINCT ON (source.product_id)
            source.product_id,
            source.product_category_name,
            translations.product_category_name_english,
            source.product_weight_g,
            source.product_length_cm,
            source.product_height_cm,
            source.product_width_cm
        FROM raw.products AS source
        LEFT JOIN translations
          ON translations.product_category_name = source.product_category_name
        WHERE source.product_id IS NOT NULL
        ORDER BY source.product_id
        """
    )


async def _load_sellers(connection: asyncpg.Connection) -> None:
    await connection.execute(
        """
        INSERT INTO curated.sellers (
            seller_id, zip_code_prefix, city, state, latitude, longitude
        )
        SELECT DISTINCT ON (source.seller_id)
            source.seller_id,
            source.seller_zip_code_prefix,
            source.seller_city,
            source.seller_state,
            geo.latitude,
            geo.longitude
        FROM raw.sellers AS source
        LEFT JOIN geo_medians AS geo
          ON geo.zip_code_prefix = source.seller_zip_code_prefix
        WHERE source.seller_id IS NOT NULL
        ORDER BY source.seller_id
        """
    )


async def _load_orders(connection: asyncpg.Connection) -> None:
    await connection.execute(
        """
        WITH valid_orders AS (
            SELECT DISTINCT ON (source.order_id)
                source.*,
                CASE
                    WHEN source.order_delivered_customer_date IS NULL THEN NULL
                    ELSE FLOOR(EXTRACT(EPOCH FROM (
                        source.order_delivered_customer_date
                        - source.order_purchase_timestamp
                    )) / 86400)::INTEGER
                END AS calculated_delivery_days
            FROM raw.orders AS source
            JOIN curated.customers AS customer
              ON customer.customer_id = source.customer_id
            WHERE source.order_id IS NOT NULL
              AND source.customer_id IS NOT NULL
              AND source.order_status IS NOT NULL
              AND source.order_purchase_timestamp IS NOT NULL
              AND (
                    source.order_delivered_customer_date IS NULL
                    OR source.order_delivered_customer_date
                       >= source.order_purchase_timestamp
              )
            ORDER BY source.order_id
        ),
        bounds AS (
            SELECT
                percentile_cont(0.25) WITHIN GROUP (
                    ORDER BY calculated_delivery_days
                ) AS q1,
                percentile_cont(0.75) WITHIN GROUP (
                    ORDER BY calculated_delivery_days
                ) AS q3
            FROM valid_orders
            WHERE calculated_delivery_days IS NOT NULL
        )
        INSERT INTO curated.orders (
            order_id, customer_id, order_status, purchase_ts, approved_ts,
            delivered_carrier_ts, delivered_customer_ts, estimated_delivery_ts,
            is_late, delivery_days, delivery_delay_days,
            is_delivery_days_outlier
        )
        SELECT
            source.order_id,
            source.customer_id,
            source.order_status,
            source.order_purchase_timestamp,
            source.order_approved_at,
            source.order_delivered_carrier_date,
            source.order_delivered_customer_date,
            source.order_estimated_delivery_date,
            CASE
                WHEN source.order_delivered_customer_date IS NULL
                  OR source.order_estimated_delivery_date IS NULL THEN NULL
                ELSE source.order_delivered_customer_date
                     > source.order_estimated_delivery_date
            END,
            source.calculated_delivery_days,
            CASE
                WHEN source.order_delivered_customer_date IS NULL
                  OR source.order_estimated_delivery_date IS NULL THEN NULL
                ELSE FLOOR(EXTRACT(EPOCH FROM (
                    source.order_delivered_customer_date
                    - source.order_estimated_delivery_date
                )) / 86400)::INTEGER
            END,
            CASE
                WHEN source.calculated_delivery_days IS NULL THEN NULL
                ELSE source.calculated_delivery_days < bounds.q1 - 1.5 * (bounds.q3 - bounds.q1)
                  OR source.calculated_delivery_days > bounds.q3 + 1.5 * (bounds.q3 - bounds.q1)
            END
        FROM valid_orders AS source
        CROSS JOIN bounds
        """
    )


async def _load_order_items(connection: asyncpg.Connection) -> None:
    await connection.execute(
        """
        WITH valid_items AS (
            SELECT DISTINCT ON (source.order_id, source.order_item_id)
                source.*
            FROM raw.order_items AS source
            JOIN curated.orders AS orders ON orders.order_id = source.order_id
            JOIN curated.products AS products ON products.product_id = source.product_id
            JOIN curated.sellers AS sellers ON sellers.seller_id = source.seller_id
            WHERE source.order_id IS NOT NULL
              AND source.order_item_id IS NOT NULL
              AND source.product_id IS NOT NULL
              AND source.seller_id IS NOT NULL
              AND source.price IS NOT NULL
              AND source.freight_value IS NOT NULL
              AND source.price >= 0
              AND source.freight_value >= 0
            ORDER BY source.order_id, source.order_item_id
        ),
        category_bounds AS (
            SELECT
                COALESCE(
                    products.category_name_english,
                    products.category_name,
                    'unknown'
                ) AS category,
                percentile_cont(0.25) WITHIN GROUP (ORDER BY price) AS price_q1,
                percentile_cont(0.75) WITHIN GROUP (ORDER BY price) AS price_q3,
                percentile_cont(0.25) WITHIN GROUP (ORDER BY freight_value) AS freight_q1,
                percentile_cont(0.75) WITHIN GROUP (ORDER BY freight_value) AS freight_q3
            FROM valid_items
            JOIN curated.products AS products
              ON products.product_id = valid_items.product_id
            GROUP BY 1
        )
        INSERT INTO curated.order_items (
            order_id, order_item_id, product_id, seller_id, shipping_limit_date,
            price, freight_value, is_price_outlier, is_freight_value_outlier
        )
        SELECT
            source.order_id,
            source.order_item_id,
            source.product_id,
            source.seller_id,
            source.shipping_limit_date,
            source.price,
            source.freight_value,
            source.price < bounds.price_q1 - 1.5 * (bounds.price_q3 - bounds.price_q1)
              OR source.price > bounds.price_q3 + 1.5 * (bounds.price_q3 - bounds.price_q1),
            source.freight_value < bounds.freight_q1 - 1.5 * (bounds.freight_q3 - bounds.freight_q1)
              OR source.freight_value > bounds.freight_q3 + 1.5 * (bounds.freight_q3 - bounds.freight_q1)
        FROM valid_items AS source
        JOIN curated.products AS products ON products.product_id = source.product_id
        JOIN category_bounds AS bounds
          ON bounds.category = COALESCE(
              products.category_name_english,
              products.category_name,
              'unknown'
          )
        """
    )


async def _load_payment_details(connection: asyncpg.Connection) -> None:
    await connection.execute(
        """
        WITH valid_payments AS (
            SELECT DISTINCT ON (source.order_id, source.payment_sequential)
                source.*
            FROM raw.order_payments AS source
            JOIN curated.orders AS orders ON orders.order_id = source.order_id
            WHERE source.order_id IS NOT NULL
              AND source.payment_sequential IS NOT NULL
              AND source.payment_type IS NOT NULL
              AND source.payment_value IS NOT NULL
              AND source.payment_value >= 0
              AND (
                    source.payment_installments IS NULL
                    OR source.payment_installments >= 0
              )
            ORDER BY source.order_id, source.payment_sequential
        ),
        bounds AS (
            SELECT
                percentile_cont(0.25) WITHIN GROUP (ORDER BY payment_value) AS q1,
                percentile_cont(0.75) WITHIN GROUP (ORDER BY payment_value) AS q3
            FROM valid_payments
        )
        INSERT INTO curated.payment_details (
            order_id, payment_sequential, payment_type, payment_installments,
            payment_value, is_payment_value_outlier
        )
        SELECT
            source.order_id,
            source.payment_sequential,
            source.payment_type,
            source.payment_installments,
            source.payment_value,
            source.payment_value < bounds.q1 - 1.5 * (bounds.q3 - bounds.q1)
              OR source.payment_value > bounds.q3 + 1.5 * (bounds.q3 - bounds.q1)
        FROM valid_payments AS source
        CROSS JOIN bounds
        """
    )


async def _load_payment_summary(connection: asyncpg.Connection) -> None:
    await connection.execute(
        """
        WITH primary_types AS (
            SELECT DISTINCT ON (order_id)
                order_id,
                payment_type
            FROM curated.payment_details
            ORDER BY order_id, payment_value DESC, payment_sequential ASC
        ),
        totals AS (
            SELECT
                order_id,
                MAX(payment_installments) AS installments_max,
                SUM(payment_value) AS total_payment_value
            FROM curated.payment_details
            GROUP BY order_id
        )
        INSERT INTO curated.payment_summary (
            order_id, primary_payment_type, installments_max, total_payment_value
        )
        SELECT
            totals.order_id,
            primary_types.payment_type,
            totals.installments_max,
            totals.total_payment_value
        FROM totals
        JOIN primary_types USING (order_id)
        """
    )


async def _load_reviews(connection: asyncpg.Connection) -> None:
    await connection.execute(
        """
        INSERT INTO curated.reviews (
            review_id, order_id, review_score, comment_title, comment_message,
            review_creation_ts, review_answer_ts
        )
        SELECT DISTINCT ON (source.review_id, source.order_id)
            source.review_id,
            source.order_id,
            source.review_score,
            source.review_comment_title,
            source.review_comment_message,
            source.review_creation_date,
            source.review_answer_timestamp
        FROM raw.order_reviews AS source
        JOIN curated.orders AS orders ON orders.order_id = source.order_id
        WHERE source.review_id IS NOT NULL
          AND source.order_id IS NOT NULL
          AND source.review_score BETWEEN 1 AND 5
        ORDER BY source.review_id, source.order_id, source.review_answer_timestamp DESC NULLS LAST
        """
    )


async def clean_curated() -> dict[str, int]:
    """Atomically rebuild all Phase 2 curated entity tables."""
    connection = await connect()
    table_list = ", ".join(f'curated."{name}"' for name in CURATED_ENTITY_TABLES)
    try:
        async with connection.transaction():
            await connection.execute(f"TRUNCATE TABLE {table_list}")
            await _create_geolocation_medians(connection)
            await _load_customers(connection)
            await _load_products(connection)
            await _load_sellers(connection)
            await _load_orders(connection)
            await _load_order_items(connection)
            await _load_payment_details(connection)
            await _load_payment_summary(connection)
            await _load_reviews(connection)

            counts = {
                table_name: await connection.fetchval(
                    f'SELECT COUNT(*) FROM curated."{table_name}"'
                )
                for table_name in CURATED_ENTITY_TABLES
            }
    finally:
        await connection.close()

    return {name: int(count) for name, count in counts.items()}
