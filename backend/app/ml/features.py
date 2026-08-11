"""Leakage-safe feature construction for customer-satisfaction classification."""

from typing import Any

import pandas as pd

from app.services.dataframes import query_frame

TARGET_COLUMN = "low_satisfaction"
GROUP_COLUMN = "order_id"
AUDIT_COLUMNS = ("review_id", GROUP_COLUMN)

NUMERIC_FEATURES = (
    "total_price",
    "total_freight",
    "item_count",
    "product_count",
    "seller_count",
    "average_item_price",
    "maximum_item_price",
    "freight_ratio",
    "payment_value",
    "payment_installments",
    "delivery_days",
    "delivery_delay_hours",
    "is_late",
    "approval_hours",
    "carrier_handling_hours",
    "estimated_delivery_days",
    "shipping_limit_slack_days",
    "seller_distance_km",
    "average_product_weight_g",
    "average_product_volume_cm3",
)

CATEGORICAL_FEATURES = (
    "customer_state",
    "seller_state",
    "dominant_category",
    "primary_payment_type",
    "purchase_month",
    "purchase_weekday",
    "purchase_hour",
)

FEATURE_COLUMNS = (*NUMERIC_FEATURES, *CATEGORICAL_FEATURES)

FEATURE_SQL = """
WITH item_features AS (
    SELECT
        oi.order_id,
        SUM(oi.price)::double precision AS total_price,
        SUM(oi.freight_value)::double precision AS total_freight,
        COUNT(*)::integer AS item_count,
        COUNT(DISTINCT oi.product_id)::integer AS product_count,
        COUNT(DISTINCT oi.seller_id)::integer AS seller_count,
        AVG(oi.price)::double precision AS average_item_price,
        MAX(oi.price)::double precision AS maximum_item_price,
        SUM(oi.freight_value)::double precision / NULLIF(SUM(oi.price), 0)
            AS freight_ratio,
        mode() WITHIN GROUP (ORDER BY COALESCE(
            p.category_name_english, p.category_name, 'unknown'
        )) AS dominant_category,
        mode() WITHIN GROUP (ORDER BY COALESCE(s.state, 'unknown')) AS seller_state,
        AVG(EXTRACT(EPOCH FROM (oi.shipping_limit_date - o.purchase_ts)) / 86400.0)
            AS shipping_limit_slack_days,
        AVG(p.weight_g)::double precision AS average_product_weight_g,
        AVG(p.length_cm * p.height_cm * p.width_cm)::double precision
            AS average_product_volume_cm3,
        AVG(CASE
            WHEN c.latitude IS NOT NULL AND c.longitude IS NOT NULL
             AND s.latitude IS NOT NULL AND s.longitude IS NOT NULL
            THEN 111.0 * SQRT(
                POWER(c.latitude - s.latitude, 2) +
                POWER((c.longitude - s.longitude) *
                      COS(RADIANS((c.latitude + s.latitude) / 2.0)), 2)
            )
        END)::double precision AS seller_distance_km
    FROM curated.order_items oi
    JOIN curated.orders o ON o.order_id = oi.order_id
    JOIN curated.customers c ON c.customer_id = o.customer_id
    JOIN curated.products p ON p.product_id = oi.product_id
    JOIN curated.sellers s ON s.seller_id = oi.seller_id
    GROUP BY oi.order_id
)
SELECT
    r.review_id,
    r.order_id,
    (r.review_score <= 3)::integer AS low_satisfaction,
    f.total_price,
    f.total_freight,
    f.item_count,
    f.product_count,
    f.seller_count,
    f.average_item_price,
    f.maximum_item_price,
    f.freight_ratio,
    ps.total_payment_value::double precision AS payment_value,
    ps.installments_max::double precision AS payment_installments,
    o.delivery_days::double precision AS delivery_days,
    EXTRACT(EPOCH FROM (o.delivered_customer_ts - o.estimated_delivery_ts)) / 3600.0
        AS delivery_delay_hours,
    o.is_late::integer AS is_late,
    EXTRACT(EPOCH FROM (o.approved_ts - o.purchase_ts)) / 3600.0 AS approval_hours,
    EXTRACT(EPOCH FROM (o.delivered_carrier_ts - o.approved_ts)) / 3600.0
        AS carrier_handling_hours,
    EXTRACT(EPOCH FROM (o.estimated_delivery_ts - o.purchase_ts)) / 86400.0
        AS estimated_delivery_days,
    f.shipping_limit_slack_days,
    f.seller_distance_km,
    f.average_product_weight_g,
    f.average_product_volume_cm3,
    COALESCE(c.state, 'unknown') AS customer_state,
    f.seller_state,
    f.dominant_category,
    COALESCE(ps.primary_payment_type, 'unknown') AS primary_payment_type,
    EXTRACT(MONTH FROM o.purchase_ts)::integer::text AS purchase_month,
    EXTRACT(ISODOW FROM o.purchase_ts)::integer::text AS purchase_weekday,
    EXTRACT(HOUR FROM o.purchase_ts)::integer::text AS purchase_hour
FROM curated.reviews r
JOIN curated.orders o ON o.order_id = r.order_id
JOIN curated.customers c ON c.customer_id = o.customer_id
JOIN item_features f ON f.order_id = o.order_id
LEFT JOIN curated.payment_summary ps ON ps.order_id = o.order_id
WHERE o.order_status = 'delivered'
ORDER BY r.review_id, r.order_id
"""


async def build_feature_frame() -> pd.DataFrame:
    """Return the authorized review-order grain with audit, label, and features."""
    frame = await query_frame(FEATURE_SQL)
    missing = set((*AUDIT_COLUMNS, TARGET_COLUMN, *FEATURE_COLUMNS)) - set(
        frame.columns
    )
    if missing:
        raise RuntimeError(f"Feature query omitted required columns: {sorted(missing)}")
    return frame


def feature_payload(frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series, pd.Series]:
    """Separate predictive inputs, positive-class labels, and order groups."""
    inputs = frame.loc[:, FEATURE_COLUMNS].copy()
    labels = frame[TARGET_COLUMN].astype(int)
    groups = frame[GROUP_COLUMN].astype(str)
    return inputs, labels, groups


def request_frame(payload: dict[str, Any]) -> pd.DataFrame:
    """Build one inference row in the exact training feature order."""
    row = {name: payload.get(name) for name in FEATURE_COLUMNS}
    for name in CATEGORICAL_FEATURES:
        if row[name] is not None:
            row[name] = str(row[name])
    return pd.DataFrame([row])
