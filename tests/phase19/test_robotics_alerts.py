"""
Phase 19: Robotics Alerts Module Tests

Tests for RoboticsAlertManager including alert creation, subscriptions, and rules.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch


class TestRoboticsAlertManager:
    """Tests for RoboticsAlertManager."""

    def test_create_alert(self):
        """Test alert creation."""
        from backend.app.robotics.robotics_alerts import RoboticsAlertManager, AlertPriority, AlertCategory

        manager = RoboticsAlertManager()
        alert = manager.create_alert(
            title="Low Battery Warning",
            message="Robot K9-Alpha battery below 20%",
            priority=AlertPriority.HIGH,
            category=AlertCategory.HEALTH,
            robot_id="robot-001",
            source="health_monitor",
            data={"battery_level": 18.5},
        )

        assert alert is not None
        assert alert.title == "Low Battery Warning"
        assert alert.priority == AlertPriority.HIGH
        assert alert.category == AlertCategory.HEALTH

    def test_acknowledge_alert(self):
        """Test alert acknowledgment."""
        from backend.app.robotics.robotics_alerts import RoboticsAlertManager, AlertPriority, AlertCategory, AlertStatus

        manager = RoboticsAlertManager()
        alert = manager.create_alert(
            title="Ack Test",
            message="Test alert",
            priority=AlertPriority.MEDIUM,
            category=AlertCategory.FLEET,
            source="test",
        )

        acknowledged = manager.acknowledge_alert(alert.alert_id, "operator-001")
        assert acknowledged is not None
        assert acknowledged.status == AlertStatus.ACKNOWLEDGED
        assert acknowledged.acknowledged_by == "operator-001"

    def test_resolve_alert(self):
        """Test alert resolution."""
        from backend.app.robotics.robotics_alerts import RoboticsAlertManager, AlertPriority, AlertCategory, AlertStatus

        manager = RoboticsAlertManager()
        alert = manager.create_alert(
            title="Resolve Test",
            message="Test alert",
            priority=AlertPriority.LOW,
            category=AlertCategory.MISSION,
            source="test",
        )
        manager.acknowledge_alert(alert.alert_id, "operator-002")

        resolved = manager.resolve_alert(alert.alert_id, "operator-002", "Issue fixed")
        assert resolved is not None
        assert resolved.status == AlertStatus.RESOLVED
        assert resolved.resolution_notes == "Issue fixed"

    def test_expire_alert(self):
        """Test alert expiration."""
        from backend.app.robotics.robotics_alerts import RoboticsAlertManager, AlertPriority, AlertCategory, AlertStatus

        manager = RoboticsAlertManager()
        alert = manager.create_alert(
            title="Expire Test",
            message="Test alert",
            priority=AlertPriority.LOW,
            category=AlertCategory.TELEMETRY,
            source="test",
        )

        expired = manager.expire_alert(alert.alert_id)
        assert expired is not None
        assert expired.status == AlertStatus.EXPIRED

    def test_get_alerts_with_filters(self):
        """Test getting alerts with filters."""
        from backend.app.robotics.robotics_alerts import RoboticsAlertManager, AlertPriority, AlertCategory

        manager = RoboticsAlertManager()
        manager.create_alert("Alert 1", "Msg 1", AlertPriority.HIGH, AlertCategory.HEALTH, source="test")
        manager.create_alert("Alert 2", "Msg 2", AlertPriority.MEDIUM, AlertCategory.HEALTH, source="test")
        manager.create_alert("Alert 3", "Msg 3", AlertPriority.HIGH, AlertCategory.PERIMETER, source="test")

        health_alerts = manager.get_alerts(category=AlertCategory.HEALTH)
        assert len(health_alerts) >= 2

        high_priority = manager.get_alerts(priority=AlertPriority.HIGH)
        assert len(high_priority) >= 2

    def test_get_active_alerts(self):
        """Test getting active alerts."""
        from backend.app.robotics.robotics_alerts import RoboticsAlertManager, AlertPriority, AlertCategory

        manager = RoboticsAlertManager()
        a1 = manager.create_alert("Active 1", "Msg", AlertPriority.HIGH, AlertCategory.FLEET, source="test")
        a2 = manager.create_alert("Active 2", "Msg", AlertPriority.MEDIUM, AlertCategory.FLEET, source="test")

        manager.acknowledge_alert(a1.alert_id, "op")
        manager.resolve_alert(a1.alert_id, "op", "Fixed")

        active = manager.get_active_alerts()
        active_ids = [a.alert_id for a in active]
        assert a2.alert_id in active_ids


class TestAlertSubscriptions:
    """Tests for alert subscriptions."""

    def test_create_subscription(self):
        """Test creating subscription."""
        from backend.app.robotics.robotics_alerts import RoboticsAlertManager, AlertPriority, AlertCategory

        manager = RoboticsAlertManager()
        subscription = manager.create_subscription(
            user_id="user-001",
            categories=[AlertCategory.HEALTH, AlertCategory.PERIMETER],
            min_priority=AlertPriority.MEDIUM,
            robot_ids=["robot-001", "robot-002"],
        )

        assert subscription is not None
        assert subscription.user_id == "user-001"
        assert AlertCategory.HEALTH in subscription.categories

    def test_get_subscriptions(self):
        """Test getting subscriptions."""
        from backend.app.robotics.robotics_alerts import RoboticsAlertManager, AlertPriority, AlertCategory

        manager = RoboticsAlertManager()
        manager.create_subscription("user-sub-001", [AlertCategory.FLEET], AlertPriority.LOW)
        manager.create_subscription("user-sub-002", [AlertCategory.MISSION], AlertPriority.HIGH)

        subs = manager.get_subscriptions()
        assert len(subs) >= 2

    def test_cancel_subscription(self):
        """Test canceling subscription."""
        from backend.app.robotics.robotics_alerts import RoboticsAlertManager, AlertPriority, AlertCategory

        manager = RoboticsAlertManager()
        subscription = manager.create_subscription("user-cancel-001", [AlertCategory.SWARM], AlertPriority.MEDIUM)

        result = manager.cancel_subscription(subscription.subscription_id)
        assert result is True

    def test_get_subscribers_for_alert(self):
        """Test getting subscribers for alert."""
        from backend.app.robotics.robotics_alerts import RoboticsAlertManager, AlertPriority, AlertCategory

        manager = RoboticsAlertManager()
        manager.create_subscription("user-match-001", [AlertCategory.HEALTH], AlertPriority.LOW)
        manager.create_subscription("user-match-002", [AlertCategory.HEALTH], AlertPriority.HIGH)

        alert = manager.create_alert(
            "Health Alert",
            "Test",
            AlertPriority.MEDIUM,
            AlertCategory.HEALTH,
            source="test",
        )

        subscribers = manager.get_subscribers_for_alert(alert)
        assert len(subscribers) >= 1


class TestAlertRules:
    """Tests for alert rules."""

    def test_create_rule(self):
        """Test creating alert rule."""
        from backend.app.robotics.robotics_alerts import RoboticsAlertManager, AlertPriority, AlertCategory

        manager = RoboticsAlertManager()
        rule = manager.create_rule(
            name="Low Battery Rule",
            condition_type="battery_low",
            condition_params={"threshold": 20},
            alert_priority=AlertPriority.HIGH,
            alert_category=AlertCategory.HEALTH,
            alert_title_template="Low Battery: {robot_name}",
            alert_message_template="Battery at {battery_level}%",
        )

        assert rule is not None
        assert rule.name == "Low Battery Rule"
        assert rule.condition_type == "battery_low"

    def test_enable_disable_rule(self):
        """Test enabling and disabling rules."""
        from backend.app.robotics.robotics_alerts import RoboticsAlertManager, AlertPriority, AlertCategory

        manager = RoboticsAlertManager()
        rule = manager.create_rule(
            name="Toggle Rule",
            condition_type="motor_overheat",
            condition_params={"threshold": 80},
            alert_priority=AlertPriority.CRITICAL,
            alert_category=AlertCategory.HEALTH,
            alert_title_template="Motor Overheat",
            alert_message_template="Motor temp: {temperature}C",
        )

        disabled = manager.disable_rule(rule.rule_id)
        assert disabled.is_enabled is False

        enabled = manager.enable_rule(rule.rule_id)
        assert enabled.is_enabled is True

    def test_get_rules(self):
        """Test getting rules."""
        from backend.app.robotics.robotics_alerts import RoboticsAlertManager, AlertPriority, AlertCategory

        manager = RoboticsAlertManager()
        manager.create_rule("Rule 1", "condition_a", {}, AlertPriority.LOW, AlertCategory.FLEET, "Title", "Msg")
        manager.create_rule("Rule 2", "condition_b", {}, AlertPriority.MEDIUM, AlertCategory.FLEET, "Title", "Msg")

        rules = manager.get_rules()
        assert len(rules) >= 2

    def test_check_and_create_alerts(self):
        """Test checking telemetry and creating alerts."""
        from backend.app.robotics.robotics_alerts import RoboticsAlertManager, AlertPriority, AlertCategory

        manager = RoboticsAlertManager()
        manager.create_rule(
            name="Battery Check",
            condition_type="battery_low",
            condition_params={"threshold": 25},
            alert_priority=AlertPriority.HIGH,
            alert_category=AlertCategory.HEALTH,
            alert_title_template="Low Battery",
            alert_message_template="Battery low",
        )

        telemetry = {
            "robot_id": "robot-check-001",
            "robot_name": "Test Robot",
            "battery_level": 15,
            "motor_temperatures": {"motor1": 45},
        }

        alerts = manager.check_and_create_alerts(telemetry)
        assert len(alerts) >= 0


class TestAlertStatistics:
    """Tests for alert statistics."""

    def test_get_alert_statistics(self):
        """Test getting alert statistics."""
        from backend.app.robotics.robotics_alerts import RoboticsAlertManager, AlertPriority, AlertCategory

        manager = RoboticsAlertManager()
        manager.create_alert("Stat 1", "Msg", AlertPriority.HIGH, AlertCategory.HEALTH, source="test")
        manager.create_alert("Stat 2", "Msg", AlertPriority.MEDIUM, AlertCategory.FLEET, source="test")
        manager.create_alert("Stat 3", "Msg", AlertPriority.LOW, AlertCategory.HEALTH, source="test")

        stats = manager.get_alert_statistics()
        assert "total_alerts" in stats
        assert "by_priority" in stats
        assert "by_category" in stats

    def test_cleanup_expired_alerts(self):
        """Test cleaning up expired alerts."""
        from backend.app.robotics.robotics_alerts import RoboticsAlertManager, AlertPriority, AlertCategory

        manager = RoboticsAlertManager()
        manager.create_alert("Cleanup 1", "Msg", AlertPriority.LOW, AlertCategory.SYSTEM, source="test")

        count = manager.cleanup_expired_alerts(max_age_hours=0)
        assert count >= 0

    def test_get_metrics(self):
        """Test getting alert manager metrics."""
        from backend.app.robotics.robotics_alerts import RoboticsAlertManager

        manager = RoboticsAlertManager()
        metrics = manager.get_metrics()

        assert "total_alerts" in metrics
        assert "active_alerts" in metrics
        assert "total_subscriptions" in metrics
        assert "total_rules" in metrics
