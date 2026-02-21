"""Base application settings."""
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from config.settings.admin import AdminSettings
from config.settings.bot import BotSettings
from config.settings.database import DatabaseSettings, RedisSettings
from config.settings.observability import (
    LoggingSettings,
    MetricsSettings,
    SentrySettings,
    TracingSettings,
)


class AppSettings(BaseSettings):
    """Main application settings aggregator."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore",
        case_sensitive=False,
    )

    # Environment
    environment: str = Field(default="development", description="Environment: development, staging, production")
    debug: bool = Field(default=False, description="Enable debug mode")

    # Application info
    app_name: str = Field(default="Telegram Bot v2", description="Application name")
    app_version: str = Field(default="3.0.0", description="Application version")

    # Sub-settings
    bot: BotSettings = Field(default_factory=BotSettings)
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    admin: AdminSettings = Field(default_factory=AdminSettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)
    metrics: MetricsSettings = Field(default_factory=MetricsSettings)
    tracing: TracingSettings = Field(default_factory=TracingSettings)
    sentry: SentrySettings = Field(default_factory=SentrySettings)

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment.lower() == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment.lower() == "production"


@lru_cache(maxsize=1)
def get_settings() -> AppSettings:
    """Get cached application settings singleton."""
    return AppSettings()
