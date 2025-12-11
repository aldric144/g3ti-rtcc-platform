"""
Test Suite 1: Bias Detection Engine Tests
Tests for bias detection and fairness metrics
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../backend'))

from app.ethics_guardian.bias_detection import (
    get_bias_detection_engine,
    BiasDetectionEngine,
    BiasStatus,
    AnalysisType,
)


class TestBiasDetectionEngine:
    """Tests for BiasDetectionEngine"""

    def setup_method(self):
        """Setup test fixtures"""
        self.engine = get_bias_detection_engine()

    def test_singleton_pattern(self):
        """Test that engine follows singleton pattern"""
        engine1 = get_bias_detection_engine()
        engine2 = get_bias_detection_engine()
        assert engine1 is engine2

    def test_riviera_beach_demographics(self):
        """Test Riviera Beach demographic baselines are correct"""
        demographics = self.engine.riviera_beach_demographics
        assert demographics["Black"] == 0.66
        assert demographics["White"] == 0.22
        assert demographics["Hispanic"] == 0.08
        assert demographics["Asian"] == 0.02
        assert demographics["Other"] == 0.02
        total = sum(demographics.values())
        assert abs(total - 1.0) < 0.01

    def test_disparate_impact_ratio_pass(self):
        """Test disparate impact ratio calculation - passing case"""
        data = {
            "demographic_outcomes": {
                "Black": {"positive": 85, "negative": 15},
                "White": {"positive": 90, "negative": 10},
            },
            "reference_group": "White",
        }
        result = self.engine.analyze_for_bias(AnalysisType.PREDICTIVE_AI, data)
        dir_metric = next(
            (m for m in result.metrics if m.name == "disparate_impact_ratio"), None
        )
        assert dir_metric is not None
        assert dir_metric.value >= 0.8

    def test_disparate_impact_ratio_fail(self):
        """Test disparate impact ratio calculation - failing case"""
        data = {
            "demographic_outcomes": {
                "Black": {"positive": 50, "negative": 50},
                "White": {"positive": 90, "negative": 10},
            },
            "reference_group": "White",
        }
        result = self.engine.analyze_for_bias(AnalysisType.PREDICTIVE_AI, data)
        dir_metric = next(
            (m for m in result.metrics if m.name == "disparate_impact_ratio"), None
        )
        assert dir_metric is not None
        assert dir_metric.value < 0.8

    def test_demographic_parity_calculation(self):
        """Test demographic parity calculation"""
        data = {
            "demographic_outcomes": {
                "Black": {"positive": 50, "negative": 50},
                "White": {"positive": 50, "negative": 50},
            },
            "reference_group": "White",
        }
        result = self.engine.analyze_for_bias(AnalysisType.RISK_SCORE, data)
        dp_metric = next(
            (m for m in result.metrics if m.name == "demographic_parity"), None
        )
        assert dp_metric is not None
        assert dp_metric.value <= 0.1

    def test_equal_opportunity_difference(self):
        """Test equal opportunity difference calculation"""
        data = {
            "demographic_outcomes": {
                "Black": {"positive": 45, "negative": 55},
                "White": {"positive": 50, "negative": 50},
            },
            "reference_group": "White",
        }
        result = self.engine.analyze_for_bias(AnalysisType.PATROL_ROUTING, data)
        eod_metric = next(
            (m for m in result.metrics if m.name == "equal_opportunity_difference"), None
        )
        assert eod_metric is not None

    def test_no_bias_detected_status(self):
        """Test NO_BIAS_DETECTED status for fair data"""
        data = {
            "demographic_outcomes": {
                "Black": {"positive": 88, "negative": 12},
                "White": {"positive": 90, "negative": 10},
                "Hispanic": {"positive": 89, "negative": 11},
            },
            "reference_group": "White",
        }
        result = self.engine.analyze_for_bias(AnalysisType.PREDICTIVE_AI, data)
        assert result.status == BiasStatus.NO_BIAS_DETECTED
        assert result.blocked is False

    def test_bias_detected_blocked_status(self):
        """Test BIAS_DETECTED_BLOCKED status for severely biased data"""
        data = {
            "demographic_outcomes": {
                "Black": {"positive": 30, "negative": 70},
                "White": {"positive": 90, "negative": 10},
            },
            "reference_group": "White",
        }
        result = self.engine.analyze_for_bias(AnalysisType.ENFORCEMENT_RECOMMENDATION, data)
        assert result.status == BiasStatus.BIAS_DETECTED_BLOCKED
        assert result.blocked is True

    def test_possible_bias_flag_review_status(self):
        """Test POSSIBLE_BIAS_FLAG_REVIEW status for marginal bias"""
        data = {
            "demographic_outcomes": {
                "Black": {"positive": 70, "negative": 30},
                "White": {"positive": 85, "negative": 15},
            },
            "reference_group": "White",
        }
        result = self.engine.analyze_for_bias(AnalysisType.SURVEILLANCE_TRIGGER, data)
        assert result.status in [
            BiasStatus.POSSIBLE_BIAS_FLAG_REVIEW,
            BiasStatus.BIAS_DETECTED_BLOCKED,
        ]

    def test_analysis_history_tracking(self):
        """Test that analysis history is tracked"""
        initial_count = len(self.engine.analysis_history)
        data = {
            "demographic_outcomes": {
                "Black": {"positive": 80, "negative": 20},
                "White": {"positive": 80, "negative": 20},
            },
            "reference_group": "White",
        }
        self.engine.analyze_for_bias(AnalysisType.PREDICTIVE_AI, data)
        assert len(self.engine.analysis_history) == initial_count + 1

    def test_model_version_tracking(self):
        """Test model version is tracked in results"""
        data = {
            "demographic_outcomes": {
                "Black": {"positive": 80, "negative": 20},
                "White": {"positive": 80, "negative": 20},
            },
            "reference_group": "White",
        }
        result = self.engine.analyze_for_bias(
            AnalysisType.PREDICTIVE_AI, data, model_version="v2.0.1"
        )
        assert result.model_version == "v2.0.1"

    def test_geographic_scope_tracking(self):
        """Test geographic scope is tracked in results"""
        data = {
            "demographic_outcomes": {
                "Black": {"positive": 80, "negative": 20},
                "White": {"positive": 80, "negative": 20},
            },
            "reference_group": "White",
        }
        result = self.engine.analyze_for_bias(
            AnalysisType.PREDICTIVE_AI, data, geographic_scope="Downtown"
        )
        assert result.geographic_scope == "Downtown"

    def test_confidence_score_range(self):
        """Test confidence score is within valid range"""
        data = {
            "demographic_outcomes": {
                "Black": {"positive": 80, "negative": 20},
                "White": {"positive": 80, "negative": 20},
            },
            "reference_group": "White",
        }
        result = self.engine.analyze_for_bias(AnalysisType.PREDICTIVE_AI, data)
        assert 0.0 <= result.confidence_score <= 1.0

    def test_affected_groups_identification(self):
        """Test affected groups are correctly identified"""
        data = {
            "demographic_outcomes": {
                "Black": {"positive": 50, "negative": 50},
                "White": {"positive": 90, "negative": 10},
                "Hispanic": {"positive": 55, "negative": 45},
            },
            "reference_group": "White",
        }
        result = self.engine.analyze_for_bias(AnalysisType.PREDICTIVE_AI, data)
        assert "Black" in result.affected_groups or "Hispanic" in result.affected_groups

    def test_all_analysis_types(self):
        """Test all analysis types are supported"""
        data = {
            "demographic_outcomes": {
                "Black": {"positive": 80, "negative": 20},
                "White": {"positive": 80, "negative": 20},
            },
            "reference_group": "White",
        }
        for analysis_type in AnalysisType:
            result = self.engine.analyze_for_bias(analysis_type, data)
            assert result is not None
            assert result.analysis_type == analysis_type


class TestFairnessMetrics:
    """Tests for individual fairness metrics"""

    def setup_method(self):
        """Setup test fixtures"""
        self.engine = get_bias_detection_engine()

    def test_five_metrics_calculated(self):
        """Test that all five fairness metrics are calculated"""
        data = {
            "demographic_outcomes": {
                "Black": {"positive": 80, "negative": 20},
                "White": {"positive": 80, "negative": 20},
            },
            "reference_group": "White",
        }
        result = self.engine.analyze_for_bias(AnalysisType.PREDICTIVE_AI, data)
        metric_names = [m.name for m in result.metrics]
        assert "disparate_impact_ratio" in metric_names
        assert "demographic_parity" in metric_names
        assert "equal_opportunity_difference" in metric_names
        assert "predictive_equality" in metric_names
        assert "calibration_fairness" in metric_names

    def test_metric_thresholds(self):
        """Test that metric thresholds are correctly set"""
        data = {
            "demographic_outcomes": {
                "Black": {"positive": 80, "negative": 20},
                "White": {"positive": 80, "negative": 20},
            },
            "reference_group": "White",
        }
        result = self.engine.analyze_for_bias(AnalysisType.PREDICTIVE_AI, data)
        for metric in result.metrics:
            if metric.name == "disparate_impact_ratio":
                assert metric.threshold == 0.8
            else:
                assert metric.threshold == 0.1
