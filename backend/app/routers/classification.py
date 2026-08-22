"""Live model metadata, evaluation, explanation, and inference routes."""

from fastapi import APIRouter

from app.core.dependencies import CurrentUser
from app.schemas.classification import (
    GlobalFeature,
    ModelInfo,
    ModelMetrics,
    PredictionRequest,
    PredictionResult,
)
from app.schemas.common import DataResponse
from app.services.api_database import fetch_all
from app.services.classification_service import (
    active_bundle,
    active_model_row,
    predict_high_profit,
)

router = APIRouter(prefix="/api/v1/classification", tags=["classification"])


@router.get("/model-info", response_model=DataResponse[ModelInfo])
async def model_info(_: CurrentUser) -> DataResponse[ModelInfo]:
    row, bundle = await active_bundle()
    metadata = bundle["metadata"]
    data = {
        "model_id": row["model_id"],
        "target_variable": row["target_variable"],
        "algorithm": row["algorithm"],
        "trained_at": row["trained_at"],
        "positive_class": "high_profit_order",
        "negative_class": "standard_profit_order",
        "prediction_probability_semantics": (
            "Confidence in predicted_label: P(high_profit_order) when high; "
            "1-P(high_profit_order) when standard."
        ),
        "feature_columns": metadata["feature_columns"],
        "top_global_features": bundle["top_global_features"][:10],
    }
    return DataResponse(data=ModelInfo.model_validate(data))


@router.get("/metrics", response_model=DataResponse[ModelMetrics])
async def model_metrics(_: CurrentUser) -> DataResponse[ModelMetrics]:
    row = await active_model_row()
    data = {
        "model_id": row["model_id"],
        "algorithm": row["algorithm"],
        "positive_class": "high_profit_order",
        "negative_class": "standard_profit_order",
        **row["metrics_json"],
    }
    data.pop("all_model_metrics", None)
    return DataResponse(data=ModelMetrics.model_validate(data))


@router.get("/feature-importance", response_model=DataResponse[list[GlobalFeature]])
async def feature_importance(_: CurrentUser) -> DataResponse[list[GlobalFeature]]:
    row = await active_model_row()
    records = await fetch_all(
        """SELECT feature_name feature,importance::double precision importance
           FROM ml.feature_importance WHERE model_id=$1 ORDER BY importance DESC""",
        row["model_id"],
    )
    return DataResponse(
        data=[GlobalFeature.model_validate(record) for record in records]
    )


@router.post("/predict", response_model=DataResponse[PredictionResult])
async def predict(
    body: PredictionRequest, _: CurrentUser
) -> DataResponse[PredictionResult]:
    result = await predict_high_profit(body.model_dump())
    return DataResponse(data=PredictionResult.model_validate(result))
