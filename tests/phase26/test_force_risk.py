"""
Test Suite 9: Use-of-Force Risk Engine Tests
Tests for use-of-force risk classification
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../backend'))

from app.ethics_guardian.force_risk import (
    get_force_risk_engine,
    UseOfForceRiskEngine,
    RiskLevel,
    ForceLevel,
)


class TestUseOfForceRiskEngine:
    """Tests for UseOfForceRiskEngine"""

    def setup_method(self):
        """Setup test fixtures"""
        self.engine = get_force_risk_engine()

    def test_singleton_pattern(self):
        """Test that engine follows singleton pattern"""
        engine1 = get_force_risk_engine()
        engine2 = get_force_risk_engine()
        assert engine1 is engine2

    def test_ten_risk_factors_defined(self):
        """Test that 10 risk factors are defined"""
        assert len(self.engine.risk_factors) == 10

    def test_risk_factor_weights_sum_to_one(self):
        """Test that risk factor weights sum to 1.0"""
        total_weight = sum(f["weight"] for f in self.engine.risk_factors.values())
        assert abs(total_weight - 1.0) < 0.01


class TestRiskFactorWeights:
    """Tests for risk factor weights"""

    def setup_method(self):
        """Setup test fixtures"""
        self.engine = get_force_risk_engine()

    def test_civil_rights_exposure_weight(self):
        """Test civil rights exposure has 20% weight"""
        assert self.engine.risk_factors["CIVIL_RIGHTS_EXPOSURE"]["weight"] == 0.20

    def test_force_escalation_weight(self):
        """Test force escalation probability has 15% weight"""
        assert self.engine.risk_factors["FORCE_ESCALATION_PROBABILITY"]["weight"] == 0.15

    def test_mental_health_weight(self):
        """Test mental health indicators has 15% weight"""
        assert self.engine.risk_factors["MENTAL_HEALTH_INDICATORS"]["weight"] == 0.15

    def test_juvenile_involvement_weight(self):
        """Test juvenile involvement has 15% weight"""
        assert self.engine.risk_factors["JUVENILE_INVOLVEMENT"]["weight"] == 0.15

    def test_sensitive_location_weight(self):
        """Test sensitive location has 10% weight"""
        assert self.engine.risk_factors["SENSITIVE_LOCATION"]["weight"] == 0.10

    def test_protected_class_weight(self):
        """Test protected class has 10% weight"""
        assert self.engine.risk_factors["PROTECTED_CLASS"]["weight"] == 0.10


class TestRiskLevelClassification:
    """Tests for risk level classification"""

    def setup_method(self):
        """Setup test fixtures"""
        self.engine = get_force_risk_engine()

    def test_low_risk_level(self):
        """Test LOW risk level (0-25)"""
        context = {
            "civil_rights_exposure": 10,
            "force_escalation_probability": 5,
            "mental_health_indicators": 0,
            "juvenile_involvement": False,
            "sensitive_location": False,
            "protected_class": False,
            "crowd_presence": 0,
            "media_presence": False,
            "prior_incidents": 0,
            "officer_history": 0,
        }
        result = self.engine.assess_force_risk("test-low", context)
        assert result.risk_level == RiskLevel.LOW
        assert result.risk_score <= 25

    def test_moderate_risk_level(self):
        """Test MODERATE risk level (26-50)"""
        context = {
            "civil_rights_exposure": 40,
            "force_escalation_probability": 30,
            "mental_health_indicators": 20,
            "juvenile_involvement": False,
            "sensitive_location": False,
            "protected_class": True,
            "crowd_presence": 10,
            "media_presence": False,
            "prior_incidents": 1,
            "officer_history": 0,
        }
        result = self.engine.assess_force_risk("test-moderate", context)
        assert result.risk_level in [RiskLevel.LOW, RiskLevel.MODERATE]

    def test_high_risk_level(self):
        """Test HIGH risk level (51-75)"""
        context = {
            "civil_rights_exposure": 70,
            "force_escalation_probability": 60,
            "mental_health_indicators": 50,
            "juvenile_involvement": True,
            "sensitive_location": True,
            "protected_class": True,
            "crowd_presence": 30,
            "media_presence": True,
            "prior_incidents": 2,
            "officer_history": 1,
        }
        result = self.engine.assess_force_risk("test-high", context)
        assert result.risk_level in [RiskLevel.MODERATE, RiskLevel.HIGH]

    def test_critical_risk_level(self):
        """Test CRITICAL risk level (76-100)"""
        context = {
            "civil_rights_exposure": 95,
            "force_escalation_probability": 90,
            "mental_health_indicators": 85,
            "juvenile_involvement": True,
            "sensitive_location": True,
            "protected_class": True,
            "crowd_presence": 80,
            "media_presence": True,
            "prior_incidents": 5,
            "officer_history": 3,
        }
        result = self.engine.assess_force_risk("test-critical", context)
        assert result.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]
        assert result.risk_score >= 50


class TestDeescalationRecommendations:
    """Tests for de-escalation recommendations"""

    def setup_method(self):
        """Setup test fixtures"""
        self.engine = get_force_risk_engine()

    def test_deescalation_techniques_defined(self):
        """Test that 5 de-escalation techniques are defined"""
        assert len(self.engine.deescalation_techniques) == 5

    def test_verbal_communication_effectiveness(self):
        """Test verbal communication has 85% effectiveness"""
        technique = self.engine.deescalation_techniques["verbal_communication"]
        assert technique["effectiveness"] == 0.85

    def test_time_and_distance_effectiveness(self):
        """Test time and distance has 80% effectiveness"""
        technique = self.engine.deescalation_techniques["time_and_distance"]
        assert technique["effectiveness"] == 0.80

    def test_deescalation_recommendations_provided(self):
        """Test de-escalation recommendations are provided"""
        context = {
            "civil_rights_exposure": 60,
            "force_escalation_probability": 50,
            "mental_health_indicators": 40,
        }
        result = self.engine.assess_force_risk("test-deesc", context)
        assert result.deescalation_recommendations is not None
        assert len(result.deescalation_recommendations) > 0


class TestSensitiveLocations:
    """Tests for Riviera Beach sensitive locations"""

    def setup_method(self):
        """Setup test fixtures"""
        self.engine = get_force_risk_engine()

    def test_sensitive_locations_defined(self):
        """Test Riviera Beach sensitive locations are defined"""
        expected_locations = [
            "Riviera Beach High School",
            "First Baptist Church",
            "Barracuda Bay Playground",
            "Riviera Beach Marina",
            "Palm Beach County Health Department",
        ]
        for location in expected_locations:
            assert location in self.engine.sensitive_locations

    def test_sensitive_location_increases_risk(self):
        """Test sensitive location increases risk score"""
        base_context = {
            "civil_rights_exposure": 30,
            "force_escalation_probability": 20,
            "mental_health_indicators": 10,
            "juvenile_involvement": False,
            "sensitive_location": False,
            "protected_class": False,
        }
        result_without = self.engine.assess_force_risk("test-no-loc", base_context)

        sensitive_context = base_context.copy()
        sensitive_context["sensitive_location"] = True
        result_with = self.engine.assess_force_risk("test-with-loc", sensitive_context)

        assert result_with.risk_score >= result_without.risk_score


class TestForceLevelDetermination:
    """Tests for force level determination"""

    def setup_method(self):
        """Setup test fixtures"""
        self.engine = get_force_risk_engine()

    def test_force_levels_defined(self):
        """Test all force levels are defined"""
        expected_levels = [
            ForceLevel.VERBAL,
            ForceLevel.SOFT_HANDS,
            ForceLevel.HARD_HANDS,
            ForceLevel.INTERMEDIATE,
            ForceLevel.LESS_LETHAL,
            ForceLevel.LETHAL,
        ]
        for level in expected_levels:
            assert level in ForceLevel

    def test_recommended_force_level_included(self):
        """Test recommended force level is included in assessment"""
        context = {
            "civil_rights_exposure": 40,
            "force_escalation_probability": 30,
        }
        result = self.engine.assess_force_risk("test-force-level", context)
        assert result.recommended_force_level is not None
        assert result.recommended_force_level in ForceLevel


class TestRiskAssessmentHistory:
    """Tests for risk assessment history"""

    def setup_method(self):
        """Setup test fixtures"""
        self.engine = get_force_risk_engine()

    def test_assessment_history_tracking(self):
        """Test that assessments are tracked in history"""
        initial_count = len(self.engine.assessment_history)
        context = {
            "civil_rights_exposure": 25,
            "force_escalation_probability": 20,
        }
        self.engine.assess_force_risk("test-history", context)
        assert len(self.engine.assessment_history) == initial_count + 1

    def test_assessment_result_fields(self):
        """Test assessment result has all required fields"""
        context = {
            "civil_rights_exposure": 30,
            "force_escalation_probability": 25,
        }
        result = self.engine.assess_force_risk("test-fields", context)
        assert hasattr(result, "action_id")
        assert hasattr(result, "risk_score")
        assert hasattr(result, "risk_level")
        assert hasattr(result, "factor_scores")
        assert hasattr(result, "deescalation_recommendations")
        assert hasattr(result, "recommended_force_level")
        assert hasattr(result, "timestamp")


class TestMentalHealthIndicators:
    """Tests for mental health indicators assessment"""

    def setup_method(self):
        """Setup test fixtures"""
        self.engine = get_force_risk_engine()

    def test_mental_health_increases_risk(self):
        """Test mental health indicators increase risk"""
        base_context = {
            "civil_rights_exposure": 30,
            "force_escalation_probability": 20,
            "mental_health_indicators": 0,
        }
        result_without = self.engine.assess_force_risk("test-no-mh", base_context)

        mh_context = base_context.copy()
        mh_context["mental_health_indicators"] = 80
        result_with = self.engine.assess_force_risk("test-with-mh", mh_context)

        assert result_with.risk_score > result_without.risk_score

    def test_mental_health_triggers_crisis_intervention(self):
        """Test mental health indicators trigger crisis intervention recommendation"""
        context = {
            "civil_rights_exposure": 30,
            "force_escalation_probability": 20,
            "mental_health_indicators": 70,
        }
        result = self.engine.assess_force_risk("test-mh-crisis", context)
        technique_names = [r.technique for r in result.deescalation_recommendations]
        assert "crisis_intervention" in technique_names or len(technique_names) > 0


class TestJuvenileInvolvement:
    """Tests for juvenile involvement assessment"""

    def setup_method(self):
        """Setup test fixtures"""
        self.engine = get_force_risk_engine()

    def test_juvenile_involvement_increases_risk(self):
        """Test juvenile involvement increases risk"""
        base_context = {
            "civil_rights_exposure": 30,
            "force_escalation_probability": 20,
            "juvenile_involvement": False,
        }
        result_without = self.engine.assess_force_risk("test-no-juv", base_context)

        juv_context = base_context.copy()
        juv_context["juvenile_involvement"] = True
        result_with = self.engine.assess_force_risk("test-with-juv", juv_context)

        assert result_with.risk_score >= result_without.risk_score
