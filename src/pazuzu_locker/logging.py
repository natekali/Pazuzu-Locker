"""Structured logging utilities for Pazuzu Locker."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any

from .config import AppConfig


class JsonFormatter(logging.Formatter):
    """JSON formatter that includes context fields."""

    def format(self, record: logging.LogRecord) -> str:
        log_data: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
        }
        for key in ("action", "file_path", "provider", "manifest_id", "manifest_url"):
            value = getattr(record, key, None)
            if value is not None:
                log_data[key] = value
        if record.exc_info:
            log_data["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(log_data, ensure_ascii=False)


def configure_logging(level: str, fmt: str = "json") -> logging.Logger:
    """Configure root logger based on the requested level and format."""

    logger = logging.getLogger("pazuzu_locker")
    logger.setLevel(getattr(logging, level, logging.INFO))
    handler = logging.StreamHandler()
    if fmt == "json":
        handler.setFormatter(JsonFormatter())
    else:
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
    logger.handlers.clear()
    logger.addHandler(handler)
    logger.propagate = False
    return logger


def get_logger(config: AppConfig, name: str = "pazuzu_locker") -> logging.LoggerAdapter:
    """Return a logger adapter with provider context attached."""

    base_logger = logging.getLogger(name)
    return logging.LoggerAdapter(base_logger, {"provider": config.provider.name})
