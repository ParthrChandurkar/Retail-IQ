"""Generate reproducible pre-clean and post-clean Markdown quality reports."""

import os
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

import asyncpg

from app.core.config import get_settings
from app.etl.constants import DATASETS
from app.etl.database import connect

OUTLIER_QUERIES = {
    "price": "SELECT price AS value FROM raw.order_items WHERE price IS NOT NULL",
    "freight_value": (
        "SELECT freight_value AS value FROM raw.order_items "
        "WHERE freight_value IS NOT NULL"
    ),
    "payment_value": (
        "SELECT payment_value AS value FROM raw.order_payments "
        "WHERE payment_value IS NOT NULL"
    ),
    "delivery_days": """
        SELECT FLOOR(EXTRACT(EPOCH FROM (
            order_delivered_customer_date - order_purchase_timestamp
        )) / 86400)::INTEGER AS value
        FROM raw.orders
        WHERE order_delivered_customer_date IS NOT NULL
          AND order_purchase_timestamp IS NOT NULL
          AND order_delivered_customer_date >= order_purchase_timestamp
    """,
}


def _format_number(value: object) -> str:
    if value is None:
        return "N/A"
    if isinstance(value, (float, Decimal)):
        return f"{float(value):,.4f}"
    if isinstance(value, int):
        return f"{value:,}"
    return str(value)


def _report_header(title: str, raw_counts: dict[str, int]) -> list[str]:
    generated_at = datetime.now(UTC).isoformat()
    commit_reference = os.getenv("GIT_COMMIT", "working-tree")
    counts = ", ".join(f"{name}={count:,}" for name, count in raw_counts.items())
    return [
        f"# {title}",
        "",
        f"- **Generated at:** `{generated_at}`",
        f"- **Code/commit reference:** `{commit_reference}`",
        f"- **Dataset row counts used:** {counts}",
        "",
    ]


async def _raw_counts(connection: asyncpg.Connection) -> dict[str, int]:
    return {
        spec.table_name: int(
            await connection.fetchval(f'SELECT COUNT(*) FROM raw."{spec.table_name}"')
        )
        for spec in DATASETS
    }


async def _null_metrics(connection: asyncpg.Connection) -> list[tuple[str, int, float]]:
    metrics: list[tuple[str, int, float]] = []
    for spec in DATASETS:
        total = int(
            await connection.fetchval(f'SELECT COUNT(*) FROM raw."{spec.table_name}"')
        )
        for column, _ in spec.columns:
            null_count = int(
                await connection.fetchval(
                    f'SELECT COUNT(*) FROM raw."{spec.table_name}" '
                    f'WHERE "{column}" IS NULL'
                )
            )
            null_pct = (null_count / total * 100) if total else 0.0
            metrics.append((f"raw.{spec.table_name}.{column}", null_count, null_pct))
    return metrics


async def _duplicate_metrics(
    connection: asyncpg.Connection,
) -> list[tuple[str, str, int]]:
    metrics: list[tuple[str, str, int]] = []
    for spec in DATASETS:
        if not spec.grain:
            metrics.append((f"raw.{spec.table_name}", "source has no unique grain", 0))
            continue
        grain = ", ".join(f'"{column}"' for column in spec.grain)
        duplicate_extras = int(
            await connection.fetchval(
                f"SELECT COALESCE(SUM(group_count - 1), 0) FROM ("
                f'SELECT COUNT(*) AS group_count FROM raw."{spec.table_name}" '
                f"GROUP BY {grain} HAVING COUNT(*) > 1) AS duplicates"
            )
        )
        metrics.append(
            (f"raw.{spec.table_name}", ", ".join(spec.grain), duplicate_extras)
        )
    return metrics


async def _orphan_metrics(connection: asyncpg.Connection) -> list[tuple[str, int]]:
    checks = {
        "orders.customer_id → customers.customer_id": """
            SELECT COUNT(*) FROM raw.orders child
            LEFT JOIN raw.customers parent ON parent.customer_id = child.customer_id
            WHERE child.customer_id IS NOT NULL AND parent.customer_id IS NULL
        """,
        "order_items.order_id → orders.order_id": """
            SELECT COUNT(*) FROM raw.order_items child
            LEFT JOIN raw.orders parent ON parent.order_id = child.order_id
            WHERE child.order_id IS NOT NULL AND parent.order_id IS NULL
        """,
        "order_items.product_id → products.product_id": """
            SELECT COUNT(*) FROM raw.order_items child
            LEFT JOIN raw.products parent ON parent.product_id = child.product_id
            WHERE child.product_id IS NOT NULL AND parent.product_id IS NULL
        """,
        "order_items.seller_id → sellers.seller_id": """
            SELECT COUNT(*) FROM raw.order_items child
            LEFT JOIN raw.sellers parent ON parent.seller_id = child.seller_id
            WHERE child.seller_id IS NOT NULL AND parent.seller_id IS NULL
        """,
        "order_payments.order_id → orders.order_id": """
            SELECT COUNT(*) FROM raw.order_payments child
            LEFT JOIN raw.orders parent ON parent.order_id = child.order_id
            WHERE child.order_id IS NOT NULL AND parent.order_id IS NULL
        """,
        "order_reviews.order_id → orders.order_id": """
            SELECT COUNT(*) FROM raw.order_reviews child
            LEFT JOIN raw.orders parent ON parent.order_id = child.order_id
            WHERE child.order_id IS NOT NULL AND parent.order_id IS NULL
        """,
    }
    return [
        (label, int(await connection.fetchval(query)))
        for label, query in checks.items()
    ]


async def _tukey_metrics(
    connection: asyncpg.Connection,
) -> list[tuple[str, float, float, float, float, float, int, float]]:
    metrics: list[tuple[str, float, float, float, float, float, int, float]] = []
    for label, values_query in OUTLIER_QUERIES.items():
        row = await connection.fetchrow(
            f"""
            WITH values AS ({values_query}), quartiles AS (
                SELECT
                    percentile_cont(0.25) WITHIN GROUP (ORDER BY value) AS q1,
                    percentile_cont(0.75) WITHIN GROUP (ORDER BY value) AS q3
                FROM values
            ), bounds AS (
                SELECT q1, q3, q3 - q1 AS iqr,
                       q1 - 1.5 * (q3 - q1) AS lower_bound,
                       q3 + 1.5 * (q3 - q1) AS upper_bound
                FROM quartiles
            )
            SELECT bounds.*,
                   COUNT(*) FILTER (
                       WHERE value < lower_bound OR value > upper_bound
                   ) AS flagged,
                   COUNT(*) AS total
            FROM values CROSS JOIN bounds
            GROUP BY q1, q3, iqr, lower_bound, upper_bound
            """
        )
        if row is None:
            continue
        total = int(row[6])
        flagged = int(row[5])
        metrics.append(
            (
                label,
                float(row[0]),
                float(row[1]),
                float(row[2]),
                float(row[3]),
                float(row[4]),
                flagged,
                flagged / total * 100 if total else 0.0,
            )
        )
    return metrics


def _write_report(filename: str, lines: list[str]) -> Path:
    report_dir = get_settings().report_dir.resolve()
    report_dir.mkdir(parents=True, exist_ok=True)
    path = report_dir / filename
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return path


async def generate_pre_clean_report() -> Path:
    """Generate source-layer quality evidence immediately after ingestion."""
    connection = await connect()
    try:
        raw_counts = await _raw_counts(connection)
        nulls = await _null_metrics(connection)
        duplicates = await _duplicate_metrics(connection)
        orphans = await _orphan_metrics(connection)
        outliers = await _tukey_metrics(connection)
    finally:
        await connection.close()

    lines = _report_header("Data Quality Report — Pre-Clean", raw_counts)
    lines.extend(
        [
            "## Source row counts",
            "",
            "| Raw table | Actual rows | SRS approximate rows | Difference |",
            "|---|---:|---:|---:|",
        ]
    )
    for spec in DATASETS:
        actual = raw_counts[spec.table_name]
        lines.append(
            f"| `raw.{spec.table_name}` | {actual:,} | {spec.approximate_rows:,} "
            f"| {actual - spec.approximate_rows:+,} |"
        )

    lines.extend(
        [
            "",
            "## Column null rates",
            "",
            "| Column | Null count | Null percentage |",
            "|---|---:|---:|",
        ]
    )
    lines.extend(
        f"| `{column}` | {count:,} | {percentage:.4f}% |"
        for column, count, percentage in nulls
    )

    lines.extend(
        [
            "",
            "## Duplicate rates at declared grain",
            "",
            "| Raw table | Declared grain | Duplicate extra rows |",
            "|---|---|---:|",
        ]
    )
    lines.extend(
        f"| `{table}` | {grain} | {count:,} |" for table, grain, count in duplicates
    )

    lines.extend(
        [
            "",
            "## Referential-integrity risks",
            "",
            "| Relationship | Orphan rows |",
            "|---|---:|",
        ]
    )
    lines.extend(f"| {label} | {count:,} |" for label, count in orphans)

    lines.extend(
        [
            "",
            "## Global Tukey outlier candidates",
            "",
            "These are diagnostic flags only. No source row is deleted.",
            "",
            "| Field | Q1 | Q3 | IQR | Lower | Upper | Flagged | Flagged % |",
            "|---|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for label, q1, q3, iqr, lower, upper, flagged, percentage in outliers:
        lines.append(
            f"| `{label}` | {q1:.4f} | {q3:.4f} | {iqr:.4f} | "
            f"{lower:.4f} | {upper:.4f} | {flagged:,} | {percentage:.4f}% |"
        )

    return _write_report("data_quality_report_pre_clean.md", lines)


async def _curated_counts(connection: asyncpg.Connection) -> dict[str, int]:
    table_names = (
        "customers",
        "orders",
        "order_items",
        "products",
        "sellers",
        "payment_details",
        "payment_summary",
        "reviews",
        "users",
        "refresh_tokens",
        "admin_settings",
        "data_refresh_log",
    )
    return {
        name: int(await connection.fetchval(f'SELECT COUNT(*) FROM curated."{name}"'))
        for name in table_names
    }


async def generate_post_clean_report() -> Path:
    """Generate curated-layer validation and a quantified cleaning diff."""
    connection = await connect()
    try:
        raw_counts = await _raw_counts(connection)
        curated_counts = await _curated_counts(connection)
        duplicates = await _duplicate_metrics(connection)
        outliers = await _tukey_metrics(connection)
        unmatched_customers = int(
            await connection.fetchval(
                """
                SELECT COUNT(*) FROM curated.customers
                WHERE zip_code_prefix IS NOT NULL AND latitude IS NULL
                """
            )
        )
        unmatched_sellers = int(
            await connection.fetchval(
                """
                SELECT COUNT(*) FROM curated.sellers
                WHERE zip_code_prefix IS NOT NULL AND latitude IS NULL
                """
            )
        )
        review_duplicate_groups = int(
            await connection.fetchval(
                """
                SELECT COUNT(*) FROM (
                    SELECT review_id FROM curated.reviews
                    GROUP BY review_id HAVING COUNT(*) > 1
                ) groups
                """
            )
        )
        inconsistent_review_groups = int(
            await connection.fetchval(
                """
                SELECT COUNT(*) FROM (
                    SELECT review_id
                    FROM curated.reviews
                    GROUP BY review_id
                    HAVING COUNT(DISTINCT review_score) > 1
                        OR COUNT(DISTINCT COALESCE(comment_title, '<NULL>')) > 1
                        OR COUNT(DISTINCT COALESCE(comment_message, '<NULL>')) > 1
                ) anomalies
                """
            )
        )
        flag_counts = {
            "delivery_days": int(
                await connection.fetchval(
                    "SELECT COUNT(*) FROM curated.orders "
                    "WHERE is_delivery_days_outlier IS TRUE"
                )
            ),
            "price": int(
                await connection.fetchval(
                    "SELECT COUNT(*) FROM curated.order_items WHERE is_price_outlier"
                )
            ),
            "freight_value": int(
                await connection.fetchval(
                    "SELECT COUNT(*) FROM curated.order_items "
                    "WHERE is_freight_value_outlier"
                )
            ),
            "payment_value": int(
                await connection.fetchval(
                    "SELECT COUNT(*) FROM curated.payment_details "
                    "WHERE is_payment_value_outlier"
                )
            ),
        }
        invalid_metrics = {
            "Customers missing required identifiers": int(
                await connection.fetchval(
                    """
                    SELECT COUNT(*) FROM raw.customers
                    WHERE customer_id IS NULL OR customer_unique_id IS NULL
                    """
                )
            ),
            "Orders missing required fields": int(
                await connection.fetchval(
                    """
                    SELECT COUNT(*) FROM raw.orders
                    WHERE order_id IS NULL OR customer_id IS NULL
                       OR order_status IS NULL OR order_purchase_timestamp IS NULL
                    """
                )
            ),
            "Orders with delivery before purchase": int(
                await connection.fetchval(
                    """
                    SELECT COUNT(*) FROM raw.orders
                    WHERE order_delivered_customer_date IS NOT NULL
                      AND order_purchase_timestamp IS NOT NULL
                      AND order_delivered_customer_date < order_purchase_timestamp
                    """
                )
            ),
            "Order items with missing required fields or negative values": int(
                await connection.fetchval(
                    """
                    SELECT COUNT(*) FROM raw.order_items
                    WHERE order_id IS NULL OR order_item_id IS NULL
                       OR product_id IS NULL OR seller_id IS NULL
                       OR price IS NULL OR freight_value IS NULL
                       OR price < 0 OR freight_value < 0
                    """
                )
            ),
            "Payments with missing required fields or impossible values": int(
                await connection.fetchval(
                    """
                    SELECT COUNT(*) FROM raw.order_payments
                    WHERE order_id IS NULL OR payment_sequential IS NULL
                       OR payment_type IS NULL OR payment_value IS NULL
                       OR payment_value < 0 OR payment_installments < 0
                    """
                )
            ),
            "Reviews with missing required fields or invalid score": int(
                await connection.fetchval(
                    """
                    SELECT COUNT(*) FROM raw.order_reviews
                    WHERE review_id IS NULL OR order_id IS NULL
                       OR review_score IS NULL OR review_score NOT BETWEEN 1 AND 5
                    """
                )
            ),
        }
    finally:
        await connection.close()

    source_to_curated = (
        ("customers", "customers", "required-key validation and grain deduplication"),
        ("orders", "orders", "required fields, valid customer FK, timestamp ordering"),
        (
            "order_items",
            "order_items",
            "required fields, non-negative values, valid FKs",
        ),
        ("products", "products", "required product_id and grain deduplication"),
        ("sellers", "sellers", "required seller_id and grain deduplication"),
        (
            "order_payments",
            "payment_details",
            "required fields, non-negative values, valid order FK",
        ),
        ("order_reviews", "reviews", "composite grain, score range, valid order FK"),
    )

    lines = _report_header("Data Quality Report — Post-Clean", raw_counts)
    lines.extend(
        [
            "## Curated row counts",
            "",
            "| Curated table | Rows |",
            "|---|---:|",
        ]
    )
    lines.extend(
        f"| `curated.{name}` | {count:,} |" for name, count in curated_counts.items()
    )

    lines.extend(
        [
            "",
            "## Cleaning diff",
            "",
            "| Source → curated | Raw rows | Curated rows | Rows removed | Rationale |",
            "|---|---:|---:|---:|---|",
        ]
    )
    for raw_name, curated_name, rationale in source_to_curated:
        raw_count = raw_counts[raw_name]
        curated_count = curated_counts[curated_name]
        lines.append(
            f"| `raw.{raw_name}` → `curated.{curated_name}` | {raw_count:,} | "
            f"{curated_count:,} | {max(raw_count - curated_count, 0):,} | {rationale} |"
        )
    lines.append(
        f"| payment detail → `curated.payment_summary` | "
        f"{curated_counts['payment_details']:,} | {curated_counts['payment_summary']:,} | "
        f"{curated_counts['payment_details'] - curated_counts['payment_summary']:,} | "
        "aggregated to one row per order |"
    )

    lines.extend(
        [
            "",
            "### Invalid-data handling",
            "",
            "Invalid rows are excluded only when they violate the binding curated "
            "contract. Optional nulls are retained.",
            "",
            "| Invalid category | Rows detected | Rows dropped | Values corrected |",
            "|---|---:|---:|---:|",
        ]
    )
    lines.extend(
        f"| {category} | {count:,} | {count:,} | 0 |"
        for category, count in invalid_metrics.items()
    )

    lines.extend(
        [
            "",
            "### Duplicate handling",
            "",
            "| Raw table | Grain | Duplicate extra rows removed |",
            "|---|---|---:|",
        ]
    )
    lines.extend(
        f"| `{table}` | {grain} | {count:,} |" for table, grain, count in duplicates
    )

    lines.extend(
        [
            "",
            "### Values imputed or enriched",
            "",
            "| Category | Count | Rationale |",
            "|---|---:|---|",
            "| Source values imputed | 0 | Optional source nulls are retained; no value is fabricated. |",
            f"| Customer ZIP prefixes without geolocation match | {unmatched_customers:,} | Coordinates remain NULL. |",
            f"| Seller ZIP prefixes without geolocation match | {unmatched_sellers:,} | Coordinates remain NULL. |",
            "| Matched coordinates | See curated non-null coordinates | Independent median latitude/longitude per ZIP prefix. |",
            "",
            "### Review duplicate consistency",
            "",
            f"- Duplicate `review_id` groups preserved across orders: **{review_duplicate_groups:,}**",
            f"- Groups with inconsistent score/title/message: **{inconsistent_review_groups:,}**",
            "- Review-grain downstream analysis must use one deterministic row per `review_id`.",
            "",
            "## Retained outlier flags",
            "",
            "All flagged rows remain in curated tables. Price/freight Q1–Q3 columns "
            "show the Phase 2 global baseline; their persisted counts use the "
            "category-conditional bounds authorized by the material Phase 3 EDA "
            "follow-up. Delivery and payment remain global.",
            "",
            "| Field | Q1 | Q3 | IQR | Lower | Upper | Flagged | Flagged % | Persisted flag count |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for label, q1, q3, iqr, lower, upper, flagged, percentage in outliers:
        lines.append(
            f"| `{label}` | {q1:.4f} | {q3:.4f} | {iqr:.4f} | {lower:.4f} "
            f"| {upper:.4f} | {flagged:,} | {percentage:.4f}% | "
            f"{flag_counts[label]:,} |"
        )

    return _write_report("data_quality_report_post_clean.md", lines)
