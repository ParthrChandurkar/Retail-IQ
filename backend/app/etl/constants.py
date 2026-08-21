"""Indian Store Data source contract shared by acquisition and ETL."""

from dataclasses import dataclass
from typing import Literal

ColumnKind = Literal["string", "integer", "numeric", "date"]


@dataclass(frozen=True)
class DatasetSpec:
    """Expected source file, raw table, and typed column contract."""

    filename: str
    table_name: str
    columns: tuple[tuple[str, ColumnKind], ...]
    approximate_rows: int
    grain: tuple[str, ...]


STORE_TRANSACTIONS = DatasetSpec(
    "indian_store_data.csv",
    "store_transactions",
    (
        ("customer_id", "string"),
        ("customer_name", "string"),
        ("last_name", "string"),
        ("date_of_birth", "date"),
        ("sales", "numeric"),
        ("year", "integer"),
        ("outlet_type", "string"),
        ("city_type", "string"),
        ("category_of_goods", "string"),
        ("region", "string"),
        ("country", "string"),
        ("segment", "string"),
        ("sales_date", "date"),
        ("order_id", "string"),
        ("order_date", "date"),
        ("ship_date", "date"),
        ("ship_mode", "string"),
        ("state", "string"),
        ("postal_code", "string"),
        ("product_id", "string"),
        ("sub_category", "string"),
        ("product_name", "string"),
        ("quantity", "integer"),
        ("discount", "numeric"),
        ("profit", "numeric"),
    ),
    100_000,
    ("order_id",),
)

SOURCE_HEADERS = (
    "Customer ID",
    "Customer Name",
    "Last Name",
    "Date of Birth",
    "Sales",
    "Year",
    "Outlet Type",
    "City Type",
    "Category of Goods",
    "Region",
    "Country",
    "Segment",
    "Sales Date",
    "Order ID",
    "Order Date",
    "Ship Date",
    "Ship Mode",
    "State",
    "Postal Code",
    "Product ID",
    "Sub-Category",
    "Product Name",
    "Quantity",
    "Discount",
    "Profit",
)

DATASETS: tuple[DatasetSpec, ...] = (STORE_TRANSACTIONS,)
DATASETS_BY_TABLE = {STORE_TRANSACTIONS.table_name: STORE_TRANSACTIONS}
