"""Generate Phase 3 Markdown reports and executed notebooks."""

import asyncio
import gc
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import nbformat
from nbclient import NotebookClient
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook

from app.core.config import get_settings
from app.services.customer_analytics_service import customer_analytics
from app.services.dataframes import json_safe, query_frame
from app.services.eda_service import run_eda
from app.services.stats_service import run_statistical_analysis


def _fmt(value: Any) -> str:
    safe = json_safe(value)
    if safe is None:
        return "—"
    if isinstance(safe, float):
        if abs(safe) < 0.0001 and safe != 0:
            return f"{safe:.4e}"
        return f"{safe:,.4f}"
    return str(safe)


def _table(headers: list[str], rows: list[list[Any]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "|" + "|".join("---" for _ in headers) + "|",
    ]
    lines.extend("| " + " | ".join(_fmt(value) for value in row) + " |" for row in rows)
    return "\n".join(lines)


async def _dataset_counts() -> dict[str, int]:
    frame = await query_frame(
        """
        SELECT 'customers' AS entity, COUNT(*) AS rows FROM curated.customers
        UNION ALL SELECT 'orders', COUNT(*) FROM curated.orders
        UNION ALL SELECT 'order_items', COUNT(*) FROM curated.order_items
        UNION ALL SELECT 'payments', COUNT(*) FROM curated.payment_details
        UNION ALL SELECT 'reviews', COUNT(*) FROM curated.reviews
        UNION ALL SELECT 'customer_profile', COUNT(*) FROM marts.customer_profile
        """
    )
    return {str(row.entity): int(row.rows) for row in frame.itertuples()}


def _header(title: str, generated_at: str, commit: str, counts: dict[str, int]) -> str:
    count_text = ", ".join(f"{name}={count:,}" for name, count in counts.items())
    return (
        f"# {title}\n\n"
        f"- **Generated at:** `{generated_at}`\n"
        f"- **Code/commit reference:** `{commit}`\n"
        f"- **Dataset row counts used:** {count_text}\n"
        "- **Metric contract:** delivered orders only for revenue, orders, customers, AOV, and historical CLV; purchase timestamp is the date axis.\n"
    )


def _eda_markdown(
    eda: dict[str, Any], generated_at: str, commit: str, counts: dict[str, int]
) -> str:
    summary_rows = [
        [
            field,
            *[
                values[key]
                for key in (
                    "count",
                    "mean",
                    "median",
                    "mode",
                    "variance",
                    "std",
                    "q1",
                    "q3",
                    "min",
                    "max",
                )
            ],
        ]
        for field, values in eda["univariate"].items()
    ]
    payment_rows = [
        [row["payment_type"], row["orders"], row["average_order_value"]]
        for row in eda["bivariate"]["payment_type_aov"]
    ]
    trend_rows = [[row["month"], row["revenue"], row["orders"]] for row in eda["trend"]]
    seasonal_rows = [
        [row["month_of_year"], row["avg_monthly_revenue"], row["avg_monthly_orders"]]
        for row in eda["seasonality"]
    ]
    outlier = eda["category_outlier_comparison"]
    review = eda["review_duplicate_consistency"]
    delivery_rows = [
        [group, values["count"], values["mean"], values["50%"], values["std"]]
        for group, values in eda["bivariate"]["review_by_delivery_group"].items()
    ]
    return (
        "\n\n".join(
            [
                _header(
                    "Exploratory Data Analysis Report", generated_at, commit, counts
                ),
                "## Univariate analysis\n\n"
                + _table(
                    [
                        "Field",
                        "N",
                        "Mean",
                        "Median",
                        "Mode",
                        "Variance",
                        "Std",
                        "Q1",
                        "Q3",
                        "Min",
                        "Max",
                    ],
                    summary_rows,
                ),
                "## Bivariate analysis\n\n### Review score by delivery outcome\n\n"
                + _table(["Group", "N", "Mean", "Median", "Std"], delivery_rows)
                + "\n\n### Average order value by primary payment type\n\n"
                + _table(["Payment type", "Orders", "AOV (BRL)"], payment_rows)
                + "\n\nThe executed EDA notebook contains the required price/freight scatter and delivery/review boxplot.",
                "## Multivariate analysis\n\nThe executed notebook contains the full Pearson correlation heatmap across order revenue, item, freight, payment, installment, delivery, and order-grain review features.",
                "## Monthly trend\n\n"
                + _table(["Month", "Revenue (BRL)", "Delivered orders"], trend_rows),
                "## Month-of-year seasonality\n\n"
                + _table(["Month", "Average revenue", "Average orders"], seasonal_rows),
                "## Category-conditional Tukey follow-up\n\n"
                + _table(
                    [
                        "Measure",
                        "Global flags",
                        "Category flags",
                        "Changed rows",
                        "Changed % of population",
                    ],
                    [
                        [
                            "Price",
                            outlier["global_price"],
                            outlier["category_price"],
                            outlier["price_changed"],
                            outlier["price_changed_pct"],
                        ],
                        [
                            "Freight",
                            outlier["global_freight"],
                            outlier["category_freight"],
                            outlier["freight_changed"],
                            outlier["freight_changed_pct"],
                        ],
                    ],
                )
                + f"\n\n**Decision:** {outlier['decision']}",
                "## Duplicate review consistency\n\n"
                f"Review-grain outputs use deterministic `DISTINCT ON (review_id)`. "
                f"The source contains **{review['duplicate_groups']:,}** duplicate-review groups; "
                f"**{review['inconsistent_groups']:,}** disagree internally on score/title/message.",
            ]
        )
        + "\n"
    )


def _matrix_markdown(matrix: dict[str, dict[str, Any]], fields: list[str]) -> str:
    return _table(
        ["Field", *fields],
        [[row, *[matrix[column][row] for column in fields]] for row in fields],
    )


def _stats_markdown(
    result: dict[str, Any], generated_at: str, commit: str, counts: dict[str, int]
) -> str:
    desc = result["descriptive_statistics"]
    desc_rows = [
        [
            row[key]
            for key in (
                "field",
                "count",
                "mean",
                "median",
                "mode",
                "variance",
                "std",
                "q1",
                "q3",
            )
        ]
        for row in desc
    ]
    test_sections = []
    for test in result["hypothesis_tests"]:
        statistic = test.get(
            "statistic", test.get("f_statistic", test.get("t_statistic"))
        )
        test_sections.append(
            f"### {test['name']}\n\n"
            f"- Null hypothesis: {test['null_hypothesis']}\n"
            f"- Statistic: `{_fmt(statistic)}`\n"
            f"- p-value: `{_fmt(test['p_value'])}`\n"
            + (f"- Degrees of freedom: `{test['dof']}`\n" if "dof" in test else "")
            + f"- Conclusion: {test['conclusion']}"
        )
    matrices = result["matrices"]
    return (
        "\n\n".join(
            [
                _header("Statistical Analysis Report", generated_at, commit, counts),
                f"All inferential decisions use α = {result['significance_level']:.2f}.",
                "## Descriptive statistics\n\n"
                + _table(
                    [
                        "Field",
                        "N",
                        "Mean",
                        "Median",
                        "Mode",
                        "Variance",
                        "Std",
                        "Q1",
                        "Q3",
                    ],
                    desc_rows,
                ),
                "## Pearson correlation matrix\n\n"
                + _matrix_markdown(matrices["correlation"], matrices["fields"]),
                "## Covariance matrix\n\n"
                + _matrix_markdown(matrices["covariance"], matrices["fields"]),
                "## Hypothesis tests\n\n" + "\n\n".join(test_sections),
            ]
        )
        + "\n"
    )


def _customer_markdown(
    result: dict[str, Any], generated_at: str, commit: str, counts: dict[str, int]
) -> str:
    overview = result["overview"]
    gap = result["time_between_orders"]
    segment_rows = [
        [row["segment"], row["customer_count"], row["avg_clv"], row["avg_order_count"]]
        for row in result["segments"]
    ]
    region_rows = [
        [row["state"], row["customers"], row["avg_orders"], row["avg_clv"]]
        for row in result["regional_behavior"][:10]
    ]
    return (
        "\n\n".join(
            [
                _header("Customer Analytics Report", generated_at, commit, counts),
                "## Customer overview\n\n"
                + _table(
                    [
                        "Customers",
                        "Repeat customers",
                        "Repeat rate %",
                        "Average orders",
                        "Average CLV",
                        "Median CLV",
                    ],
                    [
                        [
                            overview["customers"],
                            overview["repeat_customers"],
                            overview["repeat_purchase_rate_pct"],
                            overview["avg_order_count"],
                            overview["avg_clv"],
                            overview["median_clv"],
                        ]
                    ],
                ),
                "## RFM segments\n\n"
                + _table(
                    [
                        "Segment",
                        "Customers",
                        "Average historical CLV",
                        "Average orders",
                    ],
                    segment_rows,
                ),
                "## Time between delivered orders\n\n"
                + _table(
                    ["Observed gaps", "Average days", "Median days"],
                    [
                        [
                            gap["gaps"],
                            gap["avg_days_between_orders"],
                            gap["median_days_between_orders"],
                        ]
                    ],
                ),
                "## Top customer states\n\n"
                + _table(
                    ["State", "Customers", "Average orders", "Average CLV"], region_rows
                ),
                "## Method\n\n"
                f"- RFM: {result['rfm_method']['scores']}\n"
                f"- CLV: {result['rfm_method']['clv']}\n"
                f"- Segmentation: {result['rfm_method']['segmentation']}",
            ]
        )
        + "\n"
    )


def _eda_notebook(metadata: str) -> Any:
    return new_notebook(
        cells=[
            new_markdown_cell(f"# Exploratory Data Analysis\n\n{metadata}"),
            new_code_cell(
                "import matplotlib.pyplot as plt\nimport pandas as pd\nimport seaborn as sns\nfrom app.services.dataframes import query_frame\nfrom app.services.eda_service import run_eda\nsns.set_theme(style='whitegrid')\neda = await run_eda()"
            ),
            new_code_cell("pd.DataFrame(eda['univariate']).T"),
            new_code_cell(
                "items = await query_frame('SELECT price, freight_value FROM curated.order_items')\npayments = await query_frame('SELECT payment_value FROM curated.payment_details')\ndelivery = await query_frame('SELECT delivery_days FROM curated.orders WHERE delivery_days IS NOT NULL')\nreviews = await query_frame(\"SELECT review_score FROM (SELECT DISTINCT ON (review_id) review_id, review_score FROM curated.reviews ORDER BY review_id, order_id) x\")\nfig, axes = plt.subplots(2, 3, figsize=(15, 8))\nfor ax, (name, values) in zip(axes.flat, [('price', items.price), ('freight_value', items.freight_value), ('payment_value', payments.payment_value), ('delivery_days', delivery.delivery_days), ('review_score', reviews.review_score)]):\n    sns.histplot(pd.to_numeric(values), bins=30, ax=ax)\n    ax.set_title(name)\naxes.flat[-1].axis('off')\nplt.tight_layout()"
            ),
            new_code_cell(
                "scatter = pd.DataFrame(eda['bivariate']['price_freight_sample'])\nsns.scatterplot(data=scatter, x='price', y='freight_value', alpha=.25)\nplt.title('Price vs freight value')"
            ),
            new_code_cell(
                "box = await query_frame(\"SELECT CASE WHEN o.is_late THEN 'late' ELSE 'on_time' END delivery_group, r.review_score FROM curated.orders o JOIN curated.reviews r ON r.order_id=o.order_id WHERE o.order_status='delivered'\")\nsns.boxplot(data=box, x='delivery_group', y='review_score')\nplt.title('Review score by delivery outcome')"
            ),
            new_code_cell("pd.DataFrame(eda['bivariate']['payment_type_aov'])"),
            new_code_cell(
                "corr = pd.DataFrame(eda['multivariate']['correlation'])\nplt.figure(figsize=(10, 8))\nsns.heatmap(corr, cmap='vlag', center=0, annot=True, fmt='.2f')\nplt.title('Pearson correlation matrix')"
            ),
            new_code_cell(
                "trend = pd.DataFrame(eda['trend'])\ntrend['month'] = pd.to_datetime(trend['month'])\nfig, ax = plt.subplots(figsize=(12, 4))\nax.plot(trend.month, trend.revenue, marker='o')\nax.set_title('Monthly delivered-order revenue')\nax.set_ylabel('BRL')"
            ),
            new_code_cell(
                "pd.DataFrame(eda['seasonality']).set_index('month_of_year')"
            ),
            new_code_cell(
                "pd.Series(eda['category_outlier_comparison'], name='value')"
            ),
            new_code_cell(
                "pd.Series(eda['review_duplicate_consistency'], name='groups')"
            ),
        ]
    )


def _stats_notebook(metadata: str) -> Any:
    return new_notebook(
        cells=[
            new_markdown_cell(f"# Statistical Analysis\n\n{metadata}"),
            new_code_cell(
                "import pandas as pd\nimport seaborn as sns\nimport matplotlib.pyplot as plt\nfrom app.services.stats_service import run_statistical_analysis\nfrom app.services.customer_analytics_service import customer_analytics\nstats_result = await run_statistical_analysis()\ncustomers = await customer_analytics()"
            ),
            new_code_cell(
                "pd.DataFrame(stats_result['descriptive_statistics']).set_index('field')"
            ),
            new_code_cell(
                "corr = pd.DataFrame(stats_result['matrices']['correlation'])\ncov = pd.DataFrame(stats_result['matrices']['covariance'])\nfig, axes = plt.subplots(1, 2, figsize=(18, 7))\nsns.heatmap(corr, cmap='vlag', center=0, ax=axes[0], annot=True, fmt='.2f')\naxes[0].set_title('Pearson correlation')\nsns.heatmap(cov, cmap='vlag', center=0, ax=axes[1])\naxes[1].set_title('Covariance')\nplt.tight_layout()"
            ),
            new_code_cell(
                "pd.DataFrame(stats_result['hypothesis_tests'])[['name', 'statistic', 'f_statistic', 't_statistic', 'p_value', 'conclusion']].fillna('')"
            ),
            new_markdown_cell("## Customer analytics evidence"),
            new_code_cell("pd.Series(customers['overview'])"),
            new_code_cell("pd.DataFrame(customers['segments'])"),
            new_code_cell("pd.Series(customers['time_between_orders'])"),
        ]
    )


def _execute_notebook(notebook: Any, target: Path) -> None:
    client = NotebookClient(notebook, timeout=600, kernel_name="python3")
    client.execute(cwd=str(Path.cwd()))
    nbformat.write(notebook, target)


async def generate_reports() -> dict[str, str]:
    settings = get_settings()
    report_dir = settings.report_dir
    notebook_dir = report_dir.parent / "notebooks"
    report_dir.mkdir(parents=True, exist_ok=True)
    notebook_dir.mkdir(parents=True, exist_ok=True)
    generated_at = datetime.now(UTC).isoformat()
    commit = os.getenv("GIT_COMMIT", "working-tree")
    counts = await _dataset_counts()
    eda = await run_eda()
    stats_result = await run_statistical_analysis()
    customers = await customer_analytics()

    artifacts = {
        "eda_report": report_dir / "eda_report.md",
        "statistics_report": report_dir / "statistical_analysis_report.md",
        "customer_report": report_dir / "customer_analytics_report.md",
        "eda_notebook": notebook_dir / "02_eda.ipynb",
        "statistics_notebook": notebook_dir / "03_statistical_analysis.ipynb",
    }
    artifacts["eda_report"].write_text(
        _eda_markdown(eda, generated_at, commit, counts), encoding="utf-8"
    )
    artifacts["statistics_report"].write_text(
        _stats_markdown(stats_result, generated_at, commit, counts), encoding="utf-8"
    )
    artifacts["customer_report"].write_text(
        _customer_markdown(customers, generated_at, commit, counts), encoding="utf-8"
    )
    del eda, stats_result, customers
    gc.collect()
    metadata = _header("Reproducibility", generated_at, commit, counts)
    _execute_notebook(_eda_notebook(metadata), artifacts["eda_notebook"])
    _execute_notebook(_stats_notebook(metadata), artifacts["statistics_notebook"])
    return {name: str(path) for name, path in artifacts.items()}


async def main() -> None:
    artifacts = await generate_reports()
    for name, path in artifacts.items():
        print(f"{name.upper()}={path}")


if __name__ == "__main__":
    asyncio.run(main())
