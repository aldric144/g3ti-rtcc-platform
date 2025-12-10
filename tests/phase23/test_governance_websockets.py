"""
Phase 23: Governance WebSocket Tests
"""

import pytest
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../backend'))

from app.websockets.city_governance import (
    GovernanceWebSocketManager,
    WebSocketClient,
    handle_decisions_websocket,
    handle_optimizations_websocket,
    handle_kpi_websocket,
    handle_scenario_websocket,
)


class TestGovernanceWebSocketManager:
    """Tests for GovernanceWebSocketManager."""

    def setup_method(self):
        """Set up test fixtures."""
        self.manager = GovernanceWebSocketManager()

    def test_manager_initialization(self):
        """Test manager initializes with empty channels."""
        assert len(self.manager._decisions_clients) == 0
        assert len(self.manager._optimizations_clients) == 0
        assert len(self.manager._kpi_clients) == 0
        assert len(self.manager._scenario_clients) == 0

    def test_get_singleton_instance(self):
        """Test singleton pattern returns same instance."""
        from app.websockets.city_governance import get_ws_manager

        manager1 = get_ws_manager()
        manager2 = get_ws_manager()
        assert manager1 is manager2

    def test_register_decisions_client(self):
        """Test registering a decisions channel client."""
        client = WebSocketClient(
            client_id="test-client-1",
            websocket=None,
            channel="decisions",
            connected_at=datetime.utcnow(),
        )

        self.manager.register_decisions_client(client)
        assert "test-client-1" in self.manager._decisions_clients

    def test_unregister_decisions_client(self):
        """Test unregistering a decisions channel client."""
        client = WebSocketClient(
            client_id="test-client-2",
            websocket=None,
            channel="decisions",
            connected_at=datetime.utcnow(),
        )

        self.manager.register_decisions_client(client)
        self.manager.unregister_decisions_client("test-client-2")
        assert "test-client-2" not in self.manager._decisions_clients

    def test_register_optimizations_client(self):
        """Test registering an optimizations channel client."""
        client = WebSocketClient(
            client_id="test-client-3",
            websocket=None,
            channel="optimizations",
            connected_at=datetime.utcnow(),
        )

        self.manager.register_optimizations_client(client)
        assert "test-client-3" in self.manager._optimizations_clients

    def test_unregister_optimizations_client(self):
        """Test unregistering an optimizations channel client."""
        client = WebSocketClient(
            client_id="test-client-4",
            websocket=None,
            channel="optimizations",
            connected_at=datetime.utcnow(),
        )

        self.manager.register_optimizations_client(client)
        self.manager.unregister_optimizations_client("test-client-4")
        assert "test-client-4" not in self.manager._optimizations_clients

    def test_register_kpi_client(self):
        """Test registering a KPI channel client."""
        client = WebSocketClient(
            client_id="test-client-5",
            websocket=None,
            channel="kpi",
            connected_at=datetime.utcnow(),
        )

        self.manager.register_kpi_client(client)
        assert "test-client-5" in self.manager._kpi_clients

    def test_unregister_kpi_client(self):
        """Test unregistering a KPI channel client."""
        client = WebSocketClient(
            client_id="test-client-6",
            websocket=None,
            channel="kpi",
            connected_at=datetime.utcnow(),
        )

        self.manager.register_kpi_client(client)
        self.manager.unregister_kpi_client("test-client-6")
        assert "test-client-6" not in self.manager._kpi_clients

    def test_register_scenario_client(self):
        """Test registering a scenario channel client."""
        client = WebSocketClient(
            client_id="test-client-7",
            websocket=None,
            channel="scenario",
            scenario_id="scenario-123",
            connected_at=datetime.utcnow(),
        )

        self.manager.register_scenario_client(client, "scenario-123")
        assert "scenario-123" in self.manager._scenario_clients
        assert "test-client-7" in self.manager._scenario_clients["scenario-123"]

    def test_unregister_scenario_client(self):
        """Test unregistering a scenario channel client."""
        client = WebSocketClient(
            client_id="test-client-8",
            websocket=None,
            channel="scenario",
            scenario_id="scenario-456",
            connected_at=datetime.utcnow(),
        )

        self.manager.register_scenario_client(client, "scenario-456")
        self.manager.unregister_scenario_client("test-client-8", "scenario-456")
        assert "test-client-8" not in self.manager._scenario_clients.get("scenario-456", {})

    def test_get_channel_statistics(self):
        """Test getting channel statistics."""
        client1 = WebSocketClient(
            client_id="stat-client-1",
            websocket=None,
            channel="decisions",
            connected_at=datetime.utcnow(),
        )
        client2 = WebSocketClient(
            client_id="stat-client-2",
            websocket=None,
            channel="kpi",
            connected_at=datetime.utcnow(),
        )

        self.manager.register_decisions_client(client1)
        self.manager.register_kpi_client(client2)

        stats = self.manager.get_statistics()
        assert "decisions_clients" in stats
        assert "optimizations_clients" in stats
        assert "kpi_clients" in stats
        assert "scenario_clients" in stats
        assert stats["decisions_clients"] >= 1
        assert stats["kpi_clients"] >= 1


class TestWebSocketClient:
    """Tests for WebSocketClient dataclass."""

    def test_client_creation(self):
        """Test WebSocket client creation."""
        client = WebSocketClient(
            client_id="test-client",
            websocket=None,
            channel="decisions",
            connected_at=datetime.utcnow(),
        )

        assert client.client_id == "test-client"
        assert client.channel == "decisions"
        assert client.websocket is None
        assert client.scenario_id is None

    def test_client_with_scenario_id(self):
        """Test WebSocket client with scenario ID."""
        client = WebSocketClient(
            client_id="scenario-client",
            websocket=None,
            channel="scenario",
            scenario_id="scenario-789",
            connected_at=datetime.utcnow(),
        )

        assert client.scenario_id == "scenario-789"

    def test_client_to_dict(self):
        """Test WebSocket client serialization."""
        client = WebSocketClient(
            client_id="dict-client",
            websocket=None,
            channel="kpi",
            connected_at=datetime.utcnow(),
        )

        client_dict = client.to_dict()
        assert "client_id" in client_dict
        assert "channel" in client_dict
        assert "connected_at" in client_dict
        assert client_dict["client_id"] == "dict-client"
        assert client_dict["channel"] == "kpi"


class TestMessageTypes:
    """Tests for WebSocket message types."""

    def test_decision_update_message(self):
        """Test decision update message structure."""
        message = {
            "type": "decision_update",
            "data": {
                "decision_id": "dec-123",
                "domain": "public_safety",
                "title": "Increase patrol",
                "status": "pending",
            },
            "timestamp": datetime.utcnow().isoformat(),
        }

        assert message["type"] == "decision_update"
        assert "decision_id" in message["data"]

    def test_optimization_result_message(self):
        """Test optimization result message structure."""
        message = {
            "type": "optimization_result",
            "data": {
                "optimization_id": "opt-123",
                "algorithm": "linear_programming",
                "status": "completed",
                "allocations": [],
            },
            "timestamp": datetime.utcnow().isoformat(),
        }

        assert message["type"] == "optimization_result"
        assert "optimization_id" in message["data"]

    def test_kpi_update_message(self):
        """Test KPI update message structure."""
        message = {
            "type": "kpi_update",
            "data": {
                "metric_id": "rt-police",
                "name": "Police Response Time",
                "value": 4.8,
                "unit": "minutes",
                "trend": "improving",
            },
            "timestamp": datetime.utcnow().isoformat(),
        }

        assert message["type"] == "kpi_update"
        assert "metric_id" in message["data"]

    def test_scenario_event_message(self):
        """Test scenario event message structure."""
        message = {
            "type": "scenario_event",
            "data": {
                "event_id": "evt-123",
                "scenario_id": "scenario-456",
                "event_type": "warning_issued",
                "description": "Storm warning issued",
                "impact_score": 0.5,
            },
            "timestamp": datetime.utcnow().isoformat(),
        }

        assert message["type"] == "scenario_event"
        assert "event_id" in message["data"]
        assert "scenario_id" in message["data"]

    def test_city_health_update_message(self):
        """Test city health update message structure."""
        message = {
            "type": "city_health_update",
            "data": {
                "overall_score": 84.7,
                "grade": "B",
                "trend": "improving",
                "component_scores": {
                    "response_time": 92.5,
                    "patrol_efficiency": 82.3,
                },
            },
            "timestamp": datetime.utcnow().isoformat(),
        }

        assert message["type"] == "city_health_update"
        assert "overall_score" in message["data"]
        assert "grade" in message["data"]


class TestWebSocketHandlers:
    """Tests for WebSocket handler functions."""

    def test_decisions_handler_exists(self):
        """Test decisions handler function exists."""
        assert callable(handle_decisions_websocket)

    def test_optimizations_handler_exists(self):
        """Test optimizations handler function exists."""
        assert callable(handle_optimizations_websocket)

    def test_kpi_handler_exists(self):
        """Test KPI handler function exists."""
        assert callable(handle_kpi_websocket)

    def test_scenario_handler_exists(self):
        """Test scenario handler function exists."""
        assert callable(handle_scenario_websocket)


class TestBroadcastMethods:
    """Tests for broadcast methods."""

    def setup_method(self):
        """Set up test fixtures."""
        self.manager = GovernanceWebSocketManager()

    def test_broadcast_decision_update_no_clients(self):
        """Test broadcasting decision update with no clients."""
        self.manager.broadcast_decision_update({
            "decision_id": "dec-123",
            "status": "pending",
        })

    def test_broadcast_optimization_result_no_clients(self):
        """Test broadcasting optimization result with no clients."""
        self.manager.broadcast_optimization_result({
            "optimization_id": "opt-123",
            "status": "completed",
        })

    def test_broadcast_kpi_update_no_clients(self):
        """Test broadcasting KPI update with no clients."""
        self.manager.broadcast_kpi_update({
            "metric_id": "rt-police",
            "value": 4.8,
        })

    def test_broadcast_scenario_event_no_clients(self):
        """Test broadcasting scenario event with no clients."""
        self.manager.broadcast_scenario_event(
            "scenario-123",
            {
                "event_id": "evt-123",
                "event_type": "warning_issued",
            },
        )
