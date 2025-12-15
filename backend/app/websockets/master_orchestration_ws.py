"""
Master Orchestration WebSocket Manager
Phase 37: Master UI Integration & System Orchestration Shell
Unified WebSocket channel for all RTCC modules.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set
import uuid
import json
import asyncio


class MasterWSChannel(Enum):
    EVENTS = "events"
    ALERTS = "alerts"
    MODULE_STATUS = "module_status"
    STATE_SYNC = "state_sync"
    NOTIFICATIONS = "notifications"
    TACTICAL = "tactical"
    OFFICER_SAFETY = "officer_safety"
    DRONE_TELEMETRY = "drone_telemetry"
    ROBOT_TELEMETRY = "robot_telemetry"
    INVESTIGATIONS = "investigations"
    THREATS = "threats"
    EMERGENCY = "emergency"
    COMPLIANCE = "compliance"
    ALL = "all"


class MessageType(Enum):
    EVENT = "event"
    ALERT = "alert"
    MODULE_STATUS = "module_status"
    STATE_CHANGE = "state_change"
    NOTIFICATION = "notification"
    HEARTBEAT = "heartbeat"
    SUBSCRIPTION_CONFIRM = "subscription_confirm"
    ERROR = "error"
    BROADCAST = "broadcast"


@dataclass
class WSConnection:
    connection_id: str = field(default_factory=lambda: f"ws-{uuid.uuid4().hex[:12]}")
    user_id: Optional[str] = None
    channels: Set[MasterWSChannel] = field(default_factory=set)
    connected_at: datetime = field(default_factory=datetime.utcnow)
    last_activity: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "connection_id": self.connection_id,
            "user_id": self.user_id,
            "channels": [c.value for c in self.channels],
            "connected_at": self.connected_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "metadata": self.metadata,
        }


@dataclass
class WSMessage:
    message_id: str = field(default_factory=lambda: f"msg-{uuid.uuid4().hex[:12]}")
    message_type: MessageType = MessageType.BROADCAST
    channel: MasterWSChannel = MasterWSChannel.ALL
    timestamp: datetime = field(default_factory=datetime.utcnow)
    source: str = "master_orchestration"
    payload: Dict[str, Any] = field(default_factory=dict)
    priority: int = 5
    requires_ack: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "message_id": self.message_id,
            "message_type": self.message_type.value,
            "channel": self.channel.value,
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
            "payload": self.payload,
            "priority": self.priority,
            "requires_ack": self.requires_ack,
            "metadata": self.metadata,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict())


class MasterOrchestrationWSManager:
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

        self._connections: Dict[str, WSConnection] = {}
        self._channel_subscribers: Dict[MasterWSChannel, Set[str]] = {
            channel: set() for channel in MasterWSChannel
        }
        self._message_history: List[WSMessage] = []
        self._max_history = 1000
        self._statistics = {
            "connections_total": 0,
            "connections_active": 0,
            "messages_sent": 0,
            "messages_broadcast": 0,
            "subscriptions_total": 0,
        }

    async def connect(
        self,
        user_id: Optional[str] = None,
        channels: Optional[List[MasterWSChannel]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> WSConnection:
        connection = WSConnection(
            user_id=user_id,
            channels=set(channels) if channels else {MasterWSChannel.ALL},
            metadata=metadata or {},
        )

        self._connections[connection.connection_id] = connection
        self._statistics["connections_total"] += 1
        self._statistics["connections_active"] += 1

        for channel in connection.channels:
            self._channel_subscribers[channel].add(connection.connection_id)
            self._statistics["subscriptions_total"] += 1

        return connection

    async def disconnect(self, connection_id: str) -> bool:
        connection = self._connections.get(connection_id)
        if not connection:
            return False

        for channel in connection.channels:
            self._channel_subscribers[channel].discard(connection_id)

        del self._connections[connection_id]
        self._statistics["connections_active"] -= 1
        return True

    async def subscribe(self, connection_id: str, channel: MasterWSChannel) -> bool:
        connection = self._connections.get(connection_id)
        if not connection:
            return False

        connection.channels.add(channel)
        self._channel_subscribers[channel].add(connection_id)
        self._statistics["subscriptions_total"] += 1
        return True

    async def unsubscribe(self, connection_id: str, channel: MasterWSChannel) -> bool:
        connection = self._connections.get(connection_id)
        if not connection:
            return False

        connection.channels.discard(channel)
        self._channel_subscribers[channel].discard(connection_id)
        return True

    async def send_message(
        self,
        connection_id: str,
        message: WSMessage,
    ) -> bool:
        connection = self._connections.get(connection_id)
        if not connection:
            return False

        connection.last_activity = datetime.utcnow()
        self._message_history.append(message)
        self._statistics["messages_sent"] += 1

        if len(self._message_history) > self._max_history:
            self._message_history = self._message_history[-self._max_history:]

        return True

    async def broadcast_to_channel(
        self,
        channel: MasterWSChannel,
        message: WSMessage,
    ) -> int:
        message.channel = channel
        subscribers = self._channel_subscribers.get(channel, set())

        if channel == MasterWSChannel.ALL:
            subscribers = set(self._connections.keys())

        sent_count = 0
        for conn_id in subscribers:
            if await self.send_message(conn_id, message):
                sent_count += 1

        self._statistics["messages_broadcast"] += 1
        return sent_count

    async def broadcast_event(
        self,
        event_type: str,
        title: str,
        summary: str,
        source: str,
        details: Optional[Dict[str, Any]] = None,
        priority: int = 5,
    ) -> int:
        message = WSMessage(
            message_type=MessageType.EVENT,
            channel=MasterWSChannel.EVENTS,
            source=source,
            payload={
                "event_type": event_type,
                "title": title,
                "summary": summary,
                "details": details or {},
            },
            priority=priority,
        )
        return await self.broadcast_to_channel(MasterWSChannel.EVENTS, message)

    async def broadcast_alert(
        self,
        severity: str,
        title: str,
        summary: str,
        source: str,
        geolocation: Optional[Dict[str, float]] = None,
        affected_areas: Optional[List[str]] = None,
        requires_action: bool = False,
    ) -> int:
        priority_map = {"critical": 1, "high": 2, "medium": 3, "low": 4, "info": 5}
        priority = priority_map.get(severity.lower(), 5)

        message = WSMessage(
            message_type=MessageType.ALERT,
            channel=MasterWSChannel.ALERTS,
            source=source,
            payload={
                "severity": severity,
                "title": title,
                "summary": summary,
                "geolocation": geolocation,
                "affected_areas": affected_areas or [],
                "requires_action": requires_action,
            },
            priority=priority,
        )
        return await self.broadcast_to_channel(MasterWSChannel.ALERTS, message)

    async def broadcast_module_status(
        self,
        module_id: str,
        module_name: str,
        status: str,
        response_time_ms: float = 0.0,
        error_count: int = 0,
    ) -> int:
        message = WSMessage(
            message_type=MessageType.MODULE_STATUS,
            channel=MasterWSChannel.MODULE_STATUS,
            source="module_heartbeat",
            payload={
                "module_id": module_id,
                "module_name": module_name,
                "status": status,
                "response_time_ms": response_time_ms,
                "error_count": error_count,
            },
        )
        return await self.broadcast_to_channel(MasterWSChannel.MODULE_STATUS, message)

    async def broadcast_state_change(
        self,
        change_type: str,
        source_module: str,
        data: Dict[str, Any],
        targets: Optional[List[str]] = None,
    ) -> int:
        message = WSMessage(
            message_type=MessageType.STATE_CHANGE,
            channel=MasterWSChannel.STATE_SYNC,
            source=source_module,
            payload={
                "change_type": change_type,
                "data": data,
                "targets": targets or [],
            },
        )
        return await self.broadcast_to_channel(MasterWSChannel.STATE_SYNC, message)

    async def broadcast_notification(
        self,
        title: str,
        message_text: str,
        notification_type: str = "info",
        source: str = "system",
    ) -> int:
        message = WSMessage(
            message_type=MessageType.NOTIFICATION,
            channel=MasterWSChannel.NOTIFICATIONS,
            source=source,
            payload={
                "title": title,
                "message": message_text,
                "notification_type": notification_type,
            },
        )
        return await self.broadcast_to_channel(MasterWSChannel.NOTIFICATIONS, message)

    async def broadcast_tactical_update(
        self,
        update_type: str,
        data: Dict[str, Any],
        source: str = "tactical_analytics",
    ) -> int:
        message = WSMessage(
            message_type=MessageType.BROADCAST,
            channel=MasterWSChannel.TACTICAL,
            source=source,
            payload={
                "update_type": update_type,
                "data": data,
            },
        )
        return await self.broadcast_to_channel(MasterWSChannel.TACTICAL, message)

    async def broadcast_officer_safety(
        self,
        officer_id: str,
        status: str,
        location: Optional[Dict[str, float]] = None,
        alert_type: Optional[str] = None,
    ) -> int:
        priority = 1 if alert_type else 3
        message = WSMessage(
            message_type=MessageType.ALERT if alert_type else MessageType.BROADCAST,
            channel=MasterWSChannel.OFFICER_SAFETY,
            source="officer_safety",
            payload={
                "officer_id": officer_id,
                "status": status,
                "location": location,
                "alert_type": alert_type,
            },
            priority=priority,
        )
        return await self.broadcast_to_channel(MasterWSChannel.OFFICER_SAFETY, message)

    async def broadcast_drone_telemetry(
        self,
        drone_id: str,
        position: Dict[str, float],
        status: str,
        battery: float,
        mission_id: Optional[str] = None,
    ) -> int:
        message = WSMessage(
            message_type=MessageType.BROADCAST,
            channel=MasterWSChannel.DRONE_TELEMETRY,
            source="drone_ops",
            payload={
                "drone_id": drone_id,
                "position": position,
                "status": status,
                "battery": battery,
                "mission_id": mission_id,
            },
        )
        return await self.broadcast_to_channel(MasterWSChannel.DRONE_TELEMETRY, message)

    async def broadcast_robot_telemetry(
        self,
        robot_id: str,
        position: Dict[str, float],
        status: str,
        battery: float,
        task_id: Optional[str] = None,
    ) -> int:
        message = WSMessage(
            message_type=MessageType.BROADCAST,
            channel=MasterWSChannel.ROBOT_TELEMETRY,
            source="robotics",
            payload={
                "robot_id": robot_id,
                "position": position,
                "status": status,
                "battery": battery,
                "task_id": task_id,
            },
        )
        return await self.broadcast_to_channel(MasterWSChannel.ROBOT_TELEMETRY, message)

    async def broadcast_investigation_update(
        self,
        case_id: str,
        update_type: str,
        summary: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> int:
        message = WSMessage(
            message_type=MessageType.BROADCAST,
            channel=MasterWSChannel.INVESTIGATIONS,
            source="investigations",
            payload={
                "case_id": case_id,
                "update_type": update_type,
                "summary": summary,
                "details": details or {},
            },
        )
        return await self.broadcast_to_channel(MasterWSChannel.INVESTIGATIONS, message)

    async def broadcast_threat_update(
        self,
        threat_id: str,
        threat_level: str,
        title: str,
        summary: str,
        source: str = "threat_intel",
    ) -> int:
        priority_map = {"critical": 1, "high": 2, "medium": 3, "low": 4}
        priority = priority_map.get(threat_level.lower(), 3)

        message = WSMessage(
            message_type=MessageType.ALERT,
            channel=MasterWSChannel.THREATS,
            source=source,
            payload={
                "threat_id": threat_id,
                "threat_level": threat_level,
                "title": title,
                "summary": summary,
            },
            priority=priority,
        )
        return await self.broadcast_to_channel(MasterWSChannel.THREATS, message)

    async def broadcast_emergency(
        self,
        emergency_type: str,
        title: str,
        summary: str,
        affected_areas: List[str],
        severity: str = "high",
    ) -> int:
        message = WSMessage(
            message_type=MessageType.ALERT,
            channel=MasterWSChannel.EMERGENCY,
            source="emergency_mgmt",
            payload={
                "emergency_type": emergency_type,
                "title": title,
                "summary": summary,
                "affected_areas": affected_areas,
                "severity": severity,
            },
            priority=1,
        )

        await self.broadcast_to_channel(MasterWSChannel.EMERGENCY, message)
        return await self.broadcast_to_channel(MasterWSChannel.ALL, message)

    async def send_heartbeat(self) -> int:
        message = WSMessage(
            message_type=MessageType.HEARTBEAT,
            channel=MasterWSChannel.ALL,
            source="master_orchestration",
            payload={
                "timestamp": datetime.utcnow().isoformat(),
                "connections_active": self._statistics["connections_active"],
            },
        )
        return await self.broadcast_to_channel(MasterWSChannel.ALL, message)

    def get_connection(self, connection_id: str) -> Optional[WSConnection]:
        return self._connections.get(connection_id)

    def get_active_connections(self) -> List[WSConnection]:
        return list(self._connections.values())

    def get_connections_by_channel(self, channel: MasterWSChannel) -> List[WSConnection]:
        conn_ids = self._channel_subscribers.get(channel, set())
        return [self._connections[cid] for cid in conn_ids if cid in self._connections]

    def get_message_history(
        self,
        limit: int = 100,
        channel: Optional[MasterWSChannel] = None,
    ) -> List[WSMessage]:
        messages = list(reversed(self._message_history))

        if channel:
            messages = [m for m in messages if m.channel == channel]

        return messages[:limit]

    def get_statistics(self) -> Dict[str, Any]:
        return {
            **self._statistics,
            "channels": {
                channel.value: len(subscribers)
                for channel, subscribers in self._channel_subscribers.items()
            },
            "message_history_count": len(self._message_history),
        }

    def get_channel_info(self) -> Dict[str, Any]:
        return {
            channel.value: {
                "subscribers": len(self._channel_subscribers[channel]),
                "description": self._get_channel_description(channel),
            }
            for channel in MasterWSChannel
        }

    def _get_channel_description(self, channel: MasterWSChannel) -> str:
        descriptions = {
            MasterWSChannel.EVENTS: "System-wide events from all modules",
            MasterWSChannel.ALERTS: "Unified alert stream from all sources",
            MasterWSChannel.MODULE_STATUS: "Module health and status updates",
            MasterWSChannel.STATE_SYNC: "Cross-module state synchronization",
            MasterWSChannel.NOTIFICATIONS: "User notifications and messages",
            MasterWSChannel.TACTICAL: "Tactical analytics updates",
            MasterWSChannel.OFFICER_SAFETY: "Officer safety alerts and status",
            MasterWSChannel.DRONE_TELEMETRY: "Drone position and status updates",
            MasterWSChannel.ROBOT_TELEMETRY: "Robot position and status updates",
            MasterWSChannel.INVESTIGATIONS: "Investigation case updates",
            MasterWSChannel.THREATS: "Threat intelligence updates",
            MasterWSChannel.EMERGENCY: "Emergency management alerts",
            MasterWSChannel.COMPLIANCE: "Compliance and audit updates",
            MasterWSChannel.ALL: "All channels combined",
        }
        return descriptions.get(channel, "")
