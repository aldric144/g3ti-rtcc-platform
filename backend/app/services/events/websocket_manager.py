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
- Normalized event emission from all data sources
- Entity creation notifications
- Priority-based event filtering
- Geographic bounds filtering
- Redis pub/sub integration for distributed broadcasting
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
from app.core.logging import audit_logger, get_logger
from app.schemas.events import (
    EventCreate,
    EventPriority,
    EventSource,
    EventSubscription,
    EventType,
    WebSocketMessage,
    WebSocketMessageType,
)

logger = get_logger(__name__)


# Event source to human-readable name mapping
SOURCE_DISPLAY_NAMES: dict[EventSource, str] = {
    EventSource.FLOCK: "Flock LPR",
    EventSource.SHOTSPOTTER: "ShotSpotter",
    EventSource.MILESTONE: "Milestone VMS",
    EventSource.ONESOLUTION: "OneSolution CAD/RMS",
    EventSource.NESS: "NESS",
    EventSource.BWC: "Body-Worn Camera",
    EventSource.HOTSHEETS: "HotSheets BOLO",
    EventSource.MANUAL: "Manual Entry",
    EventSource.SYSTEM: "System",
}


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

    async def broadcast_normalized_event(self, event: EventCreate) -> int:
        """
        Broadcast a normalized event from any data source.

        This method handles events from all integrated sources (Flock, ShotSpotter,
        Milestone, OneSolution, NESS, BWC, HotSheets) and broadcasts them to
        subscribed clients based on their subscription filters.

        Args:
            event: Normalized EventCreate object

        Returns:
            int: Number of clients that received the event
        """
        location = None
        if event.latitude is not None and event.longitude is not None:
            location = {"lat": event.latitude, "lon": event.longitude}

        source_name = SOURCE_DISPLAY_NAMES.get(event.source, event.source.value)

        payload = {
            "id": event.external_id or str(uuid.uuid4()),
            "title": event.title,
            "description": event.description,
            "source": event.source.value,
            "source_display": source_name,
            "event_type": event.event_type.value,
            "priority": event.priority.value,
            "location": location,
            "address": event.address,
            "tags": event.tags,
            "metadata": event.metadata,
            "timestamp": (
                event.timestamp.isoformat() if event.timestamp else datetime.now(UTC).isoformat()
            ),
        }

        sent_count = await self.broadcast_event(
            event_type=event.event_type,
            source=event.source,
            priority=event.priority,
            payload=payload,
            location=location,
            tags=event.tags,
        )

        logger.info(
            "normalized_event_broadcast",
            source=event.source.value,
            event_type=event.event_type.value,
            priority=event.priority.value,
            recipients=sent_count,
        )

        return sent_count

    async def broadcast_entity_created(
        self,
        entity_type: str,
        entity_id: str,
        entity_data: dict[str, Any],
        source_event_id: str | None = None,
    ) -> int:
        """
        Broadcast an entity creation notification.

        Called when a new entity (Person, Vehicle, Incident, etc.) is
        auto-created from an ingested event.

        Args:
            entity_type: Type of entity (Person, Vehicle, Incident, etc.)
            entity_id: Neo4j node ID
            entity_data: Entity properties
            source_event_id: ID of the event that triggered creation

        Returns:
            int: Number of clients that received the notification
        """
        message = WebSocketMessage(
            type=WebSocketMessageType.EVENT,
            payload={
                "event_type": "entity_created",
                "entity_type": entity_type,
                "entity_id": entity_id,
                "entity_data": entity_data,
                "source_event_id": source_event_id,
                "timestamp": datetime.now(UTC).isoformat(),
            },
            message_id=str(uuid.uuid4()),
        )

        sent_count = 0
        for connection in list(self._connections.values()):
            if connection.subscription.include_entity_updates:
                try:
                    await self._send_message(connection, message)
                    sent_count += 1
                except Exception as e:
                    logger.warning(
                        "entity_broadcast_error",
                        client_id=connection.client_id,
                        error=str(e),
                    )

        logger.debug(
            "entity_created_broadcast",
            entity_type=entity_type,
            entity_id=entity_id,
            recipients=sent_count,
        )

        return sent_count

    async def broadcast_alert(
        self,
        alert_type: str,
        title: str,
        message_text: str,
        priority: EventPriority = EventPriority.HIGH,
        source: EventSource | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> int:
        """
        Broadcast a system alert to all connected clients.

        Used for critical notifications like BOLO matches, officer safety
        alerts, or system warnings.

        Args:
            alert_type: Type of alert (bolo_match, officer_safety, system_warning)
            title: Alert title
            message_text: Alert message
            priority: Alert priority
            source: Source system if applicable
            metadata: Additional alert data

        Returns:
            int: Number of clients that received the alert
        """
        message = WebSocketMessage(
            type=WebSocketMessageType.ALERT,
            payload={
                "alert_type": alert_type,
                "title": title,
                "message": message_text,
                "priority": priority.value,
                "source": source.value if source else None,
                "metadata": metadata or {},
                "timestamp": datetime.now(UTC).isoformat(),
            },
            message_id=str(uuid.uuid4()),
        )

        sent_count = 0
        for connection in list(self._connections.values()):
            if self._should_receive_alert(connection, priority):
                try:
                    await self._send_message(connection, message)
                    sent_count += 1
                except Exception as e:
                    logger.warning(
                        "alert_broadcast_error",
                        client_id=connection.client_id,
                        error=str(e),
                    )

        audit_logger.log_system_event(
            event_type="alert_broadcast",
            details={
                "alert_type": alert_type,
                "title": title,
                "priority": priority.value,
                "recipients": sent_count,
            },
        )

        logger.info(
            "alert_broadcast",
            alert_type=alert_type,
            priority=priority.value,
            recipients=sent_count,
        )

        return sent_count

    def _should_receive_alert(
        self,
        connection: ClientConnection,
        priority: EventPriority,
    ) -> bool:
        """
        Determine if a connection should receive an alert.

        Critical alerts are always delivered. Other alerts respect
        subscription priority filters.

        Args:
            connection: Client connection
            priority: Alert priority

        Returns:
            bool: True if client should receive the alert
        """
        if priority == EventPriority.CRITICAL:
            return True

        sub = connection.subscription
        if sub.priorities and priority not in sub.priorities:
            return False

        return True

    async def broadcast_source_status(
        self,
        source: EventSource,
        status: str,
        details: dict[str, Any] | None = None,
    ) -> int:
        """
        Broadcast a data source status update.

        Used to notify clients when a data source comes online/offline
        or experiences issues.

        Args:
            source: Data source
            status: Status (online, offline, degraded, error)
            details: Additional status details

        Returns:
            int: Number of clients that received the update
        """
        source_name = SOURCE_DISPLAY_NAMES.get(source, source.value)

        message = WebSocketMessage(
            type=WebSocketMessageType.EVENT,
            payload={
                "event_type": "source_status",
                "source": source.value,
                "source_display": source_name,
                "status": status,
                "details": details or {},
                "timestamp": datetime.now(UTC).isoformat(),
            },
            message_id=str(uuid.uuid4()),
        )

        sent_count = 0
        for connection in list(self._connections.values()):
            try:
                await self._send_message(connection, message)
                sent_count += 1
            except Exception:
                pass

        logger.info(
            "source_status_broadcast",
            source=source.value,
            status=status,
            recipients=sent_count,
        )

        return sent_count

    def get_statistics(self) -> dict[str, Any]:
        """
        Get WebSocket manager statistics.

        Returns:
            dict: Statistics including connection counts, subscriptions, etc.
        """
        source_subscriptions: dict[str, int] = {}
        priority_subscriptions: dict[str, int] = {}
        authenticated_count = 0

        for connection in self._connections.values():
            if connection.is_authenticated:
                authenticated_count += 1

            for source in connection.subscription.sources:
                source_subscriptions[source.value] = source_subscriptions.get(source.value, 0) + 1

            for priority in connection.subscription.priorities:
                priority_subscriptions[priority.value] = (
                    priority_subscriptions.get(priority.value, 0) + 1
                )

        return {
            "total_connections": len(self._connections),
            "authenticated_connections": authenticated_count,
            "unique_users": len(self._user_connections),
            "source_subscriptions": source_subscriptions,
            "priority_subscriptions": priority_subscriptions,
            "running": self._running,
        }

    def get_connection_count(self) -> int:
        """Get the number of active connections."""
        return len(self._connections)

    def get_user_connection_count(self, user_id: str) -> int:
        """Get the number of connections for a specific user."""
        return len(self._user_connections.get(user_id, set()))

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
