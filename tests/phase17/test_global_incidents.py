"""
Tests for Global Incidents module.

Phase 17: Global Threat Intelligence Engine
"""

import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch

import sys
sys.path.insert(0, '/home/ubuntu/repos/g3ti-rtcc-platform/backend')

from app.threat_intel.global_incidents import (
    GlobalIncidentMonitor,
    IncidentType,
    IncidentSeverity,
    IncidentStatus,
    FeedSource,
    AlertLevel,
    FeedConfig,
    GlobalIncident,
    CrisisAlert,
    GeoThreatCorrelation,
)


class TestGlobalIncidentMonitor:
    """Test suite for GlobalIncidentMonitor class."""

    @pytest.fixture
    def monitor(self):
        """Create a GlobalIncidentMonitor instance for testing."""
        return GlobalIncidentMonitor()

    def test_monitor_initialization(self, monitor):
        """Test that monitor initializes correctly."""
        assert monitor is not None
        assert isinstance(monitor.feed_configs, dict)
        assert isinstance(monitor.incidents, dict)
        assert isinstance(monitor.crisis_alerts, dict)

    def test_configure_feed(self, monitor):
        """Test configuring an incident feed."""
        config = monitor.configure_feed(
            name="USGS Earthquakes",
            source=FeedSource.USGS,
            url="https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson",
            incident_types=[IncidentType.EARTHQUAKE],
        )
        
        assert config is not None
        assert config.name == "USGS Earthquakes"
        assert config.source == FeedSource.USGS
        assert config.feed_id in monitor.feed_configs

    def test_configure_feed_with_filters(self, monitor):
        """Test configuring a feed with geographic filters."""
        config = monitor.configure_feed(
            name="Local Incidents",
            source=FeedSource.DHS,
            url="https://example.com/feed",
            incident_types=[IncidentType.TERRORISM, IncidentType.CIVIL_UNREST],
            geographic_filter={
                "country": "United States",
                "region": "Northeast",
            },
        )
        
        assert config is not None
        assert config.geographic_filter is not None

    def test_get_feed_configs(self, monitor):
        """Test retrieving feed configurations."""
        monitor.configure_feed(
            name="Feed 1",
            source=FeedSource.NASA,
            url="https://example.com/1",
            incident_types=[IncidentType.WILDFIRE],
        )
        monitor.configure_feed(
            name="Feed 2",
            source=FeedSource.NOAA,
            url="https://example.com/2",
            incident_types=[IncidentType.HURRICANE],
        )
        
        configs = monitor.get_feed_configs()
        assert len(configs) >= 2

    def test_ingest_incident(self, monitor):
        """Test ingesting a global incident."""
        incident = monitor.ingest_incident(
            incident_type=IncidentType.EARTHQUAKE,
            title="Major Earthquake in Pacific",
            description="7.2 magnitude earthquake struck the Pacific region",
            severity=IncidentSeverity.SEVERE,
            source=FeedSource.USGS,
            country="Japan",
            region="Kanto",
            latitude=35.6762,
            longitude=139.6503,
        )
        
        assert incident is not None
        assert incident.incident_type == IncidentType.EARTHQUAKE
        assert incident.severity == IncidentSeverity.SEVERE
        assert incident.incident_id in monitor.incidents

    def test_ingest_incident_with_casualties(self, monitor):
        """Test ingesting an incident with casualty information."""
        incident = monitor.ingest_incident(
            incident_type=IncidentType.TERRORISM,
            title="Terrorist Attack",
            description="Multiple explosions reported",
            severity=IncidentSeverity.CATASTROPHIC,
            source=FeedSource.DHS,
            country="United States",
            region="Northeast",
            latitude=40.7128,
            longitude=-74.0060,
            casualties=10,
            injuries=50,
        )
        
        assert incident is not None
        assert incident.casualties == 10
        assert incident.injuries == 50

    def test_get_incidents(self, monitor):
        """Test retrieving incidents."""
        monitor.ingest_incident(
            incident_type=IncidentType.EARTHQUAKE,
            title="Test Earthquake",
            description="Test",
            severity=IncidentSeverity.MODERATE,
            source=FeedSource.USGS,
            country="Test",
            region="Test",
            latitude=0.0,
            longitude=0.0,
        )
        
        incidents = monitor.get_incidents()
        assert isinstance(incidents, list)

    def test_get_incidents_by_type(self, monitor):
        """Test retrieving incidents by type."""
        monitor.ingest_incident(
            incident_type=IncidentType.CYBER_ATTACK,
            title="Cyber Attack",
            description="Test",
            severity=IncidentSeverity.SEVERE,
            source=FeedSource.CISA,
            country="Test",
            region="Test",
            latitude=0.0,
            longitude=0.0,
        )
        
        incidents = monitor.get_incidents(incident_type=IncidentType.CYBER_ATTACK)
        for incident in incidents:
            assert incident.incident_type == IncidentType.CYBER_ATTACK

    def test_get_incidents_by_severity(self, monitor):
        """Test retrieving incidents by minimum severity."""
        monitor.ingest_incident(
            incident_type=IncidentType.TERRORISM,
            title="Severe Incident",
            description="Test",
            severity=IncidentSeverity.CATASTROPHIC,
            source=FeedSource.DHS,
            country="Test",
            region="Test",
            latitude=0.0,
            longitude=0.0,
        )
        
        incidents = monitor.get_incidents(min_severity=IncidentSeverity.SEVERE)
        for incident in incidents:
            assert incident.severity.value >= IncidentSeverity.SEVERE.value

    def test_get_incidents_near_location(self, monitor):
        """Test retrieving incidents near a location."""
        monitor.ingest_incident(
            incident_type=IncidentType.CIVIL_UNREST,
            title="Nearby Incident",
            description="Test",
            severity=IncidentSeverity.MODERATE,
            source=FeedSource.CUSTOM,
            country="Test",
            region="Test",
            latitude=40.7128,
            longitude=-74.0060,
        )
        
        incidents = monitor.get_incidents_near_location(
            latitude=40.7500,
            longitude=-74.0000,
            radius_km=50,
        )
        assert isinstance(incidents, list)

    def test_create_crisis_alert(self, monitor):
        """Test creating a crisis alert."""
        alert = monitor.create_crisis_alert(
            title="Elevated Terrorism Threat",
            description="Intelligence indicates elevated threat level",
            alert_level=AlertLevel.WARNING,
            incident_types=[IncidentType.TERRORISM],
            affected_countries=["United States", "United Kingdom"],
        )
        
        assert alert is not None
        assert alert.title == "Elevated Terrorism Threat"
        assert alert.alert_level == AlertLevel.WARNING
        assert alert.alert_id in monitor.crisis_alerts

    def test_get_crisis_alerts(self, monitor):
        """Test retrieving crisis alerts."""
        monitor.create_crisis_alert(
            title="Test Alert",
            description="Test",
            alert_level=AlertLevel.ADVISORY,
            incident_types=[IncidentType.OTHER],
            affected_countries=["Test"],
        )
        
        alerts = monitor.get_crisis_alerts()
        assert isinstance(alerts, list)

    def test_get_active_crisis_alerts(self, monitor):
        """Test retrieving active crisis alerts."""
        monitor.create_crisis_alert(
            title="Active Alert",
            description="Test",
            alert_level=AlertLevel.WARNING,
            incident_types=[IncidentType.TERRORISM],
            affected_countries=["Test"],
        )
        
        alerts = monitor.get_crisis_alerts(active_only=True)
        for alert in alerts:
            assert alert.is_active is True

    def test_deactivate_crisis_alert(self, monitor):
        """Test deactivating a crisis alert."""
        alert = monitor.create_crisis_alert(
            title="To Deactivate",
            description="Test",
            alert_level=AlertLevel.ADVISORY,
            incident_types=[IncidentType.OTHER],
            affected_countries=["Test"],
        )
        
        result = monitor.deactivate_crisis_alert(alert.alert_id)
        assert result is True or result is None

    def test_correlate_with_local_threats(self, monitor):
        """Test correlating global incidents with local threats."""
        incident = monitor.ingest_incident(
            incident_type=IncidentType.TERRORISM,
            title="Global Terrorism Incident",
            description="Test",
            severity=IncidentSeverity.SEVERE,
            source=FeedSource.INTERPOL,
            country="Foreign Country",
            region="Region",
            latitude=51.5074,
            longitude=-0.1278,
        )
        
        correlations = monitor.correlate_with_local_threats(
            incident_id=incident.incident_id,
            local_latitude=40.7128,
            local_longitude=-74.0060,
        )
        
        assert isinstance(correlations, list)

    def test_get_crisis_map_data(self, monitor):
        """Test getting crisis map data."""
        monitor.ingest_incident(
            incident_type=IncidentType.EARTHQUAKE,
            title="Map Incident",
            description="Test",
            severity=IncidentSeverity.MODERATE,
            source=FeedSource.USGS,
            country="Test",
            region="Test",
            latitude=35.0,
            longitude=135.0,
        )
        
        map_data = monitor.get_crisis_map_data()
        assert isinstance(map_data, dict)
        assert "incidents" in map_data
        assert "alerts" in map_data

    def test_get_correlations(self, monitor):
        """Test retrieving correlations."""
        correlations = monitor.get_correlations()
        assert isinstance(correlations, list)

    def test_get_metrics(self, monitor):
        """Test retrieving metrics."""
        metrics = monitor.get_metrics()
        
        assert isinstance(metrics, dict)
        assert "total_feeds" in metrics
        assert "total_incidents" in metrics
        assert "total_alerts" in metrics
        assert "total_correlations" in metrics

    def test_haversine_distance(self, monitor):
        """Test haversine distance calculation."""
        distance = monitor._haversine_distance(
            lat1=40.7128,
            lon1=-74.0060,
            lat2=51.5074,
            lon2=-0.1278,
        )
        
        assert distance > 0
        assert distance < 10000  # NYC to London is about 5500 km


class TestFeedConfig:
    """Test suite for FeedConfig dataclass."""

    def test_feed_config_creation(self):
        """Test creating a FeedConfig."""
        config = FeedConfig(
            feed_id="feed-123",
            name="Test Feed",
            source=FeedSource.USGS,
            url="https://example.com/feed",
            incident_types=[IncidentType.EARTHQUAKE],
            geographic_filter=None,
            enabled=True,
            poll_interval_seconds=300,
            last_polled_at=None,
            created_at=datetime.utcnow(),
        )
        
        assert config.feed_id == "feed-123"
        assert config.name == "Test Feed"
        assert config.source == FeedSource.USGS


class TestGlobalIncident:
    """Test suite for GlobalIncident dataclass."""

    def test_incident_creation(self):
        """Test creating a GlobalIncident."""
        incident = GlobalIncident(
            incident_id="inc-123",
            incident_type=IncidentType.EARTHQUAKE,
            title="Test Earthquake",
            description="Test description",
            severity=IncidentSeverity.MODERATE,
            status=IncidentStatus.ONGOING,
            source=FeedSource.USGS,
            source_id="usgs-123",
            country="Japan",
            region="Kanto",
            city=None,
            latitude=35.6762,
            longitude=139.6503,
            casualties=0,
            injuries=0,
            affected_population=0,
            economic_impact=0.0,
            reported_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            metadata={},
        )
        
        assert incident.incident_id == "inc-123"
        assert incident.incident_type == IncidentType.EARTHQUAKE
        assert incident.severity == IncidentSeverity.MODERATE


class TestCrisisAlert:
    """Test suite for CrisisAlert dataclass."""

    def test_alert_creation(self):
        """Test creating a CrisisAlert."""
        alert = CrisisAlert(
            alert_id="alert-123",
            title="Test Alert",
            description="Test description",
            alert_level=AlertLevel.WARNING,
            incident_types=[IncidentType.TERRORISM],
            affected_countries=["United States"],
            affected_regions=[],
            is_active=True,
            issued_at=datetime.utcnow(),
            expires_at=None,
            source_incidents=[],
            metadata={},
        )
        
        assert alert.alert_id == "alert-123"
        assert alert.alert_level == AlertLevel.WARNING
        assert alert.is_active is True


class TestGeoThreatCorrelation:
    """Test suite for GeoThreatCorrelation dataclass."""

    def test_correlation_creation(self):
        """Test creating a GeoThreatCorrelation."""
        correlation = GeoThreatCorrelation(
            correlation_id="corr-123",
            global_incident_id="inc-123",
            local_threat_type="terrorism",
            correlation_score=75.0,
            distance_km=500.0,
            temporal_proximity_hours=24.0,
            pattern_match=True,
            description="Test correlation",
            created_at=datetime.utcnow(),
        )
        
        assert correlation.correlation_id == "corr-123"
        assert correlation.correlation_score == 75.0
        assert correlation.pattern_match is True
