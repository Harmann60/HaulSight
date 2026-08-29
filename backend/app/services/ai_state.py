"""Shared in-memory state for AI service outputs.

Holds the latest computed results from the four AI modules so they can be
served via REST and pushed over WebSocket without recomputing on every read.
"""
from __future__ import annotations

import asyncio
from typing import Any

_lock = asyncio.Lock()

_visibility: dict[str, Any] = {
    "estimated_visibility_m": 1000.0,
    "fog_severity": "NONE",
    "confidence": 0.0,
    "inputs": {},
    "data_mode": "SIMULATION",
    "updated_at": None,
}

_radar_classifications: list[dict[str, Any]] = []
_recency_counter = 0

_hotspots: dict[str, Any] = {
    "zones": [],
    "total_evaluated": 0,
    "data_mode": "SIMULATION",
    "updated_at": None,
}

_production: dict[str, Any] = {
    "normal_cycle_min": 0.0,
    "predicted_cycle_min": 0.0,
    "increase_pct": 0.0,
    "production_impact_pct": 0.0,
    "confidence": 0.0,
    "inputs": {},
    "data_mode": "ESTIMATE",
    "updated_at": None,
}


async def set_visibility(value: dict[str, Any]) -> None:
    global _visibility
    async with _lock:
        _visibility = value


async def get_visibility() -> dict[str, Any]:
    return dict(_visibility)


async def set_hotspots(value: dict[str, Any]) -> None:
    global _hotspots
    async with _lock:
        _hotspots = value


async def get_hotspots() -> dict[str, Any]:
    return dict(_hotspots)


async def set_production(value: dict[str, Any]) -> None:
    global _production
    async with _lock:
        _production = value


async def get_production() -> dict[str, Any]:
    return dict(_production)


async def add_radar_classification(value: dict[str, Any], max_keep: int = 20) -> None:
    global _recency_counter
    global _radar_classifications
    async with _lock:
        _recency_counter += 1
        value = {"index": _recency_counter, **value}
        _radar_classifications.append(value)
        if len(_radar_classifications) > max_keep:
            _radar_classifications = _radar_classifications[-max_keep:]


async def get_radar_classifications() -> list[dict[str, Any]]:
    return list(_radar_classifications)
