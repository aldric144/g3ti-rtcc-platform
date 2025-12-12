"""
Test Suite 3: Risk Fusion Engine Tests

Tests for Global Risk Fusion Engine functionality.
"""

import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch


class TestRiskDomains:
    """Tests for risk domain enumeration."""

    def test_risk_domain_climate_exists(self):
        """Test that CLIMATE domain is defined."""
        from backend.app.global_awareness.risk_fusion_engine import RiskDomain
        assert hasattr(RiskDomain, "CLIMATE")

    def test_risk_domain_geopolitical_exists(self):
        """Test that GEOPOLITICAL domain is defined."""
        from backend.app.global_awareness.risk_fusion_engine import RiskDomain
        assert hasattr(RiskDomain, "GEOPOLITICAL")

    def test_risk_domain_cyber_exists(self):
        """Test that CYBER domain is defined."""
        from backend.app.global_awareness.risk_fusion_engine import RiskDomain
        assert hasattr(RiskDomain, "CYBER")

    def test_risk_domain_supply_chain_exists(self):
        """Test that SUPPLY_CHAIN domain is defined."""
        from backend.app.global_awareness.risk_fusion_engine import RiskDomain
        assert hasattr(RiskDomain, "SUPPLY_CHAIN")

    def test_risk_domain_health_exists(self):
        """Test that HEALTH domain is defined."""
        from backend.app.global_awareness.risk_fusion_engine import RiskDomain
        assert hasattr(RiskDomain, "HEALTH")

    def test_risk_domain_conflict_exists(self):
        """Test that CONFLICT domain is defined."""
        from backend.app.global_awareness.risk_fusion_engine import RiskDomain
        assert hasattr(RiskDomain, "CONFLICT")

    def test_all_ten_risk_domains_defined(self):
        """Test that all 10 risk domains are defined."""
        from backend.app.global_awareness.risk_fusion_engine import RiskDomain
        domains = list(RiskDomain)
        assert len(domains) == 10


class TestRiskLevels:
    """Tests for risk level enumeration."""

    def test_risk_level_minimal(self):
        """Test MINIMAL risk level."""
        from backend.app.global_awareness.risk_fusion_engine import RiskLevel
        assert hasattr(RiskLevel, "MINIMAL")

    def test_risk_level_low(self):
        """Test LOW risk level."""
        from backend.app.global_awareness.risk_fusion_engine import RiskLevel
        assert hasattr(RiskLevel, "LOW")

    def test_risk_level_moderate(self):
        """Test MODERATE risk level."""
        from backend.app.global_awareness.risk_fusion_engine import RiskLevel
        assert hasattr(RiskLevel, "MODERATE")

    def test_risk_level_high(self):
        """Test HIGH risk level."""
        from backend.app.global_awareness.risk_fusion_engine import RiskLevel
        assert hasattr(RiskLevel, "HIGH")

    def test_risk_level_critical(self):
        """Test CRITICAL risk level."""
        from backend.app.global_awareness.risk_fusion_engine import RiskLevel
        assert hasattr(RiskLevel, "CRITICAL")


class TestDomainRiskScore:
    """Tests for DomainRiskScore data class."""

    def test_domain_risk_score_creation(self):
        """Test creating a DomainRiskScore instance."""
        from backend.app.global_awareness.risk_fusion_engine import (
            DomainRiskScore,
            RiskDomain,
            RiskLevel,
            TrendDirection,
        )

        score = DomainRiskScore(
            score_id="DRS-001",
            domain=RiskDomain.CONFLICT,
            region="Eastern Europe",
            country="Ukraine",
            score=85.0,
            level=RiskLevel.CRITICAL,
            trend=TrendDirection.DETERIORATING,
            contributing_factors=["Active conflict", "Military buildup"],
            data_sources=["ACLED", "GDACS"],
            confidence=0.92,
            timestamp=datetime.utcnow(),
            chain_of_custody_hash="test_hash",
        )

        assert score.score_id == "DRS-001"
        assert score.domain == RiskDomain.CONFLICT
        assert score.score == 85.0
        assert score.level == RiskLevel.CRITICAL


class TestFusedRiskAssessment:
    """Tests for FusedRiskAssessment data class."""

    def test_fused_assessment_creation(self):
        """Test creating a FusedRiskAssessment instance."""
        from backend.app.global_awareness.risk_fusion_engine import (
            FusedRiskAssessment,
            RiskLevel,
            TrendDirection,
        )

        assessment = FusedRiskAssessment(
            assessment_id="FRA-001",
            region="Middle East",
            country=None,
            overall_score=78.5,
            overall_level=RiskLevel.HIGH,
            domain_scores={},
            primary_risk_domain="conflict",
            secondary_risk_domains=["geopolitical", "economic"],
            trend=TrendDirection.STABLE,
            forecast_7_day=80.0,
            forecast_30_day=82.0,
            key_drivers=["Regional tensions"],
            mitigation_recommendations=["Diplomatic engagement"],
            timestamp=datetime.utcnow(),
            chain_of_custody_hash="test_hash",
        )

        assert assessment.assessment_id == "FRA-001"
        assert assessment.overall_score == 78.5
        assert assessment.overall_level == RiskLevel.HIGH


class TestRiskFusionEngine:
    """Tests for RiskFusionEngine class."""

    def test_risk_fusion_singleton(self):
        """Test that RiskFusionEngine is a singleton."""
        from backend.app.global_awareness.risk_fusion_engine import RiskFusionEngine

        engine1 = RiskFusionEngine()
        engine2 = RiskFusionEngine()
        assert engine1 is engine2

    def test_risk_fusion_has_domain_weights(self):
        """Test that risk fusion engine has domain weights."""
        from backend.app.global_awareness.risk_fusion_engine import RiskFusionEngine

        engine = RiskFusionEngine()
        assert hasattr(engine, "domain_weights")
        assert len(engine.domain_weights) > 0

    def test_risk_fusion_has_risk_interactions(self):
        """Test that risk fusion engine has risk interaction matrix."""
        from backend.app.global_awareness.risk_fusion_engine import RiskFusionEngine

        engine = RiskFusionEngine()
        assert hasattr(engine, "risk_interactions")


class TestDomainRiskCalculation:
    """Tests for domain-specific risk calculation."""

    def test_calculate_conflict_risk(self):
        """Test calculating conflict risk score."""
        from backend.app.global_awareness.risk_fusion_engine import (
            RiskFusionEngine,
            RiskDomain,
        )

        engine = RiskFusionEngine()
        score = engine.calculate_domain_risk(
            domain=RiskDomain.CONFLICT,
            region="Eastern Europe",
            country="Ukraine",
            indicators={
                "active_conflicts": 1,
                "military_buildup": True,
                "casualties_30_day": 1000,
            },
        )

        assert score is not None
        assert score.domain == RiskDomain.CONFLICT
        assert 0 <= score.score <= 100

    def test_calculate_cyber_risk(self):
        """Test calculating cyber risk score."""
        from backend.app.global_awareness.risk_fusion_engine import (
            RiskFusionEngine,
            RiskDomain,
        )

        engine = RiskFusionEngine()
        score = engine.calculate_domain_risk(
            domain=RiskDomain.CYBER,
            region="North America",
            country="USA",
            indicators={
                "active_campaigns": 5,
                "critical_vulnerabilities": 10,
                "ransomware_incidents": 3,
            },
        )

        assert score is not None
        assert score.domain == RiskDomain.CYBER

    def test_calculate_climate_risk(self):
        """Test calculating climate risk score."""
        from backend.app.global_awareness.risk_fusion_engine import (
            RiskFusionEngine,
            RiskDomain,
        )

        engine = RiskFusionEngine()
        score = engine.calculate_domain_risk(
            domain=RiskDomain.CLIMATE,
            region="South Asia",
            country="Bangladesh",
            indicators={
                "flood_risk": 0.8,
                "cyclone_risk": 0.6,
                "sea_level_rise_mm": 5,
            },
        )

        assert score is not None
        assert score.domain == RiskDomain.CLIMATE


class TestFusedAssessment:
    """Tests for fused risk assessment."""

    def test_create_fused_assessment(self):
        """Test creating a fused risk assessment."""
        from backend.app.global_awareness.risk_fusion_engine import RiskFusionEngine

        engine = RiskFusionEngine()
        assessment = engine.create_fused_assessment(
            region="Middle East",
            country=None,
            indicators={
                "conflict": {"active_conflicts": 2},
                "geopolitical": {"sanctions": True},
                "economic": {"inflation_rate": 15.0},
            },
        )

        assert assessment is not None
        assert assessment.assessment_id.startswith("FRA-")
        assert 0 <= assessment.overall_score <= 100

    def test_fused_assessment_includes_forecasts(self):
        """Test that fused assessment includes forecasts."""
        from backend.app.global_awareness.risk_fusion_engine import RiskFusionEngine

        engine = RiskFusionEngine()
        assessment = engine.create_fused_assessment(
            region="East Asia",
            country="Taiwan",
            indicators={},
        )

        assert assessment.forecast_7_day is not None
        assert assessment.forecast_30_day is not None

    def test_fused_assessment_has_chain_of_custody(self):
        """Test that fused assessment has chain of custody hash."""
        from backend.app.global_awareness.risk_fusion_engine import RiskFusionEngine

        engine = RiskFusionEngine()
        assessment = engine.create_fused_assessment(
            region="Western Europe",
            country="Germany",
            indicators={},
        )

        assert assessment.chain_of_custody_hash is not None
        assert len(assessment.chain_of_custody_hash) == 64


class TestRiskAlerts:
    """Tests for risk alert generation."""

    def test_get_active_alerts(self):
        """Test getting active risk alerts."""
        from backend.app.global_awareness.risk_fusion_engine import RiskFusionEngine

        engine = RiskFusionEngine()
        alerts = engine.get_active_alerts()
        assert isinstance(alerts, list)

    def test_alert_has_required_fields(self):
        """Test that alerts have required fields."""
        from backend.app.global_awareness.risk_fusion_engine import RiskFusionEngine

        engine = RiskFusionEngine()
        alerts = engine.get_active_alerts()

        if alerts:
            alert = alerts[0]
            assert hasattr(alert, "alert_id")
            assert hasattr(alert, "domain")
            assert hasattr(alert, "risk_level")


class TestRegionalSummary:
    """Tests for regional risk summary."""

    def test_get_regional_risk_summary(self):
        """Test getting regional risk summary."""
        from backend.app.global_awareness.risk_fusion_engine import RiskFusionEngine

        engine = RiskFusionEngine()
        summary = engine.get_regional_risk_summary("Middle East")

        assert summary is not None
        assert "region" in summary
        assert "overall_risk" in summary

    def test_regional_summary_includes_domain_breakdown(self):
        """Test that regional summary includes domain breakdown."""
        from backend.app.global_awareness.risk_fusion_engine import RiskFusionEngine

        engine = RiskFusionEngine()
        summary = engine.get_regional_risk_summary("Eastern Europe")

        assert "domain_risks" in summary
