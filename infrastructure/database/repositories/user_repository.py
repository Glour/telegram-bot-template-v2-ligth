"""User repository with user-specific operations."""
from datetime import datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.database.models.users import User
from infrastructure.database.repositories.base import BaseRepository
from shared.dto.user import UserCreateDTO, UserUpdateDTO
from shared.enums import UserStatus


class UserRepository(BaseRepository[User]):
    """Repository for User model."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, User)

    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        """Get user by Telegram ID."""
        return await self.get_by(telegram_id=telegram_id)

    async def get_by_username(self, username: str) -> User | None:
        """Get user by username."""
        return await self.get_by(username=username)

    async def get_or_create(self, dto: UserCreateDTO) -> tuple[User, bool]:
        """Get existing user or create new one. Returns (user, created)."""
        user = await self.get_by_telegram_id(dto.telegram_id)

        if user:
            # Update user data
            user.username = dto.username
            user.first_name = dto.first_name
            user.last_name = dto.last_name
            user.language = dto.language.value
            user.last_activity_at = datetime.utcnow()
            await self.session.flush()
            return user, False

        # Create new user
        user = await self.create(
            telegram_id=dto.telegram_id,
            username=dto.username,
            first_name=dto.first_name,
            last_name=dto.last_name,
            language=dto.language.value,
            last_activity_at=datetime.utcnow(),
        )
        return user, True

    async def update_user(self, user_id: int, dto: UserUpdateDTO) -> User | None:
        """Update user with DTO."""
        data = dto.model_dump(exclude_none=True)
        return await self.update(user_id, **data)

    async def increment_messages(self, user_id: int) -> None:
        """Increment user's message count."""
        user = await self.get(user_id)
        if user:
            user.total_messages += 1
            user.last_activity_at = datetime.utcnow()
            await self.session.flush()

    async def get_active_users(self, period_hours: int = 24) -> list[User]:
        """Get users active in the last N hours."""
        since = datetime.utcnow() - timedelta(hours=period_hours)
        stmt = (
            select(User)
            .where(User.last_activity_at >= since)
            .where(User.status == UserStatus.ACTIVE.value)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count_active_users(self, period_hours: int = 24) -> int:
        """Count active users in the last N hours."""
        since = datetime.utcnow() - timedelta(hours=period_hours)
        stmt = (
            select(func.count())
            .select_from(User)
            .where(User.last_activity_at >= since)
            .where(User.status == UserStatus.ACTIVE.value)
        )
        result = await self.session.execute(stmt)
        return result.scalar() or 0

    async def get_admins(self) -> list[User]:
        """Get all admin users."""
        from shared.enums import UserRole

        stmt = select(User).where(User.role == UserRole.ADMIN.value)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count_new_users(self, since: datetime) -> int:
        """Count users created since date."""
        stmt = select(func.count()).select_from(User).where(User.created_at >= since)
        result = await self.session.execute(stmt)
        return result.scalar() or 0

    async def count_by_status(self, status: UserStatus) -> int:
        """Count users by status."""
        return await self.count(status=status.value)
