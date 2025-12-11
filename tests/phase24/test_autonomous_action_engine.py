"""
Phase 24: AutonomousActionEngine Tests

Tests for action interpretation, categorization, execution, and approval workflow.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

from backend.app.city_autonomy import (
    AutonomousActionEngine,
    ActionLevel,
    ActionCategory,
    ActionStatus,
    RiskLevel,
    AutonomousAction,
    get_autonomous_action_engine,
)


class TestAutonomousActionEngine:
    """Test suite for AutonomousActionEngine."""

    def setup_method(self):
        """Set up test fixtures."""
        self.engine = AutonomousActionEngine()

    def test_engine_initialization(self):
        """Test engine initializes with correct defaults."""
        assert self.engine._auto_execute is True
        assert self.engine._circuit_breaker_open is False
        assert self.engine._consecutive_failures == 0
        assert len(self.engine._actions) == 0

    def test_interpret_recommendation_level_0(self):
        """Test Level 0 action interpretation."""
        recommendation = {
            "action_type": "observation",
            "title": "Monitor traffic flow",
            "description": "Observe traffic patterns",
            "parameters": {"zone": "downtown"},
            "priority": 3,
        }
        
        action = self.engine.interpret_recommendation(recommendation)
        
        assert action.level == ActionLevel.LEVEL_0
        assert action.category == ActionCategory.OBSERVATION
        assert action.status == ActionStatus.COMPLETED  # Level 0 auto-completes

    def test_interpret_recommendation_level_1(self):
        """Test Level 1 action interpretation."""
        recommendation = {
            "action_type": "traffic_signal_timing",
            "title": "Optimize signal timing",
            "description": "Adjust signal timing for congestion",
            "parameters": {"intersection": "blue_heron_us1"},
            "priority": 6,
        }
        
        action = self.engine.interpret_recommendation(recommendation)
        
        assert action.level == ActionLevel.LEVEL_1
        assert action.category == ActionCategory.TRAFFIC_CONTROL
        assert action.status == ActionStatus.COMPLETED  # Auto-executed

    def test_interpret_recommendation_level_2(self):
        """Test Level 2 action interpretation."""
        recommendation = {
            "action_type": "deploy_units",
            "title": "Deploy patrol units",
            "description": "Deploy additional patrol units to downtown",
            "parameters": {"units": 3, "zone": "downtown"},
            "priority": 8,
        }
        
        action = self.engine.interpret_recommendation(recommendation)
        
        assert action.level == ActionLevel.LEVEL_2
        assert action.category == ActionCategory.PATROL_DEPLOYMENT
        assert action.status == ActionStatus.PENDING  # Requires approval

    def test_action_categorization(self):
        """Test action type to category mapping."""
        test_cases = [
            ("traffic_signal_timing", ActionCategory.TRAFFIC_CONTROL),
            ("deploy_units", ActionCategory.PATROL_DEPLOYMENT),
            ("send_notification", ActionCategory.NOTIFICATION),
            ("coordinate_evacuation", ActionCategory.EVACUATION),
            ("observation", ActionCategory.OBSERVATION),
        ]
        
        for action_type, expected_category in test_cases:
            recommendation = {
                "action_type": action_type,
                "title": "Test",
                "description": "Test",
                "parameters": {},
            }
            action = self.engine.interpret_recommendation(recommendation)
            assert action.category == expected_category

    def test_approve_action(self):
        """Test action approval."""
        recommendation = {
            "action_type": "deploy_units",
            "title": "Deploy patrol units",
            "description": "Deploy units",
            "parameters": {"units": 2},
            "priority": 8,
        }
        
        action = self.engine.interpret_recommendation(recommendation)
        assert action.status == ActionStatus.PENDING
        
        success = self.engine.approve_action(action.action_id, "operator-001", "Approved")
        
        assert success is True
        updated_action = self.engine.get_action(action.action_id)
        assert updated_action.status == ActionStatus.COMPLETED
        assert updated_action.approved_by == "operator-001"

    def test_deny_action(self):
        """Test action denial."""
        recommendation = {
            "action_type": "deploy_units",
            "title": "Deploy patrol units",
            "description": "Deploy units",
            "parameters": {"units": 2},
            "priority": 8,
        }
        
        action = self.engine.interpret_recommendation(recommendation)
        success = self.engine.deny_action(action.action_id, "operator-001", "Not needed")
        
        assert success is True
        updated_action = self.engine.get_action(action.action_id)
        assert updated_action.status == ActionStatus.DENIED

    def test_escalate_action(self):
        """Test action escalation."""
        recommendation = {
            "action_type": "deploy_units",
            "title": "Deploy patrol units",
            "description": "Deploy units",
            "parameters": {"units": 2},
            "priority": 8,
        }
        
        action = self.engine.interpret_recommendation(recommendation)
        success = self.engine.escalate_action(action.action_id, "supervisor-001", "Need higher approval")
        
        assert success is True
        updated_action = self.engine.get_action(action.action_id)
        assert updated_action.status == ActionStatus.ESCALATED

    def test_get_pending_actions(self):
        """Test retrieving pending actions."""
        for i in range(3):
            recommendation = {
                "action_type": "deploy_units",
                "title": f"Deploy units {i}",
                "description": "Deploy units",
                "parameters": {"units": i + 1},
                "priority": 8,
            }
            self.engine.interpret_recommendation(recommendation)
        
        pending = self.engine.get_pending_actions()
        assert len(pending) == 3
        assert all(a.status == ActionStatus.PENDING for a in pending)

    def test_get_action_history(self):
        """Test retrieving action history."""
        for i in range(5):
            recommendation = {
                "action_type": "traffic_signal_timing",
                "title": f"Signal timing {i}",
                "description": "Adjust timing",
                "parameters": {},
                "priority": 5,
            }
            self.engine.interpret_recommendation(recommendation)
        
        history = self.engine.get_action_history(limit=3)
        assert len(history) == 3

    def test_circuit_breaker_triggers(self):
        """Test circuit breaker triggers after failures."""
        for i in range(5):
            self.engine._record_failure()
        
        assert self.engine._circuit_breaker_open is True
        assert self.engine._auto_execute is False

    def test_circuit_breaker_reset(self):
        """Test circuit breaker reset."""
        for i in range(5):
            self.engine._record_failure()
        
        assert self.engine._circuit_breaker_open is True
        
        self.engine.reset_circuit_breaker()
        
        assert self.engine._circuit_breaker_open is False
        assert self.engine._consecutive_failures == 0

    def test_auto_execute_disabled(self):
        """Test actions require approval when auto-execute disabled."""
        self.engine.set_auto_execute(False)
        
        recommendation = {
            "action_type": "traffic_signal_timing",
            "title": "Signal timing",
            "description": "Adjust timing",
            "parameters": {},
            "priority": 5,
        }
        
        action = self.engine.interpret_recommendation(recommendation)
        
        # Level 1 should still be pending when auto-execute is disabled
        assert action.status == ActionStatus.PENDING

    def test_get_statistics(self):
        """Test statistics retrieval."""
        for i in range(3):
            recommendation = {
                "action_type": "traffic_signal_timing",
                "title": f"Signal timing {i}",
                "description": "Adjust timing",
                "parameters": {},
                "priority": 5,
            }
            self.engine.interpret_recommendation(recommendation)
        
        stats = self.engine.get_statistics()
        
        assert "total_actions" in stats
        assert "actions_by_level" in stats
        assert "actions_by_status" in stats
        assert stats["total_actions"] == 3

    def test_singleton_instance(self):
        """Test singleton pattern."""
        engine1 = get_autonomous_action_engine()
        engine2 = get_autonomous_action_engine()
        assert engine1 is engine2


class TestActionExplainability:
    """Test suite for action explainability."""

    def setup_method(self):
        """Set up test fixtures."""
        self.engine = AutonomousActionEngine()

    def test_explainability_generated(self):
        """Test explainability is generated for actions."""
        recommendation = {
            "action_type": "deploy_units",
            "title": "Deploy patrol units",
            "description": "Deploy units to downtown",
            "parameters": {"units": 3, "zone": "downtown"},
            "priority": 8,
        }
        
        action = self.engine.interpret_recommendation(recommendation)
        
        assert action.explainability is not None
        assert action.explainability.reasoning != ""
        assert len(action.explainability.recommended_path) > 0
        assert action.explainability.confidence_score > 0

    def test_explainability_contains_model_weights(self):
        """Test explainability contains model weights."""
        recommendation = {
            "action_type": "traffic_signal_timing",
            "title": "Signal timing",
            "description": "Adjust timing",
            "parameters": {},
            "priority": 5,
        }
        
        action = self.engine.interpret_recommendation(recommendation)
        
        assert len(action.explainability.model_weights) > 0

    def test_explainability_contains_data_sources(self):
        """Test explainability contains data sources."""
        recommendation = {
            "action_type": "deploy_units",
            "title": "Deploy patrol units",
            "description": "Deploy units",
            "parameters": {"units": 2},
            "priority": 8,
        }
        
        action = self.engine.interpret_recommendation(recommendation)
        
        assert len(action.explainability.data_sources) > 0

    def test_explainability_to_dict(self):
        """Test explainability serialization."""
        recommendation = {
            "action_type": "deploy_units",
            "title": "Deploy patrol units",
            "description": "Deploy units",
            "parameters": {"units": 2},
            "priority": 8,
        }
        
        action = self.engine.interpret_recommendation(recommendation)
        explainability_dict = action.explainability.to_dict()
        
        assert "reasoning" in explainability_dict
        assert "recommended_path" in explainability_dict
        assert "model_weights" in explainability_dict
        assert "confidence_score" in explainability_dict
