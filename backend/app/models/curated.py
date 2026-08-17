"""SQLAlchemy models for Indian Store Data entities and platform tables."""

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    JSON,
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Customer(Base):
    """One source customer at the empirically verified Customer ID grain."""

    __tablename__ = "customers"
    __table_args__ = (
        Index("ix_customers_state", "state"),
        Index("ix_customers_segment", "segment"),
        {"schema": "curated"},
    )
    customer_id: Mapped[str] = mapped_column(String, primary_key=True)
    first_name: Mapped[str | None] = mapped_column(String)
    last_name: Mapped[str | None] = mapped_column(String)
    segment: Mapped[str] = mapped_column(String, nullable=False)
    postal_code: Mapped[str | None] = mapped_column(String)
    city_type: Mapped[str] = mapped_column(String, nullable=False)
    region_as_reported: Mapped[str] = mapped_column(String, nullable=False)
    state: Mapped[str] = mapped_column(String, nullable=False)


class Product(Base):
    __tablename__ = "products"
    __table_args__ = (
        Index("ix_products_category", "category", "sub_category"),
        {"schema": "curated"},
    )
    product_id: Mapped[str] = mapped_column(String, primary_key=True)
    product_name: Mapped[str | None] = mapped_column(String)
    category: Mapped[str] = mapped_column(String, nullable=False)
    sub_category: Mapped[str] = mapped_column(String, nullable=False)


class Order(Base):
    """Complete single-line order; Order ID never repeats in the source."""

    __tablename__ = "orders"
    __table_args__ = (
        Index("ix_orders_customer", "customer_id"),
        Index("ix_orders_order_date", "order_date"),
        Index("ix_orders_product", "product_id"),
        {"schema": "curated"},
    )
    order_id: Mapped[str] = mapped_column(String, primary_key=True)
    customer_id: Mapped[str] = mapped_column(
        ForeignKey("curated.customers.customer_id"), nullable=False
    )
    product_id: Mapped[str] = mapped_column(
        ForeignKey("curated.products.product_id"), nullable=False
    )
    order_date: Mapped[date] = mapped_column(Date, nullable=False)
    ship_date: Mapped[date | None] = mapped_column(Date)
    ship_mode: Mapped[str | None] = mapped_column(String)
    shipping_days: Mapped[int | None] = mapped_column(Integer)
    is_delayed_shipment: Mapped[bool | None] = mapped_column(Boolean)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    sales: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
    discount_pct: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
    profit: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
    is_sales_outlier: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default=text("false")
    )
    is_profit_outlier: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default=text("false")
    )


class StateGeocode(Base):
    __tablename__ = "state_geocode"
    __table_args__ = {"schema": "curated"}
    state: Mapped[str] = mapped_column(String, primary_key=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)


class StateRegionReference(Base):
    __tablename__ = "state_region_reference"
    __table_args__ = {"schema": "curated"}
    state: Mapped[str] = mapped_column(
        ForeignKey("curated.state_geocode.state"), primary_key=True
    )
    region: Mapped[str] = mapped_column(String, nullable=False)


class User(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "curated"}
    user_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    full_name: Mapped[str | None] = mapped_column(String)
    role: Mapped[str] = mapped_column(
        String, nullable=False, default="analyst", server_default=text("'analyst'")
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default=text("true")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=text("now()")
    )


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    __table_args__ = {"schema": "curated"}
    token_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("curated.users.user_id"), nullable=False
    )
    token_hash: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    issued_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=text("now()")
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime)


class AdminSetting(Base):
    __tablename__ = "admin_settings"
    __table_args__ = {"schema": "curated"}
    key: Mapped[str] = mapped_column(String, primary_key=True)
    value: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=text("now()")
    )


class DataRefreshLog(Base):
    __tablename__ = "data_refresh_log"
    __table_args__ = {"schema": "curated"}
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    job_name: Mapped[str] = mapped_column(String, nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime)
    status: Mapped[str] = mapped_column(String, nullable=False)
    rows_affected: Mapped[int | None] = mapped_column(Integer)
    error_message: Mapped[str | None] = mapped_column(Text)
