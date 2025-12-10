"""
WebSocket Router for Intel Orchestration Engine.

Provides real-time WebSocket channels for intelligence streaming:
- /ws/intel/fused - Fused intelligence feed
- /ws/intel/alerts - Alert notifications
- /ws/intel/priority - Priority queue updates
- /ws/intel/pipelines - Pipeline status updates
"""

import json
import logging
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

logger = logging.getLogger(__name__)

websocket_router = APIRouter(tags=["Intel WebSocket"])


class WebSocketMessage(BaseModel):
    """Standard WebSocket message format."""
    type: str
    channel: str
    data: dict[str, Any]
    timestamp: str
    message_id: str


class ConnectionManager:
    """Manages WebSocket connections for all channels."""

    def __init__(self):
        self._connections: dict[str, set[WebSocket]] = {
            "fused": set(),
            "alerts": set(),
            "priority": set(),
            "pipelines": set(),
        }
        self._connection_metadata: dict[WebSocket, dict[str, Any]] = {}

    async def connect(self, websocket: WebSocket, channel: str):
        """Accept and register a WebSocket connection."""
        await websocket.accept()

        if channel not in self._connections:
            self._connections[channel] = set()

        self._connections[channel].add(websocket)
        self._connection_metadata[websocket] = {
            "channel": channel,
            "connected_at": datetime.now(UTC).isoformat(),
            "messages_sent": 0,
        }

        logger.info("WebSocket connected to channel: %s", channel)

        # Send welcome message
        await self._send_message(websocket, {
            "type": "connected",
            "channel": channel,
            "message": f"Connected to {channel} channel",
            "timestamp": datetime.now(UTC).isoformat(),
        })

    def disconnect(self, websocket: WebSocket, channel: str):
        """Remove a WebSocket connection."""
        if channel in self._connections:
            self._connections[channel].discard(websocket)

        self._connection_metadata.pop(websocket, None)
        logger.info("WebSocket disconnected from channel: %s", channel)

    async def broadcast(self, channel: str, message: dict[str, Any]):
        """Broadcast message to all connections in a channel."""
        if channel not in self._connections:
            return

        connections = list(self._connections[channel])

        for websocket in connections:
            try:
                await self._send_message(websocket, message)

                # Update metadata
                if websocket in self._connection_metadata:
                    self._connection_metadata[websocket]["messages_sent"] += 1

            except Exception as e:
                logger.error("Error broadcasting to websocket: %s", e)
                self._connections[channel].discard(websocket)

    async def broadcast_all(self, message: dict[str, Any]):
        """Broadcast message to all channels."""
        for channel in self._connections:
            await self.broadcast(channel, message)

    async def _send_message(self, websocket: WebSocket, message: dict[str, Any]):
        """Send a message to a WebSocket."""
        if "message_id" not in message:
            message["message_id"] = str(uuid4())
        if "timestamp" not in message:
            message["timestamp"] = datetime.now(UTC).isoformat()

        await websocket.send_json(message)

    def get_connection_count(self, channel: str | None = None) -> int:
        """Get number of connections."""
        if channel:
            return len(self._connections.get(channel, set()))
        return sum(len(conns) for conns in self._connections.values())

    def get_stats(self) -> dict[str, Any]:
        """Get connection statistics."""
        return {
            "total_connections": self.get_connection_count(),
            "by_channel": {
                channel: len(conns)
                for channel, conns in self._connections.items()
            },
        }


# Global connection manager
manager = ConnectionManager()


@websocket_router.websocket("/ws/intel/fused")
async def websocket_fused(websocket: WebSocket):
    """
    WebSocket endpoint for fused intelligence feed.

    Broadcasts enriched, correlated intelligence data in real-time.
    """
    await manager.connect(websocket, "fused")

    try:
        while True:
            # Receive messages from client
            data = await websocket.receive_text()

            try:
                message = json.loads(data)
                await handle_client_message(websocket, "fused", message)
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON",
                })

    except WebSocketDisconnect:
        manager.disconnect(websocket, "fused")


@websocket_router.websocket("/ws/intel/alerts")
async def websocket_alerts(websocket: WebSocket):
    """
    WebSocket endpoint for alert notifications.

    Broadcasts high-priority alerts requiring immediate attention.
    """
    await manager.connect(websocket, "alerts")

    try:
        while True:
            data = await websocket.receive_text()

            try:
                message = json.loads(data)
                await handle_client_message(websocket, "alerts", message)
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON",
                })

    except WebSocketDisconnect:
        manager.disconnect(websocket, "alerts")


@websocket_router.websocket("/ws/intel/priority")
async def websocket_priority(websocket: WebSocket):
    """
    WebSocket endpoint for priority queue updates.

    Broadcasts priority-scored intelligence items.
    """
    await manager.connect(websocket, "priority")

    try:
        while True:
            data = await websocket.receive_text()

            try:
                message = json.loads(data)
                await handle_client_message(websocket, "priority", message)
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON",
                })

    except WebSocketDisconnect:
        manager.disconnect(websocket, "priority")


@websocket_router.websocket("/ws/intel/pipelines")
async def websocket_pipelines(websocket: WebSocket):
    """
    WebSocket endpoint for pipeline status updates.

    Broadcasts pipeline metrics and status changes.
    """
    await manager.connect(websocket, "pipelines")

    try:
        while True:
            data = await websocket.receive_text()

            try:
                message = json.loads(data)
                await handle_client_message(websocket, "pipelines", message)
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON",
                })

    except WebSocketDisconnect:
        manager.disconnect(websocket, "pipelines")


async def handle_client_message(
    websocket: WebSocket, channel: str, message: dict[str, Any]
):
    """Handle incoming client messages."""
    message_type = message.get("type", "")

    if message_type == "ping":
        await websocket.send_json({
            "type": "pong",
            "timestamp": datetime.now(UTC).isoformat(),
        })

    elif message_type == "subscribe":
        # Handle subscription to specific topics within channel
        topics = message.get("topics", [])
        await websocket.send_json({
            "type": "subscribed",
            "channel": channel,
            "topics": topics,
            "timestamp": datetime.now(UTC).isoformat(),
        })

    elif message_type == "unsubscribe":
        topics = message.get("topics", [])
        await websocket.send_json({
            "type": "unsubscribed",
            "channel": channel,
            "topics": topics,
            "timestamp": datetime.now(UTC).isoformat(),
        })

    elif message_type == "acknowledge":
        # Handle alert acknowledgment
        alert_id = message.get("alert_id")
        if alert_id:
            await websocket.send_json({
                "type": "acknowledged",
                "alert_id": alert_id,
                "timestamp": datetime.now(UTC).isoformat(),
            })

    elif message_type == "request_status":
        # Send current status
        await websocket.send_json({
            "type": "status",
            "channel": channel,
            "connections": manager.get_connection_count(channel),
            "timestamp": datetime.now(UTC).isoformat(),
        })

    else:
        await websocket.send_json({
            "type": "error",
            "message": f"Unknown message type: {message_type}",
        })


# Broadcast functions for use by other modules

async def broadcast_fused_intelligence(intelligence: dict[str, Any]):
    """Broadcast fused intelligence to connected clients."""
    await manager.broadcast("fused", {
        "type": "fused_intelligence",
        "data": intelligence,
        "timestamp": datetime.now(UTC).isoformat(),
    })


async def broadcast_alert(alert: dict[str, Any]):
    """Broadcast an alert to connected clients."""
    await manager.broadcast("alerts", {
        "type": "alert",
        "data": alert,
        "timestamp": datetime.now(UTC).isoformat(),
    })


async def broadcast_priority_update(item: dict[str, Any]):
    """Broadcast priority queue update to connected clients."""
    await manager.broadcast("priority", {
        "type": "priority_update",
        "data": item,
        "timestamp": datetime.now(UTC).isoformat(),
    })


async def broadcast_pipeline_status(pipeline_name: str, status: dict[str, Any]):
    """Broadcast pipeline status update to connected clients."""
    await manager.broadcast("pipelines", {
        "type": "pipeline_status",
        "pipeline": pipeline_name,
        "data": status,
        "timestamp": datetime.now(UTC).isoformat(),
    })


async def broadcast_officer_safety_alert(alert: dict[str, Any]):
    """Broadcast officer safety alert to all relevant channels."""
    message = {
        "type": "officer_safety_alert",
        "priority": "immediate",
        "data": alert,
        "timestamp": datetime.now(UTC).isoformat(),
        "requires_acknowledgment": True,
    }

    # Broadcast to alerts and priority channels
    await manager.broadcast("alerts", message)
    await manager.broadcast("priority", message)


async def broadcast_bolo(bolo: dict[str, Any]):
    """Broadcast BOLO to connected clients."""
    await manager.broadcast("alerts", {
        "type": "bolo",
        "data": bolo,
        "timestamp": datetime.now(UTC).isoformat(),
    })


async def broadcast_bulletin(bulletin: dict[str, Any]):
    """Broadcast intelligence bulletin to connected clients."""
    await manager.broadcast("fused", {
        "type": "bulletin",
        "data": bulletin,
        "timestamp": datetime.now(UTC).isoformat(),
    })


def get_connection_manager() -> ConnectionManager:
    """Get the global connection manager."""
    return manager


def get_websocket_stats() -> dict[str, Any]:
    """Get WebSocket connection statistics."""
    return manager.get_stats()
