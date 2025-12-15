"""
Phase 38: Orchestration WebSocket Channels
Real-time WebSocket channels for orchestration events, workflow status, and alerts.

Channels:
- /ws/orchestration/events - Real-time event stream
- /ws/orchestration/workflow-status - Workflow execution status updates
- /ws/orchestration/alerts - Critical orchestration alerts
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Any, Dict, List, Set
from datetime import datetime
import asyncio
import json
import uuid

router = APIRouter()


class OrchestrationConnectionManager:
    """Manages WebSocket connections for orchestration channels."""

    def __init__(self):
        self.events_connections: Set[WebSocket] = set()
        self.workflow_status_connections: Set[WebSocket] = set()
        self.alerts_connections: Set[WebSocket] = set()
        self._broadcast_queue: asyncio.Queue = asyncio.Queue()
        self._running = False

    async def connect_events(self, websocket: WebSocket):
        """Connect to events channel."""
        await websocket.accept()
        self.events_connections.add(websocket)
        await self._send_connection_ack(websocket, "events")

    async def connect_workflow_status(self, websocket: WebSocket):
        """Connect to workflow status channel."""
        await websocket.accept()
        self.workflow_status_connections.add(websocket)
        await self._send_connection_ack(websocket, "workflow-status")

    async def connect_alerts(self, websocket: WebSocket):
        """Connect to alerts channel."""
        await websocket.accept()
        self.alerts_connections.add(websocket)
        await self._send_connection_ack(websocket, "alerts")

    def disconnect_events(self, websocket: WebSocket):
        """Disconnect from events channel."""
        self.events_connections.discard(websocket)

    def disconnect_workflow_status(self, websocket: WebSocket):
        """Disconnect from workflow status channel."""
        self.workflow_status_connections.discard(websocket)

    def disconnect_alerts(self, websocket: WebSocket):
        """Disconnect from alerts channel."""
        self.alerts_connections.discard(websocket)

    async def _send_connection_ack(self, websocket: WebSocket, channel: str):
        """Send connection acknowledgment."""
        await websocket.send_json({
            "type": "connection_ack",
            "channel": channel,
            "message": f"Connected to orchestration {channel} channel",
            "timestamp": datetime.utcnow().isoformat(),
        })

    async def broadcast_event(self, event: Dict[str, Any]):
        """Broadcast event to all events channel subscribers."""
        message = {
            "type": "orchestration_event",
            "event_id": event.get("event_id", f"evt-{uuid.uuid4().hex[:8]}"),
            "data": event,
            "timestamp": datetime.utcnow().isoformat(),
        }
        await self._broadcast_to_connections(self.events_connections, message)

    async def broadcast_workflow_status(self, status: Dict[str, Any]):
        """Broadcast workflow status update."""
        message = {
            "type": "workflow_status_update",
            "workflow_id": status.get("workflow_id"),
            "status": status.get("status"),
            "data": status,
            "timestamp": datetime.utcnow().isoformat(),
        }
        await self._broadcast_to_connections(self.workflow_status_connections, message)

    async def broadcast_alert(self, alert: Dict[str, Any]):
        """Broadcast critical alert."""
        message = {
            "type": "orchestration_alert",
            "alert_id": alert.get("alert_id", f"alert-{uuid.uuid4().hex[:8]}"),
            "severity": alert.get("severity", "info"),
            "data": alert,
            "timestamp": datetime.utcnow().isoformat(),
        }
        await self._broadcast_to_connections(self.alerts_connections, message)

    async def broadcast_workflow_started(
        self,
        workflow_id: str,
        workflow_name: str,
        triggered_by: str,
        inputs: Dict[str, Any],
    ):
        """Broadcast workflow started event."""
        await self.broadcast_workflow_status({
            "workflow_id": workflow_id,
            "workflow_name": workflow_name,
            "status": "started",
            "triggered_by": triggered_by,
            "inputs": inputs,
            "started_at": datetime.utcnow().isoformat(),
        })

    async def broadcast_workflow_step_completed(
        self,
        workflow_id: str,
        step_id: str,
        step_name: str,
        result: Dict[str, Any],
    ):
        """Broadcast workflow step completion."""
        await self.broadcast_workflow_status({
            "workflow_id": workflow_id,
            "status": "step_completed",
            "step_id": step_id,
            "step_name": step_name,
            "result": result,
            "completed_at": datetime.utcnow().isoformat(),
        })

    async def broadcast_workflow_completed(
        self,
        workflow_id: str,
        workflow_name: str,
        success: bool,
        results: Dict[str, Any],
    ):
        """Broadcast workflow completion."""
        await self.broadcast_workflow_status({
            "workflow_id": workflow_id,
            "workflow_name": workflow_name,
            "status": "completed" if success else "failed",
            "success": success,
            "results": results,
            "completed_at": datetime.utcnow().isoformat(),
        })

    async def broadcast_workflow_error(
        self,
        workflow_id: str,
        error: str,
        step_id: str = None,
    ):
        """Broadcast workflow error."""
        await self.broadcast_workflow_status({
            "workflow_id": workflow_id,
            "status": "error",
            "error": error,
            "step_id": step_id,
            "error_at": datetime.utcnow().isoformat(),
        })
        await self.broadcast_alert({
            "alert_type": "workflow_error",
            "severity": "high",
            "workflow_id": workflow_id,
            "error": error,
            "step_id": step_id,
        })

    async def broadcast_trigger_detected(
        self,
        trigger_id: str,
        trigger_type: str,
        event_type: str,
        workflow_name: str,
    ):
        """Broadcast trigger detection."""
        await self.broadcast_event({
            "event_type": "trigger_detected",
            "trigger_id": trigger_id,
            "trigger_type": trigger_type,
            "source_event_type": event_type,
            "workflow_name": workflow_name,
        })

    async def broadcast_fused_event(self, fused_event: Dict[str, Any]):
        """Broadcast fused event from event bus."""
        await self.broadcast_event({
            "event_type": "fused_event",
            "fused_event_id": fused_event.get("fused_event_id"),
            "source_count": fused_event.get("source_count"),
            "fusion_strategy": fused_event.get("fusion_strategy"),
            "category": fused_event.get("category"),
            "priority": fused_event.get("priority"),
            "title": fused_event.get("title"),
            "summary": fused_event.get("summary"),
        })

    async def broadcast_resource_allocated(
        self,
        allocation_id: str,
        resource_id: str,
        resource_type: str,
        workflow_id: str,
    ):
        """Broadcast resource allocation."""
        await self.broadcast_event({
            "event_type": "resource_allocated",
            "allocation_id": allocation_id,
            "resource_id": resource_id,
            "resource_type": resource_type,
            "workflow_id": workflow_id,
        })

    async def broadcast_resource_released(
        self,
        resource_id: str,
        resource_type: str,
    ):
        """Broadcast resource release."""
        await self.broadcast_event({
            "event_type": "resource_released",
            "resource_id": resource_id,
            "resource_type": resource_type,
        })

    async def broadcast_policy_violation(
        self,
        workflow_id: str,
        policy_type: str,
        violation: str,
        severity: str,
    ):
        """Broadcast policy violation alert."""
        await self.broadcast_alert({
            "alert_type": "policy_violation",
            "severity": severity,
            "workflow_id": workflow_id,
            "policy_type": policy_type,
            "violation": violation,
        })

    async def broadcast_guardrail_triggered(
        self,
        workflow_id: str,
        guardrail: str,
        action_blocked: str,
        reason: str,
    ):
        """Broadcast guardrail trigger alert."""
        await self.broadcast_alert({
            "alert_type": "guardrail_triggered",
            "severity": "warning",
            "workflow_id": workflow_id,
            "guardrail": guardrail,
            "action_blocked": action_blocked,
            "reason": reason,
        })

    async def broadcast_system_status(self, status: Dict[str, Any]):
        """Broadcast system status update."""
        await self.broadcast_event({
            "event_type": "system_status",
            "kernel_status": status.get("kernel_status"),
            "active_workflows": status.get("active_workflows"),
            "queued_actions": status.get("queued_actions"),
            "resource_utilization": status.get("resource_utilization"),
        })

    async def _broadcast_to_connections(
        self, connections: Set[WebSocket], message: Dict[str, Any]
    ):
        """Broadcast message to a set of connections."""
        disconnected = set()
        for connection in connections:
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.add(connection)
        for conn in disconnected:
            connections.discard(conn)

    def get_connection_stats(self) -> Dict[str, int]:
        """Get connection statistics."""
        return {
            "events_connections": len(self.events_connections),
            "workflow_status_connections": len(self.workflow_status_connections),
            "alerts_connections": len(self.alerts_connections),
            "total_connections": (
                len(self.events_connections)
                + len(self.workflow_status_connections)
                + len(self.alerts_connections)
            ),
        }


manager = OrchestrationConnectionManager()


@router.websocket("/ws/orchestration/events")
async def orchestration_events_websocket(websocket: WebSocket):
    """
    WebSocket endpoint for real-time orchestration events.
    
    Events include:
    - Trigger detections
    - Fused events
    - Resource allocations/releases
    - System status updates
    """
    await manager.connect_events(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                if message.get("type") == "ping":
                    await websocket.send_json({
                        "type": "pong",
                        "timestamp": datetime.utcnow().isoformat(),
                    })
                elif message.get("type") == "subscribe":
                    await websocket.send_json({
                        "type": "subscription_ack",
                        "filters": message.get("filters", {}),
                        "timestamp": datetime.utcnow().isoformat(),
                    })
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON",
                    "timestamp": datetime.utcnow().isoformat(),
                })
    except WebSocketDisconnect:
        manager.disconnect_events(websocket)


@router.websocket("/ws/orchestration/workflow-status")
async def orchestration_workflow_status_websocket(websocket: WebSocket):
    """
    WebSocket endpoint for workflow execution status updates.
    
    Updates include:
    - Workflow started
    - Step completed
    - Workflow completed/failed
    - Workflow errors
    """
    await manager.connect_workflow_status(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                if message.get("type") == "ping":
                    await websocket.send_json({
                        "type": "pong",
                        "timestamp": datetime.utcnow().isoformat(),
                    })
                elif message.get("type") == "get_active":
                    await websocket.send_json({
                        "type": "active_workflows",
                        "workflows": [],
                        "timestamp": datetime.utcnow().isoformat(),
                    })
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON",
                    "timestamp": datetime.utcnow().isoformat(),
                })
    except WebSocketDisconnect:
        manager.disconnect_workflow_status(websocket)


@router.websocket("/ws/orchestration/alerts")
async def orchestration_alerts_websocket(websocket: WebSocket):
    """
    WebSocket endpoint for critical orchestration alerts.
    
    Alerts include:
    - Policy violations
    - Guardrail triggers
    - Workflow errors
    - System warnings
    """
    await manager.connect_alerts(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                if message.get("type") == "ping":
                    await websocket.send_json({
                        "type": "pong",
                        "timestamp": datetime.utcnow().isoformat(),
                    })
                elif message.get("type") == "acknowledge":
                    alert_id = message.get("alert_id")
                    await websocket.send_json({
                        "type": "alert_acknowledged",
                        "alert_id": alert_id,
                        "timestamp": datetime.utcnow().isoformat(),
                    })
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON",
                    "timestamp": datetime.utcnow().isoformat(),
                })
    except WebSocketDisconnect:
        manager.disconnect_alerts(websocket)


def get_orchestration_ws_manager() -> OrchestrationConnectionManager:
    """Get the orchestration WebSocket manager instance."""
    return manager
