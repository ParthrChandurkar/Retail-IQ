"""Executable form of docs/mart-routing.md."""

from app.core.errors import APIError
from app.schemas.filters import SharedFilters


def revenue_trend_mart(filters: SharedFilters) -> tuple[str, tuple[str, ...]]:
    dimensions = filters.active_dimensions()
    if not dimensions:
        return "marts.revenue_daily", ()
    families = [
        ({"category"}, "marts.revenue_by_category", ("category",)),
        ({"state", "city"}, "marts.revenue_by_region", ("state", "city")),
        ({"seller_id"}, "marts.seller_performance", ("seller_id",)),
    ]
    for allowed, table, supported in families:
        if dimensions <= allowed:
            return table, supported
    raise APIError(
        400,
        "unsupported_filter_combination",
        "Revenue trend accepts one of category, geography, or seller filter families; payment value is not revenue.",
    )
