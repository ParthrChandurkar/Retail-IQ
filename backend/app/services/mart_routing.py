"""Executable form of docs/mart-routing.md."""

from app.core.errors import APIError
from app.schemas.filters import SharedFilters


def revenue_trend_mart(filters: SharedFilters) -> tuple[str, tuple[str, ...]]:
    dimensions = filters.active_dimensions()
    if not dimensions:
        return "marts.revenue_daily", ()
    families = [
        (
            {"category", "sub_category"},
            "marts.revenue_by_category",
            ("category", "sub_category"),
        ),
        (
            {"region", "state", "city_type"},
            "marts.revenue_by_region",
            ("region", "state", "city_type"),
        ),
    ]
    for allowed, table, supported in families:
        if dimensions <= allowed:
            return table, supported
    raise APIError(
        400,
        "unsupported_filter_combination",
        "Revenue trend accepts either the category/sub-category family or the trusted region/state/city-type family.",
    )
