"""SQLAlchemy models for cleaned business entities and Phase 5 placeholders."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    SmallInteger,
    String,
    Text,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Customer(Base):
    """Order-linkage customer record at customer_id grain."""

    __tablename__ = "customers"
    __table_args__ = (
        Index("ix_customers_unique_id", "customer_unique_id"),
        {"schema": "curated"},
    )

    customer_id: Mapped[str] = mapped_column(String, primary_key=True)
    customer_unique_id: Mapped[str] = mapped_column(String, nullable=False)
    zip_code_prefix: Mapped[str | None] = mapped_column(String)
    city: Mapped[str | None] = mapped_column(String)
    state: Mapped[str | None] = mapped_column(String(2))
    latitude: Mapped[float | None] = mapped_column(Float)
    longitude: Mapped[float | None] = mapped_column(Float)


class Order(Base):
    """Cleaned order record."""

    __tablename__ = "orders"
    __table_args__ = (
        Index("ix_orders_customer", "customer_id"),
        Index("ix_orders_purchase_ts", "purchase_ts"),
        Index("ix_orders_status", "order_status"),
        {"schema": "curated"},
    )

    order_id: Mapped[str] = mapped_column(String, primary_key=True)
    customer_id: Mapped[str] = mapped_column(
        ForeignKey("curated.customers.customer_id"), nullable=False
    )
    order_status: Mapped[str] = mapped_column(String, nullable=False)
    purchase_ts: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    approved_ts: Mapped[datetime | None] = mapped_column(DateTime)
    delivered_carrier_ts: Mapped[datetime | None] = mapped_column(DateTime)
    delivered_customer_ts: Mapped[datetime | None] = mapped_column(DateTime)
    estimated_delivery_ts: Mapped[datetime | None] = mapped_column(DateTime)
    is_late: Mapped[bool | None] = mapped_column(Boolean)
    delivery_days: Mapped[int | None] = mapped_column(Integer)
    delivery_delay_days: Mapped[int | None] = mapped_column(Integer)
    is_delivery_days_outlier: Mapped[bool | None] = mapped_column(Boolean)


class Product(Base):
    """Cleaned product record."""

    __tablename__ = "products"
    __table_args__ = {"schema": "curated"}

    product_id: Mapped[str] = mapped_column(String, primary_key=True)
    category_name: Mapped[str | None] = mapped_column(String)
    category_name_english: Mapped[str | None] = mapped_column(String)
    weight_g: Mapped[Decimal | None] = mapped_column(Numeric)
    length_cm: Mapped[Decimal | None] = mapped_column(Numeric)
    height_cm: Mapped[Decimal | None] = mapped_column(Numeric)
    width_cm: Mapped[Decimal | None] = mapped_column(Numeric)


class Seller(Base):
    """Cleaned seller record."""

    __tablename__ = "sellers"
    __table_args__ = {"schema": "curated"}

    seller_id: Mapped[str] = mapped_column(String, primary_key=True)
    zip_code_prefix: Mapped[str | None] = mapped_column(String)
    city: Mapped[str | None] = mapped_column(String)
    state: Mapped[str | None] = mapped_column(String(2))
    latitude: Mapped[float | None] = mapped_column(Float)
    longitude: Mapped[float | None] = mapped_column(Float)


class OrderItem(Base):
    """Cleaned order-item record."""

    __tablename__ = "order_items"
    __table_args__ = {"schema": "curated"}

    order_id: Mapped[str] = mapped_column(
        ForeignKey("curated.orders.order_id"), primary_key=True
    )
    order_item_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[str] = mapped_column(
        ForeignKey("curated.products.product_id"), nullable=False
    )
    seller_id: Mapped[str] = mapped_column(
        ForeignKey("curated.sellers.seller_id"), nullable=False
    )
    shipping_limit_date: Mapped[datetime | None] = mapped_column(DateTime)
    price: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
    freight_value: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
    is_price_outlier: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default=text("false")
    )
    is_freight_value_outlier: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default=text("false")
    )


class PaymentDetail(Base):
    """Cleaned payment record at source payment grain."""

    __tablename__ = "payment_details"
    __table_args__ = {"schema": "curated"}

    order_id: Mapped[str] = mapped_column(
        ForeignKey("curated.orders.order_id"), primary_key=True
    )
    payment_sequential: Mapped[int] = mapped_column(Integer, primary_key=True)
    payment_type: Mapped[str] = mapped_column(String, nullable=False)
    payment_installments: Mapped[int | None] = mapped_column(Integer)
    payment_value: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
    is_payment_value_outlier: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default=text("false")
    )


class PaymentSummary(Base):
    """Derived order-level payment summary."""

    __tablename__ = "payment_summary"
    __table_args__ = {"schema": "curated"}

    order_id: Mapped[str] = mapped_column(
        ForeignKey("curated.orders.order_id"), primary_key=True
    )
    primary_payment_type: Mapped[str | None] = mapped_column(String)
    installments_max: Mapped[int | None] = mapped_column(Integer)
    total_payment_value: Mapped[Decimal | None] = mapped_column(Numeric)


class Review(Base):
    """Cleaned review-order link preserving the source composite grain."""

    __tablename__ = "reviews"
    __table_args__ = (
        CheckConstraint("review_score BETWEEN 1 AND 5", name="ck_review_score"),
        Index("ix_reviews_review_id", "review_id"),
        {"schema": "curated"},
    )

    review_id: Mapped[str] = mapped_column(String, primary_key=True)
    order_id: Mapped[str] = mapped_column(
        ForeignKey("curated.orders.order_id"), primary_key=True
    )
    review_score: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    comment_title: Mapped[str | None] = mapped_column(Text)
    comment_message: Mapped[str | None] = mapped_column(Text)
    review_creation_ts: Mapped[datetime | None] = mapped_column(DateTime)
    review_answer_ts: Mapped[datetime | None] = mapped_column(DateTime)


class User(Base):
    """Empty Phase 5 authentication user table."""

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
    """Empty Phase 5 refresh-token table."""

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
    """Empty Phase 5 administration settings table."""

    __tablename__ = "admin_settings"
    __table_args__ = {"schema": "curated"}

    key: Mapped[str] = mapped_column(String, primary_key=True)
    value: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=text("now()")
    )


class DataRefreshLog(Base):
    """Execution audit record for ETL and later batch jobs."""

    __tablename__ = "data_refresh_log"
    __table_args__ = {"schema": "curated"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    job_name: Mapped[str] = mapped_column(String, nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime)
    status: Mapped[str] = mapped_column(String, nullable=False)
    rows_affected: Mapped[int | None] = mapped_column(Integer)
    error_message: Mapped[str | None] = mapped_column(Text)
