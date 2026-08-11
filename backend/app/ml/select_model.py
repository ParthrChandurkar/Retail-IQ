"""Deterministic winner selection required by SRS 13.1."""

from app.ml.evaluate import EvaluationResult


def select_best_model(results: dict[str, EvaluationResult]) -> str:
    """Select within training by mean CV F1, breaking ties with mean CV ROC-AUC."""
    if not results:
        raise ValueError("At least one evaluated model is required")
    return max(
        results,
        key=lambda name: (
            sum(results[name].cv_f1_scores) / len(results[name].cv_f1_scores),
            sum(results[name].cv_roc_auc_scores) / len(results[name].cv_roc_auc_scores),
        ),
    )
