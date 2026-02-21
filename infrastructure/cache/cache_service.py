"""Cache service for Redis operations."""
import json
from typing import Any

from redis.asyncio import Redis

from infrastructure.cache.redis_client import get_redis


class CacheService:
    """Service for caching operations."""

    def __init__(self, redis: Redis | None = None):
        self.redis = redis or get_redis()

    async def get(self, key: str) -> Any | None:
        """Get value from cache."""
        value = await self.redis.get(key)
        if value is None:
            return None

        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return value

    async def set(
        self,
        key: str,
        value: Any,
        ttl: int | None = None,
    ) -> None:
        """Set value in cache with optional TTL in seconds."""
        if not isinstance(value, (str, bytes)):
            value = json.dumps(value)

        if ttl:
            await self.redis.setex(key, ttl, value)
        else:
            await self.redis.set(key, value)

    async def delete(self, key: str) -> None:
        """Delete value from cache."""
        await self.redis.delete(key)

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        return bool(await self.redis.exists(key))

    async def get_or_set(
        self,
        key: str,
        factory,
        ttl: int | None = None,
    ) -> Any:
        """Get value from cache or set it using factory function."""
        value = await self.get(key)

        if value is None:
            if callable(factory):
                value = await factory() if asyncio.iscoroutinefunction(factory) else factory()
            else:
                value = factory

            await self.set(key, value, ttl)

        return value

    async def increment(self, key: str, amount: int = 1) -> int:
        """Increment counter in cache."""
        return await self.redis.incrby(key, amount)

    async def decrement(self, key: str, amount: int = 1) -> int:
        """Decrement counter in cache."""
        return await self.redis.decrby(key, amount)


import asyncio  # noqa: E402
