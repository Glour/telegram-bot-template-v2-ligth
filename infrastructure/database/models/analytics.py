"""Analytics models for tracking events and user activity."""
from datetime import datetime

from sqlalchemy import BIGINT, ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from shared.enums import EventType

from .base import Base, TableNameMixin, TimestampMixin, int_pk


class AnalyticsEvent(Base, TableNameMixin, TimestampMixin):
    """Analytics event model for tracking user actions."""

    id: Mapped[int_pk]

    # Event details
    event_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True
    )

    # Event data (JSON field for flexibility)
    data: Mapped[dict] = mapped_column(JSON, nullable=False, server_default="{}")

    # Relationships
    user: Mapped["User | None"] = relationship("User", back_populates="analytics_events")

    def __repr__(self) -> str:
        return f"<AnalyticsEvent id={self.id} type={self.event_type} user_id={self.user_id}>"


# Update User model to include analytics relationship
from .users import User  # noqa: E402

User.analytics_events = relationship(
    "AnalyticsEvent", back_populates="user", cascade="all, delete-orphan"
)
