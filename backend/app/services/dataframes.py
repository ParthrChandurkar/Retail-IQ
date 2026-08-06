"""Small asyncpg-to-Pandas adapter shared by analytics services."""

from datetime import date, datetime
from decimal import Decimal
from typing import Any

import pandas as pd

from app.etl.database import connect


async def query_frame(sql: str, *args: object) -> pd.DataFrame:
    """Execute a read-only query and return a DataFrame with stable columns."""
    connection = await connect()
    try:
        statement = await connection.prepare(sql)
        records = await statement.fetch(*args)
        columns = [attribute.name for attribute in statement.get_attributes()]
        return pd.DataFrame([tuple(record) for record in records], columns=columns)
    finally:
        await connection.close()


def json_safe(value: Any) -> Any:
    """Convert Pandas/Numpy scalars and missing values for JSON/report output."""
    if pd.isna(value):
        return None
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if hasattr(value, "item"):
        return value.item()
    return value
