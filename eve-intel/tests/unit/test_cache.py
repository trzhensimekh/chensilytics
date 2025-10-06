"""Tests for cache adapters."""

import pytest

from eve_intel.datasources.cache import InMemoryCache


@pytest.mark.asyncio
async def test_in_memory_cache_get_set() -> None:
    """Test in-memory cache get/set."""
    cache = InMemoryCache()

    # Test set and get
    await cache.set("key1", {"value": 42})
    result = await cache.get("key1")
    assert result == {"value": 42}

    # Test get non-existent key
    result = await cache.get("nonexistent")
    assert result is None


@pytest.mark.asyncio
async def test_in_memory_cache_delete() -> None:
    """Test in-memory cache delete."""
    cache = InMemoryCache()

    await cache.set("key1", "value1")
    assert await cache.get("key1") == "value1"

    await cache.delete("key1")
    assert await cache.get("key1") is None


@pytest.mark.asyncio
async def test_in_memory_cache_close() -> None:
    """Test in-memory cache close."""
    cache = InMemoryCache()
    await cache.close()
    # Should not raise any error
