"""Logging middleware for tracking requests."""
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

        logger.info("Event received: type=%s, user_id=%s, username=%s, text=%s", event_type, user_id, username, text)

        try:
            result = await handler(event, data)
            logger.info("Event processed: type=%s, user_id=%s, status=success", event_type, user_id)
            return result
        except Exception as e:
            logger.error(
                "Event error: type=%s, user_id=%s, error=%s (%s)", event_type, user_id, e, type(e).__name__
            )
            raise
