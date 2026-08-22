"""Cross-sectional customer analytics endpoints for the migrated dataset."""

from typing import Annotated

from fastapi import APIRouter, Depends, Path

from app.core.dependencies import CurrentUser
from app.core.errors import APIError
from app.schemas.common import DataResponse, PageResponse
from app.schemas.domain import (
    CustomerDetail,
    CustomerProfile,
    DistributionRow,
    SegmentRow,
)
from app.schemas.filters import (
    Pagination,
    SharedFilters,
    get_pagination,
    get_shared_filters,
)
from app.services.api_database import fetch_all, fetch_one, pagination_sql, where_clause

router = APIRouter(prefix="/api/v1/customers", tags=["customers"])
Filters = Annotated[SharedFilters, Depends(get_shared_filters)]
Paging = Annotated[Pagination, Depends(get_pagination)]


@router.get("/segments", response_model=DataResponse[list[SegmentRow]])
async def segments(filters: Filters, _: CurrentUser) -> DataResponse[list[SegmentRow]]:
    where, values = where_clause(filters, ("segment", "city_type", "order_value_tier"))
    rows = await fetch_all(
        f"""SELECT segment,order_value_tier,city_type,customer_count,
                   avg_order_value,avg_profit,avg_discount_pct
            FROM marts.customer_segments{where}
            ORDER BY segment,order_value_tier,city_type""",
        *values,
    )
    return DataResponse(data=[SegmentRow.model_validate(row) for row in rows])


@router.get("/profiles", response_model=PageResponse[CustomerProfile])
async def profiles(
    filters: Filters, paging: Paging, _: CurrentUser
) -> PageResponse[CustomerProfile]:
    where, values = where_clause(
        filters,
        (
            "date_from",
            "date_to",
            "region",
            "state",
            "city_type",
            "segment",
            "order_value_tier",
        ),
        aliases={"date_from": "order_date", "date_to": "order_date"},
    )
    total = await fetch_one(
        f"SELECT count(*)::integer AS count FROM marts.customer_profile{where}", *values
    )
    query_values = list(values)
    limit = pagination_sql(paging.page, paging.page_size, query_values)
    rows = await fetch_all(
        f"""SELECT customer_id,order_date,recency_days,order_value,profit,
                   discount_pct,segment,city_type,region,state,order_value_tier
            FROM marts.customer_profile{where}
            ORDER BY order_value DESC{limit}""",
        *query_values,
    )
    return PageResponse(
        data=[CustomerProfile.model_validate(row) for row in rows],
        page=paging.page,
        page_size=paging.page_size,
        total=total["count"] if total else 0,
    )


@router.get(
    "/order-value-distribution", response_model=DataResponse[list[DistributionRow]]
)
async def order_value_distribution(
    filters: Filters, _: CurrentUser
) -> DataResponse[list[DistributionRow]]:
    where, values = where_clause(
        filters,
        (
            "date_from",
            "date_to",
            "region",
            "state",
            "city_type",
            "segment",
            "order_value_tier",
        ),
        aliases={"date_from": "order_date", "date_to": "order_date"},
    )
    rows = await fetch_all(
        f"""SELECT order_value_tier AS bucket,count(*)::integer AS count
            FROM marts.customer_profile{where}
            GROUP BY order_value_tier ORDER BY order_value_tier""",
        *values,
    )
    return DataResponse(data=[DistributionRow.model_validate(row) for row in rows])


@router.get("/{customer_id}", response_model=DataResponse[CustomerDetail])
async def customer_detail(
    _: CurrentUser, customer_id: str = Path(min_length=1)
) -> DataResponse[CustomerDetail]:
    row = await fetch_one(
        """SELECT cp.customer_id,cp.order_date,cp.recency_days,cp.order_value,
                  cp.profit,cp.discount_pct,cp.segment,cp.city_type,cp.region,
                  cp.state,cp.order_value_tier,c.first_name,c.last_name
           FROM marts.customer_profile cp
           JOIN curated.customers c USING(customer_id)
           WHERE cp.customer_id=$1""",
        customer_id,
    )
    if row is None:
        raise APIError(404, "customer_not_found", "Customer was not found.")
    return DataResponse(data=CustomerDetail.model_validate(row))
