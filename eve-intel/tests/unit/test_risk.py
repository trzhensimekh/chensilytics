"""Tests for risk calculations."""

import pytest

from eve_intel.analytics.risk import (
    calculate_decay_score,
    calculate_price_volatility,
    calculate_killboard_risk_stub,
)


def test_calculate_price_volatility() -> None:
    """Test price volatility calculation."""
    # Perfectly stable prices
    stable_prices = [100.0, 100.0, 100.0]
    assert calculate_price_volatility(stable_prices) == 0.0

    # More volatile prices
    volatile_prices = [80.0, 100.0, 120.0]
    volatility = calculate_price_volatility(volatile_prices)
    assert volatility > 0.0

    # Edge case: single price
    assert calculate_price_volatility([100.0]) == 0.0

    # Edge case: empty list
    assert calculate_price_volatility([]) == 0.0


def test_calculate_decay_score() -> None:
    """Test decay score calculation."""
    # High margin, high liquidity, low volatility = high score
    score1 = calculate_decay_score(
        net_margin_pct=25.0,
        liquidity_24h=1_000_000_000,
        volatility=5.0,
    )
    assert 0.0 <= score1 <= 100.0

    # Low margin, low liquidity = lower score
    score2 = calculate_decay_score(
        net_margin_pct=5.0,
        liquidity_24h=100_000_000,
        volatility=0.0,
    )
    assert score2 < score1

    # High volatility penalizes score
    score3 = calculate_decay_score(
        net_margin_pct=25.0,
        liquidity_24h=1_000_000_000,
        volatility=25.0,
    )
    assert score3 < score1


def test_calculate_killboard_risk_stub() -> None:
    """Test killboard risk stub."""
    # Stub should return fixed value for now
    risk = calculate_killboard_risk_stub(60003760, 60008494)
    assert risk == 50.0
