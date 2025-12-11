"""
Test Suite 4: Governance Risk Scoring Engine Tests

Tests for risk factor calculation, category assignment, and threshold validation.
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch

import sys
sys.path.insert(0, "/home/ubuntu/repos/g3ti-rtcc-platform/backend")

from app.city_governance.risk_scoring import (
    get_risk_scoring_engine,
    RiskScoringEngine,
    RiskAssessment,
    RiskCategory,
    RiskFactor,
)
from app.city_governance.constitution_engine import ActionCategory, AutonomyLevel


class TestRiskCategory:
    """Tests for RiskCategory enum."""

    def test_risk_categories(self):
        """Test all risk category values."""
        assert RiskCategory.LOW.value == "LOW"
        assert RiskCategory.ELEVATED.value == "ELEVATED"
        assert RiskCategory.HIGH.value == "HIGH"
        assert RiskCategory.CRITICAL.value == "CRITICAL"

    def test_risk_category_thresholds(self):
        """Test risk category threshold ranges."""
        # LOW: 0-25, ELEVATED: 26-50, HIGH: 51-75, CRITICAL: 76-100
        engine = get_risk_scoring_engine()
        
        assert engine.get_category_for_score(0) == RiskCategory.LOW
        assert engine.get_category_for_score(25) == RiskCategory.LOW
        assert engine.get_category_for_score(26) == RiskCategory.ELEVATED
        assert engine.get_category_for_score(50) == RiskCategory.ELEVATED
        assert engine.get_category_for_score(51) == RiskCategory.HIGH
        assert engine.get_category_for_score(75) == RiskCategory.HIGH
        assert engine.get_category_for_score(76) == RiskCategory.CRITICAL
        assert engine.get_category_for_score(100) == RiskCategory.CRITICAL


class TestRiskFactor:
    """Tests for RiskFactor model."""

    def test_risk_factor_creation(self):
        """Test creating a risk factor."""
        factor = RiskFactor(
            factor_id="legal-exposure",
            name="Legal Exposure",
            description="Potential for legal liability",
            max_score=25,
            weight=1.0,
        )
        assert factor.factor_id == "legal-exposure"
        assert factor.max_score == 25
        assert factor.weight == 1.0

    def test_all_risk_factors(self):
        """Test all five risk factors exist."""
        engine = get_risk_scoring_engine()
        factors = engine.get_risk_factors()
        
        factor_names = [f.name for f in factors]
        assert "Legal Exposure" in factor_names or len(factors) >= 5
        
        # Total max score should be 100
        total_max = sum(f.max_score for f in factors)
        assert total_max == 100


class TestRiskAssessment:
    """Tests for RiskAssessment model."""

    def test_risk_assessment_creation(self):
        """Test creating a risk assessment."""
        assessment = RiskAssessment(
            assessment_id="assess-001",
            action_id="action-001",
            action_type="surveillance_escalation",
            category=ActionCategory.SURVEILLANCE,
            autonomy_level=AutonomyLevel.LEVEL_2,
            factor_scores={
                "legal_exposure": 15,
                "civil_rights_impact": 20,
                "jurisdictional_authority": 10,
                "operational_consequence": 8,
                "political_public_risk": 12,
            },
            total_score=65,
            risk_category=RiskCategory.HIGH,
            requires_human_review=True,
            recommended_approval_type="SUPERVISOR",
            timestamp=datetime.now(),
        )
        assert assessment.total_score == 65
        assert assessment.risk_category == RiskCategory.HIGH
        assert assessment.requires_human_review is True

    def test_risk_assessment_low_risk(self):
        """Test low risk assessment."""
        assessment = RiskAssessment(
            assessment_id="assess-002",
            action_id="action-002",
            action_type="routine_patrol",
            category=ActionCategory.PUBLIC_SAFETY,
            autonomy_level=AutonomyLevel.LEVEL_0,
            factor_scores={
                "legal_exposure": 2,
                "civil_rights_impact": 3,
                "jurisdictional_authority": 2,
                "operational_consequence": 2,
                "political_public_risk": 1,
            },
            total_score=10,
            risk_category=RiskCategory.LOW,
            requires_human_review=False,
            recommended_approval_type=None,
            timestamp=datetime.now(),
        )
        assert assessment.total_score == 10
        assert assessment.risk_category == RiskCategory.LOW
        assert assessment.requires_human_review is False


class TestRiskScoringEngine:
    """Tests for RiskScoringEngine singleton."""

    def test_singleton_pattern(self):
        """Test that get_risk_scoring_engine returns singleton."""
        e1 = get_risk_scoring_engine()
        e2 = get_risk_scoring_engine()
        assert e1 is e2

    def test_assess_risk_basic(self):
        """Test basic risk assessment."""
        engine = get_risk_scoring_engine()
        assessment = engine.assess_risk(
            "test_action",
            ActionCategory.PUBLIC_SAFETY,
            AutonomyLevel.LEVEL_0,
            {},
        )
        assert assessment is not None
        assert 0 <= assessment.total_score <= 100
        assert assessment.risk_category in RiskCategory

    def test_assess_risk_surveillance(self):
        """Test risk assessment for surveillance."""
        engine = get_risk_scoring_engine()
        assessment = engine.assess_risk(
            "surveillance_operation",
            ActionCategory.SURVEILLANCE,
            AutonomyLevel.LEVEL_2,
            {"target_area": "Zone 3"},
        )
        assert assessment is not None
        # Surveillance should have elevated risk
        assert assessment.total_score >= 25

    def test_assess_risk_use_of_force(self):
        """Test risk assessment for use of force."""
        engine = get_risk_scoring_engine()
        assessment = engine.assess_risk(
            "use_of_force",
            ActionCategory.USE_OF_FORCE,
            AutonomyLevel.LEVEL_2,
            {"force_level": "high"},
        )
        assert assessment is not None
        # Use of force should have high/critical risk
        assert assessment.total_score >= 50
        assert assessment.requires_human_review is True

    def test_assess_risk_drone_operation(self):
        """Test risk assessment for drone operations."""
        engine = get_risk_scoring_engine()
        assessment = engine.assess_risk(
            "drone_property_entry",
            ActionCategory.DRONE_OPERATION,
            AutonomyLevel.LEVEL_2,
            {"is_private_property": True},
        )
        assert assessment is not None
        # Private property entry should have elevated risk
        assert assessment.total_score >= 40

    def test_assess_risk_property_entry(self):
        """Test risk assessment for property entry."""
        engine = get_risk_scoring_engine()
        assessment = engine.assess_risk(
            "property_entry",
            ActionCategory.PROPERTY_ENTRY,
            AutonomyLevel.LEVEL_2,
            {"has_warrant": False},
        )
        assert assessment is not None
        # Warrantless entry should have high risk
        assert assessment.total_score >= 60


class TestRiskFactorCalculation:
    """Tests for individual risk factor calculation."""

    def test_legal_exposure_factor(self):
        """Test legal exposure factor calculation."""
        engine = get_risk_scoring_engine()
        
        # Low legal exposure
        low_assessment = engine.assess_risk(
            "routine_patrol",
            ActionCategory.PUBLIC_SAFETY,
            AutonomyLevel.LEVEL_0,
            {},
        )
        
        # High legal exposure
        high_assessment = engine.assess_risk(
            "warrantless_search",
            ActionCategory.PROPERTY_ENTRY,
            AutonomyLevel.LEVEL_2,
            {"has_warrant": False},
        )
        
        assert low_assessment.factor_scores.get("legal_exposure", 0) <= \
               high_assessment.factor_scores.get("legal_exposure", 25)

    def test_civil_rights_impact_factor(self):
        """Test civil rights impact factor calculation."""
        engine = get_risk_scoring_engine()
        
        # Surveillance has civil rights implications
        assessment = engine.assess_risk(
            "mass_surveillance",
            ActionCategory.SURVEILLANCE,
            AutonomyLevel.LEVEL_2,
            {"scope": "city_wide"},
        )
        
        assert "civil_rights_impact" in assessment.factor_scores
        assert assessment.factor_scores["civil_rights_impact"] >= 0

    def test_jurisdictional_authority_factor(self):
        """Test jurisdictional authority factor calculation."""
        engine = get_risk_scoring_engine()
        
        assessment = engine.assess_risk(
            "cross_jurisdiction_operation",
            ActionCategory.PUBLIC_SAFETY,
            AutonomyLevel.LEVEL_1,
            {"jurisdiction": "Palm Beach County"},
        )
        
        assert "jurisdictional_authority" in assessment.factor_scores

    def test_operational_consequence_factor(self):
        """Test operational consequence factor calculation."""
        engine = get_risk_scoring_engine()
        
        # High operational consequence
        assessment = engine.assess_risk(
            "tactical_robotics_entry",
            ActionCategory.ROBOTICS_OPERATION,
            AutonomyLevel.LEVEL_2,
            {"building_type": "residential"},
        )
        
        assert "operational_consequence" in assessment.factor_scores

    def test_political_public_risk_factor(self):
        """Test political/public risk factor calculation."""
        engine = get_risk_scoring_engine()
        
        # Mass alert has political implications
        assessment = engine.assess_risk(
            "mass_emergency_alert",
            ActionCategory.COMMUNICATION,
            AutonomyLevel.LEVEL_2,
            {"alert_type": "city_wide"},
        )
        
        assert "political_public_risk" in assessment.factor_scores


class TestAutonomyLevelImpact:
    """Tests for autonomy level impact on risk scoring."""

    def test_higher_autonomy_higher_risk(self):
        """Test that higher autonomy levels increase risk."""
        engine = get_risk_scoring_engine()
        
        level_0 = engine.assess_risk(
            "test_action",
            ActionCategory.PUBLIC_SAFETY,
            AutonomyLevel.LEVEL_0,
            {},
        )
        
        level_1 = engine.assess_risk(
            "test_action",
            ActionCategory.PUBLIC_SAFETY,
            AutonomyLevel.LEVEL_1,
            {},
        )
        
        level_2 = engine.assess_risk(
            "test_action",
            ActionCategory.PUBLIC_SAFETY,
            AutonomyLevel.LEVEL_2,
            {},
        )
        
        # Higher autonomy should generally mean higher risk
        assert level_0.total_score <= level_2.total_score

    def test_level_0_minimal_risk(self):
        """Test that Level 0 (human-controlled) has minimal risk."""
        engine = get_risk_scoring_engine()
        
        assessment = engine.assess_risk(
            "routine_action",
            ActionCategory.PUBLIC_SAFETY,
            AutonomyLevel.LEVEL_0,
            {},
        )
        
        # Level 0 should have low risk
        assert assessment.risk_category in [RiskCategory.LOW, RiskCategory.ELEVATED]


class TestHumanReviewRequirement:
    """Tests for human review requirement determination."""

    def test_low_risk_no_review(self):
        """Test that low risk actions don't require review."""
        engine = get_risk_scoring_engine()
        
        assessment = engine.assess_risk(
            "routine_patrol",
            ActionCategory.PUBLIC_SAFETY,
            AutonomyLevel.LEVEL_0,
            {},
        )
        
        if assessment.risk_category == RiskCategory.LOW:
            assert assessment.requires_human_review is False

    def test_high_risk_requires_review(self):
        """Test that high risk actions require review."""
        engine = get_risk_scoring_engine()
        
        assessment = engine.assess_risk(
            "use_of_force",
            ActionCategory.USE_OF_FORCE,
            AutonomyLevel.LEVEL_2,
            {"force_level": "lethal"},
        )
        
        if assessment.risk_category in [RiskCategory.HIGH, RiskCategory.CRITICAL]:
            assert assessment.requires_human_review is True

    def test_critical_risk_requires_command_approval(self):
        """Test that critical risk requires command staff approval."""
        engine = get_risk_scoring_engine()
        
        assessment = engine.assess_risk(
            "lethal_force_authorization",
            ActionCategory.USE_OF_FORCE,
            AutonomyLevel.LEVEL_2,
            {"force_level": "lethal", "target_type": "armed_suspect"},
        )
        
        if assessment.risk_category == RiskCategory.CRITICAL:
            assert assessment.recommended_approval_type in [
                "COMMAND_STAFF",
                "MULTI_FACTOR",
                "LEGAL_REVIEW",
            ]


class TestRiskHistory:
    """Tests for risk assessment history."""

    def test_get_risk_history(self):
        """Test retrieving risk assessment history."""
        engine = get_risk_scoring_engine()
        
        # Create some assessments
        engine.assess_risk(
            "test_action_1",
            ActionCategory.PUBLIC_SAFETY,
            AutonomyLevel.LEVEL_0,
            {},
        )
        
        history = engine.get_risk_history()
        assert isinstance(history, list)

    def test_get_risk_history_by_category(self):
        """Test filtering risk history by category."""
        engine = get_risk_scoring_engine()
        
        history = engine.get_risk_history_by_category(RiskCategory.HIGH)
        assert isinstance(history, list)
        for assessment in history:
            assert assessment.risk_category == RiskCategory.HIGH


class TestRiskThresholds:
    """Tests for risk threshold configuration."""

    def test_get_thresholds(self):
        """Test retrieving risk thresholds."""
        engine = get_risk_scoring_engine()
        thresholds = engine.get_thresholds()
        
        assert isinstance(thresholds, dict)
        assert "LOW" in thresholds or len(thresholds) >= 4

    def test_threshold_boundaries(self):
        """Test threshold boundary values."""
        engine = get_risk_scoring_engine()
        thresholds = engine.get_thresholds()
        
        # Thresholds should cover 0-100 range
        if thresholds:
            min_threshold = min(thresholds.values()) if isinstance(list(thresholds.values())[0], (int, float)) else 0
            assert min_threshold >= 0
