from __future__ import annotations

import asyncio
import json
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()

_clients: list[WebSocket] = []
_lock = asyncio.Lock()


async def broadcast(message: dict[str, Any]) -> None:
    """Send a message to all connected WebSocket clients."""
    data = json.dumps(message, default=str)
    dead = []
    async with _lock:
        for ws in _clients:
            try:
                await ws.send_text(data)
            except Exception:
                dead.append(ws)
        for ws in dead:
            _clients.remove(ws)


@router.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    async with _lock:
        _clients.append(ws)
    try:
        while True:
            # Keep connection alive, handle client messages if needed
            data = await ws.receive_text()
            # Client can send pings or commands
            if data == "ping":
                await ws.send_text(json.dumps({"type": "pong"}))
    except WebSocketDisconnect:
        pass
    finally:
        async with _lock:
            if ws in _clients:
                _clients.remove(ws)
