"""Shared migrated filter and pagination models."""

from datetime import date

from fastapi import Query
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator


class SharedFilters(BaseModel):
    """The M2 mart/filter contract represented as one validated value object."""

    model_config = ConfigDict(extra="forbid")

    date_from: date | None = None
    date_to: date | None = None
    region: str | None = None
    state: str | None = None
    city_type: str | None = None
    category: str | None = None
    sub_category: str | None = None
    segment: str | None = None
    ship_mode: str | None = None
    order_value_tier: str | None = None
    discount_band: str | None = None

    @model_validator(mode="after")
    def validate_ranges(self) -> "SharedFilters":
        if self.date_from and self.date_to and self.date_from > self.date_to:
            raise ValueError("date_from must be on or before date_to")
        return self

    def active_dimensions(self) -> set[str]:
        """Return non-date filters supplied by the caller."""
        return {
            name
            for name in (
                "region",
                "state",
                "city_type",
                "category",
                "sub_category",
                "segment",
                "ship_mode",
                "order_value_tier",
                "discount_band",
            )
            if getattr(self, name) is not None
        }


def get_shared_filters(
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    region: str | None = Query(default=None),
    state: str | None = Query(default=None),
    city_type: str | None = Query(default=None),
    category: str | None = Query(default=None),
    sub_category: str | None = Query(default=None),
    segment: str | None = Query(default=None),
    ship_mode: str | None = Query(default=None),
    order_value_tier: str | None = Query(default=None),
    discount_band: str | None = Query(default=None),
) -> SharedFilters:
    """Build the shared migrated filter object as a FastAPI dependency."""
    try:
        return SharedFilters(
            date_from=date_from,
            date_to=date_to,
            region=region,
            state=state,
            city_type=city_type,
            category=category,
            sub_category=sub_category,
            segment=segment,
            ship_mode=ship_mode,
            order_value_tier=order_value_tier,
            discount_band=discount_band,
        )
    except ValidationError as error:
        raise RequestValidationError(error.errors()) from error


class Pagination(BaseModel):
    """Validated page controls shared by list endpoints."""

    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=50, ge=1, le=200)

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size


def get_pagination(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=200),
) -> Pagination:
    return Pagination(page=page, page_size=page_size)
