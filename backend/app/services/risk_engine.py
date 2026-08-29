from __future__ import annotations

import math
from typing import Any

from ..config import get_config
from ..models import VehicleStateRecord, RiskLevel, VehicleState
from ..state import vehicle_store
from ..services.road_graph import road_graph, haversine, bearing


def _closing_speed(a: VehicleStateRecord, b: VehicleStateRecord) -> float:
    """Calculate closing speed in m/s between two vehicles.
    Positive = approaching, negative = moving apart."""
    brng = bearing(a.latitude, a.longitude, b.latitude, b.longitude)
    brng_rad = math.radians(brng)

    # Project each vehicle's velocity onto the line connecting them
    a_head = math.radians(a.heading)
    b_head = math.radians(b.heading)

    a_speed_ms = a.speed / 3.6
    b_speed_ms = b.speed / 3.6

    # Component of A's velocity towards B
    a_towards = a_speed_ms * math.cos(a_head - brng_rad)
    # Component of B's velocity towards A (opposite direction)
    b_towards = b_speed_ms * math.cos(b_head - (brng_rad + math.pi))

    return a_towards + b_towards


def _stopping_time(speed_kmh: float, max_decel: float) -> float:
    """Time to stop in seconds."""
    speed_ms = speed_kmh / 3.6
    if speed_ms < 0.1:
        return 0.0
    return speed_ms / max_decel


def evaluate_pair(a: VehicleStateRecord, b: VehicleStateRecord) -> tuple[RiskLevel, str]:
    """Evaluate collision risk between two vehicles.
    Returns (risk_level, reason_string)."""
    config = get_config()

    # Both must be active enough to matter
    if a.state in (VehicleState.OFFLINE, VehicleState.UNKNOWN) and a.speed < 0.1:
        return RiskLevel.SAFE, ""
    if b.state in (VehicleState.OFFLINE, VehicleState.UNKNOWN) and b.speed < 0.1:
        return RiskLevel.SAFE, ""

    # Distance between vehicles
    distance = haversine(a.latitude, a.longitude, b.latitude, b.longitude)

    # If very far apart, skip
    if distance > 500:
        return RiskLevel.SAFE, ""

    # Check if they're on the same or connected segments
    same_segment = False
    connected_segment = False

    if a.current_segment and b.current_segment:
        if a.current_segment == b.current_segment:
            same_segment = True
        else:
            seg_a = road_graph.get_segment(a.current_segment)
            seg_b = road_graph.get_segment(b.current_segment)
            if seg_a and seg_b:
                shared_nodes = {seg_a.start_node, seg_a.end_node} & {seg_b.start_node, seg_b.end_node}
                if shared_nodes:
                    connected_segment = True
    elif a.current_segment or b.current_segment:
        # One on segment, one off — still check distance
        pass

    if not same_segment and not connected_segment and distance > config["dist_caution_meters"]:
        return RiskLevel.SAFE, ""

    # Closing speed
    cs = _closing_speed(a, b)

    # If moving apart, lower risk
    if cs < -2.0:
        return RiskLevel.SAFE, ""

    # Time to conflict
    if cs > 0.1:
        ttc = distance / cs
    else:
        ttc = float("inf")

    # Determine risk
    multiplier = 1.0
    blind_reason = ""
    if same_segment:
        seg = road_graph.get_segment(a.current_segment)
        if seg and seg.blind_corner:
            multiplier = config["blind_corner_threshold_multiplier"]
            blind_reason = f" on blind-corner segment {seg.segment_id}"

    # AI visibility safety margin: lower visibility -> more conservative.
    # Reduces all thresholds, making WARNING/CRITICAL trigger sooner.
    vis_margin = 1.0
    vis_note = ""
    try:
        from . import ai_state
        vis = ai_state._visibility
        vis_m = vis.get("estimated_visibility_m", 1000.0)
        if vis_m < 500:
            vis_margin = max(0.45, 0.35 + (vis_m / 500.0) * 0.65)
            vis_note = f", low visibility {vis_m:.0f}m (AI)"
    except Exception:
        pass
    multiplier = multiplier * vis_margin

    risk = RiskLevel.SAFE
    reason = ""

    critical_ttc = config["ttc_critical_seconds"] * multiplier
    warning_ttc = config["ttc_warning_seconds"] * multiplier
    caution_ttc = config["ttc_caution_seconds"] * multiplier
    critical_dist = config["dist_critical_meters"] * multiplier
    warning_dist = config["dist_warning_meters"] * multiplier
    caution_dist = config["dist_caution_meters"] * multiplier

    if (ttc < critical_ttc or distance < critical_dist) and cs > 0:
        risk = RiskLevel.CRITICAL
        reason = (
            f"Vehicles {a.vehicle_id} and {b.vehicle_id} approaching conflict zone. "
            f"TTC: {ttc:.1f}s, distance: {distance:.0f}m, closing speed: {cs * 3.6:.0f} km/h{blind_reason}{vis_note}."
        )
    elif (ttc < warning_ttc or distance < warning_dist) and cs > 0:
        risk = RiskLevel.WARNING
        reason = (
            f"Vehicles {a.vehicle_id} and {b.vehicle_id} converging. "
            f"TTC: {ttc:.1f}s, distance: {distance:.0f}m{blind_reason}{vis_note}."
        )
    elif (ttc < caution_ttc or distance < caution_dist) and cs > 0:
        risk = RiskLevel.CAUTION
        reason = (
            f"Vehicles {a.vehicle_id} and {b.vehicle_id} in proximity. "
            f"TTC: {ttc:.1f}s, distance: {distance:.0f}m{blind_reason}{vis_note}."
        )

    return risk, reason


async def evaluate_all_pairs() -> list[dict[str, Any]]:
    """Evaluate all vehicle pairs and return risk results."""
    vehicles = await vehicle_store.get_all()
    results = []

    for i in range(len(vehicles)):
        for j in range(i + 1, len(vehicles)):
            a, b = vehicles[i], vehicles[j]
            # Skip if both are truly offline
            if a.state == VehicleState.OFFLINE and b.state == VehicleState.OFFLINE:
                continue
            # Skip unknown vehicles with no data
            if a.state == VehicleState.UNKNOWN and b.state == VehicleState.UNKNOWN:
                continue

            risk, reason = evaluate_pair(a, b)

            if risk != RiskLevel.SAFE:
                results.append({
                    "vehicle_a": a.vehicle_id,
                    "vehicle_b": b.vehicle_id,
                    "risk_level": risk.value,
                    "reason": reason,
                })

            # Update individual vehicle risk to worst-case
            await vehicle_store.update_risk(a.vehicle_id, risk, reason)
            await vehicle_store.update_risk(b.vehicle_id, risk, reason)

    # Mark vehicles not in any conflict as SAFE
    involved = set()
    for r in results:
        involved.add(r["vehicle_a"])
        involved.add(r["vehicle_b"])

    for v in vehicles:
        if v.vehicle_id not in involved:
            await vehicle_store.update_risk(v.vehicle_id, RiskLevel.SAFE, "")

    return results
