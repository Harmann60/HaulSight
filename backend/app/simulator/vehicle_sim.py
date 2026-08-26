from __future__ import annotations

import asyncio
import math
import uuid
from datetime import datetime
from typing import Any

from ..config import get_config
from ..models import TelemetryPacket, GpsQuality
from ..services.road_graph import road_graph, haversine, bearing
from ..services.telemetry import ingest_telemetry
from ..api.websocket import broadcast

import random


# ── Vehicle routes along the road graph ────────────────────

# Each vehicle follows a sequence of nodes, looping
VEHICLE_ROUTES = {
    "VH1027": {
        "type": "dumper",
        "nodes": ["N1", "N2", "N3", "N4", "N5", "N6", "N7", "N12", "N11", "N10", "N9", "N8", "N4", "N3", "N2", "N1"],
        "speed_kmh": 25,
        "direction": 1,  # forward
    },
    "VH1031": {
        "type": "dumper",
        "nodes": ["N7", "N6", "N5", "N4", "N8", "N9", "N10", "N11", "N12", "N7"],
        "speed_kmh": 30,
        "direction": 1,
    },
    "VH1045": {
        "type": "grader",
        "nodes": ["N4", "N8", "N9", "N10", "N11", "N12", "N7", "N6", "N5", "N4"],
        "speed_kmh": 20,
        "direction": 1,
    },
    "VH1052": {
        "type": "excavator",
        "nodes": ["N1", "N2", "N3", "N4", "N3", "N2", "N1"],
        "speed_kmh": 15,
        "direction": 1,
    },
}


class VehicleSimulator:
    """Simulates vehicles moving along road graph routes."""

    def __init__(self) -> None:
        self._running = False
        self._vehicle_progress: dict[str, dict] = {}
        self._sequence_counters: dict[str, int] = {}
        self._active_scenario: str | None = None

    def _init_vehicle(self, vid: str, route_cfg: dict) -> None:
        nodes = route_cfg["nodes"]
        self._vehicle_progress[vid] = {
            "route": nodes,
            "segment_index": 0,
            "t": 0.0,  # interpolation along current segment [0,1]
            "speed_kmh": route_cfg["speed_kmh"],
            "paused": False,
            "gps_quality": GpsQuality.GOOD,
        }
        self._sequence_counters[vid] = 0

    def _get_position(self, vid: str) -> tuple[float, float, float, float]:
        """Returns (lat, lon, speed, heading)."""
        prog = self._vehicle_progress[vid]
        route = prog["route"]
        idx = prog["segment_index"]
        t = prog["t"]

        node_a_id = route[idx % len(route)]
        node_b_id = route[(idx + 1) % len(route)]

        node_a = road_graph.nodes.get(node_a_id)
        node_b = road_graph.nodes.get(node_b_id)
        if not node_a or not node_b:
            return 0, 0, 0, 0

        lat = node_a.latitude + t * (node_b.latitude - node_a.latitude)
        lon = node_a.longitude + t * (node_b.longitude - node_a.longitude)
        heading = bearing(node_a.latitude, node_a.longitude, node_b.latitude, node_b.longitude)
        speed = prog["speed_kmh"] + random.uniform(-2, 2)
        speed = max(0, speed)

        return lat, lon, speed, heading

    def _advance(self, vid: str) -> None:
        prog = self._vehicle_progress[vid]
        route = prog["route"]

        # Calculate segment length for timing
        idx = prog["segment_index"]
        node_a_id = route[idx % len(route)]
        node_b_id = route[(idx + 1) % len(route)]
        node_a = road_graph.nodes.get(node_a_id)
        node_b = road_graph.nodes.get(node_b_id)

        if node_a and node_b:
            seg_len = haversine(node_a.latitude, node_a.longitude, node_b.latitude, node_b.longitude)
            speed_ms = prog["speed_kmh"] / 3.6
            if speed_ms > 0:
                tick_time = 1.0  # simulator tick = 1 second
                progress_per_tick = (speed_ms * tick_time) / seg_len if seg_len > 0 else 0.5
            else:
                progress_per_tick = 0
        else:
            progress_per_tick = 0.3

        prog["t"] += progress_per_tick

        if prog["t"] >= 1.0:
            prog["t"] = 0.0
            prog["segment_index"] = (idx + 1) % (len(route) - 1)

    async def start(self) -> None:
        self._running = True
        config = get_config()
        tick = config["simulator_tick_seconds"]

        # Initialize vehicles
        for vid, cfg in VEHICLE_ROUTES.items():
            self._init_vehicle(vid, cfg)

        # Start a bit separated so vehicles don't overlap
        offsets = [0.0, 0.3, 0.5, 0.1]
        for i, vid in enumerate(VEHICLE_ROUTES):
            self._vehicle_progress[vid]["t"] = offsets[i % len(offsets)]
            self._vehicle_progress[vid]["segment_index"] = i % max(1, len(VEHICLE_ROUTES[vid]["nodes"]) - 1)

        print(f"[simulator] Started with {len(VEHICLE_ROUTES)} vehicles, tick={tick}s")

        while self._running:
            for vid, cfg in VEHICLE_ROUTES.items():
                prog = self._vehicle_progress.get(vid, {})
                is_paused = prog.get("paused", False)
                is_suppressed = prog.get("suppress", False)

                # Suppressed = no telemetry at all (network failure simulation)
                if is_suppressed:
                    continue

                lat, lon, speed, heading = self._get_position(vid)

                # If paused during scenario, keep speed but don't advance
                # If paused normally (e.g. network failure), report stopped
                if is_paused and vehicle_simulator.get_scenario():
                    pass  # keep speed as-is for risk calculation
                elif is_paused:
                    speed = 0.0

                # Vary GPS quality occasionally
                gps_quality = self._vehicle_progress.get(vid, {}).get("gps_quality", GpsQuality.GOOD)
                if not is_paused and random.random() < 0.02:
                    gps_quality = GpsQuality.POOR

                self._sequence_counters[vid] = self._sequence_counters.get(vid, 0) + 1

                packet = TelemetryPacket(
                    vehicle_id=vid,
                    latitude=lat,
                    longitude=lon,
                    speed=speed,
                    heading=heading,
                    gps_quality=gps_quality,
                    message_id=f"SIM-{vid}-{self._sequence_counters[vid]}",
                    sequence_number=self._sequence_counters[vid],
                    timestamp=datetime.utcnow(),
                )

                try:
                    await ingest_telemetry(packet)
                except Exception as e:
                    print(f"[simulator] Error ingesting {vid}: {e}")

                # Only advance if not paused
                if not is_paused:
                    self._advance(vid)

            await asyncio.sleep(tick)

    def stop(self) -> None:
        self._running = False

    def pause_vehicle(self, vid: str) -> None:
        if vid in self._vehicle_progress:
            self._vehicle_progress[vid]["paused"] = True

    def suppress_vehicle(self, vid: str) -> None:
        """Completely stop telemetry for a vehicle (simulates network loss)."""
        if vid in self._vehicle_progress:
            self._vehicle_progress[vid]["paused"] = True
            self._vehicle_progress[vid]["suppress"] = True

    def resume_vehicle(self, vid: str) -> None:
        if vid in self._vehicle_progress:
            self._vehicle_progress[vid]["paused"] = False
            self._vehicle_progress[vid]["suppress"] = False

    def set_gps_quality(self, vid: str, quality: GpsQuality) -> None:
        if vid in self._vehicle_progress:
            self._vehicle_progress[vid]["gps_quality"] = quality

    def reposition_vehicle(self, vid: str, segment_index: int, t: float = 0.1) -> None:
        """Teleport a vehicle to a specific position along its route."""
        if vid in self._vehicle_progress:
            prog = self._vehicle_progress[vid]
            prog["segment_index"] = segment_index
            prog["t"] = t
            prog["paused"] = False

    def reposition_on_segment(self, vid: str, segment_id: str, t: float = 0.5) -> None:
        """Teleport a vehicle to a specific road segment (by ID) at position t [0,1].
        Finds the segment in the vehicle's route and positions it there."""
        if vid not in self._vehicle_progress:
            return
        prog = self._vehicle_progress[vid]
        route = prog["route"]
        for i in range(len(route) - 1):
            seg_candidate = f"SEG_{route[i]}_{route[i+1]}"
            if seg_candidate == segment_id:
                prog["segment_index"] = i
                prog["t"] = t
                prog["paused"] = False
                return
        # Also check reverse direction
        for i in range(len(route) - 1):
            seg_candidate = f"SEG_{route[i+1]}_{route[i]}"
            if seg_candidate == segment_id:
                prog["segment_index"] = i
                prog["t"] = 1.0 - t  # flip t for reverse direction
                prog["paused"] = False
                return

    def set_scenario(self, scenario_name: str | None) -> None:
        self._active_scenario = scenario_name

    def get_scenario(self) -> str | None:
        return self._active_scenario


vehicle_simulator = VehicleSimulator()
