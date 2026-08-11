"""Global feature importance extraction for the registered model."""

from typing import Any

import numpy as np
import pandas as pd
from sklearn.inspection import permutation_importance
from sklearn.metrics import f1_score, make_scorer
from sklearn.pipeline import Pipeline


def global_feature_importance(
    pipeline: Pipeline, x_test: pd.DataFrame, y_test: pd.Series
) -> list[dict[str, Any]]:
    preprocessor = pipeline.named_steps["preprocessor"]
    classifier = pipeline.named_steps["classifier"]
    names = [
        str(name).replace("numeric__", "").replace("categorical__", "")
        for name in preprocessor.get_feature_names_out()
    ]
    if hasattr(classifier, "feature_importances_"):
        values = np.asarray(classifier.feature_importances_, dtype=float)
        names = [
            str(name).replace("numeric__", "").replace("categorical__", "")
            for name in preprocessor.get_feature_names_out()
        ]
    elif hasattr(classifier, "coef_"):
        sample = x_test.sample(n=min(2000, len(x_test)), random_state=42)
        sample_labels = y_test.loc[sample.index]
        scorer = make_scorer(f1_score, pos_label=1, zero_division=0)
        result = permutation_importance(
            pipeline,
            sample,
            sample_labels,
            scoring=scorer,
            n_repeats=3,
            random_state=42,
            n_jobs=1,
        )
        names = [str(name) for name in sample.columns]
        values = np.maximum(np.asarray(result.importances_mean, dtype=float), 0)
    else:
        raise RuntimeError("Selected estimator does not expose global importance")
    total = float(values.sum())
    normalized = values / total if total else values
    rows = [
        {"feature": feature, "importance": float(importance)}
        for feature, importance in zip(names, normalized, strict=True)
    ]
    return sorted(rows, key=lambda row: row["importance"], reverse=True)


def business_interpretation(feature: str) -> str:
    root = feature.split("_")[0]
    mappings = {
        "delivery": "Delivery experience is a major observable driver of review risk.",
        "is": "Whether an order missed its promise materially changes satisfaction risk.",
        "freight": "Shipping cost relative to merchandise value influences customer expectations.",
        "total": "The order's monetary composition helps distinguish satisfaction risk.",
        "seller": "Seller geography and fulfillment characteristics contribute to review outcomes.",
        "dominant": "Product-category mix captures different fulfillment and expectation patterns.",
        "customer": "Customer geography captures regional service-level differences.",
        "primary": "Payment behavior provides context for the completed order experience.",
    }
    return mappings.get(
        root,
        "This operational input contributes materially to the model's global decisions.",
    )
