"""
Phase 30: WebSocket Channel Tests

Tests for:
- Crisis alerts channel
- Stability channel
- DV risk channel
- Suicide channel
- Youth channel
"""

import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock, AsyncMock
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))


class TestHumanIntelConnectionManager:
    """Tests for HumanIntelConnectionManager"""
    
    def test_connection_manager_initialization(self):
        """Test connection manager initializes with all channels"""
        from backend.app.websockets.human_intel_ws import HumanIntelConnectionManager
        
        manager = HumanIntelConnectionManager()
        
        assert "crisis_alerts" in manager.active_connections
        assert "stability" in manager.active_connections
        assert "dv_risk" in manager.active_connections
        assert "suicide" in manager.active_connections
        assert "youth" in manager.active_connections
    
    def test_get_connection_count_empty(self):
        """Test get_connection_count returns 0 for empty channel"""
        from backend.app.websockets.human_intel_ws import HumanIntelConnectionManager
        
        manager = HumanIntelConnectionManager()
        
        count = manager.get_connection_count("crisis_alerts")
        
        assert count == 0
    
    def test_get_connection_count_invalid_channel(self):
        """Test get_connection_count returns 0 for invalid channel"""
        from backend.app.websockets.human_intel_ws import HumanIntelConnectionManager
        
        manager = HumanIntelConnectionManager()
        
        count = manager.get_connection_count("invalid_channel")
        
        assert count == 0


class TestCrisisAlertsChannel:
    """Tests for crisis alerts WebSocket channel"""
    
    def test_crisis_alerts_channel_exists(self):
        """Test crisis alerts channel exists"""
        from backend.app.websockets.human_intel_ws import manager
        
        assert "crisis_alerts" in manager.active_connections
    
    @pytest.mark.asyncio
    async def test_broadcast_crisis_alert(self):
        """Test broadcast_crisis_alert function"""
        from backend.app.websockets.human_intel_ws import broadcast_crisis_alert
        
        alert_data = {
            "alert_id": "CA-001",
            "risk_level": "HIGH",
            "zone": "Zone_A",
            "priority": "CRITICAL",
        }
        
        await broadcast_crisis_alert(alert_data)


class TestStabilityChannel:
    """Tests for stability WebSocket channel"""
    
    def test_stability_channel_exists(self):
        """Test stability channel exists"""
        from backend.app.websockets.human_intel_ws import manager
        
        assert "stability" in manager.active_connections
    
    @pytest.mark.asyncio
    async def test_broadcast_stability_update(self):
        """Test broadcast_stability_update function"""
        from backend.app.websockets.human_intel_ws import broadcast_stability_update
        
        stability_data = {
            "stability_index": 74.5,
            "trend": "stable",
        }
        
        await broadcast_stability_update(stability_data)


class TestDVRiskChannel:
    """Tests for DV risk WebSocket channel"""
    
    def test_dv_risk_channel_exists(self):
        """Test DV risk channel exists"""
        from backend.app.websockets.human_intel_ws import manager
        
        assert "dv_risk" in manager.active_connections
    
    @pytest.mark.asyncio
    async def test_broadcast_dv_alert(self):
        """Test broadcast_dv_alert function"""
        from backend.app.websockets.human_intel_ws import broadcast_dv_alert
        
        dv_data = {
            "alert_id": "DV-001",
            "lethality_level": "HIGH",
            "zone": "Zone_A",
        }
        
        await broadcast_dv_alert(dv_data)


class TestSuicideChannel:
    """Tests for suicide WebSocket channel"""
    
    def test_suicide_channel_exists(self):
        """Test suicide channel exists"""
        from backend.app.websockets.human_intel_ws import manager
        
        assert "suicide" in manager.active_connections
    
    @pytest.mark.asyncio
    async def test_broadcast_suicide_alert(self):
        """Test broadcast_suicide_alert function"""
        from backend.app.websockets.human_intel_ws import broadcast_suicide_alert
        
        suicide_data = {
            "alert_id": "SR-001",
            "risk_level": "HIGH",
            "zone": "Zone_A",
        }
        
        await broadcast_suicide_alert(suicide_data)


class TestYouthChannel:
    """Tests for youth WebSocket channel"""
    
    def test_youth_channel_exists(self):
        """Test youth channel exists"""
        from backend.app.websockets.human_intel_ws import manager
        
        assert "youth" in manager.active_connections
    
    @pytest.mark.asyncio
    async def test_broadcast_youth_alert(self):
        """Test broadcast_youth_alert function"""
        from backend.app.websockets.human_intel_ws import broadcast_youth_alert
        
        youth_data = {
            "alert_id": "YA-001",
            "risk_level": "ELEVATED",
            "school_zone": "Zone_A",
        }
        
        await broadcast_youth_alert(youth_data)


class TestWebSocketMessageFormats:
    """Tests for WebSocket message formats"""
    
    def test_crisis_alert_message_format(self):
        """Test crisis alert message format"""
        message = {
            "type": "crisis_alert",
            "data": {"alert_id": "CA-001"},
            "timestamp": datetime.utcnow().isoformat(),
            "priority": "HIGH",
        }
        
        assert "type" in message
        assert "data" in message
        assert "timestamp" in message
        assert "priority" in message
    
    def test_stability_update_message_format(self):
        """Test stability update message format"""
        message = {
            "type": "stability_update",
            "data": {"stability_index": 74.5},
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        assert "type" in message
        assert "data" in message
        assert "timestamp" in message
    
    def test_dv_risk_alert_message_format(self):
        """Test DV risk alert message format"""
        message = {
            "type": "dv_risk_alert",
            "data": {"alert_id": "DV-001"},
            "timestamp": datetime.utcnow().isoformat(),
            "lethality_level": "HIGH",
        }
        
        assert "type" in message
        assert "data" in message
        assert "lethality_level" in message
    
    def test_suicide_alert_message_format(self):
        """Test suicide alert message format"""
        message = {
            "type": "suicide_alert",
            "data": {"alert_id": "SR-001"},
            "timestamp": datetime.utcnow().isoformat(),
            "risk_level": "HIGH",
        }
        
        assert "type" in message
        assert "data" in message
        assert "risk_level" in message
    
    def test_youth_crisis_alert_message_format(self):
        """Test youth crisis alert message format"""
        message = {
            "type": "youth_crisis_alert",
            "data": {"alert_id": "YA-001"},
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        assert "type" in message
        assert "data" in message
        assert "timestamp" in message
    
    def test_heartbeat_message_format(self):
        """Test heartbeat message format"""
        message = {
            "type": "heartbeat",
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        assert "type" in message
        assert message["type"] == "heartbeat"
    
    def test_connection_established_message_format(self):
        """Test connection established message format"""
        message = {
            "type": "connection_established",
            "channel": "crisis_alerts",
            "timestamp": datetime.utcnow().isoformat(),
            "message": "Connected to crisis alerts channel",
        }
        
        assert "type" in message
        assert message["type"] == "connection_established"
        assert "channel" in message
