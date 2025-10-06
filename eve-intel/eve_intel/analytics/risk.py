"""Risk scoring and analysis."""

import math
from typing import List


def calculate_price_volatility(prices: List[float]) -> float:
    """Calculate price volatility (coefficient of variation)."""
    if len(prices) < 2:
        return 0.0

    mean = sum(prices) / len(prices)
    if mean == 0:
        return 0.0

    variance = sum((p - mean) ** 2 for p in prices) / len(prices)
    std_dev = math.sqrt(variance)

    # Coefficient of variation (CV)
    return (std_dev / mean) * 100.0


def calculate_decay_score(
    net_margin_pct: float,
    liquidity_24h: float,
    volatility: float = 0.0,
) -> float:
    """
    Calculate decay score (higher = better opportunity, lower decay risk).

    Combines:
    - Net margin (higher is better)
    - Liquidity (higher is better)
    - Volatility (lower is better)
    """
    # Normalize margin component (0-1 scale, capped at 50%)
    margin_component = min(net_margin_pct / 50.0, 1.0)

    # Normalize liquidity component (log scale, billion ISK reference)
    liquidity_component = math.log10(max(liquidity_24h, 1)) / math.log10(1_000_000_000)
    liquidity_component = min(liquidity_component, 1.0)

    # Volatility penalty (0-1 scale, capped at 30%)
    volatility_penalty = min(volatility / 30.0, 1.0)

    # Weighted score
    score = (0.5 * margin_component) + (0.3 * liquidity_component) - (0.2 * volatility_penalty)

    return max(0.0, min(score * 100.0, 100.0))


def calculate_killboard_risk_stub(from_hub_id: int, to_hub_id: int) -> float:
    """
    Placeholder for killboard-based route risk.

    In Phase 2, integrate with zKillboard API to get actual danger ratings.
    Returns a stub value for now.
    """
    # Stub: assume all routes are medium risk
    return 50.0
