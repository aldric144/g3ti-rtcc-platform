"""
Tests for National Security Alerts Manager

Tests cover:
- Alert creation
- Alert acknowledgment
- Alert escalation
- Alert resolution
- Alert routing
- Subscriptions
- Routing rules
- Audit logging
- Statistics
- Metrics collection
"""

import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch

import sys
sys.path.insert(0, '/home/ubuntu/repos/g3ti-rtcc-platform/backend')

from app.national_security.national_security_alerts import (
    NationalSecurityAlertManager,
    SecurityAlert,
    AlertSubscription,
    RoutingRule,
    AlertAuditEntry,
    AlertPriority,
    AlertCategory,
    AlertDestination,
    AlertStatus,
    EscalationLevel,
)


class TestNationalSecurityAlertManager:
    """Test suite for NationalSecurityAlertManager."""

    @pytest.fixture
    def manager(self):
        """Create a NationalSecurityAlertManager instance."""
        return NationalSecurityAlertManager()

    def test_manager_initialization(self, manager):
        """Test manager initializes with empty collections and default rules."""
        assert manager.alerts == {}
        assert manager.subscriptions == {}
        assert len(manager.routing_rules) > 0
        assert manager.audit_log == []

    def test_create_alert(self, manager):
        """Test alert creation."""
        alert = manager.create_alert(
            title="Test Security Alert",
            description="A test security alert for unit testing",
            priority=AlertPriority.PRIORITY,
            category=AlertCategory.CYBER_THREAT,
            source="test_source",
            risk_score=65.0,
            affected_entities=["System A", "System B"],
            recommended_actions=["Isolate affected systems", "Run malware scan"],
        )

        assert alert is not None
        assert alert.alert_id is not None
        assert alert.title == "Test Security Alert"
        assert alert.priority == AlertPriority.PRIORITY
        assert alert.category == AlertCategory.CYBER_THREAT
        assert alert.status == AlertStatus.OPEN
        assert len(alert.destinations) > 0

    def test_get_alert(self, manager):
        """Test retrieving a specific alert."""
        alert = manager.create_alert(
            title="Retrieve Test Alert",
            description="Alert for retrieval testing",
            priority=AlertPriority.IMMEDIATE,
            category=AlertCategory.INSIDER_THREAT,
            source="test",
            risk_score=70.0,
            affected_entities=["Employee X"],
            recommended_actions=["Review access logs"],
        )

        retrieved = manager.get_alert(alert.alert_id)
        assert retrieved is not None
        assert retrieved.title == "Retrieve Test Alert"

        non_existent = manager.get_alert("non-existent-id")
        assert non_existent is None

    def test_get_alerts_filtering(self, manager):
        """Test alert retrieval with filtering."""
        manager.create_alert(
            title="Critical Alert",
            description="Critical priority alert",
            priority=AlertPriority.CRITICAL,
            category=AlertCategory.TERRORISM,
            source="test",
            risk_score=95.0,
            affected_entities=["Target A"],
            recommended_actions=["Immediate response"],
        )

        manager.create_alert(
            title="Routine Alert",
            description="Routine priority alert",
            priority=AlertPriority.ROUTINE,
            category=AlertCategory.FINANCIAL_CRIME,
            source="test",
            risk_score=35.0,
            affected_entities=["Account B"],
            recommended_actions=["Monitor"],
        )

        critical_alerts = manager.get_alerts(priority=AlertPriority.CRITICAL)
        assert len(critical_alerts) >= 1
        assert all(a.priority == AlertPriority.CRITICAL for a in critical_alerts)

        terrorism_alerts = manager.get_alerts(category=AlertCategory.TERRORISM)
        assert len(terrorism_alerts) >= 1

    def test_acknowledge_alert(self, manager):
        """Test alert acknowledgment."""
        alert = manager.create_alert(
            title="Ack Test Alert",
            description="Alert for acknowledgment testing",
            priority=AlertPriority.PRIORITY,
            category=AlertCategory.CYBER_THREAT,
            source="test",
            risk_score=60.0,
            affected_entities=["System X"],
            recommended_actions=["Review"],
        )

        result = manager.acknowledge_alert(
            alert_id=alert.alert_id,
            acknowledged_by="security_analyst",
            notes="Acknowledged and reviewing",
        )

        assert result is True

        updated = manager.alerts[alert.alert_id]
        assert updated.status == AlertStatus.ACKNOWLEDGED
        assert updated.acknowledged_by == "security_analyst"

    def test_escalate_alert(self, manager):
        """Test alert escalation."""
        alert = manager.create_alert(
            title="Escalate Test Alert",
            description="Alert for escalation testing",
            priority=AlertPriority.PRIORITY,
            category=AlertCategory.GEOPOLITICAL,
            source="test",
            risk_score=70.0,
            affected_entities=["Region A"],
            recommended_actions=["Escalate to leadership"],
        )

        result = manager.escalate_alert(
            alert_id=alert.alert_id,
            escalated_by="analyst",
            reason="Requires executive attention",
            new_priority=AlertPriority.CRITICAL,
        )

        assert result is True

        updated = manager.alerts[alert.alert_id]
        assert updated.status == AlertStatus.ESCALATED
        assert updated.priority == AlertPriority.CRITICAL

    def test_resolve_alert(self, manager):
        """Test alert resolution."""
        alert = manager.create_alert(
            title="Resolve Test Alert",
            description="Alert for resolution testing",
            priority=AlertPriority.IMMEDIATE,
            category=AlertCategory.INSIDER_THREAT,
            source="test",
            risk_score=65.0,
            affected_entities=["Employee Y"],
            recommended_actions=["Investigate"],
        )

        manager.acknowledge_alert(
            alert_id=alert.alert_id,
            acknowledged_by="analyst",
            notes="Investigating",
        )

        result = manager.resolve_alert(
            alert_id=alert.alert_id,
            resolved_by="senior_analyst",
            resolution="False positive - authorized activity confirmed",
        )

        assert result is True

        updated = manager.alerts[alert.alert_id]
        assert updated.status == AlertStatus.RESOLVED
        assert updated.resolved_by == "senior_analyst"

    def test_close_alert(self, manager):
        """Test alert closure."""
        alert = manager.create_alert(
            title="Close Test Alert",
            description="Alert for closure testing",
            priority=AlertPriority.ROUTINE,
            category=AlertCategory.FINANCIAL_CRIME,
            source="test",
            risk_score=40.0,
            affected_entities=["Account Z"],
            recommended_actions=["Monitor"],
        )

        manager.acknowledge_alert(
            alert_id=alert.alert_id,
            acknowledged_by="analyst",
            notes="Reviewing",
        )

        manager.resolve_alert(
            alert_id=alert.alert_id,
            resolved_by="analyst",
            resolution="Issue addressed",
        )

        result = manager.close_alert(
            alert_id=alert.alert_id,
            closed_by="supervisor",
            final_notes="Case closed after review",
        )

        assert result is True

        updated = manager.alerts[alert.alert_id]
        assert updated.status == AlertStatus.CLOSED

    def test_add_action(self, manager):
        """Test adding action to alert."""
        alert = manager.create_alert(
            title="Action Test Alert",
            description="Alert for action testing",
            priority=AlertPriority.PRIORITY,
            category=AlertCategory.CYBER_THREAT,
            source="test",
            risk_score=55.0,
            affected_entities=["System A"],
            recommended_actions=["Initial action"],
        )

        result = manager.add_action(
            alert_id=alert.alert_id,
            action_type="investigation",
            description="Started forensic analysis",
            performed_by="forensic_analyst",
        )

        assert result is True

        updated = manager.alerts[alert.alert_id]
        assert len(updated.actions_taken) >= 1

    def test_create_subscription(self, manager):
        """Test subscription creation."""
        subscription = manager.create_subscription(
            subscriber_id="user-001",
            subscriber_name="Security Analyst",
            categories=[AlertCategory.CYBER_THREAT, AlertCategory.INSIDER_THREAT],
            min_priority=AlertPriority.PRIORITY,
            destinations=[AlertDestination.RTCC_DASHBOARD],
            notification_methods=["email", "sms"],
        )

        assert subscription is not None
        assert subscription.subscription_id is not None
        assert subscription.subscriber_id == "user-001"
        assert AlertCategory.CYBER_THREAT in subscription.categories

    def test_get_subscriptions_filtering(self, manager):
        """Test subscription retrieval with filtering."""
        manager.create_subscription(
            subscriber_id="user-002",
            subscriber_name="Cyber Analyst",
            categories=[AlertCategory.CYBER_THREAT],
            min_priority=AlertPriority.IMMEDIATE,
            destinations=[AlertDestination.CYBER_SECURITY_TEAM],
            notification_methods=["email"],
        )

        subscriptions = manager.get_subscriptions(
            category=AlertCategory.CYBER_THREAT
        )
        assert len(subscriptions) >= 1

    def test_create_routing_rule(self, manager):
        """Test routing rule creation."""
        rule = manager.create_routing_rule(
            name="Custom Routing Rule",
            description="Custom rule for testing",
            conditions={
                "category": AlertCategory.TERRORISM.value,
                "min_priority": AlertPriority.IMMEDIATE.value,
            },
            destinations=[
                AlertDestination.CHIEF,
                AlertDestination.HOMELAND_SECURITY_LIAISON,
                AlertDestination.FBI_LIAISON,
            ],
            escalation_level=EscalationLevel.EXECUTIVE,
            is_active=True,
        )

        assert rule is not None
        assert rule.rule_id is not None
        assert rule.name == "Custom Routing Rule"
        assert AlertDestination.CHIEF in rule.destinations

    def test_get_routing_rules(self, manager):
        """Test routing rule retrieval."""
        rules = manager.get_routing_rules()
        assert len(rules) > 0

        active_rules = manager.get_routing_rules(active_only=True)
        assert all(r.is_active for r in active_rules)

    def test_get_audit_log(self, manager):
        """Test audit log retrieval."""
        alert = manager.create_alert(
            title="Audit Test Alert",
            description="Alert for audit testing",
            priority=AlertPriority.PRIORITY,
            category=AlertCategory.CYBER_THREAT,
            source="test",
            risk_score=50.0,
            affected_entities=["System B"],
            recommended_actions=["Review"],
        )

        manager.acknowledge_alert(
            alert_id=alert.alert_id,
            acknowledged_by="analyst",
            notes="Acknowledged",
        )

        audit_entries = manager.get_audit_log(alert_id=alert.alert_id)
        assert len(audit_entries) >= 2

    def test_get_alert_statistics(self, manager):
        """Test alert statistics generation."""
        manager.create_alert(
            title="Stats Alert 1",
            description="Alert for stats",
            priority=AlertPriority.CRITICAL,
            category=AlertCategory.TERRORISM,
            source="test",
            risk_score=90.0,
            affected_entities=["Target"],
            recommended_actions=["Respond"],
        )

        manager.create_alert(
            title="Stats Alert 2",
            description="Alert for stats",
            priority=AlertPriority.ROUTINE,
            category=AlertCategory.FINANCIAL_CRIME,
            source="test",
            risk_score=30.0,
            affected_entities=["Account"],
            recommended_actions=["Monitor"],
        )

        stats = manager.get_alert_statistics()

        assert stats is not None
        assert "total_alerts" in stats
        assert "by_status" in stats
        assert "by_priority" in stats
        assert "by_category" in stats
        assert stats["total_alerts"] >= 2

    def test_get_metrics(self, manager):
        """Test metrics collection."""
        manager.create_alert(
            title="Metrics Test Alert",
            description="Alert for metrics testing",
            priority=AlertPriority.PRIORITY,
            category=AlertCategory.CYBER_THREAT,
            source="test",
            risk_score=55.0,
            affected_entities=["System"],
            recommended_actions=["Review"],
        )

        metrics = manager.get_metrics()

        assert "total_alerts" in metrics
        assert "active_alerts" in metrics
        assert "acknowledged_alerts" in metrics
        assert "escalated_alerts" in metrics
        assert "resolved_alerts" in metrics
        assert "closed_alerts" in metrics
        assert "total_subscriptions" in metrics
        assert "total_routing_rules" in metrics
        assert "audit_entries_24h" in metrics

    def test_alert_destination_determination(self, manager):
        """Test automatic destination determination based on priority and category."""
        critical_terror_alert = manager.create_alert(
            title="Critical Terror Alert",
            description="Critical terrorism alert",
            priority=AlertPriority.CRITICAL,
            category=AlertCategory.TERRORISM,
            source="test",
            risk_score=95.0,
            affected_entities=["Target"],
            recommended_actions=["Immediate response"],
        )

        assert AlertDestination.CHIEF in critical_terror_alert.destinations
        assert AlertDestination.HOMELAND_SECURITY_LIAISON in critical_terror_alert.destinations

        routine_financial_alert = manager.create_alert(
            title="Routine Financial Alert",
            description="Routine financial alert",
            priority=AlertPriority.ROUTINE,
            category=AlertCategory.FINANCIAL_CRIME,
            source="test",
            risk_score=25.0,
            affected_entities=["Account"],
            recommended_actions=["Monitor"],
        )

        assert AlertDestination.FINANCIAL_CRIMES_UNIT in routine_financial_alert.destinations

    def test_escalation_level_calculation(self, manager):
        """Test escalation level calculation based on priority and risk score."""
        critical_alert = manager.create_alert(
            title="Critical Escalation Test",
            description="Critical alert for escalation testing",
            priority=AlertPriority.CRITICAL,
            category=AlertCategory.NATIONAL_STABILITY,
            source="test",
            risk_score=92.0,
            affected_entities=["Nation"],
            recommended_actions=["Executive briefing"],
        )

        assert critical_alert.escalation_level == EscalationLevel.EXECUTIVE

        routine_alert = manager.create_alert(
            title="Routine Escalation Test",
            description="Routine alert for escalation testing",
            priority=AlertPriority.ROUTINE,
            category=AlertCategory.FINANCIAL_CRIME,
            source="test",
            risk_score=30.0,
            affected_entities=["Account"],
            recommended_actions=["Monitor"],
        )

        assert routine_alert.escalation_level in [EscalationLevel.STANDARD, EscalationLevel.ELEVATED]


class TestSecurityAlertDataclass:
    """Test SecurityAlert dataclass."""

    def test_security_alert_creation(self):
        """Test SecurityAlert dataclass creation."""
        alert = SecurityAlert(
            alert_id="alert-123",
            title="Test Alert",
            description="Test description",
            priority=AlertPriority.CRITICAL,
            category=AlertCategory.CYBER_THREAT,
            status=AlertStatus.OPEN,
            source="test_source",
            risk_score=85.0,
            affected_entities=["Entity 1", "Entity 2"],
            recommended_actions=["Action 1", "Action 2"],
            destinations=[AlertDestination.CHIEF, AlertDestination.RTCC_DIRECTOR],
            escalation_level=EscalationLevel.EXECUTIVE,
            created_at="2025-12-10T00:00:00Z",
            updated_at="2025-12-10T00:00:00Z",
            acknowledged_by=None,
            acknowledged_at=None,
            resolved_by=None,
            resolved_at=None,
            resolution=None,
            actions_taken=[],
            metadata={},
        )

        assert alert.alert_id == "alert-123"
        assert alert.priority == AlertPriority.CRITICAL
        assert alert.status == AlertStatus.OPEN


class TestAlertSubscriptionDataclass:
    """Test AlertSubscription dataclass."""

    def test_subscription_creation(self):
        """Test AlertSubscription dataclass creation."""
        subscription = AlertSubscription(
            subscription_id="sub-123",
            subscriber_id="user-001",
            subscriber_name="Test User",
            categories=[AlertCategory.CYBER_THREAT, AlertCategory.INSIDER_THREAT],
            min_priority=AlertPriority.PRIORITY,
            destinations=[AlertDestination.RTCC_DASHBOARD],
            notification_methods=["email", "sms", "push"],
            is_active=True,
            created_at="2025-12-10T00:00:00Z",
            metadata={},
        )

        assert subscription.subscription_id == "sub-123"
        assert AlertCategory.CYBER_THREAT in subscription.categories


class TestRoutingRuleDataclass:
    """Test RoutingRule dataclass."""

    def test_routing_rule_creation(self):
        """Test RoutingRule dataclass creation."""
        rule = RoutingRule(
            rule_id="rule-123",
            name="Test Rule",
            description="Test description",
            conditions={"category": "terrorism", "min_priority": "critical"},
            destinations=[AlertDestination.CHIEF, AlertDestination.FBI_LIAISON],
            escalation_level=EscalationLevel.EXECUTIVE,
            is_active=True,
            priority_order=1,
            created_at="2025-12-10T00:00:00Z",
            metadata={},
        )

        assert rule.rule_id == "rule-123"
        assert rule.name == "Test Rule"
        assert AlertDestination.CHIEF in rule.destinations


class TestAlertAuditEntryDataclass:
    """Test AlertAuditEntry dataclass."""

    def test_audit_entry_creation(self):
        """Test AlertAuditEntry dataclass creation."""
        entry = AlertAuditEntry(
            entry_id="audit-123",
            alert_id="alert-456",
            action="acknowledged",
            performed_by="analyst",
            timestamp="2025-12-10T00:00:00Z",
            previous_state={"status": "open"},
            new_state={"status": "acknowledged"},
            notes="Acknowledged after review",
            metadata={},
        )

        assert entry.entry_id == "audit-123"
        assert entry.action == "acknowledged"
        assert entry.performed_by == "analyst"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
