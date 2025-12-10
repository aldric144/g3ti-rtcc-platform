"""
Predictive AI WebSocket handlers.

Provides real-time prediction updates and alert streaming.
"""

import json
from datetime import datetime, timezone
from typing import Any
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()


class PredictiveAIConnectionManager:
    """Manages WebSocket connections for predictive AI."""
    
    def __init__(self):
        self.active_connections: dict[str, list[WebSocket]] = {
            "risk": [],
            "clusters": [],
            "patrol": [],
            "trajectories": [],
            "alerts": [],
            "fairness": [],
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


predictive_manager = PredictiveAIConnectionManager()


@router.websocket("/ws/predictive/risk")
async def risk_updates_websocket(websocket: WebSocket):
    """WebSocket endpoint for risk terrain updates."""
    await predictive_manager.connect(websocket, "risk")
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                
                await predictive_manager.broadcast("risk", {
                    "type": "risk_update",
                    "data": message,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                })
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON format",
                })
    except WebSocketDisconnect:
        predictive_manager.disconnect(websocket, "risk")


@router.websocket("/ws/predictive/clusters")
async def clusters_websocket(websocket: WebSocket):
    """WebSocket endpoint for violence cluster updates."""
    await predictive_manager.connect(websocket, "clusters")
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                
                await predictive_manager.broadcast("clusters", {
                    "type": "cluster_update",
                    "data": message,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                })
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON format",
                })
    except WebSocketDisconnect:
        predictive_manager.disconnect(websocket, "clusters")


@router.websocket("/ws/predictive/patrol")
async def patrol_websocket(websocket: WebSocket):
    """WebSocket endpoint for patrol optimization updates."""
    await predictive_manager.connect(websocket, "patrol")
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                
                await predictive_manager.broadcast("patrol", {
                    "type": "patrol_update",
                    "data": message,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                })
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON format",
                })
    except WebSocketDisconnect:
        predictive_manager.disconnect(websocket, "patrol")


@router.websocket("/ws/predictive/trajectories")
async def trajectories_websocket(websocket: WebSocket):
    """WebSocket endpoint for trajectory prediction updates."""
    await predictive_manager.connect(websocket, "trajectories")
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                
                await predictive_manager.broadcast("trajectories", {
                    "type": "trajectory_update",
                    "data": message,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                })
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON format",
                })
    except WebSocketDisconnect:
        predictive_manager.disconnect(websocket, "trajectories")


@router.websocket("/ws/predictive/alerts")
async def alerts_websocket(websocket: WebSocket):
    """WebSocket endpoint for predictive alerts."""
    await predictive_manager.connect(websocket, "alerts")
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                
                await predictive_manager.broadcast("alerts", {
                    "type": "alert_update",
                    "data": message,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                })
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON format",
                })
    except WebSocketDisconnect:
        predictive_manager.disconnect(websocket, "alerts")


@router.websocket("/ws/predictive/fairness")
async def fairness_websocket(websocket: WebSocket):
    """WebSocket endpoint for fairness and bias alerts."""
    await predictive_manager.connect(websocket, "fairness")
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                
                await predictive_manager.broadcast("fairness", {
                    "type": "fairness_update",
                    "data": message,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                })
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON format",
                })
    except WebSocketDisconnect:
        predictive_manager.disconnect(websocket, "fairness")
