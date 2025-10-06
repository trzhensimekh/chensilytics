"""Arbitrage discovery and analysis."""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from eve_intel.analytics.fees import (
    calculate_net_margin_pct,
    calculate_spread_pct,
    calculate_total_fees,
)
from eve_intel.analytics.risk import calculate_decay_score, calculate_price_volatility
from eve_intel.db.repositories import (
    ArbitrageItemRepository,
    ArbitrageRunRepository,
    OrderSnapshotRepository,
    PriceHistoryRepository,
)
from eve_intel.logging import get_logger
from eve_intel.settings import settings

logger = get_logger(__name__)


@dataclass
class ArbitrageCandidate:
    """Arbitrage opportunity candidate."""

    item_id: int
    from_hub_id: int
    to_hub_id: int
    buy_price: float
    sell_price: float
    spread_pct: float
    fees_total: float
    liquidity_24h: float
    ev_isk: float
    net_margin_pct: float
    decay_score: float
    capital_required: float


class ArbitrageEngine:
    """Arbitrage discovery and calculation engine."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.order_repo = OrderSnapshotRepository(session)
        self.price_repo = PriceHistoryRepository(session)
        self.run_repo = ArbitrageRunRepository(session)
        self.item_repo = ArbitrageItemRepository(session)

    async def find_arbitrage_opportunities(
        self,
        min_ev_isk: Optional[float] = None,
        min_margin_pct: Optional[float] = None,
        min_liquidity: Optional[float] = None,
    ) -> List[ArbitrageCandidate]:
        """Find cross-hub arbitrage opportunities."""
        min_ev = min_ev_isk or settings.min_ev_isk
        min_margin = min_margin_pct or settings.min_net_margin_pct
        min_liq = min_liquidity or settings.min_liquidity_isk_24h

        logger.info(
            "finding_arbitrage",
            min_ev=min_ev,
            min_margin=min_margin,
            min_liquidity=min_liq,
        )

        candidates = []

        # For MVP, use mock data since we need real ESI integration
        # In production, this would fetch latest order snapshots and analyze spreads
        candidates = await self._generate_mock_candidates()

        # Filter by thresholds
        filtered = [
            c
            for c in candidates
            if c.ev_isk >= min_ev
            and c.net_margin_pct >= min_margin
            and c.liquidity_24h >= min_liq
        ]

        # Sort by EV descending
        filtered.sort(key=lambda x: x.ev_isk, reverse=True)

        logger.info("arbitrage_found", total=len(candidates), filtered=len(filtered))

        return filtered

    async def _generate_mock_candidates(self) -> List[ArbitrageCandidate]:
        """Generate mock arbitrage candidates for MVP."""
        # Mock data for demonstration
        mock_items = [
            {
                "item_id": 34,
                "name": "Tritanium",
                "from_hub": 60003760,  # Jita
                "to_hub": 60008494,  # Amarr
                "buy_price": 5.50,
                "sell_price": 6.80,
            },
            {
                "item_id": 35,
                "name": "Pyerite",
                "from_hub": 60011866,  # Dodixie
                "to_hub": 60003760,  # Jita
                "buy_price": 12.20,
                "sell_price": 15.50,
            },
            {
                "item_id": 36,
                "name": "Mexallon",
                "from_hub": 60004588,  # Rens
                "to_hub": 60008494,  # Amarr
                "buy_price": 85.00,
                "sell_price": 110.00,
            },
        ]

        candidates = []
        for item in mock_items:
            buy_price = item["buy_price"]
            sell_price = item["sell_price"]

            spread_pct = calculate_spread_pct(buy_price, sell_price)
            fees_total = calculate_total_fees(buy_price, sell_price)
            net_margin_pct = calculate_net_margin_pct(buy_price, sell_price)

            # Mock liquidity (24h volume in ISK)
            liquidity_24h = 1_500_000_000.0

            # Estimate EV based on liquidity and margin
            # Assume we can capture 10% of daily liquidity
            tradeable_volume_isk = liquidity_24h * 0.1
            ev_isk = tradeable_volume_isk * (net_margin_pct / 100.0)

            # Calculate decay score
            decay_score = calculate_decay_score(net_margin_pct, liquidity_24h)

            # Capital required (assume 1 day of trading at 10% capture)
            capital_required = tradeable_volume_isk

            candidates.append(
                ArbitrageCandidate(
                    item_id=item["item_id"],
                    from_hub_id=item["from_hub"],
                    to_hub_id=item["to_hub"],
                    buy_price=buy_price,
                    sell_price=sell_price,
                    spread_pct=spread_pct,
                    fees_total=fees_total,
                    liquidity_24h=liquidity_24h,
                    ev_isk=ev_isk,
                    net_margin_pct=net_margin_pct,
                    decay_score=decay_score,
                    capital_required=capital_required,
                )
            )

        return candidates

    async def save_run_results(self, candidates: List[ArbitrageCandidate]) -> int:
        """Save arbitrage run results to database."""
        run_id = await self.run_repo.create_run()

        items_data = [
            {
                "run_id": run_id,
                "item_id": c.item_id,
                "from_hub_id": c.from_hub_id,
                "to_hub_id": c.to_hub_id,
                "buy_price": c.buy_price,
                "sell_price": c.sell_price,
                "spread_pct": c.spread_pct,
                "fees_total": c.fees_total,
                "liquidity_24h": c.liquidity_24h,
                "ev_isk": c.ev_isk,
                "net_margin_pct": c.net_margin_pct,
                "decay_score": c.decay_score,
                "capital_required": c.capital_required,
            }
            for c in candidates
        ]

        await self.item_repo.insert_batch(items_data)
        await self.run_repo.complete_run(run_id, len(candidates))

        logger.info("saved_arbitrage_run", run_id=run_id, num_candidates=len(candidates))

        return run_id
