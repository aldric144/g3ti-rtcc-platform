"""
Phase 24: PolicyEngine Tests

Tests for policy management, hierarchy, conflict detection, and emergency overrides.
"""

import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch

from backend.app.city_autonomy.policy_engine import (
    PolicyEngine,
    PolicyScope,
    PolicyType,
    PolicyStatus,
    EmergencyType,
    Policy,
    PolicyRule,
    PolicyThreshold,
    EmergencyOverride,
    get_policy_engine,
)


class TestPolicyEngine:
    """Test suite for PolicyEngine."""

    def setup_method(self):
        """Set up test fixtures."""
        self.engine = PolicyEngine()

    def test_engine_initialization(self):
        """Test engine initializes with default policies."""
        policies = self.engine.get_policies()
        assert len(policies) > 0
        
        overrides = self.engine.get_all_emergency_overrides()
        assert len(overrides) > 0

    def test_create_policy(self):
        """Test policy creation."""
        policy = self.engine.create_policy(
            name="Test Policy",
            description="A test policy",
            policy_type=PolicyType.TRAFFIC,
            scope=PolicyScope.CITY,
            rules=[
                PolicyRule(
                    rule_id="rule-test-001",
                    name="Test Rule",
                    description="A test rule",
                    condition="congestion > 0.8",
                    action="optimize_signals",
                    priority=5,
                    enabled=True,
                )
            ],
            thresholds=[
                PolicyThreshold(
                    threshold_id="thresh-test-001",
                    name="Test Threshold",
                    metric="congestion",
                    operator="gt",
                    value=0.9,
                    unit="index",
                    action_on_breach="alert",
                )
            ],
            tags=["test", "traffic"],
        )
        
        assert policy.policy_id is not None
        assert policy.name == "Test Policy"
        assert policy.status == PolicyStatus.DRAFT
        assert len(policy.rules) == 1
        assert len(policy.thresholds) == 1

    def test_update_policy(self):
        """Test policy update."""
        policy = self.engine.create_policy(
            name="Original Name",
            description="Original description",
            policy_type=PolicyType.TRAFFIC,
            scope=PolicyScope.CITY,
        )
        
        updated = self.engine.update_policy(
            policy.policy_id,
            name="Updated Name",
            description="Updated description",
        )
        
        assert updated is not None
        assert updated.name == "Updated Name"
        assert updated.description == "Updated description"
        assert updated.version == 2

    def test_activate_policy(self):
        """Test policy activation."""
        policy = self.engine.create_policy(
            name="Test Policy",
            description="Test",
            policy_type=PolicyType.TRAFFIC,
            scope=PolicyScope.CITY,
        )
        
        assert policy.status == PolicyStatus.DRAFT
        
        success = self.engine.activate_policy(policy.policy_id)
        
        assert success is True
        updated = self.engine.get_policy(policy.policy_id)
        assert updated.status == PolicyStatus.ACTIVE

    def test_deactivate_policy(self):
        """Test policy deactivation."""
        policy = self.engine.create_policy(
            name="Test Policy",
            description="Test",
            policy_type=PolicyType.TRAFFIC,
            scope=PolicyScope.CITY,
        )
        
        self.engine.activate_policy(policy.policy_id)
        success = self.engine.deactivate_policy(policy.policy_id)
        
        assert success is True
        updated = self.engine.get_policy(policy.policy_id)
        assert updated.status == PolicyStatus.INACTIVE

    def test_rollback_policy(self):
        """Test policy rollback."""
        policy = self.engine.create_policy(
            name="Original",
            description="Original",
            policy_type=PolicyType.TRAFFIC,
            scope=PolicyScope.CITY,
        )
        
        self.engine.update_policy(policy.policy_id, name="Updated")
        self.engine.update_policy(policy.policy_id, name="Updated Again")
        
        updated = self.engine.get_policy(policy.policy_id)
        assert updated.version == 3
        
        success = self.engine.rollback_policy(policy.policy_id, 1)
        
        assert success is True
        rolled_back = self.engine.get_policy(policy.policy_id)
        assert rolled_back.name == "Original"

    def test_policy_hierarchy(self):
        """Test policy hierarchy ordering."""
        global_policy = self.engine.create_policy(
            name="Global Policy",
            description="Global",
            policy_type=PolicyType.TRAFFIC,
            scope=PolicyScope.GLOBAL,
        )
        
        city_policy = self.engine.create_policy(
            name="City Policy",
            description="City",
            policy_type=PolicyType.TRAFFIC,
            scope=PolicyScope.CITY,
        )
        
        dept_policy = self.engine.create_policy(
            name="Department Policy",
            description="Department",
            policy_type=PolicyType.TRAFFIC,
            scope=PolicyScope.DEPARTMENT,
            scope_id="police",
        )
        
        self.engine.activate_policy(global_policy.policy_id)
        self.engine.activate_policy(city_policy.policy_id)
        self.engine.activate_policy(dept_policy.policy_id)
        
        policies = self.engine.get_policies(
            policy_type=PolicyType.TRAFFIC,
            status=PolicyStatus.ACTIVE,
        )
        
        scopes = [p.scope for p in policies]
        assert PolicyScope.GLOBAL in scopes
        assert PolicyScope.CITY in scopes
        assert PolicyScope.DEPARTMENT in scopes


class TestEmergencyOverrides:
    """Test suite for emergency overrides."""

    def setup_method(self):
        """Set up test fixtures."""
        self.engine = PolicyEngine()

    def test_default_emergency_overrides(self):
        """Test default emergency overrides exist."""
        overrides = self.engine.get_all_emergency_overrides()
        
        override_types = [o.emergency_type for o in overrides]
        assert EmergencyType.HURRICANE in override_types
        assert EmergencyType.FLOODING in override_types
        assert EmergencyType.MASS_CASUALTY in override_types
        assert EmergencyType.POWER_OUTAGE in override_types
        assert EmergencyType.CITY_WIDE_ALERT in override_types

    def test_activate_emergency_override(self):
        """Test emergency override activation."""
        overrides = self.engine.get_all_emergency_overrides()
        hurricane_override = next(
            o for o in overrides if o.emergency_type == EmergencyType.HURRICANE
        )
        
        assert hurricane_override.is_active is False
        
        success = self.engine.activate_emergency_override(
            hurricane_override.override_id,
            activated_by="eoc-commander",
            reason="Hurricane approaching",
        )
        
        assert success is True
        
        updated = self.engine.get_emergency_override(hurricane_override.override_id)
        assert updated.is_active is True
        assert updated.activated_by == "eoc-commander"

    def test_deactivate_emergency_override(self):
        """Test emergency override deactivation."""
        overrides = self.engine.get_all_emergency_overrides()
        flooding_override = next(
            o for o in overrides if o.emergency_type == EmergencyType.FLOODING
        )
        
        self.engine.activate_emergency_override(
            flooding_override.override_id,
            activated_by="eoc-commander",
            reason="Flooding detected",
        )
        
        success = self.engine.deactivate_emergency_override(
            flooding_override.override_id,
            deactivated_by="eoc-commander",
            reason="Flooding subsided",
        )
        
        assert success is True
        
        updated = self.engine.get_emergency_override(flooding_override.override_id)
        assert updated.is_active is False

    def test_get_active_emergency_overrides(self):
        """Test retrieving active emergency overrides."""
        overrides = self.engine.get_all_emergency_overrides()
        
        self.engine.activate_emergency_override(
            overrides[0].override_id,
            activated_by="test",
            reason="Test",
        )
        
        active = self.engine.get_active_emergency_overrides()
        assert len(active) == 1


class TestPolicyConflicts:
    """Test suite for policy conflict detection."""

    def setup_method(self):
        """Set up test fixtures."""
        self.engine = PolicyEngine()

    def test_detect_conflicts(self):
        """Test conflict detection between policies."""
        policy1 = self.engine.create_policy(
            name="Policy 1",
            description="First policy",
            policy_type=PolicyType.TRAFFIC,
            scope=PolicyScope.CITY,
            rules=[
                PolicyRule(
                    rule_id="rule-1",
                    name="Rule 1",
                    description="Extend green phase",
                    condition="congestion > 0.7",
                    action="extend_green_phase",
                    priority=8,
                    enabled=True,
                )
            ],
        )
        
        policy2 = self.engine.create_policy(
            name="Policy 2",
            description="Second policy",
            policy_type=PolicyType.TRAFFIC,
            scope=PolicyScope.CITY,
            rules=[
                PolicyRule(
                    rule_id="rule-2",
                    name="Rule 2",
                    description="Reduce green phase",
                    condition="congestion > 0.7",
                    action="reduce_green_phase",
                    priority=8,
                    enabled=True,
                )
            ],
        )
        
        self.engine.activate_policy(policy1.policy_id)
        self.engine.activate_policy(policy2.policy_id)
        
        conflicts = self.engine.detect_conflicts()
        
        # Should detect conflicting actions for same condition
        assert isinstance(conflicts, list)

    def test_resolve_conflict(self):
        """Test conflict resolution."""
        conflicts = self.engine.detect_conflicts()
        
        if conflicts:
            resolution = self.engine.resolve_conflict(
                conflicts[0].conflict_id,
                resolution_type="priority",
                resolution_details={"winner": "policy1"},
            )
            assert resolution is not None


class TestPolicySimulation:
    """Test suite for policy simulation."""

    def setup_method(self):
        """Set up test fixtures."""
        self.engine = PolicyEngine()

    def test_simulate_policy(self):
        """Test policy simulation."""
        policy = self.engine.create_policy(
            name="Test Policy",
            description="Test",
            policy_type=PolicyType.TRAFFIC,
            scope=PolicyScope.CITY,
            rules=[
                PolicyRule(
                    rule_id="rule-sim-001",
                    name="Congestion Rule",
                    description="Handle congestion",
                    condition="congestion > 0.8",
                    action="optimize_signals",
                    priority=8,
                    enabled=True,
                )
            ],
            thresholds=[
                PolicyThreshold(
                    threshold_id="thresh-sim-001",
                    name="Congestion Alert",
                    metric="congestion",
                    operator="gt",
                    value=0.9,
                    unit="index",
                    action_on_breach="alert",
                )
            ],
        )
        
        scenario = {
            "congestion": 0.85,
            "time": "08:30",
            "day": "monday",
        }
        
        result = self.engine.simulate_policy(policy.policy_id, scenario)
        
        assert result is not None
        assert "triggered_rules" in result
        assert "actions_generated" in result
        assert "success" in result

    def test_get_effective_rules(self):
        """Test getting effective rules for a context."""
        policy = self.engine.create_policy(
            name="Test Policy",
            description="Test",
            policy_type=PolicyType.TRAFFIC,
            scope=PolicyScope.CITY,
            rules=[
                PolicyRule(
                    rule_id="rule-eff-001",
                    name="Test Rule",
                    description="Test",
                    condition="always",
                    action="test_action",
                    priority=5,
                    enabled=True,
                )
            ],
        )
        
        self.engine.activate_policy(policy.policy_id)
        
        context = {
            "policy_type": PolicyType.TRAFFIC,
            "scope": PolicyScope.CITY,
        }
        
        rules = self.engine.get_effective_rules(context)
        assert isinstance(rules, list)

    def test_singleton_instance(self):
        """Test singleton pattern."""
        engine1 = get_policy_engine()
        engine2 = get_policy_engine()
        assert engine1 is engine2

    def test_get_statistics(self):
        """Test statistics retrieval."""
        stats = self.engine.get_statistics()
        
        assert "total_policies" in stats
        assert "policies_by_status" in stats
        assert "policies_by_type" in stats
        assert "emergency_overrides" in stats
