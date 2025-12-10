"""
Phase 21: Crisis Detection Engine

Real-time crisis detection for storms, floods, fires, earthquakes, and explosions.
Integrates with NOAA, USGS, and other external data sources.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
import uuid
import math


class CrisisType(Enum):
    STORM = "storm"
    FLOOD = "flood"
    FIRE = "fire"
    EARTHQUAKE = "earthquake"
    EXPLOSION = "explosion"
    TORNADO = "tornado"
    HURRICANE = "hurricane"
    TSUNAMI = "tsunami"


class CrisisSeverity(Enum):
    MINOR = "minor"
    MODERATE = "moderate"
    SEVERE = "severe"
    EXTREME = "extreme"
    CATASTROPHIC = "catastrophic"


class AlertLevel(Enum):
    WATCH = "watch"
    WARNING = "warning"
    EMERGENCY = "emergency"
    CRITICAL = "critical"


class StormCategory(Enum):
    TROPICAL_DEPRESSION = "tropical_depression"
    TROPICAL_STORM = "tropical_storm"
    CATEGORY_1 = "category_1"
    CATEGORY_2 = "category_2"
    CATEGORY_3 = "category_3"
    CATEGORY_4 = "category_4"
    CATEGORY_5 = "category_5"


class FloodRisk(Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"
    EXTREME = "extreme"


class FireSpreadRate(Enum):
    SLOW = "slow"
    MODERATE = "moderate"
    FAST = "fast"
    EXTREME = "extreme"


@dataclass
class CrisisAlert:
    alert_id: str
    crisis_type: CrisisType
    severity: CrisisSeverity
    alert_level: AlertLevel
    title: str
    description: str
    location: Dict[str, Any]
    affected_area_km2: float
    population_at_risk: int
    start_time: datetime
    expected_duration_hours: Optional[float]
    recommendations: List[str]
    source: str
    confidence_score: float
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True


@dataclass
class StormData:
    storm_id: str
    name: str
    category: StormCategory
    wind_speed_mph: float
    pressure_mb: float
    movement_direction: str
    movement_speed_mph: float
    current_position: Dict[str, float]
    predicted_path: List[Dict[str, Any]]
    storm_surge_ft: float
    rainfall_inches: float
    tornado_probability: float
    landfall_time: Optional[datetime]
    affected_counties: List[str]
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class FloodPrediction:
    prediction_id: str
    location: Dict[str, Any]
    flood_risk: FloodRisk
    predicted_water_level_ft: float
    current_water_level_ft: float
    flood_stage_ft: float
    time_to_flood_hours: Optional[float]
    rainfall_24h_inches: float
    rainfall_forecast_inches: float
    terrain_risk_factor: float
    drainage_capacity_factor: float
    affected_structures: int
    evacuation_recommended: bool
    confidence_score: float
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class FireSpread:
    fire_id: str
    name: str
    origin: Dict[str, float]
    current_perimeter: List[Dict[str, float]]
    area_acres: float
    containment_percent: float
    spread_rate: FireSpreadRate
    spread_direction: str
    wind_speed_mph: float
    wind_direction: str
    humidity_percent: float
    temperature_f: float
    fuel_type: str
    structures_threatened: int
    structures_destroyed: int
    evacuation_zones: List[str]
    predicted_spread_24h: List[Dict[str, float]]
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class EarthquakeData:
    earthquake_id: str
    magnitude: float
    depth_km: float
    epicenter: Dict[str, float]
    location_description: str
    shake_intensity: str
    affected_radius_km: float
    population_affected: int
    aftershock_probability: float
    tsunami_risk: bool
    infrastructure_damage_estimate: str
    occurred_at: datetime
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ExplosionImpact:
    explosion_id: str
    location: Dict[str, float]
    explosion_type: str
    estimated_yield_kg_tnt: float
    blast_radius_m: float
    thermal_radius_m: float
    overpressure_zones: List[Dict[str, Any]]
    casualties_estimate: Dict[str, int]
    structures_affected: int
    hazmat_risk: bool
    evacuation_radius_m: float
    wind_direction: str
    plume_projection: Optional[List[Dict[str, float]]]
    created_at: datetime = field(default_factory=datetime.utcnow)


class StormTracker:
    """
    Tracks storms using NOAA data feeds (stub implementation).
    Monitors tropical systems, hurricanes, and severe weather.
    """

    def __init__(self):
        self._storms: Dict[str, StormData] = {}
        self._alerts: Dict[str, CrisisAlert] = {}

    def fetch_noaa_data(self) -> List[Dict[str, Any]]:
        """Fetch storm data from NOAA (stub)."""
        return [
            {
                "id": "AL092024",
                "name": "Hurricane Milton",
                "category": "category_4",
                "wind_speed": 145,
                "pressure": 940,
                "lat": 26.5,
                "lon": -82.5,
            }
        ]

    def track_storm(
        self,
        name: str,
        category: str,
        wind_speed_mph: float,
        pressure_mb: float,
        position: Dict[str, float],
        movement_direction: str,
        movement_speed_mph: float,
    ) -> StormData:
        """Track a new storm or update existing storm data."""
        storm_id = f"storm-{uuid.uuid4().hex[:8]}"

        category_enum = StormCategory(category) if category in [c.value for c in StormCategory] else StormCategory.TROPICAL_STORM

        predicted_path = self._predict_storm_path(position, movement_direction, movement_speed_mph)
        storm_surge = self._calculate_storm_surge(category_enum, wind_speed_mph)
        tornado_prob = self._calculate_tornado_probability(category_enum)

        storm = StormData(
            storm_id=storm_id,
            name=name,
            category=category_enum,
            wind_speed_mph=wind_speed_mph,
            pressure_mb=pressure_mb,
            movement_direction=movement_direction,
            movement_speed_mph=movement_speed_mph,
            current_position=position,
            predicted_path=predicted_path,
            storm_surge_ft=storm_surge,
            rainfall_inches=self._estimate_rainfall(category_enum),
            tornado_probability=tornado_prob,
            landfall_time=self._estimate_landfall(position, predicted_path),
            affected_counties=self._get_affected_counties(predicted_path),
        )

        self._storms[storm_id] = storm
        self._generate_storm_alert(storm)
        return storm

    def _predict_storm_path(
        self,
        position: Dict[str, float],
        direction: str,
        speed_mph: float,
    ) -> List[Dict[str, Any]]:
        """Predict storm path for next 120 hours."""
        path = []
        lat, lon = position.get("lat", 0), position.get("lon", 0)

        direction_vectors = {
            "N": (0.1, 0),
            "NE": (0.07, 0.07),
            "E": (0, 0.1),
            "SE": (-0.07, 0.07),
            "S": (-0.1, 0),
            "SW": (-0.07, -0.07),
            "W": (0, -0.1),
            "NW": (0.07, -0.07),
        }

        dlat, dlon = direction_vectors.get(direction, (0.05, 0.05))
        speed_factor = speed_mph / 10

        for hours in range(0, 121, 6):
            path.append({
                "hours": hours,
                "lat": lat + (dlat * speed_factor * hours / 6),
                "lon": lon + (dlon * speed_factor * hours / 6),
                "wind_speed": max(35, 145 - hours * 0.5),
                "confidence": max(0.3, 1.0 - hours * 0.005),
            })

        return path

    def _calculate_storm_surge(self, category: StormCategory, wind_speed: float) -> float:
        """Calculate expected storm surge based on category."""
        surge_map = {
            StormCategory.TROPICAL_DEPRESSION: 1.0,
            StormCategory.TROPICAL_STORM: 2.0,
            StormCategory.CATEGORY_1: 4.0,
            StormCategory.CATEGORY_2: 6.0,
            StormCategory.CATEGORY_3: 9.0,
            StormCategory.CATEGORY_4: 13.0,
            StormCategory.CATEGORY_5: 18.0,
        }
        base_surge = surge_map.get(category, 2.0)
        return base_surge * (wind_speed / 100)

    def _calculate_tornado_probability(self, category: StormCategory) -> float:
        """Calculate tornado probability based on storm category."""
        prob_map = {
            StormCategory.TROPICAL_DEPRESSION: 0.05,
            StormCategory.TROPICAL_STORM: 0.15,
            StormCategory.CATEGORY_1: 0.25,
            StormCategory.CATEGORY_2: 0.35,
            StormCategory.CATEGORY_3: 0.45,
            StormCategory.CATEGORY_4: 0.55,
            StormCategory.CATEGORY_5: 0.65,
        }
        return prob_map.get(category, 0.1)

    def _estimate_rainfall(self, category: StormCategory) -> float:
        """Estimate rainfall in inches based on category."""
        rainfall_map = {
            StormCategory.TROPICAL_DEPRESSION: 3.0,
            StormCategory.TROPICAL_STORM: 6.0,
            StormCategory.CATEGORY_1: 8.0,
            StormCategory.CATEGORY_2: 12.0,
            StormCategory.CATEGORY_3: 15.0,
            StormCategory.CATEGORY_4: 20.0,
            StormCategory.CATEGORY_5: 25.0,
        }
        return rainfall_map.get(category, 5.0)

    def _estimate_landfall(
        self,
        position: Dict[str, float],
        path: List[Dict[str, Any]],
    ) -> Optional[datetime]:
        """Estimate landfall time based on predicted path."""
        for point in path:
            if point.get("lat", 0) > 25 and -90 < point.get("lon", 0) < -80:
                hours = point.get("hours", 0)
                return datetime.utcnow()
        return None

    def _get_affected_counties(self, path: List[Dict[str, Any]]) -> List[str]:
        """Get list of potentially affected counties."""
        return ["Miami-Dade", "Broward", "Palm Beach", "Monroe", "Collier"]

    def _generate_storm_alert(self, storm: StormData) -> CrisisAlert:
        """Generate crisis alert for storm."""
        severity_map = {
            StormCategory.TROPICAL_DEPRESSION: CrisisSeverity.MINOR,
            StormCategory.TROPICAL_STORM: CrisisSeverity.MODERATE,
            StormCategory.CATEGORY_1: CrisisSeverity.MODERATE,
            StormCategory.CATEGORY_2: CrisisSeverity.SEVERE,
            StormCategory.CATEGORY_3: CrisisSeverity.SEVERE,
            StormCategory.CATEGORY_4: CrisisSeverity.EXTREME,
            StormCategory.CATEGORY_5: CrisisSeverity.CATASTROPHIC,
        }

        alert = CrisisAlert(
            alert_id=f"alert-{uuid.uuid4().hex[:8]}",
            crisis_type=CrisisType.HURRICANE,
            severity=severity_map.get(storm.category, CrisisSeverity.MODERATE),
            alert_level=AlertLevel.WARNING if storm.category.value.startswith("category") else AlertLevel.WATCH,
            title=f"{storm.name} - {storm.category.value.replace('_', ' ').title()}",
            description=f"Hurricane {storm.name} with {storm.wind_speed_mph} mph winds approaching.",
            location=storm.current_position,
            affected_area_km2=50000,
            population_at_risk=2000000,
            start_time=datetime.utcnow(),
            expected_duration_hours=72,
            recommendations=[
                "Evacuate if in evacuation zone",
                "Secure outdoor items",
                "Stock emergency supplies",
                "Monitor official channels",
            ],
            source="NOAA/NHC",
            confidence_score=0.85,
        )

        self._alerts[alert.alert_id] = alert
        return alert

    def get_storm(self, storm_id: str) -> Optional[StormData]:
        """Get storm by ID."""
        return self._storms.get(storm_id)

    def get_active_storms(self) -> List[StormData]:
        """Get all active storms."""
        return list(self._storms.values())

    def get_alerts(self, crisis_type: Optional[CrisisType] = None) -> List[CrisisAlert]:
        """Get all alerts, optionally filtered by type."""
        alerts = list(self._alerts.values())
        if crisis_type:
            alerts = [a for a in alerts if a.crisis_type == crisis_type]
        return alerts


class FloodPredictor:
    """
    Predicts flood risk using terrain models and rainfall projections.
    """

    def __init__(self):
        self._predictions: Dict[str, FloodPrediction] = {}
        self._alerts: Dict[str, CrisisAlert] = {}

    def predict_flood(
        self,
        location: Dict[str, Any],
        current_water_level_ft: float,
        flood_stage_ft: float,
        rainfall_24h_inches: float,
        rainfall_forecast_inches: float,
        terrain_elevation_ft: float,
    ) -> FloodPrediction:
        """Predict flood risk for a location."""
        prediction_id = f"flood-{uuid.uuid4().hex[:8]}"

        terrain_risk = self._calculate_terrain_risk(terrain_elevation_ft, flood_stage_ft)
        drainage_factor = self._calculate_drainage_capacity(location)
        total_rainfall = rainfall_24h_inches + rainfall_forecast_inches

        predicted_level = current_water_level_ft + (total_rainfall * 0.5 * terrain_risk)
        flood_risk = self._assess_flood_risk(predicted_level, flood_stage_ft)

        time_to_flood = None
        if predicted_level > flood_stage_ft:
            rise_rate = (predicted_level - current_water_level_ft) / 24
            if rise_rate > 0:
                time_to_flood = (flood_stage_ft - current_water_level_ft) / rise_rate

        prediction = FloodPrediction(
            prediction_id=prediction_id,
            location=location,
            flood_risk=flood_risk,
            predicted_water_level_ft=predicted_level,
            current_water_level_ft=current_water_level_ft,
            flood_stage_ft=flood_stage_ft,
            time_to_flood_hours=time_to_flood,
            rainfall_24h_inches=rainfall_24h_inches,
            rainfall_forecast_inches=rainfall_forecast_inches,
            terrain_risk_factor=terrain_risk,
            drainage_capacity_factor=drainage_factor,
            affected_structures=self._estimate_affected_structures(location, predicted_level),
            evacuation_recommended=flood_risk in [FloodRisk.HIGH, FloodRisk.VERY_HIGH, FloodRisk.EXTREME],
            confidence_score=0.75,
        )

        self._predictions[prediction_id] = prediction

        if flood_risk in [FloodRisk.HIGH, FloodRisk.VERY_HIGH, FloodRisk.EXTREME]:
            self._generate_flood_alert(prediction)

        return prediction

    def _calculate_terrain_risk(self, elevation: float, flood_stage: float) -> float:
        """Calculate terrain risk factor based on elevation."""
        if elevation < flood_stage:
            return 1.5
        elif elevation < flood_stage + 5:
            return 1.2
        elif elevation < flood_stage + 10:
            return 1.0
        else:
            return 0.7

    def _calculate_drainage_capacity(self, location: Dict[str, Any]) -> float:
        """Calculate drainage capacity factor for location."""
        return 0.8

    def _assess_flood_risk(self, predicted_level: float, flood_stage: float) -> FloodRisk:
        """Assess flood risk based on predicted water level."""
        diff = predicted_level - flood_stage
        if diff < -2:
            return FloodRisk.LOW
        elif diff < 0:
            return FloodRisk.MODERATE
        elif diff < 3:
            return FloodRisk.HIGH
        elif diff < 6:
            return FloodRisk.VERY_HIGH
        else:
            return FloodRisk.EXTREME

    def _estimate_affected_structures(self, location: Dict[str, Any], water_level: float) -> int:
        """Estimate number of structures affected by flooding."""
        return int(water_level * 100)

    def _generate_flood_alert(self, prediction: FloodPrediction) -> CrisisAlert:
        """Generate crisis alert for flood prediction."""
        severity_map = {
            FloodRisk.LOW: CrisisSeverity.MINOR,
            FloodRisk.MODERATE: CrisisSeverity.MODERATE,
            FloodRisk.HIGH: CrisisSeverity.SEVERE,
            FloodRisk.VERY_HIGH: CrisisSeverity.EXTREME,
            FloodRisk.EXTREME: CrisisSeverity.CATASTROPHIC,
        }

        alert = CrisisAlert(
            alert_id=f"alert-{uuid.uuid4().hex[:8]}",
            crisis_type=CrisisType.FLOOD,
            severity=severity_map.get(prediction.flood_risk, CrisisSeverity.MODERATE),
            alert_level=AlertLevel.WARNING if prediction.evacuation_recommended else AlertLevel.WATCH,
            title=f"Flood {prediction.flood_risk.value.replace('_', ' ').title()} Risk",
            description=f"Predicted water level: {prediction.predicted_water_level_ft:.1f} ft (flood stage: {prediction.flood_stage_ft:.1f} ft)",
            location=prediction.location,
            affected_area_km2=50,
            population_at_risk=prediction.affected_structures * 3,
            start_time=datetime.utcnow(),
            expected_duration_hours=prediction.time_to_flood_hours,
            recommendations=[
                "Move to higher ground if in flood zone",
                "Do not drive through flooded roads",
                "Prepare emergency supplies",
                "Monitor water levels",
            ],
            source="Flood Prediction Model",
            confidence_score=prediction.confidence_score,
        )

        self._alerts[alert.alert_id] = alert
        return alert

    def get_prediction(self, prediction_id: str) -> Optional[FloodPrediction]:
        """Get flood prediction by ID."""
        return self._predictions.get(prediction_id)

    def get_predictions(self, flood_risk: Optional[FloodRisk] = None) -> List[FloodPrediction]:
        """Get all predictions, optionally filtered by risk level."""
        predictions = list(self._predictions.values())
        if flood_risk:
            predictions = [p for p in predictions if p.flood_risk == flood_risk]
        return predictions


class FireSpreadModel:
    """
    Models fire spread using weather, terrain, and fuel data (stub).
    """

    def __init__(self):
        self._fires: Dict[str, FireSpread] = {}
        self._alerts: Dict[str, CrisisAlert] = {}

    def model_fire(
        self,
        name: str,
        origin: Dict[str, float],
        area_acres: float,
        containment_percent: float,
        wind_speed_mph: float,
        wind_direction: str,
        humidity_percent: float,
        temperature_f: float,
        fuel_type: str,
    ) -> FireSpread:
        """Model fire spread based on conditions."""
        fire_id = f"fire-{uuid.uuid4().hex[:8]}"

        spread_rate = self._calculate_spread_rate(wind_speed_mph, humidity_percent, temperature_f)
        spread_direction = self._calculate_spread_direction(wind_direction)
        perimeter = self._calculate_perimeter(origin, area_acres)
        predicted_spread = self._predict_spread_24h(origin, spread_rate, spread_direction, area_acres)

        fire = FireSpread(
            fire_id=fire_id,
            name=name,
            origin=origin,
            current_perimeter=perimeter,
            area_acres=area_acres,
            containment_percent=containment_percent,
            spread_rate=spread_rate,
            spread_direction=spread_direction,
            wind_speed_mph=wind_speed_mph,
            wind_direction=wind_direction,
            humidity_percent=humidity_percent,
            temperature_f=temperature_f,
            fuel_type=fuel_type,
            structures_threatened=self._estimate_structures_threatened(area_acres, spread_rate),
            structures_destroyed=0,
            evacuation_zones=self._determine_evacuation_zones(origin, spread_direction),
            predicted_spread_24h=predicted_spread,
        )

        self._fires[fire_id] = fire

        if spread_rate in [FireSpreadRate.FAST, FireSpreadRate.EXTREME]:
            self._generate_fire_alert(fire)

        return fire

    def _calculate_spread_rate(
        self,
        wind_speed: float,
        humidity: float,
        temperature: float,
    ) -> FireSpreadRate:
        """Calculate fire spread rate based on conditions."""
        risk_score = (wind_speed / 10) + ((100 - humidity) / 20) + ((temperature - 60) / 20)

        if risk_score < 5:
            return FireSpreadRate.SLOW
        elif risk_score < 10:
            return FireSpreadRate.MODERATE
        elif risk_score < 15:
            return FireSpreadRate.FAST
        else:
            return FireSpreadRate.EXTREME

    def _calculate_spread_direction(self, wind_direction: str) -> str:
        """Fire spreads in the direction the wind is blowing."""
        return wind_direction

    def _calculate_perimeter(self, origin: Dict[str, float], area_acres: float) -> List[Dict[str, float]]:
        """Calculate fire perimeter as polygon."""
        radius = math.sqrt(area_acres / math.pi) * 0.001
        lat, lon = origin.get("lat", 0), origin.get("lon", 0)

        perimeter = []
        for angle in range(0, 360, 30):
            rad = math.radians(angle)
            perimeter.append({
                "lat": lat + radius * math.cos(rad),
                "lon": lon + radius * math.sin(rad),
            })

        return perimeter

    def _predict_spread_24h(
        self,
        origin: Dict[str, float],
        spread_rate: FireSpreadRate,
        direction: str,
        current_area: float,
    ) -> List[Dict[str, float]]:
        """Predict fire spread over 24 hours."""
        rate_multiplier = {
            FireSpreadRate.SLOW: 1.1,
            FireSpreadRate.MODERATE: 1.3,
            FireSpreadRate.FAST: 1.6,
            FireSpreadRate.EXTREME: 2.0,
        }

        multiplier = rate_multiplier.get(spread_rate, 1.2)
        predicted_area = current_area * multiplier

        return self._calculate_perimeter(origin, predicted_area)

    def _estimate_structures_threatened(self, area: float, spread_rate: FireSpreadRate) -> int:
        """Estimate structures threatened by fire."""
        base = int(area * 0.5)
        rate_multiplier = {
            FireSpreadRate.SLOW: 1,
            FireSpreadRate.MODERATE: 2,
            FireSpreadRate.FAST: 4,
            FireSpreadRate.EXTREME: 8,
        }
        return base * rate_multiplier.get(spread_rate, 1)

    def _determine_evacuation_zones(self, origin: Dict[str, float], direction: str) -> List[str]:
        """Determine evacuation zones based on fire location and spread direction."""
        return ["Zone A", "Zone B", "Zone C"]

    def _generate_fire_alert(self, fire: FireSpread) -> CrisisAlert:
        """Generate crisis alert for fire."""
        severity_map = {
            FireSpreadRate.SLOW: CrisisSeverity.MINOR,
            FireSpreadRate.MODERATE: CrisisSeverity.MODERATE,
            FireSpreadRate.FAST: CrisisSeverity.SEVERE,
            FireSpreadRate.EXTREME: CrisisSeverity.EXTREME,
        }

        alert = CrisisAlert(
            alert_id=f"alert-{uuid.uuid4().hex[:8]}",
            crisis_type=CrisisType.FIRE,
            severity=severity_map.get(fire.spread_rate, CrisisSeverity.MODERATE),
            alert_level=AlertLevel.EMERGENCY if fire.spread_rate == FireSpreadRate.EXTREME else AlertLevel.WARNING,
            title=f"{fire.name} - {fire.area_acres:.0f} Acres",
            description=f"Wildfire spreading {fire.spread_rate.value} to the {fire.spread_direction}. {fire.containment_percent:.0f}% contained.",
            location=fire.origin,
            affected_area_km2=fire.area_acres * 0.00404686,
            population_at_risk=fire.structures_threatened * 3,
            start_time=datetime.utcnow(),
            expected_duration_hours=48,
            recommendations=[
                "Evacuate if in evacuation zone",
                "Close windows and doors",
                "Prepare to leave immediately",
                "Monitor air quality",
            ],
            source="Fire Spread Model",
            confidence_score=0.8,
        )

        self._alerts[alert.alert_id] = alert
        return alert

    def get_fire(self, fire_id: str) -> Optional[FireSpread]:
        """Get fire by ID."""
        return self._fires.get(fire_id)

    def get_active_fires(self) -> List[FireSpread]:
        """Get all active fires."""
        return list(self._fires.values())


class EarthquakeShakeModel:
    """
    Models earthquake shake intensity using USGS data (stub).
    """

    def __init__(self):
        self._earthquakes: Dict[str, EarthquakeData] = {}
        self._alerts: Dict[str, CrisisAlert] = {}

    def fetch_usgs_data(self) -> List[Dict[str, Any]]:
        """Fetch earthquake data from USGS (stub)."""
        return []

    def model_earthquake(
        self,
        magnitude: float,
        depth_km: float,
        epicenter: Dict[str, float],
        location_description: str,
    ) -> EarthquakeData:
        """Model earthquake impact."""
        earthquake_id = f"eq-{uuid.uuid4().hex[:8]}"

        shake_intensity = self._calculate_shake_intensity(magnitude, depth_km)
        affected_radius = self._calculate_affected_radius(magnitude)
        population = self._estimate_population_affected(epicenter, affected_radius)
        aftershock_prob = self._calculate_aftershock_probability(magnitude)
        tsunami_risk = self._assess_tsunami_risk(epicenter, magnitude)
        damage_estimate = self._estimate_infrastructure_damage(magnitude, depth_km)

        earthquake = EarthquakeData(
            earthquake_id=earthquake_id,
            magnitude=magnitude,
            depth_km=depth_km,
            epicenter=epicenter,
            location_description=location_description,
            shake_intensity=shake_intensity,
            affected_radius_km=affected_radius,
            population_affected=population,
            aftershock_probability=aftershock_prob,
            tsunami_risk=tsunami_risk,
            infrastructure_damage_estimate=damage_estimate,
            occurred_at=datetime.utcnow(),
        )

        self._earthquakes[earthquake_id] = earthquake

        if magnitude >= 4.0:
            self._generate_earthquake_alert(earthquake)

        return earthquake

    def _calculate_shake_intensity(self, magnitude: float, depth: float) -> str:
        """Calculate Modified Mercalli Intensity."""
        intensity_score = magnitude - (depth / 50)

        if intensity_score < 2:
            return "I - Not felt"
        elif intensity_score < 3:
            return "II-III - Weak"
        elif intensity_score < 4:
            return "IV - Light"
        elif intensity_score < 5:
            return "V - Moderate"
        elif intensity_score < 6:
            return "VI - Strong"
        elif intensity_score < 7:
            return "VII - Very Strong"
        elif intensity_score < 8:
            return "VIII - Severe"
        elif intensity_score < 9:
            return "IX - Violent"
        else:
            return "X+ - Extreme"

    def _calculate_affected_radius(self, magnitude: float) -> float:
        """Calculate affected radius in km based on magnitude."""
        return 10 ** (0.5 * magnitude - 1)

    def _estimate_population_affected(self, epicenter: Dict[str, float], radius: float) -> int:
        """Estimate population in affected area."""
        return int(radius * radius * 100)

    def _calculate_aftershock_probability(self, magnitude: float) -> float:
        """Calculate probability of significant aftershocks."""
        return min(0.95, 0.1 * magnitude)

    def _assess_tsunami_risk(self, epicenter: Dict[str, float], magnitude: float) -> bool:
        """Assess tsunami risk for coastal earthquakes."""
        lon = epicenter.get("lon", 0)
        return magnitude >= 7.0 and -130 < lon < -70

    def _estimate_infrastructure_damage(self, magnitude: float, depth: float) -> str:
        """Estimate infrastructure damage level."""
        if magnitude < 4:
            return "None to minimal"
        elif magnitude < 5:
            return "Minor damage possible"
        elif magnitude < 6:
            return "Moderate damage likely"
        elif magnitude < 7:
            return "Significant damage expected"
        elif magnitude < 8:
            return "Major damage expected"
        else:
            return "Catastrophic damage expected"

    def _generate_earthquake_alert(self, earthquake: EarthquakeData) -> CrisisAlert:
        """Generate crisis alert for earthquake."""
        if earthquake.magnitude < 5:
            severity = CrisisSeverity.MINOR
        elif earthquake.magnitude < 6:
            severity = CrisisSeverity.MODERATE
        elif earthquake.magnitude < 7:
            severity = CrisisSeverity.SEVERE
        elif earthquake.magnitude < 8:
            severity = CrisisSeverity.EXTREME
        else:
            severity = CrisisSeverity.CATASTROPHIC

        alert = CrisisAlert(
            alert_id=f"alert-{uuid.uuid4().hex[:8]}",
            crisis_type=CrisisType.EARTHQUAKE,
            severity=severity,
            alert_level=AlertLevel.EMERGENCY if earthquake.magnitude >= 6 else AlertLevel.WARNING,
            title=f"M{earthquake.magnitude:.1f} Earthquake - {earthquake.location_description}",
            description=f"Earthquake at depth {earthquake.depth_km:.1f} km. {earthquake.shake_intensity}",
            location=earthquake.epicenter,
            affected_area_km2=math.pi * earthquake.affected_radius_km ** 2,
            population_at_risk=earthquake.population_affected,
            start_time=earthquake.occurred_at,
            expected_duration_hours=None,
            recommendations=[
                "Drop, Cover, and Hold On",
                "Check for injuries and damage",
                "Be prepared for aftershocks",
                "Avoid damaged structures",
            ],
            source="USGS/Shake Model",
            confidence_score=0.9,
        )

        self._alerts[alert.alert_id] = alert
        return alert

    def get_earthquake(self, earthquake_id: str) -> Optional[EarthquakeData]:
        """Get earthquake by ID."""
        return self._earthquakes.get(earthquake_id)

    def get_recent_earthquakes(self, min_magnitude: float = 0) -> List[EarthquakeData]:
        """Get recent earthquakes above minimum magnitude."""
        return [eq for eq in self._earthquakes.values() if eq.magnitude >= min_magnitude]


class ExplosionImpactModel:
    """
    Models explosion impact including pressure waves and thermal effects.
    """

    def __init__(self):
        self._explosions: Dict[str, ExplosionImpact] = {}
        self._alerts: Dict[str, CrisisAlert] = {}

    def model_explosion(
        self,
        location: Dict[str, float],
        explosion_type: str,
        estimated_yield_kg_tnt: float,
        wind_direction: str,
        hazmat_materials: Optional[List[str]] = None,
    ) -> ExplosionImpact:
        """Model explosion impact."""
        explosion_id = f"exp-{uuid.uuid4().hex[:8]}"

        blast_radius = self._calculate_blast_radius(estimated_yield_kg_tnt)
        thermal_radius = self._calculate_thermal_radius(estimated_yield_kg_tnt)
        overpressure_zones = self._calculate_overpressure_zones(estimated_yield_kg_tnt)
        casualties = self._estimate_casualties(blast_radius, thermal_radius, location)
        structures = self._estimate_structures_affected(blast_radius, location)
        hazmat_risk = hazmat_materials is not None and len(hazmat_materials) > 0
        evac_radius = blast_radius * 3 if hazmat_risk else blast_radius * 1.5

        plume = None
        if hazmat_risk:
            plume = self._calculate_plume_projection(location, wind_direction)

        explosion = ExplosionImpact(
            explosion_id=explosion_id,
            location=location,
            explosion_type=explosion_type,
            estimated_yield_kg_tnt=estimated_yield_kg_tnt,
            blast_radius_m=blast_radius,
            thermal_radius_m=thermal_radius,
            overpressure_zones=overpressure_zones,
            casualties_estimate=casualties,
            structures_affected=structures,
            hazmat_risk=hazmat_risk,
            evacuation_radius_m=evac_radius,
            wind_direction=wind_direction,
            plume_projection=plume,
        )

        self._explosions[explosion_id] = explosion
        self._generate_explosion_alert(explosion)

        return explosion

    def _calculate_blast_radius(self, yield_kg: float) -> float:
        """Calculate blast radius in meters using scaled distance."""
        return 4.5 * (yield_kg ** (1/3))

    def _calculate_thermal_radius(self, yield_kg: float) -> float:
        """Calculate thermal effect radius in meters."""
        return 2.5 * (yield_kg ** (1/3))

    def _calculate_overpressure_zones(self, yield_kg: float) -> List[Dict[str, Any]]:
        """Calculate overpressure zones."""
        base_radius = yield_kg ** (1/3)

        return [
            {"zone": "severe", "radius_m": base_radius * 2, "overpressure_psi": 10},
            {"zone": "moderate", "radius_m": base_radius * 4, "overpressure_psi": 5},
            {"zone": "light", "radius_m": base_radius * 8, "overpressure_psi": 2},
            {"zone": "glass_breakage", "radius_m": base_radius * 15, "overpressure_psi": 0.5},
        ]

    def _estimate_casualties(
        self,
        blast_radius: float,
        thermal_radius: float,
        location: Dict[str, float],
    ) -> Dict[str, int]:
        """Estimate casualties based on impact zones."""
        population_density = 1000
        blast_area = math.pi * blast_radius ** 2
        thermal_area = math.pi * thermal_radius ** 2

        fatalities = int((blast_area / 1000000) * population_density * 0.5)
        injuries = int((thermal_area / 1000000) * population_density * 0.3)

        return {
            "fatalities": fatalities,
            "critical_injuries": injuries,
            "moderate_injuries": injuries * 2,
            "minor_injuries": injuries * 4,
        }

    def _estimate_structures_affected(self, blast_radius: float, location: Dict[str, float]) -> int:
        """Estimate structures affected by explosion."""
        structure_density = 50
        area_km2 = math.pi * (blast_radius / 1000) ** 2
        return int(area_km2 * structure_density)

    def _calculate_plume_projection(
        self,
        location: Dict[str, float],
        wind_direction: str,
    ) -> List[Dict[str, float]]:
        """Calculate hazmat plume projection."""
        lat, lon = location.get("lat", 0), location.get("lon", 0)

        direction_vectors = {
            "N": (0.01, 0),
            "NE": (0.007, 0.007),
            "E": (0, 0.01),
            "SE": (-0.007, 0.007),
            "S": (-0.01, 0),
            "SW": (-0.007, -0.007),
            "W": (0, -0.01),
            "NW": (0.007, -0.007),
        }

        dlat, dlon = direction_vectors.get(wind_direction, (0.01, 0))

        plume = []
        for i in range(10):
            plume.append({
                "lat": lat + dlat * i,
                "lon": lon + dlon * i,
                "concentration": max(0.1, 1.0 - i * 0.1),
            })

        return plume

    def _generate_explosion_alert(self, explosion: ExplosionImpact) -> CrisisAlert:
        """Generate crisis alert for explosion."""
        if explosion.estimated_yield_kg_tnt < 10:
            severity = CrisisSeverity.MINOR
        elif explosion.estimated_yield_kg_tnt < 100:
            severity = CrisisSeverity.MODERATE
        elif explosion.estimated_yield_kg_tnt < 1000:
            severity = CrisisSeverity.SEVERE
        else:
            severity = CrisisSeverity.EXTREME

        recommendations = [
            "Evacuate the area immediately",
            "Move upwind from the explosion site",
            "Seek medical attention if injured",
            "Report any suspicious activity",
        ]

        if explosion.hazmat_risk:
            recommendations.extend([
                "Avoid breathing fumes or smoke",
                "Cover nose and mouth with cloth",
                "Shelter in place if unable to evacuate",
            ])

        alert = CrisisAlert(
            alert_id=f"alert-{uuid.uuid4().hex[:8]}",
            crisis_type=CrisisType.EXPLOSION,
            severity=severity,
            alert_level=AlertLevel.CRITICAL if explosion.hazmat_risk else AlertLevel.EMERGENCY,
            title=f"Explosion - {explosion.explosion_type}",
            description=f"Explosion detected. Blast radius: {explosion.blast_radius_m:.0f}m. Evacuation radius: {explosion.evacuation_radius_m:.0f}m.",
            location=explosion.location,
            affected_area_km2=math.pi * (explosion.evacuation_radius_m / 1000) ** 2,
            population_at_risk=sum(explosion.casualties_estimate.values()),
            start_time=datetime.utcnow(),
            expected_duration_hours=24 if explosion.hazmat_risk else 6,
            recommendations=recommendations,
            source="Explosion Impact Model",
            confidence_score=0.7,
        )

        self._alerts[alert.alert_id] = alert
        return alert

    def get_explosion(self, explosion_id: str) -> Optional[ExplosionImpact]:
        """Get explosion by ID."""
        return self._explosions.get(explosion_id)

    def get_explosions(self) -> List[ExplosionImpact]:
        """Get all modeled explosions."""
        return list(self._explosions.values())


class CrisisDetectionEngine:
    """
    Main crisis detection engine coordinating all crisis models.
    """

    def __init__(self):
        self.storm_tracker = StormTracker()
        self.flood_predictor = FloodPredictor()
        self.fire_model = FireSpreadModel()
        self.earthquake_model = EarthquakeShakeModel()
        self.explosion_model = ExplosionImpactModel()
        self._all_alerts: Dict[str, CrisisAlert] = {}

    def get_all_active_alerts(self) -> List[CrisisAlert]:
        """Get all active crisis alerts from all models."""
        alerts = []
        alerts.extend(self.storm_tracker.get_alerts())
        alerts.extend(self.flood_predictor._alerts.values())
        alerts.extend(self.fire_model._alerts.values())
        alerts.extend(self.earthquake_model._alerts.values())
        alerts.extend(self.explosion_model._alerts.values())
        return [a for a in alerts if a.is_active]

    def get_alerts_by_severity(self, severity: CrisisSeverity) -> List[CrisisAlert]:
        """Get alerts filtered by severity."""
        return [a for a in self.get_all_active_alerts() if a.severity == severity]

    def get_alerts_by_type(self, crisis_type: CrisisType) -> List[CrisisAlert]:
        """Get alerts filtered by crisis type."""
        return [a for a in self.get_all_active_alerts() if a.crisis_type == crisis_type]

    def get_critical_alerts(self) -> List[CrisisAlert]:
        """Get all critical and emergency level alerts."""
        return [
            a for a in self.get_all_active_alerts()
            if a.alert_level in [AlertLevel.CRITICAL, AlertLevel.EMERGENCY]
        ]

    def get_metrics(self) -> Dict[str, Any]:
        """Get crisis detection metrics."""
        alerts = self.get_all_active_alerts()
        return {
            "total_active_alerts": len(alerts),
            "by_type": {
                ct.value: len([a for a in alerts if a.crisis_type == ct])
                for ct in CrisisType
            },
            "by_severity": {
                cs.value: len([a for a in alerts if a.severity == cs])
                for cs in CrisisSeverity
            },
            "active_storms": len(self.storm_tracker.get_active_storms()),
            "active_fires": len(self.fire_model.get_active_fires()),
            "flood_predictions": len(self.flood_predictor.get_predictions()),
            "recent_earthquakes": len(self.earthquake_model.get_recent_earthquakes(4.0)),
        }
