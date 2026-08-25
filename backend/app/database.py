from __future__ import annotations

import aiosqlite

from .config import db_path

_DB: aiosqlite.Connection | None = None

_SCHEMA = """
CREATE TABLE IF NOT EXISTS vehicles (
    vehicle_id TEXT PRIMARY KEY,
    vehicle_type TEXT NOT NULL DEFAULT 'dumper',
    is_equipped INTEGER NOT NULL DEFAULT 1,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS telemetry_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vehicle_id TEXT NOT NULL,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    speed REAL NOT NULL,
    heading REAL NOT NULL,
    gps_quality TEXT DEFAULT 'good',
    message_id TEXT UNIQUE,
    sequence_number INTEGER,
    received_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS road_nodes (
    node_id TEXT PRIMARY KEY,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    node_type TEXT DEFAULT 'waypoint',
    name TEXT
);

CREATE TABLE IF NOT EXISTS road_segments (
    segment_id TEXT PRIMARY KEY,
    start_node TEXT NOT NULL,
    end_node TEXT NOT NULL,
    start_lat REAL NOT NULL,
    start_lon REAL NOT NULL,
    end_lat REAL NOT NULL,
    end_lon REAL NOT NULL,
    speed_limit REAL DEFAULT 30,
    gradient REAL DEFAULT 0,
    width REAL DEFAULT 10,
    blind_corner INTEGER DEFAULT 0,
    is_active INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS alerts (
    alert_id TEXT PRIMARY KEY,
    vehicle_ids TEXT NOT NULL,
    severity TEXT NOT NULL,
    reason TEXT NOT NULL,
    segment_id TEXT,
    status TEXT DEFAULT 'active',
    created_at TEXT DEFAULT (datetime('now')),
    resolved_at TEXT
);

CREATE TABLE IF NOT EXISTS radar_beacons (
    beacon_id TEXT PRIMARY KEY,
    node_id TEXT NOT NULL,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    status TEXT DEFAULT 'online',
    last_heartbeat TEXT
);

CREATE TABLE IF NOT EXISTS radar_detections (
    detection_id TEXT PRIMARY KEY,
    beacon_id TEXT NOT NULL,
    detected_vehicle_id TEXT,
    range_meters REAL,
    direction REAL,
    confidence REAL DEFAULT 0.8,
    timestamp TEXT DEFAULT (datetime('now'))
);
"""


async def get_db() -> aiosqlite.Connection:
    global _DB
    if _DB is None:
        _DB = await aiosqlite.connect(db_path())
        _DB.row_factory = aiosqlite.Row
        await _DB.executescript(_SCHEMA)
        await _DB.commit()
    return _DB


async def close_db() -> None:
    global _DB
    if _DB is not None:
        await _DB.close()
        _DB = None
