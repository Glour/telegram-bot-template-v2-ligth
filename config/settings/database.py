"""Database configuration settings."""
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine.url import URL


class DatabaseSettings(BaseSettings):
    """PostgreSQL database configuration."""

    model_config = SettingsConfigDict(
        env_prefix="POSTGRES__",
        extra="ignore",
    )

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

    @property
    def async_url(self) -> str:
        """Construct async SQLAlchemy URL for asyncpg."""
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
        uri = URL.create(
            drivername="postgresql+psycopg2",
            username=self.db_user,
            password=self.db_password.get_secret_value(),
            host=self.db_host,
            port=self.db_port,
            database=self.db_name,
        )
        return uri.render_as_string(hide_password=False)


class RedisSettings(BaseSettings):
    """Redis cache configuration."""

    model_config = SettingsConfigDict(
        env_prefix="REDIS__",
        extra="ignore",
    )

    host: str = Field(default="localhost", description="Redis host")
    port: int = Field(default=6379, description="Redis port")
    db: int = Field(default=0, description="Redis database number")
    password: SecretStr | None = Field(default=None, description="Redis password")

    # Connection settings
    decode_responses: bool = Field(default=False, description="Decode responses to strings")
    max_connections: int = Field(default=50, description="Max connections in pool")
    socket_timeout: int = Field(default=5, description="Socket timeout in seconds")
    socket_connect_timeout: int = Field(default=5, description="Socket connect timeout")

    @property
    def url(self) -> str:
        """Construct Redis URL."""
        if self.password:
            pwd = self.password.get_secret_value()
            return f"redis://:{pwd}@{self.host}:{self.port}/{self.db}"
        return f"redis://{self.host}:{self.port}/{self.db}"
