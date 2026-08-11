"""Product, seller, regional, payment, and review domain routers."""

from typing import Annotated, Any

from fastapi import APIRouter, Depends, Path

from app.core.dependencies import CurrentUser
from app.core.errors import APIError
from app.schemas.common import DataResponse
from app.schemas.domain import (
    DeliveryRow,
    DistributionRow,
    PaymentRow,
    PerformanceRow,
    ProductDetail,
    RegionRow,
    ReviewRow,
    SellerDetail,
)
from app.schemas.filters import SharedFilters, get_shared_filters
from app.services.api_database import fetch_all, fetch_one, where_clause

Filters = Annotated[SharedFilters, Depends(get_shared_filters)]
products_router = APIRouter(prefix="/api/v1/products", tags=["products"])
sellers_router = APIRouter(prefix="/api/v1/sellers", tags=["sellers"])
regions_router = APIRouter(prefix="/api/v1/regions", tags=["regions"])
payments_router = APIRouter(prefix="/api/v1/payments", tags=["payments"])
reviews_router = APIRouter(prefix="/api/v1/reviews", tags=["reviews"])


async def _category_performance(filters: SharedFilters) -> list[PerformanceRow]:
    where, values = where_clause(
        filters,
        ("date_from", "date_to", "category"),
        aliases={"date_from": "date", "date_to": "date"},
    )
    rows = await fetch_all(
        f"""SELECT category AS key, sum(revenue) revenue, sum(order_count)::integer order_count,
                   sum(units)::integer units, NULL::numeric average_review_score
            FROM marts.revenue_by_category{where} GROUP BY category ORDER BY revenue DESC""",
        *values,
    )
    return [PerformanceRow.model_validate(row) for row in rows]


@products_router.get("/performance", response_model=DataResponse[list[PerformanceRow]])
async def product_performance(
    filters: Filters, _: CurrentUser
) -> DataResponse[list[PerformanceRow]]:
    return DataResponse(data=await _category_performance(filters))


@products_router.get("/categories", response_model=DataResponse[list[PerformanceRow]])
async def product_categories(
    filters: Filters, _: CurrentUser
) -> DataResponse[list[PerformanceRow]]:
    return DataResponse(data=await _category_performance(filters))


@products_router.get("/{product_id}", response_model=DataResponse[ProductDetail])
async def product_detail(
    _: CurrentUser, product_id: str = Path(min_length=1)
) -> DataResponse[ProductDetail]:
    row = await fetch_one(
        """SELECT p.product_id, p.category_name_english category,
                  coalesce(sum(oi.price+oi.freight_value) FILTER (WHERE o.order_status='delivered'),0) revenue,
                  count(oi.*) FILTER (WHERE o.order_status='delivered')::integer units,
                  count(DISTINCT oi.order_id) FILTER (WHERE o.order_status='delivered')::integer order_count
           FROM curated.products p LEFT JOIN curated.order_items oi USING(product_id)
           LEFT JOIN curated.orders o USING(order_id) WHERE p.product_id=$1
           GROUP BY p.product_id,p.category_name_english""",
        product_id,
    )
    if row is None:
        raise APIError(404, "product_not_found", "Product was not found.")
    return DataResponse(data=ProductDetail.model_validate(row))


@sellers_router.get("/performance", response_model=DataResponse[list[PerformanceRow]])
async def seller_performance(
    filters: Filters, _: CurrentUser
) -> DataResponse[list[PerformanceRow]]:
    where, values = where_clause(
        filters,
        ("date_from", "date_to", "seller_id"),
        aliases={"date_from": "date", "date_to": "date"},
    )
    rows = await fetch_all(
        f"""SELECT seller_id key, sum(revenue) revenue, sum(order_count)::integer order_count,
                   sum(units)::integer units,
                   sum(avg_review_score*order_count)/nullif(sum(order_count),0) average_review_score
            FROM marts.seller_performance{where} GROUP BY seller_id ORDER BY revenue DESC""",
        *values,
    )
    return DataResponse(data=[PerformanceRow.model_validate(row) for row in rows])


@sellers_router.get("/{seller_id}", response_model=DataResponse[SellerDetail])
async def seller_detail(
    _: CurrentUser, seller_id: str = Path(min_length=1)
) -> DataResponse[SellerDetail]:
    row = await fetch_one(
        """SELECT s.seller_id,s.city,s.state,coalesce(sum(m.revenue),0) revenue,
                  coalesce(sum(m.order_count),0)::integer order_count,
                  coalesce(sum(m.units),0)::integer units,
                  sum(m.avg_review_score*m.order_count)/nullif(sum(m.order_count),0) average_review_score
           FROM curated.sellers s LEFT JOIN marts.seller_performance m USING(seller_id)
           WHERE s.seller_id=$1 GROUP BY s.seller_id,s.city,s.state""",
        seller_id,
    )
    if row is None:
        raise APIError(404, "seller_not_found", "Seller was not found.")
    return DataResponse(data=SellerDetail.model_validate(row))


async def _region_rows(filters: SharedFilters, geo: bool = False) -> list[RegionRow]:
    where, values = where_clause(
        filters,
        ("date_from", "date_to", "state", "city"),
        aliases={"date_from": "date", "date_to": "date"},
    )
    city_column = "city" if geo or filters.city else "NULL::text"
    group = "state,city" if geo or filters.city else "state"
    rows = await fetch_all(
        f"""SELECT state,{city_column} city,sum(revenue) revenue,sum(order_count)::integer order_count,
                   sum(customer_count)::integer customer_count,
                   avg(latitude) latitude,avg(longitude) longitude
            FROM marts.revenue_by_region{where} GROUP BY {group} ORDER BY revenue DESC""",
        *values,
    )
    return [RegionRow.model_validate(row) for row in rows]


@regions_router.get("/sales", response_model=DataResponse[list[RegionRow]])
async def region_sales(
    filters: Filters, _: CurrentUser
) -> DataResponse[list[RegionRow]]:
    return DataResponse(data=await _region_rows(filters))


@regions_router.get("/geo", response_model=DataResponse[list[RegionRow]])
async def region_geo(filters: Filters, _: CurrentUser) -> DataResponse[list[RegionRow]]:
    return DataResponse(data=await _region_rows(filters, geo=True))


@regions_router.get(
    "/delivery-performance", response_model=DataResponse[list[DeliveryRow]]
)
async def delivery_performance(
    filters: Filters, _: CurrentUser
) -> DataResponse[list[DeliveryRow]]:
    supported = (
        "date_from",
        "date_to",
        "state",
        "city",
        "category",
        "seller_id",
        "payment_type",
        "customer_segment",
        "review_score_min",
        "review_score_max",
    )
    where, values = where_clause(
        filters,
        supported,
        aliases={
            "date_from": "date",
            "date_to": "date",
            "review_score_min": "review_score",
            "review_score_max": "review_score",
        },
    )
    rows = await fetch_all(
        f"""SELECT state,city,sum(order_count)::integer order_count,sum(delivered_count)::integer delivered_count,
                   sum(late_count)::integer late_count,
                   coalesce(round(100.0*sum(late_count)/nullif(sum(delivered_count),0),4),0) late_rate_pct,
                   sum(avg_delivery_days*delivered_count)/nullif(sum(delivered_count),0) avg_delivery_days
            FROM marts.delivery_performance{where} GROUP BY state,city ORDER BY order_count DESC""",
        *values,
    )
    return DataResponse(data=[DeliveryRow.model_validate(row) for row in rows])


@payments_router.get("/method-mix", response_model=DataResponse[list[PaymentRow]])
async def method_mix(
    filters: Filters, _: CurrentUser
) -> DataResponse[list[PaymentRow]]:
    where, values = where_clause(
        filters,
        ("date_from", "date_to", "payment_type"),
        aliases={"date_from": "date", "date_to": "date"},
    )
    rows = await fetch_all(
        f"""SELECT payment_type,sum(payment_count)::integer payment_count,sum(order_count)::integer order_count,
                   sum(payment_value) payment_value,
                   sum(avg_installments*payment_count)/nullif(sum(payment_count),0) avg_installments
            FROM marts.payment_method_mix{where} GROUP BY payment_type ORDER BY payment_value DESC""",
        *values,
    )
    return DataResponse(data=[PaymentRow.model_validate(row) for row in rows])


@payments_router.get(
    "/installments-distribution", response_model=DataResponse[list[DistributionRow]]
)
async def installments_distribution(
    filters: Filters, _: CurrentUser
) -> DataResponse[list[DistributionRow]]:
    where, values = where_clause(
        filters,
        ("date_from", "date_to", "payment_type"),
        aliases={
            "date_from": "o.purchase_ts::date",
            "date_to": "o.purchase_ts::date",
            "payment_type": "pd.payment_type",
        },
    )
    rows = await fetch_all(
        f"""SELECT coalesce(pd.payment_installments,0)::text bucket,count(*)::integer count
            FROM curated.payment_details pd JOIN curated.orders o USING(order_id){where}
            GROUP BY pd.payment_installments ORDER BY pd.payment_installments""",
        *values,
    )
    return DataResponse(data=[DistributionRow.model_validate(row) for row in rows])


async def _review_rows(filters: SharedFilters, trend: bool) -> list[ReviewRow]:
    supported = (
        "date_from",
        "date_to",
        "state",
        "city",
        "category",
        "seller_id",
        "payment_type",
        "customer_segment",
        "review_score_min",
        "review_score_max",
    )
    where, values = where_clause(
        filters,
        supported,
        aliases={
            "date_from": "date",
            "date_to": "date",
            "review_score_min": "review_score",
            "review_score_max": "review_score",
        },
    )
    key = "date::text" if trend else "review_score::text"
    group = "date" if trend else "review_score"
    rows = await fetch_all(
        f"""SELECT {key} key,sum(review_count)::integer review_count,
                   sum(avg_review_score*review_count)/nullif(sum(review_count),0) average_review_score,
                   sum(comments_with_text)::integer comments_with_text
            FROM marts.review_summary{where} GROUP BY {group} ORDER BY {group}""",
        *values,
    )
    return [ReviewRow.model_validate(row) for row in rows]


@reviews_router.get("/score-distribution", response_model=DataResponse[list[ReviewRow]])
async def score_distribution(
    filters: Filters, _: CurrentUser
) -> DataResponse[list[ReviewRow]]:
    return DataResponse(data=await _review_rows(filters, False))


@reviews_router.get("/trends", response_model=DataResponse[list[ReviewRow]])
async def review_trends(
    filters: Filters, _: CurrentUser
) -> DataResponse[list[ReviewRow]]:
    return DataResponse(data=await _review_rows(filters, True))


@reviews_router.get("/nlp-summary", response_model=DataResponse[dict[str, Any]])
async def nlp_summary(filters: Filters, _: CurrentUser) -> DataResponse[dict[str, Any]]:
    """Return the governed score/trend fallback after the Phase 6 NLP no-go."""
    distribution = await _review_rows(filters, False)
    trends = await _review_rows(filters, True)
    return DataResponse(
        data={
            "decision": "no-go",
            "fallback": "review_score_distribution_and_trend",
            "score_distribution": [row.model_dump() for row in distribution],
            "trends": [row.model_dump() for row in trends],
        }
    )
