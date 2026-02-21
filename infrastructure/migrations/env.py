"""Alembic migration environment."""
from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine, pool

from config.settings.base import get_settings
from infrastructure.database.models.base import Base

# Import all models for autogenerate
from infrastructure.database.models.users import User  # noqa: F401

# === IMPORT NEW MODELS FOR MIGRATION ABOVE ===

# Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata for 'autogenerate' support
target_metadata = Base.metadata

# Get database URL from settings (sync URL for psycopg2)
settings = get_settings()
config.set_main_option("sqlalchemy.url", settings.database.sync_url)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = create_engine(
        config.get_main_option("sqlalchemy.url"),
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()

    connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
