from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.database.models import User
from infrastructure.database.repo.base import BaseRepo


class UserRepo(BaseRepo):
    def __init__(self, session: AsyncSession):
        super().__init__(session, User)  # noqa

    async def get_or_create(
            self,
            user_id: int | str,
            first_name: str,
            full_name: str,
            language: str,
            username: str | None = None,
    ) -> User:
        insert_stmt = (
            insert(User)
            .values(
                id=int(user_id),
                username=username,
                first_name=first_name,
                full_name=full_name,
                language=language,
            )
            .on_conflict_do_update(
                index_elements=[User.id],
                set_=dict(
                    username=username,
                    first_name=first_name,
                    full_name=full_name,
                ),
            )
            .returning(User)
        )
        result = await self.session.execute(insert_stmt)
        await self.session.commit()
        return result.scalar_one_or_none()
