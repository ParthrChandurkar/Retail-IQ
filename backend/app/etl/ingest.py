"""Idempotent, row-faithful ingestion of Indian Store Data into raw.*."""

from collections.abc import Iterator
from datetime import date
from decimal import Decimal
from pathlib import Path

import pandas as pd

from app.core.config import get_settings
from app.etl.constants import (
    SOURCE_HEADERS,
    STORE_TRANSACTIONS,
    ColumnKind,
    DatasetSpec,
)
from app.etl.database import connect
from app.etl.download_data import missing_files

CHUNK_SIZE = 100_000


def convert_value(value: str, kind: ColumnKind) -> object | None:
    """Convert a non-empty CSV value without cleaning or correction."""
    if value == "":
        return None
    if kind == "string":
        return value
    if kind == "integer":
        return int(value)
    if kind == "numeric":
        return Decimal(value)
    if kind == "date":
        return date.fromisoformat(value)
    raise ValueError(f"Unsupported column kind: {kind}")


def iter_record_chunks(
    path: Path, spec: DatasetSpec
) -> Iterator[list[tuple[object, ...]]]:
    """Validate the exact 25-column header and yield bounded typed chunks."""
    for frame in pd.read_csv(
        path, dtype=str, keep_default_na=False, chunksize=CHUNK_SIZE, encoding="utf-8"
    ):
        actual_headers = tuple(frame.columns)
        if actual_headers != SOURCE_HEADERS:
            raise ValueError(
                f"Unexpected columns in {path.name}: {list(actual_headers)}; "
                f"expected {list(SOURCE_HEADERS)}"
            )
        yield [
            tuple(
                convert_value(value, kind)
                for value, (_, kind) in zip(row, spec.columns, strict=True)
            )
            for row in frame.itertuples(index=False, name=None)
        ]


async def ingest_raw() -> dict[str, int]:
    """Atomically replace raw.store_transactions for repeatable ingestion."""
    data_dir = get_settings().data_raw_dir.resolve()
    missing = missing_files(data_dir)
    if missing:
        raise FileNotFoundError(f"Missing required source CSV: {', '.join(missing)}")

    spec = STORE_TRANSACTIONS
    connection = await connect()
    row_count = 0
    try:
        async with connection.transaction():
            await connection.execute("TRUNCATE TABLE raw.store_transactions")
            columns = [name for name, _ in spec.columns]
            for records in iter_record_chunks(data_dir / spec.filename, spec):
                await connection.copy_records_to_table(
                    spec.table_name,
                    records=records,
                    columns=columns,
                    schema_name="raw",
                )
                row_count += len(records)
    finally:
        await connection.close()

    return {spec.table_name: row_count}
