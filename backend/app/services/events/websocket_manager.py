"""
WebSocket connection manager for the G3TI RTCC-UIP Backend.

This module provides WebSocket connection management for real-time
event broadcasting to connected clients.

Features:
- Connection lifecycle management
- Client subscription management
- Broadcast and targeted messaging
- Heartbeat monitoring
- Connection authentication
"""

import asyncio
import json
import uuid
from collections.abc import Callable, Coroutine
from datetime import UTC, datetime
from typing import Any

from fastapi import WebSocket
from starlette.websockets import WebSocketState

from app.core.config import settings
from app.core.logging import get_logger
from app.schemas.events import (
    EventPriority,
    EventSource,
    EventSubscription,
    EventType,
    WebSocketMessage,
    WebSocketMessageType,
)

logger = get_logger(__name__)


class ClientConnection:
    """
    Represents a connected WebSocket client.

    Tracks connection state, subscriptions, and metadata.
    """

    def __init__(
        self,
        websocket: WebSocket,
        client_id: str,
        user_id: str | None = None,
        user_role: str | None = None,
    ) -> None:
        """
        Initialize client connection.

        Args:
            websocket: WebSocket connection
            client_id: Unique client identifier
            user_id: Authenticated user ID
            user_role: User's role for authorization
        """
        self.websocket = websocket
        self.client_id = client_id
        self.user_id = user_id
        self.user_role = user_role
        self.connected_at = datetime.now(UTC)
        self.last_activity = datetime.now(UTC)
        self.subscription = EventSubscription()
        self.message_count = 0
        self.is_authenticated = user_id is not None

    def update_activity(self) -> None:
        """Update last activity timestamp."""
        self.last_activity = datetime.now(UTC)

    def matches_event(
        self,
        event_type: EventType,
        source: EventSource,
        priority: EventPriority,
        location: dict[str, float] | None = None,
        tags: list[str] | None = None,
    ) -> bool:
        """
        Check if client subscription matches an event.

        Args:
            event_type: Event type
            source: Event source
            priority: Event priority
            location: Event location (lat, lon)
            tags: Event tags

        Returns:
            bool: True if client should receive the event
        """
        sub = self.subscription

        # Check event type filter
        if sub.event_types and event_type not in sub.event_types:
            return False

        # Check source filter
        if sub.sources and source not in sub.sources:
            return False

        # Check priority filter
        if sub.priorities and priority not in sub.priorities:
            return False

        # Check tag filter
        if sub.tags and tags:
            if not any(tag in sub.tags for tag in tags):
                return False

        # Check geographic bounds
        if sub.geographic_bounds and location:
            bounds = sub.geographic_bounds
            lat, lon = location.get("lat", 0), location.get("lon", 0)
            if not (
                bounds.get("south", -90) <= lat <= bounds.get("north", 90)
                and bounds.get("west", -180) <= lon <= bounds.get("east", 180)
            ):
                return False

        return True


class WebSocketManager:
    """
    Manages WebSocket connections and message broadcasting.

    Provides methods for:
    - Accepting and tracking connections
    - Broadcasting events to subscribed clients
    - Handling client subscriptions
    - Monitoring connection health
    """

    def __init__(self) -> None:
        """Initialize the WebSocket manager."""
        self._connections: dict[str, ClientConnection] = {}
        self._user_connections: dict[str, set[str]] = {}  # user_id -> client_ids
        self._heartbeat_task: asyncio.Task | None = None
        self._running = False
        self._message_handlers: dict[
            WebSocketMessageType,
            Callable[[ClientConnection, dict[str, Any]], Coroutine[Any, Any, None]],
        ] = {}

        # Register default handlers
        self._register_default_handlers()

    def _register_default_handlers(self) -> None:
        """Register default message handlers."""
        self._message_handlers[WebSocketMessageType.SUBSCRIBE] = self._handle_subscribe
        self._message_handlers[WebSocketMessageType.UNSUBSCRIBE] = self._handle_unsubscribe
        self._message_handlers[WebSocketMessageType.PING] = self._handle_ping
        self._message_handlers[WebSocketMessageType.ACKNOWLEDGE] = self._handle_acknowledge

    async def start(self) -> None:
        """Start the WebSocket manager and background tasks."""
        if self._running:
            return

        self._running = True
        self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        logger.info("websocket_manager_started")

    async def stop(self) -> None:
        """Stop the WebSocket manager and close all connections."""
        self._running = False

        if self._heartbeat_task:
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass

        # Close all connections
        for client_id in list(self._connections.keys()):
            await self.disconnect(client_id)

        logger.info("websocket_manager_stopped")

    async def connect(
        self, websocket: WebSocket, user_id: str | None = None, user_role: str | None = None
    ) -> str:
        """
        Accept a new WebSocket connection.

        Args:
            websocket: WebSocket connection
            user_id: Authenticated user ID
            user_role: User's role

        Returns:
            str: Client ID for the connection
        """
        # Check connection limit
        if len(self._connections) >= settings.ws_max_connections:
            await websocket.close(code=1013, reason="Server at capacity")
            raise ConnectionError("Maximum connections reached")

        await websocket.accept()

        client_id = str(uuid.uuid4())
        connection = ClientConnection(
            websocket=websocket, client_id=client_id, user_id=user_id, user_role=user_role
        )

        self._connections[client_id] = connection

        # Track user connections
        if user_id:
            if user_id not in self._user_connections:
                self._user_connections[user_id] = set()
            self._user_connections[user_id].add(client_id)

        # Send connected message
        await self._send_message(
            connection,
            WebSocketMessage(
                type=WebSocketMessageType.CONNECTED,
                payload={
                    "client_id": client_id,
                    "server_time": datetime.now(UTC).isoformat(),
                    "heartbeat_interval": settings.ws_heartbeat_interval,
                },
            ),
        )

        logger.info(
            "websocket_connected",
            client_id=client_id,
            user_id=user_id,
            total_connections=len(self._connections),
        )

        return client_id

    async def disconnect(self, client_id: str) -> None:
        """
        Disconnect a client.

        Args:
            client_id: Client identifier
        """
        connection = self._connections.pop(client_id, None)
        if not connection:
            return

        # Remove from user connections
        if connection.user_id and connection.user_id in self._user_connections:
            self._user_connections[connection.user_id].discard(client_id)
            if not self._user_connections[connection.user_id]:
                del self._user_connections[connection.user_id]

        # Close WebSocket if still open
        if connection.websocket.client_state == WebSocketState.CONNECTED:
            try:
                await connection.websocket.close()
            except Exception:
                pass

        logger.info(
            "websocket_disconnected",
            client_id=client_id,
            user_id=connection.user_id,
            total_connections=len(self._connections),
        )

    async def handle_message(self, client_id: str, data: str | bytes) -> None:
        """
        Handle an incoming WebSocket message.

        Args:
            client_id: Client identifier
            data: Raw message data
        """
        connection = self._connections.get(client_id)
        if not connection:
            return

        connection.update_activity()

        try:
            if isinstance(data, bytes):
                data = data.decode("utf-8")

            message_data = json.loads(data)
            message_type = WebSocketMessageType(message_data.get("type"))
            payload = message_data.get("payload", {})

            handler = self._message_handlers.get(message_type)
            if handler:
                await handler(connection, payload)
            else:
                await self._send_error(connection, f"Unknown message type: {message_type}")

        except json.JSONDecodeError:
            await self._send_error(connection, "Invalid JSON message")
        except ValueError as e:
            await self._send_error(connection, str(e))
        except Exception as e:
            logger.error("websocket_message_error", client_id=client_id, error=str(e))
            await self._send_error(connection, "Internal error processing message")

    async def broadcast_event(
        self,
        event_type: EventType,
        source: EventSource,
        priority: EventPriority,
        payload: dict[str, Any],
        location: dict[str, float] | None = None,
        tags: list[str] | None = None,
    ) -> int:
        """
        Broadcast an event to all subscribed clients.

        Args:
            event_type: Event type
            source: Event source
            priority: Event priority
            payload: Event payload
            location: Event location
            tags: Event tags

        Returns:
            int: Number of clients that received the event
        """
        message = WebSocketMessage(
            type=WebSocketMessageType.EVENT,
            payload={
                "event_type": event_type.value,
                "source": source.value,
                "priority": priority.value,
                "data": payload,
                "location": location,
                "tags": tags,
                "timestamp": datetime.now(UTC).isoformat(),
            },
            message_id=str(uuid.uuid4()),
        )

        sent_count = 0
        for connection in list(self._connections.values()):
            if connection.matches_event(event_type, source, priority, location, tags):
                try:
                    await self._send_message(connection, message)
                    sent_count += 1
                except Exception as e:
                    logger.warning(
                        "broadcast_send_error", client_id=connection.client_id, error=str(e)
                    )

        logger.debug(
            "event_broadcast",
            event_type=event_type.value,
            source=source.value,
            recipients=sent_count,
        )

        return sent_count

    async def send_to_user(self, user_id: str, message: WebSocketMessage) -> int:
        """
        Send a message to all connections for a specific user.

        Args:
            user_id: User identifier
            message: Message to send

        Returns:
            int: Number of connections that received the message
        """
        client_ids = self._user_connections.get(user_id, set())
        sent_count = 0

        for client_id in client_ids:
            connection = self._connections.get(client_id)
            if connection:
                try:
                    await self._send_message(connection, message)
                    sent_count += 1
                except Exception:
                    pass

        return sent_count

    async def send_to_client(self, client_id: str, message: WebSocketMessage) -> bool:
        """
        Send a message to a specific client.

        Args:
            client_id: Client identifier
            message: Message to send

        Returns:
            bool: True if sent successfully
        """
        connection = self._connections.get(client_id)
        if not connection:
            return False

        try:
            await self._send_message(connection, message)
            return True
        except Exception:
            return False

    def get_connection_count(self) -> int:
        """Get the number of active connections."""
        return len(self._connections)

    def get_user_connection_count(self, user_id: str) -> int:
        """Get the number of connections for a specific user."""
        return len(self._user_connections.get(user_id, set()))

    async def broadcast_ai_insight(
        self,
        insight_type: str,
        payload: dict[str, Any],
        priority: EventPriority = EventPriority.MEDIUM,
        related_entities: list[str] | None = None,
        location: dict[str, float] | None = None,
    ) -> int:
        """
        Broadcast an AI insight event to subscribed clients.

        This method is specifically designed for AI engine events including:
        - anomaly_detected
        - pattern_shift
        - high_risk_entity_updated
        - relationship_discovered
        - predictive_alert

        Args:
            insight_type: Type of AI insight (anomaly_detected, pattern_shift, etc.)
            payload: Insight data payload
            priority: Event priority level
            related_entities: List of related entity IDs
            location: Geographic location if applicable

        Returns:
            int: Number of clients that received the insight
        """
        # Map insight type to event type
        event_type_map = {
            "anomaly_detected": EventType.AI_ANOMALY_DETECTED,
            "pattern_shift": EventType.AI_PATTERN_SHIFT,
            "high_risk_entity_updated": EventType.AI_HIGH_RISK_ENTITY,
            "relationship_discovered": EventType.AI_RELATIONSHIP_DISCOVERED,
            "predictive_alert": EventType.AI_PREDICTIVE_ALERT,
            "entity_resolved": EventType.AI_ENTITY_RESOLVED,
            "query_result": EventType.AI_QUERY_RESULT,
        }

        event_type = event_type_map.get(insight_type, EventType.AI_ANOMALY_DETECTED)

        message = WebSocketMessage(
            type=WebSocketMessageType.EVENT,
            payload={
                "event_type": event_type.value,
                "source": EventSource.AI_ENGINE.value,
                "priority": priority.value,
                "insight_type": insight_type,
                "data": payload,
                "related_entities": related_entities or [],
                "location": location,
                "timestamp": datetime.now(UTC).isoformat(),
            },
            message_id=str(uuid.uuid4()),
        )

        sent_count = 0
        for connection in list(self._connections.values()):
            # Check if client is subscribed to AI events
            if connection.matches_event(
                event_type, EventSource.AI_ENGINE, priority, location, ["ai", "intelligence"]
            ):
                try:
                    await self._send_message(connection, message)
                    sent_count += 1
                except Exception as e:
                    logger.warning(
                        "ai_insight_send_error", client_id=connection.client_id, error=str(e)
                    )

        logger.debug(
            "ai_insight_broadcast",
            insight_type=insight_type,
            event_type=event_type.value,
            recipients=sent_count,
        )

        return sent_count

    async def broadcast_ai_anomaly(
        self,
        anomaly_id: str,
        anomaly_type: str,
        severity: str,
        description: str,
        confidence: float,
        entities: list[str] | None = None,
        location: dict[str, float] | None = None,
    ) -> int:
        """
        Broadcast an anomaly detection event.

        Args:
            anomaly_id: Unique anomaly identifier
            anomaly_type: Type of anomaly detected
            severity: Severity level (critical, high, medium, low)
            description: Human-readable description
            confidence: Detection confidence (0-1)
            entities: Related entity IDs
            location: Geographic location

        Returns:
            int: Number of clients notified
        """
        priority_map = {
            "critical": EventPriority.CRITICAL,
            "high": EventPriority.HIGH,
            "medium": EventPriority.MEDIUM,
            "low": EventPriority.LOW,
        }

        return await self.broadcast_ai_insight(
            insight_type="anomaly_detected",
            payload={
                "anomaly_id": anomaly_id,
                "anomaly_type": anomaly_type,
                "severity": severity,
                "description": description,
                "confidence": confidence,
                "detected_at": datetime.now(UTC).isoformat(),
            },
            priority=priority_map.get(severity.lower(), EventPriority.MEDIUM),
            related_entities=entities,
            location=location,
        )

    async def broadcast_ai_pattern(
        self,
        pattern_id: str,
        pattern_type: str,
        description: str,
        strength: float,
        entities: list[str] | None = None,
        locations: list[dict[str, float]] | None = None,
    ) -> int:
        """
        Broadcast a pattern shift event.

        Args:
            pattern_id: Unique pattern identifier
            pattern_type: Type of pattern detected
            description: Human-readable description
            strength: Pattern strength (0-1)
            entities: Related entity IDs
            locations: Geographic locations involved

        Returns:
            int: Number of clients notified
        """
        return await self.broadcast_ai_insight(
            insight_type="pattern_shift",
            payload={
                "pattern_id": pattern_id,
                "pattern_type": pattern_type,
                "description": description,
                "strength": strength,
                "locations": locations or [],
                "detected_at": datetime.now(UTC).isoformat(),
            },
            priority=EventPriority.MEDIUM if strength < 0.7 else EventPriority.HIGH,
            related_entities=entities,
            location=locations[0] if locations else None,
        )

    async def broadcast_ai_risk_update(
        self,
        entity_id: str,
        entity_type: str,
        risk_score: float,
        risk_level: str,
        factors: list[dict[str, Any]] | None = None,
    ) -> int:
        """
        Broadcast a high-risk entity update event.

        Args:
            entity_id: Entity identifier
            entity_type: Type of entity (person, vehicle, address, weapon)
            risk_score: Calculated risk score (0-100)
            risk_level: Risk level (critical, high, medium, low, minimal)
            factors: Contributing risk factors

        Returns:
            int: Number of clients notified
        """
        priority_map = {
            "critical": EventPriority.CRITICAL,
            "high": EventPriority.HIGH,
            "medium": EventPriority.MEDIUM,
            "low": EventPriority.LOW,
            "minimal": EventPriority.INFO,
        }

        return await self.broadcast_ai_insight(
            insight_type="high_risk_entity_updated",
            payload={
                "entity_id": entity_id,
                "entity_type": entity_type,
                "risk_score": risk_score,
                "risk_level": risk_level,
                "factors": factors or [],
                "updated_at": datetime.now(UTC).isoformat(),
            },
            priority=priority_map.get(risk_level.lower(), EventPriority.MEDIUM),
            related_entities=[entity_id],
        )

    async def broadcast_ai_prediction(
        self,
        prediction_id: str,
        prediction_type: str,
        description: str,
        probability: float,
        time_horizon: str,
        entities: list[str] | None = None,
        location: dict[str, float] | None = None,
    ) -> int:
        """
        Broadcast a predictive alert event.

        Args:
            prediction_id: Unique prediction identifier
            prediction_type: Type of prediction
            description: Human-readable description
            probability: Prediction probability (0-1)
            time_horizon: Time horizon for prediction
            entities: Related entity IDs
            location: Predicted location

        Returns:
            int: Number of clients notified
        """
        priority = EventPriority.HIGH if probability >= 0.7 else EventPriority.MEDIUM

        return await self.broadcast_ai_insight(
            insight_type="predictive_alert",
            payload={
                "prediction_id": prediction_id,
                "prediction_type": prediction_type,
                "description": description,
                "probability": probability,
                "time_horizon": time_horizon,
                "predicted_at": datetime.now(UTC).isoformat(),
            },
            priority=priority,
            related_entities=entities,
            location=location,
        )

    async def _send_message(self, connection: ClientConnection, message: WebSocketMessage) -> None:
        """Send a message to a client."""
        if connection.websocket.client_state != WebSocketState.CONNECTED:
            return

        await connection.websocket.send_text(message.model_dump_json())
        connection.message_count += 1

    async def _send_error(self, connection: ClientConnection, error_message: str) -> None:
        """Send an error message to a client."""
        await self._send_message(
            connection,
            WebSocketMessage(type=WebSocketMessageType.ERROR, payload={"error": error_message}),
        )

    async def _handle_subscribe(
        self, connection: ClientConnection, payload: dict[str, Any]
    ) -> None:
        """Handle subscription request."""
        try:
            subscription = EventSubscription(**payload)
            connection.subscription = subscription

            await self._send_message(
                connection,
                WebSocketMessage(
                    type=WebSocketMessageType.SUBSCRIBED,
                    payload={"subscription": subscription.model_dump()},
                ),
            )

            logger.debug(
                "client_subscribed",
                client_id=connection.client_id,
                event_types=[et.value for et in subscription.event_types],
            )

        except Exception as e:
            await self._send_error(connection, f"Invalid subscription: {e}")

    async def _handle_unsubscribe(
        self, connection: ClientConnection, payload: dict[str, Any]
    ) -> None:
        """Handle unsubscription request."""
        connection.subscription = EventSubscription()

        await self._send_message(
            connection, WebSocketMessage(type=WebSocketMessageType.UNSUBSCRIBED, payload={})
        )

    async def _handle_ping(self, connection: ClientConnection, payload: dict[str, Any]) -> None:
        """Handle ping request."""
        await self._send_message(
            connection,
            WebSocketMessage(
                type=WebSocketMessageType.PONG,
                payload={"server_time": datetime.now(UTC).isoformat()},
            ),
        )

    async def _handle_acknowledge(
        self, connection: ClientConnection, payload: dict[str, Any]
    ) -> None:
        """Handle event acknowledgment."""
        event_id = payload.get("event_id")
        if event_id:
            await self._send_message(
                connection,
                WebSocketMessage(
                    type=WebSocketMessageType.ACKNOWLEDGED, payload={"event_id": event_id}
                ),
            )

    async def _heartbeat_loop(self) -> None:
        """Background task to check connection health."""
        while self._running:
            try:
                await asyncio.sleep(settings.ws_heartbeat_interval)

                now = datetime.now(UTC)
                timeout_threshold = settings.ws_heartbeat_interval * 3

                for client_id in list(self._connections.keys()):
                    connection = self._connections.get(client_id)
                    if not connection:
                        continue

                    # Check for stale connections
                    inactive_seconds = (now - connection.last_activity).total_seconds()
                    if inactive_seconds > timeout_threshold:
                        logger.info(
                            "disconnecting_stale_client",
                            client_id=client_id,
                            inactive_seconds=inactive_seconds,
                        )
                        await self.disconnect(client_id)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("heartbeat_error", error=str(e))


# Global WebSocket manager instance
_websocket_manager: WebSocketManager | None = None


def get_websocket_manager() -> WebSocketManager:
    """Get the WebSocket manager instance."""
    global _websocket_manager
    if _websocket_manager is None:
        _websocket_manager = WebSocketManager()
    return _websocket_manager
