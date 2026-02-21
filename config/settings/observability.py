"""Observability configuration (logging, metrics, tracing)."""
import logging

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class LoggingSettings(BaseSettings):
    """Logging configuration."""

    model_config = SettingsConfigDict(
        env_prefix="LOGGING__",
        extra="ignore",
    )

    level: str = Field(default="INFO", description="Logging level")
    format: str = Field(default="json", description="Log format: json or console")

    # Structured logging
    include_timestamp: bool = Field(default=True, description="Include timestamp in logs")
    include_caller: bool = Field(default=True, description="Include caller info")

    # File logging
    log_to_file: bool = Field(default=False, description="Enable file logging")
    log_file_path: str = Field(default="logs/bot.log", description="Log file path")
    log_rotation: str = Field(default="1 day", description="Log rotation period")
    log_retention: str = Field(default="7 days", description="Log retention period")

    @property
    def log_level(self) -> int:
        """Convert string level to logging constant."""
        return getattr(logging, self.level.upper(), logging.INFO)


class MetricsSettings(BaseSettings):
    """Prometheus metrics configuration."""

    model_config = SettingsConfigDict(
        env_prefix="METRICS__",
        extra="ignore",
    )

    enabled: bool = Field(default=True, description="Enable metrics collection")
    port: int = Field(default=9090, description="Metrics exposition port")
    include_default: bool = Field(default=True, description="Include default Python metrics")


class TracingSettings(BaseSettings):
    """Tracing configuration (optional)."""

    model_config = SettingsConfigDict(
        env_prefix="TRACING__",
        extra="ignore",
    )

    enabled: bool = Field(default=False, description="Enable distributed tracing")
    service_name: str = Field(default="telegram-bot", description="Service name for tracing")
    jaeger_host: str | None = Field(default=None, description="Jaeger agent host")
    jaeger_port: int = Field(default=6831, description="Jaeger agent port")


class SentrySettings(BaseSettings):
    """Sentry error tracking configuration."""

    model_config = SettingsConfigDict(
        env_prefix="SENTRY__",
        extra="ignore",
    )

    enabled: bool = Field(default=False, description="Enable Sentry error tracking")
    dsn: str | None = Field(default=None, description="Sentry DSN")
    environment: str = Field(default="development", description="Environment name")
    traces_sample_rate: float = Field(default=0.1, description="Traces sample rate (0.0-1.0)")
