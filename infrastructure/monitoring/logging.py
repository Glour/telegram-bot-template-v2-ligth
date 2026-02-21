"""Standard Python logging setup."""
import logging
import sys

from config.settings.base import get_settings


def setup_logging() -> logging.Logger:
    """Configure standard Python logging."""
    settings = get_settings()

    # Configure root logger
    logging.basicConfig(
        level=settings.logging.log_level,
        format=settings.logging.format,
        stream=sys.stdout,
    )

    # Reduce noise from third-party libraries
    logging.getLogger("aiogram").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)

    logger = logging.getLogger(settings.app_name)
    logger.info("Logging configured (level=%s)", settings.logging.level)

    return logger


def get_logger(name: str | None = None) -> logging.Logger:
    """Get logger instance."""
    return logging.getLogger(name or get_settings().app_name)
