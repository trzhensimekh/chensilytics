"""Data access repositories."""

from datetime import UTC, datetime
from typing import List, Optional

from sqlalchemy import delete, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from eve_intel.db.models import (
    AnalyticsArbitrageItem,
    AnalyticsArbitrageRun,
    Item,
    Market,
    OrderSnapshot,
    PriceHistory,
)


class ItemRepository:
    """Repository for Item operations."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def upsert_batch(self, items: List[dict]) -> None:
        """Upsert items in batch."""
        if not items:
            return

        stmt = insert(Item).values(items)
        stmt = stmt.on_conflict_do_update(
            index_elements=["item_id"],
            set_={
                "name": stmt.excluded.name,
                "group_id": stmt.excluded.group_id,
                "volume_m3": stmt.excluded.volume_m3,
                "updated_at": datetime.now(datetime.UTC),
            },
        )
        await self.session.execute(stmt)

    async def get_by_id(self, item_id: int) -> Optional[Item]:
        """Get item by ID."""
        stmt = select(Item).where(Item.item_id == item_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self) -> List[Item]:
        """Get all items."""
        stmt = select(Item)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class MarketRepository:
    """Repository for Market operations."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def upsert_batch(self, markets: List[dict]) -> None:
        """Upsert markets in batch."""
        if not markets:
            return

        stmt = insert(Market).values(markets)
        stmt = stmt.on_conflict_do_update(
            index_elements=["hub_id"],
            set_={
                "name": stmt.excluded.name,
                "region_id": stmt.excluded.region_id,
                "system_id": stmt.excluded.system_id,
                "updated_at": datetime.now(datetime.UTC),
            },
        )
        await self.session.execute(stmt)

    async def get_by_id(self, hub_id: int) -> Optional[Market]:
        """Get market by hub ID."""
        stmt = select(Market).where(Market.hub_id == hub_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self) -> List[Market]:
        """Get all markets."""
        stmt = select(Market)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class OrderSnapshotRepository:
    """Repository for OrderSnapshot operations."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def insert_batch(self, orders: List[dict]) -> None:
        """Insert order snapshots in batch."""
        if not orders:
            return

        stmt = insert(OrderSnapshot).values(orders)
        await self.session.execute(stmt)

    async def get_latest_by_hub(
        self, hub_id: int, since: Optional[datetime] = None
    ) -> List[OrderSnapshot]:
        """Get latest orders for a hub."""
        stmt = select(OrderSnapshot).where(OrderSnapshot.hub_id == hub_id)
        if since:
            stmt = stmt.where(OrderSnapshot.ts_snapshot >= since)
        stmt = stmt.order_by(OrderSnapshot.ts_snapshot.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class PriceHistoryRepository:
    """Repository for PriceHistory operations."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def upsert_batch(self, prices: List[dict]) -> None:
        """Upsert price history in batch."""
        if not prices:
            return

        stmt = insert(PriceHistory).values(prices)
        stmt = stmt.on_conflict_do_update(
            index_elements=["item_id", "hub_id", "date"],
            set_={
                "avg_price": stmt.excluded.avg_price,
                "min_price": stmt.excluded.min_price,
                "max_price": stmt.excluded.max_price,
                "volume": stmt.excluded.volume,
            },
        )
        await self.session.execute(stmt)

    async def get_recent_by_item_hub(
        self, item_id: int, hub_id: int, days: int = 30
    ) -> List[PriceHistory]:
        """Get recent price history for item and hub."""
        stmt = (
            select(PriceHistory)
            .where(PriceHistory.item_id == item_id, PriceHistory.hub_id == hub_id)
            .order_by(PriceHistory.date.desc())
            .limit(days)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class ArbitrageRunRepository:
    """Repository for ArbitrageRun operations."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_run(self) -> int:
        """Create a new analytics run."""
        run = AnalyticsArbitrageRun(status="running")
        self.session.add(run)
        await self.session.flush()
        return run.run_id

    async def complete_run(self, run_id: int, num_candidates: int) -> None:
        """Mark run as complete."""
        stmt = (
            update(AnalyticsArbitrageRun)
            .where(AnalyticsArbitrageRun.run_id == run_id)
            .values(completed_at=datetime.now(datetime.UTC), num_candidates=num_candidates, status="completed")
        )
        await self.session.execute(stmt)

    async def get_latest_run(self) -> Optional[AnalyticsArbitrageRun]:
        """Get the latest run."""
        stmt = select(AnalyticsArbitrageRun).order_by(AnalyticsArbitrageRun.created_at.desc()).limit(1)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


class ArbitrageItemRepository:
    """Repository for ArbitrageItem operations."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def insert_batch(self, items: List[dict]) -> None:
        """Insert arbitrage items in batch."""
        if not items:
            return

        stmt = insert(AnalyticsArbitrageItem).values(items)
        await self.session.execute(stmt)

    async def get_by_run(self, run_id: int, limit: int = 100) -> List[AnalyticsArbitrageItem]:
        """Get arbitrage items for a run, ordered by EV."""
        stmt = (
            select(AnalyticsArbitrageItem)
            .where(AnalyticsArbitrageItem.run_id == run_id)
            .order_by(AnalyticsArbitrageItem.ev_isk.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def delete_by_run(self, run_id: int) -> None:
        """Delete all items for a run."""
        stmt = delete(AnalyticsArbitrageItem).where(AnalyticsArbitrageItem.run_id == run_id)
        await self.session.execute(stmt)
