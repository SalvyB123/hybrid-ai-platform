from __future__ import annotations

import time
import uuid
from collections.abc import Callable

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response


class RequestContextMiddleware(BaseHTTPMiddleware):
    """
    - Generates or propagates X-Request-ID
    - Adds it to request.state for downstream use
    - Ensures the response always carries X-Request-ID
    - (Optional) captures simple latency metrics
    """

    header_name = "X-Request-ID"

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        req_id = request.headers.get(self.header_name) or uuid.uuid4().hex
        request.state.request_id = req_id

        started = time.perf_counter()
        try:
            response = await call_next(request)
        finally:
            # If an exception is raised, Starlette will re-enter via exception handlers.
            # We still want to surface the header when a normal response is produced here.
            elapsed_ms = int((time.perf_counter() - started) * 1000)
            request.state.elapsed_ms = elapsed_ms  # available to handlers/loggers

        # Always attach request-id on success path
        response.headers.setdefault(self.header_name, req_id)
        return response
