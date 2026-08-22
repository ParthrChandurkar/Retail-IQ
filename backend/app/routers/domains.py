"""Migrated product and Indian regional domain routers."""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.dependencies import CurrentUser
from app.schemas.common import DataResponse
from app.schemas.domain import (
    DiscountProfitRow,
    PerformanceRow,
    RegionRow,
    ShippingRow,
)
from app.schemas.filters import SharedFilters, get_shared_filters
from app.services.api_database import fetch_all, where_clause

Filters = Annotated[SharedFilters, Depends(get_shared_filters)]
products_router = APIRouter(prefix="/api/v1/products", tags=["products"])
regions_router = APIRouter(prefix="/api/v1/regions", tags=["regions"])


async def _product_performance(
    filters: SharedFilters, *, include_sub_category: bool
) -> list[PerformanceRow]:
    where, values = where_clause(
        filters,
        ("date_from", "date_to", "category", "sub_category"),
        aliases={"date_from": "date", "date_to": "date"},
    )
    key = "category || ' / ' || sub_category" if include_sub_category else "category"
    group = "category,sub_category" if include_sub_category else "category"
    rows = await fetch_all(
        f"""SELECT {key} AS key, sum(revenue) revenue,
                   sum(total_profit) total_profit,
                   sum(order_count)::integer order_count,
                   sum(units)::integer units,
                   sum(avg_discount_pct*order_count)/nullif(sum(order_count),0) avg_discount_pct,
                   100.0*sum(total_profit)/nullif(sum(revenue),0) profit_margin_pct
            FROM marts.revenue_by_category{where}
            GROUP BY {group} ORDER BY revenue DESC""",
        *values,
    )
    return [PerformanceRow.model_validate(row) for row in rows]


@products_router.get("/performance", response_model=DataResponse[list[PerformanceRow]])
async def product_performance(
    filters: Filters, _: CurrentUser
) -> DataResponse[list[PerformanceRow]]:
    """Return category/sub-category performance; Product ID is not analytical."""
    return DataResponse(
        data=await _product_performance(filters, include_sub_category=True)
    )


@products_router.get("/categories", response_model=DataResponse[list[PerformanceRow]])
async def product_categories(
    filters: Filters, _: CurrentUser
) -> DataResponse[list[PerformanceRow]]:
    return DataResponse(
        data=await _product_performance(filters, include_sub_category=False)
    )


@products_router.get(
    "/discount-profit", response_model=DataResponse[list[DiscountProfitRow]]
)
async def discount_profit(
    filters: Filters, _: CurrentUser
) -> DataResponse[list[DiscountProfitRow]]:
    where, values = where_clause(filters, ("category", "sub_category", "discount_band"))
    rows = await fetch_all(
        f"""SELECT category,sub_category,discount_band,order_count,revenue,
                   total_profit,avg_discount_pct,avg_profit_margin_pct
            FROM marts.category_discount_profit{where}
            ORDER BY category,sub_category,discount_band""",
        *values,
    )
    return DataResponse(data=[DiscountProfitRow.model_validate(row) for row in rows])


async def _regional_rows(
    filters: SharedFilters, *, include_city_type: bool
) -> list[RegionRow]:
    where, values = where_clause(
        filters,
        ("date_from", "date_to", "region", "state", "city_type"),
        aliases={"date_from": "date", "date_to": "date"},
    )
    city_select = "city_type" if include_city_type else "NULL::text AS city_type"
    group = "state,region,city_type" if include_city_type else "state,region"
    rows = await fetch_all(
        f"""SELECT state,region,{city_select},sum(revenue) revenue,
                   sum(total_profit) total_profit,
                   sum(order_count)::integer order_count,
                   sum(customer_count)::integer customer_count,
                   sum(avg_discount_pct*order_count)/nullif(sum(order_count),0) avg_discount_pct,
                   100.0*sum(total_profit)/nullif(sum(revenue),0) profit_margin_pct,
                   avg(latitude)::double precision latitude,
                   avg(longitude)::double precision longitude
            FROM marts.revenue_by_region{where}
            GROUP BY {group} ORDER BY revenue DESC""",
        *values,
    )
    return [RegionRow.model_validate(row) for row in rows]


@regions_router.get("/sales", response_model=DataResponse[list[RegionRow]])
async def region_sales(
    filters: Filters, _: CurrentUser
) -> DataResponse[list[RegionRow]]:
    return DataResponse(data=await _regional_rows(filters, include_city_type=True))


@regions_router.get("/choropleth", response_model=DataResponse[list[RegionRow]])
async def region_choropleth(
    filters: Filters, _: CurrentUser
) -> DataResponse[list[RegionRow]]:
    """Return state totals located only at governed state centroids."""
    return DataResponse(data=await _regional_rows(filters, include_city_type=False))


@regions_router.get(
    "/shipping-performance", response_model=DataResponse[list[ShippingRow]]
)
async def shipping_performance(
    filters: Filters, _: CurrentUser
) -> DataResponse[list[ShippingRow]]:
    where, values = where_clause(
        filters,
        ("date_from", "date_to", "region", "ship_mode"),
        aliases={"date_from": "date", "date_to": "date"},
    )
    rows = await fetch_all(
        f"""SELECT date,ship_mode,region,order_count,avg_shipping_days,
                   median_shipping_days,min_shipping_days,max_shipping_days
            FROM marts.shipping_performance{where}
            ORDER BY date,region,ship_mode""",
        *values,
    )
    return DataResponse(data=[ShippingRow.model_validate(row) for row in rows])
