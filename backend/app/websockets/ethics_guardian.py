"""
Phase 26: Ethics Guardian WebSocket Channels

WebSocket channels for real-time ethics monitoring:
- /ws/ethics/alerts - Bias or ethics violations
- /ws/ethics/review - Required human input
- /ws/ethics/audit - Transparency logs
"""

from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List, Set, Optional, Any
from datetime import datetime
from enum import Enum
import json
import asyncio


class EthicsAlertType(Enum):
    """Types of ethics alerts."""
    BIAS_DETECTED = "BIAS_DETECTED"
    BIAS_POSSIBLE = "BIAS_POSSIBLE"
    CIVIL_RIGHTS_VIOLATION = "CIVIL_RIGHTS_VIOLATION"
    FORCE_RISK_HIGH = "FORCE_RISK_HIGH"
    ETHICS_SCORE_LOW = "ETHICS_SCORE_LOW"
    SAFEGUARD_TRIGGERED = "SAFEGUARD_TRIGGERED"
    COMMUNITY_IMPACT = "COMMUNITY_IMPACT"
    ACTION_BLOCKED = "ACTION_BLOCKED"


class ReviewType(Enum):
    """Types of human review requests."""
    BIAS_REVIEW = "BIAS_REVIEW"
    FORCE_AUTHORIZATION = "FORCE_AUTHORIZATION"
    CIVIL_RIGHTS_REVIEW = "CIVIL_RIGHTS_REVIEW"
    ETHICS_APPROVAL = "ETHICS_APPROVAL"
    COMMUNITY_LIAISON = "COMMUNITY_LIAISON"
    ESCALATION = "ESCALATION"


class EthicsWSClient:
    """WebSocket client for ethics channels."""
    
    def __init__(
        self,
        websocket: WebSocket,
        client_id: str,
        role: str = "OPERATOR",
        department: str = "RTCC",
    ):
        self.websocket = websocket
        self.client_id = client_id
        self.role = role
        self.department = department
        self.connected_at = datetime.now()
        self.subscribed_channels: Set[str] = set()
        self.alert_filters: Dict[str, Any] = {}
    
    async def send_message(self, message: Dict[str, Any]):
        """Send message to client."""
        try:
            await self.websocket.send_json(message)
        except Exception:
            pass
    
    def matches_filter(self, alert_type: str, severity: str) -> bool:
        """Check if alert matches client's filters."""
        if not self.alert_filters:
            return True
        
        type_filter = self.alert_filters.get("alert_types", [])
        if type_filter and alert_type not in type_filter:
            return False
        
        severity_filter = self.alert_filters.get("min_severity", "INFO")
        severity_order = ["INFO", "WARNING", "CRITICAL", "VIOLATION"]
        if severity_order.index(severity) < severity_order.index(severity_filter):
            return False
        
        return True


class EthicsWSManager:
    """
    WebSocket manager for ethics guardian channels.
    
    Manages connections for:
    - /ws/ethics/alerts - Real-time bias and ethics alerts
    - /ws/ethics/review - Human review requests
    - /ws/ethics/audit - Transparency audit logs
    """
    
    _instance = None
    
    def __init__(self):
        self._alerts_clients: Dict[str, EthicsWSClient] = {}
        self._review_clients: Dict[str, EthicsWSClient] = {}
        self._audit_clients: Dict[str, EthicsWSClient] = {}
        self._pending_reviews: Dict[str, Dict] = {}
        self._alert_history: List[Dict] = []
    
    @classmethod
    def get_instance(cls) -> "EthicsWSManager":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    async def connect_alerts(
        self,
        websocket: WebSocket,
        client_id: str,
        role: str = "OPERATOR",
        department: str = "RTCC",
    ):
        """Connect client to alerts channel."""
        await websocket.accept()
        
        client = EthicsWSClient(
            websocket=websocket,
            client_id=client_id,
            role=role,
            department=department,
        )
        client.subscribed_channels.add("alerts")
        
        self._alerts_clients[client_id] = client
        
        await client.send_message({
            "type": "connection_established",
            "channel": "alerts",
            "client_id": client_id,
            "timestamp": datetime.now().isoformat(),
        })
    
    async def disconnect_alerts(self, client_id: str):
        """Disconnect client from alerts channel."""
        if client_id in self._alerts_clients:
            del self._alerts_clients[client_id]
    
    async def connect_review(
        self,
        websocket: WebSocket,
        client_id: str,
        role: str = "SUPERVISOR",
        department: str = "RTCC",
    ):
        """Connect client to review channel."""
        await websocket.accept()
        
        client = EthicsWSClient(
            websocket=websocket,
            client_id=client_id,
            role=role,
            department=department,
        )
        client.subscribed_channels.add("review")
        
        self._review_clients[client_id] = client
        
        pending_count = len([
            r for r in self._pending_reviews.values()
            if r.get("status") == "PENDING"
        ])
        
        await client.send_message({
            "type": "connection_established",
            "channel": "review",
            "client_id": client_id,
            "pending_reviews": pending_count,
            "timestamp": datetime.now().isoformat(),
        })
    
    async def disconnect_review(self, client_id: str):
        """Disconnect client from review channel."""
        if client_id in self._review_clients:
            del self._review_clients[client_id]
    
    async def connect_audit(
        self,
        websocket: WebSocket,
        client_id: str,
        role: str = "AUDITOR",
        department: str = "RTCC",
    ):
        """Connect client to audit channel."""
        await websocket.accept()
        
        client = EthicsWSClient(
            websocket=websocket,
            client_id=client_id,
            role=role,
            department=department,
        )
        client.subscribed_channels.add("audit")
        
        self._audit_clients[client_id] = client
        
        await client.send_message({
            "type": "connection_established",
            "channel": "audit",
            "client_id": client_id,
            "timestamp": datetime.now().isoformat(),
        })
    
    async def disconnect_audit(self, client_id: str):
        """Disconnect client from audit channel."""
        if client_id in self._audit_clients:
            del self._audit_clients[client_id]
    
    async def broadcast_alert(
        self,
        alert_type: EthicsAlertType,
        severity: str,
        action_id: str,
        data: Dict[str, Any],
    ):
        """Broadcast ethics alert to all connected clients."""
        message = {
            "type": "ethics_alert",
            "alert_type": alert_type.value,
            "severity": severity,
            "action_id": action_id,
            "data": data,
            "timestamp": datetime.now().isoformat(),
        }
        
        self._alert_history.append(message)
        if len(self._alert_history) > 1000:
            self._alert_history = self._alert_history[-500:]
        
        for client in self._alerts_clients.values():
            if client.matches_filter(alert_type.value, severity):
                await client.send_message(message)
    
    async def broadcast_bias_alert(
        self,
        action_id: str,
        bias_status: str,
        affected_groups: List[str],
        metrics: Dict[str, float],
        blocked: bool,
    ):
        """Broadcast bias detection alert."""
        if bias_status == "BIAS_DETECTED_BLOCKED":
            alert_type = EthicsAlertType.BIAS_DETECTED
            severity = "VIOLATION"
        elif bias_status == "POSSIBLE_BIAS_FLAG_REVIEW":
            alert_type = EthicsAlertType.BIAS_POSSIBLE
            severity = "WARNING"
        else:
            return
        
        await self.broadcast_alert(
            alert_type=alert_type,
            severity=severity,
            action_id=action_id,
            data={
                "bias_status": bias_status,
                "affected_groups": affected_groups,
                "metrics": metrics,
                "blocked": blocked,
            },
        )
    
    async def broadcast_civil_rights_alert(
        self,
        action_id: str,
        violations: List[Dict],
        blocked: bool,
    ):
        """Broadcast civil rights violation alert."""
        if not violations:
            return
        
        severity = "VIOLATION" if blocked else "WARNING"
        
        await self.broadcast_alert(
            alert_type=EthicsAlertType.CIVIL_RIGHTS_VIOLATION,
            severity=severity,
            action_id=action_id,
            data={
                "violations": violations,
                "blocked": blocked,
            },
        )
    
    async def broadcast_force_risk_alert(
        self,
        action_id: str,
        risk_score: float,
        risk_level: str,
        requires_review: bool,
    ):
        """Broadcast high force risk alert."""
        if risk_level not in ["HIGH", "CRITICAL"]:
            return
        
        severity = "CRITICAL" if risk_level == "CRITICAL" else "WARNING"
        
        await self.broadcast_alert(
            alert_type=EthicsAlertType.FORCE_RISK_HIGH,
            severity=severity,
            action_id=action_id,
            data={
                "risk_score": risk_score,
                "risk_level": risk_level,
                "requires_review": requires_review,
            },
        )
    
    async def broadcast_ethics_score_alert(
        self,
        action_id: str,
        ethics_score: float,
        ethics_level: str,
        required_action: str,
    ):
        """Broadcast low ethics score alert."""
        if ethics_level not in ["CONCERNING", "CRITICAL"]:
            return
        
        severity = "CRITICAL" if ethics_level == "CRITICAL" else "WARNING"
        
        await self.broadcast_alert(
            alert_type=EthicsAlertType.ETHICS_SCORE_LOW,
            severity=severity,
            action_id=action_id,
            data={
                "ethics_score": ethics_score,
                "ethics_level": ethics_level,
                "required_action": required_action,
            },
        )
    
    async def broadcast_safeguard_alert(
        self,
        action_id: str,
        communities_affected: List[str],
        triggered_rules: List[str],
        safeguard_level: str,
    ):
        """Broadcast safeguard triggered alert."""
        if safeguard_level not in ["HIGH", "MAXIMUM"]:
            return
        
        severity = "WARNING" if safeguard_level == "HIGH" else "CRITICAL"
        
        await self.broadcast_alert(
            alert_type=EthicsAlertType.SAFEGUARD_TRIGGERED,
            severity=severity,
            action_id=action_id,
            data={
                "communities_affected": communities_affected,
                "triggered_rules": triggered_rules,
                "safeguard_level": safeguard_level,
            },
        )
    
    async def request_human_review(
        self,
        review_id: str,
        review_type: ReviewType,
        action_id: str,
        urgency: str,
        context: Dict[str, Any],
        required_role: str = "SUPERVISOR",
    ):
        """Request human review and notify reviewers."""
        review_request = {
            "review_id": review_id,
            "review_type": review_type.value,
            "action_id": action_id,
            "urgency": urgency,
            "context": context,
            "required_role": required_role,
            "status": "PENDING",
            "created_at": datetime.now().isoformat(),
            "assigned_to": None,
            "completed_at": None,
            "decision": None,
        }
        
        self._pending_reviews[review_id] = review_request
        
        message = {
            "type": "review_request",
            "review_id": review_id,
            "review_type": review_type.value,
            "action_id": action_id,
            "urgency": urgency,
            "context": context,
            "required_role": required_role,
            "timestamp": datetime.now().isoformat(),
        }
        
        for client in self._review_clients.values():
            role_hierarchy = {
                "OPERATOR": 1,
                "SUPERVISOR": 2,
                "COMMAND_STAFF": 3,
                "ADMIN": 4,
            }
            client_level = role_hierarchy.get(client.role, 1)
            required_level = role_hierarchy.get(required_role, 2)
            
            if client_level >= required_level:
                await client.send_message(message)
    
    async def submit_review_decision(
        self,
        review_id: str,
        reviewer_id: str,
        decision: str,
        notes: str,
    ):
        """Submit review decision and notify clients."""
        if review_id not in self._pending_reviews:
            return False
        
        review = self._pending_reviews[review_id]
        review["status"] = "COMPLETED"
        review["assigned_to"] = reviewer_id
        review["completed_at"] = datetime.now().isoformat()
        review["decision"] = decision
        review["notes"] = notes
        
        message = {
            "type": "review_completed",
            "review_id": review_id,
            "action_id": review["action_id"],
            "reviewer_id": reviewer_id,
            "decision": decision,
            "notes": notes,
            "timestamp": datetime.now().isoformat(),
        }
        
        for client in self._review_clients.values():
            await client.send_message(message)
        
        return True
    
    async def broadcast_audit_entry(
        self,
        entry_id: str,
        action_id: str,
        action_type: str,
        severity: str,
        summary: str,
        details: Dict[str, Any],
    ):
        """Broadcast audit log entry to audit channel."""
        message = {
            "type": "audit_entry",
            "entry_id": entry_id,
            "action_id": action_id,
            "action_type": action_type,
            "severity": severity,
            "summary": summary,
            "details": details,
            "timestamp": datetime.now().isoformat(),
        }
        
        for client in self._audit_clients.values():
            await client.send_message(message)
    
    async def set_client_filters(
        self,
        client_id: str,
        channel: str,
        filters: Dict[str, Any],
    ):
        """Set alert filters for a client."""
        if channel == "alerts" and client_id in self._alerts_clients:
            self._alerts_clients[client_id].alert_filters = filters
        elif channel == "review" and client_id in self._review_clients:
            self._review_clients[client_id].alert_filters = filters
        elif channel == "audit" and client_id in self._audit_clients:
            self._audit_clients[client_id].alert_filters = filters
    
    def get_connected_clients(self, channel: str) -> List[str]:
        """Get list of connected client IDs for a channel."""
        if channel == "alerts":
            return list(self._alerts_clients.keys())
        elif channel == "review":
            return list(self._review_clients.keys())
        elif channel == "audit":
            return list(self._audit_clients.keys())
        return []
    
    def get_pending_reviews(self) -> List[Dict]:
        """Get list of pending review requests."""
        return [
            r for r in self._pending_reviews.values()
            if r.get("status") == "PENDING"
        ]
    
    def get_alert_history(self, limit: int = 100) -> List[Dict]:
        """Get recent alert history."""
        return self._alert_history[-limit:]


def get_ethics_ws_manager() -> EthicsWSManager:
    """Get the singleton EthicsWSManager instance."""
    return EthicsWSManager.get_instance()


async def handle_alerts_websocket(websocket: WebSocket, client_id: str):
    """Handle WebSocket connection for alerts channel."""
    manager = get_ethics_ws_manager()
    
    try:
        await manager.connect_alerts(websocket, client_id)
        
        while True:
            data = await websocket.receive_json()
            
            if data.get("type") == "set_filters":
                await manager.set_client_filters(
                    client_id,
                    "alerts",
                    data.get("filters", {}),
                )
            elif data.get("type") == "ping":
                await websocket.send_json({
                    "type": "pong",
                    "timestamp": datetime.now().isoformat(),
                })
    
    except WebSocketDisconnect:
        await manager.disconnect_alerts(client_id)


async def handle_review_websocket(websocket: WebSocket, client_id: str, role: str):
    """Handle WebSocket connection for review channel."""
    manager = get_ethics_ws_manager()
    
    try:
        await manager.connect_review(websocket, client_id, role)
        
        while True:
            data = await websocket.receive_json()
            
            if data.get("type") == "submit_decision":
                await manager.submit_review_decision(
                    data.get("review_id"),
                    client_id,
                    data.get("decision"),
                    data.get("notes", ""),
                )
            elif data.get("type") == "ping":
                await websocket.send_json({
                    "type": "pong",
                    "timestamp": datetime.now().isoformat(),
                })
    
    except WebSocketDisconnect:
        await manager.disconnect_review(client_id)


async def handle_audit_websocket(websocket: WebSocket, client_id: str):
    """Handle WebSocket connection for audit channel."""
    manager = get_ethics_ws_manager()
    
    try:
        await manager.connect_audit(websocket, client_id)
        
        while True:
            data = await websocket.receive_json()
            
            if data.get("type") == "ping":
                await websocket.send_json({
                    "type": "pong",
                    "timestamp": datetime.now().isoformat(),
                })
    
    except WebSocketDisconnect:
        await manager.disconnect_audit(client_id)
