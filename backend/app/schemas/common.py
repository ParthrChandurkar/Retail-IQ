"""Shared typed API response envelopes."""

from datetime import UTC, datetime
from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


def utc_now() -> datetime:
    """Return a timezone-aware UTC response timestamp."""
    return datetime.now(UTC)


class DataResponse(BaseModel, Generic[T]):
    """Standard single-object or aggregate response."""

    generated_at: datetime = Field(default_factory=utc_now)
    data: T


class PageResponse(BaseModel, Generic[T]):
    """Standard paginated list response."""

    generated_at: datetime = Field(default_factory=utc_now)
    data: list[T]
    page: int
    page_size: int
    total: int


class ProblemResponse(BaseModel):
    """Stable error contract for OpenAPI documentation."""

    generated_at: datetime
    detail: str
    code: str
