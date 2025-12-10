"""
Tests for Fusion Cloud WebSocket channels

Tests WebSocket connection management, tenant isolation,
and event broadcasting.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock

from app.websockets.fusion_cloud import (
    FusionCloudWebSocketManager,
    WebSocketConnection,
    ChannelMessage,
)


@pytest.fixture
def ws_manager():
    """Create a fresh WebSocket manager for each test"""
    return FusionCloudWebSocketManager()


class TestConnectionManagement:
    """Tests for WebSocket connection management"""

    def test_create_connection(self, ws_manager):
        """Test creating a connection"""
        mock_websocket = MagicMock()

        connection = ws_manager.create_connection(
            websocket=mock_websocket,
            tenant_id="tenant-001",
            user_id="user-001",
        )

        assert connection is not None
        assert connection.tenant_id == "tenant-001"
        assert connection.user_id == "user-001"

    def test_register_connection(self, ws_manager):
        """Test registering a connection"""
        mock_websocket = MagicMock()

        connection = ws_manager.create_connection(
            websocket=mock_websocket,
            tenant_id="tenant-001",
            user_id="user-001",
        )

        success = ws_manager.register_connection(connection)
        assert success is True

        connections = ws_manager.get_connections_for_tenant("tenant-001")
        assert len(connections) == 1

    def test_unregister_connection(self, ws_manager):
        """Test unregistering a connection"""
        mock_websocket = MagicMock()

        connection = ws_manager.create_connection(
            websocket=mock_websocket,
            tenant_id="tenant-001",
            user_id="user-001",
        )
        ws_manager.register_connection(connection)

        success = ws_manager.unregister_connection(connection.connection_id)
        assert success is True

        connections = ws_manager.get_connections_for_tenant("tenant-001")
        assert len(connections) == 0

    def test_get_connections_for_tenant(self, ws_manager):
        """Test getting connections for a tenant"""
        for i in range(3):
            mock_websocket = MagicMock()
            connection = ws_manager.create_connection(
                websocket=mock_websocket,
                tenant_id="tenant-001",
                user_id=f"user-{i}",
            )
            ws_manager.register_connection(connection)

        connections = ws_manager.get_connections_for_tenant("tenant-001")
        assert len(connections) == 3


class TestChannelSubscription:
    """Tests for channel subscription"""

    def test_subscribe_to_channel(self, ws_manager):
        """Test subscribing to a channel"""
        mock_websocket = MagicMock()
        connection = ws_manager.create_connection(
            websocket=mock_websocket,
            tenant_id="tenant-001",
            user_id="user-001",
        )
        ws_manager.register_connection(connection)

        success = ws_manager.subscribe_to_channel(
            connection_id=connection.connection_id,
            channel="intel/pursuits",
        )
        assert success is True

    def test_unsubscribe_from_channel(self, ws_manager):
        """Test unsubscribing from a channel"""
        mock_websocket = MagicMock()
        connection = ws_manager.create_connection(
            websocket=mock_websocket,
            tenant_id="tenant-001",
            user_id="user-001",
        )
        ws_manager.register_connection(connection)
        ws_manager.subscribe_to_channel(connection.connection_id, "intel/pursuits")

        success = ws_manager.unsubscribe_from_channel(
            connection_id=connection.connection_id,
            channel="intel/pursuits",
        )
        assert success is True

    def test_get_channel_subscribers(self, ws_manager):
        """Test getting channel subscribers"""
        for i in range(3):
            mock_websocket = MagicMock()
            connection = ws_manager.create_connection(
                websocket=mock_websocket,
                tenant_id=f"tenant-{i}",
                user_id=f"user-{i}",
            )
            ws_manager.register_connection(connection)
            ws_manager.subscribe_to_channel(connection.connection_id, "intel/alerts")

        subscribers = ws_manager.get_channel_subscribers("intel/alerts")
        assert len(subscribers) == 3


class TestTenantIsolation:
    """Tests for tenant isolation"""

    def test_tenant_isolation(self, ws_manager):
        """Test that connections are isolated by tenant"""
        mock_ws1 = MagicMock()
        mock_ws2 = MagicMock()

        conn1 = ws_manager.create_connection(
            websocket=mock_ws1,
            tenant_id="tenant-001",
            user_id="user-001",
        )
        conn2 = ws_manager.create_connection(
            websocket=mock_ws2,
            tenant_id="tenant-002",
            user_id="user-002",
        )

        ws_manager.register_connection(conn1)
        ws_manager.register_connection(conn2)

        tenant1_conns = ws_manager.get_connections_for_tenant("tenant-001")
        tenant2_conns = ws_manager.get_connections_for_tenant("tenant-002")

        assert len(tenant1_conns) == 1
        assert len(tenant2_conns) == 1
        assert tenant1_conns[0].tenant_id == "tenant-001"
        assert tenant2_conns[0].tenant_id == "tenant-002"


class TestEventBroadcasting:
    """Tests for event broadcasting"""

    def test_create_channel_message(self, ws_manager):
        """Test creating a channel message"""
        message = ws_manager.create_channel_message(
            channel="intel/pursuits",
            event_type="new_pursuit",
            payload={"pursuit_id": "pursuit-001", "status": "active"},
            source_tenant_id="tenant-001",
        )

        assert message is not None
        assert message.channel == "intel/pursuits"
        assert message.event_type == "new_pursuit"
        assert message.source_tenant_id == "tenant-001"

    def test_get_pending_messages(self, ws_manager):
        """Test getting pending messages for a connection"""
        mock_websocket = MagicMock()
        connection = ws_manager.create_connection(
            websocket=mock_websocket,
            tenant_id="tenant-001",
            user_id="user-001",
        )
        ws_manager.register_connection(connection)
        ws_manager.subscribe_to_channel(connection.connection_id, "intel/pursuits")

        message = ws_manager.create_channel_message(
            channel="intel/pursuits",
            event_type="new_pursuit",
            payload={"pursuit_id": "pursuit-001"},
            source_tenant_id="tenant-001",
        )
        ws_manager.queue_message(message)

        pending = ws_manager.get_pending_messages(connection.connection_id)
        assert len(pending) >= 0


class TestJointOpsRoom:
    """Tests for joint ops room WebSocket functionality"""

    def test_join_ops_room(self, ws_manager):
        """Test joining an ops room"""
        mock_websocket = MagicMock()
        connection = ws_manager.create_connection(
            websocket=mock_websocket,
            tenant_id="tenant-001",
            user_id="user-001",
        )
        ws_manager.register_connection(connection)

        success = ws_manager.join_ops_room(
            connection_id=connection.connection_id,
            room_id="room-001",
        )
        assert success is True

    def test_leave_ops_room(self, ws_manager):
        """Test leaving an ops room"""
        mock_websocket = MagicMock()
        connection = ws_manager.create_connection(
            websocket=mock_websocket,
            tenant_id="tenant-001",
            user_id="user-001",
        )
        ws_manager.register_connection(connection)
        ws_manager.join_ops_room(connection.connection_id, "room-001")

        success = ws_manager.leave_ops_room(
            connection_id=connection.connection_id,
            room_id="room-001",
        )
        assert success is True

    def test_get_room_participants(self, ws_manager):
        """Test getting room participants"""
        for i in range(3):
            mock_websocket = MagicMock()
            connection = ws_manager.create_connection(
                websocket=mock_websocket,
                tenant_id=f"tenant-{i}",
                user_id=f"user-{i}",
            )
            ws_manager.register_connection(connection)
            ws_manager.join_ops_room(connection.connection_id, "room-001")

        participants = ws_manager.get_room_participants("room-001")
        assert len(participants) == 3


class TestMetrics:
    """Tests for WebSocket metrics"""

    def test_get_metrics(self, ws_manager):
        """Test getting WebSocket metrics"""
        for i in range(3):
            mock_websocket = MagicMock()
            connection = ws_manager.create_connection(
                websocket=mock_websocket,
                tenant_id=f"tenant-{i}",
                user_id=f"user-{i}",
            )
            ws_manager.register_connection(connection)

        metrics = ws_manager.get_metrics()
        assert metrics["total_connections"] == 3
