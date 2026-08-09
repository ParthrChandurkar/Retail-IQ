"""Small asyncpg query layer shared by Phase 5 API services."""

from collections.abc import Sequence
from typing import Any, cast

from app.etl.database import connect


async def fetch_all(query: str, *values: object) -> list[dict[str, Any]]:
    connection = await connect()
    try:
        return [dict(row) for row in await connection.fetch(query, *values)]
    finally:
        await connection.close()


async def fetch_one(query: str, *values: object) -> dict[str, Any] | None:
    connection = await connect()
    try:
        row = await connection.fetchrow(query, *values)
        return dict(row) if row else None
    finally:
        await connection.close()


async def execute(query: str, *values: object) -> str:
    connection = await connect()
    try:
        return cast(str, await connection.execute(query, *values))
    finally:
        await connection.close()


def where_clause(
    filters: object,
    supported: Sequence[str],
    *,
    aliases: dict[str, str] | None = None,
) -> tuple[str, list[object]]:
    """Build a parameterized WHERE clause from validated shared filters."""
    from app.core.errors import APIError

    aliases = aliases or {}
    values: list[object] = []
    clauses: list[str] = []
    for name in (
        "date_from",
        "date_to",
        "state",
        "city",
        "category",
        "seller_id",
        "payment_type",
        "customer_segment",
        "review_score_min",
        "review_score_max",
    ):
        value = getattr(filters, name, None)
        if value is None:
            continue
        if name not in supported:
            raise APIError(
                400,
                "unsupported_filter",
                f"Filter '{name}' is not supported by this endpoint.",
            )
        column = aliases.get(name, name)
        operator = (
            ">="
            if name in {"date_from", "review_score_min"}
            else "<="
            if name in {"date_to", "review_score_max"}
            else "="
        )
        values.append(value)
        clauses.append(f"{column} {operator} ${len(values)}")
    return (" WHERE " + " AND ".join(clauses) if clauses else "", values)


def pagination_sql(page: int, page_size: int, values: list[object]) -> str:
    values.extend([page_size, (page - 1) * page_size])
    return f" LIMIT ${len(values) - 1} OFFSET ${len(values)}"
