"""
Test Suite: Personas WebSockets

Tests for WebSocket channels and real-time communication.
"""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

from backend.app.websockets.personas_ws import (
    PersonaWSManager,
    WebSocketConnection,
    WebSocketMessage,
)
from backend.app.personas.persona_engine import PersonaEngine


class TestPersonaWSManager:
    """Tests for PersonaWSManager singleton."""
    
    def test_singleton_pattern(self):
        """Test that PersonaWSManager follows singleton pattern."""
        manager1 = PersonaWSManager()
        manager2 = PersonaWSManager()
        assert manager1 is manager2
    
    def test_get_connection_count(self):
        """Test getting connection counts."""
        manager = PersonaWSManager()
        counts = manager.get_connection_count()
        
        assert "total" in counts
        assert "chat" in counts
        assert "alerts" in counts
        assert "reasoning" in counts
        assert "missions" in counts
    
    def test_get_active_chat_personas(self):
        """Test getting active chat personas."""
        manager = PersonaWSManager()
        active = manager.get_active_chat_personas()
        
        assert isinstance(active, list)
    
    def test_get_statistics(self):
        """Test getting WebSocket statistics."""
        manager = PersonaWSManager()
        stats = manager.get_statistics()
        
        assert "connections" in stats
        assert "active_chat_personas" in stats
        assert "total_chat_channels" in stats


class TestWebSocketConnection:
    """Tests for WebSocketConnection dataclass."""
    
    def test_connection_creation(self):
        """Test creating a WebSocket connection."""
        connection = WebSocketConnection(
            connection_id="conn-001",
            channel="chat:persona-001",
            user_id="user-001",
            persona_id="persona-001",
            session_id="session-001",
        )
        
        assert connection.connection_id == "conn-001"
        assert connection.channel == "chat:persona-001"
        assert connection.user_id == "user-001"
        assert connection.persona_id == "persona-001"
    
    def test_connection_timestamps(self):
        """Test connection timestamp initialization."""
        connection = WebSocketConnection(
            connection_id="conn-002",
            channel="alerts",
            user_id="user-002",
        )
        
        assert connection.connected_at is not None
        assert connection.last_activity is not None


class TestWebSocketMessage:
    """Tests for WebSocketMessage dataclass."""
    
    def test_message_creation(self):
        """Test creating a WebSocket message."""
        message = WebSocketMessage(
            message_id="msg-001",
            channel="chat:persona-001",
            message_type="chat_response",
            payload={"content": "Hello"},
            sender="persona-001",
        )
        
        assert message.message_id == "msg-001"
        assert message.channel == "chat:persona-001"
        assert message.message_type == "chat_response"
        assert message.payload["content"] == "Hello"
    
    def test_message_to_dict(self):
        """Test message serialization."""
        message = WebSocketMessage(
            message_id="msg-002",
            channel="alerts",
            message_type="alert",
            payload={"alert_type": "escalation"},
            sender="system",
        )
        
        data = message.to_dict()
        
        assert data["message_id"] == "msg-002"
        assert data["channel"] == "alerts"
        assert data["message_type"] == "alert"
        assert "timestamp" in data
    
    def test_message_to_json(self):
        """Test message JSON serialization."""
        message = WebSocketMessage(
            message_id="msg-003",
            channel="missions",
            message_type="mission_update",
            payload={"mission_id": "mission-001"},
            sender="system",
        )
        
        json_str = message.to_json()
        
        assert isinstance(json_str, str)
        assert "msg-003" in json_str
        assert "missions" in json_str


class TestChatChannel:
    """Tests for chat channel functionality."""
    
    @pytest.mark.asyncio
    async def test_connect_chat(self):
        """Test connecting to chat channel."""
        manager = PersonaWSManager()
        engine = PersonaEngine()
        
        personas = engine.get_all_personas()
        if personas:
            mock_websocket = AsyncMock()
            mock_websocket.send_text = AsyncMock()
            
            connection = await manager.connect_chat(
                connection_id="test-conn-001",
                persona_id=personas[0].persona_id,
                user_id="test-user",
                websocket=mock_websocket,
            )
            
            assert connection is not None
            assert connection.persona_id == personas[0].persona_id
            assert connection.session_id is not None
            
            await manager.disconnect("test-conn-001")
    
    @pytest.mark.asyncio
    async def test_connect_chat_invalid_persona(self):
        """Test connecting to chat with invalid persona."""
        manager = PersonaWSManager()
        mock_websocket = AsyncMock()
        
        with pytest.raises(ValueError):
            await manager.connect_chat(
                connection_id="test-conn-002",
                persona_id="nonexistent-persona",
                user_id="test-user",
                websocket=mock_websocket,
            )
    
    @pytest.mark.asyncio
    async def test_handle_chat_message(self):
        """Test handling chat message."""
        manager = PersonaWSManager()
        engine = PersonaEngine()
        
        personas = engine.get_all_personas()
        if personas:
            mock_websocket = AsyncMock()
            mock_websocket.send_text = AsyncMock()
            
            connection = await manager.connect_chat(
                connection_id="test-conn-003",
                persona_id=personas[0].persona_id,
                user_id="test-user",
                websocket=mock_websocket,
            )
            
            message = await manager.handle_chat_message(
                connection_id="test-conn-003",
                message="Hello, what is your status?",
            )
            
            assert message is not None
            assert message.message_type == "chat_response"
            assert "content" in message.payload
            
            await manager.disconnect("test-conn-003")


class TestAlertsChannel:
    """Tests for alerts channel functionality."""
    
    @pytest.mark.asyncio
    async def test_connect_alerts(self):
        """Test connecting to alerts channel."""
        manager = PersonaWSManager()
        mock_websocket = AsyncMock()
        
        connection = await manager.connect_alerts(
            connection_id="test-alert-001",
            user_id="test-user",
            websocket=mock_websocket,
        )
        
        assert connection is not None
        assert connection.channel == "alerts"
        
        await manager.disconnect("test-alert-001")
    
    @pytest.mark.asyncio
    async def test_broadcast_alert(self):
        """Test broadcasting alert."""
        manager = PersonaWSManager()
        mock_websocket = AsyncMock()
        mock_websocket.send_text = AsyncMock()
        
        await manager.connect_alerts(
            connection_id="test-alert-002",
            user_id="test-user",
            websocket=mock_websocket,
        )
        
        sent_count = await manager.broadcast_alert({
            "alert_type": "test_alert",
            "message": "Test alert message",
        })
        
        assert sent_count >= 0
        
        await manager.disconnect("test-alert-002")


class TestReasoningChannel:
    """Tests for reasoning channel functionality."""
    
    @pytest.mark.asyncio
    async def test_connect_reasoning(self):
        """Test connecting to reasoning channel."""
        manager = PersonaWSManager()
        mock_websocket = AsyncMock()
        
        connection = await manager.connect_reasoning(
            connection_id="test-reasoning-001",
            user_id="test-user",
            websocket=mock_websocket,
        )
        
        assert connection is not None
        assert connection.channel == "reasoning"
        
        await manager.disconnect("test-reasoning-001")
    
    @pytest.mark.asyncio
    async def test_broadcast_reasoning_update(self):
        """Test broadcasting reasoning update."""
        manager = PersonaWSManager()
        mock_websocket = AsyncMock()
        mock_websocket.send_text = AsyncMock()
        
        await manager.connect_reasoning(
            connection_id="test-reasoning-002",
            user_id="test-user",
            websocket=mock_websocket,
        )
        
        sent_count = await manager.broadcast_reasoning_update(
            mission_id="mission-001",
            reasoning_data={
                "step": 1,
                "action": "analyzing",
                "result": "in_progress",
            },
        )
        
        assert sent_count >= 0
        
        await manager.disconnect("test-reasoning-002")


class TestMissionsChannel:
    """Tests for missions channel functionality."""
    
    @pytest.mark.asyncio
    async def test_connect_missions(self):
        """Test connecting to missions channel."""
        manager = PersonaWSManager()
        mock_websocket = AsyncMock()
        
        connection = await manager.connect_missions(
            connection_id="test-missions-001",
            user_id="test-user",
            websocket=mock_websocket,
        )
        
        assert connection is not None
        assert connection.channel == "missions"
        
        await manager.disconnect("test-missions-001")
    
    @pytest.mark.asyncio
    async def test_broadcast_mission_update(self):
        """Test broadcasting mission update."""
        manager = PersonaWSManager()
        mock_websocket = AsyncMock()
        mock_websocket.send_text = AsyncMock()
        
        await manager.connect_missions(
            connection_id="test-missions-002",
            user_id="test-user",
            websocket=mock_websocket,
        )
        
        sent_count = await manager.broadcast_mission_update(
            mission_id="mission-001",
            update_type="mission_started",
            mission_data={"status": "in_progress"},
        )
        
        assert sent_count >= 0
        
        await manager.disconnect("test-missions-002")
    
    @pytest.mark.asyncio
    async def test_broadcast_mission_created(self):
        """Test broadcasting mission created event."""
        manager = PersonaWSManager()
        
        sent_count = await manager.broadcast_mission_created(
            mission_id="mission-002",
            mission_data={"title": "New Mission"},
        )
        
        assert sent_count >= 0
    
    @pytest.mark.asyncio
    async def test_broadcast_mission_completed(self):
        """Test broadcasting mission completed event."""
        manager = PersonaWSManager()
        
        sent_count = await manager.broadcast_mission_completed(
            mission_id="mission-003",
            mission_data={"status": "completed", "success": True},
        )
        
        assert sent_count >= 0


class TestDisconnection:
    """Tests for disconnection handling."""
    
    @pytest.mark.asyncio
    async def test_disconnect(self):
        """Test disconnecting a connection."""
        manager = PersonaWSManager()
        mock_websocket = AsyncMock()
        
        await manager.connect_alerts(
            connection_id="test-disconnect-001",
            user_id="test-user",
            websocket=mock_websocket,
        )
        
        await manager.disconnect("test-disconnect-001")
        
        info = manager.get_connection_info("test-disconnect-001")
        assert info is None
    
    @pytest.mark.asyncio
    async def test_disconnect_nonexistent(self):
        """Test disconnecting non-existent connection."""
        manager = PersonaWSManager()
        
        await manager.disconnect("nonexistent-connection")


class TestConnectionInfo:
    """Tests for connection info retrieval."""
    
    @pytest.mark.asyncio
    async def test_get_connection_info(self):
        """Test getting connection info."""
        manager = PersonaWSManager()
        mock_websocket = AsyncMock()
        
        await manager.connect_alerts(
            connection_id="test-info-001",
            user_id="test-user",
            websocket=mock_websocket,
        )
        
        info = manager.get_connection_info("test-info-001")
        
        assert info is not None
        assert info["connection_id"] == "test-info-001"
        assert info["user_id"] == "test-user"
        assert info["channel"] == "alerts"
        
        await manager.disconnect("test-info-001")
    
    def test_get_connection_info_nonexistent(self):
        """Test getting info for non-existent connection."""
        manager = PersonaWSManager()
        
        info = manager.get_connection_info("nonexistent")
        assert info is None
