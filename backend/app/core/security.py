"""Password hashing, JWT issuance, and opaque refresh-token helpers."""

import hashlib
import secrets
from datetime import UTC, datetime, timedelta
from typing import Any

import bcrypt
from jose import JWTError, jwt

from app.core.config import get_settings

ALGORITHM = "HS256"


class InvalidTokenError(ValueError):
    """Raised when a JWT cannot be verified or lacks required claims."""


def hash_password(password: str) -> str:
    """Hash a password with bcrypt through Passlib."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against its stored bcrypt hash."""
    return bcrypt.checkpw(password.encode(), hashed_password.encode())


def create_access_token(*, user_id: int, email: str, role: str) -> str:
    """Issue a signed access token with the binding Addendum claims."""
    settings = get_settings()
    issued_at = datetime.now(UTC)
    payload: dict[str, Any] = {
        "sub": str(user_id),
        "email": email,
        "role": role,
        "iat": issued_at,
        "exp": issued_at + timedelta(minutes=settings.jwt_access_expire_minutes),
    }
    return str(jwt.encode(payload, settings.jwt_secret, algorithm=ALGORITHM))


def decode_access_token(token: str) -> dict[str, Any]:
    """Verify an access token and return its required claims."""
    try:
        payload = jwt.decode(token, get_settings().jwt_secret, algorithms=[ALGORITHM])
    except JWTError as exc:
        raise InvalidTokenError("Invalid or expired access token") from exc
    required = {"sub", "email", "role", "iat", "exp"}
    if not required.issubset(payload):
        raise InvalidTokenError("Access token is missing required claims")
    return dict(payload)


def create_refresh_token() -> str:
    """Generate a high-entropy opaque refresh token."""
    return secrets.token_urlsafe(48)


def hash_refresh_token(token: str) -> str:
    """Hash an opaque refresh token before persistence."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
