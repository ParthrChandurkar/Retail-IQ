"""JWT authentication routes."""

from typing import Annotated

from fastapi import APIRouter, Cookie, Response

from app.core.config import get_settings
from app.core.dependencies import CurrentUser
from app.schemas.auth import LoginRequest, TokenPayload, UserPublic
from app.schemas.common import DataResponse
from app.services.auth_service import login, rotate

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


def _set_refresh_cookie(response: Response, token: str) -> None:
    settings = get_settings()
    response.set_cookie(
        "refresh_token",
        token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=settings.jwt_refresh_expire_days * 86400,
        path="/api/v1/auth",
    )


@router.post("/login", response_model=DataResponse[TokenPayload])
async def login_route(
    body: LoginRequest, response: Response
) -> DataResponse[TokenPayload]:
    payload, refresh_token = await login(body.email, body.password)
    _set_refresh_cookie(response, refresh_token)
    return DataResponse(data=TokenPayload.model_validate(payload))


@router.post("/refresh", response_model=DataResponse[TokenPayload])
async def refresh_route(
    response: Response,
    refresh_token: Annotated[str | None, Cookie()] = None,
) -> DataResponse[TokenPayload]:
    payload, replacement = await rotate(refresh_token)
    _set_refresh_cookie(response, replacement)
    return DataResponse(data=TokenPayload.model_validate(payload))


@router.get("/me", response_model=DataResponse[UserPublic])
async def me_route(user: CurrentUser) -> DataResponse[UserPublic]:
    return DataResponse(data=UserPublic.model_validate(user))
