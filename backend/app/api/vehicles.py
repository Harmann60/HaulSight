from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ..models import VehicleProfile, VehicleType
from ..state import vehicle_store
from ..database import get_db

router = APIRouter(prefix="/api/v1/vehicles", tags=["vehicles"])


@router.get("")
async def list_vehicles():
    vehicles = await vehicle_store.get_all()
    return [
        {
            "vehicle_id": v.vehicle_id,
            "vehicle_type": v.vehicle_type.value if hasattr(v.vehicle_type, 'value') else v.vehicle_type,
            "is_equipped": v.is_equipped,
            "state": v.state.value,
            "latitude": v.latitude,
            "longitude": v.longitude,
            "speed": v.speed,
            "heading": v.heading,
            "gps_quality": v.gps_quality.value if hasattr(v.gps_quality, 'value') else v.gps_quality,
            "current_segment": v.current_segment,
            "risk_level": v.risk_level.value,
            "risk_reason": v.risk_reason,
            "last_seen": v.last_seen.isoformat() if v.last_seen else None,
        }
        for v in vehicles
    ]


@router.get("/{vehicle_id}")
async def get_vehicle(vehicle_id: str):
    v = await vehicle_store.get(vehicle_id)
    if not v:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return {
        "vehicle_id": v.vehicle_id,
        "vehicle_type": v.vehicle_type.value if hasattr(v.vehicle_type, 'value') else v.vehicle_type,
        "is_equipped": v.is_equipped,
        "state": v.state.value,
        "latitude": v.latitude,
        "longitude": v.longitude,
        "speed": v.speed,
        "heading": v.heading,
        "gps_quality": v.gps_quality.value if hasattr(v.gps_quality, 'value') else v.gps_quality,
        "current_segment": v.current_segment,
        "risk_level": v.risk_level.value,
        "risk_reason": v.risk_reason,
        "last_seen": v.last_seen.isoformat() if v.last_seen else None,
    }


@router.post("")
async def register_vehicle(profile: VehicleProfile):
    db = await get_db()
    await db.execute(
        "INSERT OR REPLACE INTO vehicles (vehicle_id, vehicle_type, is_equipped) VALUES (?,?,?)",
        (profile.vehicle_id, profile.vehicle_type.value, int(profile.is_equipped)),
    )
    await db.commit()
    return {"status": "ok", "vehicle_id": profile.vehicle_id}
