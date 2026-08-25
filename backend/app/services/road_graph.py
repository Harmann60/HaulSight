from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

from ..models import RoadNode, RoadSegment


def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Distance in meters between two lat/lon points."""
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def bearing(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Bearing in degrees [0, 360) from point 1 to point 2."""
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dlam = math.radians(lon2 - lon1)
    x = math.sin(dlam) * math.cos(phi2)
    y = math.cos(phi1) * math.sin(phi2) - math.sin(phi1) * math.cos(phi2) * math.cos(dlam)
    brng = math.degrees(math.atan2(x, y))
    return (brng + 360) % 360


def point_to_segment_distance(
    plat: float, plon: float,
    slat1: float, slon1: float,
    slat2: float, slon2: float,
) -> float:
    """Approximate perpendicular distance from a point to a line segment, in meters.
    Uses a simple projection in local flat-earth approximation."""
    dlat = slat2 - slat1
    dlon = slon2 - slon1
    seg_len_sq = dlat * dlat + dlon * dlon
    if seg_len_sq < 1e-12:
        return haversine(plat, plon, slat1, slon1)

    t = max(0.0, min(1.0, ((plat - slat1) * dlat + (plon - slon1) * dlon) / seg_len_sq))
    proj_lat = slat1 + t * dlat
    proj_lon = slon1 + t * dlon
    return haversine(plat, plon, proj_lat, proj_lon)


def project_point_on_segment(
    plat: float, plon: float,
    slat1: float, slon1: float,
    slat2: float, slon2: float,
) -> float:
    """Return parameter t in [0,1] representing where the point projects onto the segment."""
    dlat = slat2 - slat1
    dlon = slon2 - slon1
    seg_len_sq = dlat * dlat + dlon * dlon
    if seg_len_sq < 1e-12:
        return 0.0
    t = ((plat - slat1) * dlat + (plon - slon1) * dlon) / seg_len_sq
    return max(0.0, min(1.0, t))


class RoadGraph:
    """In-memory road graph loaded from JSON."""

    def __init__(self) -> None:
        self.nodes: dict[str, RoadNode] = {}
        self.segments: dict[str, RoadSegment] = {}
        self.adjacency: dict[str, list[str]] = {}

    def load_from_file(self, path: str | Path) -> None:
        with open(path) as f:
            data = json.load(f)

        for nd in data.get("nodes", []):
            node = RoadNode(**nd)
            self.nodes[node.node_id] = node

        for seg in data.get("segments", []):
            segment = RoadSegment(**seg)
            self.segments[segment.segment_id] = segment
            self.adjacency.setdefault(segment.start_node, []).append(segment.segment_id)
            self.adjacency.setdefault(segment.end_node, []).append(segment.segment_id)

    def get_segment(self, segment_id: str) -> RoadSegment | None:
        return self.segments.get(segment_id)

    def get_segments_for_node(self, node_id: str) -> list[RoadSegment]:
        seg_ids = self.adjacency.get(node_id, [])
        return [self.segments[sid] for sid in seg_ids if sid in self.segments]

    def find_nearest_segment(self, lat: float, lon: float) -> tuple[RoadSegment | None, float]:
        """Find the nearest road segment to a point. Returns (segment, distance_m)."""
        best_seg = None
        best_dist = float("inf")
        for seg in self.segments.values():
            if not seg.is_active:
                continue
            d = point_to_segment_distance(lat, lon, seg.start_lat, seg.start_lon, seg.end_lat, seg.end_lon)
            if d < best_dist:
                best_dist = d
                best_seg = seg
        return best_seg, best_dist

    def get_connected_segments(self, segment_id: str) -> list[RoadSegment]:
        """Get segments that share a node with the given segment."""
        seg = self.segments.get(segment_id)
        if not seg:
            return []
        connected = []
        for other_id, other_seg in self.segments.items():
            if other_id == segment_id or not other_seg.is_active:
                continue
            if (other_seg.start_node in (seg.start_node, seg.end_node) or
                    other_seg.end_node in (seg.start_node, seg.end_node)):
                connected.append(other_seg)
        return connected


road_graph = RoadGraph()
