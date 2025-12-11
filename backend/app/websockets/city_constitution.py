"""
Phase 25: AI City Constitution WebSocket Channels

Real-time WebSocket channels for constitutional governance:
- /ws/governance/decisions - Real-time constitutional decision notifications
- /ws/governance/approvals - Approval workflow updates
- /ws/governance/policy-updates - Policy change notifications
"""

import asyncio
import json
from datetime import datetime
from typing import Any, Optional
from dataclasses import dataclass, field
import uuid


@dataclass
class ConstitutionWebSocketClient:
    """Represents a connected WebSocket client for constitutional governance."""
    client_id: str
    channel: str
    connected_at: datetime = field(default_factory=datetime.utcnow)
    last_message: Optional[datetime] = None
    subscriptions: list[str] = field(default_factory=list)
    user_id: Optional[str] = None
    role: Optional[str] = None


class ConstitutionWebSocketManager:
    """
    WebSocket manager for AI City Constitution real-time updates.
    
    Channels:
    - /ws/governance/decisions - Real-time constitutional validation decisions
    - /ws/governance/approvals - Human-in-the-loop approval workflow updates
    - /ws/governance/policy-updates - Policy translation and change notifications
    """

    def __init__(self):
        self._clients: dict[str, list[Any]] = {
            "decisions": [],
            "approvals": [],
            "policy-updates": [],
        }
        self._client_info: dict[str, ConstitutionWebSocketClient] = {}
        self._message_queue: list[dict[str, Any]] = []
        self._running = False
        self._broadcast_interval = 0.5

    async def connect(
        self,
        websocket: Any,
        channel: str,
        user_id: Optional[str] = None,
        role: Optional[str] = None,
    ) -> str:
        """Connect a client to a channel."""
        client_id = f"const-client-{uuid.uuid4().hex[:12]}"

        if channel in self._clients:
            self._clients[channel].append(websocket)

        self._client_info[client_id] = ConstitutionWebSocketClient(
            client_id=client_id,
            channel=channel,
            user_id=user_id,
            role=role,
        )

        await self._send_welcome(websocket, client_id, channel)
        return client_id

    async def disconnect(self, websocket: Any, channel: str):
        """Disconnect a client from a channel."""
        if channel in self._clients:
            if websocket in self._clients[channel]:
                self._clients[channel].remove(websocket)

        client_id = None
        for cid, info in self._client_info.items():
            if info.channel == channel:
                client_id = cid
                break

        if client_id:
            del self._client_info[client_id]

    async def _send_welcome(self, websocket: Any, client_id: str, channel: str):
        """Send welcome message to newly connected client."""
        message = {
            "type": "welcome",
            "client_id": client_id,
            "channel": channel,
            "timestamp": datetime.utcnow().isoformat(),
            "message": f"Connected to constitutional governance {channel} channel",
            "service": "ai-city-constitution",
        }
        await self._send_to_client(websocket, message)

    async def _send_to_client(self, websocket: Any, message: dict[str, Any]):
        """Send a message to a specific client."""
        try:
            if hasattr(websocket, "send_json"):
                await websocket.send_json(message)
            elif hasattr(websocket, "send"):
                await websocket.send(json.dumps(message))
        except Exception:
            pass

    async def broadcast_validation_decision(self, decision: dict[str, Any]):
        """Broadcast a constitutional validation decision."""
        message = {
            "type": "validation_decision",
            "data": decision,
            "timestamp": datetime.utcnow().isoformat(),
        }
        await self._broadcast_to_channel("decisions", message)

    async def broadcast_validation_denied(
        self,
        decision_id: str,
        action_type: str,
        blocking_rules: list[dict[str, Any]],
        explanation: str,
    ):
        """Broadcast a denied validation with explanation."""
        message = {
            "type": "validation_denied",
            "decision_id": decision_id,
            "action_type": action_type,
            "blocking_rules": blocking_rules,
            "explanation": explanation,
            "timestamp": datetime.utcnow().isoformat(),
        }
        await self._broadcast_to_channel("decisions", message)

    async def broadcast_validation_requires_review(
        self,
        decision_id: str,
        action_type: str,
        required_approvals: list[str],
        risk_factors: list[str],
    ):
        """Broadcast a validation that requires human review."""
        message = {
            "type": "validation_requires_review",
            "decision_id": decision_id,
            "action_type": action_type,
            "required_approvals": required_approvals,
            "risk_factors": risk_factors,
            "timestamp": datetime.utcnow().isoformat(),
        }
        await self._broadcast_to_channel("decisions", message)

    async def broadcast_risk_assessment(self, assessment: dict[str, Any]):
        """Broadcast a risk assessment result."""
        message = {
            "type": "risk_assessment",
            "data": assessment,
            "timestamp": datetime.utcnow().isoformat(),
        }
        await self._broadcast_to_channel("decisions", message)

    async def broadcast_high_risk_alert(
        self,
        assessment_id: str,
        action_type: str,
        risk_score: float,
        risk_category: str,
        recommendations: list[str],
    ):
        """Broadcast a high-risk alert."""
        message = {
            "type": "high_risk_alert",
            "assessment_id": assessment_id,
            "action_type": action_type,
            "risk_score": risk_score,
            "risk_category": risk_category,
            "recommendations": recommendations,
            "timestamp": datetime.utcnow().isoformat(),
        }
        await self._broadcast_to_channel("decisions", message)

    async def broadcast_approval_request_created(self, request: dict[str, Any]):
        """Broadcast a new approval request."""
        message = {
            "type": "approval_request_created",
            "data": request,
            "timestamp": datetime.utcnow().isoformat(),
        }
        await self._broadcast_to_channel("approvals", message)

    async def broadcast_approval_submitted(
        self,
        request_id: str,
        approver_id: str,
        approval_type: str,
        decision: str,
        remaining_approvals: int,
    ):
        """Broadcast an approval submission."""
        message = {
            "type": "approval_submitted",
            "request_id": request_id,
            "approver_id": approver_id,
            "approval_type": approval_type,
            "decision": decision,
            "remaining_approvals": remaining_approvals,
            "timestamp": datetime.utcnow().isoformat(),
        }
        await self._broadcast_to_channel("approvals", message)

    async def broadcast_approval_completed(
        self,
        request_id: str,
        action_id: str,
        final_status: str,
        total_approvals: int,
    ):
        """Broadcast approval workflow completion."""
        message = {
            "type": "approval_completed",
            "request_id": request_id,
            "action_id": action_id,
            "final_status": final_status,
            "total_approvals": total_approvals,
            "timestamp": datetime.utcnow().isoformat(),
        }
        await self._broadcast_to_channel("approvals", message)

    async def broadcast_approval_escalated(
        self,
        request_id: str,
        escalated_by: str,
        reason: str,
        new_approval_level: str,
    ):
        """Broadcast approval escalation."""
        message = {
            "type": "approval_escalated",
            "request_id": request_id,
            "escalated_by": escalated_by,
            "reason": reason,
            "new_approval_level": new_approval_level,
            "timestamp": datetime.utcnow().isoformat(),
        }
        await self._broadcast_to_channel("approvals", message)

    async def broadcast_approval_expired(
        self,
        request_id: str,
        action_id: str,
        expired_at: str,
    ):
        """Broadcast approval expiration."""
        message = {
            "type": "approval_expired",
            "request_id": request_id,
            "action_id": action_id,
            "expired_at": expired_at,
            "timestamp": datetime.utcnow().isoformat(),
        }
        await self._broadcast_to_channel("approvals", message)

    async def broadcast_pending_approval_reminder(
        self,
        request_id: str,
        action_type: str,
        time_remaining_minutes: int,
        required_approvals: list[str],
    ):
        """Broadcast reminder for pending approval."""
        message = {
            "type": "pending_approval_reminder",
            "request_id": request_id,
            "action_type": action_type,
            "time_remaining_minutes": time_remaining_minutes,
            "required_approvals": required_approvals,
            "timestamp": datetime.utcnow().isoformat(),
        }
        await self._broadcast_to_channel("approvals", message)

    async def broadcast_policy_created(self, policy: dict[str, Any]):
        """Broadcast a new policy creation."""
        message = {
            "type": "policy_created",
            "data": policy,
            "timestamp": datetime.utcnow().isoformat(),
        }
        await self._broadcast_to_channel("policy-updates", message)

    async def broadcast_policy_updated(
        self,
        policy_id: str,
        changes: dict[str, Any],
        updated_by: str,
    ):
        """Broadcast a policy update."""
        message = {
            "type": "policy_updated",
            "policy_id": policy_id,
            "changes": changes,
            "updated_by": updated_by,
            "timestamp": datetime.utcnow().isoformat(),
        }
        await self._broadcast_to_channel("policy-updates", message)

    async def broadcast_policy_deactivated(
        self,
        policy_id: str,
        deactivated_by: str,
        reason: Optional[str] = None,
    ):
        """Broadcast a policy deactivation."""
        message = {
            "type": "policy_deactivated",
            "policy_id": policy_id,
            "deactivated_by": deactivated_by,
            "reason": reason,
            "timestamp": datetime.utcnow().isoformat(),
        }
        await self._broadcast_to_channel("policy-updates", message)

    async def broadcast_policy_conflict_detected(
        self,
        policy_ids: list[str],
        conflict_type: str,
        description: str,
        resolution_suggestions: list[str],
    ):
        """Broadcast a policy conflict detection."""
        message = {
            "type": "policy_conflict_detected",
            "policy_ids": policy_ids,
            "conflict_type": conflict_type,
            "description": description,
            "resolution_suggestions": resolution_suggestions,
            "timestamp": datetime.utcnow().isoformat(),
        }
        await self._broadcast_to_channel("policy-updates", message)

    async def broadcast_legal_document_updated(
        self,
        document_id: str,
        document_title: str,
        source: str,
        update_type: str,
    ):
        """Broadcast a legal document update."""
        message = {
            "type": "legal_document_updated",
            "document_id": document_id,
            "document_title": document_title,
            "source": source,
            "update_type": update_type,
            "timestamp": datetime.utcnow().isoformat(),
        }
        await self._broadcast_to_channel("policy-updates", message)

    async def broadcast_constitutional_rule_added(
        self,
        rule_id: str,
        layer: str,
        action_categories: list[str],
        rationale: str,
    ):
        """Broadcast a new constitutional rule addition."""
        message = {
            "type": "constitutional_rule_added",
            "rule_id": rule_id,
            "layer": layer,
            "action_categories": action_categories,
            "rationale": rationale,
            "timestamp": datetime.utcnow().isoformat(),
        }
        await self._broadcast_to_channel("policy-updates", message)

    async def _broadcast_to_channel(self, channel: str, message: dict[str, Any]):
        """Broadcast message to all clients in a channel."""
        if channel not in self._clients:
            return

        disconnected = []
        for websocket in self._clients[channel]:
            try:
                await self._send_to_client(websocket, message)
            except Exception:
                disconnected.append(websocket)

        for ws in disconnected:
            self._clients[channel].remove(ws)

    def get_channel_stats(self) -> dict[str, Any]:
        """Get statistics for all channels."""
        return {
            "decisions": {
                "connected_clients": len(self._clients.get("decisions", [])),
            },
            "approvals": {
                "connected_clients": len(self._clients.get("approvals", [])),
            },
            "policy-updates": {
                "connected_clients": len(self._clients.get("policy-updates", [])),
            },
            "total_clients": len(self._client_info),
        }

    def get_client_info(self, client_id: str) -> Optional[dict[str, Any]]:
        """Get information about a specific client."""
        client = self._client_info.get(client_id)
        if client:
            return {
                "client_id": client.client_id,
                "channel": client.channel,
                "connected_at": client.connected_at.isoformat(),
                "last_message": client.last_message.isoformat() if client.last_message else None,
                "subscriptions": client.subscriptions,
                "user_id": client.user_id,
                "role": client.role,
            }
        return None

    def get_clients_by_role(self, role: str) -> list[dict[str, Any]]:
        """Get all clients with a specific role."""
        return [
            self.get_client_info(cid)
            for cid, info in self._client_info.items()
            if info.role == role
        ]


_constitution_ws_manager: Optional[ConstitutionWebSocketManager] = None


def get_constitution_ws_manager() -> ConstitutionWebSocketManager:
    """Get the singleton WebSocket manager instance."""
    global _constitution_ws_manager
    if _constitution_ws_manager is None:
        _constitution_ws_manager = ConstitutionWebSocketManager()
    return _constitution_ws_manager


async def handle_decisions_websocket(websocket: Any, user_id: Optional[str] = None):
    """
    Handle WebSocket connection for constitutional decisions channel.
    
    Channel: /ws/governance/decisions
    
    Receives real-time notifications for:
    - Constitutional validation decisions
    - Validation denials with explanations
    - Validations requiring human review
    - Risk assessments
    - High-risk alerts
    """
    manager = get_constitution_ws_manager()
    client_id = await manager.connect(websocket, "decisions", user_id)

    try:
        while True:
            try:
                if hasattr(websocket, "receive_json"):
                    data = await websocket.receive_json()
                elif hasattr(websocket, "recv"):
                    raw = await websocket.recv()
                    data = json.loads(raw)
                else:
                    await asyncio.sleep(1)
                    continue

                if data.get("type") == "ping":
                    await manager._send_to_client(websocket, {
                        "type": "pong",
                        "timestamp": datetime.utcnow().isoformat(),
                    })

                elif data.get("type") == "request_validation_stats":
                    from ..city_governance.constitution_engine import get_constitution_engine
                    engine = get_constitution_engine()
                    stats = {
                        "total_validations": engine.get_validation_count(),
                        "rules_count": len(engine.get_all_rules()),
                    }
                    await manager._send_to_client(websocket, {
                        "type": "validation_stats",
                        "data": stats,
                        "timestamp": datetime.utcnow().isoformat(),
                    })

                elif data.get("type") == "subscribe_action_category":
                    category = data.get("category")
                    client = manager._client_info.get(client_id)
                    if client and category:
                        client.subscriptions.append(f"category:{category}")
                        await manager._send_to_client(websocket, {
                            "type": "subscription_confirmed",
                            "subscription": f"category:{category}",
                            "timestamp": datetime.utcnow().isoformat(),
                        })

            except Exception:
                break
    finally:
        await manager.disconnect(websocket, "decisions")


async def handle_approvals_websocket(websocket: Any, user_id: Optional[str] = None, role: Optional[str] = None):
    """
    Handle WebSocket connection for approvals channel.
    
    Channel: /ws/governance/approvals
    
    Receives real-time notifications for:
    - New approval requests
    - Approval submissions
    - Approval completions
    - Approval escalations
    - Approval expirations
    - Pending approval reminders
    """
    manager = get_constitution_ws_manager()
    client_id = await manager.connect(websocket, "approvals", user_id, role)

    try:
        while True:
            try:
                if hasattr(websocket, "receive_json"):
                    data = await websocket.receive_json()
                elif hasattr(websocket, "recv"):
                    raw = await websocket.recv()
                    data = json.loads(raw)
                else:
                    await asyncio.sleep(1)
                    continue

                if data.get("type") == "ping":
                    await manager._send_to_client(websocket, {
                        "type": "pong",
                        "timestamp": datetime.utcnow().isoformat(),
                    })

                elif data.get("type") == "request_pending_approvals":
                    from ..city_governance.human_in_loop import get_human_in_loop_gateway
                    gateway = get_human_in_loop_gateway()
                    pending = gateway.get_pending_requests()
                    await manager._send_to_client(websocket, {
                        "type": "pending_approvals",
                        "data": [r.to_dict() for r in pending],
                        "count": len(pending),
                        "timestamp": datetime.utcnow().isoformat(),
                    })

                elif data.get("type") == "request_my_approvals":
                    from ..city_governance.human_in_loop import get_human_in_loop_gateway
                    gateway = get_human_in_loop_gateway()
                    approver_id = data.get("approver_id", user_id)
                    if approver_id:
                        pending = gateway.get_pending_for_approver(approver_id)
                        await manager._send_to_client(websocket, {
                            "type": "my_pending_approvals",
                            "data": [r.to_dict() for r in pending],
                            "count": len(pending),
                            "timestamp": datetime.utcnow().isoformat(),
                        })

                elif data.get("type") == "subscribe_approval_type":
                    approval_type = data.get("approval_type")
                    client = manager._client_info.get(client_id)
                    if client and approval_type:
                        client.subscriptions.append(f"approval_type:{approval_type}")
                        await manager._send_to_client(websocket, {
                            "type": "subscription_confirmed",
                            "subscription": f"approval_type:{approval_type}",
                            "timestamp": datetime.utcnow().isoformat(),
                        })

            except Exception:
                break
    finally:
        await manager.disconnect(websocket, "approvals")


async def handle_policy_updates_websocket(websocket: Any, user_id: Optional[str] = None):
    """
    Handle WebSocket connection for policy updates channel.
    
    Channel: /ws/governance/policy-updates
    
    Receives real-time notifications for:
    - Policy creations
    - Policy updates
    - Policy deactivations
    - Policy conflict detections
    - Legal document updates
    - Constitutional rule additions
    """
    manager = get_constitution_ws_manager()
    client_id = await manager.connect(websocket, "policy-updates", user_id)

    try:
        while True:
            try:
                if hasattr(websocket, "receive_json"):
                    data = await websocket.receive_json()
                elif hasattr(websocket, "recv"):
                    raw = await websocket.recv()
                    data = json.loads(raw)
                else:
                    await asyncio.sleep(1)
                    continue

                if data.get("type") == "ping":
                    await manager._send_to_client(websocket, {
                        "type": "pong",
                        "timestamp": datetime.utcnow().isoformat(),
                    })

                elif data.get("type") == "request_policy_stats":
                    from ..city_governance.policy_translator import get_policy_translator
                    translator = get_policy_translator()
                    rules = translator.get_all_rules()
                    stats = {
                        "total_policies": len(rules),
                        "active_policies": len([r for r in rules if r.is_active]),
                        "by_source": {},
                    }
                    for rule in rules:
                        source = rule.source.value
                        stats["by_source"][source] = stats["by_source"].get(source, 0) + 1
                    await manager._send_to_client(websocket, {
                        "type": "policy_stats",
                        "data": stats,
                        "timestamp": datetime.utcnow().isoformat(),
                    })

                elif data.get("type") == "request_legal_documents":
                    from ..city_governance.legislative_kb import get_legislative_kb
                    kb = get_legislative_kb()
                    documents = kb.get_all_documents()
                    await manager._send_to_client(websocket, {
                        "type": "legal_documents",
                        "data": [d.to_dict() for d in documents[:50]],
                        "total": len(documents),
                        "timestamp": datetime.utcnow().isoformat(),
                    })

                elif data.get("type") == "subscribe_source":
                    source = data.get("source")
                    client = manager._client_info.get(client_id)
                    if client and source:
                        client.subscriptions.append(f"source:{source}")
                        await manager._send_to_client(websocket, {
                            "type": "subscription_confirmed",
                            "subscription": f"source:{source}",
                            "timestamp": datetime.utcnow().isoformat(),
                        })

            except Exception:
                break
    finally:
        await manager.disconnect(websocket, "policy-updates")


async def start_approval_reminder_task(interval_minutes: int = 5):
    """
    Background task to send reminders for pending approvals.
    
    Runs periodically and broadcasts reminders for approvals
    that are approaching their expiration time.
    """
    manager = get_constitution_ws_manager()
    
    while True:
        try:
            from ..city_governance.human_in_loop import get_human_in_loop_gateway
            gateway = get_human_in_loop_gateway()
            pending = gateway.get_pending_requests()
            
            for request in pending:
                if request.expires_at:
                    time_remaining = (request.expires_at - datetime.utcnow()).total_seconds() / 60
                    
                    if 0 < time_remaining <= 30:
                        await manager.broadcast_pending_approval_reminder(
                            request_id=request.request_id,
                            action_type=request.action_type,
                            time_remaining_minutes=int(time_remaining),
                            required_approvals=[req.approval_type.value for req in request.requirements],
                        )
            
            await asyncio.sleep(interval_minutes * 60)
        except Exception:
            await asyncio.sleep(60)
