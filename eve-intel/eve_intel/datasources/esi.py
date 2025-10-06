"""EVE Swagger Interface (ESI) client."""

import hashlib
from typing import Any, Dict, List, Optional

import httpx
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from eve_intel.datasources.cache import CacheAdapter
from eve_intel.logging import get_logger
from eve_intel.settings import settings

logger = get_logger(__name__)


class ESIClient:
    """ESI API client with rate limiting, backoff, and caching."""

    def __init__(self, cache: Optional[CacheAdapter] = None) -> None:
        self.base_url = settings.esi_base_url
        self.user_agent = settings.esi_user_agent
        self.cache = cache
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={"User-Agent": self.user_agent},
            timeout=30.0,
        )

    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()

    def _cache_key(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> str:
        """Generate cache key from endpoint and params."""
        key_str = f"{endpoint}:{params}" if params else endpoint
        return f"esi:{hashlib.md5(key_str.encode()).hexdigest()}"

    @retry(
        retry=retry_if_exception_type((httpx.HTTPStatusError, httpx.TimeoutException)),
        stop=stop_after_attempt(settings.esi_max_retries),
        wait=wait_exponential(multiplier=settings.esi_backoff_factor, min=1, max=60),
    )
    async def _get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Make GET request with retry logic."""
        logger.info("esi_request", endpoint=endpoint, params=params)

        response = await self.client.get(endpoint, params=params)
        response.raise_for_status()

        return response.json()

    async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Get data from ESI with caching."""
        cache_key = self._cache_key(endpoint, params)

        # Try cache first
        if self.cache:
            cached = await self.cache.get(cache_key)
            if cached is not None:
                logger.debug("cache_hit", key=cache_key)
                return cached

        # Fetch from API
        data = await self._get(endpoint, params)

        # Store in cache
        if self.cache:
            await self.cache.set(cache_key, data, ttl=settings.cache_ttl_seconds)

        return data

    async def get_markets_orders(
        self, region_id: int, order_type: str = "all", page: int = 1
    ) -> List[Dict[str, Any]]:
        """Get market orders for a region."""
        return await self.get(
            f"/markets/{region_id}/orders/",
            params={"order_type": order_type, "page": page},
        )

    async def get_markets_history(
        self, region_id: int, type_id: int
    ) -> List[Dict[str, Any]]:
        """Get market history for an item in a region."""
        return await self.get(f"/markets/{region_id}/history/", params={"type_id": type_id})

    async def get_universe_types(self, type_id: int) -> Dict[str, Any]:
        """Get type information."""
        return await self.get(f"/universe/types/{type_id}/")

    async def get_universe_stations(self, station_id: int) -> Dict[str, Any]:
        """Get station information."""
        return await self.get(f"/universe/stations/{station_id}/")

    async def get_universe_structures(self, structure_id: int) -> Dict[str, Any]:
        """Get structure information (requires auth for some)."""
        return await self.get(f"/universe/structures/{structure_id}/")
