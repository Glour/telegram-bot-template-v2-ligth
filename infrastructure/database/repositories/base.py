"""Base repository with common CRUD operations."""
from collections.abc import Sequence
from typing import Any, Generic, TypeVar

from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.database.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Base repository for all database operations."""

    def __init__(self, session: AsyncSession, model: type[ModelType]):
        self.session = session
        self.model = model

    async def get(self, id: Any) -> ModelType | None:
        """Get model by ID."""
        stmt = select(self.model).where(self.model.id == id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by(self, **filters) -> ModelType | None:
        """Get model by filters."""
        stmt = select(self.model).filter_by(**filters)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(
        self,
        limit: int | None = None,
        offset: int | None = None,
        **filters,
    ) -> Sequence[ModelType]:
        """Get all models with optional filters."""
        stmt = select(self.model).filter_by(**filters)

        if offset is not None:
            stmt = stmt.offset(offset)
        if limit is not None:
            stmt = stmt.limit(limit)

        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create(self, **kwargs) -> ModelType:
        """Create new model."""
        instance = self.model(**kwargs)
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def create_many(self, data: list[dict[str, Any]]) -> list[ModelType]:
        """Create multiple models."""
        instances = [self.model(**item) for item in data]
        self.session.add_all(instances)
        await self.session.flush()
        return instances

    async def update(self, id: Any, **kwargs) -> ModelType | None:
        """Update model by ID."""
        stmt = (
            update(self.model)
            .where(self.model.id == id)
            .values(**kwargs)
            .returning(self.model)
        )
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.scalar_one_or_none()

    async def delete(self, id: Any) -> bool:
        """Delete model by ID."""
        stmt = delete(self.model).where(self.model.id == id)
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.rowcount > 0

    async def count(self, **filters) -> int:
        """Count models with optional filters."""
        stmt = select(func.count()).select_from(self.model).filter_by(**filters)
        result = await self.session.execute(stmt)
        return result.scalar() or 0

    async def exists(self, **filters) -> bool:
        """Check if model exists."""
        count = await self.count(**filters)
        return count > 0
