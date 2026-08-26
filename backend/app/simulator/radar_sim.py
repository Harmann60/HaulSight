from __future__ import annotations

import asyncio
import uuid
import random
import math
from datetime import datetime

from ..models import RadarDetection
from ..services import radar_service
from ..services.road_graph import road_graph
from ..api.websocket import broadcast


class RadarSimulator:
    """Simulates radar beacon detections at blind corners."""

    def __init__(self) -> None:
        self._running = False
        self._detection_interval = 3.0  # seconds between checks

    async def start(self) -> None:
        self._running = True
        print("[radar_sim] Started")

        # Import here to avoid circular import
        from .vehicle_sim import vehicle_simulator

        while self._running:
            # Skip random detections during active scenarios
            if vehicle_simulator.get_scenario():
                await asyncio.sleep(self._detection_interval)
                continue

            # Simulate occasional detections at blind corners
            beacons = radar_service.get_all_beacons()

            for beacon in beacons:
                if beacon["status"] != "online":
                    continue

                # Random chance of detecting something
                if random.random() < 0.15:
                    detection_range = random.uniform(10, 80)
                    direction = random.uniform(0, 360)
                    confidence = random.uniform(0.6, 0.95)

                    # Always detect known vehicles during normal operation
                    known_vehicles = ["VH1027", "VH1031", "VH1045", "VH1052"]
                    detected_vehicle = random.choice(known_vehicles)

                    detection = RadarDetection(
                        detection_id=str(uuid.uuid4())[:8],
                        beacon_id=beacon["beacon_id"],
                        detected_vehicle_id=detected_vehicle,
                        range_meters=detection_range,
                        direction=direction,
                        confidence=confidence,
                        timestamp=datetime.utcnow(),
                    )

                    result = await radar_service.record_detection(detection)

                    if result.get("local_warning"):
                        await broadcast({
                            "type": "radar_warning",
                            "data": {
                                "beacon_id": beacon["beacon_id"],
                                "message": result.get("warning_message", "Object detected"),
                                "range": detection_range,
                            },
                        })

            await asyncio.sleep(self._detection_interval)

    def stop(self) -> None:
        self._running = False


radar_simulator = RadarSimulator()
