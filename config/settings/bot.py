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

    # Features
    use_redis: bool = Field(default=True, description="Enable Redis for FSM storage")
    webhook_enabled: bool = Field(default=False, description="Use webhook instead of polling")

    # Webhook settings (if enabled)
    webhook_url: str | None = Field(default=None, description="Webhook URL")
    webhook_path: str = Field(default="/webhook", description="Webhook path")
    webhook_secret: SecretStr | None = Field(default=None, description="Webhook secret token")

    # Bot behavior
    parse_mode: str = Field(default="HTML", description="Default parse mode")
    drop_pending_updates: bool = Field(default=True, description="Drop pending updates on start")

    # Channels and groups
    channel_link: str | None = Field(default=None, description="Main channel link")
    support_chat_id: int | None = Field(default=None, description="Support chat ID")

    # Rate limiting
    rate_limit: float = Field(default=1.0, description="Rate limit per user (seconds)")

    def is_admin(self, user_id: int) -> bool:
        """Check if user is admin."""
        return user_id in self.admin_ids
