"""Main bot application entry point."""
import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from dishka.integrations.aiogram import setup_dishka

from apps.bot.di_container import create_container
from apps.bot.middlewares.logging_middleware import LoggingMiddleware
from apps.bot.middlewares.metrics_middleware import MetricsMiddleware
from config.settings.base import get_settings
from infrastructure.cache.redis_client import close_redis
from infrastructure.database.core.session import close_engine
from infrastructure.monitoring.logging import setup_logging
from infrastructure.monitoring.metrics import start_metrics_server

logger = setup_logging()


def register_routers(dp: Dispatcher) -> None:
    """Register all routers."""
    from apps.bot.handlers.user import start

    dp.include_router(start.router)


def register_middlewares(dp: Dispatcher) -> None:
    """Register middlewares."""
    # Metrics middleware
    dp.message.middleware(MetricsMiddleware())
    dp.callback_query.middleware(MetricsMiddleware())

    # Logging middleware
    dp.message.middleware(LoggingMiddleware())
    dp.callback_query.middleware(LoggingMiddleware())


async def on_startup(bot: Bot) -> None:
    """Actions on bot startup."""
    settings = get_settings()

    logger.info(
        "bot_starting",
        environment=settings.environment,
        bot_username=(await bot.get_me()).username,
    )

    # Start metrics server
    start_metrics_server()


async def on_shutdown(bot: Bot) -> None:
    """Actions on bot shutdown."""
    logger.info("bot_shutting_down")

    # Close connections
    await close_redis()
    await close_engine()

    logger.info("bot_stopped")


async def main() -> None:
    """Main bot function."""
    # Load settings
    settings = get_settings()

    # Create bot and dispatcher
    bot = Bot(
        token=settings.bot.token.get_secret_value(),
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    dp = Dispatcher()

    # Create DI container
    container = create_container()

    # Setup Dishka integration
    setup_dishka(container=container, router=dp)

    # Register routers and middlewares
    register_routers(dp)
    register_middlewares(dp)

    # Startup/shutdown handlers
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    # Start polling
    logger.info("starting_polling")

    try:
        await dp.start_polling(
            bot,
            allowed_updates=dp.resolve_used_update_types(),
            drop_pending_updates=settings.bot.drop_pending_updates,
        )
    finally:
        await bot.session.close()
        await container.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("bot_stopped_by_user")
