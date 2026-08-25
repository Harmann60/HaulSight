from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ..services import alert_manager

router = APIRouter(prefix="/api/v1/alerts", tags=["alerts"])


@router.get("")
async def list_active_alerts():
    return alert_manager.get_active_alerts()


@router.get("/history")
async def list_alert_history(limit: int = 50):
    return await alert_manager.get_alert_history(limit)


@router.put("/{alert_id}/acknowledge")
async def acknowledge(alert_id: str):
    ok = await alert_manager.acknowledge_alert(alert_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Alert not found")
    return {"status": "ok"}
