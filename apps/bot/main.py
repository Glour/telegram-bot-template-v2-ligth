"""Main bot application entry point."""
import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from dishka.integrations.aiogram import setup_dishka

from apps.bot.di_container import create_container
from apps.bot.middlewares.logging_middleware import LoggingMiddleware
from config.settings.base import get_settings
from infrastructure.database.core.session import close_engine
from infrastructure.monitoring.logging import setup_logging

logger = setup_logging()


def register_routers(dp: Dispatcher) -> None:
    """Register all routers."""
    from apps.bot.handlers import errors
    from apps.bot.handlers.user import start

    dp.include_router(start.router)
    dp.include_router(errors.router)
    # === REGISTER NEW ROUTERS ABOVE ===


def register_middlewares(dp: Dispatcher) -> None:
    """Register middlewares."""
    dp.message.middleware(LoggingMiddleware())
    dp.callback_query.middleware(LoggingMiddleware())


async def on_startup(bot: Bot) -> None:
    """Actions on bot startup."""
    settings = get_settings()
    bot_info = await bot.get_me()
    logger.info("Bot starting (environment=%s, username=%s)", settings.environment, bot_info.username)


async def on_shutdown(bot: Bot) -> None:
    """Actions on bot shutdown."""
    logger.info("Bot shutting down...")
    await close_engine()
    logger.info("Bot stopped")


async def main() -> None:
    """Main bot function."""
    settings = get_settings()

    bot = Bot(
        token=settings.bot.token.get_secret_value(),
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    dp = Dispatcher()

    container = create_container()
    setup_dishka(container=container, router=dp, auto_inject=True)

    register_routers(dp)
    register_middlewares(dp)

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    logger.info("Starting polling...")

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
        logger.info("Bot stopped by user")
