"""Dashboard-facing aggregates for the Indian Store Data migration."""

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
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
    """Cross-sectional customer profile; the source has no repeat customers."""

    __tablename__ = "customer_profile"
    __table_args__ = (
        Index("ix_customer_profile_dimensions", "segment", "city_type", "region"),
        Index("ix_customer_profile_order_value", "order_value"),
        {"schema": "marts"},
    )

    customer_id: Mapped[str] = mapped_column(String, primary_key=True)
    order_date: Mapped[date] = mapped_column(Date, nullable=False)
    recency_days: Mapped[int] = mapped_column(Integer, nullable=False)
    order_value: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
    profit: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
    discount_pct: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
    segment: Mapped[str] = mapped_column(String, nullable=False)
    city_type: Mapped[str] = mapped_column(String, nullable=False)
    region: Mapped[str] = mapped_column(String, nullable=False)
    state: Mapped[str] = mapped_column(String, nullable=False)
    order_value_tier: Mapped[str] = mapped_column(String, nullable=False)


class CustomerSegment(Base):
    """Given segment × order-value quartile × city-type summary."""

    __tablename__ = "customer_segments"
    __table_args__ = {"schema": "marts"}

    segment: Mapped[str] = mapped_column(String, primary_key=True)
    order_value_tier: Mapped[str] = mapped_column(String, primary_key=True)
    city_type: Mapped[str] = mapped_column(String, primary_key=True)
    customer_count: Mapped[int] = mapped_column(Integer, nullable=False)
    avg_order_value: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
    avg_profit: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
    avg_discount_pct: Mapped[Decimal] = mapped_column(Numeric, nullable=False)


class RevenueDaily(Base):
    __tablename__ = "revenue_daily"
    __table_args__ = {"schema": "marts"}

    date: Mapped[date] = mapped_column(Date, primary_key=True)
    revenue: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
    total_profit: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
    total_discount_value: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
    order_count: Mapped[int] = mapped_column(Integer, nullable=False)
    customer_count: Mapped[int] = mapped_column(Integer, nullable=False)
    units: Mapped[int] = mapped_column(Integer, nullable=False)
    avg_discount_pct: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
    profit_margin_pct: Mapped[Decimal] = mapped_column(Numeric, nullable=False)


class RevenueByCategory(Base):
    __tablename__ = "revenue_by_category"
    __table_args__ = (
        Index("ix_revenue_category_date", "category", "sub_category", "date"),
        {"schema": "marts"},
    )

    date: Mapped[date] = mapped_column(Date, primary_key=True)
    category: Mapped[str] = mapped_column(String, primary_key=True)
    sub_category: Mapped[str] = mapped_column(String, primary_key=True)
    revenue: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
    total_profit: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
    total_discount_value: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
    order_count: Mapped[int] = mapped_column(Integer, nullable=False)
    customer_count: Mapped[int] = mapped_column(Integer, nullable=False)
    units: Mapped[int] = mapped_column(Integer, nullable=False)
    avg_discount_pct: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
    profit_margin_pct: Mapped[Decimal] = mapped_column(Numeric, nullable=False)


class RevenueByRegion(Base):
    __tablename__ = "revenue_by_region"
    __table_args__ = (
        Index("ix_revenue_region_date", "region", "state", "city_type", "date"),
        {"schema": "marts"},
    )

    date: Mapped[date] = mapped_column(Date, primary_key=True)
    state: Mapped[str] = mapped_column(String, primary_key=True)
    region: Mapped[str] = mapped_column(String, primary_key=True)
    city_type: Mapped[str] = mapped_column(String, primary_key=True)
    revenue: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
    total_profit: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
    total_discount_value: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
    order_count: Mapped[int] = mapped_column(Integer, nullable=False)
    customer_count: Mapped[int] = mapped_column(Integer, nullable=False)
    units: Mapped[int] = mapped_column(Integer, nullable=False)
    avg_discount_pct: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
    profit_margin_pct: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)


class ShippingPerformance(Base):
    """Descriptive shipping-duration mart; not a delay-label definition."""

    __tablename__ = "shipping_performance"
    __table_args__ = (
        Index("ix_shipping_performance_date", "ship_mode", "region", "date"),
        {"schema": "marts"},
    )

    date: Mapped[date] = mapped_column(Date, primary_key=True)
    ship_mode: Mapped[str] = mapped_column(String, primary_key=True)
    region: Mapped[str] = mapped_column(String, primary_key=True)
    order_count: Mapped[int] = mapped_column(Integer, nullable=False)
    avg_shipping_days: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
    median_shipping_days: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
    min_shipping_days: Mapped[int] = mapped_column(Integer, nullable=False)
    max_shipping_days: Mapped[int] = mapped_column(Integer, nullable=False)


class CategoryDiscountProfit(Base):
    __tablename__ = "category_discount_profit"
    __table_args__ = (
        Index(
            "ix_category_discount_profit", "category", "sub_category", "discount_band"
        ),
        {"schema": "marts"},
    )

    category: Mapped[str] = mapped_column(String, primary_key=True)
    sub_category: Mapped[str] = mapped_column(String, primary_key=True)
    discount_band: Mapped[str] = mapped_column(String, primary_key=True)
    order_count: Mapped[int] = mapped_column(Integer, nullable=False)
    revenue: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
    total_profit: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
    avg_discount_pct: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
    avg_profit_margin_pct: Mapped[Decimal] = mapped_column(Numeric, nullable=False)


class KpiSnapshot(Base):
    """Dimension-free all-observed-period snapshot."""

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
    total_profit: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
    total_orders: Mapped[int] = mapped_column(Integer, nullable=False)
    total_customers: Mapped[int] = mapped_column(Integer, nullable=False)
    average_order_value: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
    average_discount_pct: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
    profit_margin_pct: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
    latest_month_revenue: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
    latest_month_profit: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
    revenue_mom_growth_pct: Mapped[Decimal | None] = mapped_column(Numeric)
    revenue_yoy_growth_pct: Mapped[Decimal | None] = mapped_column(Numeric)
