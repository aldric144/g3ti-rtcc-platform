"""
WebSocket Router for Operations Continuity.

Provides real-time streaming of health updates, failover events,
and diagnostic events.
"""

import asyncio
from datetime import datetime, timezone
from typing import Any, Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field


websocket_router = APIRouter(tags=["Operations WebSocket"])


class WebSocketMessage(BaseModel):
    """WebSocket message model."""
    type: str
    channel: str
    data: dict[str, Any]
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class OpsConnectionManager:
    """Manages WebSocket connections for operations channels."""

    def __init__(self):
        self.active_connections: dict[str, list[WebSocket]] = {}
        self.channels = ["health", "failover", "diagnostics"]

        for channel in self.channels:
            self.active_connections[channel] = []

    async def connect(self, websocket: WebSocket, channel: str) -> None:
        """Accept and register a WebSocket connection."""
        await websocket.accept()
        if channel not in self.active_connections:
            self.active_connections[channel] = []
        self.active_connections[channel].append(websocket)

    def disconnect(self, websocket: WebSocket, channel: str) -> None:
        """Remove a WebSocket connection."""
        if channel in self.active_connections:
            if websocket in self.active_connections[channel]:
                self.active_connections[channel].remove(websocket)

    async def send_personal_message(self, message: dict[str, Any], websocket: WebSocket) -> None:
        """Send a message to a specific WebSocket."""
        try:
            await websocket.send_json(message)
        except Exception:
            pass

    async def broadcast(self, message: dict[str, Any], channel: str) -> None:
        """Broadcast a message to all connections in a channel."""
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

    async def broadcast_all(self, message: dict[str, Any]) -> None:
        """Broadcast a message to all channels."""
        for channel in self.channels:
            await self.broadcast(message, channel)

    def get_connection_count(self) -> int:
        """Get total connection count across all channels."""
        return sum(len(conns) for conns in self.active_connections.values())

    def get_channel_count(self, channel: str) -> int:
        """Get connection count for a specific channel."""
        return len(self.active_connections.get(channel, []))


manager = OpsConnectionManager()


async def handle_client_message(websocket: WebSocket, channel: str, data: dict[str, Any]) -> None:
    """Handle incoming client messages."""
    msg_type = data.get("type", "")

    if msg_type == "ping":
        await manager.send_personal_message({
            "type": "pong",
            "channel": channel,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }, websocket)

    elif msg_type == "subscribe":
        channels = data.get("channels", [])
        await manager.send_personal_message({
            "type": "subscribed",
            "channel": channel,
            "data": {"channels": channels},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }, websocket)

    elif msg_type == "request_status":
        await manager.send_personal_message({
            "type": "status",
            "channel": channel,
            "data": {
                "connections": manager.get_connection_count(),
                "channel_connections": manager.get_channel_count(channel),
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }, websocket)


@websocket_router.websocket("/ws/ops/health")
async def websocket_health(websocket: WebSocket):
    """
    WebSocket endpoint for health updates.

    Broadcasts service health status changes in real-time.
    """
    await manager.connect(websocket, "health")
    try:
        await manager.send_personal_message({
            "type": "connected",
            "channel": "health",
            "data": {"message": "Connected to health channel"},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }, websocket)

        while True:
            data = await websocket.receive_json()
            await handle_client_message(websocket, "health", data)

    except WebSocketDisconnect:
        manager.disconnect(websocket, "health")
    except Exception:
        manager.disconnect(websocket, "health")


@websocket_router.websocket("/ws/ops/failover")
async def websocket_failover(websocket: WebSocket):
    """
    WebSocket endpoint for failover events.

    Broadcasts failover activations, recoveries, and state changes.
    """
    await manager.connect(websocket, "failover")
    try:
        await manager.send_personal_message({
            "type": "connected",
            "channel": "failover",
            "data": {"message": "Connected to failover channel"},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }, websocket)

        while True:
            data = await websocket.receive_json()
            await handle_client_message(websocket, "failover", data)

    except WebSocketDisconnect:
        manager.disconnect(websocket, "failover")
    except Exception:
        manager.disconnect(websocket, "failover")


@websocket_router.websocket("/ws/ops/diagnostics")
async def websocket_diagnostics(websocket: WebSocket):
    """
    WebSocket endpoint for diagnostic events.

    Broadcasts diagnostic events, slow queries, and predictive alerts.
    """
    await manager.connect(websocket, "diagnostics")
    try:
        await manager.send_personal_message({
            "type": "connected",
            "channel": "diagnostics",
            "data": {"message": "Connected to diagnostics channel"},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }, websocket)

        while True:
            data = await websocket.receive_json()
            await handle_client_message(websocket, "diagnostics", data)

    except WebSocketDisconnect:
        manager.disconnect(websocket, "diagnostics")
    except Exception:
        manager.disconnect(websocket, "diagnostics")


async def broadcast_health_update(health_data: dict[str, Any]) -> None:
    """Broadcast a health update to all health channel subscribers."""
    message = {
        "type": "health_update",
        "channel": "health",
        "data": health_data,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    await manager.broadcast(message, "health")


async def broadcast_service_status_change(
    service_id: str,
    service_name: str,
    old_status: str,
    new_status: str,
    latency_ms: float,
) -> None:
    """Broadcast a service status change."""
    message = {
        "type": "service_status_change",
        "channel": "health",
        "data": {
            "service_id": service_id,
            "service_name": service_name,
            "old_status": old_status,
            "new_status": new_status,
            "latency_ms": latency_ms,
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    await manager.broadcast(message, "health")


async def broadcast_service_degraded(
    service_id: str,
    service_name: str,
    reason: str,
) -> None:
    """Broadcast a service degradation event."""
    message = {
        "type": "service_degraded",
        "channel": "health",
        "data": {
            "service_id": service_id,
            "service_name": service_name,
            "reason": reason,
            "severity": "warning",
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    await manager.broadcast(message, "health")


async def broadcast_service_failure(
    service_id: str,
    service_name: str,
    error_message: str,
) -> None:
    """Broadcast a service failure event."""
    message = {
        "type": "service_failure",
        "channel": "health",
        "data": {
            "service_id": service_id,
            "service_name": service_name,
            "error_message": error_message,
            "severity": "critical",
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    await manager.broadcast(message, "health")
    await manager.broadcast(message, "failover")


async def broadcast_failover_event(failover_data: dict[str, Any]) -> None:
    """Broadcast a failover event to all failover channel subscribers."""
    message = {
        "type": "failover_event",
        "channel": "failover",
        "data": failover_data,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    await manager.broadcast(message, "failover")


async def broadcast_failover_activated(
    service_type: str,
    from_target: str,
    to_target: str,
    reason: str,
) -> None:
    """Broadcast a failover activation."""
    message = {
        "type": "failover_activated",
        "channel": "failover",
        "data": {
            "service_type": service_type,
            "from_target": from_target,
            "to_target": to_target,
            "reason": reason,
            "severity": "warning",
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    await manager.broadcast(message, "failover")


async def broadcast_recovery_completed(
    service_type: str,
    recovery_time_seconds: float,
) -> None:
    """Broadcast a recovery completion."""
    message = {
        "type": "recovery_completed",
        "channel": "failover",
        "data": {
            "service_type": service_type,
            "recovery_time_seconds": recovery_time_seconds,
            "severity": "info",
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    await manager.broadcast(message, "failover")


async def broadcast_emergency_state(
    active_failovers: int,
    affected_services: list[str],
) -> None:
    """Broadcast an emergency state."""
    message = {
        "type": "emergency_state",
        "channel": "failover",
        "data": {
            "active_failovers": active_failovers,
            "affected_services": affected_services,
            "severity": "critical",
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    await manager.broadcast(message, "failover")
    await manager.broadcast(message, "health")


async def broadcast_diagnostic_event(diagnostic_data: dict[str, Any]) -> None:
    """Broadcast a diagnostic event to all diagnostics channel subscribers."""
    message = {
        "type": "diagnostic_event",
        "channel": "diagnostics",
        "data": diagnostic_data,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    await manager.broadcast(message, "diagnostics")


async def broadcast_slow_query(
    database: str,
    query_type: str,
    duration_ms: float,
    query_preview: str,
) -> None:
    """Broadcast a slow query event."""
    message = {
        "type": "slow_query",
        "channel": "diagnostics",
        "data": {
            "database": database,
            "query_type": query_type,
            "duration_ms": duration_ms,
            "query_preview": query_preview,
            "severity": "warning",
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    await manager.broadcast(message, "diagnostics")


async def broadcast_predictive_alert(
    category: str,
    prediction_type: str,
    confidence: float,
    indicators: list[str],
    recommended_actions: list[str],
) -> None:
    """Broadcast a predictive alert."""
    message = {
        "type": "predictive_alert",
        "channel": "diagnostics",
        "data": {
            "category": category,
            "prediction_type": prediction_type,
            "confidence": confidence,
            "indicators": indicators,
            "recommended_actions": recommended_actions,
            "severity": "warning",
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    await manager.broadcast(message, "diagnostics")


async def broadcast_vendor_unavailable(
    vendor: str,
    error_message: str,
) -> None:
    """Broadcast a vendor unavailability event."""
    message = {
        "type": "vendor_unavailable",
        "channel": "diagnostics",
        "data": {
            "vendor": vendor,
            "error_message": error_message,
            "severity": "error",
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    await manager.broadcast(message, "diagnostics")
    await manager.broadcast(message, "health")


async def broadcast_federal_interruption(
    endpoint: str,
    error_message: str,
    duration_minutes: float,
) -> None:
    """Broadcast a federal feed interruption."""
    message = {
        "type": "federal_interruption",
        "channel": "diagnostics",
        "data": {
            "endpoint": endpoint,
            "error_message": error_message,
            "duration_minutes": duration_minutes,
            "severity": "critical" if duration_minutes > 5 else "warning",
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    await manager.broadcast(message, "diagnostics")
    await manager.broadcast(message, "failover")


async def broadcast_etl_stall(
    pipeline: str,
    stall_duration_minutes: float,
    last_processed: str,
) -> None:
    """Broadcast an ETL pipeline stall."""
    message = {
        "type": "etl_stall",
        "channel": "diagnostics",
        "data": {
            "pipeline": pipeline,
            "stall_duration_minutes": stall_duration_minutes,
            "last_processed": last_processed,
            "severity": "error",
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    await manager.broadcast(message, "diagnostics")


async def broadcast_queue_threshold_exceeded(
    queue_name: str,
    current_depth: int,
    threshold: int,
) -> None:
    """Broadcast a queue threshold exceeded event."""
    message = {
        "type": "queue_threshold_exceeded",
        "channel": "diagnostics",
        "data": {
            "queue_name": queue_name,
            "current_depth": current_depth,
            "threshold": threshold,
            "severity": "warning",
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    await manager.broadcast(message, "diagnostics")
