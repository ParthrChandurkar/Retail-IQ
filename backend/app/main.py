"""FastAPI application factory for Retail IQ."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.errors import install_exception_handlers
from app.db.bootstrap import create_schemas
from app.routers.analytics import router as analytics_router
from app.routers.auth import router as auth_router
from app.routers.customers import router as customers_router
from app.routers.dashboard import router as dashboard_router
from app.routers.domains import (
    payments_router,
    products_router,
    regions_router,
    reviews_router,
    sellers_router,
)
from app.routers.health import router as health_router
from app.routers.system import (
    admin_router,
    classification_router,
    recommendations_router,
)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Create the four empty PostgreSQL schemas before serving requests."""
    await create_schemas()
    yield


def create_app(*, enable_database_bootstrap: bool = True) -> FastAPI:
    """Create and configure the FastAPI application."""
    application = FastAPI(
        title="Retail IQ API",
        version="1.0.0",
        openapi_url="/api/v1/openapi.json",
        lifespan=lifespan if enable_database_bootstrap else None,
    )
    settings = get_settings()
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.include_router(health_router)
    for router in (
        auth_router,
        dashboard_router,
        customers_router,
        products_router,
        sellers_router,
        regions_router,
        payments_router,
        reviews_router,
        analytics_router,
        classification_router,
        recommendations_router,
        admin_router,
    ):
        application.include_router(router)
    install_exception_handlers(application)
    return application


app = create_app()
