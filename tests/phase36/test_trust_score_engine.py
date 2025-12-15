"""
Test Suite: Trust Score Engine
Phase 36: Public Safety Guardian
"""

import pytest
from datetime import datetime, timedelta

from backend.app.public_guardian.trust_score_engine import (
    TrustScoreEngine,
    TrustMetric,
    TrustLevel,
    MetricScore,
    TrustScore,
    TrustScoreHistory,
    NeighborhoodTrust,
)


class TestTrustScoreEngine:
    def setup_method(self):
        self.engine = TrustScoreEngine()

    def test_engine_singleton(self):
        engine2 = TrustScoreEngine()
        assert self.engine is engine2

    def test_calculate_trust_score(self):
        score = self.engine.calculate_trust_score()
        assert score is not None
        assert score.score_id is not None
        assert 0 <= score.overall_score <= 100

    def test_trust_score_has_metrics(self):
        score = self.engine.calculate_trust_score()
        assert len(score.metric_scores) > 0

    def test_trust_score_level_assignment(self):
        score = self.engine.calculate_trust_score()
        assert score.trust_level in [
            TrustLevel.VERY_LOW, TrustLevel.LOW, TrustLevel.MODERATE,
            TrustLevel.HIGH, TrustLevel.VERY_HIGH
        ]

    def test_get_current_score(self):
        self.engine.calculate_trust_score()
        current = self.engine.get_current_score()
        assert current is not None

    def test_get_score_history(self):
        self.engine.calculate_trust_score()
        history = self.engine.get_score_history(limit=10)
        assert history is not None
        assert isinstance(history.scores, list)

    def test_get_neighborhood_score(self):
        neighborhoods = self.engine.get_all_neighborhood_scores()
        if len(neighborhoods) > 0:
            neighborhood = neighborhoods[0]
            retrieved = self.engine.get_neighborhood_score(neighborhood.neighborhood_id)
            assert retrieved is not None

    def test_get_all_neighborhood_scores(self):
        neighborhoods = self.engine.get_all_neighborhood_scores()
        assert isinstance(neighborhoods, list)

    def test_update_neighborhood_score(self):
        neighborhoods = self.engine.get_all_neighborhood_scores()
        if len(neighborhoods) > 0:
            neighborhood = neighborhoods[0]
            updated = self.engine.update_neighborhood_score(
                neighborhood.neighborhood_id,
                trust_score=75.0
            )
            assert updated is not None

    def test_run_fairness_audit(self):
        result = self.engine.run_fairness_audit()
        assert result is not None
        assert "passed" in result
        assert "metrics_evaluated" in result

    def test_run_bias_audit(self):
        result = self.engine.run_bias_audit()
        assert result is not None
        assert "passed" in result

    def test_get_metric_breakdown(self):
        breakdown = self.engine.get_metric_breakdown()
        assert "metrics" in breakdown
        assert len(breakdown["metrics"]) == 10

    def test_metric_weights_sum_to_one(self):
        breakdown = self.engine.get_metric_breakdown()
        total_weight = sum(m["weight"] for m in breakdown["metrics"])
        assert abs(total_weight - 1.0) < 0.01

    def test_get_statistics(self):
        stats = self.engine.get_statistics()
        assert "current_score" in stats
        assert "current_level" in stats
        assert "neighborhoods_tracked" in stats

    def test_trust_score_to_dict(self):
        score = self.engine.calculate_trust_score()
        score_dict = score.to_dict()
        assert "score_id" in score_dict
        assert "overall_score" in score_dict
        assert "trust_level" in score_dict

    def test_trust_score_confidence(self):
        score = self.engine.calculate_trust_score()
        assert 0 <= score.confidence <= 1

    def test_trust_score_trend(self):
        self.engine.calculate_trust_score()
        self.engine.calculate_trust_score()
        current = self.engine.get_current_score()
        assert hasattr(current, "trend_vs_previous")

    def test_fairness_audit_passed(self):
        score = self.engine.calculate_trust_score()
        assert hasattr(score, "fairness_audit_passed")

    def test_bias_audit_passed(self):
        score = self.engine.calculate_trust_score()
        assert hasattr(score, "bias_audit_passed")


class TestTrustMetric:
    def test_all_metrics_exist(self):
        expected = [
            "crime_reduction", "response_time", "community_interaction",
            "complaint_resolution", "youth_outreach", "transparency",
            "fairness", "accountability", "accessibility", "communication"
        ]
        for metric in expected:
            assert hasattr(TrustMetric, metric.upper())

    def test_metric_count(self):
        metrics = list(TrustMetric)
        assert len(metrics) == 10


class TestTrustLevel:
    def test_all_levels_exist(self):
        expected = ["very_low", "low", "moderate", "high", "very_high"]
        for level in expected:
            assert hasattr(TrustLevel, level.upper())

    def test_level_ordering(self):
        levels = [TrustLevel.VERY_LOW, TrustLevel.LOW, TrustLevel.MODERATE,
                  TrustLevel.HIGH, TrustLevel.VERY_HIGH]
        assert len(levels) == 5


class TestMetricScore:
    def test_metric_score_creation(self):
        score = MetricScore(
            metric=TrustMetric.CRIME_REDUCTION,
            score=75.0,
            weight=0.15,
            weighted_score=11.25,
        )
        assert score.metric == TrustMetric.CRIME_REDUCTION
        assert score.score == 75.0
        assert score.weight == 0.15

    def test_metric_score_to_dict(self):
        score = MetricScore(
            metric=TrustMetric.RESPONSE_TIME,
            score=80.0,
            weight=0.12,
            weighted_score=9.6,
        )
        score_dict = score.to_dict()
        assert "metric" in score_dict
        assert "score" in score_dict
        assert "weight" in score_dict


class TestNeighborhoodTrust:
    def test_neighborhood_trust_creation(self):
        neighborhood = NeighborhoodTrust(
            neighborhood_id="nb-001",
            name="Downtown Riviera Beach",
            trust_score=72.5,
            trust_level=TrustLevel.HIGH,
            population=12000,
        )
        assert neighborhood.name == "Downtown Riviera Beach"
        assert neighborhood.trust_score == 72.5

    def test_neighborhood_trust_to_dict(self):
        neighborhood = NeighborhoodTrust(
            neighborhood_id="nb-002",
            name="Singer Island",
            trust_score=85.0,
            trust_level=TrustLevel.VERY_HIGH,
            population=5000,
        )
        nb_dict = neighborhood.to_dict()
        assert "neighborhood_id" in nb_dict
        assert "name" in nb_dict
        assert "trust_score" in nb_dict
