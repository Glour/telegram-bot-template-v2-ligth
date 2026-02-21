"""Start command handler."""
from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from dishka import FromDishka

from apps.bot.services.analytics_service import AnalyticsService
from apps.bot.services.user_service import UserService
from infrastructure.monitoring.logging import get_logger

logger = get_logger(__name__)
router = Router(name="start")


@router.message(CommandStart())
async def cmd_start(
    message: Message,
    user_service: FromDishka[UserService],
    analytics_service: FromDishka[AnalyticsService],
) -> None:
    """Handle /start command."""
    # Register or update user
    user = await user_service.register_or_update(message.from_user)

    # Track command
    await analytics_service.track_command("start", user.id)

    # Get user stats
    stats = await user_service.get_stats()

    # Send welcome message
    text = f"""
👋 <b>Привет, {user.first_name}!</b>

Добро пожаловать в современный Telegram Bot Template v2!

📊 <b>Статистика бота:</b>
• Всего пользователей: {stats.total_users}
• Активных пользователей: {stats.active_users}
• Новых за сегодня: {stats.new_users_today}

Это демонстрация новой архитектуры с:
✅ Service Layer
✅ Dependency Injection (Dishka)
✅ Unit of Work pattern
✅ Structured Logging
✅ Prometheus Metrics
✅ Admin Panel
✅ Analytics
    """.strip()

    await message.answer(text)

    logger.info(
        "start_command_executed",
        user_id=user.id,
        telegram_id=user.telegram_id,
        username=user.username,
    )
