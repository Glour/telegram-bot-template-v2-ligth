"""Unit of Work pattern implementation."""
from types import TracebackType
from typing import Self

from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.database.repositories.user_repository import UserRepository


class UnitOfWork:
    """Unit of Work for managing database transactions and repositories."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self._users: UserRepository | None = None

    @property
    def users(self) -> UserRepository:
        """Get User repository."""
        if self._users is None:
            self._users = UserRepository(self.session)
        return self._users

    # === REGISTER NEW REPOSITORIES ABOVE ===

    async def commit(self) -> None:
        """Commit the transaction."""
        await self.session.commit()

    async def rollback(self) -> None:
        """Rollback the transaction."""
        await self.session.rollback()

    async def close(self) -> None:
        """Close the session."""
        await self.session.close()

    async def __aenter__(self) -> Self:
        """Enter async context."""
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Exit async context."""
        if exc_type is not None:
            await self.rollback()
        else:
            await self.commit()
        await self.close()
