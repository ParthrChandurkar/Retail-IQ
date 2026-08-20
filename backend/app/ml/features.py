"""Leakage-safe order features for migrated high-profit classification."""

from typing import Any

import pandas as pd

from app.services.dataframes import query_frame

TARGET_COLUMN = "is_high_profit_order"
GROUP_COLUMN = "order_id"
AUDIT_COLUMNS = (GROUP_COLUMN,)

NUMERIC_FEATURES = (
    "sales",
    "discount_pct",
    "order_month",
    "order_dow",
)

CATEGORICAL_FEATURES = (
    "category",
    "sub_category",
    "segment",
    "city_type",
    "state",
    "region",
)

FEATURE_COLUMNS = (*NUMERIC_FEATURES, *CATEGORICAL_FEATURES)

FEATURE_SQL = """
SELECT
    o.order_id,
    o.is_high_profit_order::integer AS is_high_profit_order,
    o.sales::double precision AS sales,
    o.discount_pct::double precision AS discount_pct,
    o.order_month::integer AS order_month,
    o.order_dow::integer AS order_dow,
    p.category,
    p.sub_category,
    c.segment,
    c.city_type,
    c.state,
    rr.region
FROM curated.orders o
JOIN curated.customers c ON c.customer_id = o.customer_id
JOIN curated.products p ON p.product_id = o.product_id
JOIN curated.state_region_reference rr ON rr.state = c.state
ORDER BY o.order_id
"""


async def build_feature_frame() -> pd.DataFrame:
    """Return one governed feature row per migrated order."""
    frame = await query_frame(FEATURE_SQL)
    required = set((*AUDIT_COLUMNS, TARGET_COLUMN, *FEATURE_COLUMNS))
    missing = required - set(frame.columns)
    if missing:
        raise RuntimeError(f"Feature query omitted required columns: {sorted(missing)}")
    if frame[GROUP_COLUMN].duplicated().any():
        raise RuntimeError("M6 requires exactly one feature row per order")
    if frame[list(FEATURE_COLUMNS)].isna().any(axis=None):
        raise RuntimeError("M6 feature frame contains unexpected null values")
    return frame


def feature_payload(frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series, pd.Series]:
    """Separate predictive inputs, positive-class labels, and audit keys."""
    inputs = frame.loc[:, FEATURE_COLUMNS].copy()
    labels = frame[TARGET_COLUMN].astype(int)
    order_ids = frame[GROUP_COLUMN].astype(str)
    return inputs, labels, order_ids


def request_frame(payload: dict[str, Any]) -> pd.DataFrame:
    """Build one inference row in the exact training feature order."""
    row = {name: payload.get(name) for name in FEATURE_COLUMNS}
    for name in CATEGORICAL_FEATURES:
        if row[name] is not None:
            row[name] = str(row[name])
    return pd.DataFrame([row])
