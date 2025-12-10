"""
Tests for Data Ingestion module.
"""

import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch, AsyncMock


class TestDataIngestionManager:
    """Tests for DataIngestionManager class."""

    def test_ingestion_manager_initialization(self):
        """Test DataIngestionManager initializes correctly."""
        from backend.app.city_brain.ingestion import DataIngestionManager
        
        manager = DataIngestionManager()
        assert manager is not None

    def test_get_status_summary(self):
        """Test getting status summary from all ingestors."""
        from backend.app.city_brain.ingestion import DataIngestionManager
        
        manager = DataIngestionManager()
        summary = manager.get_status_summary()
        
        assert summary is not None
        assert "weather" in summary
        assert "marine" in summary
        assert "air_quality" in summary
        assert "traffic" in summary
        assert "power" in summary
        assert "utilities" in summary
        assert "public_safety" in summary


class TestNWSWeatherIngestor:
    """Tests for NWSWeatherIngestor class."""

    def test_weather_ingestor_initialization(self):
        """Test NWSWeatherIngestor initializes correctly."""
        from backend.app.city_brain.ingestion import NWSWeatherIngestor
        
        ingestor = NWSWeatherIngestor()
        assert ingestor is not None

    @pytest.mark.asyncio
    async def test_weather_ingestor_refresh(self):
        """Test weather data refresh."""
        from backend.app.city_brain.ingestion import NWSWeatherIngestor
        
        ingestor = NWSWeatherIngestor()
        result = await ingestor.refresh()
        
        assert result is not None
        assert result.success is True
        assert result.data is not None

    def test_weather_conditions_dataclass(self):
        """Test WeatherConditions dataclass."""
        from backend.app.city_brain.ingestion import WeatherConditions
        
        conditions = WeatherConditions(
            timestamp=datetime.utcnow(),
            temperature_f=85.0,
            humidity_percent=75,
            wind_speed_mph=12.0,
            wind_direction="SE",
            conditions="Partly Cloudy",
            visibility_miles=10.0,
            pressure_mb=1015.0,
            uv_index=8,
        )
        
        assert conditions.temperature_f == 85.0
        assert conditions.humidity_percent == 75


class TestNOAAMarineIngestor:
    """Tests for NOAAMarineIngestor class."""

    def test_marine_ingestor_initialization(self):
        """Test NOAAMarineIngestor initializes correctly."""
        from backend.app.city_brain.ingestion import NOAAMarineIngestor
        
        ingestor = NOAAMarineIngestor()
        assert ingestor is not None

    @pytest.mark.asyncio
    async def test_marine_ingestor_refresh(self):
        """Test marine data refresh."""
        from backend.app.city_brain.ingestion import NOAAMarineIngestor
        
        ingestor = NOAAMarineIngestor()
        result = await ingestor.refresh()
        
        assert result is not None
        assert result.success is True


class TestEPAAirQualityIngestor:
    """Tests for EPAAirQualityIngestor class."""

    def test_air_quality_ingestor_initialization(self):
        """Test EPAAirQualityIngestor initializes correctly."""
        from backend.app.city_brain.ingestion import EPAAirQualityIngestor
        
        ingestor = EPAAirQualityIngestor()
        assert ingestor is not None

    @pytest.mark.asyncio
    async def test_air_quality_ingestor_refresh(self):
        """Test air quality data refresh."""
        from backend.app.city_brain.ingestion import EPAAirQualityIngestor
        
        ingestor = EPAAirQualityIngestor()
        result = await ingestor.refresh()
        
        assert result is not None
        assert result.success is True

    def test_air_quality_dataclass(self):
        """Test AirQualityData dataclass."""
        from backend.app.city_brain.ingestion import AirQualityData
        
        data = AirQualityData(
            timestamp=datetime.utcnow(),
            aqi=45,
            pm25=12.5,
            pm10=25.0,
            ozone=0.035,
            category="Good",
            health_advisory=None,
        )
        
        assert data.aqi == 45
        assert data.category == "Good"


class TestFDOTTrafficIngestor:
    """Tests for FDOTTrafficIngestor class."""

    def test_traffic_ingestor_initialization(self):
        """Test FDOTTrafficIngestor initializes correctly."""
        from backend.app.city_brain.ingestion import FDOTTrafficIngestor
        
        ingestor = FDOTTrafficIngestor()
        assert ingestor is not None

    @pytest.mark.asyncio
    async def test_traffic_ingestor_refresh(self):
        """Test traffic data refresh."""
        from backend.app.city_brain.ingestion import FDOTTrafficIngestor
        
        ingestor = FDOTTrafficIngestor()
        result = await ingestor.refresh()
        
        assert result is not None
        assert result.success is True


class TestFPLOutageIngestor:
    """Tests for FPLOutageIngestor class."""

    def test_outage_ingestor_initialization(self):
        """Test FPLOutageIngestor initializes correctly."""
        from backend.app.city_brain.ingestion import FPLOutageIngestor
        
        ingestor = FPLOutageIngestor()
        assert ingestor is not None

    @pytest.mark.asyncio
    async def test_outage_ingestor_refresh(self):
        """Test outage data refresh."""
        from backend.app.city_brain.ingestion import FPLOutageIngestor
        
        ingestor = FPLOutageIngestor()
        result = await ingestor.refresh()
        
        assert result is not None
        assert result.success is True


class TestCityUtilitiesIngestor:
    """Tests for CityUtilitiesIngestor class."""

    def test_utilities_ingestor_initialization(self):
        """Test CityUtilitiesIngestor initializes correctly."""
        from backend.app.city_brain.ingestion import CityUtilitiesIngestor
        
        ingestor = CityUtilitiesIngestor()
        assert ingestor is not None

    @pytest.mark.asyncio
    async def test_utilities_ingestor_refresh(self):
        """Test utilities data refresh."""
        from backend.app.city_brain.ingestion import CityUtilitiesIngestor
        
        ingestor = CityUtilitiesIngestor()
        result = await ingestor.refresh()
        
        assert result is not None
        assert result.success is True


class TestPublicSafetyIngestor:
    """Tests for PublicSafetyIngestor class."""

    def test_public_safety_ingestor_initialization(self):
        """Test PublicSafetyIngestor initializes correctly."""
        from backend.app.city_brain.ingestion import PublicSafetyIngestor
        
        ingestor = PublicSafetyIngestor()
        assert ingestor is not None

    @pytest.mark.asyncio
    async def test_public_safety_ingestor_refresh(self):
        """Test public safety data refresh."""
        from backend.app.city_brain.ingestion import PublicSafetyIngestor
        
        ingestor = PublicSafetyIngestor()
        result = await ingestor.refresh()
        
        assert result is not None
        assert result.success is True


class TestIngestionDataclasses:
    """Tests for ingestion dataclasses."""

    def test_ingestion_result(self):
        """Test IngestionResult dataclass."""
        from backend.app.city_brain.ingestion import IngestionResult, IngestionStatus
        
        result = IngestionResult(
            source="weather",
            status=IngestionStatus.SUCCESS,
            timestamp=datetime.utcnow(),
            data={"temperature": 85},
            success=True,
            error=None,
        )
        
        assert result.success is True
        assert result.source == "weather"

    def test_traffic_incident(self):
        """Test TrafficIncident dataclass."""
        from backend.app.city_brain.ingestion import TrafficIncident
        
        incident = TrafficIncident(
            incident_id="inc-001",
            incident_type="accident",
            location="Blue Heron Blvd",
            latitude=26.7753,
            longitude=-80.0583,
            severity="major",
            description="Multi-vehicle accident",
            reported_at=datetime.utcnow(),
            estimated_clearance=None,
        )
        
        assert incident.incident_id == "inc-001"
        assert incident.severity == "major"

    def test_power_outage(self):
        """Test PowerOutage dataclass."""
        from backend.app.city_brain.ingestion import PowerOutage
        
        outage = PowerOutage(
            outage_id="out-001",
            area_name="Singer Island",
            customers_affected=500,
            cause="Equipment failure",
            start_time=datetime.utcnow(),
            estimated_restoration=None,
            status="active",
        )
        
        assert outage.outage_id == "out-001"
        assert outage.customers_affected == 500
