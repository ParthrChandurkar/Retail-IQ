"""Application health endpoint."""

from fastapi import APIRouter
from sqlalchemy import text

from app.db.connection import engine
from app.schemas.health import HealthResponse

router = APIRouter(tags=["health"])


async def check_database_connection() -> None:
    """Raise when PostgreSQL cannot answer a minimal query."""
    async with engine.connect() as connection:
        await connection.execute(text("SELECT 1"))


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Confirm that the API and PostgreSQL connection are healthy."""
    await check_database_connection()
    return HealthResponse(status="ok", database="reachable")
