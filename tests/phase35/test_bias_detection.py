"""
Test Suite: Bias Detection

Phase 35: AI Moral Compass & Societal Ethics Reasoning Engine
Tests for bias detection and prevention.
"""

import pytest

from backend.app.moral_compass.fairness_analyzer import (
    FairnessAnalyzer,
    BiasType,
    DisparityLevel,
    ProtectedAttribute,
    BiasDetection,
)
from backend.app.moral_compass.ethical_guardrails import (
    EthicalGuardrails,
    GuardrailType,
)


class TestBiasTypes:
    """Tests for bias type detection."""

    def test_selection_bias_detection(self):
        analyzer = FairnessAnalyzer()
        assessment = analyzer.assess_fairness(
            action_type="targeting",
            requester_id="system_001",
            historical_data={"selection_bias": True},
        )
        bias_detections = [b for b in assessment.bias_detections if b.bias_type == BiasType.SELECTION]
        assert len(bias_detections) > 0

    def test_historical_bias_detection(self):
        analyzer = FairnessAnalyzer()
        assessment = analyzer.assess_fairness(
            action_type="risk_scoring",
            requester_id="system_002",
            historical_data={"historical_discrimination": True},
        )
        bias_detections = [b for b in assessment.bias_detections if b.bias_type == BiasType.HISTORICAL]
        assert len(bias_detections) > 0

    def test_algorithmic_bias_detection(self):
        analyzer = FairnessAnalyzer()
        assessment = analyzer.assess_fairness(
            action_type="prediction",
            requester_id="system_003",
            historical_data={"algorithmic_disparity": True},
        )
        bias_detections = [b for b in assessment.bias_detections if b.bias_type == BiasType.ALGORITHMIC]
        assert len(bias_detections) > 0

    def test_representation_bias_detection(self):
        analyzer = FairnessAnalyzer()
        assessment = analyzer.assess_fairness(
            action_type="training",
            requester_id="system_004",
            historical_data={"underrepresentation": True},
        )
        bias_detections = [b for b in assessment.bias_detections if b.bias_type == BiasType.REPRESENTATION]
        assert len(bias_detections) > 0


class TestBiasDetectionDataclass:
    """Tests for BiasDetection dataclass."""

    def test_bias_detection_creation(self):
        detection = BiasDetection(
            bias_type=BiasType.HISTORICAL,
            detected=True,
            confidence=0.85,
            source="Historical arrest data",
            impact="May perpetuate racial disparities",
            mitigation_strategies=["Review data", "Apply correction factors"],
        )
        assert detection.detected is True
        assert detection.confidence == 0.85
        assert len(detection.mitigation_strategies) == 2

    def test_bias_detection_not_detected(self):
        detection = BiasDetection(
            bias_type=BiasType.SELECTION,
            detected=False,
            confidence=0.2,
            source="Random sampling",
            impact="Low risk",
            mitigation_strategies=[],
        )
        assert detection.detected is False
        assert detection.confidence == 0.2


class TestBiasPreventionGuardrails:
    """Tests for bias prevention guardrails."""

    def test_bias_prevention_rule_exists(self):
        guardrails = EthicalGuardrails()
        bias_rules = [
            r for r in guardrails.rules.values()
            if r.guardrail_type == GuardrailType.BIAS_PREVENTION
        ]
        assert len(bias_rules) > 0

    def test_prevent_bias_reinforcement(self):
        guardrails = EthicalGuardrails()
        result = guardrails.prevent_bias_reinforcement(
            action_type="predictive_targeting",
            historical_data={
                "demographic_disparity": True,
                "repeat_targeting": True,
            },
        )
        assert result["bias_risks_identified"] is True
        assert len(result["bias_risks"]) > 0
        assert result["mitigation_required"] is True

    def test_no_bias_reinforcement(self):
        guardrails = EthicalGuardrails()
        result = guardrails.prevent_bias_reinforcement(
            action_type="patrol",
            historical_data={},
        )
        assert result["bias_risks_identified"] is False


class TestDisparityDetection:
    """Tests for disparity detection."""

    def test_detect_demographic_disparity(self):
        analyzer = FairnessAnalyzer()
        result = analyzer.detect_real_time_disparity(
            action_type="arrests",
            current_data={
                "distribution": {
                    "group_a": 80,
                    "group_b": 20,
                },
            },
            baseline_data={
                "distribution": {
                    "group_a": 50,
                    "group_b": 50,
                },
            },
        )
        assert result["disparities_detected"] is True

    def test_detect_geographic_disparity(self):
        analyzer = FairnessAnalyzer()
        result = analyzer.detect_real_time_disparity(
            action_type="patrols",
            current_data={
                "distribution": {
                    "north": 100,
                    "south": 10,
                },
            },
            baseline_data={
                "distribution": {
                    "north": 50,
                    "south": 50,
                },
            },
        )
        assert result["disparities_detected"] is True

    def test_no_disparity(self):
        analyzer = FairnessAnalyzer()
        result = analyzer.detect_real_time_disparity(
            action_type="responses",
            current_data={
                "distribution": {
                    "area_a": 50,
                    "area_b": 50,
                },
            },
            baseline_data={
                "distribution": {
                    "area_a": 50,
                    "area_b": 50,
                },
            },
        )
        assert result["disparities_detected"] is False


class TestDisparityLevels:
    """Tests for disparity level classification."""

    def test_disparity_levels_exist(self):
        levels = [
            DisparityLevel.NONE,
            DisparityLevel.MINIMAL,
            DisparityLevel.LOW,
            DisparityLevel.MODERATE,
            DisparityLevel.HIGH,
            DisparityLevel.SEVERE,
        ]
        assert len(levels) == 6


class TestProtectedAttributes:
    """Tests for protected attribute handling."""

    def test_protected_attributes_exist(self):
        attributes = [
            ProtectedAttribute.RACE,
            ProtectedAttribute.ETHNICITY,
            ProtectedAttribute.GENDER,
            ProtectedAttribute.AGE,
            ProtectedAttribute.RELIGION,
            ProtectedAttribute.DISABILITY,
            ProtectedAttribute.NATIONAL_ORIGIN,
            ProtectedAttribute.SOCIOECONOMIC,
            ProtectedAttribute.GEOGRAPHIC,
        ]
        assert len(attributes) == 9


class TestBiasIntegration:
    """Integration tests for bias detection."""

    def test_bias_detection_with_moral_assessment(self):
        from backend.app.moral_compass.moral_engine import MoralEngine
        
        engine = MoralEngine()
        assessment = engine.assess(
            action_type="predictive_targeting",
            action_description="Target area based on historical data",
            requester_id="system_001",
            context={"historical_bias_present": True},
        )
        assert assessment is not None

    def test_bias_detection_with_guardrails(self):
        guardrails = EthicalGuardrails()
        analyzer = FairnessAnalyzer()
        
        fairness_assessment = analyzer.assess_fairness(
            action_type="risk_scoring",
            requester_id="system_002",
            historical_data={"demographic_disparity": True},
        )
        
        guardrail_assessment = guardrails.check_action(
            action_type="risk_scoring",
            action_description="Score individuals based on algorithm",
            requester_id="system_002",
            context={"bias_detected": any(b.detected for b in fairness_assessment.bias_detections)},
        )
        
        assert guardrail_assessment is not None
