"""Orchestrate the complete Phase 2 ETL sequence."""

import asyncio
import json
from datetime import UTC, datetime

from app.etl.clean import clean_curated
from app.etl.database import connect
from app.etl.ingest import ingest_raw
from app.etl.quality import generate_post_clean_report, generate_pre_clean_report


async def _start_log() -> int:
    connection = await connect()
    try:
        now = datetime.now(UTC).replace(tzinfo=None)
        await connection.execute(
            """
            UPDATE curated.data_refresh_log
            SET finished_at = $1,
                status = 'failed',
                error_message = 'Superseded after an unclean ETL shutdown'
            WHERE job_name = 'etl' AND status = 'running'
            """,
            now,
        )
        return int(
            await connection.fetchval(
                """
                INSERT INTO curated.data_refresh_log (job_name, started_at, status)
                VALUES ('etl', $1, 'running')
                RETURNING id
                """,
                now,
            )
        )
    finally:
        await connection.close()


async def _finish_log(
    log_id: int, *, status: str, rows_affected: int | None, error_message: str | None
) -> None:
    connection = await connect()
    try:
        await connection.execute(
            """
            UPDATE curated.data_refresh_log
            SET finished_at = $1,
                status = $2,
                rows_affected = $3,
                error_message = $4
            WHERE id = $5
            """,
            datetime.now(UTC).replace(tzinfo=None),
            status,
            rows_affected,
            error_message,
            log_id,
        )
    finally:
        await connection.close()


async def run_etl() -> None:
    """Run ingestion, pre-clean report, cleaning, and post-clean report in order."""
    log_id = await _start_log()
    try:
        raw_counts = await ingest_raw()
        pre_report = await generate_pre_clean_report()
        curated_counts = await clean_curated()
        post_report = await generate_post_clean_report()
        rows_affected = sum(raw_counts.values()) + sum(curated_counts.values())
        await _finish_log(
            log_id,
            status="success",
            rows_affected=rows_affected,
            error_message=None,
        )
    except Exception as exc:
        await _finish_log(
            log_id,
            status="failed",
            rows_affected=None,
            error_message=str(exc),
        )
        raise

    print("RAW_COUNTS=" + json.dumps(raw_counts, sort_keys=True))
    print("CURATED_COUNTS=" + json.dumps(curated_counts, sort_keys=True))
    print(f"PRE_CLEAN_REPORT={pre_report}")
    print(f"POST_CLEAN_REPORT={post_report}")


if __name__ == "__main__":
    asyncio.run(run_etl())
