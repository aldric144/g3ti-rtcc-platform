"""Tests for Crime Analysis WebSocket Handler."""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from app.crime_analysis.websocket_handler import (
    CrimeWebSocketManager,
    CrimeAlert,
    get_crime_ws_manager,
    crime_alerts_websocket,
)


class TestCrimeAlert:
    """Test suite for CrimeAlert model."""

    def test_alert_creation(self):
        """Test creating a crime alert."""
        alert = CrimeAlert(
            alert_id="alert-001",
            alert_type="spike",
            severity="high",
            title="Crime Spike Detected",
            description="Unusual increase in crime activity",
            timestamp=datetime.utcnow().isoformat(),
        )
        
        assert alert.alert_id == "alert-001"
        assert alert.alert_type == "spike"
        assert alert.severity == "high"

    def test_alert_with_location(self):
        """Test creating an alert with location."""
        alert = CrimeAlert(
            alert_id="alert-002",
            alert_type="repeat_location",
            severity="medium",
            title="Repeat Location Hotspot",
            description="Multiple incidents at location",
            location={"latitude": 26.78, "longitude": -80.07},
            sector="Sector 1",
            timestamp=datetime.utcnow().isoformat(),
        )
        
        assert alert.location is not None
        assert alert.location["latitude"] == 26.78
        assert alert.sector == "Sector 1"

    def test_alert_with_data(self):
        """Test creating an alert with additional data."""
        alert = CrimeAlert(
            alert_id="alert-003",
            alert_type="high_risk_zone",
            severity="critical",
            title="High Risk Zone",
            description="Sector has elevated risk",
            timestamp=datetime.utcnow().isoformat(),
            data={"score": 4.5, "incidents": 15},
        )
        
        assert alert.data is not None
        assert alert.data["score"] == 4.5


class TestCrimeWebSocketManager:
    """Test suite for CrimeWebSocketManager class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.manager = CrimeWebSocketManager()

    def test_manager_initialization(self):
        """Test manager initializes correctly."""
        assert self.manager.active_connections == set()
        assert self.manager._alert_counter == 0
        assert self.manager._running is False

    def test_generate_alert_id(self):
        """Test alert ID generation."""
        id1 = self.manager._generate_alert_id()
        id2 = self.manager._generate_alert_id()
        
        assert id1 != id2
        assert id1.startswith("alert-")
        assert id2.startswith("alert-")

    def test_generate_alert_id_increments(self):
        """Test alert ID counter increments."""
        initial_counter = self.manager._alert_counter
        self.manager._generate_alert_id()
        
        assert self.manager._alert_counter == initial_counter + 1

    @pytest.mark.asyncio
    async def test_connect(self):
        """Test WebSocket connection."""
        mock_websocket = AsyncMock()
        
        await self.manager.connect(mock_websocket)
        
        assert mock_websocket in self.manager.active_connections
        mock_websocket.accept.assert_called_once()

    def test_disconnect(self):
        """Test WebSocket disconnection."""
        mock_websocket = MagicMock()
        self.manager.active_connections.add(mock_websocket)
        
        self.manager.disconnect(mock_websocket)
        
        assert mock_websocket not in self.manager.active_connections

    def test_disconnect_nonexistent(self):
        """Test disconnecting non-existent connection."""
        mock_websocket = MagicMock()
        
        # Should not raise error
        self.manager.disconnect(mock_websocket)
        
        assert mock_websocket not in self.manager.active_connections

    @pytest.mark.asyncio
    async def test_broadcast(self):
        """Test broadcasting alert to connections."""
        mock_ws1 = AsyncMock()
        mock_ws2 = AsyncMock()
        self.manager.active_connections = {mock_ws1, mock_ws2}
        
        alert = CrimeAlert(
            alert_id="alert-001",
            alert_type="spike",
            severity="high",
            title="Test Alert",
            description="Test description",
            timestamp=datetime.utcnow().isoformat(),
        )
        
        await self.manager.broadcast(alert)
        
        assert mock_ws1.send_json.called
        assert mock_ws2.send_json.called

    @pytest.mark.asyncio
    async def test_broadcast_handles_disconnected(self):
        """Test broadcast handles disconnected clients."""
        mock_ws1 = AsyncMock()
        mock_ws2 = AsyncMock()
        mock_ws2.send_json.side_effect = Exception("Connection closed")
        self.manager.active_connections = {mock_ws1, mock_ws2}
        
        alert = CrimeAlert(
            alert_id="alert-001",
            alert_type="spike",
            severity="high",
            title="Test Alert",
            description="Test description",
            timestamp=datetime.utcnow().isoformat(),
        )
        
        await self.manager.broadcast(alert)
        
        # ws2 should be disconnected
        assert mock_ws2 not in self.manager.active_connections

    @pytest.mark.asyncio
    async def test_send_to_client(self):
        """Test sending data to specific client."""
        mock_websocket = AsyncMock()
        
        await self.manager._send_to_client(mock_websocket, {"type": "test"})
        
        mock_websocket.send_json.assert_called_once_with({"type": "test"})

    @pytest.mark.asyncio
    async def test_send_to_client_handles_error(self):
        """Test send handles connection errors."""
        mock_websocket = AsyncMock()
        mock_websocket.send_json.side_effect = Exception("Connection closed")
        self.manager.active_connections.add(mock_websocket)
        
        await self.manager._send_to_client(mock_websocket, {"type": "test"})
        
        # Should disconnect the client
        assert mock_websocket not in self.manager.active_connections


class TestWebSocketSingleton:
    """Test suite for WebSocket manager singleton."""

    def test_get_crime_ws_manager_singleton(self):
        """Test global manager singleton."""
        manager1 = get_crime_ws_manager()
        manager2 = get_crime_ws_manager()
        
        assert manager1 is manager2

    def test_manager_type(self):
        """Test manager is correct type."""
        manager = get_crime_ws_manager()
        
        assert isinstance(manager, CrimeWebSocketManager)
