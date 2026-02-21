"""User-related Data Transfer Objects."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from shared.enums import Language, UserRole, UserStatus


class UserCreateDTO(BaseModel):
    """DTO for creating a new user."""

    telegram_id: int = Field(..., description="Telegram user ID")
    username: str | None = Field(default=None, description="Telegram username")
    first_name: str = Field(..., description="User first name")
    last_name: str | None = Field(default=None, description="User last name")
    language: Language = Field(default=Language.RU, description="User language")


class UserUpdateDTO(BaseModel):
    """DTO for updating user data."""

    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    language: Language | None = None
    role: UserRole | None = None
    status: UserStatus | None = None


class UserResponseDTO(BaseModel):
    """DTO for user response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    telegram_id: int
    username: str | None
    first_name: str
    last_name: str | None
    full_name: str | None
    language: Language
    role: UserRole
    status: UserStatus
    created_at: datetime
    updated_at: datetime | None

    @property
    def display_name(self) -> str:
        """Get display name for user."""
        if self.username:
            return f"@{self.username}"
        return self.full_name or self.first_name
