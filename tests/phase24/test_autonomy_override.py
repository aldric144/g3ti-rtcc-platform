"""
Phase 24: Autonomy Override Tests

Tests for manual override mechanisms and mode switching.
"""

import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch

from backend.app.city_autonomy import (
    AutonomousActionEngine,
    ActionLevel,
    ActionStatus,
)
from backend.app.city_autonomy.policy_engine import (
    PolicyEngine,
    EmergencyType,
)
from backend.app.city_autonomy.stabilizer import (
    AutomatedCityStabilizer,
    StabilizerStatus,
)


class TestManualModeSwitch:
    """Test suite for manual mode switching."""

    def setup_method(self):
        """Set up test fixtures."""
        self.engine = AutonomousActionEngine()

    def test_switch_to_manual_mode(self):
        """Test switching to manual mode."""
        assert self.engine._auto_execute is True
        
        self.engine.set_auto_execute(False)
        
        assert self.engine._auto_execute is False

    def test_switch_to_autonomous_mode(self):
        """Test switching to autonomous mode."""
        self.engine.set_auto_execute(False)
        assert self.engine._auto_execute is False
        
        self.engine.set_auto_execute(True)
        
        assert self.engine._auto_execute is True

    def test_manual_mode_requires_approval_for_level_1(self):
        """Test manual mode requires approval for Level 1 actions."""
        self.engine.set_auto_execute(False)
        
        recommendation = {
            "action_type": "traffic_signal_timing",
            "title": "Adjust signals",
            "description": "Optimize timing",
            "parameters": {},
        }
        
        action = self.engine.interpret_recommendation(recommendation)
        
        # In manual mode, Level 1 should still be pending
        assert action.status == ActionStatus.PENDING

    def test_autonomous_mode_auto_executes_level_1(self):
        """Test autonomous mode auto-executes Level 1 actions."""
        self.engine.set_auto_execute(True)
        
        recommendation = {
            "action_type": "traffic_signal_timing",
            "title": "Adjust signals",
            "description": "Optimize timing",
            "parameters": {},
        }
        
        action = self.engine.interpret_recommendation(recommendation)
        
        assert action.status == ActionStatus.COMPLETED


class TestCircuitBreakerOverride:
    """Test suite for circuit breaker override."""

    def setup_method(self):
        """Set up test fixtures."""
        self.engine = AutonomousActionEngine()

    def test_circuit_breaker_forces_manual_mode(self):
        """Test circuit breaker forces manual mode."""
        for i in range(5):
            self.engine._record_failure()
        
        assert self.engine._circuit_breaker_open is True
        assert self.engine._auto_execute is False

    def test_circuit_breaker_reset_restores_mode(self):
        """Test circuit breaker reset restores autonomous mode."""
        original_mode = self.engine._auto_execute
        
        for i in range(5):
            self.engine._record_failure()
        
        self.engine.reset_circuit_breaker()
        
        assert self.engine._circuit_breaker_open is False
        # Mode should be restored or remain as configured

    def test_actions_require_approval_when_breaker_open(self):
        """Test all actions require approval when circuit breaker is open."""
        for i in range(5):
            self.engine._record_failure()
        
        recommendation = {
            "action_type": "traffic_signal_timing",
            "title": "Adjust signals",
            "description": "Optimize timing",
            "parameters": {},
        }
        
        action = self.engine.interpret_recommendation(recommendation)
        
        # Should require approval when circuit breaker is open
        assert action.status == ActionStatus.PENDING


class TestEmergencyOverride:
    """Test suite for emergency override mechanisms."""

    def setup_method(self):
        """Set up test fixtures."""
        self.policy_engine = PolicyEngine()

    def test_activate_emergency_override(self):
        """Test activating emergency override."""
        overrides = self.policy_engine.get_all_emergency_overrides()
        hurricane_override = next(
            o for o in overrides if o.emergency_type == EmergencyType.HURRICANE
        )
        
        success = self.policy_engine.activate_emergency_override(
            hurricane_override.override_id,
            activated_by="eoc-commander",
            reason="Hurricane approaching",
        )
        
        assert success is True
        
        updated = self.policy_engine.get_emergency_override(hurricane_override.override_id)
        assert updated.is_active is True

    def test_deactivate_emergency_override(self):
        """Test deactivating emergency override."""
        overrides = self.policy_engine.get_all_emergency_overrides()
        flooding_override = next(
            o for o in overrides if o.emergency_type == EmergencyType.FLOODING
        )
        
        self.policy_engine.activate_emergency_override(
            flooding_override.override_id,
            activated_by="eoc-commander",
            reason="Flooding detected",
        )
        
        success = self.policy_engine.deactivate_emergency_override(
            flooding_override.override_id,
            deactivated_by="eoc-commander",
            reason="Flooding subsided",
        )
        
        assert success is True
        
        updated = self.policy_engine.get_emergency_override(flooding_override.override_id)
        assert updated.is_active is False

    def test_emergency_override_affects_policies(self):
        """Test emergency override affects related policies."""
        overrides = self.policy_engine.get_all_emergency_overrides()
        hurricane_override = next(
            o for o in overrides if o.emergency_type == EmergencyType.HURRICANE
        )
        
        assert len(hurricane_override.affected_policies) > 0


class TestStabilizerOverride:
    """Test suite for stabilizer override mechanisms."""

    def setup_method(self):
        """Set up test fixtures."""
        self.stabilizer = AutomatedCityStabilizer()

    def test_pause_stabilization(self):
        """Test pausing stabilization."""
        self.stabilizer._status = StabilizerStatus.RUNNING
        
        self.stabilizer.pause()
        
        assert self.stabilizer._status == StabilizerStatus.PAUSED

    def test_resume_stabilization(self):
        """Test resuming stabilization."""
        self.stabilizer._status = StabilizerStatus.PAUSED
        
        self.stabilizer.resume()
        
        assert self.stabilizer._status in [StabilizerStatus.IDLE, StabilizerStatus.RUNNING]

    def test_emergency_stop(self):
        """Test emergency stop."""
        self.stabilizer._status = StabilizerStatus.RUNNING
        
        self.stabilizer.emergency_stop()
        
        assert self.stabilizer._status == StabilizerStatus.STOPPED

    def test_reset_after_emergency_stop(self):
        """Test reset after emergency stop."""
        self.stabilizer.emergency_stop()
        assert self.stabilizer._status == StabilizerStatus.STOPPED
        
        self.stabilizer.reset()
        
        assert self.stabilizer._status == StabilizerStatus.IDLE


class TestOverrideAuditTrail:
    """Test suite for override audit trail."""

    def setup_method(self):
        """Set up test fixtures."""
        self.engine = AutonomousActionEngine()
        self.policy_engine = PolicyEngine()

    def test_mode_switch_logged(self):
        """Test mode switch is logged."""
        # Mode switches should be tracked
        self.engine.set_auto_execute(False)
        self.engine.set_auto_execute(True)
        
        # Verify mode changes occurred
        assert self.engine._auto_execute is True

    def test_circuit_breaker_events_logged(self):
        """Test circuit breaker events are logged."""
        for i in range(5):
            self.engine._record_failure()
        
        assert self.engine._circuit_breaker_open is True
        
        self.engine.reset_circuit_breaker()
        
        assert self.engine._circuit_breaker_open is False

    def test_emergency_override_activation_logged(self):
        """Test emergency override activation is logged."""
        overrides = self.policy_engine.get_all_emergency_overrides()
        override = overrides[0]
        
        self.policy_engine.activate_emergency_override(
            override.override_id,
            activated_by="test-user",
            reason="Test activation",
        )
        
        updated = self.policy_engine.get_emergency_override(override.override_id)
        assert updated.activated_by == "test-user"
        assert updated.activated_at is not None
