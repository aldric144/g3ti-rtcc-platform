"""
Phase 21: Emergency Management WebSocket Channels

Real-time WebSocket channels for:
- /ws/emergency/crisis - Crisis alerts and updates
- /ws/emergency/evac - Evacuation status and routes
- /ws/emergency/resources - Resource logistics updates
- /ws/emergency/medical - Medical surge updates
- /ws/emergency/incidents - Incident command updates
- /ws/emergency/damage - Damage assessment updates
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set
import asyncio
import json
import uuid


class EmergencyChannelType(Enum):
    CRISIS = "crisis"
    EVAC = "evac"
    RESOURCES = "resources"
    MEDICAL = "medical"
    INCIDENTS = "incidents"
    DAMAGE = "damage"


class MessageType(Enum):
    ALERT = "alert"
    UPDATE = "update"
    STATUS = "status"
    NOTIFICATION = "notification"
    COMMAND = "command"
    BROADCAST = "broadcast"


@dataclass
class WebSocketConnection:
    connection_id: str
    channel: EmergencyChannelType
    user_id: Optional[str]
    subscriptions: Set[str]
    connected_at: datetime
    last_activity: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ChannelMessage:
    message_id: str
    channel: EmergencyChannelType
    message_type: MessageType
    payload: Dict[str, Any]
    sender: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    priority: int = 0
    target_subscriptions: Optional[List[str]] = None


class CrisisChannel:
    """
    WebSocket channel for crisis alerts and updates.
    Broadcasts storm, flood, fire, earthquake, and explosion alerts.
    """

    def __init__(self):
        self._connections: Dict[str, WebSocketConnection] = {}
        self._message_handlers: List[Callable] = []
        self._message_history: List[ChannelMessage] = []

    async def connect(
        self,
        connection_id: str,
        user_id: Optional[str] = None,
        subscriptions: Optional[Set[str]] = None,
    ) -> WebSocketConnection:
        """Connect to the crisis channel."""
        connection = WebSocketConnection(
            connection_id=connection_id,
            channel=EmergencyChannelType.CRISIS,
            user_id=user_id,
            subscriptions=subscriptions or {"all"},
            connected_at=datetime.utcnow(),
            last_activity=datetime.utcnow(),
        )
        self._connections[connection_id] = connection
        return connection

    async def disconnect(self, connection_id: str) -> None:
        """Disconnect from the crisis channel."""
        if connection_id in self._connections:
            del self._connections[connection_id]

    async def broadcast_alert(
        self,
        alert_type: str,
        alert_data: Dict[str, Any],
        priority: int = 0,
    ) -> ChannelMessage:
        """Broadcast a crisis alert to all connections."""
        message = ChannelMessage(
            message_id=f"msg-{uuid.uuid4().hex[:8]}",
            channel=EmergencyChannelType.CRISIS,
            message_type=MessageType.ALERT,
            payload={
                "alert_type": alert_type,
                "data": alert_data,
            },
            sender="crisis_engine",
            priority=priority,
        )

        self._message_history.append(message)
        await self._dispatch_message(message)
        return message

    async def broadcast_update(
        self,
        update_type: str,
        update_data: Dict[str, Any],
    ) -> ChannelMessage:
        """Broadcast a crisis update."""
        message = ChannelMessage(
            message_id=f"msg-{uuid.uuid4().hex[:8]}",
            channel=EmergencyChannelType.CRISIS,
            message_type=MessageType.UPDATE,
            payload={
                "update_type": update_type,
                "data": update_data,
            },
            sender="crisis_engine",
        )

        self._message_history.append(message)
        await self._dispatch_message(message)
        return message

    async def _dispatch_message(self, message: ChannelMessage) -> None:
        """Dispatch message to all handlers."""
        for handler in self._message_handlers:
            try:
                await handler(message)
            except Exception:
                pass

    def register_handler(self, handler: Callable) -> None:
        """Register a message handler."""
        self._message_handlers.append(handler)

    def get_connections(self) -> List[WebSocketConnection]:
        """Get all active connections."""
        return list(self._connections.values())

    def get_recent_messages(self, limit: int = 50) -> List[ChannelMessage]:
        """Get recent messages."""
        return self._message_history[-limit:]


class EvacuationChannel:
    """
    WebSocket channel for evacuation status and route updates.
    """

    def __init__(self):
        self._connections: Dict[str, WebSocketConnection] = {}
        self._message_handlers: List[Callable] = []
        self._message_history: List[ChannelMessage] = []

    async def connect(
        self,
        connection_id: str,
        user_id: Optional[str] = None,
        zone_subscriptions: Optional[Set[str]] = None,
    ) -> WebSocketConnection:
        """Connect to the evacuation channel."""
        connection = WebSocketConnection(
            connection_id=connection_id,
            channel=EmergencyChannelType.EVAC,
            user_id=user_id,
            subscriptions=zone_subscriptions or {"all"},
            connected_at=datetime.utcnow(),
            last_activity=datetime.utcnow(),
        )
        self._connections[connection_id] = connection
        return connection

    async def disconnect(self, connection_id: str) -> None:
        """Disconnect from the evacuation channel."""
        if connection_id in self._connections:
            del self._connections[connection_id]

    async def broadcast_evacuation_order(
        self,
        order_data: Dict[str, Any],
    ) -> ChannelMessage:
        """Broadcast an evacuation order."""
        message = ChannelMessage(
            message_id=f"msg-{uuid.uuid4().hex[:8]}",
            channel=EmergencyChannelType.EVAC,
            message_type=MessageType.COMMAND,
            payload={
                "command": "evacuation_order",
                "data": order_data,
            },
            sender="evacuation_manager",
            priority=10,
            target_subscriptions=[order_data.get("zone", "all")],
        )

        self._message_history.append(message)
        await self._dispatch_message(message)
        return message

    async def broadcast_route_update(
        self,
        route_id: str,
        route_data: Dict[str, Any],
    ) -> ChannelMessage:
        """Broadcast a route status update."""
        message = ChannelMessage(
            message_id=f"msg-{uuid.uuid4().hex[:8]}",
            channel=EmergencyChannelType.EVAC,
            message_type=MessageType.UPDATE,
            payload={
                "update_type": "route_status",
                "route_id": route_id,
                "data": route_data,
            },
            sender="route_optimizer",
        )

        self._message_history.append(message)
        await self._dispatch_message(message)
        return message

    async def broadcast_traffic_update(
        self,
        traffic_data: Dict[str, Any],
    ) -> ChannelMessage:
        """Broadcast traffic conditions update."""
        message = ChannelMessage(
            message_id=f"msg-{uuid.uuid4().hex[:8]}",
            channel=EmergencyChannelType.EVAC,
            message_type=MessageType.UPDATE,
            payload={
                "update_type": "traffic",
                "data": traffic_data,
            },
            sender="traffic_simulator",
        )

        self._message_history.append(message)
        await self._dispatch_message(message)
        return message

    async def broadcast_population_movement(
        self,
        movement_data: Dict[str, Any],
    ) -> ChannelMessage:
        """Broadcast population movement update."""
        message = ChannelMessage(
            message_id=f"msg-{uuid.uuid4().hex[:8]}",
            channel=EmergencyChannelType.EVAC,
            message_type=MessageType.STATUS,
            payload={
                "status_type": "population_movement",
                "data": movement_data,
            },
            sender="movement_predictor",
        )

        self._message_history.append(message)
        await self._dispatch_message(message)
        return message

    async def _dispatch_message(self, message: ChannelMessage) -> None:
        """Dispatch message to all handlers."""
        for handler in self._message_handlers:
            try:
                await handler(message)
            except Exception:
                pass

    def register_handler(self, handler: Callable) -> None:
        """Register a message handler."""
        self._message_handlers.append(handler)

    def get_connections(self) -> List[WebSocketConnection]:
        """Get all active connections."""
        return list(self._connections.values())


class ResourcesChannel:
    """
    WebSocket channel for resource logistics updates.
    """

    def __init__(self):
        self._connections: Dict[str, WebSocketConnection] = {}
        self._message_handlers: List[Callable] = []
        self._message_history: List[ChannelMessage] = []

    async def connect(
        self,
        connection_id: str,
        user_id: Optional[str] = None,
        resource_subscriptions: Optional[Set[str]] = None,
    ) -> WebSocketConnection:
        """Connect to the resources channel."""
        connection = WebSocketConnection(
            connection_id=connection_id,
            channel=EmergencyChannelType.RESOURCES,
            user_id=user_id,
            subscriptions=resource_subscriptions or {"all"},
            connected_at=datetime.utcnow(),
            last_activity=datetime.utcnow(),
        )
        self._connections[connection_id] = connection
        return connection

    async def disconnect(self, connection_id: str) -> None:
        """Disconnect from the resources channel."""
        if connection_id in self._connections:
            del self._connections[connection_id]

    async def broadcast_shelter_update(
        self,
        shelter_id: str,
        shelter_data: Dict[str, Any],
    ) -> ChannelMessage:
        """Broadcast shelter status update."""
        message = ChannelMessage(
            message_id=f"msg-{uuid.uuid4().hex[:8]}",
            channel=EmergencyChannelType.RESOURCES,
            message_type=MessageType.UPDATE,
            payload={
                "update_type": "shelter",
                "shelter_id": shelter_id,
                "data": shelter_data,
            },
            sender="shelter_registry",
        )

        self._message_history.append(message)
        await self._dispatch_message(message)
        return message

    async def broadcast_supply_alert(
        self,
        supply_data: Dict[str, Any],
    ) -> ChannelMessage:
        """Broadcast supply alert (low stock, etc.)."""
        message = ChannelMessage(
            message_id=f"msg-{uuid.uuid4().hex[:8]}",
            channel=EmergencyChannelType.RESOURCES,
            message_type=MessageType.ALERT,
            payload={
                "alert_type": "supply",
                "data": supply_data,
            },
            sender="supply_chain",
            priority=5,
        )

        self._message_history.append(message)
        await self._dispatch_message(message)
        return message

    async def broadcast_deployment_update(
        self,
        unit_id: str,
        deployment_data: Dict[str, Any],
    ) -> ChannelMessage:
        """Broadcast deployment unit update."""
        message = ChannelMessage(
            message_id=f"msg-{uuid.uuid4().hex[:8]}",
            channel=EmergencyChannelType.RESOURCES,
            message_type=MessageType.UPDATE,
            payload={
                "update_type": "deployment",
                "unit_id": unit_id,
                "data": deployment_data,
            },
            sender="deployment_allocator",
        )

        self._message_history.append(message)
        await self._dispatch_message(message)
        return message

    async def broadcast_infrastructure_outage(
        self,
        asset_id: str,
        outage_data: Dict[str, Any],
    ) -> ChannelMessage:
        """Broadcast infrastructure outage alert."""
        message = ChannelMessage(
            message_id=f"msg-{uuid.uuid4().hex[:8]}",
            channel=EmergencyChannelType.RESOURCES,
            message_type=MessageType.ALERT,
            payload={
                "alert_type": "infrastructure_outage",
                "asset_id": asset_id,
                "data": outage_data,
            },
            sender="infrastructure_monitor",
            priority=8,
        )

        self._message_history.append(message)
        await self._dispatch_message(message)
        return message

    async def _dispatch_message(self, message: ChannelMessage) -> None:
        """Dispatch message to all handlers."""
        for handler in self._message_handlers:
            try:
                await handler(message)
            except Exception:
                pass

    def register_handler(self, handler: Callable) -> None:
        """Register a message handler."""
        self._message_handlers.append(handler)

    def get_connections(self) -> List[WebSocketConnection]:
        """Get all active connections."""
        return list(self._connections.values())


class MedicalChannel:
    """
    WebSocket channel for medical surge updates.
    """

    def __init__(self):
        self._connections: Dict[str, WebSocketConnection] = {}
        self._message_handlers: List[Callable] = []
        self._message_history: List[ChannelMessage] = []

    async def connect(
        self,
        connection_id: str,
        user_id: Optional[str] = None,
        medical_subscriptions: Optional[Set[str]] = None,
    ) -> WebSocketConnection:
        """Connect to the medical channel."""
        connection = WebSocketConnection(
            connection_id=connection_id,
            channel=EmergencyChannelType.MEDICAL,
            user_id=user_id,
            subscriptions=medical_subscriptions or {"all"},
            connected_at=datetime.utcnow(),
            last_activity=datetime.utcnow(),
        )
        self._connections[connection_id] = connection
        return connection

    async def disconnect(self, connection_id: str) -> None:
        """Disconnect from the medical channel."""
        if connection_id in self._connections:
            del self._connections[connection_id]

    async def broadcast_hospital_status(
        self,
        hospital_id: str,
        status_data: Dict[str, Any],
    ) -> ChannelMessage:
        """Broadcast hospital status update."""
        message = ChannelMessage(
            message_id=f"msg-{uuid.uuid4().hex[:8]}",
            channel=EmergencyChannelType.MEDICAL,
            message_type=MessageType.STATUS,
            payload={
                "status_type": "hospital",
                "hospital_id": hospital_id,
                "data": status_data,
            },
            sender="hospital_predictor",
        )

        self._message_history.append(message)
        await self._dispatch_message(message)
        return message

    async def broadcast_surge_alert(
        self,
        surge_data: Dict[str, Any],
    ) -> ChannelMessage:
        """Broadcast medical surge alert."""
        message = ChannelMessage(
            message_id=f"msg-{uuid.uuid4().hex[:8]}",
            channel=EmergencyChannelType.MEDICAL,
            message_type=MessageType.ALERT,
            payload={
                "alert_type": "surge",
                "data": surge_data,
            },
            sender="medical_surge_manager",
            priority=9,
        )

        self._message_history.append(message)
        await self._dispatch_message(message)
        return message

    async def broadcast_triage_update(
        self,
        triage_data: Dict[str, Any],
    ) -> ChannelMessage:
        """Broadcast triage status update."""
        message = ChannelMessage(
            message_id=f"msg-{uuid.uuid4().hex[:8]}",
            channel=EmergencyChannelType.MEDICAL,
            message_type=MessageType.UPDATE,
            payload={
                "update_type": "triage",
                "data": triage_data,
            },
            sender="triage_model",
        )

        self._message_history.append(message)
        await self._dispatch_message(message)
        return message

    async def broadcast_ems_update(
        self,
        ems_data: Dict[str, Any],
    ) -> ChannelMessage:
        """Broadcast EMS status update."""
        message = ChannelMessage(
            message_id=f"msg-{uuid.uuid4().hex[:8]}",
            channel=EmergencyChannelType.MEDICAL,
            message_type=MessageType.UPDATE,
            payload={
                "update_type": "ems",
                "data": ems_data,
            },
            sender="ems_forecaster",
        )

        self._message_history.append(message)
        await self._dispatch_message(message)
        return message

    async def broadcast_supply_critical(
        self,
        supply_data: Dict[str, Any],
    ) -> ChannelMessage:
        """Broadcast critical medical supply alert."""
        message = ChannelMessage(
            message_id=f"msg-{uuid.uuid4().hex[:8]}",
            channel=EmergencyChannelType.MEDICAL,
            message_type=MessageType.ALERT,
            payload={
                "alert_type": "critical_supply",
                "data": supply_data,
            },
            sender="supply_tracker",
            priority=7,
        )

        self._message_history.append(message)
        await self._dispatch_message(message)
        return message

    async def _dispatch_message(self, message: ChannelMessage) -> None:
        """Dispatch message to all handlers."""
        for handler in self._message_handlers:
            try:
                await handler(message)
            except Exception:
                pass

    def register_handler(self, handler: Callable) -> None:
        """Register a message handler."""
        self._message_handlers.append(handler)

    def get_connections(self) -> List[WebSocketConnection]:
        """Get all active connections."""
        return list(self._connections.values())


class IncidentsChannel:
    """
    WebSocket channel for incident command updates.
    """

    def __init__(self):
        self._connections: Dict[str, WebSocketConnection] = {}
        self._message_handlers: List[Callable] = []
        self._message_history: List[ChannelMessage] = []

    async def connect(
        self,
        connection_id: str,
        user_id: Optional[str] = None,
        room_subscriptions: Optional[Set[str]] = None,
    ) -> WebSocketConnection:
        """Connect to the incidents channel."""
        connection = WebSocketConnection(
            connection_id=connection_id,
            channel=EmergencyChannelType.INCIDENTS,
            user_id=user_id,
            subscriptions=room_subscriptions or {"all"},
            connected_at=datetime.utcnow(),
            last_activity=datetime.utcnow(),
        )
        self._connections[connection_id] = connection
        return connection

    async def disconnect(self, connection_id: str) -> None:
        """Disconnect from the incidents channel."""
        if connection_id in self._connections:
            del self._connections[connection_id]

    async def broadcast_incident_created(
        self,
        room_id: str,
        incident_data: Dict[str, Any],
    ) -> ChannelMessage:
        """Broadcast new incident creation."""
        message = ChannelMessage(
            message_id=f"msg-{uuid.uuid4().hex[:8]}",
            channel=EmergencyChannelType.INCIDENTS,
            message_type=MessageType.NOTIFICATION,
            payload={
                "notification_type": "incident_created",
                "room_id": room_id,
                "data": incident_data,
            },
            sender="room_manager",
            priority=8,
        )

        self._message_history.append(message)
        await self._dispatch_message(message)
        return message

    async def broadcast_incident_update(
        self,
        room_id: str,
        update_data: Dict[str, Any],
    ) -> ChannelMessage:
        """Broadcast incident status update."""
        message = ChannelMessage(
            message_id=f"msg-{uuid.uuid4().hex[:8]}",
            channel=EmergencyChannelType.INCIDENTS,
            message_type=MessageType.UPDATE,
            payload={
                "update_type": "incident_status",
                "room_id": room_id,
                "data": update_data,
            },
            sender="room_manager",
            target_subscriptions=[room_id, "all"],
        )

        self._message_history.append(message)
        await self._dispatch_message(message)
        return message

    async def broadcast_task_update(
        self,
        room_id: str,
        task_data: Dict[str, Any],
    ) -> ChannelMessage:
        """Broadcast task update."""
        message = ChannelMessage(
            message_id=f"msg-{uuid.uuid4().hex[:8]}",
            channel=EmergencyChannelType.INCIDENTS,
            message_type=MessageType.UPDATE,
            payload={
                "update_type": "task",
                "room_id": room_id,
                "data": task_data,
            },
            sender="task_engine",
            target_subscriptions=[room_id],
        )

        self._message_history.append(message)
        await self._dispatch_message(message)
        return message

    async def broadcast_brief(
        self,
        room_id: str,
        brief_data: Dict[str, Any],
    ) -> ChannelMessage:
        """Broadcast incident brief."""
        message = ChannelMessage(
            message_id=f"msg-{uuid.uuid4().hex[:8]}",
            channel=EmergencyChannelType.INCIDENTS,
            message_type=MessageType.BROADCAST,
            payload={
                "broadcast_type": "brief",
                "room_id": room_id,
                "data": brief_data,
            },
            sender="brief_builder",
            priority=6,
            target_subscriptions=[room_id, "all"],
        )

        self._message_history.append(message)
        await self._dispatch_message(message)
        return message

    async def broadcast_timeline_event(
        self,
        room_id: str,
        event_data: Dict[str, Any],
    ) -> ChannelMessage:
        """Broadcast timeline event."""
        message = ChannelMessage(
            message_id=f"msg-{uuid.uuid4().hex[:8]}",
            channel=EmergencyChannelType.INCIDENTS,
            message_type=MessageType.UPDATE,
            payload={
                "update_type": "timeline_event",
                "room_id": room_id,
                "data": event_data,
            },
            sender="timeline_sync",
            target_subscriptions=[room_id],
        )

        self._message_history.append(message)
        await self._dispatch_message(message)
        return message

    async def broadcast_eoc_update(
        self,
        eoc_data: Dict[str, Any],
    ) -> ChannelMessage:
        """Broadcast EOC status update."""
        message = ChannelMessage(
            message_id=f"msg-{uuid.uuid4().hex[:8]}",
            channel=EmergencyChannelType.INCIDENTS,
            message_type=MessageType.STATUS,
            payload={
                "status_type": "eoc",
                "data": eoc_data,
            },
            sender="eoc_coordinator",
        )

        self._message_history.append(message)
        await self._dispatch_message(message)
        return message

    async def _dispatch_message(self, message: ChannelMessage) -> None:
        """Dispatch message to all handlers."""
        for handler in self._message_handlers:
            try:
                await handler(message)
            except Exception:
                pass

    def register_handler(self, handler: Callable) -> None:
        """Register a message handler."""
        self._message_handlers.append(handler)

    def get_connections(self) -> List[WebSocketConnection]:
        """Get all active connections."""
        return list(self._connections.values())


class DamageChannel:
    """
    WebSocket channel for damage assessment updates.
    """

    def __init__(self):
        self._connections: Dict[str, WebSocketConnection] = {}
        self._message_handlers: List[Callable] = []
        self._message_history: List[ChannelMessage] = []

    async def connect(
        self,
        connection_id: str,
        user_id: Optional[str] = None,
        area_subscriptions: Optional[Set[str]] = None,
    ) -> WebSocketConnection:
        """Connect to the damage channel."""
        connection = WebSocketConnection(
            connection_id=connection_id,
            channel=EmergencyChannelType.DAMAGE,
            user_id=user_id,
            subscriptions=area_subscriptions or {"all"},
            connected_at=datetime.utcnow(),
            last_activity=datetime.utcnow(),
        )
        self._connections[connection_id] = connection
        return connection

    async def disconnect(self, connection_id: str) -> None:
        """Disconnect from the damage channel."""
        if connection_id in self._connections:
            del self._connections[connection_id]

    async def broadcast_assessment_complete(
        self,
        assessment_data: Dict[str, Any],
    ) -> ChannelMessage:
        """Broadcast completed assessment."""
        message = ChannelMessage(
            message_id=f"msg-{uuid.uuid4().hex[:8]}",
            channel=EmergencyChannelType.DAMAGE,
            message_type=MessageType.NOTIFICATION,
            payload={
                "notification_type": "assessment_complete",
                "data": assessment_data,
            },
            sender="damage_manager",
        )

        self._message_history.append(message)
        await self._dispatch_message(message)
        return message

    async def broadcast_drone_image_processed(
        self,
        image_data: Dict[str, Any],
    ) -> ChannelMessage:
        """Broadcast drone image processing complete."""
        message = ChannelMessage(
            message_id=f"msg-{uuid.uuid4().hex[:8]}",
            channel=EmergencyChannelType.DAMAGE,
            message_type=MessageType.UPDATE,
            payload={
                "update_type": "drone_image_processed",
                "data": image_data,
            },
            sender="drone_classifier",
        )

        self._message_history.append(message)
        await self._dispatch_message(message)
        return message

    async def broadcast_high_risk_alert(
        self,
        risk_data: Dict[str, Any],
    ) -> ChannelMessage:
        """Broadcast high risk structure alert."""
        message = ChannelMessage(
            message_id=f"msg-{uuid.uuid4().hex[:8]}",
            channel=EmergencyChannelType.DAMAGE,
            message_type=MessageType.ALERT,
            payload={
                "alert_type": "high_risk_structure",
                "data": risk_data,
            },
            sender="risk_scorer",
            priority=7,
        )

        self._message_history.append(message)
        await self._dispatch_message(message)
        return message

    async def broadcast_recovery_update(
        self,
        timeline_id: str,
        recovery_data: Dict[str, Any],
    ) -> ChannelMessage:
        """Broadcast recovery timeline update."""
        message = ChannelMessage(
            message_id=f"msg-{uuid.uuid4().hex[:8]}",
            channel=EmergencyChannelType.DAMAGE,
            message_type=MessageType.UPDATE,
            payload={
                "update_type": "recovery_progress",
                "timeline_id": timeline_id,
                "data": recovery_data,
            },
            sender="recovery_engine",
        )

        self._message_history.append(message)
        await self._dispatch_message(message)
        return message

    async def broadcast_area_summary(
        self,
        area_id: str,
        summary_data: Dict[str, Any],
    ) -> ChannelMessage:
        """Broadcast area damage summary."""
        message = ChannelMessage(
            message_id=f"msg-{uuid.uuid4().hex[:8]}",
            channel=EmergencyChannelType.DAMAGE,
            message_type=MessageType.STATUS,
            payload={
                "status_type": "area_summary",
                "area_id": area_id,
                "data": summary_data,
            },
            sender="damage_manager",
        )

        self._message_history.append(message)
        await self._dispatch_message(message)
        return message

    async def _dispatch_message(self, message: ChannelMessage) -> None:
        """Dispatch message to all handlers."""
        for handler in self._message_handlers:
            try:
                await handler(message)
            except Exception:
                pass

    def register_handler(self, handler: Callable) -> None:
        """Register a message handler."""
        self._message_handlers.append(handler)

    def get_connections(self) -> List[WebSocketConnection]:
        """Get all active connections."""
        return list(self._connections.values())


class EmergencyWebSocketManager:
    """
    Main WebSocket manager for all emergency channels.
    """

    def __init__(self):
        self.crisis_channel = CrisisChannel()
        self.evac_channel = EvacuationChannel()
        self.resources_channel = ResourcesChannel()
        self.medical_channel = MedicalChannel()
        self.incidents_channel = IncidentsChannel()
        self.damage_channel = DamageChannel()

    def get_channel(self, channel_type: EmergencyChannelType):
        """Get channel by type."""
        channel_map = {
            EmergencyChannelType.CRISIS: self.crisis_channel,
            EmergencyChannelType.EVAC: self.evac_channel,
            EmergencyChannelType.RESOURCES: self.resources_channel,
            EmergencyChannelType.MEDICAL: self.medical_channel,
            EmergencyChannelType.INCIDENTS: self.incidents_channel,
            EmergencyChannelType.DAMAGE: self.damage_channel,
        }
        return channel_map.get(channel_type)

    def get_all_connections(self) -> Dict[str, List[WebSocketConnection]]:
        """Get all connections across all channels."""
        return {
            "crisis": self.crisis_channel.get_connections(),
            "evac": self.evac_channel.get_connections(),
            "resources": self.resources_channel.get_connections(),
            "medical": self.medical_channel.get_connections(),
            "incidents": self.incidents_channel.get_connections(),
            "damage": self.damage_channel.get_connections(),
        }

    def get_connection_counts(self) -> Dict[str, int]:
        """Get connection counts per channel."""
        return {
            "crisis": len(self.crisis_channel.get_connections()),
            "evac": len(self.evac_channel.get_connections()),
            "resources": len(self.resources_channel.get_connections()),
            "medical": len(self.medical_channel.get_connections()),
            "incidents": len(self.incidents_channel.get_connections()),
            "damage": len(self.damage_channel.get_connections()),
        }

    async def broadcast_to_all(
        self,
        message_type: MessageType,
        payload: Dict[str, Any],
        priority: int = 0,
    ) -> None:
        """Broadcast message to all channels."""
        if message_type == MessageType.ALERT:
            await self.crisis_channel.broadcast_alert("system", payload, priority)
        else:
            await self.crisis_channel.broadcast_update("system", payload)


emergency_ws_manager = EmergencyWebSocketManager()
