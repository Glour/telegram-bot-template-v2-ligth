# Architecture Documentation

## Overview

This project implements a modern microservices-ready architecture for a Telegram bot with built-in observability, admin panel, and analytics.

## Architecture Layers

### 1. Application Layer (`apps/`)

#### Bot Service (`apps/bot/`)
- **Entry Point**: `main.py`
- **Handlers**: Message handlers organized by user type (user, admin, channel)
- **Services**: Business logic layer (UserService, AnalyticsService)
- **Middlewares**: DI, Logging, Metrics collection
- **DI Container**: Dishka-based dependency injection setup

**Key Components**:
- `di_container.py` - Dependency injection configuration
- `services/` - Business logic implementation
- `handlers/` - Telegram message handlers
- `middlewares/` - Request/response processing

#### Admin Panel (`apps/admin/`)
- **Entry Point**: `main.py`
- **Framework**: FastAPI
- **Admin Interface**: SQLAdmin
- **API Routes**: REST endpoints for user management, stats

**Key Components**:
- `admin_panel/views/` - SQLAdmin model views
- `api/routes/` - REST API endpoints

### 2. Infrastructure Layer (`infrastructure/`)

#### Database (`infrastructure/database/`)
**Pattern**: Repository + Unit of Work

Components:
- `core/session.py` - Database engine and session management
- `models/` - SQLAlchemy ORM models
- `repositories/` - Repository pattern implementation
- `uow.py` - Unit of Work for transaction management

**Models**:
- `User` - User model with role, status, referrals
- `AnalyticsEvent` - Event tracking model

**Repositories**:
- `BaseRepository` - Generic CRUD operations
- `UserRepository` - User-specific queries
- `AnalyticsRepository` - Analytics queries

#### Cache (`infrastructure/cache/`)
- `redis_client.py` - Redis connection management
- `cache_service.py` - High-level caching operations

#### Monitoring (`infrastructure/monitoring/`)
- `logging.py` - Structured logging with structlog
- `metrics.py` - Prometheus metrics collection

### 3. Shared Layer (`shared/`)

#### DTOs (`shared/dto/`)
Pydantic models for data transfer:
- `UserCreateDTO`, `UserResponseDTO`, `UserStatsDTO`
- `EventCreateDTO`, `MetricsDTO`

#### Enums (`shared/enums/`)
- `UserRole`, `UserStatus`, `Language`, `EventType`

#### Exceptions (`shared/exceptions/`)
- Custom exception hierarchy

### 4. Configuration (`config/`)

Pydantic Settings with environment variable support:
- `settings/base.py` - Main settings aggregator
- `settings/bot.py` - Bot configuration
- `settings/database.py` - Database & Redis
- `settings/admin.py` - Admin panel settings
- `settings/observability.py` - Logging, metrics, tracing

## Design Patterns

### 1. Repository Pattern
```python
class UserRepository(BaseRepository[User]):
    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        return await self.get_by(telegram_id=telegram_id)
```

**Benefits**:
- Abstraction over data access
- Easier testing (mock repositories)
- Centralized query logic

### 2. Unit of Work Pattern
```python
async def register_user(dto: UserCreateDTO) -> User:
    async with UnitOfWork(session) as uow:
        user = await uow.users.create(**dto.dict())
        await uow.analytics.track_event(...)
        await uow.commit()  # Atomic transaction
```

**Benefits**:
- Transaction management
- Multiple repository coordination
- ACID guarantees

### 3. Service Layer Pattern
```python
class UserService:
    def __init__(self, uow: UnitOfWork, cache: CacheService):
        self.uow = uow
        self.cache = cache

    async def register_or_update(self, telegram_user) -> User:
        # Business logic here
```

**Benefits**:
- Business logic separation
- Reusable across bot and admin
- Easier testing

### 4. Dependency Injection
```python
@router.message(CommandStart())
async def cmd_start(
    message: Message,
    user_service: FromDishka[UserService],  # Auto-injected
):
    user = await user_service.register_or_update(message.from_user)
```

**Benefits**:
- Loose coupling
- Easier testing (mock services)
- Cleaner code

## Data Flow

### User Message Flow
```
1. User sends message to Bot
2. Middleware chain:
   - DIMiddleware: Inject dependencies
   - LoggingMiddleware: Log request
   - MetricsMiddleware: Collect metrics
3. Handler receives message + injected services
4. Handler calls Service layer
5. Service uses UoW to access repositories
6. Repository performs database operations
7. Response sent to user
8. Metrics and logs recorded
```

### Admin Panel Flow
```
1. Admin makes HTTP request
2. FastAPI route handler
3. Dependency injection (FastAPI Depends)
4. Service/Repository layer
5. Database query
6. JSON response
```

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT UNIQUE NOT NULL,
    username VARCHAR(255),
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255),
    language VARCHAR(2) DEFAULT 'ru',
    status VARCHAR(20) DEFAULT 'active',
    role VARCHAR(20) DEFAULT 'user',
    referrer_id INTEGER REFERENCES users(id),
    total_messages INTEGER DEFAULT 0,
    last_activity_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
);

CREATE INDEX idx_users_telegram_id ON users(telegram_id);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_status ON users(status);
CREATE INDEX idx_users_role ON users(role);
```

### Analytics Events Table
```sql
CREATE TABLE analytics_events (
    id SERIAL PRIMARY KEY,
    event_type VARCHAR(50) NOT NULL,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    data JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
);

CREATE INDEX idx_analytics_event_type ON analytics_events(event_type);
CREATE INDEX idx_analytics_user_id ON analytics_events(user_id);
CREATE INDEX idx_analytics_created_at ON analytics_events(created_at);
```

## Monitoring Stack

### Metrics (Prometheus)
**Bot Metrics**:
- `bot_messages_total{handler, status}` - Total messages
- `bot_commands_total{command}` - Commands executed
- `bot_errors_total{error_type}` - Errors occurred
- `bot_response_time_seconds{handler}` - Response time histogram
- `bot_active_users{period}` - Active users gauge

**Collection**: Prometheus scrapes `/metrics` endpoint from bot service

### Logging (Loki + Structlog)
**Format**: Structured JSON logs
```json
{
  "event": "bot_event_processed",
  "user_id": 123,
  "duration_ms": 45,
  "level": "info",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Pipeline**: App → Structlog → Docker logs → Promtail → Loki → Grafana

### Visualization (Grafana)
- **Dashboards**: Bot overview, database performance, system metrics
- **Data Sources**: Prometheus (metrics), Loki (logs)
- **Alerts**: (Optional) Error rate, response time thresholds

## Deployment

### Development
```bash
docker compose up --build
```

### Production
```bash
# Set environment
export ENVIRONMENT=production

# Build and deploy
docker compose up -d --build

# Check status
docker compose ps

# View logs
docker compose logs -f bot
```

### Services Ports
- Bot Metrics: 9090
- Admin Panel: 8000
- Grafana: 3000
- Prometheus: 9091
- Loki: 3100
- Dozzle: 8888

## Testing Strategy

### Unit Tests
- Test services in isolation
- Mock repositories
- Fast execution

### Integration Tests
- Test with real database (test DB)
- Test repository layer
- Test API endpoints

### End-to-End Tests
- Test bot handlers
- Test full user flows
- Use pytest-aiogram

## Performance Considerations

### Database
- **Connection Pooling**: 10 connections, 20 overflow
- **Indexes**: On frequently queried columns
- **Query Optimization**: Use `select` with joins, avoid N+1

### Cache
- **User Stats**: Cached for 5 minutes
- **Active Users**: Cached for 5 minutes
- **Session Data**: Stored in Redis

### Scaling
- **Horizontal**: Multiple bot instances (polling → webhooks)
- **Database**: Read replicas, connection pooling
- **Cache**: Redis cluster

## Security

### Authentication
- **Admin Panel**: Basic auth (change in production!)
- **API**: Can add JWT/OAuth2

### Data Protection
- **Secrets**: Use `SecretStr` in settings
- **Passwords**: Hashed (for admin users)
- **SQL Injection**: Prevented by SQLAlchemy ORM

### Rate Limiting
- Bot: Throttling middleware (1 msg/sec per user)
- API: Can add rate limiting middleware

## Future Enhancements

### Phase 1 (Current) ✅
- Modular architecture
- Service layer
- Unit of Work
- Monitoring
- Admin panel

### Phase 2 (Planned)
- [ ] Webhook support
- [ ] Background tasks (Taskiq)
- [ ] Message queue (RabbitMQ)
- [ ] Improved caching strategies

### Phase 3 (Planned)
- [ ] Kubernetes deployment
- [ ] Multi-bot support
- [ ] GraphQL API
- [ ] Advanced analytics
- [ ] A/B testing framework

## Troubleshooting

### Bot not starting
```bash
# Check logs
docker compose logs bot

# Check database connection
docker compose exec bot python -c "from infrastructure.database.core import get_engine; import asyncio; asyncio.run(get_engine().connect())"

# Check migrations
docker compose exec bot alembic current
```

### Admin panel 500 error
```bash
# Check logs
docker compose logs admin

# Check database
docker compose exec postgres psql -U postgres -d telegram_bot -c "SELECT COUNT(*) FROM users;"
```

### Metrics not showing
```bash
# Check Prometheus targets
curl http://localhost:9091/api/v1/targets

# Check bot metrics endpoint
curl http://localhost:9090/metrics
```

## Best Practices

### Code Organization
- ✅ One model per file
- ✅ One service per business domain
- ✅ Handlers should be thin (delegate to services)
- ✅ Keep DTOs separate from models

### Database
- ✅ Always use migrations
- ✅ Add indexes for frequent queries
- ✅ Use async sessions
- ✅ Close sessions properly

### Testing
- ✅ Test business logic in services
- ✅ Mock external dependencies
- ✅ Use fixtures for test data
- ✅ Aim for 80%+ coverage

### Monitoring
- ✅ Log structured data
- ✅ Include context (user_id, request_id)
- ✅ Track important metrics
- ✅ Set up alerts for critical errors

## Resources

- [aiogram Documentation](https://docs.aiogram.dev/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Dishka Documentation](https://dishka.readthedocs.io/)
- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
