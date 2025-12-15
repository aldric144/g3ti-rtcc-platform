"""
Phase 37: Orchestration Integration Tests
End-to-end integration tests for the Master Orchestration system.
"""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

from backend.app.master_orchestration.event_bus import (
    MasterEventBus,
    EventType,
    EventPriority,
    EventSource,
)
from backend.app.master_orchestration.alert_aggregator import (
    UnifiedAlertStream,
    AlertSeverity,
    AlertSource,
)
from backend.app.master_orchestration.module_heartbeat import (
    ModuleHeartbeatChecker,
    ModuleStatus,
)
from backend.app.master_orchestration.state_synchronizer import (
    CrossModuleStateSynchronizer,
    StateChangeType,
    SyncTarget,
)
from backend.app.master_orchestration.permissions_manager import (
    GlobalPermissionsManager,
    PermissionAction,
)


class TestOrchestrationIntegration:
    """Integration tests for the Master Orchestration system."""

    def setup_method(self):
        """Reset all singletons for each test."""
        MasterEventBus._instance = None
        UnifiedAlertStream._instance = None
        ModuleHeartbeatChecker._instance = None
        CrossModuleStateSynchronizer._instance = None
        GlobalPermissionsManager._instance = None

        self.event_bus = MasterEventBus()
        self.alert_stream = UnifiedAlertStream()
        self.heartbeat_checker = ModuleHeartbeatChecker()
        self.state_sync = CrossModuleStateSynchronizer()
        self.permissions = GlobalPermissionsManager()

    def test_all_components_initialize(self):
        """Test that all orchestration components initialize properly."""
        assert self.event_bus is not None
        assert self.alert_stream is not None
        assert self.heartbeat_checker is not None
        assert self.state_sync is not None
        assert self.permissions is not None

    def test_event_to_alert_flow(self):
        """Test flow from event creation to alert generation."""
        event = self.event_bus.create_event(
            event_type=EventType.ALERT,
            source=EventSource.OFFICER_SAFETY,
            title="Officer Safety Event",
            summary="High risk situation",
            priority=EventPriority.CRITICAL,
        )
        self.event_bus.publish_sync(event)

        alert = self.alert_stream.create_alert(
            severity=AlertSeverity.CRITICAL,
            source=AlertSource.OFFICER_ASSIST,
            title="Officer Safety Alert",
            summary="High risk situation detected",
            requires_action=True,
        )

        assert event.event_id is not None
        assert alert.alert_id is not None
        assert alert.severity == AlertSeverity.CRITICAL

    def test_alert_triggers_state_sync(self):
        """Test that alert creation triggers state synchronization."""
        alert = self.alert_stream.create_alert(
            severity=AlertSeverity.HIGH,
            source=AlertSource.TACTICAL_ANALYTICS,
            title="Tactical Alert",
        )

        change = self.state_sync.create_change(
            change_type=StateChangeType.ALERT_UPDATE,
            source_module="alert_stream",
            data={"alert_id": alert.alert_id, "action": "created"},
            targets=[SyncTarget.ALERTS, SyncTarget.MASTER_DASHBOARD],
        )
        self.state_sync.publish_change_sync(change)

        assert change.propagated is True

    def test_module_health_affects_events(self):
        """Test that module health status generates events."""
        self.heartbeat_checker.register_module(
            module_id="integration-test-module",
            module_name="Integration Test Module",
        )

        self.heartbeat_checker.update_heartbeat(
            module_id="integration-test-module",
            response_time_ms=500.0,
            error_count=10,
            endpoints_healthy=2,
            endpoints_total=10,
        )

        health = self.heartbeat_checker.get_module_health("integration-test-module")

        if health.status in [ModuleStatus.DEGRADED, ModuleStatus.UNHEALTHY]:
            event = self.event_bus.create_event(
                event_type=EventType.MODULE_STATUS,
                source=EventSource.SYSTEM,
                title=f"Module {health.module_name} status: {health.status.value}",
                priority=EventPriority.HIGH,
            )
            self.event_bus.publish_sync(event)

            assert event.event_id is not None

    def test_permission_check_before_action(self):
        """Test permission check before performing actions."""
        self.permissions.assign_role("test-operator", "operator")

        can_view = self.permissions.check_permission(
            user_id="test-operator",
            module="real_time_ops",
            feature="incidents",
            action=PermissionAction.VIEW,
        )

        can_admin = self.permissions.check_permission(
            user_id="test-operator",
            module="admin",
            feature="system",
            action=PermissionAction.ADMIN,
        )

        assert can_view is True
        assert can_admin is False

    def test_cross_module_event_propagation(self):
        """Test event propagation across modules."""
        event = self.event_bus.create_event(
            event_type=EventType.TACTICAL_EVENT,
            source=EventSource.TACTICAL_ANALYTICS,
            title="Crime Pattern Detected",
            affected_modules=["real_time_ops", "investigations", "predictive_intel"],
        )
        self.event_bus.publish_sync(event)

        change = self.state_sync.create_change(
            change_type=StateChangeType.TACTICAL_HEATMAP_UPDATE,
            source_module="tactical_analytics",
            data={"event_id": event.event_id, "pattern_type": "burglary"},
            targets=[
                SyncTarget.TACTICAL_HEATMAPS,
                SyncTarget.MAPS,
                SyncTarget.PREDICTIVE_MODELS,
            ],
        )
        self.state_sync.publish_change_sync(change)

        assert len(change.targets) == 3
        assert change.propagated is True

    def test_alert_escalation_flow(self):
        """Test alert escalation workflow."""
        alert = self.alert_stream.create_alert(
            severity=AlertSeverity.MEDIUM,
            source=AlertSource.HUMAN_STABILITY,
            title="Crisis Situation",
            requires_action=True,
        )

        self.alert_stream.take_action(
            alert.alert_id,
            action_by="operator-001",
            action_notes="Initial response",
        )

        escalated = self.alert_stream.escalate_alert(
            alert.alert_id,
            escalation_notes="Requires supervisor attention",
        )

        assert escalated.escalated is True
        assert escalated.escalation_level > 0

    def test_full_incident_workflow(self):
        """Test complete incident workflow from detection to resolution."""
        incident_event = self.event_bus.create_event(
            event_type=EventType.ALERT,
            source=EventSource.REAL_TIME_OPS,
            title="Incident Detected",
            priority=EventPriority.HIGH,
            requires_acknowledgment=True,
        )
        self.event_bus.publish_sync(incident_event)

        incident_alert = self.alert_stream.create_alert(
            severity=AlertSeverity.HIGH,
            source=AlertSource.OFFICER_ASSIST,
            title="Incident Alert",
            requires_action=True,
        )

        map_update = self.state_sync.create_change(
            change_type=StateChangeType.MAP_UPDATE,
            source_module="real_time_ops",
            data={"incident_id": incident_event.event_id},
            targets=[SyncTarget.MAPS, SyncTarget.OPERATOR_HUD],
        )
        self.state_sync.publish_change_sync(map_update)

        self.event_bus.acknowledge_event(incident_event.event_id, "operator-001")
        self.alert_stream.take_action(incident_alert.alert_id, "operator-001")

        self.alert_stream.resolve_alert(
            incident_alert.alert_id,
            resolved_by="supervisor-001",
            notes="Incident resolved",
        )

        resolved_alert = self.alert_stream.get_alert(incident_alert.alert_id)
        acked_event = self.event_bus.get_event(incident_event.event_id)

        assert resolved_alert.active is False
        assert acked_event.acknowledged_by == "operator-001"

    def test_system_health_overview(self):
        """Test system-wide health overview."""
        heartbeat_result = self.heartbeat_checker.perform_heartbeat_check_sync()
        system_overview = self.heartbeat_checker.get_system_overview()

        assert heartbeat_result.modules_checked > 0
        assert "total_modules" in system_overview
        assert "overall_health" in system_overview

    def test_statistics_aggregation(self):
        """Test statistics aggregation across all components."""
        event_stats = self.event_bus.get_statistics()
        alert_stats = self.alert_stream.get_statistics()
        heartbeat_stats = self.heartbeat_checker.get_statistics()
        sync_stats = self.state_sync.get_statistics()
        perm_stats = self.permissions.get_statistics()

        assert "total_events" in event_stats
        assert "total_alerts" in alert_stats
        assert "total_modules" in heartbeat_stats
        assert "total_changes" in sync_stats
        assert "total_roles" in perm_stats

    def test_concurrent_operations(self):
        """Test concurrent operations don't cause conflicts."""
        for i in range(10):
            event = self.event_bus.create_event(
                event_type=EventType.SYSTEM_MESSAGE,
                source=EventSource.SYSTEM,
                title=f"Concurrent Event {i}",
            )
            self.event_bus.publish_sync(event)

            alert = self.alert_stream.create_alert(
                severity=AlertSeverity.LOW,
                source=AlertSource.SYSTEM,
                title=f"Concurrent Alert {i}",
            )

            change = self.state_sync.create_change(
                change_type=StateChangeType.MODULE_STATUS_UPDATE,
                source_module="test",
                data={"iteration": i},
            )
            self.state_sync.publish_change_sync(change)

        events = self.event_bus.get_recent_events(limit=20)
        alerts = self.alert_stream.get_active_alerts(limit=20)
        changes = self.state_sync.get_recent_changes(limit=20)

        assert len(events) >= 10
        assert len(alerts) >= 10
        assert len(changes) >= 10
