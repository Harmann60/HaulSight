from __future__ import annotations

"""
Demo scenarios for HaulSight.
Each scenario positions vehicles and sets system state for clear demonstration.
"""

from ..simulator.vehicle_sim import vehicle_simulator, VEHICLE_ROUTES
from ..simulator.radar_sim import radar_simulator
from ..api.websocket import broadcast
from ..models import GpsQuality


async def scenario_1_normal_operation():
    """Scenario 1: Two vehicles approach Blind Corner Alpha from opposite directions.
    VH1027 approaching N3 from N2 side, VH1031 approaching N3 from N4 side.
    Risk escalates: SAFE → CAUTION → WARNING → CRITICAL."""
    print("[scenario] Running Scenario 1: Blind corner collision course")

    vehicle_simulator.set_scenario("scenario_1")

    # SCENARIO: Two dumpers on the same haul road approaching Blind Corner Alpha (N3).
    # VH1027 is behind (near N2) and faster (25 km/h).
    # VH1052 is ahead (near N3) and slower (15 km/h).
    # VH1027 is catching up → collision risk as they approach the blind corner.

    # Both on SEG_N2_N3 (blind corner segment, ~250m long):
    # VH1027 at t=0.45, VH1052 at t=0.55 → ~25m apart
    # VH1027 (25km/h) catching up to VH1052 (15km/h) → TTC ~6s → WARNING/CRITICAL
    vehicle_simulator.reposition_on_segment("VH1027", "SEG_N2_N3", t=0.45)
    vehicle_simulator.set_gps_quality("VH1027", GpsQuality.GOOD)

    vehicle_simulator.reposition_on_segment("VH1052", "SEG_N2_N3", t=0.55)
    vehicle_simulator.set_gps_quality("VH1052", GpsQuality.GOOD)

    # Move other vehicles to different roads so they don't interfere
    vehicle_simulator.reposition_on_segment("VH1031", "SEG_N9_N10", t=0.5)
    vehicle_simulator.reposition_on_segment("VH1045", "SEG_N7_N12", t=0.5)

    # Pause all vehicles so they stay in position for risk evaluation
    # The risk engine will see them close on the same blind-corner segment
    for vid in VEHICLE_ROUTES:
        vehicle_simulator.pause_vehicle(vid)

    # Resume all vehicles
    for vid in VEHICLE_ROUTES:
        vehicle_simulator.resume_vehicle(vid)

    await broadcast({
        "type": "scenario",
        "data": {
            "name": "scenario_1",
            "title": "Blind Corner Collision Course",
            "description": "VH1027 and VH1052 approaching Blind Corner Alpha from same segment — risk escalation",
            "status": "active",
        },
    })


async def scenario_2_network_failure():
    """Scenario 2: Gateway/network failure.
    Two vehicles stop transmitting. Dashboard shows degraded state.
    Radar beacons continue working."""
    print("[scenario] Running Scenario 2: Network gateway failure")

    vehicle_simulator.set_scenario("scenario_2")

    # Suppress two vehicles — no telemetry sent at all → STALE → OFFLINE
    vehicle_simulator.suppress_vehicle("VH1027")
    vehicle_simulator.suppress_vehicle("VH1045")

    # Broadcast scenario notification FIRST
    await broadcast({
        "type": "scenario",
        "data": {
            "name": "scenario_2",
            "title": "Network Gateway Failure",
            "description": "VH1027 and VH1045 stopped transmitting — gateway degraded. Radar beacons still operational.",
            "status": "active",
        },
    })

    # Then broadcast the degraded health
    await broadcast({
        "type": "gateway_status",
        "data": {"gateway_status": "degraded", "message": "Gateway connectivity interrupted"},
    })


async def scenario_3_non_equipped_vehicle():
    """Scenario 3: Non-equipped vehicle detected by radar at blind corner.
    Radar detects an unknown vehicle, triggers local warning."""
    print("[scenario] Running Scenario 3: Non-equipped vehicle detection")

    vehicle_simulator.set_scenario("scenario_3")

    # Trigger a radar detection for an unknown vehicle
    from ..models import RadarDetection
    from ..services import radar_service
    import uuid

    detection = RadarDetection(
        detection_id=str(uuid.uuid4())[:8],
        beacon_id="RADAR_ALPHA",
        detected_vehicle_id=None,  # Unknown vehicle — no HaulSight unit
        range_meters=35.0,
        direction=180.0,
        confidence=0.85,
    )

    result = await radar_service.record_detection(detection)

    await broadcast({
        "type": "scenario",
        "data": {
            "name": "scenario_3",
            "title": "Non-Equipped Vehicle Detected",
            "description": "Unknown vehicle detected by RADAR_ALPHA at Blind Corner Alpha — no GPS unit, radar-only detection",
            "status": "active",
            "detection": result,
        },
    })

    await broadcast({
        "type": "radar_warning",
        "data": {
            "beacon_id": "RADAR_ALPHA",
            "message": f"⚠ LOCAL WARNING: Non-equipped vehicle detected {detection.range_meters:.0f}m from Blind Corner Alpha",
            "range": detection.range_meters,
        },
    })


async def reset_all():
    """Reset all scenarios — resume normal operation."""
    print("[scenario] Resetting all scenarios")

    vehicle_simulator.set_scenario(None)

    for vid in VEHICLE_ROUTES:
        vehicle_simulator.resume_vehicle(vid)
        vehicle_simulator.set_gps_quality(vid, GpsQuality.GOOD)

    await broadcast({
        "type": "gateway_status",
        "data": {"gateway_status": "online", "message": "All systems normal"},
    })

    await broadcast({
        "type": "scenario",
        "data": {
            "name": "reset",
            "title": "Normal Operation",
            "description": "All systems restored to normal",
            "status": "inactive",
        },
    })
