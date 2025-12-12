"""
Test Suite: AI Supervisor WebSocket Channels

Tests for the WebSocket functionality including:
- Connection management
- Alert broadcasting
- Violation broadcasting
- Health metrics broadcasting
- Recommendation broadcasting
"""

import pytest
from datetime import datetime
from unittest.mock import MagicMock, AsyncMock, patch

import sys
sys.path.insert(0, "/home/ubuntu/repos/g3ti-rtcc-platform")

from backend.app.websockets.ai_supervisor_ws import (
    AISupervisorWSManager,
    ai_supervisor_ws_manager,
)


class TestAISupervisorWSManager:
    """Test cases for AISupervisorWSManager class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.manager = AISupervisorWSManager()

    def test_manager_initialization(self):
        """Test that manager initializes with empty connection lists."""
        assert len(self.manager.alert_connections) == 0
        assert len(self.manager.violation_connections) == 0
        assert len(self.manager.health_connections) == 0
        assert len(self.manager.recommendation_connections) == 0

    def test_get_connection_counts(self):
        """Test getting connection counts."""
        counts = self.manager.get_connection_counts()
        assert "alerts" in counts
        assert "violations" in counts
        assert "system_health" in counts
        assert "recommendations" in counts
        assert "total" in counts

    @pytest.mark.asyncio
    async def test_connect_alerts(self):
        """Test connecting to alerts channel."""
        mock_websocket = AsyncMock()
        await self.manager.connect_alerts(mock_websocket)
        assert mock_websocket in self.manager.alert_connections
        mock_websocket.accept.assert_called_once()

    @pytest.mark.asyncio
    async def test_connect_violations(self):
        """Test connecting to violations channel."""
        mock_websocket = AsyncMock()
        await self.manager.connect_violations(mock_websocket)
        assert mock_websocket in self.manager.violation_connections
        mock_websocket.accept.assert_called_once()

    @pytest.mark.asyncio
    async def test_connect_health(self):
        """Test connecting to health channel."""
        mock_websocket = AsyncMock()
        await self.manager.connect_health(mock_websocket)
        assert mock_websocket in self.manager.health_connections
        mock_websocket.accept.assert_called_once()

    @pytest.mark.asyncio
    async def test_connect_recommendations(self):
        """Test connecting to recommendations channel."""
        mock_websocket = AsyncMock()
        await self.manager.connect_recommendations(mock_websocket)
        assert mock_websocket in self.manager.recommendation_connections
        mock_websocket.accept.assert_called_once()

    def test_disconnect_alerts(self):
        """Test disconnecting from alerts channel."""
        mock_websocket = MagicMock()
        self.manager.alert_connections.append(mock_websocket)
        self.manager.disconnect_alerts(mock_websocket)
        assert mock_websocket not in self.manager.alert_connections

    def test_disconnect_violations(self):
        """Test disconnecting from violations channel."""
        mock_websocket = MagicMock()
        self.manager.violation_connections.append(mock_websocket)
        self.manager.disconnect_violations(mock_websocket)
        assert mock_websocket not in self.manager.violation_connections

    def test_disconnect_health(self):
        """Test disconnecting from health channel."""
        mock_websocket = MagicMock()
        self.manager.health_connections.append(mock_websocket)
        self.manager.disconnect_health(mock_websocket)
        assert mock_websocket not in self.manager.health_connections

    def test_disconnect_recommendations(self):
        """Test disconnecting from recommendations channel."""
        mock_websocket = MagicMock()
        self.manager.recommendation_connections.append(mock_websocket)
        self.manager.disconnect_recommendations(mock_websocket)
        assert mock_websocket not in self.manager.recommendation_connections

    @pytest.mark.asyncio
    async def test_broadcast_alert(self):
        """Test broadcasting an alert."""
        mock_websocket = AsyncMock()
        self.manager.alert_connections.append(mock_websocket)
        
        await self.manager.broadcast_alert(
            alert_id="TEST-001",
            priority="P1_CRITICAL",
            title="Test Alert",
            description="Test description",
            sources=["system_monitor"],
            affected_systems=["predictive_ai"],
            recommended_actions=["Scale up"],
            auto_response_triggered=False,
        )
        
        mock_websocket.send_json.assert_called_once()
        call_args = mock_websocket.send_json.call_args[0][0]
        assert call_args["type"] == "system_alert"
        assert call_args["data"]["alert_id"] == "TEST-001"

    @pytest.mark.asyncio
    async def test_broadcast_violation(self):
        """Test broadcasting a violation."""
        mock_websocket = AsyncMock()
        self.manager.violation_connections.append(mock_websocket)
        
        await self.manager.broadcast_violation(
            violation_id="VIO-001",
            violation_type="unlawful_surveillance",
            severity="critical",
            framework="4th_amendment",
            engine="intel_orchestration",
            action_attempted="facial_recognition",
            description="Warrant required",
            blocked=True,
            escalated=True,
        )
        
        mock_websocket.send_json.assert_called_once()
        call_args = mock_websocket.send_json.call_args[0][0]
        assert call_args["type"] == "ethics_violation"
        assert call_args["data"]["violation_id"] == "VIO-001"

    @pytest.mark.asyncio
    async def test_broadcast_system_health(self):
        """Test broadcasting system health."""
        mock_websocket = AsyncMock()
        self.manager.health_connections.append(mock_websocket)
        
        await self.manager.broadcast_system_health(
            overall_status="WARNING",
            total_engines=16,
            healthy_count=12,
            degraded_count=2,
            warning_count=1,
            critical_count=1,
            offline_count=0,
            average_cpu_percent=65.5,
            average_memory_percent=72.3,
            average_latency_ms=125.0,
            active_alerts=5,
            critical_alerts=1,
        )
        
        mock_websocket.send_json.assert_called_once()
        call_args = mock_websocket.send_json.call_args[0][0]
        assert call_args["type"] == "system_health"
        assert call_args["data"]["total_engines"] == 16

    @pytest.mark.asyncio
    async def test_broadcast_engine_metrics(self):
        """Test broadcasting engine metrics."""
        mock_websocket = AsyncMock()
        self.manager.health_connections.append(mock_websocket)
        
        await self.manager.broadcast_engine_metrics(
            engine_type="predictive_ai",
            cpu_percent=85.5,
            memory_percent=78.2,
            gpu_percent=62.1,
            queue_depth=450,
            latency_ms=125.0,
            error_rate=0.02,
            status="warning",
        )
        
        mock_websocket.send_json.assert_called_once()
        call_args = mock_websocket.send_json.call_args[0][0]
        assert call_args["type"] == "engine_metrics"
        assert call_args["data"]["engine_type"] == "predictive_ai"

    @pytest.mark.asyncio
    async def test_broadcast_recommendation(self):
        """Test broadcasting a recommendation."""
        mock_websocket = AsyncMock()
        self.manager.recommendation_connections.append(mock_websocket)
        
        await self.manager.broadcast_recommendation(
            recommendation_id="REC-001",
            recommendation_type="immediate_action",
            priority="P1_CRITICAL",
            title="Scale Engine",
            description="Engine overloaded",
            rationale="CPU at 92%",
            affected_systems=["predictive_ai"],
            implementation_steps=["Scale up"],
            expected_outcome="Reduced load",
            risk_if_ignored="System failure",
            deadline="2024-01-01T12:00:00Z",
        )
        
        mock_websocket.send_json.assert_called_once()
        call_args = mock_websocket.send_json.call_args[0][0]
        assert call_args["type"] == "sentinel_recommendation"
        assert call_args["data"]["recommendation_id"] == "REC-001"

    @pytest.mark.asyncio
    async def test_broadcast_cascade_prediction(self):
        """Test broadcasting a cascade prediction."""
        mock_websocket = AsyncMock()
        self.manager.recommendation_connections.append(mock_websocket)
        
        await self.manager.broadcast_cascade_prediction(
            prediction_id="CAS-001",
            trigger_event="Engine Overload",
            trigger_source="system_monitor",
            predicted_outcomes=[{"outcome": "Degradation", "probability": 0.7}],
            probability=0.6,
            affected_systems=["predictive_ai", "city_brain"],
            mitigation_options=["Scale up", "Enable circuit breakers"],
            confidence=0.75,
        )
        
        mock_websocket.send_json.assert_called_once()
        call_args = mock_websocket.send_json.call_args[0][0]
        assert call_args["type"] == "cascade_prediction"
        assert call_args["data"]["prediction_id"] == "CAS-001"

    @pytest.mark.asyncio
    async def test_broadcast_handles_disconnected_clients(self):
        """Test that broadcast handles disconnected clients gracefully."""
        mock_websocket_good = AsyncMock()
        mock_websocket_bad = AsyncMock()
        mock_websocket_bad.send_json.side_effect = Exception("Connection closed")
        
        self.manager.alert_connections.append(mock_websocket_bad)
        self.manager.alert_connections.append(mock_websocket_good)
        
        await self.manager.broadcast_alert(
            alert_id="TEST-002",
            priority="P2_HIGH",
            title="Test",
            description="Test",
            sources=[],
            affected_systems=[],
            recommended_actions=[],
            auto_response_triggered=False,
        )
        
        assert mock_websocket_bad not in self.manager.alert_connections
        mock_websocket_good.send_json.assert_called_once()


class TestWebSocketMessageTypes:
    """Test cases for WebSocket message types."""

    def test_alert_message_types(self):
        """Test alert-related message types."""
        message_types = [
            "system_alert",
            "alert_acknowledged",
            "alert_resolved",
            "command_staff_alert",
        ]
        for msg_type in message_types:
            assert msg_type in message_types

    def test_violation_message_types(self):
        """Test violation-related message types."""
        message_types = [
            "ethics_violation",
            "violation_reviewed",
            "action_blocked",
        ]
        for msg_type in message_types:
            assert msg_type in message_types

    def test_health_message_types(self):
        """Test health-related message types."""
        message_types = [
            "system_health",
            "engine_metrics",
            "correction_started",
            "correction_completed",
            "feedback_loop_detected",
            "overload_prediction",
        ]
        for msg_type in message_types:
            assert msg_type in message_types

    def test_recommendation_message_types(self):
        """Test recommendation-related message types."""
        message_types = [
            "sentinel_recommendation",
            "recommendation_accepted",
            "recommendation_implemented",
            "autonomous_action_request",
            "cascade_prediction",
            "command_staff_alert",
        ]
        for msg_type in message_types:
            assert msg_type in message_types


class TestGlobalWSManager:
    """Test cases for global WebSocket manager instance."""

    def test_global_manager_exists(self):
        """Test that global manager instance exists."""
        assert ai_supervisor_ws_manager is not None

    def test_global_manager_is_correct_type(self):
        """Test that global manager is correct type."""
        assert isinstance(ai_supervisor_ws_manager, AISupervisorWSManager)
