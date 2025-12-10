"""
Phase 19: Robotics WebSocket Module

Provides WebSocket channels for real-time robotics operations:
- /ws/robotics/fleet - Fleet status updates
- /ws/robotics/telemetry - Real-time telemetry streaming
- /ws/robotics/missions - Mission status and events
- /ws/robotics/perimeter - Perimeter security alerts
- /ws/robotics/swarms - Swarm coordination updates
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Set
from fastapi import WebSocket, WebSocketDisconnect
import json
import asyncio


class RoboticsConnectionManager:
    """Manager for robotics WebSocket connections."""

    def __init__(self):
        self.fleet_connections: Set[WebSocket] = set()
        self.telemetry_connections: Dict[str, Set[WebSocket]] = {}
        self.mission_connections: Dict[str, Set[WebSocket]] = {}
        self.perimeter_connections: Set[WebSocket] = set()
        self.swarm_connections: Dict[str, Set[WebSocket]] = {}
        self.all_connections: Set[WebSocket] = set()

    async def connect_fleet(self, websocket: WebSocket):
        """Connect to fleet updates channel."""
        await websocket.accept()
        self.fleet_connections.add(websocket)
        self.all_connections.add(websocket)

    async def connect_telemetry(self, websocket: WebSocket, robot_id: Optional[str] = None):
        """Connect to telemetry channel."""
        await websocket.accept()
        key = robot_id or "all"
        if key not in self.telemetry_connections:
            self.telemetry_connections[key] = set()
        self.telemetry_connections[key].add(websocket)
        self.all_connections.add(websocket)

    async def connect_mission(self, websocket: WebSocket, mission_id: Optional[str] = None):
        """Connect to mission updates channel."""
        await websocket.accept()
        key = mission_id or "all"
        if key not in self.mission_connections:
            self.mission_connections[key] = set()
        self.mission_connections[key].add(websocket)
        self.all_connections.add(websocket)

    async def connect_perimeter(self, websocket: WebSocket):
        """Connect to perimeter security channel."""
        await websocket.accept()
        self.perimeter_connections.add(websocket)
        self.all_connections.add(websocket)

    async def connect_swarm(self, websocket: WebSocket, swarm_id: Optional[str] = None):
        """Connect to swarm updates channel."""
        await websocket.accept()
        key = swarm_id or "all"
        if key not in self.swarm_connections:
            self.swarm_connections[key] = set()
        self.swarm_connections[key].add(websocket)
        self.all_connections.add(websocket)

    def disconnect(self, websocket: WebSocket):
        """Disconnect a WebSocket from all channels."""
        self.fleet_connections.discard(websocket)
        self.perimeter_connections.discard(websocket)
        self.all_connections.discard(websocket)

        for connections in self.telemetry_connections.values():
            connections.discard(websocket)

        for connections in self.mission_connections.values():
            connections.discard(websocket)

        for connections in self.swarm_connections.values():
            connections.discard(websocket)

    async def broadcast_fleet_update(self, data: Dict[str, Any]):
        """Broadcast fleet update to all fleet subscribers."""
        message = {
            "channel": "fleet",
            "event": "update",
            "data": data,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
        await self._broadcast_to_set(self.fleet_connections, message)

    async def broadcast_robot_status(self, robot_id: str, status: str, data: Dict[str, Any]):
        """Broadcast robot status change."""
        message = {
            "channel": "fleet",
            "event": "robot_status",
            "robot_id": robot_id,
            "status": status,
            "data": data,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
        await self._broadcast_to_set(self.fleet_connections, message)

    async def broadcast_telemetry(self, robot_id: str, telemetry: Dict[str, Any]):
        """Broadcast telemetry data."""
        message = {
            "channel": "telemetry",
            "event": "data",
            "robot_id": robot_id,
            "telemetry": telemetry,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

        if "all" in self.telemetry_connections:
            await self._broadcast_to_set(self.telemetry_connections["all"], message)

        if robot_id in self.telemetry_connections:
            await self._broadcast_to_set(self.telemetry_connections[robot_id], message)

    async def broadcast_health_alert(self, robot_id: str, health_data: Dict[str, Any]):
        """Broadcast health alert."""
        message = {
            "channel": "telemetry",
            "event": "health_alert",
            "robot_id": robot_id,
            "health": health_data,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

        if "all" in self.telemetry_connections:
            await self._broadcast_to_set(self.telemetry_connections["all"], message)

        if robot_id in self.telemetry_connections:
            await self._broadcast_to_set(self.telemetry_connections[robot_id], message)

    async def broadcast_mission_update(self, mission_id: str, event: str, data: Dict[str, Any]):
        """Broadcast mission update."""
        message = {
            "channel": "missions",
            "event": event,
            "mission_id": mission_id,
            "data": data,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

        if "all" in self.mission_connections:
            await self._broadcast_to_set(self.mission_connections["all"], message)

        if mission_id in self.mission_connections:
            await self._broadcast_to_set(self.mission_connections[mission_id], message)

    async def broadcast_waypoint_reached(self, mission_id: str, waypoint_id: str, position: Dict[str, float]):
        """Broadcast waypoint reached event."""
        message = {
            "channel": "missions",
            "event": "waypoint_reached",
            "mission_id": mission_id,
            "waypoint_id": waypoint_id,
            "position": position,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

        if "all" in self.mission_connections:
            await self._broadcast_to_set(self.mission_connections["all"], message)

        if mission_id in self.mission_connections:
            await self._broadcast_to_set(self.mission_connections[mission_id], message)

    async def broadcast_perimeter_breach(self, breach_data: Dict[str, Any]):
        """Broadcast perimeter breach alert."""
        message = {
            "channel": "perimeter",
            "event": "breach",
            "data": breach_data,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
        await self._broadcast_to_set(self.perimeter_connections, message)

    async def broadcast_thermal_anomaly(self, sensor_id: str, reading: Dict[str, Any]):
        """Broadcast thermal anomaly detection."""
        message = {
            "channel": "perimeter",
            "event": "thermal_anomaly",
            "sensor_id": sensor_id,
            "reading": reading,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
        await self._broadcast_to_set(self.perimeter_connections, message)

    async def broadcast_motion_detection(self, sensor_id: str, event_data: Dict[str, Any]):
        """Broadcast motion detection event."""
        message = {
            "channel": "perimeter",
            "event": "motion_detection",
            "sensor_id": sensor_id,
            "data": event_data,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
        await self._broadcast_to_set(self.perimeter_connections, message)

    async def broadcast_auto_response(self, response_data: Dict[str, Any]):
        """Broadcast auto-response dispatch."""
        message = {
            "channel": "perimeter",
            "event": "auto_response",
            "data": response_data,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
        await self._broadcast_to_set(self.perimeter_connections, message)

    async def broadcast_swarm_update(self, swarm_id: str, event: str, data: Dict[str, Any]):
        """Broadcast swarm update."""
        message = {
            "channel": "swarms",
            "event": event,
            "swarm_id": swarm_id,
            "data": data,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

        if "all" in self.swarm_connections:
            await self._broadcast_to_set(self.swarm_connections["all"], message)

        if swarm_id in self.swarm_connections:
            await self._broadcast_to_set(self.swarm_connections[swarm_id], message)

    async def broadcast_formation_change(self, swarm_id: str, formation_data: Dict[str, Any]):
        """Broadcast formation change."""
        message = {
            "channel": "swarms",
            "event": "formation_change",
            "swarm_id": swarm_id,
            "formation": formation_data,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

        if "all" in self.swarm_connections:
            await self._broadcast_to_set(self.swarm_connections["all"], message)

        if swarm_id in self.swarm_connections:
            await self._broadcast_to_set(self.swarm_connections[swarm_id], message)

    async def broadcast_swarm_telemetry(self, swarm_id: str, telemetry: Dict[str, Any]):
        """Broadcast synchronized swarm telemetry."""
        message = {
            "channel": "swarms",
            "event": "telemetry",
            "swarm_id": swarm_id,
            "telemetry": telemetry,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

        if "all" in self.swarm_connections:
            await self._broadcast_to_set(self.swarm_connections["all"], message)

        if swarm_id in self.swarm_connections:
            await self._broadcast_to_set(self.swarm_connections[swarm_id], message)

    async def broadcast_task_allocation(self, swarm_id: str, task_data: Dict[str, Any]):
        """Broadcast task allocation event."""
        message = {
            "channel": "swarms",
            "event": "task_allocation",
            "swarm_id": swarm_id,
            "task": task_data,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

        if "all" in self.swarm_connections:
            await self._broadcast_to_set(self.swarm_connections["all"], message)

        if swarm_id in self.swarm_connections:
            await self._broadcast_to_set(self.swarm_connections[swarm_id], message)

    async def broadcast_alert(self, alert_data: Dict[str, Any]):
        """Broadcast robotics alert to all channels."""
        message = {
            "channel": "alerts",
            "event": "alert",
            "data": alert_data,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
        await self._broadcast_to_set(self.all_connections, message)

    async def _broadcast_to_set(self, connections: Set[WebSocket], message: Dict[str, Any]):
        """Broadcast message to a set of connections."""
        if not connections:
            return

        disconnected = set()
        message_json = json.dumps(message)

        for connection in connections:
            try:
                await connection.send_text(message_json)
            except Exception:
                disconnected.add(connection)

        for connection in disconnected:
            self.disconnect(connection)

    def get_connection_stats(self) -> Dict[str, Any]:
        """Get connection statistics."""
        return {
            "fleet_connections": len(self.fleet_connections),
            "telemetry_connections": sum(len(c) for c in self.telemetry_connections.values()),
            "mission_connections": sum(len(c) for c in self.mission_connections.values()),
            "perimeter_connections": len(self.perimeter_connections),
            "swarm_connections": sum(len(c) for c in self.swarm_connections.values()),
            "total_connections": len(self.all_connections),
        }


robotics_manager = RoboticsConnectionManager()


async def handle_fleet_websocket(websocket: WebSocket):
    """Handle fleet WebSocket connection."""
    await robotics_manager.connect_fleet(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            if message.get("action") == "ping":
                await websocket.send_json({
                    "action": "pong",
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                })
            elif message.get("action") == "subscribe_robot":
                robot_id = message.get("robot_id")
                if robot_id:
                    await websocket.send_json({
                        "action": "subscribed",
                        "robot_id": robot_id,
                    })

    except WebSocketDisconnect:
        robotics_manager.disconnect(websocket)


async def handle_telemetry_websocket(websocket: WebSocket, robot_id: Optional[str] = None):
    """Handle telemetry WebSocket connection."""
    await robotics_manager.connect_telemetry(websocket, robot_id)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            if message.get("action") == "ping":
                await websocket.send_json({
                    "action": "pong",
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                })

    except WebSocketDisconnect:
        robotics_manager.disconnect(websocket)


async def handle_mission_websocket(websocket: WebSocket, mission_id: Optional[str] = None):
    """Handle mission WebSocket connection."""
    await robotics_manager.connect_mission(websocket, mission_id)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            if message.get("action") == "ping":
                await websocket.send_json({
                    "action": "pong",
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                })
            elif message.get("action") == "subscribe_mission":
                new_mission_id = message.get("mission_id")
                if new_mission_id:
                    if new_mission_id not in robotics_manager.mission_connections:
                        robotics_manager.mission_connections[new_mission_id] = set()
                    robotics_manager.mission_connections[new_mission_id].add(websocket)
                    await websocket.send_json({
                        "action": "subscribed",
                        "mission_id": new_mission_id,
                    })

    except WebSocketDisconnect:
        robotics_manager.disconnect(websocket)


async def handle_perimeter_websocket(websocket: WebSocket):
    """Handle perimeter security WebSocket connection."""
    await robotics_manager.connect_perimeter(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            if message.get("action") == "ping":
                await websocket.send_json({
                    "action": "pong",
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                })
            elif message.get("action") == "subscribe_zone":
                zone_id = message.get("zone_id")
                if zone_id:
                    await websocket.send_json({
                        "action": "subscribed",
                        "zone_id": zone_id,
                    })

    except WebSocketDisconnect:
        robotics_manager.disconnect(websocket)


async def handle_swarm_websocket(websocket: WebSocket, swarm_id: Optional[str] = None):
    """Handle swarm WebSocket connection."""
    await robotics_manager.connect_swarm(websocket, swarm_id)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            if message.get("action") == "ping":
                await websocket.send_json({
                    "action": "pong",
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                })
            elif message.get("action") == "subscribe_swarm":
                new_swarm_id = message.get("swarm_id")
                if new_swarm_id:
                    if new_swarm_id not in robotics_manager.swarm_connections:
                        robotics_manager.swarm_connections[new_swarm_id] = set()
                    robotics_manager.swarm_connections[new_swarm_id].add(websocket)
                    await websocket.send_json({
                        "action": "subscribed",
                        "swarm_id": new_swarm_id,
                    })

    except WebSocketDisconnect:
        robotics_manager.disconnect(websocket)


__all__ = [
    "robotics_manager",
    "RoboticsConnectionManager",
    "handle_fleet_websocket",
    "handle_telemetry_websocket",
    "handle_mission_websocket",
    "handle_perimeter_websocket",
    "handle_swarm_websocket",
]
