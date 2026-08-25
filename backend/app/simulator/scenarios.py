from __future__ import annotations

"""
Demo scenarios for HaulSight.
These modify the simulator to create specific demonstration situations.
"""

from ..simulator.vehicle_sim import vehicle_simulator, VEHICLE_ROUTES
from ..simulator.radar_sim import radar_simulator
from ..api.websocket import broadcast
from ..models import GpsQuality


async def scenario_1_normal_operation():
    """Scenario 1: Two vehicles approach a blind corner.
    Risk escalates: SAFE → CAUTION → WARNING → CRITICAL."""
    print("[scenario] Running Scenario 1: Normal blind corner approach")

    # Reset all vehicles
    for vid in VEHICLE_ROUTES:
        vehicle_simulator.resume_vehicle(vid)
        vehicle_simulator.set_gps_quality(vid, GpsQuality.GOOD)

    await broadcast({
        "type": "scenario",
        "data": {"name": "scenario_1", "description": "Normal blind corner approach"},
    })


async def scenario_2_network_failure():
    """Scenario 2: Gateway/network failure.
    Dashboard shows degraded state, radar continues."""
    print("[scenario] Running Scenario 2: Network/gateway failure")

    await broadcast({
        "type": "scenario",
        "data": {"name": "scenario_2", "description": "Network gateway failure simulated"},
    })

    # Simulate by pausing some vehicles (simulating lost telemetry)
    vehicle_simulator.pause_vehicle("VH1027")
    vehicle_simulator.pause_vehicle("VH1045")

    await broadcast({
        "type": "system_health",
        "data": {"gateway_status": "degraded", "message": "Gateway connectivity interrupted"},
    })


async def scenario_3_non_equipped_vehicle():
    """Scenario 3: Non-equipped vehicle detected by radar.
    Radar detects an unknown vehicle at a blind corner."""
    print("[scenario] Running Scenario 3: Non-equipped vehicle detection")

    # Radar simulator will pick up something unknown
    from ..models import RadarDetection
    from ..services import radar_service
    import uuid

    detection = RadarDetection(
        detection_id=str(uuid.uuid4())[:8],
        beacon_id="RADAR_ALPHA",
        detected_vehicle_id=None,  # Unknown vehicle
        range_meters=35.0,
        direction=180.0,
        confidence=0.85,
    )

    result = await radar_service.record_detection(detection)
    print(f"[scenario] Radar detection result: {result}")

    await broadcast({
        "type": "scenario",
        "data": {
            "name": "scenario_3",
            "description": "Non-equipped vehicle detected by radar at blind corner",
            "detection": result,
        },
    })


async def reset_all():
    """Reset all scenarios — resume normal operation."""
    print("[scenario] Resetting all scenarios")
    for vid in VEHICLE_ROUTES:
        vehicle_simulator.resume_vehicle(vid)
        vehicle_simulator.set_gps_quality(vid, GpsQuality.GOOD)

    await broadcast({
        "type": "system_health",
        "data": {"gateway_status": "online", "message": "All systems normal"},
    })

    await broadcast({
        "type": "scenario",
        "data": {"name": "reset", "description": "All systems restored to normal"},
    })
