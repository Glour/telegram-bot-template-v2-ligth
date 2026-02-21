"""Logging middleware for tracking requests."""
import time
from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject

from infrastructure.monitoring.logging import get_logger

logger = get_logger(__name__)


class LoggingMiddleware(BaseMiddleware):
    """Middleware for logging all bot interactions."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        """Log request and response."""
        start_time = time.time()

        # Extract event info
        if isinstance(event, Message):
            event_type = "message"
            user_id = event.from_user.id if event.from_user else None
            username = event.from_user.username if event.from_user else None
            text = event.text or event.caption or "<non-text>"
        elif isinstance(event, CallbackQuery):
            event_type = "callback"
            user_id = event.from_user.id if event.from_user else None
            username = event.from_user.username if event.from_user else None
            text = event.data
        else:
            event_type = "unknown"
            user_id = None
            username = None
            text = None

        logger.info(
            "bot_event_received",
            event_type=event_type,
            user_id=user_id,
            username=username,
            text=text,
        )

        try:
            result = await handler(event, data)

            duration = time.time() - start_time
            logger.info(
                "bot_event_processed",
                event_type=event_type,
                user_id=user_id,
                duration_ms=round(duration * 1000, 2),
                status="success",
            )

            return result

        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                "bot_event_error",
                event_type=event_type,
                user_id=user_id,
                duration_ms=round(duration * 1000, 2),
                error=str(e),
                error_type=type(e).__name__,
            )
            raise
