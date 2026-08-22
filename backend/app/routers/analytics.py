"""Phase 3 statistical outputs exposed as authenticated APIs."""

from typing import Annotated, Any

from fastapi import APIRouter, Depends

from app.core.dependencies import CurrentUser
from app.schemas.common import DataResponse
from app.schemas.filters import SharedFilters, get_shared_filters
from app.services.api_database import fetch_all, where_clause
from app.services.eda_service import analysis_frame, categorical_numeric_screen
from app.services.stats_service import (
    correlation_and_covariance,
    descriptive_statistics,
    run_statistical_analysis,
)

router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])
Filters = Annotated[SharedFilters, Depends(get_shared_filters)]


def _validate_unfiltered(filters: SharedFilters) -> None:
    """Phase 3 evidence is a fixed whole-dataset artifact, not a filterable mart."""
    where_clause(filters, ())


@router.get("/correlation-matrix", response_model=DataResponse[dict[str, Any]])
async def correlation_matrix(
    filters: Filters, _: CurrentUser
) -> DataResponse[dict[str, Any]]:
    _validate_unfiltered(filters)
    return DataResponse(data=await correlation_and_covariance())


@router.get("/hypothesis-tests", response_model=DataResponse[list[dict[str, Any]]])
async def hypothesis_tests(
    filters: Filters, _: CurrentUser
) -> DataResponse[list[dict[str, Any]]]:
    _validate_unfiltered(filters)
    result = await run_statistical_analysis()
    return DataResponse(data=result["hypothesis_tests"])


@router.get("/broad-screen", response_model=DataResponse[dict[str, Any]])
async def broad_screen(
    filters: Filters, _: CurrentUser
) -> DataResponse[dict[str, Any]]:
    """Expose the complete M3 categorical×numeric screen and field findings."""
    _validate_unfiltered(filters)
    return DataResponse(data=categorical_numeric_screen(await analysis_frame()))


@router.get("/descriptive-stats", response_model=DataResponse[list[dict[str, Any]]])
async def descriptive_stats(
    filters: Filters, _: CurrentUser
) -> DataResponse[list[dict[str, Any]]]:
    _validate_unfiltered(filters)
    return DataResponse(data=await descriptive_statistics())


@router.get("/seasonality", response_model=DataResponse[list[dict[str, Any]]])
async def seasonality(
    filters: Filters, _: CurrentUser
) -> DataResponse[list[dict[str, Any]]]:
    where, values = where_clause(
        filters,
        ("date_from", "date_to"),
        aliases={"date_from": "date", "date_to": "date"},
    )
    rows = await fetch_all(
        f"""SELECT extract(month FROM date)::integer AS month_number,
                  round(avg(revenue),2) average_daily_revenue,
                  sum(revenue) total_revenue,
                  sum(order_count)::integer order_count
           FROM marts.revenue_daily{where} GROUP BY 1 ORDER BY 1""",
        *values,
    )
    return DataResponse(data=rows)
