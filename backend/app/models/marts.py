"""Dashboard-facing aggregate models populated by the Phase 3 batch job."""

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Date,
    DateTime,
    Float,
    Index,
    Integer,
    Numeric,
    SmallInteger,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class CustomerProfile(Base):
    """Single source of truth at customer_unique_id grain."""

    __tablename__ = "customer_profile"
    __table_args__ = (
        Index("ix_customer_profile_segment", "rfm_segment"),
        Index("ix_customer_profile_region", "primary_state", "primary_city"),
        {"schema": "marts"},
    )

    customer_unique_id: Mapped[str] = mapped_column(String, primary_key=True)
    first_order_ts: Mapped[datetime | None] = mapped_column(DateTime)
    last_order_ts: Mapped[datetime | None] = mapped_column(DateTime)
    order_count: Mapped[int] = mapped_column(Integer, nullable=False)
    total_spend: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
    primary_state: Mapped[str | None] = mapped_column(String(2))
    primary_city: Mapped[str | None] = mapped_column(String)
    recency_score: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    frequency_score: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    monetary_score: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    rfm_segment: Mapped[str] = mapped_column(String, nullable=False)
    clv_historical: Mapped[Decimal] = mapped_column(Numeric, nullable=False)


class CustomerSegment(Base):
    """Customer segment aggregate; never duplicates customer-grain RFM rows."""

    __tablename__ = "customer_segments"
    __table_args__ = {"schema": "marts"}

    segment: Mapped[str] = mapped_column(String, primary_key=True)
    customer_count: Mapped[int] = mapped_column(Integer, nullable=False)
    avg_clv: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
    avg_order_count: Mapped[Decimal] = mapped_column(Numeric, nullable=False)


class AggregateDimensions:
    """Shared pre-joined dimensions used by filterable aggregate marts."""

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    state: Mapped[str | None] = mapped_column(String(2))
    city: Mapped[str | None] = mapped_column(String)
    category: Mapped[str | None] = mapped_column(String)
    seller_id: Mapped[str | None] = mapped_column(String)
    payment_type: Mapped[str | None] = mapped_column(String)
    customer_segment: Mapped[str | None] = mapped_column(String)


class RevenueDaily(AggregateDimensions, Base):
    __tablename__ = "revenue_daily"
    __table_args__ = (
        Index("ix_revenue_daily_filters", "date", "state", "category"),
        {"schema": "marts"},
    )

    revenue: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
    order_count: Mapped[int] = mapped_column(Integer, nullable=False)
    customer_count: Mapped[int] = mapped_column(Integer, nullable=False)
    item_count: Mapped[int] = mapped_column(Integer, nullable=False)


class RevenueByCategory(AggregateDimensions, Base):
    __tablename__ = "revenue_by_category"
    __table_args__ = (
        Index("ix_revenue_category_filters", "category", "date"),
        {"schema": "marts"},
    )

    revenue: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
    order_count: Mapped[int] = mapped_column(Integer, nullable=False)
    customer_count: Mapped[int] = mapped_column(Integer, nullable=False)
    units: Mapped[int] = mapped_column(Integer, nullable=False)


class RevenueByRegion(AggregateDimensions, Base):
    __tablename__ = "revenue_by_region"
    __table_args__ = (
        Index("ix_revenue_region_filters", "state", "city", "date"),
        {"schema": "marts"},
    )

    revenue: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
    order_count: Mapped[int] = mapped_column(Integer, nullable=False)
    customer_count: Mapped[int] = mapped_column(Integer, nullable=False)
    latitude: Mapped[float | None] = mapped_column(Float)
    longitude: Mapped[float | None] = mapped_column(Float)


class SellerPerformance(AggregateDimensions, Base):
    __tablename__ = "seller_performance"
    __table_args__ = (
        Index("ix_seller_performance_filters", "seller_id", "date"),
        {"schema": "marts"},
    )

    revenue: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
    order_count: Mapped[int] = mapped_column(Integer, nullable=False)
    units: Mapped[int] = mapped_column(Integer, nullable=False)
    avg_review_score: Mapped[Decimal | None] = mapped_column(Numeric)


class PaymentMethodMix(AggregateDimensions, Base):
    __tablename__ = "payment_method_mix"
    __table_args__ = (
        Index("ix_payment_mix_filters", "payment_type", "date"),
        {"schema": "marts"},
    )

    payment_count: Mapped[int] = mapped_column(Integer, nullable=False)
    order_count: Mapped[int] = mapped_column(Integer, nullable=False)
    payment_value: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
    avg_installments: Mapped[Decimal | None] = mapped_column(Numeric)


class DeliveryPerformance(AggregateDimensions, Base):
    __tablename__ = "delivery_performance"
    __table_args__ = (
        Index("ix_delivery_performance_filters", "date", "state", "category"),
        {"schema": "marts"},
    )

    review_score: Mapped[int | None] = mapped_column(SmallInteger)
    order_status: Mapped[str] = mapped_column(String, nullable=False)
    order_count: Mapped[int] = mapped_column(Integer, nullable=False)
    delivered_count: Mapped[int] = mapped_column(Integer, nullable=False)
    late_count: Mapped[int] = mapped_column(Integer, nullable=False)
    avg_delivery_days: Mapped[Decimal | None] = mapped_column(Numeric)
    avg_delivery_delay_days: Mapped[Decimal | None] = mapped_column(Numeric)


class ReviewSummary(AggregateDimensions, Base):
    __tablename__ = "review_summary"
    __table_args__ = (
        Index(
            "ix_review_summary_filters", "date", "category", "seller_id", "review_score"
        ),
        {"schema": "marts"},
    )

    review_score: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    review_count: Mapped[int] = mapped_column(Integer, nullable=False)
    avg_review_score: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
    comments_with_text: Mapped[int] = mapped_column(Integer, nullable=False)


class KpiSnapshot(Base):
    """Dimension-free latest snapshot; arbitrary periods read revenue_daily."""

    __tablename__ = "kpi_snapshot"
    __table_args__ = (
        CheckConstraint("snapshot_id = 1", name="ck_kpi_singleton"),
        {"schema": "marts"},
    )

    snapshot_id: Mapped[int] = mapped_column(SmallInteger, primary_key=True)
    generated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    period_start: Mapped[date] = mapped_column(Date, nullable=False)
    period_end: Mapped[date] = mapped_column(Date, nullable=False)
    total_revenue: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
    total_orders: Mapped[int] = mapped_column(Integer, nullable=False)
    total_customers: Mapped[int] = mapped_column(Integer, nullable=False)
    average_order_value: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
    latest_month_revenue: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
    revenue_mom_growth_pct: Mapped[Decimal | None] = mapped_column(Numeric)
    revenue_yoy_growth_pct: Mapped[Decimal | None] = mapped_column(Numeric)
