"""
Phase 17: Global Threat Intelligence WebSocket Channels

Provides real-time WebSocket channels for:
- /ws/global-threats - Main threat intelligence feed
- /ws/global-threats/dark-web - Dark web signals
- /ws/global-threats/osint - OSINT signals
- /ws/global-threats/extremist - Extremist network updates
- /ws/global-threats/incidents - Global incident updates
- /ws/global-threats/alerts - Threat alerts
- /ws/global-threats/scoring - Threat score updates
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Optional
import json
import uuid


class ThreatIntelChannel(Enum):
    """Available threat intelligence WebSocket channels"""
    MAIN = "global-threats"
    DARK_WEB = "global-threats/dark-web"
    OSINT = "global-threats/osint"
    EXTREMIST = "global-threats/extremist"
    INCIDENTS = "global-threats/incidents"
    ALERTS = "global-threats/alerts"
    SCORING = "global-threats/scoring"
    ESCALATIONS = "global-threats/escalations"


class MessageType(Enum):
    """Types of WebSocket messages"""
    SIGNAL = "signal"
    ALERT = "alert"
    UPDATE = "update"
    SCORE = "score"
    INCIDENT = "incident"
    NETWORK = "network"
    PREDICTION = "prediction"
    SPIKE = "spike"
    CORRELATION = "correlation"
    SYSTEM = "system"


@dataclass
class WebSocketConnection:
    """A WebSocket connection"""
    connection_id: str = ""
    user_id: str = ""
    user_name: str = ""
    channels: list[str] = field(default_factory=list)
    jurisdiction_codes: list[str] = field(default_factory=list)
    connected_at: datetime = field(default_factory=datetime.utcnow)
    last_activity: datetime = field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.connection_id:
            self.connection_id = f"ws-{uuid.uuid4().hex[:12]}"


@dataclass
class ThreatIntelMessage:
    """A message to broadcast on WebSocket channels"""
    message_id: str = ""
    message_type: MessageType = MessageType.SIGNAL
    channel: ThreatIntelChannel = ThreatIntelChannel.MAIN
    source_module: str = ""
    priority: str = "normal"
    title: str = ""
    summary: str = ""
    data: dict[str, Any] = field(default_factory=dict)
    jurisdiction_codes: list[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.message_id:
            self.message_id = f"msg-{uuid.uuid4().hex[:12]}"

    def to_json(self) -> str:
        """Convert message to JSON string"""
        return json.dumps({
            "message_id": self.message_id,
            "message_type": self.message_type.value,
            "channel": self.channel.value,
            "source_module": self.source_module,
            "priority": self.priority,
            "title": self.title,
            "summary": self.summary,
            "data": self.data,
            "jurisdiction_codes": self.jurisdiction_codes,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        })


class ThreatIntelWebSocketManager:
    """
    WebSocket manager for Global Threat Intelligence channels.
    
    Handles connection management, channel subscriptions, and message broadcasting.
    """

    def __init__(self):
        self._connections: dict[str, WebSocketConnection] = {}
        self._channel_subscribers: dict[str, set[str]] = {
            channel.value: set() for channel in ThreatIntelChannel
        }
        self._message_handlers: dict[str, Callable[[ThreatIntelMessage], None]] = {}
        self._message_history: list[ThreatIntelMessage] = []
        self._max_history = 1000
        self._events: list[dict[str, Any]] = []

    def _record_event(self, event_type: str, data: dict[str, Any]) -> None:
        """Record an event for audit purposes"""
        self._events.append({
            "event_type": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data,
        })

    def connect(
        self,
        user_id: str,
        user_name: str = "",
        jurisdiction_codes: Optional[list[str]] = None,
    ) -> WebSocketConnection:
        """Register a new WebSocket connection"""
        connection = WebSocketConnection(
            user_id=user_id,
            user_name=user_name,
            jurisdiction_codes=jurisdiction_codes or [],
        )
        
        self._connections[connection.connection_id] = connection
        self._record_event("connection_opened", {
            "connection_id": connection.connection_id,
            "user_id": user_id,
        })
        
        return connection

    def disconnect(self, connection_id: str) -> bool:
        """Remove a WebSocket connection"""
        connection = self._connections.get(connection_id)
        if not connection:
            return False
        
        for channel in connection.channels:
            if channel in self._channel_subscribers:
                self._channel_subscribers[channel].discard(connection_id)
        
        del self._connections[connection_id]
        self._record_event("connection_closed", {"connection_id": connection_id})
        
        return True

    def subscribe(
        self,
        connection_id: str,
        channel: ThreatIntelChannel,
    ) -> bool:
        """Subscribe a connection to a channel"""
        connection = self._connections.get(connection_id)
        if not connection:
            return False
        
        channel_name = channel.value
        if channel_name not in connection.channels:
            connection.channels.append(channel_name)
        
        self._channel_subscribers[channel_name].add(connection_id)
        self._record_event("channel_subscribed", {
            "connection_id": connection_id,
            "channel": channel_name,
        })
        
        return True

    def unsubscribe(
        self,
        connection_id: str,
        channel: ThreatIntelChannel,
    ) -> bool:
        """Unsubscribe a connection from a channel"""
        connection = self._connections.get(connection_id)
        if not connection:
            return False
        
        channel_name = channel.value
        if channel_name in connection.channels:
            connection.channels.remove(channel_name)
        
        self._channel_subscribers[channel_name].discard(connection_id)
        self._record_event("channel_unsubscribed", {
            "connection_id": connection_id,
            "channel": channel_name,
        })
        
        return True

    def register_handler(
        self,
        channel: ThreatIntelChannel,
        handler: Callable[[ThreatIntelMessage], None],
    ) -> None:
        """Register a message handler for a channel"""
        self._message_handlers[channel.value] = handler

    def broadcast(
        self,
        message: ThreatIntelMessage,
        jurisdiction_filter: bool = True,
    ) -> int:
        """Broadcast a message to all subscribers of a channel"""
        channel_name = message.channel.value
        subscribers = self._channel_subscribers.get(channel_name, set())
        
        sent_count = 0
        for conn_id in subscribers:
            connection = self._connections.get(conn_id)
            if not connection:
                continue
            
            if jurisdiction_filter and message.jurisdiction_codes:
                if connection.jurisdiction_codes:
                    if not any(j in connection.jurisdiction_codes for j in message.jurisdiction_codes):
                        continue
            
            handler = self._message_handlers.get(channel_name)
            if handler:
                try:
                    handler(message)
                    sent_count += 1
                except Exception:
                    pass
            else:
                sent_count += 1
            
            connection.last_activity = datetime.utcnow()
        
        self._message_history.append(message)
        if len(self._message_history) > self._max_history:
            self._message_history = self._message_history[-self._max_history:]
        
        self._record_event("message_broadcast", {
            "message_id": message.message_id,
            "channel": channel_name,
            "sent_count": sent_count,
        })
        
        return sent_count

    def broadcast_to_main(
        self,
        message_type: MessageType,
        source_module: str,
        title: str,
        summary: str,
        data: dict[str, Any],
        priority: str = "normal",
        jurisdiction_codes: Optional[list[str]] = None,
    ) -> ThreatIntelMessage:
        """Broadcast a message to the main threat intel channel"""
        message = ThreatIntelMessage(
            message_type=message_type,
            channel=ThreatIntelChannel.MAIN,
            source_module=source_module,
            priority=priority,
            title=title,
            summary=summary,
            data=data,
            jurisdiction_codes=jurisdiction_codes or [],
        )
        
        self.broadcast(message)
        return message

    def broadcast_dark_web_signal(
        self,
        signal_id: str,
        signal_type: str,
        title: str,
        priority_score: float,
        data: dict[str, Any],
        jurisdiction_codes: Optional[list[str]] = None,
    ) -> ThreatIntelMessage:
        """Broadcast a dark web signal"""
        priority = "critical" if priority_score >= 80 else "high" if priority_score >= 60 else "normal"
        
        message = ThreatIntelMessage(
            message_type=MessageType.SIGNAL,
            channel=ThreatIntelChannel.DARK_WEB,
            source_module="dark_web_monitor",
            priority=priority,
            title=title,
            summary=f"Dark web signal detected: {signal_type}",
            data={"signal_id": signal_id, "signal_type": signal_type, **data},
            jurisdiction_codes=jurisdiction_codes or [],
        )
        
        self.broadcast(message)
        
        if priority_score >= 70:
            message.channel = ThreatIntelChannel.MAIN
            self.broadcast(message)
        
        return message

    def broadcast_osint_signal(
        self,
        signal_id: str,
        source_type: str,
        title: str,
        relevance_score: float,
        data: dict[str, Any],
        jurisdiction_codes: Optional[list[str]] = None,
    ) -> ThreatIntelMessage:
        """Broadcast an OSINT signal"""
        priority = "high" if relevance_score >= 70 else "normal"
        
        message = ThreatIntelMessage(
            message_type=MessageType.SIGNAL,
            channel=ThreatIntelChannel.OSINT,
            source_module="osint_harvester",
            priority=priority,
            title=title,
            summary=f"OSINT signal from {source_type}",
            data={"signal_id": signal_id, "source_type": source_type, **data},
            jurisdiction_codes=jurisdiction_codes or [],
        )
        
        self.broadcast(message)
        return message

    def broadcast_keyword_spike(
        self,
        spike_id: str,
        keyword: str,
        spike_percentage: float,
        data: dict[str, Any],
    ) -> ThreatIntelMessage:
        """Broadcast a keyword spike detection"""
        priority = "high" if spike_percentage >= 500 else "normal"
        
        message = ThreatIntelMessage(
            message_type=MessageType.SPIKE,
            channel=ThreatIntelChannel.OSINT,
            source_module="osint_harvester",
            priority=priority,
            title=f"Keyword Spike: {keyword}",
            summary=f"Keyword '{keyword}' spiked {spike_percentage:.0f}%",
            data={"spike_id": spike_id, "keyword": keyword, "spike_percentage": spike_percentage, **data},
        )
        
        self.broadcast(message)
        return message

    def broadcast_extremist_update(
        self,
        update_type: str,
        node_id: str,
        title: str,
        data: dict[str, Any],
        threat_level: str = "unknown",
    ) -> ThreatIntelMessage:
        """Broadcast an extremist network update"""
        priority = "critical" if threat_level in ["severe", "critical"] else "high" if threat_level == "high" else "normal"
        
        message = ThreatIntelMessage(
            message_type=MessageType.NETWORK,
            channel=ThreatIntelChannel.EXTREMIST,
            source_module="extremist_networks",
            priority=priority,
            title=title,
            summary=f"Extremist network {update_type}",
            data={"update_type": update_type, "node_id": node_id, "threat_level": threat_level, **data},
        )
        
        self.broadcast(message)
        return message

    def broadcast_global_incident(
        self,
        incident_id: str,
        incident_type: str,
        title: str,
        severity: str,
        latitude: float,
        longitude: float,
        data: dict[str, Any],
        jurisdiction_codes: Optional[list[str]] = None,
    ) -> ThreatIntelMessage:
        """Broadcast a global incident"""
        priority = "critical" if severity == "catastrophic" else "high" if severity == "severe" else "normal"
        
        message = ThreatIntelMessage(
            message_type=MessageType.INCIDENT,
            channel=ThreatIntelChannel.INCIDENTS,
            source_module="global_incidents",
            priority=priority,
            title=title,
            summary=f"Global incident: {incident_type} ({severity})",
            data={
                "incident_id": incident_id,
                "incident_type": incident_type,
                "severity": severity,
                "latitude": latitude,
                "longitude": longitude,
                **data,
            },
            jurisdiction_codes=jurisdiction_codes or [],
        )
        
        self.broadcast(message)
        
        if severity in ["severe", "catastrophic"]:
            message.channel = ThreatIntelChannel.MAIN
            self.broadcast(message)
        
        return message

    def broadcast_threat_score(
        self,
        score_id: str,
        entity_id: str,
        entity_name: str,
        overall_score: float,
        threat_level: str,
        data: dict[str, Any],
        jurisdiction_codes: Optional[list[str]] = None,
    ) -> ThreatIntelMessage:
        """Broadcast a threat score update"""
        priority = "critical" if overall_score >= 80 else "high" if overall_score >= 60 else "normal"
        
        message = ThreatIntelMessage(
            message_type=MessageType.SCORE,
            channel=ThreatIntelChannel.SCORING,
            source_module="threat_scoring_engine",
            priority=priority,
            title=f"Threat Score: {entity_name}",
            summary=f"Threat level {threat_level} (score: {overall_score:.1f})",
            data={
                "score_id": score_id,
                "entity_id": entity_id,
                "entity_name": entity_name,
                "overall_score": overall_score,
                "threat_level": threat_level,
                **data,
            },
            jurisdiction_codes=jurisdiction_codes or [],
        )
        
        self.broadcast(message)
        
        if overall_score >= 70:
            message.channel = ThreatIntelChannel.MAIN
            self.broadcast(message)
        
        return message

    def broadcast_threat_alert(
        self,
        alert_id: str,
        title: str,
        priority: str,
        category: str,
        data: dict[str, Any],
        jurisdiction_codes: Optional[list[str]] = None,
    ) -> ThreatIntelMessage:
        """Broadcast a threat alert"""
        message = ThreatIntelMessage(
            message_type=MessageType.ALERT,
            channel=ThreatIntelChannel.ALERTS,
            source_module="threat_alerts",
            priority=priority,
            title=title,
            summary=f"Threat alert: {category}",
            data={"alert_id": alert_id, "category": category, **data},
            jurisdiction_codes=jurisdiction_codes or [],
        )
        
        self.broadcast(message)
        
        message.channel = ThreatIntelChannel.MAIN
        self.broadcast(message)
        
        if priority in ["p1_critical", "p2_high"]:
            message.channel = ThreatIntelChannel.ESCALATIONS
            self.broadcast(message)
        
        return message

    def broadcast_correlation(
        self,
        correlation_id: str,
        correlation_type: str,
        description: str,
        confidence_score: float,
        data: dict[str, Any],
        jurisdiction_codes: Optional[list[str]] = None,
    ) -> ThreatIntelMessage:
        """Broadcast a geo-threat correlation"""
        priority = "high" if confidence_score >= 0.7 else "normal"
        
        message = ThreatIntelMessage(
            message_type=MessageType.CORRELATION,
            channel=ThreatIntelChannel.INCIDENTS,
            source_module="global_incidents",
            priority=priority,
            title=f"Threat Correlation: {correlation_type}",
            summary=description,
            data={
                "correlation_id": correlation_id,
                "correlation_type": correlation_type,
                "confidence_score": confidence_score,
                **data,
            },
            jurisdiction_codes=jurisdiction_codes or [],
        )
        
        self.broadcast(message)
        return message

    def get_connection(self, connection_id: str) -> Optional[WebSocketConnection]:
        """Get a connection by ID"""
        return self._connections.get(connection_id)

    def get_all_connections(self) -> list[WebSocketConnection]:
        """Get all active connections"""
        return list(self._connections.values())

    def get_channel_subscribers(self, channel: ThreatIntelChannel) -> list[str]:
        """Get all subscribers for a channel"""
        return list(self._channel_subscribers.get(channel.value, set()))

    def get_recent_messages(
        self,
        channel: Optional[ThreatIntelChannel] = None,
        limit: int = 100,
    ) -> list[ThreatIntelMessage]:
        """Get recent messages from history"""
        messages = self._message_history
        
        if channel:
            messages = [m for m in messages if m.channel == channel]
        
        return messages[-limit:]

    def get_metrics(self) -> dict[str, Any]:
        """Get WebSocket manager metrics"""
        channel_counts = {}
        for channel in ThreatIntelChannel:
            channel_counts[channel.value] = len(self._channel_subscribers.get(channel.value, set()))
        
        return {
            "total_connections": len(self._connections),
            "channel_subscriber_counts": channel_counts,
            "message_history_size": len(self._message_history),
            "total_events": len(self._events),
        }


threat_intel_ws_manager = ThreatIntelWebSocketManager()
