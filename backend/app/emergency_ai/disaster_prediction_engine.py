"""
Phase 31: Multi-Hazard Disaster Prediction Engine

Predictive models for:
- Severe Weather (Hurricanes, Tornadoes, Flooding)
- Urban Fire Spread Prediction
- Chemical / Hazmat Release Modeling
- Infrastructure Collapse Prediction

City: Riviera Beach, Florida 33404
Agency ORI: FL0500400
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
import hashlib
import json
import uuid
import math


class HazardType(Enum):
    """Types of hazards"""
    HURRICANE = "hurricane"
    TORNADO = "tornado"
    FLOODING = "flooding"
    STORM_SURGE = "storm_surge"
    SEVERE_THUNDERSTORM = "severe_thunderstorm"
    URBAN_FIRE = "urban_fire"
    WILDFIRE = "wildfire"
    HAZMAT_RELEASE = "hazmat_release"
    CHEMICAL_SPILL = "chemical_spill"
    BRIDGE_COLLAPSE = "bridge_collapse"
    SEAWALL_FAILURE = "seawall_failure"
    POWER_GRID_FAILURE = "power_grid_failure"
    ROADWAY_SUBSIDENCE = "roadway_subsidence"
    CANAL_BREACH = "canal_breach"


class ThreatLevel(Enum):
    """Threat severity levels (1-5)"""
    MINIMAL = 1
    LOW = 2
    MODERATE = 3
    HIGH = 4
    EXTREME = 5


class WeatherDataSource(Enum):
    """Weather data sources"""
    NOAA = "noaa"
    NHC = "nhc"
    NWS = "nws"
    LOCAL_SENSORS = "local_sensors"
    RADAR = "radar"
    SATELLITE = "satellite"


@dataclass
class WeatherHazard:
    """Weather hazard data"""
    hazard_id: str
    hazard_type: HazardType
    timestamp: datetime
    threat_level: ThreatLevel
    storm_name: Optional[str] = None
    category: Optional[int] = None
    wind_speed_mph: float = 0.0
    wind_direction: str = ""
    pressure_mb: float = 0.0
    movement_speed_mph: float = 0.0
    movement_direction: str = ""
    rainfall_inches: float = 0.0
    storm_surge_feet: float = 0.0
    tornado_probability: float = 0.0
    track_coordinates: List[Tuple[float, float]] = field(default_factory=list)
    cone_of_uncertainty: List[Tuple[float, float]] = field(default_factory=list)
    time_to_impact_hours: float = 0.0
    affected_zones: List[str] = field(default_factory=list)
    data_sources: List[str] = field(default_factory=list)
    confidence_score: float = 0.0
    
    def __post_init__(self):
        self.chain_of_custody_hash = self._generate_hash()
    
    def _generate_hash(self) -> str:
        data = f"{self.hazard_id}:{self.timestamp.isoformat()}:{self.hazard_type.value}:{self.threat_level.value}"
        return hashlib.sha256(data.encode()).hexdigest()


@dataclass
class FloodPrediction:
    """Street-level flood prediction"""
    prediction_id: str
    timestamp: datetime
    zone: str
    street_address: Optional[str] = None
    flood_probability: float = 0.0
    expected_depth_inches: float = 0.0
    time_to_flood_hours: float = 0.0
    drainage_capacity_percent: float = 100.0
    elevation_feet: float = 0.0
    risk_factors: List[str] = field(default_factory=list)
    recommended_actions: List[str] = field(default_factory=list)
    confidence_score: float = 0.0


@dataclass
class FireHazard:
    """Urban fire spread prediction"""
    hazard_id: str
    timestamp: datetime
    threat_level: ThreatLevel
    origin_location: Tuple[float, float] = (0.0, 0.0)
    origin_zone: str = ""
    fire_type: str = "structure"
    current_size_acres: float = 0.0
    spread_rate_acres_per_hour: float = 0.0
    wind_speed_mph: float = 0.0
    wind_direction: str = ""
    humidity_percent: float = 0.0
    temperature_f: float = 0.0
    structure_density: str = "medium"
    time_to_critical_hours: float = 0.0
    affected_structures: int = 0
    vulnerable_structures: List[Dict[str, Any]] = field(default_factory=list)
    hydrant_availability: Dict[str, bool] = field(default_factory=dict)
    evacuation_required: bool = False
    affected_zones: List[str] = field(default_factory=list)
    recommended_actions: List[str] = field(default_factory=list)
    confidence_score: float = 0.0
    
    def __post_init__(self):
        self.chain_of_custody_hash = self._generate_hash()
    
    def _generate_hash(self) -> str:
        data = f"{self.hazard_id}:{self.timestamp.isoformat()}:{self.threat_level.value}"
        return hashlib.sha256(data.encode()).hexdigest()


@dataclass
class HazmatHazard:
    """Chemical/Hazmat release modeling"""
    hazard_id: str
    timestamp: datetime
    threat_level: ThreatLevel
    chemical_name: str = ""
    chemical_class: str = ""
    release_type: str = "spill"
    release_quantity_gallons: float = 0.0
    origin_location: Tuple[float, float] = (0.0, 0.0)
    origin_zone: str = ""
    plume_direction: str = ""
    plume_speed_mph: float = 0.0
    affected_radius_miles: float = 0.0
    evacuation_radius_miles: float = 0.0
    shelter_in_place_radius_miles: float = 0.0
    health_effects: List[str] = field(default_factory=list)
    exposure_duration_safe_minutes: float = 0.0
    decontamination_required: bool = False
    water_contamination_risk: bool = False
    affected_population: int = 0
    affected_zones: List[str] = field(default_factory=list)
    evacuation_priority_zones: List[str] = field(default_factory=list)
    recommended_actions: List[str] = field(default_factory=list)
    agencies_required: List[str] = field(default_factory=list)
    confidence_score: float = 0.0
    
    def __post_init__(self):
        self.chain_of_custody_hash = self._generate_hash()
    
    def _generate_hash(self) -> str:
        data = f"{self.hazard_id}:{self.timestamp.isoformat()}:{self.chemical_name}:{self.threat_level.value}"
        return hashlib.sha256(data.encode()).hexdigest()


@dataclass
class InfrastructureHazard:
    """Infrastructure collapse/failure prediction"""
    hazard_id: str
    timestamp: datetime
    threat_level: ThreatLevel
    infrastructure_type: str = ""
    infrastructure_name: str = ""
    location: Tuple[float, float] = (0.0, 0.0)
    zone: str = ""
    failure_probability: float = 0.0
    stress_level_percent: float = 0.0
    anomaly_detected: bool = False
    anomaly_type: str = ""
    last_inspection_date: Optional[datetime] = None
    age_years: int = 0
    condition_rating: str = "fair"
    affected_population: int = 0
    traffic_impact: str = "none"
    utility_impact: List[str] = field(default_factory=list)
    time_to_failure_hours: Optional[float] = None
    affected_zones: List[str] = field(default_factory=list)
    recommended_actions: List[str] = field(default_factory=list)
    agencies_required: List[str] = field(default_factory=list)
    confidence_score: float = 0.0
    
    def __post_init__(self):
        self.chain_of_custody_hash = self._generate_hash()
    
    def _generate_hash(self) -> str:
        data = f"{self.hazard_id}:{self.timestamp.isoformat()}:{self.infrastructure_type}:{self.threat_level.value}"
        return hashlib.sha256(data.encode()).hexdigest()


@dataclass
class HazardPrediction:
    """Unified hazard prediction output"""
    prediction_id: str
    timestamp: datetime
    hazard_type: HazardType
    threat_level: ThreatLevel
    confidence_score: float
    time_to_impact_hours: float
    affected_zones: List[str]
    affected_population: int
    recommended_actions: List[str]
    agencies_required: List[str]
    potential_casualties_prevented: int
    economic_impact_estimate: float
    weather_hazard: Optional[WeatherHazard] = None
    fire_hazard: Optional[FireHazard] = None
    hazmat_hazard: Optional[HazmatHazard] = None
    infrastructure_hazard: Optional[InfrastructureHazard] = None
    flood_predictions: List[FloodPrediction] = field(default_factory=list)
    
    def __post_init__(self):
        self.chain_of_custody_hash = self._generate_hash()
    
    def _generate_hash(self) -> str:
        data = f"{self.prediction_id}:{self.timestamp.isoformat()}:{self.hazard_type.value}:{self.threat_level.value}"
        return hashlib.sha256(data.encode()).hexdigest()


class DisasterPredictionEngine:
    """
    Multi-Hazard Disaster Prediction Engine
    
    Provides predictive models for severe weather, urban fires,
    hazmat releases, and infrastructure failures.
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        
        self.agency_config = {
            "ori": "FL0500400",
            "city": "Riviera Beach",
            "state": "FL",
            "zip": "33404",
            "county": "Palm Beach",
            "latitude": 26.7753,
            "longitude": -80.0583,
        }
        
        self.city_zones = [
            "Zone_A", "Zone_B", "Zone_C", "Zone_D", "Zone_E",
            "Zone_F", "Zone_G", "Zone_H", "Zone_I", "Zone_J",
        ]
        
        self.zone_populations = {
            "Zone_A": 3500, "Zone_B": 4200, "Zone_C": 3800,
            "Zone_D": 2900, "Zone_E": 4500, "Zone_F": 3200,
            "Zone_G": 2800, "Zone_H": 3600, "Zone_I": 4100,
            "Zone_J": 3400,
        }
        
        self.zone_elevations = {
            "Zone_A": 8.5, "Zone_B": 12.0, "Zone_C": 6.2,
            "Zone_D": 15.3, "Zone_E": 4.8, "Zone_F": 9.7,
            "Zone_G": 11.2, "Zone_H": 7.1, "Zone_I": 5.5,
            "Zone_J": 10.8,
        }
        
        self.critical_infrastructure = {
            "bridges": ["Blue Heron Bridge", "Riviera Beach Bridge", "Singer Island Causeway"],
            "seawalls": ["Lake Worth Lagoon Seawall", "Singer Island Seawall"],
            "canals": ["C-17 Canal", "Earman River Canal"],
            "power_substations": ["Riviera Beach Substation", "Singer Island Substation"],
        }
        
        self.statistics = {
            "total_predictions": 0,
            "weather_predictions": 0,
            "fire_predictions": 0,
            "hazmat_predictions": 0,
            "infrastructure_predictions": 0,
            "high_threat_alerts": 0,
        }
    
    def predict_weather_hazard(
        self,
        hazard_type: HazardType,
        noaa_data: Optional[Dict[str, Any]] = None,
        nhc_data: Optional[Dict[str, Any]] = None,
        local_sensor_data: Optional[Dict[str, Any]] = None,
    ) -> WeatherHazard:
        """
        Predict weather hazard based on NOAA/NHC data and local sensors.
        """
        hazard_id = f"WH-{uuid.uuid4().hex[:8].upper()}"
        timestamp = datetime.utcnow()
        
        wind_speed = 0.0
        rainfall = 0.0
        storm_surge = 0.0
        pressure = 1013.0
        
        if noaa_data:
            wind_speed = noaa_data.get("wind_speed_mph", 0.0)
            rainfall = noaa_data.get("rainfall_inches", 0.0)
            pressure = noaa_data.get("pressure_mb", 1013.0)
        
        if nhc_data:
            storm_surge = nhc_data.get("storm_surge_feet", 0.0)
            if nhc_data.get("wind_speed_mph", 0) > wind_speed:
                wind_speed = nhc_data.get("wind_speed_mph", 0)
        
        if local_sensor_data:
            if local_sensor_data.get("wind_speed_mph", 0) > wind_speed:
                wind_speed = local_sensor_data.get("wind_speed_mph", 0)
        
        threat_level = self._calculate_weather_threat_level(
            hazard_type, wind_speed, rainfall, storm_surge, pressure
        )
        
        affected_zones = self._determine_affected_zones_weather(
            hazard_type, wind_speed, rainfall, storm_surge
        )
        
        time_to_impact = self._calculate_time_to_impact(nhc_data or noaa_data or {})
        
        confidence_score = self._calculate_confidence_score(
            [noaa_data, nhc_data, local_sensor_data]
        )
        
        hazard = WeatherHazard(
            hazard_id=hazard_id,
            hazard_type=hazard_type,
            timestamp=timestamp,
            threat_level=threat_level,
            storm_name=nhc_data.get("storm_name") if nhc_data else None,
            category=nhc_data.get("category") if nhc_data else None,
            wind_speed_mph=wind_speed,
            wind_direction=noaa_data.get("wind_direction", "N") if noaa_data else "N",
            pressure_mb=pressure,
            movement_speed_mph=nhc_data.get("movement_speed_mph", 0) if nhc_data else 0,
            movement_direction=nhc_data.get("movement_direction", "") if nhc_data else "",
            rainfall_inches=rainfall,
            storm_surge_feet=storm_surge,
            tornado_probability=self._calculate_tornado_probability(wind_speed, pressure),
            track_coordinates=nhc_data.get("track_coordinates", []) if nhc_data else [],
            cone_of_uncertainty=nhc_data.get("cone_of_uncertainty", []) if nhc_data else [],
            time_to_impact_hours=time_to_impact,
            affected_zones=affected_zones,
            data_sources=self._get_data_sources([noaa_data, nhc_data, local_sensor_data]),
            confidence_score=confidence_score,
        )
        
        self.statistics["total_predictions"] += 1
        self.statistics["weather_predictions"] += 1
        if threat_level.value >= ThreatLevel.HIGH.value:
            self.statistics["high_threat_alerts"] += 1
        
        return hazard
    
    def predict_flood_risk(
        self,
        zone: str,
        rainfall_inches: float,
        storm_surge_feet: float = 0.0,
        tide_level: str = "normal",
    ) -> FloodPrediction:
        """
        Predict street-level flood risk for a zone.
        """
        prediction_id = f"FP-{uuid.uuid4().hex[:8].upper()}"
        timestamp = datetime.utcnow()
        
        elevation = self.zone_elevations.get(zone, 10.0)
        
        base_flood_prob = 0.0
        if rainfall_inches > 2:
            base_flood_prob = min(0.3 + (rainfall_inches - 2) * 0.1, 0.9)
        
        if storm_surge_feet > 0:
            base_flood_prob = min(base_flood_prob + storm_surge_feet * 0.1, 0.95)
        
        if elevation < 8:
            base_flood_prob = min(base_flood_prob + 0.2, 0.98)
        elif elevation < 12:
            base_flood_prob = min(base_flood_prob + 0.1, 0.95)
        
        if tide_level == "high":
            base_flood_prob = min(base_flood_prob + 0.15, 0.98)
        elif tide_level == "king":
            base_flood_prob = min(base_flood_prob + 0.25, 0.99)
        
        expected_depth = 0.0
        if base_flood_prob > 0.3:
            expected_depth = (rainfall_inches - 2) * 2 + storm_surge_feet * 6
            if elevation < 8:
                expected_depth += 6
        
        time_to_flood = max(0.5, 4 - rainfall_inches * 0.5)
        
        risk_factors = []
        if elevation < 8:
            risk_factors.append("low_elevation")
        if rainfall_inches > 4:
            risk_factors.append("heavy_rainfall")
        if storm_surge_feet > 2:
            risk_factors.append("storm_surge")
        if tide_level in ["high", "king"]:
            risk_factors.append(f"{tide_level}_tide")
        
        recommended_actions = []
        if base_flood_prob > 0.7:
            recommended_actions.append("Evacuate flood-prone areas")
            recommended_actions.append("Move vehicles to higher ground")
        elif base_flood_prob > 0.4:
            recommended_actions.append("Prepare for potential flooding")
            recommended_actions.append("Monitor water levels")
        
        return FloodPrediction(
            prediction_id=prediction_id,
            timestamp=timestamp,
            zone=zone,
            flood_probability=base_flood_prob,
            expected_depth_inches=expected_depth,
            time_to_flood_hours=time_to_flood,
            drainage_capacity_percent=max(0, 100 - rainfall_inches * 10),
            elevation_feet=elevation,
            risk_factors=risk_factors,
            recommended_actions=recommended_actions,
            confidence_score=0.75,
        )
    
    def predict_fire_spread(
        self,
        origin_zone: str,
        fire_type: str = "structure",
        current_size_acres: float = 0.1,
        wind_speed_mph: float = 10.0,
        wind_direction: str = "E",
        humidity_percent: float = 50.0,
        temperature_f: float = 85.0,
    ) -> FireHazard:
        """
        Predict urban fire spread based on conditions.
        """
        hazard_id = f"FH-{uuid.uuid4().hex[:8].upper()}"
        timestamp = datetime.utcnow()
        
        spread_rate = current_size_acres * 0.1
        if wind_speed_mph > 15:
            spread_rate *= 1.5
        if wind_speed_mph > 25:
            spread_rate *= 2.0
        if humidity_percent < 30:
            spread_rate *= 1.3
        if temperature_f > 95:
            spread_rate *= 1.2
        
        threat_level = ThreatLevel.LOW
        if current_size_acres > 1 or spread_rate > 0.5:
            threat_level = ThreatLevel.MODERATE
        if current_size_acres > 5 or spread_rate > 1.0:
            threat_level = ThreatLevel.HIGH
        if current_size_acres > 10 or spread_rate > 2.0:
            threat_level = ThreatLevel.EXTREME
        
        time_to_critical = 24.0
        if spread_rate > 0:
            time_to_critical = max(0.5, (5 - current_size_acres) / spread_rate)
        
        affected_zones = [origin_zone]
        zone_idx = self.city_zones.index(origin_zone) if origin_zone in self.city_zones else 0
        if spread_rate > 0.5 and zone_idx < len(self.city_zones) - 1:
            affected_zones.append(self.city_zones[zone_idx + 1])
        
        affected_structures = int(current_size_acres * 10)
        
        recommended_actions = []
        if threat_level.value >= ThreatLevel.HIGH.value:
            recommended_actions.append("Evacuate affected area")
            recommended_actions.append("Request mutual aid")
        recommended_actions.append("Deploy fire suppression units")
        recommended_actions.append("Establish perimeter")
        
        return FireHazard(
            hazard_id=hazard_id,
            timestamp=timestamp,
            threat_level=threat_level,
            origin_zone=origin_zone,
            fire_type=fire_type,
            current_size_acres=current_size_acres,
            spread_rate_acres_per_hour=spread_rate,
            wind_speed_mph=wind_speed_mph,
            wind_direction=wind_direction,
            humidity_percent=humidity_percent,
            temperature_f=temperature_f,
            structure_density="high" if origin_zone in ["Zone_A", "Zone_B"] else "medium",
            time_to_critical_hours=time_to_critical,
            affected_structures=affected_structures,
            evacuation_required=threat_level.value >= ThreatLevel.HIGH.value,
            affected_zones=affected_zones,
            recommended_actions=recommended_actions,
            confidence_score=0.80,
        )
    
    def predict_hazmat_release(
        self,
        chemical_name: str,
        chemical_class: str,
        release_type: str,
        release_quantity_gallons: float,
        origin_zone: str,
        wind_speed_mph: float = 5.0,
        wind_direction: str = "E",
    ) -> HazmatHazard:
        """
        Model chemical/hazmat release and affected areas.
        """
        hazard_id = f"HM-{uuid.uuid4().hex[:8].upper()}"
        timestamp = datetime.utcnow()
        
        base_radius = math.sqrt(release_quantity_gallons) * 0.01
        if wind_speed_mph > 10:
            base_radius *= 1.5
        if chemical_class in ["toxic", "flammable"]:
            base_radius *= 1.3
        
        evacuation_radius = base_radius * 2
        shelter_radius = base_radius * 3
        
        threat_level = ThreatLevel.LOW
        if release_quantity_gallons > 100:
            threat_level = ThreatLevel.MODERATE
        if release_quantity_gallons > 500 or chemical_class == "toxic":
            threat_level = ThreatLevel.HIGH
        if release_quantity_gallons > 1000 or (chemical_class == "toxic" and release_quantity_gallons > 100):
            threat_level = ThreatLevel.EXTREME
        
        affected_zones = [origin_zone]
        zone_idx = self.city_zones.index(origin_zone) if origin_zone in self.city_zones else 0
        if evacuation_radius > 0.5:
            for i in range(max(0, zone_idx - 1), min(len(self.city_zones), zone_idx + 2)):
                if self.city_zones[i] not in affected_zones:
                    affected_zones.append(self.city_zones[i])
        
        affected_population = sum(
            self.zone_populations.get(z, 0) for z in affected_zones
        )
        
        health_effects = []
        if chemical_class == "toxic":
            health_effects = ["respiratory_irritation", "skin_irritation", "nausea"]
        elif chemical_class == "flammable":
            health_effects = ["burn_risk", "explosion_risk"]
        elif chemical_class == "corrosive":
            health_effects = ["chemical_burns", "eye_damage"]
        
        recommended_actions = [
            "Establish incident command",
            "Evacuate affected radius",
            "Deploy hazmat team",
            "Notify hospitals",
        ]
        
        agencies_required = [
            "Fire/Rescue",
            "Police",
            "Hazmat Team",
            "EMS",
            "Public Health",
        ]
        
        return HazmatHazard(
            hazard_id=hazard_id,
            timestamp=timestamp,
            threat_level=threat_level,
            chemical_name=chemical_name,
            chemical_class=chemical_class,
            release_type=release_type,
            release_quantity_gallons=release_quantity_gallons,
            origin_zone=origin_zone,
            plume_direction=wind_direction,
            plume_speed_mph=wind_speed_mph,
            affected_radius_miles=base_radius,
            evacuation_radius_miles=evacuation_radius,
            shelter_in_place_radius_miles=shelter_radius,
            health_effects=health_effects,
            exposure_duration_safe_minutes=15 if chemical_class == "toxic" else 60,
            decontamination_required=chemical_class in ["toxic", "corrosive"],
            water_contamination_risk=release_type == "spill",
            affected_population=affected_population,
            affected_zones=affected_zones,
            evacuation_priority_zones=affected_zones[:2],
            recommended_actions=recommended_actions,
            agencies_required=agencies_required,
            confidence_score=0.75,
        )
    
    def predict_infrastructure_failure(
        self,
        infrastructure_type: str,
        infrastructure_name: str,
        zone: str,
        stress_indicators: Optional[Dict[str, Any]] = None,
        weather_conditions: Optional[Dict[str, Any]] = None,
    ) -> InfrastructureHazard:
        """
        Predict infrastructure collapse or failure risk.
        """
        hazard_id = f"IF-{uuid.uuid4().hex[:8].upper()}"
        timestamp = datetime.utcnow()
        
        base_failure_prob = 0.05
        stress_level = 20.0
        
        if stress_indicators:
            if stress_indicators.get("vibration_anomaly"):
                base_failure_prob += 0.15
                stress_level += 20
            if stress_indicators.get("crack_detected"):
                base_failure_prob += 0.20
                stress_level += 25
            if stress_indicators.get("subsidence_detected"):
                base_failure_prob += 0.25
                stress_level += 30
            if stress_indicators.get("corrosion_level", 0) > 50:
                base_failure_prob += 0.10
                stress_level += 15
        
        if weather_conditions:
            if weather_conditions.get("wind_speed_mph", 0) > 50:
                base_failure_prob += 0.10
                stress_level += 15
            if weather_conditions.get("flooding"):
                base_failure_prob += 0.15
                stress_level += 20
            if weather_conditions.get("storm_surge_feet", 0) > 3:
                base_failure_prob += 0.20
                stress_level += 25
        
        threat_level = ThreatLevel.MINIMAL
        if base_failure_prob > 0.2:
            threat_level = ThreatLevel.LOW
        if base_failure_prob > 0.4:
            threat_level = ThreatLevel.MODERATE
        if base_failure_prob > 0.6:
            threat_level = ThreatLevel.HIGH
        if base_failure_prob > 0.8:
            threat_level = ThreatLevel.EXTREME
        
        affected_zones = [zone]
        if infrastructure_type == "bridge":
            zone_idx = self.city_zones.index(zone) if zone in self.city_zones else 0
            if zone_idx > 0:
                affected_zones.append(self.city_zones[zone_idx - 1])
            if zone_idx < len(self.city_zones) - 1:
                affected_zones.append(self.city_zones[zone_idx + 1])
        
        affected_population = sum(
            self.zone_populations.get(z, 0) for z in affected_zones
        )
        
        traffic_impact = "none"
        if infrastructure_type in ["bridge", "roadway"]:
            traffic_impact = "major" if threat_level.value >= ThreatLevel.HIGH.value else "moderate"
        
        utility_impact = []
        if infrastructure_type == "power_substation":
            utility_impact = ["electricity"]
        elif infrastructure_type == "seawall":
            utility_impact = ["flood_protection"]
        
        recommended_actions = []
        if threat_level.value >= ThreatLevel.HIGH.value:
            recommended_actions.append(f"Close {infrastructure_name}")
            recommended_actions.append("Evacuate affected area")
        recommended_actions.append("Deploy inspection team")
        recommended_actions.append("Monitor continuously")
        
        agencies_required = ["Public Works", "Police"]
        if infrastructure_type == "power_substation":
            agencies_required.append("Utility Company")
        
        time_to_failure = None
        if base_failure_prob > 0.5:
            time_to_failure = max(1.0, (1 - base_failure_prob) * 48)
        
        return InfrastructureHazard(
            hazard_id=hazard_id,
            timestamp=timestamp,
            threat_level=threat_level,
            infrastructure_type=infrastructure_type,
            infrastructure_name=infrastructure_name,
            zone=zone,
            failure_probability=min(base_failure_prob, 0.99),
            stress_level_percent=min(stress_level, 100),
            anomaly_detected=stress_level > 50,
            anomaly_type="structural_stress" if stress_level > 50 else "",
            condition_rating="poor" if stress_level > 70 else "fair" if stress_level > 40 else "good",
            affected_population=affected_population,
            traffic_impact=traffic_impact,
            utility_impact=utility_impact,
            time_to_failure_hours=time_to_failure,
            affected_zones=affected_zones,
            recommended_actions=recommended_actions,
            agencies_required=agencies_required,
            confidence_score=0.70,
        )
    
    def get_unified_prediction(
        self,
        hazard_type: HazardType,
        **kwargs,
    ) -> HazardPrediction:
        """
        Get unified hazard prediction with all relevant data.
        """
        prediction_id = f"HP-{uuid.uuid4().hex[:8].upper()}"
        timestamp = datetime.utcnow()
        
        weather_hazard = None
        fire_hazard = None
        hazmat_hazard = None
        infrastructure_hazard = None
        flood_predictions = []
        
        if hazard_type in [HazardType.HURRICANE, HazardType.TORNADO, HazardType.FLOODING,
                          HazardType.STORM_SURGE, HazardType.SEVERE_THUNDERSTORM]:
            weather_hazard = self.predict_weather_hazard(hazard_type, **kwargs)
            threat_level = weather_hazard.threat_level
            affected_zones = weather_hazard.affected_zones
            time_to_impact = weather_hazard.time_to_impact_hours
            confidence_score = weather_hazard.confidence_score
            
            if hazard_type in [HazardType.FLOODING, HazardType.STORM_SURGE, HazardType.HURRICANE]:
                for zone in affected_zones:
                    flood_pred = self.predict_flood_risk(
                        zone=zone,
                        rainfall_inches=weather_hazard.rainfall_inches,
                        storm_surge_feet=weather_hazard.storm_surge_feet,
                    )
                    flood_predictions.append(flood_pred)
        
        elif hazard_type in [HazardType.URBAN_FIRE, HazardType.WILDFIRE]:
            fire_hazard = self.predict_fire_spread(**kwargs)
            threat_level = fire_hazard.threat_level
            affected_zones = fire_hazard.affected_zones
            time_to_impact = fire_hazard.time_to_critical_hours
            confidence_score = fire_hazard.confidence_score
        
        elif hazard_type in [HazardType.HAZMAT_RELEASE, HazardType.CHEMICAL_SPILL]:
            hazmat_hazard = self.predict_hazmat_release(**kwargs)
            threat_level = hazmat_hazard.threat_level
            affected_zones = hazmat_hazard.affected_zones
            time_to_impact = 0.0
            confidence_score = hazmat_hazard.confidence_score
        
        elif hazard_type in [HazardType.BRIDGE_COLLAPSE, HazardType.SEAWALL_FAILURE,
                            HazardType.POWER_GRID_FAILURE, HazardType.ROADWAY_SUBSIDENCE,
                            HazardType.CANAL_BREACH]:
            infrastructure_hazard = self.predict_infrastructure_failure(**kwargs)
            threat_level = infrastructure_hazard.threat_level
            affected_zones = infrastructure_hazard.affected_zones
            time_to_impact = infrastructure_hazard.time_to_failure_hours or 24.0
            confidence_score = infrastructure_hazard.confidence_score
        
        else:
            threat_level = ThreatLevel.MINIMAL
            affected_zones = []
            time_to_impact = 0.0
            confidence_score = 0.5
        
        affected_population = sum(
            self.zone_populations.get(z, 0) for z in affected_zones
        )
        
        recommended_actions = self._get_recommended_actions(hazard_type, threat_level)
        agencies_required = self._get_required_agencies(hazard_type, threat_level)
        
        potential_casualties_prevented = self._estimate_casualties_prevented(
            hazard_type, threat_level, affected_population
        )
        
        economic_impact = self._estimate_economic_impact(
            hazard_type, threat_level, affected_zones
        )
        
        return HazardPrediction(
            prediction_id=prediction_id,
            timestamp=timestamp,
            hazard_type=hazard_type,
            threat_level=threat_level,
            confidence_score=confidence_score,
            time_to_impact_hours=time_to_impact,
            affected_zones=affected_zones,
            affected_population=affected_population,
            recommended_actions=recommended_actions,
            agencies_required=agencies_required,
            potential_casualties_prevented=potential_casualties_prevented,
            economic_impact_estimate=economic_impact,
            weather_hazard=weather_hazard,
            fire_hazard=fire_hazard,
            hazmat_hazard=hazmat_hazard,
            infrastructure_hazard=infrastructure_hazard,
            flood_predictions=flood_predictions,
        )
    
    def get_active_hazards(self) -> List[Dict[str, Any]]:
        """
        Get list of currently active hazards.
        """
        return [
            {
                "hazard_id": f"AH-{uuid.uuid4().hex[:8].upper()}",
                "hazard_type": HazardType.FLOODING.value,
                "threat_level": ThreatLevel.LOW.value,
                "affected_zones": ["Zone_E", "Zone_I"],
                "time_to_impact_hours": 12.0,
                "status": "monitoring",
            }
        ]
    
    def _calculate_weather_threat_level(
        self,
        hazard_type: HazardType,
        wind_speed: float,
        rainfall: float,
        storm_surge: float,
        pressure: float,
    ) -> ThreatLevel:
        """Calculate threat level based on weather conditions."""
        score = 0
        
        if wind_speed > 74:
            score += 4
        elif wind_speed > 58:
            score += 3
        elif wind_speed > 39:
            score += 2
        elif wind_speed > 20:
            score += 1
        
        if rainfall > 8:
            score += 3
        elif rainfall > 4:
            score += 2
        elif rainfall > 2:
            score += 1
        
        if storm_surge > 6:
            score += 4
        elif storm_surge > 4:
            score += 3
        elif storm_surge > 2:
            score += 2
        elif storm_surge > 1:
            score += 1
        
        if pressure < 960:
            score += 3
        elif pressure < 980:
            score += 2
        elif pressure < 1000:
            score += 1
        
        if score >= 10:
            return ThreatLevel.EXTREME
        elif score >= 7:
            return ThreatLevel.HIGH
        elif score >= 4:
            return ThreatLevel.MODERATE
        elif score >= 2:
            return ThreatLevel.LOW
        return ThreatLevel.MINIMAL
    
    def _determine_affected_zones_weather(
        self,
        hazard_type: HazardType,
        wind_speed: float,
        rainfall: float,
        storm_surge: float,
    ) -> List[str]:
        """Determine affected zones based on weather conditions."""
        affected = []
        
        if storm_surge > 2:
            for zone, elevation in self.zone_elevations.items():
                if elevation < 10:
                    affected.append(zone)
        
        if rainfall > 4:
            for zone, elevation in self.zone_elevations.items():
                if elevation < 8 and zone not in affected:
                    affected.append(zone)
        
        if wind_speed > 50:
            affected = self.city_zones.copy()
        
        if not affected:
            affected = ["Zone_E", "Zone_C", "Zone_I"]
        
        return affected
    
    def _calculate_time_to_impact(self, data: Dict[str, Any]) -> float:
        """Calculate time to impact in hours."""
        if not data:
            return 24.0
        
        distance = data.get("distance_miles", 100)
        speed = data.get("movement_speed_mph", 10)
        
        if speed > 0:
            return distance / speed
        return 24.0
    
    def _calculate_confidence_score(self, data_sources: List[Optional[Dict]]) -> float:
        """Calculate confidence score based on available data sources."""
        valid_sources = sum(1 for d in data_sources if d is not None)
        return min(0.5 + valid_sources * 0.15, 0.95)
    
    def _calculate_tornado_probability(self, wind_speed: float, pressure: float) -> float:
        """Calculate tornado probability."""
        prob = 0.0
        if wind_speed > 50:
            prob += 0.1
        if wind_speed > 74:
            prob += 0.15
        if pressure < 980:
            prob += 0.1
        return min(prob, 0.5)
    
    def _get_data_sources(self, sources: List[Optional[Dict]]) -> List[str]:
        """Get list of data source names."""
        names = []
        source_names = ["NOAA", "NHC", "Local Sensors"]
        for i, source in enumerate(sources):
            if source is not None:
                names.append(source_names[i])
        return names
    
    def _get_recommended_actions(
        self,
        hazard_type: HazardType,
        threat_level: ThreatLevel,
    ) -> List[str]:
        """Get recommended actions based on hazard type and threat level."""
        actions = []
        
        if threat_level.value >= ThreatLevel.EXTREME.value:
            actions.append("Issue mandatory evacuation order")
            actions.append("Activate Emergency Operations Center")
            actions.append("Request state/federal assistance")
        elif threat_level.value >= ThreatLevel.HIGH.value:
            actions.append("Issue voluntary evacuation advisory")
            actions.append("Open emergency shelters")
            actions.append("Pre-position emergency resources")
        elif threat_level.value >= ThreatLevel.MODERATE.value:
            actions.append("Issue public warning")
            actions.append("Prepare emergency resources")
        
        if hazard_type in [HazardType.HURRICANE, HazardType.FLOODING]:
            actions.append("Activate flood barriers")
            actions.append("Clear drainage systems")
        elif hazard_type in [HazardType.URBAN_FIRE, HazardType.WILDFIRE]:
            actions.append("Deploy fire suppression units")
            actions.append("Establish firebreaks")
        elif hazard_type in [HazardType.HAZMAT_RELEASE]:
            actions.append("Deploy hazmat team")
            actions.append("Establish decontamination stations")
        
        return actions
    
    def _get_required_agencies(
        self,
        hazard_type: HazardType,
        threat_level: ThreatLevel,
    ) -> List[str]:
        """Get required agencies based on hazard type."""
        agencies = ["Police", "Fire/Rescue", "EMS"]
        
        if hazard_type in [HazardType.HURRICANE, HazardType.FLOODING, HazardType.STORM_SURGE]:
            agencies.extend(["Public Works", "Utilities", "Red Cross"])
        elif hazard_type in [HazardType.HAZMAT_RELEASE, HazardType.CHEMICAL_SPILL]:
            agencies.extend(["Hazmat Team", "Public Health", "EPA"])
        elif hazard_type in [HazardType.BRIDGE_COLLAPSE, HazardType.ROADWAY_SUBSIDENCE]:
            agencies.extend(["Public Works", "DOT"])
        
        if threat_level.value >= ThreatLevel.HIGH.value:
            agencies.extend(["Regional EOC", "National Guard"])
        
        return list(set(agencies))
    
    def _estimate_casualties_prevented(
        self,
        hazard_type: HazardType,
        threat_level: ThreatLevel,
        affected_population: int,
    ) -> int:
        """Estimate potential casualties prevented by early warning."""
        base_rate = 0.001
        
        if threat_level == ThreatLevel.EXTREME:
            base_rate = 0.01
        elif threat_level == ThreatLevel.HIGH:
            base_rate = 0.005
        elif threat_level == ThreatLevel.MODERATE:
            base_rate = 0.002
        
        if hazard_type in [HazardType.HAZMAT_RELEASE, HazardType.CHEMICAL_SPILL]:
            base_rate *= 2
        
        return int(affected_population * base_rate * 0.8)
    
    def _estimate_economic_impact(
        self,
        hazard_type: HazardType,
        threat_level: ThreatLevel,
        affected_zones: List[str],
    ) -> float:
        """Estimate economic impact in dollars."""
        base_impact = len(affected_zones) * 100000
        
        multiplier = threat_level.value
        
        if hazard_type in [HazardType.HURRICANE, HazardType.FLOODING]:
            multiplier *= 2
        elif hazard_type in [HazardType.BRIDGE_COLLAPSE]:
            multiplier *= 5
        
        return base_impact * multiplier
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get engine statistics."""
        return {
            **self.statistics,
            "agency": self.agency_config,
            "zones_monitored": len(self.city_zones),
            "critical_infrastructure_count": sum(
                len(v) for v in self.critical_infrastructure.values()
            ),
        }
