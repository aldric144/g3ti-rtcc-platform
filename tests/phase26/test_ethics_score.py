"""
Test Suite 4: Ethics Score Engine Tests
Tests for ethics scoring
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../backend'))

from app.ethics_guardian.ethics_score import (
    get_ethics_score_engine,
    EthicsScoreEngine,
    EthicsLevel,
    RequiredAction,
)


class TestEthicsScoreEngine:
    """Tests for EthicsScoreEngine"""

    def setup_method(self):
        """Setup test fixtures"""
        self.engine = get_ethics_score_engine()

    def test_singleton_pattern(self):
        """Test that engine follows singleton pattern"""
        engine1 = get_ethics_score_engine()
        engine2 = get_ethics_score_engine()
        assert engine1 is engine2

    def test_component_weights_sum_to_one(self):
        """Test that component weights sum to 1.0"""
        total_weight = sum(self.engine.component_weights.values())
        assert abs(total_weight - 1.0) < 0.01

    def test_eight_components_defined(self):
        """Test that 8 scoring components are defined"""
        assert len(self.engine.component_weights) == 8
        expected_components = [
            "FAIRNESS",
            "CIVIL_RIGHTS",
            "USE_OF_FORCE",
            "HISTORICAL_DISPARITY",
            "POLICY_COMPLIANCE",
            "TRANSPARENCY",
            "COMMUNITY_IMPACT",
            "ACCOUNTABILITY",
        ]
        for component in expected_components:
            assert component in self.engine.component_weights


class TestEthicsLevels:
    """Tests for ethics level classification"""

    def setup_method(self):
        """Setup test fixtures"""
        self.engine = get_ethics_score_engine()

    def test_excellent_level(self):
        """Test EXCELLENT level (90-100)"""
        context = {
            "bias_detected": False,
            "civil_rights_compliant": True,
            "force_risk": 10,
            "historical_disparity": False,
            "policy_compliant": True,
            "transparency_score": 0.95,
            "community_impact": 0.1,
            "accountability_score": 0.95,
        }
        result = self.engine.compute_ethics_score("test-001", "patrol", context)
        assert result.ethics_level == EthicsLevel.EXCELLENT
        assert result.total_score >= 90

    def test_good_level(self):
        """Test GOOD level (75-89)"""
        context = {
            "bias_detected": False,
            "civil_rights_compliant": True,
            "force_risk": 25,
            "historical_disparity": False,
            "policy_compliant": True,
            "transparency_score": 0.80,
            "community_impact": 0.2,
            "accountability_score": 0.85,
        }
        result = self.engine.compute_ethics_score("test-002", "surveillance", context)
        assert result.ethics_level in [EthicsLevel.EXCELLENT, EthicsLevel.GOOD]
        assert result.total_score >= 75

    def test_acceptable_level(self):
        """Test ACCEPTABLE level (60-74)"""
        context = {
            "bias_detected": False,
            "civil_rights_compliant": True,
            "force_risk": 40,
            "historical_disparity": True,
            "policy_compliant": True,
            "transparency_score": 0.65,
            "community_impact": 0.4,
            "accountability_score": 0.70,
        }
        result = self.engine.compute_ethics_score("test-003", "enforcement", context)
        assert result.total_score >= 60

    def test_concerning_level(self):
        """Test CONCERNING level (40-59)"""
        context = {
            "bias_detected": True,
            "civil_rights_compliant": False,
            "force_risk": 60,
            "historical_disparity": True,
            "policy_compliant": False,
            "transparency_score": 0.45,
            "community_impact": 0.6,
            "accountability_score": 0.50,
        }
        result = self.engine.compute_ethics_score("test-004", "enforcement", context)
        assert result.ethics_level in [EthicsLevel.CONCERNING, EthicsLevel.CRITICAL]

    def test_critical_level(self):
        """Test CRITICAL level (0-39)"""
        context = {
            "bias_detected": True,
            "civil_rights_violation": True,
            "force_risk": 85,
            "historical_disparity": True,
            "policy_compliant": False,
            "transparency_score": 0.20,
            "community_impact": 0.9,
            "accountability_score": 0.25,
        }
        result = self.engine.compute_ethics_score("test-005", "enforcement", context)
        assert result.ethics_level == EthicsLevel.CRITICAL
        assert result.total_score < 40


class TestRequiredActions:
    """Tests for required action determination"""

    def setup_method(self):
        """Setup test fixtures"""
        self.engine = get_ethics_score_engine()

    def test_allow_action(self):
        """Test ALLOW action for excellent scores"""
        context = {
            "bias_detected": False,
            "civil_rights_compliant": True,
            "force_risk": 5,
            "policy_compliant": True,
            "transparency_score": 0.98,
        }
        result = self.engine.compute_ethics_score("test-allow", "patrol", context)
        assert result.required_action == RequiredAction.ALLOW

    def test_block_action(self):
        """Test BLOCK action for critical scores"""
        context = {
            "bias_detected": True,
            "civil_rights_violation": True,
            "force_risk": 90,
            "policy_compliant": False,
            "transparency_score": 0.15,
        }
        result = self.engine.compute_ethics_score("test-block", "enforcement", context)
        assert result.required_action == RequiredAction.BLOCK

    def test_review_action(self):
        """Test REVIEW action for concerning scores"""
        context = {
            "bias_detected": True,
            "civil_rights_compliant": False,
            "force_risk": 55,
            "policy_compliant": False,
            "transparency_score": 0.50,
        }
        result = self.engine.compute_ethics_score("test-review", "enforcement", context)
        assert result.required_action in [RequiredAction.REVIEW, RequiredAction.BLOCK]


class TestColorCodes:
    """Tests for ethics level color codes"""

    def setup_method(self):
        """Setup test fixtures"""
        self.engine = get_ethics_score_engine()

    def test_color_codes_defined(self):
        """Test that color codes are defined for all levels"""
        expected_colors = {
            EthicsLevel.EXCELLENT: "#22C55E",
            EthicsLevel.GOOD: "#84CC16",
            EthicsLevel.ACCEPTABLE: "#EAB308",
            EthicsLevel.CONCERNING: "#F97316",
            EthicsLevel.CRITICAL: "#EF4444",
        }
        for level, expected_color in expected_colors.items():
            assert self.engine.level_colors[level] == expected_color


class TestComponentScores:
    """Tests for individual component scores"""

    def setup_method(self):
        """Setup test fixtures"""
        self.engine = get_ethics_score_engine()

    def test_component_scores_included(self):
        """Test that component scores are included in result"""
        context = {
            "bias_detected": False,
            "civil_rights_compliant": True,
            "force_risk": 20,
            "policy_compliant": True,
            "transparency_score": 0.85,
        }
        result = self.engine.compute_ethics_score("test-components", "patrol", context)
        assert hasattr(result, "component_scores")
        assert len(result.component_scores) == 8

    def test_component_score_range(self):
        """Test that component scores are within valid range"""
        context = {
            "bias_detected": False,
            "civil_rights_compliant": True,
            "force_risk": 30,
            "policy_compliant": True,
            "transparency_score": 0.75,
        }
        result = self.engine.compute_ethics_score("test-range", "surveillance", context)
        for component, score in result.component_scores.items():
            assert 0 <= score <= 100


class TestHumanReviewRequirement:
    """Tests for human review requirement"""

    def setup_method(self):
        """Setup test fixtures"""
        self.engine = get_ethics_score_engine()

    def test_human_review_required_for_low_scores(self):
        """Test human review is required for low ethics scores"""
        context = {
            "bias_detected": True,
            "civil_rights_compliant": False,
            "force_risk": 70,
            "policy_compliant": False,
            "transparency_score": 0.40,
        }
        result = self.engine.compute_ethics_score("test-review-req", "enforcement", context)
        assert result.human_review_required is True

    def test_no_human_review_for_high_scores(self):
        """Test human review not required for high ethics scores"""
        context = {
            "bias_detected": False,
            "civil_rights_compliant": True,
            "force_risk": 10,
            "policy_compliant": True,
            "transparency_score": 0.95,
        }
        result = self.engine.compute_ethics_score("test-no-review", "patrol", context)
        assert result.human_review_required is False


class TestEthicsHistory:
    """Tests for ethics score history"""

    def setup_method(self):
        """Setup test fixtures"""
        self.engine = get_ethics_score_engine()

    def test_ethics_history_tracking(self):
        """Test that ethics scores are tracked in history"""
        initial_count = len(self.engine.ethics_history)
        context = {
            "bias_detected": False,
            "civil_rights_compliant": True,
            "force_risk": 15,
            "policy_compliant": True,
        }
        self.engine.compute_ethics_score("test-history", "patrol", context)
        assert len(self.engine.ethics_history) == initial_count + 1
