from __future__ import annotations

import asyncio
import time
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import load_config, get_config
from .database import get_db, close_db
from .services.road_graph import road_graph
from .services import radar_service
from .services.risk_engine import evaluate_all_pairs
from .services.alert_manager import process_risk_results
from .api.websocket import broadcast
from .simulator.vehicle_sim import vehicle_simulator
from .simulator.radar_sim import radar_simulator

from .api import vehicles, roads, alerts, radar, websocket

_START_TIME = time.time()

_APP = None


async def _risk_loop():
    """Periodic risk evaluation loop."""
    config = get_config()
    tick = config.get("telemetry_tick_seconds", 0.5)
    while True:
        try:
            results = await evaluate_all_pairs()
            alert_events = await process_risk_results(results)
            for event in alert_events:
                await broadcast(event)

            # Broadcast vehicle states
            from .state import vehicle_store
            vehicles_data = await vehicle_store.get_all()
            await broadcast({
                "type": "vehicle_update",
                "data": [
                    {
                        "vehicle_id": v.vehicle_id,
                        "vehicle_type": v.vehicle_type.value if hasattr(v.vehicle_type, 'value') else v.vehicle_type,
                        "is_equipped": v.is_equipped,
                        "state": v.state.value,
                        "latitude": v.latitude,
                        "longitude": v.longitude,
                        "speed": v.speed,
                        "heading": v.heading,
                        "gps_quality": v.gps_quality.value if hasattr(v.gps_quality, 'value') else v.gps_quality,
                        "current_segment": v.current_segment,
                        "risk_level": v.risk_level.value,
                        "risk_reason": v.risk_reason,
                        "last_seen": v.last_seen.isoformat() if v.last_seen else None,
                    }
                    for v in vehicles_data
                ],
            })

            # Broadcast active alerts
            from .services.alert_manager import get_active_alerts
            await broadcast({
                "type": "alert_update",
                "data": get_active_alerts(),
            })

            # Broadcast system health
            beacon_count = len(radar_service.get_all_beacons())
            online_beacons = sum(1 for b in radar_service.get_all_beacons() if b["status"] == "online")
            await broadcast({
                "type": "system_health",
                "data": {
                    "status": "online",
                    "vehicles_tracked": len(vehicles_data),
                    "active_alerts": len(get_active_alerts()),
                    "radar_beacons_online": f"{online_beacons}/{beacon_count}",
                    "gateway_status": "online",
                    "uptime_seconds": round(time.time() - _START_TIME),
                },
            })
        except Exception as e:
            print(f"[risk_loop] Error: {e}")
        await asyncio.sleep(tick)


async def _stale_loop():
    """Periodic stale/offline detection."""
    from .services.stale_detector import stale_detection_loop
    await stale_detection_loop(broadcast_callback=broadcast)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    config = load_config()
    print("[haulshight] Loading config...")
    print(f"[haulshight] Stale threshold: {config['stale_threshold_seconds']}s")

    # Initialize database
    db = await get_db()
    print("[haulshight] Database initialized")

    # Load road graph
    graph_path = Path(__file__).resolve().parent.parent / "data" / "mine_graph.json"
    road_graph.load_from_file(graph_path)
    print(f"[haulshight] Road graph loaded: {len(road_graph.nodes)} nodes, {len(road_graph.segments)} segments")

    # Load radar beacons from graph
    import json
    with open(graph_path) as f:
        graph_data = json.load(f)
    await radar_service.load_beacons_from_graph(graph_data)
    print(f"[haulshight] Radar beacons loaded: {len(radar_service.get_all_beacons())}")

    # Register vehicles in DB
    for vid, cfg in vehicle_simulator.__class__.__mro__[0].__dict__.get('__init__', lambda s: None).__code__.co_varnames[:0]:
        pass
    from .simulator.vehicle_sim import VEHICLE_ROUTES
    for vid, cfg in VEHICLE_ROUTES.items():
        await db.execute(
            "INSERT OR IGNORE INTO vehicles (vehicle_id, vehicle_type, is_equipped) VALUES (?,?,?)",
            (vid, cfg["type"], 1),
        )
    await db.commit()

    # Start background tasks
    risk_task = asyncio.create_task(_risk_loop())
    stale_task = asyncio.create_task(_stale_loop())
    sim_task = asyncio.create_task(vehicle_simulator.start())
    radar_task = asyncio.create_task(radar_simulator.start())

    print("[haulshight] All systems started")

    yield

    # Shutdown
    vehicle_simulator.stop()
    radar_simulator.stop()
    risk_task.cancel()
    stale_task.cancel()
    sim_task.cancel()
    radar_task.cancel()
    await close_db()
    print("[haulshight] Shutdown complete")


def create_app() -> FastAPI:
    global _APP
    config = get_config() if get_config() else load_config()

    _APP = FastAPI(
        title="HaulSight",
        description="Mine vehicle safety and collision risk monitoring system",
        version="0.1.0",
        lifespan=lifespan,
    )

    _APP.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    _APP.include_router(vehicles.router)
    _APP.include_router(roads.router)
    _APP.include_router(alerts.router)
    _APP.include_router(radar.router)
    _APP.include_router(websocket.router)

    @_APP.get("/api/v1/health")
    async def health():
        from .state import vehicle_store
        from .services.alert_manager import get_active_alerts
        v_count = await vehicle_store.count()
        a_count = len(get_active_alerts())
        beacon_count = len(radar_service.get_all_beacons())
        online_beacons = sum(1 for b in radar_service.get_all_beacons() if b["status"] == "online")
        return {
            "status": "ok",
            "vehicles_tracked": v_count,
            "active_alerts": a_count,
            "radar_beacons_online": f"{online_beacons}/{beacon_count}",
            "gateway_status": "online",
            "uptime_seconds": round(time.time() - _START_TIME),
        }

    @_APP.get("/api/v1/config")
    async def get_current_config():
        return get_config()

    @_APP.post("/api/v1/scenario/{scenario_name}")
    async def run_scenario(scenario_name: str):
        from .simulator.scenarios import (
            scenario_1_normal_operation,
            scenario_2_network_failure,
            scenario_3_non_equipped_vehicle,
            reset_all,
        )
        scenarios = {
            "1": scenario_1_normal_operation,
            "normal": scenario_1_normal_operation,
            "2": scenario_2_network_failure,
            "failure": scenario_2_network_failure,
            "3": scenario_3_non_equipped_vehicle,
            "non_equipped": scenario_3_non_equipped_vehicle,
            "reset": reset_all,
        }
        fn = scenarios.get(scenario_name)
        if not fn:
            return {"error": f"Unknown scenario: {scenario_name}"}
        await fn()
        return {"status": "ok", "scenario": scenario_name}

    return _APP


app = create_app()
