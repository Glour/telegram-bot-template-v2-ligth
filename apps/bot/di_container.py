"""Dependency Injection container setup with Dishka."""
from collections.abc import AsyncIterable

from dishka import AsyncContainer, Provider, Scope, provide
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from apps.bot.services.analytics_service import AnalyticsService
from apps.bot.services.user_service import UserService
from config.settings.base import AppSettings, get_settings
from infrastructure.cache.cache_service import CacheService
from infrastructure.cache.redis_client import get_redis
from infrastructure.database.core.session import get_engine, get_session_factory
from infrastructure.database.uow import UnitOfWork


class SettingsProvider(Provider):
    """Provider for application settings."""

    scope = Scope.APP

    @provide
    def get_app_settings(self) -> AppSettings:
        """Provide application settings."""
        return get_settings()


class InfrastructureProvider(Provider):
    """Provider for infrastructure components."""

    @provide(scope=Scope.APP)
    def get_db_engine(self, settings: AppSettings) -> AsyncEngine:
        """Provide database engine."""
        return get_engine()

    @provide(scope=Scope.REQUEST)
    async def get_session(self, engine: AsyncEngine) -> AsyncIterable[AsyncSession]:
        """Provide database session."""
        session_factory = get_session_factory()
        async with session_factory() as session:
            yield session

    @provide(scope=Scope.APP)
    def get_redis(self) -> Redis:
        """Provide Redis client."""
        return get_redis()

    @provide(scope=Scope.REQUEST)
    def get_cache_service(self, redis: Redis) -> CacheService:
        """Provide cache service."""
        return CacheService(redis)

    @provide(scope=Scope.REQUEST)
    def get_uow(self, session: AsyncSession) -> UnitOfWork:
        """Provide Unit of Work."""
        return UnitOfWork(session)


class ServiceProvider(Provider):
    """Provider for business services."""

    scope = Scope.REQUEST

    @provide
    def get_user_service(self, uow: UnitOfWork, cache: CacheService) -> UserService:
        """Provide user service."""
        return UserService(uow, cache)

    @provide
    def get_analytics_service(self, uow: UnitOfWork) -> AnalyticsService:
        """Provide analytics service."""
        return AnalyticsService(uow)


def create_container() -> AsyncContainer:
    """Create and configure DI container."""
    from dishka import make_async_container

    container = make_async_container(
        SettingsProvider(),
        InfrastructureProvider(),
        ServiceProvider(),
    )

    return container
