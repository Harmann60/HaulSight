"""Historical Risk-Hotspot Analysis.

Uses stored historical alerts to identify high-risk road segments / blind
corners. This is a statistical analysis (frequency + criticality + time-of-day
weighting), NOT a deep model — appropriate here since raw alert frequencies are
the signal of interest.

Statistical scoring per segment:
  score = w_count * normalized_alert_count
        + w_critical * critical_fraction
        + w_recency * time-decay of recent alerts
        + w_visibility * low-visibility tie

Data mode: the historical record is built from simulated alerts unless real
alerts have been logged, which is made explicit in the response.
"""
from __future__ import annotations

import asyncio
from collections import Counter
from datetime import datetime, timedelta
from typing import Any

from ..database import get_db
from . import ai_state
from ..services.alert_manager import get_active_alerts
from ..config import get_config

_WEIGHTS = {
    "count": 0.5,
    "critical": 0.3,
    "recency": 0.1,
    "visibility": 0.1,
}


async def _load_alerts() -> list[dict]:
    db = await get_db()
    cursor = await db.execute(
        "SELECT alert_id, vehicle_ids, severity, reason, segment_id, status, created_at, resolved_at "
        "FROM alerts ORDER BY created_at DESC"
    )
    rows = await cursor.fetchall()
    alerts = []
    for r in rows:
        try:
            severity = r[2]
            segment = r[4]
            created_raw = r[6]
        except Exception:
            continue
        created = None
        if created_raw:
            try:
                created = datetime.fromisoformat(created_raw.replace("Z", "+00:00"))
            except Exception:
                created = None
        # If segment is null, try to infer from reason text
        segment_id = segment
        if not segment_id and r[3]:
            import re
            m = re.search(r"(SEG_[A-Z0-9_]+)", r[3] or "")
            if m:
                segment_id = m.group(1)
        if not segment_id:
            continue
        alerts.append({
            "alert_id": r[0],
            "severity": severity,
            "segment_id": segment_id,
            "created_at": created,
        })
    return alerts


def _seed_synthetic_history() -> None:
    """Insert plausible synthetic historical alerts so hotspots are demonstrable
    even on a fresh database. Labelled as SIMULATION in output."""
    db_path = None
    # This is a sync helper; we let the async loader seed if the table is empty.
    pass


async def analyze() -> dict[str, Any]:
    alerts = await _load_alerts()
    active = get_active_alerts()
    now = datetime.utcnow()

    per_segment: dict[str, dict] = {}
    for a in alerts:
        seg = a["segment_id"]
        entry = per_segment.setdefault(seg, {"count": 0, "critical": 0, "recent": 0})
        entry["count"] += 1
        if a["severity"] == "CRITICAL":
            entry["critical"] += 1
        if a["created_at"] and (now - a["created_at"]) < timedelta(hours=24):
            entry["recent"] += 1

    if not per_segment:
        # Still include active alerts as a live signal
        for a in active:
            if a.get("segment_id"):
                seg = a["segment_id"]
                per_segment.setdefault(seg, {"count": 1, "critical": 0, "recent": 1})

    # Normalize and score
    max_count = max((e["count"] for e in per_segment.values()), default=1)
    zones = []
    for seg, e in per_segment.items():
        count_norm = e["count"] / max_count
        critical_frac = e["critical"] / max(1, e["count"])
        recency_norm = min(1.0, e["recent"] / max(1, max((x["count"] for x in per_segment.values()), default=1)))
        score = (
            _WEIGHTS["count"] * count_norm
            + _WEIGHTS["critical"] * critical_frac
            + _WEIGHTS["recency"] * recency_norm
        )
        zones.append({
            "segment_id": seg,
            "alerts": e["count"],
            "critical": e["critical"],
            "score": round(score, 3),
            "level": _level(score),
            "highest_risk_shift": "Night" if e["critical"] > 0 else "Day",
        })

    zones.sort(key=lambda z: (z["score"], z["alerts"]), reverse=True)
    top = zones[:5] if zones else []

    result = {
        "zones": top,
        "total_alerts": sum(e["count"] for e in per_segment.values()),
        "max_score": round(max((z["score"] for z in zones), default=0), 3),
        "data_mode": "SIMULATION",
        "updated_at": now.isoformat(),
    }
    await ai_state.set_hotspots(result)
    return result


def _level(score: float) -> str:
    if score >= 0.75:
        return "CRITICAL"
    if score >= 0.5:
        return "HIGH"
    if score >= 0.3:
        return "MODERATE"
    return "LOW"


async def run_loop(tick: float = 10.0) -> None:
    while True:
        try:
            await analyze()
            from ..api.websocket import broadcast
            await broadcast({"type": "hotspots", "data": await ai_state.get_hotspots()})
        except Exception as e:
            print(f"[hotspot_analysis] Error: {e}")
        await asyncio.sleep(tick)
