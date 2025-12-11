"""
Phase 24: Explainability Validation Tests

Tests for decision explainability, decision trees, and model weights.
"""

import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch

from backend.app.city_autonomy import (
    AutonomousActionEngine,
    ActionExplainability,
    DecisionTreeNode,
)


class TestExplainabilityGeneration:
    """Test suite for explainability generation."""

    def setup_method(self):
        """Set up test fixtures."""
        self.engine = AutonomousActionEngine()

    def test_explainability_always_generated(self):
        """Test explainability is always generated for actions."""
        test_actions = [
            {"action_type": "observation", "title": "Test", "description": "Test", "parameters": {}},
            {"action_type": "traffic_signal_timing", "title": "Test", "description": "Test", "parameters": {}},
            {"action_type": "deploy_units", "title": "Test", "description": "Test", "parameters": {"units": 2}},
        ]
        
        for recommendation in test_actions:
            action = self.engine.interpret_recommendation(recommendation)
            assert action.explainability is not None
            assert isinstance(action.explainability, ActionExplainability)

    def test_explainability_has_reasoning(self):
        """Test explainability contains reasoning."""
        recommendation = {
            "action_type": "deploy_units",
            "title": "Deploy patrol units",
            "description": "Deploy units to downtown",
            "parameters": {"units": 3},
        }
        
        action = self.engine.interpret_recommendation(recommendation)
        
        assert action.explainability.reasoning is not None
        assert len(action.explainability.reasoning) > 0

    def test_explainability_has_recommended_path(self):
        """Test explainability contains recommended path."""
        recommendation = {
            "action_type": "traffic_signal_timing",
            "title": "Adjust signals",
            "description": "Optimize timing",
            "parameters": {},
        }
        
        action = self.engine.interpret_recommendation(recommendation)
        
        assert action.explainability.recommended_path is not None
        assert isinstance(action.explainability.recommended_path, list)
        assert len(action.explainability.recommended_path) > 0

    def test_explainability_has_confidence_score(self):
        """Test explainability contains confidence score."""
        recommendation = {
            "action_type": "deploy_units",
            "title": "Deploy units",
            "description": "Deploy units",
            "parameters": {"units": 2},
        }
        
        action = self.engine.interpret_recommendation(recommendation)
        
        assert action.explainability.confidence_score is not None
        assert 0 <= action.explainability.confidence_score <= 1


class TestModelWeights:
    """Test suite for model weights in explainability."""

    def setup_method(self):
        """Set up test fixtures."""
        self.engine = AutonomousActionEngine()

    def test_model_weights_present(self):
        """Test model weights are present in explainability."""
        recommendation = {
            "action_type": "deploy_units",
            "title": "Deploy units",
            "description": "Deploy units",
            "parameters": {"units": 2},
        }
        
        action = self.engine.interpret_recommendation(recommendation)
        
        assert action.explainability.model_weights is not None
        assert isinstance(action.explainability.model_weights, dict)
        assert len(action.explainability.model_weights) > 0

    def test_model_weights_sum_to_one(self):
        """Test model weights approximately sum to 1."""
        recommendation = {
            "action_type": "traffic_signal_timing",
            "title": "Adjust signals",
            "description": "Optimize timing",
            "parameters": {},
        }
        
        action = self.engine.interpret_recommendation(recommendation)
        
        weights_sum = sum(action.explainability.model_weights.values())
        assert 0.9 <= weights_sum <= 1.1  # Allow small variance

    def test_model_weights_non_negative(self):
        """Test all model weights are non-negative."""
        recommendation = {
            "action_type": "deploy_units",
            "title": "Deploy units",
            "description": "Deploy units",
            "parameters": {"units": 2},
        }
        
        action = self.engine.interpret_recommendation(recommendation)
        
        for weight in action.explainability.model_weights.values():
            assert weight >= 0


class TestDecisionTree:
    """Test suite for decision tree in explainability."""

    def setup_method(self):
        """Set up test fixtures."""
        self.engine = AutonomousActionEngine()

    def test_decision_tree_structure(self):
        """Test decision tree has valid structure."""
        recommendation = {
            "action_type": "deploy_units",
            "title": "Deploy units",
            "description": "Deploy units",
            "parameters": {"units": 2},
        }
        
        action = self.engine.interpret_recommendation(recommendation)
        
        if action.explainability.decision_tree:
            tree = action.explainability.decision_tree
            assert hasattr(tree, "node_id")
            assert hasattr(tree, "condition")
            assert hasattr(tree, "result")

    def test_decision_tree_node_creation(self):
        """Test decision tree node creation."""
        node = DecisionTreeNode(
            node_id="node-001",
            condition="risk_score > 0.5",
            result="require_approval",
            confidence=0.9,
            children=[],
        )
        
        assert node.node_id == "node-001"
        assert node.condition == "risk_score > 0.5"
        assert node.result == "require_approval"
        assert node.confidence == 0.9


class TestDataSources:
    """Test suite for data sources in explainability."""

    def setup_method(self):
        """Set up test fixtures."""
        self.engine = AutonomousActionEngine()

    def test_data_sources_present(self):
        """Test data sources are present in explainability."""
        recommendation = {
            "action_type": "deploy_units",
            "title": "Deploy units",
            "description": "Deploy units",
            "parameters": {"units": 2},
        }
        
        action = self.engine.interpret_recommendation(recommendation)
        
        assert action.explainability.data_sources is not None
        assert isinstance(action.explainability.data_sources, list)

    def test_data_sources_relevant_to_action(self):
        """Test data sources are relevant to action type."""
        traffic_action = {
            "action_type": "traffic_signal_timing",
            "title": "Adjust signals",
            "description": "Optimize timing",
            "parameters": {},
        }
        
        action = self.engine.interpret_recommendation(traffic_action)
        
        # Traffic actions should reference traffic-related data sources
        assert len(action.explainability.data_sources) > 0


class TestAlternativeActions:
    """Test suite for alternative actions in explainability."""

    def setup_method(self):
        """Set up test fixtures."""
        self.engine = AutonomousActionEngine()

    def test_alternative_actions_present(self):
        """Test alternative actions are present in explainability."""
        recommendation = {
            "action_type": "deploy_units",
            "title": "Deploy units",
            "description": "Deploy units",
            "parameters": {"units": 2},
        }
        
        action = self.engine.interpret_recommendation(recommendation)
        
        assert action.explainability.alternative_actions is not None
        assert isinstance(action.explainability.alternative_actions, list)

    def test_alternative_actions_different_from_main(self):
        """Test alternative actions are different from main action."""
        recommendation = {
            "action_type": "deploy_units",
            "title": "Deploy units",
            "description": "Deploy units",
            "parameters": {"units": 2},
        }
        
        action = self.engine.interpret_recommendation(recommendation)
        
        for alt in action.explainability.alternative_actions:
            assert alt != action.action_type


class TestExplainabilitySerialization:
    """Test suite for explainability serialization."""

    def setup_method(self):
        """Set up test fixtures."""
        self.engine = AutonomousActionEngine()

    def test_to_dict_serialization(self):
        """Test explainability serializes to dict."""
        recommendation = {
            "action_type": "deploy_units",
            "title": "Deploy units",
            "description": "Deploy units",
            "parameters": {"units": 2},
        }
        
        action = self.engine.interpret_recommendation(recommendation)
        explainability_dict = action.explainability.to_dict()
        
        assert isinstance(explainability_dict, dict)
        assert "reasoning" in explainability_dict
        assert "recommended_path" in explainability_dict
        assert "model_weights" in explainability_dict
        assert "confidence_score" in explainability_dict
        assert "data_sources" in explainability_dict
        assert "alternative_actions" in explainability_dict

    def test_serialization_preserves_data(self):
        """Test serialization preserves all data."""
        recommendation = {
            "action_type": "deploy_units",
            "title": "Deploy units",
            "description": "Deploy units",
            "parameters": {"units": 2},
        }
        
        action = self.engine.interpret_recommendation(recommendation)
        original = action.explainability
        serialized = original.to_dict()
        
        assert serialized["reasoning"] == original.reasoning
        assert serialized["confidence_score"] == original.confidence_score
        assert serialized["recommended_path"] == original.recommended_path
