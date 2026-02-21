# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a modern Telegram bot template v2 featuring microservices architecture with aiogram 3.13+, FastAPI admin panel, comprehensive monitoring (Prometheus/Grafana/Loki), and dependency injection via Dishka. The project follows clean architecture patterns with service layer, repository pattern, and Unit of Work.

## Development Commands

### Local Development
```bash
# Install dependencies
poetry install

# Install with dev dependencies
poetry install --with dev

# Run bot locally (requires .env file)
python3 apps/bot/main.py

# Run admin panel locally
python3 apps/admin/main.py
```

### Docker Development
```bash
# Start all services (bot, admin, PostgreSQL, Redis, monitoring stack)
docker compose up --build

# Start in detached mode
docker compose up -d --build

# Stop all services
docker compose down

# View specific service logs
docker compose logs -f bot
docker compose logs -f admin

# Rebuild specific service
docker compose up --build bot
```

### Database Migrations (Alembic)
```bash
# Create new migration (prompts for migration name)
sh scripts/alembic/create_migrations.sh

# Run migrations (apply to database)
sh scripts/alembic/run_migrations.sh

# Downgrade one migration
sh scripts/alembic/downgrade_migration.sh

# Manual migration commands inside container
docker compose exec bot alembic revision --autogenerate -m "migration_name"
docker compose exec bot alembic upgrade head
docker compose exec bot alembic downgrade -1
docker compose exec bot alembic current
```

Note: Migration scripts execute commands inside the `telegram_bot` container using `docker exec tg_bot`. The container name is `telegram_bot` for the bot service.

### Testing
```bash
# Run all tests
poetry run pytest

# Run with coverage report
poetry run pytest --cov=apps --cov=infrastructure --cov-report=html --cov-report=term-missing

# Run specific test file
poetry run pytest tests/unit/test_user_service.py

# Run specific test
poetry run pytest tests/unit/test_user_service.py::test_register_user
```

### Code Quality
```bash
# Linting
poetry run ruff check .

# Auto-fix linting issues
poetry run ruff check . --fix

# Type checking
poetry run mypy .

# Format check
poetry run ruff format --check .
```

## Architecture Overview

### Application Structure
The project uses a modular architecture with three main applications:

1. **apps/bot/** - Telegram bot service (aiogram 3.13+)
   - `main.py`: Entry point, bot initialization, polling setup
   - `di_container.py`: Dishka dependency injection configuration
   - `handlers/`: Message handlers organized by user type (user, admin, channel)
   - `services/`: Business logic layer (UserService, AnalyticsService)
   - `middlewares/`: Logging, metrics collection, DI injection

2. **apps/admin/** - Admin panel service (FastAPI + SQLAdmin)
   - `main.py`: FastAPI app entry point
   - `admin_panel/views/`: SQLAdmin model views for database management
   - `api/routes/`: REST API endpoints (users, stats)

3. **apps/worker/** - Background tasks (optional, Taskiq)

### Infrastructure Layer
Located in `infrastructure/`, provides core services:

- **database/**: Database layer with Repository + Unit of Work pattern
  - `core/session.py`: SQLAlchemy async engine and session management
  - `models/`: ORM models (User, AnalyticsEvent, etc.)
  - `repositories/`: Repository implementations extending BaseRepository
  - `uow.py`: Unit of Work for transaction management
  - Note: Old `requests.py` and `repo/` may exist but are deprecated in favor of `repositories/` and `uow.py`

- **cache/**: Redis caching layer
  - `redis_client.py`: Redis connection management
  - `cache_service.py`: High-level caching operations

- **monitoring/**: Observability stack
  - `logging.py`: Structured logging with structlog (JSON format)
  - `metrics.py`: Prometheus metrics collection

### Configuration System
Settings use Pydantic Settings with environment variable nesting via `__` delimiter:

- `config/settings/base.py`: Main AppSettings aggregator with `@lru_cache` singleton
- `config/settings/bot.py`: Bot token, admin IDs, feature flags
- `config/settings/database.py`: PostgreSQL and Redis configuration
- `config/settings/admin.py`: Admin panel settings (host, port, auth)
- `config/settings/observability.py`: Logging, metrics, tracing, Sentry

Environment variable format: `SECTION__KEY=value` (e.g., `POSTGRES__DB_HOST=localhost`, `BOT__ADMIN_IDS=[123,456]`)

### Dependency Injection (Dishka)
The DI container is configured in `apps/bot/di_container.py` with three provider groups:

1. **SettingsProvider** (Scope.APP): Application settings singleton
2. **InfrastructureProvider**: Database engine (APP scope), sessions (REQUEST scope), Redis, cache service, UnitOfWork
3. **ServiceProvider** (Scope.REQUEST): Business services (UserService, AnalyticsService)

Handlers receive dependencies via `FromDishka` type hints:
```python
@router.message(CommandStart())
async def cmd_start(
    message: Message,
    user_service: FromDishka[UserService],  # Auto-injected
):
    user = await user_service.register_or_update(message.from_user)
```

### Data Flow Patterns

**Repository Pattern** (`infrastructure/database/repositories/`):
- `BaseRepository[T]`: Generic CRUD operations (get, create, update, delete, get_all, count)
- `UserRepository`: User-specific queries (get_by_telegram_id, count_active_users)
- `AnalyticsRepository`: Analytics queries

**Unit of Work Pattern** (`infrastructure/database/uow.py`):
- Manages transactions across multiple repositories
- Provides `.users`, `.analytics` repository properties
- Supports context manager: `async with UnitOfWork(session) as uow:`
- Auto-commits on success, auto-rollbacks on exception

**Service Layer** (`apps/bot/services/`):
- Encapsulates business logic
- Uses UnitOfWork to coordinate multiple repositories
- Example: `UserService(uow, cache)` handles user registration, updates, analytics tracking

### Bot Middleware Chain
Middlewares registered in `apps/bot/main.py` via `register_middlewares()`:

1. **MetricsMiddleware**: Collects Prometheus metrics (messages, response times)
2. **LoggingMiddleware**: Structured logging with user context
3. **Dishka DI Middleware** (via `setup_dishka()`): Injects dependencies into handlers

### Handler Organization
Handlers in `apps/bot/handlers/` are organized by user type:
- `user/`: User commands and interactions
- `admin/`: Admin-only commands (with admin filters)
- `channel/`: Channel post handlers
- `errors/`: Error handling routers

All routers are registered in `main.py` via `register_routers()`.

## Monitoring & Observability

### Service URLs (via Docker Compose)
- **Bot**: N/A (polling mode)
- **Admin Panel**: http://localhost:8000 (API docs: /api/docs)
- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9091
- **Dozzle** (logs viewer): http://localhost:8888
- **Bot Metrics Endpoint**: http://localhost:9090/metrics

### Metrics (Prometheus)
The bot exposes metrics on port 9090. Common metrics:
- `bot_messages_total{handler, status}`: Total messages processed
- `bot_commands_total{command}`: Commands executed
- `bot_errors_total{error_type}`: Errors occurred
- `bot_response_time_seconds{handler}`: Response time histogram
- `bot_active_users{period}`: Active users gauge

### Logging (Structlog + Loki)
All logs are in structured JSON format:
```json
{
  "event": "bot_event_processed",
  "user_id": 123,
  "duration_ms": 45,
  "level": "info",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

Pipeline: App → Structlog → Docker logs → Promtail → Loki → Grafana

## Common Patterns

### Adding New Database Models
1. Create model in `infrastructure/database/models/your_model.py`
2. Create repository in `infrastructure/database/repositories/your_repository.py` extending `BaseRepository[YourModel]`
3. Add repository property to `UnitOfWork` in `infrastructure/database/uow.py`:
   ```python
   @property
   def your_model(self) -> YourRepository:
       if self._your_model is None:
           self._your_model = YourRepository(self.session)
       return self._your_model
   ```
4. Create migration: `sh scripts/alembic/create_migrations.sh`
5. Run migration: `sh scripts/alembic/run_migrations.sh`

### Adding New Services
1. Create service in `apps/bot/services/your_service.py`
2. Add provider to `ServiceProvider` in `apps/bot/di_container.py`:
   ```python
   @provide
   def get_your_service(self, uow: UnitOfWork) -> YourService:
       return YourService(uow)
   ```
3. Inject in handlers: `your_service: FromDishka[YourService]`

### Adding New Handlers
1. Create handler file in `apps/bot/handlers/<category>/your_handler.py`
2. Register router in `apps/bot/main.py` in `register_routers()`:
   ```python
   from apps.bot.handlers.user import your_handler
   dp.include_router(your_handler.router)
   ```

### Adding Admin Panel Views
1. Create view in `apps/admin/admin_panel/views/your_admin.py` extending `ModelView`
2. Register in `apps/admin/main.py`:
   ```python
   from apps.admin.admin_panel.views.your_admin import YourAdmin
   admin.add_view(YourAdmin)
   ```

### Adding API Endpoints
1. Create router file in `apps/admin/api/routes/your_route.py`
2. Include in `apps/admin/main.py`:
   ```python
   from apps.admin.api.routes import your_route
   app.include_router(your_route.router, prefix="/api", tags=["your_tag"])
   ```

## Docker Services

The `docker-compose.yml` orchestrates these services:

**Core Services**:
- `postgres`: PostgreSQL 16 (port 5432)
- `redis`: Redis 7 (port 6379)
- `bot`: Telegram bot container (metrics port 9090)
- `admin`: Admin panel FastAPI app (port 8000)

**Monitoring Stack**:
- `prometheus`: Metrics storage (port 9091)
- `grafana`: Metrics visualization (port 3000)
- `loki`: Log aggregation (port 3100)
- `promtail`: Log collector (reads Docker container logs)

**Development Tools**:
- `dozzle`: Real-time container logs viewer (port 8888)

All services communicate via `bot_network` bridge network.

## Important Notes

### Environment Variables
- Use `.env` file (copy from `.env.example`)
- Nested settings use `__` delimiter: `POSTGRES__DB_HOST`, `BOT__ADMIN_IDS`
- Admin IDs must be a JSON array: `BOT__ADMIN_IDS=[123456789,987654321]`

### Database Sessions
- Always use async sessions from Dishka injection
- Sessions are REQUEST scoped (created per handler invocation)
- UnitOfWork automatically manages commits/rollbacks when used as context manager
- Never create sessions manually; use DI

### Container Names
- Bot container: `telegram_bot`
- Admin container: `admin_panel`
- Use these names for `docker exec` commands

### Migration Workflow
- Alembic migrations auto-run on bot container startup (via entrypoint)
- Always create migrations before modifying database schema
- Test migrations with `alembic upgrade head` then `alembic downgrade -1` before committing

### Settings Singleton
- `get_settings()` uses `@lru_cache` to return singleton instance
- Settings are immutable after first load
- Restart application to reload settings changes