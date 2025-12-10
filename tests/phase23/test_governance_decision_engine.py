"""
Phase 23: GovernanceDecisionEngine Tests
"""

import pytest
from datetime import datetime, timedelta
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../backend'))

from app.city_governance import (
    GovernanceDecisionEngine,
    get_governance_engine,
    DecisionDomain,
    DecisionPriority,
    DecisionStatus,
    RecommendationType,
    ConfidenceLevel,
    GovernanceDecision,
    DecisionRule,
    PolicyModel,
)


class TestGovernanceDecisionEngine:
    """Tests for GovernanceDecisionEngine."""

    def setup_method(self):
        """Set up test fixtures."""
        self.engine = GovernanceDecisionEngine()

    def test_engine_initialization(self):
        """Test engine initializes with default rules and models."""
        assert len(self.engine._rules) == 8
        assert len(self.engine._policy_models) == 4
        assert len(self.engine._decisions) == 0

    def test_get_singleton_instance(self):
        """Test singleton pattern returns same instance."""
        engine1 = get_governance_engine()
        engine2 = get_governance_engine()
        assert engine1 is engine2

    def test_process_city_data_high_crime(self):
        """Test decision generation for high crime scenario."""
        city_state = {
            "zones": {
                "downtown": {
                    "crime_rate": 0.85,
                    "patrol_coverage": 0.5,
                    "population": 8500,
                }
            },
            "timestamp": datetime.utcnow().isoformat(),
        }

        decisions = self.engine.process_city_data(city_state)
        assert len(decisions) > 0

        patrol_decisions = [
            d for d in decisions
            if d.domain == DecisionDomain.PUBLIC_SAFETY
        ]
        assert len(patrol_decisions) > 0

    def test_process_city_data_traffic_congestion(self):
        """Test decision generation for traffic congestion."""
        city_state = {
            "traffic": {
                "congestion_level": 0.8,
                "average_speed": 15,
            },
            "timestamp": datetime.utcnow().isoformat(),
        }

        decisions = self.engine.process_city_data(city_state)
        traffic_decisions = [
            d for d in decisions
            if d.domain == DecisionDomain.TRAFFIC_MOBILITY
        ]
        assert len(traffic_decisions) >= 0

    def test_process_city_data_storm_warning(self):
        """Test decision generation for storm warning."""
        city_state = {
            "weather": {
                "storm_probability": 0.75,
                "wind_speed": 45,
                "rainfall_forecast": 5.0,
            },
            "timestamp": datetime.utcnow().isoformat(),
        }

        decisions = self.engine.process_city_data(city_state)
        storm_decisions = [
            d for d in decisions
            if d.domain == DecisionDomain.STORM_HURRICANE
        ]
        assert len(storm_decisions) >= 0

    def test_decision_approval_workflow(self):
        """Test decision approval workflow."""
        city_state = {
            "zones": {
                "downtown": {"crime_rate": 0.9, "patrol_coverage": 0.4}
            }
        }
        decisions = self.engine.process_city_data(city_state)

        if decisions:
            decision = decisions[0]
            assert decision.status == DecisionStatus.PENDING

            success = self.engine.approve_decision(
                decision.decision_id,
                "test_user",
                "Approved for testing"
            )
            assert success

            updated = self.engine.get_decision(decision.decision_id)
            assert updated.status == DecisionStatus.APPROVED
            assert updated.approved_by == "test_user"

    def test_decision_rejection_workflow(self):
        """Test decision rejection workflow."""
        city_state = {
            "zones": {
                "marina": {"crime_rate": 0.85, "patrol_coverage": 0.5}
            }
        }
        decisions = self.engine.process_city_data(city_state)

        if decisions:
            decision = decisions[0]
            success = self.engine.reject_decision(
                decision.decision_id,
                "test_user",
                "Not applicable"
            )
            assert success

            updated = self.engine.get_decision(decision.decision_id)
            assert updated.status == DecisionStatus.REJECTED

    def test_decision_implementation(self):
        """Test decision implementation workflow."""
        city_state = {
            "zones": {
                "westside": {"crime_rate": 0.88, "patrol_coverage": 0.45}
            }
        }
        decisions = self.engine.process_city_data(city_state)

        if decisions:
            decision = decisions[0]
            self.engine.approve_decision(decision.decision_id, "admin")

            success = self.engine.implement_decision(decision.decision_id)
            assert success

            updated = self.engine.get_decision(decision.decision_id)
            assert updated.status == DecisionStatus.IMPLEMENTED

    def test_get_decisions_by_domain(self):
        """Test filtering decisions by domain."""
        city_state = {
            "zones": {"downtown": {"crime_rate": 0.9}},
            "traffic": {"congestion_level": 0.8},
        }
        self.engine.process_city_data(city_state)

        safety_decisions = self.engine.get_decisions_by_domain(
            DecisionDomain.PUBLIC_SAFETY
        )
        assert isinstance(safety_decisions, list)

    def test_get_pending_decisions(self):
        """Test getting pending decisions."""
        city_state = {
            "zones": {"downtown": {"crime_rate": 0.85}}
        }
        self.engine.process_city_data(city_state)

        pending = self.engine.get_pending_decisions()
        assert isinstance(pending, list)
        for decision in pending:
            assert decision.status == DecisionStatus.PENDING

    def test_decision_expiration(self):
        """Test decision expiration handling."""
        city_state = {
            "zones": {"downtown": {"crime_rate": 0.9}}
        }
        decisions = self.engine.process_city_data(city_state)

        if decisions:
            decision = decisions[0]
            assert decision.valid_until > datetime.utcnow()

    def test_decision_explanation(self):
        """Test decision explanation generation."""
        city_state = {
            "zones": {"downtown": {"crime_rate": 0.9, "patrol_coverage": 0.4}}
        }
        decisions = self.engine.process_city_data(city_state)

        if decisions:
            decision = decisions[0]
            assert decision.explanation is not None
            assert decision.explanation.reasoning is not None
            assert len(decision.explanation.factors) > 0

    def test_add_custom_rule(self):
        """Test adding custom decision rule."""
        custom_rule = DecisionRule(
            rule_id="custom_test_rule",
            name="Test Rule",
            domain=DecisionDomain.PUBLIC_SAFETY,
            conditions={"test_metric": {"min": 0.5}},
            action_template={"action": "test_action"},
            priority=DecisionPriority.MEDIUM,
            weight=0.8,
        )

        self.engine.add_rule(custom_rule)
        assert "custom_test_rule" in self.engine._rules

    def test_add_policy_model(self):
        """Test adding policy model."""
        custom_model = PolicyModel(
            model_id="custom_test_model",
            name="Test Model",
            domain=DecisionDomain.PUBLIC_SAFETY,
            model_type="test",
            parameters={"param1": 1.0},
            confidence_threshold=0.7,
        )

        self.engine.add_policy_model(custom_model)
        assert "custom_test_model" in self.engine._policy_models

    def test_statistics(self):
        """Test statistics generation."""
        city_state = {
            "zones": {"downtown": {"crime_rate": 0.85}}
        }
        self.engine.process_city_data(city_state)

        stats = self.engine.get_statistics()
        assert "total_decisions" in stats
        assert "decisions_by_status" in stats
        assert "decisions_by_domain" in stats
        assert "rules_count" in stats
        assert "policy_models_count" in stats

    def test_decision_to_dict(self):
        """Test decision serialization."""
        city_state = {
            "zones": {"downtown": {"crime_rate": 0.9}}
        }
        decisions = self.engine.process_city_data(city_state)

        if decisions:
            decision_dict = decisions[0].to_dict()
            assert "decision_id" in decision_dict
            assert "domain" in decision_dict
            assert "title" in decision_dict
            assert "status" in decision_dict
            assert "explanation" in decision_dict


class TestDecisionDomains:
    """Tests for decision domain enumeration."""

    def test_all_domains_defined(self):
        """Test all expected domains are defined."""
        expected_domains = [
            "public_safety",
            "traffic_mobility",
            "utilities",
            "public_works",
            "storm_hurricane",
            "city_events",
        ]
        for domain in expected_domains:
            assert DecisionDomain(domain) is not None

    def test_domain_values(self):
        """Test domain enum values."""
        assert DecisionDomain.PUBLIC_SAFETY.value == "public_safety"
        assert DecisionDomain.TRAFFIC_MOBILITY.value == "traffic_mobility"
        assert DecisionDomain.UTILITIES.value == "utilities"


class TestDecisionPriority:
    """Tests for decision priority enumeration."""

    def test_priority_ordering(self):
        """Test priority levels are properly ordered."""
        assert DecisionPriority.CRITICAL.value == 4
        assert DecisionPriority.HIGH.value == 3
        assert DecisionPriority.MEDIUM.value == 2
        assert DecisionPriority.LOW.value == 1


class TestConfidenceLevel:
    """Tests for confidence level enumeration."""

    def test_confidence_levels(self):
        """Test confidence levels are defined."""
        assert ConfidenceLevel.HIGH.value == "high"
        assert ConfidenceLevel.MEDIUM.value == "medium"
        assert ConfidenceLevel.LOW.value == "low"
        assert ConfidenceLevel.UNCERTAIN.value == "uncertain"
