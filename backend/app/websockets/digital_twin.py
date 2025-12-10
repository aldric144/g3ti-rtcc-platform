"""
Digital Twin WebSocket handlers.

Provides real-time entity updates and overlay streaming for the digital twin.
"""

import json
from datetime import datetime, timezone
from typing import Any
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()


class DigitalTwinConnectionManager:
    """Manages WebSocket connections for digital twin."""
    
    def __init__(self):
        self.active_connections: dict[str, list[WebSocket]] = {
            "entities": [],
            "overlays": [],
            "incidents": [],
            "playback": [],
            "sync": [],
        }
    
    async def connect(self, websocket: WebSocket, channel: str) -> None:
        """Accept a new WebSocket connection."""
        await websocket.accept()
        if channel in self.active_connections:
            self.active_connections[channel].append(websocket)
    
    def disconnect(self, websocket: WebSocket, channel: str) -> None:
        """Remove a WebSocket connection."""
        if channel in self.active_connections:
            if websocket in self.active_connections[channel]:
                self.active_connections[channel].remove(websocket)
    
    async def broadcast(self, channel: str, message: dict[str, Any]) -> None:
        """Broadcast a message to all connections on a channel."""
        if channel not in self.active_connections:
            return
        
        disconnected = []
        for connection in self.active_connections[channel]:
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.append(connection)
        
        for conn in disconnected:
            self.disconnect(conn, channel)


twin_manager = DigitalTwinConnectionManager()


@router.websocket("/ws/digital-twin/entities")
async def entities_websocket(websocket: WebSocket):
    """WebSocket endpoint for entity position updates."""
    await twin_manager.connect(websocket, "entities")
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                
                await twin_manager.broadcast("entities", {
                    "type": "entity_update",
                    "data": message,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                })
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON format",
                })
    except WebSocketDisconnect:
        twin_manager.disconnect(websocket, "entities")


@router.websocket("/ws/digital-twin/overlays")
async def overlays_websocket(websocket: WebSocket):
    """WebSocket endpoint for overlay updates."""
    await twin_manager.connect(websocket, "overlays")
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                
                await twin_manager.broadcast("overlays", {
                    "type": "overlay_update",
                    "data": message,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                })
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON format",
                })
    except WebSocketDisconnect:
        twin_manager.disconnect(websocket, "overlays")


@router.websocket("/ws/digital-twin/incidents")
async def incidents_websocket(websocket: WebSocket):
    """WebSocket endpoint for incident updates."""
    await twin_manager.connect(websocket, "incidents")
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                
                await twin_manager.broadcast("incidents", {
                    "type": "incident_update",
                    "data": message,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                })
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON format",
                })
    except WebSocketDisconnect:
        twin_manager.disconnect(websocket, "incidents")


@router.websocket("/ws/digital-twin/playback/{session_id}")
async def playback_websocket(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for time travel playback."""
    await twin_manager.connect(websocket, "playback")
    try:
        await websocket.send_json({
            "type": "playback_connected",
            "session_id": session_id,
            "status": "connected",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                
                await twin_manager.broadcast("playback", {
                    "type": "playback_update",
                    "session_id": session_id,
                    "data": message,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                })
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON format",
                })
    except WebSocketDisconnect:
        twin_manager.disconnect(websocket, "playback")


@router.websocket("/ws/digital-twin/sync")
async def sync_websocket(websocket: WebSocket):
    """WebSocket endpoint for full state synchronization."""
    await twin_manager.connect(websocket, "sync")
    try:
        await websocket.send_json({
            "type": "sync_connected",
            "status": "connected",
            "message": "Ready for state synchronization",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                
                await twin_manager.broadcast("sync", {
                    "type": "sync_update",
                    "data": message,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                })
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON format",
                })
    except WebSocketDisconnect:
        twin_manager.disconnect(websocket, "sync")
