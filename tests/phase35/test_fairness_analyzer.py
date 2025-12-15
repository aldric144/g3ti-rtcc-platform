"""
Test Suite: Fairness & Bias Analyzer

Phase 35: AI Moral Compass & Societal Ethics Reasoning Engine
Tests for fairness assessment and bias detection.
"""

import pytest
from datetime import datetime

from backend.app.moral_compass.fairness_analyzer import (
    FairnessAnalyzer,
    FairnessMetric,
    BiasType,
    DisparityLevel,
    ProtectedAttribute,
    FairnessScore,
    DisparityAlert,
    BiasDetection,
    FairnessAssessment,
)


class TestFairnessMetric:
    """Tests for FairnessMetric enum."""

    def test_metrics_exist(self):
        metrics = [
            FairnessMetric.DEMOGRAPHIC_PARITY,
            FairnessMetric.EQUALIZED_ODDS,
            FairnessMetric.EQUAL_OPPORTUNITY,
            FairnessMetric.PREDICTIVE_PARITY,
            FairnessMetric.CALIBRATION,
            FairnessMetric.INDIVIDUAL_FAIRNESS,
            FairnessMetric.COUNTERFACTUAL_FAIRNESS,
        ]
        assert len(metrics) == 7


class TestBiasType:
    """Tests for BiasType enum."""

    def test_bias_types_exist(self):
        types = [
            BiasType.SELECTION,
            BiasType.MEASUREMENT,
            BiasType.ALGORITHMIC,
            BiasType.HISTORICAL,
            BiasType.REPRESENTATION,
            BiasType.AGGREGATION,
            BiasType.EVALUATION,
            BiasType.DEPLOYMENT,
        ]
        assert len(types) == 8


class TestFairnessAnalyzer:
    """Tests for FairnessAnalyzer singleton."""

    def test_singleton_pattern(self):
        analyzer1 = FairnessAnalyzer()
        analyzer2 = FairnessAnalyzer()
        assert analyzer1 is analyzer2

    def test_initialization(self):
        analyzer = FairnessAnalyzer()
        assert analyzer._initialized is True

    def test_assess_fairness_basic(self):
        analyzer = FairnessAnalyzer()
        assessment = analyzer.assess_fairness(
            action_type="patrol",
            requester_id="officer_001",
        )
        assert assessment is not None
        assert assessment.assessment_id is not None
        assert assessment.overall_fairness_score >= 0
        assert assessment.overall_fairness_score <= 1

    def test_assess_fairness_with_disparity(self):
        analyzer = FairnessAnalyzer()
        assessment = analyzer.assess_fairness(
            action_type="targeting",
            requester_id="system_001",
            historical_data={"demographic_disparity": True},
        )
        assert assessment is not None
        assert len(assessment.disparity_alerts) > 0

    def test_assess_fairness_with_bias(self):
        analyzer = FairnessAnalyzer()
        assessment = analyzer.assess_fairness(
            action_type="risk_scoring",
            requester_id="system_002",
            historical_data={"historical_discrimination": True},
        )
        assert assessment is not None
        assert any(b.detected for b in assessment.bias_detections)

    def test_detect_real_time_disparity(self):
        analyzer = FairnessAnalyzer()
        result = analyzer.detect_real_time_disparity(
            action_type="arrests",
            current_data={"distribution": {"area_a": 100, "area_b": 20}},
            baseline_data={"distribution": {"area_a": 50, "area_b": 50}},
        )
        assert "disparities_detected" in result
        assert result["disparities_detected"] is True

    def test_detect_no_disparity(self):
        analyzer = FairnessAnalyzer()
        result = analyzer.detect_real_time_disparity(
            action_type="patrols",
            current_data={"distribution": {"area_a": 50, "area_b": 50}},
            baseline_data={"distribution": {"area_a": 50, "area_b": 50}},
        )
        assert result["disparities_detected"] is False

    def test_balance_geographic_fairness(self):
        analyzer = FairnessAnalyzer()
        result = analyzer.balance_geographic_fairness(
            action_type="resource_allocation",
            geographic_data={"areas": {"north": 100, "south": 20, "east": 50, "west": 50}},
        )
        assert "balanced" in result
        assert "imbalanced_areas" in result

    def test_identify_harmful_patterns(self):
        analyzer = FairnessAnalyzer()
        result = analyzer.identify_harmful_patterns(
            historical_data={
                "repeat_targeting": True,
                "demographic_concentration": True,
            },
        )
        assert result["harmful_patterns_found"] is True
        assert result["overall_risk"] == "high"

    def test_identify_no_harmful_patterns(self):
        analyzer = FairnessAnalyzer()
        result = analyzer.identify_harmful_patterns(
            historical_data={},
        )
        assert result["harmful_patterns_found"] is False

    def test_normalize_outputs(self):
        analyzer = FairnessAnalyzer()
        result = analyzer.normalize_outputs(
            outputs={"scores": {"group_a": 0.9, "group_b": 0.3}},
            fairness_constraints={"max_disparity": 0.2},
        )
        assert "normalized_outputs" in result
        assert "adjustments_made" in result

    def test_get_active_alerts(self):
        analyzer = FairnessAnalyzer()
        alerts = analyzer.get_active_alerts()
        assert isinstance(alerts, list)

    def test_acknowledge_alert(self):
        analyzer = FairnessAnalyzer()
        analyzer.assess_fairness(
            action_type="test",
            requester_id="test",
            historical_data={"geographic_disparity": True},
        )
        alerts = analyzer.get_active_alerts()
        if alerts:
            result = analyzer.acknowledge_alert(alerts[0].alert_id)
            assert result is True

    def test_get_statistics(self):
        analyzer = FairnessAnalyzer()
        stats = analyzer.get_statistics()
        assert "total_assessments" in stats
        assert "passed" in stats
        assert "failed" in stats
        assert "bias_detected" in stats


class TestFairnessScore:
    """Tests for FairnessScore dataclass."""

    def test_score_creation(self):
        score = FairnessScore(
            metric=FairnessMetric.DEMOGRAPHIC_PARITY,
            score=0.85,
            threshold=0.8,
            passed=True,
            details="Test score",
        )
        assert score.score == 0.85
        assert score.passed is True

    def test_score_to_dict(self):
        score = FairnessScore(
            metric=FairnessMetric.EQUALIZED_ODDS,
            score=0.75,
            threshold=0.8,
            passed=False,
            details="Below threshold",
        )
        data = score.to_dict()
        assert data["metric"] == "equalized_odds"
        assert data["passed"] is False


class TestDisparityAlert:
    """Tests for DisparityAlert dataclass."""

    def test_alert_creation(self):
        alert = DisparityAlert(
            disparity_type="geographic",
            protected_attribute=ProtectedAttribute.GEOGRAPHIC,
            disparity_level=DisparityLevel.MODERATE,
            affected_groups=["area_a"],
            disparity_ratio=1.5,
            description="Geographic concentration detected",
        )
        assert alert.alert_id is not None
        assert alert.disparity_level == DisparityLevel.MODERATE

    def test_alert_to_dict(self):
        alert = DisparityAlert(
            disparity_type="demographic",
            protected_attribute=ProtectedAttribute.RACE,
            disparity_level=DisparityLevel.HIGH,
            affected_groups=["group_a"],
            disparity_ratio=2.0,
            description="Demographic disparity",
        )
        data = alert.to_dict()
        assert data["disparity_level"] == "high"


class TestBiasDetection:
    """Tests for BiasDetection dataclass."""

    def test_detection_creation(self):
        detection = BiasDetection(
            bias_type=BiasType.HISTORICAL,
            detected=True,
            confidence=0.8,
            source="Historical data",
            impact="May perpetuate inequities",
            mitigation_strategies=["Review data", "Apply correction"],
        )
        assert detection.detected is True
        assert detection.confidence == 0.8

    def test_detection_to_dict(self):
        detection = BiasDetection(
            bias_type=BiasType.ALGORITHMIC,
            detected=False,
            confidence=0.3,
            source="Algorithm",
            impact="Low risk",
            mitigation_strategies=[],
        )
        data = detection.to_dict()
        assert data["bias_type"] == "algorithmic"
        assert data["detected"] is False


class TestFairnessAssessment:
    """Tests for FairnessAssessment dataclass."""

    def test_assessment_creation(self):
        assessment = FairnessAssessment(
            action_type="test",
            requester_id="test_user",
        )
        assert assessment.assessment_id is not None
        assert assessment.passed is True

    def test_assessment_hash(self):
        assessment = FairnessAssessment(
            action_type="test",
            requester_id="test_user",
            overall_fairness_score=0.9,
        )
        assert assessment.assessment_hash is not None
        assert len(assessment.assessment_hash) == 16
