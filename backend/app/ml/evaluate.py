"""Binding positive-class evaluation for migrated high-profit models."""

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    make_scorer,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import cross_validate
from sklearn.pipeline import Pipeline

POSITIVE_LABEL = "high_profit_order"
NEGATIVE_LABEL = "standard_profit_order"


@dataclass(frozen=True)
class EvaluationResult:
    accuracy: float
    precision: float
    recall: float
    f1: float
    roc_auc: float
    cv_f1_scores: list[float]
    cv_roc_auc_scores: list[float]
    confusion_matrix: dict[str, Any]

    def as_dict(self) -> dict[str, Any]:
        return {
            "accuracy": self.accuracy,
            "precision_high_profit_order": self.precision,
            "recall_high_profit_order": self.recall,
            "f1_high_profit_order": self.f1,
            "roc_auc": self.roc_auc,
            "cv_f1_scores": self.cv_f1_scores,
            "cv_mean_f1_high_profit_order": float(np.mean(self.cv_f1_scores)),
            "cv_roc_auc_scores": self.cv_roc_auc_scores,
            "cv_mean_roc_auc": float(np.mean(self.cv_roc_auc_scores)),
            "confusion_matrix": self.confusion_matrix,
        }


def positive_probability(pipeline: Pipeline, inputs: pd.DataFrame) -> np.ndarray:
    probabilities = pipeline.predict_proba(inputs)
    classes = list(pipeline.classes_)
    return np.asarray(probabilities[:, classes.index(1)], dtype=float)


def labeled_confusion_matrix(
    labels: pd.Series, predictions: np.ndarray
) -> dict[str, Any]:
    matrix = confusion_matrix(labels, predictions, labels=[1, 0])
    return {
        "row_header": "actual_label",
        "column_headers": [POSITIVE_LABEL, NEGATIVE_LABEL],
        "rows": [
            {
                "actual_label": POSITIVE_LABEL,
                POSITIVE_LABEL: int(matrix[0, 0]),
                NEGATIVE_LABEL: int(matrix[0, 1]),
            },
            {
                "actual_label": NEGATIVE_LABEL,
                POSITIVE_LABEL: int(matrix[1, 0]),
                NEGATIVE_LABEL: int(matrix[1, 1]),
            },
        ],
    }


def evaluate_model(
    pipeline: Pipeline,
    x_train: pd.DataFrame,
    y_train: pd.Series,
    x_test: pd.DataFrame,
    y_test: pd.Series,
    cv_splits: list[tuple[Any, Any]],
) -> EvaluationResult:
    predictions = np.asarray(pipeline.predict(x_test), dtype=int)
    probabilities = positive_probability(pipeline, x_test)
    scorer = make_scorer(f1_score, pos_label=1, zero_division=0)
    cv_scores = cross_validate(
        clone(pipeline),
        x_train,
        y_train,
        cv=cv_splits,
        scoring={"f1_high_profit_order": scorer, "roc_auc": "roc_auc"},
        n_jobs=1,
    )
    return EvaluationResult(
        accuracy=float(accuracy_score(y_test, predictions)),
        precision=float(
            precision_score(y_test, predictions, pos_label=1, zero_division=0)
        ),
        recall=float(recall_score(y_test, predictions, pos_label=1, zero_division=0)),
        f1=float(f1_score(y_test, predictions, pos_label=1, zero_division=0)),
        roc_auc=float(roc_auc_score(y_test, probabilities)),
        cv_f1_scores=[float(score) for score in cv_scores["test_f1_high_profit_order"]],
        cv_roc_auc_scores=[float(score) for score in cv_scores["test_roc_auc"]],
        confusion_matrix=labeled_confusion_matrix(y_test, predictions),
    )
