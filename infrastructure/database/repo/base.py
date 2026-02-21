from typing import Any, Optional, Type, TypeVar, Sequence

from sqlalchemy import insert, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import DeclarativeMeta

T = TypeVar('T', bound=DeclarativeMeta)


class BaseRepo:
    def __init__(self, session: AsyncSession, model: Type[T]):
        self.session = session
        self.model = model

    async def get(self, obj_id: Any) -> Optional[T]:
        stmt = (
            select(self.model)
            .filter_by(id=int(obj_id))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, **kwargs) -> Optional[T]:
        insert_stmt = (
            insert(self.model)
            .values(**kwargs)
            .returning(self.model)
        )
        result = await self.session.execute(insert_stmt)
        await self.session.commit()
        return result.scalar_one_or_none()

    async def update(self, obj_id: Any, **kwargs) -> Optional[T]:
        stmt = (
            update(self.model)
            .values(**kwargs)
            .filter_by(id=obj_id)
            .returning(self.model)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one_or_none()

    async def delete(self, obj_id: Any) -> Optional[T]:
        stmt = (
            delete(self.model)
            .filter_by(id=obj_id)
            .returning(self.model)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one_or_none()

    async def get_all(
            self,
            limit: Optional[int] = None,
            offset: Optional[int] = None
    ) -> Sequence[T]:
        stmt = (
            select(self.model)
            .order_by(self.model.id)
        )

        if limit:
            stmt = stmt.limit(limit)
        if offset:
            stmt = stmt.offset(offset)

        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count_all(self) -> int:
        stmt = (
            select(func.count())
            .select_from(self.model)
        )
        result = await self.session.execute(stmt)
        return result.scalar()
