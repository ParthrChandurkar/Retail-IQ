"""Load and serve the active registered model without inline retraining."""

import json
from decimal import Decimal
from pathlib import Path
from typing import Any

import joblib
from sklearn.pipeline import Pipeline

from app.core.config import get_settings
from app.core.errors import APIError
from app.etl.database import connect
from app.ml.evaluate import positive_probability
from app.ml.features import request_frame

_bundle_cache: dict[int, dict[str, Any]] = {}


def label_and_confidence(
    predicted: int, probability_high_profit: float
) -> tuple[str, float]:
    """Return the migrated literal label and confidence in that label."""
    if predicted == 1:
        return "high_profit_order", probability_high_profit
    return "standard_profit_order", 1.0 - probability_high_profit


async def active_model_row() -> dict[str, Any]:
    connection = await connect()
    try:
        row = await connection.fetchrow(
            """SELECT model_id,target_variable,algorithm,trained_at,artifact_path,metrics_json
               FROM ml.model_registry WHERE is_active=true
               ORDER BY trained_at DESC,model_id DESC LIMIT 1"""
        )
    finally:
        await connection.close()
    if row is None:
        raise APIError(
            503, "model_unavailable", "No active classification model is registered."
        )
    result = dict(row)
    if result["target_variable"] != "is_high_profit_order":
        raise APIError(
            503,
            "retired_model_active",
            "The active registry row is not the migrated high-profit model.",
        )
    if isinstance(result["metrics_json"], str):
        result["metrics_json"] = json.loads(result["metrics_json"])
    return result


def _artifact_path(value: str) -> Path:
    stored = Path(value)
    if stored.exists():
        return stored
    candidate = get_settings().model_registry_dir / stored.name
    if candidate.exists():
        return candidate
    raise APIError(
        503, "model_artifact_missing", "The active model artifact is unavailable."
    )


async def active_bundle() -> tuple[dict[str, Any], dict[str, Any]]:
    row = await active_model_row()
    model_id = int(row["model_id"])
    if model_id not in _bundle_cache:
        bundle = joblib.load(_artifact_path(str(row["artifact_path"])))
        if not isinstance(bundle, dict):
            raise APIError(
                503, "invalid_model_artifact", "The active artifact is invalid."
            )
        if int(bundle.get("model_id", -1)) != model_id:
            raise APIError(503, "invalid_model_artifact", "Artifact model ID mismatch.")
        if bundle.get("target_variable") != "is_high_profit_order":
            raise APIError(503, "retired_model_artifact", "Olist artifact is retired.")
        _bundle_cache.clear()
        _bundle_cache[model_id] = bundle
    return row, _bundle_cache[model_id]


async def predict_high_profit(payload: dict[str, Any]) -> dict[str, Any]:
    row, bundle = await active_bundle()
    pipeline = bundle["pipeline"]
    if not isinstance(pipeline, Pipeline):
        raise APIError(503, "invalid_model_artifact", "The active pipeline is invalid.")
    inputs = request_frame(payload)
    predicted = int(pipeline.predict(inputs)[0])
    probability_high_profit = float(positive_probability(pipeline, inputs)[0])
    label, confidence = label_and_confidence(predicted, probability_high_profit)
    connection = await connect()
    try:
        await connection.execute(
            """INSERT INTO ml.predictions
                 (model_id,entity_id,predicted_label,predicted_probability)
               VALUES($1,$2,$3,$4)""",
            int(row["model_id"]),
            payload["entity_id"],
            label,
            Decimal(str(confidence)),
        )
    finally:
        await connection.close()
    return {
        "model_id": int(row["model_id"]),
        "target_variable": "is_high_profit_order",
        "predicted_label": label,
        "predicted_probability": confidence,
        "top_global_features": bundle["top_global_features"][:10],
    }
