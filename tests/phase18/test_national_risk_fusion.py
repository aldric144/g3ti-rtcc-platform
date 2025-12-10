"""
Tests for National Risk Fusion Engine

Tests cover:
- National Stability Score calculation
- Multi-domain risk fusion
- Early warning generation
- Trend predictions
- Fusion timeline
- Metrics collection
"""

import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch

import sys
sys.path.insert(0, '/home/ubuntu/repos/g3ti-rtcc-platform/backend')

from app.national_security.national_risk_fusion import (
    NationalRiskFusionEngine,
    DomainRiskScore,
    NationalStabilityScore,
    RiskFusionResult,
    EarlyWarningSignal,
    TrendPrediction,
    FusionEvent,
    StabilityLevel,
    RiskDomain,
    FusionMethod,
    TrendDirection,
    AlertUrgency,
)


class TestNationalRiskFusionEngine:
    """Test suite for NationalRiskFusionEngine."""

    @pytest.fixture
    def engine(self):
        """Create a NationalRiskFusionEngine instance."""
        return NationalRiskFusionEngine()

    def test_engine_initialization(self, engine):
        """Test engine initializes with empty collections."""
        assert engine.stability_scores == {}
        assert engine.fusion_results == {}
        assert engine.early_warnings == {}
        assert engine.trend_predictions == {}
        assert engine.fusion_timeline == []

    def test_calculate_national_stability_score(self, engine):
        """Test National Stability Score calculation."""
        domain_scores = {
            RiskDomain.CYBER: DomainRiskScore(
                domain=RiskDomain.CYBER,
                score=45.0,
                confidence=0.85,
                trend=TrendDirection.STABLE,
                key_factors=["malware_activity", "botnet_threats"],
                last_updated="2025-12-10T00:00:00Z",
            ),
            RiskDomain.GEOPOLITICAL: DomainRiskScore(
                domain=RiskDomain.GEOPOLITICAL,
                score=55.0,
                confidence=0.90,
                trend=TrendDirection.DEGRADING,
                key_factors=["regional_conflict", "sanctions"],
                last_updated="2025-12-10T00:00:00Z",
            ),
            RiskDomain.FINANCIAL: DomainRiskScore(
                domain=RiskDomain.FINANCIAL,
                score=35.0,
                confidence=0.88,
                trend=TrendDirection.IMPROVING,
                key_factors=["fraud_patterns"],
                last_updated="2025-12-10T00:00:00Z",
            ),
            RiskDomain.INSIDER: DomainRiskScore(
                domain=RiskDomain.INSIDER,
                score=25.0,
                confidence=0.92,
                trend=TrendDirection.STABLE,
                key_factors=["access_anomalies"],
                last_updated="2025-12-10T00:00:00Z",
            ),
        }

        nss = engine.calculate_national_stability_score(
            domain_scores=domain_scores,
            fusion_method=FusionMethod.WEIGHTED_AVERAGE,
        )

        assert nss is not None
        assert nss.assessment_id is not None
        assert nss.overall_score >= 0
        assert nss.overall_score <= 100
        assert nss.stability_level is not None
        assert nss.trend is not None
        assert nss.confidence_level > 0

    def test_stability_level_classification(self, engine):
        """Test stability level classification based on score."""
        test_cases = [
            (15.0, StabilityLevel.OPTIMAL),
            (28.0, StabilityLevel.STABLE),
            (42.0, StabilityLevel.ELEVATED_CONCERN),
            (60.0, StabilityLevel.UNSTABLE),
            (78.0, StabilityLevel.CRITICAL),
            (92.0, StabilityLevel.EMERGENCY),
        ]

        for score, expected_level in test_cases:
            domain_scores = {
                RiskDomain.CYBER: DomainRiskScore(
                    domain=RiskDomain.CYBER,
                    score=score,
                    confidence=0.9,
                    trend=TrendDirection.STABLE,
                    key_factors=[],
                    last_updated="2025-12-10T00:00:00Z",
                ),
            }

            nss = engine.calculate_national_stability_score(
                domain_scores=domain_scores,
                fusion_method=FusionMethod.WEIGHTED_AVERAGE,
            )

            assert nss.stability_level == expected_level, f"Score {score} should be {expected_level}"

    def test_perform_risk_fusion_weighted_average(self, engine):
        """Test risk fusion with weighted average method."""
        domain_scores = {
            RiskDomain.CYBER: DomainRiskScore(
                domain=RiskDomain.CYBER,
                score=50.0,
                confidence=0.9,
                trend=TrendDirection.STABLE,
                key_factors=["factor1"],
                last_updated="2025-12-10T00:00:00Z",
            ),
            RiskDomain.GEOPOLITICAL: DomainRiskScore(
                domain=RiskDomain.GEOPOLITICAL,
                score=60.0,
                confidence=0.85,
                trend=TrendDirection.DEGRADING,
                key_factors=["factor2"],
                last_updated="2025-12-10T00:00:00Z",
            ),
        }

        result = engine.perform_risk_fusion(
            domain_scores=domain_scores,
            method=FusionMethod.WEIGHTED_AVERAGE,
            context={"analysis_type": "routine"},
        )

        assert result is not None
        assert result.fusion_id is not None
        assert result.method == FusionMethod.WEIGHTED_AVERAGE
        assert result.fused_score >= 0
        assert result.fused_score <= 100

    def test_perform_risk_fusion_max_risk(self, engine):
        """Test risk fusion with max risk method."""
        domain_scores = {
            RiskDomain.CYBER: DomainRiskScore(
                domain=RiskDomain.CYBER,
                score=40.0,
                confidence=0.9,
                trend=TrendDirection.STABLE,
                key_factors=[],
                last_updated="2025-12-10T00:00:00Z",
            ),
            RiskDomain.TERRORISM: DomainRiskScore(
                domain=RiskDomain.TERRORISM,
                score=80.0,
                confidence=0.95,
                trend=TrendDirection.RAPIDLY_DEGRADING,
                key_factors=["imminent_threat"],
                last_updated="2025-12-10T00:00:00Z",
            ),
        }

        result = engine.perform_risk_fusion(
            domain_scores=domain_scores,
            method=FusionMethod.MAX_RISK,
            context={},
        )

        assert result is not None
        assert result.fused_score == 80.0

    def test_perform_risk_fusion_ensemble(self, engine):
        """Test risk fusion with ensemble method."""
        domain_scores = {
            RiskDomain.CYBER: DomainRiskScore(
                domain=RiskDomain.CYBER,
                score=45.0,
                confidence=0.88,
                trend=TrendDirection.STABLE,
                key_factors=[],
                last_updated="2025-12-10T00:00:00Z",
            ),
            RiskDomain.FINANCIAL: DomainRiskScore(
                domain=RiskDomain.FINANCIAL,
                score=55.0,
                confidence=0.92,
                trend=TrendDirection.DEGRADING,
                key_factors=[],
                last_updated="2025-12-10T00:00:00Z",
            ),
        }

        result = engine.perform_risk_fusion(
            domain_scores=domain_scores,
            method=FusionMethod.ENSEMBLE,
            context={},
        )

        assert result is not None
        assert result.method == FusionMethod.ENSEMBLE
        assert result.fused_score >= 0

    def test_generate_early_warning(self, engine):
        """Test early warning signal generation."""
        warning = engine.generate_early_warning(
            title="Test Early Warning",
            description="A test early warning signal",
            urgency=AlertUrgency.PRIORITY,
            domains_affected=[RiskDomain.CYBER, RiskDomain.INFRASTRUCTURE],
            risk_score=72.0,
            probability=0.75,
            time_horizon_hours=48,
            recommended_actions=["Increase monitoring", "Alert security teams"],
            supporting_evidence=["Malware spike detected", "Unusual network activity"],
        )

        assert warning is not None
        assert warning.signal_id is not None
        assert warning.title == "Test Early Warning"
        assert warning.urgency == AlertUrgency.PRIORITY
        assert warning.risk_score == 72.0
        assert warning.is_active is True

    def test_get_early_warnings_filtering(self, engine):
        """Test early warning retrieval with filtering."""
        engine.generate_early_warning(
            title="Flash Warning",
            description="Urgent warning",
            urgency=AlertUrgency.FLASH,
            domains_affected=[RiskDomain.TERRORISM],
            risk_score=90.0,
            probability=0.9,
            time_horizon_hours=6,
            recommended_actions=["Immediate action required"],
            supporting_evidence=["Intelligence report"],
        )

        engine.generate_early_warning(
            title="Routine Warning",
            description="Routine warning",
            urgency=AlertUrgency.ROUTINE,
            domains_affected=[RiskDomain.FINANCIAL],
            risk_score=40.0,
            probability=0.5,
            time_horizon_hours=168,
            recommended_actions=["Monitor situation"],
            supporting_evidence=["Trend analysis"],
        )

        flash_warnings = engine.get_early_warnings(urgency=AlertUrgency.FLASH)
        assert len(flash_warnings) >= 1

        active_warnings = engine.get_early_warnings(active_only=True)
        assert all(w.is_active for w in active_warnings)

    def test_create_trend_prediction(self, engine):
        """Test trend prediction creation."""
        prediction = engine.create_trend_prediction(
            domain=RiskDomain.CYBER,
            current_score=45.0,
            predicted_score_24h=48.0,
            predicted_score_7d=52.0,
            predicted_score_30d=50.0,
            trend_direction=TrendDirection.DEGRADING,
            confidence=0.82,
            factors=["Increasing malware activity", "New vulnerability disclosures"],
        )

        assert prediction is not None
        assert prediction.prediction_id is not None
        assert prediction.domain == RiskDomain.CYBER
        assert prediction.trend_direction == TrendDirection.DEGRADING

    def test_record_fusion_event(self, engine):
        """Test fusion event recording."""
        event = engine.record_fusion_event(
            event_type="stability_assessment",
            domain=RiskDomain.CYBER,
            severity=65.0,
            description="Routine stability assessment completed",
            impact_assessment="Moderate impact on overall stability",
        )

        assert event is not None
        assert event.event_id is not None
        assert event.event_type == "stability_assessment"
        assert event.severity == 65.0

    def test_get_fusion_timeline(self, engine):
        """Test fusion timeline retrieval."""
        engine.record_fusion_event(
            event_type="warning_generated",
            domain=RiskDomain.GEOPOLITICAL,
            severity=75.0,
            description="Early warning generated",
            impact_assessment="High impact",
        )

        engine.record_fusion_event(
            event_type="score_update",
            domain=RiskDomain.FINANCIAL,
            severity=40.0,
            description="Score updated",
            impact_assessment="Low impact",
        )

        timeline = engine.get_fusion_timeline(hours=24)
        assert len(timeline) >= 2

        domain_timeline = engine.get_fusion_timeline(
            hours=24,
            domain=RiskDomain.GEOPOLITICAL
        )
        assert all(e.domain == RiskDomain.GEOPOLITICAL for e in domain_timeline)

    def test_get_latest_stability_score(self, engine):
        """Test retrieving latest stability score."""
        domain_scores = {
            RiskDomain.CYBER: DomainRiskScore(
                domain=RiskDomain.CYBER,
                score=50.0,
                confidence=0.9,
                trend=TrendDirection.STABLE,
                key_factors=[],
                last_updated="2025-12-10T00:00:00Z",
            ),
        }

        engine.calculate_national_stability_score(
            domain_scores=domain_scores,
            fusion_method=FusionMethod.WEIGHTED_AVERAGE,
        )

        latest = engine.get_latest_stability_score()
        assert latest is not None
        assert latest.overall_score >= 0

    def test_acknowledge_warning(self, engine):
        """Test acknowledging an early warning."""
        warning = engine.generate_early_warning(
            title="Ack Test Warning",
            description="Warning for acknowledgment testing",
            urgency=AlertUrgency.PRIORITY,
            domains_affected=[RiskDomain.CYBER],
            risk_score=60.0,
            probability=0.7,
            time_horizon_hours=24,
            recommended_actions=["Review and acknowledge"],
            supporting_evidence=["Test evidence"],
        )

        result = engine.acknowledge_warning(
            signal_id=warning.signal_id,
            acknowledged_by="security_analyst",
            notes="Reviewed and acknowledged",
        )

        assert result is True

        updated = engine.early_warnings[warning.signal_id]
        assert updated.acknowledged is True

    def test_get_metrics(self, engine):
        """Test metrics collection."""
        domain_scores = {
            RiskDomain.CYBER: DomainRiskScore(
                domain=RiskDomain.CYBER,
                score=45.0,
                confidence=0.9,
                trend=TrendDirection.STABLE,
                key_factors=[],
                last_updated="2025-12-10T00:00:00Z",
            ),
        }

        engine.calculate_national_stability_score(
            domain_scores=domain_scores,
            fusion_method=FusionMethod.WEIGHTED_AVERAGE,
        )

        engine.generate_early_warning(
            title="Metrics Test Warning",
            description="Warning for metrics testing",
            urgency=AlertUrgency.ROUTINE,
            domains_affected=[RiskDomain.FINANCIAL],
            risk_score=35.0,
            probability=0.5,
            time_horizon_hours=72,
            recommended_actions=["Monitor"],
            supporting_evidence=["Data"],
        )

        metrics = engine.get_metrics()

        assert "total_stability_assessments" in metrics
        assert "latest_stability_score" in metrics
        assert "total_fusion_results" in metrics
        assert "total_early_warnings" in metrics
        assert "active_warnings" in metrics
        assert "unacknowledged_warnings" in metrics
        assert "total_trend_predictions" in metrics
        assert "fusion_events_24h" in metrics


class TestNationalStabilityScoreDataclass:
    """Test NationalStabilityScore dataclass."""

    def test_stability_score_creation(self):
        """Test NationalStabilityScore dataclass creation."""
        nss = NationalStabilityScore(
            assessment_id="nss-123",
            timestamp="2025-12-10T00:00:00Z",
            overall_score=45.0,
            stability_level=StabilityLevel.ELEVATED_CONCERN,
            domain_scores={},
            trend=TrendDirection.STABLE,
            confidence_level=0.88,
            key_drivers=["cyber_threats", "geopolitical_tension"],
            recommendations=["Increase monitoring", "Review security posture"],
            forecast_24h=47.0,
            forecast_7d=50.0,
            forecast_30d=48.0,
            metadata={},
        )

        assert nss.assessment_id == "nss-123"
        assert nss.overall_score == 45.0
        assert nss.stability_level == StabilityLevel.ELEVATED_CONCERN


class TestRiskFusionResultDataclass:
    """Test RiskFusionResult dataclass."""

    def test_fusion_result_creation(self):
        """Test RiskFusionResult dataclass creation."""
        result = RiskFusionResult(
            fusion_id="fusion-123",
            timestamp="2025-12-10T00:00:00Z",
            method=FusionMethod.ENSEMBLE,
            input_domains=[RiskDomain.CYBER, RiskDomain.FINANCIAL],
            domain_scores={},
            fused_score=52.0,
            confidence=0.85,
            correlations={"cyber_financial": 0.65},
            anomalies_detected=["Unusual correlation spike"],
            context={"analysis_type": "routine"},
            metadata={},
        )

        assert result.fusion_id == "fusion-123"
        assert result.method == FusionMethod.ENSEMBLE
        assert result.fused_score == 52.0


class TestEarlyWarningSignalDataclass:
    """Test EarlyWarningSignal dataclass."""

    def test_early_warning_creation(self):
        """Test EarlyWarningSignal dataclass creation."""
        warning = EarlyWarningSignal(
            signal_id="warn-123",
            title="Test Warning",
            description="Test description",
            urgency=AlertUrgency.IMMEDIATE,
            domains_affected=[RiskDomain.CYBER, RiskDomain.INFRASTRUCTURE],
            risk_score=75.0,
            probability=0.8,
            time_horizon_hours=24,
            recommended_actions=["Action 1", "Action 2"],
            supporting_evidence=["Evidence 1"],
            is_active=True,
            acknowledged=False,
            acknowledged_by=None,
            acknowledged_at=None,
            created_at="2025-12-10T00:00:00Z",
            expires_at="2025-12-11T00:00:00Z",
            metadata={},
        )

        assert warning.signal_id == "warn-123"
        assert warning.urgency == AlertUrgency.IMMEDIATE
        assert warning.risk_score == 75.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
