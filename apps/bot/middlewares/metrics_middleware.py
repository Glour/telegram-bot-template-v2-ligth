"""Metrics middleware for Prometheus."""
import time
from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject

from infrastructure.monitoring.metrics import (
    bot_commands_total,
    bot_errors_total,
    bot_messages_total,
    bot_response_time,
)


class MetricsMiddleware(BaseMiddleware):
    """Middleware for collecting Prometheus metrics."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        """Collect metrics for requests."""
        handler_name = handler.__name__

        # Track message type
        if isinstance(event, Message):
            if event.text and event.text.startswith("/"):
                command = event.text.split()[0]
                bot_commands_total.labels(command=command).inc()

        # Measure response time
        start_time = time.time()

        try:
            result = await handler(event, data)

            # Record success
            duration = time.time() - start_time
            bot_response_time.labels(handler=handler_name).observe(duration)
            bot_messages_total.labels(handler=handler_name, status="success").inc()

            return result

        except Exception as e:
            # Record error
            duration = time.time() - start_time
            bot_response_time.labels(handler=handler_name).observe(duration)
            bot_messages_total.labels(handler=handler_name, status="error").inc()
            bot_errors_total.labels(error_type=type(e).__name__).inc()

            raise
