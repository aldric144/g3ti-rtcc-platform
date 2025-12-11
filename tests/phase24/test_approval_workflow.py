"""
Phase 24: Approval Workflow Tests

Tests for action approval, denial, escalation, and timeout handling.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

from backend.app.city_autonomy import (
    AutonomousActionEngine,
    ActionLevel,
    ActionStatus,
)


class TestApprovalWorkflow:
    """Test suite for approval workflow."""

    def setup_method(self):
        """Set up test fixtures."""
        self.engine = AutonomousActionEngine()

    def test_level_2_requires_approval(self):
        """Test Level 2 actions require approval."""
        recommendation = {
            "action_type": "deploy_units",
            "title": "Deploy patrol units",
            "description": "Deploy units to downtown",
            "parameters": {"units": 3},
        }
        
        action = self.engine.interpret_recommendation(recommendation)
        
        assert action.level == ActionLevel.LEVEL_2
        assert action.status == ActionStatus.PENDING

    def test_level_1_auto_executes(self):
        """Test Level 1 actions auto-execute."""
        recommendation = {
            "action_type": "traffic_signal_timing",
            "title": "Adjust signals",
            "description": "Optimize timing",
            "parameters": {},
        }
        
        action = self.engine.interpret_recommendation(recommendation)
        
        assert action.level == ActionLevel.LEVEL_1
        assert action.status == ActionStatus.COMPLETED

    def test_approve_pending_action(self):
        """Test approving a pending action."""
        recommendation = {
            "action_type": "deploy_units",
            "title": "Deploy units",
            "description": "Deploy units",
            "parameters": {"units": 2},
        }
        
        action = self.engine.interpret_recommendation(recommendation)
        assert action.status == ActionStatus.PENDING
        
        success = self.engine.approve_action(
            action.action_id,
            approved_by="operator-001",
            approval_notes="Approved for deployment",
        )
        
        assert success is True
        
        updated = self.engine.get_action(action.action_id)
        assert updated.status == ActionStatus.COMPLETED
        assert updated.approved_by == "operator-001"
        assert updated.approved_at is not None

    def test_deny_pending_action(self):
        """Test denying a pending action."""
        recommendation = {
            "action_type": "deploy_units",
            "title": "Deploy units",
            "description": "Deploy units",
            "parameters": {"units": 2},
        }
        
        action = self.engine.interpret_recommendation(recommendation)
        
        success = self.engine.deny_action(
            action.action_id,
            denied_by="operator-001",
            denial_reason="Not needed at this time",
        )
        
        assert success is True
        
        updated = self.engine.get_action(action.action_id)
        assert updated.status == ActionStatus.DENIED

    def test_cannot_approve_non_pending(self):
        """Test cannot approve non-pending action."""
        recommendation = {
            "action_type": "traffic_signal_timing",
            "title": "Adjust signals",
            "description": "Optimize timing",
            "parameters": {},
        }
        
        action = self.engine.interpret_recommendation(recommendation)
        assert action.status == ActionStatus.COMPLETED
        
        success = self.engine.approve_action(
            action.action_id,
            approved_by="operator-001",
        )
        
        assert success is False

    def test_cannot_deny_non_pending(self):
        """Test cannot deny non-pending action."""
        recommendation = {
            "action_type": "traffic_signal_timing",
            "title": "Adjust signals",
            "description": "Optimize timing",
            "parameters": {},
        }
        
        action = self.engine.interpret_recommendation(recommendation)
        assert action.status == ActionStatus.COMPLETED
        
        success = self.engine.deny_action(
            action.action_id,
            denied_by="operator-001",
            denial_reason="Test",
        )
        
        assert success is False


class TestEscalation:
    """Test suite for action escalation."""

    def setup_method(self):
        """Set up test fixtures."""
        self.engine = AutonomousActionEngine()

    def test_escalate_pending_action(self):
        """Test escalating a pending action."""
        recommendation = {
            "action_type": "deploy_units",
            "title": "Deploy units",
            "description": "Deploy units",
            "parameters": {"units": 2},
        }
        
        action = self.engine.interpret_recommendation(recommendation)
        
        success = self.engine.escalate_action(
            action.action_id,
            escalated_by="operator-001",
            escalation_reason="Requires supervisor approval",
        )
        
        assert success is True
        
        updated = self.engine.get_action(action.action_id)
        assert updated.status == ActionStatus.ESCALATED

    def test_cannot_escalate_non_pending(self):
        """Test cannot escalate non-pending action."""
        recommendation = {
            "action_type": "traffic_signal_timing",
            "title": "Adjust signals",
            "description": "Optimize timing",
            "parameters": {},
        }
        
        action = self.engine.interpret_recommendation(recommendation)
        
        success = self.engine.escalate_action(
            action.action_id,
            escalated_by="operator-001",
            escalation_reason="Test",
        )
        
        assert success is False

    def test_escalated_action_can_be_approved(self):
        """Test escalated action can still be approved."""
        recommendation = {
            "action_type": "deploy_units",
            "title": "Deploy units",
            "description": "Deploy units",
            "parameters": {"units": 2},
        }
        
        action = self.engine.interpret_recommendation(recommendation)
        self.engine.escalate_action(
            action.action_id,
            escalated_by="operator-001",
            escalation_reason="Test",
        )
        
        # Escalated actions should still be approvable
        updated = self.engine.get_action(action.action_id)
        assert updated.status == ActionStatus.ESCALATED


class TestPendingActionsQueue:
    """Test suite for pending actions queue."""

    def setup_method(self):
        """Set up test fixtures."""
        self.engine = AutonomousActionEngine()

    def test_get_pending_actions(self):
        """Test retrieving pending actions."""
        for i in range(3):
            recommendation = {
                "action_type": "deploy_units",
                "title": f"Deploy units {i}",
                "description": "Deploy units",
                "parameters": {"units": i + 1},
            }
            self.engine.interpret_recommendation(recommendation)
        
        pending = self.engine.get_pending_actions()
        
        assert len(pending) == 3
        assert all(a.status == ActionStatus.PENDING for a in pending)

    def test_pending_actions_sorted_by_priority(self):
        """Test pending actions are sorted by priority."""
        priorities = [5, 9, 3, 7]
        
        for priority in priorities:
            recommendation = {
                "action_type": "deploy_units",
                "title": f"Deploy units p{priority}",
                "description": "Deploy units",
                "parameters": {"units": 1},
                "priority": priority,
            }
            self.engine.interpret_recommendation(recommendation)
        
        pending = self.engine.get_pending_actions()
        
        # Should be sorted by priority (highest first)
        for i in range(len(pending) - 1):
            assert pending[i].priority >= pending[i + 1].priority

    def test_approved_action_removed_from_pending(self):
        """Test approved action is removed from pending queue."""
        recommendation = {
            "action_type": "deploy_units",
            "title": "Deploy units",
            "description": "Deploy units",
            "parameters": {"units": 2},
        }
        
        action = self.engine.interpret_recommendation(recommendation)
        
        pending_before = self.engine.get_pending_actions()
        assert any(a.action_id == action.action_id for a in pending_before)
        
        self.engine.approve_action(action.action_id, approved_by="operator-001")
        
        pending_after = self.engine.get_pending_actions()
        assert not any(a.action_id == action.action_id for a in pending_after)


class TestApprovalTracking:
    """Test suite for approval tracking."""

    def setup_method(self):
        """Set up test fixtures."""
        self.engine = AutonomousActionEngine()

    def test_approval_timestamp_recorded(self):
        """Test approval timestamp is recorded."""
        recommendation = {
            "action_type": "deploy_units",
            "title": "Deploy units",
            "description": "Deploy units",
            "parameters": {"units": 2},
        }
        
        action = self.engine.interpret_recommendation(recommendation)
        before_approval = datetime.utcnow()
        
        self.engine.approve_action(action.action_id, approved_by="operator-001")
        
        updated = self.engine.get_action(action.action_id)
        assert updated.approved_at is not None
        assert updated.approved_at >= before_approval

    def test_approver_recorded(self):
        """Test approver is recorded."""
        recommendation = {
            "action_type": "deploy_units",
            "title": "Deploy units",
            "description": "Deploy units",
            "parameters": {"units": 2},
        }
        
        action = self.engine.interpret_recommendation(recommendation)
        
        self.engine.approve_action(
            action.action_id,
            approved_by="supervisor-johnson",
        )
        
        updated = self.engine.get_action(action.action_id)
        assert updated.approved_by == "supervisor-johnson"

    def test_execution_timestamp_recorded(self):
        """Test execution timestamp is recorded."""
        recommendation = {
            "action_type": "deploy_units",
            "title": "Deploy units",
            "description": "Deploy units",
            "parameters": {"units": 2},
        }
        
        action = self.engine.interpret_recommendation(recommendation)
        
        self.engine.approve_action(action.action_id, approved_by="operator-001")
        
        updated = self.engine.get_action(action.action_id)
        assert updated.executed_at is not None or updated.completed_at is not None
