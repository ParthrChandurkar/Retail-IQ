"""Phase 6 target semantics, split governance, evaluation, and API contracts."""

import numpy as np
import pandas as pd
from fastapi.testclient import TestClient

from app.main import create_app
from app.ml.evaluate import (
    NEGATIVE_LABEL,
    POSITIVE_LABEL,
    EvaluationResult,
    labeled_confusion_matrix,
)
from app.ml.features import AUDIT_COLUMNS, FEATURE_COLUMNS, TARGET_COLUMN
from app.ml.preprocessing import group_stratified_split
from app.ml.select_model import select_best_model
from app.services.classification_service import label_and_confidence


def test_feature_contract_excludes_review_outcome_and_identifiers() -> None:
    forbidden = {
        "review_score",
        TARGET_COLUMN,
        *AUDIT_COLUMNS,
        "comment_title",
        "comment_message",
        "review_creation_ts",
        "review_answer_ts",
        "rfm_segment",
        "clv_historical",
    }
    assert forbidden.isdisjoint(FEATURE_COLUMNS)


def test_group_stratified_split_has_no_order_overlap() -> None:
    rows = 100
    inputs = pd.DataFrame({name: range(rows) for name in FEATURE_COLUMNS})
    labels = pd.Series(([0] * 4 + [1]) * 20)
    groups = pd.Series([f"order-{index // 2}" for index in range(rows)])
    split = group_stratified_split(inputs, labels, groups)
    assert not (set(split.groups_train) & set(split.groups_test))
    assert len(split.x_test) / rows == 0.2


def test_confusion_matrix_is_explicitly_labeled() -> None:
    matrix = labeled_confusion_matrix(pd.Series([1, 1, 0, 0]), np.array([1, 0, 1, 0]))
    assert matrix["column_headers"] == [POSITIVE_LABEL, NEGATIVE_LABEL]
    assert matrix["rows"][0] == {
        "actual_label": POSITIVE_LABEL,
        POSITIVE_LABEL: 1,
        NEGATIVE_LABEL: 1,
    }


def test_selection_uses_training_cv_f1_not_test_f1() -> None:
    matrix = {"rows": [], "column_headers": [POSITIVE_LABEL, NEGATIVE_LABEL]}
    higher_test = EvaluationResult(
        0.9, 0.9, 0.9, 0.9, 0.9, [0.40] * 5, [0.80] * 5, matrix
    )
    higher_cv = EvaluationResult(
        0.8, 0.8, 0.8, 0.8, 0.8, [0.41] * 5, [0.70] * 5, matrix
    )
    assert select_best_model({"test": higher_test, "cv": higher_cv}) == "cv"


def test_openapi_binds_literal_labels_and_global_explanation() -> None:
    client = TestClient(create_app(enable_database_bootstrap=False))
    schema = client.get("/api/v1/openapi.json").json()
    result = schema["components"]["schemas"]["PredictionResult"]
    properties = result["properties"]
    assert set(properties["predicted_label"]["enum"]) == {
        POSITIVE_LABEL,
        NEGATIVE_LABEL,
    }
    assert "top_global_features" in properties
    assert "local_shap_contributions" not in properties
    metrics = schema["components"]["schemas"]["ModelMetrics"]["properties"]
    assert metrics["positive_class"]["const"] == POSITIVE_LABEL
    assert metrics["negative_class"]["const"] == NEGATIVE_LABEL
    request_properties = schema["components"]["schemas"]["PredictionRequest"][
        "properties"
    ]
    assert set(request_properties) - {"entity_id"} == set(FEATURE_COLUMNS)
    assert "/api/v1/reviews/nlp-summary" in schema["paths"]


def test_probability_is_confidence_in_returned_label() -> None:
    assert label_and_confidence(1, 0.72) == (POSITIVE_LABEL, 0.72)
    assert label_and_confidence(0, 0.25) == (NEGATIVE_LABEL, 0.75)
