"""Typed Phase 5 domain payloads exposed through OpenAPI."""

from datetime import date, datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel


class DashboardSummary(BaseModel):
    period_start: date
    period_end: date
    total_revenue: Decimal
    total_orders: int
    total_customers: int
    average_order_value: Decimal
    revenue_mom_growth_pct: Decimal | None
    revenue_yoy_growth_pct: Decimal | None


class RevenuePoint(BaseModel):
    date: date
    revenue: Decimal
    order_count: int
    customer_count: int


class PerformanceRow(BaseModel):
    key: str
    revenue: Decimal
    order_count: int
    units: int | None = None
    average_review_score: Decimal | None = None


class CustomerRow(BaseModel):
    customer_unique_id: str
    first_order_ts: datetime | None
    last_order_ts: datetime | None
    order_count: int
    total_spend: Decimal
    primary_state: str | None
    primary_city: str | None
    recency_score: int
    frequency_score: int
    monetary_score: int
    rfm_segment: str
    clv_historical: Decimal


class SegmentRow(BaseModel):
    segment: str
    customer_count: int
    avg_clv: Decimal
    avg_order_count: Decimal


class DistributionRow(BaseModel):
    bucket: str
    count: int


class RepeatPurchase(BaseModel):
    total_customers: int
    repeat_customers: int
    repeat_purchase_rate_pct: Decimal


class ProductDetail(BaseModel):
    product_id: str
    category: str | None
    revenue: Decimal
    units: int
    order_count: int


class SellerDetail(BaseModel):
    seller_id: str
    city: str | None
    state: str | None
    revenue: Decimal
    order_count: int
    units: int
    average_review_score: Decimal | None


class RegionRow(BaseModel):
    state: str
    city: str | None = None
    revenue: Decimal
    order_count: int
    customer_count: int
    latitude: float | None = None
    longitude: float | None = None


class DeliveryRow(BaseModel):
    state: str | None
    city: str | None
    order_count: int
    delivered_count: int
    late_count: int
    late_rate_pct: Decimal
    avg_delivery_days: Decimal | None


class PaymentRow(BaseModel):
    payment_type: str
    payment_count: int
    order_count: int
    payment_value: Decimal
    avg_installments: Decimal | None


class ReviewRow(BaseModel):
    key: str
    review_count: int
    average_review_score: Decimal
    comments_with_text: int


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
