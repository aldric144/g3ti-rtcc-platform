"""
Phase 37: Master Orchestration WebSocket Tests
Tests for the Master Orchestration WebSocket Manager.
"""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

from backend.app.websockets.master_orchestration_ws import (
    MasterOrchestrationWSManager,
    MasterWSChannel,
    MessageType,
    WSConnection,
    WSMessage,
)


class TestMasterOrchestrationWSManager:
    """Test suite for MasterOrchestrationWSManager."""

    def setup_method(self):
        """Reset singleton for each test."""
        MasterOrchestrationWSManager._instance = None
        self.ws_manager = MasterOrchestrationWSManager()

    def test_singleton_pattern(self):
        """Test that MasterOrchestrationWSManager follows singleton pattern."""
        manager1 = MasterOrchestrationWSManager()
        manager2 = MasterOrchestrationWSManager()
        assert manager1 is manager2

    @pytest.mark.asyncio
    async def test_connect(self):
        """Test WebSocket connection."""
        connection = await self.ws_manager.connect(
            user_id="user-001",
            channels=[MasterWSChannel.EVENTS, MasterWSChannel.ALERTS],
            metadata={"role": "operator"},
        )

        assert connection.connection_id is not None
        assert connection.user_id == "user-001"
        assert MasterWSChannel.EVENTS in connection.channels
        assert MasterWSChannel.ALERTS in connection.channels

    @pytest.mark.asyncio
    async def test_disconnect(self):
        """Test WebSocket disconnection."""
        connection = await self.ws_manager.connect(user_id="user-002")

        result = await self.ws_manager.disconnect(connection.connection_id)
        assert result is True

        retrieved = self.ws_manager.get_connection(connection.connection_id)
        assert retrieved is None

    @pytest.mark.asyncio
    async def test_subscribe_to_channel(self):
        """Test subscribing to a channel."""
        connection = await self.ws_manager.connect(user_id="user-003")

        result = await self.ws_manager.subscribe(
            connection.connection_id,
            MasterWSChannel.TACTICAL,
        )
        assert result is True

        updated = self.ws_manager.get_connection(connection.connection_id)
        assert MasterWSChannel.TACTICAL in updated.channels

    @pytest.mark.asyncio
    async def test_unsubscribe_from_channel(self):
        """Test unsubscribing from a channel."""
        connection = await self.ws_manager.connect(
            user_id="user-004",
            channels=[MasterWSChannel.EVENTS, MasterWSChannel.ALERTS],
        )

        result = await self.ws_manager.unsubscribe(
            connection.connection_id,
            MasterWSChannel.ALERTS,
        )
        assert result is True

        updated = self.ws_manager.get_connection(connection.connection_id)
        assert MasterWSChannel.ALERTS not in updated.channels

    @pytest.mark.asyncio
    async def test_send_message(self):
        """Test sending a message to a connection."""
        connection = await self.ws_manager.connect(user_id="user-005")

        message = WSMessage(
            message_type=MessageType.NOTIFICATION,
            channel=MasterWSChannel.NOTIFICATIONS,
            payload={"title": "Test", "message": "Test message"},
        )

        result = await self.ws_manager.send_message(
            connection.connection_id,
            message,
        )
        assert result is True

    @pytest.mark.asyncio
    async def test_broadcast_to_channel(self):
        """Test broadcasting to a channel."""
        await self.ws_manager.connect(
            user_id="user-006",
            channels=[MasterWSChannel.EVENTS],
        )
        await self.ws_manager.connect(
            user_id="user-007",
            channels=[MasterWSChannel.EVENTS],
        )

        message = WSMessage(
            message_type=MessageType.EVENT,
            payload={"event": "test"},
        )

        sent_count = await self.ws_manager.broadcast_to_channel(
            MasterWSChannel.EVENTS,
            message,
        )
        assert sent_count >= 2

    @pytest.mark.asyncio
    async def test_broadcast_event(self):
        """Test broadcasting an event."""
        await self.ws_manager.connect(
            user_id="user-008",
            channels=[MasterWSChannel.EVENTS],
        )

        sent_count = await self.ws_manager.broadcast_event(
            event_type="alert",
            title="Test Event",
            summary="Test summary",
            source="test",
            priority=1,
        )
        assert sent_count >= 1

    @pytest.mark.asyncio
    async def test_broadcast_alert(self):
        """Test broadcasting an alert."""
        await self.ws_manager.connect(
            user_id="user-009",
            channels=[MasterWSChannel.ALERTS],
        )

        sent_count = await self.ws_manager.broadcast_alert(
            severity="high",
            title="Test Alert",
            summary="Test summary",
            source="test",
            requires_action=True,
        )
        assert sent_count >= 1

    @pytest.mark.asyncio
    async def test_broadcast_module_status(self):
        """Test broadcasting module status."""
        await self.ws_manager.connect(
            user_id="user-010",
            channels=[MasterWSChannel.MODULE_STATUS],
        )

        sent_count = await self.ws_manager.broadcast_module_status(
            module_id="test-module",
            module_name="Test Module",
            status="healthy",
            response_time_ms=50.0,
        )
        assert sent_count >= 1

    @pytest.mark.asyncio
    async def test_broadcast_state_change(self):
        """Test broadcasting state change."""
        await self.ws_manager.connect(
            user_id="user-011",
            channels=[MasterWSChannel.STATE_SYNC],
        )

        sent_count = await self.ws_manager.broadcast_state_change(
            change_type="map_update",
            source_module="real_time_ops",
            data={"incident_id": "inc-001"},
        )
        assert sent_count >= 1

    @pytest.mark.asyncio
    async def test_broadcast_notification(self):
        """Test broadcasting notification."""
        await self.ws_manager.connect(
            user_id="user-012",
            channels=[MasterWSChannel.NOTIFICATIONS],
        )

        sent_count = await self.ws_manager.broadcast_notification(
            title="Test Notification",
            message_text="Test message",
            notification_type="info",
        )
        assert sent_count >= 1

    @pytest.mark.asyncio
    async def test_broadcast_officer_safety(self):
        """Test broadcasting officer safety update."""
        await self.ws_manager.connect(
            user_id="user-013",
            channels=[MasterWSChannel.OFFICER_SAFETY],
        )

        sent_count = await self.ws_manager.broadcast_officer_safety(
            officer_id="off-001",
            status="responding",
            location={"lat": 26.77, "lng": -80.05},
        )
        assert sent_count >= 1

    @pytest.mark.asyncio
    async def test_broadcast_drone_telemetry(self):
        """Test broadcasting drone telemetry."""
        await self.ws_manager.connect(
            user_id="user-014",
            channels=[MasterWSChannel.DRONE_TELEMETRY],
        )

        sent_count = await self.ws_manager.broadcast_drone_telemetry(
            drone_id="drone-001",
            position={"lat": 26.77, "lng": -80.05},
            status="active",
            battery=85.0,
        )
        assert sent_count >= 1

    @pytest.mark.asyncio
    async def test_broadcast_emergency(self):
        """Test broadcasting emergency."""
        await self.ws_manager.connect(
            user_id="user-015",
            channels=[MasterWSChannel.EMERGENCY],
        )

        sent_count = await self.ws_manager.broadcast_emergency(
            emergency_type="weather",
            title="Storm Warning",
            summary="Tropical storm approaching",
            affected_areas=["All Neighborhoods"],
            severity="high",
        )
        assert sent_count >= 1

    @pytest.mark.asyncio
    async def test_send_heartbeat(self):
        """Test sending heartbeat."""
        await self.ws_manager.connect(
            user_id="user-016",
            channels=[MasterWSChannel.ALL],
        )

        sent_count = await self.ws_manager.send_heartbeat()
        assert sent_count >= 1

    def test_get_active_connections(self):
        """Test retrieving active connections."""
        connections = self.ws_manager.get_active_connections()
        assert isinstance(connections, list)

    def test_get_message_history(self):
        """Test retrieving message history."""
        history = self.ws_manager.get_message_history(limit=10)
        assert isinstance(history, list)

    def test_get_statistics(self):
        """Test statistics retrieval."""
        stats = self.ws_manager.get_statistics()

        assert "connections_total" in stats
        assert "connections_active" in stats
        assert "messages_sent" in stats
        assert "channels" in stats

    def test_get_channel_info(self):
        """Test channel info retrieval."""
        info = self.ws_manager.get_channel_info()

        assert isinstance(info, dict)
        assert len(info) == len(MasterWSChannel)

    def test_ws_channel_enum(self):
        """Test all WebSocket channels are defined."""
        assert len(MasterWSChannel) == 14
        assert MasterWSChannel.EVENTS.value == "events"
        assert MasterWSChannel.ALERTS.value == "alerts"
        assert MasterWSChannel.ALL.value == "all"

    def test_message_type_enum(self):
        """Test all message types are defined."""
        assert len(MessageType) >= 8
        assert MessageType.EVENT.value == "event"
        assert MessageType.ALERT.value == "alert"
        assert MessageType.HEARTBEAT.value == "heartbeat"

    def test_ws_connection_to_dict(self):
        """Test WSConnection serialization."""
        connection = WSConnection(
            user_id="user-test",
            channels={MasterWSChannel.EVENTS},
        )

        conn_dict = connection.to_dict()

        assert "connection_id" in conn_dict
        assert conn_dict["user_id"] == "user-test"
        assert "events" in conn_dict["channels"]

    def test_ws_message_to_dict(self):
        """Test WSMessage serialization."""
        message = WSMessage(
            message_type=MessageType.ALERT,
            channel=MasterWSChannel.ALERTS,
            payload={"test": "data"},
        )

        msg_dict = message.to_dict()

        assert "message_id" in msg_dict
        assert msg_dict["message_type"] == "alert"
        assert msg_dict["channel"] == "alerts"

    def test_ws_message_to_json(self):
        """Test WSMessage JSON serialization."""
        message = WSMessage(
            message_type=MessageType.NOTIFICATION,
            payload={"title": "Test"},
        )

        json_str = message.to_json()

        assert isinstance(json_str, str)
        assert "message_id" in json_str
