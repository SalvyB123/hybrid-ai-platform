from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from typing import Any


class JsonFormatter(logging.Formatter):
    """Minimal JSON log formatter (no external deps)."""

    def format(self, record: logging.LogRecord) -> str:  # noqa: D401
        payload: dict[str, Any] = {
            "ts": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        # Include standard extras if present
        for attr in ("request_id", "path", "method", "status_code", "exc_info"):
            if hasattr(record, attr) and getattr(record, attr) is not None:
                payload[attr] = getattr(record, attr)

        # Exception info (if any) as string
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)

        return json.dumps(payload, ensure_ascii=False)


def setup_json_logging(level: str | int | None = None) -> None:
    """Configure root logger for JSON output once at startup."""
    if isinstance(level, str):
        level = getattr(logging, level.upper(), logging.INFO)
    else:
        level = level or logging.INFO

    # Idempotent: if already configured, don't duplicate handlers
    root = logging.getLogger()
    if getattr(root, "_json_configured", False):
        return

    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())

    root.handlers[:] = [handler]
    root.setLevel(level)
    root._json_configured = True  # type: ignore[attr-defined]

    # Quiet noisy libraries in prod defaults
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
