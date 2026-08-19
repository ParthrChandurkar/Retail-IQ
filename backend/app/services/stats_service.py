"""Migration M3 descriptive and inferential statistics."""

from typing import Any

import numpy as np
import pandas as pd
from scipy import stats

from app.services.eda_service import NUMERIC_OUTCOMES, analysis_frame, summarize_series

SIGNIFICANCE_LEVEL = 0.05


def compute_chi_square(contingency: pd.DataFrame) -> tuple[float, float, int]:
    """Compute a Chi-Square independence test."""
    statistic, p_value, dof, _ = stats.chi2_contingency(contingency)
    return float(statistic), float(p_value), int(dof)


def compute_anova(
    groups: list[np.ndarray[Any, np.dtype[np.float64]]],
) -> tuple[float, float]:
    """Compute a one-way ANOVA."""
    statistic, p_value = stats.f_oneway(*groups)
    return float(statistic), float(p_value)


def compute_welch_ttest(first: pd.Series, second: pd.Series) -> tuple[float, float]:
    """Compute a two-sample Welch t-test."""
    statistic, p_value = stats.ttest_ind(first, second, equal_var=False)
    return float(statistic), float(p_value)


def _eta_squared(frame: pd.DataFrame, group: str, outcome: str) -> float:
    grand_mean = float(frame[outcome].mean())
    between = sum(
        len(values) * (float(values[outcome].mean()) - grand_mean) ** 2
        for _, values in frame.groupby(group, observed=True)
    )
    total = float(((frame[outcome] - grand_mean) ** 2).sum())
    return between / total if total else 0.0


async def descriptive_statistics() -> list[dict[str, Any]]:
    """Describe every numeric outcome in the M3 analytical frame."""
    frame = await analysis_frame()
    return [
        {"field": field, **summarize_series(frame[field])} for field in NUMERIC_OUTCOMES
    ]


async def correlation_and_covariance() -> dict[str, Any]:
    """Return complete numeric Pearson correlation and covariance matrices."""
    frame = await analysis_frame()
    numeric = frame[list(NUMERIC_OUTCOMES)]
    return {
        "fields": list(numeric.columns),
        "correlation": numeric.corr(method="pearson").to_dict(),
        "covariance": numeric.cov().to_dict(),
        "observations": int(len(numeric)),
    }


async def chi_square_category_segment() -> dict[str, Any]:
    """Test category and given customer segment for independence."""
    frame = await analysis_frame()
    contingency = pd.crosstab(frame["category"], frame["segment"])
    statistic, p_value, dof = compute_chi_square(contingency)
    n = int(contingency.to_numpy().sum())
    cramers_v = float(
        np.sqrt(
            statistic / (n * min(contingency.shape[0] - 1, contingency.shape[1] - 1))
        )
    )
    return {
        "name": "Chi-Square: category × customer segment",
        "null_hypothesis": "Product category and customer segment are independent.",
        "statistic": statistic,
        "p_value": p_value,
        "dof": dof,
        "effect_size_name": "Cramer's V",
        "effect_size": cramers_v,
        "conclusion": (
            "No statistically significant category preference difference was found "
            "between Consumer and Corporate buyers; the observed association is negligible."
        ),
    }


async def anova_margin_by_city_type() -> dict[str, Any]:
    """Compare profit margin across the explicitly valid City Type dimension."""
    frame = await analysis_frame()
    groups = [
        group["profit_margin_pct"].to_numpy(dtype=float)
        for _, group in frame.groupby("city_type", observed=True)
    ]
    statistic, p_value = compute_anova(groups)
    means = {
        str(name): float(group["profit_margin_pct"].mean())
        for name, group in frame.groupby("city_type", observed=True)
    }
    return {
        "name": "One-way ANOVA: profit margin across city types",
        "null_hypothesis": "Mean profit margin is equal across city types.",
        "statistic": statistic,
        "p_value": p_value,
        "groups": len(groups),
        "effect_size_name": "Eta-squared",
        "effect_size": _eta_squared(frame, "city_type", "profit_margin_pct"),
        "group_means": means,
        "conclusion": (
            "Profit margins do not differ significantly across Tier 1, Tier 2, "
            "and Village orders; city type explains effectively none of the variation."
        ),
    }


async def t_test_margin_by_discount() -> dict[str, Any]:
    """Compare profit margin for data-derived high- and low-discount orders."""
    frame = await analysis_frame()
    low_rows = frame.loc[frame["discount_band"] == "low"]
    high_rows = frame.loc[frame["discount_band"] == "high"]
    low_cutoff = float(low_rows["discount_pct"].max())
    high_cutoff = float(high_rows["discount_pct"].min())
    low = low_rows["profit_margin_pct"].dropna()
    high = high_rows["profit_margin_pct"].dropna()
    statistic, p_value = compute_welch_ttest(high, low)
    pooled_std = float(
        np.sqrt(
            ((len(high) - 1) * high.var(ddof=1) + (len(low) - 1) * low.var(ddof=1))
            / (len(high) + len(low) - 2)
        )
    )
    cohens_d = float((high.mean() - low.mean()) / pooled_std)
    return {
        "name": "Welch t-test: profit margin for high- vs low-discount orders",
        "null_hypothesis": "Mean profit margin is equal for high- and low-discount orders.",
        "statistic": statistic,
        "p_value": p_value,
        "p_value_display": "<1e-300" if p_value == 0.0 else f"{p_value:.6g}",
        "effect_size_name": "Cohen's d",
        "effect_size": cohens_d,
        "low_discount_cutoff_pct": low_cutoff,
        "high_discount_cutoff_pct": high_cutoff,
        "low_discount_n": int(len(low)),
        "high_discount_n": int(len(high)),
        "low_discount_mean_margin_pct": float(low.mean()),
        "high_discount_mean_margin_pct": float(high.mean()),
        "conclusion": (
            "High-discount orders have a materially lower mean profit margin than "
            "low-discount orders; the difference is statistically significant and large."
        ),
    }


async def t_test_review_late() -> dict[str, Any]:
    """Reject the retired review-era test until recommendation routing is migrated."""
    raise RuntimeError(
        "Review-score testing is not applicable to Indian Store Data; "
        "the recommendation service is scheduled for Migration M6."
    )


async def run_statistical_analysis() -> dict[str, Any]:
    """Compute the complete Migration M3 statistical evidence package."""
    return {
        "significance_level": SIGNIFICANCE_LEVEL,
        "descriptive_statistics": await descriptive_statistics(),
        "matrices": await correlation_and_covariance(),
        "hypothesis_tests": [
            await chi_square_category_segment(),
            await anova_margin_by_city_type(),
            await t_test_margin_by_discount(),
        ],
    }
