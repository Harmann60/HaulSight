from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


# ── Enums ──────────────────────────────────────────────────

class VehicleState(str, Enum):
    UNKNOWN = "UNKNOWN"
    LIVE = "LIVE"
    STALE = "STALE"
    DEGRADED = "DEGRADED"
    OFFLINE = "OFFLINE"


class RiskLevel(str, Enum):
    SAFE = "SAFE"
    CAUTION = "CAUTION"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class GpsQuality(str, Enum):
    GOOD = "good"
    POOR = "poor"
    INVALID = "invalid"


class AlertStatus(str, Enum):
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    EXPIRED = "expired"


class VehicleType(str, Enum):
    DUMPER = "dumper"
    GRADER = "grader"
    EXCAVATOR = "excavator"
    DRILL = "drill"
    WATER_TANKER = "water_tanker"
    BUS = "bus"
    LIGHT_VEHICLE = "light_vehicle"


# ── Telemetry Ingestion ───────────────────────────────────

class TelemetryPacket(BaseModel):
    vehicle_id: str
    latitude: float
    longitude: float
    speed: float = Field(ge=0)
    heading: float = Field(ge=0, lt=360)
    gps_quality: GpsQuality = GpsQuality.GOOD
    message_id: str
    sequence_number: int = 0
    timestamp: datetime | None = None


# ── Vehicle ────────────────────────────────────────────────

class VehicleProfile(BaseModel):
    vehicle_id: str
    vehicle_type: VehicleType = VehicleType.DUMPER
    is_equipped: bool = True


class VehicleStateRecord(BaseModel):
    vehicle_id: str
    vehicle_type: VehicleType = VehicleType.DUMPER
    is_equipped: bool = True
    state: VehicleState = VehicleState.UNKNOWN
    latitude: float = 0.0
    longitude: float = 0.0
    speed: float = 0.0
    heading: float = 0.0
    gps_quality: GpsQuality = GpsQuality.GOOD
    current_segment: str | None = None
    risk_level: RiskLevel = RiskLevel.SAFE
    risk_reason: str = ""
    last_seen: datetime | None = None
    last_sequence: int = -1


# ── Road ───────────────────────────────────────────────────

class RoadNode(BaseModel):
    node_id: str
    latitude: float
    longitude: float
    node_type: str = "waypoint"
    name: str | None = None


class RoadSegment(BaseModel):
    segment_id: str
    start_node: str
    end_node: str
    start_lat: float
    start_lon: float
    end_lat: float
    end_lon: float
    speed_limit: float = 30.0
    gradient: float = 0.0
    width: float = 10.0
    blind_corner: bool = False
    is_active: bool = True


# ── Alert ──────────────────────────────────────────────────

class Alert(BaseModel):
    alert_id: str
    vehicle_ids: list[str]
    severity: RiskLevel
    reason: str
    segment_id: str | None = None
    status: AlertStatus = AlertStatus.ACTIVE
    created_at: datetime = Field(default_factory=datetime.utcnow)
    resolved_at: datetime | None = None


# ── Radar ──────────────────────────────────────────────────

class RadarBeacon(BaseModel):
    beacon_id: str
    node_id: str
    latitude: float
    longitude: float
    status: str = "online"
    last_heartbeat: datetime | None = None


class RadarDetection(BaseModel):
    detection_id: str
    beacon_id: str
    detected_vehicle_id: str | None = None
    range_meters: float = 0.0
    direction: float = 0.0
    confidence: float = 0.8
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ── API Responses ──────────────────────────────────────────

class VehicleResponse(BaseModel):
    vehicle_id: str
    vehicle_type: str
    is_equipped: bool
    state: str
    latitude: float
    longitude: float
    speed: float
    heading: float
    gps_quality: str
    current_segment: str | None
    risk_level: str
    risk_reason: str
    last_seen: str | None


class AlertResponse(BaseModel):
    alert_id: str
    vehicle_ids: list[str]
    severity: str
    reason: str
    segment_id: str | None
    status: str
    created_at: str
    resolved_at: str | None


class HealthResponse(BaseModel):
    status: str
    vehicles_tracked: int
    active_alerts: int
    radar_beacons_online: int
    gateway_status: str
    uptime_seconds: float
