"""Transactional model registration and artifact persistence."""

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import joblib
from sklearn.pipeline import Pipeline

from app.core.config import get_settings
from app.etl.database import connect


async def register_model(
    algorithm: str,
    pipeline: Pipeline,
    metrics: dict[str, Any],
    feature_importance: list[dict[str, Any]],
    metadata: dict[str, Any],
) -> tuple[int, Path]:
    registry_dir = get_settings().model_registry_dir
    registry_dir.mkdir(parents=True, exist_ok=True)
    connection = await connect()
    try:
        async with connection.transaction():
            await connection.execute(
                "UPDATE ml.model_registry SET is_active=false WHERE target_variable=$1",
                "low_satisfaction",
            )
            model_id = await connection.fetchval(
                """INSERT INTO ml.model_registry
                     (target_variable,algorithm,trained_at,is_active,artifact_path,metrics_json)
                   VALUES($1,$2,$3,true,'pending',$4::jsonb) RETURNING model_id""",
                "low_satisfaction",
                algorithm,
                datetime.now(UTC).replace(tzinfo=None),
                json.dumps(metrics),
            )
            artifact_path = registry_dir / f"{model_id}.joblib"
            bundle = {
                "model_id": model_id,
                "target_variable": "low_satisfaction",
                "algorithm": algorithm,
                "pipeline": pipeline,
                "metrics": metrics,
                "top_global_features": feature_importance,
                "metadata": metadata,
            }
            joblib.dump(bundle, artifact_path)
            await connection.execute(
                "UPDATE ml.model_registry SET artifact_path=$1 WHERE model_id=$2",
                artifact_path.as_posix(),
                model_id,
            )
            await connection.executemany(
                """INSERT INTO ml.feature_importance(model_id,feature_name,importance)
                   VALUES($1,$2,$3)""",
                [
                    (model_id, row["feature"], row["importance"])
                    for row in feature_importance
                ],
            )
    finally:
        await connection.close()
    return int(model_id), artifact_path
