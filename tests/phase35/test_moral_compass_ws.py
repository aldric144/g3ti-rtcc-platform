"""
Test Suite: Moral Compass WebSocket

Phase 35: AI Moral Compass & Societal Ethics Reasoning Engine
Tests for WebSocket channels and real-time alerts.
"""

import pytest
from datetime import datetime

from backend.app.websockets.moral_compass_ws import (
    MoralCompassWSManager,
    MoralWSChannel,
    MoralAlertType,
    MoralAlertSeverity,
    MoralWSConnection,
    MoralWSMessage,
    MoralAlert,
)


class TestMoralWSChannel:
    """Tests for MoralWSChannel enum."""

    def test_channels_exist(self):
        channels = [
            MoralWSChannel.ALERTS,
            MoralWSChannel.VIOLATIONS,
            MoralWSChannel.REASONING,
            MoralWSChannel.FAIRNESS,
        ]
        assert len(channels) == 4


class TestMoralAlertType:
    """Tests for MoralAlertType enum."""

    def test_alert_types_exist(self):
        types = [
            MoralAlertType.ETHICAL_VIOLATION,
            MoralAlertType.BIAS_DETECTED,
            MoralAlertType.HIGH_RISK_ACTION,
            MoralAlertType.COMMUNITY_HARM_RISK,
            MoralAlertType.FAIRNESS_CONCERN,
            MoralAlertType.GUARDRAIL_TRIGGERED,
            MoralAlertType.VETO_ISSUED,
            MoralAlertType.APPROVAL_REQUIRED,
        ]
        assert len(types) == 8


class TestMoralAlertSeverity:
    """Tests for MoralAlertSeverity enum."""

    def test_severity_levels_exist(self):
        levels = [
            MoralAlertSeverity.INFO,
            MoralAlertSeverity.WARNING,
            MoralAlertSeverity.SERIOUS,
            MoralAlertSeverity.CRITICAL,
            MoralAlertSeverity.BLOCKING,
        ]
        assert len(levels) == 5


class TestMoralCompassWSManager:
    """Tests for MoralCompassWSManager singleton."""

    def test_singleton_pattern(self):
        manager1 = MoralCompassWSManager()
        manager2 = MoralCompassWSManager()
        assert manager1 is manager2

    def test_initialization(self):
        manager = MoralCompassWSManager()
        assert manager._initialized is True
        assert len(manager.channel_connections) == 4

    @pytest.mark.asyncio
    async def test_connect(self):
        manager = MoralCompassWSManager()
        mock_websocket = object()
        connection = await manager.connect(
            channel=MoralWSChannel.ALERTS,
            user_id="user_001",
            websocket=mock_websocket,
        )
        assert connection is not None
        assert connection.connection_id is not None
        assert connection.channel == MoralWSChannel.ALERTS

    @pytest.mark.asyncio
    async def test_disconnect(self):
        manager = MoralCompassWSManager()
        mock_websocket = object()
        connection = await manager.connect(
            channel=MoralWSChannel.VIOLATIONS,
            user_id="user_002",
            websocket=mock_websocket,
        )
        result = await manager.disconnect(connection.connection_id)
        assert result is True

    @pytest.mark.asyncio
    async def test_broadcast_alert(self):
        manager = MoralCompassWSManager()
        alert = MoralAlert(
            alert_type=MoralAlertType.ETHICAL_VIOLATION,
            severity=MoralAlertSeverity.SERIOUS,
            title="Test Alert",
            description="Test description",
            action_type="test",
            requester_id="test_user",
        )
        count = await manager.broadcast_alert(alert)
        assert count >= 0

    @pytest.mark.asyncio
    async def test_broadcast_violation(self):
        manager = MoralCompassWSManager()
        count = await manager.broadcast_violation(
            violation_id="viol-123",
            violation_type="constitutional",
            severity="critical",
            details={"rule": "4th_amendment"},
        )
        assert count >= 0

    @pytest.mark.asyncio
    async def test_broadcast_reasoning_update(self):
        manager = MoralCompassWSManager()
        count = await manager.broadcast_reasoning_update(
            capsule_id="cap-123",
            action_type="search",
            decision="allow",
            reasoning_summary="Action permitted",
            confidence=0.9,
        )
        assert count >= 0

    @pytest.mark.asyncio
    async def test_broadcast_fairness_alert(self):
        manager = MoralCompassWSManager()
        count = await manager.broadcast_fairness_alert(
            alert_id="fair-123",
            disparity_type="geographic",
            severity="moderate",
            affected_groups=["area_a"],
            recommendations=["Review allocation"],
        )
        assert count >= 0

    @pytest.mark.asyncio
    async def test_send_ethical_violation_alert(self):
        manager = MoralCompassWSManager()
        alert = await manager.send_ethical_violation_alert(
            action_type="search",
            requester_id="officer_001",
            violation_details="Warrantless search attempted",
            severity=MoralAlertSeverity.SERIOUS,
        )
        assert alert is not None
        assert alert.alert_type == MoralAlertType.ETHICAL_VIOLATION

    @pytest.mark.asyncio
    async def test_send_bias_alert(self):
        manager = MoralCompassWSManager()
        alert = await manager.send_bias_alert(
            action_type="targeting",
            bias_type="historical",
            confidence=0.8,
            mitigation_strategies=["Review data"],
        )
        assert alert is not None
        assert alert.alert_type == MoralAlertType.BIAS_DETECTED

    @pytest.mark.asyncio
    async def test_send_high_risk_alert(self):
        manager = MoralCompassWSManager()
        alert = await manager.send_high_risk_alert(
            action_type="use_of_force",
            requester_id="officer_002",
            risk_factors=["high_visibility", "vulnerable_population"],
            required_approvals=["supervisor"],
        )
        assert alert is not None
        assert alert.alert_type == MoralAlertType.HIGH_RISK_ACTION

    @pytest.mark.asyncio
    async def test_send_community_harm_alert(self):
        manager = MoralCompassWSManager()
        alert = await manager.send_community_harm_alert(
            action_type="raid",
            location="Downtown",
            harm_risk_score=75.0,
            community_considerations=["high_trust_area"],
        )
        assert alert is not None
        assert alert.alert_type == MoralAlertType.COMMUNITY_HARM_RISK

    @pytest.mark.asyncio
    async def test_send_veto_notification(self):
        manager = MoralCompassWSManager()
        alert = await manager.send_veto_notification(
            action_type="warrantless_search",
            requester_id="officer_003",
            reason="Constitutional violation",
            alternatives=["Obtain warrant"],
        )
        assert alert is not None
        assert alert.alert_type == MoralAlertType.VETO_ISSUED

    @pytest.mark.asyncio
    async def test_send_approval_request(self):
        manager = MoralCompassWSManager()
        alert = await manager.send_approval_request(
            action_type="high_risk_operation",
            requester_id="officer_004",
            approval_type="supervisor",
            required_authority="lieutenant",
            urgency="high",
        )
        assert alert is not None
        assert alert.alert_type == MoralAlertType.APPROVAL_REQUIRED

    def test_get_active_alerts(self):
        manager = MoralCompassWSManager()
        alerts = manager.get_active_alerts()
        assert isinstance(alerts, list)

    def test_acknowledge_alert(self):
        manager = MoralCompassWSManager()
        alert = MoralAlert(
            alert_type=MoralAlertType.ETHICAL_VIOLATION,
            severity=MoralAlertSeverity.WARNING,
            title="Test",
            description="Test",
            action_type="test",
            requester_id="test",
        )
        manager.alerts[alert.alert_id] = alert
        result = manager.acknowledge_alert(alert.alert_id)
        assert result is True
        assert alert.acknowledged is True

    def test_get_statistics(self):
        manager = MoralCompassWSManager()
        stats = manager.get_statistics()
        assert "total_connections" in stats
        assert "total_messages_sent" in stats
        assert "total_alerts_broadcast" in stats
        assert "active_connections" in stats


class TestMoralWSConnection:
    """Tests for MoralWSConnection dataclass."""

    def test_connection_creation(self):
        connection = MoralWSConnection(
            channel=MoralWSChannel.ALERTS,
            user_id="user_001",
        )
        assert connection.connection_id is not None
        assert connection.channel == MoralWSChannel.ALERTS

    def test_connection_to_dict(self):
        connection = MoralWSConnection(
            channel=MoralWSChannel.REASONING,
            user_id="user_002",
        )
        data = connection.to_dict()
        assert data["channel"] == "reasoning"
        assert data["user_id"] == "user_002"


class TestMoralWSMessage:
    """Tests for MoralWSMessage dataclass."""

    def test_message_creation(self):
        message = MoralWSMessage(
            channel=MoralWSChannel.VIOLATIONS,
            message_type="violation_alert",
            payload={"test": "data"},
        )
        assert message.message_id is not None
        assert message.channel == MoralWSChannel.VIOLATIONS

    def test_message_to_json(self):
        message = MoralWSMessage(
            channel=MoralWSChannel.FAIRNESS,
            message_type="fairness_update",
            payload={"score": 0.85},
        )
        json_str = message.to_json()
        assert "fairness" in json_str
        assert "0.85" in json_str


class TestMoralAlert:
    """Tests for MoralAlert dataclass."""

    def test_alert_creation(self):
        alert = MoralAlert(
            alert_type=MoralAlertType.BIAS_DETECTED,
            severity=MoralAlertSeverity.WARNING,
            title="Bias Alert",
            description="Potential bias detected",
            action_type="targeting",
            requester_id="system_001",
        )
        assert alert.alert_id is not None
        assert alert.acknowledged is False

    def test_alert_to_dict(self):
        alert = MoralAlert(
            alert_type=MoralAlertType.HIGH_RISK_ACTION,
            severity=MoralAlertSeverity.CRITICAL,
            title="High Risk",
            description="High risk action",
            action_type="force",
            requester_id="officer_001",
            requires_action=True,
        )
        data = alert.to_dict()
        assert data["alert_type"] == "high_risk_action"
        assert data["severity"] == "critical"
        assert data["requires_action"] is True
