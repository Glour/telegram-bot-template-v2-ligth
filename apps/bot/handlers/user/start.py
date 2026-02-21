"""Start command handler."""
from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from dishka import FromDishka

from apps.bot.services.user_service import UserService
from infrastructure.monitoring.logging import get_logger

logger = get_logger(__name__)
router = Router(name="start")


@router.message(CommandStart())
async def cmd_start(
    message: Message,
    user_service: FromDishka[UserService],
) -> None:
    """Handle /start command."""
    user = await user_service.register_or_update(message.from_user)

    text = (
        f"<b>Привет, {user.first_name}!</b>\n\n"
        f"Добро пожаловать в бот."
    )

    await message.answer(text)

    logger.info(
        "start command: user_id=%s, telegram_id=%s, username=%s",
        user.id,
        user.telegram_id,
        user.username,
    )
