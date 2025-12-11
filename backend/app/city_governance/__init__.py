"""
Phase 23: AI City Governance & Resource Optimization Engine

This module implements the governance decision engine that transforms
Riviera Beach's RTCC into a full city operations co-pilot.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Optional
import uuid
import json
import math
import random


class DecisionDomain(Enum):
    """Decision domains supported by the governance engine."""
    PUBLIC_SAFETY = "public_safety"
    TRAFFIC_MOBILITY = "traffic_mobility"
    UTILITIES = "utilities"
    PUBLIC_WORKS = "public_works"
    STORM_RESPONSE = "storm_response"
    CROWD_MANAGEMENT = "crowd_management"
    EMERGENCY_SERVICES = "emergency_services"
    RESOURCE_ALLOCATION = "resource_allocation"


class DecisionPriority(Enum):
    """Priority levels for governance decisions."""
    LOW = 0
    MEDIUM = 1
    HIGH = 2
    CRITICAL = 3
    EMERGENCY = 4


class DecisionStatus(Enum):
    """Status of a governance decision."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    IMPLEMENTED = "implemented"
    EXPIRED = "expired"
    SUPERSEDED = "superseded"


class RecommendationType(Enum):
    """Types of recommendations."""
    DEPLOYMENT = "deployment"
    REALLOCATION = "reallocation"
    PREVENTIVE = "preventive"
    REACTIVE = "reactive"
    OPTIMIZATION = "optimization"
    ALERT = "alert"
    POLICY = "policy"


class ConfidenceLevel(Enum):
    """Confidence levels for recommendations."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


@dataclass
class DecisionExplanation:
    """Explanation for a governance decision (Explainability Layer)."""
    explanation_id: str
    summary: str
    factors: list[dict[str, Any]]
    data_sources: list[str]
    confidence_breakdown: dict[str, float]
    alternative_options: list[dict[str, Any]]
    risk_assessment: dict[str, Any]
    historical_precedents: list[dict[str, Any]]
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict[str, Any]:
        return {
            "explanation_id": self.explanation_id,
            "summary": self.summary,
            "factors": self.factors,
            "data_sources": self.data_sources,
            "confidence_breakdown": self.confidence_breakdown,
            "alternative_options": self.alternative_options,
            "risk_assessment": self.risk_assessment,
            "historical_precedents": self.historical_precedents,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class GovernanceDecision:
    """A governance decision recommendation."""
    decision_id: str
    domain: DecisionDomain
    recommendation_type: RecommendationType
    title: str
    description: str
    priority: DecisionPriority
    confidence: ConfidenceLevel
    status: DecisionStatus
    recommended_action: dict[str, Any]
    expected_impact: dict[str, Any]
    explanation: DecisionExplanation
    affected_resources: list[str]
    affected_zones: list[str]
    valid_from: datetime
    valid_until: datetime
    created_at: datetime = field(default_factory=datetime.utcnow)
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    implementation_notes: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "decision_id": self.decision_id,
            "domain": self.domain.value,
            "recommendation_type": self.recommendation_type.value,
            "title": self.title,
            "description": self.description,
            "priority": self.priority.value,
            "confidence": self.confidence.value,
            "status": self.status.value,
            "recommended_action": self.recommended_action,
            "expected_impact": self.expected_impact,
            "explanation": self.explanation.to_dict(),
            "affected_resources": self.affected_resources,
            "affected_zones": self.affected_zones,
            "valid_from": self.valid_from.isoformat(),
            "valid_until": self.valid_until.isoformat(),
            "created_at": self.created_at.isoformat(),
            "approved_by": self.approved_by,
            "approved_at": self.approved_at.isoformat() if self.approved_at else None,
            "implementation_notes": self.implementation_notes,
        }


@dataclass
class DecisionRule:
    """A rule in the weighted rules engine."""
    rule_id: str
    name: str
    domain: DecisionDomain
    condition: Callable[[dict[str, Any]], bool]
    weight: float
    action_template: dict[str, Any]
    priority_modifier: int
    enabled: bool = True

    def evaluate(self, context: dict[str, Any]) -> tuple[bool, float]:
        """Evaluate the rule against the given context."""
        if not self.enabled:
            return False, 0.0
        try:
            result = self.condition(context)
            return result, self.weight if result else 0.0
        except Exception:
            return False, 0.0


@dataclass
class PolicyModel:
    """ML policy model for decision making."""
    model_id: str
    name: str
    domain: DecisionDomain
    version: str
    accuracy: float
    last_trained: datetime
    feature_weights: dict[str, float]
    threshold: float = 0.5

    def predict(self, features: dict[str, float]) -> tuple[float, dict[str, float]]:
        """Predict decision score based on features."""
        score = 0.0
        contributions = {}
        for feature_name, feature_value in features.items():
            weight = self.feature_weights.get(feature_name, 0.0)
            contribution = feature_value * weight
            score += contribution
            contributions[feature_name] = contribution
        normalized_score = 1 / (1 + math.exp(-score))
        return normalized_score, contributions


class GovernanceDecisionEngine:
    """
    Main governance decision engine that parses real-time city data
    and computes decision recommendations.
    """

    def __init__(self):
        self._rules: dict[str, DecisionRule] = {}
        self._policy_models: dict[str, PolicyModel] = {}
        self._decisions: dict[str, GovernanceDecision] = {}
        self._decision_history: list[GovernanceDecision] = []
        self._audit_log: list[dict[str, Any]] = []
        self._initialize_default_rules()
        self._initialize_policy_models()

    def _initialize_default_rules(self):
        """Initialize default decision rules."""
        self._rules["high_crime_patrol"] = DecisionRule(
            rule_id="rule-001",
            name="High Crime Area Patrol Increase",
            domain=DecisionDomain.PUBLIC_SAFETY,
            condition=lambda ctx: ctx.get("crime_risk", 0) > 0.7,
            weight=0.8,
            action_template={
                "action": "increase_patrol",
                "resource_type": "police_unit",
                "increase_percentage": 25,
            },
            priority_modifier=1,
        )

        self._rules["traffic_congestion_reroute"] = DecisionRule(
            rule_id="rule-002",
            name="Traffic Congestion Reroute",
            domain=DecisionDomain.TRAFFIC_MOBILITY,
            condition=lambda ctx: ctx.get("congestion_level", 0) > 0.8,
            weight=0.7,
            action_template={
                "action": "activate_reroute",
                "signal_timing_adjustment": True,
                "advisory_broadcast": True,
            },
            priority_modifier=0,
        )

        self._rules["storm_preparation"] = DecisionRule(
            rule_id="rule-003",
            name="Storm Preparation Protocol",
            domain=DecisionDomain.STORM_RESPONSE,
            condition=lambda ctx: ctx.get("storm_probability", 0) > 0.6,
            weight=0.9,
            action_template={
                "action": "activate_storm_protocol",
                "shelter_preparation": True,
                "resource_staging": True,
                "evacuation_standby": True,
            },
            priority_modifier=2,
        )

        self._rules["utility_failure_response"] = DecisionRule(
            rule_id="rule-004",
            name="Utility Failure Response",
            domain=DecisionDomain.UTILITIES,
            condition=lambda ctx: ctx.get("outage_customers", 0) > 500,
            weight=0.85,
            action_template={
                "action": "dispatch_utility_crews",
                "priority_restoration": True,
                "backup_power_activation": True,
            },
            priority_modifier=1,
        )

        self._rules["crowd_surge_management"] = DecisionRule(
            rule_id="rule-005",
            name="Crowd Surge Management",
            domain=DecisionDomain.CROWD_MANAGEMENT,
            condition=lambda ctx: ctx.get("crowd_density", 0) > 0.75,
            weight=0.75,
            action_template={
                "action": "deploy_crowd_control",
                "additional_units": 3,
                "traffic_control": True,
                "medical_standby": True,
            },
            priority_modifier=1,
        )

        self._rules["ems_coverage_gap"] = DecisionRule(
            rule_id="rule-006",
            name="EMS Coverage Gap Response",
            domain=DecisionDomain.EMERGENCY_SERVICES,
            condition=lambda ctx: ctx.get("ems_coverage_gap", False),
            weight=0.9,
            action_template={
                "action": "reposition_ems_units",
                "mutual_aid_request": True,
                "coverage_optimization": True,
            },
            priority_modifier=2,
        )

        self._rules["fire_risk_prevention"] = DecisionRule(
            rule_id="rule-007",
            name="Fire Risk Prevention",
            domain=DecisionDomain.PUBLIC_SAFETY,
            condition=lambda ctx: ctx.get("fire_risk_index", 0) > 0.7 and ctx.get("temperature_f", 0) > 95,
            weight=0.8,
            action_template={
                "action": "fire_prevention_patrol",
                "brush_fire_watch": True,
                "hydrant_check": True,
            },
            priority_modifier=1,
        )

        self._rules["public_works_maintenance"] = DecisionRule(
            rule_id="rule-008",
            name="Preventive Maintenance Trigger",
            domain=DecisionDomain.PUBLIC_WORKS,
            condition=lambda ctx: ctx.get("infrastructure_risk", 0) > 0.6,
            weight=0.6,
            action_template={
                "action": "schedule_maintenance",
                "priority": "high",
                "inspection_required": True,
            },
            priority_modifier=0,
        )

    def _initialize_policy_models(self):
        """Initialize ML policy models."""
        self._policy_models["patrol_optimization"] = PolicyModel(
            model_id="model-001",
            name="Patrol Optimization Model",
            domain=DecisionDomain.PUBLIC_SAFETY,
            version="1.0.0",
            accuracy=0.87,
            last_trained=datetime.utcnow() - timedelta(days=7),
            feature_weights={
                "crime_rate": 0.35,
                "call_volume": 0.25,
                "time_of_day": 0.15,
                "day_of_week": 0.10,
                "weather_factor": 0.08,
                "event_factor": 0.07,
            },
        )

        self._policy_models["traffic_optimization"] = PolicyModel(
            model_id="model-002",
            name="Traffic Flow Optimization Model",
            domain=DecisionDomain.TRAFFIC_MOBILITY,
            version="1.0.0",
            accuracy=0.82,
            last_trained=datetime.utcnow() - timedelta(days=5),
            feature_weights={
                "congestion_level": 0.30,
                "incident_count": 0.20,
                "time_of_day": 0.20,
                "weather_impact": 0.15,
                "event_impact": 0.15,
            },
        )

        self._policy_models["resource_allocation"] = PolicyModel(
            model_id="model-003",
            name="Resource Allocation Model",
            domain=DecisionDomain.RESOURCE_ALLOCATION,
            version="1.0.0",
            accuracy=0.85,
            last_trained=datetime.utcnow() - timedelta(days=3),
            feature_weights={
                "demand_forecast": 0.30,
                "current_utilization": 0.25,
                "response_time_target": 0.20,
                "cost_factor": 0.15,
                "coverage_gap": 0.10,
            },
        )

        self._policy_models["emergency_response"] = PolicyModel(
            model_id="model-004",
            name="Emergency Response Model",
            domain=DecisionDomain.EMERGENCY_SERVICES,
            version="1.0.0",
            accuracy=0.91,
            last_trained=datetime.utcnow() - timedelta(days=2),
            feature_weights={
                "incident_severity": 0.35,
                "resource_availability": 0.25,
                "response_time": 0.20,
                "coverage_status": 0.12,
                "mutual_aid_status": 0.08,
            },
        )

    def process_city_data(self, city_state: dict[str, Any]) -> list[GovernanceDecision]:
        """Process city data and generate decision recommendations."""
        decisions = []
        context = self._build_context(city_state)
        rule_decisions = self._evaluate_rules(context)
        decisions.extend(rule_decisions)
        ml_decisions = self._evaluate_policy_models(context)
        decisions.extend(ml_decisions)
        decisions = self._deduplicate_decisions(decisions)
        decisions = self._prioritize_decisions(decisions)
        for decision in decisions:
            self._decisions[decision.decision_id] = decision
            self._decision_history.append(decision)
            self._log_audit("decision_generated", decision.decision_id, decision.to_dict())
        return decisions

    def _build_context(self, city_state: dict[str, Any]) -> dict[str, Any]:
        """Build context from city state for rule evaluation."""
        weather = city_state.get("weather", {})
        traffic = city_state.get("traffic", {})
        utilities = city_state.get("utilities", {})
        incidents = city_state.get("incidents", {})
        predictions = city_state.get("predictions", {})

        context = {
            "crime_risk": predictions.get("crime", {}).get("overall_risk", 0.3),
            "congestion_level": traffic.get("overall_congestion", 0.4),
            "storm_probability": weather.get("storm_probability", 0.0),
            "outage_customers": utilities.get("power", {}).get("customers_affected", 0),
            "crowd_density": city_state.get("population", {}).get("crowd_density", 0.3),
            "ems_coverage_gap": incidents.get("ems_coverage_gap", False),
            "fire_risk_index": predictions.get("fire_risk", 0.2),
            "temperature_f": weather.get("temperature_f", 85),
            "infrastructure_risk": predictions.get("infrastructure", {}).get("overall_risk", 0.3),
            "call_volume": incidents.get("call_volume_24h", 50),
            "active_incidents": len(incidents.get("active", [])),
            "available_units": city_state.get("resources", {}).get("available_units", 10),
            "time_of_day": datetime.utcnow().hour,
            "day_of_week": datetime.utcnow().weekday(),
        }
        return context

    def _evaluate_rules(self, context: dict[str, Any]) -> list[GovernanceDecision]:
        """Evaluate all rules against the context."""
        decisions = []
        for rule in self._rules.values():
            triggered, weight = rule.evaluate(context)
            if triggered:
                decision = self._create_decision_from_rule(rule, context, weight)
                decisions.append(decision)
        return decisions

    def _evaluate_policy_models(self, context: dict[str, Any]) -> list[GovernanceDecision]:
        """Evaluate ML policy models."""
        decisions = []
        for model in self._policy_models.values():
            features = self._extract_features_for_model(model, context)
            score, contributions = model.predict(features)
            if score > model.threshold:
                decision = self._create_decision_from_model(model, context, score, contributions)
                decisions.append(decision)
        return decisions

    def _extract_features_for_model(self, model: PolicyModel, context: dict[str, Any]) -> dict[str, float]:
        """Extract features for a specific model."""
        features = {}
        for feature_name in model.feature_weights.keys():
            if feature_name in context:
                features[feature_name] = float(context[feature_name])
            elif feature_name == "time_of_day":
                features[feature_name] = context.get("time_of_day", 12) / 24.0
            elif feature_name == "day_of_week":
                features[feature_name] = context.get("day_of_week", 0) / 7.0
            elif feature_name == "weather_factor":
                features[feature_name] = 1.0 if context.get("storm_probability", 0) > 0.3 else 0.0
            elif feature_name == "event_factor":
                features[feature_name] = min(context.get("crowd_density", 0), 1.0)
            elif feature_name == "demand_forecast":
                features[feature_name] = context.get("call_volume", 50) / 100.0
            elif feature_name == "current_utilization":
                available = context.get("available_units", 10)
                features[feature_name] = 1.0 - (available / 20.0)
            elif feature_name == "response_time_target":
                features[feature_name] = 0.8
            elif feature_name == "cost_factor":
                features[feature_name] = 0.5
            elif feature_name == "coverage_gap":
                features[feature_name] = 1.0 if context.get("ems_coverage_gap", False) else 0.0
            elif feature_name == "incident_severity":
                features[feature_name] = min(context.get("active_incidents", 0) / 10.0, 1.0)
            elif feature_name == "resource_availability":
                features[feature_name] = context.get("available_units", 10) / 20.0
            elif feature_name == "response_time":
                features[feature_name] = 0.7
            elif feature_name == "coverage_status":
                features[feature_name] = 0.8
            elif feature_name == "mutual_aid_status":
                features[feature_name] = 1.0
            elif feature_name == "crime_rate":
                features[feature_name] = context.get("crime_risk", 0.3)
            elif feature_name == "call_volume":
                features[feature_name] = context.get("call_volume", 50) / 100.0
            elif feature_name == "congestion_level":
                features[feature_name] = context.get("congestion_level", 0.4)
            elif feature_name == "incident_count":
                features[feature_name] = min(context.get("active_incidents", 0) / 5.0, 1.0)
            elif feature_name == "weather_impact":
                features[feature_name] = context.get("storm_probability", 0)
            elif feature_name == "event_impact":
                features[feature_name] = context.get("crowd_density", 0.3)
            else:
                features[feature_name] = 0.5
        return features

    def _create_decision_from_rule(
        self, rule: DecisionRule, context: dict[str, Any], weight: float
    ) -> GovernanceDecision:
        """Create a governance decision from a triggered rule."""
        decision_id = f"dec-{uuid.uuid4().hex[:12]}"
        now = datetime.utcnow()

        priority = DecisionPriority(min(rule.priority_modifier + 1, 4))
        confidence = ConfidenceLevel.HIGH if weight > 0.8 else (
            ConfidenceLevel.MEDIUM if weight > 0.6 else ConfidenceLevel.LOW
        )

        explanation = DecisionExplanation(
            explanation_id=f"exp-{uuid.uuid4().hex[:8]}",
            summary=f"Rule '{rule.name}' triggered based on current city conditions.",
            factors=[
                {"factor": "rule_weight", "value": weight, "impact": "high"},
                {"factor": "context_match", "value": True, "impact": "high"},
            ],
            data_sources=["city_brain", "real_time_sensors", "historical_data"],
            confidence_breakdown={"rule_confidence": weight, "data_quality": 0.9},
            alternative_options=[],
            risk_assessment={
                "implementation_risk": "low",
                "resource_impact": "moderate",
                "public_impact": "positive",
            },
            historical_precedents=[],
        )

        return GovernanceDecision(
            decision_id=decision_id,
            domain=rule.domain,
            recommendation_type=RecommendationType.DEPLOYMENT,
            title=rule.name,
            description=f"Automated recommendation based on rule: {rule.name}",
            priority=priority,
            confidence=confidence,
            status=DecisionStatus.PENDING,
            recommended_action=rule.action_template.copy(),
            expected_impact={
                "efficiency_improvement": 0.15,
                "response_time_reduction": 0.10,
                "cost_impact": "neutral",
            },
            explanation=explanation,
            affected_resources=self._get_affected_resources(rule.domain),
            affected_zones=self._get_affected_zones(context),
            valid_from=now,
            valid_until=now + timedelta(hours=4),
        )

    def _create_decision_from_model(
        self,
        model: PolicyModel,
        context: dict[str, Any],
        score: float,
        contributions: dict[str, float],
    ) -> GovernanceDecision:
        """Create a governance decision from ML model prediction."""
        decision_id = f"dec-{uuid.uuid4().hex[:12]}"
        now = datetime.utcnow()

        priority = DecisionPriority.HIGH if score > 0.8 else (
            DecisionPriority.MEDIUM if score > 0.6 else DecisionPriority.LOW
        )
        confidence = ConfidenceLevel.VERY_HIGH if model.accuracy > 0.9 else (
            ConfidenceLevel.HIGH if model.accuracy > 0.8 else ConfidenceLevel.MEDIUM
        )

        factors = [
            {"factor": name, "value": value, "impact": "high" if abs(value) > 0.1 else "low"}
            for name, value in contributions.items()
        ]

        explanation = DecisionExplanation(
            explanation_id=f"exp-{uuid.uuid4().hex[:8]}",
            summary=f"ML model '{model.name}' recommends action with {score:.1%} confidence.",
            factors=factors,
            data_sources=["city_brain", "ml_model", "historical_patterns"],
            confidence_breakdown={
                "model_accuracy": model.accuracy,
                "prediction_score": score,
                "data_quality": 0.85,
            },
            alternative_options=[
                {"option": "no_action", "score": 1 - score},
                {"option": "partial_action", "score": score * 0.7},
            ],
            risk_assessment={
                "implementation_risk": "low" if score > 0.7 else "moderate",
                "resource_impact": "moderate",
                "public_impact": "positive",
            },
            historical_precedents=[
                {"date": (now - timedelta(days=30)).isoformat(), "outcome": "positive"},
            ],
        )

        action = self._generate_action_from_model(model, score)

        return GovernanceDecision(
            decision_id=decision_id,
            domain=model.domain,
            recommendation_type=RecommendationType.OPTIMIZATION,
            title=f"{model.name} Recommendation",
            description=f"ML-driven recommendation from {model.name} (v{model.version})",
            priority=priority,
            confidence=confidence,
            status=DecisionStatus.PENDING,
            recommended_action=action,
            expected_impact={
                "efficiency_improvement": score * 0.2,
                "response_time_reduction": score * 0.15,
                "cost_impact": "savings" if score > 0.7 else "neutral",
            },
            explanation=explanation,
            affected_resources=self._get_affected_resources(model.domain),
            affected_zones=self._get_affected_zones(context),
            valid_from=now,
            valid_until=now + timedelta(hours=6),
        )

    def _generate_action_from_model(self, model: PolicyModel, score: float) -> dict[str, Any]:
        """Generate action based on model domain and score."""
        if model.domain == DecisionDomain.PUBLIC_SAFETY:
            return {
                "action": "optimize_patrol_deployment",
                "rebalance_units": True,
                "priority_zones": ["downtown", "marina"],
                "intensity": "high" if score > 0.8 else "moderate",
            }
        elif model.domain == DecisionDomain.TRAFFIC_MOBILITY:
            return {
                "action": "optimize_traffic_flow",
                "signal_timing": True,
                "reroute_advisory": score > 0.7,
                "congestion_mitigation": True,
            }
        elif model.domain == DecisionDomain.RESOURCE_ALLOCATION:
            return {
                "action": "rebalance_resources",
                "optimize_coverage": True,
                "reduce_response_time": True,
                "cost_optimization": score > 0.6,
            }
        elif model.domain == DecisionDomain.EMERGENCY_SERVICES:
            return {
                "action": "optimize_emergency_response",
                "unit_repositioning": True,
                "mutual_aid_coordination": score > 0.8,
                "coverage_enhancement": True,
            }
        return {"action": "general_optimization", "score": score}

    def _get_affected_resources(self, domain: DecisionDomain) -> list[str]:
        """Get affected resources based on domain."""
        resource_map = {
            DecisionDomain.PUBLIC_SAFETY: ["police_units", "patrol_vehicles", "officers"],
            DecisionDomain.TRAFFIC_MOBILITY: ["traffic_signals", "message_boards", "traffic_units"],
            DecisionDomain.UTILITIES: ["utility_crews", "repair_equipment", "backup_generators"],
            DecisionDomain.PUBLIC_WORKS: ["maintenance_crews", "equipment", "materials"],
            DecisionDomain.STORM_RESPONSE: ["emergency_crews", "shelters", "evacuation_buses"],
            DecisionDomain.CROWD_MANAGEMENT: ["crowd_control_units", "barriers", "medical_teams"],
            DecisionDomain.EMERGENCY_SERVICES: ["fire_units", "ems_units", "rescue_equipment"],
            DecisionDomain.RESOURCE_ALLOCATION: ["all_units", "dispatch_system", "coordination"],
        }
        return resource_map.get(domain, ["general_resources"])

    def _get_affected_zones(self, context: dict[str, Any]) -> list[str]:
        """Get affected zones based on context."""
        zones = ["downtown", "marina", "singer_island", "westside", "industrial", "north"]
        if context.get("crime_risk", 0) > 0.5:
            return ["downtown", "westside"]
        if context.get("crowd_density", 0) > 0.5:
            return ["downtown", "marina"]
        if context.get("storm_probability", 0) > 0.3:
            return ["singer_island", "marina"]
        return zones[:3]

    def _deduplicate_decisions(self, decisions: list[GovernanceDecision]) -> list[GovernanceDecision]:
        """Remove duplicate decisions."""
        seen_domains = set()
        unique_decisions = []
        for decision in sorted(decisions, key=lambda d: d.priority.value, reverse=True):
            key = (decision.domain, decision.recommendation_type)
            if key not in seen_domains:
                seen_domains.add(key)
                unique_decisions.append(decision)
        return unique_decisions

    def _prioritize_decisions(self, decisions: list[GovernanceDecision]) -> list[GovernanceDecision]:
        """Sort decisions by priority."""
        return sorted(decisions, key=lambda d: (d.priority.value, d.confidence.value), reverse=True)

    def get_decision(self, decision_id: str) -> Optional[GovernanceDecision]:
        """Get a specific decision by ID."""
        return self._decisions.get(decision_id)

    def get_pending_decisions(self) -> list[GovernanceDecision]:
        """Get all pending decisions."""
        return [d for d in self._decisions.values() if d.status == DecisionStatus.PENDING]

    def get_decisions_by_domain(self, domain: DecisionDomain) -> list[GovernanceDecision]:
        """Get decisions for a specific domain."""
        return [d for d in self._decisions.values() if d.domain == domain]

    def approve_decision(self, decision_id: str, approved_by: str, notes: Optional[str] = None) -> bool:
        """Approve a pending decision."""
        decision = self._decisions.get(decision_id)
        if decision and decision.status == DecisionStatus.PENDING:
            decision.status = DecisionStatus.APPROVED
            decision.approved_by = approved_by
            decision.approved_at = datetime.utcnow()
            decision.implementation_notes = notes
            self._log_audit("decision_approved", decision_id, {"approved_by": approved_by})
            return True
        return False

    def reject_decision(self, decision_id: str, rejected_by: str, reason: str) -> bool:
        """Reject a pending decision."""
        decision = self._decisions.get(decision_id)
        if decision and decision.status == DecisionStatus.PENDING:
            decision.status = DecisionStatus.REJECTED
            decision.implementation_notes = f"Rejected by {rejected_by}: {reason}"
            self._log_audit("decision_rejected", decision_id, {"rejected_by": rejected_by, "reason": reason})
            return True
        return False

    def implement_decision(self, decision_id: str) -> bool:
        """Mark a decision as implemented."""
        decision = self._decisions.get(decision_id)
        if decision and decision.status == DecisionStatus.APPROVED:
            decision.status = DecisionStatus.IMPLEMENTED
            self._log_audit("decision_implemented", decision_id, {})
            return True
        return False

    def _log_audit(self, action: str, decision_id: str, details: dict[str, Any]):
        """Log an audit entry."""
        self._audit_log.append({
            "timestamp": datetime.utcnow().isoformat(),
            "action": action,
            "decision_id": decision_id,
            "details": details,
        })

    def get_audit_log(self, limit: int = 100) -> list[dict[str, Any]]:
        """Get recent audit log entries."""
        return self._audit_log[-limit:]

    def get_statistics(self) -> dict[str, Any]:
        """Get engine statistics."""
        total = len(self._decisions)
        by_status = {}
        by_domain = {}
        for decision in self._decisions.values():
            status = decision.status.value
            domain = decision.domain.value
            by_status[status] = by_status.get(status, 0) + 1
            by_domain[domain] = by_domain.get(domain, 0) + 1

        return {
            "total_decisions": total,
            "by_status": by_status,
            "by_domain": by_domain,
            "active_rules": len([r for r in self._rules.values() if r.enabled]),
            "policy_models": len(self._policy_models),
            "audit_log_entries": len(self._audit_log),
        }


_governance_engine: Optional[GovernanceDecisionEngine] = None


def get_governance_engine() -> GovernanceDecisionEngine:
    """Get the singleton governance decision engine instance."""
    global _governance_engine
    if _governance_engine is None:
        _governance_engine = GovernanceDecisionEngine()
    return _governance_engine
