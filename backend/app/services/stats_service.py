"""Descriptive, matrix, and hypothesis-test analytics for SRS 12.2."""

from typing import Any

import numpy as np
import pandas as pd
from scipy import stats

from app.services.dataframes import query_frame
from app.services.eda_service import KEY_FIELDS, summarize_series

SIGNIFICANCE_LEVEL = 0.05


def _finite(value: float) -> float | None:
    return value if np.isfinite(value) else None


def _significance(p_value: float) -> str:
    return (
        "statistically significant"
        if p_value < SIGNIFICANCE_LEVEL
        else "not statistically significant"
    )


def compute_chi_square(contingency: pd.DataFrame) -> tuple[float, float, int]:
    """Compute a Chi-Square independence test for a supplied contingency table."""
    statistic, p_value, dof, _ = stats.chi2_contingency(contingency)
    return float(statistic), float(p_value), int(dof)


def compute_anova(
    groups: list[np.ndarray[Any, np.dtype[np.float64]]],
) -> tuple[float, float]:
    """Compute a one-way ANOVA for two or more numeric groups."""
    statistic, p_value = stats.f_oneway(*groups)
    return float(statistic), float(p_value)


def compute_welch_ttest(first: pd.Series, second: pd.Series) -> tuple[float, float]:
    """Compute a two-sample Welch T-Test without assuming equal variances."""
    statistic, p_value = stats.ttest_ind(first, second, equal_var=False)
    return float(statistic), float(p_value)


async def _key_numeric_data() -> dict[str, pd.Series]:
    items = await query_frame("SELECT price, freight_value FROM curated.order_items")
    payments = await query_frame("SELECT payment_value FROM curated.payment_details")
    orders = await query_frame(
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
        "delivery_days": orders["delivery_days"],
        "review_score": reviews["review_score"],
    }


async def _order_numeric_frame() -> pd.DataFrame:
    frame = await query_frame(
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
    return frame.apply(pd.to_numeric, errors="coerce")


async def descriptive_statistics() -> list[dict[str, Any]]:
    """Return required summaries using review-grain dedup for review_score."""
    data = await _key_numeric_data()
    return [{"field": field, **summarize_series(data[field])} for field in KEY_FIELDS]


async def correlation_and_covariance() -> dict[str, Any]:
    """Return full pairwise Pearson correlation and covariance matrices."""
    numeric = await _order_numeric_frame()
    return {
        "fields": list(numeric.columns),
        "correlation": numeric.corr(method="pearson").to_dict(),
        "covariance": numeric.cov().to_dict(),
        "observations": int(len(numeric)),
    }


async def chi_square_payment_segment() -> dict[str, Any]:
    """Test independence of primary payment type and RFM segment."""
    frame = await query_frame(
        """
        SELECT ps.primary_payment_type AS payment_type,
               cp.rfm_segment AS customer_segment, COUNT(*) AS orders
        FROM curated.orders o
        JOIN curated.customers c ON c.customer_id = o.customer_id
        JOIN curated.payment_summary ps ON ps.order_id = o.order_id
        JOIN marts.customer_profile cp
          ON cp.customer_unique_id = c.customer_unique_id
        WHERE o.order_status = 'delivered'
        GROUP BY ps.primary_payment_type, cp.rfm_segment
        """
    )
    contingency = frame.pivot(
        index="payment_type", columns="customer_segment", values="orders"
    ).fillna(0)
    statistic, p_value, dof = compute_chi_square(contingency)
    relation = _significance(float(p_value))
    return {
        "name": "Chi-Square: primary payment type × customer segment",
        "null_hypothesis": "Primary payment type and customer segment are independent.",
        "statistic": float(statistic),
        "p_value": float(p_value),
        "dof": int(dof),
        "conclusion": (
            f"The association between primary payment method and customer segment is {relation} "
            f"at α={SIGNIFICANCE_LEVEL:.2f}."
        ),
    }


async def anova_delivery_by_state() -> dict[str, Any]:
    """Compare delivered-order delivery days across customer states."""
    frame = await query_frame(
        """
        SELECT c.state, o.delivery_days
        FROM curated.orders o
        JOIN curated.customers c ON c.customer_id = o.customer_id
        WHERE o.order_status = 'delivered' AND o.delivery_days IS NOT NULL
          AND c.state IS NOT NULL
        """
    )
    groups = [
        pd.to_numeric(group["delivery_days"], errors="coerce").dropna().to_numpy()
        for _, group in frame.groupby("state")
        if len(group) >= 2
    ]
    statistic, p_value = compute_anova(groups)
    relation = _significance(float(p_value))
    return {
        "name": "One-way ANOVA: delivery days across customer states",
        "null_hypothesis": "Mean delivery time is equal across customer states.",
        "f_statistic": float(statistic),
        "p_value": float(p_value),
        "groups": len(groups),
        "conclusion": (
            f"Differences in mean delivery time across states are {relation} "
            f"at α={SIGNIFICANCE_LEVEL:.2f}."
        ),
    }


async def t_test_review_late() -> dict[str, Any]:
    """Compare order-grain review scores for on-time and late deliveries."""
    frame = await query_frame(
        """
        SELECT o.is_late, r.review_score
        FROM curated.orders o
        JOIN curated.reviews r ON r.order_id = o.order_id
        WHERE o.order_status = 'delivered' AND o.is_late IS NOT NULL
        """
    )
    on_time = pd.to_numeric(
        frame.loc[~frame["is_late"], "review_score"], errors="coerce"
    ).dropna()
    late = pd.to_numeric(
        frame.loc[frame["is_late"], "review_score"], errors="coerce"
    ).dropna()
    statistic, p_value = compute_welch_ttest(on_time, late)
    relation = _significance(float(p_value))
    direction = "lower" if late.mean() < on_time.mean() else "higher"
    return {
        "name": "Welch T-Test: review score for on-time vs late delivery",
        "null_hypothesis": "Mean review score is equal for on-time and late deliveries.",
        "t_statistic": _finite(float(statistic)),
        "p_value": _finite(float(p_value)),
        "on_time_mean": float(on_time.mean()),
        "late_mean": float(late.mean()),
        "on_time_n": int(len(on_time)),
        "late_n": int(len(late)),
        "conclusion": (
            f"Late deliveries have a {direction} mean review score than on-time deliveries; "
            f"the difference is {relation} at α={SIGNIFICANCE_LEVEL:.2f}."
        ),
    }


async def run_statistical_analysis() -> dict[str, Any]:
    """Compute the complete SRS 12.2 statistical evidence package."""
    return {
        "significance_level": SIGNIFICANCE_LEVEL,
        "descriptive_statistics": await descriptive_statistics(),
        "matrices": await correlation_and_covariance(),
        "hypothesis_tests": [
            await chi_square_payment_segment(),
            await anova_delivery_by_state(),
            await t_test_review_late(),
        ],
    }
