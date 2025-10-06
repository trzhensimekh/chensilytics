"""Mock ESI adapter for testing."""

from typing import Any, Dict, List, Optional

from eve_intel.datasources.cache import CacheAdapter


class MockESIClient:
    """Mock ESI client for testing."""

    def __init__(self, cache: Optional[CacheAdapter] = None) -> None:
        self.cache = cache

    async def close(self) -> None:
        """Close mock client."""
        pass

    async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Mock get request."""
        return {}

    async def get_markets_orders(
        self, region_id: int, order_type: str = "all", page: int = 1
    ) -> List[Dict[str, Any]]:
        """Return mock market orders."""
        return [
            {
                "order_id": 1,
                "type_id": 34,
                "location_id": 60003760,
                "is_buy_order": True,
                "price": 5.0,
                "volume_remain": 1000,
            },
            {
                "order_id": 2,
                "type_id": 34,
                "location_id": 60003760,
                "is_buy_order": False,
                "price": 6.0,
                "volume_remain": 500,
            },
        ]

    async def get_markets_history(
        self, region_id: int, type_id: int
    ) -> List[Dict[str, Any]]:
        """Return mock market history."""
        return [
            {
                "date": "2025-01-15",
                "average": 5.5,
                "lowest": 5.0,
                "highest": 6.0,
                "volume": 10000,
            }
        ]

    async def get_universe_types(self, type_id: int) -> Dict[str, Any]:
        """Return mock type info."""
        return {"type_id": type_id, "name": f"Mock Item {type_id}", "volume": 1.0}

    async def get_universe_stations(self, station_id: int) -> Dict[str, Any]:
        """Return mock station info."""
        return {
            "station_id": station_id,
            "name": f"Mock Station {station_id}",
            "system_id": 30000142,
        }

    async def get_universe_structures(self, structure_id: int) -> Dict[str, Any]:
        """Return mock structure info."""
        return {
            "structure_id": structure_id,
            "name": f"Mock Structure {structure_id}",
            "system_id": 30000142,
        }
