"""Global error handler."""
from aiogram import Router
from aiogram.types import ErrorEvent

from infrastructure.monitoring.logging import get_logger

logger = get_logger(__name__)
router = Router(name="errors")


@router.error()
async def error_handler(event: ErrorEvent) -> None:
    """Handle unhandled errors in bot handlers."""
    logger.error("Unhandled error: %s", event.exception, exc_info=event.exception)
    if event.update.message:
        await event.update.message.answer("Произошла ошибка. Попробуйте позже.")
