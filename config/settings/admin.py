"""Admin panel configuration settings."""
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class AdminSettings(BaseSettings):
    """Admin panel configuration."""

    model_config = SettingsConfigDict(
        env_prefix="ADMIN__",
        extra="ignore",
    )

    # Server settings
    host: str = Field(default="0.0.0.0", description="Admin panel host")
    port: int = Field(default=8000, description="Admin panel port")
    reload: bool = Field(default=False, description="Enable auto-reload in development")

    # Authentication
    secret_key: SecretStr = Field(
        default=SecretStr("change-me-in-production"),
        description="Secret key for session encryption"
    )
    admin_username: str = Field(default="admin", description="Admin username")
    admin_password: SecretStr = Field(
        default=SecretStr("admin"),
        description="Admin password (change in production!)"
    )

    # Session settings
    session_lifetime: int = Field(default=3600, description="Session lifetime in seconds")

    # CORS settings
    cors_origins: list[str] = Field(
        default_factory=lambda: ["*"],
        description="Allowed CORS origins"
    )

    # Features
    enable_swagger: bool = Field(default=True, description="Enable Swagger UI")
    enable_broadcast: bool = Field(default=True, description="Enable broadcast feature")
