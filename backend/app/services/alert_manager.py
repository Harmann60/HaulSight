from __future__ import annotations

import asyncio
from datetime import datetime, timedelta
from typing import Any

from ..config import get_config
from ..models import Alert, AlertStatus, RiskLevel
from ..database import get_db

# In-memory active alerts
_active_alerts: dict[str, Alert] = {}
# Debounce counters: key = frozenset({vA, vB}) -> consecutive elevated ticks
_debounce_counters: dict[frozenset, int] = {}
# Resolution counters: key = alert_id -> consecutive safe ticks
_resolution_counters: dict[str, int] = {}


def _make_alert_key(vehicle_ids: list[str]) -> frozenset:
    return frozenset(sorted(vehicle_ids))


async def process_risk_results(risk_results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Process risk engine results, create/resolve alerts. Returns alert events for broadcast."""
    config = get_config()
    now = datetime.utcnow()
    db = await get_db()
    events = []

    involved_keys = set()

    for result in risk_results:
        v_ids = sorted([result["vehicle_a"], result["vehicle_b"]])
        key = _make_alert_key(v_ids)
        involved_keys.add(key)
        risk_level = result["risk_level"]

        if risk_level in (RiskLevel.CRITICAL, RiskLevel.WARNING, RiskLevel.CAUTION):
            _debounce_counters[key] = _debounce_counters.get(key, 0) + 1

            if _debounce_counters[key] >= config["risk_debounce_ticks"]:
                existing = _find_active_alert_for_key(key)
                if existing:
                    # Update severity if escalated
                    if RiskLevel[risk_level].value > existing.severity.value:
                        old_sev = existing.severity
                        existing.severity = RiskLevel[risk_level]
                        existing.reason = result["reason"]
                        await db.execute(
                            "UPDATE alerts SET severity=?, reason=? WHERE alert_id=?",
                            (risk_level, result["reason"], existing.alert_id),
                        )
                        await db.commit()
                        events.append({"type": "alert_updated", "data": _alert_to_dict(existing)})
                    _resolution_counters.pop(existing.alert_id, None)
                else:
                    # Create new alert
                    alert_id = f"ALT-{now.strftime('%H%M%S')}-{len(v_ids[0])}-{key.__hash__() & 0xFFFF:04x}"
                    alert = Alert(
                        alert_id=alert_id,
                        vehicle_ids=v_ids,
                        severity=RiskLevel[risk_level],
                        reason=result["reason"],
                        status=AlertStatus.ACTIVE,
                        created_at=now,
                    )
                    _active_alerts[alert_id] = alert
                    await db.execute(
                        "INSERT INTO alerts (alert_id, vehicle_ids, severity, reason, status, created_at) VALUES (?,?,?,?,?,?)",
                        (alert_id, str(v_ids), risk_level, result["reason"], "active", now.isoformat()),
                    )
                    await db.commit()
                    events.append({"type": "alert_new", "data": _alert_to_dict(alert)})
        else:
            _debounce_counters[key] = 0

    # Check for alerts that should resolve (involved pairs now safe)
    for alert_id, alert in list(_active_alerts.items()):
        key = _make_alert_key(alert.vehicle_ids)
        if key not in involved_keys:
            _resolution_counters[alert_id] = _resolution_counters.get(alert_id, 0) + 1
            if _resolution_counters[alert_id] >= config["risk_downgrade_ticks"]:
                await _resolve_alert(alert_id, now, db, events)
        else:
            _resolution_counters.pop(alert_id, None)

    # Check for expired alerts
    expiry = timedelta(seconds=config["alert_expiry_seconds"])
    for alert_id, alert in list(_active_alerts.items()):
        if now - alert.created_at > expiry:
            await _resolve_alert(alert_id, now, db, events, expired=True)

    return events


async def _resolve_alert(alert_id: str, now: datetime, db, events: list, expired: bool = False):
    alert = _active_alerts.pop(alert_id, None)
    if not alert:
        return
    status = AlertStatus.EXPIRED if expired else AlertStatus.RESOLVED
    alert.status = status
    alert.resolved_at = now
    await db.execute(
        "UPDATE alerts SET status=?, resolved_at=? WHERE alert_id=?",
        (status.value, now.isoformat(), alert_id),
    )
    await db.commit()
    events.append({"type": "alert_resolved", "data": _alert_to_dict(alert)})


def _find_active_alert_for_key(key: frozenset) -> Alert | None:
    for alert in _active_alerts.values():
        if _make_alert_key(alert.vehicle_ids) == key and alert.status == AlertStatus.ACTIVE:
            return alert
    return None


def get_active_alerts() -> list[dict]:
    return [_alert_to_dict(a) for a in _active_alerts.values()]


async def get_alert_history(limit: int = 50) -> list[dict]:
    db = await get_db()
    cursor = await db.execute(
        "SELECT alert_id, vehicle_ids, severity, reason, segment_id, status, created_at, resolved_at FROM alerts ORDER BY created_at DESC LIMIT ?",
        (limit,),
    )
    rows = await cursor.fetchall()
    return [
        {
            "alert_id": r[0],
            "vehicle_ids": eval(r[1]) if r[1] else [],
            "severity": r[2],
            "reason": r[3],
            "segment_id": r[4],
            "status": r[5],
            "created_at": r[6],
            "resolved_at": r[7],
        }
        for r in rows
    ]


async def acknowledge_alert(alert_id: str) -> bool:
    alert = _active_alerts.get(alert_id)
    if not alert:
        return False
    alert.status = AlertStatus.ACKNOWLEDGED
    db = await get_db()
    await db.execute("UPDATE alerts SET status=? WHERE alert_id=?", ("acknowledged", alert_id))
    await db.commit()
    return True


def _alert_to_dict(alert: Alert) -> dict:
    return {
        "alert_id": alert.alert_id,
        "vehicle_ids": alert.vehicle_ids,
        "severity": alert.severity.value,
        "reason": alert.reason,
        "segment_id": alert.segment_id,
        "status": alert.status.value,
        "created_at": alert.created_at.isoformat() if alert.created_at else None,
        "resolved_at": alert.resolved_at.isoformat() if alert.resolved_at else None,
    }
