from __future__ import annotations

import logging
import time
import uuid

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

_REQUEST_ID_HEADER = "X-Request-ID"
logger = logging.getLogger("api.access")


class RequestContextMiddleware(BaseHTTPMiddleware):
    """
    - Assigns a request_id for each request.
    - Adds it to response header.
    - Emits structured access logs on completion.
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start = time.perf_counter()
        request_id = request.headers.get(_REQUEST_ID_HEADER) or str(uuid.uuid4())
        # Make request_id accessible to handlers via state
        request.state.request_id = request_id

        try:
            response = await call_next(request)
        except Exception:
            # In case of unhandled exception, we still want to log with request_id
            elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
            logger.exception(
                "request_error",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": 500,
                    "elapsed_ms": elapsed_ms,
                },
            )
            raise

        # Add header + access log
        response.headers[_REQUEST_ID_HEADER] = request_id
        elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
        logger.info(
            "request_complete",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "elapsed_ms": elapsed_ms,
            },
        )
        return response
