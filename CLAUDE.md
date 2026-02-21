# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Lightweight Telegram bot template v2-light: aiogram 3.13+, PostgreSQL, Dishka DI, Repository + Unit of Work pattern. Supports two deployment modes: standalone Docker container with external DB, or docker-compose with local PostgreSQL.

**For AI bot generation, see [AI_GENERATION_GUIDE.md](AI_GENERATION_GUIDE.md)** — full guide with registration checklists, code templates, and worked examples.

## Deployment Modes

### Standalone Docker (external DB)
```bash
docker build -t bot .
docker run --env-file .env -e DATABASE_URL="postgresql://user:pass@host:5432/db?sslmode=require" bot
```
Uses root `Dockerfile`. Auto-runs `alembic upgrade head` on startup.

### Docker Compose (local development)
```bash
docker compose up --build
```
Uses `apps/bot/Dockerfile` + local PostgreSQL container. Connection via `POSTGRES__*` env vars.

### Local Development
```bash
poetry install
poetry install --with dev
python3 apps/bot/main.py
```

## Development Commands

### Database Migrations (Alembic)
```bash
sh scripts/alembic/create_migrations.sh
sh scripts/alembic/run_migrations.sh
sh scripts/alembic/downgrade_migration.sh
```

Scripts auto-detect environment: if `telegram_bot` container is running, use `docker exec`; otherwise run `alembic` directly.

```bash
# Manual commands inside container
docker compose exec bot alembic revision --autogenerate -m "migration_name"
docker compose exec bot alembic upgrade head
docker compose exec bot alembic downgrade -1
```

### Testing
```bash
poetry run pytest
poetry run pytest --cov=apps --cov=infrastructure --cov-report=html --cov-report=term-missing
```

### Code Quality
```bash
poetry run ruff check .
poetry run ruff check . --fix
poetry run mypy .
poetry run ruff format --check .
```

## Architecture Overview

### Application Structure

**apps/bot/** — Telegram bot service (aiogram 3.13+)
- `main.py`: Entry point, bot initialization, polling setup
- `di_container.py`: Dishka dependency injection configuration
- `handlers/user/`: User-facing handlers (start.py)
- `handlers/errors.py`: Global error handler
- `services/`: Business logic layer (UserService)
- `keyboards/`: Inline/Reply keyboard builders
- `filters/`: Custom aiogram filters (IsAdminFilter)
- `states/`: FSM states for multi-step interactions
- `middlewares/`: Event logging

### Infrastructure Layer (`infrastructure/`)

- **database/core/session.py**: SQLAlchemy async engine and session management
- **database/models/**: ORM models (User) with mixins (Base, TableNameMixin, TimestampMixin)
- **database/repositories/**: Repository implementations (BaseRepository, UserRepository)
- **database/uow.py**: Unit of Work for transaction management
- **monitoring/logging.py**: Standard Python logging setup

### Configuration System (`config/settings/`)

Settings use Pydantic Settings with `__` delimiter:
- `base.py`: AppSettings aggregator + LoggingSettings, `@lru_cache` singleton
- `bot.py`: BotSettings (token, admin_ids)
- `database.py`: DatabaseSettings (PostgreSQL connection)

Environment variable format: `SECTION__KEY=value` (e.g., `POSTGRES__DB_HOST=localhost`)

Database connection supports two modes:
- `DATABASE_URL` env var — single connection string for external DBs (Supabase, Neon). Parsed via `model_validator(mode="before")`.
- `POSTGRES__*` fields — individual fields for docker-compose. Used when `DATABASE_URL` is not set.
- `SSL_MODE` env var — SSL mode for external DBs (e.g., `require`). Auto-detected from `?sslmode=` in DATABASE_URL if not set explicitly.

### Shared Layer (`shared/`)

- `dto/`: Data Transfer Objects (UserCreateDTO, UserUpdateDTO, UserResponseDTO)
- `enums/`: Application enums (UserRole, UserStatus, Language)
- `exceptions/`: Exception hierarchy (AppException, NotFoundError, ValidationError, etc.)

### Dependency Injection (Dishka)

DI container in `apps/bot/di_container.py` with three provider groups:
1. **SettingsProvider** (Scope.APP): Settings singleton
2. **InfrastructureProvider**: Engine (APP scope), Session (REQUEST scope), UnitOfWork (REQUEST)
3. **ServiceProvider** (Scope.REQUEST): UserService

Handlers receive dependencies via `FromDishka` type hints:
```python
@router.message(CommandStart())
async def cmd_start(
    message: Message,
    user_service: FromDishka[UserService],
):
    user = await user_service.register_or_update(message.from_user)
```

### Data Flow Patterns

**Repository Pattern**: `BaseRepository[T]` with generic CRUD, `UserRepository` with user-specific queries.

**Unit of Work**: Manages transactions, provides `.users` property, auto-commits/rollbacks via DI provider.

**Service Layer**: `UserService(uow)` encapsulates business logic.

## Marker Comments

The codebase uses marker comments to indicate registration points for new components. When adding new code, insert it **before** the marker line.

| Marker | File | Purpose |
|--------|------|---------|
| `# === REGISTER NEW ROUTERS ABOVE ===` | `apps/bot/main.py` | Router registration |
| `# === REGISTER NEW SERVICES ABOVE ===` | `apps/bot/di_container.py` | Service DI providers |
| `# === REGISTER NEW REPOSITORIES ABOVE ===` | `infrastructure/database/uow.py` | Repository properties |
| `# === IMPORT NEW REPOSITORIES ABOVE ===` | `infrastructure/database/repositories/__init__.py` | Repository imports |
| `# === EXPORT NEW REPOSITORIES ABOVE ===` | `infrastructure/database/repositories/__init__.py` | Repository __all__ exports |
| `# === IMPORT NEW MODELS ABOVE ===` | `infrastructure/database/models/__init__.py` | Model imports |
| `# === IMPORT NEW MODELS FOR MIGRATION ABOVE ===` | `infrastructure/migrations/env.py` | Model imports for Alembic |

## Common Patterns

### Adding New Database Models
1. Create model in `infrastructure/database/models/`
2. Add import in `infrastructure/database/models/__init__.py` (before marker)
3. Add import in `infrastructure/migrations/env.py` (before marker)
4. Create repository extending `BaseRepository[YourModel]`
5. Register repository in `infrastructure/database/repositories/__init__.py` (before markers)
6. Add repository property to `UnitOfWork` in `infrastructure/database/uow.py` (before marker)
7. Create migration: `sh scripts/alembic/create_migrations.sh`

### Adding New Services
1. Create service in `apps/bot/services/`
2. Add import and `@provide` method to `ServiceProvider` in `di_container.py` (before marker)
3. Inject in handlers: `your_service: FromDishka[YourService]`

### Adding New Handlers
1. Create handler in `apps/bot/handlers/<category>/`
2. Register router in `apps/bot/main.py` in `register_routers()` (before marker)

## Docker

### Standalone Dockerfile (root)
- `Dockerfile` — single container for deployment with external DB
- CMD: `alembic upgrade head && python3 apps/bot/main.py`
- Requires `DATABASE_URL` env var

### Docker Compose Services
- `postgres`: PostgreSQL 16 (port 5432)
- `bot`: Telegram bot container (`telegram_bot`), uses `apps/bot/Dockerfile`

All compose services communicate via `bot_network` bridge network.

## Important Notes

### Environment Variables
- Use `.env` file (copy from `.env.example`)
- Nested settings use `__` delimiter
- Admin IDs must be a JSON array: `BOT__ADMIN_IDS=[123456789]`

### Database Sessions
- Always use async sessions from Dishka injection (REQUEST scoped)
- Commits are managed by `InfrastructureProvider.get_session`, not by repositories
- Repositories use `session.flush()`, not `session.commit()`
- Never create sessions manually; use DI

### DI Integration
- `auto_inject=True` is enabled — do NOT use old DI middleware or `inject` decorator
- Use `FromDishka[ServiceType]` in handler function signatures
- ParseMode.HTML is set as default — use HTML tags in bot messages

### Container Names
- Bot container: `telegram_bot`

### Settings Singleton
- `get_settings()` uses `@lru_cache` to return singleton instance
- Settings are immutable after first load
- Restart application to reload settings changes
