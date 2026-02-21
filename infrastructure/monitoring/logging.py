"""Structured logging setup with structlog."""
import logging
import sys
from pathlib import Path

import structlog
from structlog.types import FilteringBoundLogger

from config.settings.base import get_settings


def setup_logging() -> FilteringBoundLogger:
    """Configure structured logging with structlog."""
    settings = get_settings()

    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=settings.logging.log_level,
    )

    # File handler if enabled
    if settings.logging.log_to_file:
        log_path = Path(settings.logging.log_file_path)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_path)
        file_handler.setLevel(settings.logging.log_level)
        logging.root.addHandler(file_handler)

    # Configure structlog processors
    processors: list = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
    ]

    if settings.logging.include_timestamp:
        processors.append(structlog.processors.TimeStamper(fmt="iso"))

    if settings.logging.include_caller:
        processors.append(structlog.processors.CallsiteParameterAdder())

    # Format based on settings
    if settings.logging.format == "json":
        processors.extend(
            [
                structlog.processors.format_exc_info,
                structlog.processors.JSONRenderer(),
            ]
        )
    else:
        processors.extend(
            [
                structlog.processors.format_exc_info,
                structlog.dev.ConsoleRenderer(colors=True),
            ]
        )

    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(settings.logging.log_level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )

    logger = structlog.get_logger()
    logger.info(
        "logging_configured",
        level=settings.logging.level,
        format=settings.logging.format,
    )

    return logger


def get_logger(name: str | None = None) -> FilteringBoundLogger:
    """Get logger instance."""
    if name:
        return structlog.get_logger(name)
    return structlog.get_logger()
