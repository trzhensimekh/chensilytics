"""Seed database with initial data."""

import asyncio

from eve_intel.db.base import get_db_session
from eve_intel.db.repositories import ItemRepository, MarketRepository
from eve_intel.logging import configure_logging, get_logger

logger = get_logger(__name__)


async def seed_items() -> None:
    """Seed items table with common trade goods."""
    items = [
        {"item_id": 34, "name": "Tritanium", "group_id": 18, "volume_m3": 0.01},
        {"item_id": 35, "name": "Pyerite", "group_id": 18, "volume_m3": 0.01},
        {"item_id": 36, "name": "Mexallon", "group_id": 18, "volume_m3": 0.01},
        {"item_id": 37, "name": "Isogen", "group_id": 18, "volume_m3": 0.01},
        {"item_id": 38, "name": "Nocxium", "group_id": 18, "volume_m3": 0.01},
        {"item_id": 39, "name": "Zydrine", "group_id": 18, "volume_m3": 0.01},
        {"item_id": 40, "name": "Megacyte", "group_id": 18, "volume_m3": 0.01},
        {"item_id": 44, "name": "Enriched Uranium", "group_id": 423, "volume_m3": 0.01},
        {"item_id": 11399, "name": "Morphite", "group_id": 18, "volume_m3": 0.01},
        {"item_id": 29668, "name": "PLEX", "group_id": 1668, "volume_m3": 0.01},
    ]

    async with get_db_session() as session:
        repo = ItemRepository(session)
        await repo.upsert_batch(items)

    logger.info("seeded_items", count=len(items))


async def seed_markets() -> None:
    """Seed markets table with major trade hubs."""
    markets = [
        {
            "hub_id": 60003760,
            "name": "Jita IV - Moon 4 - Caldari Navy Assembly Plant",
            "region_id": 10000002,
            "system_id": 30000142,
        },
        {
            "hub_id": 60008494,
            "name": "Amarr VIII (Oris) - Emperor Family Academy",
            "region_id": 10000043,
            "system_id": 30002187,
        },
        {
            "hub_id": 60011866,
            "name": "Dodixie IX - Moon 20 - Federation Navy Assembly Plant",
            "region_id": 10000032,
            "system_id": 30002659,
        },
        {
            "hub_id": 60004588,
            "name": "Rens VI - Moon 8 - Brutor Tribe Treasury",
            "region_id": 10000030,
            "system_id": 30002510,
        },
        {
            "hub_id": 60005686,
            "name": "Hek VIII - Moon 12 - Boundless Creation Factory",
            "region_id": 10000042,
            "system_id": 30002053,
        },
    ]

    async with get_db_session() as session:
        repo = MarketRepository(session)
        await repo.upsert_batch(markets)

    logger.info("seeded_markets", count=len(markets))


async def main() -> None:
    """Run all seed operations."""
    configure_logging()

    logger.info("starting_seed")

    await seed_items()
    await seed_markets()

    logger.info("seed_complete")


if __name__ == "__main__":
    asyncio.run(main())
