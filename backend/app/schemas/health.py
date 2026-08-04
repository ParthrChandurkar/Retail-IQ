"""Health endpoint response schemas."""

from typing import Literal

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Service and database health state."""

    status: Literal["ok"]
    database: Literal["reachable"]
