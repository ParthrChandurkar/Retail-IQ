"""Generate Migration M3 reports and executed notebooks."""

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
        SELECT 'raw_transactions' AS entity, COUNT(*) AS rows
        FROM raw.store_transactions
        UNION ALL SELECT 'customers', COUNT(*) FROM curated.customers
        UNION ALL SELECT 'products', COUNT(*) FROM curated.products
        UNION ALL SELECT 'orders', COUNT(*) FROM curated.orders
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
        "- **Metric contract:** all curated orders; Revenue=`SUM(sales)`, "
        "Profit=`SUM(profit)`, date axis=`order_date`, currency=INR.\n"
    )


def _screen_markdown(
    screen: dict[str, Any], generated_at: str, commit: str, counts: dict[str, int]
) -> str:
    summary_rows = [
        [
            row["categorical_field"],
            row["groups"],
            row["max_effect_size"],
            row["any_fdr_significant"],
            row["classification"],
        ]
        for row in screen["field_summary"]
    ]
    detail_rows = [
        [
            row["categorical_field"],
            row["numeric_outcome"],
            row["groups"],
            row["anova_f"],
            row["anova_p"],
            row["anova_fdr_q"],
            row["eta_squared"],
            row["kruskal_h"],
            row["kruskal_p"],
            row["kruskal_fdr_q"],
            row["epsilon_squared"],
        ]
        for row in screen["rows"]
    ]
    return (
        "\n\n".join(
            [
                _header("Categorical × Numeric Screen", generated_at, commit, counts),
                "## Result first\n\n"
                "`outlet_type` is the newly identified fourth decorative field. "
                "`country` is constant metadata, while `postal_code` is a redundant "
                "State proxy. The previously identified `region_as_reported`, "
                "`year_as_reported`, and `ship_mode` remain decorative. No comparison "
                "survived full-screen FDR correction with a material effect size. "
                "The specification-designated State, City Type, Segment, Category, "
                "Sub-Category, trusted Region, and order-year dimensions remain valid "
                "descriptive groupings, but the screen does not support causal or "
                "performance-difference claims for them.",
                "## Field-level summary\n\n"
                + _table(
                    [
                        "Field",
                        "Groups",
                        "Maximum effect",
                        "Any FDR significant",
                        "Classification",
                    ],
                    summary_rows,
                ),
                "## Complete 13 × 6 screen\n\n"
                + _table(
                    [
                        "Categorical field",
                        "Numeric outcome",
                        "Groups",
                        "ANOVA F",
                        "ANOVA p",
                        "ANOVA FDR q",
                        "η²",
                        "Kruskal H",
                        "Kruskal p",
                        "Kruskal FDR q",
                        "ε²",
                    ],
                    detail_rows,
                ),
                "## Method and exclusions\n\n"
                f"{screen['method']} Practical association screening uses 0.01 as the "
                "small-effect boundary; statistical significance alone is not treated "
                "as business importance.\n\n"
                f"{screen['excluded_non_dimensions']}",
            ]
        )
        + "\n"
    )


def _matrix_markdown(matrix: dict[str, dict[str, Any]], fields: list[str]) -> str:
    return _table(
        ["Field", *fields],
        [[row, *[matrix[column][row] for column in fields]] for row in fields],
    )


def _eda_markdown(
    eda: dict[str, Any], generated_at: str, commit: str, counts: dict[str, int]
) -> str:
    univariate_rows = [
        [
            field,
            *[
                values[key]
                for key in ("count", "mean", "median", "std", "q1", "q3", "min", "max")
            ],
        ]
        for field, values in eda["univariate"].items()
    ]
    region_rows = [
        [
            row["trusted_region"],
            row["count"],
            row["mean"],
            row["median"],
            row["std"],
            row["min"],
            row["max"],
        ]
        for row in eda["bivariate"]["shipping_by_trusted_region"]
    ]
    annual_rows = [
        [row["year"], row["revenue"], row["profit"], row["orders"]]
        for row in eda["annual"]
    ]
    seasonal_rows = [
        [
            row["month_of_year"],
            row["avg_monthly_revenue"],
            row["avg_daily_revenue"],
            row["avg_monthly_profit"],
            row["avg_monthly_orders"],
            row["avg_order_value"],
        ]
        for row in eda["seasonality"]
    ]
    trend_rows = [
        [row["month"], row["revenue"], row["profit"], row["orders"]]
        for row in eda["trend"]
    ]
    multivariate = eda["multivariate"]
    return (
        "\n\n".join(
            [
                _header(
                    "Migration M3 Exploratory Data Analysis",
                    generated_at,
                    commit,
                    counts,
                ),
                "## Field-screen constraint\n\n"
                "Downstream group comparisons use only specification-approved dimensions. "
                "Outlet Type, reported Region, reported Year, Country, Postal Code, and "
                "Ship Mode are not used for business-performance claims.",
                "## Univariate analysis\n\n"
                + _table(
                    ["Field", "N", "Mean", "Median", "Std", "Q1", "Q3", "Min", "Max"],
                    univariate_rows,
                ),
                "## Bivariate analysis\n\n"
                f"Discount versus Profit Pearson correlation: **{eda['bivariate']['discount_profit_pearson']:.6f}**. "
                f"Discount versus Profit Margin correlation: **{eda['bivariate']['discount_margin_pearson']:.6f}**. "
                "Discount has little relationship with gross sales but a clear negative "
                "relationship with profitability. The executed notebook contains the "
                "discount/profit scatter and trusted-region shipping boxplot.\n\n"
                "### Shipping days by trusted region\n\n"
                + _table(
                    ["Region", "N", "Mean", "Median", "Std", "Min", "Max"], region_rows
                ),
                "## Multivariate analysis\n\n### Pearson correlation\n\n"
                + _matrix_markdown(multivariate["correlation"], multivariate["fields"])
                + "\n\n### Covariance\n\n"
                + _matrix_markdown(multivariate["covariance"], multivariate["fields"]),
                "## Five-year trend\n\n"
                + _table(
                    ["Year", "Revenue (INR)", "Profit (INR)", "Orders"], annual_rows
                )
                + "\n\nThe annual totals are nearly flat; there is no evidence of sustained growth or decline.",
                "## Monthly trend, 2019–2023\n\n"
                + _table(
                    ["Month", "Revenue (INR)", "Profit (INR)", "Orders"], trend_rows
                ),
                "## Month-of-year seasonality\n\n"
                + _table(
                    [
                        "Month",
                        "Average monthly revenue",
                        "Average daily revenue",
                        "Average monthly profit",
                        "Average orders",
                        "Average order value",
                    ],
                    seasonal_rows,
                )
                + "\n\nRaw monthly revenue differs by calendar month "
                f"(ANOVA F={eda['seasonality_tests']['revenue']['f_statistic']:.6f}, "
                f"p={eda['seasonality_tests']['revenue']['p_value']:.6g}), with May "
                "highest and February lowest. After normalizing for calendar days, the "
                "difference disappears "
                f"(F={eda['seasonality_tests']['daily_revenue']['f_statistic']:.6f}, "
                f"p={eda['seasonality_tests']['daily_revenue']['p_value']:.6f}); AOV also "
                f"shows no month effect (p={eda['seasonality_tests']['average_order_value']['p_value']:.6f}). "
                "The apparent seasonality is calendar-length exposure, not demonstrated "
                "month-specific customer demand.",
                "## Ship Mode diagnostic\n\n"
                "Ship Mode remains excluded from business interpretation: every mode has "
                "median shipping duration 4 days, ANOVA p=0.349304, and η²=0.0000329.",
            ]
        )
        + "\n"
    )


def _stats_markdown(
    result: dict[str, Any], generated_at: str, commit: str, counts: dict[str, int]
) -> str:
    desc_rows = [
        [row[key] for key in ("field", "count", "mean", "median", "std", "q1", "q3")]
        for row in result["descriptive_statistics"]
    ]
    sections = []
    for test in result["hypothesis_tests"]:
        p_display = test.get("p_value_display", _fmt(test["p_value"]))
        extras = ""
        if "dof" in test:
            extras += f"- Degrees of freedom: `{test['dof']}`\n"
        if "group_means" in test:
            extras += f"- Group means: `{test['group_means']}`\n"
        if "low_discount_cutoff_pct" in test:
            extras += (
                f"- Low group: ≤{test['low_discount_cutoff_pct']:.2f}% "
                f"(n={test['low_discount_n']:,}, mean margin={test['low_discount_mean_margin_pct']:.6f}%)\n"
                f"- High group: ≥{test['high_discount_cutoff_pct']:.2f}% "
                f"(n={test['high_discount_n']:,}, mean margin={test['high_discount_mean_margin_pct']:.6f}%)\n"
            )
        sections.append(
            f"### {test['name']}\n\n"
            f"- Null hypothesis: {test['null_hypothesis']}\n"
            f"- Statistic: `{_fmt(test['statistic'])}`\n"
            f"- p-value: `{p_display}`\n"
            f"- {test['effect_size_name']}: `{_fmt(test['effect_size'])}`\n"
            f"{extras}"
            f"- Conclusion: {test['conclusion']}"
        )
    matrices = result["matrices"]
    return (
        "\n\n".join(
            [
                _header(
                    "Migration M3 Statistical Analysis", generated_at, commit, counts
                ),
                f"All inferential decisions use α={result['significance_level']:.2f}.",
                "## Descriptive statistics\n\n"
                + _table(
                    ["Field", "N", "Mean", "Median", "Std", "Q1", "Q3"], desc_rows
                ),
                "## Pearson correlation matrix\n\n"
                + _matrix_markdown(matrices["correlation"], matrices["fields"]),
                "## Covariance matrix\n\n"
                + _matrix_markdown(matrices["covariance"], matrices["fields"]),
                "## Required hypothesis tests\n\n" + "\n\n".join(sections),
            ]
        )
        + "\n"
    )


def _eda_notebook(metadata: str) -> Any:
    return new_notebook(
        cells=[
            new_markdown_cell(f"# Migration M3 — EDA\n\n{metadata}"),
            new_code_cell(
                "import matplotlib.pyplot as plt\nimport pandas as pd\nimport seaborn as sns\n"
                "from app.services.eda_service import analysis_frame, run_eda\n"
                "sns.set_theme(style='whitegrid')\nframe = await analysis_frame()\neda = await run_eda()"
            ),
            new_markdown_cell("## Broad categorical × numeric screen"),
            new_code_cell("pd.DataFrame(eda['categorical_screen']['field_summary'])"),
            new_code_cell("pd.DataFrame(eda['categorical_screen']['rows'])"),
            new_markdown_cell("## Univariate distributions"),
            new_code_cell(
                "fig, axes = plt.subplots(2, 2, figsize=(14, 9))\n"
                "for ax, field in zip(axes.flat, ['sales','discount_pct','profit','shipping_days']):\n"
                "    sns.histplot(frame[field], bins=35, ax=ax)\n    ax.set_title(field)\nplt.tight_layout()"
            ),
            new_markdown_cell("## Bivariate analysis"),
            new_code_cell(
                "sample = frame.iloc[::10]\nfig, axes = plt.subplots(1, 2, figsize=(14, 5))\n"
                "sns.scatterplot(data=sample, x='discount_pct', y='profit', alpha=.2, ax=axes[0])\n"
                "sns.boxplot(data=frame, x='trusted_region', y='shipping_days', ax=axes[1])\n"
                "axes[1].tick_params(axis='x', rotation=30)\nplt.tight_layout()"
            ),
            new_markdown_cell("## Multivariate correlation"),
            new_code_cell(
                "corr = pd.DataFrame(eda['multivariate']['correlation'])\n"
                "plt.figure(figsize=(9, 7))\nsns.heatmap(corr, cmap='vlag', center=0, annot=True, fmt='.3f')\nplt.tight_layout()"
            ),
            new_markdown_cell("## Five-year trend and seasonality"),
            new_code_cell(
                "trend = pd.DataFrame(eda['trend']); trend['month'] = pd.to_datetime(trend['month'])\n"
                "fig, axes = plt.subplots(2, 1, figsize=(13, 8))\n"
                "axes[0].plot(trend.month, trend.revenue, label='Revenue')\naxes[0].set_title('Monthly revenue, 2019–2023')\n"
                "season = pd.DataFrame(eda['seasonality'])\naxes[1].bar(season.month_of_year, season.avg_daily_revenue)\n"
                "axes[1].set_title('Average daily revenue by month of year')\nplt.tight_layout()"
            ),
        ]
    )


def _stats_notebook(metadata: str) -> Any:
    return new_notebook(
        cells=[
            new_markdown_cell(f"# Migration M3 — Statistical Analysis\n\n{metadata}"),
            new_code_cell(
                "import pandas as pd\nimport seaborn as sns\nimport matplotlib.pyplot as plt\n"
                "from app.services.stats_service import run_statistical_analysis\n"
                "result = await run_statistical_analysis()"
            ),
            new_code_cell(
                "pd.DataFrame(result['descriptive_statistics']).set_index('field')"
            ),
            new_code_cell(
                "corr = pd.DataFrame(result['matrices']['correlation'])\n"
                "cov = pd.DataFrame(result['matrices']['covariance'])\n"
                "fig, axes = plt.subplots(1, 2, figsize=(18, 7))\n"
                "sns.heatmap(corr, cmap='vlag', center=0, annot=True, fmt='.3f', ax=axes[0])\n"
                "sns.heatmap(cov, cmap='vlag', center=0, ax=axes[1])\nplt.tight_layout()"
            ),
            new_code_cell("pd.DataFrame(result['hypothesis_tests'])"),
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
    artifacts = {
        "categorical_screen_report": report_dir / "categorical_numeric_screen.md",
        "eda_report": report_dir / "eda_report.md",
        "statistics_report": report_dir / "statistical_analysis_report.md",
        "eda_notebook": notebook_dir / "02_eda.ipynb",
        "statistics_notebook": notebook_dir / "03_statistical_analysis.ipynb",
    }
    artifacts["categorical_screen_report"].write_text(
        _screen_markdown(eda["categorical_screen"], generated_at, commit, counts),
        encoding="utf-8",
    )
    artifacts["eda_report"].write_text(
        _eda_markdown(eda, generated_at, commit, counts), encoding="utf-8"
    )
    artifacts["statistics_report"].write_text(
        _stats_markdown(stats_result, generated_at, commit, counts), encoding="utf-8"
    )
    del eda, stats_result
    gc.collect()
    metadata = _header("Reproducibility", generated_at, commit, counts)
    _execute_notebook(_eda_notebook(metadata), artifacts["eda_notebook"])
    _execute_notebook(_stats_notebook(metadata), artifacts["statistics_notebook"])
    return {name: str(path) for name, path in artifacts.items()}


async def main() -> None:
    for name, path in (await generate_reports()).items():
        print(f"{name.upper()}={path}")


if __name__ == "__main__":
    asyncio.run(main())
