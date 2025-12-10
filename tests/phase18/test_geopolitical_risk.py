"""
Tests for Geopolitical Risk Engine

Tests cover:
- Conflict event recording
- Conflict intensity index calculation
- Nation-state threat assessment
- Sanctions event ingestion
- Geo-economic risk assessment
- Global risk summary
- Metrics collection
"""

import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch

import sys
sys.path.insert(0, '/home/ubuntu/repos/g3ti-rtcc-platform/backend')

from app.national_security.geopolitical_risk import (
    GeopoliticalRiskEngine,
    ConflictEvent,
    NationStateThreat,
    SanctionsEvent,
    GeoEconomicRisk,
    GlobalEvent,
    ConflictIntensity,
    ThreatActorType,
    RegionStability,
    ThreatDomain,
    SanctionType,
    EventCategory,
)


class TestGeopoliticalRiskEngine:
    """Test suite for GeopoliticalRiskEngine."""

    @pytest.fixture
    def engine(self):
        """Create a GeopoliticalRiskEngine instance."""
        return GeopoliticalRiskEngine()

    def test_engine_initialization(self, engine):
        """Test engine initializes with empty collections."""
        assert engine.conflict_events == {}
        assert engine.nation_state_threats == {}
        assert engine.sanctions_events == {}
        assert engine.geo_economic_risks == {}
        assert engine.global_events == {}

    def test_record_conflict_event(self, engine):
        """Test conflict event recording."""
        event = engine.record_conflict_event(
            name="Test Conflict",
            description="A test conflict for unit testing",
            intensity=ConflictIntensity.MEDIUM,
            region="Eastern Europe",
            countries_involved=["Country A", "Country B"],
            start_date="2025-01-01",
            casualties_estimate=1000,
            displacement_estimate=50000,
        )

        assert event is not None
        assert event.event_id is not None
        assert event.name == "Test Conflict"
        assert event.intensity == ConflictIntensity.MEDIUM
        assert event.is_active is True
        assert event.escalation_risk > 0

    def test_get_conflict_events_filtering(self, engine):
        """Test conflict event retrieval with filtering."""
        engine.record_conflict_event(
            name="High Intensity Conflict",
            description="High intensity conflict",
            intensity=ConflictIntensity.HIGH,
            region="Middle East",
            countries_involved=["Country X", "Country Y"],
            start_date="2025-01-01",
            casualties_estimate=5000,
            displacement_estimate=100000,
        )

        engine.record_conflict_event(
            name="Low Intensity Conflict",
            description="Low intensity conflict",
            intensity=ConflictIntensity.LOW,
            region="Africa",
            countries_involved=["Country M", "Country N"],
            start_date="2025-02-01",
            casualties_estimate=100,
            displacement_estimate=5000,
        )

        high_intensity = engine.get_conflict_events(intensity=ConflictIntensity.HIGH)
        assert len(high_intensity) == 1
        assert high_intensity[0].name == "High Intensity Conflict"

        active_events = engine.get_conflict_events(active_only=True)
        assert all(e.is_active for e in active_events)

    def test_calculate_conflict_intensity_index(self, engine):
        """Test conflict intensity index calculation."""
        engine.record_conflict_event(
            name="Conflict 1",
            description="First conflict",
            intensity=ConflictIntensity.HIGH,
            region="Europe",
            countries_involved=["A", "B"],
            start_date="2025-01-01",
            casualties_estimate=2000,
            displacement_estimate=30000,
        )

        engine.record_conflict_event(
            name="Conflict 2",
            description="Second conflict",
            intensity=ConflictIntensity.MEDIUM,
            region="Europe",
            countries_involved=["C", "D"],
            start_date="2025-02-01",
            casualties_estimate=500,
            displacement_estimate=10000,
        )

        index = engine.calculate_conflict_intensity_index()

        assert index is not None
        assert "global_index" in index
        assert "regional_indices" in index
        assert "active_conflicts" in index
        assert index["global_index"] >= 0

        regional_index = engine.calculate_conflict_intensity_index(region="Europe")
        assert regional_index is not None

    def test_assess_nation_state_threat(self, engine):
        """Test nation-state threat assessment."""
        threat = engine.assess_nation_state_threat(
            actor_name="Test Actor",
            actor_type=ThreatActorType.NATION_STATE,
            country_of_origin="Country X",
            target_countries=["Country A", "Country B"],
            threat_domains=[ThreatDomain.CYBER, ThreatDomain.ECONOMIC],
            capability_score=80.0,
            intent_score=70.0,
            historical_actions=["Previous cyber attack", "Economic sanctions evasion"],
        )

        assert threat is not None
        assert threat.threat_id is not None
        assert threat.actor_name == "Test Actor"
        assert threat.actor_type == ThreatActorType.NATION_STATE
        assert threat.overall_threat_score > 0

    def test_get_nation_state_threats_filtering(self, engine):
        """Test nation-state threat retrieval with filtering."""
        engine.assess_nation_state_threat(
            actor_name="Cyber Actor",
            actor_type=ThreatActorType.APT_GROUP,
            country_of_origin="Country Y",
            target_countries=["Country C"],
            threat_domains=[ThreatDomain.CYBER],
            capability_score=90.0,
            intent_score=85.0,
            historical_actions=["Multiple cyber attacks"],
        )

        apt_threats = engine.get_nation_state_threats(actor_type=ThreatActorType.APT_GROUP)
        assert len(apt_threats) >= 1

    def test_record_sanctions_event(self, engine):
        """Test sanctions event recording."""
        event = engine.record_sanctions_event(
            sanction_type=SanctionType.ECONOMIC,
            target_country="Country Z",
            target_entities=["Entity A", "Entity B"],
            imposing_countries=["Country 1", "Country 2"],
            reason="Test sanctions reason",
            effective_date="2025-01-01",
        )

        assert event is not None
        assert event.event_id is not None
        assert event.sanction_type == SanctionType.ECONOMIC
        assert event.is_active is True

    def test_get_sanctions_events_filtering(self, engine):
        """Test sanctions event retrieval with filtering."""
        engine.record_sanctions_event(
            sanction_type=SanctionType.TRAVEL_BAN,
            target_country="Country W",
            target_entities=["Individual X"],
            imposing_countries=["Country 3"],
            reason="Human rights violations",
            effective_date="2025-03-01",
        )

        travel_bans = engine.get_sanctions_events(sanction_type=SanctionType.TRAVEL_BAN)
        assert len(travel_bans) >= 1

    def test_assess_geo_economic_risk(self, engine):
        """Test geo-economic risk assessment."""
        risk = engine.assess_geo_economic_risk(
            country="Test Country",
            region="Test Region",
            economic_indicators={
                "gdp_growth": -2.5,
                "inflation": 15.0,
                "unemployment": 12.0,
                "debt_to_gdp": 120.0,
            },
            political_indicators={
                "government_stability": 3.0,
                "corruption_index": 70.0,
                "civil_unrest_level": 7.0,
            },
            security_indicators={
                "terrorism_risk": 6.0,
                "crime_rate": 8.0,
                "border_security": 4.0,
            },
        )

        assert risk is not None
        assert risk.risk_id is not None
        assert risk.country == "Test Country"
        assert risk.overall_risk_score > 0
        assert risk.stability_level is not None

    def test_get_geo_economic_risks_filtering(self, engine):
        """Test geo-economic risk retrieval with filtering."""
        engine.assess_geo_economic_risk(
            country="High Risk Country",
            region="Test Region",
            economic_indicators={"gdp_growth": -5.0, "inflation": 25.0},
            political_indicators={"government_stability": 2.0},
            security_indicators={"terrorism_risk": 8.0},
        )

        risks = engine.get_geo_economic_risks(region="Test Region")
        assert len(risks) >= 1

    def test_record_global_event(self, engine):
        """Test global event recording."""
        event = engine.record_global_event(
            category=EventCategory.NATURAL_DISASTER,
            title="Test Earthquake",
            description="A test earthquake event",
            location="Test Location",
            affected_countries=["Country A", "Country B"],
            severity=8.0,
            source="test_source",
        )

        assert event is not None
        assert event.event_id is not None
        assert event.category == EventCategory.NATURAL_DISASTER
        assert event.severity == 8.0

    def test_get_global_events_filtering(self, engine):
        """Test global event retrieval with filtering."""
        engine.record_global_event(
            category=EventCategory.TERRORISM,
            title="Test Terror Event",
            description="A test terrorism event",
            location="Test City",
            affected_countries=["Country X"],
            severity=9.0,
            source="test",
        )

        terror_events = engine.get_global_events(category=EventCategory.TERRORISM)
        assert len(terror_events) >= 1

    def test_get_country_risk_score(self, engine):
        """Test country risk score retrieval."""
        engine.assess_geo_economic_risk(
            country="Scored Country",
            region="Test Region",
            economic_indicators={"gdp_growth": 2.0, "inflation": 3.0},
            political_indicators={"government_stability": 7.0},
            security_indicators={"terrorism_risk": 2.0},
        )

        score = engine.get_country_risk_score("Scored Country")
        assert score is not None
        assert score >= 0

        unknown_score = engine.get_country_risk_score("Unknown Country")
        assert unknown_score is None

    def test_get_region_stability(self, engine):
        """Test region stability retrieval."""
        engine.assess_geo_economic_risk(
            country="Region Test Country",
            region="Stability Test Region",
            economic_indicators={"gdp_growth": 1.0},
            political_indicators={"government_stability": 5.0},
            security_indicators={"terrorism_risk": 5.0},
        )

        stability = engine.get_region_stability("Stability Test Region")
        assert stability is not None

    def test_get_global_risk_summary(self, engine):
        """Test global risk summary generation."""
        engine.record_conflict_event(
            name="Summary Conflict",
            description="Conflict for summary test",
            intensity=ConflictIntensity.MEDIUM,
            region="Summary Region",
            countries_involved=["A", "B"],
            start_date="2025-01-01",
            casualties_estimate=100,
            displacement_estimate=1000,
        )

        engine.assess_nation_state_threat(
            actor_name="Summary Actor",
            actor_type=ThreatActorType.NATION_STATE,
            country_of_origin="Country S",
            target_countries=["Country T"],
            threat_domains=[ThreatDomain.MILITARY],
            capability_score=60.0,
            intent_score=50.0,
            historical_actions=[],
        )

        summary = engine.get_global_risk_summary()

        assert summary is not None
        assert "active_conflicts" in summary
        assert "nation_state_threats" in summary
        assert "active_sanctions" in summary
        assert "high_risk_countries" in summary
        assert "global_conflict_index" in summary

    def test_get_metrics(self, engine):
        """Test metrics collection."""
        engine.record_conflict_event(
            name="Metrics Conflict",
            description="Conflict for metrics test",
            intensity=ConflictIntensity.LOW,
            region="Metrics Region",
            countries_involved=["M", "N"],
            start_date="2025-01-01",
            casualties_estimate=50,
            displacement_estimate=500,
        )

        metrics = engine.get_metrics()

        assert "total_conflict_events" in metrics
        assert "active_conflicts" in metrics
        assert "total_nation_state_threats" in metrics
        assert "total_sanctions_events" in metrics
        assert "active_sanctions" in metrics
        assert "total_geo_economic_risks" in metrics
        assert "total_global_events" in metrics


class TestConflictEventDataclass:
    """Test ConflictEvent dataclass."""

    def test_conflict_event_creation(self):
        """Test ConflictEvent dataclass creation."""
        event = ConflictEvent(
            event_id="conflict-123",
            name="Test Conflict",
            description="Test description",
            intensity=ConflictIntensity.HIGH,
            region="Test Region",
            countries_involved=["A", "B", "C"],
            start_date="2025-01-01",
            end_date=None,
            is_active=True,
            escalation_risk=0.75,
            casualties_estimate=5000,
            displacement_estimate=100000,
            economic_impact_estimate=1000000000.0,
            last_updated="2025-12-10T00:00:00Z",
            sources=["source1", "source2"],
            metadata={},
        )

        assert event.event_id == "conflict-123"
        assert event.intensity == ConflictIntensity.HIGH
        assert event.escalation_risk == 0.75


class TestNationStateThreatDataclass:
    """Test NationStateThreat dataclass."""

    def test_nation_state_threat_creation(self):
        """Test NationStateThreat dataclass creation."""
        threat = NationStateThreat(
            threat_id="threat-123",
            actor_name="Test Actor",
            actor_type=ThreatActorType.APT_GROUP,
            country_of_origin="Country X",
            target_countries=["A", "B"],
            threat_domains=[ThreatDomain.CYBER, ThreatDomain.ESPIONAGE],
            capability_score=85.0,
            intent_score=75.0,
            overall_threat_score=80.0,
            historical_actions=["Action 1", "Action 2"],
            known_ttps=["TTP1", "TTP2"],
            assessment_date="2025-12-10T00:00:00Z",
            confidence_level=0.9,
            metadata={},
        )

        assert threat.threat_id == "threat-123"
        assert threat.actor_type == ThreatActorType.APT_GROUP
        assert threat.overall_threat_score == 80.0


class TestGeoEconomicRiskDataclass:
    """Test GeoEconomicRisk dataclass."""

    def test_geo_economic_risk_creation(self):
        """Test GeoEconomicRisk dataclass creation."""
        risk = GeoEconomicRisk(
            risk_id="risk-123",
            country="Test Country",
            region="Test Region",
            stability_level=RegionStability.VOLATILE,
            overall_risk_score=65.0,
            economic_risk_score=60.0,
            political_risk_score=70.0,
            security_risk_score=65.0,
            economic_indicators={"gdp_growth": -1.0},
            political_indicators={"stability": 4.0},
            security_indicators={"terrorism": 6.0},
            assessment_date="2025-12-10T00:00:00Z",
            forecast_6m=70.0,
            forecast_12m=68.0,
            key_risks=["Economic downturn", "Political instability"],
            metadata={},
        )

        assert risk.risk_id == "risk-123"
        assert risk.stability_level == RegionStability.VOLATILE
        assert risk.overall_risk_score == 65.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
