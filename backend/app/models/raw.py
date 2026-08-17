"""Loose, nullable mirror of the Indian Store Data CSV."""

from sqlalchemy import Column, Date, Integer, MetaData, Numeric, String, Table

raw_metadata = MetaData(schema="raw")

store_transactions = Table(
    "store_transactions",
    raw_metadata,
    Column("customer_id", String, nullable=True),
    Column("customer_name", String, nullable=True),
    Column("last_name", String, nullable=True),
    Column("date_of_birth", Date, nullable=True),
    Column("sales", Numeric, nullable=True),
    Column("year", Integer, nullable=True),
    Column("outlet_type", String, nullable=True),
    Column("city_type", String, nullable=True),
    Column("category_of_goods", String, nullable=True),
    Column("region", String, nullable=True),
    Column("country", String, nullable=True),
    Column("segment", String, nullable=True),
    Column("sales_date", Date, nullable=True),
    Column("order_id", String, nullable=True),
    Column("order_date", Date, nullable=True),
    Column("ship_date", Date, nullable=True),
    Column("ship_mode", String, nullable=True),
    Column("state", String, nullable=True),
    Column("postal_code", String, nullable=True),
    Column("product_id", String, nullable=True),
    Column("sub_category", String, nullable=True),
    Column("product_name", String, nullable=True),
    Column("quantity", Integer, nullable=True),
    Column("discount", Numeric, nullable=True),
    Column("profit", Numeric, nullable=True),
)

RAW_TABLES = {store_transactions.name: store_transactions}
