"""Standard API exceptions and generated-at response handlers."""

from datetime import UTC, datetime

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


class APIError(Exception):
    """Known client-facing API failure with a stable machine code."""

    def __init__(self, status_code: int, code: str, detail: str) -> None:
        super().__init__(detail)
        self.status_code = status_code
        self.code = code
        self.detail = detail


def utc_now_iso() -> str:
    """Return an ISO-8601 UTC timestamp for response envelopes."""
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def install_exception_handlers(application: FastAPI) -> None:
    """Install binding generated-at error envelopes."""

    @application.exception_handler(APIError)
    async def api_error_handler(_: Request, exc: APIError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "generated_at": utc_now_iso(),
                "detail": exc.detail,
                "code": exc.code,
            },
        )

    @application.exception_handler(RequestValidationError)
    async def validation_error_handler(
        _: Request, exc: RequestValidationError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={
                "generated_at": utc_now_iso(),
                "detail": str(exc),
                "code": "validation_error",
            },
        )

    @application.exception_handler(StarletteHTTPException)
    async def http_error_handler(
        _: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        detail = str(exc.detail)
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "generated_at": utc_now_iso(),
                "detail": detail,
                "code": "http_error",
            },
        )
