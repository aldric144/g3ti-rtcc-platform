"""Tests for the WebSocket module."""

import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
import json

import sys
sys.path.insert(0, "/home/ubuntu/repos/g3ti-rtcc-platform/backend")

from app.api.intel_orchestration.websocket import (
    WebSocketMessage,
    ConnectionManager,
    broadcast_fused_intelligence,
    broadcast_alert,
    broadcast_priority_update,
    broadcast_pipeline_status,
    broadcast_officer_safety_alert,
    broadcast_bolo,
    broadcast_bulletin,
)


class TestWebSocketMessage:
    """Tests for WebSocketMessage model."""

    def test_message_creation(self):
        """Test creating a WebSocket message."""
        msg = WebSocketMessage(
            type="fused_intelligence",
            channel="fused",
            data={"id": "intel-123", "tier": "tier2"},
        )
        
        assert msg.type == "fused_intelligence"
        assert msg.channel == "fused"
        assert msg.data["id"] == "intel-123"

    def test_message_with_timestamp(self):
        """Test message includes timestamp."""
        msg = WebSocketMessage(
            type="alert",
            channel="alerts",
            data={},
        )
        
        assert msg.timestamp is not None

    def test_message_serialization(self):
        """Test message can be serialized to JSON."""
        msg = WebSocketMessage(
            type="priority_update",
            channel="priority",
            data={"score": 85.0},
        )
        
        json_str = msg.model_dump_json()
        parsed = json.loads(json_str)
        
        assert parsed["type"] == "priority_update"
        assert parsed["data"]["score"] == 85.0


class TestConnectionManager:
    """Tests for ConnectionManager class."""

    def test_manager_initialization(self):
        """Test connection manager initialization."""
        manager = ConnectionManager()
        
        assert manager.active_connections == {}
        assert "fused" in manager.channels
        assert "alerts" in manager.channels
        assert "priority" in manager.channels
        assert "pipelines" in manager.channels

    @pytest.mark.asyncio
    async def test_connect(self):
        """Test connecting a WebSocket."""
        manager = ConnectionManager()
        
        mock_ws = AsyncMock()
        mock_ws.accept = AsyncMock()
        
        await manager.connect(mock_ws, "fused")
        
        mock_ws.accept.assert_called_once()
        assert "fused" in manager.active_connections
        assert mock_ws in manager.active_connections["fused"]

    @pytest.mark.asyncio
    async def test_disconnect(self):
        """Test disconnecting a WebSocket."""
        manager = ConnectionManager()
        
        mock_ws = AsyncMock()
        mock_ws.accept = AsyncMock()
        
        await manager.connect(mock_ws, "fused")
        manager.disconnect(mock_ws, "fused")
        
        assert mock_ws not in manager.active_connections.get("fused", [])

    @pytest.mark.asyncio
    async def test_send_personal_message(self):
        """Test sending a personal message."""
        manager = ConnectionManager()
        
        mock_ws = AsyncMock()
        mock_ws.send_json = AsyncMock()
        
        message = {"type": "test", "data": "hello"}
        await manager.send_personal_message(message, mock_ws)
        
        mock_ws.send_json.assert_called_once_with(message)

    @pytest.mark.asyncio
    async def test_broadcast_to_channel(self):
        """Test broadcasting to a channel."""
        manager = ConnectionManager()
        
        mock_ws1 = AsyncMock()
        mock_ws1.accept = AsyncMock()
        mock_ws1.send_json = AsyncMock()
        
        mock_ws2 = AsyncMock()
        mock_ws2.accept = AsyncMock()
        mock_ws2.send_json = AsyncMock()
        
        await manager.connect(mock_ws1, "fused")
        await manager.connect(mock_ws2, "fused")
        
        message = {"type": "broadcast", "data": "test"}
        await manager.broadcast(message, "fused")
        
        mock_ws1.send_json.assert_called_once_with(message)
        mock_ws2.send_json.assert_called_once_with(message)

    @pytest.mark.asyncio
    async def test_broadcast_to_all_channels(self):
        """Test broadcasting to all channels."""
        manager = ConnectionManager()
        
        mock_ws_fused = AsyncMock()
        mock_ws_fused.accept = AsyncMock()
        mock_ws_fused.send_json = AsyncMock()
        
        mock_ws_alerts = AsyncMock()
        mock_ws_alerts.accept = AsyncMock()
        mock_ws_alerts.send_json = AsyncMock()
        
        await manager.connect(mock_ws_fused, "fused")
        await manager.connect(mock_ws_alerts, "alerts")
        
        message = {"type": "system", "data": "announcement"}
        await manager.broadcast_all(message)
        
        mock_ws_fused.send_json.assert_called_once()
        mock_ws_alerts.send_json.assert_called_once()

    def test_get_connection_count(self):
        """Test getting connection count."""
        manager = ConnectionManager()
        
        count = manager.get_connection_count()
        
        assert count == 0

    @pytest.mark.asyncio
    async def test_get_connection_count_with_connections(self):
        """Test getting connection count with active connections."""
        manager = ConnectionManager()
        
        mock_ws1 = AsyncMock()
        mock_ws1.accept = AsyncMock()
        mock_ws2 = AsyncMock()
        mock_ws2.accept = AsyncMock()
        
        await manager.connect(mock_ws1, "fused")
        await manager.connect(mock_ws2, "alerts")
        
        count = manager.get_connection_count()
        
        assert count == 2

    def test_get_channel_count(self):
        """Test getting channel connection count."""
        manager = ConnectionManager()
        
        count = manager.get_channel_count("fused")
        
        assert count == 0

    @pytest.mark.asyncio
    async def test_handle_disconnect_on_send_error(self):
        """Test handling disconnect on send error."""
        manager = ConnectionManager()
        
        mock_ws = AsyncMock()
        mock_ws.accept = AsyncMock()
        mock_ws.send_json = AsyncMock(side_effect=Exception("Connection closed"))
        
        await manager.connect(mock_ws, "fused")
        
        # Should handle error gracefully
        message = {"type": "test", "data": "hello"}
        await manager.broadcast(message, "fused")
        
        # Connection should be removed after error
        assert mock_ws not in manager.active_connections.get("fused", [])


class TestBroadcastFunctions:
    """Tests for broadcast helper functions."""

    @pytest.mark.asyncio
    async def test_broadcast_fused_intelligence(self):
        """Test broadcasting fused intelligence."""
        manager = ConnectionManager()
        
        mock_ws = AsyncMock()
        mock_ws.accept = AsyncMock()
        mock_ws.send_json = AsyncMock()
        
        await manager.connect(mock_ws, "fused")
        
        intelligence = {
            "id": "intel-123",
            "tier": "tier2",
            "title": "Pattern Match",
            "priority_score": 75.0,
        }
        
        with patch("app.api.intel_orchestration.websocket.manager", manager):
            await broadcast_fused_intelligence(intelligence)
        
        mock_ws.send_json.assert_called_once()
        call_args = mock_ws.send_json.call_args[0][0]
        assert call_args["type"] == "fused_intelligence"
        assert call_args["data"]["id"] == "intel-123"

    @pytest.mark.asyncio
    async def test_broadcast_alert(self):
        """Test broadcasting an alert."""
        manager = ConnectionManager()
        
        mock_ws = AsyncMock()
        mock_ws.accept = AsyncMock()
        mock_ws.send_json = AsyncMock()
        
        await manager.connect(mock_ws, "alerts")
        
        alert = {
            "id": "alert-123",
            "priority": "high",
            "title": "Suspicious Activity",
        }
        
        with patch("app.api.intel_orchestration.websocket.manager", manager):
            await broadcast_alert(alert)
        
        mock_ws.send_json.assert_called_once()
        call_args = mock_ws.send_json.call_args[0][0]
        assert call_args["type"] == "alert"

    @pytest.mark.asyncio
    async def test_broadcast_priority_update(self):
        """Test broadcasting priority update."""
        manager = ConnectionManager()
        
        mock_ws = AsyncMock()
        mock_ws.accept = AsyncMock()
        mock_ws.send_json = AsyncMock()
        
        await manager.connect(mock_ws, "priority")
        
        update = {
            "entity_id": "person-123",
            "old_score": 50.0,
            "new_score": 85.0,
            "threat_level": "high",
        }
        
        with patch("app.api.intel_orchestration.websocket.manager", manager):
            await broadcast_priority_update(update)
        
        mock_ws.send_json.assert_called_once()
        call_args = mock_ws.send_json.call_args[0][0]
        assert call_args["type"] == "priority_update"

    @pytest.mark.asyncio
    async def test_broadcast_pipeline_status(self):
        """Test broadcasting pipeline status."""
        manager = ConnectionManager()
        
        mock_ws = AsyncMock()
        mock_ws.accept = AsyncMock()
        mock_ws.send_json = AsyncMock()
        
        await manager.connect(mock_ws, "pipelines")
        
        status = {
            "pipeline_name": "real_time",
            "status": "running",
            "items_processed": 1000,
            "throughput": 50.5,
        }
        
        with patch("app.api.intel_orchestration.websocket.manager", manager):
            await broadcast_pipeline_status(status)
        
        mock_ws.send_json.assert_called_once()
        call_args = mock_ws.send_json.call_args[0][0]
        assert call_args["type"] == "pipeline_status"

    @pytest.mark.asyncio
    async def test_broadcast_officer_safety_alert(self):
        """Test broadcasting officer safety alert."""
        manager = ConnectionManager()
        
        mock_ws = AsyncMock()
        mock_ws.accept = AsyncMock()
        mock_ws.send_json = AsyncMock()
        
        await manager.connect(mock_ws, "alerts")
        
        alert = {
            "id": "safety-123",
            "type": "officer_safety",
            "threat_level": "critical",
            "location": {"lat": 33.749, "lng": -84.388},
            "description": "Armed suspect in area",
        }
        
        with patch("app.api.intel_orchestration.websocket.manager", manager):
            await broadcast_officer_safety_alert(alert)
        
        mock_ws.send_json.assert_called_once()
        call_args = mock_ws.send_json.call_args[0][0]
        assert call_args["type"] == "officer_safety_alert"

    @pytest.mark.asyncio
    async def test_broadcast_bolo(self):
        """Test broadcasting BOLO."""
        manager = ConnectionManager()
        
        mock_ws = AsyncMock()
        mock_ws.accept = AsyncMock()
        mock_ws.send_json = AsyncMock()
        
        await manager.connect(mock_ws, "alerts")
        
        bolo = {
            "id": "bolo-123",
            "subject_type": "vehicle",
            "description": "Black SUV, plate ABC123",
            "reason": "Wanted in connection with armed robbery",
            "jurisdiction": "Metro PD",
        }
        
        with patch("app.api.intel_orchestration.websocket.manager", manager):
            await broadcast_bolo(bolo)
        
        mock_ws.send_json.assert_called_once()
        call_args = mock_ws.send_json.call_args[0][0]
        assert call_args["type"] == "bolo"

    @pytest.mark.asyncio
    async def test_broadcast_bulletin(self):
        """Test broadcasting bulletin."""
        manager = ConnectionManager()
        
        mock_ws = AsyncMock()
        mock_ws.accept = AsyncMock()
        mock_ws.send_json = AsyncMock()
        
        await manager.connect(mock_ws, "fused")
        
        bulletin = {
            "id": "bulletin-123",
            "title": "Crime Pattern Alert",
            "content": "Series of burglaries in District 5",
            "priority": "high",
        }
        
        with patch("app.api.intel_orchestration.websocket.manager", manager):
            await broadcast_bulletin(bulletin)
        
        mock_ws.send_json.assert_called_once()
        call_args = mock_ws.send_json.call_args[0][0]
        assert call_args["type"] == "bulletin"


class TestWebSocketChannels:
    """Tests for WebSocket channel configuration."""

    def test_fused_channel_exists(self):
        """Test /ws/intel/fused channel exists."""
        manager = ConnectionManager()
        assert "fused" in manager.channels

    def test_alerts_channel_exists(self):
        """Test /ws/intel/alerts channel exists."""
        manager = ConnectionManager()
        assert "alerts" in manager.channels

    def test_priority_channel_exists(self):
        """Test /ws/intel/priority channel exists."""
        manager = ConnectionManager()
        assert "priority" in manager.channels

    def test_pipelines_channel_exists(self):
        """Test /ws/intel/pipelines channel exists."""
        manager = ConnectionManager()
        assert "pipelines" in manager.channels


class TestWebSocketMessageTypes:
    """Tests for WebSocket message types."""

    def test_ping_pong_message(self):
        """Test ping/pong message type."""
        msg = WebSocketMessage(
            type="pong",
            channel="fused",
            data={"timestamp": datetime.now(timezone.utc).isoformat()},
        )
        
        assert msg.type == "pong"

    def test_subscribe_message(self):
        """Test subscribe message type."""
        msg = WebSocketMessage(
            type="subscribed",
            channel="alerts",
            data={"channels": ["alerts", "priority"]},
        )
        
        assert msg.type == "subscribed"

    def test_acknowledge_message(self):
        """Test acknowledge message type."""
        msg = WebSocketMessage(
            type="acknowledged",
            channel="alerts",
            data={"alert_id": "alert-123", "user_id": "user-456"},
        )
        
        assert msg.type == "acknowledged"

    def test_status_message(self):
        """Test status message type."""
        msg = WebSocketMessage(
            type="status",
            channel="pipelines",
            data={
                "orchestrator_running": True,
                "pipelines_active": 7,
                "connections": 15,
            },
        )
        
        assert msg.type == "status"

    def test_error_message(self):
        """Test error message type."""
        msg = WebSocketMessage(
            type="error",
            channel="fused",
            data={"error": "Invalid message format", "code": "INVALID_FORMAT"},
        )
        
        assert msg.type == "error"
