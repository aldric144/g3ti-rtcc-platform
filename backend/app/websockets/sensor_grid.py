"""
Sensor Grid WebSocket handlers.

Provides real-time sensor event streaming and fusion updates.
"""

import json
from datetime import datetime, timezone
from typing import Any
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()


class SensorGridConnectionManager:
    """Manages WebSocket connections for sensor grid."""
    
    def __init__(self):
        self.active_connections: dict[str, list[WebSocket]] = {
            "events": [],
            "gunshots": [],
            "environmental": [],
            "crowd": [],
            "fusion": [],
            "health": [],
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


sensor_manager = SensorGridConnectionManager()


@router.websocket("/ws/sensors/events")
async def sensor_events_websocket(websocket: WebSocket):
    """WebSocket endpoint for all sensor events."""
    await sensor_manager.connect(websocket, "events")
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                
                await sensor_manager.broadcast("events", {
                    "type": "sensor_event",
                    "data": message,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                })
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON format",
                })
    except WebSocketDisconnect:
        sensor_manager.disconnect(websocket, "events")


@router.websocket("/ws/sensors/gunshots")
async def gunshot_events_websocket(websocket: WebSocket):
    """WebSocket endpoint for gunshot detection events."""
    await sensor_manager.connect(websocket, "gunshots")
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                
                await sensor_manager.broadcast("gunshots", {
                    "type": "gunshot_event",
                    "data": message,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                })
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON format",
                })
    except WebSocketDisconnect:
        sensor_manager.disconnect(websocket, "gunshots")


@router.websocket("/ws/sensors/environmental")
async def environmental_events_websocket(websocket: WebSocket):
    """WebSocket endpoint for environmental sensor events."""
    await sensor_manager.connect(websocket, "environmental")
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                
                await sensor_manager.broadcast("environmental", {
                    "type": "environmental_event",
                    "data": message,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                })
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON format",
                })
    except WebSocketDisconnect:
        sensor_manager.disconnect(websocket, "environmental")


@router.websocket("/ws/sensors/crowd")
async def crowd_events_websocket(websocket: WebSocket):
    """WebSocket endpoint for crowd density events."""
    await sensor_manager.connect(websocket, "crowd")
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                
                await sensor_manager.broadcast("crowd", {
                    "type": "crowd_event",
                    "data": message,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                })
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON format",
                })
    except WebSocketDisconnect:
        sensor_manager.disconnect(websocket, "crowd")


@router.websocket("/ws/sensors/fusion")
async def fusion_events_websocket(websocket: WebSocket):
    """WebSocket endpoint for fused sensor events."""
    await sensor_manager.connect(websocket, "fusion")
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                
                await sensor_manager.broadcast("fusion", {
                    "type": "fusion_event",
                    "data": message,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                })
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON format",
                })
    except WebSocketDisconnect:
        sensor_manager.disconnect(websocket, "fusion")


@router.websocket("/ws/sensors/health")
async def sensor_health_websocket(websocket: WebSocket):
    """WebSocket endpoint for sensor health updates."""
    await sensor_manager.connect(websocket, "health")
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                
                await sensor_manager.broadcast("health", {
                    "type": "health_update",
                    "data": message,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                })
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON format",
                })
    except WebSocketDisconnect:
        sensor_manager.disconnect(websocket, "health")
