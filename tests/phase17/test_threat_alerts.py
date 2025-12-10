"""
Tests for Threat Alerts module.

Phase 17: Global Threat Intelligence Engine
"""

import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch

import sys
sys.path.insert(0, '/home/ubuntu/repos/g3ti-rtcc-platform/backend')

from app.threat_intel.threat_alerts import (
    ThreatAlertManager,
    AlertPriority,
    AlertStatus,
    AlertCategory,
    AlertDestination,
    EscalationLevel,
    ThreatAlert,
    AlertSubscription,
    RoutingRule,
    AlertAuditEntry,
)


class TestThreatAlertManager:
    """Test suite for ThreatAlertManager class."""

    @pytest.fixture
    def manager(self):
        """Create a ThreatAlertManager instance for testing."""
        return ThreatAlertManager()

    def test_manager_initialization(self, manager):
        """Test that manager initializes correctly."""
        assert manager is not None
        assert isinstance(manager.alerts, dict)
        assert isinstance(manager.subscriptions, dict)
        assert isinstance(manager.routing_rules, dict)

    def test_create_alert(self, manager):
        """Test creating a threat alert."""
        alert = manager.create_alert(
            title="High Priority Threat Detected",
            description="Dark web signal indicates potential weapons trafficking",
            priority=AlertPriority.P1_CRITICAL,
            category=AlertCategory.WEAPONS,
            source_module="dark_web_monitor",
            threat_score=85.0,
        )
        
        assert alert is not None
        assert alert.title == "High Priority Threat Detected"
        assert alert.priority == AlertPriority.P1_CRITICAL
        assert alert.category == AlertCategory.WEAPONS
        assert alert.alert_id in manager.alerts

    def test_create_alert_with_location(self, manager):
        """Test creating an alert with location data."""
        alert = manager.create_alert(
            title="Localized Threat",
            description="Threat detected in specific area",
            priority=AlertPriority.P2_HIGH,
            category=AlertCategory.TERRORISM,
            source_module="global_incidents",
            threat_score=75.0,
            latitude=40.7128,
            longitude=-74.0060,
            jurisdiction_codes=["US-NY"],
        )
        
        assert alert is not None
        assert alert.latitude == 40.7128
        assert alert.longitude == -74.0060
        assert "US-NY" in alert.jurisdiction_codes

    def test_create_alert_with_entity(self, manager):
        """Test creating an alert linked to an entity."""
        alert = manager.create_alert(
            title="Entity Alert",
            description="High-risk entity detected",
            priority=AlertPriority.P2_HIGH,
            category=AlertCategory.EXTREMISM,
            source_module="extremist_networks",
            threat_score=80.0,
            entity_id="entity-123",
            entity_type="person",
        )
        
        assert alert is not None
        assert alert.entity_id == "entity-123"
        assert alert.entity_type == "person"

    def test_get_alert(self, manager):
        """Test retrieving an alert by ID."""
        alert = manager.create_alert(
            title="Test Alert",
            description="Test",
            priority=AlertPriority.P3_MODERATE,
            category=AlertCategory.GENERAL,
            source_module="test",
            threat_score=50.0,
        )
        
        retrieved = manager.get_alert(alert.alert_id)
        assert retrieved is not None
        assert retrieved.alert_id == alert.alert_id

    def test_get_alerts(self, manager):
        """Test retrieving all alerts."""
        manager.create_alert(
            title="Alert 1",
            description="Test 1",
            priority=AlertPriority.P3_MODERATE,
            category=AlertCategory.CRIME,
            source_module="test",
            threat_score=50.0,
        )
        manager.create_alert(
            title="Alert 2",
            description="Test 2",
            priority=AlertPriority.P2_HIGH,
            category=AlertCategory.GANG,
            source_module="test",
            threat_score=70.0,
        )
        
        alerts = manager.get_alerts()
        assert len(alerts) >= 2

    def test_get_alerts_by_priority(self, manager):
        """Test retrieving alerts by priority."""
        manager.create_alert(
            title="Critical Alert",
            description="Test",
            priority=AlertPriority.P1_CRITICAL,
            category=AlertCategory.TERRORISM,
            source_module="test",
            threat_score=90.0,
        )
        
        alerts = manager.get_alerts(min_priority=AlertPriority.P1_CRITICAL)
        for alert in alerts:
            assert alert.priority == AlertPriority.P1_CRITICAL

    def test_get_alerts_by_category(self, manager):
        """Test retrieving alerts by category."""
        manager.create_alert(
            title="Cyber Alert",
            description="Test",
            priority=AlertPriority.P2_HIGH,
            category=AlertCategory.CYBER,
            source_module="test",
            threat_score=75.0,
        )
        
        alerts = manager.get_alerts(category=AlertCategory.CYBER)
        for alert in alerts:
            assert alert.category == AlertCategory.CYBER

    def test_get_alerts_by_status(self, manager):
        """Test retrieving alerts by status."""
        alerts = manager.get_alerts(status=AlertStatus.NEW)
        for alert in alerts:
            assert alert.status == AlertStatus.NEW

    def test_acknowledge_alert(self, manager):
        """Test acknowledging an alert."""
        alert = manager.create_alert(
            title="To Acknowledge",
            description="Test",
            priority=AlertPriority.P3_MODERATE,
            category=AlertCategory.GENERAL,
            source_module="test",
            threat_score=50.0,
        )
        
        result = manager.acknowledge_alert(
            alert_id=alert.alert_id,
            user_id="user-123",
            notes="Acknowledged for review",
        )
        
        assert result is True
        updated = manager.get_alert(alert.alert_id)
        assert updated.status == AlertStatus.ACKNOWLEDGED
        assert updated.acknowledged_by == "user-123"

    def test_escalate_alert(self, manager):
        """Test escalating an alert."""
        alert = manager.create_alert(
            title="To Escalate",
            description="Test",
            priority=AlertPriority.P3_MODERATE,
            category=AlertCategory.CRIME,
            source_module="test",
            threat_score=60.0,
        )
        
        result = manager.escalate_alert(
            alert_id=alert.alert_id,
            user_id="user-123",
            new_level=EscalationLevel.SUPERVISOR,
            reason="Requires supervisor attention",
        )
        
        assert result is True
        updated = manager.get_alert(alert.alert_id)
        assert updated.escalation_level == EscalationLevel.SUPERVISOR

    def test_resolve_alert(self, manager):
        """Test resolving an alert."""
        alert = manager.create_alert(
            title="To Resolve",
            description="Test",
            priority=AlertPriority.P4_LOW,
            category=AlertCategory.GENERAL,
            source_module="test",
            threat_score=30.0,
        )
        
        result = manager.resolve_alert(
            alert_id=alert.alert_id,
            user_id="user-123",
            resolution_notes="Issue resolved, no further action needed",
        )
        
        assert result is True
        updated = manager.get_alert(alert.alert_id)
        assert updated.status == AlertStatus.RESOLVED
        assert updated.resolved_by == "user-123"

    def test_get_alerts_by_destination(self, manager):
        """Test retrieving alerts by destination."""
        alert = manager.create_alert(
            title="Dashboard Alert",
            description="Test",
            priority=AlertPriority.P2_HIGH,
            category=AlertCategory.TERRORISM,
            source_module="test",
            threat_score=80.0,
            destinations=[AlertDestination.RTCC_DASHBOARD, AlertDestination.COMMAND_CENTER],
        )
        
        alerts = manager.get_alerts_by_destination(AlertDestination.RTCC_DASHBOARD)
        assert isinstance(alerts, list)

    def test_create_routing_rule(self, manager):
        """Test creating a routing rule."""
        rule = manager.create_routing_rule(
            name="Critical to Command",
            categories=[AlertCategory.TERRORISM, AlertCategory.WEAPONS],
            min_priority=AlertPriority.P1_CRITICAL,
            destinations=[AlertDestination.COMMAND_CENTER, AlertDestination.DISPATCH],
        )
        
        assert rule is not None
        assert rule.name == "Critical to Command"
        assert AlertDestination.COMMAND_CENTER in rule.destinations
        assert rule.rule_id in manager.routing_rules

    def test_create_routing_rule_with_jurisdiction(self, manager):
        """Test creating a routing rule with jurisdiction filter."""
        rule = manager.create_routing_rule(
            name="NYC Alerts",
            categories=[AlertCategory.CRIME, AlertCategory.GANG],
            min_priority=AlertPriority.P3_MODERATE,
            destinations=[AlertDestination.RTCC_DASHBOARD],
            jurisdiction_codes=["US-NY"],
        )
        
        assert rule is not None
        assert "US-NY" in rule.jurisdiction_codes

    def test_get_routing_rules(self, manager):
        """Test retrieving routing rules."""
        manager.create_routing_rule(
            name="Rule 1",
            categories=[AlertCategory.GENERAL],
            min_priority=AlertPriority.P4_LOW,
            destinations=[AlertDestination.RTCC_DASHBOARD],
        )
        
        rules = manager.get_routing_rules()
        assert isinstance(rules, list)

    def test_create_subscription(self, manager):
        """Test creating an alert subscription."""
        subscription = manager.create_subscription(
            subscriber_id="user-456",
            subscriber_type="analyst",
            categories=[AlertCategory.TERRORISM, AlertCategory.CYBER],
            min_priority=AlertPriority.P2_HIGH,
            destinations=[AlertDestination.MOBILE_UNITS],
        )
        
        assert subscription is not None
        assert subscription.subscriber_id == "user-456"
        assert AlertCategory.TERRORISM in subscription.categories
        assert subscription.subscription_id in manager.subscriptions

    def test_create_subscription_with_webhook(self, manager):
        """Test creating a subscription with webhook."""
        subscription = manager.create_subscription(
            subscriber_id="system-123",
            subscriber_type="integration",
            categories=[AlertCategory.GENERAL],
            min_priority=AlertPriority.P3_MODERATE,
            destinations=[AlertDestination.EXTERNAL_AGENCY],
            webhook_url="https://example.com/webhook",
        )
        
        assert subscription is not None
        assert subscription.webhook_url == "https://example.com/webhook"

    def test_get_subscriptions(self, manager):
        """Test retrieving subscriptions for a subscriber."""
        manager.create_subscription(
            subscriber_id="user-789",
            subscriber_type="officer",
            categories=[AlertCategory.CRIME],
            min_priority=AlertPriority.P3_MODERATE,
            destinations=[AlertDestination.MOBILE_UNITS],
        )
        
        subscriptions = manager.get_subscriptions("user-789")
        assert isinstance(subscriptions, list)

    def test_route_alert(self, manager):
        """Test routing an alert based on rules."""
        manager.create_routing_rule(
            name="Auto Route",
            categories=[AlertCategory.TERRORISM],
            min_priority=AlertPriority.P1_CRITICAL,
            destinations=[AlertDestination.COMMAND_CENTER],
        )
        
        alert = manager.create_alert(
            title="Terrorism Alert",
            description="Test",
            priority=AlertPriority.P1_CRITICAL,
            category=AlertCategory.TERRORISM,
            source_module="test",
            threat_score=95.0,
        )
        
        routed = manager.route_alert(alert.alert_id)
        assert isinstance(routed, list) or routed is None

    def test_get_alert_audit_log(self, manager):
        """Test retrieving audit log for an alert."""
        alert = manager.create_alert(
            title="Audited Alert",
            description="Test",
            priority=AlertPriority.P3_MODERATE,
            category=AlertCategory.GENERAL,
            source_module="test",
            threat_score=50.0,
        )
        
        manager.acknowledge_alert(alert.alert_id, "user-123", "Test ack")
        
        audit_log = manager.get_alert_audit_log(alert.alert_id)
        assert isinstance(audit_log, list)

    def test_get_statistics(self, manager):
        """Test retrieving alert statistics."""
        manager.create_alert(
            title="Stat Alert 1",
            description="Test",
            priority=AlertPriority.P1_CRITICAL,
            category=AlertCategory.TERRORISM,
            source_module="test",
            threat_score=90.0,
        )
        manager.create_alert(
            title="Stat Alert 2",
            description="Test",
            priority=AlertPriority.P3_MODERATE,
            category=AlertCategory.CRIME,
            source_module="test",
            threat_score=50.0,
        )
        
        stats = manager.get_statistics()
        assert isinstance(stats, dict)
        assert "total_alerts" in stats
        assert "by_priority" in stats
        assert "by_category" in stats
        assert "by_status" in stats

    def test_get_metrics(self, manager):
        """Test retrieving metrics."""
        metrics = manager.get_metrics()
        
        assert isinstance(metrics, dict)
        assert "total_alerts" in metrics
        assert "total_subscriptions" in metrics
        assert "total_routing_rules" in metrics


class TestThreatAlert:
    """Test suite for ThreatAlert dataclass."""

    def test_alert_creation(self):
        """Test creating a ThreatAlert."""
        alert = ThreatAlert(
            alert_id="alert-123",
            title="Test Alert",
            description="Test description",
            priority=AlertPriority.P2_HIGH,
            status=AlertStatus.NEW,
            category=AlertCategory.TERRORISM,
            source_module="dark_web_monitor",
            threat_score=80.0,
            entity_id=None,
            entity_type=None,
            latitude=None,
            longitude=None,
            jurisdiction_codes=[],
            recommended_actions=[],
            destinations=[AlertDestination.RTCC_DASHBOARD],
            routed_to=[],
            escalation_level=EscalationLevel.STANDARD,
            assigned_to=None,
            acknowledged_by=None,
            resolved_by=None,
            tags=[],
            related_alerts=[],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            metadata={},
        )
        
        assert alert.alert_id == "alert-123"
        assert alert.priority == AlertPriority.P2_HIGH
        assert alert.status == AlertStatus.NEW


class TestAlertSubscription:
    """Test suite for AlertSubscription dataclass."""

    def test_subscription_creation(self):
        """Test creating an AlertSubscription."""
        subscription = AlertSubscription(
            subscription_id="sub-123",
            subscriber_id="user-123",
            subscriber_type="analyst",
            categories=[AlertCategory.TERRORISM, AlertCategory.WEAPONS],
            min_priority=AlertPriority.P2_HIGH,
            jurisdiction_codes=["US-NY"],
            destinations=[AlertDestination.MOBILE_UNITS],
            webhook_url=None,
            websocket_channel=None,
            email=None,
            sms=None,
            enabled=True,
            created_at=datetime.utcnow(),
            metadata={},
        )
        
        assert subscription.subscription_id == "sub-123"
        assert subscription.subscriber_id == "user-123"
        assert len(subscription.categories) == 2


class TestRoutingRule:
    """Test suite for RoutingRule dataclass."""

    def test_routing_rule_creation(self):
        """Test creating a RoutingRule."""
        rule = RoutingRule(
            rule_id="rule-123",
            name="Test Rule",
            categories=[AlertCategory.TERRORISM],
            min_priority=AlertPriority.P1_CRITICAL,
            jurisdiction_codes=[],
            destinations=[AlertDestination.COMMAND_CENTER],
            escalation_threshold_minutes=30,
            auto_escalate=True,
            enabled=True,
            created_at=datetime.utcnow(),
            metadata={},
        )
        
        assert rule.rule_id == "rule-123"
        assert rule.name == "Test Rule"
        assert rule.auto_escalate is True


class TestAlertAuditEntry:
    """Test suite for AlertAuditEntry dataclass."""

    def test_audit_entry_creation(self):
        """Test creating an AlertAuditEntry."""
        entry = AlertAuditEntry(
            entry_id="audit-123",
            alert_id="alert-123",
            action="acknowledged",
            actor_id="user-123",
            previous_status=AlertStatus.NEW,
            new_status=AlertStatus.ACKNOWLEDGED,
            notes="Acknowledged for review",
            timestamp=datetime.utcnow(),
        )
        
        assert entry.entry_id == "audit-123"
        assert entry.action == "acknowledged"
        assert entry.previous_status == AlertStatus.NEW
        assert entry.new_status == AlertStatus.ACKNOWLEDGED
