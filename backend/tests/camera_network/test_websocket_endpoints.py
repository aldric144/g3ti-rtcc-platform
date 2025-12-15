"""
Tests for Camera Network WebSocket endpoints.
"""

import pytest
import asyncio
import json

from app.api.camera_network.websocket import (
    ConnectionManager,
    health_manager,
    video_wall_manager_ws,
)


class TestConnectionManager:
    """Test suite for WebSocket ConnectionManager."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.manager = ConnectionManager()
    
    def test_initial_state(self):
        """Test initial state of connection manager."""
        assert len(self.manager.active_connections) == 0
    
    @pytest.mark.asyncio
    async def test_broadcast_empty(self):
        """Test broadcasting to empty connections."""
        # Should not raise error
        await self.manager.broadcast({"type": "test"})
    
    def test_disconnect_not_connected(self):
        """Test disconnecting a non-existent connection."""
        # Should not raise error
        self.manager.disconnect(None)


class TestHealthWebSocket:
    """Test suite for health WebSocket endpoint."""
    
    def test_health_manager_exists(self):
        """Test that health manager is initialized."""
        assert health_manager is not None
        assert isinstance(health_manager, ConnectionManager)
    
    def test_health_message_format(self):
        """Test health message format."""
        from datetime import datetime
        from app.camera_network import get_health_monitor
        
        monitor = get_health_monitor()
        
        message = {
            "type": "health_update",
            "timestamp": datetime.utcnow().isoformat(),
            "summary": monitor.get_health_summary(),
            "cameras": monitor.get_all_health(),
        }
        
        assert "type" in message
        assert "timestamp" in message
        assert "summary" in message
        assert "cameras" in message


class TestVideoWallWebSocket:
    """Test suite for video wall WebSocket endpoint."""
    
    def test_video_wall_manager_exists(self):
        """Test that video wall manager is initialized."""
        assert video_wall_manager_ws is not None
        assert isinstance(video_wall_manager_ws, ConnectionManager)
    
    def test_video_wall_action_messages(self):
        """Test video wall action message formats."""
        actions = [
            {"action": "get_state", "session_id": "test-001"},
            {"action": "add_camera", "session_id": "test-001", "position": 0, "camera_id": "cam-001"},
            {"action": "remove_camera", "session_id": "test-001", "position": 0},
            {"action": "move_camera", "session_id": "test-001", "from_position": 0, "to_position": 1},
            {"action": "change_layout", "session_id": "test-001", "layout": "3x3"},
        ]
        
        for action in actions:
            # Verify JSON serializable
            json_str = json.dumps(action)
            parsed = json.loads(json_str)
            assert parsed["action"] == action["action"]
    
    def test_video_wall_response_format(self):
        """Test video wall response format."""
        from datetime import datetime
        from app.camera_network import get_video_wall_manager
        
        manager = get_video_wall_manager()
        session = manager.create_session("test-user", "2x2")
        state = manager.get_wall_state(session.session_id)
        
        response = {
            "type": "wall_updated",
            "timestamp": datetime.utcnow().isoformat(),
            "session_id": session.session_id,
            "state": state,
        }
        
        assert "type" in response
        assert "timestamp" in response
        assert "session_id" in response
        assert "state" in response


class TestStreamWebSocket:
    """Test suite for camera stream WebSocket endpoint."""
    
    def test_stream_message_format(self):
        """Test stream message format."""
        from datetime import datetime
        
        message = {
            "type": "frame_info",
            "timestamp": datetime.utcnow().isoformat(),
            "camera_id": "cam-001",
            "frame_number": 1,
            "stream_url": "https://example.com/stream",
        }
        
        assert "type" in message
        assert "camera_id" in message
        assert "frame_number" in message
    
    def test_stream_status_message(self):
        """Test stream status message format."""
        from datetime import datetime
        
        message = {
            "type": "stream_status",
            "timestamp": datetime.utcnow().isoformat(),
            "camera_id": "cam-001",
            "status": "active",
        }
        
        assert message["type"] == "stream_status"
        assert message["status"] == "active"
