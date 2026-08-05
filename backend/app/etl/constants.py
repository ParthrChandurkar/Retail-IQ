"""Dataset contracts shared by acquisition, ingestion, and reporting."""

from dataclasses import dataclass
from typing import Literal

ColumnKind = Literal["string", "integer", "numeric", "timestamp"]


@dataclass(frozen=True)
class DatasetSpec:
    """Expected source file, raw table, and typed column contract."""

    filename: str
    table_name: str
    columns: tuple[tuple[str, ColumnKind], ...]
    approximate_rows: int
    grain: tuple[str, ...]


DATASETS: tuple[DatasetSpec, ...] = (
    DatasetSpec(
        "olist_customers_dataset.csv",
        "customers",
        (
            ("customer_id", "string"),
            ("customer_unique_id", "string"),
            ("customer_zip_code_prefix", "string"),
            ("customer_city", "string"),
            ("customer_state", "string"),
        ),
        99_000,
        ("customer_id",),
    ),
    DatasetSpec(
        "olist_orders_dataset.csv",
        "orders",
        (
            ("order_id", "string"),
            ("customer_id", "string"),
            ("order_status", "string"),
            ("order_purchase_timestamp", "timestamp"),
            ("order_approved_at", "timestamp"),
            ("order_delivered_carrier_date", "timestamp"),
            ("order_delivered_customer_date", "timestamp"),
            ("order_estimated_delivery_date", "timestamp"),
        ),
        99_000,
        ("order_id",),
    ),
    DatasetSpec(
        "olist_order_items_dataset.csv",
        "order_items",
        (
            ("order_id", "string"),
            ("order_item_id", "integer"),
            ("product_id", "string"),
            ("seller_id", "string"),
            ("shipping_limit_date", "timestamp"),
            ("price", "numeric"),
            ("freight_value", "numeric"),
        ),
        112_000,
        ("order_id", "order_item_id"),
    ),
    DatasetSpec(
        "olist_products_dataset.csv",
        "products",
        (
            ("product_id", "string"),
            ("product_category_name", "string"),
            ("product_name_lenght", "numeric"),
            ("product_description_lenght", "numeric"),
            ("product_photos_qty", "numeric"),
            ("product_weight_g", "numeric"),
            ("product_length_cm", "numeric"),
            ("product_height_cm", "numeric"),
            ("product_width_cm", "numeric"),
        ),
        33_000,
        ("product_id",),
    ),
    DatasetSpec(
        "olist_sellers_dataset.csv",
        "sellers",
        (
            ("seller_id", "string"),
            ("seller_zip_code_prefix", "string"),
            ("seller_city", "string"),
            ("seller_state", "string"),
        ),
        3_000,
        ("seller_id",),
    ),
    DatasetSpec(
        "olist_order_payments_dataset.csv",
        "order_payments",
        (
            ("order_id", "string"),
            ("payment_sequential", "integer"),
            ("payment_type", "string"),
            ("payment_installments", "integer"),
            ("payment_value", "numeric"),
        ),
        104_000,
        ("order_id", "payment_sequential"),
    ),
    DatasetSpec(
        "olist_order_reviews_dataset.csv",
        "order_reviews",
        (
            ("review_id", "string"),
            ("order_id", "string"),
            ("review_score", "integer"),
            ("review_comment_title", "string"),
            ("review_comment_message", "string"),
            ("review_creation_date", "timestamp"),
            ("review_answer_timestamp", "timestamp"),
        ),
        99_000,
        ("review_id", "order_id"),
    ),
    DatasetSpec(
        "olist_geolocation_dataset.csv",
        "geolocation",
        (
            ("geolocation_zip_code_prefix", "string"),
            ("geolocation_lat", "numeric"),
            ("geolocation_lng", "numeric"),
            ("geolocation_city", "string"),
            ("geolocation_state", "string"),
        ),
        1_000_000,
        (),
    ),
    DatasetSpec(
        "product_category_name_translation.csv",
        "product_category_translation",
        (
            ("product_category_name", "string"),
            ("product_category_name_english", "string"),
        ),
        71,
        ("product_category_name",),
    ),
)

DATASETS_BY_TABLE = {dataset.table_name: dataset for dataset in DATASETS}
