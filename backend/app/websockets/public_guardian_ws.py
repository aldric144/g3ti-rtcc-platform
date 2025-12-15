"""
Public Guardian WebSocket Manager

Phase 36: Public Safety Guardian
WebSocket channels for real-time community engagement, trust score updates,
and sentiment monitoring.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set
import asyncio
import hashlib
import json
import uuid


class PublicWSChannel(Enum):
    ENGAGEMENT = "engagement"
    TRUST = "trust"
    SENTIMENT = "sentiment"


class EngagementUpdateType(Enum):
    NEW_EVENT = "new_event"
    EVENT_UPDATE = "event_update"
    EVENT_CANCELLED = "event_cancelled"
    EVENT_REMINDER = "event_reminder"
    NEW_ALERT = "new_alert"
    ALERT_UPDATE = "alert_update"
    ALERT_DEACTIVATED = "alert_deactivated"
    COMMUNITY_NOTICE = "community_notice"


class TrustUpdateType(Enum):
    SCORE_UPDATE = "score_update"
    NEIGHBORHOOD_UPDATE = "neighborhood_update"
    FAIRNESS_AUDIT = "fairness_audit"
    BIAS_AUDIT = "bias_audit"
    METRIC_CHANGE = "metric_change"
    TREND_ALERT = "trend_alert"


class SentimentUpdateType(Enum):
    NEW_FEEDBACK = "new_feedback"
    SENTIMENT_SHIFT = "sentiment_shift"
    TREND_DETECTED = "trend_detected"
    CONCERN_SPIKE = "concern_spike"
    PRAISE_SPIKE = "praise_spike"
    NEIGHBORHOOD_INSIGHT = "neighborhood_insight"


class UpdateSeverity(Enum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class PublicWSConnection:
    connection_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    channels: Set[PublicWSChannel] = field(default_factory=set)
    connected_at: datetime = field(default_factory=datetime.utcnow)
    last_activity: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "connection_id": self.connection_id,
            "channels": [c.value for c in self.channels],
            "connected_at": self.connected_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "metadata": self.metadata,
        }


@dataclass
class PublicWSMessage:
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    channel: PublicWSChannel = PublicWSChannel.ENGAGEMENT
    update_type: str = ""
    severity: UpdateSeverity = UpdateSeverity.INFO
    title: str = ""
    message: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    message_hash: str = ""

    def __post_init__(self):
        if not self.message_hash:
            self.message_hash = self._generate_hash()

    def _generate_hash(self) -> str:
        content = f"{self.message_id}{self.channel.value}{self.timestamp.isoformat()}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "message_id": self.message_id,
            "channel": self.channel.value,
            "update_type": self.update_type,
            "severity": self.severity.value,
            "title": self.title,
            "message": self.message,
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
            "message_hash": self.message_hash,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict())


@dataclass
class EngagementUpdate:
    update_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    update_type: EngagementUpdateType = EngagementUpdateType.COMMUNITY_NOTICE
    event_id: Optional[str] = None
    alert_id: Optional[str] = None
    title: str = ""
    description: str = ""
    affected_areas: List[str] = field(default_factory=list)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    severity: UpdateSeverity = UpdateSeverity.INFO
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "update_id": self.update_id,
            "update_type": self.update_type.value,
            "event_id": self.event_id,
            "alert_id": self.alert_id,
            "title": self.title,
            "description": self.description,
            "affected_areas": self.affected_areas,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "severity": self.severity.value,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class TrustUpdate:
    update_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    update_type: TrustUpdateType = TrustUpdateType.SCORE_UPDATE
    previous_score: float = 0.0
    current_score: float = 0.0
    change: float = 0.0
    trust_level: str = ""
    neighborhood: Optional[str] = None
    metric: Optional[str] = None
    audit_result: Optional[Dict[str, Any]] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "update_id": self.update_id,
            "update_type": self.update_type.value,
            "previous_score": self.previous_score,
            "current_score": self.current_score,
            "change": self.change,
            "trust_level": self.trust_level,
            "neighborhood": self.neighborhood,
            "metric": self.metric,
            "audit_result": self.audit_result,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class SentimentUpdate:
    update_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    update_type: SentimentUpdateType = SentimentUpdateType.NEW_FEEDBACK
    feedback_id: Optional[str] = None
    neighborhood: Optional[str] = None
    sentiment_level: str = ""
    sentiment_score: float = 0.0
    trend_direction: str = ""
    category: Optional[str] = None
    count: int = 0
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "update_id": self.update_id,
            "update_type": self.update_type.value,
            "feedback_id": self.feedback_id,
            "neighborhood": self.neighborhood,
            "sentiment_level": self.sentiment_level,
            "sentiment_score": self.sentiment_score,
            "trend_direction": self.trend_direction,
            "category": self.category,
            "count": self.count,
            "timestamp": self.timestamp.isoformat(),
        }


class PublicGuardianWSManager:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.connections: Dict[str, PublicWSConnection] = {}
        self.channel_subscribers: Dict[PublicWSChannel, Set[str]] = {
            channel: set() for channel in PublicWSChannel
        }
        self.message_history: List[PublicWSMessage] = []
        self.message_handlers: Dict[PublicWSChannel, List[Callable]] = {
            channel: [] for channel in PublicWSChannel
        }
        self.statistics = {
            "total_connections": 0,
            "active_connections": 0,
            "messages_sent": 0,
            "engagement_updates": 0,
            "trust_updates": 0,
            "sentiment_updates": 0,
            "broadcasts": 0,
        }

    async def connect(
        self,
        connection_id: Optional[str] = None,
        channels: Optional[List[PublicWSChannel]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> PublicWSConnection:
        connection = PublicWSConnection(
            connection_id=connection_id or str(uuid.uuid4()),
            channels=set(channels) if channels else {PublicWSChannel.ENGAGEMENT},
            metadata=metadata or {},
        )

        self.connections[connection.connection_id] = connection

        for channel in connection.channels:
            self.channel_subscribers[channel].add(connection.connection_id)

        self.statistics["total_connections"] += 1
        self.statistics["active_connections"] = len(self.connections)

        return connection

    async def disconnect(self, connection_id: str) -> bool:
        connection = self.connections.get(connection_id)
        if not connection:
            return False

        for channel in connection.channels:
            self.channel_subscribers[channel].discard(connection_id)

        del self.connections[connection_id]
        self.statistics["active_connections"] = len(self.connections)

        return True

    async def subscribe(
        self,
        connection_id: str,
        channel: PublicWSChannel,
    ) -> bool:
        connection = self.connections.get(connection_id)
        if not connection:
            return False

        connection.channels.add(channel)
        self.channel_subscribers[channel].add(connection_id)
        connection.last_activity = datetime.utcnow()

        return True

    async def unsubscribe(
        self,
        connection_id: str,
        channel: PublicWSChannel,
    ) -> bool:
        connection = self.connections.get(connection_id)
        if not connection:
            return False

        connection.channels.discard(channel)
        self.channel_subscribers[channel].discard(connection_id)
        connection.last_activity = datetime.utcnow()

        return True

    async def broadcast_to_channel(
        self,
        channel: PublicWSChannel,
        message: PublicWSMessage,
    ) -> int:
        subscribers = self.channel_subscribers.get(channel, set())
        sent_count = 0

        for connection_id in subscribers:
            connection = self.connections.get(connection_id)
            if connection:
                connection.last_activity = datetime.utcnow()
                sent_count += 1

        self.message_history.append(message)
        self.statistics["messages_sent"] += sent_count
        self.statistics["broadcasts"] += 1

        for handler in self.message_handlers.get(channel, []):
            try:
                await handler(message)
            except Exception:
                pass

        return sent_count

    async def broadcast_engagement_update(
        self,
        update: EngagementUpdate,
    ) -> int:
        message = PublicWSMessage(
            channel=PublicWSChannel.ENGAGEMENT,
            update_type=update.update_type.value,
            severity=update.severity,
            title=update.title,
            message=update.description,
            data=update.to_dict(),
        )

        self.statistics["engagement_updates"] += 1
        return await self.broadcast_to_channel(PublicWSChannel.ENGAGEMENT, message)

    async def broadcast_trust_update(
        self,
        update: TrustUpdate,
    ) -> int:
        severity = UpdateSeverity.INFO
        if abs(update.change) > 5:
            severity = UpdateSeverity.HIGH
        elif abs(update.change) > 2:
            severity = UpdateSeverity.MEDIUM

        title = f"Trust Score Update: {update.current_score:.1f}"
        if update.neighborhood:
            title = f"{update.neighborhood} Trust Update: {update.current_score:.1f}"

        message = PublicWSMessage(
            channel=PublicWSChannel.TRUST,
            update_type=update.update_type.value,
            severity=severity,
            title=title,
            message=f"Score changed by {update.change:+.1f} points",
            data=update.to_dict(),
        )

        self.statistics["trust_updates"] += 1
        return await self.broadcast_to_channel(PublicWSChannel.TRUST, message)

    async def broadcast_sentiment_update(
        self,
        update: SentimentUpdate,
    ) -> int:
        severity = UpdateSeverity.INFO
        if update.update_type in [SentimentUpdateType.CONCERN_SPIKE]:
            severity = UpdateSeverity.HIGH
        elif update.update_type in [SentimentUpdateType.SENTIMENT_SHIFT, SentimentUpdateType.TREND_DETECTED]:
            severity = UpdateSeverity.MEDIUM

        title = f"Sentiment Update: {update.sentiment_level}"
        if update.neighborhood:
            title = f"{update.neighborhood} Sentiment: {update.sentiment_level}"

        message = PublicWSMessage(
            channel=PublicWSChannel.SENTIMENT,
            update_type=update.update_type.value,
            severity=severity,
            title=title,
            message=f"Sentiment score: {update.sentiment_score:.2f}",
            data=update.to_dict(),
        )

        self.statistics["sentiment_updates"] += 1
        return await self.broadcast_to_channel(PublicWSChannel.SENTIMENT, message)

    async def broadcast_new_event(
        self,
        event_id: str,
        title: str,
        description: str,
        location: str,
        start_time: datetime,
        affected_areas: Optional[List[str]] = None,
    ) -> int:
        update = EngagementUpdate(
            update_type=EngagementUpdateType.NEW_EVENT,
            event_id=event_id,
            title=title,
            description=f"{description} at {location}",
            affected_areas=affected_areas or [],
            start_time=start_time,
            severity=UpdateSeverity.INFO,
        )
        return await self.broadcast_engagement_update(update)

    async def broadcast_new_alert(
        self,
        alert_id: str,
        title: str,
        message: str,
        severity: UpdateSeverity,
        affected_areas: Optional[List[str]] = None,
        end_time: Optional[datetime] = None,
    ) -> int:
        update = EngagementUpdate(
            update_type=EngagementUpdateType.NEW_ALERT,
            alert_id=alert_id,
            title=title,
            description=message,
            affected_areas=affected_areas or [],
            end_time=end_time,
            severity=severity,
        )
        return await self.broadcast_engagement_update(update)

    async def broadcast_score_change(
        self,
        previous_score: float,
        current_score: float,
        trust_level: str,
        neighborhood: Optional[str] = None,
    ) -> int:
        update = TrustUpdate(
            update_type=TrustUpdateType.SCORE_UPDATE if not neighborhood else TrustUpdateType.NEIGHBORHOOD_UPDATE,
            previous_score=previous_score,
            current_score=current_score,
            change=current_score - previous_score,
            trust_level=trust_level,
            neighborhood=neighborhood,
        )
        return await self.broadcast_trust_update(update)

    async def broadcast_new_feedback(
        self,
        feedback_id: str,
        sentiment_level: str,
        sentiment_score: float,
        neighborhood: Optional[str] = None,
        category: Optional[str] = None,
    ) -> int:
        update = SentimentUpdate(
            update_type=SentimentUpdateType.NEW_FEEDBACK,
            feedback_id=feedback_id,
            sentiment_level=sentiment_level,
            sentiment_score=sentiment_score,
            neighborhood=neighborhood,
            category=category,
        )
        return await self.broadcast_sentiment_update(update)

    async def broadcast_sentiment_trend(
        self,
        trend_direction: str,
        sentiment_level: str,
        sentiment_score: float,
        neighborhood: Optional[str] = None,
        category: Optional[str] = None,
        count: int = 0,
    ) -> int:
        update = SentimentUpdate(
            update_type=SentimentUpdateType.TREND_DETECTED,
            sentiment_level=sentiment_level,
            sentiment_score=sentiment_score,
            trend_direction=trend_direction,
            neighborhood=neighborhood,
            category=category,
            count=count,
        )
        return await self.broadcast_sentiment_update(update)

    def register_handler(
        self,
        channel: PublicWSChannel,
        handler: Callable,
    ):
        self.message_handlers[channel].append(handler)

    def unregister_handler(
        self,
        channel: PublicWSChannel,
        handler: Callable,
    ):
        if handler in self.message_handlers[channel]:
            self.message_handlers[channel].remove(handler)

    def get_connection(self, connection_id: str) -> Optional[PublicWSConnection]:
        return self.connections.get(connection_id)

    def get_channel_subscribers(self, channel: PublicWSChannel) -> List[str]:
        return list(self.channel_subscribers.get(channel, set()))

    def get_message_history(
        self,
        channel: Optional[PublicWSChannel] = None,
        limit: int = 100,
    ) -> List[PublicWSMessage]:
        if channel:
            filtered = [m for m in self.message_history if m.channel == channel]
        else:
            filtered = self.message_history

        return filtered[-limit:]

    def get_statistics(self) -> Dict[str, Any]:
        return {
            **self.statistics,
            "connections_by_channel": {
                channel.value: len(subscribers)
                for channel, subscribers in self.channel_subscribers.items()
            },
            "message_history_size": len(self.message_history),
        }
