from __future__ import annotations

from fastapi import APIRouter

from ..services.road_graph import road_graph

router = APIRouter(prefix="/api/v1/roads", tags=["roads"])


@router.get("")
async def get_road_graph():
    return {
        "nodes": [n.model_dump() for n in road_graph.nodes.values()],
        "segments": [s.model_dump() for s in road_graph.segments.values()],
    }


@router.get("/nodes")
async def get_nodes():
    return [n.model_dump() for n in road_graph.nodes.values()]


@router.get("/segments")
async def get_segments():
    return [s.model_dump() for s in road_graph.segments.values()]
