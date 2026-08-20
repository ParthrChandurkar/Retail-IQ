"""Train, compare, explain, register, and report the migrated M6 classifier."""

import asyncio
import os
from datetime import UTC, datetime
from typing import Any

import joblib
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.tree import DecisionTreeClassifier
from xgboost import XGBClassifier

from app.core.config import get_settings
from app.ml.evaluate import (
    NEGATIVE_LABEL,
    POSITIVE_LABEL,
    EvaluationResult,
    evaluate_model,
    positive_probability,
)
from app.ml.explain import business_interpretation, global_feature_importance
from app.ml.features import FEATURE_COLUMNS, build_feature_frame, feature_payload
from app.ml.preprocessing import (
    RANDOM_SEED,
    TEST_SIZE,
    build_preprocessor,
    stratified_order_split,
    training_cv_splits,
)
from app.ml.registry import register_model
from app.ml.select_model import select_best_model


def candidate_estimators() -> dict[str, Any]:
    """Return all five binding algorithms with deterministic parameters."""
    return {
        "Logistic Regression": LogisticRegression(
            max_iter=500,
            solver="liblinear",
            random_state=RANDOM_SEED,
        ),
        "Decision Tree": DecisionTreeClassifier(
            max_depth=14,
            min_samples_leaf=10,
            random_state=RANDOM_SEED,
        ),
        "Random Forest": RandomForestClassifier(
            n_estimators=160,
            max_depth=20,
            min_samples_leaf=5,
            n_jobs=-1,
            random_state=RANDOM_SEED,
        ),
        "Gradient Boosting": GradientBoostingClassifier(
            n_estimators=140,
            learning_rate=0.05,
            max_depth=3,
            random_state=RANDOM_SEED,
        ),
        "XGBoost": XGBClassifier(
            n_estimators=180,
            learning_rate=0.05,
            max_depth=6,
            min_child_weight=5,
            subsample=0.85,
            colsample_bytree=0.85,
            eval_metric="logloss",
            n_jobs=-1,
            random_state=RANDOM_SEED,
        ),
    }


def build_pipeline(estimator: Any) -> Pipeline:
    return Pipeline([("preprocessor", build_preprocessor()), ("classifier", estimator)])


def prediction_examples(pipeline: Pipeline, test_inputs: Any) -> list[dict[str, Any]]:
    """Return one real held-out example for each predicted label."""
    predictions = np.asarray(pipeline.predict(test_inputs), dtype=int)
    probabilities = positive_probability(pipeline, test_inputs)
    examples: list[dict[str, Any]] = []
    for requested_prediction in (1, 0):
        matching = np.flatnonzero(predictions == requested_prediction)
        if not matching.size:
            raise RuntimeError(
                f"Selected model produced no held-out example for class {requested_prediction}"
            )
        index = int(matching[0])
        payload = test_inputs.iloc[index].to_dict()
        payload = {
            key: value.item() if isinstance(value, np.generic) else value
            for key, value in payload.items()
        }
        positive_probability_value = float(probabilities[index])
        label = POSITIVE_LABEL if requested_prediction == 1 else NEGATIVE_LABEL
        confidence = (
            positive_probability_value
            if requested_prediction == 1
            else 1.0 - positive_probability_value
        )
        examples.append(
            {
                "request": payload,
                "response": {
                    "predicted_label": label,
                    "predicted_probability": confidence,
                },
            }
        )
    return examples


def _report(
    model_id: int,
    winner: str,
    results: dict[str, EvaluationResult],
    importance: list[dict[str, Any]],
    examples: list[dict[str, Any]],
    row_counts: dict[str, int],
    retired_count: int,
) -> None:
    generated = datetime.now(UTC).isoformat().replace("+00:00", "Z")
    commit = os.getenv("GIT_COMMIT", "working-tree")
    accuracy_winner = max(results, key=lambda name: results[name].accuracy)
    lines = [
        "# Migration M6 Model Comparison — High-Profit Order",
        "",
        f"- **Generated at:** `{generated}`",
        (
            "- **Dataset row counts used:** "
            f"orders={row_counts['all']:,}; train={row_counts['train']:,}; "
            f"test={row_counts['test']:,}"
        ),
        f"- **Code/commit reference:** `{commit}`",
        f"- **Features:** `{', '.join(FEATURE_COLUMNS)}`",
        f"- **Positive class:** `{POSITIVE_LABEL}` (`profit >= INR 5,363.845`)",
        f"- **Negative class:** `{NEGATIVE_LABEL}`",
        "- **Validation:** order-grain stratified 80/20 split and five-fold stratified training CV; seed 42",
        "",
        f"Precision, Recall, F1, and CV F1 are for `{POSITIVE_LABEL}` only; they are not macro- or weighted-averaged.",
        "",
        "| Algorithm | Accuracy | Precision | Recall | F1 | ROC-AUC | CV Mean F1 | CV Mean ROC-AUC |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for name, result in results.items():
        lines.append(
            f"| {name} | {result.accuracy:.6f} | {result.precision:.6f} | "
            f"{result.recall:.6f} | {result.f1:.6f} | {result.roc_auc:.6f} | "
            f"{np.mean(result.cv_f1_scores):.6f} | {np.mean(result.cv_roc_auc_scores):.6f} |"
        )
    selected = results[winner]
    matrix = selected.confusion_matrix["rows"]
    lines.extend(
        [
            "",
            "## Selected model",
            "",
            f"**{winner}** (`model_id={model_id}`) was selected by highest training-CV positive-class F1; mean CV ROC-AUC was the declared tiebreaker. The held-out test partition was not used for selection.",
            "",
            f"The highest held-out accuracy belongs to **{accuracy_winner}**. "
            + (
                "Accuracy and positive-class F1 select the same algorithm in this migration."
                if accuracy_winner == winner
                else f"Accuracy alone would therefore have selected a different—and under the binding decision rule, wrong—model than {winner}."
            ),
            "",
            "## Labeled confusion matrix",
            "",
            "Rows are actual labels; columns are predicted labels.",
            "",
            f"| Actual \\ Predicted | {POSITIVE_LABEL} | {NEGATIVE_LABEL} |",
            "|---|---:|---:|",
            f"| {POSITIVE_LABEL} | {matrix[0][POSITIVE_LABEL]} | {matrix[0][NEGATIVE_LABEL]} |",
            f"| {NEGATIVE_LABEL} | {matrix[1][POSITIVE_LABEL]} | {matrix[1][NEGATIVE_LABEL]} |",
            "",
            "## Top-10 global feature importances",
            "",
            "| Rank | Feature | Importance | Business interpretation |",
            "|---:|---|---:|---|",
        ]
    )
    for index, row in enumerate(importance[:10], start=1):
        interpretation = (
            business_interpretation(str(row["feature"])) if index <= 3 else "—"
        )
        lines.append(
            f"| {index} | `{row['feature']}` | {row['importance']:.6f} | {interpretation} |"
        )
    lines.extend(
        [
            "",
            "SHAP was not implemented. No local SHAP contribution field or fabricated explanation is emitted.",
            "",
            "## Prediction contract examples",
            "",
            "These examples were generated from real held-out rows through the selected registered pipeline. They are model-contract examples for M7; no API router was changed in M6.",
            "",
        ]
    )
    for index, example in enumerate(examples, start=1):
        lines.extend(
            [
                f"### Example {index}: `{example['response']['predicted_label']}`",
                "",
                "Request:",
                "",
                "```json",
                _json_for_report(example["request"]),
                "```",
                "",
                "Response:",
                "",
                "```json",
                _json_for_report(example["response"]),
                "```",
                "",
            ]
        )
    lines.extend(
        [
            "`predicted_probability` is confidence in the returned label: P(high-profit) for `high_profit_order`, and `1 - P(high-profit)` for `standard_profit_order`.",
            "",
            "## Retirement and phase boundary",
            "",
            f"Registration removed **{retired_count}** Olist-era `low_satisfaction` registry rows, their prediction/importance rows, and their joblib artifacts. Exactly one migrated active model remains. No NLP work was performed (N/A), and no API router or frontend file was changed.",
            "",
        ]
    )
    path = get_settings().report_dir / "model_comparison_v2.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _json_for_report(value: dict[str, Any]) -> str:
    import json

    return json.dumps(value, indent=2, sort_keys=True)


async def train_all() -> None:
    frame = await build_feature_frame()
    inputs, labels, order_ids = feature_payload(frame)
    split = stratified_order_split(inputs, labels, order_ids)
    cv_splits = training_cv_splits(split.x_train, split.y_train)
    checkpoint_path = (
        get_settings().model_registry_dir / ".m6-training-checkpoint.joblib"
    )
    checkpoint_signature = "migration-m6-high-profit-v1"
    fitted: dict[str, Pipeline] = {}
    results: dict[str, EvaluationResult] = {}
    if checkpoint_path.exists():
        checkpoint = joblib.load(checkpoint_path)
        if checkpoint.get("signature") == checkpoint_signature:
            fitted = checkpoint["fitted"]
            results = checkpoint["results"]
            print(f"Resuming {len(results)} completed candidate(s) from checkpoint")
    for name, estimator in candidate_estimators().items():
        if name in results:
            continue
        print(f"Training {name}...")
        pipeline = build_pipeline(estimator)
        pipeline.fit(split.x_train, split.y_train)
        results[name] = evaluate_model(
            pipeline,
            split.x_train,
            split.y_train,
            split.x_test,
            split.y_test,
            cv_splits,
        )
        fitted[name] = pipeline
        checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(
            {"signature": checkpoint_signature, "fitted": fitted, "results": results},
            checkpoint_path,
        )
        print(f"{name}: F1={results[name].f1:.6f}, ROC-AUC={results[name].roc_auc:.6f}")
    winner = select_best_model(results)
    winner_pipeline = fitted[winner]
    importance = global_feature_importance(winner_pipeline, split.x_test, split.y_test)
    examples = prediction_examples(winner_pipeline, split.x_test)
    metrics = results[winner].as_dict()
    metrics["all_model_metrics"] = {
        name: result.as_dict() for name, result in results.items()
    }
    metadata = {
        "feature_columns": list(FEATURE_COLUMNS),
        "positive_class": POSITIVE_LABEL,
        "negative_class": NEGATIVE_LABEL,
        "positive_threshold_inr": 5363.845,
        "random_seed": RANDOM_SEED,
        "test_size": TEST_SIZE,
        "split": "stratified_order_80_20",
        "probability_semantics": "confidence_in_predicted_label",
        "prediction_examples": examples,
        "shap_implemented": False,
        "commit_reference": os.getenv("GIT_COMMIT", "working-tree"),
    }
    model_id, artifact_path, retired_count = await register_model(
        winner, winner_pipeline, metrics, importance, metadata
    )
    _report(
        model_id,
        winner,
        results,
        importance,
        examples,
        {"all": len(frame), "train": len(split.x_train), "test": len(split.x_test)},
        retired_count,
    )
    print(f"Selected {winner}; registered model_id={model_id} at {artifact_path}")
    print(f"Retired {retired_count} Olist-era model registration(s)")
    checkpoint_path.unlink(missing_ok=True)


if __name__ == "__main__":
    asyncio.run(train_all())
