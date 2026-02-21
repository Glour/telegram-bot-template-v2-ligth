"""Analytics service for tracking events."""
from infrastructure.database.uow import UnitOfWork
from shared.dto.analytics import EventCreateDTO, MetricsDTO
from shared.enums import EventType


class AnalyticsService:
    """Service for analytics operations."""

    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def track_event(self, dto: EventCreateDTO) -> None:
        """Track analytics event."""
        await self.uow.analytics.track_event(dto)

    async def track_command(self, command: str, user_id: int) -> None:
        """Track command execution."""
        await self.track_event(
            EventCreateDTO(
                event_type=EventType.COMMAND_EXECUTED,
                user_id=user_id,
                data={"command": command},
            )
        )

    async def track_message(self, user_id: int, message_type: str = "text") -> None:
        """Track message sent."""
        await self.track_event(
            EventCreateDTO(
                event_type=EventType.MESSAGE_SENT,
                user_id=user_id,
                data={"message_type": message_type},
            )
        )

    async def track_button_click(
        self, button_data: str, user_id: int
    ) -> None:
        """Track button click."""
        await self.track_event(
            EventCreateDTO(
                event_type=EventType.BUTTON_CLICKED,
                user_id=user_id,
                data={"button_data": button_data},
            )
        )

    async def track_error(
        self, error_type: str, user_id: int | None = None, details: dict | None = None
    ) -> None:
        """Track error occurrence."""
        await self.track_event(
            EventCreateDTO(
                event_type=EventType.ERROR_OCCURRED,
                user_id=user_id,
                data={"error_type": error_type, "details": details or {}},
            )
        )

    async def get_metrics(self) -> MetricsDTO:
        """Get bot metrics."""
        from datetime import datetime, timedelta

        now = datetime.utcnow()
        hour_ago = now - timedelta(hours=1)
        day_ago = now - timedelta(days=1)
        week_ago = now - timedelta(days=7)

        return MetricsDTO(
            total_messages=await self.uow.analytics.count_events_by_type(
                EventType.MESSAGE_SENT
            ),
            total_commands=await self.uow.analytics.count_events_by_type(
                EventType.COMMAND_EXECUTED
            ),
            total_errors=await self.uow.analytics.count_events_by_type(
                EventType.ERROR_OCCURRED
            ),
            active_users_1h=await self.uow.users.count_active_users(1),
            active_users_24h=await self.uow.users.count_active_users(24),
            active_users_7d=await self.uow.users.count_active_users(168),
        )
