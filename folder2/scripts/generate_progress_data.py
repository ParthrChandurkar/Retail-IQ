"""Generate Power BI-ready extracts from the checked-in analytics evidence.

This script deliberately reads the generated Markdown reports. It does not invent
or duplicate analytical results, and it fails when an expected report/table is
missing so a stale faculty dashboard cannot silently be published.
"""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REPORTS = ROOT / "analytics" / "reports"
OUTPUT = ROOT / "folder2" / "data"
PREVIEW_DATA = ROOT / "folder2" / "preview" / "data.js"


def read_report(name: str) -> str:
    path = REPORTS / name
    if not path.exists():
        raise FileNotFoundError(f"Required evidence is missing: {path}")
    return path.read_text(encoding="utf-8")


def section(text: str, heading: str) -> str:
    match = re.search(
        rf"^##+\s+{re.escape(heading)}\s*$\n(.*?)(?=^##+\s|\Z)",
        text,
        flags=re.MULTILINE | re.DOTALL,
    )
    if not match:
        raise ValueError(f"Section not found: {heading}")
    return match.group(1)


def markdown_table(text: str, heading: str) -> list[dict[str, str]]:
    block = section(text, heading)
    lines = [line.strip() for line in block.splitlines() if line.strip().startswith("|")]
    if len(lines) < 3:
        raise ValueError(f"Markdown table not found below: {heading}")
    headers = [cell.strip() for cell in lines[0].strip("|").split("|")]
    rows: list[dict[str, str]] = []
    for line in lines[2:]:
        cells = [cell.strip().strip("`") for cell in line.strip("|").split("|")]
        if len(cells) == len(headers):
            rows.append(dict(zip(headers, cells, strict=True)))
    return rows


def number(value: str) -> float:
    cleaned = value.replace(",", "").replace("%", "").strip()
    return float(cleaned)


def report_value(text: str, pattern: str, label: str) -> float:
    match = re.search(pattern, text, flags=re.MULTILINE)
    if not match:
        raise ValueError(f"Could not derive report value: {label}")
    return number(match.group(1))


def write_csv(name: str, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"Refusing to write empty extract: {name}")
    path = OUTPUT / name
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    eda = read_report("eda_report.md")
    quality = read_report("data_quality_report_post_clean.md")
    customer = read_report("customer_analytics_report.md")
    statistics = read_report("statistical_analysis_report.md")

    overview = markdown_table(customer, "Customer overview")[0]
    monthly = [
        {
            "month": row["Month"],
            "revenue_brl": number(row["Revenue (BRL)"]),
            "delivered_orders": int(number(row["Delivered orders"])),
        }
        for row in markdown_table(eda, "Monthly trend")
    ]
    segments = [
        {
            "segment": row["Segment"],
            "customers": int(number(row["Customers"])),
            "average_historical_clv": number(row["Average historical CLV"]),
            "average_orders": number(row["Average orders"]),
        }
        for row in markdown_table(customer, "RFM segments")
    ]
    customer_overview = [
        {
            "customers": int(number(overview["Customers"])),
            "repeat_customers": int(number(overview["Repeat customers"])),
            "repeat_rate_pct": number(overview["Repeat rate %"]),
            "average_orders": number(overview["Average orders"]),
            "average_clv": number(overview["Average CLV"]),
            "median_clv": number(overview["Median CLV"]),
        }
    ]
    delivery_review = [
        {
            "delivery_outcome": row["Group"],
            "reviews": int(number(row["N"])),
            "mean_review_score": number(row["Mean"]),
            "median_review_score": number(row["Median"]),
            "std_review_score": number(row["Std"]),
        }
        for row in markdown_table(eda, "Review score by delivery outcome")
    ]
    curated = [
        {"layer": "curated", "table": row["Curated table"], "rows": int(number(row["Rows"]))}
        for row in markdown_table(quality, "Curated row counts")
    ]
    outliers = [
        {
            "field": row["Field"],
            "global_flagged": int(number(row["Flagged"])),
            "global_flagged_pct": number(row["Flagged %"]),
            "persisted_flagged": int(number(row["Persisted flag count"])),
            "handling": "retained and flagged",
        }
        for row in markdown_table(quality, "Retained outlier flags")
    ]
    cleaning = [
        {
            "source_to_curated": row["Source → curated"],
            "raw_rows": int(number(row["Raw rows"])),
            "curated_rows": int(number(row["Curated rows"])),
            "rows_removed": int(number(row["Rows removed"])),
            "rationale": row["Rationale"],
        }
        for row in markdown_table(quality, "Cleaning diff")
    ]

    revenue = round(sum(row["revenue_brl"] for row in monthly), 2)
    delivered_orders = sum(row["delivered_orders"] for row in monthly)
    customers = int(number(overview["Customers"]))
    review_score = number(markdown_table(eda, "Univariate analysis")[-1]["Mean"])
    kpis = [
        {"metric": "Delivered revenue", "value": revenue, "unit": "BRL", "definition": "Item price plus freight for delivered orders"},
        {"metric": "Delivered orders", "value": delivered_orders, "unit": "orders", "definition": "Distinct delivered orders"},
        {"metric": "Customers", "value": customers, "unit": "customers", "definition": "Distinct customers with a delivered order"},
        {"metric": "Average order value", "value": round(revenue / delivered_orders, 2), "unit": "BRL", "definition": "Delivered revenue divided by delivered orders"},
        {"metric": "Repeat-customer rate", "value": number(overview["Repeat rate %"]), "unit": "percent", "definition": "Customers with more than one delivered order"},
        {"metric": "Average review score", "value": review_score, "unit": "score", "definition": "Review-grain deterministic deduplication"},
    ]
    phases = [
        {"phase": 1, "name": "Project setup", "status": "Complete", "evidence": "Docker, FastAPI, Next.js, PostgreSQL schemas, CI"},
        {"phase": 2, "name": "Backend foundation & ETL", "status": "Complete", "evidence": "9 raw tables, curated layer, idempotent ETL, quality reports"},
        {"phase": 3, "name": "Analytics, EDA & statistics", "status": "Complete", "evidence": "Marts, RFM/CLV, EDA, three hypothesis tests"},
        {"phase": 4, "name": "Target variable selection", "status": "Pending", "evidence": "No checked-in target_variable_selection.md yet"},
        {"phase": 5, "name": "API & authentication", "status": "Pending", "evidence": "Not started"},
        {"phase": 6, "name": "Machine learning", "status": "Pending", "evidence": "Not started"},
        {"phase": 7, "name": "Frontend integration", "status": "Pending", "evidence": "Not started"},
        {"phase": 8, "name": "Testing & hardening", "status": "Pending", "evidence": "Not started"},
        {"phase": 9, "name": "Documentation & Power BI", "status": "Pending", "evidence": "Final governed deliverables not started"},
    ]
    test_specs = [
        ("Chi-Square", "Chi-Square: primary payment type × customer segment", "Payment type × customer segment"),
        ("One-way ANOVA", "One-way ANOVA: delivery days across customer states", "Delivery days across states"),
        ("Welch T-Test", "Welch T-Test: review score for on-time vs late delivery", "Review score: on-time vs late"),
    ]
    tests = []
    for test_name, report_heading, comparison in test_specs:
        block = section(statistics, report_heading)
        statistic = report_value(block, r"^- Statistic: `([^`]+)`", f"{test_name} statistic")
        p_value = report_value(block, r"^- p-value: `([^`]+)`", f"{test_name} p-value")
        conclusion_match = re.search(r"^- Conclusion: (.+)$", block, flags=re.MULTILINE)
        if not conclusion_match:
            raise ValueError(f"Could not derive report conclusion: {test_name}")
        tests.append(
            {
                "test": test_name,
                "comparison": comparison,
                "statistic": statistic,
                "p_value": p_value,
                "significant": "Yes" if p_value < 0.05 else "No",
                "conclusion": conclusion_match.group(1),
            }
        )

    datasets = {
        "project_progress": phases,
        "kpi_summary": kpis,
        "monthly_revenue": monthly,
        "customer_segments": segments,
        "customer_overview": customer_overview,
        "delivery_review": delivery_review,
        "curated_row_counts": curated,
        "cleaning_summary": cleaning,
        "outlier_summary": outliers,
        "hypothesis_tests": tests,
    }
    for name, rows in datasets.items():
        write_csv(f"{name}.csv", rows)

    payload = json.dumps(datasets, ensure_ascii=False, separators=(",", ":"))
    PREVIEW_DATA.write_text(f"window.RETAIL_IQ_DATA={payload};\n", encoding="utf-8")
    print(f"Generated {len(datasets)} evidence-backed extracts in {OUTPUT}")


if __name__ == "__main__":
    main()
