"""
Test Suite 13: WebSocket Channel Tests

Tests for Cyber Intel WebSocket channels.
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch, AsyncMock, MagicMock
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))


class TestWebSocketChannels:
    """Tests for Cyber Intel WebSocket channels"""
    
    def test_router_initialization(self):
        """Test WebSocket router initializes correctly"""
        from backend.app.websockets.cyber_intel_ws import router
        
        assert router is not None
    
    def test_connection_manager_initialization(self):
        """Test CyberIntelConnectionManager initializes correctly"""
        from backend.app.websockets.cyber_intel_ws import CyberIntelConnectionManager
        
        manager = CyberIntelConnectionManager()
        
        assert manager is not None
        assert "threats" in manager.active_connections
        assert "quantum" in manager.active_connections
        assert "disinfo" in manager.active_connections
        assert "alerts" in manager.active_connections
    
    def test_connection_manager_channels(self):
        """Test connection manager has all required channels"""
        from backend.app.websockets.cyber_intel_ws import CyberIntelConnectionManager
        
        manager = CyberIntelConnectionManager()
        
        assert len(manager.active_connections) == 4
        assert "threats" in manager.active_connections
        assert "quantum" in manager.active_connections
        assert "disinfo" in manager.active_connections
        assert "alerts" in manager.active_connections
    
    def test_get_connection_count(self):
        """Test getting connection count"""
        from backend.app.websockets.cyber_intel_ws import CyberIntelConnectionManager
        
        manager = CyberIntelConnectionManager()
        
        count = manager.get_connection_count("threats")
        assert count == 0
        
        count = manager.get_connection_count("quantum")
        assert count == 0
    
    def test_threats_websocket_endpoint_exists(self):
        """Test threats WebSocket endpoint exists"""
        from backend.app.websockets.cyber_intel_ws import router
        
        routes = [route.path for route in router.routes]
        assert "/ws/cyber-intel/threats" in routes
    
    def test_quantum_websocket_endpoint_exists(self):
        """Test quantum WebSocket endpoint exists"""
        from backend.app.websockets.cyber_intel_ws import router
        
        routes = [route.path for route in router.routes]
        assert "/ws/cyber-intel/quantum" in routes
    
    def test_disinfo_websocket_endpoint_exists(self):
        """Test disinfo WebSocket endpoint exists"""
        from backend.app.websockets.cyber_intel_ws import router
        
        routes = [route.path for route in router.routes]
        assert "/ws/cyber-intel/disinfo" in routes
    
    def test_alerts_websocket_endpoint_exists(self):
        """Test alerts WebSocket endpoint exists"""
        from backend.app.websockets.cyber_intel_ws import router
        
        routes = [route.path for route in router.routes]
        assert "/ws/cyber-intel/alerts" in routes
    
    def test_broadcast_cyber_threat_function(self):
        """Test broadcast_cyber_threat function exists"""
        from backend.app.websockets.cyber_intel_ws import broadcast_cyber_threat
        
        assert broadcast_cyber_threat is not None
        assert callable(broadcast_cyber_threat)
    
    def test_broadcast_quantum_alert_function(self):
        """Test broadcast_quantum_alert function exists"""
        from backend.app.websockets.cyber_intel_ws import broadcast_quantum_alert
        
        assert broadcast_quantum_alert is not None
        assert callable(broadcast_quantum_alert)
    
    def test_broadcast_disinfo_alert_function(self):
        """Test broadcast_disinfo_alert function exists"""
        from backend.app.websockets.cyber_intel_ws import broadcast_disinfo_alert
        
        assert broadcast_disinfo_alert is not None
        assert callable(broadcast_disinfo_alert)
    
    @pytest.mark.asyncio
    async def test_connection_manager_connect(self):
        """Test connection manager connect method"""
        from backend.app.websockets.cyber_intel_ws import CyberIntelConnectionManager
        
        manager = CyberIntelConnectionManager()
        
        mock_websocket = AsyncMock()
        mock_websocket.accept = AsyncMock()
        
        await manager.connect(mock_websocket, "threats", "user-123")
        
        mock_websocket.accept.assert_called_once()
        assert mock_websocket in manager.active_connections["threats"]
    
    def test_connection_manager_disconnect(self):
        """Test connection manager disconnect method"""
        from backend.app.websockets.cyber_intel_ws import CyberIntelConnectionManager
        
        manager = CyberIntelConnectionManager()
        
        mock_websocket = MagicMock()
        manager.active_connections["threats"].append(mock_websocket)
        manager.connection_metadata[mock_websocket] = {"channel": "threats"}
        
        manager.disconnect(mock_websocket, "threats")
        
        assert mock_websocket not in manager.active_connections["threats"]
        assert mock_websocket not in manager.connection_metadata
    
    @pytest.mark.asyncio
    async def test_connection_manager_broadcast(self):
        """Test connection manager broadcast method"""
        from backend.app.websockets.cyber_intel_ws import CyberIntelConnectionManager
        
        manager = CyberIntelConnectionManager()
        
        mock_websocket = AsyncMock()
        mock_websocket.send_json = AsyncMock()
        manager.active_connections["threats"].append(mock_websocket)
        
        message = {"type": "test", "data": "test_data"}
        await manager.broadcast("threats", message)
        
        mock_websocket.send_json.assert_called_once_with(message)
    
    @pytest.mark.asyncio
    async def test_connection_manager_send_personal(self):
        """Test connection manager send_personal method"""
        from backend.app.websockets.cyber_intel_ws import CyberIntelConnectionManager
        
        manager = CyberIntelConnectionManager()
        
        mock_websocket = AsyncMock()
        mock_websocket.send_json = AsyncMock()
        
        message = {"type": "personal", "data": "personal_data"}
        await manager.send_personal(mock_websocket, message)
        
        mock_websocket.send_json.assert_called_once_with(message)
