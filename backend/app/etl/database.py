"""Low-level database helpers for batch ETL jobs."""

import asyncpg
from sqlalchemy.engine import make_url

from app.core.config import get_settings


def asyncpg_dsn() -> str:
    """Convert the SQLAlchemy async URL into an asyncpg-compatible DSN."""
    url = make_url(get_settings().database_url).set(drivername="postgresql")
    return url.render_as_string(hide_password=False)


async def connect() -> asyncpg.Connection:
    """Open a direct asyncpg connection for high-throughput batch operations."""
    return await asyncpg.connect(asyncpg_dsn())
