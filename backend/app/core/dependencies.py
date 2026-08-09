"""Authentication and authorization dependencies."""

from typing import Annotated, Any

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.errors import APIError
from app.core.security import InvalidTokenError, decode_access_token
from app.services.auth_service import get_user

bearer = HTTPBearer(auto_error=False)


async def current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
) -> dict[str, Any]:
    if credentials is None:
        raise APIError(401, "not_authenticated", "Bearer access token is required.")
    try:
        claims = decode_access_token(credentials.credentials)
        return await get_user(int(claims["sub"]))
    except (InvalidTokenError, KeyError, ValueError) as exc:
        raise APIError(
            401, "invalid_token", "Access token subject is invalid."
        ) from exc


async def admin_user(
    user: Annotated[dict[str, Any], Depends(current_user)],
) -> dict[str, Any]:
    if user["role"] != "admin":
        raise APIError(403, "admin_required", "Administrator role is required.")
    return user


CurrentUser = Annotated[dict[str, Any], Depends(current_user)]
AdminUser = Annotated[dict[str, Any], Depends(admin_user)]
