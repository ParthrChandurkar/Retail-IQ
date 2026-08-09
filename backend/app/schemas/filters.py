"""Shared SRS §9.6 filter and pagination models."""

from datetime import date

from fastapi import Query
from pydantic import BaseModel, Field, model_validator


class SharedFilters(BaseModel):
    """All shared dashboard filters in one validated value object."""

    date_from: date | None = None
    date_to: date | None = None
    state: str | None = None
    city: str | None = None
    category: str | None = None
    seller_id: str | None = None
    payment_type: str | None = None
    customer_segment: str | None = None
    review_score_min: int | None = Field(default=None, ge=1, le=5)
    review_score_max: int | None = Field(default=None, ge=1, le=5)

    @model_validator(mode="after")
    def validate_ranges(self) -> "SharedFilters":
        """Reject inverted ranges and ambiguous city-only geography."""
        if self.date_from and self.date_to and self.date_from > self.date_to:
            raise ValueError("date_from must be on or before date_to")
        if self.review_score_min and self.review_score_max:
            if self.review_score_min > self.review_score_max:
                raise ValueError("review_score_min must not exceed review_score_max")
        if self.city and not self.state:
            raise ValueError("city requires state")
        return self

    def active_dimensions(self) -> set[str]:
        """Return non-date filter names supplied by the caller."""
        return {
            name
            for name in (
                "state",
                "city",
                "category",
                "seller_id",
                "payment_type",
                "customer_segment",
                "review_score_min",
                "review_score_max",
            )
            if getattr(self, name) is not None
        }


def get_shared_filters(
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    state: str | None = Query(default=None, min_length=2, max_length=2),
    city: str | None = Query(default=None),
    category: str | None = Query(default=None),
    seller_id: str | None = Query(default=None),
    payment_type: str | None = Query(default=None),
    customer_segment: str | None = Query(default=None),
    review_score_min: int | None = Query(default=None, ge=1, le=5),
    review_score_max: int | None = Query(default=None, ge=1, le=5),
) -> SharedFilters:
    """Build the shared filter object as a FastAPI dependency."""
    return SharedFilters(
        date_from=date_from,
        date_to=date_to,
        state=state,
        city=city,
        category=category,
        seller_id=seller_id,
        payment_type=payment_type,
        customer_segment=customer_segment,
        review_score_min=review_score_min,
        review_score_max=review_score_max,
    )


class Pagination(BaseModel):
    """Validated page controls shared by list endpoints."""

    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=50, ge=1, le=200)

    @property
    def offset(self) -> int:
        """Return the SQL offset represented by this page."""
        return (self.page - 1) * self.page_size


def get_pagination(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=200),
) -> Pagination:
    """Build pagination controls as a FastAPI dependency."""
    return Pagination(page=page, page_size=page_size)
