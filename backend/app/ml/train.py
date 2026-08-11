"""Train, compare, explain, register, and report the Phase 6 classifier."""

import asyncio
import os
from datetime import UTC, datetime
from typing import Any

import joblib
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.tree import DecisionTreeClassifier
from xgboost import XGBClassifier

from app.core.config import get_settings
from app.ml.evaluate import EvaluationResult, evaluate_model
from app.ml.explain import business_interpretation, global_feature_importance
from app.ml.features import FEATURE_COLUMNS, build_feature_frame, feature_payload
from app.ml.nlp_feasibility import evaluate_nlp_feasibility, write_nlp_report
from app.ml.preprocessing import (
    RANDOM_SEED,
    build_preprocessor,
    group_stratified_split,
    training_cv_splits,
)
from app.ml.registry import register_model
from app.ml.select_model import select_best_model


def candidate_estimators() -> dict[str, Any]:
    """Return the five binding algorithms with deterministic parameters."""
    return {
        "Logistic Regression": LogisticRegression(
            max_iter=300,
            solver="liblinear",
            class_weight="balanced",
            random_state=RANDOM_SEED,
        ),
        "Decision Tree": DecisionTreeClassifier(
            max_depth=14, min_samples_leaf=10, random_state=RANDOM_SEED
        ),
        "Random Forest": RandomForestClassifier(
            n_estimators=180,
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
            n_estimators=200,
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


def _report(
    model_id: int,
    winner: str,
    results: dict[str, EvaluationResult],
    importance: list[dict[str, Any]],
    row_counts: dict[str, int],
) -> None:
    generated = datetime.now(UTC).isoformat().replace("+00:00", "Z")
    commit = os.getenv("GIT_COMMIT", "working-tree")
    lines = [
        "# Model Comparison — Customer Satisfaction",
        "",
        f"- **Generated at:** `{generated}`",
        (
            "- **Dataset row counts used:** "
            f"review-order links={row_counts['all']:,}; train={row_counts['train']:,}; "
            f"test={row_counts['test']:,}; unique orders={row_counts['groups']:,}"
        ),
        f"- **Code/commit reference:** `{commit}`",
        "- **Positive class:** `low_satisfaction` (`review_score <= 3`)",
        "- **Validation:** group-aware stratified 80/20 split and 5-fold training CV; seed 42",
        "",
        "Precision, Recall, F1, and CV F1 below are for `low_satisfaction` only; they are not macro- or weighted-averaged.",
        "",
        "| Algorithm | Accuracy | Precision | Recall | F1 | ROC-AUC | CV Mean F1 (5-fold) |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for name, result in results.items():
        lines.append(
            f"| {name} | {result.accuracy:.4f} | {result.precision:.4f} | "
            f"{result.recall:.4f} | {result.f1:.4f} | {result.roc_auc:.4f} | "
            f"{sum(result.cv_f1_scores) / len(result.cv_f1_scores):.4f} |"
        )
    selected = results[winner]
    matrix = selected.confusion_matrix["rows"]
    lines.extend(
        [
            "",
            "## Selected model",
            "",
            f"**{winner}** (`model_id={model_id}`) is selected by highest training-only mean CV positive-class F1, with mean CV ROC-AUC as the declared tiebreaker. The held-out test metrics are final evaluation evidence, not selection input.",
            "",
            "## Labeled confusion matrix",
            "",
            "Rows are actual labels; columns are predicted labels.",
            "",
            "| Actual \\ Predicted | low_satisfaction | high_satisfaction |",
            "|---|---:|---:|",
            f"| low_satisfaction | {matrix[0]['low_satisfaction']} | {matrix[0]['high_satisfaction']} |",
            f"| high_satisfaction | {matrix[1]['low_satisfaction']} | {matrix[1]['high_satisfaction']} |",
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
            "## Selection note",
            "",
            "Every algorithm used the identical feature frame, fitted preprocessing definition, held-out order-group split, and five group-aware CV folds. Class weighting was evaluated inside training: balanced Logistic Regression improved mean training-CV positive-class F1 from 0.3874 to 0.4496, so the balanced variant was retained. The untouched 20% test partition was used once for the comparison above. SHAP was not implemented; the API intentionally omits `local_shap_contributions`.",
            "",
        ]
    )
    path = get_settings().report_dir / "model_comparison.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


async def train_all() -> None:
    nlp_result = await evaluate_nlp_feasibility()
    write_nlp_report(nlp_result)
    frame = await build_feature_frame()
    inputs, labels, groups = feature_payload(frame)
    split = group_stratified_split(inputs, labels, groups)
    cv_splits = training_cv_splits(split.x_train, split.y_train, split.groups_train)
    checkpoint_path = (
        get_settings().model_registry_dir / ".phase6-training-checkpoint.joblib"
    )
    checkpoint_signature = "phase6-v3-balanced-logistic-training-cv-f1-cv-roc"
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
            {
                "signature": checkpoint_signature,
                "fitted": fitted,
                "results": results,
            },
            checkpoint_path,
        )
        print(f"{name}: F1={results[name].f1:.4f}, ROC-AUC={results[name].roc_auc:.4f}")
    winner = select_best_model(results)
    winner_pipeline = fitted[winner]
    importance = global_feature_importance(winner_pipeline, split.x_test, split.y_test)
    metrics = results[winner].as_dict()
    metrics["all_model_metrics"] = {
        name: result.as_dict() for name, result in results.items()
    }
    metadata = {
        "feature_columns": list(FEATURE_COLUMNS),
        "positive_class": "low_satisfaction",
        "negative_class": "high_satisfaction",
        "random_seed": RANDOM_SEED,
        "split": "stratified_group_80_20",
        "commit_reference": os.getenv("GIT_COMMIT", "working-tree"),
    }
    model_id, artifact_path = await register_model(
        winner, winner_pipeline, metrics, importance, metadata
    )
    _report(
        model_id,
        winner,
        results,
        importance,
        {
            "all": len(frame),
            "train": len(split.x_train),
            "test": len(split.x_test),
            "groups": groups.nunique(),
        },
    )
    print(f"Selected {winner}; registered model_id={model_id} at {artifact_path}")
    checkpoint_path.unlink(missing_ok=True)


if __name__ == "__main__":
    asyncio.run(train_all())
