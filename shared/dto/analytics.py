"""Analytics-related Data Transfer Objects."""
from datetime import datetime

from pydantic import BaseModel, Field

from shared.enums import EventType


class EventCreateDTO(BaseModel):
    """DTO for creating analytics event."""

    event_type: EventType = Field(..., description="Type of event")
    user_id: int | None = Field(default=None, description="User ID who triggered event")
    data: dict = Field(default_factory=dict, description="Additional event data")


class EventResponseDTO(BaseModel):
    """DTO for analytics event response."""

    id: int
    event_type: EventType
    user_id: int | None
    data: dict
    created_at: datetime


class MetricsDTO(BaseModel):
    """DTO for bot metrics."""

    total_messages: int = 0
    total_commands: int = 0
    total_errors: int = 0
    active_users_1h: int = 0
    active_users_24h: int = 0
    active_users_7d: int = 0
