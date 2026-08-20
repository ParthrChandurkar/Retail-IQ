"""Migration M6 feature, split, metric, and selection governance tests."""

import numpy as np
import pandas as pd

from app.ml.evaluate import (
    NEGATIVE_LABEL,
    POSITIVE_LABEL,
    EvaluationResult,
    labeled_confusion_matrix,
)
from app.ml.features import AUDIT_COLUMNS, FEATURE_COLUMNS, TARGET_COLUMN
from app.ml.preprocessing import RANDOM_SEED, TEST_SIZE, stratified_order_split
from app.ml.select_model import select_best_model


def test_m6_feature_contract_is_exact_and_leakage_safe() -> None:
    assert FEATURE_COLUMNS == (
        "sales",
        "discount_pct",
        "order_month",
        "order_dow",
        "category",
        "sub_category",
        "segment",
        "city_type",
        "state",
        "region",
    )
    forbidden = {
        TARGET_COLUMN,
        *AUDIT_COLUMNS,
        "profit",
        "profit_margin_pct",
        "is_profit_outlier",
        "ship_date",
        "shipping_days",
        "quantity",
        "order_year",
        "region_as_reported",
    }
    assert forbidden.isdisjoint(FEATURE_COLUMNS)


def test_stratified_order_split_is_80_20_seeded_and_leakage_free() -> None:
    rows = 1000
    inputs = pd.DataFrame({name: range(rows) for name in FEATURE_COLUMNS})
    labels = pd.Series(([0] * 3 + [1]) * 250)
    order_ids = pd.Series([f"order-{index}" for index in range(rows)])
    first = stratified_order_split(inputs, labels, order_ids)
    second = stratified_order_split(inputs, labels, order_ids)
    assert RANDOM_SEED == 42
    assert TEST_SIZE == 0.20
    assert len(first.x_test) == 200
    assert first.y_test.mean() == labels.mean()
    assert first.order_ids_test.equals(second.order_ids_test)
    assert not (set(first.order_ids_train) & set(first.order_ids_test))


def test_confusion_matrix_uses_migrated_literal_labels() -> None:
    matrix = labeled_confusion_matrix(pd.Series([1, 1, 0, 0]), np.array([1, 0, 1, 0]))
    assert POSITIVE_LABEL == "high_profit_order"
    assert NEGATIVE_LABEL == "standard_profit_order"
    assert matrix["column_headers"] == [POSITIVE_LABEL, NEGATIVE_LABEL]
    assert matrix["rows"][0] == {
        "actual_label": POSITIVE_LABEL,
        POSITIVE_LABEL: 1,
        NEGATIVE_LABEL: 1,
    }


def test_selection_uses_training_cv_positive_f1_then_roc_auc() -> None:
    matrix = {"rows": [], "column_headers": [POSITIVE_LABEL, NEGATIVE_LABEL]}
    higher_test = EvaluationResult(
        0.99, 0.99, 0.99, 0.99, 0.99, [0.40] * 5, [0.90] * 5, matrix
    )
    higher_cv = EvaluationResult(
        0.80, 0.80, 0.80, 0.80, 0.80, [0.41] * 5, [0.70] * 5, matrix
    )
    assert select_best_model({"test": higher_test, "cv": higher_cv}) == "cv"

    tied_f1_lower_auc = EvaluationResult(
        0.80, 0.80, 0.80, 0.80, 0.80, [0.41] * 5, [0.69] * 5, matrix
    )
    assert (
        select_best_model({"winner": higher_cv, "loser": tied_f1_lower_auc}) == "winner"
    )


def test_probability_contract_is_confidence_in_returned_label() -> None:
    probability_high_profit = 0.72
    positive_response = (POSITIVE_LABEL, probability_high_profit)
    negative_response = (NEGATIVE_LABEL, 1.0 - 0.25)
    assert positive_response == ("high_profit_order", 0.72)
    assert negative_response == ("standard_profit_order", 0.75)
