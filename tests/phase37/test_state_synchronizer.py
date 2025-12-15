"""
Phase 37: Cross-Module State Synchronizer Tests
Tests for the Cross-Module State Synchronizer functionality.
"""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

from backend.app.master_orchestration.state_synchronizer import (
    CrossModuleStateSynchronizer,
    StateChangeType,
    StateChange,
    SyncTarget,
)


class TestCrossModuleStateSynchronizer:
    """Test suite for CrossModuleStateSynchronizer."""

    def setup_method(self):
        """Reset singleton for each test."""
        CrossModuleStateSynchronizer._instance = None
        self.sync = CrossModuleStateSynchronizer()

    def test_singleton_pattern(self):
        """Test that CrossModuleStateSynchronizer follows singleton pattern."""
        sync1 = CrossModuleStateSynchronizer()
        sync2 = CrossModuleStateSynchronizer()
        assert sync1 is sync2

    def test_create_change(self):
        """Test state change creation."""
        change = self.sync.create_change(
            change_type=StateChangeType.MAP_UPDATE,
            source_module="real_time_ops",
            data={"incident_id": "inc-001", "location": {"lat": 26.77, "lng": -80.05}},
            targets=[SyncTarget.MAPS, SyncTarget.OPERATOR_HUD],
            priority=1,
            requires_acknowledgment=True,
        )

        assert change.change_id is not None
        assert change.change_type == StateChangeType.MAP_UPDATE
        assert change.source_module == "real_time_ops"
        assert SyncTarget.MAPS in change.targets

    def test_change_to_dict(self):
        """Test state change serialization."""
        change = self.sync.create_change(
            change_type=StateChangeType.ALERT_UPDATE,
            source_module="alert_stream",
            data={"alert_id": "alert-001"},
        )

        change_dict = change.to_dict()

        assert "change_id" in change_dict
        assert change_dict["change_type"] == "alert_update"
        assert change_dict["source_module"] == "alert_stream"

    @pytest.mark.asyncio
    async def test_publish_change(self):
        """Test async state change publishing."""
        change = self.sync.create_change(
            change_type=StateChangeType.OFFICER_STATUS_UPDATE,
            source_module="officer_safety",
            data={"officer_id": "off-001", "status": "responding"},
        )

        await self.sync.publish_change(change)

        retrieved = self.sync.get_change(change.change_id)
        assert retrieved is not None
        assert retrieved.propagated is True

    def test_publish_change_sync(self):
        """Test synchronous state change publishing."""
        change = self.sync.create_change(
            change_type=StateChangeType.DRONE_TELEMETRY_UPDATE,
            source_module="drone_ops",
            data={"drone_id": "drone-001", "position": {"lat": 26.77, "lng": -80.05}},
        )

        self.sync.publish_change_sync(change)

        retrieved = self.sync.get_change(change.change_id)
        assert retrieved is not None

    def test_subscribe_to_changes(self):
        """Test subscribing to state changes."""
        callback = MagicMock()

        subscription_id = self.sync.subscribe(
            subscriber_id="test-subscriber",
            targets=[SyncTarget.MAPS, SyncTarget.ALERTS],
            callback=callback,
        )

        assert subscription_id is not None

    @pytest.mark.asyncio
    async def test_subscribe_async(self):
        """Test async subscription to state changes."""
        async_callback = AsyncMock()

        subscription_id = self.sync.subscribe_async(
            subscriber_id="async-subscriber",
            targets=[SyncTarget.TACTICAL_HEATMAPS],
            callback=async_callback,
        )

        assert subscription_id is not None

    def test_get_recent_changes(self):
        """Test retrieving recent state changes."""
        for i in range(5):
            change = self.sync.create_change(
                change_type=StateChangeType.INCIDENT_UPDATE,
                source_module="incidents",
                data={"incident_id": f"inc-{i}"},
            )
            self.sync.publish_change_sync(change)

        changes = self.sync.get_recent_changes(limit=3)
        assert len(changes) <= 3

    def test_get_changes_by_target(self):
        """Test filtering changes by target."""
        change = self.sync.create_change(
            change_type=StateChangeType.INVESTIGATION_UPDATE,
            source_module="investigations",
            data={"case_id": "case-001"},
            targets=[SyncTarget.INVESTIGATIONS],
        )
        self.sync.publish_change_sync(change)

        changes = self.sync.get_changes_by_target(SyncTarget.INVESTIGATIONS)
        assert all(SyncTarget.INVESTIGATIONS in c.targets for c in changes)

    def test_acknowledge_change(self):
        """Test acknowledging a state change."""
        change = self.sync.create_change(
            change_type=StateChangeType.THREAT_UPDATE,
            source_module="threat_intel",
            data={"threat_id": "threat-001"},
            requires_acknowledgment=True,
        )
        self.sync.publish_change_sync(change)

        result = self.sync.acknowledge_change(change.change_id, "operator-001")
        assert result is True

        updated = self.sync.get_change(change.change_id)
        assert "operator-001" in updated.acknowledged_by

    def test_get_pending_acknowledgments(self):
        """Test retrieving changes pending acknowledgment."""
        change = self.sync.create_change(
            change_type=StateChangeType.COMPLIANCE_UPDATE,
            source_module="compliance",
            data={"audit_id": "audit-001"},
            requires_acknowledgment=True,
        )
        self.sync.publish_change_sync(change)

        pending = self.sync.get_pending_acknowledgments()
        assert any(c.change_id == change.change_id for c in pending)

    def test_get_sync_rules(self):
        """Test sync rules retrieval."""
        rules = self.sync.get_sync_rules()

        assert isinstance(rules, dict)
        assert len(rules) > 0

    def test_add_sync_rule(self):
        """Test adding a sync rule."""
        self.sync.add_sync_rule(
            change_type=StateChangeType.SENSOR_UPDATE,
            targets=[SyncTarget.SENSOR_DASHBOARD, SyncTarget.DIGITAL_TWIN_VIEW],
        )

        rules = self.sync.get_sync_rules()
        assert StateChangeType.SENSOR_UPDATE.value in rules

    def test_get_statistics(self):
        """Test statistics retrieval."""
        stats = self.sync.get_statistics()

        assert "total_changes" in stats
        assert "changes_by_type" in stats
        assert "changes_by_source" in stats

    def test_get_current_state_summary(self):
        """Test current state summary retrieval."""
        summary = self.sync.get_current_state_summary()

        assert "last_update" in summary
        assert "active_subscriptions" in summary

    def test_state_change_type_enum(self):
        """Test all state change types are defined."""
        assert len(StateChangeType) >= 20
        assert StateChangeType.MAP_UPDATE.value == "map_update"
        assert StateChangeType.ALERT_UPDATE.value == "alert_update"
        assert StateChangeType.INVESTIGATION_UPDATE.value == "investigation_update"

    def test_sync_target_enum(self):
        """Test all sync targets are defined."""
        assert len(SyncTarget) >= 22
        assert SyncTarget.MAPS.value == "maps"
        assert SyncTarget.ALERTS.value == "alerts"
        assert SyncTarget.MASTER_DASHBOARD.value == "master_dashboard"
        assert SyncTarget.ALL.value == "all"

    def test_automatic_target_resolution(self):
        """Test that sync rules automatically resolve targets."""
        change = self.sync.create_change(
            change_type=StateChangeType.MAP_UPDATE,
            source_module="real_time_ops",
            data={"update": "test"},
        )

        rules = self.sync.get_sync_rules()
        if StateChangeType.MAP_UPDATE.value in rules:
            expected_targets = rules[StateChangeType.MAP_UPDATE.value]
            assert len(expected_targets) > 0

    def test_propagation_tracking(self):
        """Test that propagation is tracked."""
        change = self.sync.create_change(
            change_type=StateChangeType.CITY_BRAIN_UPDATE,
            source_module="city_brain",
            data={"prediction": "test"},
        )

        assert change.propagated is False

        self.sync.publish_change_sync(change)

        updated = self.sync.get_change(change.change_id)
        assert updated.propagated is True
        assert updated.propagated_at is not None
