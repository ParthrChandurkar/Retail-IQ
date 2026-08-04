"""Phase 1 database schema bootstrap."""

from sqlalchemy import text

from app.db.connection import engine

SCHEMA_NAMES = ("raw", "curated", "marts", "ml")


async def create_schemas() -> None:
    """Create the four required empty schemas idempotently."""
    async with engine.begin() as connection:
        for schema_name in SCHEMA_NAMES:
            await connection.execute(
                text(f'CREATE SCHEMA IF NOT EXISTS "{schema_name}"')
            )
