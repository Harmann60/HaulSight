from __future__ import annotations

import asyncio

from ..config import get_config
from ..models import VehicleState
from ..state import vehicle_store
from .vehicle_state import check_vehicle_states


async def stale_detection_loop(broadcast_callback=None):
    """Background task that periodically checks vehicle states."""
    config = get_config()
    interval = config["state_check_interval_seconds"]
    while True:
        try:
            changes = await check_vehicle_states()
            if changes and broadcast_callback:
                for change in changes:
                    await broadcast_callback({
                        "type": "vehicle_state_change",
                        "data": change,
                    })
        except Exception as e:
            print(f"[stale_detector] Error: {e}")
        await asyncio.sleep(interval)
