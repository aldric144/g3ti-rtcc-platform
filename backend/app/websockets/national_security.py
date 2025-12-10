"""
National Security WebSocket Channels

Provides real-time WebSocket channels for:
- /ws/national-security - Main national security alerts channel
- Sub-channels for cyber, insider, geopolitical, financial, fusion alerts
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Set
from fastapi import WebSocket, WebSocketDisconnect
import json
import asyncio


class NationalSecurityWebSocketManager:
    """
    WebSocket manager for national security alerts and intelligence.
    
    Provides real-time broadcasting of:
    - Security alerts
    - Cyber threat intelligence
    - Insider threat notifications
    - Geopolitical risk updates
    - Financial crime alerts
    - National stability score changes
    - Early warning signals
    """

    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {
            "main": set(),
            "cyber": set(),
            "insider": set(),
            "geopolitical": set(),
            "financial": set(),
            "fusion": set(),
            "alerts": set(),
            "stability": set(),
        }
        self.connection_metadata: Dict[WebSocket, Dict[str, Any]] = {}

    async def connect(
        self,
        websocket: WebSocket,
        channel: str = "main",
        user_id: Optional[str] = None,
        clearance_level: Optional[str] = None,
        roles: Optional[List[str]] = None,
    ) -> bool:
        """Connect a client to a channel."""
        if channel not in self.active_connections:
            return False
        
        await websocket.accept()
        self.active_connections[channel].add(websocket)
        
        self.connection_metadata[websocket] = {
            "channel": channel,
            "user_id": user_id,
            "clearance_level": clearance_level or "unclassified",
            "roles": roles or [],
            "connected_at": datetime.utcnow().isoformat(),
            "subscriptions": [channel],
        }
        
        await self._send_connection_ack(websocket, channel)
        return True

    async def disconnect(self, websocket: WebSocket) -> None:
        """Disconnect a client from all channels."""
        for channel_connections in self.active_connections.values():
            channel_connections.discard(websocket)
        
        if websocket in self.connection_metadata:
            del self.connection_metadata[websocket]

    async def subscribe(self, websocket: WebSocket, channel: str) -> bool:
        """Subscribe a connected client to an additional channel."""
        if channel not in self.active_connections:
            return False
        
        self.active_connections[channel].add(websocket)
        
        if websocket in self.connection_metadata:
            if channel not in self.connection_metadata[websocket]["subscriptions"]:
                self.connection_metadata[websocket]["subscriptions"].append(channel)
        
        return True

    async def unsubscribe(self, websocket: WebSocket, channel: str) -> bool:
        """Unsubscribe a client from a channel."""
        if channel not in self.active_connections:
            return False
        
        self.active_connections[channel].discard(websocket)
        
        if websocket in self.connection_metadata:
            if channel in self.connection_metadata[websocket]["subscriptions"]:
                self.connection_metadata[websocket]["subscriptions"].remove(channel)
        
        return True

    async def _send_connection_ack(self, websocket: WebSocket, channel: str) -> None:
        """Send connection acknowledgment."""
        await websocket.send_json({
            "type": "connection_ack",
            "channel": channel,
            "timestamp": datetime.utcnow().isoformat(),
            "message": f"Connected to national security channel: {channel}",
        })

    async def broadcast_to_channel(
        self,
        channel: str,
        message: Dict[str, Any],
        min_clearance: Optional[str] = None,
        required_roles: Optional[List[str]] = None,
    ) -> int:
        """Broadcast a message to all clients in a channel."""
        if channel not in self.active_connections:
            return 0
        
        sent_count = 0
        disconnected = []
        
        for websocket in self.active_connections[channel]:
            if not self._check_access(websocket, min_clearance, required_roles):
                continue
            
            try:
                await websocket.send_json(message)
                sent_count += 1
            except Exception:
                disconnected.append(websocket)
        
        for ws in disconnected:
            await self.disconnect(ws)
        
        return sent_count

    def _check_access(
        self,
        websocket: WebSocket,
        min_clearance: Optional[str],
        required_roles: Optional[List[str]],
    ) -> bool:
        """Check if a client has access to receive a message."""
        if not min_clearance and not required_roles:
            return True
        
        metadata = self.connection_metadata.get(websocket, {})
        
        if min_clearance:
            clearance_levels = ["unclassified", "confidential", "secret", "top_secret", "sci"]
            client_clearance = metadata.get("clearance_level", "unclassified")
            
            if clearance_levels.index(client_clearance) < clearance_levels.index(min_clearance):
                return False
        
        if required_roles:
            client_roles = metadata.get("roles", [])
            if not any(role in client_roles for role in required_roles):
                return False
        
        return True

    async def broadcast_security_alert(
        self,
        alert_id: str,
        title: str,
        description: str,
        priority: str,
        category: str,
        risk_score: float,
        destinations: List[str],
        escalation_level: str,
    ) -> int:
        """Broadcast a security alert to relevant channels."""
        message = {
            "type": "security_alert",
            "alert_id": alert_id,
            "title": title,
            "description": description,
            "priority": priority,
            "category": category,
            "risk_score": risk_score,
            "destinations": destinations,
            "escalation_level": escalation_level,
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        sent_count = await self.broadcast_to_channel("main", message)
        sent_count += await self.broadcast_to_channel("alerts", message)
        
        category_channel_map = {
            "cyber_threat": "cyber",
            "insider_threat": "insider",
            "geopolitical": "geopolitical",
            "financial_crime": "financial",
            "national_stability": "fusion",
            "early_warning": "fusion",
        }
        
        if category in category_channel_map:
            sent_count += await self.broadcast_to_channel(
                category_channel_map[category], message
            )
        
        return sent_count

    async def broadcast_cyber_threat(
        self,
        threat_type: str,
        threat_id: str,
        name: str,
        severity: str,
        threat_score: float,
        details: Dict[str, Any],
    ) -> int:
        """Broadcast a cyber threat notification."""
        message = {
            "type": "cyber_threat",
            "threat_type": threat_type,
            "threat_id": threat_id,
            "name": name,
            "severity": severity,
            "threat_score": threat_score,
            "details": details,
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        sent_count = await self.broadcast_to_channel("cyber", message)
        sent_count += await self.broadcast_to_channel("main", message)
        
        return sent_count

    async def broadcast_insider_threat(
        self,
        threat_type: str,
        employee_id: str,
        risk_level: str,
        risk_score: float,
        description: str,
        details: Dict[str, Any],
    ) -> int:
        """Broadcast an insider threat notification."""
        message = {
            "type": "insider_threat",
            "threat_type": threat_type,
            "employee_id": employee_id,
            "risk_level": risk_level,
            "risk_score": risk_score,
            "description": description,
            "details": details,
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        sent_count = await self.broadcast_to_channel(
            "insider", message,
            required_roles=["insider_threat_analyst", "security_admin", "chief"]
        )
        sent_count += await self.broadcast_to_channel("main", message)
        
        return sent_count

    async def broadcast_geopolitical_update(
        self,
        update_type: str,
        event_id: str,
        title: str,
        severity: float,
        region: str,
        details: Dict[str, Any],
    ) -> int:
        """Broadcast a geopolitical risk update."""
        message = {
            "type": "geopolitical_update",
            "update_type": update_type,
            "event_id": event_id,
            "title": title,
            "severity": severity,
            "region": region,
            "details": details,
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        sent_count = await self.broadcast_to_channel("geopolitical", message)
        sent_count += await self.broadcast_to_channel("main", message)
        
        return sent_count

    async def broadcast_financial_crime_alert(
        self,
        alert_type: str,
        alert_id: str,
        fraud_type: str,
        risk_score: float,
        amount: float,
        currency: str,
        details: Dict[str, Any],
    ) -> int:
        """Broadcast a financial crime alert."""
        message = {
            "type": "financial_crime_alert",
            "alert_type": alert_type,
            "alert_id": alert_id,
            "fraud_type": fraud_type,
            "risk_score": risk_score,
            "amount": amount,
            "currency": currency,
            "details": details,
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        sent_count = await self.broadcast_to_channel("financial", message)
        sent_count += await self.broadcast_to_channel("main", message)
        
        return sent_count

    async def broadcast_stability_score_update(
        self,
        assessment_id: str,
        overall_score: float,
        stability_level: str,
        trend: str,
        key_drivers: List[str],
        forecasts: Dict[str, float],
    ) -> int:
        """Broadcast a national stability score update."""
        message = {
            "type": "stability_score_update",
            "assessment_id": assessment_id,
            "overall_score": overall_score,
            "stability_level": stability_level,
            "trend": trend,
            "key_drivers": key_drivers,
            "forecasts": forecasts,
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        sent_count = await self.broadcast_to_channel("stability", message)
        sent_count += await self.broadcast_to_channel("fusion", message)
        sent_count += await self.broadcast_to_channel("main", message)
        
        return sent_count

    async def broadcast_early_warning(
        self,
        signal_id: str,
        title: str,
        urgency: str,
        risk_score: float,
        probability: float,
        time_horizon_hours: int,
        domains_affected: List[str],
        recommended_actions: List[str],
    ) -> int:
        """Broadcast an early warning signal."""
        message = {
            "type": "early_warning",
            "signal_id": signal_id,
            "title": title,
            "urgency": urgency,
            "risk_score": risk_score,
            "probability": probability,
            "time_horizon_hours": time_horizon_hours,
            "domains_affected": domains_affected,
            "recommended_actions": recommended_actions,
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        sent_count = await self.broadcast_to_channel("fusion", message)
        sent_count += await self.broadcast_to_channel("main", message)
        
        if urgency in ["flash", "emergency"]:
            sent_count += await self.broadcast_to_channel("alerts", message)
        
        return sent_count

    async def broadcast_alert_status_change(
        self,
        alert_id: str,
        new_status: str,
        changed_by: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> int:
        """Broadcast an alert status change."""
        message = {
            "type": "alert_status_change",
            "alert_id": alert_id,
            "new_status": new_status,
            "changed_by": changed_by,
            "details": details or {},
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        sent_count = await self.broadcast_to_channel("alerts", message)
        sent_count += await self.broadcast_to_channel("main", message)
        
        return sent_count

    def get_connection_stats(self) -> Dict[str, Any]:
        """Get connection statistics."""
        stats = {
            "total_connections": len(self.connection_metadata),
            "channels": {},
        }
        
        for channel, connections in self.active_connections.items():
            stats["channels"][channel] = len(connections)
        
        return stats

    def get_channel_subscribers(self, channel: str) -> List[Dict[str, Any]]:
        """Get list of subscribers for a channel."""
        if channel not in self.active_connections:
            return []
        
        subscribers = []
        for ws in self.active_connections[channel]:
            metadata = self.connection_metadata.get(ws, {})
            subscribers.append({
                "user_id": metadata.get("user_id"),
                "clearance_level": metadata.get("clearance_level"),
                "roles": metadata.get("roles"),
                "connected_at": metadata.get("connected_at"),
            })
        
        return subscribers


ws_manager = NationalSecurityWebSocketManager()


async def handle_national_security_websocket(
    websocket: WebSocket,
    channel: str = "main",
    user_id: Optional[str] = None,
    clearance_level: Optional[str] = None,
):
    """Handle WebSocket connections for national security channels."""
    roles = []
    
    connected = await ws_manager.connect(
        websocket,
        channel=channel,
        user_id=user_id,
        clearance_level=clearance_level,
        roles=roles,
    )
    
    if not connected:
        await websocket.close(code=4000, reason="Invalid channel")
        return
    
    try:
        while True:
            data = await websocket.receive_json()
            
            if data.get("action") == "subscribe":
                target_channel = data.get("channel")
                if target_channel:
                    success = await ws_manager.subscribe(websocket, target_channel)
                    await websocket.send_json({
                        "type": "subscription_result",
                        "channel": target_channel,
                        "success": success,
                    })
            
            elif data.get("action") == "unsubscribe":
                target_channel = data.get("channel")
                if target_channel:
                    success = await ws_manager.unsubscribe(websocket, target_channel)
                    await websocket.send_json({
                        "type": "unsubscription_result",
                        "channel": target_channel,
                        "success": success,
                    })
            
            elif data.get("action") == "ping":
                await websocket.send_json({
                    "type": "pong",
                    "timestamp": datetime.utcnow().isoformat(),
                })
            
            elif data.get("action") == "get_stats":
                stats = ws_manager.get_connection_stats()
                await websocket.send_json({
                    "type": "stats",
                    "data": stats,
                })
    
    except WebSocketDisconnect:
        await ws_manager.disconnect(websocket)
    except Exception:
        await ws_manager.disconnect(websocket)
