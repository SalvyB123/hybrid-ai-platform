from __future__ import annotations

import logging
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

logger = logging.getLogger("api.errors")


def _envelope(
    request: Request, status: int, type_: str, message: str, details: Any | None = None
) -> JSONResponse:
    rid = getattr(request.state, "request_id", None)
    body: dict[str, Any] = {
        "error": {
            "type": type_,
            "message": message,
            "request_id": rid,
        }
    }
    if details is not None:
        body["error"]["details"] = details
    return JSONResponse(status_code=status, content=body)


def install_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(HTTPException)
    async def on_http_exc(request: Request, exc: HTTPException):
        logger.warning(
            "http_error",
            extra={
                "request_id": getattr(request.state, "request_id", None),
                "path": request.url.path,
                "status_code": exc.status_code,
            },
        )
        return _envelope(request, exc.status_code, "http_error", exc.detail or "HTTP error")

    @app.exception_handler(RequestValidationError)
    async def on_validation(request: Request, exc: RequestValidationError):
        logger.info(
            "validation_error",
            extra={
                "request_id": getattr(request.state, "request_id", None),
                "path": request.url.path,
                "status_code": 422,
            },
        )
        return _envelope(
            request, 422, "validation_error", "Invalid request payload", details=exc.errors()
        )

    @app.exception_handler(Exception)
    async def on_unhandled(request: Request, exc: Exception):
        logger.exception(
            "unhandled_error",
            extra={
                "request_id": getattr(request.state, "request_id", None),
                "path": request.url.path,
                "status_code": 500,
            },
        )
        # Do not leak internals to clients
        return _envelope(request, 500, "internal_error", "An unexpected error occurred")
