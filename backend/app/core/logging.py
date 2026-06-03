"""Structured JSON logging and request logging middleware."""
import json
import logging
import sys
import time
from datetime import datetime, timezone
from typing import Any, Awaitable, Callable, Dict

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.middleware import REQUEST_ID_HEADER


_LOGGER_NAME = "app"


class JSONFormatter(logging.Formatter):
    """Emit logs as a single JSON line per record."""

    def format(self, record: logging.LogRecord) -> str:
        payload: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        for key, value in record.__dict__.items():
            if key not in {
                "name", "msg", "args", "levelname", "levelno", "pathname",
                "filename", "module", "exc_info", "exc_text", "stack_info",
                "lineno", "funcName", "created", "msecs", "relativeCreated",
                "thread", "threadName", "processName", "process", "message",
                "taskName",
            }:
                try:
                    json.dumps(value)
                    payload[key] = value
                except (TypeError, ValueError):
                    payload[key] = str(value)
        return json.dumps(payload, ensure_ascii=False)


def configure_logging(level: str = "INFO") -> None:
    """Configure root logger to emit structured JSON to stdout."""
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level.upper())
    # Tame noisy third-party loggers
    for noisy in ("uvicorn.access", "sqlalchemy.engine", "asyncio"):
        logging.getLogger(noisy).setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(f"{_LOGGER_NAME}.{name}")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log one structured line per request with latency and status."""

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        logger = get_logger("request")
        start = time.perf_counter()
        method = request.method
        path = request.url.path
        try:
            response = await call_next(request)
            status = response.status_code
        except Exception:
            duration_ms = (time.perf_counter() - start) * 1000
            logger.exception(
                "request_failed",
                extra={
                    "method": method,
                    "path": path,
                    "duration_ms": round(duration_ms, 2),
                    "request_id": getattr(request.state, "request_id", None),
                },
            )
            raise
        duration_ms = (time.perf_counter() - start) * 1000
        logger.info(
            "request_completed",
            extra={
                "method": method,
                "path": path,
                "status": status,
                "duration_ms": round(duration_ms, 2),
                "request_id": getattr(request.state, "request_id", None),
                "client": request.client.host if request.client else None,
            },
        )
        response.headers[REQUEST_ID_HEADER] = getattr(
            request.state, "request_id", ""
        )
        return response
