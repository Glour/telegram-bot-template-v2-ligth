# Telegram Bot Template v2 Light

Lightweight Telegram bot template with clean architecture: **aiogram 3.13+**, **PostgreSQL**, **Dishka DI**, **Repository + Unit of Work**.

## Stack

- **aiogram 3.13+** — Telegram Bot framework
- **PostgreSQL 16** — database
- **SQLAlchemy 2.0** (async) — ORM
- **Alembic** — migrations
- **Dishka** — dependency injection
- **Pydantic Settings** — configuration

## Quick Start

### 1. Setup

```bash
cp .env.example .env
# Edit .env — set your BOT__TOKEN
```

### 2. Run

**Docker Compose** (local PostgreSQL):
```bash
docker compose up --build
```

**Standalone Docker** (external DB — Supabase, Neon, etc.):
```bash
docker build -t bot .
docker run --env-file .env -e DATABASE_URL="postgresql://user:pass@host:5432/db?sslmode=require" bot
```

### 3. Migrations

```bash
# Create migration
sh scripts/alembic/create_migrations.sh

# Apply migrations
sh scripts/alembic/run_migrations.sh

# Rollback
sh scripts/alembic/downgrade_migration.sh
```

## Project Structure

```
apps/bot/
  main.py                — entry point, polling
  di_container.py        — Dishka DI container
  handlers/user/
    start.py             — /start command
  services/
    user_service.py      — user business logic
  middlewares/
    logging_middleware.py — event logging
  Dockerfile

infrastructure/
  database/
    core/session.py      — AsyncEngine + session factory
    models/
      base.py            — Base, mixins
      users.py           — User model
    repositories/
      base.py            — BaseRepository[T]
      user_repository.py — UserRepository
    uow.py               — Unit of Work
  monitoring/
    logging.py           — standard Python logging
  migrations/            — Alembic migrations

config/settings/
  base.py                — AppSettings + LoggingSettings
  bot.py                 — BotSettings
  database.py            — DatabaseSettings

shared/
  dto/user.py            — UserCreateDTO, UserResponseDTO
  enums/                 — UserRole, UserStatus, Language
  exceptions/            — NotFoundError, etc.

Dockerfile               — standalone (external DB)
docker-compose.yml       — postgres + bot (local dev)
```

## Usage Examples

### Handler with DI

```python
@router.message(CommandStart())
async def cmd_start(
    message: Message,
    user_service: FromDishka[UserService],
):
    user = await user_service.register_or_update(message.from_user)
    await message.answer(f"Hello, {user.first_name}!")
```

### Adding New Models

1. Create model in `infrastructure/database/models/`
2. Create repository in `infrastructure/database/repositories/`
3. Add property to `UnitOfWork` in `uow.py`
4. Create migration: `sh scripts/alembic/create_migrations.sh`
5. Apply: `sh scripts/alembic/run_migrations.sh`

### Adding New Services

1. Create service in `apps/bot/services/`
2. Add provider to `di_container.py`
3. Inject in handlers: `service: FromDishka[YourService]`

## Development

```bash
# Install dependencies
poetry install --with dev

# Run locally
python3 apps/bot/main.py

# Linting
poetry run ruff check .

# Type checking
poetry run mypy .

# Tests
poetry run pytest
```

## License

MIT
