"""
Phase 23: City Scenario Simulator Module

Simulates "what-if" outcomes for various city scenarios including
road closures, weather events, major incidents, infrastructure outages,
crowd surges, crime displacement, and disaster impact modeling.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional
import uuid
import math
import random


class ScenarioType(Enum):
    """Types of scenarios that can be simulated."""
    ROAD_CLOSURE = "road_closure"
    WEATHER_EVENT = "weather_event"
    MAJOR_INCIDENT = "major_incident"
    MULTI_DAY_OPERATION = "multi_day_operation"
    INFRASTRUCTURE_OUTAGE = "infrastructure_outage"
    CROWD_SURGE = "crowd_surge"
    CRIME_DISPLACEMENT = "crime_displacement"
    HURRICANE = "hurricane"
    FLOODING = "flooding"
    HEATWAVE = "heatwave"
    MASS_CASUALTY = "mass_casualty"
    CIVIL_UNREST = "civil_unrest"
    SPECIAL_EVENT = "special_event"


class ScenarioStatus(Enum):
    """Status of a scenario simulation."""
    DRAFT = "draft"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ImpactSeverity(Enum):
    """Severity levels for scenario impacts."""
    MINIMAL = "minimal"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    SEVERE = "severe"
    CATASTROPHIC = "catastrophic"


class OutcomeCategory(Enum):
    """Categories of simulation outcomes."""
    TRAFFIC = "traffic"
    PUBLIC_SAFETY = "public_safety"
    UTILITIES = "utilities"
    EMERGENCY_SERVICES = "emergency_services"
    POPULATION = "population"
    ECONOMIC = "economic"
    INFRASTRUCTURE = "infrastructure"
    ENVIRONMENTAL = "environmental"


@dataclass
class ScenarioVariable:
    """A variable that can be adjusted in a scenario."""
    variable_id: str
    name: str
    description: str
    variable_type: str
    min_value: float
    max_value: float
    default_value: float
    current_value: float
    unit: str
    category: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "variable_id": self.variable_id,
            "name": self.name,
            "description": self.description,
            "variable_type": self.variable_type,
            "min_value": self.min_value,
            "max_value": self.max_value,
            "default_value": self.default_value,
            "current_value": self.current_value,
            "unit": self.unit,
            "category": self.category,
        }


@dataclass
class TimelineEvent:
    """An event in the simulation timeline."""
    event_id: str
    timestamp: datetime
    event_type: str
    description: str
    impact_score: float
    affected_zones: list[str]
    metrics_snapshot: dict[str, float]

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "timestamp": self.timestamp.isoformat(),
            "event_type": self.event_type,
            "description": self.description,
            "impact_score": self.impact_score,
            "affected_zones": self.affected_zones,
            "metrics_snapshot": self.metrics_snapshot,
        }


@dataclass
class OutcomePath:
    """A possible outcome path from the simulation."""
    path_id: str
    name: str
    probability: float
    description: str
    timeline: list[TimelineEvent]
    final_metrics: dict[str, float]
    risk_score: float
    recommendations: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "path_id": self.path_id,
            "name": self.name,
            "probability": self.probability,
            "description": self.description,
            "timeline": [e.to_dict() for e in self.timeline],
            "final_metrics": self.final_metrics,
            "risk_score": self.risk_score,
            "recommendations": self.recommendations,
        }


@dataclass
class ImpactAssessment:
    """Assessment of scenario impact on a specific category."""
    category: OutcomeCategory
    severity: ImpactSeverity
    description: str
    metrics: dict[str, float]
    affected_resources: list[str]
    mitigation_options: list[str]
    recovery_time_hours: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "category": self.category.value,
            "severity": self.severity.value,
            "description": self.description,
            "metrics": self.metrics,
            "affected_resources": self.affected_resources,
            "mitigation_options": self.mitigation_options,
            "recovery_time_hours": self.recovery_time_hours,
        }


@dataclass
class ScenarioConfiguration:
    """Configuration for a scenario simulation."""
    scenario_id: str
    scenario_type: ScenarioType
    name: str
    description: str
    variables: list[ScenarioVariable]
    duration_hours: int
    time_step_minutes: int
    affected_zones: list[str]
    start_time: datetime
    created_by: str
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict[str, Any]:
        return {
            "scenario_id": self.scenario_id,
            "scenario_type": self.scenario_type.value,
            "name": self.name,
            "description": self.description,
            "variables": [v.to_dict() for v in self.variables],
            "duration_hours": self.duration_hours,
            "time_step_minutes": self.time_step_minutes,
            "affected_zones": self.affected_zones,
            "start_time": self.start_time.isoformat(),
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class SimulationResult:
    """Result of a scenario simulation."""
    result_id: str
    scenario_id: str
    status: ScenarioStatus
    outcome_paths: list[OutcomePath]
    impact_assessments: list[ImpactAssessment]
    overall_risk_score: float
    recommended_actions: list[dict[str, Any]]
    resource_requirements: dict[str, int]
    estimated_cost: float
    execution_time_ms: int
    started_at: datetime
    completed_at: Optional[datetime] = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "result_id": self.result_id,
            "scenario_id": self.scenario_id,
            "status": self.status.value,
            "outcome_paths": [p.to_dict() for p in self.outcome_paths],
            "impact_assessments": [a.to_dict() for a in self.impact_assessments],
            "overall_risk_score": self.overall_risk_score,
            "recommended_actions": self.recommended_actions,
            "resource_requirements": self.resource_requirements,
            "estimated_cost": self.estimated_cost,
            "execution_time_ms": self.execution_time_ms,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


class SimulationEngine:
    """Core simulation engine for running scenarios."""

    def __init__(self):
        self._base_metrics = {
            "traffic_flow": 0.75,
            "response_time": 5.5,
            "coverage": 0.85,
            "utilization": 0.65,
            "crime_rate": 0.3,
            "utility_uptime": 0.98,
            "population_density": 0.5,
            "economic_activity": 0.7,
        }

    def run_simulation(
        self,
        config: ScenarioConfiguration,
    ) -> SimulationResult:
        """Run a scenario simulation."""
        start_time = datetime.utcnow()
        result_id = f"sim-{uuid.uuid4().hex[:12]}"

        outcome_paths = self._generate_outcome_paths(config)

        impact_assessments = self._assess_impacts(config, outcome_paths)

        overall_risk = self._calculate_overall_risk(outcome_paths, impact_assessments)

        recommended_actions = self._generate_recommendations(config, impact_assessments)

        resource_requirements = self._estimate_resource_requirements(config, impact_assessments)

        estimated_cost = self._estimate_cost(config, resource_requirements)

        end_time = datetime.utcnow()
        execution_time_ms = int((end_time - start_time).total_seconds() * 1000)

        return SimulationResult(
            result_id=result_id,
            scenario_id=config.scenario_id,
            status=ScenarioStatus.COMPLETED,
            outcome_paths=outcome_paths,
            impact_assessments=impact_assessments,
            overall_risk_score=overall_risk,
            recommended_actions=recommended_actions,
            resource_requirements=resource_requirements,
            estimated_cost=estimated_cost,
            execution_time_ms=execution_time_ms,
            started_at=start_time,
            completed_at=end_time,
        )

    def _generate_outcome_paths(self, config: ScenarioConfiguration) -> list[OutcomePath]:
        """Generate possible outcome paths for the scenario."""
        paths = []

        best_case = self._generate_path(config, "best_case", 0.25)
        paths.append(best_case)

        most_likely = self._generate_path(config, "most_likely", 0.50)
        paths.append(most_likely)

        worst_case = self._generate_path(config, "worst_case", 0.25)
        paths.append(worst_case)

        return paths

    def _generate_path(
        self,
        config: ScenarioConfiguration,
        path_type: str,
        probability: float,
    ) -> OutcomePath:
        """Generate a single outcome path."""
        path_id = f"path-{uuid.uuid4().hex[:8]}"

        impact_multiplier = {
            "best_case": 0.5,
            "most_likely": 1.0,
            "worst_case": 1.8,
        }.get(path_type, 1.0)

        timeline = self._generate_timeline(config, impact_multiplier)

        final_metrics = self._calculate_final_metrics(config, impact_multiplier)

        risk_score = self._calculate_path_risk(config, impact_multiplier)

        recommendations = self._generate_path_recommendations(config, path_type)

        return OutcomePath(
            path_id=path_id,
            name=path_type.replace("_", " ").title(),
            probability=probability,
            description=f"{path_type.replace('_', ' ').title()} outcome for {config.name}",
            timeline=timeline,
            final_metrics=final_metrics,
            risk_score=risk_score,
            recommendations=recommendations,
        )

    def _generate_timeline(
        self,
        config: ScenarioConfiguration,
        impact_multiplier: float,
    ) -> list[TimelineEvent]:
        """Generate timeline events for a path."""
        events = []
        current_time = config.start_time
        end_time = config.start_time + timedelta(hours=config.duration_hours)
        step = timedelta(minutes=config.time_step_minutes)

        event_templates = self._get_event_templates(config.scenario_type)

        while current_time < end_time:
            progress = (current_time - config.start_time).total_seconds() / (
                end_time - config.start_time
            ).total_seconds()

            if random.random() < 0.3:
                template = random.choice(event_templates)
                impact_score = template["base_impact"] * impact_multiplier * (1 + progress * 0.5)

                event = TimelineEvent(
                    event_id=f"evt-{uuid.uuid4().hex[:8]}",
                    timestamp=current_time,
                    event_type=template["type"],
                    description=template["description"],
                    impact_score=min(impact_score, 1.0),
                    affected_zones=random.sample(
                        config.affected_zones,
                        min(len(config.affected_zones), random.randint(1, 3)),
                    ),
                    metrics_snapshot=self._calculate_metrics_at_time(
                        config, progress, impact_multiplier
                    ),
                )
                events.append(event)

            current_time += step

        return events

    def _get_event_templates(self, scenario_type: ScenarioType) -> list[dict[str, Any]]:
        """Get event templates for a scenario type."""
        templates = {
            ScenarioType.ROAD_CLOSURE: [
                {"type": "traffic_backup", "description": "Traffic backup forming", "base_impact": 0.3},
                {"type": "reroute_activated", "description": "Alternate route activated", "base_impact": 0.2},
                {"type": "congestion_peak", "description": "Congestion reaching peak", "base_impact": 0.5},
            ],
            ScenarioType.WEATHER_EVENT: [
                {"type": "weather_warning", "description": "Weather warning issued", "base_impact": 0.4},
                {"type": "visibility_reduced", "description": "Visibility reduced", "base_impact": 0.3},
                {"type": "flooding_reported", "description": "Localized flooding reported", "base_impact": 0.6},
            ],
            ScenarioType.HURRICANE: [
                {"type": "evacuation_order", "description": "Evacuation order issued", "base_impact": 0.7},
                {"type": "shelter_activation", "description": "Emergency shelters activated", "base_impact": 0.5},
                {"type": "power_outage", "description": "Widespread power outages", "base_impact": 0.8},
                {"type": "storm_surge", "description": "Storm surge warning", "base_impact": 0.9},
            ],
            ScenarioType.INFRASTRUCTURE_OUTAGE: [
                {"type": "outage_detected", "description": "Infrastructure outage detected", "base_impact": 0.5},
                {"type": "crews_dispatched", "description": "Repair crews dispatched", "base_impact": 0.3},
                {"type": "partial_restoration", "description": "Partial service restored", "base_impact": 0.2},
            ],
            ScenarioType.CROWD_SURGE: [
                {"type": "crowd_gathering", "description": "Crowd gathering detected", "base_impact": 0.3},
                {"type": "capacity_warning", "description": "Venue approaching capacity", "base_impact": 0.5},
                {"type": "crowd_control", "description": "Crowd control measures activated", "base_impact": 0.4},
            ],
            ScenarioType.CRIME_DISPLACEMENT: [
                {"type": "activity_shift", "description": "Criminal activity shifting", "base_impact": 0.4},
                {"type": "patrol_adjustment", "description": "Patrol patterns adjusted", "base_impact": 0.3},
                {"type": "hotspot_emergence", "description": "New hotspot emerging", "base_impact": 0.5},
            ],
            ScenarioType.MAJOR_INCIDENT: [
                {"type": "incident_reported", "description": "Major incident reported", "base_impact": 0.6},
                {"type": "resources_deployed", "description": "Emergency resources deployed", "base_impact": 0.4},
                {"type": "scene_secured", "description": "Scene secured", "base_impact": 0.3},
            ],
        }
        return templates.get(scenario_type, [
            {"type": "event", "description": "Scenario event occurred", "base_impact": 0.4},
        ])

    def _calculate_metrics_at_time(
        self,
        config: ScenarioConfiguration,
        progress: float,
        impact_multiplier: float,
    ) -> dict[str, float]:
        """Calculate metrics at a specific point in time."""
        metrics = self._base_metrics.copy()

        impact_factor = self._get_scenario_impact_factor(config.scenario_type)

        for key in metrics:
            degradation = impact_factor.get(key, 0) * impact_multiplier * progress
            if key in ["traffic_flow", "coverage", "utility_uptime", "economic_activity"]:
                metrics[key] = max(0, metrics[key] - degradation)
            else:
                metrics[key] = min(1, metrics[key] + degradation)

        return metrics

    def _get_scenario_impact_factor(self, scenario_type: ScenarioType) -> dict[str, float]:
        """Get impact factors for a scenario type."""
        factors = {
            ScenarioType.ROAD_CLOSURE: {
                "traffic_flow": 0.4,
                "response_time": 0.3,
                "economic_activity": 0.2,
            },
            ScenarioType.WEATHER_EVENT: {
                "traffic_flow": 0.3,
                "response_time": 0.2,
                "utility_uptime": 0.2,
            },
            ScenarioType.HURRICANE: {
                "traffic_flow": 0.6,
                "response_time": 0.4,
                "utility_uptime": 0.7,
                "economic_activity": 0.5,
                "coverage": 0.3,
            },
            ScenarioType.INFRASTRUCTURE_OUTAGE: {
                "utility_uptime": 0.6,
                "economic_activity": 0.3,
            },
            ScenarioType.CROWD_SURGE: {
                "traffic_flow": 0.3,
                "response_time": 0.2,
                "coverage": 0.2,
            },
            ScenarioType.CRIME_DISPLACEMENT: {
                "crime_rate": 0.4,
                "coverage": 0.2,
            },
            ScenarioType.MAJOR_INCIDENT: {
                "response_time": 0.3,
                "coverage": 0.3,
                "utilization": 0.4,
            },
        }
        return factors.get(scenario_type, {})

    def _calculate_final_metrics(
        self,
        config: ScenarioConfiguration,
        impact_multiplier: float,
    ) -> dict[str, float]:
        """Calculate final metrics after scenario completion."""
        return self._calculate_metrics_at_time(config, 1.0, impact_multiplier)

    def _calculate_path_risk(
        self,
        config: ScenarioConfiguration,
        impact_multiplier: float,
    ) -> float:
        """Calculate risk score for a path."""
        base_risk = {
            ScenarioType.ROAD_CLOSURE: 0.3,
            ScenarioType.WEATHER_EVENT: 0.4,
            ScenarioType.HURRICANE: 0.8,
            ScenarioType.INFRASTRUCTURE_OUTAGE: 0.5,
            ScenarioType.CROWD_SURGE: 0.4,
            ScenarioType.CRIME_DISPLACEMENT: 0.4,
            ScenarioType.MAJOR_INCIDENT: 0.6,
            ScenarioType.FLOODING: 0.6,
            ScenarioType.HEATWAVE: 0.5,
            ScenarioType.MASS_CASUALTY: 0.9,
            ScenarioType.CIVIL_UNREST: 0.7,
            ScenarioType.SPECIAL_EVENT: 0.3,
        }.get(config.scenario_type, 0.5)

        return min(base_risk * impact_multiplier, 1.0)

    def _generate_path_recommendations(
        self,
        config: ScenarioConfiguration,
        path_type: str,
    ) -> list[str]:
        """Generate recommendations for a path."""
        recommendations = {
            "best_case": [
                "Maintain current resource levels",
                "Continue monitoring situation",
                "Prepare contingency plans",
            ],
            "most_likely": [
                "Increase patrol presence in affected zones",
                "Activate traffic management protocols",
                "Coordinate with neighboring agencies",
                "Pre-position emergency resources",
            ],
            "worst_case": [
                "Request mutual aid immediately",
                "Activate emergency operations center",
                "Implement full evacuation protocols",
                "Deploy all available resources",
                "Establish unified command",
            ],
        }
        return recommendations.get(path_type, ["Monitor and assess"])

    def _assess_impacts(
        self,
        config: ScenarioConfiguration,
        outcome_paths: list[OutcomePath],
    ) -> list[ImpactAssessment]:
        """Assess impacts across all categories."""
        assessments = []

        categories_to_assess = self._get_relevant_categories(config.scenario_type)

        for category in categories_to_assess:
            avg_risk = sum(p.risk_score for p in outcome_paths) / len(outcome_paths)
            severity = self._risk_to_severity(avg_risk)

            assessment = ImpactAssessment(
                category=category,
                severity=severity,
                description=f"Impact on {category.value} from {config.scenario_type.value}",
                metrics=self._get_category_metrics(category, avg_risk),
                affected_resources=self._get_affected_resources(category),
                mitigation_options=self._get_mitigation_options(category, severity),
                recovery_time_hours=self._estimate_recovery_time(category, severity),
            )
            assessments.append(assessment)

        return assessments

    def _get_relevant_categories(self, scenario_type: ScenarioType) -> list[OutcomeCategory]:
        """Get relevant impact categories for a scenario type."""
        category_map = {
            ScenarioType.ROAD_CLOSURE: [
                OutcomeCategory.TRAFFIC,
                OutcomeCategory.EMERGENCY_SERVICES,
                OutcomeCategory.ECONOMIC,
            ],
            ScenarioType.WEATHER_EVENT: [
                OutcomeCategory.TRAFFIC,
                OutcomeCategory.PUBLIC_SAFETY,
                OutcomeCategory.UTILITIES,
            ],
            ScenarioType.HURRICANE: [
                OutcomeCategory.TRAFFIC,
                OutcomeCategory.PUBLIC_SAFETY,
                OutcomeCategory.UTILITIES,
                OutcomeCategory.EMERGENCY_SERVICES,
                OutcomeCategory.POPULATION,
                OutcomeCategory.INFRASTRUCTURE,
            ],
            ScenarioType.INFRASTRUCTURE_OUTAGE: [
                OutcomeCategory.UTILITIES,
                OutcomeCategory.ECONOMIC,
                OutcomeCategory.POPULATION,
            ],
            ScenarioType.CROWD_SURGE: [
                OutcomeCategory.PUBLIC_SAFETY,
                OutcomeCategory.TRAFFIC,
                OutcomeCategory.EMERGENCY_SERVICES,
            ],
            ScenarioType.CRIME_DISPLACEMENT: [
                OutcomeCategory.PUBLIC_SAFETY,
                OutcomeCategory.POPULATION,
            ],
        }
        return category_map.get(scenario_type, [OutcomeCategory.PUBLIC_SAFETY])

    def _risk_to_severity(self, risk: float) -> ImpactSeverity:
        """Convert risk score to severity level."""
        if risk < 0.2:
            return ImpactSeverity.MINIMAL
        elif risk < 0.4:
            return ImpactSeverity.LOW
        elif risk < 0.6:
            return ImpactSeverity.MODERATE
        elif risk < 0.8:
            return ImpactSeverity.HIGH
        elif risk < 0.95:
            return ImpactSeverity.SEVERE
        else:
            return ImpactSeverity.CATASTROPHIC

    def _get_category_metrics(
        self, category: OutcomeCategory, risk: float
    ) -> dict[str, float]:
        """Get metrics for a specific category."""
        base_metrics = {
            OutcomeCategory.TRAFFIC: {
                "congestion_increase": risk * 50,
                "travel_time_increase": risk * 30,
                "incidents_expected": risk * 5,
            },
            OutcomeCategory.PUBLIC_SAFETY: {
                "response_time_increase": risk * 40,
                "coverage_reduction": risk * 25,
                "incident_probability": risk * 0.6,
            },
            OutcomeCategory.UTILITIES: {
                "outage_probability": risk * 0.7,
                "customers_affected": risk * 5000,
                "restoration_hours": risk * 24,
            },
            OutcomeCategory.EMERGENCY_SERVICES: {
                "resource_strain": risk * 0.8,
                "mutual_aid_needed": risk > 0.6,
                "overtime_hours": risk * 100,
            },
            OutcomeCategory.POPULATION: {
                "displacement_count": risk * 1000,
                "shelter_needs": risk * 500,
                "evacuation_required": risk > 0.7,
            },
            OutcomeCategory.ECONOMIC: {
                "business_impact_dollars": risk * 500000,
                "productivity_loss": risk * 0.4,
                "recovery_cost": risk * 250000,
            },
            OutcomeCategory.INFRASTRUCTURE: {
                "damage_probability": risk * 0.6,
                "repair_cost": risk * 100000,
                "downtime_hours": risk * 48,
            },
        }
        return base_metrics.get(category, {"impact": risk})

    def _get_affected_resources(self, category: OutcomeCategory) -> list[str]:
        """Get affected resources for a category."""
        resources = {
            OutcomeCategory.TRAFFIC: ["traffic_signals", "message_boards", "traffic_units"],
            OutcomeCategory.PUBLIC_SAFETY: ["police_units", "patrol_vehicles", "dispatch"],
            OutcomeCategory.UTILITIES: ["power_grid", "water_system", "utility_crews"],
            OutcomeCategory.EMERGENCY_SERVICES: ["fire_units", "ems_units", "rescue_equipment"],
            OutcomeCategory.POPULATION: ["shelters", "evacuation_routes", "social_services"],
            OutcomeCategory.ECONOMIC: ["businesses", "transportation", "commerce"],
            OutcomeCategory.INFRASTRUCTURE: ["roads", "bridges", "buildings"],
        }
        return resources.get(category, ["general_resources"])

    def _get_mitigation_options(
        self, category: OutcomeCategory, severity: ImpactSeverity
    ) -> list[str]:
        """Get mitigation options for a category and severity."""
        options = {
            OutcomeCategory.TRAFFIC: [
                "Activate traffic management center",
                "Deploy traffic control officers",
                "Implement signal timing changes",
            ],
            OutcomeCategory.PUBLIC_SAFETY: [
                "Increase patrol presence",
                "Activate reserve officers",
                "Request mutual aid",
            ],
            OutcomeCategory.UTILITIES: [
                "Pre-position repair crews",
                "Activate backup generators",
                "Coordinate with utility providers",
            ],
            OutcomeCategory.EMERGENCY_SERVICES: [
                "Staff up emergency units",
                "Pre-position resources",
                "Activate EOC",
            ],
        }
        base_options = options.get(category, ["Monitor situation"])

        if severity in [ImpactSeverity.SEVERE, ImpactSeverity.CATASTROPHIC]:
            base_options.extend([
                "Declare local emergency",
                "Request state assistance",
                "Activate all available resources",
            ])

        return base_options

    def _estimate_recovery_time(
        self, category: OutcomeCategory, severity: ImpactSeverity
    ) -> float:
        """Estimate recovery time in hours."""
        base_times = {
            OutcomeCategory.TRAFFIC: 4,
            OutcomeCategory.PUBLIC_SAFETY: 8,
            OutcomeCategory.UTILITIES: 24,
            OutcomeCategory.EMERGENCY_SERVICES: 12,
            OutcomeCategory.POPULATION: 48,
            OutcomeCategory.ECONOMIC: 72,
            OutcomeCategory.INFRASTRUCTURE: 168,
        }
        base = base_times.get(category, 24)

        multipliers = {
            ImpactSeverity.MINIMAL: 0.25,
            ImpactSeverity.LOW: 0.5,
            ImpactSeverity.MODERATE: 1.0,
            ImpactSeverity.HIGH: 2.0,
            ImpactSeverity.SEVERE: 4.0,
            ImpactSeverity.CATASTROPHIC: 8.0,
        }
        return base * multipliers.get(severity, 1.0)

    def _calculate_overall_risk(
        self,
        outcome_paths: list[OutcomePath],
        impact_assessments: list[ImpactAssessment],
    ) -> float:
        """Calculate overall risk score."""
        path_risk = sum(p.risk_score * p.probability for p in outcome_paths)

        severity_scores = {
            ImpactSeverity.MINIMAL: 0.1,
            ImpactSeverity.LOW: 0.25,
            ImpactSeverity.MODERATE: 0.5,
            ImpactSeverity.HIGH: 0.75,
            ImpactSeverity.SEVERE: 0.9,
            ImpactSeverity.CATASTROPHIC: 1.0,
        }
        impact_risk = sum(
            severity_scores.get(a.severity, 0.5) for a in impact_assessments
        ) / len(impact_assessments) if impact_assessments else 0

        return (path_risk + impact_risk) / 2

    def _generate_recommendations(
        self,
        config: ScenarioConfiguration,
        impact_assessments: list[ImpactAssessment],
    ) -> list[dict[str, Any]]:
        """Generate recommended actions based on simulation results."""
        recommendations = []

        for assessment in impact_assessments:
            for option in assessment.mitigation_options[:2]:
                recommendations.append({
                    "action": option,
                    "category": assessment.category.value,
                    "priority": "high" if assessment.severity.value in ["severe", "catastrophic"] else "medium",
                    "timing": "immediate" if assessment.severity.value in ["severe", "catastrophic"] else "planned",
                })

        return recommendations

    def _estimate_resource_requirements(
        self,
        config: ScenarioConfiguration,
        impact_assessments: list[ImpactAssessment],
    ) -> dict[str, int]:
        """Estimate resource requirements."""
        requirements = {
            "police_units": 0,
            "fire_units": 0,
            "ems_units": 0,
            "public_works_crews": 0,
            "utility_crews": 0,
            "shelter_capacity": 0,
        }

        for assessment in impact_assessments:
            multiplier = {
                ImpactSeverity.MINIMAL: 1,
                ImpactSeverity.LOW: 2,
                ImpactSeverity.MODERATE: 3,
                ImpactSeverity.HIGH: 5,
                ImpactSeverity.SEVERE: 8,
                ImpactSeverity.CATASTROPHIC: 12,
            }.get(assessment.severity, 1)

            if assessment.category == OutcomeCategory.PUBLIC_SAFETY:
                requirements["police_units"] += multiplier
            elif assessment.category == OutcomeCategory.EMERGENCY_SERVICES:
                requirements["fire_units"] += multiplier
                requirements["ems_units"] += multiplier
            elif assessment.category == OutcomeCategory.UTILITIES:
                requirements["utility_crews"] += multiplier
            elif assessment.category == OutcomeCategory.INFRASTRUCTURE:
                requirements["public_works_crews"] += multiplier
            elif assessment.category == OutcomeCategory.POPULATION:
                requirements["shelter_capacity"] += multiplier * 100

        return requirements

    def _estimate_cost(
        self,
        config: ScenarioConfiguration,
        resource_requirements: dict[str, int],
    ) -> float:
        """Estimate total cost of response."""
        cost_per_unit = {
            "police_units": 500,
            "fire_units": 800,
            "ems_units": 600,
            "public_works_crews": 400,
            "utility_crews": 450,
            "shelter_capacity": 50,
        }

        total = sum(
            resource_requirements.get(resource, 0) * cost_per_unit.get(resource, 100) * config.duration_hours
            for resource in resource_requirements
        )

        return total


class CityScenarioSimulator:
    """
    Main scenario simulator that manages scenario configurations and simulations.
    """

    def __init__(self):
        self._engine = SimulationEngine()
        self._scenarios: dict[str, ScenarioConfiguration] = {}
        self._results: dict[str, SimulationResult] = {}
        self._templates: dict[str, ScenarioConfiguration] = {}
        self._initialize_templates()

    def _initialize_templates(self):
        """Initialize scenario templates."""
        now = datetime.utcnow()

        self._templates["hurricane_cat3"] = ScenarioConfiguration(
            scenario_id="template-hurricane-cat3",
            scenario_type=ScenarioType.HURRICANE,
            name="Category 3 Hurricane",
            description="Simulation of a Category 3 hurricane impact on Riviera Beach",
            variables=[
                ScenarioVariable("wind_speed", "Wind Speed", "Maximum sustained winds", "float",
                                111, 129, 120, 120, "mph", "weather"),
                ScenarioVariable("storm_surge", "Storm Surge", "Expected storm surge height", "float",
                                6, 12, 9, 9, "feet", "weather"),
                ScenarioVariable("rainfall", "Rainfall", "Expected rainfall amount", "float",
                                6, 15, 10, 10, "inches", "weather"),
                ScenarioVariable("evacuation_compliance", "Evacuation Compliance", "Expected evacuation compliance rate",
                                "float", 0.5, 0.95, 0.75, 0.75, "percent", "population"),
            ],
            duration_hours=72,
            time_step_minutes=60,
            affected_zones=["singer_island", "marina", "downtown", "westside"],
            start_time=now,
            created_by="system",
        )

        self._templates["major_event"] = ScenarioConfiguration(
            scenario_id="template-major-event",
            scenario_type=ScenarioType.SPECIAL_EVENT,
            name="Major Public Event",
            description="Simulation of a major public event at the marina",
            variables=[
                ScenarioVariable("attendance", "Expected Attendance", "Number of attendees", "int",
                                5000, 50000, 15000, 15000, "people", "crowd"),
                ScenarioVariable("duration", "Event Duration", "Duration of the event", "float",
                                4, 12, 6, 6, "hours", "timing"),
                ScenarioVariable("parking_capacity", "Parking Capacity", "Available parking spaces", "int",
                                500, 5000, 2000, 2000, "spaces", "infrastructure"),
            ],
            duration_hours=12,
            time_step_minutes=30,
            affected_zones=["marina", "downtown"],
            start_time=now,
            created_by="system",
        )

        self._templates["power_outage"] = ScenarioConfiguration(
            scenario_id="template-power-outage",
            scenario_type=ScenarioType.INFRASTRUCTURE_OUTAGE,
            name="Major Power Outage",
            description="Simulation of a major power outage affecting multiple zones",
            variables=[
                ScenarioVariable("customers_affected", "Customers Affected", "Number of customers without power",
                                "int", 1000, 20000, 5000, 5000, "customers", "utilities"),
                ScenarioVariable("restoration_time", "Estimated Restoration", "Expected restoration time",
                                "float", 2, 48, 8, 8, "hours", "timing"),
                ScenarioVariable("critical_facilities", "Critical Facilities", "Number of critical facilities affected",
                                "int", 0, 10, 2, 2, "facilities", "infrastructure"),
            ],
            duration_hours=24,
            time_step_minutes=30,
            affected_zones=["downtown", "westside", "industrial"],
            start_time=now,
            created_by="system",
        )

        self._templates["road_closure"] = ScenarioConfiguration(
            scenario_id="template-road-closure",
            scenario_type=ScenarioType.ROAD_CLOSURE,
            name="Major Road Closure",
            description="Simulation of a major road closure on Blue Heron Blvd",
            variables=[
                ScenarioVariable("closure_duration", "Closure Duration", "Duration of road closure",
                                "float", 1, 72, 8, 8, "hours", "timing"),
                ScenarioVariable("lanes_affected", "Lanes Affected", "Number of lanes closed",
                                "int", 1, 4, 2, 2, "lanes", "infrastructure"),
                ScenarioVariable("detour_capacity", "Detour Capacity", "Capacity of detour routes",
                                "float", 0.5, 1.0, 0.7, 0.7, "percent", "traffic"),
            ],
            duration_hours=12,
            time_step_minutes=15,
            affected_zones=["downtown", "marina"],
            start_time=now,
            created_by="system",
        )

    def create_scenario(
        self,
        scenario_type: ScenarioType,
        name: str,
        description: str,
        variables: list[dict[str, Any]],
        duration_hours: int,
        affected_zones: list[str],
        created_by: str,
    ) -> ScenarioConfiguration:
        """Create a new scenario configuration."""
        scenario_id = f"scenario-{uuid.uuid4().hex[:12]}"

        scenario_variables = [
            ScenarioVariable(
                variable_id=f"var-{uuid.uuid4().hex[:8]}",
                name=v["name"],
                description=v.get("description", ""),
                variable_type=v.get("type", "float"),
                min_value=v.get("min", 0),
                max_value=v.get("max", 100),
                default_value=v.get("default", 50),
                current_value=v.get("value", v.get("default", 50)),
                unit=v.get("unit", ""),
                category=v.get("category", "general"),
            )
            for v in variables
        ]

        config = ScenarioConfiguration(
            scenario_id=scenario_id,
            scenario_type=scenario_type,
            name=name,
            description=description,
            variables=scenario_variables,
            duration_hours=duration_hours,
            time_step_minutes=max(15, duration_hours),
            affected_zones=affected_zones,
            start_time=datetime.utcnow(),
            created_by=created_by,
        )

        self._scenarios[scenario_id] = config
        return config

    def create_from_template(
        self,
        template_id: str,
        variable_overrides: Optional[dict[str, float]] = None,
        created_by: str = "user",
    ) -> Optional[ScenarioConfiguration]:
        """Create a scenario from a template."""
        template = self._templates.get(template_id)
        if not template:
            return None

        scenario_id = f"scenario-{uuid.uuid4().hex[:12]}"

        variables = []
        for v in template.variables:
            new_var = ScenarioVariable(
                variable_id=f"var-{uuid.uuid4().hex[:8]}",
                name=v.name,
                description=v.description,
                variable_type=v.variable_type,
                min_value=v.min_value,
                max_value=v.max_value,
                default_value=v.default_value,
                current_value=variable_overrides.get(v.name, v.current_value) if variable_overrides else v.current_value,
                unit=v.unit,
                category=v.category,
            )
            variables.append(new_var)

        config = ScenarioConfiguration(
            scenario_id=scenario_id,
            scenario_type=template.scenario_type,
            name=template.name,
            description=template.description,
            variables=variables,
            duration_hours=template.duration_hours,
            time_step_minutes=template.time_step_minutes,
            affected_zones=template.affected_zones.copy(),
            start_time=datetime.utcnow(),
            created_by=created_by,
        )

        self._scenarios[scenario_id] = config
        return config

    def run_scenario(self, scenario_id: str) -> Optional[SimulationResult]:
        """Run a scenario simulation."""
        config = self._scenarios.get(scenario_id)
        if not config:
            return None

        result = self._engine.run_simulation(config)
        self._results[result.result_id] = result
        return result

    def get_scenario(self, scenario_id: str) -> Optional[ScenarioConfiguration]:
        """Get a scenario configuration."""
        return self._scenarios.get(scenario_id)

    def get_result(self, result_id: str) -> Optional[SimulationResult]:
        """Get a simulation result."""
        return self._results.get(result_id)

    def get_templates(self) -> list[ScenarioConfiguration]:
        """Get all scenario templates."""
        return list(self._templates.values())

    def get_scenarios(self) -> list[ScenarioConfiguration]:
        """Get all scenarios."""
        return list(self._scenarios.values())

    def get_results(self) -> list[SimulationResult]:
        """Get all simulation results."""
        return list(self._results.values())

    def update_variable(
        self,
        scenario_id: str,
        variable_name: str,
        new_value: float,
    ) -> bool:
        """Update a variable value in a scenario."""
        config = self._scenarios.get(scenario_id)
        if not config:
            return False

        for variable in config.variables:
            if variable.name == variable_name:
                if variable.min_value <= new_value <= variable.max_value:
                    variable.current_value = new_value
                    return True
        return False

    def delete_scenario(self, scenario_id: str) -> bool:
        """Delete a scenario."""
        if scenario_id in self._scenarios:
            del self._scenarios[scenario_id]
            return True
        return False

    def get_statistics(self) -> dict[str, Any]:
        """Get simulator statistics."""
        return {
            "total_templates": len(self._templates),
            "total_scenarios": len(self._scenarios),
            "total_simulations": len(self._results),
            "scenarios_by_type": {
                st.value: sum(1 for s in self._scenarios.values() if s.scenario_type == st)
                for st in ScenarioType
            },
        }


_scenario_simulator: Optional[CityScenarioSimulator] = None


def get_scenario_simulator() -> CityScenarioSimulator:
    """Get the singleton scenario simulator instance."""
    global _scenario_simulator
    if _scenario_simulator is None:
        _scenario_simulator = CityScenarioSimulator()
    return _scenario_simulator
