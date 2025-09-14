# src/common/json_logging.py
from __future__ import annotations

import json
import logging
import sys
from datetime import UTC, datetime
from typing import TextIO


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "ts": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }

        # Merge selected 'extra' fields if present
        for k, v in getattr(record, "__dict__", {}).items():
            if k in payload or k.startswith("_"):
                continue
            if k in {"request_id", "method", "path", "status_code", "error_type", "error_message"}:
                payload[k] = v

        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)

        return json.dumps(payload, ensure_ascii=False, default=str)


def setup_json_logging(
    level: int = logging.INFO,
    stream: TextIO | None = None,
    include_uvicorn_noise: bool = False,
) -> None:
    """
    Configure root logging to emit JSON lines.

    Call this once at app start (e.g., in create_app()).
    """
    handler = logging.StreamHandler(stream or sys.stdout)
    handler.setFormatter(JsonFormatter())

    root = logging.getLogger()
    # Make the configuration idempotent for tests / reloading
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level)

    # Tame noisy libraries (tweak to taste)
    if not include_uvicorn_noise:
        for noisy in ("uvicorn", "uvicorn.error", "uvicorn.access", "gunicorn"):
            logging.getLogger(noisy).setLevel(logging.WARNING)


def get_json_logger(name: str | None = None) -> logging.Logger:
    """
    Convenience accessor so callers don't need to import logging directly.
    """
    return logging.getLogger(name)


__all__ = ["JsonFormatter", "setup_json_logging", "get_json_logger"]
