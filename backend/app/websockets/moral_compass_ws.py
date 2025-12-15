"""
Moral Compass WebSocket Channels

Phase 35: AI Moral Compass & Societal Ethics Reasoning Engine
Real-time WebSocket channels for moral alerts, violations, reasoning, and fairness.
"""

import asyncio
import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set


class MoralWSChannel(Enum):
    """WebSocket channel types for moral compass."""
    ALERTS = "alerts"
    VIOLATIONS = "violations"
    REASONING = "reasoning"
    FAIRNESS = "fairness"


class MoralAlertType(Enum):
    """Types of moral alerts."""
    ETHICAL_VIOLATION = "ethical_violation"
    BIAS_DETECTED = "bias_detected"
    HIGH_RISK_ACTION = "high_risk_action"
    COMMUNITY_HARM_RISK = "community_harm_risk"
    FAIRNESS_CONCERN = "fairness_concern"
    GUARDRAIL_TRIGGERED = "guardrail_triggered"
    VETO_ISSUED = "veto_issued"
    APPROVAL_REQUIRED = "approval_required"


class MoralAlertSeverity(Enum):
    """Severity levels for moral alerts."""
    INFO = "info"
    WARNING = "warning"
    SERIOUS = "serious"
    CRITICAL = "critical"
    BLOCKING = "blocking"


@dataclass
class MoralWSConnection:
    """WebSocket connection for moral compass."""
    connection_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    channel: MoralWSChannel = MoralWSChannel.ALERTS
    user_id: str = ""
    connected_at: datetime = field(default_factory=datetime.utcnow)
    last_activity: datetime = field(default_factory=datetime.utcnow)
    subscriptions: Set[str] = field(default_factory=set)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "connection_id": self.connection_id,
            "channel": self.channel.value,
            "user_id": self.user_id,
            "connected_at": self.connected_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "subscriptions": list(self.subscriptions),
        }


@dataclass
class MoralWSMessage:
    """WebSocket message for moral compass."""
    message_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    channel: MoralWSChannel = MoralWSChannel.ALERTS
    message_type: str = ""
    payload: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "message_id": self.message_id,
            "channel": self.channel.value,
            "message_type": self.message_type,
            "payload": self.payload,
            "timestamp": self.timestamp.isoformat(),
        }
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict())


@dataclass
class MoralAlert:
    """A moral alert for broadcasting."""
    alert_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    alert_type: MoralAlertType = MoralAlertType.ETHICAL_VIOLATION
    severity: MoralAlertSeverity = MoralAlertSeverity.WARNING
    title: str = ""
    description: str = ""
    action_type: str = ""
    requester_id: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    requires_action: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    acknowledged: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "alert_id": self.alert_id,
            "alert_type": self.alert_type.value,
            "severity": self.severity.value,
            "title": self.title,
            "description": self.description,
            "action_type": self.action_type,
            "requester_id": self.requester_id,
            "details": self.details,
            "recommendations": self.recommendations,
            "requires_action": self.requires_action,
            "created_at": self.created_at.isoformat(),
            "acknowledged": self.acknowledged,
        }


class MoralCompassWSManager:
    """
    WebSocket Manager for Moral Compass.
    
    Manages real-time connections for moral alerts, violations,
    reasoning updates, and fairness notifications.
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self.connections: Dict[str, MoralWSConnection] = {}
        self.channel_connections: Dict[MoralWSChannel, Set[str]] = {
            channel: set() for channel in MoralWSChannel
        }
        self.alerts: Dict[str, MoralAlert] = {}
        self.message_handlers: Dict[str, Callable] = {}
        self.statistics = {
            "total_connections": 0,
            "total_messages_sent": 0,
            "total_alerts_broadcast": 0,
            "active_connections": 0,
        }
    
    async def connect(
        self,
        channel: MoralWSChannel,
        user_id: str,
        websocket: Any,
    ) -> MoralWSConnection:
        """
        Connect a client to a moral compass channel.
        
        Args:
            channel: Channel to connect to
            user_id: User ID
            websocket: WebSocket connection object
        
        Returns:
            MoralWSConnection object
        """
        connection = MoralWSConnection(
            channel=channel,
            user_id=user_id,
        )
        
        self.connections[connection.connection_id] = connection
        self.channel_connections[channel].add(connection.connection_id)
        
        self.statistics["total_connections"] += 1
        self.statistics["active_connections"] = len(self.connections)
        
        welcome_message = MoralWSMessage(
            channel=channel,
            message_type="connection_established",
            payload={
                "connection_id": connection.connection_id,
                "channel": channel.value,
                "message": f"Connected to moral compass {channel.value} channel",
            },
        )
        
        return connection
    
    async def disconnect(self, connection_id: str) -> bool:
        """
        Disconnect a client.
        
        Args:
            connection_id: Connection ID to disconnect
        
        Returns:
            True if disconnected successfully
        """
        connection = self.connections.get(connection_id)
        if not connection:
            return False
        
        self.channel_connections[connection.channel].discard(connection_id)
        del self.connections[connection_id]
        
        self.statistics["active_connections"] = len(self.connections)
        
        return True
    
    async def broadcast_alert(self, alert: MoralAlert) -> int:
        """
        Broadcast a moral alert to all connected clients.
        
        Args:
            alert: Alert to broadcast
        
        Returns:
            Number of clients notified
        """
        self.alerts[alert.alert_id] = alert
        
        message = MoralWSMessage(
            channel=MoralWSChannel.ALERTS,
            message_type="moral_alert",
            payload=alert.to_dict(),
        )
        
        count = len(self.channel_connections[MoralWSChannel.ALERTS])
        
        self.statistics["total_alerts_broadcast"] += 1
        self.statistics["total_messages_sent"] += count
        
        return count
    
    async def broadcast_violation(
        self,
        violation_id: str,
        violation_type: str,
        severity: str,
        details: Dict[str, Any],
    ) -> int:
        """
        Broadcast a guardrail violation.
        
        Args:
            violation_id: Violation ID
            violation_type: Type of violation
            severity: Severity level
            details: Violation details
        
        Returns:
            Number of clients notified
        """
        message = MoralWSMessage(
            channel=MoralWSChannel.VIOLATIONS,
            message_type="guardrail_violation",
            payload={
                "violation_id": violation_id,
                "violation_type": violation_type,
                "severity": severity,
                "details": details,
                "timestamp": datetime.utcnow().isoformat(),
            },
        )
        
        count = len(self.channel_connections[MoralWSChannel.VIOLATIONS])
        self.statistics["total_messages_sent"] += count
        
        return count
    
    async def broadcast_reasoning_update(
        self,
        capsule_id: str,
        action_type: str,
        decision: str,
        reasoning_summary: str,
        confidence: float,
    ) -> int:
        """
        Broadcast a reasoning update.
        
        Args:
            capsule_id: Explainability capsule ID
            action_type: Type of action
            decision: Decision made
            reasoning_summary: Summary of reasoning
            confidence: Confidence level
        
        Returns:
            Number of clients notified
        """
        message = MoralWSMessage(
            channel=MoralWSChannel.REASONING,
            message_type="reasoning_update",
            payload={
                "capsule_id": capsule_id,
                "action_type": action_type,
                "decision": decision,
                "reasoning_summary": reasoning_summary,
                "confidence": confidence,
                "timestamp": datetime.utcnow().isoformat(),
            },
        )
        
        count = len(self.channel_connections[MoralWSChannel.REASONING])
        self.statistics["total_messages_sent"] += count
        
        return count
    
    async def broadcast_fairness_alert(
        self,
        alert_id: str,
        disparity_type: str,
        severity: str,
        affected_groups: List[str],
        recommendations: List[str],
    ) -> int:
        """
        Broadcast a fairness/disparity alert.
        
        Args:
            alert_id: Alert ID
            disparity_type: Type of disparity
            severity: Severity level
            affected_groups: Groups affected
            recommendations: Recommended actions
        
        Returns:
            Number of clients notified
        """
        message = MoralWSMessage(
            channel=MoralWSChannel.FAIRNESS,
            message_type="fairness_alert",
            payload={
                "alert_id": alert_id,
                "disparity_type": disparity_type,
                "severity": severity,
                "affected_groups": affected_groups,
                "recommendations": recommendations,
                "timestamp": datetime.utcnow().isoformat(),
            },
        )
        
        count = len(self.channel_connections[MoralWSChannel.FAIRNESS])
        self.statistics["total_messages_sent"] += count
        
        return count
    
    async def send_ethical_violation_alert(
        self,
        action_type: str,
        requester_id: str,
        violation_details: str,
        severity: MoralAlertSeverity = MoralAlertSeverity.SERIOUS,
    ) -> MoralAlert:
        """
        Send an ethical violation alert.
        
        Args:
            action_type: Type of action
            requester_id: Requester ID
            violation_details: Details of violation
            severity: Alert severity
        
        Returns:
            Created alert
        """
        alert = MoralAlert(
            alert_type=MoralAlertType.ETHICAL_VIOLATION,
            severity=severity,
            title="Ethical Violation Detected",
            description=violation_details,
            action_type=action_type,
            requester_id=requester_id,
            requires_action=severity in [MoralAlertSeverity.CRITICAL, MoralAlertSeverity.BLOCKING],
            recommendations=[
                "Review action for ethical compliance",
                "Consult with supervisor",
                "Document incident",
            ],
        )
        
        await self.broadcast_alert(alert)
        
        return alert
    
    async def send_bias_alert(
        self,
        action_type: str,
        bias_type: str,
        confidence: float,
        mitigation_strategies: List[str],
    ) -> MoralAlert:
        """
        Send a bias detection alert.
        
        Args:
            action_type: Type of action
            bias_type: Type of bias detected
            confidence: Detection confidence
            mitigation_strategies: Suggested mitigations
        
        Returns:
            Created alert
        """
        alert = MoralAlert(
            alert_type=MoralAlertType.BIAS_DETECTED,
            severity=MoralAlertSeverity.WARNING if confidence < 0.7 else MoralAlertSeverity.SERIOUS,
            title="Potential Bias Detected",
            description=f"Bias type: {bias_type} detected with {confidence:.0%} confidence",
            action_type=action_type,
            details={"bias_type": bias_type, "confidence": confidence},
            recommendations=mitigation_strategies,
            requires_action=confidence >= 0.7,
        )
        
        await self.broadcast_alert(alert)
        
        return alert
    
    async def send_high_risk_alert(
        self,
        action_type: str,
        requester_id: str,
        risk_factors: List[str],
        required_approvals: List[str],
    ) -> MoralAlert:
        """
        Send a high-risk action alert.
        
        Args:
            action_type: Type of action
            requester_id: Requester ID
            risk_factors: Identified risk factors
            required_approvals: Required approvals
        
        Returns:
            Created alert
        """
        alert = MoralAlert(
            alert_type=MoralAlertType.HIGH_RISK_ACTION,
            severity=MoralAlertSeverity.CRITICAL,
            title="High-Risk Action Detected",
            description=f"Action '{action_type}' requires elevated review",
            action_type=action_type,
            requester_id=requester_id,
            details={"risk_factors": risk_factors},
            recommendations=[f"Obtain approval from: {', '.join(required_approvals)}"],
            requires_action=True,
        )
        
        await self.broadcast_alert(alert)
        
        return alert
    
    async def send_community_harm_alert(
        self,
        action_type: str,
        location: str,
        harm_risk_score: float,
        community_considerations: List[str],
    ) -> MoralAlert:
        """
        Send a community harm risk alert.
        
        Args:
            action_type: Type of action
            location: Location of action
            harm_risk_score: Risk score (0-100)
            community_considerations: Community factors
        
        Returns:
            Created alert
        """
        severity = MoralAlertSeverity.INFO
        if harm_risk_score >= 75:
            severity = MoralAlertSeverity.CRITICAL
        elif harm_risk_score >= 50:
            severity = MoralAlertSeverity.SERIOUS
        elif harm_risk_score >= 25:
            severity = MoralAlertSeverity.WARNING
        
        alert = MoralAlert(
            alert_type=MoralAlertType.COMMUNITY_HARM_RISK,
            severity=severity,
            title="Community Harm Risk Identified",
            description=f"Action at {location} has {harm_risk_score:.0f}% community harm risk",
            action_type=action_type,
            details={
                "location": location,
                "harm_risk_score": harm_risk_score,
                "considerations": community_considerations,
            },
            recommendations=[
                "Consider community impact",
                "Engage community liaison if needed",
                "Document community considerations",
            ],
            requires_action=harm_risk_score >= 50,
        )
        
        await self.broadcast_alert(alert)
        
        return alert
    
    async def send_veto_notification(
        self,
        action_type: str,
        requester_id: str,
        reason: str,
        alternatives: List[str],
    ) -> MoralAlert:
        """
        Send a veto notification.
        
        Args:
            action_type: Type of action vetoed
            requester_id: Requester ID
            reason: Reason for veto
            alternatives: Alternative actions
        
        Returns:
            Created alert
        """
        alert = MoralAlert(
            alert_type=MoralAlertType.VETO_ISSUED,
            severity=MoralAlertSeverity.BLOCKING,
            title="Action Vetoed",
            description=f"Action '{action_type}' has been vetoed: {reason}",
            action_type=action_type,
            requester_id=requester_id,
            details={"reason": reason},
            recommendations=alternatives,
            requires_action=True,
        )
        
        await self.broadcast_alert(alert)
        
        return alert
    
    async def send_approval_request(
        self,
        action_type: str,
        requester_id: str,
        approval_type: str,
        required_authority: str,
        urgency: str,
    ) -> MoralAlert:
        """
        Send an approval request notification.
        
        Args:
            action_type: Type of action
            requester_id: Requester ID
            approval_type: Type of approval needed
            required_authority: Authority level required
            urgency: Urgency level
        
        Returns:
            Created alert
        """
        severity = MoralAlertSeverity.WARNING
        if urgency == "critical":
            severity = MoralAlertSeverity.CRITICAL
        elif urgency == "high":
            severity = MoralAlertSeverity.SERIOUS
        
        alert = MoralAlert(
            alert_type=MoralAlertType.APPROVAL_REQUIRED,
            severity=severity,
            title="Approval Required",
            description=f"Action '{action_type}' requires {required_authority} approval",
            action_type=action_type,
            requester_id=requester_id,
            details={
                "approval_type": approval_type,
                "required_authority": required_authority,
                "urgency": urgency,
            },
            recommendations=[
                f"Route to {required_authority} for approval",
                "Document approval decision",
            ],
            requires_action=True,
        )
        
        await self.broadcast_alert(alert)
        
        return alert
    
    async def handle_message(
        self,
        connection_id: str,
        message: Dict[str, Any],
    ) -> Optional[MoralWSMessage]:
        """
        Handle an incoming WebSocket message.
        
        Args:
            connection_id: Connection ID
            message: Message payload
        
        Returns:
            Response message if any
        """
        connection = self.connections.get(connection_id)
        if not connection:
            return None
        
        connection.last_activity = datetime.utcnow()
        
        message_type = message.get("type", "")
        
        if message_type == "subscribe":
            topics = message.get("topics", [])
            connection.subscriptions.update(topics)
            return MoralWSMessage(
                channel=connection.channel,
                message_type="subscribed",
                payload={"topics": list(connection.subscriptions)},
            )
        
        elif message_type == "unsubscribe":
            topics = message.get("topics", [])
            connection.subscriptions.difference_update(topics)
            return MoralWSMessage(
                channel=connection.channel,
                message_type="unsubscribed",
                payload={"topics": list(connection.subscriptions)},
            )
        
        elif message_type == "acknowledge_alert":
            alert_id = message.get("alert_id")
            if alert_id in self.alerts:
                self.alerts[alert_id].acknowledged = True
                return MoralWSMessage(
                    channel=connection.channel,
                    message_type="alert_acknowledged",
                    payload={"alert_id": alert_id},
                )
        
        elif message_type == "ping":
            return MoralWSMessage(
                channel=connection.channel,
                message_type="pong",
                payload={"timestamp": datetime.utcnow().isoformat()},
            )
        
        return None
    
    def get_connection(self, connection_id: str) -> Optional[MoralWSConnection]:
        """Get connection by ID."""
        return self.connections.get(connection_id)
    
    def get_connections_by_channel(self, channel: MoralWSChannel) -> List[MoralWSConnection]:
        """Get all connections for a channel."""
        return [
            self.connections[cid]
            for cid in self.channel_connections[channel]
            if cid in self.connections
        ]
    
    def get_active_alerts(self) -> List[MoralAlert]:
        """Get unacknowledged alerts."""
        return [a for a in self.alerts.values() if not a.acknowledged]
    
    def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge an alert."""
        alert = self.alerts.get(alert_id)
        if alert:
            alert.acknowledged = True
            return True
        return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get WebSocket manager statistics."""
        return {
            **self.statistics,
            "connections_by_channel": {
                channel.value: len(connections)
                for channel, connections in self.channel_connections.items()
            },
            "active_alerts": len(self.get_active_alerts()),
        }


async def alerts_channel_handler(websocket: Any, user_id: str):
    """Handler for /ws/moral/alerts channel."""
    manager = MoralCompassWSManager()
    connection = await manager.connect(MoralWSChannel.ALERTS, user_id, websocket)
    
    try:
        while True:
            data = await websocket.receive_json()
            response = await manager.handle_message(connection.connection_id, data)
            if response:
                await websocket.send_json(response.to_dict())
    except Exception:
        pass
    finally:
        await manager.disconnect(connection.connection_id)


async def violations_channel_handler(websocket: Any, user_id: str):
    """Handler for /ws/moral/violations channel."""
    manager = MoralCompassWSManager()
    connection = await manager.connect(MoralWSChannel.VIOLATIONS, user_id, websocket)
    
    try:
        while True:
            data = await websocket.receive_json()
            response = await manager.handle_message(connection.connection_id, data)
            if response:
                await websocket.send_json(response.to_dict())
    except Exception:
        pass
    finally:
        await manager.disconnect(connection.connection_id)


async def reasoning_channel_handler(websocket: Any, user_id: str):
    """Handler for /ws/moral/reasoning channel."""
    manager = MoralCompassWSManager()
    connection = await manager.connect(MoralWSChannel.REASONING, user_id, websocket)
    
    try:
        while True:
            data = await websocket.receive_json()
            response = await manager.handle_message(connection.connection_id, data)
            if response:
                await websocket.send_json(response.to_dict())
    except Exception:
        pass
    finally:
        await manager.disconnect(connection.connection_id)


async def fairness_channel_handler(websocket: Any, user_id: str):
    """Handler for /ws/moral/fairness channel."""
    manager = MoralCompassWSManager()
    connection = await manager.connect(MoralWSChannel.FAIRNESS, user_id, websocket)
    
    try:
        while True:
            data = await websocket.receive_json()
            response = await manager.handle_message(connection.connection_id, data)
            if response:
                await websocket.send_json(response.to_dict())
    except Exception:
        pass
    finally:
        await manager.disconnect(connection.connection_id)
