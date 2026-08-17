"""Migrate dataset-dependent tables to Indian Store Data v2.1.

Revision ID: 20260817_0006
Revises: 20260812_0005
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260817_0006"
down_revision: str | None = "20260812_0005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

GEOCODES = (
    ("Delhi", 28.643393, 77.115493),
    ("Gujarat", 22.698438, 71.572450),
    ("Karnataka", 14.710270, 76.167417),
    ("Madhya Pradesh", 23.538008, 78.288901),
    ("Maharashtra", 19.451475, 76.107576),
    ("Punjab", 30.842485, 75.415377),
    ("Rajasthan", 26.584438, 73.849731),
    ("Tamil Nadu", 11.013587, 78.408311),
    ("Uttar Pradesh", 26.923032, 80.565983),
    ("West Bengal", 23.810442, 87.983958),
)

REGIONS = (
    ("Delhi", "North"),
    ("Punjab", "North"),
    ("Uttar Pradesh", "North"),
    ("West Bengal", "East"),
    ("Gujarat", "West"),
    ("Madhya Pradesh", "West"),
    ("Maharashtra", "West"),
    ("Rajasthan", "West"),
    ("Karnataka", "South"),
    ("Tamil Nadu", "South"),
)

OLD_RAW_TABLES = (
    "customers",
    "geolocation",
    "order_items",
    "order_payments",
    "order_reviews",
    "orders",
    "product_category_translation",
    "products",
    "sellers",
)


def upgrade() -> None:
    """Replace only dataset-dependent raw and curated tables."""
    for table in ("reviews", "payment_summary", "payment_details", "order_items"):
        op.drop_table(table, schema="curated")
    op.drop_table("orders", schema="curated")
    op.drop_table("sellers", schema="curated")
    op.drop_table("products", schema="curated")
    op.drop_table("customers", schema="curated")
    for table in OLD_RAW_TABLES:
        op.drop_table(table, schema="raw")

    op.create_table(
        "store_transactions",
        sa.Column("customer_id", sa.String(), nullable=True),
        sa.Column("customer_name", sa.String(), nullable=True),
        sa.Column("last_name", sa.String(), nullable=True),
        sa.Column("date_of_birth", sa.Date(), nullable=True),
        sa.Column("sales", sa.Numeric(), nullable=True),
        sa.Column("year", sa.Integer(), nullable=True),
        sa.Column("outlet_type", sa.String(), nullable=True),
        sa.Column("city_type", sa.String(), nullable=True),
        sa.Column("category_of_goods", sa.String(), nullable=True),
        sa.Column("region", sa.String(), nullable=True),
        sa.Column("country", sa.String(), nullable=True),
        sa.Column("segment", sa.String(), nullable=True),
        sa.Column("sales_date", sa.Date(), nullable=True),
        sa.Column("order_id", sa.String(), nullable=True),
        sa.Column("order_date", sa.Date(), nullable=True),
        sa.Column("ship_date", sa.Date(), nullable=True),
        sa.Column("ship_mode", sa.String(), nullable=True),
        sa.Column("state", sa.String(), nullable=True),
        sa.Column("postal_code", sa.String(), nullable=True),
        sa.Column("product_id", sa.String(), nullable=True),
        sa.Column("sub_category", sa.String(), nullable=True),
        sa.Column("product_name", sa.String(), nullable=True),
        sa.Column("quantity", sa.Integer(), nullable=True),
        sa.Column("discount", sa.Numeric(), nullable=True),
        sa.Column("profit", sa.Numeric(), nullable=True),
        schema="raw",
    )
    op.create_table(
        "customers",
        sa.Column("customer_id", sa.String(), primary_key=True),
        sa.Column("first_name", sa.String(), nullable=True),
        sa.Column("last_name", sa.String(), nullable=True),
        sa.Column("segment", sa.String(), nullable=False),
        sa.Column("postal_code", sa.String(), nullable=True),
        sa.Column("city_type", sa.String(), nullable=False),
        sa.Column("region_as_reported", sa.String(), nullable=False),
        sa.Column("state", sa.String(), nullable=False),
        schema="curated",
    )
    op.create_index("ix_customers_state", "customers", ["state"], schema="curated")
    op.create_index("ix_customers_segment", "customers", ["segment"], schema="curated")
    op.create_table(
        "products",
        sa.Column("product_id", sa.String(), primary_key=True),
        sa.Column("product_name", sa.String(), nullable=True),
        sa.Column("category", sa.String(), nullable=False),
        sa.Column("sub_category", sa.String(), nullable=False),
        schema="curated",
    )
    op.create_index(
        "ix_products_category",
        "products",
        ["category", "sub_category"],
        schema="curated",
    )
    op.create_table(
        "orders",
        sa.Column("order_id", sa.String(), primary_key=True),
        sa.Column("customer_id", sa.String(), nullable=False),
        sa.Column("product_id", sa.String(), nullable=False),
        sa.Column("order_date", sa.Date(), nullable=False),
        sa.Column("ship_date", sa.Date(), nullable=True),
        sa.Column("ship_mode", sa.String(), nullable=True),
        sa.Column("shipping_days", sa.Integer(), nullable=True),
        sa.Column("is_delayed_shipment", sa.Boolean(), nullable=True),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("sales", sa.Numeric(), nullable=False),
        sa.Column("discount_pct", sa.Numeric(), nullable=False),
        sa.Column("profit", sa.Numeric(), nullable=False),
        sa.Column(
            "is_sales_outlier",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        sa.Column(
            "is_profit_outlier",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["customer_id"], ["curated.customers.customer_id"]),
        sa.ForeignKeyConstraint(["product_id"], ["curated.products.product_id"]),
        schema="curated",
    )
    op.create_index("ix_orders_customer", "orders", ["customer_id"], schema="curated")
    op.create_index("ix_orders_order_date", "orders", ["order_date"], schema="curated")
    op.create_index("ix_orders_product", "orders", ["product_id"], schema="curated")
    op.create_table(
        "state_geocode",
        sa.Column("state", sa.String(), primary_key=True),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        schema="curated",
    )
    geocode_table = sa.table(
        "state_geocode",
        sa.column("state", sa.String()),
        sa.column("latitude", sa.Float()),
        sa.column("longitude", sa.Float()),
        schema="curated",
    )
    op.bulk_insert(
        geocode_table,
        [
            {"state": state, "latitude": lat, "longitude": lon}
            for state, lat, lon in GEOCODES
        ],
    )
    op.create_table(
        "state_region_reference",
        sa.Column("state", sa.String(), primary_key=True),
        sa.Column("region", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(["state"], ["curated.state_geocode.state"]),
        sa.CheckConstraint(
            "region IN ('North','South','East','West')",
            name="ck_state_region_reference_region",
        ),
        schema="curated",
    )
    region_table = sa.table(
        "state_region_reference",
        sa.column("state", sa.String()),
        sa.column("region", sa.String()),
        schema="curated",
    )
    op.bulk_insert(
        region_table, [{"state": state, "region": region} for state, region in REGIONS]
    )


def _restore_old_raw() -> None:
    definitions: dict[str, list[sa.Column[object]]] = {
        "customers": [
            sa.Column("customer_id", sa.String()),
            sa.Column("customer_unique_id", sa.String()),
            sa.Column("customer_zip_code_prefix", sa.String()),
            sa.Column("customer_city", sa.String()),
            sa.Column("customer_state", sa.String()),
        ],
        "geolocation": [
            sa.Column("geolocation_zip_code_prefix", sa.String()),
            sa.Column("geolocation_lat", sa.Numeric()),
            sa.Column("geolocation_lng", sa.Numeric()),
            sa.Column("geolocation_city", sa.String()),
            sa.Column("geolocation_state", sa.String()),
        ],
        "order_items": [
            sa.Column("order_id", sa.String()),
            sa.Column("order_item_id", sa.Integer()),
            sa.Column("product_id", sa.String()),
            sa.Column("seller_id", sa.String()),
            sa.Column("shipping_limit_date", sa.DateTime()),
            sa.Column("price", sa.Numeric()),
            sa.Column("freight_value", sa.Numeric()),
        ],
        "order_payments": [
            sa.Column("order_id", sa.String()),
            sa.Column("payment_sequential", sa.Integer()),
            sa.Column("payment_type", sa.String()),
            sa.Column("payment_installments", sa.Integer()),
            sa.Column("payment_value", sa.Numeric()),
        ],
        "order_reviews": [
            sa.Column("review_id", sa.String()),
            sa.Column("order_id", sa.String()),
            sa.Column("review_score", sa.Integer()),
            sa.Column("review_comment_title", sa.Text()),
            sa.Column("review_comment_message", sa.Text()),
            sa.Column("review_creation_date", sa.DateTime()),
            sa.Column("review_answer_timestamp", sa.DateTime()),
        ],
        "orders": [
            sa.Column("order_id", sa.String()),
            sa.Column("customer_id", sa.String()),
            sa.Column("order_status", sa.String()),
            sa.Column("order_purchase_timestamp", sa.DateTime()),
            sa.Column("order_approved_at", sa.DateTime()),
            sa.Column("order_delivered_carrier_date", sa.DateTime()),
            sa.Column("order_delivered_customer_date", sa.DateTime()),
            sa.Column("order_estimated_delivery_date", sa.DateTime()),
        ],
        "product_category_translation": [
            sa.Column("product_category_name", sa.String()),
            sa.Column("product_category_name_english", sa.String()),
        ],
        "products": [
            sa.Column("product_id", sa.String()),
            sa.Column("product_category_name", sa.String()),
            sa.Column("product_name_lenght", sa.Numeric()),
            sa.Column("product_description_lenght", sa.Numeric()),
            sa.Column("product_photos_qty", sa.Numeric()),
            sa.Column("product_weight_g", sa.Numeric()),
            sa.Column("product_length_cm", sa.Numeric()),
            sa.Column("product_height_cm", sa.Numeric()),
            sa.Column("product_width_cm", sa.Numeric()),
        ],
        "sellers": [
            sa.Column("seller_id", sa.String()),
            sa.Column("seller_zip_code_prefix", sa.String()),
            sa.Column("seller_city", sa.String()),
            sa.Column("seller_state", sa.String()),
        ],
    }
    for name, columns in definitions.items():
        op.create_table(name, *columns, schema="raw")


def _restore_old_curated() -> None:
    op.create_table(
        "customers",
        sa.Column("customer_id", sa.String(), primary_key=True),
        sa.Column("customer_unique_id", sa.String(), nullable=False),
        sa.Column("zip_code_prefix", sa.String()),
        sa.Column("city", sa.String()),
        sa.Column("state", sa.String(2)),
        sa.Column("latitude", sa.Float()),
        sa.Column("longitude", sa.Float()),
        schema="curated",
    )
    op.create_index(
        "ix_customers_unique_id", "customers", ["customer_unique_id"], schema="curated"
    )
    op.create_table(
        "products",
        sa.Column("product_id", sa.String(), primary_key=True),
        sa.Column("category_name", sa.String()),
        sa.Column("category_name_english", sa.String()),
        sa.Column("weight_g", sa.Numeric()),
        sa.Column("length_cm", sa.Numeric()),
        sa.Column("height_cm", sa.Numeric()),
        sa.Column("width_cm", sa.Numeric()),
        schema="curated",
    )
    op.create_table(
        "sellers",
        sa.Column("seller_id", sa.String(), primary_key=True),
        sa.Column("zip_code_prefix", sa.String()),
        sa.Column("city", sa.String()),
        sa.Column("state", sa.String(2)),
        sa.Column("latitude", sa.Float()),
        sa.Column("longitude", sa.Float()),
        schema="curated",
    )
    op.create_table(
        "orders",
        sa.Column("order_id", sa.String(), primary_key=True),
        sa.Column("customer_id", sa.String(), nullable=False),
        sa.Column("order_status", sa.String(), nullable=False),
        sa.Column("purchase_ts", sa.DateTime(), nullable=False),
        sa.Column("approved_ts", sa.DateTime()),
        sa.Column("delivered_carrier_ts", sa.DateTime()),
        sa.Column("delivered_customer_ts", sa.DateTime()),
        sa.Column("estimated_delivery_ts", sa.DateTime()),
        sa.Column("is_late", sa.Boolean()),
        sa.Column("delivery_days", sa.Integer()),
        sa.Column("delivery_delay_days", sa.Integer()),
        sa.Column("is_delivery_days_outlier", sa.Boolean()),
        sa.ForeignKeyConstraint(["customer_id"], ["curated.customers.customer_id"]),
        schema="curated",
    )
    op.create_index("ix_orders_customer", "orders", ["customer_id"], schema="curated")
    op.create_index(
        "ix_orders_purchase_ts", "orders", ["purchase_ts"], schema="curated"
    )
    op.create_index("ix_orders_status", "orders", ["order_status"], schema="curated")
    op.create_table(
        "order_items",
        sa.Column("order_id", sa.String(), primary_key=True),
        sa.Column("order_item_id", sa.Integer(), primary_key=True),
        sa.Column("product_id", sa.String(), nullable=False),
        sa.Column("seller_id", sa.String(), nullable=False),
        sa.Column("shipping_limit_date", sa.DateTime()),
        sa.Column("price", sa.Numeric(), nullable=False),
        sa.Column("freight_value", sa.Numeric(), nullable=False),
        sa.Column(
            "is_price_outlier",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        sa.Column(
            "is_freight_value_outlier",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["order_id"], ["curated.orders.order_id"]),
        sa.ForeignKeyConstraint(["product_id"], ["curated.products.product_id"]),
        sa.ForeignKeyConstraint(["seller_id"], ["curated.sellers.seller_id"]),
        schema="curated",
    )
    op.create_table(
        "payment_details",
        sa.Column("order_id", sa.String(), primary_key=True),
        sa.Column("payment_sequential", sa.Integer(), primary_key=True),
        sa.Column("payment_type", sa.String(), nullable=False),
        sa.Column("payment_installments", sa.Integer()),
        sa.Column("payment_value", sa.Numeric(), nullable=False),
        sa.Column(
            "is_payment_value_outlier",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["order_id"], ["curated.orders.order_id"]),
        schema="curated",
    )
    op.create_table(
        "payment_summary",
        sa.Column("order_id", sa.String(), primary_key=True),
        sa.Column("primary_payment_type", sa.String()),
        sa.Column("installments_max", sa.Integer()),
        sa.Column("total_payment_value", sa.Numeric()),
        sa.ForeignKeyConstraint(["order_id"], ["curated.orders.order_id"]),
        schema="curated",
    )
    op.create_table(
        "reviews",
        sa.Column("review_id", sa.String(), primary_key=True),
        sa.Column("order_id", sa.String(), primary_key=True),
        sa.Column("review_score", sa.SmallInteger(), nullable=False),
        sa.Column("comment_title", sa.Text()),
        sa.Column("comment_message", sa.Text()),
        sa.Column("review_creation_ts", sa.DateTime()),
        sa.Column("review_answer_ts", sa.DateTime()),
        sa.CheckConstraint("review_score BETWEEN 1 AND 5", name="ck_review_score"),
        sa.ForeignKeyConstraint(["order_id"], ["curated.orders.order_id"]),
        schema="curated",
    )
    op.create_index("ix_reviews_review_id", "reviews", ["review_id"], schema="curated")


def downgrade() -> None:
    op.drop_table("state_region_reference", schema="curated")
    op.drop_table("state_geocode", schema="curated")
    op.drop_table("orders", schema="curated")
    op.drop_table("products", schema="curated")
    op.drop_table("customers", schema="curated")
    op.drop_table("store_transactions", schema="raw")
    _restore_old_raw()
    _restore_old_curated()
