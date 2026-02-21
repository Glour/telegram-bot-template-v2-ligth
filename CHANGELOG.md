# Changelog

All notable changes to this project will be documented in this file.

## [2.0.0] - 2026-01-01

### 🎉 Major Release - Complete Architecture Overhaul

This is a complete rewrite of the Telegram bot template with modern architecture and best practices.

### ✨ Added

#### Architecture
- **Modular Structure**: Separated into `apps/` (bot, admin, worker)
- **Service Layer**: Business logic separated from handlers
- **Unit of Work Pattern**: Transaction management across repositories
- **Repository Pattern**: Database abstraction layer
- **Dependency Injection**: Using Dishka for clean DI

#### New Applications
- **Admin Panel**: FastAPI + SQLAdmin for database management
  - User CRUD operations
  - Statistics dashboard
  - REST API endpoints
  - Swagger documentation

#### Monitoring & Observability
- **Structured Logging**: JSON logs with Structlog
- **Metrics Collection**: Prometheus metrics
- **Visualization**: Grafana dashboards
- **Log Aggregation**: Loki + Promtail
- **Real-time Logs**: Dozzle for development

#### Database
- **Enhanced Models**:
  - User model with roles, status, referrals, analytics
  - AnalyticsEvent model for event tracking
- **Improved Schema**: Proper indexes, relationships
- **Better Migrations**: Updated Alembic setup

#### Features
- **Analytics System**: Event tracking and metrics
- **Cache Layer**: Redis integration with high-level API
- **DTOs**: Pydantic models for data transfer
- **Enums**: Type-safe enumerations
- **Exception Hierarchy**: Custom exceptions

#### Configuration
- **Pydantic Settings**: Type-safe configuration
- **Environment Variables**: Proper env var support
- **Multiple Environments**: Dev, staging, production
- **Secret Management**: SecretStr for sensitive data

### 🔄 Changed

#### From legacy to v1

**Project Structure**:
```
OLD:                          NEW:
tg_bot/                       apps/bot/
├── main.py                   ├── main.py
├── handlers/                 ├── handlers/
├── middlewares/              ├── services/      # NEW
└── ...                       ├── middlewares/
                              └── di_container.py # NEW

settings/                     config/settings/
infrastructure/               infrastructure/
├── database/                 ├── database/
│   ├── setup.py              │   ├── core/      # NEW structure
│   ├── models/               │   ├── models/
│   ├── repo/                 │   ├── repositories/
│   └── requests.py           │   └── uow.py     # NEW
└── ...                       ├── cache/         # NEW
                              └── monitoring/    # NEW
```

**Key Changes**:
- ❌ Removed `betterlogging` → ✅ Added `structlog`
- ❌ Removed `APScheduler` → ✅ Added `Taskiq` (ready for use)
- ❌ Removed manual DI → ✅ Added `Dishka`
- ❌ Removed direct repo access → ✅ Added Service Layer + UoW
- ✅ PostgreSQL 15 → PostgreSQL 16
- ✅ Redis 7.0 → Redis 7+ (Alpine)
- ✅ Added FastAPI for admin panel
- ✅ Added full monitoring stack

### 📦 Dependencies

**Added**:
- `fastapi ^0.115` - Admin panel
- `uvicorn ^0.30` - ASGI server
- `sqladmin ^0.18` - Admin interface
- `dishka ^1.3` - Dependency injection
- `structlog ^24.1` - Structured logging
- `prometheus-client ^0.20` - Metrics
- `taskiq ^0.11` - Task queue (optional)
- `pytest ^8.0` - Testing
- `ruff ^0.6` - Linting
- `mypy ^1.11` - Type checking

**Updated**:
- `aiogram 3.13` (from 3.13.1)
- `pydantic 2.9` (from 2.9.2)
- `sqlalchemy 2.0` (from 2.0.29)
- `redis 5.0` (from 4.5)

**Removed**:
- `betterlogging`
- `apscheduler` (replaced with Taskiq)

### 🐳 Docker

**New Services**:
- `admin` - Admin panel (port 8000)
- `prometheus` - Metrics storage (port 9091)
- `grafana` - Dashboards (port 3000)
- `loki` - Log aggregation (port 3100)
- `promtail` - Log collector

**Updated**:
- PostgreSQL 15.3 → 16-alpine
- Redis 7.0.11 → 7-alpine
- Multi-stage builds for bot and admin

### 📊 Monitoring

**Metrics**:
- Bot messages, commands, errors
- Response times (histogram)
- Active users (gauge)
- Database connections

**Logs**:
- Structured JSON format
- Automatic Docker log collection
- Searchable in Grafana via Loki

**Dashboards**:
- Bot overview
- Database performance
- System resources

### 🔒 Security

- Secret management with `SecretStr`
- CORS configuration for admin
- Rate limiting middleware (ready)
- SQL injection protection (SQLAlchemy ORM)

### 📝 Documentation

- **README.md**: Complete setup guide
- **ARCHITECTURE.md**: Architecture documentation
- **CHANGELOG.md**: This file
- **CLAUDE.md**: AI assistant instructions (updated)

### 🧪 Testing

- Test structure setup (`tests/`)
- Pytest configuration
- Coverage reporting
- Type checking with mypy

### 🛠️ Developer Experience

- **Pre-commit hooks**: Ready to setup
- **Ruff**: Fast Python linter
- **Mypy**: Static type checking
- **Rich**: Beautiful terminal output
- **IPython**: Enhanced REPL

### ⚡ Performance

- Connection pooling (10/20)
- Database indexes on key columns
- Redis caching for stats
- Async everywhere
- Query optimization

### 🎯 Migration Guide from v2

1. **Update dependencies**:
   ```bash
   poetry install
   ```

2. **Update environment variables**:
   - Copy `.env.example` to `.env`
   - Update settings structure (double underscore notation)

3. **Update imports**:
   ```python
   # OLD
   from settings import get_app_settings
   from infrastructure.database.requests import RequestsRepo

   # NEW
   from config.settings.base import get_settings
   from infrastructure.database.uow import UnitOfWork
   ```

4. **Update handlers**:
   ```python
   # OLD
   async def handler(message: Message, repo: RequestsRepo):
       user = await repo.users.get(...)

   # NEW
   async def handler(
       message: Message,
       user_service: FromDishka[UserService],
   ):
       user = await user_service.get_user(...)
   ```

5. **Run new migrations**:
   ```bash
   alembic upgrade head
   ```

### 🐛 Bug Fixes

- Fixed session management issues
- Fixed circular import problems
- Fixed migration autogenerate
- Improved error handling

### 📈 Statistics (Lines of Code)

- **Total**: ~3000+ lines
- **New Code**: ~2000 lines
- **Refactored**: ~1000 lines
- **Files Created**: 50+
- **Files Modified**: 15+

### 🙏 Credits

Built with modern Python best practices and inspired by:
- Clean Architecture
- Domain-Driven Design
- Microservices patterns
- 12-Factor App

---

## [2.0.0] - Previous Version

### Features
- Basic bot structure
- PostgreSQL + Redis
- Alembic migrations
- i18n support
- APScheduler
- Dozzle logging

---

## [1.0.0] - Initial Release

### Features
- Basic Telegram bot
- Simple structure
- SQLite database
