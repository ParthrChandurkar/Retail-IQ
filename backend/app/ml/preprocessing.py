"""Shared preprocessing and authorized group-aware split strategy."""

from dataclasses import dataclass

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from app.ml.features import CATEGORICAL_FEATURES, NUMERIC_FEATURES

RANDOM_SEED = 42


@dataclass(frozen=True)
class DataSplit:
    x_train: pd.DataFrame
    x_test: pd.DataFrame
    y_train: pd.Series
    y_test: pd.Series
    groups_train: pd.Series
    groups_test: pd.Series


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


def group_stratified_split(
    inputs: pd.DataFrame, labels: pd.Series, groups: pd.Series
) -> DataSplit:
    """Use the Phase 4-authorized first fold of a shuffled five-fold split."""
    splitter = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=RANDOM_SEED)
    train_index, test_index = next(splitter.split(inputs, labels, groups))
    split = DataSplit(
        x_train=inputs.iloc[train_index].reset_index(drop=True),
        x_test=inputs.iloc[test_index].reset_index(drop=True),
        y_train=labels.iloc[train_index].reset_index(drop=True),
        y_test=labels.iloc[test_index].reset_index(drop=True),
        groups_train=groups.iloc[train_index].reset_index(drop=True),
        groups_test=groups.iloc[test_index].reset_index(drop=True),
    )
    overlap = set(split.groups_train) & set(split.groups_test)
    if overlap:
        raise RuntimeError(f"Order-group leakage detected for {len(overlap)} groups")
    return split


def training_cv_splits(
    inputs: pd.DataFrame, labels: pd.Series, groups: pd.Series
) -> list[tuple[object, object]]:
    splitter = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=RANDOM_SEED)
    return list(splitter.split(inputs, labels, groups))
