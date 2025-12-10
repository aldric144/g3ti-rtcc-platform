"""
Drone WebSocket handlers.

Provides real-time telemetry streaming and command channels for drones.
"""

import json
from datetime import datetime, timezone
from typing import Any
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()


class DroneConnectionManager:
    """Manages WebSocket connections for drone telemetry."""
    
    def __init__(self):
        self.active_connections: dict[str, list[WebSocket]] = {
            "telemetry": [],
            "commands": [],
            "missions": [],
            "dispatch": [],
            "video": [],
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
    
    async def send_to_drone(self, drone_id: str, message: dict[str, Any]) -> None:
        """Send a message to a specific drone's connections."""
        await self.broadcast("commands", {
            "type": "drone_command",
            "drone_id": drone_id,
            "data": message,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })


drone_manager = DroneConnectionManager()


@router.websocket("/ws/drones/telemetry")
async def drone_telemetry_websocket(websocket: WebSocket):
    """WebSocket endpoint for drone telemetry streaming."""
    await drone_manager.connect(websocket, "telemetry")
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                
                await drone_manager.broadcast("telemetry", {
                    "type": "telemetry_update",
                    "data": message,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                })
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON format",
                })
    except WebSocketDisconnect:
        drone_manager.disconnect(websocket, "telemetry")


@router.websocket("/ws/drones/commands")
async def drone_commands_websocket(websocket: WebSocket):
    """WebSocket endpoint for drone command channel."""
    await drone_manager.connect(websocket, "commands")
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                
                await drone_manager.broadcast("commands", {
                    "type": "command_update",
                    "data": message,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                })
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON format",
                })
    except WebSocketDisconnect:
        drone_manager.disconnect(websocket, "commands")


@router.websocket("/ws/drones/missions")
async def drone_missions_websocket(websocket: WebSocket):
    """WebSocket endpoint for drone mission updates."""
    await drone_manager.connect(websocket, "missions")
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                
                await drone_manager.broadcast("missions", {
                    "type": "mission_update",
                    "data": message,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                })
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON format",
                })
    except WebSocketDisconnect:
        drone_manager.disconnect(websocket, "missions")


@router.websocket("/ws/drones/dispatch")
async def drone_dispatch_websocket(websocket: WebSocket):
    """WebSocket endpoint for auto-dispatch events."""
    await drone_manager.connect(websocket, "dispatch")
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                
                await drone_manager.broadcast("dispatch", {
                    "type": "dispatch_update",
                    "data": message,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                })
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON format",
                })
    except WebSocketDisconnect:
        drone_manager.disconnect(websocket, "dispatch")


@router.websocket("/ws/drones/video/{drone_id}")
async def drone_video_websocket(websocket: WebSocket, drone_id: str):
    """WebSocket endpoint for drone video streaming."""
    await drone_manager.connect(websocket, "video")
    try:
        await websocket.send_json({
            "type": "video_stream_info",
            "drone_id": drone_id,
            "status": "connected",
            "message": "Video stream connection established",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        
        while True:
            data = await websocket.receive_bytes()
            
            await drone_manager.broadcast("video", {
                "type": "video_frame",
                "drone_id": drone_id,
                "frame_size": len(data),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })
    except WebSocketDisconnect:
        drone_manager.disconnect(websocket, "video")
