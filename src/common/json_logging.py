# src/common/json_logging.py
from __future__ import annotations

import json
import logging
from datetime import UTC, datetime


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "ts": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }

        # Merge 'extra' fields if present
        # (LogRecord.__dict__ may contain many internals; pick a safe subset.)
        for k, v in getattr(record, "__dict__", {}).items():
            if k in payload or k.startswith("_"):
                continue
            # keep selected safe extras only
            if k in {"request_id", "method", "path", "status_code", "error_type", "error_message"}:
                payload[k] = v

        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)

        # 🔒 Make it robust for any value types
        return json.dumps(payload, ensure_ascii=False, default=str)
