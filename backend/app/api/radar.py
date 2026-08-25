from __future__ import annotations

from fastapi import APIRouter

from ..services import radar_service
from ..models import RadarDetection

router = APIRouter(prefix="/api/v1/radar", tags=["radar"])


@router.get("/beacons")
async def list_beacons():
    return radar_service.get_all_beacons()


@router.get("/detections")
async def list_detections(limit: int = 20):
    return radar_service.get_recent_detections(limit)


@router.post("/detections")
async def report_detection(detection: RadarDetection):
    return await radar_service.record_detection(detection)
