"""Credential verification and rotating refresh-token persistence."""

from datetime import UTC, datetime, timedelta
from typing import Any

from app.core.config import get_settings
from app.core.errors import APIError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_refresh_token,
    verify_password,
)
from app.etl.database import connect


def _public_user(row: dict[str, Any]) -> dict[str, Any]:
    return {
        key: row[key] for key in ("user_id", "email", "full_name", "role", "is_active")
    }


async def login(email: str, password: str) -> tuple[dict[str, Any], str]:
    connection = await connect()
    try:
        row = await connection.fetchrow(
            "SELECT * FROM curated.users WHERE lower(email) = lower($1)", email
        )
        if (
            row is None
            or not row["is_active"]
            or not verify_password(password, row["hashed_password"])
        ):
            raise APIError(401, "invalid_credentials", "Invalid email or password.")
        return await _issue(connection, dict(row))
    finally:
        await connection.close()


async def _issue(connection: Any, user: dict[str, Any]) -> tuple[dict[str, Any], str]:
    settings = get_settings()
    raw_refresh = create_refresh_token()
    expires_at = datetime.now(UTC).replace(tzinfo=None) + timedelta(
        days=settings.jwt_refresh_expire_days
    )
    await connection.execute(
        "INSERT INTO curated.refresh_tokens (user_id, token_hash, expires_at) VALUES ($1, $2, $3)",
        user["user_id"],
        hash_refresh_token(raw_refresh),
        expires_at,
    )
    access = create_access_token(
        user_id=user["user_id"], email=user["email"], role=user["role"]
    )
    return {
        "access_token": access,
        "token_type": "bearer",
        "expires_in": settings.jwt_access_expire_minutes * 60,
        "user": _public_user(user),
    }, raw_refresh


async def rotate(raw_refresh: str | None) -> tuple[dict[str, Any], str]:
    if not raw_refresh:
        raise APIError(401, "missing_refresh_token", "Refresh cookie is missing.")
    connection = await connect()
    try:
        async with connection.transaction():
            row = await connection.fetchrow(
                """SELECT rt.token_id, u.* FROM curated.refresh_tokens rt
                   JOIN curated.users u ON u.user_id = rt.user_id
                   WHERE rt.token_hash = $1 AND rt.revoked_at IS NULL
                     AND rt.expires_at > now() FOR UPDATE""",
                hash_refresh_token(raw_refresh),
            )
            if row is None or not row["is_active"]:
                raise APIError(
                    401, "invalid_refresh_token", "Refresh token is invalid or expired."
                )
            await connection.execute(
                "UPDATE curated.refresh_tokens SET revoked_at = now() WHERE token_id = $1",
                row["token_id"],
            )
            return await _issue(connection, dict(row))
    finally:
        await connection.close()


async def get_user(user_id: int) -> dict[str, Any]:
    connection = await connect()
    try:
        row = await connection.fetchrow(
            "SELECT user_id,email,full_name,role,is_active FROM curated.users WHERE user_id=$1",
            user_id,
        )
        if row is None or not row["is_active"]:
            raise APIError(401, "invalid_token", "User is unavailable.")
        return dict(row)
    finally:
        await connection.close()
