"""Cross-cutting migrated dashboard endpoints backed by Indian-data marts."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.core.dependencies import CurrentUser
from app.schemas.common import DataResponse
from app.schemas.domain import DashboardSummary, PerformanceRow, RevenuePoint
from app.schemas.filters import SharedFilters, get_shared_filters
from app.services.api_database import fetch_all, fetch_one, where_clause
from app.services.mart_routing import revenue_trend_mart

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
            f"""SELECT min(date) period_start,max(date) period_end,
                       sum(revenue) total_revenue,sum(total_profit) total_profit,
                       sum(order_count)::integer total_orders,
                       sum(revenue)/nullif(sum(order_count),0) average_order_value,
                       sum(avg_discount_pct*order_count)/nullif(sum(order_count),0) avg_discount_pct,
                       100.0*sum(total_profit)/nullif(sum(revenue),0) profit_margin_pct
                FROM marts.revenue_daily{where}""",
            *values,
        )
        customer_where = where.replace("date", "order_date")
        customer = await fetch_one(
            f"""SELECT count(DISTINCT customer_id)::integer total_customers
                FROM marts.customer_profile{customer_where}""",
            *values,
        )
        assert row is not None and customer is not None
        row.update(customer)
        row.update(revenue_mom_growth_pct=None, revenue_yoy_growth_pct=None)
    else:
        row = await fetch_one(
            """SELECT period_start,period_end,total_revenue,total_profit,
                      total_orders,total_customers,average_order_value,
                      average_discount_pct AS avg_discount_pct,profit_margin_pct,
                      revenue_mom_growth_pct,revenue_yoy_growth_pct
               FROM marts.kpi_snapshot WHERE snapshot_id=1"""
        )
    assert row is not None
    return DataResponse(data=DashboardSummary.model_validate(row))


@router.get("/revenue-trend", response_model=DataResponse[list[RevenuePoint]])
async def revenue_trend(
    filters: Filters, _: CurrentUser
) -> DataResponse[list[RevenuePoint]]:
    table, dimension_filters = revenue_trend_mart(filters)
    where, values = where_clause(
        filters,
        ("date_from", "date_to", *dimension_filters),
        aliases={"date_from": "date", "date_to": "date"},
    )
    rows = await fetch_all(
        f"""SELECT date,sum(revenue) revenue,sum(total_profit) total_profit,
                   sum(order_count)::integer order_count,
                   sum(customer_count)::integer customer_count
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
        ("date_from", "date_to", "category", "sub_category"),
        aliases={"date_from": "date", "date_to": "date"},
    )
    values.append(limit)
    rows = await fetch_all(
        f"""SELECT category AS key,sum(revenue) revenue,
                   sum(total_profit) total_profit,
                   sum(order_count)::integer order_count,
                   sum(units)::integer units,
                   sum(avg_discount_pct*order_count)/nullif(sum(order_count),0) avg_discount_pct,
                   100.0*sum(total_profit)/nullif(sum(revenue),0) profit_margin_pct
            FROM marts.revenue_by_category{where}
            GROUP BY category ORDER BY revenue DESC LIMIT ${len(values)}""",
        *values,
    )
    return DataResponse(data=[PerformanceRow.model_validate(row) for row in rows])
