"""Transactional migrated-model registration and legacy retirement."""

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import joblib
from sklearn.pipeline import Pipeline

from app.core.config import get_settings
from app.etl.database import connect

TARGET_VARIABLE = "is_high_profit_order"


def _remove_managed_artifact(path: Path, registry_dir: Path) -> None:
    """Remove only files resolved inside the configured registry directory."""
    resolved_registry = registry_dir.resolve()
    resolved_path = path.resolve()
    if resolved_path.parent != resolved_registry:
        raise RuntimeError(f"Refusing to remove unmanaged artifact: {resolved_path}")
    resolved_path.unlink(missing_ok=True)


async def register_model(
    algorithm: str,
    pipeline: Pipeline,
    metrics: dict[str, Any],
    feature_importance: list[dict[str, Any]],
    metadata: dict[str, Any],
) -> tuple[int, Path, int]:
    """Register one winner and fully retire every Olist-era registry record."""
    registry_dir = get_settings().model_registry_dir
    registry_dir.mkdir(parents=True, exist_ok=True)
    connection = await connect()
    old_artifacts: list[str] = []
    artifact_path: Path | None = None
    retired_count = 0
    try:
        async with connection.transaction():
            old_rows = await connection.fetch(
                "SELECT model_id, artifact_path FROM ml.model_registry FOR UPDATE"
            )
            retired_count = len(old_rows)
            old_artifacts = [str(row["artifact_path"]) for row in old_rows]
            await connection.execute("DELETE FROM ml.predictions")
            await connection.execute("DELETE FROM ml.feature_importance")
            await connection.execute("DELETE FROM ml.model_registry")
            model_id = await connection.fetchval(
                """INSERT INTO ml.model_registry
                     (target_variable,algorithm,trained_at,is_active,artifact_path,metrics_json)
                   VALUES($1,$2,$3,true,'pending',$4::jsonb) RETURNING model_id""",
                TARGET_VARIABLE,
                algorithm,
                datetime.now(UTC).replace(tzinfo=None),
                json.dumps(metrics),
            )
            artifact_path = registry_dir / f"{model_id}.joblib"
            bundle = {
                "model_id": model_id,
                "target_variable": TARGET_VARIABLE,
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
    except Exception:
        if artifact_path is not None:
            _remove_managed_artifact(artifact_path, registry_dir)
        raise
    finally:
        await connection.close()

    if artifact_path is None:
        raise RuntimeError("Model registration did not create an artifact")
    for stored_path in old_artifacts:
        _remove_managed_artifact(registry_dir / Path(stored_path).name, registry_dir)
    for candidate in registry_dir.glob("*.joblib"):
        if candidate.resolve() != artifact_path.resolve():
            _remove_managed_artifact(candidate, registry_dir)
    return int(model_id), artifact_path, retired_count
