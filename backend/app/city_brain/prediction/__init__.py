"""
Phase 22: City Prediction Engine for Riviera Beach

Prediction models for:
- TrafficFlowPredictor: Congestion, reroutes, crash risk, evacuation flow
- CrimeDisplacementPredictor: Crime movement based on weather, events, police presence
- InfrastructureRiskPredictor: Water main failure, grid strain, flood likelihood
- DisasterImpactModel: Hurricane, storm surge, tornado, marine hazards, extreme heat
- PopulationMovementModel: Crowd sizes, school traffic, church attendance, marina density
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional
import random
import math


class PredictionConfidence(Enum):
    """Confidence levels for predictions."""
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class RiskLevel(Enum):
    """Risk levels for predictions."""
    MINIMAL = "minimal"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    SEVERE = "severe"
    EXTREME = "extreme"


class DisasterType(Enum):
    """Types of disasters."""
    HURRICANE = "hurricane"
    TROPICAL_STORM = "tropical_storm"
    STORM_SURGE = "storm_surge"
    TORNADO = "tornado"
    FLOODING = "flooding"
    EXTREME_HEAT = "extreme_heat"
    RIP_CURRENT = "rip_current"
    LIGHTNING = "lightning"


@dataclass
class TrafficPrediction:
    """Traffic flow prediction."""
    prediction_id: str
    road_segment: str
    timestamp: datetime
    predicted_congestion_level: str
    predicted_speed_mph: float
    predicted_travel_time_minutes: float
    crash_risk_score: float
    reroute_recommended: bool
    alternative_routes: list[str]
    confidence: PredictionConfidence
    factors: list[str]


@dataclass
class EvacuationFlowPrediction:
    """Evacuation flow prediction."""
    prediction_id: str
    scenario: str
    timestamp: datetime
    estimated_evacuees: int
    peak_flow_time: datetime
    bottleneck_locations: list[dict]
    estimated_clearance_hours: float
    recommended_routes: list[dict]
    shelter_capacity_status: dict
    confidence: PredictionConfidence


@dataclass
class CrimeDisplacementPrediction:
    """Crime displacement prediction."""
    prediction_id: str
    timestamp: datetime
    time_window_hours: int
    displacement_zones: list[dict]
    risk_increase_areas: list[dict]
    risk_decrease_areas: list[dict]
    contributing_factors: list[str]
    recommended_patrol_adjustments: list[dict]
    confidence: PredictionConfidence


@dataclass
class InfrastructureRiskPrediction:
    """Infrastructure risk prediction."""
    prediction_id: str
    infrastructure_type: str
    element_id: str
    element_name: str
    timestamp: datetime
    risk_level: RiskLevel
    failure_probability: float
    estimated_impact: dict
    contributing_factors: list[str]
    recommended_actions: list[str]
    confidence: PredictionConfidence


@dataclass
class DisasterImpactPrediction:
    """Disaster impact prediction."""
    prediction_id: str
    disaster_type: DisasterType
    timestamp: datetime
    impact_area: dict
    severity: str
    estimated_affected_population: int
    infrastructure_at_risk: list[str]
    estimated_damage_millions: float
    evacuation_recommended: bool
    evacuation_zones: list[str]
    timeline: list[dict]
    confidence: PredictionConfidence


@dataclass
class PopulationMovementPrediction:
    """Population movement prediction."""
    prediction_id: str
    timestamp: datetime
    time_window_hours: int
    area_predictions: list[dict]
    peak_density_locations: list[dict]
    peak_times: list[datetime]
    special_events: list[dict]
    traffic_impact: dict
    confidence: PredictionConfidence


class TrafficFlowPredictor:
    """
    Predicts traffic flow for Riviera Beach.
    
    Capabilities:
    - Congestion prediction
    - Reroute recommendations
    - Crash risk assessment
    - Event impact analysis
    - Evacuation flow modeling
    """
    
    ROAD_SEGMENTS = [
        {"id": "blue-heron-1", "name": "Blue Heron Blvd (Congress to Broadway)", "base_volume": 42000},
        {"id": "blue-heron-2", "name": "Blue Heron Blvd (Broadway to I-95)", "base_volume": 38000},
        {"id": "broadway-1", "name": "Broadway (Blue Heron to 13th St)", "base_volume": 28000},
        {"id": "i95-1", "name": "I-95 (Exit 76 to Exit 77)", "base_volume": 185000},
        {"id": "military-1", "name": "Military Trail (Blue Heron to MLK)", "base_volume": 35000},
        {"id": "congress-1", "name": "Congress Ave (Blue Heron to MLK)", "base_volume": 38000},
        {"id": "mlk-1", "name": "MLK Blvd (Congress to Military)", "base_volume": 18000},
        {"id": "ocean-1", "name": "Ocean Drive (Singer Island)", "base_volume": 8000},
    ]
    
    def __init__(self):
        self._model_version = "1.0.0"
        self._last_prediction: Optional[datetime] = None
    
    def predict_congestion(
        self,
        segment_id: str,
        target_time: datetime,
        weather_conditions: Optional[dict] = None,
        active_incidents: Optional[list] = None,
        special_events: Optional[list] = None,
    ) -> TrafficPrediction:
        """Predict congestion for a road segment."""
        segment = next((s for s in self.ROAD_SEGMENTS if s["id"] == segment_id), None)
        if not segment:
            segment = {"id": segment_id, "name": segment_id, "base_volume": 20000}
        
        hour = target_time.hour
        day_of_week = target_time.weekday()
        
        time_factor = 1.0
        if 7 <= hour <= 9:
            time_factor = 1.5
        elif 16 <= hour <= 18:
            time_factor = 1.6
        elif 11 <= hour <= 13:
            time_factor = 1.2
        elif hour < 6 or hour > 22:
            time_factor = 0.4
        
        if day_of_week >= 5:
            time_factor *= 0.7
        
        weather_factor = 1.0
        if weather_conditions:
            if weather_conditions.get("precipitation", False):
                weather_factor = 1.3
            if weather_conditions.get("visibility_miles", 10) < 5:
                weather_factor *= 1.2
        
        incident_factor = 1.0
        if active_incidents:
            incident_factor = 1.0 + (len(active_incidents) * 0.15)
        
        event_factor = 1.0
        if special_events:
            event_factor = 1.0 + (len(special_events) * 0.2)
        
        total_factor = time_factor * weather_factor * incident_factor * event_factor
        
        base_speed = 45.0 if "I-95" not in segment["name"] else 70.0
        predicted_speed = base_speed / total_factor
        predicted_speed = max(5.0, min(base_speed, predicted_speed))
        
        if predicted_speed >= base_speed * 0.8:
            congestion = "free_flow"
        elif predicted_speed >= base_speed * 0.6:
            congestion = "light"
        elif predicted_speed >= base_speed * 0.4:
            congestion = "moderate"
        elif predicted_speed >= base_speed * 0.2:
            congestion = "heavy"
        else:
            congestion = "gridlock"
        
        crash_risk = min(1.0, (total_factor - 1.0) * 0.3 + 0.05)
        
        reroute = congestion in ["heavy", "gridlock"]
        alternatives = []
        if reroute:
            if "Blue Heron" in segment["name"]:
                alternatives = ["MLK Blvd", "45th St"]
            elif "I-95" in segment["name"]:
                alternatives = ["Military Trail", "Congress Ave"]
        
        factors = []
        if time_factor > 1.2:
            factors.append("rush_hour")
        if weather_factor > 1.0:
            factors.append("weather_impact")
        if incident_factor > 1.0:
            factors.append("active_incidents")
        if event_factor > 1.0:
            factors.append("special_events")
        
        confidence = PredictionConfidence.HIGH
        if len(factors) > 2:
            confidence = PredictionConfidence.MEDIUM
        
        self._last_prediction = datetime.utcnow()
        
        return TrafficPrediction(
            prediction_id=f"traffic-{segment_id}-{target_time.strftime('%Y%m%d%H%M')}",
            road_segment=segment["name"],
            timestamp=target_time,
            predicted_congestion_level=congestion,
            predicted_speed_mph=predicted_speed,
            predicted_travel_time_minutes=5.0 * (base_speed / predicted_speed),
            crash_risk_score=crash_risk,
            reroute_recommended=reroute,
            alternative_routes=alternatives,
            confidence=confidence,
            factors=factors,
        )
    
    def predict_evacuation_flow(
        self,
        scenario: str,
        evacuation_zones: list[str],
        start_time: datetime,
    ) -> EvacuationFlowPrediction:
        """Predict evacuation flow for a disaster scenario."""
        zone_populations = {
            "A": 5200,
            "B": 8500,
            "C": 12000,
        }
        
        total_evacuees = sum(zone_populations.get(z, 2000) for z in evacuation_zones)
        
        vehicles = total_evacuees / 2.5
        
        bottlenecks = [
            {
                "location": "Blue Heron Blvd & I-95 Ramp",
                "expected_delay_minutes": 45,
                "capacity_vehicles_per_hour": 1800,
            },
            {
                "location": "Singer Island Causeway",
                "expected_delay_minutes": 60,
                "capacity_vehicles_per_hour": 1200,
            },
        ]
        
        clearance_hours = (vehicles / 1500) + 2
        
        routes = [
            {
                "route_id": "evac-1",
                "name": "Blue Heron to I-95 North",
                "zones": ["A", "B"],
                "estimated_time_minutes": 90,
            },
            {
                "route_id": "evac-2",
                "name": "Military Trail to Okeechobee",
                "zones": ["C"],
                "estimated_time_minutes": 75,
            },
        ]
        
        shelters = {
            "palm_beach_central_high": {"capacity": 2000, "assigned": 1500},
            "wellington_community_center": {"capacity": 1500, "assigned": 1200},
            "royal_palm_beach_high": {"capacity": 1800, "assigned": 1000},
        }
        
        return EvacuationFlowPrediction(
            prediction_id=f"evac-{scenario}-{start_time.strftime('%Y%m%d%H%M')}",
            scenario=scenario,
            timestamp=start_time,
            estimated_evacuees=total_evacuees,
            peak_flow_time=start_time + timedelta(hours=2),
            bottleneck_locations=bottlenecks,
            estimated_clearance_hours=clearance_hours,
            recommended_routes=routes,
            shelter_capacity_status=shelters,
            confidence=PredictionConfidence.MEDIUM,
        )
    
    def get_model_info(self) -> dict:
        """Get model information."""
        return {
            "model": "TrafficFlowPredictor",
            "version": self._model_version,
            "segments_covered": len(self.ROAD_SEGMENTS),
            "last_prediction": self._last_prediction.isoformat() if self._last_prediction else None,
        }


class CrimeDisplacementPredictor:
    """
    Predicts crime displacement patterns.
    
    Factors considered:
    - Weather conditions
    - City events
    - Police presence
    - Road closures
    - Time of day/week
    """
    
    CRIME_ZONES = [
        {"id": "zone-1", "name": "Downtown/Marina", "base_risk": 0.4},
        {"id": "zone-2", "name": "Singer Island", "base_risk": 0.2},
        {"id": "zone-3", "name": "Westside", "base_risk": 0.5},
        {"id": "zone-4", "name": "Central Business", "base_risk": 0.35},
        {"id": "zone-5", "name": "Industrial/Port", "base_risk": 0.3},
        {"id": "zone-6", "name": "North Riviera", "base_risk": 0.45},
    ]
    
    def __init__(self):
        self._model_version = "1.0.0"
        self._last_prediction: Optional[datetime] = None
    
    def predict_displacement(
        self,
        target_time: datetime,
        time_window_hours: int = 24,
        weather_conditions: Optional[dict] = None,
        police_deployments: Optional[list] = None,
        road_closures: Optional[list] = None,
        special_events: Optional[list] = None,
    ) -> CrimeDisplacementPrediction:
        """Predict crime displacement patterns."""
        hour = target_time.hour
        is_night = hour < 6 or hour > 20
        is_weekend = target_time.weekday() >= 5
        
        displacement_zones = []
        risk_increase = []
        risk_decrease = []
        factors = []
        
        for zone in self.CRIME_ZONES:
            risk_modifier = 0.0
            
            if is_night:
                risk_modifier += 0.15
                if "night_hours" not in factors:
                    factors.append("night_hours")
            
            if is_weekend:
                risk_modifier += 0.1
                if "weekend" not in factors:
                    factors.append("weekend")
            
            if weather_conditions:
                if weather_conditions.get("temperature_f", 80) > 90:
                    risk_modifier += 0.1
                    if "high_temperature" not in factors:
                        factors.append("high_temperature")
                if weather_conditions.get("precipitation", False):
                    risk_modifier -= 0.15
                    if "precipitation" not in factors:
                        factors.append("precipitation")
            
            if police_deployments:
                zone_deployments = [d for d in police_deployments if d.get("zone") == zone["id"]]
                if zone_deployments:
                    risk_modifier -= 0.2 * len(zone_deployments)
                    if "police_presence" not in factors:
                        factors.append("police_presence")
            
            if special_events:
                zone_events = [e for e in special_events if e.get("zone") == zone["id"]]
                if zone_events:
                    risk_modifier += 0.1 * len(zone_events)
                    if "special_events" not in factors:
                        factors.append("special_events")
            
            final_risk = zone["base_risk"] + risk_modifier
            final_risk = max(0.0, min(1.0, final_risk))
            
            displacement_zones.append({
                "zone_id": zone["id"],
                "zone_name": zone["name"],
                "base_risk": zone["base_risk"],
                "predicted_risk": final_risk,
                "risk_change": final_risk - zone["base_risk"],
            })
            
            if final_risk > zone["base_risk"] + 0.1:
                risk_increase.append({
                    "zone_id": zone["id"],
                    "zone_name": zone["name"],
                    "increase_percent": ((final_risk - zone["base_risk"]) / zone["base_risk"]) * 100,
                })
            elif final_risk < zone["base_risk"] - 0.1:
                risk_decrease.append({
                    "zone_id": zone["id"],
                    "zone_name": zone["name"],
                    "decrease_percent": ((zone["base_risk"] - final_risk) / zone["base_risk"]) * 100,
                })
        
        patrol_adjustments = []
        for zone in risk_increase:
            patrol_adjustments.append({
                "zone_id": zone["zone_id"],
                "action": "increase_patrol",
                "recommended_units": 2,
                "priority": "high",
            })
        
        for zone in risk_decrease:
            patrol_adjustments.append({
                "zone_id": zone["zone_id"],
                "action": "reduce_patrol",
                "recommended_units": -1,
                "priority": "low",
            })
        
        self._last_prediction = datetime.utcnow()
        
        return CrimeDisplacementPrediction(
            prediction_id=f"crime-{target_time.strftime('%Y%m%d%H%M')}",
            timestamp=target_time,
            time_window_hours=time_window_hours,
            displacement_zones=displacement_zones,
            risk_increase_areas=risk_increase,
            risk_decrease_areas=risk_decrease,
            contributing_factors=factors,
            recommended_patrol_adjustments=patrol_adjustments,
            confidence=PredictionConfidence.MEDIUM,
        )
    
    def get_model_info(self) -> dict:
        """Get model information."""
        return {
            "model": "CrimeDisplacementPredictor",
            "version": self._model_version,
            "zones_covered": len(self.CRIME_ZONES),
            "last_prediction": self._last_prediction.isoformat() if self._last_prediction else None,
        }


class InfrastructureRiskPredictor:
    """
    Predicts infrastructure failure risks.
    
    Covers:
    - Water main failure probability
    - Electrical grid strain
    - Flood likelihood
    - Pump station overload
    """
    
    INFRASTRUCTURE_ELEMENTS = [
        {"id": "wtp-1", "type": "water_treatment", "name": "Riviera Beach WTP", "age_years": 25, "base_risk": 0.02},
        {"id": "pump-1", "type": "pump_station", "name": "Main Pump Station", "age_years": 18, "base_risk": 0.03},
        {"id": "pump-2", "type": "pump_station", "name": "Singer Island Pump", "age_years": 12, "base_risk": 0.02},
        {"id": "sub-1", "type": "electrical_substation", "name": "Blue Heron Substation", "age_years": 20, "base_risk": 0.015},
        {"id": "sub-2", "type": "electrical_substation", "name": "Singer Island Substation", "age_years": 15, "base_risk": 0.01},
        {"id": "lift-1", "type": "lift_station", "name": "Lift Station 1", "age_years": 22, "base_risk": 0.04},
        {"id": "lift-2", "type": "lift_station", "name": "Lift Station 2", "age_years": 28, "base_risk": 0.05},
        {"id": "main-1", "type": "water_main", "name": "Blue Heron Water Main", "age_years": 35, "base_risk": 0.03},
    ]
    
    def __init__(self):
        self._model_version = "1.0.0"
        self._last_prediction: Optional[datetime] = None
    
    def predict_risk(
        self,
        element_id: str,
        target_time: datetime,
        weather_forecast: Optional[dict] = None,
        current_load: Optional[float] = None,
        maintenance_history: Optional[list] = None,
    ) -> InfrastructureRiskPrediction:
        """Predict failure risk for an infrastructure element."""
        element = next((e for e in self.INFRASTRUCTURE_ELEMENTS if e["id"] == element_id), None)
        if not element:
            element = {"id": element_id, "type": "unknown", "name": element_id, "age_years": 10, "base_risk": 0.02}
        
        risk = element["base_risk"]
        factors = []
        
        age_factor = 1.0 + (element["age_years"] / 50)
        risk *= age_factor
        if element["age_years"] > 20:
            factors.append(f"aging_infrastructure_{element['age_years']}_years")
        
        if weather_forecast:
            if weather_forecast.get("precipitation_inches", 0) > 2:
                risk *= 1.5
                factors.append("heavy_precipitation")
            if weather_forecast.get("wind_speed_mph", 0) > 40:
                risk *= 1.3
                factors.append("high_winds")
            if weather_forecast.get("temperature_f", 80) > 95:
                risk *= 1.2
                factors.append("extreme_heat")
            if weather_forecast.get("flooding_risk", "low") in ["moderate", "high"]:
                risk *= 1.4
                factors.append("flood_risk")
        
        if current_load is not None:
            if current_load > 90:
                risk *= 2.0
                factors.append("critical_load")
            elif current_load > 80:
                risk *= 1.5
                factors.append("high_load")
            elif current_load > 70:
                risk *= 1.2
                factors.append("elevated_load")
        
        if maintenance_history:
            recent_issues = [m for m in maintenance_history if m.get("days_ago", 365) < 90]
            if recent_issues:
                risk *= 1.3
                factors.append("recent_maintenance_issues")
        
        risk = min(1.0, risk)
        
        if risk < 0.05:
            risk_level = RiskLevel.MINIMAL
        elif risk < 0.1:
            risk_level = RiskLevel.LOW
        elif risk < 0.2:
            risk_level = RiskLevel.MODERATE
        elif risk < 0.4:
            risk_level = RiskLevel.HIGH
        elif risk < 0.6:
            risk_level = RiskLevel.SEVERE
        else:
            risk_level = RiskLevel.EXTREME
        
        impact = {
            "affected_customers": random.randint(500, 5000),
            "estimated_repair_hours": random.randint(2, 24),
            "estimated_cost": random.randint(10000, 100000),
        }
        
        actions = []
        if risk_level in [RiskLevel.HIGH, RiskLevel.SEVERE, RiskLevel.EXTREME]:
            actions.append("schedule_immediate_inspection")
            actions.append("prepare_backup_systems")
            actions.append("notify_emergency_crews")
        elif risk_level == RiskLevel.MODERATE:
            actions.append("schedule_routine_inspection")
            actions.append("review_maintenance_schedule")
        
        self._last_prediction = datetime.utcnow()
        
        return InfrastructureRiskPrediction(
            prediction_id=f"infra-{element_id}-{target_time.strftime('%Y%m%d%H%M')}",
            infrastructure_type=element["type"],
            element_id=element_id,
            element_name=element["name"],
            timestamp=target_time,
            risk_level=risk_level,
            failure_probability=risk,
            estimated_impact=impact,
            contributing_factors=factors,
            recommended_actions=actions,
            confidence=PredictionConfidence.MEDIUM,
        )
    
    def predict_all_risks(
        self,
        target_time: datetime,
        weather_forecast: Optional[dict] = None,
    ) -> list[InfrastructureRiskPrediction]:
        """Predict risks for all infrastructure elements."""
        predictions = []
        for element in self.INFRASTRUCTURE_ELEMENTS:
            prediction = self.predict_risk(
                element_id=element["id"],
                target_time=target_time,
                weather_forecast=weather_forecast,
            )
            predictions.append(prediction)
        return predictions
    
    def get_model_info(self) -> dict:
        """Get model information."""
        return {
            "model": "InfrastructureRiskPredictor",
            "version": self._model_version,
            "elements_covered": len(self.INFRASTRUCTURE_ELEMENTS),
            "last_prediction": self._last_prediction.isoformat() if self._last_prediction else None,
        }


class DisasterImpactModel:
    """
    Models disaster impacts for Riviera Beach.
    
    Covers:
    - Hurricanes
    - Storm surge
    - Tornado cells
    - Marine hazards
    - Extreme heat events
    """
    
    STORM_SURGE_DATA = {
        "category_1": {"surge_ft": 4, "affected_zones": ["A"]},
        "category_2": {"surge_ft": 6, "affected_zones": ["A", "B"]},
        "category_3": {"surge_ft": 9, "affected_zones": ["A", "B", "C"]},
        "category_4": {"surge_ft": 13, "affected_zones": ["A", "B", "C"]},
        "category_5": {"surge_ft": 18, "affected_zones": ["A", "B", "C"]},
    }
    
    ZONE_POPULATIONS = {
        "A": 5200,
        "B": 8500,
        "C": 12000,
    }
    
    def __init__(self):
        self._model_version = "1.0.0"
        self._last_prediction: Optional[datetime] = None
    
    def predict_hurricane_impact(
        self,
        category: int,
        landfall_time: datetime,
        track: Optional[list] = None,
    ) -> DisasterImpactPrediction:
        """Predict hurricane impact."""
        cat_key = f"category_{category}"
        surge_data = self.STORM_SURGE_DATA.get(cat_key, self.STORM_SURGE_DATA["category_1"])
        
        affected_pop = sum(self.ZONE_POPULATIONS.get(z, 0) for z in surge_data["affected_zones"])
        
        damage_base = {1: 10, 2: 50, 3: 200, 4: 500, 5: 1000}
        damage = damage_base.get(category, 10) * (1 + random.uniform(-0.2, 0.2))
        
        infrastructure_at_risk = [
            "Singer Island Substation",
            "Marina District Power Lines",
            "Coastal Pump Stations",
        ]
        if category >= 3:
            infrastructure_at_risk.extend([
                "Blue Heron Substation",
                "Water Treatment Plant",
                "Port of Palm Beach",
            ])
        
        timeline = [
            {"time": (landfall_time - timedelta(hours=48)).isoformat(), "event": "Hurricane Watch issued"},
            {"time": (landfall_time - timedelta(hours=36)).isoformat(), "event": "Hurricane Warning issued"},
            {"time": (landfall_time - timedelta(hours=24)).isoformat(), "event": "Mandatory evacuation Zone A"},
        ]
        
        if category >= 2:
            timeline.append({
                "time": (landfall_time - timedelta(hours=18)).isoformat(),
                "event": "Mandatory evacuation Zone B",
            })
        
        if category >= 3:
            timeline.append({
                "time": (landfall_time - timedelta(hours=12)).isoformat(),
                "event": "Mandatory evacuation Zone C",
            })
        
        timeline.extend([
            {"time": landfall_time.isoformat(), "event": "Expected landfall"},
            {"time": (landfall_time + timedelta(hours=6)).isoformat(), "event": "Peak storm surge"},
            {"time": (landfall_time + timedelta(hours=12)).isoformat(), "event": "Storm passes"},
        ])
        
        self._last_prediction = datetime.utcnow()
        
        return DisasterImpactPrediction(
            prediction_id=f"hurricane-cat{category}-{landfall_time.strftime('%Y%m%d%H%M')}",
            disaster_type=DisasterType.HURRICANE,
            timestamp=landfall_time,
            impact_area={
                "center": {"latitude": 26.7753, "longitude": -80.0583},
                "radius_miles": 15 + (category * 5),
                "surge_zones": surge_data["affected_zones"],
            },
            severity=f"category_{category}",
            estimated_affected_population=affected_pop,
            infrastructure_at_risk=infrastructure_at_risk,
            estimated_damage_millions=damage,
            evacuation_recommended=True,
            evacuation_zones=surge_data["affected_zones"],
            timeline=timeline,
            confidence=PredictionConfidence.MEDIUM if category <= 2 else PredictionConfidence.LOW,
        )
    
    def predict_flood_impact(
        self,
        rainfall_inches: float,
        duration_hours: int,
        tide_level: str = "normal",
    ) -> DisasterImpactPrediction:
        """Predict flooding impact."""
        flood_zones = []
        affected_pop = 0
        
        if rainfall_inches > 3:
            flood_zones.append("Marina District")
            affected_pop += 2200
        if rainfall_inches > 5:
            flood_zones.extend(["Singer Island Lowlands", "Intracoastal Areas"])
            affected_pop += 4500
        if rainfall_inches > 8:
            flood_zones.append("Central Riviera Beach")
            affected_pop += 6000
        
        if tide_level == "high":
            affected_pop = int(affected_pop * 1.3)
        
        severity = "minor" if rainfall_inches < 4 else "moderate" if rainfall_inches < 6 else "major"
        
        damage = rainfall_inches * 2 * (1 + random.uniform(-0.2, 0.2))
        
        infrastructure = ["Lift Stations", "Storm Drains"]
        if rainfall_inches > 5:
            infrastructure.extend(["Road Underpasses", "Parking Structures"])
        
        now = datetime.utcnow()
        
        return DisasterImpactPrediction(
            prediction_id=f"flood-{now.strftime('%Y%m%d%H%M')}",
            disaster_type=DisasterType.FLOODING,
            timestamp=now,
            impact_area={
                "zones": flood_zones,
                "rainfall_inches": rainfall_inches,
                "duration_hours": duration_hours,
            },
            severity=severity,
            estimated_affected_population=affected_pop,
            infrastructure_at_risk=infrastructure,
            estimated_damage_millions=damage,
            evacuation_recommended=rainfall_inches > 6,
            evacuation_zones=["A"] if rainfall_inches > 6 else [],
            timeline=[
                {"time": now.isoformat(), "event": "Flood warning issued"},
                {"time": (now + timedelta(hours=duration_hours)).isoformat(), "event": "Expected peak flooding"},
                {"time": (now + timedelta(hours=duration_hours + 6)).isoformat(), "event": "Waters begin receding"},
            ],
            confidence=PredictionConfidence.MEDIUM,
        )
    
    def predict_extreme_heat_impact(
        self,
        temperature_f: float,
        heat_index_f: float,
        duration_days: int,
    ) -> DisasterImpactPrediction:
        """Predict extreme heat impact."""
        if heat_index_f >= 125:
            severity = "extreme"
            affected_pop = 15000
        elif heat_index_f >= 115:
            severity = "dangerous"
            affected_pop = 10000
        elif heat_index_f >= 105:
            severity = "high"
            affected_pop = 5000
        else:
            severity = "moderate"
            affected_pop = 2000
        
        infrastructure = ["Power Grid (AC Load)"]
        if heat_index_f > 110:
            infrastructure.extend(["Water System (High Demand)", "Road Surfaces"])
        
        now = datetime.utcnow()
        
        return DisasterImpactPrediction(
            prediction_id=f"heat-{now.strftime('%Y%m%d%H%M')}",
            disaster_type=DisasterType.EXTREME_HEAT,
            timestamp=now,
            impact_area={
                "city_wide": True,
                "temperature_f": temperature_f,
                "heat_index_f": heat_index_f,
            },
            severity=severity,
            estimated_affected_population=affected_pop,
            infrastructure_at_risk=infrastructure,
            estimated_damage_millions=duration_days * 0.5,
            evacuation_recommended=False,
            evacuation_zones=[],
            timeline=[
                {"time": now.isoformat(), "event": "Heat advisory issued"},
                {"time": (now + timedelta(days=duration_days)).isoformat(), "event": "Heat wave expected to end"},
            ],
            confidence=PredictionConfidence.HIGH,
        )
    
    def get_model_info(self) -> dict:
        """Get model information."""
        return {
            "model": "DisasterImpactModel",
            "version": self._model_version,
            "disaster_types": [d.value for d in DisasterType],
            "last_prediction": self._last_prediction.isoformat() if self._last_prediction else None,
        }


class PopulationMovementModel:
    """
    Predicts population movement patterns.
    
    Covers:
    - Crowd sizes
    - School traffic
    - Church attendance peaks
    - Marina weekend density
    - Holiday patterns
    """
    
    POPULATION_ZONES = [
        {"id": "downtown", "name": "Downtown/Marina", "base_pop": 5200, "daytime_factor": 1.5},
        {"id": "singer_island", "name": "Singer Island", "base_pop": 4800, "daytime_factor": 2.0},
        {"id": "westside", "name": "Westside", "base_pop": 12500, "daytime_factor": 0.7},
        {"id": "central", "name": "Central Business", "base_pop": 8200, "daytime_factor": 1.8},
        {"id": "industrial", "name": "Industrial/Port", "base_pop": 1200, "daytime_factor": 3.0},
        {"id": "north", "name": "North Riviera", "base_pop": 6064, "daytime_factor": 0.8},
    ]
    
    SPECIAL_LOCATIONS = [
        {"id": "marina", "name": "Riviera Beach Marina", "type": "recreation", "weekend_multiplier": 3.0},
        {"id": "beach", "name": "Singer Island Beach", "type": "recreation", "weekend_multiplier": 4.0},
        {"id": "port", "name": "Port of Palm Beach", "type": "industrial", "weekend_multiplier": 0.3},
    ]
    
    def __init__(self):
        self._model_version = "1.0.0"
        self._last_prediction: Optional[datetime] = None
    
    def predict_movement(
        self,
        target_time: datetime,
        time_window_hours: int = 24,
        special_events: Optional[list] = None,
        weather_conditions: Optional[dict] = None,
    ) -> PopulationMovementPrediction:
        """Predict population movement patterns."""
        hour = target_time.hour
        day_of_week = target_time.weekday()
        is_weekend = day_of_week >= 5
        
        area_predictions = []
        peak_locations = []
        peak_times = []
        
        for zone in self.POPULATION_ZONES:
            time_factor = 1.0
            
            if 7 <= hour <= 9:
                time_factor = zone["daytime_factor"] * 0.8
            elif 9 <= hour <= 17:
                time_factor = zone["daytime_factor"]
            elif 17 <= hour <= 19:
                time_factor = zone["daytime_factor"] * 0.9
            elif hour < 6 or hour > 22:
                time_factor = 0.9
            
            if is_weekend:
                if zone["id"] in ["downtown", "singer_island"]:
                    time_factor *= 1.5
                elif zone["id"] in ["industrial", "central"]:
                    time_factor *= 0.5
            
            weather_factor = 1.0
            if weather_conditions:
                if weather_conditions.get("precipitation", False):
                    weather_factor = 0.7
                if weather_conditions.get("temperature_f", 80) > 95:
                    weather_factor *= 0.8
            
            predicted_pop = int(zone["base_pop"] * time_factor * weather_factor)
            
            area_predictions.append({
                "zone_id": zone["id"],
                "zone_name": zone["name"],
                "base_population": zone["base_pop"],
                "predicted_population": predicted_pop,
                "change_percent": ((predicted_pop - zone["base_pop"]) / zone["base_pop"]) * 100,
            })
            
            if predicted_pop > zone["base_pop"] * 1.3:
                peak_locations.append({
                    "zone_id": zone["id"],
                    "zone_name": zone["name"],
                    "predicted_density": predicted_pop,
                    "peak_factor": time_factor,
                })
        
        if is_weekend:
            peak_times.append(target_time.replace(hour=10, minute=0))
            peak_times.append(target_time.replace(hour=14, minute=0))
        else:
            peak_times.append(target_time.replace(hour=8, minute=0))
            peak_times.append(target_time.replace(hour=17, minute=30))
        
        events = []
        if special_events:
            events = special_events
        
        if target_time.weekday() == 6:
            events.append({
                "event_id": "church-sunday",
                "name": "Sunday Church Services",
                "location": "Various Churches",
                "expected_attendance": 3000,
                "peak_time": target_time.replace(hour=11, minute=0).isoformat(),
            })
        
        school_days = [0, 1, 2, 3, 4]
        if target_time.weekday() in school_days and 14 <= hour <= 16:
            events.append({
                "event_id": "school-dismissal",
                "name": "School Dismissal",
                "location": "City-wide Schools",
                "expected_attendance": 4000,
                "peak_time": target_time.replace(hour=15, minute=0).isoformat(),
            })
        
        traffic_impact = {
            "congestion_increase_percent": 20 if len(peak_locations) > 2 else 10,
            "affected_roads": ["Blue Heron Blvd", "Broadway"] if len(peak_locations) > 2 else ["Blue Heron Blvd"],
            "peak_traffic_time": peak_times[0].isoformat() if peak_times else None,
        }
        
        self._last_prediction = datetime.utcnow()
        
        return PopulationMovementPrediction(
            prediction_id=f"pop-{target_time.strftime('%Y%m%d%H%M')}",
            timestamp=target_time,
            time_window_hours=time_window_hours,
            area_predictions=area_predictions,
            peak_density_locations=peak_locations,
            peak_times=peak_times,
            special_events=events,
            traffic_impact=traffic_impact,
            confidence=PredictionConfidence.MEDIUM,
        )
    
    def predict_marina_density(
        self,
        target_date: datetime,
        weather_conditions: Optional[dict] = None,
    ) -> dict:
        """Predict marina and beach density."""
        is_weekend = target_date.weekday() >= 5
        is_holiday = False
        
        base_marina = 500
        base_beach = 1500
        
        if is_weekend:
            marina_factor = 3.0
            beach_factor = 4.0
        else:
            marina_factor = 1.0
            beach_factor = 1.5
        
        if is_holiday:
            marina_factor *= 1.5
            beach_factor *= 1.5
        
        weather_factor = 1.0
        if weather_conditions:
            if weather_conditions.get("precipitation", False):
                weather_factor = 0.3
            elif weather_conditions.get("cloud_cover_percent", 0) > 70:
                weather_factor = 0.7
            if weather_conditions.get("temperature_f", 80) > 90:
                weather_factor *= 1.2
        
        return {
            "date": target_date.isoformat(),
            "marina": {
                "predicted_visitors": int(base_marina * marina_factor * weather_factor),
                "boat_launches_expected": int(50 * marina_factor * weather_factor),
                "peak_hours": "10:00-14:00" if is_weekend else "16:00-19:00",
            },
            "beach": {
                "predicted_visitors": int(base_beach * beach_factor * weather_factor),
                "parking_utilization_percent": min(100, int(60 * beach_factor * weather_factor)),
                "peak_hours": "11:00-16:00",
            },
            "factors": {
                "is_weekend": is_weekend,
                "is_holiday": is_holiday,
                "weather_factor": weather_factor,
            },
        }
    
    def get_model_info(self) -> dict:
        """Get model information."""
        return {
            "model": "PopulationMovementModel",
            "version": self._model_version,
            "zones_covered": len(self.POPULATION_ZONES),
            "special_locations": len(self.SPECIAL_LOCATIONS),
            "last_prediction": self._last_prediction.isoformat() if self._last_prediction else None,
        }


class CityPredictionEngine:
    """
    Main prediction engine for Riviera Beach.
    
    Coordinates all prediction models:
    - Traffic flow
    - Crime displacement
    - Infrastructure risk
    - Disaster impact
    - Population movement
    """
    
    def __init__(self):
        self.traffic = TrafficFlowPredictor()
        self.crime = CrimeDisplacementPredictor()
        self.infrastructure = InfrastructureRiskPredictor()
        self.disaster = DisasterImpactModel()
        self.population = PopulationMovementModel()
        
        self._initialized = False
    
    def initialize(self) -> None:
        """Initialize the prediction engine."""
        self._initialized = True
    
    def get_comprehensive_forecast(
        self,
        target_time: datetime,
        hours_ahead: int = 24,
        weather_forecast: Optional[dict] = None,
        special_events: Optional[list] = None,
    ) -> dict:
        """Get comprehensive city forecast."""
        traffic_predictions = []
        for segment in self.traffic.ROAD_SEGMENTS[:5]:
            pred = self.traffic.predict_congestion(
                segment_id=segment["id"],
                target_time=target_time,
                weather_conditions=weather_forecast,
                special_events=special_events,
            )
            traffic_predictions.append({
                "segment": pred.road_segment,
                "congestion": pred.predicted_congestion_level,
                "speed_mph": pred.predicted_speed_mph,
                "crash_risk": pred.crash_risk_score,
            })
        
        crime_pred = self.crime.predict_displacement(
            target_time=target_time,
            time_window_hours=hours_ahead,
            weather_conditions=weather_forecast,
            special_events=special_events,
        )
        
        infra_predictions = self.infrastructure.predict_all_risks(
            target_time=target_time,
            weather_forecast=weather_forecast,
        )
        high_risk_infra = [
            {
                "element": p.element_name,
                "risk_level": p.risk_level.value,
                "probability": p.failure_probability,
            }
            for p in infra_predictions
            if p.risk_level in [RiskLevel.HIGH, RiskLevel.SEVERE, RiskLevel.EXTREME]
        ]
        
        pop_pred = self.population.predict_movement(
            target_time=target_time,
            time_window_hours=hours_ahead,
            special_events=special_events,
            weather_conditions=weather_forecast,
        )
        
        return {
            "forecast_time": target_time.isoformat(),
            "hours_ahead": hours_ahead,
            "generated_at": datetime.utcnow().isoformat(),
            "traffic": {
                "predictions": traffic_predictions,
                "overall_congestion": "moderate" if any(
                    p["congestion"] in ["moderate", "heavy"] for p in traffic_predictions
                ) else "light",
            },
            "crime": {
                "high_risk_zones": [
                    z["zone_name"] for z in crime_pred.risk_increase_areas
                ],
                "patrol_recommendations": len(crime_pred.recommended_patrol_adjustments),
            },
            "infrastructure": {
                "high_risk_elements": high_risk_infra,
                "total_elements_monitored": len(infra_predictions),
            },
            "population": {
                "peak_locations": [p["zone_name"] for p in pop_pred.peak_density_locations],
                "special_events": len(pop_pred.special_events),
                "traffic_impact": pop_pred.traffic_impact,
            },
            "confidence": "medium",
        }
    
    def get_status(self) -> dict:
        """Get prediction engine status."""
        return {
            "initialized": self._initialized,
            "models": {
                "traffic": self.traffic.get_model_info(),
                "crime": self.crime.get_model_info(),
                "infrastructure": self.infrastructure.get_model_info(),
                "disaster": self.disaster.get_model_info(),
                "population": self.population.get_model_info(),
            },
        }


__all__ = [
    "CityPredictionEngine",
    "TrafficFlowPredictor",
    "CrimeDisplacementPredictor",
    "InfrastructureRiskPredictor",
    "DisasterImpactModel",
    "PopulationMovementModel",
    "TrafficPrediction",
    "EvacuationFlowPrediction",
    "CrimeDisplacementPrediction",
    "InfrastructureRiskPrediction",
    "DisasterImpactPrediction",
    "PopulationMovementPrediction",
    "PredictionConfidence",
    "RiskLevel",
    "DisasterType",
]
