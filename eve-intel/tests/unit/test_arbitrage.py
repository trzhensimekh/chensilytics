"""Tests for arbitrage analytics."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from eve_intel.analytics.arbitrage import ArbitrageEngine


@pytest.mark.asyncio
async def test_find_arbitrage_with_filters(db_session: AsyncSession) -> None:
    """Test arbitrage filtering by thresholds."""
    engine = ArbitrageEngine(db_session)

    # High threshold should filter out some candidates
    candidates_high = await engine.find_arbitrage_opportunities(
        min_ev_isk=1_000_000_000_000,  # Very high
        min_margin_pct=90.0,  # Very high
    )

    candidates_low = await engine.find_arbitrage_opportunities(
        min_ev_isk=1_000_000,  # Very low
        min_margin_pct=1.0,  # Very low
    )

    # Low threshold should return more or equal candidates
    assert len(candidates_low) >= len(candidates_high)


@pytest.mark.asyncio
async def test_mock_candidates_generated(db_session: AsyncSession) -> None:
    """Test that mock candidates are generated."""
    engine = ArbitrageEngine(db_session)
    
    # Call the private mock method directly
    candidates = await engine._generate_mock_candidates()
    
    assert len(candidates) > 0
    for c in candidates:
        assert c.item_id > 0
        assert c.from_hub_id > 0
        assert c.to_hub_id > 0
        assert c.buy_price > 0
        assert c.sell_price > c.buy_price
