"""Database configuration settings."""

import ssl
from typing import Any
from urllib.parse import urlparse, urlunparse

from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine.url import URL


class DatabaseSettings(BaseSettings):
    """PostgreSQL database configuration.

    Supports two connection modes:
    - DATABASE_URL: single connection string (for external DBs like Supabase, Neon)
    - Individual POSTGRES__* fields (for docker-compose local development)
    """

    model_config = SettingsConfigDict(
        env_prefix="POSTGRES__",
        extra="ignore",
    )

    # External DB connection (takes priority over individual fields)
    database_url: str | None = Field(default=None, description="Full database URL")
    ssl_mode: str | None = Field(default=None, description="SSL mode (e.g. require)")

    # Individual connection fields (used when database_url is not set)
    db_host: str = Field(default="localhost", description="Database host")
    db_port: int = Field(default=5432, description="Database port")
    db_user: str = Field(default="postgres", description="Database user")
    db_password: SecretStr = Field(default=SecretStr("postgres"), description="Database password")
    db_name: str = Field(default="telegram_bot", description="Database name")

    # Connection pool settings
    pool_size: int = Field(default=10, description="SQLAlchemy pool size")
    max_overflow: int = Field(default=20, description="SQLAlchemy max overflow")
    pool_pre_ping: bool = Field(default=True, description="Enable pool pre-ping")
    pool_recycle: int = Field(default=3600, description="Pool recycle time in seconds")
    echo: bool = Field(default=False, description="Enable SQL query logging")

    @model_validator(mode="before")
    @classmethod
    def read_database_url(cls, values: dict[str, Any]) -> dict[str, Any]:
        """Read DATABASE_URL from env (without POSTGRES__ prefix)."""
        import os

        database_url = os.environ.get("DATABASE_URL")
        if database_url and "database_url" not in values:
            values["database_url"] = database_url

        ssl_mode = os.environ.get("SSL_MODE")
        if ssl_mode and "ssl_mode" not in values:
            values["ssl_mode"] = ssl_mode

        return values

    def _parse_database_url(self, driver: str) -> str:
        """Parse database_url and rebuild with the specified driver."""
        parsed = urlparse(self.database_url)

        # Replace scheme with the target driver
        scheme = driver

        # Remove sslmode from query params (asyncpg handles SSL via connect_args)
        query = parsed.query
        if driver == "postgresql+asyncpg" and query:
            params = [p for p in query.split("&") if not p.startswith("sslmode=")]
            query = "&".join(params)

        rebuilt = urlunparse(
            (
                scheme,
                parsed.netloc,
                parsed.path,
                parsed.params,
                query,
                parsed.fragment,
            )
        )

        return rebuilt

    @property
    def async_connect_args(self) -> dict[str, Any]:
        """Return connect_args for asyncpg (SSL context if needed)."""
        effective_ssl = self.ssl_mode

        # Auto-detect sslmode from database_url query params
        if not effective_ssl and self.database_url:
            parsed = urlparse(self.database_url)
            if parsed.query:
                for param in parsed.query.split("&"):
                    if param.startswith("sslmode="):
                        effective_ssl = param.split("=", 1)[1]
                        break

        if effective_ssl and effective_ssl != "disable":
            ctx = ssl.create_default_context()
            if effective_ssl == "require":
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
            return {"ssl": ctx}

        return {}

    @property
    def async_url(self) -> str:
        """Construct async SQLAlchemy URL for asyncpg."""
        if self.database_url:
            return self._parse_database_url("postgresql+asyncpg")

        uri = URL.create(
            drivername="postgresql+asyncpg",
            username=self.db_user,
            password=self.db_password.get_secret_value(),
            host=self.db_host,
            port=self.db_port,
            database=self.db_name,
        )
        return uri.render_as_string(hide_password=False)

    @property
    def sync_url(self) -> str:
        """Construct sync SQLAlchemy URL for psycopg2 (used in Alembic)."""
        if self.database_url:
            return self._parse_database_url("postgresql+psycopg2")

        uri = URL.create(
            drivername="postgresql+psycopg2",
            username=self.db_user,
            password=self.db_password.get_secret_value(),
            host=self.db_host,
            port=self.db_port,
            database=self.db_name,
        )
        return uri.render_as_string(hide_password=False)
