from __future__ import annotations

from datetime import datetime
from typing import Any

from ..models import RadarBeacon, RadarDetection
from ..database import get_db
from ..state import vehicle_store
from ..models import VehicleStateRecord, VehicleState, GpsQuality, RiskLevel
from ..services.road_graph import road_graph, haversine
from ..config import get_config

# In-memory beacon state
_beacons: dict[str, RadarBeacon] = {}
_recent_detections: list[dict] = []


async def load_beacons_from_db() -> None:
    db = await get_db()
    cursor = await db.execute("SELECT beacon_id, node_id, latitude, longitude, status, last_heartbeat FROM radar_beacons")
    rows = await cursor.fetchall()
    for r in rows:
        beacon = RadarBeacon(
            beacon_id=r[0], node_id=r[1], latitude=r[2], longitude=r[3],
            status=r[4], last_heartbeat=r[5],
        )
        _beacons[beacon.beacon_id] = beacon


async def load_beacons_from_graph(data: dict) -> None:
    """Load radar beacons from mine_graph.json data."""
    db = await get_db()
    for bd in data.get("radar_beacons", []):
        beacon = RadarBeacon(**bd)
        _beacons[beacon.beacon_id] = beacon
        await db.execute(
            "INSERT OR IGNORE INTO radar_beacons (beacon_id, node_id, latitude, longitude, status) VALUES (?,?,?,?,?)",
            (beacon.beacon_id, beacon.node_id, beacon.latitude, beacon.longitude, beacon.status),
        )
    await db.commit()


async def record_detection(detection: RadarDetection) -> dict[str, Any]:
    """Record a radar detection. If no vehicle_id, it's a non-equipped vehicle."""
    config = get_config()
    db = await get_db()
    beacon = _beacons.get(detection.beacon_id)

    result: dict[str, Any] = {
        "detection_id": detection.detection_id,
        "beacon_id": detection.beacon_id,
        "vehicle_id": detection.detected_vehicle_id,
        "range_meters": detection.range_meters,
        "status": "recorded",
        "local_warning": False,
    }

    if beacon:
        beacon.last_heartbeat = datetime.utcnow()

    # Log to DB
    await db.execute(
        """INSERT OR IGNORE INTO radar_detections
           (detection_id, beacon_id, detected_vehicle_id, range_meters, direction, confidence, timestamp)
           VALUES (?,?,?,?,?,?,?)""",
        (detection.detection_id, detection.beacon_id, detection.detected_vehicle_id,
         detection.range_meters, detection.direction, detection.confidence,
         detection.timestamp.isoformat()),
    )
    await db.commit()

    # Keep recent detections in memory (last 100)
    _recent_detections.append(result)
    if len(_recent_detections) > 100:
        _recent_detections.pop(0)

    # Generate local warning if something is close to blind corner
    if beacon:
        node = road_graph.nodes.get(beacon.node_id)
        if node:
            # If detection is within 50m of a blind corner beacon, trigger local warning
            if detection.range_meters < 50:
                result["local_warning"] = True
                result["warning_message"] = (
                    f"⚠ LOCAL WARNING at {beacon.node_id}: "
                    f"Object detected {detection.range_meters:.0f}m away"
                )

    # If non-equipped vehicle detected, create a temporary virtual vehicle state
    if not detection.detected_vehicle_id:
        virtual_id = f"RADAR-{detection.beacon_id}-{detection.detection_id[-6:]}"
        result["virtual_vehicle_id"] = virtual_id

        if beacon:
            # Calculate approximate position from beacon + range + direction
            import math
            R = 6371000
            brng_rad = math.radians(detection.direction)
            d = detection.range_meters
            lat1 = math.radians(beacon.latitude)
            lon1 = math.radians(beacon.longitude)
            lat2 = math.asin(math.sin(lat1) * math.cos(d / R) + math.cos(lat1) * math.sin(d / R) * math.cos(brng_rad))
            lon2 = lon1 + math.atan2(math.sin(brng_rad) * math.sin(d / R) * math.cos(lat1),
                                     math.cos(d / R) - math.sin(lat1) * math.sin(lat2))

            record = VehicleStateRecord(
                vehicle_id=virtual_id,
                vehicle_type="unknown",
                is_equipped=False,
                state=VehicleState.LIVE,
                latitude=math.degrees(lat2),
                longitude=math.degrees(lon2),
                speed=0.0,
                heading=detection.direction,
                gps_quality=GpsQuality.GOOD,
                risk_level=RiskLevel.SAFE,
                risk_reason="Non-equipped vehicle detected by radar",
                last_seen=datetime.utcnow(),
            )
            await vehicle_store.upsert(record)

    return result


def get_all_beacons() -> list[dict]:
    return [
        {
            "beacon_id": b.beacon_id,
            "node_id": b.node_id,
            "latitude": b.latitude,
            "longitude": b.longitude,
            "status": b.status,
            "last_heartbeat": b.last_heartbeat.isoformat() if b.last_heartbeat else None,
        }
        for b in _beacons.values()
    ]


def get_recent_detections(limit: int = 20) -> list[dict]:
    return _recent_detections[-limit:]
