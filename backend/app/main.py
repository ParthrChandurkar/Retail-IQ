"""FastAPI application factory for Retail IQ."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db.bootstrap import create_schemas
from app.routers.health import router as health_router


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Create the four empty PostgreSQL schemas before serving requests."""
    await create_schemas()
    yield


def create_app(*, enable_database_bootstrap: bool = True) -> FastAPI:
    """Create and configure the FastAPI application."""
    application = FastAPI(
        title="Retail IQ API",
        version="0.1.0",
        lifespan=lifespan if enable_database_bootstrap else None,
    )
    application.include_router(health_router)
    return application


app = create_app()
