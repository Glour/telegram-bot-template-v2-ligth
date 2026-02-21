"""User service with business logic."""
from aiogram.types import User as TelegramUser

from infrastructure.database.models.users import User
from infrastructure.database.uow import UnitOfWork
from shared.dto.user import UserCreateDTO
from shared.enums import Language
from shared.exceptions.base import NotFoundError


class UserService:
    """Service for user-related business logic."""

    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def register_or_update(self, telegram_user: TelegramUser) -> User:
        """Register new user or update existing one."""
        dto = UserCreateDTO(
            telegram_id=telegram_user.id,
            username=telegram_user.username,
            first_name=telegram_user.first_name,
            last_name=telegram_user.last_name,
            language=Language(telegram_user.language_code or "ru"),
        )

        user, created = await self.uow.users.get_or_create(dto)
        return user

    async def get_user(self, user_id: int) -> User:
        """Get user by ID."""
        user = await self.uow.users.get(user_id)
        if not user:
            raise NotFoundError(f"User with id={user_id} not found")
        return user

    async def get_user_by_telegram_id(self, telegram_id: int) -> User | None:
        """Get user by Telegram ID."""
        return await self.uow.users.get_by_telegram_id(telegram_id)

    async def get_total_users(self) -> int:
        """Get total number of users."""
        return await self.uow.users.count()
