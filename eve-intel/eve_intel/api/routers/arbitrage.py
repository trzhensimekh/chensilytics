"""Arbitrage signals API router."""

from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from eve_intel.analytics.arbitrage import ArbitrageEngine
from eve_intel.db.base import get_session
from eve_intel.db.repositories import ArbitrageItemRepository, ArbitrageRunRepository

router = APIRouter()


class ArbitrageSignal(BaseModel):
    """Arbitrage signal response model."""

    item_id: int = Field(..., description="Item type ID")
    from_hub: int = Field(..., description="Buy hub station ID")
    to_hub: int = Field(..., description="Sell hub station ID")
    buy_price: float = Field(..., description="Buy price")
    sell_price: float = Field(..., description="Sell price")
    net_margin_pct: float = Field(..., description="Net profit margin %")
    ev_isk: float = Field(..., description="Expected value in ISK")
    daily_liquidity: float = Field(..., description="24h liquidity in ISK")
    capital_required: float = Field(..., description="Capital required in ISK")
    decay_score: float = Field(..., description="Opportunity decay score (0-100)")
    fees_total: float = Field(..., description="Total fees per unit")
    spread_pct: float = Field(..., description="Raw spread %")


class ArbitrageResponse(BaseModel):
    """Arbitrage API response."""

    run_id: Optional[int] = Field(None, description="Analytics run ID")
    timestamp: Optional[str] = Field(None, description="Run timestamp")
    count: int = Field(..., description="Number of signals")
    signals: List[ArbitrageSignal] = Field(..., description="Arbitrage signals")


@router.get("/arbitrage", response_model=ArbitrageResponse)
async def get_arbitrage_signals(
    min_ev: Optional[float] = Query(None, description="Minimum expected value (ISK)"),
    min_margin: Optional[float] = Query(None, description="Minimum net margin %"),
    limit: int = Query(100, ge=1, le=1000, description="Max results"),
    session: AsyncSession = Depends(get_session),
) -> ArbitrageResponse:
    """
    Get ranked arbitrage opportunities.

    Returns the latest arbitrage signals, filtered and ranked by expected value.
    """
    engine = ArbitrageEngine(session)

    # Find opportunities
    candidates = await engine.find_arbitrage_opportunities(
        min_ev_isk=min_ev,
        min_margin_pct=min_margin,
    )

    # Limit results
    candidates = candidates[:limit]

    # Convert to response models
    signals = [
        ArbitrageSignal(
            item_id=c.item_id,
            from_hub=c.from_hub_id,
            to_hub=c.to_hub_id,
            buy_price=c.buy_price,
            sell_price=c.sell_price,
            net_margin_pct=c.net_margin_pct,
            ev_isk=c.ev_isk,
            daily_liquidity=c.liquidity_24h,
            capital_required=c.capital_required,
            decay_score=c.decay_score,
            fees_total=c.fees_total,
            spread_pct=c.spread_pct,
        )
        for c in candidates
    ]

    # Try to get latest run info
    run_repo = ArbitrageRunRepository(session)
    latest_run = await run_repo.get_latest_run()

    return ArbitrageResponse(
        run_id=latest_run.run_id if latest_run else None,
        timestamp=latest_run.created_at.isoformat() if latest_run else None,
        count=len(signals),
        signals=signals,
    )


@router.post("/arbitrage/analyze", response_model=ArbitrageResponse)
async def analyze_arbitrage(
    min_ev: Optional[float] = Query(None, description="Minimum expected value (ISK)"),
    min_margin: Optional[float] = Query(None, description="Minimum net margin %"),
    save_results: bool = Query(True, description="Save results to database"),
    session: AsyncSession = Depends(get_session),
) -> ArbitrageResponse:
    """
    Run fresh arbitrage analysis.

    Analyzes current market data and optionally saves results to database.
    """
    engine = ArbitrageEngine(session)

    # Find opportunities
    candidates = await engine.find_arbitrage_opportunities(
        min_ev_isk=min_ev,
        min_margin_pct=min_margin,
    )

    # Save if requested
    run_id = None
    if save_results and candidates:
        run_id = await engine.save_run_results(candidates)

    # Convert to response
    signals = [
        ArbitrageSignal(
            item_id=c.item_id,
            from_hub=c.from_hub_id,
            to_hub=c.to_hub_id,
            buy_price=c.buy_price,
            sell_price=c.sell_price,
            net_margin_pct=c.net_margin_pct,
            ev_isk=c.ev_isk,
            daily_liquidity=c.liquidity_24h,
            capital_required=c.capital_required,
            decay_score=c.decay_score,
            fees_total=c.fees_total,
            spread_pct=c.spread_pct,
        )
        for c in candidates
    ]

    return ArbitrageResponse(
        run_id=run_id,
        timestamp=None,
        count=len(signals),
        signals=signals,
    )
