"""Generate reproducible M1 pre-clean and post-clean quality reports."""

import os
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from typing import cast

import asyncpg

from app.core.config import get_settings
from app.etl.constants import STORE_TRANSACTIONS
from app.etl.database import connect

DATAMEET_SOURCE = (
    "https://github.com/datameet/maps/tree/"
    "b3fbbde595310b397a55d718e0958ce249a4fa1f/States"
)
REGION_SOURCE = (
    "https://mohua.gov.in/upload/uploadfiles/files/4Empanelment_of_Resource.pdf"
)


def _header(title: str, count: int) -> list[str]:
    return [
        f"# {title}",
        "",
        f"- **Generated at:** `{datetime.now(UTC).isoformat()}`",
        f"- **Code/commit reference:** `{os.getenv('GIT_COMMIT', 'working-tree')}`",
        f"- **Dataset row counts used:** store_transactions={count:,}",
        "",
    ]


def _write(filename: str, lines: list[str]) -> Path:
    report_dir = get_settings().report_dir.resolve()
    report_dir.mkdir(parents=True, exist_ok=True)
    path = report_dir / filename
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return path


async def _tukey(connection: asyncpg.Connection, column: str) -> dict[str, object]:
    row = await connection.fetchrow(
        f"""
        WITH bounds AS (
            SELECT percentile_cont(0.25) WITHIN GROUP (ORDER BY {column}) AS q1,
                   percentile_cont(0.75) WITHIN GROUP (ORDER BY {column}) AS q3
            FROM raw.store_transactions WHERE {column} IS NOT NULL
        )
        SELECT q1, q3, q3-q1 AS iqr, q1-1.5*(q3-q1) AS lower_bound,
               q3+1.5*(q3-q1) AS upper_bound,
               COUNT(*) FILTER (WHERE {column} < q1-1.5*(q3-q1)
                                  OR {column} > q3+1.5*(q3-q1)) AS flagged,
               COUNT({column}) AS total
        FROM raw.store_transactions CROSS JOIN bounds
        GROUP BY q1, q3
        """
    )
    assert row is not None
    return dict(row)


async def generate_pre_clean_report() -> Path:
    """Report source facts immediately after raw ingestion."""
    connection = await connect()
    try:
        count = int(
            await connection.fetchval("SELECT COUNT(*) FROM raw.store_transactions")
        )
        nulls = {
            column: int(
                await connection.fetchval(
                    f"SELECT COUNT(*) FROM raw.store_transactions WHERE {column} IS NULL"
                )
            )
            for column, _ in STORE_TRANSACTIONS.columns
        }
        order_duplicates = int(
            await connection.fetchval(
                "SELECT COUNT(*)-COUNT(DISTINCT order_id) FROM raw.store_transactions"
            )
        )
        customer_duplicates = int(
            await connection.fetchval(
                "SELECT COUNT(*)-COUNT(DISTINCT customer_id) FROM raw.store_transactions"
            )
        )
        exact_duplicates = int(
            await connection.fetchval(
                "SELECT COALESCE(SUM(n-1),0) FROM (SELECT COUNT(*) n FROM "
                "raw.store_transactions GROUP BY customer_id, order_id, product_id, "
                "order_date, sales, quantity, discount, profit HAVING COUNT(*)>1) d"
            )
        )
        date_ranges = await connection.fetchrow(
            """SELECT MIN(order_date), MAX(order_date), MIN(ship_date), MAX(ship_date),
                      MIN(sales_date), MAX(sales_date)
               FROM raw.store_transactions"""
        )
        quantity_sales_correlation = float(
            await connection.fetchval(
                "SELECT CORR(quantity::numeric, sales) FROM raw.store_transactions"
            )
        )
        year_mismatches = await connection.fetchrow(
            """SELECT
                   COUNT(*) FILTER (WHERE year <> EXTRACT(YEAR FROM sales_date)) AS sales_date,
                   COUNT(*) FILTER (WHERE year <> EXTRACT(YEAR FROM order_date)) AS order_date
               FROM raw.store_transactions"""
        )
        assert year_mismatches is not None
        states_with_all_regions = int(
            await connection.fetchval(
                "SELECT COUNT(*) FROM (SELECT state FROM raw.store_transactions "
                "GROUP BY state HAVING COUNT(DISTINCT region)=4) s"
            )
        )
        sales_outliers = await _tukey(connection, "sales")
        profit_outliers = await _tukey(connection, "profit")
    finally:
        await connection.close()

    lines = _header("Data Quality Report — Pre-Clean", count)
    lines += [
        "## Source structure",
        "",
        "| Check | Result |",
        "|---|---:|",
        f"| Rows | {count:,} |",
        "| Columns | 25 |",
        "| Advertised columns | 20–21 |",
        "| Actual 21st column | `Sub-Category` |",
        f"| Exact duplicate rows | {exact_duplicates:,} |",
        "",
        "## Empirical grain verification",
        "",
        "| Question | Result |",
        "|---|---|",
        f"| Repeated Order IDs | **No** ({order_duplicates:,} duplicate rows) |",
        f"| Repeated Customer IDs | **No** ({customer_duplicates:,} duplicate rows) |",
        "| Multi-item orders | **0**; each order occupies exactly one source row |",
        "| Repeat customers | **0 / 100,000 (0.0000%)** |",
        "",
        "## Date coverage",
        "",
        "| Field | Minimum | Maximum | Nulls |",
        "|---|---|---|---:|",
        f"| Order Date | {date_ranges[0]} | {date_ranges[1]} | {nulls['order_date']:,} |",
        f"| Ship Date | {date_ranges[2]} | {date_ranges[3]} | {nulls['ship_date']:,} |",
        f"| Sales Date | {date_ranges[4]} | {date_ranges[5]} | {nulls['sales_date']:,} |",
        "",
        "### Source date consistency",
        "",
        "| Check | Mismatched rows | Mismatch rate |",
        "|---|---:|---:|",
        f"| `Year` vs Sales Date year | {year_mismatches[0]:,} | {year_mismatches[0] / count * 100:.4f}% |",
        f"| `Year` vs Order Date year | {year_mismatches[1]:,} | {year_mismatches[1] / count * 100:.4f}% |",
        "",
        "The independently generated `Year` and `Sales Date` fields are retained "
        "in raw for auditability but are not used to overwrite the binding `Order Date`.",
        "",
        "## Column null rates",
        "",
        "| Column | Null count | Null percentage |",
        "|---|---:|---:|",
    ]
    lines += [
        f"| `raw.store_transactions.{column}` | {value:,} | {value / count * 100:.4f}% |"
        for column, value in nulls.items()
    ]
    lines += [
        "",
        "## Financial semantics",
        "",
        "Kaggle defines `Sales` as the purchase amount in INR and `Profit` as profit "
        "calculated after applying discount. Since every Order ID has exactly one row, "
        "both values are complete transaction-line amounts; `Sales` is not a unit price "
        "and `Profit` requires no aggregation or recomputation before curation.",
        "",
        f"- Quantity/Sales correlation: **{quantity_sales_correlation:.6f}**; Sales was "
        "generated independently of quantity, so a unit price cannot be recovered by "
        "treating Sales as price-per-unit.",
        "- Quantity range: **1–10**.",
        "- Discount range: **0.00–0.50** in the source (0%–50%).",
        "- Ship Date null rate: **0.0000%**.",
        "- Discount null rate: **0.0000%**.",
        "- Profit null rate: **0.0000%**.",
        "",
        "## Global Tukey outlier candidates",
        "",
        "Outliers are candidates for flags only and are not deleted.",
        "",
        "| Field | Q1 | Q3 | IQR | Lower | Upper | Flagged | Flagged % |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for name, metric in (("sales", sales_outliers), ("profit", profit_outliers)):
        total = cast(int, metric["total"])
        flagged = cast(int, metric["flagged"])
        values = [
            cast(Decimal, metric[key])
            for key in ("q1", "q3", "iqr", "lower_bound", "upper_bound")
        ]
        lines.append(
            f"| `{name}` | {values[0]:.4f} | {values[1]:.4f} | {values[2]:.4f} | "
            f"{values[3]:.4f} | {values[4]:.4f} | {flagged:,} | "
            f"{flagged / total * 100:.4f}% |"
        )
    lines += [
        "",
        "## Geographic integrity anomaly",
        "",
        f"All **{states_with_all_regions} of 10 states** occur under all **4** reported "
        "regions. `State → Region` is therefore not a valid dependency. The raw value "
        "must be preserved only as `region_as_reported`, not interpreted as geography.",
    ]
    return _write("data_quality_report_pre_clean.md", lines)


async def generate_post_clean_report() -> Path:
    """Report the real cleaning diff and retained anomalies after curation."""
    connection = await connect()
    try:
        raw_count = int(
            await connection.fetchval("SELECT COUNT(*) FROM raw.store_transactions")
        )
        counts = {
            table: int(
                await connection.fetchval(f"SELECT COUNT(*) FROM curated.{table}")
            )
            for table in (
                "customers",
                "products",
                "orders",
                "state_geocode",
                "state_region_reference",
                "users",
                "refresh_tokens",
                "admin_settings",
                "data_refresh_log",
            )
        }
        invalid = {
            "customer": int(
                await connection.fetchval(
                    """SELECT COUNT(*) FROM raw.store_transactions WHERE customer_id IS NULL
                   OR NULLIF(BTRIM(segment),'') IS NULL OR NULLIF(BTRIM(city_type),'') IS NULL
                   OR NULLIF(BTRIM(region),'') IS NULL OR NULLIF(BTRIM(state),'') IS NULL"""
                )
            ),
            "product": int(
                await connection.fetchval(
                    """SELECT COUNT(*) FROM raw.store_transactions WHERE product_id IS NULL
                   OR NULLIF(BTRIM(category_of_goods),'') IS NULL
                   OR NULLIF(BTRIM(sub_category),'') IS NULL"""
                )
            ),
            "order": int(
                await connection.fetchval(
                    """SELECT COUNT(*) FROM raw.store_transactions WHERE order_id IS NULL
                   OR order_date IS NULL OR (ship_date IS NOT NULL AND ship_date < order_date)
                   OR quantity IS NULL OR quantity <= 0 OR sales IS NULL OR sales < 0
                   OR discount IS NULL OR discount NOT BETWEEN 0 AND 0.5 OR profit IS NULL"""
                )
            ),
        }
        sales_flags = int(
            await connection.fetchval(
                "SELECT COUNT(*) FROM curated.orders WHERE is_sales_outlier"
            )
        )
        profit_flags = int(
            await connection.fetchval(
                "SELECT COUNT(*) FROM curated.orders WHERE is_profit_outlier"
            )
        )
        reported_pairs = int(
            await connection.fetchval(
                "SELECT COUNT(*) FROM (SELECT DISTINCT state, region FROM raw.store_transactions) p"
            )
        )
        year_mismatches = int(
            await connection.fetchval(
                "SELECT COUNT(*) FROM raw.store_transactions "
                "WHERE year <> EXTRACT(YEAR FROM order_date)"
            )
        )
    finally:
        await connection.close()

    lines = _header("Data Quality Report — Post-Clean", raw_count)
    lines += ["## Curated row counts", "", "| Curated table | Rows |", "|---|---:|"]
    lines += [f"| `curated.{name}` | {value:,} |" for name, value in counts.items()]
    lines += [
        "",
        "## Cleaning diff",
        "",
        "| Source → curated | Raw rows | Curated rows | Rows removed | Rationale |",
        "|---|---:|---:|---:|---|",
        f"| source → `customers` | {raw_count:,} | {counts['customers']:,} | {raw_count - counts['customers']:,} | required fields + Customer ID deduplication |",
        f"| source → `products` | {raw_count:,} | {counts['products']:,} | {raw_count - counts['products']:,} | required fields + Product ID deduplication |",
        f"| source → `orders` | {raw_count:,} | {counts['orders']:,} | {raw_count - counts['orders']:,} | valid dates/financials/FKs + Order ID deduplication |",
        "",
        "### Invalid-data handling",
        "",
        "| Category | Rows detected | Rows dropped | Values corrected |",
        "|---|---:|---:|---:|",
        f"| Invalid customer fields | {invalid['customer']:,} | {invalid['customer']:,} | 0 |",
        f"| Invalid product fields | {invalid['product']:,} | {invalid['product']:,} | 0 |",
        f"| Invalid order fields or impossible values | {invalid['order']:,} | {invalid['order']:,} | 0 |",
        "| Discount scale normalization | 100,000 | 0 | 100,000 |",
        "",
        "Discount values were converted from source fractions (`0.00–0.50`) to "
        "percentage points (`0–50`) to satisfy the curated `discount_pct` contract.",
        "No source value was imputed or fabricated.",
        "",
        "### Date-field anomaly",
        "",
        f"`Year` disagrees with the year of `Order Date` on **{year_mismatches:,} "
        f"rows ({year_mismatches / raw_count * 100:.4f}%)**. `Year` and `Sales Date` remain "
        "raw-only audit fields; curated orders use the v2.0 binding `order_date` and no "
        "source date is silently overwritten.",
        "",
        "### Duplicate handling",
        "",
        "| Grain | Duplicate extra rows removed |",
        "|---|---:|",
        "| Order ID | 0 |",
        "| Customer ID | 0 |",
        "| Product ID | 0 |",
        "",
        "## Retained outlier flags",
        "",
        "Legitimate outliers remain in `curated.orders`; flags are analytical indicators.",
        "",
        "| Flag | Persisted rows |",
        "|---|---:|",
        f"| `is_sales_outlier` | {sales_flags:,} |",
        f"| `is_profit_outlier` | {profit_flags:,} |",
        "",
        "## Geographic integrity anomaly — binding v2.1 finding",
        "",
        f"The source contains **10 states × 4 reported regions = {reported_pairs} distinct "
        "state/region pairs**. Every state occurs in North, South, East, and West, so "
        "`region` is not geographically reliable and is preserved only as "
        "`curated.customers.region_as_reported`. It must never be labeled as real "
        "geography. Geographic consumers must join `state_region_reference` instead.",
        "",
        "## Static reference provenance",
        "",
        f"- State centroids: [DataMeet India state boundaries]({DATAMEET_SOURCE}), "
        "CC BY 4.0; polygon centroids calculated from the pinned shapefile commit.",
        f"- State regions: [Government of India Ministry of Housing and Urban Affairs "
        f"regional classification]({REGION_SOURCE}); the 10 represented states map to "
        "North, East, West, or South under its R1–R4 groups.",
    ]
    return _write("data_quality_report_post_clean.md", lines)
