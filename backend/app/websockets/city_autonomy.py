"""
Phase 24: City Autonomy WebSocket Channels

Real-time WebSocket channels for AI City Autonomy - Level-2 Autonomous City Operations.

Channels:
- /ws/autonomy/actions - Real-time action notifications
- /ws/autonomy/approvals - Approval workflow updates
- /ws/autonomy/stabilizer - Anomaly detection and stabilization progress
- /ws/autonomy/audit - Audit trail updates
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Set, Callable
from enum import Enum
import asyncio
import json
import uuid


class AutonomyChannelType(Enum):
    """Types of autonomy WebSocket channels."""
    ACTIONS = "actions"
    APPROVALS = "approvals"
    STABILIZER = "stabilizer"
    AUDIT = "audit"


class MessageType(Enum):
    """Types of WebSocket messages."""
    # Action messages
    ACTION_CREATED = "action_created"
    ACTION_UPDATED = "action_updated"
    ACTION_APPROVED = "action_approved"
    ACTION_DENIED = "action_denied"
    ACTION_EXECUTED = "action_executed"
    ACTION_COMPLETED = "action_completed"
    ACTION_FAILED = "action_failed"
    ACTION_ESCALATED = "action_escalated"
    
    # Approval messages
    APPROVAL_REQUESTED = "approval_requested"
    APPROVAL_REMINDER = "approval_reminder"
    APPROVAL_TIMEOUT_WARNING = "approval_timeout_warning"
    APPROVAL_EXPIRED = "approval_expired"
    
    # Stabilizer messages
    ANOMALY_DETECTED = "anomaly_detected"
    ANOMALY_RESOLVED = "anomaly_resolved"
    CASCADE_PREDICTION = "cascade_prediction"
    STABILIZATION_STARTED = "stabilization_started"
    STABILIZATION_PROGRESS = "stabilization_progress"
    STABILIZATION_COMPLETED = "stabilization_completed"
    CIRCUIT_BREAKER_TRIGGERED = "circuit_breaker_triggered"
    CIRCUIT_BREAKER_RESET = "circuit_breaker_reset"
    
    # Audit messages
    AUDIT_ENTRY_CREATED = "audit_entry_created"
    CHAIN_SEALED = "chain_sealed"
    COMPLIANCE_ALERT = "compliance_alert"
    INTEGRITY_WARNING = "integrity_warning"
    
    # System messages
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"
    HEARTBEAT = "heartbeat"
    MODE_CHANGED = "mode_changed"


@dataclass
class WebSocketClient:
    """Represents a connected WebSocket client."""
    client_id: str
    channel: AutonomyChannelType
    user_id: Optional[str] = None
    role: Optional[str] = None
    connected_at: datetime = field(default_factory=datetime.utcnow)
    last_activity: datetime = field(default_factory=datetime.utcnow)
    subscriptions: Set[str] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "client_id": self.client_id,
            "channel": self.channel.value,
            "user_id": self.user_id,
            "role": self.role,
            "connected_at": self.connected_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "subscriptions": list(self.subscriptions),
            "metadata": self.metadata,
        }


@dataclass
class WebSocketMessage:
    """WebSocket message structure."""
    message_id: str
    message_type: MessageType
    channel: AutonomyChannelType
    payload: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.utcnow)
    correlation_id: Optional[str] = None
    target_clients: Optional[List[str]] = None  # None means broadcast to all

    def to_dict(self) -> Dict[str, Any]:
        return {
            "message_id": self.message_id,
            "message_type": self.message_type.value,
            "channel": self.channel.value,
            "payload": self.payload,
            "timestamp": self.timestamp.isoformat(),
            "correlation_id": self.correlation_id,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict())


class AutonomyActionsChannel:
    """
    WebSocket channel for real-time action notifications.
    
    Broadcasts:
    - New action creation
    - Action status updates
    - Action execution results
    - Action completion/failure
    """

    def __init__(self):
        self._clients: Dict[str, WebSocketClient] = {}
        self._message_handlers: Dict[MessageType, List[Callable]] = {}
        self._message_queue: asyncio.Queue = asyncio.Queue()
        self._running = False

    async def connect(
        self,
        client_id: str,
        user_id: Optional[str] = None,
        role: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> WebSocketClient:
        """Connect a new client to the actions channel."""
        client = WebSocketClient(
            client_id=client_id,
            channel=AutonomyChannelType.ACTIONS,
            user_id=user_id,
            role=role,
            metadata=metadata or {},
        )
        self._clients[client_id] = client

        # Send connection confirmation
        await self.send_to_client(
            client_id,
            MessageType.CONNECTED,
            {"message": "Connected to actions channel", "client_id": client_id},
        )

        return client

    async def disconnect(self, client_id: str):
        """Disconnect a client from the channel."""
        if client_id in self._clients:
            del self._clients[client_id]

    async def send_to_client(
        self,
        client_id: str,
        message_type: MessageType,
        payload: Dict[str, Any],
        correlation_id: Optional[str] = None,
    ):
        """Send a message to a specific client."""
        message = WebSocketMessage(
            message_id=f"msg-{uuid.uuid4().hex[:8]}",
            message_type=message_type,
            channel=AutonomyChannelType.ACTIONS,
            payload=payload,
            correlation_id=correlation_id,
            target_clients=[client_id],
        )
        await self._message_queue.put(message)

    async def broadcast(
        self,
        message_type: MessageType,
        payload: Dict[str, Any],
        correlation_id: Optional[str] = None,
        exclude_clients: Optional[List[str]] = None,
    ):
        """Broadcast a message to all connected clients."""
        message = WebSocketMessage(
            message_id=f"msg-{uuid.uuid4().hex[:8]}",
            message_type=message_type,
            channel=AutonomyChannelType.ACTIONS,
            payload=payload,
            correlation_id=correlation_id,
        )
        await self._message_queue.put(message)

    async def notify_action_created(self, action_data: Dict[str, Any]):
        """Notify clients of a new action."""
        await self.broadcast(
            MessageType.ACTION_CREATED,
            {
                "action": action_data,
                "requires_approval": action_data.get("level") == 2,
            },
        )

    async def notify_action_approved(
        self,
        action_id: str,
        approved_by: str,
        action_data: Dict[str, Any],
    ):
        """Notify clients of an approved action."""
        await self.broadcast(
            MessageType.ACTION_APPROVED,
            {
                "action_id": action_id,
                "approved_by": approved_by,
                "action": action_data,
            },
        )

    async def notify_action_denied(
        self,
        action_id: str,
        denied_by: str,
        reason: str,
    ):
        """Notify clients of a denied action."""
        await self.broadcast(
            MessageType.ACTION_DENIED,
            {
                "action_id": action_id,
                "denied_by": denied_by,
                "reason": reason,
            },
        )

    async def notify_action_executed(
        self,
        action_id: str,
        execution_result: Dict[str, Any],
    ):
        """Notify clients of action execution."""
        await self.broadcast(
            MessageType.ACTION_EXECUTED,
            {
                "action_id": action_id,
                "result": execution_result,
            },
        )

    async def notify_action_completed(
        self,
        action_id: str,
        result: Dict[str, Any],
    ):
        """Notify clients of action completion."""
        await self.broadcast(
            MessageType.ACTION_COMPLETED,
            {
                "action_id": action_id,
                "result": result,
            },
        )

    async def notify_action_failed(
        self,
        action_id: str,
        error: str,
    ):
        """Notify clients of action failure."""
        await self.broadcast(
            MessageType.ACTION_FAILED,
            {
                "action_id": action_id,
                "error": error,
            },
        )

    def get_connected_clients(self) -> List[WebSocketClient]:
        """Get all connected clients."""
        return list(self._clients.values())

    def get_statistics(self) -> Dict[str, Any]:
        """Get channel statistics."""
        return {
            "channel": AutonomyChannelType.ACTIONS.value,
            "connected_clients": len(self._clients),
            "clients_by_role": self._count_by_role(),
            "queue_size": self._message_queue.qsize(),
        }

    def _count_by_role(self) -> Dict[str, int]:
        """Count clients by role."""
        counts: Dict[str, int] = {}
        for client in self._clients.values():
            role = client.role or "unknown"
            counts[role] = counts.get(role, 0) + 1
        return counts


class AutonomyApprovalsChannel:
    """
    WebSocket channel for approval workflow updates.
    
    Broadcasts:
    - Approval requests
    - Approval reminders
    - Timeout warnings
    - Approval expirations
    """

    def __init__(self):
        self._clients: Dict[str, WebSocketClient] = {}
        self._pending_approvals: Dict[str, Dict[str, Any]] = {}
        self._message_queue: asyncio.Queue = asyncio.Queue()

    async def connect(
        self,
        client_id: str,
        user_id: Optional[str] = None,
        role: Optional[str] = None,
        can_approve: bool = False,
    ) -> WebSocketClient:
        """Connect a new client to the approvals channel."""
        client = WebSocketClient(
            client_id=client_id,
            channel=AutonomyChannelType.APPROVALS,
            user_id=user_id,
            role=role,
            metadata={"can_approve": can_approve},
        )
        self._clients[client_id] = client

        # Send connection confirmation with pending approvals
        await self.send_to_client(
            client_id,
            MessageType.CONNECTED,
            {
                "message": "Connected to approvals channel",
                "pending_approvals": list(self._pending_approvals.values()),
            },
        )

        return client

    async def disconnect(self, client_id: str):
        """Disconnect a client from the channel."""
        if client_id in self._clients:
            del self._clients[client_id]

    async def send_to_client(
        self,
        client_id: str,
        message_type: MessageType,
        payload: Dict[str, Any],
    ):
        """Send a message to a specific client."""
        message = WebSocketMessage(
            message_id=f"msg-{uuid.uuid4().hex[:8]}",
            message_type=message_type,
            channel=AutonomyChannelType.APPROVALS,
            payload=payload,
            target_clients=[client_id],
        )
        await self._message_queue.put(message)

    async def broadcast_to_approvers(
        self,
        message_type: MessageType,
        payload: Dict[str, Any],
    ):
        """Broadcast to clients who can approve."""
        approvers = [
            c.client_id for c in self._clients.values()
            if c.metadata.get("can_approve", False)
        ]
        message = WebSocketMessage(
            message_id=f"msg-{uuid.uuid4().hex[:8]}",
            message_type=message_type,
            channel=AutonomyChannelType.APPROVALS,
            payload=payload,
            target_clients=approvers,
        )
        await self._message_queue.put(message)

    async def request_approval(
        self,
        action_id: str,
        action_data: Dict[str, Any],
        timeout_minutes: int = 30,
    ):
        """Request approval for an action."""
        approval_request = {
            "action_id": action_id,
            "action": action_data,
            "requested_at": datetime.utcnow().isoformat(),
            "timeout_minutes": timeout_minutes,
            "status": "pending",
        }
        self._pending_approvals[action_id] = approval_request

        await self.broadcast_to_approvers(
            MessageType.APPROVAL_REQUESTED,
            approval_request,
        )

    async def send_approval_reminder(self, action_id: str):
        """Send a reminder for pending approval."""
        if action_id in self._pending_approvals:
            await self.broadcast_to_approvers(
                MessageType.APPROVAL_REMINDER,
                {
                    "action_id": action_id,
                    "approval_request": self._pending_approvals[action_id],
                },
            )

    async def send_timeout_warning(
        self,
        action_id: str,
        minutes_remaining: int,
    ):
        """Send a timeout warning for pending approval."""
        if action_id in self._pending_approvals:
            await self.broadcast_to_approvers(
                MessageType.APPROVAL_TIMEOUT_WARNING,
                {
                    "action_id": action_id,
                    "minutes_remaining": minutes_remaining,
                },
            )

    async def notify_approval_expired(self, action_id: str):
        """Notify that an approval request has expired."""
        if action_id in self._pending_approvals:
            del self._pending_approvals[action_id]
            await self.broadcast_to_approvers(
                MessageType.APPROVAL_EXPIRED,
                {"action_id": action_id},
            )

    async def clear_pending_approval(self, action_id: str):
        """Clear a pending approval (after approval/denial)."""
        if action_id in self._pending_approvals:
            del self._pending_approvals[action_id]

    def get_pending_approvals(self) -> List[Dict[str, Any]]:
        """Get all pending approvals."""
        return list(self._pending_approvals.values())

    def get_statistics(self) -> Dict[str, Any]:
        """Get channel statistics."""
        return {
            "channel": AutonomyChannelType.APPROVALS.value,
            "connected_clients": len(self._clients),
            "approvers_online": len([
                c for c in self._clients.values()
                if c.metadata.get("can_approve", False)
            ]),
            "pending_approvals": len(self._pending_approvals),
        }


class AutonomyStabilizerChannel:
    """
    WebSocket channel for anomaly detection and stabilization progress.
    
    Broadcasts:
    - Anomaly detection alerts
    - Cascade failure predictions
    - Stabilization action progress
    - Circuit breaker status
    """

    def __init__(self):
        self._clients: Dict[str, WebSocketClient] = {}
        self._active_anomalies: Dict[str, Dict[str, Any]] = {}
        self._stabilization_progress: Dict[str, Dict[str, Any]] = {}
        self._message_queue: asyncio.Queue = asyncio.Queue()

    async def connect(
        self,
        client_id: str,
        user_id: Optional[str] = None,
        subscribed_domains: Optional[List[str]] = None,
    ) -> WebSocketClient:
        """Connect a new client to the stabilizer channel."""
        client = WebSocketClient(
            client_id=client_id,
            channel=AutonomyChannelType.STABILIZER,
            user_id=user_id,
            subscriptions=set(subscribed_domains or []),
        )
        self._clients[client_id] = client

        # Send connection confirmation with current state
        await self.send_to_client(
            client_id,
            MessageType.CONNECTED,
            {
                "message": "Connected to stabilizer channel",
                "active_anomalies": list(self._active_anomalies.values()),
                "stabilization_in_progress": list(self._stabilization_progress.values()),
            },
        )

        return client

    async def disconnect(self, client_id: str):
        """Disconnect a client from the channel."""
        if client_id in self._clients:
            del self._clients[client_id]

    async def send_to_client(
        self,
        client_id: str,
        message_type: MessageType,
        payload: Dict[str, Any],
    ):
        """Send a message to a specific client."""
        message = WebSocketMessage(
            message_id=f"msg-{uuid.uuid4().hex[:8]}",
            message_type=message_type,
            channel=AutonomyChannelType.STABILIZER,
            payload=payload,
            target_clients=[client_id],
        )
        await self._message_queue.put(message)

    async def broadcast(
        self,
        message_type: MessageType,
        payload: Dict[str, Any],
        domain: Optional[str] = None,
    ):
        """Broadcast to all clients or those subscribed to a domain."""
        target_clients = None
        if domain:
            target_clients = [
                c.client_id for c in self._clients.values()
                if not c.subscriptions or domain in c.subscriptions
            ]

        message = WebSocketMessage(
            message_id=f"msg-{uuid.uuid4().hex[:8]}",
            message_type=message_type,
            channel=AutonomyChannelType.STABILIZER,
            payload=payload,
            target_clients=target_clients,
        )
        await self._message_queue.put(message)

    async def notify_anomaly_detected(self, anomaly_data: Dict[str, Any]):
        """Notify clients of a detected anomaly."""
        anomaly_id = anomaly_data.get("anomaly_id")
        self._active_anomalies[anomaly_id] = anomaly_data

        await self.broadcast(
            MessageType.ANOMALY_DETECTED,
            {"anomaly": anomaly_data},
            domain=anomaly_data.get("domain"),
        )

    async def notify_anomaly_resolved(self, anomaly_id: str):
        """Notify clients that an anomaly has been resolved."""
        if anomaly_id in self._active_anomalies:
            anomaly = self._active_anomalies.pop(anomaly_id)
            await self.broadcast(
                MessageType.ANOMALY_RESOLVED,
                {"anomaly_id": anomaly_id, "anomaly": anomaly},
                domain=anomaly.get("domain"),
            )

    async def notify_cascade_prediction(self, prediction_data: Dict[str, Any]):
        """Notify clients of a cascade failure prediction."""
        await self.broadcast(
            MessageType.CASCADE_PREDICTION,
            {"prediction": prediction_data},
        )

    async def notify_stabilization_started(
        self,
        action_id: str,
        action_data: Dict[str, Any],
    ):
        """Notify clients that stabilization has started."""
        self._stabilization_progress[action_id] = {
            "action_id": action_id,
            "action": action_data,
            "status": "in_progress",
            "started_at": datetime.utcnow().isoformat(),
        }

        await self.broadcast(
            MessageType.STABILIZATION_STARTED,
            {"action_id": action_id, "action": action_data},
            domain=action_data.get("target_domain"),
        )

    async def notify_stabilization_progress(
        self,
        action_id: str,
        progress_percentage: int,
        status_message: str,
    ):
        """Notify clients of stabilization progress."""
        if action_id in self._stabilization_progress:
            self._stabilization_progress[action_id]["progress"] = progress_percentage
            self._stabilization_progress[action_id]["status_message"] = status_message

        await self.broadcast(
            MessageType.STABILIZATION_PROGRESS,
            {
                "action_id": action_id,
                "progress_percentage": progress_percentage,
                "status_message": status_message,
            },
        )

    async def notify_stabilization_completed(
        self,
        action_id: str,
        result: Dict[str, Any],
    ):
        """Notify clients that stabilization has completed."""
        if action_id in self._stabilization_progress:
            del self._stabilization_progress[action_id]

        await self.broadcast(
            MessageType.STABILIZATION_COMPLETED,
            {"action_id": action_id, "result": result},
        )

    async def notify_circuit_breaker_triggered(self, reason: str):
        """Notify clients that the circuit breaker has been triggered."""
        await self.broadcast(
            MessageType.CIRCUIT_BREAKER_TRIGGERED,
            {
                "reason": reason,
                "triggered_at": datetime.utcnow().isoformat(),
            },
        )

    async def notify_circuit_breaker_reset(self):
        """Notify clients that the circuit breaker has been reset."""
        await self.broadcast(
            MessageType.CIRCUIT_BREAKER_RESET,
            {"reset_at": datetime.utcnow().isoformat()},
        )

    def get_statistics(self) -> Dict[str, Any]:
        """Get channel statistics."""
        return {
            "channel": AutonomyChannelType.STABILIZER.value,
            "connected_clients": len(self._clients),
            "active_anomalies": len(self._active_anomalies),
            "stabilizations_in_progress": len(self._stabilization_progress),
        }


class AutonomyAuditChannel:
    """
    WebSocket channel for audit trail updates.
    
    Broadcasts:
    - New audit entries
    - Chain sealing events
    - Compliance alerts
    - Integrity warnings
    """

    def __init__(self):
        self._clients: Dict[str, WebSocketClient] = {}
        self._message_queue: asyncio.Queue = asyncio.Queue()
        self._recent_entries: List[Dict[str, Any]] = []
        self._max_recent_entries = 100

    async def connect(
        self,
        client_id: str,
        user_id: Optional[str] = None,
        role: Optional[str] = None,
        subscribed_event_types: Optional[List[str]] = None,
    ) -> WebSocketClient:
        """Connect a new client to the audit channel."""
        client = WebSocketClient(
            client_id=client_id,
            channel=AutonomyChannelType.AUDIT,
            user_id=user_id,
            role=role,
            subscriptions=set(subscribed_event_types or []),
        )
        self._clients[client_id] = client

        # Send connection confirmation with recent entries
        await self.send_to_client(
            client_id,
            MessageType.CONNECTED,
            {
                "message": "Connected to audit channel",
                "recent_entries_count": len(self._recent_entries),
            },
        )

        return client

    async def disconnect(self, client_id: str):
        """Disconnect a client from the channel."""
        if client_id in self._clients:
            del self._clients[client_id]

    async def send_to_client(
        self,
        client_id: str,
        message_type: MessageType,
        payload: Dict[str, Any],
    ):
        """Send a message to a specific client."""
        message = WebSocketMessage(
            message_id=f"msg-{uuid.uuid4().hex[:8]}",
            message_type=message_type,
            channel=AutonomyChannelType.AUDIT,
            payload=payload,
            target_clients=[client_id],
        )
        await self._message_queue.put(message)

    async def broadcast(
        self,
        message_type: MessageType,
        payload: Dict[str, Any],
        event_type: Optional[str] = None,
    ):
        """Broadcast to all clients or those subscribed to an event type."""
        target_clients = None
        if event_type:
            target_clients = [
                c.client_id for c in self._clients.values()
                if not c.subscriptions or event_type in c.subscriptions
            ]

        message = WebSocketMessage(
            message_id=f"msg-{uuid.uuid4().hex[:8]}",
            message_type=message_type,
            channel=AutonomyChannelType.AUDIT,
            payload=payload,
            target_clients=target_clients,
        )
        await self._message_queue.put(message)

    async def notify_audit_entry_created(self, entry_data: Dict[str, Any]):
        """Notify clients of a new audit entry."""
        # Store in recent entries
        self._recent_entries.append(entry_data)
        if len(self._recent_entries) > self._max_recent_entries:
            self._recent_entries = self._recent_entries[-self._max_recent_entries:]

        await self.broadcast(
            MessageType.AUDIT_ENTRY_CREATED,
            {"entry": entry_data},
            event_type=entry_data.get("event_type"),
        )

    async def notify_chain_sealed(
        self,
        resource_type: str,
        resource_id: str,
    ):
        """Notify clients that a chain of custody has been sealed."""
        await self.broadcast(
            MessageType.CHAIN_SEALED,
            {
                "resource_type": resource_type,
                "resource_id": resource_id,
                "sealed_at": datetime.utcnow().isoformat(),
            },
        )

    async def notify_compliance_alert(
        self,
        compliance_standard: str,
        alert_type: str,
        description: str,
        severity: str,
    ):
        """Notify clients of a compliance alert."""
        await self.broadcast(
            MessageType.COMPLIANCE_ALERT,
            {
                "compliance_standard": compliance_standard,
                "alert_type": alert_type,
                "description": description,
                "severity": severity,
                "timestamp": datetime.utcnow().isoformat(),
            },
        )

    async def notify_integrity_warning(
        self,
        warning_type: str,
        description: str,
        affected_entries: List[str],
    ):
        """Notify clients of an integrity warning."""
        await self.broadcast(
            MessageType.INTEGRITY_WARNING,
            {
                "warning_type": warning_type,
                "description": description,
                "affected_entries": affected_entries,
                "timestamp": datetime.utcnow().isoformat(),
            },
        )

    def get_recent_entries(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent audit entries."""
        return self._recent_entries[-limit:]

    def get_statistics(self) -> Dict[str, Any]:
        """Get channel statistics."""
        return {
            "channel": AutonomyChannelType.AUDIT.value,
            "connected_clients": len(self._clients),
            "recent_entries_cached": len(self._recent_entries),
        }


class CityAutonomyWebSocketManager:
    """
    Manager for all city autonomy WebSocket channels.
    
    Provides unified access to:
    - Actions channel
    - Approvals channel
    - Stabilizer channel
    - Audit channel
    """

    def __init__(self):
        self.actions_channel = AutonomyActionsChannel()
        self.approvals_channel = AutonomyApprovalsChannel()
        self.stabilizer_channel = AutonomyStabilizerChannel()
        self.audit_channel = AutonomyAuditChannel()
        self._heartbeat_interval = 30  # seconds

    async def connect_to_channel(
        self,
        channel_type: AutonomyChannelType,
        client_id: str,
        **kwargs,
    ) -> WebSocketClient:
        """Connect a client to a specific channel."""
        if channel_type == AutonomyChannelType.ACTIONS:
            return await self.actions_channel.connect(client_id, **kwargs)
        elif channel_type == AutonomyChannelType.APPROVALS:
            return await self.approvals_channel.connect(client_id, **kwargs)
        elif channel_type == AutonomyChannelType.STABILIZER:
            return await self.stabilizer_channel.connect(client_id, **kwargs)
        elif channel_type == AutonomyChannelType.AUDIT:
            return await self.audit_channel.connect(client_id, **kwargs)
        else:
            raise ValueError(f"Unknown channel type: {channel_type}")

    async def disconnect_from_channel(
        self,
        channel_type: AutonomyChannelType,
        client_id: str,
    ):
        """Disconnect a client from a specific channel."""
        if channel_type == AutonomyChannelType.ACTIONS:
            await self.actions_channel.disconnect(client_id)
        elif channel_type == AutonomyChannelType.APPROVALS:
            await self.approvals_channel.disconnect(client_id)
        elif channel_type == AutonomyChannelType.STABILIZER:
            await self.stabilizer_channel.disconnect(client_id)
        elif channel_type == AutonomyChannelType.AUDIT:
            await self.audit_channel.disconnect(client_id)

    async def broadcast_mode_change(self, mode: str):
        """Broadcast mode change to all channels."""
        payload = {
            "mode": mode,
            "changed_at": datetime.utcnow().isoformat(),
        }

        await self.actions_channel.broadcast(MessageType.MODE_CHANGED, payload)
        await self.approvals_channel.broadcast_to_approvers(MessageType.MODE_CHANGED, payload)
        await self.stabilizer_channel.broadcast(MessageType.MODE_CHANGED, payload)
        await self.audit_channel.broadcast(MessageType.MODE_CHANGED, payload)

    def get_all_statistics(self) -> Dict[str, Any]:
        """Get statistics from all channels."""
        return {
            "actions": self.actions_channel.get_statistics(),
            "approvals": self.approvals_channel.get_statistics(),
            "stabilizer": self.stabilizer_channel.get_statistics(),
            "audit": self.audit_channel.get_statistics(),
            "total_clients": (
                len(self.actions_channel._clients) +
                len(self.approvals_channel._clients) +
                len(self.stabilizer_channel._clients) +
                len(self.audit_channel._clients)
            ),
        }


# Singleton instance
_ws_manager: Optional[CityAutonomyWebSocketManager] = None


def get_autonomy_ws_manager() -> CityAutonomyWebSocketManager:
    """Get the singleton WebSocket manager instance."""
    global _ws_manager
    if _ws_manager is None:
        _ws_manager = CityAutonomyWebSocketManager()
    return _ws_manager
