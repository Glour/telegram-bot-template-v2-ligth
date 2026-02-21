# Telegram Bot Template v2 🤖

Modern Telegram bot template with **microservices architecture**, built-in **admin panel**, **monitoring**, and **analytics**.

## ✨ Features

### Architecture
- 🏗️ **Modular Structure** - Clean separation of concerns (apps/bot, apps/admin, apps/worker)
- 💉 **Dependency Injection** - Using Dishka for proper DI
- 📦 **Service Layer** - Business logic separated from handlers
- 🔄 **Unit of Work Pattern** - Transaction management
- 📊 **Repository Pattern** - Database abstraction

### Technology Stack
- **Bot Framework**: aiogram 3.13+
- **Web Framework**: FastAPI 0.115+
- **Database**: PostgreSQL 16
- **Cache**: Redis 7
- **ORM**: SQLAlchemy 2.0 (async)
- **Validation**: Pydantic 2.9
- **DI**: Dishka 1.3
- **Admin**: SQLAdmin 0.18

### Monitoring & Observability
- **Metrics**: Prometheus + Grafana
- **Logging**: Structlog + Loki + Promtail
- **Structured Logging**: JSON format with context
- **Real-time Logs**: Dozzle for development

### Admin Panel
- 📊 **Dashboard** - User stats, analytics, metrics
- 👥 **User Management** - CRUD operations, filtering, search
- 📡 **API** - REST endpoints for integrations
- 📈 **Analytics** - Event tracking and visualization

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Docker & Docker Compose
- Poetry (for local development)

### 1. Clone & Setup

```bash
# Clone repository
git clone <repo-url>
cd telegram-bot-template-v2

# Copy environment file
cp .env.example .env

# Edit .env and add your bot token
nano .env  # or vim/code .env
```

### 2. Run with Docker Compose

```bash
# Build and start all services
docker compose up --build

# Or in detached mode
docker compose up -d --build
```

### 3. Access Services

| Service | URL                            | Description |
|---------|--------------------------------|-------------|
| **Bot** | -                              | Telegram bot (polling) |
| **Admin Panel** | http://localhost:8000/admin        | SQLAdmin dashboard |
| **Admin API** | http://localhost:8000/api/docs | Swagger UI |
| **Grafana** | http://localhost:3000          | Metrics dashboards (admin/admin) |
| **Prometheus** | http://localhost:9091          | Metrics storage |
| **Dozzle** | http://localhost:8888          | Container logs viewer |

### 4. Database Migrations

```bash
# Create migration
docker compose exec bot alembic revision --autogenerate -m "migration_name"

# Apply migrations
docker compose exec bot alembic upgrade head

# Rollback
docker compose exec bot alembic downgrade -1
```

## 📁 Project Structure

```
telegram-bot-v2/
├── apps/
│   ├── bot/                    # Telegram Bot Service
│   │   ├── handlers/           # Message handlers
│   │   ├── services/           # Business logic
│   │   ├── middlewares/        # Bot middlewares
│   │   ├── di_container.py     # DI setup
│   │   └── main.py             # Bot entry point
│   ├── admin/                  # Admin Panel Service
│   │   ├── api/                # REST API routes
│   │   ├── admin_panel/        # SQLAdmin views
│   │   └── main.py             # FastAPI app
│   └── worker/                 # Background Tasks (optional)
├── infrastructure/
│   ├── database/               # Database layer
│   │   ├── core/               # Engine, session
│   │   ├── models/             # SQLAlchemy models
│   │   ├── repositories/       # Repository pattern
│   │   └── uow.py              # Unit of Work
│   ├── cache/                  # Redis layer
│   ├── monitoring/             # Logging, metrics
│   └── messaging/              # Event bus (optional)
├── shared/
│   ├── dto/                    # Data Transfer Objects
│   ├── exceptions/             # Custom exceptions
│   ├── enums/                  # Enumerations
│   └── utils/                  # Utilities
├── config/
│   └── settings/               # Pydantic settings
├── monitoring/
│   ├── prometheus/             # Prometheus config
│   ├── grafana/                # Grafana dashboards
│   ├── loki/                   # Loki config
│   └── promtail/               # Promtail config
├── tests/                      # Tests
├── docker-compose.yml          # Docker setup
└── pyproject.toml              # Dependencies
```

## 🎯 Usage Examples

### Handler with DI

```python
from aiogram import Router
from dishka import FromDishka

from apps.bot.services.user_service import UserService

router = Router()

@router.message(CommandStart())
async def cmd_start(
    message: Message,
    user_service: FromDishka[UserService],  # Auto-injected
):
    user = await user_service.register_or_update(message.from_user)
    await message.answer(f"Hello, {user.first_name}!")
```

### Service Layer

```python
class UserService:
    def __init__(self, uow: UnitOfWork, cache: CacheService):
        self.uow = uow
        self.cache = cache

    async def register_or_update(self, telegram_user: TelegramUser) -> User:
        dto = UserCreateDTO(...)
        user, created = await self.uow.users.get_or_create(dto)

        if created:
            await self.uow.analytics.track_event(...)

        return user
```

### Repository

```python
class UserRepository(BaseRepository[User]):
    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        return await self.get_by(telegram_id=telegram_id)

    async def count_active_users(self, period_hours: int = 24) -> int:
        since = datetime.utcnow() - timedelta(hours=period_hours)
        stmt = select(func.count()).select_from(User)...
        return result.scalar() or 0
```

## 📊 Monitoring

### Metrics Available

- `bot_messages_total` - Total messages processed
- `bot_commands_total` - Commands executed
- `bot_errors_total` - Errors occurred
- `bot_response_time_seconds` - Response time histogram
- `bot_active_users` - Active users gauge

### Grafana Dashboards

1. **Bot Overview** - Messages, users, errors
2. **Database Performance** - Query times, connections
3. **System Metrics** - CPU, memory, disk

### Structured Logging

All logs in JSON format:

```json
{
  "event": "user_action",
  "user_id": 123,
  "action": "start_command",
  "duration_ms": 45,
  "timestamp": "2024-01-15T10:30:00Z",
  "level": "info"
}
```

## 🧪 Testing

```bash
# Install dev dependencies
poetry install --with dev

# Run tests
poetry run pytest

# With coverage
poetry run pytest --cov=apps --cov=infrastructure

# Linting
poetry run ruff check .
poetry run mypy .
```

## 🚢 Deployment

### Production

1. Update `.env` with production values
2. Set `ENVIRONMENT=production`
3. Change admin passwords
4. Deploy:

```bash
docker compose -f docker-compose.yml up -d --build
```

### VPS Requirements

**Minimum**:
- 2 CPU cores
- 4GB RAM
- 40GB SSD
- **Cost**: ~€5-12/month (Hetzner, Contabo)

## 📚 Documentation

### Adding New Models

1. Create model in `infrastructure/database/models/`
2. Create repository in `infrastructure/database/repositories/`
3. Add to `UnitOfWork` in `uow.py`
4. Create migration: `alembic revision --autogenerate -m "add_model"`
5. Apply: `alembic upgrade head`

### Adding New Services

1. Create service in `apps/bot/services/`
2. Add provider to `di_container.py`
3. Inject in handlers: `service: FromDishka[YourService]`

### Adding Admin Views

1. Create view in `apps/admin/admin_panel/views/`
2. Register in `main.py`: `admin.add_view(YourView)`

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

## 📄 License

MIT License - see LICENSE file

## 🙏 Acknowledgments

- [aiogram](https://github.com/aiogram/aiogram) - Telegram Bot framework
- [FastAPI](https://github.com/tiangolo/fastapi) - Web framework
- [SQLAdmin](https://github.com/aminalaee/sqladmin) - Admin interface
- [Dishka](https://github.com/reagento/dishka) - Dependency injection
- [Structlog](https://github.com/hynek/structlog) - Structured logging

