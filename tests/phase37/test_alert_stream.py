"""
Phase 37: Unified Alert Stream Tests
Tests for the Unified Alert Stream functionality.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock

from backend.app.master_orchestration.alert_aggregator import (
    UnifiedAlertStream,
    AlertSeverity,
    AlertSource,
    UnifiedAlert,
    AlertFilter,
)


class TestUnifiedAlertStream:
    """Test suite for UnifiedAlertStream."""

    def setup_method(self):
        """Reset singleton for each test."""
        UnifiedAlertStream._instance = None
        self.alert_stream = UnifiedAlertStream()

    def test_singleton_pattern(self):
        """Test that UnifiedAlertStream follows singleton pattern."""
        stream1 = UnifiedAlertStream()
        stream2 = UnifiedAlertStream()
        assert stream1 is stream2

    def test_create_alert(self):
        """Test alert creation with all fields."""
        alert = self.alert_stream.create_alert(
            severity=AlertSeverity.HIGH,
            source=AlertSource.OFFICER_ASSIST,
            title="Officer Safety Alert",
            summary="High risk situation detected",
            full_details={"incident_type": "traffic_stop"},
            geolocation={"lat": 26.7753, "lng": -80.0589},
            constitutional_compliance_tag=True,
            moral_compass_tag="compliant",
            public_safety_audit_ref="audit-001",
            affected_areas=["Downtown"],
            affected_officers=["officer-001"],
            requires_action=True,
        )

        assert alert.alert_id is not None
        assert alert.severity == AlertSeverity.HIGH
        assert alert.source == AlertSource.OFFICER_ASSIST
        assert alert.title == "Officer Safety Alert"
        assert alert.requires_action is True
        assert alert.active is True

    def test_alert_to_dict(self):
        """Test alert serialization to dictionary."""
        alert = self.alert_stream.create_alert(
            severity=AlertSeverity.MEDIUM,
            source=AlertSource.TACTICAL_ANALYTICS,
            title="Pattern Detected",
        )

        alert_dict = alert.to_dict()

        assert "alert_id" in alert_dict
        assert alert_dict["severity"] == "medium"
        assert alert_dict["source"] == "tactical_analytics"
        assert alert_dict["title"] == "Pattern Detected"

    def test_get_active_alerts(self):
        """Test retrieving active alerts."""
        alert = self.alert_stream.create_alert(
            severity=AlertSeverity.LOW,
            source=AlertSource.SYSTEM,
            title="Test Alert",
        )

        active = self.alert_stream.get_active_alerts()
        assert any(a.alert_id == alert.alert_id for a in active)

    def test_get_alerts_by_severity(self):
        """Test filtering alerts by severity."""
        critical_alert = self.alert_stream.create_alert(
            severity=AlertSeverity.CRITICAL,
            source=AlertSource.EMERGENCY_MGMT,
            title="Critical Alert",
        )

        critical_alerts = self.alert_stream.get_alerts_by_severity(
            AlertSeverity.CRITICAL
        )
        assert all(a.severity == AlertSeverity.CRITICAL for a in critical_alerts)

    def test_get_alerts_by_source(self):
        """Test filtering alerts by source."""
        alert = self.alert_stream.create_alert(
            severity=AlertSeverity.MEDIUM,
            source=AlertSource.DRONE_OPS,
            title="Drone Alert",
        )

        drone_alerts = self.alert_stream.get_alerts_by_source(AlertSource.DRONE_OPS)
        assert all(a.source == AlertSource.DRONE_OPS for a in drone_alerts)

    def test_get_critical_alerts(self):
        """Test retrieving critical alerts."""
        alert = self.alert_stream.create_alert(
            severity=AlertSeverity.CRITICAL,
            source=AlertSource.OFFICER_ASSIST,
            title="Critical Officer Alert",
        )

        critical = self.alert_stream.get_critical_alerts()
        assert all(a.severity == AlertSeverity.CRITICAL for a in critical)

    def test_get_alerts_requiring_action(self):
        """Test retrieving alerts requiring action."""
        alert = self.alert_stream.create_alert(
            severity=AlertSeverity.HIGH,
            source=AlertSource.MORAL_COMPASS,
            title="Action Required",
            requires_action=True,
        )

        action_alerts = self.alert_stream.get_alerts_requiring_action()
        assert all(a.requires_action for a in action_alerts)

    def test_take_action(self):
        """Test taking action on an alert."""
        alert = self.alert_stream.create_alert(
            severity=AlertSeverity.HIGH,
            source=AlertSource.SYSTEM,
            title="Action Test",
            requires_action=True,
        )

        updated = self.alert_stream.take_action(
            alert.alert_id,
            action_by="operator-001",
            action_notes="Acknowledged and dispatched unit",
        )

        assert updated is not None
        assert updated.action_taken is True
        assert updated.action_by == "operator-001"
        assert updated.action_at is not None

    def test_resolve_alert(self):
        """Test resolving an alert."""
        alert = self.alert_stream.create_alert(
            severity=AlertSeverity.MEDIUM,
            source=AlertSource.INVESTIGATIONS,
            title="Resolution Test",
        )

        result = self.alert_stream.resolve_alert(
            alert.alert_id,
            resolved_by="supervisor-001",
            notes="Situation resolved",
        )

        assert result is True

        resolved = self.alert_stream.get_alert(alert.alert_id)
        assert resolved.active is False

    def test_escalate_alert(self):
        """Test escalating an alert."""
        alert = self.alert_stream.create_alert(
            severity=AlertSeverity.MEDIUM,
            source=AlertSource.HUMAN_STABILITY,
            title="Escalation Test",
        )

        escalated = self.alert_stream.escalate_alert(
            alert.alert_id,
            escalation_notes="Requires supervisor attention",
        )

        assert escalated is not None
        assert escalated.escalated is True
        assert escalated.escalation_level > 0

    def test_link_alerts(self):
        """Test linking related alerts."""
        alert1 = self.alert_stream.create_alert(
            severity=AlertSeverity.HIGH,
            source=AlertSource.TACTICAL_ANALYTICS,
            title="Primary Alert",
        )

        alert2 = self.alert_stream.create_alert(
            severity=AlertSeverity.MEDIUM,
            source=AlertSource.PREDICTIVE_INTEL,
            title="Related Alert",
        )

        result = self.alert_stream.link_alerts(alert1.alert_id, alert2.alert_id)
        assert result is True

        updated1 = self.alert_stream.get_alert(alert1.alert_id)
        assert alert2.alert_id in updated1.related_alerts

    def test_get_alerts_by_area(self):
        """Test filtering alerts by affected area."""
        alert = self.alert_stream.create_alert(
            severity=AlertSeverity.MEDIUM,
            source=AlertSource.CITY_AUTONOMY,
            title="Area Alert",
            affected_areas=["Downtown Riviera Beach"],
        )

        area_alerts = self.alert_stream.get_alerts_by_area("Downtown Riviera Beach")
        assert any(a.alert_id == alert.alert_id for a in area_alerts)

    def test_get_alerts_for_officer(self):
        """Test filtering alerts by affected officer."""
        alert = self.alert_stream.create_alert(
            severity=AlertSeverity.HIGH,
            source=AlertSource.OFFICER_ASSIST,
            title="Officer Alert",
            affected_officers=["officer-123"],
        )

        officer_alerts = self.alert_stream.get_alerts_for_officer("officer-123")
        assert any(a.alert_id == alert.alert_id for a in officer_alerts)

    def test_get_unified_feed(self):
        """Test unified feed retrieval."""
        for i in range(5):
            self.alert_stream.create_alert(
                severity=AlertSeverity.MEDIUM,
                source=AlertSource.SYSTEM,
                title=f"Feed Alert {i}",
            )

        feed = self.alert_stream.get_unified_feed(limit=10)
        assert len(feed) <= 10
        assert all("alert_id" in item for item in feed)

    def test_get_statistics(self):
        """Test statistics retrieval."""
        stats = self.alert_stream.get_statistics()

        assert "total_alerts" in stats
        assert "active_alerts" in stats
        assert "alerts_by_severity" in stats
        assert "alerts_by_source" in stats

    def test_alert_severity_enum(self):
        """Test all alert severities are defined."""
        assert len(AlertSeverity) == 5
        assert AlertSeverity.CRITICAL.value == "critical"
        assert AlertSeverity.HIGH.value == "high"
        assert AlertSeverity.MEDIUM.value == "medium"
        assert AlertSeverity.LOW.value == "low"
        assert AlertSeverity.INFO.value == "info"

    def test_alert_source_enum(self):
        """Test all alert sources are defined."""
        assert len(AlertSource) >= 24
        assert AlertSource.OFFICER_ASSIST.value == "officer_assist"
        assert AlertSource.MORAL_COMPASS.value == "moral_compass"
        assert AlertSource.HUMAN_STABILITY.value == "human_stability"

    def test_alert_filter(self):
        """Test alert filtering with AlertFilter."""
        filter_obj = AlertFilter(
            severities=[AlertSeverity.CRITICAL, AlertSeverity.HIGH],
            sources=[AlertSource.OFFICER_ASSIST],
            active_only=True,
            requires_action_only=True,
        )

        assert AlertSeverity.CRITICAL in filter_obj.severities
        assert filter_obj.active_only is True
