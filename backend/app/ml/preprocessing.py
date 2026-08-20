"""Shared preprocessing and the binding M6 order-grain split."""

from dataclasses import dataclass

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from app.ml.features import CATEGORICAL_FEATURES, NUMERIC_FEATURES

RANDOM_SEED = 42
TEST_SIZE = 0.20


@dataclass(frozen=True)
class DataSplit:
    x_train: pd.DataFrame
    x_test: pd.DataFrame
    y_train: pd.Series
    y_test: pd.Series
    order_ids_train: pd.Series
    order_ids_test: pd.Series


def build_preprocessor() -> ColumnTransformer:
    numeric = Pipeline(
        [("imputer", SimpleImputer(strategy="median")), ("scaler", StandardScaler())]
    )
    categorical = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="most_frequent")),
            (
                "encoder",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
            ),
        ]
    )
    return ColumnTransformer(
        [
            ("numeric", numeric, list(NUMERIC_FEATURES)),
            ("categorical", categorical, list(CATEGORICAL_FEATURES)),
        ],
        sparse_threshold=0,
    )


def stratified_order_split(
    inputs: pd.DataFrame, labels: pd.Series, order_ids: pd.Series
) -> DataSplit:
    """Apply the binding 80/20 stratified random split at order grain."""
    train_index, test_index = train_test_split(
        range(len(inputs)),
        test_size=TEST_SIZE,
        random_state=RANDOM_SEED,
        stratify=labels,
    )
    split = DataSplit(
        x_train=inputs.iloc[train_index].reset_index(drop=True),
        x_test=inputs.iloc[test_index].reset_index(drop=True),
        y_train=labels.iloc[train_index].reset_index(drop=True),
        y_test=labels.iloc[test_index].reset_index(drop=True),
        order_ids_train=order_ids.iloc[train_index].reset_index(drop=True),
        order_ids_test=order_ids.iloc[test_index].reset_index(drop=True),
    )
    overlap = set(split.order_ids_train) & set(split.order_ids_test)
    if overlap:
        raise RuntimeError(f"Order leakage detected for {len(overlap)} orders")
    return split


def training_cv_splits(
    inputs: pd.DataFrame, labels: pd.Series
) -> list[tuple[object, object]]:
    """Return the same deterministic five stratified folds for every model."""
    splitter = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_SEED)
    return list(splitter.split(inputs, labels))
