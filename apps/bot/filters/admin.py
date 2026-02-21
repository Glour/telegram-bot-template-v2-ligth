"""Admin access filter."""
from aiogram.filters import BaseFilter
from aiogram.types import Message

from config.settings.base import get_settings


class IsAdminFilter(BaseFilter):
    """Filter that passes only for admin users."""

    async def __call__(self, message: Message) -> bool:
        """Check if user is in admin list."""
        settings = get_settings()
        return message.from_user.id in settings.bot.admin_ids
