"""Cross-cutting dashboard endpoints backed by corrected marts."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.core.dependencies import CurrentUser
from app.schemas.common import DataResponse
from app.schemas.domain import (
    DashboardSummary,
    PerformanceRow,
    ProductDetail,
    RevenuePoint,
)
from app.schemas.filters import SharedFilters, get_shared_filters
from app.services.api_database import fetch_all, fetch_one, where_clause
from app.services.mart_routing import revenue_trend_mart
from app.services.metrics import ELIGIBLE_ORDER_TOTALS_CTE

router = APIRouter(prefix="/api/v1/dashboard", tags=["dashboard"])
Filters = Annotated[SharedFilters, Depends(get_shared_filters)]


@router.get("/summary", response_model=DataResponse[DashboardSummary])
async def summary(filters: Filters, _: CurrentUser) -> DataResponse[DashboardSummary]:
    if filters.active_dimensions():
        where_clause(filters, ())
    if filters.date_from or filters.date_to:
        where, values = where_clause(
            filters,
            ("date_from", "date_to"),
            aliases={"date_from": "date", "date_to": "date"},
        )
        row = await fetch_one(
            f"""SELECT min(date) AS period_start, max(date) AS period_end,
                       sum(revenue) AS total_revenue, sum(order_count)::integer AS total_orders,
                       CASE WHEN sum(order_count)=0 THEN 0 ELSE sum(revenue)/sum(order_count) END AS average_order_value
                FROM marts.revenue_daily{where}""",
            *values,
        )
        customer_where = where.replace("date", "purchase_ts::date")
        customer = await fetch_one(
            f"WITH {ELIGIBLE_ORDER_TOTALS_CTE} SELECT count(DISTINCT customer_unique_id)::integer AS total_customers FROM eligible_order_totals{customer_where}",
            *values,
        )
        assert row is not None and customer is not None
        row.update(customer)
        row.update(revenue_mom_growth_pct=None, revenue_yoy_growth_pct=None)
    else:
        row = await fetch_one(
            """SELECT period_start, period_end, total_revenue, total_orders,
                      total_customers, average_order_value, revenue_mom_growth_pct,
                      revenue_yoy_growth_pct FROM marts.kpi_snapshot WHERE snapshot_id=1"""
        )
    assert row is not None
    return DataResponse(data=DashboardSummary.model_validate(row))


@router.get("/revenue-trend", response_model=DataResponse[list[RevenuePoint]])
async def revenue_trend(
    filters: Filters, _: CurrentUser
) -> DataResponse[list[RevenuePoint]]:
    table, dimension_filters = revenue_trend_mart(filters)
    supported = ("date_from", "date_to", *dimension_filters)
    where, values = where_clause(
        filters, supported, aliases={"date_from": "date", "date_to": "date"}
    )
    rows = await fetch_all(
        f"""SELECT date, sum(revenue) AS revenue, sum(order_count)::integer AS order_count,
                   sum(customer_count)::integer AS customer_count
            FROM {table}{where} GROUP BY date ORDER BY date""",
        *values,
    )
    return DataResponse(data=[RevenuePoint.model_validate(row) for row in rows])


@router.get("/top-categories", response_model=DataResponse[list[PerformanceRow]])
async def top_categories(
    filters: Filters, _: CurrentUser, limit: int = Query(10, ge=1, le=100)
) -> DataResponse[list[PerformanceRow]]:
    where, values = where_clause(
        filters,
        ("date_from", "date_to", "category"),
        aliases={"date_from": "date", "date_to": "date"},
    )
    values.append(limit)
    rows = await fetch_all(
        f"""SELECT category AS key, sum(revenue) AS revenue, sum(order_count)::integer AS order_count,
                   sum(units)::integer AS units, NULL::numeric AS average_review_score
            FROM marts.revenue_by_category{where} GROUP BY category ORDER BY revenue DESC LIMIT ${len(values)}""",
        *values,
    )
    return DataResponse(data=[PerformanceRow.model_validate(row) for row in rows])


@router.get("/top-sellers", response_model=DataResponse[list[PerformanceRow]])
async def top_sellers(
    filters: Filters, _: CurrentUser, limit: int = Query(10, ge=1, le=100)
) -> DataResponse[list[PerformanceRow]]:
    where, values = where_clause(
        filters,
        ("date_from", "date_to", "seller_id"),
        aliases={"date_from": "date", "date_to": "date"},
    )
    values.append(limit)
    rows = await fetch_all(
        f"""SELECT seller_id AS key, sum(revenue) AS revenue, sum(order_count)::integer AS order_count,
                   sum(units)::integer AS units,
                   sum(avg_review_score*order_count)/nullif(sum(order_count),0) AS average_review_score
            FROM marts.seller_performance{where} GROUP BY seller_id ORDER BY revenue DESC LIMIT ${len(values)}""",
        *values,
    )
    return DataResponse(data=[PerformanceRow.model_validate(row) for row in rows])


@router.get("/top-products", response_model=DataResponse[list[ProductDetail]])
async def top_products(
    filters: Filters, _: CurrentUser, limit: int = Query(10, ge=1, le=100)
) -> DataResponse[list[ProductDetail]]:
    where, values = where_clause(
        filters,
        ("date_from", "date_to", "category", "seller_id"),
        aliases={
            "date_from": "o.purchase_ts::date",
            "date_to": "o.purchase_ts::date",
            "category": "p.category_name_english",
            "seller_id": "oi.seller_id",
        },
    )
    prefix = " AND" if where else " WHERE"
    values.append(limit)
    rows = await fetch_all(
        f"""SELECT oi.product_id, p.category_name_english AS category,
                   sum(oi.price+oi.freight_value) AS revenue, count(*)::integer AS units,
                   count(DISTINCT oi.order_id)::integer AS order_count
            FROM curated.order_items oi JOIN curated.orders o USING(order_id)
            JOIN curated.products p USING(product_id){where}{prefix} o.order_status='delivered'
            GROUP BY oi.product_id,p.category_name_english ORDER BY revenue DESC LIMIT ${len(values)}""",
        *values,
    )
    return DataResponse(data=[ProductDetail.model_validate(row) for row in rows])
