# AI Generation Guide

Инструкция для AI-генератора ботов на основе шаблона v2-light. Используй этот документ как главный справочник при генерации Telegram-ботов.

---

## 1. Архитектура

### Стек технологий
- **aiogram 3.13+** — Telegram Bot API framework
- **Dishka** — Dependency Injection (auto_inject=True)
- **SQLAlchemy 2.0** — async ORM (Mapped[] аннотации)
- **Alembic** — миграции БД
- **PostgreSQL 16** — база данных (внешняя через `DATABASE_URL` или локальная через docker-compose)
- **Pydantic Settings** — конфигурация
- **Docker** — standalone контейнер (внешняя БД) или docker-compose (bot + postgres)

### Структура проекта
```
├── apps/bot/                    # Telegram bot application
│   ├── main.py                  # Entry point, router/middleware registration
│   ├── di_container.py          # Dishka DI container setup
│   ├── handlers/                # Message/callback handlers
│   │   ├── user/                # User-facing handlers
│   │   │   └── start.py         # /start command
│   │   └── errors.py            # Global error handler
│   ├── services/                # Business logic layer
│   │   └── user_service.py      # User operations
│   ├── keyboards/               # Inline/Reply keyboards
│   │   └── common.py            # Common keyboards
│   ├── filters/                 # Custom filters
│   │   └── admin.py             # Admin access filter
│   ├── states/                  # FSM states
│   │   └── example.py           # Example states
│   └── middlewares/             # Middlewares
│       └── logging_middleware.py # Event logging
├── infrastructure/
│   ├── database/
│   │   ├── core/session.py      # Engine & session factory
│   │   ├── models/              # SQLAlchemy ORM models
│   │   │   ├── base.py          # Base, mixins (TableNameMixin, TimestampMixin)
│   │   │   └── users.py         # User model
│   │   ├── repositories/        # Repository implementations
│   │   │   ├── base.py          # BaseRepository[T] with generic CRUD
│   │   │   └── user_repository.py
│   │   └── uow.py              # Unit of Work
│   ├── migrations/              # Alembic migrations
│   │   └── env.py               # Migration environment
│   └── monitoring/
│       └── logging.py           # Logging setup
├── config/settings/             # Pydantic Settings
│   ├── base.py                  # AppSettings aggregator
│   ├── bot.py                   # BotSettings
│   └── database.py              # DatabaseSettings
├── shared/
│   ├── dto/                     # Data Transfer Objects
│   │   └── user.py              # UserCreateDTO, UserUpdateDTO, UserResponseDTO
│   ├── enums/                   # Enumerations
│   │   └── __init__.py          # UserRole, UserStatus, Language
│   └── exceptions/              # Application exceptions
│       └── base.py              # AppException hierarchy
└── docker-compose.yml
```

### Поток данных
```
Handler (aiogram) → Service (бизнес-логика) → UnitOfWork → Repository → Database
     ↑                    ↑
     └── FromDishka[...]   └── UnitOfWork через DI
```

---

## 2. Чеклист регистрации (КРИТИЧНО)

Каждый новый компонент нужно зарегистрировать в определённых файлах. Ищи маркеры `# === ... ABOVE ===` и вставляй новый код **ПЕРЕД** маркером.

### Новая модель БД (3 точки)

1. **Создать файл** `infrastructure/database/models/your_model.py`
2. **Импорт в models/__init__.py** — перед `# === IMPORT NEW MODELS ABOVE ===`
   ```python
   from .your_model import YourModel as YourModel
   ```
3. **Импорт в migrations/env.py** — перед `# === IMPORT NEW MODELS FOR MIGRATION ABOVE ===`
   ```python
   from infrastructure.database.models.your_model import YourModel  # noqa: F401
   ```

### Новый репозиторий (3 файла, 4 точки)

1. **Создать файл** `infrastructure/database/repositories/your_model_repository.py`
2. **Импорт в repositories/__init__.py** — перед `# === IMPORT NEW REPOSITORIES ABOVE ===`
   ```python
   from infrastructure.database.repositories.your_model_repository import YourModelRepository
   ```
3. **Экспорт в repositories/__init__.py** — в `__all__` перед `# === EXPORT NEW REPOSITORIES ABOVE ===`
   ```python
   "YourModelRepository",
   ```
4. **Property в uow.py** — добавить `_your_models: YourModelRepository | None = None` в `__init__`, и property перед `# === REGISTER NEW REPOSITORIES ABOVE ===`
   ```python
   @property
   def your_models(self) -> YourModelRepository:
       if self._your_models is None:
           self._your_models = YourModelRepository(self.session)
       return self._your_models
   ```

### Новый сервис (1 файл, 1 точка)

1. **Создать файл** `apps/bot/services/your_service.py`
2. **Добавить import** сервиса в начало `apps/bot/di_container.py`
3. **Добавить @provide метод** в `ServiceProvider` перед `# === REGISTER NEW SERVICES ABOVE ===`
   ```python
   @provide
   def get_your_service(self, uow: UnitOfWork) -> YourService:
       return YourService(uow)
   ```

### Новый хэндлер (1 файл, 1 точка)

1. **Создать файл** `apps/bot/handlers/<category>/your_handler.py`
2. **Зарегистрировать** в `apps/bot/main.py` `register_routers()` перед `# === REGISTER NEW ROUTERS ABOVE ===`
   ```python
   from apps.bot.handlers.<category> import your_handler
   dp.include_router(your_handler.router)
   ```

### Клавиатуры / фильтры / стейты / DTO

Эти компоненты **НЕ требуют регистрации** — просто создай файл и импортируй в хэндлерах:
- Клавиатуры: `apps/bot/keyboards/your_keyboard.py`
- Фильтры: `apps/bot/filters/your_filter.py`
- Стейты: `apps/bot/states/your_states.py`
- DTO: `shared/dto/your_dto.py`

---

## 3. Шаблоны кода

### Модель (SQLAlchemy 2.0)
```python
"""YourModel model."""
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, TableNameMixin, TimestampMixin, int_pk


class YourModel(Base, TableNameMixin, TimestampMixin):
    """Description of the model."""

    id: Mapped[int_pk]
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    is_active: Mapped[bool] = mapped_column(server_default="true", nullable=False)
```

### Репозиторий
```python
"""YourModel repository."""
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.database.models.your_model import YourModel
from infrastructure.database.repositories.base import BaseRepository


class YourModelRepository(BaseRepository[YourModel]):
    """Repository for YourModel."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, YourModel)

    async def get_active(self) -> list[YourModel]:
        """Get all active items."""
        result = await self.get_all(is_active=True)
        return list(result)
```

### Сервис
```python
"""YourModel service."""
from infrastructure.database.uow import UnitOfWork
from shared.exceptions.base import NotFoundError


class YourModelService:
    """Service for YourModel business logic."""

    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def get_all(self) -> list:
        """Get all items."""
        return list(await self.uow.your_models.get_all())

    async def get_by_id(self, item_id: int):
        """Get item by ID."""
        item = await self.uow.your_models.get(item_id)
        if not item:
            raise NotFoundError(f"Item with id={item_id} not found")
        return item

    async def create(self, **kwargs):
        """Create new item."""
        return await self.uow.your_models.create(**kwargs)
```

### Хэндлер
```python
"""YourModel handlers."""
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from dishka import FromDishka

from apps.bot.services.your_service import YourModelService
from infrastructure.monitoring.logging import get_logger

logger = get_logger(__name__)
router = Router(name="your_model")


@router.message(Command("your_command"))
async def cmd_your_command(
    message: Message,
    your_service: FromDishka[YourModelService],
) -> None:
    """Handle /your_command."""
    items = await your_service.get_all()
    text = f"Найдено: {len(items)}"
    await message.answer(text)


@router.callback_query(F.data == "your_callback")
async def on_your_callback(
    callback: CallbackQuery,
    your_service: FromDishka[YourModelService],
) -> None:
    """Handle callback."""
    await callback.answer()
    await callback.message.answer("Callback обработан")
```

### Клавиатура (Inline)
```python
"""YourModel keyboards."""
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_your_keyboard() -> InlineKeyboardMarkup:
    """Build keyboard."""
    builder = InlineKeyboardBuilder()
    builder.button(text="Кнопка 1", callback_data="action_1")
    builder.button(text="Кнопка 2", callback_data="action_2")
    builder.adjust(2)
    return builder.as_markup()
```

### FSM стейты
```python
"""YourModel FSM states."""
from aiogram.fsm.state import State, StatesGroup


class YourModelForm(StatesGroup):
    """Form for creating YourModel."""

    waiting_for_name = State()
    waiting_for_description = State()
    confirmation = State()
```

### Фильтр
```python
"""Custom filter."""
from aiogram.filters import BaseFilter
from aiogram.types import Message


class YourFilter(BaseFilter):
    """Custom filter description."""

    def __init__(self, param: str):
        self.param = param

    async def __call__(self, message: Message) -> bool:
        """Check filter condition."""
        return self.param in (message.text or "")
```

### DTO (Pydantic)
```python
"""YourModel DTOs."""
from pydantic import BaseModel, Field


class YourModelCreateDTO(BaseModel):
    """DTO for creating YourModel."""

    name: str = Field(..., description="Item name")
    description: str | None = Field(default=None, description="Item description")


class YourModelResponseDTO(BaseModel):
    """DTO for YourModel response."""

    model_config = {"from_attributes": True}

    id: int
    name: str
    description: str | None
    is_active: bool
```

### Middleware
```python
"""Custom middleware."""
from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from infrastructure.monitoring.logging import get_logger

logger = get_logger(__name__)


class YourMiddleware(BaseMiddleware):
    """Middleware description."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        """Process event."""
        # Before handler
        result = await handler(event, data)
        # After handler
        return result
```

---

## 4. Критические правила

1. **FromDishka для DI** — используй `FromDishka[ServiceType]` для инъекции в хэндлеры. НЕ передавай сервисы вручную.

2. **НЕ создавай сессии вручную** — используй UnitOfWork через DI. Сессия управляется `InfrastructureProvider`.

3. **Mapped[] аннотации** — все поля моделей в SQLAlchemy 2.0 стиле: `name: Mapped[str] = mapped_column(...)`.

4. **3 точки регистрации для модели** — `models/__init__.py`, `migrations/env.py`, + репозиторий в `uow.py`. Пропуск любой точки = миграция не увидит модель или UoW не найдёт репозиторий.

5. **flush(), не commit()** — в репозиториях используй `session.flush()`. Коммит выполняет DI provider (`InfrastructureProvider.get_session`).

6. **__init__.py репозитория** — обновляй и import, и `__all__`. Оба маркера: `IMPORT` и `EXPORT`.

7. **auto_inject=True** — уже включен в `main.py`. НЕ используй старый DI middleware, НЕ добавляй `inject` декоратор.

8. **get_logger(__name__)** — используй `from infrastructure.monitoring.logging import get_logger` для логирования.

9. **Async хэндлеры** — хэндлеры должны быть `async def` функциями с типами `Message`, `CallbackQuery` или `ErrorEvent`.

10. **ParseMode.HTML** — установлен по умолчанию. Используй HTML-теги в текстах: `<b>bold</b>`, `<i>italic</i>`, `<code>code</code>`.

11. **Env-переменные** — через Pydantic Settings с `__` разделителем. Пример: `BOT__TOKEN=xxx`, `POSTGRES__DB_HOST=localhost`. Для внешних БД используй `DATABASE_URL` (без префикса).

12. **Docker volumes** — директории `apps/bot/`, `infrastructure/`, `shared/`, `config/` примонтированы. Новые файлы подхватываются без пересборки.

13. **Миграции** — для новых таблиц нужна миграция: `alembic revision --autogenerate -m "add_your_table"`.

14. **Enums** — используй существующие `UserRole`, `UserStatus`, `Language` из `shared/enums/` или создавай новые в том же пакете.

---

## 5. Полный пример: добавление Product

Задача: добавить модель Product, репозиторий, сервис, хэндлер каталога.

### Шаг 1: Модель `infrastructure/database/models/products.py`
```python
"""Product model."""
from sqlalchemy import BIGINT, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, TableNameMixin, TimestampMixin, int_pk


class Product(Base, TableNameMixin, TimestampMixin):
    """Product model."""

    id: Mapped[int_pk]
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    is_active: Mapped[bool] = mapped_column(server_default="true", nullable=False)
    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
```

### Шаг 2: Регистрация модели

**`infrastructure/database/models/__init__.py`** — добавь перед маркером:
```python
from .products import Product as Product
# === IMPORT NEW MODELS ABOVE ===
```

**`infrastructure/migrations/env.py`** — добавь перед маркером:
```python
from infrastructure.database.models.products import Product  # noqa: F401
# === IMPORT NEW MODELS FOR MIGRATION ABOVE ===
```

### Шаг 3: Репозиторий `infrastructure/database/repositories/product_repository.py`
```python
"""Product repository."""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.database.models.products import Product
from infrastructure.database.repositories.base import BaseRepository


class ProductRepository(BaseRepository[Product]):
    """Repository for Product model."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, Product)

    async def get_active_products(self) -> list[Product]:
        """Get all active products."""
        stmt = select(Product).where(Product.is_active.is_(True))
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_owner(self, owner_id: int) -> list[Product]:
        """Get products by owner."""
        result = await self.get_all(owner_id=owner_id)
        return list(result)
```

### Шаг 4: Регистрация репозитория

**`infrastructure/database/repositories/__init__.py`**:
```python
from infrastructure.database.repositories.product_repository import ProductRepository
# === IMPORT NEW REPOSITORIES ABOVE ===

__all__ = [
    "BaseRepository",
    "UserRepository",
    "ProductRepository",
    # === EXPORT NEW REPOSITORIES ABOVE ===
]
```

**`infrastructure/database/uow.py`** — в `__init__` добавь поле, и property перед маркером:
```python
def __init__(self, session: AsyncSession):
    self.session = session
    self._users: UserRepository | None = None
    self._products: ProductRepository | None = None

@property
def products(self) -> ProductRepository:
    if self._products is None:
        self._products = ProductRepository(self.session)
    return self._products

# === REGISTER NEW REPOSITORIES ABOVE ===
```

### Шаг 5: Сервис `apps/bot/services/product_service.py`
```python
"""Product service."""
from infrastructure.database.models.products import Product
from infrastructure.database.uow import UnitOfWork
from shared.exceptions.base import NotFoundError


class ProductService:
    """Service for product business logic."""

    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def get_catalog(self) -> list[Product]:
        """Get active products catalog."""
        return await self.uow.products.get_active_products()

    async def get_product(self, product_id: int) -> Product:
        """Get product by ID."""
        product = await self.uow.products.get(product_id)
        if not product:
            raise NotFoundError(f"Product with id={product_id} not found")
        return product

    async def create_product(
        self, name: str, price: float, owner_id: int, description: str | None = None
    ) -> Product:
        """Create new product."""
        return await self.uow.products.create(
            name=name, price=price, owner_id=owner_id, description=description
        )
```

### Шаг 6: Регистрация сервиса

**`apps/bot/di_container.py`** — добавь import и @provide метод:
```python
from apps.bot.services.product_service import ProductService

# В ServiceProvider:
@provide
def get_product_service(self, uow: UnitOfWork) -> ProductService:
    return ProductService(uow)

# === REGISTER NEW SERVICES ABOVE ===
```

### Шаг 7: Хэндлер `apps/bot/handlers/user/catalog.py`
```python
"""Catalog handler."""
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from dishka import FromDishka

from apps.bot.services.product_service import ProductService
from infrastructure.monitoring.logging import get_logger

logger = get_logger(__name__)
router = Router(name="catalog")


@router.message(Command("catalog"))
async def cmd_catalog(
    message: Message,
    product_service: FromDishka[ProductService],
) -> None:
    """Show product catalog."""
    products = await product_service.get_catalog()

    if not products:
        await message.answer("Каталог пуст.")
        return

    lines = ["<b>Каталог:</b>\n"]
    for p in products:
        lines.append(f"  {p.name} — <b>{p.price} руб.</b>")

    await message.answer("\n".join(lines))
```

### Шаг 8: Регистрация хэндлера

**`apps/bot/main.py`** — в `register_routers()`:
```python
from apps.bot.handlers.user import catalog
dp.include_router(catalog.router)
# === REGISTER NEW ROUTERS ABOVE ===
```

### Шаг 9: Миграция
```bash
alembic revision --autogenerate -m "add_products_table"
alembic upgrade head
```
