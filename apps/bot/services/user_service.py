"""User service with business logic."""
from aiogram.types import User as TelegramUser

from infrastructure.cache.cache_service import CacheService
from infrastructure.database.models.users import User
from infrastructure.database.uow import UnitOfWork
from shared.dto.user import UserCreateDTO, UserResponseDTO, UserStatsDTO
from shared.enums import Language, UserStatus
from shared.exceptions.base import NotFoundError


class UserService:
    """Service for user-related business logic."""

    def __init__(self, uow: UnitOfWork, cache: CacheService):
        self.uow = uow
        self.cache = cache

    async def register_or_update(self, telegram_user: TelegramUser) -> User:
        """Register new user or update existing one."""
        # Create DTO from Telegram user
        dto = UserCreateDTO(
            telegram_id=telegram_user.id,
            username=telegram_user.username,
            first_name=telegram_user.first_name,
            last_name=telegram_user.last_name,
            language=Language(telegram_user.language_code or "ru"),
        )

        # Get or create user
        user, created = await self.uow.users.get_or_create(dto)

        # Track registration event if new user
        if created:
            from shared.dto.analytics import EventCreateDTO
            from shared.enums import EventType

            await self.uow.analytics.track_event(
                EventCreateDTO(
                    event_type=EventType.USER_REGISTERED,
                    user_id=user.id,
                    data={"telegram_id": telegram_user.id},
                )
            )

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

    async def get_user_dto(self, user_id: int) -> UserResponseDTO:
        """Get user DTO."""
        user = await self.get_user(user_id)
        return UserResponseDTO.model_validate(user)

    async def increment_messages(self, user_id: int) -> None:
        """Increment user's message counter."""
        await self.uow.users.increment_messages(user_id)

    async def get_stats(self) -> UserStatsDTO:
        """Get user statistics."""
        from datetime import datetime, timedelta

        # Try to get from cache
        cache_key = "user_stats"
        cached = await self.cache.get(cache_key)
        if cached:
            return UserStatsDTO(**cached)

        # Calculate stats
        now = datetime.utcnow()
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)

        stats = UserStatsDTO(
            total_users=await self.uow.users.count(),
            active_users=await self.uow.users.count_by_status(UserStatus.ACTIVE),
            blocked_users=await self.uow.users.count_by_status(UserStatus.BLOCKED),
            banned_users=await self.uow.users.count_by_status(UserStatus.BANNED),
            new_users_today=await self.uow.users.count_new_users(today),
            new_users_this_week=await self.uow.users.count_new_users(week_ago),
            new_users_this_month=await self.uow.users.count_new_users(month_ago),
        )

        # Cache for 5 minutes
        await self.cache.set(cache_key, stats.model_dump(), ttl=300)

        return stats

    async def get_active_users_count(self, period_hours: int = 24) -> int:
        """Get count of active users in period."""
        cache_key = f"active_users_{period_hours}h"

        # Try cache
        cached = await self.cache.get(cache_key)
        if cached is not None:
            return int(cached)

        # Calculate
        count = await self.uow.users.count_active_users(period_hours)

        # Cache for 5 minutes
        await self.cache.set(cache_key, count, ttl=300)

        return count
