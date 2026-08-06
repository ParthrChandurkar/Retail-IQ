"""Exploratory analysis against curated data and Phase 3 marts."""

from typing import Any

import pandas as pd

from app.services.dataframes import json_safe, query_frame
from app.services.metrics import ELIGIBLE_ORDER_TOTALS_CTE

KEY_FIELDS = (
    "price",
    "freight_value",
    "payment_value",
    "delivery_days",
    "review_score",
)


def summarize_series(series: pd.Series) -> dict[str, float | int | None]:
    """Compute the binding numeric summary without silently dropping outliers."""
    values = pd.to_numeric(series, errors="coerce").dropna()
    modes = values.mode()
    return {
        "count": int(values.count()),
        "mean": json_safe(values.mean()),
        "median": json_safe(values.median()),
        "mode": json_safe(modes.iloc[0]) if not modes.empty else None,
        "variance": json_safe(values.var(ddof=1)),
        "std": json_safe(values.std(ddof=1)),
        "q1": json_safe(values.quantile(0.25)),
        "q3": json_safe(values.quantile(0.75)),
        "min": json_safe(values.min()),
        "max": json_safe(values.max()),
    }


async def _numeric_samples() -> dict[str, pd.Series]:
    items = await query_frame("SELECT price, freight_value FROM curated.order_items")
    payments = await query_frame("SELECT payment_value FROM curated.payment_details")
    delivery = await query_frame(
        "SELECT delivery_days FROM curated.orders WHERE delivery_days IS NOT NULL"
    )
    reviews = await query_frame(
        """
        SELECT review_score FROM (
            SELECT DISTINCT ON (review_id) review_id, review_score
            FROM curated.reviews ORDER BY review_id, order_id
        ) review_grain
        """
    )
    return {
        "price": items["price"],
        "freight_value": items["freight_value"],
        "payment_value": payments["payment_value"],
        "delivery_days": delivery["delivery_days"],
        "review_score": reviews["review_score"],
    }


async def category_outlier_comparison() -> dict[str, Any]:
    """Compare global and category-conditional Tukey classifications."""
    frame = await query_frame(
        """
        WITH global_bounds AS (
            SELECT percentile_cont(.25) WITHIN GROUP (ORDER BY price) AS q1p,
                   percentile_cont(.75) WITHIN GROUP (ORDER BY price) AS q3p,
                   percentile_cont(.25) WITHIN GROUP (
                       ORDER BY freight_value
                   ) AS q1f,
                   percentile_cont(.75) WITHIN GROUP (
                       ORDER BY freight_value
                   ) AS q3f
            FROM curated.order_items
        ), category_bounds AS (
            SELECT COALESCE(p.category_name_english, p.category_name, 'unknown')
                       AS category,
                   percentile_cont(.25) WITHIN GROUP (ORDER BY oi.price) AS q1p,
                   percentile_cont(.75) WITHIN GROUP (ORDER BY oi.price) AS q3p,
                   percentile_cont(.25) WITHIN GROUP (
                       ORDER BY oi.freight_value
                   ) AS q1f,
                   percentile_cont(.75) WITHIN GROUP (
                       ORDER BY oi.freight_value
                   ) AS q3f
            FROM curated.order_items oi
            JOIN curated.products p ON p.product_id = oi.product_id
            GROUP BY 1
        ), flags AS (
            SELECT
              (oi.price < gb.q1p - 1.5 * (gb.q3p - gb.q1p)
               OR oi.price > gb.q3p + 1.5 * (gb.q3p - gb.q1p)) AS global_price,
              (oi.price < cb.q1p - 1.5 * (cb.q3p - cb.q1p)
               OR oi.price > cb.q3p + 1.5 * (cb.q3p - cb.q1p)) AS category_price,
              (oi.freight_value < gb.q1f - 1.5 * (gb.q3f - gb.q1f)
               OR oi.freight_value > gb.q3f + 1.5 * (gb.q3f - gb.q1f))
                 AS global_freight,
              (oi.freight_value < cb.q1f - 1.5 * (cb.q3f - cb.q1f)
               OR oi.freight_value > cb.q3f + 1.5 * (cb.q3f - cb.q1f))
                 AS category_freight
            FROM curated.order_items oi
            JOIN curated.products p ON p.product_id = oi.product_id
            CROSS JOIN global_bounds gb
            JOIN category_bounds cb
              ON cb.category = COALESCE(
                  p.category_name_english, p.category_name, 'unknown'
              )
        )
        SELECT COUNT(*) AS population,
               COUNT(*) FILTER (WHERE global_price) AS global_price,
               COUNT(*) FILTER (WHERE category_price) AS category_price,
               COUNT(*) FILTER (
                   WHERE global_price <> category_price
               ) AS price_changed,
               COUNT(*) FILTER (WHERE global_freight) AS global_freight,
               COUNT(*) FILTER (WHERE category_freight) AS category_freight,
               COUNT(*) FILTER (
                   WHERE global_freight <> category_freight
               ) AS freight_changed
        FROM flags
        """
    )
    result = {key: json_safe(value) for key, value in frame.iloc[0].items()}
    population = int(result["population"])
    result["price_changed_pct"] = 100 * int(result["price_changed"]) / population
    result["freight_changed_pct"] = 100 * int(result["freight_changed"]) / population
    result["decision"] = (
        "Category-conditional bounds replace global item flags because thousands "
        "of rows change classification and the global category mix is materially "
        "misleading. Source rows remain retained."
    )
    return result


async def review_duplicate_consistency() -> dict[str, int]:
    """Validate the v1.2 review-grain deduplication precondition."""
    frame = await query_frame(
        """
        WITH duplicate_groups AS (
            SELECT review_id, COUNT(*) AS links,
                   COUNT(DISTINCT review_score) AS score_versions,
                   COUNT(DISTINCT COALESCE(comment_title, '<NULL>'))
                       AS title_versions,
                   COUNT(DISTINCT COALESCE(comment_message, '<NULL>'))
                       AS message_versions
            FROM curated.reviews GROUP BY review_id HAVING COUNT(*) > 1
        )
        SELECT COUNT(*) AS duplicate_groups,
               COUNT(*) FILTER (
                   WHERE score_versions > 1 OR title_versions > 1
                      OR message_versions > 1
               ) AS inconsistent_groups
        FROM duplicate_groups
        """
    )
    return {key: int(value) for key, value in frame.iloc[0].items()}


async def run_eda() -> dict[str, Any]:
    """Compute every SRS 12.1 output from real curated/mart data."""
    samples = await _numeric_samples()
    scatter = await query_frame(
        """
        SELECT price, freight_value FROM curated.order_items
        ORDER BY order_id, order_item_id LIMIT 10000
        """
    )
    delay_review = await query_frame(
        """
        SELECT o.delivery_delay_days, r.review_score,
               CASE WHEN o.is_late THEN 'late' ELSE 'on_time' END AS delivery_group
        FROM curated.orders o
        JOIN curated.reviews r ON r.order_id = o.order_id
        WHERE o.order_status = 'delivered'
          AND o.delivery_delay_days IS NOT NULL
        """
    )
    payment_aov = await query_frame(
        f"""
        WITH {ELIGIBLE_ORDER_TOTALS_CTE}, order_totals AS (
            SELECT eo.order_id, ps.primary_payment_type AS payment_type, eo.revenue
            FROM eligible_order_totals eo
            LEFT JOIN curated.payment_summary ps ON ps.order_id = eo.order_id
        )
        SELECT payment_type, COUNT(*) AS orders, AVG(revenue) AS average_order_value
        FROM order_totals GROUP BY payment_type ORDER BY orders DESC
        """
    )
    trend = await query_frame(
        f"""
        WITH {ELIGIBLE_ORDER_TOTALS_CTE}
        SELECT date_trunc('month', purchase_ts)::date AS month,
               SUM(revenue) AS revenue, COUNT(*) AS orders
        FROM eligible_order_totals GROUP BY 1 ORDER BY 1
        """
    )
    seasonality = await query_frame(
        f"""
        WITH monthly AS (
            WITH {ELIGIBLE_ORDER_TOTALS_CTE}
            SELECT date_trunc('month', purchase_ts)::date AS month,
                   SUM(revenue) AS revenue, COUNT(*) AS orders
            FROM eligible_order_totals GROUP BY 1
        )
        SELECT EXTRACT(MONTH FROM month)::integer AS month_of_year,
               AVG(revenue) AS avg_monthly_revenue,
               AVG(orders::numeric) AS avg_monthly_orders
        FROM monthly GROUP BY 1 ORDER BY 1
        """
    )
    correlation_frame = await query_frame(
        """
        WITH item_rollup AS (
            SELECT order_id, SUM(price + freight_value) AS order_revenue,
                   AVG(price) AS avg_item_price, SUM(freight_value) AS freight_value,
                   COUNT(*) AS item_count
            FROM curated.order_items GROUP BY order_id
        ), order_review AS (
            SELECT order_id, AVG(review_score::numeric) AS review_score
            FROM curated.reviews GROUP BY order_id
        )
        SELECT ir.order_revenue, ir.avg_item_price, ir.freight_value,
               ir.item_count, ps.total_payment_value, ps.installments_max,
               o.delivery_days, o.delivery_delay_days, rv.review_score
        FROM curated.orders o
        JOIN item_rollup ir ON ir.order_id = o.order_id
        LEFT JOIN curated.payment_summary ps ON ps.order_id = o.order_id
        LEFT JOIN order_review rv ON rv.order_id = o.order_id
        WHERE o.order_status = 'delivered'
        """
    )
    numeric = correlation_frame.apply(pd.to_numeric, errors="coerce")
    return {
        "univariate": {field: summarize_series(samples[field]) for field in KEY_FIELDS},
        "bivariate": {
            "price_freight_sample": scatter.to_dict(orient="records"),
            "review_by_delivery_group": delay_review.groupby("delivery_group")[
                "review_score"
            ]
            .describe()
            .to_dict(orient="index"),
            "payment_type_aov": payment_aov.to_dict(orient="records"),
        },
        "multivariate": {
            "correlation": numeric.corr(method="pearson").to_dict(),
            "fields": list(numeric.columns),
        },
        "trend": trend.to_dict(orient="records"),
        "seasonality": seasonality.to_dict(orient="records"),
        "category_outlier_comparison": await category_outlier_comparison(),
        "review_duplicate_consistency": await review_duplicate_consistency(),
    }
