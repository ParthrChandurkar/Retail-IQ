"""Constraint-free SQLAlchemy table definitions for the raw source mirror."""

from sqlalchemy import Column, DateTime, Integer, MetaData, Numeric, String, Table, Text

raw_metadata = MetaData(schema="raw")

customers = Table(
    "customers",
    raw_metadata,
    Column("customer_id", String, nullable=True),
    Column("customer_unique_id", String, nullable=True),
    Column("customer_zip_code_prefix", String, nullable=True),
    Column("customer_city", String, nullable=True),
    Column("customer_state", String, nullable=True),
)

orders = Table(
    "orders",
    raw_metadata,
    Column("order_id", String, nullable=True),
    Column("customer_id", String, nullable=True),
    Column("order_status", String, nullable=True),
    Column("order_purchase_timestamp", DateTime, nullable=True),
    Column("order_approved_at", DateTime, nullable=True),
    Column("order_delivered_carrier_date", DateTime, nullable=True),
    Column("order_delivered_customer_date", DateTime, nullable=True),
    Column("order_estimated_delivery_date", DateTime, nullable=True),
)

order_items = Table(
    "order_items",
    raw_metadata,
    Column("order_id", String, nullable=True),
    Column("order_item_id", Integer, nullable=True),
    Column("product_id", String, nullable=True),
    Column("seller_id", String, nullable=True),
    Column("shipping_limit_date", DateTime, nullable=True),
    Column("price", Numeric, nullable=True),
    Column("freight_value", Numeric, nullable=True),
)

products = Table(
    "products",
    raw_metadata,
    Column("product_id", String, nullable=True),
    Column("product_category_name", String, nullable=True),
    Column("product_name_lenght", Numeric, nullable=True),
    Column("product_description_lenght", Numeric, nullable=True),
    Column("product_photos_qty", Numeric, nullable=True),
    Column("product_weight_g", Numeric, nullable=True),
    Column("product_length_cm", Numeric, nullable=True),
    Column("product_height_cm", Numeric, nullable=True),
    Column("product_width_cm", Numeric, nullable=True),
)

sellers = Table(
    "sellers",
    raw_metadata,
    Column("seller_id", String, nullable=True),
    Column("seller_zip_code_prefix", String, nullable=True),
    Column("seller_city", String, nullable=True),
    Column("seller_state", String, nullable=True),
)

order_payments = Table(
    "order_payments",
    raw_metadata,
    Column("order_id", String, nullable=True),
    Column("payment_sequential", Integer, nullable=True),
    Column("payment_type", String, nullable=True),
    Column("payment_installments", Integer, nullable=True),
    Column("payment_value", Numeric, nullable=True),
)

order_reviews = Table(
    "order_reviews",
    raw_metadata,
    Column("review_id", String, nullable=True),
    Column("order_id", String, nullable=True),
    Column("review_score", Integer, nullable=True),
    Column("review_comment_title", Text, nullable=True),
    Column("review_comment_message", Text, nullable=True),
    Column("review_creation_date", DateTime, nullable=True),
    Column("review_answer_timestamp", DateTime, nullable=True),
)

geolocation = Table(
    "geolocation",
    raw_metadata,
    Column("geolocation_zip_code_prefix", String, nullable=True),
    Column("geolocation_lat", Numeric, nullable=True),
    Column("geolocation_lng", Numeric, nullable=True),
    Column("geolocation_city", String, nullable=True),
    Column("geolocation_state", String, nullable=True),
)

product_category_translation = Table(
    "product_category_translation",
    raw_metadata,
    Column("product_category_name", String, nullable=True),
    Column("product_category_name_english", String, nullable=True),
)

RAW_TABLES = {
    table.name: table
    for table in (
        customers,
        orders,
        order_items,
        products,
        sellers,
        order_payments,
        order_reviews,
        geolocation,
        product_category_translation,
    )
}
