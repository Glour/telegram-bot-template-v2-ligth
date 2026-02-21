"""Analytics repository."""
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.database.models.analytics import AnalyticsEvent
from infrastructure.database.repositories.base import BaseRepository
from shared.dto.analytics import EventCreateDTO
from shared.enums import EventType


class AnalyticsRepository(BaseRepository[AnalyticsEvent]):
    """Repository for AnalyticsEvent model."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, AnalyticsEvent)

    async def track_event(self, dto: EventCreateDTO) -> AnalyticsEvent:
        """Track analytics event."""
        return await self.create(
            event_type=dto.event_type.value,
            user_id=dto.user_id,
            data=dto.data,
        )

    async def get_user_events(
        self, user_id: int, limit: int = 100
    ) -> list[AnalyticsEvent]:
        """Get events for specific user."""
        stmt = (
            select(AnalyticsEvent)
            .where(AnalyticsEvent.user_id == user_id)
            .order_by(AnalyticsEvent.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count_events_by_type(
        self, event_type: EventType, since: datetime | None = None
    ) -> int:
        """Count events by type."""
        stmt = (
            select(func.count())
            .select_from(AnalyticsEvent)
            .where(AnalyticsEvent.event_type == event_type.value)
        )

        if since:
            stmt = stmt.where(AnalyticsEvent.created_at >= since)

        result = await self.session.execute(stmt)
        return result.scalar() or 0

    async def count_total_events(self, since: datetime | None = None) -> int:
        """Count total events."""
        stmt = select(func.count()).select_from(AnalyticsEvent)

        if since:
            stmt = stmt.where(AnalyticsEvent.created_at >= since)

        result = await self.session.execute(stmt)
        return result.scalar() or 0
