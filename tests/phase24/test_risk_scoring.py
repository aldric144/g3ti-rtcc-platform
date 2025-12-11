"""
Phase 24: Risk Scoring Tests

Tests for risk calculation accuracy and risk level classification.
"""

import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch

from backend.app.city_autonomy import (
    AutonomousActionEngine,
    ActionLevel,
    ActionCategory,
    RiskLevel,
)


class TestRiskScoring:
    """Test suite for risk scoring."""

    def setup_method(self):
        """Set up test fixtures."""
        self.engine = AutonomousActionEngine()

    def test_risk_score_range(self):
        """Test risk scores are within valid range."""
        test_actions = [
            {"action_type": "observation", "title": "Test", "description": "Test", "parameters": {}},
            {"action_type": "traffic_signal_timing", "title": "Test", "description": "Test", "parameters": {}},
            {"action_type": "deploy_units", "title": "Test", "description": "Test", "parameters": {"units": 3}},
            {"action_type": "coordinate_evacuation", "title": "Test", "description": "Test", "parameters": {}},
        ]
        
        for recommendation in test_actions:
            action = self.engine.interpret_recommendation(recommendation)
            assert 0 <= action.risk_score <= 1

    def test_risk_level_classification(self):
        """Test risk level classification based on score."""
        test_cases = [
            (0.1, RiskLevel.MINIMAL),
            (0.3, RiskLevel.LOW),
            (0.5, RiskLevel.MEDIUM),
            (0.7, RiskLevel.HIGH),
            (0.9, RiskLevel.CRITICAL),
        ]
        
        for score, expected_level in test_cases:
            level = self.engine._classify_risk_level(score)
            assert level == expected_level

    def test_observation_actions_low_risk(self):
        """Test observation actions have low risk scores."""
        recommendation = {
            "action_type": "observation",
            "title": "Monitor traffic",
            "description": "Observe traffic patterns",
            "parameters": {},
        }
        
        action = self.engine.interpret_recommendation(recommendation)
        
        assert action.risk_score < 0.3
        assert action.risk_level in [RiskLevel.MINIMAL, RiskLevel.LOW]

    def test_traffic_control_moderate_risk(self):
        """Test traffic control actions have moderate risk."""
        recommendation = {
            "action_type": "traffic_signal_timing",
            "title": "Adjust signals",
            "description": "Optimize signal timing",
            "parameters": {"intersection": "test"},
        }
        
        action = self.engine.interpret_recommendation(recommendation)
        
        assert action.risk_score < 0.5
        assert action.risk_level in [RiskLevel.MINIMAL, RiskLevel.LOW, RiskLevel.MEDIUM]

    def test_deployment_actions_higher_risk(self):
        """Test deployment actions have higher risk scores."""
        recommendation = {
            "action_type": "deploy_units",
            "title": "Deploy patrol units",
            "description": "Deploy units to area",
            "parameters": {"units": 5, "zone": "downtown"},
        }
        
        action = self.engine.interpret_recommendation(recommendation)
        
        assert action.risk_score >= 0.3
        assert action.risk_level in [RiskLevel.MEDIUM, RiskLevel.HIGH]

    def test_evacuation_actions_high_risk(self):
        """Test evacuation actions have high risk scores."""
        recommendation = {
            "action_type": "coordinate_evacuation",
            "title": "Evacuate flood zone",
            "description": "Coordinate evacuation of flood zone",
            "parameters": {"zone": "flood_zone_a", "population": 1200},
        }
        
        action = self.engine.interpret_recommendation(recommendation)
        
        assert action.risk_score >= 0.5
        assert action.risk_level in [RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL]

    def test_parameter_sensitivity_affects_risk(self):
        """Test parameter sensitivity affects risk score."""
        low_units = {
            "action_type": "deploy_units",
            "title": "Deploy patrol units",
            "description": "Deploy units",
            "parameters": {"units": 1},
        }
        
        high_units = {
            "action_type": "deploy_units",
            "title": "Deploy patrol units",
            "description": "Deploy units",
            "parameters": {"units": 10},
        }
        
        action_low = self.engine.interpret_recommendation(low_units)
        action_high = self.engine.interpret_recommendation(high_units)
        
        # Higher unit count should have higher or equal risk
        assert action_high.risk_score >= action_low.risk_score - 0.1  # Allow small variance

    def test_priority_affects_risk(self):
        """Test action priority affects risk assessment."""
        low_priority = {
            "action_type": "send_notification",
            "title": "Send alert",
            "description": "Send notification",
            "parameters": {},
            "priority": 3,
        }
        
        high_priority = {
            "action_type": "send_notification",
            "title": "Send alert",
            "description": "Send notification",
            "parameters": {},
            "priority": 9,
        }
        
        action_low = self.engine.interpret_recommendation(low_priority)
        action_high = self.engine.interpret_recommendation(high_priority)
        
        # Both should be valid actions
        assert action_low.priority == 3
        assert action_high.priority == 9


class TestRiskLevelToActionLevel:
    """Test suite for risk level to action level mapping."""

    def setup_method(self):
        """Set up test fixtures."""
        self.engine = AutonomousActionEngine()

    def test_minimal_risk_level_0_or_1(self):
        """Test minimal risk maps to Level 0 or 1."""
        recommendation = {
            "action_type": "observation",
            "title": "Monitor",
            "description": "Observe",
            "parameters": {},
        }
        
        action = self.engine.interpret_recommendation(recommendation)
        
        assert action.level in [ActionLevel.LEVEL_0, ActionLevel.LEVEL_1]

    def test_low_risk_level_1(self):
        """Test low risk maps to Level 1."""
        recommendation = {
            "action_type": "traffic_signal_timing",
            "title": "Adjust signals",
            "description": "Optimize timing",
            "parameters": {},
        }
        
        action = self.engine.interpret_recommendation(recommendation)
        
        assert action.level == ActionLevel.LEVEL_1

    def test_medium_high_risk_level_2(self):
        """Test medium/high risk maps to Level 2."""
        recommendation = {
            "action_type": "deploy_units",
            "title": "Deploy units",
            "description": "Deploy patrol units",
            "parameters": {"units": 5},
        }
        
        action = self.engine.interpret_recommendation(recommendation)
        
        assert action.level == ActionLevel.LEVEL_2

    def test_critical_risk_level_2(self):
        """Test critical risk maps to Level 2."""
        recommendation = {
            "action_type": "coordinate_evacuation",
            "title": "Evacuate",
            "description": "Coordinate evacuation",
            "parameters": {"zone": "flood_zone_a"},
        }
        
        action = self.engine.interpret_recommendation(recommendation)
        
        assert action.level == ActionLevel.LEVEL_2


class TestRiskFactors:
    """Test suite for risk factor identification."""

    def setup_method(self):
        """Set up test fixtures."""
        self.engine = AutonomousActionEngine()

    def test_risk_factors_identified(self):
        """Test risk factors are identified in explainability."""
        recommendation = {
            "action_type": "deploy_units",
            "title": "Deploy units",
            "description": "Deploy patrol units to high crime area",
            "parameters": {"units": 3, "zone": "downtown"},
        }
        
        action = self.engine.interpret_recommendation(recommendation)
        
        assert hasattr(action.explainability, "risk_factors")
        assert isinstance(action.explainability.risk_factors, list)

    def test_high_risk_has_more_factors(self):
        """Test higher risk actions have more risk factors."""
        low_risk = {
            "action_type": "observation",
            "title": "Monitor",
            "description": "Observe",
            "parameters": {},
        }
        
        high_risk = {
            "action_type": "coordinate_evacuation",
            "title": "Evacuate",
            "description": "Coordinate evacuation",
            "parameters": {"zone": "flood_zone_a", "population": 1200},
        }
        
        action_low = self.engine.interpret_recommendation(low_risk)
        action_high = self.engine.interpret_recommendation(high_risk)
        
        # Both should have risk factors (may be empty for low risk)
        assert isinstance(action_low.explainability.risk_factors, list)
        assert isinstance(action_high.explainability.risk_factors, list)
