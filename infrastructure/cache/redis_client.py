"""Redis client setup and utilities."""
from redis.asyncio import Redis, from_url
from redis.asyncio.connection import ConnectionPool

from config.settings.base import get_settings

_redis_pool: ConnectionPool | None = None
_redis_client: Redis | None = None


def get_redis_pool() -> ConnectionPool:
    """Get or create Redis connection pool."""
    global _redis_pool

    if _redis_pool is None:
        settings = get_settings()
        _redis_pool = ConnectionPool.from_url(
            settings.redis.url,
            max_connections=settings.redis.max_connections,
            decode_responses=settings.redis.decode_responses,
            socket_timeout=settings.redis.socket_timeout,
            socket_connect_timeout=settings.redis.socket_connect_timeout,
        )

    return _redis_pool


def get_redis() -> Redis:
    """Get or create Redis client."""
    global _redis_client

    if _redis_client is None:
        pool = get_redis_pool()
        _redis_client = Redis(connection_pool=pool)

    return _redis_client


async def close_redis() -> None:
    """Close Redis connection."""
    global _redis_client, _redis_pool

    if _redis_client is not None:
        await _redis_client.aclose()
        _redis_client = None

    if _redis_pool is not None:
        await _redis_pool.aclose()
        _redis_pool = None
