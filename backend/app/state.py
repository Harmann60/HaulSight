from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Any

from .models import VehicleStateRecord, VehicleState, RiskLevel, GpsQuality


class VehicleStateStore:
    """In-memory store for live vehicle state. Thread-safe via asyncio Lock."""

    def __init__(self) -> None:
        self._vehicles: dict[str, VehicleStateRecord] = {}
        self._lock = asyncio.Lock()

    async def upsert(self, record: VehicleStateRecord) -> None:
        async with self._lock:
            self._vehicles[record.vehicle_id] = record

    async def get(self, vehicle_id: str) -> VehicleStateRecord | None:
        return self._vehicles.get(vehicle_id)

    async def get_all(self) -> list[VehicleStateRecord]:
        return list(self._vehicles.values())

    async def get_all_dict(self) -> dict[str, VehicleStateRecord]:
        return dict(self._vehicles)

    async def update_state(self, vehicle_id: str, state: VehicleState) -> None:
        async with self._lock:
            if vehicle_id in self._vehicles:
                self._vehicles[vehicle_id].state = state

    async def update_risk(self, vehicle_id: str, level: RiskLevel, reason: str = "") -> None:
        async with self._lock:
            if vehicle_id in self._vehicles:
                self._vehicles[vehicle_id].risk_level = level
                self._vehicles[vehicle_id].risk_reason = reason

    async def update_segment(self, vehicle_id: str, segment_id: str | None) -> None:
        async with self._lock:
            if vehicle_id in self._vehicles:
                self._vehicles[vehicle_id].current_segment = segment_id

    async def remove(self, vehicle_id: str) -> None:
        async with self._lock:
            self._vehicles.pop(vehicle_id, None)

    async def count(self) -> int:
        return len(self._vehicles)


vehicle_store = VehicleStateStore()
