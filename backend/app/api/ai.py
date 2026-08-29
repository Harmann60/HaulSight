from __future__ import annotations

from fastapi import APIRouter

from ..services import ai_state
from ..services import visibility_ai, hotspot_analysis, production_forecast

router = APIRouter(prefix="/api/v1/ai", tags=["ai"])


@router.get("/visibility")
async def get_visibility():
    await visibility_ai.update_visibility()
    return await ai_state.get_visibility()


@router.get("/radar")
async def get_radar_classifications():
    return await ai_state.get_radar_classifications()


@router.get("/hotspots")
async def get_hotspots():
    await hotspot_analysis.analyze()
    return await ai_state.get_hotspots()


@router.get("/production")
async def get_production():
    await production_forecast.update_forecast()
    return await ai_state.get_production()
