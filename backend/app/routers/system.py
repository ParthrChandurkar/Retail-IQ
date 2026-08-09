"""Recommendations, classification placeholders, and administration routes."""

import json
from typing import Any

from fastapi import APIRouter

from app.core.dependencies import AdminUser, CurrentUser
from app.core.errors import APIError
from app.schemas.common import DataResponse
from app.schemas.domain import AdminSettingPayload, Recommendation, RefreshStatus
from app.services.api_database import execute, fetch_all, fetch_one
from app.services.recommendation_service import build_recommendations

recommendations_router = APIRouter(prefix="/api/v1", tags=["recommendations"])
classification_router = APIRouter(
    prefix="/api/v1/classification", tags=["classification"]
)
admin_router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


@recommendations_router.get(
    "/recommendations", response_model=DataResponse[list[Recommendation]]
)
async def recommendations(_: CurrentUser) -> DataResponse[list[Recommendation]]:
    rows = await build_recommendations()
    return DataResponse(data=[Recommendation.model_validate(row) for row in rows])


def _not_implemented() -> None:
    raise APIError(
        501,
        "classification_not_implemented",
        "Classification becomes available after Phase 6 model training.",
    )


@classification_router.get("/model-info", response_model=DataResponse[dict[str, Any]])
async def model_info(_: CurrentUser) -> None:
    _not_implemented()


@classification_router.get("/metrics", response_model=DataResponse[dict[str, Any]])
async def model_metrics(_: CurrentUser) -> None:
    _not_implemented()


@classification_router.get(
    "/feature-importance", response_model=DataResponse[list[dict[str, Any]]]
)
async def feature_importance(_: CurrentUser) -> None:
    _not_implemented()


@classification_router.post("/predict", response_model=DataResponse[dict[str, Any]])
async def predict(_: CurrentUser, payload: dict[str, Any]) -> None:
    del payload
    _not_implemented()


@admin_router.get("/settings", response_model=DataResponse[AdminSettingPayload])
async def get_settings(_: AdminUser) -> DataResponse[AdminSettingPayload]:
    rows = await fetch_all("SELECT key,value FROM curated.admin_settings ORDER BY key")
    return DataResponse(
        data=AdminSettingPayload(settings={row["key"]: row["value"] for row in rows})
    )


@admin_router.put("/settings", response_model=DataResponse[AdminSettingPayload])
async def put_settings(
    body: AdminSettingPayload, _: AdminUser
) -> DataResponse[AdminSettingPayload]:
    for key, value in body.settings.items():
        await execute(
            """INSERT INTO curated.admin_settings(key,value,updated_at) VALUES($1,$2::jsonb,now())
               ON CONFLICT(key) DO UPDATE SET value=excluded.value,updated_at=now()""",
            key,
            json.dumps(value),
        )
    return DataResponse(data=body)


@admin_router.get("/data-refresh-status", response_model=DataResponse[RefreshStatus])
async def data_refresh_status(_: AdminUser) -> DataResponse[RefreshStatus]:
    row = await fetch_one(
        """SELECT job_name,started_at,finished_at,status,rows_affected,error_message
           FROM curated.data_refresh_log ORDER BY started_at DESC LIMIT 1"""
    )
    if row is None:
        raise APIError(
            404, "refresh_status_unavailable", "No data refresh has run yet."
        )
    return DataResponse(data=RefreshStatus.model_validate(row))
