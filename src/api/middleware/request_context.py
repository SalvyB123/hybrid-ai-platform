# src/api/middleware/request_context.py
from __future__ import annotations

import logging
from collections.abc import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("api.access")


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = getattr(request.state, "request_id", None)
        try:
            response = await call_next(request)
            logger.info(
                "request",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": getattr(response, "status_code", None),
                },
            )
            return response
        except Exception as e:  # noqa: PIE786
            # 🔒 Ensure extras are JSON-serializable
            logger.exception(
                "request_error",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "error_type": e.__class__.__name__,
                    "error_message": str(e),
                },
            )
            raise
