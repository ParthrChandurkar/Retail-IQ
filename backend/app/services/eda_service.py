"""Migration M3 exploratory analysis for Indian Store Data."""

from typing import Any

import pandas as pd
from scipy import stats

from app.services.dataframes import json_safe, query_frame

NUMERIC_OUTCOMES = (
    "sales",
    "profit",
    "discount_pct",
    "quantity",
    "shipping_days",
    "profit_margin_pct",
)

CATEGORICAL_FIELDS = (
    "outlet_type",
    "city_type",
    "category",
    "region_as_reported",
    "country",
    "segment",
    "ship_mode",
    "state",
    "postal_code",
    "sub_category",
    "trusted_region",
    "year_as_reported",
    "order_year",
)

KNOWN_GOOD_DIMENSIONS = {
    "city_type",
    "category",
    "segment",
    "state",
    "sub_category",
    "trusted_region",
    "order_year",
}


def summarize_series(series: pd.Series) -> dict[str, float | int | None]:
    """Return robust descriptive statistics without deleting valid outliers."""
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


def _benjamini_hochberg(values: list[float | None]) -> list[float | None]:
    """Adjust a family of p-values with the Benjamini-Hochberg procedure."""
    valid = [(index, value) for index, value in enumerate(values) if value is not None]
    adjusted: list[float | None] = [None] * len(values)
    running = 1.0
    total = len(valid)
    for rank, (index, value) in reversed(
        list(enumerate(sorted(valid, key=lambda x: x[1]), 1))
    ):
        running = min(running, value * total / rank)
        adjusted[index] = min(1.0, running)
    return adjusted


async def analysis_frame() -> pd.DataFrame:
    """Load the authoritative order-grain analysis frame."""
    frame = await query_frame(
        """
        SELECT r.outlet_type, c.city_type, p.category,
               c.region_as_reported, r.country, c.segment, o.ship_mode,
               c.state, c.postal_code, p.sub_category,
               sr.region AS trusted_region, r.year AS year_as_reported,
               o.order_year,
               o.order_date, o.sales, o.profit, o.discount_pct, o.quantity,
               o.shipping_days, o.profit_margin_pct, o.discount_band,
               o.is_high_profit_order, o.order_month, o.order_dow
        FROM curated.orders o
        JOIN curated.customers c ON c.customer_id = o.customer_id
        JOIN curated.products p ON p.product_id = o.product_id
        JOIN curated.state_region_reference sr ON sr.state = c.state
        JOIN raw.store_transactions r ON r.order_id = o.order_id
        """
    )
    for field in NUMERIC_OUTCOMES:
        frame[field] = pd.to_numeric(frame[field], errors="coerce")
    return frame


def _screen_pair(frame: pd.DataFrame, category: str, outcome: str) -> dict[str, Any]:
    sample = frame[[category, outcome]].dropna()
    groups = [
        group[outcome].to_numpy(dtype=float)
        for _, group in sample.groupby(category, observed=True)
        if len(group) >= 2
    ]
    if len(groups) < 2:
        return {
            "categorical_field": category,
            "numeric_outcome": outcome,
            "groups": len(groups),
            "observations": int(len(sample)),
            "anova_f": None,
            "anova_p": None,
            "eta_squared": 0.0,
            "kruskal_h": None,
            "kruskal_p": None,
            "epsilon_squared": 0.0,
        }
    anova_f, anova_p = stats.f_oneway(*groups)
    kruskal_h, kruskal_p = stats.kruskal(*groups)
    grand_mean = float(sample[outcome].mean())
    between = sum(
        len(group) * (float(group.mean()) - grand_mean) ** 2 for group in groups
    )
    total = float(((sample[outcome] - grand_mean) ** 2).sum())
    eta_squared = between / total if total else 0.0
    epsilon_squared = max(
        0.0,
        (float(kruskal_h) - len(groups) + 1) / (len(sample) - len(groups)),
    )
    return {
        "categorical_field": category,
        "numeric_outcome": outcome,
        "groups": len(groups),
        "observations": int(len(sample)),
        "anova_f": float(anova_f),
        "anova_p": float(anova_p),
        "eta_squared": eta_squared,
        "kruskal_h": float(kruskal_h),
        "kruskal_p": float(kruskal_p),
        "epsilon_squared": epsilon_squared,
    }


def categorical_numeric_screen(frame: pd.DataFrame) -> dict[str, Any]:
    """Screen every analytical categorical field against every numeric outcome."""
    rows = [
        _screen_pair(frame, categorical, outcome)
        for categorical in CATEGORICAL_FIELDS
        for outcome in NUMERIC_OUTCOMES
    ]
    anova_q = _benjamini_hochberg([row["anova_p"] for row in rows])
    kruskal_q = _benjamini_hochberg([row["kruskal_p"] for row in rows])
    for row, aq, kq in zip(rows, anova_q, kruskal_q, strict=True):
        row["anova_fdr_q"] = aq
        row["kruskal_fdr_q"] = kq

    summary = []
    for field in CATEGORICAL_FIELDS:
        field_rows = [row for row in rows if row["categorical_field"] == field]
        groups = max(int(row["groups"]) for row in field_rows)
        max_effect = max(
            max(float(row["eta_squared"]), float(row["epsilon_squared"]))
            for row in field_rows
        )
        fdr_significant = any(
            (row["anova_fdr_q"] is not None and row["anova_fdr_q"] < 0.05)
            or (row["kruskal_fdr_q"] is not None and row["kruskal_fdr_q"] < 0.05)
            for row in field_rows
        )
        if groups < 2:
            classification = "constant_metadata"
        elif field in KNOWN_GOOD_DIMENSIONS:
            classification = "valid_dimension_no_material_numeric_effect"
        elif field == "postal_code":
            classification = "redundant_state_proxy"
        elif not fdr_significant and max_effect < 0.01:
            classification = "decorative"
        else:
            classification = "material_numeric_association"
        summary.append(
            {
                "categorical_field": field,
                "groups": groups,
                "max_effect_size": max_effect,
                "any_fdr_significant": fdr_significant,
                "classification": classification,
            }
        )
    return {
        "method": (
            "One-way ANOVA and Kruskal-Wallis for all field/outcome pairs; "
            "Benjamini-Hochberg FDR correction within the complete screen. "
            "Effect sizes are eta-squared and epsilon-squared."
        ),
        "rows": rows,
        "field_summary": summary,
        "excluded_non_dimensions": (
            "Customer/Order/Product IDs, names, product name and date of birth are "
            "identifiers or PII; dates are handled as time dimensions."
        ),
    }


async def run_eda() -> dict[str, Any]:
    """Compute every Migration v2.0 section 5 output from real data."""
    frame = await analysis_frame()
    numeric = frame[list(NUMERIC_OUTCOMES)]
    monthly = await query_frame(
        """
        SELECT date_trunc('month', order_date)::date AS month,
               SUM(sales) AS revenue, SUM(profit) AS profit,
               COUNT(DISTINCT order_id)::integer AS orders
        FROM curated.orders GROUP BY 1 ORDER BY 1
        """
    )
    seasonality = monthly.copy()
    seasonality["month"] = pd.to_datetime(seasonality["month"])
    seasonality["month_of_year"] = seasonality["month"].dt.month
    seasonality["days_in_month"] = seasonality["month"].dt.days_in_month
    seasonality["daily_revenue"] = (
        pd.to_numeric(seasonality["revenue"]) / seasonality["days_in_month"]
    )
    seasonality["average_order_value"] = pd.to_numeric(
        seasonality["revenue"]
    ) / pd.to_numeric(seasonality["orders"])
    seasonal_summary = (
        seasonality.groupby("month_of_year", as_index=False)
        .agg(
            avg_monthly_revenue=("revenue", "mean"),
            avg_daily_revenue=("daily_revenue", "mean"),
            avg_monthly_profit=("profit", "mean"),
            avg_monthly_orders=("orders", "mean"),
            avg_order_value=("average_order_value", "mean"),
        )
        .to_dict(orient="records")
    )
    seasonality_tests = {}
    for field in ("revenue", "daily_revenue", "average_order_value"):
        groups = [
            pd.to_numeric(group[field]).to_numpy(dtype=float)
            for _, group in seasonality.groupby("month_of_year")
        ]
        statistic, p_value = stats.f_oneway(*groups)
        seasonality_tests[field] = {
            "f_statistic": float(statistic),
            "p_value": float(p_value),
        }
    discount_profit = frame[["discount_pct", "profit", "profit_margin_pct"]]
    region_shipping = (
        frame.groupby("trusted_region", as_index=False)["shipping_days"]
        .agg(["count", "mean", "median", "std", "min", "max"])
        .reset_index()
    )
    ship_mode_diagnostic = (
        frame.groupby("ship_mode", as_index=False)["shipping_days"]
        .agg(["count", "mean", "median", "std", "min", "max"])
        .reset_index()
    )
    annual = (
        frame.assign(year=pd.to_datetime(frame["order_date"]).dt.year)
        .groupby("year", as_index=False)
        .agg(
            revenue=("sales", "sum"), profit=("profit", "sum"), orders=("sales", "size")
        )
    )
    return {
        "categorical_screen": categorical_numeric_screen(frame),
        "univariate": {
            field: summarize_series(frame[field])
            for field in ("sales", "discount_pct", "profit", "shipping_days")
        },
        "bivariate": {
            "discount_profit_pearson": float(
                discount_profit.corr().loc["discount_pct", "profit"]
            ),
            "discount_margin_pearson": float(
                discount_profit.corr().loc["discount_pct", "profit_margin_pct"]
            ),
            "discount_profit_sample": discount_profit.iloc[::10].to_dict(
                orient="records"
            ),
            "shipping_by_trusted_region": region_shipping.to_dict(orient="records"),
            "ship_mode_integrity_diagnostic": ship_mode_diagnostic.to_dict(
                orient="records"
            ),
        },
        "multivariate": {
            "fields": list(numeric.columns),
            "correlation": numeric.corr(method="pearson").to_dict(),
            "covariance": numeric.cov().to_dict(),
        },
        "trend": monthly.to_dict(orient="records"),
        "annual": annual.to_dict(orient="records"),
        "seasonality": seasonal_summary,
        "seasonality_tests": seasonality_tests,
    }
