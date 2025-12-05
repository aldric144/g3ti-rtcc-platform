"""
Integration tests for WebSocket functionality.

Tests cover:
- WebSocket connection
- Event subscription
- Event broadcasting
- Client management
- Message handling
"""

from datetime import datetime
from unittest.mock import AsyncMock

import pytest

from app.api.realtime.websocket import ConnectionManager, WebSocketManager
from app.schemas.events import (
    EventPriority,
    EventSource,
    EventSubscription,
    EventType,
    RTCCEvent,
    WebSocketMessageType,
)


class TestWebSocketManager:
    """Tests for WebSocket manager functionality."""

    @pytest.fixture
    def ws_manager(self):
        """Create a WebSocket manager instance."""
        return WebSocketManager()

    def test_manager_initialization(self, ws_manager):
        """Test WebSocket manager initializes correctly."""
        assert ws_manager is not None
        assert hasattr(ws_manager, "active_connections")
        assert hasattr(ws_manager, "subscriptions")

    def test_connection_count_starts_at_zero(self, ws_manager):
        """Test that connection count starts at zero."""
        assert ws_manager.get_connection_count() == 0

    @pytest.mark.asyncio
    async def test_connect_adds_connection(self, ws_manager):
        """Test that connect adds a connection."""
        mock_websocket = AsyncMock()
        mock_websocket.accept = AsyncMock()

        await ws_manager.connect(mock_websocket, client_id="client-001")

        assert ws_manager.get_connection_count() == 1
        mock_websocket.accept.assert_called_once()

    @pytest.mark.asyncio
    async def test_disconnect_removes_connection(self, ws_manager):
        """Test that disconnect removes a connection."""
        mock_websocket = AsyncMock()
        mock_websocket.accept = AsyncMock()

        await ws_manager.connect(mock_websocket, client_id="client-001")
        assert ws_manager.get_connection_count() == 1

        ws_manager.disconnect(client_id="client-001")
        assert ws_manager.get_connection_count() == 0

    @pytest.mark.asyncio
    async def test_multiple_connections(self, ws_manager):
        """Test handling multiple connections."""
        mock_ws1 = AsyncMock()
        mock_ws1.accept = AsyncMock()
        mock_ws2 = AsyncMock()
        mock_ws2.accept = AsyncMock()

        await ws_manager.connect(mock_ws1, client_id="client-001")
        await ws_manager.connect(mock_ws2, client_id="client-002")

        assert ws_manager.get_connection_count() == 2

        ws_manager.disconnect(client_id="client-001")
        assert ws_manager.get_connection_count() == 1


class TestEventSubscription:
    """Tests for event subscription functionality."""

    @pytest.fixture
    def ws_manager(self):
        """Create a WebSocket manager instance."""
        return WebSocketManager()

    @pytest.mark.asyncio
    async def test_subscribe_to_event_types(self, ws_manager):
        """Test subscribing to specific event types."""
        mock_websocket = AsyncMock()
        mock_websocket.accept = AsyncMock()

        await ws_manager.connect(mock_websocket, client_id="client-001")

        subscription = EventSubscription(
            event_types=[EventType.GUNSHOT, EventType.LPR_HIT],
            sources=[],
            priorities=[],
        )

        ws_manager.subscribe(client_id="client-001", subscription=subscription)

        client_sub = ws_manager.get_subscription("client-001")
        assert EventType.GUNSHOT in client_sub.event_types
        assert EventType.LPR_HIT in client_sub.event_types

    @pytest.mark.asyncio
    async def test_subscribe_to_sources(self, ws_manager):
        """Test subscribing to specific sources."""
        mock_websocket = AsyncMock()
        mock_websocket.accept = AsyncMock()

        await ws_manager.connect(mock_websocket, client_id="client-001")

        subscription = EventSubscription(
            event_types=[],
            sources=[EventSource.SHOTSPOTTER, EventSource.FLOCK],
            priorities=[],
        )

        ws_manager.subscribe(client_id="client-001", subscription=subscription)

        client_sub = ws_manager.get_subscription("client-001")
        assert EventSource.SHOTSPOTTER in client_sub.sources
        assert EventSource.FLOCK in client_sub.sources

    @pytest.mark.asyncio
    async def test_subscribe_to_priorities(self, ws_manager):
        """Test subscribing to specific priorities."""
        mock_websocket = AsyncMock()
        mock_websocket.accept = AsyncMock()

        await ws_manager.connect(mock_websocket, client_id="client-001")

        subscription = EventSubscription(
            event_types=[],
            sources=[],
            priorities=[EventPriority.CRITICAL, EventPriority.HIGH],
        )

        ws_manager.subscribe(client_id="client-001", subscription=subscription)

        client_sub = ws_manager.get_subscription("client-001")
        assert EventPriority.CRITICAL in client_sub.priorities
        assert EventPriority.HIGH in client_sub.priorities

    @pytest.mark.asyncio
    async def test_unsubscribe(self, ws_manager):
        """Test unsubscribing from events."""
        mock_websocket = AsyncMock()
        mock_websocket.accept = AsyncMock()

        await ws_manager.connect(mock_websocket, client_id="client-001")

        subscription = EventSubscription(
            event_types=[EventType.GUNSHOT],
            sources=[],
            priorities=[],
        )

        ws_manager.subscribe(client_id="client-001", subscription=subscription)
        ws_manager.unsubscribe(client_id="client-001")

        client_sub = ws_manager.get_subscription("client-001")
        assert client_sub is None or len(client_sub.event_types) == 0


class TestEventBroadcasting:
    """Tests for event broadcasting functionality."""

    @pytest.fixture
    def ws_manager(self):
        """Create a WebSocket manager instance."""
        return WebSocketManager()

    @pytest.fixture
    def sample_event(self, sample_event_data):
        """Create a sample RTCC event."""
        return RTCCEvent(**sample_event_data)

    @pytest.mark.asyncio
    async def test_broadcast_to_all(self, ws_manager, sample_event):
        """Test broadcasting event to all connected clients."""
        mock_ws1 = AsyncMock()
        mock_ws1.accept = AsyncMock()
        mock_ws1.send_json = AsyncMock()
        mock_ws2 = AsyncMock()
        mock_ws2.accept = AsyncMock()
        mock_ws2.send_json = AsyncMock()

        await ws_manager.connect(mock_ws1, client_id="client-001")
        await ws_manager.connect(mock_ws2, client_id="client-002")

        await ws_manager.broadcast(sample_event)

        mock_ws1.send_json.assert_called_once()
        mock_ws2.send_json.assert_called_once()

    @pytest.mark.asyncio
    async def test_broadcast_filtered_by_event_type(self, ws_manager, sample_event):
        """Test that broadcast respects event type filters."""
        mock_ws1 = AsyncMock()
        mock_ws1.accept = AsyncMock()
        mock_ws1.send_json = AsyncMock()
        mock_ws2 = AsyncMock()
        mock_ws2.accept = AsyncMock()
        mock_ws2.send_json = AsyncMock()

        await ws_manager.connect(mock_ws1, client_id="client-001")
        await ws_manager.connect(mock_ws2, client_id="client-002")

        # Client 1 subscribes to gunshots
        ws_manager.subscribe(
            client_id="client-001",
            subscription=EventSubscription(
                event_types=[EventType.GUNSHOT],
                sources=[],
                priorities=[],
            ),
        )

        # Client 2 subscribes to LPR hits only
        ws_manager.subscribe(
            client_id="client-002",
            subscription=EventSubscription(
                event_types=[EventType.LPR_HIT],
                sources=[],
                priorities=[],
            ),
        )

        # Broadcast gunshot event
        await ws_manager.broadcast_filtered(sample_event)

        # Only client 1 should receive it
        mock_ws1.send_json.assert_called_once()
        mock_ws2.send_json.assert_not_called()

    @pytest.mark.asyncio
    async def test_broadcast_filtered_by_priority(self, ws_manager):
        """Test that broadcast respects priority filters."""
        mock_ws1 = AsyncMock()
        mock_ws1.accept = AsyncMock()
        mock_ws1.send_json = AsyncMock()

        await ws_manager.connect(mock_ws1, client_id="client-001")

        # Subscribe to critical only
        ws_manager.subscribe(
            client_id="client-001",
            subscription=EventSubscription(
                event_types=[],
                sources=[],
                priorities=[EventPriority.CRITICAL],
            ),
        )

        # Create low priority event
        low_priority_event = RTCCEvent(
            id="event-002",
            event_type=EventType.CAMERA_ALERT,
            source=EventSource.MILESTONE,
            priority=EventPriority.LOW,
            title="Camera Motion",
            timestamp=datetime.utcnow(),
        )

        await ws_manager.broadcast_filtered(low_priority_event)

        # Should not receive low priority event
        mock_ws1.send_json.assert_not_called()


class TestMessageHandling:
    """Tests for WebSocket message handling."""

    @pytest.fixture
    def ws_manager(self):
        """Create a WebSocket manager instance."""
        return WebSocketManager()

    @pytest.mark.asyncio
    async def test_handle_ping_message(self, ws_manager):
        """Test handling ping message."""
        mock_websocket = AsyncMock()
        mock_websocket.accept = AsyncMock()
        mock_websocket.send_json = AsyncMock()

        await ws_manager.connect(mock_websocket, client_id="client-001")

        message = {
            "type": WebSocketMessageType.PING,
            "payload": {},
            "timestamp": datetime.utcnow().isoformat(),
        }

        await ws_manager.handle_message(client_id="client-001", message=message)

        # Should respond with pong
        mock_websocket.send_json.assert_called()
        call_args = mock_websocket.send_json.call_args[0][0]
        assert call_args["type"] == WebSocketMessageType.PONG

    @pytest.mark.asyncio
    async def test_handle_subscribe_message(self, ws_manager):
        """Test handling subscribe message."""
        mock_websocket = AsyncMock()
        mock_websocket.accept = AsyncMock()
        mock_websocket.send_json = AsyncMock()

        await ws_manager.connect(mock_websocket, client_id="client-001")

        message = {
            "type": WebSocketMessageType.SUBSCRIBE,
            "payload": {
                "event_types": ["gunshot", "lpr_hit"],
                "sources": ["shotspotter"],
                "priorities": ["critical"],
            },
            "timestamp": datetime.utcnow().isoformat(),
        }

        await ws_manager.handle_message(client_id="client-001", message=message)

        # Should confirm subscription
        mock_websocket.send_json.assert_called()

        # Verify subscription was stored
        sub = ws_manager.get_subscription("client-001")
        assert sub is not None

    @pytest.mark.asyncio
    async def test_handle_acknowledge_message(self, ws_manager):
        """Test handling acknowledge message."""
        mock_websocket = AsyncMock()
        mock_websocket.accept = AsyncMock()
        mock_websocket.send_json = AsyncMock()

        await ws_manager.connect(mock_websocket, client_id="client-001")

        message = {
            "type": WebSocketMessageType.ACKNOWLEDGE,
            "payload": {
                "event_id": "event-001",
                "notes": "Dispatched unit 42",
            },
            "timestamp": datetime.utcnow().isoformat(),
        }

        await ws_manager.handle_message(client_id="client-001", message=message)

        # Should confirm acknowledgment
        mock_websocket.send_json.assert_called()

    @pytest.mark.asyncio
    async def test_handle_invalid_message_type(self, ws_manager):
        """Test handling invalid message type."""
        mock_websocket = AsyncMock()
        mock_websocket.accept = AsyncMock()
        mock_websocket.send_json = AsyncMock()

        await ws_manager.connect(mock_websocket, client_id="client-001")

        message = {
            "type": "invalid_type",
            "payload": {},
            "timestamp": datetime.utcnow().isoformat(),
        }

        await ws_manager.handle_message(client_id="client-001", message=message)

        # Should send error response
        mock_websocket.send_json.assert_called()
        call_args = mock_websocket.send_json.call_args[0][0]
        assert call_args["type"] == WebSocketMessageType.ERROR


class TestWebSocketEndpoint:
    """Tests for WebSocket API endpoint."""

    def test_websocket_endpoint_requires_auth(self, client):
        """Test that WebSocket endpoint requires authentication."""
        # Note: TestClient doesn't fully support WebSocket testing
        # This is a placeholder for the endpoint test
        pass

    def test_websocket_connection_with_valid_token(self, client, test_user_token):
        """Test WebSocket connection with valid token."""
        # WebSocket testing requires special handling
        # This is a placeholder for integration testing
        pass


class TestConnectionManager:
    """Tests for connection manager functionality."""

    @pytest.fixture
    def connection_manager(self):
        """Create a connection manager instance."""
        return ConnectionManager()

    def test_connection_manager_initialization(self, connection_manager):
        """Test connection manager initializes correctly."""
        assert connection_manager is not None

    @pytest.mark.asyncio
    async def test_connection_tracking(self, connection_manager):
        """Test that connections are properly tracked."""
        mock_websocket = AsyncMock()
        mock_websocket.accept = AsyncMock()

        await connection_manager.connect(mock_websocket, user_id="user-001")

        assert connection_manager.is_connected("user-001")

    @pytest.mark.asyncio
    async def test_get_user_connections(self, connection_manager):
        """Test getting all connections for a user."""
        mock_ws1 = AsyncMock()
        mock_ws1.accept = AsyncMock()
        mock_ws2 = AsyncMock()
        mock_ws2.accept = AsyncMock()

        await connection_manager.connect(mock_ws1, user_id="user-001", client_id="client-001")
        await connection_manager.connect(mock_ws2, user_id="user-001", client_id="client-002")

        connections = connection_manager.get_user_connections("user-001")
        assert len(connections) == 2
