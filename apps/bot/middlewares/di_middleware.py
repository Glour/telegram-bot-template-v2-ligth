"""Dependency Injection middleware for aiogram."""
from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from dishka import AsyncContainer
from dishka.integrations.aiogram import inject


class DIMiddleware(BaseMiddleware):
    """Middleware for dependency injection with Dishka."""

    def __init__(self, container: AsyncContainer):
        super().__init__()
        self.container = container

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        """Inject container into handler data."""
        async with self.container() as request_container:
            data["container"] = request_container
            return await handler(event, data)
