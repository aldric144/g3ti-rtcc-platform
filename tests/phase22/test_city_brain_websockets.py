"""
Tests for City Brain WebSocket channels.
"""

import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch, AsyncMock
import json


class TestCityBrainWebSocketManager:
    """Tests for CityBrainWebSocketManager class."""

    def test_websocket_manager_initialization(self):
        """Test CityBrainWebSocketManager initializes correctly."""
        from backend.app.websockets.city_brain import CityBrainWebSocketManager
        
        manager = CityBrainWebSocketManager()
        assert manager is not None
        assert len(manager._clients) == 0

    @pytest.mark.asyncio
    async def test_connect_client(self):
        """Test connecting a client."""
        from backend.app.websockets.city_brain import CityBrainWebSocketManager
        
        manager = CityBrainWebSocketManager()
        
        mock_websocket = AsyncMock()
        client_id = await manager.connect(mock_websocket)
        
        assert client_id is not None
        assert client_id in manager._clients

    @pytest.mark.asyncio
    async def test_disconnect_client(self):
        """Test disconnecting a client."""
        from backend.app.websockets.city_brain import CityBrainWebSocketManager
        
        manager = CityBrainWebSocketManager()
        
        mock_websocket = AsyncMock()
        client_id = await manager.connect(mock_websocket)
        
        await manager.disconnect(client_id)
        
        assert client_id not in manager._clients

    @pytest.mark.asyncio
    async def test_subscribe_to_channel(self):
        """Test subscribing to a channel."""
        from backend.app.websockets.city_brain import CityBrainWebSocketManager, CityBrainChannel
        
        manager = CityBrainWebSocketManager()
        
        mock_websocket = AsyncMock()
        client_id = await manager.connect(mock_websocket)
        
        subscription = await manager.subscribe(client_id, CityBrainChannel.WEATHER)
        
        assert subscription is not None
        assert subscription.channel == CityBrainChannel.WEATHER

    @pytest.mark.asyncio
    async def test_unsubscribe_from_channel(self):
        """Test unsubscribing from a channel."""
        from backend.app.websockets.city_brain import CityBrainWebSocketManager, CityBrainChannel
        
        manager = CityBrainWebSocketManager()
        
        mock_websocket = AsyncMock()
        client_id = await manager.connect(mock_websocket)
        
        await manager.subscribe(client_id, CityBrainChannel.WEATHER)
        success = await manager.unsubscribe(client_id, CityBrainChannel.WEATHER)
        
        assert success is True

    @pytest.mark.asyncio
    async def test_broadcast_to_channel(self):
        """Test broadcasting to a channel."""
        from backend.app.websockets.city_brain import (
            CityBrainWebSocketManager, CityBrainChannel, MessageType
        )
        
        manager = CityBrainWebSocketManager()
        
        mock_websocket = AsyncMock()
        client_id = await manager.connect(mock_websocket)
        await manager.subscribe(client_id, CityBrainChannel.WEATHER)
        
        sent_count = await manager.broadcast_to_channel(
            CityBrainChannel.WEATHER,
            MessageType.WEATHER_UPDATE,
            {"temperature": 85},
        )
        
        assert sent_count == 1

    def test_get_connection_stats(self):
        """Test getting connection statistics."""
        from backend.app.websockets.city_brain import CityBrainWebSocketManager
        
        manager = CityBrainWebSocketManager()
        stats = manager.get_connection_stats()
        
        assert stats is not None
        assert "total_clients" in stats
        assert "subscriptions_by_channel" in stats


class TestCityBrainChannel:
    """Tests for CityBrainChannel enum."""

    def test_channel_values(self):
        """Test CityBrainChannel enum values."""
        from backend.app.websockets.city_brain import CityBrainChannel
        
        assert CityBrainChannel.STATE.value == "state"
        assert CityBrainChannel.WEATHER.value == "weather"
        assert CityBrainChannel.TRAFFIC.value == "traffic"
        assert CityBrainChannel.DIGITAL_TWIN.value == "digital_twin"
        assert CityBrainChannel.PREDICTIONS.value == "predictions"
        assert CityBrainChannel.EVENTS.value == "events"
        assert CityBrainChannel.ALERTS.value == "alerts"


class TestMessageType:
    """Tests for MessageType enum."""

    def test_message_type_values(self):
        """Test MessageType enum values."""
        from backend.app.websockets.city_brain import MessageType
        
        assert MessageType.STATE_UPDATE.value == "state_update"
        assert MessageType.WEATHER_UPDATE.value == "weather_update"
        assert MessageType.TRAFFIC_UPDATE.value == "traffic_update"
        assert MessageType.INCIDENT_UPDATE.value == "incident_update"
        assert MessageType.UTILITY_UPDATE.value == "utility_update"
        assert MessageType.PREDICTION_UPDATE.value == "prediction_update"
        assert MessageType.DIGITAL_TWIN_UPDATE.value == "digital_twin_update"
        assert MessageType.EVENT_CREATED.value == "event_created"
        assert MessageType.ALERT.value == "alert"
        assert MessageType.EMERGENCY.value == "emergency"


class TestWebSocketMessage:
    """Tests for WebSocketMessage dataclass."""

    def test_websocket_message_creation(self):
        """Test WebSocketMessage creation."""
        from backend.app.websockets.city_brain import WebSocketMessage, MessageType, CityBrainChannel
        
        message = WebSocketMessage(
            message_id="msg-001",
            message_type=MessageType.WEATHER_UPDATE,
            channel=CityBrainChannel.WEATHER,
            timestamp=datetime.utcnow(),
            data={"temperature": 85},
            priority=0,
        )
        
        assert message.message_id == "msg-001"
        assert message.message_type == MessageType.WEATHER_UPDATE

    def test_websocket_message_to_json(self):
        """Test WebSocketMessage to_json method."""
        from backend.app.websockets.city_brain import WebSocketMessage, MessageType, CityBrainChannel
        
        message = WebSocketMessage(
            message_id="msg-001",
            message_type=MessageType.WEATHER_UPDATE,
            channel=CityBrainChannel.WEATHER,
            timestamp=datetime.utcnow(),
            data={"temperature": 85},
            priority=0,
        )
        
        json_str = message.to_json()
        parsed = json.loads(json_str)
        
        assert parsed["message_id"] == "msg-001"
        assert parsed["type"] == "weather_update"
        assert parsed["channel"] == "weather"
        assert parsed["data"]["temperature"] == 85


class TestSubscription:
    """Tests for Subscription dataclass."""

    def test_subscription_creation(self):
        """Test Subscription creation."""
        from backend.app.websockets.city_brain import Subscription, CityBrainChannel
        
        subscription = Subscription(
            subscription_id="sub-001",
            client_id="client-001",
            channel=CityBrainChannel.WEATHER,
            filters={},
        )
        
        assert subscription.subscription_id == "sub-001"
        assert subscription.client_id == "client-001"
        assert subscription.channel == CityBrainChannel.WEATHER


class TestBroadcastMethods:
    """Tests for broadcast helper methods."""

    @pytest.mark.asyncio
    async def test_broadcast_state_update(self):
        """Test broadcast_state_update method."""
        from backend.app.websockets.city_brain import CityBrainWebSocketManager, CityBrainChannel
        
        manager = CityBrainWebSocketManager()
        
        mock_websocket = AsyncMock()
        client_id = await manager.connect(mock_websocket)
        await manager.subscribe(client_id, CityBrainChannel.STATE)
        
        sent_count = await manager.broadcast_state_update({"health": 0.95})
        
        assert sent_count == 1

    @pytest.mark.asyncio
    async def test_broadcast_weather_update(self):
        """Test broadcast_weather_update method."""
        from backend.app.websockets.city_brain import CityBrainWebSocketManager, CityBrainChannel
        
        manager = CityBrainWebSocketManager()
        
        mock_websocket = AsyncMock()
        client_id = await manager.connect(mock_websocket)
        await manager.subscribe(client_id, CityBrainChannel.WEATHER)
        
        sent_count = await manager.broadcast_weather_update({"temperature": 85})
        
        assert sent_count == 1

    @pytest.mark.asyncio
    async def test_broadcast_traffic_update(self):
        """Test broadcast_traffic_update method."""
        from backend.app.websockets.city_brain import CityBrainWebSocketManager, CityBrainChannel
        
        manager = CityBrainWebSocketManager()
        
        mock_websocket = AsyncMock()
        client_id = await manager.connect(mock_websocket)
        await manager.subscribe(client_id, CityBrainChannel.TRAFFIC)
        
        sent_count = await manager.broadcast_traffic_update({"congestion": "moderate"})
        
        assert sent_count == 1

    @pytest.mark.asyncio
    async def test_broadcast_digital_twin_update(self):
        """Test broadcast_digital_twin_update method."""
        from backend.app.websockets.city_brain import CityBrainWebSocketManager, CityBrainChannel
        
        manager = CityBrainWebSocketManager()
        
        mock_websocket = AsyncMock()
        client_id = await manager.connect(mock_websocket)
        await manager.subscribe(client_id, CityBrainChannel.DIGITAL_TWIN)
        
        sent_count = await manager.broadcast_digital_twin_update({"objects": []})
        
        assert sent_count == 1

    @pytest.mark.asyncio
    async def test_broadcast_prediction_update(self):
        """Test broadcast_prediction_update method."""
        from backend.app.websockets.city_brain import CityBrainWebSocketManager, CityBrainChannel
        
        manager = CityBrainWebSocketManager()
        
        mock_websocket = AsyncMock()
        client_id = await manager.connect(mock_websocket)
        await manager.subscribe(client_id, CityBrainChannel.PREDICTIONS)
        
        sent_count = await manager.broadcast_prediction_update({"traffic": []})
        
        assert sent_count == 1

    @pytest.mark.asyncio
    async def test_broadcast_alert(self):
        """Test broadcast_alert method."""
        from backend.app.websockets.city_brain import CityBrainWebSocketManager, CityBrainChannel
        
        manager = CityBrainWebSocketManager()
        
        mock_websocket = AsyncMock()
        client_id = await manager.connect(mock_websocket)
        await manager.subscribe(client_id, CityBrainChannel.ALERTS)
        
        sent_count = await manager.broadcast_alert({"type": "weather", "message": "Storm warning"})
        
        assert sent_count == 1

    @pytest.mark.asyncio
    async def test_broadcast_emergency(self):
        """Test broadcast_alert with emergency flag."""
        from backend.app.websockets.city_brain import CityBrainWebSocketManager, CityBrainChannel
        
        manager = CityBrainWebSocketManager()
        
        mock_websocket = AsyncMock()
        client_id = await manager.connect(mock_websocket)
        await manager.subscribe(client_id, CityBrainChannel.ALERTS)
        
        sent_count = await manager.broadcast_alert(
            {"type": "hurricane", "message": "Mandatory evacuation"},
            is_emergency=True,
        )
        
        assert sent_count == 1


class TestClientMessageHandling:
    """Tests for client message handling."""

    @pytest.mark.asyncio
    async def test_handle_subscribe_message(self):
        """Test handling subscribe message from client."""
        from backend.app.websockets.city_brain import CityBrainWebSocketManager
        
        manager = CityBrainWebSocketManager()
        
        mock_websocket = AsyncMock()
        client_id = await manager.connect(mock_websocket)
        
        message = json.dumps({"action": "subscribe", "channel": "weather"})
        result = await manager.handle_client_message(client_id, message)
        
        assert result["status"] == "success"
        assert result["action"] == "subscribe"

    @pytest.mark.asyncio
    async def test_handle_unsubscribe_message(self):
        """Test handling unsubscribe message from client."""
        from backend.app.websockets.city_brain import CityBrainWebSocketManager, CityBrainChannel
        
        manager = CityBrainWebSocketManager()
        
        mock_websocket = AsyncMock()
        client_id = await manager.connect(mock_websocket)
        await manager.subscribe(client_id, CityBrainChannel.WEATHER)
        
        message = json.dumps({"action": "unsubscribe", "channel": "weather"})
        result = await manager.handle_client_message(client_id, message)
        
        assert result["status"] == "success"
        assert result["action"] == "unsubscribe"

    @pytest.mark.asyncio
    async def test_handle_ping_message(self):
        """Test handling ping message from client."""
        from backend.app.websockets.city_brain import CityBrainWebSocketManager
        
        manager = CityBrainWebSocketManager()
        
        mock_websocket = AsyncMock()
        client_id = await manager.connect(mock_websocket)
        
        message = json.dumps({"action": "ping"})
        result = await manager.handle_client_message(client_id, message)
        
        assert result["status"] == "success"
        assert result["action"] == "pong"

    @pytest.mark.asyncio
    async def test_handle_invalid_json(self):
        """Test handling invalid JSON from client."""
        from backend.app.websockets.city_brain import CityBrainWebSocketManager
        
        manager = CityBrainWebSocketManager()
        
        mock_websocket = AsyncMock()
        client_id = await manager.connect(mock_websocket)
        
        result = await manager.handle_client_message(client_id, "not valid json")
        
        assert result["status"] == "error"

    @pytest.mark.asyncio
    async def test_handle_unknown_action(self):
        """Test handling unknown action from client."""
        from backend.app.websockets.city_brain import CityBrainWebSocketManager
        
        manager = CityBrainWebSocketManager()
        
        mock_websocket = AsyncMock()
        client_id = await manager.connect(mock_websocket)
        
        message = json.dumps({"action": "unknown_action"})
        result = await manager.handle_client_message(client_id, message)
        
        assert result["status"] == "error"


class TestSingletonFunctions:
    """Tests for singleton getter functions."""

    def test_get_city_brain_ws_manager(self):
        """Test get_city_brain_ws_manager function."""
        from backend.app.websockets.city_brain import get_city_brain_ws_manager
        
        manager1 = get_city_brain_ws_manager()
        manager2 = get_city_brain_ws_manager()
        
        assert manager1 is manager2
