"""Customer analytics endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, Path

from app.core.dependencies import CurrentUser
from app.core.errors import APIError
from app.schemas.common import DataResponse, PageResponse
from app.schemas.domain import CustomerRow, DistributionRow, RepeatPurchase, SegmentRow
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
    where, values = where_clause(
        filters, ("customer_segment",), aliases={"customer_segment": "segment"}
    )
    rows = await fetch_all(
        f"SELECT * FROM marts.customer_segments{where} ORDER BY customer_count DESC",
        *values,
    )
    return DataResponse(data=[SegmentRow.model_validate(row) for row in rows])


@router.get("/rfm", response_model=PageResponse[CustomerRow])
async def rfm(
    filters: Filters, paging: Paging, _: CurrentUser
) -> PageResponse[CustomerRow]:
    aliases = {
        "state": "primary_state",
        "city": "primary_city",
        "customer_segment": "rfm_segment",
    }
    where, values = where_clause(
        filters, ("state", "city", "customer_segment"), aliases=aliases
    )
    total = await fetch_one(
        f"SELECT count(*)::integer AS count FROM marts.customer_profile{where}", *values
    )
    query_values = list(values)
    limit = pagination_sql(paging.page, paging.page_size, query_values)
    rows = await fetch_all(
        f"SELECT * FROM marts.customer_profile{where} ORDER BY total_spend DESC{limit}",
        *query_values,
    )
    return PageResponse(
        data=[CustomerRow.model_validate(row) for row in rows],
        page=paging.page,
        page_size=paging.page_size,
        total=total["count"] if total else 0,
    )


@router.get("/clv-distribution", response_model=DataResponse[list[DistributionRow]])
async def clv_distribution(
    filters: Filters, _: CurrentUser
) -> DataResponse[list[DistributionRow]]:
    where, values = where_clause(
        filters,
        ("state", "city", "customer_segment"),
        aliases={
            "state": "primary_state",
            "city": "primary_city",
            "customer_segment": "rfm_segment",
        },
    )
    rows = await fetch_all(
        f"""WITH selected AS (SELECT clv_historical, ntile(10) OVER (ORDER BY clv_historical) AS decile FROM marts.customer_profile{where})
            SELECT 'D' || decile AS bucket, count(*)::integer AS count FROM selected GROUP BY decile ORDER BY decile""",
        *values,
    )
    return DataResponse(data=[DistributionRow.model_validate(row) for row in rows])


@router.get("/repeat-purchase-rate", response_model=DataResponse[RepeatPurchase])
async def repeat_purchase(
    filters: Filters, _: CurrentUser
) -> DataResponse[RepeatPurchase]:
    where, values = where_clause(
        filters,
        ("state", "city", "customer_segment"),
        aliases={
            "state": "primary_state",
            "city": "primary_city",
            "customer_segment": "rfm_segment",
        },
    )
    row = await fetch_one(
        f"""SELECT count(*)::integer total_customers,
                   count(*) FILTER (WHERE order_count >= 2)::integer repeat_customers,
                   round(100.0*count(*) FILTER (WHERE order_count >= 2)/nullif(count(*),0),4) repeat_purchase_rate_pct
            FROM marts.customer_profile{where}""",
        *values,
    )
    assert row is not None
    return DataResponse(data=RepeatPurchase.model_validate(row))


@router.get("/{customer_unique_id}", response_model=DataResponse[CustomerRow])
async def customer_detail(
    _: CurrentUser, customer_unique_id: str = Path(min_length=1)
) -> DataResponse[CustomerRow]:
    row = await fetch_one(
        "SELECT * FROM marts.customer_profile WHERE customer_unique_id=$1",
        customer_unique_id,
    )
    if row is None:
        raise APIError(404, "customer_not_found", "Customer was not found.")
    return DataResponse(data=CustomerRow.model_validate(row))
