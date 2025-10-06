"""Tests for database repositories."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from eve_intel.db.repositories import ItemRepository, MarketRepository


@pytest.mark.asyncio
async def test_item_repository_get_all(db_session: AsyncSession) -> None:
    """Test getting all items from empty database."""
    repo = ItemRepository(db_session)
    
    all_items = await repo.get_all()
    assert len(all_items) == 0


@pytest.mark.asyncio
async def test_item_repository_get_by_id(db_session: AsyncSession) -> None:
    """Test getting item by ID from empty database."""
    repo = ItemRepository(db_session)
    
    result = await repo.get_by_id(999)
    assert result is None


@pytest.mark.asyncio
async def test_market_repository_get_all(db_session: AsyncSession) -> None:
    """Test getting all markets from empty database."""
    repo = MarketRepository(db_session)
    
    all_markets = await repo.get_all()
    assert len(all_markets) == 0


@pytest.mark.asyncio
async def test_empty_batch_upsert(db_session: AsyncSession) -> None:
    """Test that empty batch upsert doesn't fail."""
    repo = ItemRepository(db_session)
    await repo.upsert_batch([])
    # Should not raise any error
