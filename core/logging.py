"""core/logging.py — SENTRY structlog JSON logging configuration.

Call ``configure_logging()`` once at application startup (in the FastAPI
lifespan hook, CLI entrypoint, or test fixtures).  After that, every stage
obtains a logger via:

    import structlog
    logger = structlog.get_logger(__name__)

The ``request_id`` context variable is set per-request by the API middleware
and propagated automatically to all log records emitted within that request.
"""

from __future__ import annotations

import logging
import sys
from contextvars import ContextVar
from typing import Any

import structlog

# ---------------------------------------------------------------------------
# Context variable holding the current request ID.
# Middleware sets this at the start of each request so every log line emitted
# anywhere in the call stack is correlated to the originating request.
# Usage:
#     from core.logging import request_id_var
#     request_id_var.set("req_01J...")
# ---------------------------------------------------------------------------
request_id_var: ContextVar[str | None] = ContextVar("request_id", default=None)


def _add_request_id(
    logger: Any,  # noqa: ANN401 — structlog passes an opaque logger object
    method: str,
    event_dict: dict[str, Any],
) -> dict[str, Any]:
    """structlog processor: inject request_id into every log record.

    Placed early in the processor chain so all downstream processors see it.
    Omitted (not set to None) when no request context is active, so batch
    jobs and CLI tools don't emit a noisy ``request_id: null`` field.
    """
    rid = request_id_var.get()
    if rid is not None:
        event_dict["request_id"] = rid
    return event_dict


def configure_logging(*, log_level: str = "INFO", pretty: bool = False) -> None:
    """Configure structlog for the SENTRY application.

    Parameters
    ----------
    log_level:
        Standard logging level name, e.g. "DEBUG", "INFO", "WARNING".
    pretty:
        If True, emit colourised human-readable output instead of JSON.
        Set to True in local development; always False in production.

    This function is idempotent: calling it more than once is safe and a no-op
    after the first call, matching structlog's own guidance.
    """
    shared_processors: list[Any] = [
        # Inject request_id before anything else.
        _add_request_id,
        # Add the logger name (module path) to every record.
        structlog.stdlib.add_logger_name,
        # Add the log level as a string field.
        structlog.stdlib.add_log_level,
        # ISO-8601 UTC timestamp on every record.
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        # Render exception info into the event dict.
        structlog.processors.StackInfoRenderer(),
        # Format exceptions as a single string field rather than multi-line.
        structlog.processors.ExceptionRenderer(),
    ]

    if pretty:
        # Human-readable colourised output for local development.
        renderer: Any = structlog.dev.ConsoleRenderer()
    else:
        # Machine-readable JSON for production and CI log aggregation.
        renderer = structlog.processors.JSONRenderer()

    structlog.configure(
        processors=[
            *shared_processors,
            # Bridge structlog events to stdlib logging so existing libraries
            # (pydantic-settings, uvicorn, etc.) appear in the same stream.
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        # Cache the logger wrapper class for performance.
        cache_logger_on_first_use=True,
    )

    # Configure the stdlib root logger so it formats via structlog.
    formatter = structlog.stdlib.ProcessorFormatter(
        # These processors run after the shared ones, on the stdlib side.
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            renderer,
        ],
        foreign_pre_chain=shared_processors,
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    # Avoid duplicate handlers if configure_logging is called more than once.
    if not any(isinstance(h, logging.StreamHandler) and h.stream is sys.stdout
               for h in root_logger.handlers):
        root_logger.addHandler(handler)

    root_logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
