"""Cache adapters."""

import json
from abc import ABC, abstractmethod
from typing import Any, Optional

import redis.asyncio as aioredis

from eve_intel.logging import get_logger
from eve_intel.settings import settings

logger = get_logger(__name__)


class CacheAdapter(ABC):
    """Abstract cache adapter."""

    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        pass

    @abstractmethod
    async def set(self, key: str, value: Any, ttl: int = 300) -> None:
        """Set value in cache with TTL."""
        pass

    @abstractmethod
    async def delete(self, key: str) -> None:
        """Delete key from cache."""
        pass

    @abstractmethod
    async def close(self) -> None:
        """Close cache connection."""
        pass


class RedisCache(CacheAdapter):
    """Redis cache adapter."""

    def __init__(self, url: Optional[str] = None) -> None:
        self.url = url or settings.redis_url
        self.client = aioredis.from_url(self.url, decode_responses=True)

    async def get(self, key: str) -> Optional[Any]:
        """Get value from Redis."""
        try:
            value = await self.client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.warning("cache_get_error", key=key, error=str(e))
            return None

    async def set(self, key: str, value: Any, ttl: int = 300) -> None:
        """Set value in Redis."""
        try:
            await self.client.setex(key, ttl, json.dumps(value))
        except Exception as e:
            logger.warning("cache_set_error", key=key, error=str(e))

    async def delete(self, key: str) -> None:
        """Delete key from Redis."""
        try:
            await self.client.delete(key)
        except Exception as e:
            logger.warning("cache_delete_error", key=key, error=str(e))

    async def close(self) -> None:
        """Close Redis connection."""
        await self.client.aclose()


class InMemoryCache(CacheAdapter):
    """In-memory cache adapter for testing."""

    def __init__(self) -> None:
        self._cache: Dict[str, Any] = {}

    async def get(self, key: str) -> Optional[Any]:
        """Get value from memory."""
        return self._cache.get(key)

    async def set(self, key: str, value: Any, ttl: int = 300) -> None:
        """Set value in memory (TTL ignored)."""
        self._cache[key] = value

    async def delete(self, key: str) -> None:
        """Delete key from memory."""
        self._cache.pop(key, None)

    async def close(self) -> None:
        """No-op for in-memory."""
        pass
