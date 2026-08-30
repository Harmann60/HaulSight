from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml

_DEFAULTS: dict[str, Any] = {
    "stale_threshold_seconds": 10,
    "offline_threshold_seconds": 30,
    "state_check_interval_seconds": 2,
    "telemetry_tick_seconds": 0.5,
    "simulator_tick_seconds": 1.0,
    "risk_debounce_ticks": 3,
    "risk_downgrade_ticks": 6,
    "alert_suppression_window_seconds": 30,
    "alert_expiry_seconds": 300,
    "max_speed_kmh": 60,
    "max_deceleration_ms2": 3.0,
    "ttc_critical_seconds": 5.0,
    "ttc_warning_seconds": 10.0,
    "ttc_caution_seconds": 15.0,
    "dist_critical_meters": 20.0,
    "dist_warning_meters": 50.0,
    "dist_caution_meters": 100.0,
    "blind_corner_threshold_multiplier": 0.7,
    "gps_jump_max_meters": 500.0,
    "cors_origins": ["http://localhost:5173", "http://localhost:3000"],
}

_config: dict[str, Any] = {}


def _config_path() -> Path:
    return Path(__file__).resolve().parent.parent / "data" / "default_config.yaml"


def load_config() -> dict[str, Any]:
    global _config
    path = _config_path()
    if path.exists():
        with open(path) as f:
            file_cfg = yaml.safe_load(f) or {}
    else:
        file_cfg = {}
    _config = {**_DEFAULTS, **file_cfg}
    return _config


def get_config() -> dict[str, Any]:
    if not _config:
        load_config()
    return _config


def update_config(updates: dict[str, Any]) -> dict[str, Any]:
    _config.update(updates)
    return _config


def db_path() -> str:
    if os.environ.get("VERCEL"):
        return "/tmp/haulsight.db"

    return str(Path(__file__).resolve().parent.parent / "data" / "haulsight.db")
