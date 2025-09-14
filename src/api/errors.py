# src/api/errors.py
from __future__ import annotations

import logging
import uuid
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger("api.errors")


def _get_request_id(request: Request) -> str:
    """
    Ensure a request id exists for the current request.
    Prefer request.state.request_id (set by middleware), then header, else generate one.
    """
    rid = getattr(request.state, "request_id", None)
    if not rid:
        rid = request.headers.get("X-Request-ID") or uuid.uuid4().hex
        request.state.request_id = rid
    return rid


def _envelope(
    *,
    request_id: str,
    type_: str,
    title: str,
    detail: str,
    status_code: int,
    extra: dict[str, Any] | None = None,
) -> JSONResponse:
    body: dict[str, Any] = {
        "error": {
            "type": type_,  # e.g. "validation_error", "http_error", "internal_server_error"
            "title": title,
            "detail": detail,
            "request_id": request_id,
        }
    }
    if extra:
        body["error"]["extra"] = extra
    resp = JSONResponse(status_code=status_code, content=body)
    resp.headers["X-Request-ID"] = request_id
    return resp


async def on_http_exception(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """
    Handles FastAPI/Starlette HTTPException.
    4xx -> type "http_error"
    5xx -> type "internal_server_error" (to satisfy tests/ops expectations)
    """
    rid = _get_request_id(request)
    type_ = "internal_server_error" if exc.status_code >= 500 else "http_error"
    title = "HTTP Error" if isinstance(exc.detail, dict) else str(exc.detail)
    logger.warning("http_error", exc_info=exc)
    return _envelope(
        request_id=rid,
        type_=type_,
        title=title,
        detail=title,
        status_code=exc.status_code,
    )


async def on_validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
    """422 validation errors from request parsing."""
    rid = _get_request_id(request)
    logger.info("validation_error", extra={"errors": exc.errors()})
    return _envelope(
        request_id=rid,
        type_="validation_error",
        title="Validation Error",
        detail="Request payload is invalid.",
        status_code=422,
        extra={"errors": exc.errors()},
    )


async def on_unhandled(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all for unexpected exceptions."""
    rid = _get_request_id(request)
    logger.exception("unhandled_error")
    return _envelope(
        request_id=rid,
        type_="internal_server_error",
        title="Internal Server Error",
        detail="An unexpected error occurred.",
        status_code=500,
    )


def install_error_handlers(app: FastAPI) -> None:
    """
    Register global exception handlers.
    Import and call this from app startup (before mounting routers).
    """
    app.add_exception_handler(StarletteHTTPException, on_http_exception)
    app.add_exception_handler(RequestValidationError, on_validation_error)
    app.add_exception_handler(Exception, on_unhandled)
