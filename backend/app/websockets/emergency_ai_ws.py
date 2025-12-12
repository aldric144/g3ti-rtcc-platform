"""
Phase 31: Emergency AI WebSocket Channels

WebSocket channels:
- /ws/emergency-ai/hazards - Hazard updates
- /ws/emergency-ai/evac - Evacuation orders
- /ws/emergency-ai/resources - Resource availability
- /ws/emergency-ai/recovery - Damage assessments and recovery updates
"""

from datetime import datetime
from typing import Dict, List, Set, Optional, Any
from fastapi import WebSocket, WebSocketDisconnect
import json
import asyncio
import uuid


class EmergencyAIConnectionManager:
    """
    Manages WebSocket connections for Emergency AI channels.
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
        
        self.hazards_connections: List[WebSocket] = []
        self.evac_connections: List[WebSocket] = []
        self.resources_connections: List[WebSocket] = []
        self.recovery_connections: List[WebSocket] = []
        
        self.connection_metadata: Dict[WebSocket, Dict[str, Any]] = {}
        
        self.statistics = {
            "total_connections": 0,
            "hazards_messages_sent": 0,
            "evac_messages_sent": 0,
            "resources_messages_sent": 0,
            "recovery_messages_sent": 0,
        }
    
    async def connect_hazards(self, websocket: WebSocket) -> None:
        """Connect to hazards channel."""
        await websocket.accept()
        self.hazards_connections.append(websocket)
        self.connection_metadata[websocket] = {
            "channel": "hazards",
            "connected_at": datetime.utcnow().isoformat(),
            "connection_id": f"HAZ-{uuid.uuid4().hex[:8].upper()}",
        }
        self.statistics["total_connections"] += 1
        
        await websocket.send_json({
            "type": "connection_established",
            "channel": "hazards",
            "connection_id": self.connection_metadata[websocket]["connection_id"],
            "timestamp": datetime.utcnow().isoformat(),
            "message": "Connected to Emergency AI Hazards channel",
        })
    
    async def connect_evac(self, websocket: WebSocket) -> None:
        """Connect to evacuation channel."""
        await websocket.accept()
        self.evac_connections.append(websocket)
        self.connection_metadata[websocket] = {
            "channel": "evac",
            "connected_at": datetime.utcnow().isoformat(),
            "connection_id": f"EVAC-{uuid.uuid4().hex[:8].upper()}",
        }
        self.statistics["total_connections"] += 1
        
        await websocket.send_json({
            "type": "connection_established",
            "channel": "evac",
            "connection_id": self.connection_metadata[websocket]["connection_id"],
            "timestamp": datetime.utcnow().isoformat(),
            "message": "Connected to Emergency AI Evacuation channel",
        })
    
    async def connect_resources(self, websocket: WebSocket) -> None:
        """Connect to resources channel."""
        await websocket.accept()
        self.resources_connections.append(websocket)
        self.connection_metadata[websocket] = {
            "channel": "resources",
            "connected_at": datetime.utcnow().isoformat(),
            "connection_id": f"RES-{uuid.uuid4().hex[:8].upper()}",
        }
        self.statistics["total_connections"] += 1
        
        await websocket.send_json({
            "type": "connection_established",
            "channel": "resources",
            "connection_id": self.connection_metadata[websocket]["connection_id"],
            "timestamp": datetime.utcnow().isoformat(),
            "message": "Connected to Emergency AI Resources channel",
        })
    
    async def connect_recovery(self, websocket: WebSocket) -> None:
        """Connect to recovery channel."""
        await websocket.accept()
        self.recovery_connections.append(websocket)
        self.connection_metadata[websocket] = {
            "channel": "recovery",
            "connected_at": datetime.utcnow().isoformat(),
            "connection_id": f"REC-{uuid.uuid4().hex[:8].upper()}",
        }
        self.statistics["total_connections"] += 1
        
        await websocket.send_json({
            "type": "connection_established",
            "channel": "recovery",
            "connection_id": self.connection_metadata[websocket]["connection_id"],
            "timestamp": datetime.utcnow().isoformat(),
            "message": "Connected to Emergency AI Recovery channel",
        })
    
    def disconnect(self, websocket: WebSocket) -> None:
        """Disconnect from any channel."""
        if websocket in self.hazards_connections:
            self.hazards_connections.remove(websocket)
        if websocket in self.evac_connections:
            self.evac_connections.remove(websocket)
        if websocket in self.resources_connections:
            self.resources_connections.remove(websocket)
        if websocket in self.recovery_connections:
            self.recovery_connections.remove(websocket)
        if websocket in self.connection_metadata:
            del self.connection_metadata[websocket]
    
    async def broadcast_hazard_update(
        self,
        hazard_id: str,
        hazard_type: str,
        threat_level: int,
        affected_zones: List[str],
        time_to_impact_hours: float,
        recommended_actions: List[str],
        confidence_score: float,
    ) -> None:
        """Broadcast hazard update to all hazards channel subscribers."""
        message = {
            "type": "hazard_update",
            "timestamp": datetime.utcnow().isoformat(),
            "hazard_id": hazard_id,
            "hazard_type": hazard_type,
            "threat_level": threat_level,
            "affected_zones": affected_zones,
            "time_to_impact_hours": time_to_impact_hours,
            "recommended_actions": recommended_actions,
            "confidence_score": confidence_score,
        }
        
        disconnected = []
        for connection in self.hazards_connections:
            try:
                await connection.send_json(message)
                self.statistics["hazards_messages_sent"] += 1
            except Exception:
                disconnected.append(connection)
        
        for conn in disconnected:
            self.disconnect(conn)
    
    async def broadcast_hazard_alert(
        self,
        alert_id: str,
        alert_type: str,
        priority: int,
        title: str,
        message_text: str,
        affected_zones: List[str],
        agencies_required: List[str],
    ) -> None:
        """Broadcast hazard alert to all hazards channel subscribers."""
        message = {
            "type": "hazard_alert",
            "timestamp": datetime.utcnow().isoformat(),
            "alert_id": alert_id,
            "alert_type": alert_type,
            "priority": priority,
            "title": title,
            "message": message_text,
            "affected_zones": affected_zones,
            "agencies_required": agencies_required,
        }
        
        disconnected = []
        for connection in self.hazards_connections:
            try:
                await connection.send_json(message)
                self.statistics["hazards_messages_sent"] += 1
            except Exception:
                disconnected.append(connection)
        
        for conn in disconnected:
            self.disconnect(conn)
    
    async def broadcast_evacuation_order(
        self,
        order_id: str,
        order_type: str,
        affected_zones: List[str],
        evacuation_routes: List[Dict[str, Any]],
        shelters: List[Dict[str, Any]],
        effective_time: str,
        expiration_time: Optional[str],
    ) -> None:
        """Broadcast evacuation order to all evac channel subscribers."""
        message = {
            "type": "evacuation_order",
            "timestamp": datetime.utcnow().isoformat(),
            "order_id": order_id,
            "order_type": order_type,
            "affected_zones": affected_zones,
            "evacuation_routes": evacuation_routes,
            "shelters": shelters,
            "effective_time": effective_time,
            "expiration_time": expiration_time,
        }
        
        disconnected = []
        for connection in self.evac_connections:
            try:
                await connection.send_json(message)
                self.statistics["evac_messages_sent"] += 1
            except Exception:
                disconnected.append(connection)
        
        for conn in disconnected:
            self.disconnect(conn)
    
    async def broadcast_road_closure(
        self,
        closure_id: str,
        road_name: str,
        reason: str,
        affected_zones: List[str],
        alternate_routes: List[str],
        estimated_reopening: Optional[str],
    ) -> None:
        """Broadcast road closure to all evac channel subscribers."""
        message = {
            "type": "road_closure",
            "timestamp": datetime.utcnow().isoformat(),
            "closure_id": closure_id,
            "road_name": road_name,
            "reason": reason,
            "affected_zones": affected_zones,
            "alternate_routes": alternate_routes,
            "estimated_reopening": estimated_reopening,
        }
        
        disconnected = []
        for connection in self.evac_connections:
            try:
                await connection.send_json(message)
                self.statistics["evac_messages_sent"] += 1
            except Exception:
                disconnected.append(connection)
        
        for conn in disconnected:
            self.disconnect(conn)
    
    async def broadcast_resource_update(
        self,
        resource_type: str,
        resource_id: str,
        status: str,
        zone: str,
        capacity: int,
        utilization_percent: float,
    ) -> None:
        """Broadcast resource update to all resources channel subscribers."""
        message = {
            "type": "resource_update",
            "timestamp": datetime.utcnow().isoformat(),
            "resource_type": resource_type,
            "resource_id": resource_id,
            "status": status,
            "zone": zone,
            "capacity": capacity,
            "utilization_percent": utilization_percent,
        }
        
        disconnected = []
        for connection in self.resources_connections:
            try:
                await connection.send_json(message)
                self.statistics["resources_messages_sent"] += 1
            except Exception:
                disconnected.append(connection)
        
        for conn in disconnected:
            self.disconnect(conn)
    
    async def broadcast_shelter_update(
        self,
        shelter_id: str,
        shelter_name: str,
        status: str,
        capacity: int,
        current_occupancy: int,
        amenities: List[str],
    ) -> None:
        """Broadcast shelter update to all resources channel subscribers."""
        message = {
            "type": "shelter_update",
            "timestamp": datetime.utcnow().isoformat(),
            "shelter_id": shelter_id,
            "shelter_name": shelter_name,
            "status": status,
            "capacity": capacity,
            "current_occupancy": current_occupancy,
            "available_capacity": capacity - current_occupancy,
            "occupancy_percent": (current_occupancy / capacity * 100) if capacity > 0 else 0,
            "amenities": amenities,
        }
        
        disconnected = []
        for connection in self.resources_connections:
            try:
                await connection.send_json(message)
                self.statistics["resources_messages_sent"] += 1
            except Exception:
                disconnected.append(connection)
        
        for conn in disconnected:
            self.disconnect(conn)
    
    async def broadcast_damage_assessment(
        self,
        assessment_id: str,
        zone: str,
        incident_type: str,
        disaster_impact_index: float,
        structures_damaged: int,
        displaced_residents: int,
        priority_repairs: List[str],
    ) -> None:
        """Broadcast damage assessment to all recovery channel subscribers."""
        message = {
            "type": "damage_assessment",
            "timestamp": datetime.utcnow().isoformat(),
            "assessment_id": assessment_id,
            "zone": zone,
            "incident_type": incident_type,
            "disaster_impact_index": disaster_impact_index,
            "structures_damaged": structures_damaged,
            "displaced_residents": displaced_residents,
            "priority_repairs": priority_repairs,
        }
        
        disconnected = []
        for connection in self.recovery_connections:
            try:
                await connection.send_json(message)
                self.statistics["recovery_messages_sent"] += 1
            except Exception:
                disconnected.append(connection)
        
        for conn in disconnected:
            self.disconnect(conn)
    
    async def broadcast_recovery_update(
        self,
        update_id: str,
        zone: str,
        recovery_phase: str,
        progress_percent: float,
        milestones_completed: List[str],
        next_milestone: str,
        estimated_completion_date: str,
    ) -> None:
        """Broadcast recovery update to all recovery channel subscribers."""
        message = {
            "type": "recovery_update",
            "timestamp": datetime.utcnow().isoformat(),
            "update_id": update_id,
            "zone": zone,
            "recovery_phase": recovery_phase,
            "progress_percent": progress_percent,
            "milestones_completed": milestones_completed,
            "next_milestone": next_milestone,
            "estimated_completion_date": estimated_completion_date,
        }
        
        disconnected = []
        for connection in self.recovery_connections:
            try:
                await connection.send_json(message)
                self.statistics["recovery_messages_sent"] += 1
            except Exception:
                disconnected.append(connection)
        
        for conn in disconnected:
            self.disconnect(conn)
    
    async def send_heartbeat(self, websocket: WebSocket) -> None:
        """Send heartbeat to a specific connection."""
        try:
            await websocket.send_json({
                "type": "heartbeat",
                "timestamp": datetime.utcnow().isoformat(),
            })
        except Exception:
            self.disconnect(websocket)
    
    def get_connection_count(self, channel: Optional[str] = None) -> int:
        """Get connection count for a channel or all channels."""
        if channel == "hazards":
            return len(self.hazards_connections)
        elif channel == "evac":
            return len(self.evac_connections)
        elif channel == "resources":
            return len(self.resources_connections)
        elif channel == "recovery":
            return len(self.recovery_connections)
        else:
            return (
                len(self.hazards_connections) +
                len(self.evac_connections) +
                len(self.resources_connections) +
                len(self.recovery_connections)
            )
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get WebSocket statistics."""
        return {
            **self.statistics,
            "current_hazards_connections": len(self.hazards_connections),
            "current_evac_connections": len(self.evac_connections),
            "current_resources_connections": len(self.resources_connections),
            "current_recovery_connections": len(self.recovery_connections),
            "total_current_connections": self.get_connection_count(),
        }


manager = EmergencyAIConnectionManager()


async def websocket_hazards_endpoint(websocket: WebSocket) -> None:
    """WebSocket endpoint for hazards channel."""
    await manager.connect_hazards(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                if message.get("type") == "ping":
                    await manager.send_heartbeat(websocket)
            except json.JSONDecodeError:
                pass
    except WebSocketDisconnect:
        manager.disconnect(websocket)


async def websocket_evac_endpoint(websocket: WebSocket) -> None:
    """WebSocket endpoint for evacuation channel."""
    await manager.connect_evac(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                if message.get("type") == "ping":
                    await manager.send_heartbeat(websocket)
            except json.JSONDecodeError:
                pass
    except WebSocketDisconnect:
        manager.disconnect(websocket)


async def websocket_resources_endpoint(websocket: WebSocket) -> None:
    """WebSocket endpoint for resources channel."""
    await manager.connect_resources(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                if message.get("type") == "ping":
                    await manager.send_heartbeat(websocket)
            except json.JSONDecodeError:
                pass
    except WebSocketDisconnect:
        manager.disconnect(websocket)


async def websocket_recovery_endpoint(websocket: WebSocket) -> None:
    """WebSocket endpoint for recovery channel."""
    await manager.connect_recovery(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                if message.get("type") == "ping":
                    await manager.send_heartbeat(websocket)
            except json.JSONDecodeError:
                pass
    except WebSocketDisconnect:
        manager.disconnect(websocket)
