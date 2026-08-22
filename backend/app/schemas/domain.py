"""Typed migrated domain payloads exposed through OpenAPI."""

from datetime import date, datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel


class DashboardSummary(BaseModel):
    period_start: date
    period_end: date
    total_revenue: Decimal
    total_profit: Decimal
    total_orders: int
    total_customers: int
    average_order_value: Decimal
    avg_discount_pct: Decimal
    profit_margin_pct: Decimal
    revenue_mom_growth_pct: Decimal | None
    revenue_yoy_growth_pct: Decimal | None


class RevenuePoint(BaseModel):
    date: date
    revenue: Decimal
    total_profit: Decimal
    order_count: int
    customer_count: int


class PerformanceRow(BaseModel):
    key: str
    revenue: Decimal
    total_profit: Decimal
    order_count: int
    units: int
    avg_discount_pct: Decimal
    profit_margin_pct: Decimal


class DiscountProfitRow(BaseModel):
    category: str
    sub_category: str
    discount_band: str
    order_count: int
    revenue: Decimal
    total_profit: Decimal
    avg_discount_pct: Decimal
    avg_profit_margin_pct: Decimal


class CustomerProfile(BaseModel):
    customer_id: str
    order_date: date
    recency_days: int
    order_value: Decimal
    profit: Decimal
    discount_pct: Decimal
    segment: str
    city_type: str
    region: str
    state: str
    order_value_tier: str


class CustomerDetail(CustomerProfile):
    first_name: str
    last_name: str


class SegmentRow(BaseModel):
    segment: str
    order_value_tier: str
    city_type: str
    customer_count: int
    avg_order_value: Decimal
    avg_profit: Decimal
    avg_discount_pct: Decimal


class DistributionRow(BaseModel):
    bucket: str
    count: int


class RegionRow(BaseModel):
    state: str
    region: str
    city_type: str | None = None
    revenue: Decimal
    total_profit: Decimal
    order_count: int
    customer_count: int
    avg_discount_pct: Decimal
    profit_margin_pct: Decimal
    latitude: float
    longitude: float


class ShippingRow(BaseModel):
    date: date
    ship_mode: str
    region: str
    order_count: int
    avg_shipping_days: Decimal
    median_shipping_days: Decimal
    min_shipping_days: int
    max_shipping_days: int


class AnalyticsPayload(BaseModel):
    columns: list[str] | None = None
    rows: list[dict[str, Any]]
    conclusion: str | None = None


class Recommendation(BaseModel):
    id: str
    category: str
    severity: str
    title: str
    description: str
    supporting_metric: dict[str, Any]


class AdminSettingPayload(BaseModel):
    settings: dict[str, Any]


class RefreshStatus(BaseModel):
    job_name: str
    started_at: datetime
    finished_at: datetime | None
    status: str
    rows_affected: int | None
    error_message: str | None
