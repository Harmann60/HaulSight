from __future__ import annotations

from datetime import datetime, timedelta

from ..config import get_config
from ..models import VehicleState
from ..state import vehicle_store


async def check_vehicle_states() -> list[dict]:
    """Run state transitions for all vehicles. Returns list of changes."""
    config = get_config()
    stale_thresh = timedelta(seconds=config["stale_threshold_seconds"])
    offline_thresh = timedelta(seconds=config["offline_threshold_seconds"])
    now = datetime.utcnow()
    changes = []

    vehicles = await vehicle_store.get_all()
    for v in vehicles:
        if v.last_seen is None:
            continue
        age = now - v.last_seen
        old_state = v.state

        if age > offline_thresh and old_state != VehicleState.OFFLINE:
            await vehicle_store.update_state(v.vehicle_id, VehicleState.OFFLINE)
            changes.append({"vehicle_id": v.vehicle_id, "old": old_state.value, "new": VehicleState.OFFLINE.value})
        elif age > stale_thresh and old_state not in (VehicleState.OFFLINE, VehicleState.STALE):
            await vehicle_store.update_state(v.vehicle_id, VehicleState.STALE)
            changes.append({"vehicle_id": v.vehicle_id, "old": old_state.value, "new": VehicleState.STALE.value})

    return changes
