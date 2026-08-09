"""Idempotently bootstrap the first administrator from environment secrets."""

import asyncio

from app.core.config import get_settings
from app.core.security import hash_password
from app.etl.database import connect


async def seed_admin() -> None:
    settings = get_settings()
    connection = await connect()
    try:
        count = await connection.fetchval("SELECT count(*) FROM curated.users")
        if count:
            return
        if not settings.admin_email or not settings.admin_password:
            raise RuntimeError(
                "ADMIN_EMAIL and ADMIN_PASSWORD are required "
                "when curated.users is empty"
            )
        await connection.execute(
            """INSERT INTO curated.users
                   (email, hashed_password, full_name, role, is_active)
               VALUES (lower($1), $2, 'Retail IQ Administrator', 'admin', true)""",
            settings.admin_email,
            hash_password(settings.admin_password),
        )
        print(f"Seeded administrator: {settings.admin_email}")
    finally:
        await connection.close()


if __name__ == "__main__":
    asyncio.run(seed_admin())
