"""Telegram bot configuration settings."""
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class BotSettings(BaseSettings):
    """Telegram bot configuration."""

    model_config = SettingsConfigDict(
        env_prefix="BOT__",
        extra="ignore",
    )

    token: SecretStr = Field(..., description="Telegram bot token from @BotFather")
    admin_ids: list[int] = Field(default_factory=list, description="List of admin user IDs")

    # Bot behavior
    drop_pending_updates: bool = Field(default=True, description="Drop pending updates on start")

    def is_admin(self, user_id: int) -> bool:
        """Check if user is admin."""
        return user_id in self.admin_ids
