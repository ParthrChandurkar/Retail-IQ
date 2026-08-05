"""Idempotent row-and-value-faithful loading of source CSVs into raw.*."""

from collections.abc import Iterator
from datetime import datetime
from decimal import Decimal
from pathlib import Path

import asyncpg
import pandas as pd

from app.core.config import get_settings
from app.etl.constants import DATASETS, ColumnKind, DatasetSpec
from app.etl.database import connect
from app.etl.download_data import missing_files

CHUNK_SIZE = 100_000


def convert_value(value: str, kind: ColumnKind) -> object | None:
    """Convert one CSV value to its raw table storage type without correction."""
    if value == "":
        return None
    if kind == "string":
        return value
    if kind == "integer":
        return int(value)
    if kind == "numeric":
        return Decimal(value)
    if kind == "timestamp":
        return datetime.fromisoformat(value)
    raise ValueError(f"Unsupported column kind: {kind}")


def iter_record_chunks(
    path: Path, spec: DatasetSpec
) -> Iterator[list[tuple[object, ...]]]:
    """Yield typed source records in bounded-memory chunks."""
    expected_columns = [column for column, _ in spec.columns]
    for frame in pd.read_csv(
        path,
        dtype=str,
        keep_default_na=False,
        chunksize=CHUNK_SIZE,
        encoding="utf-8",
    ):
        actual_columns = list(frame.columns)
        if actual_columns != expected_columns:
            raise ValueError(
                f"Unexpected columns in {path.name}: {actual_columns}; "
                f"expected {expected_columns}"
            )
        yield [
            tuple(
                convert_value(value, kind)
                for value, (_, kind) in zip(row, spec.columns, strict=True)
            )
            for row in frame.itertuples(index=False, name=None)
        ]


async def load_dataset(
    connection: asyncpg.Connection, data_dir: Path, spec: DatasetSpec
) -> int:
    """Copy one source CSV into its matching raw table."""
    row_count = 0
    columns = [column for column, _ in spec.columns]
    for records in iter_record_chunks(data_dir / spec.filename, spec):
        await connection.copy_records_to_table(
            spec.table_name,
            records=records,
            columns=columns,
            schema_name="raw",
        )
        row_count += len(records)
    return row_count


async def ingest_raw() -> dict[str, int]:
    """Atomically replace all raw tables so repeated runs cannot duplicate data."""
    data_dir = get_settings().data_raw_dir.resolve()
    missing = missing_files(data_dir)
    if missing:
        raise FileNotFoundError(f"Missing required source CSVs: {', '.join(missing)}")

    connection = await connect()
    counts: dict[str, int] = {}
    table_list = ", ".join(f'raw."{spec.table_name}"' for spec in DATASETS)
    try:
        async with connection.transaction():
            await connection.execute(f"TRUNCATE TABLE {table_list}")
            for spec in DATASETS:
                counts[spec.table_name] = await load_dataset(connection, data_dir, spec)
    finally:
        await connection.close()

    return counts
