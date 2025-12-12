"""
AI Supervisor WebSocket Channels

Real-time WebSocket channels for the AI Sentinel Supervisor:
- /ws/supervisor/alerts - System alerts and notifications
- /ws/supervisor/violations - Ethics violations feed
- /ws/supervisor/system-health - Real-time system health metrics
- /ws/supervisor/recommendations - Sentinel recommendations
"""

import asyncio
import json
from datetime import datetime
from typing import Optional
from fastapi import WebSocket, WebSocketDisconnect


class AISupervisorWSManager:
    """
    WebSocket connection manager for AI Supervisor channels.
    
    Manages connections and broadcasts for:
    - System alerts
    - Ethics violations
    - System health metrics
    - Sentinel recommendations
    """
    
    def __init__(self):
        self.alert_connections: list[WebSocket] = []
        self.violation_connections: list[WebSocket] = []
        self.health_connections: list[WebSocket] = []
        self.recommendation_connections: list[WebSocket] = []
        
        self.all_connections: dict[str, list[WebSocket]] = {
            "alerts": self.alert_connections,
            "violations": self.violation_connections,
            "system-health": self.health_connections,
            "recommendations": self.recommendation_connections,
        }
    
    async def connect_alerts(self, websocket: WebSocket):
        """Connect to alerts channel."""
        await websocket.accept()
        self.alert_connections.append(websocket)
        await self._send_connection_ack(websocket, "alerts")
    
    async def connect_violations(self, websocket: WebSocket):
        """Connect to violations channel."""
        await websocket.accept()
        self.violation_connections.append(websocket)
        await self._send_connection_ack(websocket, "violations")
    
    async def connect_health(self, websocket: WebSocket):
        """Connect to system health channel."""
        await websocket.accept()
        self.health_connections.append(websocket)
        await self._send_connection_ack(websocket, "system-health")
    
    async def connect_recommendations(self, websocket: WebSocket):
        """Connect to recommendations channel."""
        await websocket.accept()
        self.recommendation_connections.append(websocket)
        await self._send_connection_ack(websocket, "recommendations")
    
    async def _send_connection_ack(self, websocket: WebSocket, channel: str):
        """Send connection acknowledgment."""
        await websocket.send_json({
            "type": "connection_ack",
            "channel": channel,
            "message": f"Connected to AI Supervisor {channel} channel",
            "timestamp": datetime.utcnow().isoformat(),
        })
    
    def disconnect_alerts(self, websocket: WebSocket):
        """Disconnect from alerts channel."""
        if websocket in self.alert_connections:
            self.alert_connections.remove(websocket)
    
    def disconnect_violations(self, websocket: WebSocket):
        """Disconnect from violations channel."""
        if websocket in self.violation_connections:
            self.violation_connections.remove(websocket)
    
    def disconnect_health(self, websocket: WebSocket):
        """Disconnect from system health channel."""
        if websocket in self.health_connections:
            self.health_connections.remove(websocket)
    
    def disconnect_recommendations(self, websocket: WebSocket):
        """Disconnect from recommendations channel."""
        if websocket in self.recommendation_connections:
            self.recommendation_connections.remove(websocket)
    
    async def broadcast_alert(
        self,
        alert_id: str,
        priority: str,
        title: str,
        description: str,
        sources: list[str],
        affected_systems: list[str],
        recommended_actions: list[str],
        auto_response_triggered: bool,
    ):
        """Broadcast a system alert."""
        message = {
            "type": "system_alert",
            "data": {
                "alert_id": alert_id,
                "priority": priority,
                "title": title,
                "description": description,
                "sources": sources,
                "affected_systems": affected_systems,
                "recommended_actions": recommended_actions,
                "auto_response_triggered": auto_response_triggered,
            },
            "timestamp": datetime.utcnow().isoformat(),
        }
        await self._broadcast_to_channel(self.alert_connections, message)
    
    async def broadcast_alert_acknowledged(
        self,
        alert_id: str,
        acknowledged_by: str,
    ):
        """Broadcast alert acknowledgment."""
        message = {
            "type": "alert_acknowledged",
            "data": {
                "alert_id": alert_id,
                "acknowledged_by": acknowledged_by,
            },
            "timestamp": datetime.utcnow().isoformat(),
        }
        await self._broadcast_to_channel(self.alert_connections, message)
    
    async def broadcast_alert_resolved(
        self,
        alert_id: str,
        resolution_notes: str,
    ):
        """Broadcast alert resolution."""
        message = {
            "type": "alert_resolved",
            "data": {
                "alert_id": alert_id,
                "resolution_notes": resolution_notes,
            },
            "timestamp": datetime.utcnow().isoformat(),
        }
        await self._broadcast_to_channel(self.alert_connections, message)
    
    async def broadcast_violation(
        self,
        violation_id: str,
        violation_type: str,
        severity: str,
        framework: str,
        engine: str,
        action_attempted: str,
        description: str,
        blocked: bool,
        escalated: bool,
    ):
        """Broadcast an ethics violation."""
        message = {
            "type": "ethics_violation",
            "data": {
                "violation_id": violation_id,
                "violation_type": violation_type,
                "severity": severity,
                "framework": framework,
                "engine": engine,
                "action_attempted": action_attempted,
                "description": description,
                "blocked": blocked,
                "escalated": escalated,
            },
            "timestamp": datetime.utcnow().isoformat(),
        }
        await self._broadcast_to_channel(self.violation_connections, message)
    
    async def broadcast_violation_reviewed(
        self,
        violation_id: str,
        reviewed_by: str,
        decision: str,
    ):
        """Broadcast violation review."""
        message = {
            "type": "violation_reviewed",
            "data": {
                "violation_id": violation_id,
                "reviewed_by": reviewed_by,
                "decision": decision,
            },
            "timestamp": datetime.utcnow().isoformat(),
        }
        await self._broadcast_to_channel(self.violation_connections, message)
    
    async def broadcast_action_blocked(
        self,
        validation_id: str,
        action_type: str,
        engine: str,
        target: str,
        violations: list[str],
        legal_basis: str,
    ):
        """Broadcast blocked action notification."""
        message = {
            "type": "action_blocked",
            "data": {
                "validation_id": validation_id,
                "action_type": action_type,
                "engine": engine,
                "target": target,
                "violations": violations,
                "legal_basis": legal_basis,
            },
            "timestamp": datetime.utcnow().isoformat(),
        }
        await self._broadcast_to_channel(self.violation_connections, message)
    
    async def broadcast_system_health(
        self,
        overall_status: str,
        total_engines: int,
        healthy_count: int,
        degraded_count: int,
        warning_count: int,
        critical_count: int,
        offline_count: int,
        average_cpu_percent: float,
        average_memory_percent: float,
        average_latency_ms: float,
        active_alerts: int,
        critical_alerts: int,
    ):
        """Broadcast system health update."""
        message = {
            "type": "system_health",
            "data": {
                "overall_status": overall_status,
                "total_engines": total_engines,
                "healthy_count": healthy_count,
                "degraded_count": degraded_count,
                "warning_count": warning_count,
                "critical_count": critical_count,
                "offline_count": offline_count,
                "average_cpu_percent": average_cpu_percent,
                "average_memory_percent": average_memory_percent,
                "average_latency_ms": average_latency_ms,
                "active_alerts": active_alerts,
                "critical_alerts": critical_alerts,
            },
            "timestamp": datetime.utcnow().isoformat(),
        }
        await self._broadcast_to_channel(self.health_connections, message)
    
    async def broadcast_engine_metrics(
        self,
        engine_type: str,
        cpu_percent: float,
        memory_percent: float,
        gpu_percent: float,
        queue_depth: int,
        latency_ms: float,
        error_rate: float,
        status: str,
    ):
        """Broadcast engine metrics update."""
        message = {
            "type": "engine_metrics",
            "data": {
                "engine_type": engine_type,
                "cpu_percent": cpu_percent,
                "memory_percent": memory_percent,
                "gpu_percent": gpu_percent,
                "queue_depth": queue_depth,
                "latency_ms": latency_ms,
                "error_rate": error_rate,
                "status": status,
            },
            "timestamp": datetime.utcnow().isoformat(),
        }
        await self._broadcast_to_channel(self.health_connections, message)
    
    async def broadcast_correction_started(
        self,
        action_id: str,
        correction_type: str,
        target_engine: str,
        target_component: str,
        priority: str,
    ):
        """Broadcast correction action started."""
        message = {
            "type": "correction_started",
            "data": {
                "action_id": action_id,
                "correction_type": correction_type,
                "target_engine": target_engine,
                "target_component": target_component,
                "priority": priority,
            },
            "timestamp": datetime.utcnow().isoformat(),
        }
        await self._broadcast_to_channel(self.health_connections, message)
    
    async def broadcast_correction_completed(
        self,
        action_id: str,
        result_id: str,
        success: bool,
        message_text: str,
        duration_seconds: float,
    ):
        """Broadcast correction action completed."""
        message = {
            "type": "correction_completed",
            "data": {
                "action_id": action_id,
                "result_id": result_id,
                "success": success,
                "message": message_text,
                "duration_seconds": duration_seconds,
            },
            "timestamp": datetime.utcnow().isoformat(),
        }
        await self._broadcast_to_channel(self.health_connections, message)
    
    async def broadcast_feedback_loop_detected(
        self,
        detection_id: str,
        source_engine: str,
        target_engine: str,
        loop_type: str,
        risk_level: str,
        mitigation_strategy: str,
    ):
        """Broadcast feedback loop detection."""
        message = {
            "type": "feedback_loop_detected",
            "data": {
                "detection_id": detection_id,
                "source_engine": source_engine,
                "target_engine": target_engine,
                "loop_type": loop_type,
                "risk_level": risk_level,
                "mitigation_strategy": mitigation_strategy,
            },
            "timestamp": datetime.utcnow().isoformat(),
        }
        await self._broadcast_to_channel(self.health_connections, message)
    
    async def broadcast_overload_prediction(
        self,
        prediction_id: str,
        engine_type: str,
        predicted_overload_time: str,
        confidence: float,
        current_load_percent: float,
        projected_load_percent: float,
        recommended_actions: list[str],
    ):
        """Broadcast overload prediction."""
        message = {
            "type": "overload_prediction",
            "data": {
                "prediction_id": prediction_id,
                "engine_type": engine_type,
                "predicted_overload_time": predicted_overload_time,
                "confidence": confidence,
                "current_load_percent": current_load_percent,
                "projected_load_percent": projected_load_percent,
                "recommended_actions": recommended_actions,
            },
            "timestamp": datetime.utcnow().isoformat(),
        }
        await self._broadcast_to_channel(self.health_connections, message)
    
    async def broadcast_recommendation(
        self,
        recommendation_id: str,
        recommendation_type: str,
        priority: str,
        title: str,
        description: str,
        rationale: str,
        affected_systems: list[str],
        implementation_steps: list[str],
        expected_outcome: str,
        risk_if_ignored: str,
        deadline: Optional[str],
    ):
        """Broadcast a sentinel recommendation."""
        message = {
            "type": "sentinel_recommendation",
            "data": {
                "recommendation_id": recommendation_id,
                "recommendation_type": recommendation_type,
                "priority": priority,
                "title": title,
                "description": description,
                "rationale": rationale,
                "affected_systems": affected_systems,
                "implementation_steps": implementation_steps,
                "expected_outcome": expected_outcome,
                "risk_if_ignored": risk_if_ignored,
                "deadline": deadline,
            },
            "timestamp": datetime.utcnow().isoformat(),
        }
        await self._broadcast_to_channel(self.recommendation_connections, message)
    
    async def broadcast_recommendation_accepted(
        self,
        recommendation_id: str,
    ):
        """Broadcast recommendation acceptance."""
        message = {
            "type": "recommendation_accepted",
            "data": {
                "recommendation_id": recommendation_id,
            },
            "timestamp": datetime.utcnow().isoformat(),
        }
        await self._broadcast_to_channel(self.recommendation_connections, message)
    
    async def broadcast_recommendation_implemented(
        self,
        recommendation_id: str,
    ):
        """Broadcast recommendation implementation."""
        message = {
            "type": "recommendation_implemented",
            "data": {
                "recommendation_id": recommendation_id,
            },
            "timestamp": datetime.utcnow().isoformat(),
        }
        await self._broadcast_to_channel(self.recommendation_connections, message)
    
    async def broadcast_autonomous_action_request(
        self,
        request_id: str,
        source_engine: str,
        action_type: str,
        autonomy_level: int,
        target: str,
        justification: str,
        risk_score: float,
        approval_status: str,
    ):
        """Broadcast autonomous action request."""
        message = {
            "type": "autonomous_action_request",
            "data": {
                "request_id": request_id,
                "source_engine": source_engine,
                "action_type": action_type,
                "autonomy_level": autonomy_level,
                "target": target,
                "justification": justification,
                "risk_score": risk_score,
                "approval_status": approval_status,
            },
            "timestamp": datetime.utcnow().isoformat(),
        }
        await self._broadcast_to_channel(self.recommendation_connections, message)
    
    async def broadcast_cascade_prediction(
        self,
        prediction_id: str,
        trigger_event: str,
        trigger_source: str,
        predicted_outcomes: list[dict],
        probability: float,
        affected_systems: list[str],
        mitigation_options: list[str],
        confidence: float,
    ):
        """Broadcast cascade prediction."""
        message = {
            "type": "cascade_prediction",
            "data": {
                "prediction_id": prediction_id,
                "trigger_event": trigger_event,
                "trigger_source": trigger_source,
                "predicted_outcomes": predicted_outcomes,
                "probability": probability,
                "affected_systems": affected_systems,
                "mitigation_options": mitigation_options,
                "confidence": confidence,
            },
            "timestamp": datetime.utcnow().isoformat(),
        }
        await self._broadcast_to_channel(self.recommendation_connections, message)
    
    async def broadcast_command_staff_alert(
        self,
        alert_id: str,
        priority: str,
        recipient_role: str,
        title: str,
        summary: str,
        required_action: str,
        deadline: Optional[str],
    ):
        """Broadcast command staff alert."""
        message = {
            "type": "command_staff_alert",
            "data": {
                "alert_id": alert_id,
                "priority": priority,
                "recipient_role": recipient_role,
                "title": title,
                "summary": summary,
                "required_action": required_action,
                "deadline": deadline,
            },
            "timestamp": datetime.utcnow().isoformat(),
        }
        await self._broadcast_to_channel(self.alert_connections, message)
        await self._broadcast_to_channel(self.recommendation_connections, message)
    
    async def _broadcast_to_channel(self, connections: list[WebSocket], message: dict):
        """Broadcast message to all connections in a channel."""
        disconnected = []
        for connection in connections:
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.append(connection)
        
        for connection in disconnected:
            if connection in connections:
                connections.remove(connection)
    
    def get_connection_counts(self) -> dict:
        """Get connection counts for all channels."""
        return {
            "alerts": len(self.alert_connections),
            "violations": len(self.violation_connections),
            "system_health": len(self.health_connections),
            "recommendations": len(self.recommendation_connections),
            "total": sum(len(c) for c in self.all_connections.values()),
        }


ai_supervisor_ws_manager = AISupervisorWSManager()


async def handle_alerts_websocket(websocket: WebSocket):
    """Handle WebSocket connection for alerts channel."""
    await ai_supervisor_ws_manager.connect_alerts(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "ping":
                await websocket.send_json({
                    "type": "pong",
                    "timestamp": datetime.utcnow().isoformat(),
                })
            elif message.get("type") == "acknowledge":
                alert_id = message.get("alert_id")
                acknowledged_by = message.get("acknowledged_by", "unknown")
                await ai_supervisor_ws_manager.broadcast_alert_acknowledged(
                    alert_id=alert_id,
                    acknowledged_by=acknowledged_by,
                )
    except WebSocketDisconnect:
        ai_supervisor_ws_manager.disconnect_alerts(websocket)


async def handle_violations_websocket(websocket: WebSocket):
    """Handle WebSocket connection for violations channel."""
    await ai_supervisor_ws_manager.connect_violations(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "ping":
                await websocket.send_json({
                    "type": "pong",
                    "timestamp": datetime.utcnow().isoformat(),
                })
    except WebSocketDisconnect:
        ai_supervisor_ws_manager.disconnect_violations(websocket)


async def handle_health_websocket(websocket: WebSocket):
    """Handle WebSocket connection for system health channel."""
    await ai_supervisor_ws_manager.connect_health(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "ping":
                await websocket.send_json({
                    "type": "pong",
                    "timestamp": datetime.utcnow().isoformat(),
                })
            elif message.get("type") == "request_health":
                await websocket.send_json({
                    "type": "health_requested",
                    "message": "Health data will be sent shortly",
                    "timestamp": datetime.utcnow().isoformat(),
                })
    except WebSocketDisconnect:
        ai_supervisor_ws_manager.disconnect_health(websocket)


async def handle_recommendations_websocket(websocket: WebSocket):
    """Handle WebSocket connection for recommendations channel."""
    await ai_supervisor_ws_manager.connect_recommendations(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "ping":
                await websocket.send_json({
                    "type": "pong",
                    "timestamp": datetime.utcnow().isoformat(),
                })
            elif message.get("type") == "accept_recommendation":
                recommendation_id = message.get("recommendation_id")
                await ai_supervisor_ws_manager.broadcast_recommendation_accepted(
                    recommendation_id=recommendation_id,
                )
    except WebSocketDisconnect:
        ai_supervisor_ws_manager.disconnect_recommendations(websocket)
