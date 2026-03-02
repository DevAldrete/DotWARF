"""Structured JSON logging configuration for production.

In DEBUG mode, uses a human-readable format.
In production, emits newline-delimited JSON so Railway / log aggregators can
parse each field (level, logger, message, timestamp, exc_info, etc.).
"""

import logging
import logging.config
import sys


class _JsonFormatter(logging.Formatter):
    """Minimal stdlib-only JSON log formatter (no extra dependencies)."""

    def format(self, record: logging.LogRecord) -> str:
        import json
        import traceback

        payload: dict = {
            "ts": self.formatTime(record, "%Y-%m-%dT%H:%M:%S"),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }

        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        elif record.exc_text:
            payload["exc"] = record.exc_text

        if record.stack_info:
            payload["stack"] = self.formatStack(record.stack_info)

        return json.dumps(payload, ensure_ascii=False)


def configure_logging(debug: bool | None = None) -> None:
    """Set up root logger. Call once at application startup.

    Args:
        debug: Override DEBUG detection. If None, reads from Settings.
    """
    if debug is None:
        from app.core.config import get_settings

        debug = get_settings().DEBUG

    handler = logging.StreamHandler(sys.stdout)

    if debug:
        fmt = "%(levelname)-8s %(name)s  %(message)s"
        handler.setFormatter(logging.Formatter(fmt))
    else:
        handler.setFormatter(_JsonFormatter())

    root = logging.getLogger()
    root.setLevel(logging.DEBUG if debug else logging.INFO)

    # Replace any existing handlers (avoids duplicate output)
    root.handlers.clear()
    root.addHandler(handler)

    # Quiet down noisy libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.INFO if debug else logging.WARNING
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("litellm").setLevel(logging.WARNING)
