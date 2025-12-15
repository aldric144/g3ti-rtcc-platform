"""
Phase 39 Test Suite: WebSocket Validation
Tests for verifying WebSocket ping, handshake, and broadcast functionality.
"""

import pytest
from typing import Dict, List, Any


class TestWebSocketValidation:
    """Test suite for WebSocket validation."""

    def test_ws_checker_singleton(self):
        """Test WSIntegrationChecker singleton pattern."""
        from app.system.ws_integration_checker import WSIntegrationChecker

        checker1 = WSIntegrationChecker()
        checker2 = WSIntegrationChecker()
        assert checker1 is checker2

    def test_ws_checker_initialization(self):
        """Test WSIntegrationChecker initializes with default channels."""
        from app.system.ws_integration_checker import get_ws_integration_checker

        checker = get_ws_integration_checker()
        assert checker is not None
        assert checker.get_channel_count() > 0

    def test_channel_count_minimum(self):
        """Test that at least 80 WebSocket channels are registered."""
        from app.system.ws_integration_checker import get_ws_integration_checker

        checker = get_ws_integration_checker()
        assert checker.get_channel_count() >= 80

    def test_critical_channels_identified(self):
        """Test that critical channels are properly identified."""
        from app.system.ws_integration_checker import get_ws_integration_checker

        checker = get_ws_integration_checker()
        critical = checker.get_critical_channels()

        assert len(critical) > 0
        for channel in critical:
            assert channel.get("critical", False) is True

    def test_ws_check_status_enum(self):
        """Test WSCheckStatus enum values."""
        from app.system.ws_integration_checker import WSCheckStatus

        assert WSCheckStatus.PASSED.value == "passed"
        assert WSCheckStatus.FAILED.value == "failed"
        assert WSCheckStatus.WARNING.value == "warning"
        assert WSCheckStatus.TIMEOUT.value == "timeout"
        assert WSCheckStatus.SKIPPED.value == "skipped"

    def test_ping_result_structure(self):
        """Test PingResult dataclass structure."""
        from app.system.ws_integration_checker import PingResult, WSCheckStatus

        result = PingResult(
            channel_path="/ws/test",
            latency_ms=10.5,
            status=WSCheckStatus.PASSED,
        )

        assert result.channel_path == "/ws/test"
        assert result.latency_ms == 10.5
        assert result.status == WSCheckStatus.PASSED

    def test_ping_result_to_dict(self):
        """Test PingResult serialization."""
        from app.system.ws_integration_checker import PingResult, WSCheckStatus

        result = PingResult(
            channel_path="/ws/test",
            latency_ms=10.5,
            status=WSCheckStatus.PASSED,
        )

        data = result.to_dict()
        assert data["channel_path"] == "/ws/test"
        assert data["latency_ms"] == 10.5
        assert data["status"] == "passed"

    def test_handshake_result_structure(self):
        """Test HandshakeResult dataclass structure."""
        from app.system.ws_integration_checker import HandshakeResult, WSCheckStatus

        result = HandshakeResult(
            channel_path="/ws/test",
            handshake_ok=True,
            protocol_version="13",
        )

        assert result.channel_path == "/ws/test"
        assert result.handshake_ok is True
        assert result.protocol_version == "13"

    def test_broadcast_result_structure(self):
        """Test BroadcastResult dataclass structure."""
        from app.system.ws_integration_checker import BroadcastResult, WSCheckStatus

        result = BroadcastResult(
            channel_path="/ws/test",
            messages_sent=10,
            messages_received=10,
            success_rate=100.0,
        )

        assert result.channel_path == "/ws/test"
        assert result.messages_sent == 10
        assert result.messages_received == 10
        assert result.success_rate == 100.0

    @pytest.mark.asyncio
    async def test_ping_channel(self):
        """Test pinging a single channel."""
        from app.system.ws_integration_checker import get_ws_integration_checker

        checker = get_ws_integration_checker()
        channel = {"path": "/ws/test", "name": "Test Channel"}

        result = await checker.ping_channel(channel)
        assert result.channel_path == "/ws/test"
        assert result.latency_ms >= 0

    @pytest.mark.asyncio
    async def test_handshake_test(self):
        """Test handshake with a single channel."""
        from app.system.ws_integration_checker import get_ws_integration_checker

        checker = get_ws_integration_checker()
        channel = {"path": "/ws/test", "name": "Test Channel"}

        result = await checker.test_handshake(channel)
        assert result.channel_path == "/ws/test"
        assert result.handshake_ok is True

    @pytest.mark.asyncio
    async def test_broadcast_test(self):
        """Test broadcast simulation on a channel."""
        from app.system.ws_integration_checker import get_ws_integration_checker

        checker = get_ws_integration_checker()
        channel = {"path": "/ws/test", "name": "Test Channel"}

        result = await checker.test_broadcast(channel, message_count=5)
        assert result.channel_path == "/ws/test"
        assert result.messages_sent == 5

    @pytest.mark.asyncio
    async def test_full_check_returns_status(self):
        """Test full check returns WSIntegrationStatus."""
        from app.system.ws_integration_checker import get_ws_integration_checker, WSIntegrationStatus

        checker = get_ws_integration_checker()
        status = await checker.run_full_check(include_stress_test=False)

        assert isinstance(status, WSIntegrationStatus)
        assert len(status.ping_results) > 0
        assert len(status.handshake_results) > 0

    def test_orchestration_channels_registered(self):
        """Test orchestration WebSocket channels are registered."""
        from app.system.ws_integration_checker import get_ws_integration_checker

        checker = get_ws_integration_checker()
        channels = checker._channels

        orchestration_channels = [c for c in channels if "/orchestration" in c["path"]]
        assert len(orchestration_channels) >= 3

    def test_incidents_channel_registered(self):
        """Test incidents WebSocket channel is registered."""
        from app.system.ws_integration_checker import get_ws_integration_checker

        checker = get_ws_integration_checker()
        channels = checker._channels

        incident_channels = [c for c in channels if "/incidents" in c["path"]]
        assert len(incident_channels) >= 1

    def test_alerts_channel_registered(self):
        """Test alerts WebSocket channel is registered."""
        from app.system.ws_integration_checker import get_ws_integration_checker

        checker = get_ws_integration_checker()
        channels = checker._channels

        alert_channels = [c for c in channels if "/alerts" in c["path"]]
        assert len(alert_channels) >= 1

    def test_statistics_retrieval(self):
        """Test statistics retrieval."""
        from app.system.ws_integration_checker import get_ws_integration_checker

        checker = get_ws_integration_checker()
        stats = checker.get_statistics()

        assert "total_channels" in stats
        assert "critical_channels" in stats
        assert stats["total_channels"] >= 80
