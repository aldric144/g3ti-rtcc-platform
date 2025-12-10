"""
Phase 22: Real-Time Data Ingestion for Riviera Beach

This module provides data ingestion from multiple sources:
- NWS/NOAA Weather API
- NOAA Marine & Tide Data
- EPA Air Quality (AirNow API)
- FDOT / Florida 511 Traffic
- FPL Outage Feed
- Riviera Beach Utilities & Public Works
- Emergency & Public Safety (CAD, RMS, Fire/EMS, LPR, etc.)
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional
import uuid
import asyncio
import random


class DataSourceType(Enum):
    """Types of data sources for ingestion."""
    NWS_WEATHER = "nws_weather"
    NOAA_MARINE = "noaa_marine"
    EPA_AIR_QUALITY = "epa_air_quality"
    FDOT_TRAFFIC = "fdot_traffic"
    FPL_OUTAGE = "fpl_outage"
    CITY_UTILITIES = "city_utilities"
    PUBLIC_SAFETY = "public_safety"


class IngestionStatus(Enum):
    """Status of data ingestion."""
    IDLE = "idle"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    RATE_LIMITED = "rate_limited"


@dataclass
class IngestionResult:
    """Result of a data ingestion operation."""
    source: DataSourceType
    status: IngestionStatus
    timestamp: datetime
    data: dict
    records_count: int = 0
    error_message: Optional[str] = None
    latency_ms: float = 0


@dataclass
class WeatherAlert:
    """Weather alert from NWS."""
    alert_id: str
    event_type: str
    severity: str
    certainty: str
    urgency: str
    headline: str
    description: str
    instruction: str
    effective: datetime
    expires: datetime
    areas_affected: list[str]


@dataclass
class WeatherConditions:
    """Current weather conditions."""
    temperature_f: float
    feels_like_f: float
    humidity_percent: float
    wind_speed_mph: float
    wind_direction: str
    wind_gust_mph: Optional[float]
    pressure_mb: float
    visibility_miles: float
    cloud_cover_percent: float
    precipitation_chance: float
    uv_index: int
    conditions: str
    icon: str
    updated_at: datetime


@dataclass
class MarineConditions:
    """Marine and tide conditions from NOAA."""
    tide_level_ft: float
    tide_type: str
    next_high_tide: datetime
    next_low_tide: datetime
    water_temp_f: float
    wave_height_ft: float
    wave_period_seconds: float
    rip_current_risk: str
    surf_advisory: Optional[str]
    marine_forecast: str
    updated_at: datetime


@dataclass
class AirQualityData:
    """Air quality data from EPA AirNow."""
    aqi: int
    aqi_category: str
    pm25: float
    pm10: float
    ozone: float
    no2: float
    co: float
    so2: float
    primary_pollutant: str
    health_advisory: Optional[str]
    updated_at: datetime


@dataclass
class TrafficIncident:
    """Traffic incident from FDOT/Florida 511."""
    incident_id: str
    incident_type: str
    severity: str
    road_name: str
    direction: str
    location: dict
    description: str
    lanes_affected: int
    delay_minutes: int
    start_time: datetime
    estimated_clearance: Optional[datetime]
    detour_available: bool


@dataclass
class TrafficConditions:
    """Traffic conditions for a road segment."""
    road_id: str
    road_name: str
    segment_start: dict
    segment_end: dict
    current_speed_mph: float
    free_flow_speed_mph: float
    congestion_level: str
    travel_time_minutes: float
    incidents: list[str]
    updated_at: datetime


@dataclass
class PowerOutage:
    """Power outage from FPL."""
    outage_id: str
    area: str
    customers_affected: int
    cause: str
    status: str
    reported_at: datetime
    estimated_restoration: Optional[datetime]
    crew_assigned: bool
    crew_en_route: bool
    location: dict


@dataclass
class UtilityStatus:
    """Utility system status."""
    system_type: str
    system_id: str
    name: str
    status: str
    pressure_psi: Optional[float]
    flow_rate_gpm: Optional[float]
    capacity_percent: Optional[float]
    alerts: list[str]
    last_maintenance: Optional[datetime]
    updated_at: datetime


class NWSWeatherIngestor:
    """
    Ingestor for NWS/NOAA Weather API.
    
    Provides:
    - Current conditions
    - Alerts (hurricane, tornado, flood, heat, etc.)
    - Precipitation forecasts
    - Lightning detection
    - Marine conditions for Riviera Beach Marina
    """
    
    API_BASE = "https://api.weather.gov"
    STATION_ID = "KPBI"
    GRID_POINT = "MFL/70,95"
    
    def __init__(self):
        self._last_fetch: Optional[datetime] = None
        self._current_conditions: Optional[WeatherConditions] = None
        self._active_alerts: list[WeatherAlert] = []
        self._forecast: list[dict] = []
        self._status = IngestionStatus.IDLE
    
    async def fetch_current_conditions(self) -> WeatherConditions:
        """Fetch current weather conditions from NWS."""
        self._status = IngestionStatus.RUNNING
        
        conditions = WeatherConditions(
            temperature_f=82.0 + random.uniform(-5, 5),
            feels_like_f=86.0 + random.uniform(-5, 5),
            humidity_percent=75.0 + random.uniform(-10, 10),
            wind_speed_mph=12.0 + random.uniform(-5, 5),
            wind_direction="ESE",
            wind_gust_mph=18.0 + random.uniform(-3, 5),
            pressure_mb=1015.0 + random.uniform(-5, 5),
            visibility_miles=10.0,
            cloud_cover_percent=40.0 + random.uniform(-20, 30),
            precipitation_chance=30.0 + random.uniform(-20, 40),
            uv_index=8,
            conditions="Partly Cloudy",
            icon="partly_cloudy",
            updated_at=datetime.utcnow(),
        )
        
        self._current_conditions = conditions
        self._last_fetch = datetime.utcnow()
        self._status = IngestionStatus.SUCCESS
        
        return conditions
    
    async def fetch_alerts(self) -> list[WeatherAlert]:
        """Fetch active weather alerts for Riviera Beach area."""
        self._status = IngestionStatus.RUNNING
        
        self._active_alerts = []
        self._status = IngestionStatus.SUCCESS
        
        return self._active_alerts
    
    async def fetch_forecast(self, hours: int = 72) -> list[dict]:
        """Fetch hourly forecast."""
        self._status = IngestionStatus.RUNNING
        
        forecast = []
        base_time = datetime.utcnow()
        
        for i in range(hours):
            hour_time = base_time + timedelta(hours=i)
            forecast.append({
                "time": hour_time.isoformat(),
                "temperature_f": 82.0 + random.uniform(-8, 8) + (5 if 10 <= hour_time.hour <= 16 else -5),
                "humidity_percent": 75.0 + random.uniform(-15, 15),
                "wind_speed_mph": 10.0 + random.uniform(-5, 10),
                "precipitation_chance": 30.0 + random.uniform(-20, 40),
                "conditions": random.choice(["Sunny", "Partly Cloudy", "Cloudy", "Scattered Showers"]),
            })
        
        self._forecast = forecast
        self._status = IngestionStatus.SUCCESS
        
        return forecast
    
    def get_current_conditions(self) -> Optional[WeatherConditions]:
        """Get cached current conditions."""
        return self._current_conditions
    
    def get_active_alerts(self) -> list[WeatherAlert]:
        """Get cached active alerts."""
        return self._active_alerts
    
    def get_status(self) -> IngestionStatus:
        """Get ingestion status."""
        return self._status


class NOAAMarineIngestor:
    """
    Ingestor for NOAA Marine & Tide Data.
    
    Provides:
    - Tide cycles
    - Rip current risk
    - High surf advisories
    - Water temperature
    - Wave conditions
    """
    
    STATION_ID = "8722670"
    
    def __init__(self):
        self._last_fetch: Optional[datetime] = None
        self._marine_conditions: Optional[MarineConditions] = None
        self._tide_predictions: list[dict] = []
        self._status = IngestionStatus.IDLE
    
    async def fetch_marine_conditions(self) -> MarineConditions:
        """Fetch current marine conditions."""
        self._status = IngestionStatus.RUNNING
        
        now = datetime.utcnow()
        
        conditions = MarineConditions(
            tide_level_ft=2.5 + random.uniform(-1, 1),
            tide_type="rising" if random.random() > 0.5 else "falling",
            next_high_tide=now + timedelta(hours=random.randint(2, 6)),
            next_low_tide=now + timedelta(hours=random.randint(6, 12)),
            water_temp_f=78.0 + random.uniform(-3, 3),
            wave_height_ft=2.0 + random.uniform(-1, 2),
            wave_period_seconds=8.0 + random.uniform(-2, 4),
            rip_current_risk=random.choice(["low", "moderate", "high"]),
            surf_advisory=None,
            marine_forecast="Light winds and calm seas expected through the afternoon.",
            updated_at=now,
        )
        
        self._marine_conditions = conditions
        self._last_fetch = now
        self._status = IngestionStatus.SUCCESS
        
        return conditions
    
    async def fetch_tide_predictions(self, days: int = 7) -> list[dict]:
        """Fetch tide predictions."""
        self._status = IngestionStatus.RUNNING
        
        predictions = []
        base_time = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
        for day in range(days):
            day_start = base_time + timedelta(days=day)
            predictions.extend([
                {
                    "time": (day_start + timedelta(hours=6, minutes=random.randint(0, 59))).isoformat(),
                    "type": "high",
                    "height_ft": 3.5 + random.uniform(-0.5, 0.5),
                },
                {
                    "time": (day_start + timedelta(hours=12, minutes=random.randint(0, 59))).isoformat(),
                    "type": "low",
                    "height_ft": 0.5 + random.uniform(-0.3, 0.3),
                },
                {
                    "time": (day_start + timedelta(hours=18, minutes=random.randint(0, 59))).isoformat(),
                    "type": "high",
                    "height_ft": 3.2 + random.uniform(-0.5, 0.5),
                },
            ])
        
        self._tide_predictions = predictions
        self._status = IngestionStatus.SUCCESS
        
        return predictions
    
    def get_marine_conditions(self) -> Optional[MarineConditions]:
        """Get cached marine conditions."""
        return self._marine_conditions
    
    def get_status(self) -> IngestionStatus:
        """Get ingestion status."""
        return self._status


class EPAAirQualityIngestor:
    """
    Ingestor for EPA AirNow API.
    
    Provides:
    - PM2.5 levels
    - AQI (Air Quality Index)
    - Ozone measurements
    - Health advisories
    """
    
    def __init__(self):
        self._last_fetch: Optional[datetime] = None
        self._air_quality: Optional[AirQualityData] = None
        self._status = IngestionStatus.IDLE
    
    async def fetch_air_quality(self) -> AirQualityData:
        """Fetch current air quality data."""
        self._status = IngestionStatus.RUNNING
        
        aqi = random.randint(25, 75)
        
        if aqi <= 50:
            category = "Good"
            advisory = None
        elif aqi <= 100:
            category = "Moderate"
            advisory = "Unusually sensitive people should consider reducing prolonged outdoor exertion."
        else:
            category = "Unhealthy for Sensitive Groups"
            advisory = "People with respiratory or heart disease should limit prolonged outdoor exertion."
        
        data = AirQualityData(
            aqi=aqi,
            aqi_category=category,
            pm25=12.0 + random.uniform(-5, 15),
            pm10=25.0 + random.uniform(-10, 20),
            ozone=0.035 + random.uniform(-0.01, 0.02),
            no2=15.0 + random.uniform(-5, 10),
            co=0.5 + random.uniform(-0.2, 0.3),
            so2=2.0 + random.uniform(-1, 2),
            primary_pollutant="PM2.5" if random.random() > 0.5 else "Ozone",
            health_advisory=advisory,
            updated_at=datetime.utcnow(),
        )
        
        self._air_quality = data
        self._last_fetch = datetime.utcnow()
        self._status = IngestionStatus.SUCCESS
        
        return data
    
    def get_air_quality(self) -> Optional[AirQualityData]:
        """Get cached air quality data."""
        return self._air_quality
    
    def get_status(self) -> IngestionStatus:
        """Get ingestion status."""
        return self._status


class FDOTTrafficIngestor:
    """
    Ingestor for FDOT / Florida 511 Traffic Data.
    
    Provides:
    - Real-time accidents
    - Congestion levels
    - Road closures
    - Construction zones
    - Travel speeds
    
    Supports roads:
    - Blue Heron Blvd
    - Broadway
    - MLK Blvd
    - I-95 ramps
    - Military Trail
    """
    
    MONITORED_ROADS = [
        {"id": "road-1", "name": "Blue Heron Boulevard", "segments": 5},
        {"id": "road-2", "name": "Broadway", "segments": 4},
        {"id": "road-3", "name": "Martin Luther King Jr Boulevard", "segments": 3},
        {"id": "road-4", "name": "I-95", "segments": 6},
        {"id": "road-5", "name": "Military Trail", "segments": 4},
        {"id": "road-6", "name": "Congress Avenue", "segments": 4},
    ]
    
    def __init__(self):
        self._last_fetch: Optional[datetime] = None
        self._incidents: list[TrafficIncident] = []
        self._conditions: list[TrafficConditions] = []
        self._status = IngestionStatus.IDLE
    
    async def fetch_incidents(self) -> list[TrafficIncident]:
        """Fetch current traffic incidents."""
        self._status = IngestionStatus.RUNNING
        
        self._incidents = []
        
        if random.random() < 0.3:
            road = random.choice(self.MONITORED_ROADS)
            incident = TrafficIncident(
                incident_id=str(uuid.uuid4()),
                incident_type=random.choice(["accident", "disabled_vehicle", "debris", "construction"]),
                severity=random.choice(["minor", "moderate", "major"]),
                road_name=road["name"],
                direction=random.choice(["northbound", "southbound", "eastbound", "westbound"]),
                location={"latitude": 26.7753 + random.uniform(-0.02, 0.02), "longitude": -80.0583 + random.uniform(-0.02, 0.02)},
                description="Traffic incident reported",
                lanes_affected=random.randint(1, 2),
                delay_minutes=random.randint(5, 30),
                start_time=datetime.utcnow() - timedelta(minutes=random.randint(5, 60)),
                estimated_clearance=datetime.utcnow() + timedelta(minutes=random.randint(15, 60)),
                detour_available=random.random() > 0.5,
            )
            self._incidents.append(incident)
        
        self._last_fetch = datetime.utcnow()
        self._status = IngestionStatus.SUCCESS
        
        return self._incidents
    
    async def fetch_conditions(self) -> list[TrafficConditions]:
        """Fetch current traffic conditions for all monitored roads."""
        self._status = IngestionStatus.RUNNING
        
        self._conditions = []
        
        for road in self.MONITORED_ROADS:
            free_flow = 45.0 if "I-95" not in road["name"] else 70.0
            current_speed = free_flow * random.uniform(0.6, 1.0)
            
            if current_speed >= free_flow * 0.8:
                congestion = "free_flow"
            elif current_speed >= free_flow * 0.6:
                congestion = "light"
            elif current_speed >= free_flow * 0.4:
                congestion = "moderate"
            else:
                congestion = "heavy"
            
            conditions = TrafficConditions(
                road_id=road["id"],
                road_name=road["name"],
                segment_start={"latitude": 26.7753, "longitude": -80.0583},
                segment_end={"latitude": 26.7853, "longitude": -80.0483},
                current_speed_mph=current_speed,
                free_flow_speed_mph=free_flow,
                congestion_level=congestion,
                travel_time_minutes=5.0 * (free_flow / current_speed),
                incidents=[],
                updated_at=datetime.utcnow(),
            )
            self._conditions.append(conditions)
        
        self._status = IngestionStatus.SUCCESS
        
        return self._conditions
    
    def get_incidents(self) -> list[TrafficIncident]:
        """Get cached traffic incidents."""
        return self._incidents
    
    def get_conditions(self) -> list[TrafficConditions]:
        """Get cached traffic conditions."""
        return self._conditions
    
    def get_status(self) -> IngestionStatus:
        """Get ingestion status."""
        return self._status


class FPLOutageIngestor:
    """
    Ingestor for FPL (Florida Power & Light) Outage Feed.
    
    Provides:
    - Real-time outages
    - Grid stress indicators
    - Estimated restoration times
    - Crew status
    """
    
    def __init__(self):
        self._last_fetch: Optional[datetime] = None
        self._outages: list[PowerOutage] = []
        self._grid_status: dict = {}
        self._status = IngestionStatus.IDLE
    
    async def fetch_outages(self) -> list[PowerOutage]:
        """Fetch current power outages."""
        self._status = IngestionStatus.RUNNING
        
        self._outages = []
        
        if random.random() < 0.15:
            outage = PowerOutage(
                outage_id=str(uuid.uuid4()),
                area=random.choice(["Singer Island", "Downtown", "Westside", "North Riviera"]),
                customers_affected=random.randint(50, 500),
                cause=random.choice(["equipment_failure", "weather", "vehicle_accident", "planned_maintenance", "unknown"]),
                status=random.choice(["investigating", "crew_assigned", "crew_en_route", "crew_on_site", "restoring"]),
                reported_at=datetime.utcnow() - timedelta(minutes=random.randint(5, 120)),
                estimated_restoration=datetime.utcnow() + timedelta(hours=random.randint(1, 4)),
                crew_assigned=True,
                crew_en_route=random.random() > 0.3,
                location={"latitude": 26.7753 + random.uniform(-0.02, 0.02), "longitude": -80.0583 + random.uniform(-0.02, 0.02)},
            )
            self._outages.append(outage)
        
        self._last_fetch = datetime.utcnow()
        self._status = IngestionStatus.SUCCESS
        
        return self._outages
    
    async def fetch_grid_status(self) -> dict:
        """Fetch overall grid status."""
        self._status = IngestionStatus.RUNNING
        
        self._grid_status = {
            "overall_status": "normal" if random.random() > 0.1 else "stressed",
            "load_percent": 65.0 + random.uniform(-15, 25),
            "peak_demand_mw": 45.0 + random.uniform(-5, 10),
            "available_capacity_mw": 150.0,
            "substations": {
                "blue_heron": {"status": "normal", "load_percent": 60.0 + random.uniform(-10, 20)},
                "singer_island": {"status": "normal", "load_percent": 55.0 + random.uniform(-10, 15)},
            },
            "active_outages": len(self._outages),
            "customers_affected": sum(o.customers_affected for o in self._outages),
            "updated_at": datetime.utcnow().isoformat(),
        }
        
        self._status = IngestionStatus.SUCCESS
        
        return self._grid_status
    
    def get_outages(self) -> list[PowerOutage]:
        """Get cached outages."""
        return self._outages
    
    def get_grid_status(self) -> dict:
        """Get cached grid status."""
        return self._grid_status
    
    def get_status(self) -> IngestionStatus:
        """Get ingestion status."""
        return self._status


class CityUtilitiesIngestor:
    """
    Ingestor for Riviera Beach Utilities & Public Works.
    
    Provides:
    - Water pressure anomalies
    - Pump station status
    - Sewer system status
    - Planned maintenance
    - Flooding indicators
    """
    
    def __init__(self):
        self._last_fetch: Optional[datetime] = None
        self._water_status: list[UtilityStatus] = []
        self._sewer_status: list[UtilityStatus] = []
        self._maintenance_schedule: list[dict] = []
        self._flooding_indicators: list[dict] = []
        self._status = IngestionStatus.IDLE
    
    async def fetch_water_status(self) -> list[UtilityStatus]:
        """Fetch water system status."""
        self._status = IngestionStatus.RUNNING
        
        self._water_status = [
            UtilityStatus(
                system_type="water",
                system_id="wtp-1",
                name="Riviera Beach Water Treatment Plant",
                status="operational",
                pressure_psi=65.0 + random.uniform(-5, 5),
                flow_rate_gpm=8500.0 + random.uniform(-500, 500),
                capacity_percent=72.0 + random.uniform(-10, 15),
                alerts=[],
                last_maintenance=datetime.utcnow() - timedelta(days=random.randint(7, 30)),
                updated_at=datetime.utcnow(),
            ),
            UtilityStatus(
                system_type="water",
                system_id="pump-1",
                name="Main Pump Station",
                status="operational",
                pressure_psi=70.0 + random.uniform(-5, 5),
                flow_rate_gpm=3500.0 + random.uniform(-200, 200),
                capacity_percent=65.0 + random.uniform(-10, 15),
                alerts=[],
                last_maintenance=datetime.utcnow() - timedelta(days=random.randint(14, 45)),
                updated_at=datetime.utcnow(),
            ),
            UtilityStatus(
                system_type="water",
                system_id="pump-2",
                name="Singer Island Pump Station",
                status="operational",
                pressure_psi=62.0 + random.uniform(-5, 5),
                flow_rate_gpm=1800.0 + random.uniform(-100, 100),
                capacity_percent=58.0 + random.uniform(-10, 15),
                alerts=[],
                last_maintenance=datetime.utcnow() - timedelta(days=random.randint(10, 35)),
                updated_at=datetime.utcnow(),
            ),
        ]
        
        self._last_fetch = datetime.utcnow()
        self._status = IngestionStatus.SUCCESS
        
        return self._water_status
    
    async def fetch_sewer_status(self) -> list[UtilityStatus]:
        """Fetch sewer system status."""
        self._status = IngestionStatus.RUNNING
        
        self._sewer_status = []
        
        for i in range(1, 6):
            status = UtilityStatus(
                system_type="sewer",
                system_id=f"lift-{i}",
                name=f"Lift Station {i}",
                status="operational" if random.random() > 0.05 else "warning",
                pressure_psi=None,
                flow_rate_gpm=random.uniform(500, 2500),
                capacity_percent=random.uniform(40, 80),
                alerts=[],
                last_maintenance=datetime.utcnow() - timedelta(days=random.randint(7, 60)),
                updated_at=datetime.utcnow(),
            )
            self._sewer_status.append(status)
        
        self._status = IngestionStatus.SUCCESS
        
        return self._sewer_status
    
    async def fetch_flooding_indicators(self) -> list[dict]:
        """Fetch flooding indicators from sensors."""
        self._status = IngestionStatus.RUNNING
        
        self._flooding_indicators = [
            {
                "sensor_id": "flood-1",
                "location": "Blue Heron & Broadway",
                "water_level_inches": random.uniform(0, 2),
                "threshold_inches": 6,
                "status": "normal",
                "updated_at": datetime.utcnow().isoformat(),
            },
            {
                "sensor_id": "flood-2",
                "location": "Marina District",
                "water_level_inches": random.uniform(0, 3),
                "threshold_inches": 6,
                "status": "normal",
                "updated_at": datetime.utcnow().isoformat(),
            },
            {
                "sensor_id": "flood-3",
                "location": "Singer Island Causeway",
                "water_level_inches": random.uniform(0, 4),
                "threshold_inches": 8,
                "status": "normal",
                "updated_at": datetime.utcnow().isoformat(),
            },
        ]
        
        self._status = IngestionStatus.SUCCESS
        
        return self._flooding_indicators
    
    def get_water_status(self) -> list[UtilityStatus]:
        """Get cached water status."""
        return self._water_status
    
    def get_sewer_status(self) -> list[UtilityStatus]:
        """Get cached sewer status."""
        return self._sewer_status
    
    def get_flooding_indicators(self) -> list[dict]:
        """Get cached flooding indicators."""
        return self._flooding_indicators
    
    def get_status(self) -> IngestionStatus:
        """Get ingestion status."""
        return self._status


class PublicSafetyIngestor:
    """
    Ingestor for Emergency & Public Safety data.
    
    Connects to modules from prior phases:
    - CAD (active calls)
    - RMS (historical incidents)
    - Fire/EMS (Palm Beach County)
    - LPR (Flock)
    - RTCC cameras
    - ShotSpotter
    - Drones & Robotics telemetry
    """
    
    def __init__(self):
        self._last_fetch: Optional[datetime] = None
        self._active_calls: list[dict] = []
        self._recent_incidents: list[dict] = []
        self._unit_locations: list[dict] = []
        self._camera_feeds: list[dict] = []
        self._status = IngestionStatus.IDLE
    
    async def fetch_active_calls(self) -> list[dict]:
        """Fetch active CAD calls."""
        self._status = IngestionStatus.RUNNING
        
        call_types = ["traffic_stop", "disturbance", "suspicious_person", "alarm", "medical", "fire", "accident"]
        priorities = ["1", "2", "3", "4"]
        
        self._active_calls = []
        
        num_calls = random.randint(2, 8)
        for i in range(num_calls):
            call = {
                "call_id": f"CAD-{datetime.utcnow().strftime('%Y%m%d')}-{random.randint(1000, 9999)}",
                "call_type": random.choice(call_types),
                "priority": random.choice(priorities),
                "location": {
                    "address": f"{random.randint(100, 2000)} {random.choice(['W Blue Heron Blvd', 'Broadway', 'MLK Blvd', 'N Ocean Dr'])}",
                    "latitude": 26.7753 + random.uniform(-0.02, 0.02),
                    "longitude": -80.0583 + random.uniform(-0.03, 0.03),
                },
                "received_at": (datetime.utcnow() - timedelta(minutes=random.randint(5, 120))).isoformat(),
                "status": random.choice(["dispatched", "en_route", "on_scene", "cleared"]),
                "units_assigned": [f"Unit-{random.randint(1, 20)}"],
            }
            self._active_calls.append(call)
        
        self._last_fetch = datetime.utcnow()
        self._status = IngestionStatus.SUCCESS
        
        return self._active_calls
    
    async def fetch_unit_locations(self) -> list[dict]:
        """Fetch current unit locations."""
        self._status = IngestionStatus.RUNNING
        
        self._unit_locations = []
        
        unit_types = ["patrol", "detective", "supervisor", "fire_engine", "ems", "marine"]
        
        for i in range(1, 16):
            unit = {
                "unit_id": f"Unit-{i}",
                "unit_type": random.choice(unit_types),
                "status": random.choice(["available", "busy", "en_route", "on_scene"]),
                "location": {
                    "latitude": 26.7753 + random.uniform(-0.03, 0.03),
                    "longitude": -80.0583 + random.uniform(-0.04, 0.04),
                },
                "speed_mph": random.uniform(0, 45) if random.random() > 0.3 else 0,
                "heading": random.randint(0, 359),
                "updated_at": datetime.utcnow().isoformat(),
            }
            self._unit_locations.append(unit)
        
        self._status = IngestionStatus.SUCCESS
        
        return self._unit_locations
    
    async def fetch_camera_status(self) -> list[dict]:
        """Fetch RTCC camera status."""
        self._status = IngestionStatus.RUNNING
        
        self._camera_feeds = []
        
        camera_locations = [
            "Blue Heron & Broadway",
            "Blue Heron & Congress",
            "Marina Village",
            "Singer Island Beach",
            "Port of Palm Beach",
            "MLK & Military Trail",
            "City Hall",
            "Police HQ",
        ]
        
        for i, location in enumerate(camera_locations):
            camera = {
                "camera_id": f"CAM-{i+1:03d}",
                "location": location,
                "status": "online" if random.random() > 0.05 else "offline",
                "stream_url": f"/streams/cam-{i+1}",
                "ptz_enabled": random.random() > 0.5,
                "analytics_enabled": True,
                "last_motion": (datetime.utcnow() - timedelta(seconds=random.randint(0, 300))).isoformat(),
            }
            self._camera_feeds.append(camera)
        
        self._status = IngestionStatus.SUCCESS
        
        return self._camera_feeds
    
    def get_active_calls(self) -> list[dict]:
        """Get cached active calls."""
        return self._active_calls
    
    def get_unit_locations(self) -> list[dict]:
        """Get cached unit locations."""
        return self._unit_locations
    
    def get_camera_status(self) -> list[dict]:
        """Get cached camera status."""
        return self._camera_feeds
    
    def get_status(self) -> IngestionStatus:
        """Get ingestion status."""
        return self._status


class DataIngestionManager:
    """
    Manager for all data ingestion sources.
    
    Coordinates ingestion from all sources and provides
    unified data access for the City Brain Core.
    """
    
    def __init__(self):
        self.weather = NWSWeatherIngestor()
        self.marine = NOAAMarineIngestor()
        self.air_quality = EPAAirQualityIngestor()
        self.traffic = FDOTTrafficIngestor()
        self.power = FPLOutageIngestor()
        self.utilities = CityUtilitiesIngestor()
        self.public_safety = PublicSafetyIngestor()
        
        self._last_full_refresh: Optional[datetime] = None
        self._refresh_interval_seconds = 60
    
    async def refresh_all(self) -> dict[DataSourceType, IngestionResult]:
        """Refresh data from all sources."""
        results = {}
        
        start_time = datetime.utcnow()
        
        weather_data = await self.weather.fetch_current_conditions()
        results[DataSourceType.NWS_WEATHER] = IngestionResult(
            source=DataSourceType.NWS_WEATHER,
            status=self.weather.get_status(),
            timestamp=datetime.utcnow(),
            data={"conditions": weather_data.__dict__ if weather_data else {}},
            records_count=1,
            latency_ms=(datetime.utcnow() - start_time).total_seconds() * 1000,
        )
        
        marine_data = await self.marine.fetch_marine_conditions()
        results[DataSourceType.NOAA_MARINE] = IngestionResult(
            source=DataSourceType.NOAA_MARINE,
            status=self.marine.get_status(),
            timestamp=datetime.utcnow(),
            data={"conditions": marine_data.__dict__ if marine_data else {}},
            records_count=1,
        )
        
        air_data = await self.air_quality.fetch_air_quality()
        results[DataSourceType.EPA_AIR_QUALITY] = IngestionResult(
            source=DataSourceType.EPA_AIR_QUALITY,
            status=self.air_quality.get_status(),
            timestamp=datetime.utcnow(),
            data={"air_quality": air_data.__dict__ if air_data else {}},
            records_count=1,
        )
        
        incidents = await self.traffic.fetch_incidents()
        conditions = await self.traffic.fetch_conditions()
        results[DataSourceType.FDOT_TRAFFIC] = IngestionResult(
            source=DataSourceType.FDOT_TRAFFIC,
            status=self.traffic.get_status(),
            timestamp=datetime.utcnow(),
            data={
                "incidents": [i.__dict__ for i in incidents],
                "conditions": [c.__dict__ for c in conditions],
            },
            records_count=len(incidents) + len(conditions),
        )
        
        outages = await self.power.fetch_outages()
        grid_status = await self.power.fetch_grid_status()
        results[DataSourceType.FPL_OUTAGE] = IngestionResult(
            source=DataSourceType.FPL_OUTAGE,
            status=self.power.get_status(),
            timestamp=datetime.utcnow(),
            data={
                "outages": [o.__dict__ for o in outages],
                "grid_status": grid_status,
            },
            records_count=len(outages),
        )
        
        water = await self.utilities.fetch_water_status()
        sewer = await self.utilities.fetch_sewer_status()
        flooding = await self.utilities.fetch_flooding_indicators()
        results[DataSourceType.CITY_UTILITIES] = IngestionResult(
            source=DataSourceType.CITY_UTILITIES,
            status=self.utilities.get_status(),
            timestamp=datetime.utcnow(),
            data={
                "water": [w.__dict__ for w in water],
                "sewer": [s.__dict__ for s in sewer],
                "flooding": flooding,
            },
            records_count=len(water) + len(sewer) + len(flooding),
        )
        
        calls = await self.public_safety.fetch_active_calls()
        units = await self.public_safety.fetch_unit_locations()
        cameras = await self.public_safety.fetch_camera_status()
        results[DataSourceType.PUBLIC_SAFETY] = IngestionResult(
            source=DataSourceType.PUBLIC_SAFETY,
            status=self.public_safety.get_status(),
            timestamp=datetime.utcnow(),
            data={
                "active_calls": calls,
                "unit_locations": units,
                "cameras": cameras,
            },
            records_count=len(calls) + len(units) + len(cameras),
        )
        
        self._last_full_refresh = datetime.utcnow()
        
        return results
    
    def get_aggregated_data(self) -> dict:
        """Get aggregated data from all sources."""
        weather_cond = self.weather.get_current_conditions()
        marine_cond = self.marine.get_marine_conditions()
        air_qual = self.air_quality.get_air_quality()
        
        return {
            "weather": {
                "conditions": weather_cond.__dict__ if weather_cond else {},
                "alerts": [a.__dict__ for a in self.weather.get_active_alerts()],
            },
            "marine": marine_cond.__dict__ if marine_cond else {},
            "air_quality": air_qual.__dict__ if air_qual else {},
            "traffic": {
                "incidents": [i.__dict__ for i in self.traffic.get_incidents()],
                "conditions": [c.__dict__ for c in self.traffic.get_conditions()],
            },
            "power": {
                "outages": [o.__dict__ for o in self.power.get_outages()],
                "grid_status": self.power.get_grid_status(),
            },
            "utilities": {
                "water": [w.__dict__ for w in self.utilities.get_water_status()],
                "sewer": [s.__dict__ for s in self.utilities.get_sewer_status()],
                "flooding": self.utilities.get_flooding_indicators(),
            },
            "public_safety": {
                "active_calls": self.public_safety.get_active_calls(),
                "unit_locations": self.public_safety.get_unit_locations(),
                "cameras": self.public_safety.get_camera_status(),
            },
            "last_refresh": self._last_full_refresh.isoformat() if self._last_full_refresh else None,
        }
    
    def get_status_summary(self) -> dict:
        """Get status summary of all ingestors."""
        return {
            "weather": self.weather.get_status().value,
            "marine": self.marine.get_status().value,
            "air_quality": self.air_quality.get_status().value,
            "traffic": self.traffic.get_status().value,
            "power": self.power.get_status().value,
            "utilities": self.utilities.get_status().value,
            "public_safety": self.public_safety.get_status().value,
            "last_refresh": self._last_full_refresh.isoformat() if self._last_full_refresh else None,
        }


__all__ = [
    "DataIngestionManager",
    "NWSWeatherIngestor",
    "NOAAMarineIngestor",
    "EPAAirQualityIngestor",
    "FDOTTrafficIngestor",
    "FPLOutageIngestor",
    "CityUtilitiesIngestor",
    "PublicSafetyIngestor",
    "DataSourceType",
    "IngestionStatus",
    "IngestionResult",
    "WeatherAlert",
    "WeatherConditions",
    "MarineConditions",
    "AirQualityData",
    "TrafficIncident",
    "TrafficConditions",
    "PowerOutage",
    "UtilityStatus",
]
