"""
Phase 30: Human Intel WebSocket Channels

WebSocket channels for Human Stability Intelligence Engine:
- /ws/human-intel/crisis-alerts
- /ws/human-intel/stability
- /ws/human-intel/dv-risk
- /ws/human-intel/suicide
- /ws/human-intel/youth

Agency: Riviera Beach Police Department (ORI: FL0500400)
"""

from datetime import datetime
from typing import Dict, List, Optional, Any, Set
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import asyncio
import json

router = APIRouter()


class HumanIntelConnectionManager:
    """
    Manages WebSocket connections for Human Intel channels
    
    Channels:
    - crisis_alerts: Crisis escalation warnings
    - stability: Community stability updates
    - dv_risk: DV lethality red flags
    - suicide: Suicide ideation alerts
    - youth: Youth instability clusters
    """
    
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {
            "crisis_alerts": [],
            "stability": [],
            "dv_risk": [],
            "suicide": [],
            "youth": [],
        }
        self.connection_metadata: Dict[WebSocket, Dict[str, Any]] = {}
    
    async def connect(
        self,
        websocket: WebSocket,
        channel: str,
        user_id: Optional[str] = None,
    ):
        """Connect a client to a channel"""
        await websocket.accept()
        
        if channel not in self.active_connections:
            self.active_connections[channel] = []
        
        self.active_connections[channel].append(websocket)
        self.connection_metadata[websocket] = {
            "channel": channel,
            "user_id": user_id,
            "connected_at": datetime.utcnow().isoformat(),
        }
    
    def disconnect(self, websocket: WebSocket, channel: str):
        """Disconnect a client from a channel"""
        if channel in self.active_connections:
            if websocket in self.active_connections[channel]:
                self.active_connections[channel].remove(websocket)
        
        if websocket in self.connection_metadata:
            del self.connection_metadata[websocket]
    
    async def broadcast(self, channel: str, message: Dict[str, Any]):
        """Broadcast a message to all clients on a channel"""
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
    
    async def send_personal(
        self,
        websocket: WebSocket,
        message: Dict[str, Any],
    ):
        """Send a message to a specific client"""
        try:
            await websocket.send_json(message)
        except Exception:
            pass
    
    def get_connection_count(self, channel: str) -> int:
        """Get the number of connections on a channel"""
        return len(self.active_connections.get(channel, []))


manager = HumanIntelConnectionManager()


@router.websocket("/ws/human-intel/crisis-alerts")
async def crisis_alerts_websocket(websocket: WebSocket):
    """
    Crisis Alerts WebSocket Channel
    
    Pushes:
    - Crisis escalation warnings
    - Mental health emergencies
    - Immediate danger alerts
    """
    await manager.connect(websocket, "crisis_alerts")
    
    try:
        await manager.send_personal(websocket, {
            "type": "connection_established",
            "channel": "crisis_alerts",
            "timestamp": datetime.utcnow().isoformat(),
            "message": "Connected to crisis alerts channel",
        })
        
        while True:
            try:
                data = await asyncio.wait_for(
                    websocket.receive_json(),
                    timeout=30.0
                )
                
                if data.get("type") == "ping":
                    await manager.send_personal(websocket, {
                        "type": "pong",
                        "timestamp": datetime.utcnow().isoformat(),
                    })
                elif data.get("type") == "subscribe_zone":
                    zone = data.get("zone")
                    await manager.send_personal(websocket, {
                        "type": "subscribed",
                        "zone": zone,
                        "timestamp": datetime.utcnow().isoformat(),
                    })
                    
            except asyncio.TimeoutError:
                await manager.send_personal(websocket, {
                    "type": "heartbeat",
                    "timestamp": datetime.utcnow().isoformat(),
                })
                
    except WebSocketDisconnect:
        manager.disconnect(websocket, "crisis_alerts")


@router.websocket("/ws/human-intel/stability")
async def stability_websocket(websocket: WebSocket):
    """
    Stability WebSocket Channel
    
    Pushes:
    - Community stability updates
    - Trauma wave alerts
    - Stability index changes
    """
    await manager.connect(websocket, "stability")
    
    try:
        await manager.send_personal(websocket, {
            "type": "connection_established",
            "channel": "stability",
            "timestamp": datetime.utcnow().isoformat(),
            "message": "Connected to stability channel",
        })
        
        while True:
            try:
                data = await asyncio.wait_for(
                    websocket.receive_json(),
                    timeout=30.0
                )
                
                if data.get("type") == "ping":
                    await manager.send_personal(websocket, {
                        "type": "pong",
                        "timestamp": datetime.utcnow().isoformat(),
                    })
                elif data.get("type") == "get_current_stability":
                    from backend.app.human_intel.behavioral_crisis_engine import BehavioralCrisisEngine
                    engine = BehavioralCrisisEngine()
                    index = engine.get_stability_index()
                    await manager.send_personal(websocket, {
                        "type": "stability_update",
                        "stability_index": index.overall_score,
                        "timestamp": datetime.utcnow().isoformat(),
                    })
                    
            except asyncio.TimeoutError:
                await manager.send_personal(websocket, {
                    "type": "heartbeat",
                    "timestamp": datetime.utcnow().isoformat(),
                })
                
    except WebSocketDisconnect:
        manager.disconnect(websocket, "stability")


@router.websocket("/ws/human-intel/dv-risk")
async def dv_risk_websocket(websocket: WebSocket):
    """
    DV Risk WebSocket Channel
    
    Pushes:
    - DV lethality red flags
    - High-risk DV alerts
    - Repeat DV patterns
    """
    await manager.connect(websocket, "dv_risk")
    
    try:
        await manager.send_personal(websocket, {
            "type": "connection_established",
            "channel": "dv_risk",
            "timestamp": datetime.utcnow().isoformat(),
            "message": "Connected to DV risk channel",
        })
        
        while True:
            try:
                data = await asyncio.wait_for(
                    websocket.receive_json(),
                    timeout=30.0
                )
                
                if data.get("type") == "ping":
                    await manager.send_personal(websocket, {
                        "type": "pong",
                        "timestamp": datetime.utcnow().isoformat(),
                    })
                    
            except asyncio.TimeoutError:
                await manager.send_personal(websocket, {
                    "type": "heartbeat",
                    "timestamp": datetime.utcnow().isoformat(),
                })
                
    except WebSocketDisconnect:
        manager.disconnect(websocket, "dv_risk")


@router.websocket("/ws/human-intel/suicide")
async def suicide_websocket(websocket: WebSocket):
    """
    Suicide Alert WebSocket Channel
    
    Pushes:
    - Suicide ideation alerts
    - High-risk suicide assessments
    - Immediate danger notifications
    """
    await manager.connect(websocket, "suicide")
    
    try:
        await manager.send_personal(websocket, {
            "type": "connection_established",
            "channel": "suicide",
            "timestamp": datetime.utcnow().isoformat(),
            "message": "Connected to suicide alert channel",
        })
        
        while True:
            try:
                data = await asyncio.wait_for(
                    websocket.receive_json(),
                    timeout=30.0
                )
                
                if data.get("type") == "ping":
                    await manager.send_personal(websocket, {
                        "type": "pong",
                        "timestamp": datetime.utcnow().isoformat(),
                    })
                    
            except asyncio.TimeoutError:
                await manager.send_personal(websocket, {
                    "type": "heartbeat",
                    "timestamp": datetime.utcnow().isoformat(),
                })
                
    except WebSocketDisconnect:
        manager.disconnect(websocket, "suicide")


@router.websocket("/ws/human-intel/youth")
async def youth_websocket(websocket: WebSocket):
    """
    Youth Crisis WebSocket Channel
    
    Pushes:
    - Youth instability clusters
    - School incident alerts
    - Gang exposure warnings
    """
    await manager.connect(websocket, "youth")
    
    try:
        await manager.send_personal(websocket, {
            "type": "connection_established",
            "channel": "youth",
            "timestamp": datetime.utcnow().isoformat(),
            "message": "Connected to youth crisis channel",
        })
        
        while True:
            try:
                data = await asyncio.wait_for(
                    websocket.receive_json(),
                    timeout=30.0
                )
                
                if data.get("type") == "ping":
                    await manager.send_personal(websocket, {
                        "type": "pong",
                        "timestamp": datetime.utcnow().isoformat(),
                    })
                elif data.get("type") == "get_youth_stability":
                    from backend.app.human_intel.youth_crisis_engine import YouthCrisisEngine
                    engine = YouthCrisisEngine()
                    stability_map = engine.get_youth_stability_map()
                    await manager.send_personal(websocket, {
                        "type": "youth_stability_update",
                        "data": stability_map,
                        "timestamp": datetime.utcnow().isoformat(),
                    })
                    
            except asyncio.TimeoutError:
                await manager.send_personal(websocket, {
                    "type": "heartbeat",
                    "timestamp": datetime.utcnow().isoformat(),
                })
                
    except WebSocketDisconnect:
        manager.disconnect(websocket, "youth")


async def broadcast_crisis_alert(alert_data: Dict[str, Any]):
    """Broadcast a crisis alert to all connected clients"""
    message = {
        "type": "crisis_alert",
        "data": alert_data,
        "timestamp": datetime.utcnow().isoformat(),
        "priority": alert_data.get("priority", "HIGH"),
    }
    await manager.broadcast("crisis_alerts", message)


async def broadcast_stability_update(stability_data: Dict[str, Any]):
    """Broadcast a stability update to all connected clients"""
    message = {
        "type": "stability_update",
        "data": stability_data,
        "timestamp": datetime.utcnow().isoformat(),
    }
    await manager.broadcast("stability", message)


async def broadcast_dv_alert(dv_data: Dict[str, Any]):
    """Broadcast a DV risk alert to all connected clients"""
    message = {
        "type": "dv_risk_alert",
        "data": dv_data,
        "timestamp": datetime.utcnow().isoformat(),
        "lethality_level": dv_data.get("lethality_level", "UNKNOWN"),
    }
    await manager.broadcast("dv_risk", message)


async def broadcast_suicide_alert(suicide_data: Dict[str, Any]):
    """Broadcast a suicide alert to all connected clients"""
    message = {
        "type": "suicide_alert",
        "data": suicide_data,
        "timestamp": datetime.utcnow().isoformat(),
        "risk_level": suicide_data.get("risk_level", "UNKNOWN"),
    }
    await manager.broadcast("suicide", message)


async def broadcast_youth_alert(youth_data: Dict[str, Any]):
    """Broadcast a youth crisis alert to all connected clients"""
    message = {
        "type": "youth_crisis_alert",
        "data": youth_data,
        "timestamp": datetime.utcnow().isoformat(),
    }
    await manager.broadcast("youth", message)
