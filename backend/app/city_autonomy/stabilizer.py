"""
Phase 24: AutomatedCityStabilizer - City System Monitoring and Stabilization

This module monitors city systems and generates stabilization actions:
- Grid load monitoring
- Traffic congestion detection
- Crime anomaly detection
- EMS/Fire demand spike detection
- Weather and flooding model integration
- Crowd movement analysis
- Cascade failure prediction
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Callable, Tuple
import uuid
import math
import random


class MonitoringDomain(Enum):
    """Domains being monitored by the stabilizer."""
    GRID_LOAD = "grid_load"
    TRAFFIC = "traffic"
    CRIME = "crime"
    EMS_DEMAND = "ems_demand"
    FIRE_DEMAND = "fire_demand"
    WEATHER = "weather"
    FLOODING = "flooding"
    CROWD = "crowd"
    INFRASTRUCTURE = "infrastructure"
    UTILITIES = "utilities"


class AnomalyType(Enum):
    """Types of anomalies detected."""
    SPIKE = "spike"
    DROP = "drop"
    PATTERN_DEVIATION = "pattern_deviation"
    THRESHOLD_BREACH = "threshold_breach"
    TREND_CHANGE = "trend_change"
    CASCADE_RISK = "cascade_risk"
    CORRELATION_ANOMALY = "correlation_anomaly"


class AnomalySeverity(Enum):
    """Severity levels for anomalies."""
    INFO = "info"
    WARNING = "warning"
    ELEVATED = "elevated"
    HIGH = "high"
    CRITICAL = "critical"


class StabilizationActionType(Enum):
    """Types of stabilization actions."""
    REROUTE_TRAFFIC = "reroute_traffic"
    INCREASE_PATROL_HEAT = "increase_patrol_heat"
    DISPATCH_CITY_CREWS = "dispatch_city_crews"
    LOAD_SHEDDING = "load_shedding"
    ACTIVATE_BACKUP_SYSTEMS = "activate_backup_systems"
    DEPLOY_EMERGENCY_UNITS = "deploy_emergency_units"
    ISSUE_PUBLIC_ALERT = "issue_public_alert"
    ACTIVATE_EVACUATION = "activate_evacuation"
    CROWD_DISPERSAL = "crowd_dispersal"
    INFRASTRUCTURE_PROTECTION = "infrastructure_protection"


class StabilizerStatus(Enum):
    """Status of the stabilizer."""
    ACTIVE = "active"
    MONITORING = "monitoring"
    STABILIZING = "stabilizing"
    MANUAL_MODE = "manual_mode"
    CIRCUIT_BREAKER_OPEN = "circuit_breaker_open"


@dataclass
class SensorReading:
    """Individual sensor reading."""
    sensor_id: str
    domain: MonitoringDomain
    metric: str
    value: float
    unit: str
    location: Optional[Dict[str, float]] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    quality: float = 1.0  # Data quality score 0-1

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sensor_id": self.sensor_id,
            "domain": self.domain.value,
            "metric": self.metric,
            "value": self.value,
            "unit": self.unit,
            "location": self.location,
            "timestamp": self.timestamp.isoformat(),
            "quality": self.quality,
        }


@dataclass
class Anomaly:
    """Detected anomaly in city systems."""
    anomaly_id: str
    domain: MonitoringDomain
    anomaly_type: AnomalyType
    severity: AnomalySeverity
    title: str
    description: str
    affected_area: Optional[str] = None
    affected_systems: List[str] = field(default_factory=list)
    metrics: Dict[str, float] = field(default_factory=dict)
    baseline_value: Optional[float] = None
    current_value: Optional[float] = None
    deviation_percentage: Optional[float] = None
    confidence: float = 0.8
    detected_at: datetime = field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None
    cascade_risk: float = 0.0
    related_anomalies: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "anomaly_id": self.anomaly_id,
            "domain": self.domain.value,
            "anomaly_type": self.anomaly_type.value,
            "severity": self.severity.value,
            "title": self.title,
            "description": self.description,
            "affected_area": self.affected_area,
            "affected_systems": self.affected_systems,
            "metrics": self.metrics,
            "baseline_value": self.baseline_value,
            "current_value": self.current_value,
            "deviation_percentage": self.deviation_percentage,
            "confidence": self.confidence,
            "detected_at": self.detected_at.isoformat(),
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "cascade_risk": self.cascade_risk,
            "related_anomalies": self.related_anomalies,
        }


@dataclass
class CascadeFailurePrediction:
    """Prediction of potential cascade failures."""
    prediction_id: str
    trigger_anomaly_id: str
    affected_domains: List[MonitoringDomain]
    failure_sequence: List[Dict[str, Any]]
    probability: float
    time_to_cascade_minutes: int
    impact_score: float
    mitigation_actions: List[str]
    predicted_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "prediction_id": self.prediction_id,
            "trigger_anomaly_id": self.trigger_anomaly_id,
            "affected_domains": [d.value for d in self.affected_domains],
            "failure_sequence": self.failure_sequence,
            "probability": self.probability,
            "time_to_cascade_minutes": self.time_to_cascade_minutes,
            "impact_score": self.impact_score,
            "mitigation_actions": self.mitigation_actions,
            "predicted_at": self.predicted_at.isoformat(),
        }


@dataclass
class StabilizationAction:
    """Action to stabilize city systems."""
    action_id: str
    action_type: StabilizationActionType
    title: str
    description: str
    target_domain: MonitoringDomain
    target_area: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    priority: int = 5
    estimated_impact: float = 0.5
    estimated_duration_minutes: int = 30
    requires_approval: bool = False
    triggered_by_anomaly_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    executed_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    success: Optional[bool] = None
    result_metrics: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action_id": self.action_id,
            "action_type": self.action_type.value,
            "title": self.title,
            "description": self.description,
            "target_domain": self.target_domain.value,
            "target_area": self.target_area,
            "parameters": self.parameters,
            "priority": self.priority,
            "estimated_impact": self.estimated_impact,
            "estimated_duration_minutes": self.estimated_duration_minutes,
            "requires_approval": self.requires_approval,
            "triggered_by_anomaly_id": self.triggered_by_anomaly_id,
            "created_at": self.created_at.isoformat(),
            "executed_at": self.executed_at.isoformat() if self.executed_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "success": self.success,
            "result_metrics": self.result_metrics,
        }


@dataclass
class DomainBaseline:
    """Baseline metrics for a monitoring domain."""
    domain: MonitoringDomain
    metrics: Dict[str, float]
    thresholds: Dict[str, Dict[str, float]]  # metric -> {warning, elevated, high, critical}
    last_updated: datetime = field(default_factory=datetime.utcnow)
    sample_count: int = 0


class AutomatedCityStabilizer:
    """
    Automated system for monitoring city operations and generating
    stabilization actions when anomalies are detected.
    
    Monitors: grid load, traffic congestion, crime anomalies, EMS/Fire demand,
    weather, flooding, and crowd movement for Riviera Beach.
    """

    def __init__(self):
        self._status = StabilizerStatus.MONITORING
        self._anomalies: Dict[str, Anomaly] = {}
        self._active_anomalies: Dict[str, Anomaly] = {}
        self._cascade_predictions: Dict[str, CascadeFailurePrediction] = {}
        self._stabilization_actions: Dict[str, StabilizationAction] = {}
        self._sensor_readings: Dict[str, List[SensorReading]] = {}
        self._baselines: Dict[MonitoringDomain, DomainBaseline] = {}
        self._action_callback: Optional[Callable] = None
        self._circuit_breaker_open = False
        self._consecutive_failures = 0
        self._max_failures = 5
        self._initialize_baselines()
        self._initialize_riviera_beach_config()

    def _initialize_baselines(self):
        """Initialize baseline metrics for all domains."""
        self._baselines = {
            MonitoringDomain.GRID_LOAD: DomainBaseline(
                domain=MonitoringDomain.GRID_LOAD,
                metrics={
                    "load_percentage": 65.0,
                    "peak_demand_mw": 45.0,
                    "reserve_margin": 0.25,
                },
                thresholds={
                    "load_percentage": {"warning": 75, "elevated": 85, "high": 90, "critical": 95},
                    "reserve_margin": {"warning": 0.20, "elevated": 0.15, "high": 0.10, "critical": 0.05},
                },
            ),
            MonitoringDomain.TRAFFIC: DomainBaseline(
                domain=MonitoringDomain.TRAFFIC,
                metrics={
                    "congestion_index": 0.35,
                    "avg_speed_mph": 28.0,
                    "incident_count": 2.0,
                },
                thresholds={
                    "congestion_index": {"warning": 0.5, "elevated": 0.65, "high": 0.8, "critical": 0.9},
                    "avg_speed_mph": {"warning": 20, "elevated": 15, "high": 10, "critical": 5},
                },
            ),
            MonitoringDomain.CRIME: DomainBaseline(
                domain=MonitoringDomain.CRIME,
                metrics={
                    "incident_rate": 2.5,
                    "violent_crime_count": 0.5,
                    "property_crime_count": 3.0,
                },
                thresholds={
                    "incident_rate": {"warning": 4, "elevated": 6, "high": 8, "critical": 12},
                    "violent_crime_count": {"warning": 2, "elevated": 3, "high": 5, "critical": 8},
                },
            ),
            MonitoringDomain.EMS_DEMAND: DomainBaseline(
                domain=MonitoringDomain.EMS_DEMAND,
                metrics={
                    "calls_per_hour": 3.0,
                    "avg_response_time_min": 6.5,
                    "units_available": 4.0,
                },
                thresholds={
                    "calls_per_hour": {"warning": 5, "elevated": 8, "high": 12, "critical": 15},
                    "avg_response_time_min": {"warning": 8, "elevated": 10, "high": 12, "critical": 15},
                    "units_available": {"warning": 3, "elevated": 2, "high": 1, "critical": 0},
                },
            ),
            MonitoringDomain.FIRE_DEMAND: DomainBaseline(
                domain=MonitoringDomain.FIRE_DEMAND,
                metrics={
                    "calls_per_hour": 1.5,
                    "avg_response_time_min": 5.0,
                    "units_available": 3.0,
                },
                thresholds={
                    "calls_per_hour": {"warning": 3, "elevated": 5, "high": 8, "critical": 10},
                    "avg_response_time_min": {"warning": 7, "elevated": 9, "high": 11, "critical": 14},
                },
            ),
            MonitoringDomain.WEATHER: DomainBaseline(
                domain=MonitoringDomain.WEATHER,
                metrics={
                    "wind_speed_mph": 10.0,
                    "rainfall_rate_in_hr": 0.0,
                    "heat_index": 85.0,
                },
                thresholds={
                    "wind_speed_mph": {"warning": 25, "elevated": 40, "high": 58, "critical": 74},
                    "rainfall_rate_in_hr": {"warning": 0.5, "elevated": 1.0, "high": 2.0, "critical": 4.0},
                    "heat_index": {"warning": 95, "elevated": 103, "high": 110, "critical": 115},
                },
            ),
            MonitoringDomain.FLOODING: DomainBaseline(
                domain=MonitoringDomain.FLOODING,
                metrics={
                    "water_level_ft": 0.0,
                    "pump_capacity_pct": 100.0,
                    "drainage_flow_rate": 1.0,
                },
                thresholds={
                    "water_level_ft": {"warning": 2, "elevated": 4, "high": 6, "critical": 8},
                    "pump_capacity_pct": {"warning": 80, "elevated": 60, "high": 40, "critical": 20},
                },
            ),
            MonitoringDomain.CROWD: DomainBaseline(
                domain=MonitoringDomain.CROWD,
                metrics={
                    "density_per_sqft": 0.02,
                    "movement_velocity": 2.5,
                    "gathering_count": 1.0,
                },
                thresholds={
                    "density_per_sqft": {"warning": 0.05, "elevated": 0.08, "high": 0.12, "critical": 0.15},
                    "gathering_count": {"warning": 3, "elevated": 5, "high": 8, "critical": 10},
                },
            ),
        }

    def _initialize_riviera_beach_config(self):
        """Initialize Riviera Beach specific configuration."""
        self._city_config = {
            "name": "Riviera Beach",
            "state": "Florida",
            "zip": "33404",
            "coordinates": {"lat": 26.7753, "lon": -80.0583},
            "population": 37964,
            "area_sq_miles": 9.76,
            "districts": [
                "Downtown", "Marina District", "Industrial Area",
                "Residential North", "Residential South", "Commercial Corridor"
            ],
            "flood_zones": ["Zone A", "Zone AE", "Zone X"],
            "hurricane_zone": "Zone B",
            "critical_infrastructure": [
                "City Hall", "Police Station", "Fire Station 1", "Fire Station 2",
                "Water Treatment Plant", "Power Substation", "Port of Palm Beach"
            ],
        }

    def ingest_sensor_reading(self, reading: SensorReading):
        """Ingest a sensor reading and check for anomalies."""
        domain_key = reading.domain.value
        if domain_key not in self._sensor_readings:
            self._sensor_readings[domain_key] = []

        self._sensor_readings[domain_key].append(reading)

        # Keep only last 1000 readings per domain
        if len(self._sensor_readings[domain_key]) > 1000:
            self._sensor_readings[domain_key] = self._sensor_readings[domain_key][-1000:]

        # Check for anomalies
        anomaly = self._detect_anomaly(reading)
        if anomaly:
            self._anomalies[anomaly.anomaly_id] = anomaly
            self._active_anomalies[anomaly.anomaly_id] = anomaly

            # Check for cascade risks
            cascade = self._predict_cascade_failure(anomaly)
            if cascade:
                self._cascade_predictions[cascade.prediction_id] = cascade

            # Generate stabilization actions
            actions = self._generate_stabilization_actions(anomaly)
            for action in actions:
                self._stabilization_actions[action.action_id] = action
                if self._action_callback:
                    self._action_callback(action)

    def _detect_anomaly(self, reading: SensorReading) -> Optional[Anomaly]:
        """Detect anomalies in sensor readings."""
        baseline = self._baselines.get(reading.domain)
        if not baseline:
            return None

        thresholds = baseline.thresholds.get(reading.metric)
        if not thresholds:
            return None

        baseline_value = baseline.metrics.get(reading.metric, 0)
        current_value = reading.value

        # Determine severity based on thresholds
        severity = None
        anomaly_type = AnomalyType.THRESHOLD_BREACH

        # For metrics where higher is worse
        if reading.metric in ["load_percentage", "congestion_index", "incident_rate",
                              "calls_per_hour", "wind_speed_mph", "rainfall_rate_in_hr",
                              "heat_index", "water_level_ft", "density_per_sqft",
                              "violent_crime_count", "property_crime_count", "gathering_count",
                              "avg_response_time_min"]:
            if current_value >= thresholds.get("critical", float("inf")):
                severity = AnomalySeverity.CRITICAL
            elif current_value >= thresholds.get("high", float("inf")):
                severity = AnomalySeverity.HIGH
            elif current_value >= thresholds.get("elevated", float("inf")):
                severity = AnomalySeverity.ELEVATED
            elif current_value >= thresholds.get("warning", float("inf")):
                severity = AnomalySeverity.WARNING

        # For metrics where lower is worse
        elif reading.metric in ["avg_speed_mph", "units_available", "reserve_margin",
                                "pump_capacity_pct", "drainage_flow_rate"]:
            if current_value <= thresholds.get("critical", float("-inf")):
                severity = AnomalySeverity.CRITICAL
            elif current_value <= thresholds.get("high", float("-inf")):
                severity = AnomalySeverity.HIGH
            elif current_value <= thresholds.get("elevated", float("-inf")):
                severity = AnomalySeverity.ELEVATED
            elif current_value <= thresholds.get("warning", float("-inf")):
                severity = AnomalySeverity.WARNING

        if not severity:
            # Check for significant deviation from baseline
            if baseline_value > 0:
                deviation = abs(current_value - baseline_value) / baseline_value
                if deviation > 0.5:
                    severity = AnomalySeverity.WARNING
                    anomaly_type = AnomalyType.PATTERN_DEVIATION

        if not severity:
            return None

        deviation_pct = ((current_value - baseline_value) / baseline_value * 100) if baseline_value else 0

        return Anomaly(
            anomaly_id=f"anomaly-{uuid.uuid4().hex[:12]}",
            domain=reading.domain,
            anomaly_type=anomaly_type,
            severity=severity,
            title=f"{reading.domain.value.replace('_', ' ').title()} Anomaly Detected",
            description=f"{reading.metric} at {current_value:.2f} {reading.unit} "
                       f"(baseline: {baseline_value:.2f}, deviation: {deviation_pct:.1f}%)",
            affected_area=reading.location.get("area") if reading.location else None,
            affected_systems=[reading.sensor_id],
            metrics={reading.metric: current_value},
            baseline_value=baseline_value,
            current_value=current_value,
            deviation_percentage=deviation_pct,
            confidence=reading.quality,
            cascade_risk=self._calculate_cascade_risk(reading.domain, severity),
        )

    def _calculate_cascade_risk(
        self,
        domain: MonitoringDomain,
        severity: AnomalySeverity,
    ) -> float:
        """Calculate the risk of cascade failure."""
        base_risk = {
            AnomalySeverity.INFO: 0.05,
            AnomalySeverity.WARNING: 0.15,
            AnomalySeverity.ELEVATED: 0.35,
            AnomalySeverity.HIGH: 0.60,
            AnomalySeverity.CRITICAL: 0.85,
        }.get(severity, 0.1)

        # Domain-specific cascade multipliers
        domain_multiplier = {
            MonitoringDomain.GRID_LOAD: 1.5,  # Power affects everything
            MonitoringDomain.FLOODING: 1.4,   # Flooding affects infrastructure
            MonitoringDomain.WEATHER: 1.3,    # Weather affects multiple systems
            MonitoringDomain.TRAFFIC: 1.1,
            MonitoringDomain.CRIME: 1.0,
            MonitoringDomain.EMS_DEMAND: 1.2,
            MonitoringDomain.FIRE_DEMAND: 1.2,
            MonitoringDomain.CROWD: 1.1,
        }.get(domain, 1.0)

        # Check for existing active anomalies that compound risk
        active_count = len(self._active_anomalies)
        compound_factor = 1.0 + (active_count * 0.1)

        return min(base_risk * domain_multiplier * compound_factor, 1.0)

    def _predict_cascade_failure(self, anomaly: Anomaly) -> Optional[CascadeFailurePrediction]:
        """Predict potential cascade failures from an anomaly."""
        if anomaly.cascade_risk < 0.3:
            return None

        # Define cascade relationships
        cascade_map = {
            MonitoringDomain.GRID_LOAD: [
                MonitoringDomain.TRAFFIC,  # Traffic signals
                MonitoringDomain.UTILITIES,  # Water pumps
                MonitoringDomain.EMS_DEMAND,  # Medical equipment
            ],
            MonitoringDomain.FLOODING: [
                MonitoringDomain.TRAFFIC,
                MonitoringDomain.GRID_LOAD,
                MonitoringDomain.INFRASTRUCTURE,
            ],
            MonitoringDomain.WEATHER: [
                MonitoringDomain.FLOODING,
                MonitoringDomain.TRAFFIC,
                MonitoringDomain.GRID_LOAD,
            ],
            MonitoringDomain.TRAFFIC: [
                MonitoringDomain.EMS_DEMAND,  # Response times
                MonitoringDomain.FIRE_DEMAND,
            ],
            MonitoringDomain.CRIME: [
                MonitoringDomain.CROWD,
                MonitoringDomain.TRAFFIC,
            ],
        }

        affected_domains = cascade_map.get(anomaly.domain, [])
        if not affected_domains:
            return None

        # Build failure sequence
        failure_sequence = []
        time_offset = 0
        for domain in affected_domains:
            time_offset += random.randint(5, 20)
            failure_sequence.append({
                "domain": domain.value,
                "estimated_time_minutes": time_offset,
                "impact": "moderate" if anomaly.severity in [AnomalySeverity.WARNING, AnomalySeverity.ELEVATED] else "severe",
            })

        # Generate mitigation actions
        mitigation_actions = self._get_mitigation_actions(anomaly.domain, affected_domains)

        return CascadeFailurePrediction(
            prediction_id=f"cascade-{uuid.uuid4().hex[:8]}",
            trigger_anomaly_id=anomaly.anomaly_id,
            affected_domains=affected_domains,
            failure_sequence=failure_sequence,
            probability=anomaly.cascade_risk,
            time_to_cascade_minutes=failure_sequence[0]["estimated_time_minutes"] if failure_sequence else 30,
            impact_score=anomaly.cascade_risk * len(affected_domains) * 0.3,
            mitigation_actions=mitigation_actions,
        )

    def _get_mitigation_actions(
        self,
        trigger_domain: MonitoringDomain,
        affected_domains: List[MonitoringDomain],
    ) -> List[str]:
        """Get recommended mitigation actions for cascade prevention."""
        actions = []

        if trigger_domain == MonitoringDomain.GRID_LOAD:
            actions.extend([
                "Activate load shedding for non-critical areas",
                "Deploy backup generators to critical facilities",
                "Alert FPL for emergency support",
            ])
        elif trigger_domain == MonitoringDomain.FLOODING:
            actions.extend([
                "Activate all pump stations at maximum capacity",
                "Close flooded roadways",
                "Deploy sandbag crews to vulnerable areas",
            ])
        elif trigger_domain == MonitoringDomain.WEATHER:
            actions.extend([
                "Issue public weather alert",
                "Pre-position emergency response units",
                "Activate emergency operations center",
            ])
        elif trigger_domain == MonitoringDomain.TRAFFIC:
            actions.extend([
                "Activate alternate traffic routes",
                "Deploy traffic control officers",
                "Adjust signal timing for emergency corridors",
            ])
        elif trigger_domain == MonitoringDomain.CRIME:
            actions.extend([
                "Increase patrol presence in affected area",
                "Alert neighboring jurisdictions",
                "Activate crime suppression unit",
            ])

        return actions

    def _generate_stabilization_actions(self, anomaly: Anomaly) -> List[StabilizationAction]:
        """Generate stabilization actions for an anomaly."""
        actions = []

        action_generators = {
            MonitoringDomain.GRID_LOAD: self._generate_grid_actions,
            MonitoringDomain.TRAFFIC: self._generate_traffic_actions,
            MonitoringDomain.CRIME: self._generate_crime_actions,
            MonitoringDomain.EMS_DEMAND: self._generate_ems_actions,
            MonitoringDomain.FIRE_DEMAND: self._generate_fire_actions,
            MonitoringDomain.WEATHER: self._generate_weather_actions,
            MonitoringDomain.FLOODING: self._generate_flooding_actions,
            MonitoringDomain.CROWD: self._generate_crowd_actions,
        }

        generator = action_generators.get(anomaly.domain)
        if generator:
            actions = generator(anomaly)

        return actions

    def _generate_grid_actions(self, anomaly: Anomaly) -> List[StabilizationAction]:
        """Generate grid stabilization actions."""
        actions = []
        requires_approval = anomaly.severity in [AnomalySeverity.HIGH, AnomalySeverity.CRITICAL]

        if anomaly.severity >= AnomalySeverity.ELEVATED:
            actions.append(StabilizationAction(
                action_id=f"stab-{uuid.uuid4().hex[:8]}",
                action_type=StabilizationActionType.LOAD_SHEDDING,
                title="Activate Load Shedding",
                description="Reduce non-critical load to stabilize grid",
                target_domain=MonitoringDomain.GRID_LOAD,
                parameters={
                    "reduction_target_pct": 15 if anomaly.severity == AnomalySeverity.ELEVATED else 25,
                    "priority_areas": ["hospitals", "emergency_services", "water_treatment"],
                },
                priority=9 if anomaly.severity >= AnomalySeverity.HIGH else 7,
                estimated_impact=0.7,
                requires_approval=requires_approval,
                triggered_by_anomaly_id=anomaly.anomaly_id,
            ))

        if anomaly.severity >= AnomalySeverity.HIGH:
            actions.append(StabilizationAction(
                action_id=f"stab-{uuid.uuid4().hex[:8]}",
                action_type=StabilizationActionType.ACTIVATE_BACKUP_SYSTEMS,
                title="Activate Backup Generators",
                description="Deploy backup power to critical facilities",
                target_domain=MonitoringDomain.GRID_LOAD,
                parameters={
                    "facilities": ["city_hall", "police_station", "fire_stations", "water_plant"],
                },
                priority=10,
                estimated_impact=0.8,
                requires_approval=True,
                triggered_by_anomaly_id=anomaly.anomaly_id,
            ))

        return actions

    def _generate_traffic_actions(self, anomaly: Anomaly) -> List[StabilizationAction]:
        """Generate traffic stabilization actions."""
        actions = []

        if anomaly.severity >= AnomalySeverity.WARNING:
            actions.append(StabilizationAction(
                action_id=f"stab-{uuid.uuid4().hex[:8]}",
                action_type=StabilizationActionType.REROUTE_TRAFFIC,
                title="Activate Alternate Routes",
                description="Reroute traffic to reduce congestion",
                target_domain=MonitoringDomain.TRAFFIC,
                target_area=anomaly.affected_area,
                parameters={
                    "signal_timing_adjustment": True,
                    "dynamic_message_signs": True,
                    "navigation_app_alerts": True,
                },
                priority=7,
                estimated_impact=0.5,
                requires_approval=False,
                triggered_by_anomaly_id=anomaly.anomaly_id,
            ))

        if anomaly.severity >= AnomalySeverity.HIGH:
            actions.append(StabilizationAction(
                action_id=f"stab-{uuid.uuid4().hex[:8]}",
                action_type=StabilizationActionType.DISPATCH_CITY_CREWS,
                title="Deploy Traffic Control Officers",
                description="Deploy officers to manage critical intersections",
                target_domain=MonitoringDomain.TRAFFIC,
                target_area=anomaly.affected_area,
                parameters={
                    "intersections": ["blue_heron_us1", "broadway_us1", "mlk_congress"],
                    "officer_count": 4,
                },
                priority=8,
                estimated_impact=0.6,
                requires_approval=True,
                triggered_by_anomaly_id=anomaly.anomaly_id,
            ))

        return actions

    def _generate_crime_actions(self, anomaly: Anomaly) -> List[StabilizationAction]:
        """Generate crime response stabilization actions."""
        actions = []

        if anomaly.severity >= AnomalySeverity.WARNING:
            actions.append(StabilizationAction(
                action_id=f"stab-{uuid.uuid4().hex[:8]}",
                action_type=StabilizationActionType.INCREASE_PATROL_HEAT,
                title="Increase Patrol Presence",
                description="Deploy additional patrol units to affected area",
                target_domain=MonitoringDomain.CRIME,
                target_area=anomaly.affected_area,
                parameters={
                    "additional_units": 2 if anomaly.severity == AnomalySeverity.WARNING else 4,
                    "duration_hours": 4,
                    "patrol_type": "high_visibility",
                },
                priority=8,
                estimated_impact=0.6,
                requires_approval=anomaly.severity >= AnomalySeverity.HIGH,
                triggered_by_anomaly_id=anomaly.anomaly_id,
            ))

        if anomaly.severity >= AnomalySeverity.HIGH:
            actions.append(StabilizationAction(
                action_id=f"stab-{uuid.uuid4().hex[:8]}",
                action_type=StabilizationActionType.DEPLOY_EMERGENCY_UNITS,
                title="Activate Crime Suppression Unit",
                description="Deploy specialized crime suppression resources",
                target_domain=MonitoringDomain.CRIME,
                target_area=anomaly.affected_area,
                parameters={
                    "unit_type": "crime_suppression",
                    "coordination": ["detective_bureau", "k9_unit"],
                },
                priority=9,
                estimated_impact=0.7,
                requires_approval=True,
                triggered_by_anomaly_id=anomaly.anomaly_id,
            ))

        return actions

    def _generate_ems_actions(self, anomaly: Anomaly) -> List[StabilizationAction]:
        """Generate EMS stabilization actions."""
        actions = []

        if anomaly.severity >= AnomalySeverity.WARNING:
            actions.append(StabilizationAction(
                action_id=f"stab-{uuid.uuid4().hex[:8]}",
                action_type=StabilizationActionType.DEPLOY_EMERGENCY_UNITS,
                title="Reposition EMS Units",
                description="Optimize EMS unit positioning for faster response",
                target_domain=MonitoringDomain.EMS_DEMAND,
                parameters={
                    "reposition_strategy": "demand_based",
                    "coverage_optimization": True,
                },
                priority=8,
                estimated_impact=0.5,
                requires_approval=False,
                triggered_by_anomaly_id=anomaly.anomaly_id,
            ))

        if anomaly.severity >= AnomalySeverity.HIGH:
            actions.append(StabilizationAction(
                action_id=f"stab-{uuid.uuid4().hex[:8]}",
                action_type=StabilizationActionType.DEPLOY_EMERGENCY_UNITS,
                title="Request Mutual Aid",
                description="Request EMS mutual aid from neighboring jurisdictions",
                target_domain=MonitoringDomain.EMS_DEMAND,
                parameters={
                    "agencies": ["palm_beach_county_fire_rescue", "west_palm_beach_fire"],
                    "units_requested": 2,
                },
                priority=9,
                estimated_impact=0.7,
                requires_approval=True,
                triggered_by_anomaly_id=anomaly.anomaly_id,
            ))

        return actions

    def _generate_fire_actions(self, anomaly: Anomaly) -> List[StabilizationAction]:
        """Generate fire department stabilization actions."""
        actions = []

        if anomaly.severity >= AnomalySeverity.ELEVATED:
            actions.append(StabilizationAction(
                action_id=f"stab-{uuid.uuid4().hex[:8]}",
                action_type=StabilizationActionType.DEPLOY_EMERGENCY_UNITS,
                title="Recall Off-Duty Personnel",
                description="Recall off-duty firefighters to increase capacity",
                target_domain=MonitoringDomain.FIRE_DEMAND,
                parameters={
                    "recall_level": "partial" if anomaly.severity == AnomalySeverity.ELEVATED else "full",
                },
                priority=8,
                estimated_impact=0.6,
                requires_approval=True,
                triggered_by_anomaly_id=anomaly.anomaly_id,
            ))

        return actions

    def _generate_weather_actions(self, anomaly: Anomaly) -> List[StabilizationAction]:
        """Generate weather-related stabilization actions."""
        actions = []

        if anomaly.severity >= AnomalySeverity.WARNING:
            actions.append(StabilizationAction(
                action_id=f"stab-{uuid.uuid4().hex[:8]}",
                action_type=StabilizationActionType.ISSUE_PUBLIC_ALERT,
                title="Issue Weather Alert",
                description="Send public weather warning to residents",
                target_domain=MonitoringDomain.WEATHER,
                parameters={
                    "channels": ["sms", "email", "social_media", "sirens"],
                    "message_type": "weather_warning",
                    "severity": anomaly.severity.value,
                },
                priority=7,
                estimated_impact=0.4,
                requires_approval=False,
                triggered_by_anomaly_id=anomaly.anomaly_id,
            ))

        if anomaly.severity >= AnomalySeverity.HIGH:
            actions.append(StabilizationAction(
                action_id=f"stab-{uuid.uuid4().hex[:8]}",
                action_type=StabilizationActionType.ACTIVATE_EVACUATION,
                title="Prepare Evacuation Routes",
                description="Pre-position resources for potential evacuation",
                target_domain=MonitoringDomain.WEATHER,
                parameters={
                    "evacuation_zones": ["coastal", "flood_zone_a"],
                    "shelter_activation": True,
                    "contraflow_ready": True,
                },
                priority=9,
                estimated_impact=0.8,
                requires_approval=True,
                triggered_by_anomaly_id=anomaly.anomaly_id,
            ))

        return actions

    def _generate_flooding_actions(self, anomaly: Anomaly) -> List[StabilizationAction]:
        """Generate flooding stabilization actions."""
        actions = []

        if anomaly.severity >= AnomalySeverity.WARNING:
            actions.append(StabilizationAction(
                action_id=f"stab-{uuid.uuid4().hex[:8]}",
                action_type=StabilizationActionType.DISPATCH_CITY_CREWS,
                title="Activate Pump Stations",
                description="Increase pump station capacity",
                target_domain=MonitoringDomain.FLOODING,
                parameters={
                    "pump_stations": ["north", "south", "marina"],
                    "capacity_target": "maximum",
                },
                priority=8,
                estimated_impact=0.6,
                requires_approval=False,
                triggered_by_anomaly_id=anomaly.anomaly_id,
            ))

        if anomaly.severity >= AnomalySeverity.ELEVATED:
            actions.append(StabilizationAction(
                action_id=f"stab-{uuid.uuid4().hex[:8]}",
                action_type=StabilizationActionType.REROUTE_TRAFFIC,
                title="Close Flooded Roadways",
                description="Close flooded roads and activate detours",
                target_domain=MonitoringDomain.FLOODING,
                target_area=anomaly.affected_area,
                parameters={
                    "barricade_deployment": True,
                    "detour_signs": True,
                    "navigation_alerts": True,
                },
                priority=8,
                estimated_impact=0.7,
                requires_approval=False,
                triggered_by_anomaly_id=anomaly.anomaly_id,
            ))

        if anomaly.severity >= AnomalySeverity.HIGH:
            actions.append(StabilizationAction(
                action_id=f"stab-{uuid.uuid4().hex[:8]}",
                action_type=StabilizationActionType.ACTIVATE_EVACUATION,
                title="Evacuate Flood Zone",
                description="Initiate evacuation of affected flood zones",
                target_domain=MonitoringDomain.FLOODING,
                target_area=anomaly.affected_area,
                parameters={
                    "evacuation_type": "mandatory" if anomaly.severity == AnomalySeverity.CRITICAL else "voluntary",
                    "shelter_locations": ["riviera_beach_high", "community_center"],
                    "transportation_assistance": True,
                },
                priority=10,
                estimated_impact=0.9,
                requires_approval=True,
                triggered_by_anomaly_id=anomaly.anomaly_id,
            ))

        return actions

    def _generate_crowd_actions(self, anomaly: Anomaly) -> List[StabilizationAction]:
        """Generate crowd management stabilization actions."""
        actions = []

        if anomaly.severity >= AnomalySeverity.WARNING:
            actions.append(StabilizationAction(
                action_id=f"stab-{uuid.uuid4().hex[:8]}",
                action_type=StabilizationActionType.INCREASE_PATROL_HEAT,
                title="Deploy Crowd Management Units",
                description="Increase police presence for crowd management",
                target_domain=MonitoringDomain.CROWD,
                target_area=anomaly.affected_area,
                parameters={
                    "unit_type": "crowd_management",
                    "officer_count": 4,
                },
                priority=7,
                estimated_impact=0.5,
                requires_approval=False,
                triggered_by_anomaly_id=anomaly.anomaly_id,
            ))

        if anomaly.severity >= AnomalySeverity.HIGH:
            actions.append(StabilizationAction(
                action_id=f"stab-{uuid.uuid4().hex[:8]}",
                action_type=StabilizationActionType.CROWD_DISPERSAL,
                title="Initiate Crowd Dispersal",
                description="Begin controlled crowd dispersal procedures",
                target_domain=MonitoringDomain.CROWD,
                target_area=anomaly.affected_area,
                parameters={
                    "method": "announcement_first",
                    "exit_routes": True,
                    "medical_standby": True,
                },
                priority=9,
                estimated_impact=0.7,
                requires_approval=True,
                triggered_by_anomaly_id=anomaly.anomaly_id,
            ))

        return actions

    def resolve_anomaly(self, anomaly_id: str) -> bool:
        """Mark an anomaly as resolved."""
        anomaly = self._active_anomalies.get(anomaly_id)
        if not anomaly:
            return False

        anomaly.resolved_at = datetime.utcnow()
        del self._active_anomalies[anomaly_id]
        return True

    def execute_stabilization_action(self, action_id: str) -> bool:
        """Execute a stabilization action."""
        action = self._stabilization_actions.get(action_id)
        if not action:
            return False

        if self._circuit_breaker_open:
            return False

        try:
            action.executed_at = datetime.utcnow()
            # Simulate execution
            action.success = True
            action.completed_at = datetime.utcnow()
            action.result_metrics = {
                "execution_time_ms": 150,
                "resources_deployed": 1,
            }
            self._consecutive_failures = 0
            return True
        except Exception:
            self._consecutive_failures += 1
            if self._consecutive_failures >= self._max_failures:
                self._circuit_breaker_open = True
                self._status = StabilizerStatus.CIRCUIT_BREAKER_OPEN
            return False

    def get_active_anomalies(self) -> List[Anomaly]:
        """Get all active anomalies."""
        return list(self._active_anomalies.values())

    def get_cascade_predictions(self) -> List[CascadeFailurePrediction]:
        """Get all cascade failure predictions."""
        return list(self._cascade_predictions.values())

    def get_stabilization_actions(
        self,
        pending_only: bool = False,
    ) -> List[StabilizationAction]:
        """Get stabilization actions."""
        actions = list(self._stabilization_actions.values())
        if pending_only:
            actions = [a for a in actions if a.executed_at is None]
        return actions

    def get_status(self) -> Dict[str, Any]:
        """Get stabilizer status."""
        return {
            "status": self._status.value,
            "circuit_breaker_open": self._circuit_breaker_open,
            "consecutive_failures": self._consecutive_failures,
            "active_anomalies": len(self._active_anomalies),
            "cascade_predictions": len(self._cascade_predictions),
            "pending_actions": len([a for a in self._stabilization_actions.values() if a.executed_at is None]),
            "city_config": self._city_config,
        }

    def get_statistics(self) -> Dict[str, Any]:
        """Get stabilizer statistics."""
        all_anomalies = list(self._anomalies.values())
        all_actions = list(self._stabilization_actions.values())

        return {
            "total_anomalies_detected": len(all_anomalies),
            "active_anomalies": len(self._active_anomalies),
            "resolved_anomalies": len(all_anomalies) - len(self._active_anomalies),
            "anomalies_by_domain": {
                domain.value: len([a for a in all_anomalies if a.domain == domain])
                for domain in MonitoringDomain
            },
            "anomalies_by_severity": {
                sev.value: len([a for a in all_anomalies if a.severity == sev])
                for sev in AnomalySeverity
            },
            "total_actions_generated": len(all_actions),
            "actions_executed": len([a for a in all_actions if a.executed_at]),
            "actions_pending": len([a for a in all_actions if not a.executed_at]),
            "actions_requiring_approval": len([a for a in all_actions if a.requires_approval and not a.executed_at]),
            "cascade_predictions": len(self._cascade_predictions),
            "circuit_breaker_status": "open" if self._circuit_breaker_open else "closed",
        }

    def reset_circuit_breaker(self):
        """Reset the circuit breaker."""
        self._circuit_breaker_open = False
        self._consecutive_failures = 0
        self._status = StabilizerStatus.MONITORING

    def set_action_callback(self, callback: Callable):
        """Set callback for when actions are generated."""
        self._action_callback = callback

    def run_stabilization_cycle(self) -> Dict[str, Any]:
        """Run a full stabilization cycle."""
        self._status = StabilizerStatus.STABILIZING

        # Process any pending actions that don't require approval
        auto_executed = 0
        for action in self._stabilization_actions.values():
            if not action.requires_approval and not action.executed_at:
                if self.execute_stabilization_action(action.action_id):
                    auto_executed += 1

        self._status = StabilizerStatus.MONITORING

        return {
            "cycle_completed": True,
            "auto_executed_actions": auto_executed,
            "pending_approval_actions": len([
                a for a in self._stabilization_actions.values()
                if a.requires_approval and not a.executed_at
            ]),
            "active_anomalies": len(self._active_anomalies),
        }


_city_stabilizer: Optional[AutomatedCityStabilizer] = None


def get_city_stabilizer() -> AutomatedCityStabilizer:
    """Get the singleton AutomatedCityStabilizer instance."""
    global _city_stabilizer
    if _city_stabilizer is None:
        _city_stabilizer = AutomatedCityStabilizer()
    return _city_stabilizer
