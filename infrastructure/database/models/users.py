"""User model."""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import BIGINT, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from shared.enums import Language, UserRole, UserStatus

from .base import Base, TableNameMixin, TimestampMixin, int_pk


class User(Base, TableNameMixin, TimestampMixin):
    """User model representing Telegram bot users."""

    # Primary key
    id: Mapped[int_pk]
    telegram_id: Mapped[int] = mapped_column(BIGINT, unique=True, index=True, nullable=False)

    # Basic info
    username: Mapped[str | None] = mapped_column(String(255), index=True, nullable=True)
    first_name: Mapped[str] = mapped_column(String(255), nullable=False)
    last_name: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Settings
    language: Mapped[str] = mapped_column(
        String(2), server_default=Language.RU.value, nullable=False
    )

    # Status and role
    status: Mapped[str] = mapped_column(
        String(20), server_default=UserStatus.ACTIVE.value, nullable=False, index=True
    )
    role: Mapped[str] = mapped_column(
        String(20), server_default=UserRole.USER.value, nullable=False, index=True
    )

    # Referral system
    referrer_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    referrer: Mapped[User | None] = relationship(
        "User", back_populates="referrals", foreign_keys=[referrer_id], remote_side=lambda: [User.id]
    )
    referrals: Mapped[list[User]] = relationship(
        "User", back_populates="referrer", foreign_keys=[referrer_id]
    )

    # Analytics
    last_activity_at: Mapped[datetime | None] = mapped_column(nullable=True, index=True)
    total_messages: Mapped[int] = mapped_column(server_default="0", nullable=False)

    @property
    def full_name(self) -> str:
        """Get user's full name."""
        if self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name

    @property
    def is_admin(self) -> bool:
        """Check if user is admin."""
        return self.role == UserRole.ADMIN.value

    @property
    def is_active(self) -> bool:
        """Check if user is active."""
        return self.status == UserStatus.ACTIVE.value

    def __repr__(self) -> str:
        return f"<User id={self.id} telegram_id={self.telegram_id} username={self.username}>"
