"""Redis cache utility functions."""

import logging
from datetime import datetime, timedelta
from functools import wraps
from typing import Any, Dict, Optional

import redis

from app.core.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()

# Initialize Redis client
redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    password=settings.REDIS_PASSWORD,
    ssl=settings.REDIS_SSL,
    socket_timeout=settings.REDIS_TIMEOUT,
    decode_responses=True,
)


class CacheManager:
    """Manages caching of function results."""

    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}

    async def get(self, key: str) -> Optional[Any]:
        """Get a value from cache if it exists and hasn't expired."""
        if key not in self._cache:
            return None

        cache_data = self._cache[key]
        if cache_data["expires_at"] < datetime.utcnow():
            del self._cache[key]
            return None

        return cache_data["value"]

    async def set(self, key: str, value: Any, ttl: int) -> None:
        """Set a value in cache with expiration."""
        self._cache[key] = {
            "value": value,
            "expires_at": datetime.utcnow() + timedelta(seconds=ttl),
        }

    async def delete(self, key: str) -> None:
        """Delete a value from cache."""
        if key in self._cache:
            del self._cache[key]

    async def clear(self) -> None:
        """Clear all cached values."""
        self._cache.clear()


# Global cache manager instance
cache_manager = CacheManager()


def cache_key(*args, **kwargs) -> str:
    """Generate a cache key from function arguments."""
    key_parts = [str(arg) for arg in args]
    key_parts.extend(f"{k}:{v}" for k, v in sorted(kwargs.items()))
    return ":".join(key_parts)


def cache(ttl: int = 300):
    """Cache decorator for async functions."""

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            key = cache_key(func.__name__, *args, **kwargs)

            # Try to get from cache first
            cached_value = await cache_manager.get(key)
            if cached_value is not None:
                logger.debug(f"Cache hit for key: {key}")

            # If not in cache, execute function
            result = await func(*args, **kwargs)

            # Store in cache
            await cache_manager.set(key, result, ttl)
            logger.debug(f"Cache set for key: {key}")


def invalidate_cache(key_pattern: str) -> None:
    """Invalidate cache entries matching a pattern."""
    keys_to_delete = [key for key in cache_manager._cache.keys() if key_pattern in key]
    for key in keys_to_delete:
        cache_manager.delete(key)
        logger.debug(f"Invalidated cache for key: {key}")


def clear_cache() -> None:
    """Clear all cached values."""
    cache_manager.clear()
    logger.debug("Cache cleared")


__all__ = [
    "get_cache",
    "set_cache",
    "delete_cache",
    "cache_response",
    "clear_cache_pattern",
    "invalidate_cache",
]
