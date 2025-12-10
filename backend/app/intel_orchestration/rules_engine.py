"""
Rules Engine for G3TI RTCC-UIP.

This module provides priority scoring and threat assessment capabilities
using configurable rulesets.
"""

import logging
from collections.abc import Callable
from datetime import UTC, datetime
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class RuleCategory(str, Enum):
    """Categories of scoring rules."""
    ENGINE_CONFIDENCE = "engine_confidence"
    ENTITY_RISK = "entity_risk"
    LOCATION_RISK = "location_risk"
    INTEL_CATEGORY = "intel_category"
    OFFICER_SAFETY = "officer_safety"
    FEDERAL_MATCH = "federal_match"
    HISTORICAL_TREND = "historical_trend"
    TEMPORAL = "temporal"
    PATTERN = "pattern"
    CUSTOM = "custom"


class RuleOperator(str, Enum):
    """Operators for rule conditions."""
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    GREATER_OR_EQUAL = "greater_or_equal"
    LESS_OR_EQUAL = "less_or_equal"
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    IN = "in"
    NOT_IN = "not_in"
    EXISTS = "exists"
    NOT_EXISTS = "not_exists"
    MATCHES = "matches"


class ThreatLevel(str, Enum):
    """Threat level classification."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    MINIMAL = "minimal"


class ScoringRule(BaseModel):
    """A rule for calculating priority scores."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    description: str = ""
    category: RuleCategory
    enabled: bool = True
    priority: int = 5  # Rule evaluation priority (1-10)
    conditions: list[dict[str, Any]] = Field(default_factory=list)
    score_modifier: float = 0.0  # Added to base score
    score_multiplier: float = 1.0  # Multiplied with current score
    max_contribution: float = 100.0  # Maximum score contribution
    min_contribution: float = 0.0  # Minimum score contribution
    metadata: dict[str, Any] = Field(default_factory=dict)


class RuleCondition(BaseModel):
    """A condition within a rule."""
    field: str
    operator: RuleOperator
    value: Any
    case_sensitive: bool = False


class PriorityScore(BaseModel):
    """Result of priority scoring."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    entity_id: str
    total_score: float = Field(ge=0.0, le=100.0)
    base_score: float = 0.0
    rule_contributions: dict[str, float] = Field(default_factory=dict)
    rules_applied: list[str] = Field(default_factory=list)
    threat_level: ThreatLevel
    confidence: float = Field(ge=0.0, le=1.0)
    factors: list[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


class RiskProfile(BaseModel):
    """Risk profile for an entity."""
    entity_id: str
    entity_type: str
    risk_score: float = Field(ge=0.0, le=100.0)
    risk_level: ThreatLevel
    risk_factors: list[dict[str, Any]] = Field(default_factory=list)
    historical_scores: list[float] = Field(default_factory=list)
    trend: str = "stable"  # increasing, decreasing, stable
    last_updated: datetime = Field(default_factory=lambda: datetime.now(UTC))
    metadata: dict[str, Any] = Field(default_factory=dict)


class ThreatAssessment(BaseModel):
    """Comprehensive threat assessment."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    entity_id: str
    threat_level: ThreatLevel
    priority_score: float
    risk_profile: RiskProfile | None = None
    contributing_factors: list[str] = Field(default_factory=list)
    mitigating_factors: list[str] = Field(default_factory=list)
    recommended_actions: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)
    valid_until: datetime | None = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


class RulesEngineConfig(BaseModel):
    """Configuration for the rules engine."""
    enabled: bool = True
    default_base_score: float = 50.0
    min_score: float = 0.0
    max_score: float = 100.0
    enable_caching: bool = True
    cache_ttl_seconds: int = 60
    parallel_evaluation: bool = True


class RulesEngine:
    """
    Priority scoring and threat assessment engine.

    Evaluates intelligence signals against configurable rulesets to
    calculate priority scores and threat assessments.
    """

    def __init__(self, config: RulesEngineConfig | None = None):
        self.config = config or RulesEngineConfig()
        self._rules: dict[str, ScoringRule] = {}
        self._custom_evaluators: dict[str, Callable] = {}
        self._score_cache: dict[str, PriorityScore] = {}
        self._risk_profiles: dict[str, RiskProfile] = {}

        # Initialize default rules
        self._initialize_default_rules()

        logger.info("RulesEngine initialized")

    def _initialize_default_rules(self):
        """Initialize default scoring rules."""
        default_rules = [
            # Engine confidence rules
            ScoringRule(
                name="high_ai_confidence",
                description="High confidence from AI engine",
                category=RuleCategory.ENGINE_CONFIDENCE,
                conditions=[
                    {"field": "source", "operator": "equals", "value": "ai_engine"},
                    {"field": "confidence", "operator": "greater_or_equal", "value": 0.9},
                ],
                score_modifier=15.0,
            ),
            ScoringRule(
                name="tactical_engine_signal",
                description="Signal from tactical analytics engine",
                category=RuleCategory.ENGINE_CONFIDENCE,
                conditions=[
                    {"field": "source", "operator": "equals", "value": "tactical_engine"},
                ],
                score_modifier=10.0,
            ),

            # Entity risk rules
            ScoringRule(
                name="known_offender",
                description="Entity is a known repeat offender",
                category=RuleCategory.ENTITY_RISK,
                conditions=[
                    {"field": "entity.is_repeat_offender", "operator": "equals", "value": True},
                ],
                score_modifier=20.0,
            ),
            ScoringRule(
                name="high_risk_entity",
                description="Entity has high risk score",
                category=RuleCategory.ENTITY_RISK,
                conditions=[
                    {"field": "entity.risk_score", "operator": "greater_or_equal", "value": 80},
                ],
                score_modifier=25.0,
            ),

            # Location risk rules
            ScoringRule(
                name="high_crime_area",
                description="Location is in high crime area",
                category=RuleCategory.LOCATION_RISK,
                conditions=[
                    {"field": "location.crime_index", "operator": "greater_or_equal", "value": 0.8},
                ],
                score_modifier=10.0,
            ),
            ScoringRule(
                name="school_zone",
                description="Location is near a school",
                category=RuleCategory.LOCATION_RISK,
                conditions=[
                    {"field": "location.near_school", "operator": "equals", "value": True},
                ],
                score_modifier=15.0,
            ),

            # Officer safety rules
            ScoringRule(
                name="officer_safety_threat",
                description="Direct threat to officer safety",
                category=RuleCategory.OFFICER_SAFETY,
                priority=10,
                conditions=[
                    {"field": "category", "operator": "equals", "value": "officer_safety"},
                ],
                score_modifier=40.0,
            ),
            ScoringRule(
                name="weapon_involved",
                description="Weapon is involved",
                category=RuleCategory.OFFICER_SAFETY,
                priority=9,
                conditions=[
                    {"field": "weapon_involved", "operator": "equals", "value": True},
                ],
                score_modifier=25.0,
            ),

            # Federal match rules
            ScoringRule(
                name="ncic_hit",
                description="NCIC database hit",
                category=RuleCategory.FEDERAL_MATCH,
                priority=8,
                conditions=[
                    {"field": "federal_matches.ncic", "operator": "exists", "value": True},
                ],
                score_modifier=30.0,
            ),
            ScoringRule(
                name="ndex_match",
                description="N-DEx database match",
                category=RuleCategory.FEDERAL_MATCH,
                conditions=[
                    {"field": "federal_matches.ndex", "operator": "exists", "value": True},
                ],
                score_modifier=20.0,
            ),

            # Historical trend rules
            ScoringRule(
                name="escalating_pattern",
                description="Entity shows escalating behavior pattern",
                category=RuleCategory.HISTORICAL_TREND,
                conditions=[
                    {"field": "historical.trend", "operator": "equals", "value": "escalating"},
                ],
                score_modifier=15.0,
            ),

            # Temporal rules
            ScoringRule(
                name="recent_activity",
                description="Recent related activity detected",
                category=RuleCategory.TEMPORAL,
                conditions=[
                    {"field": "temporal.recent_incidents", "operator": "greater_than", "value": 0},
                ],
                score_modifier=10.0,
            ),
        ]

        for rule in default_rules:
            self._rules[rule.id] = rule

    async def calculate_priority(self, signal: Any) -> float:
        """
        Calculate priority score for a signal.

        Returns score from 0-100.
        """
        if not self.config.enabled:
            return self.config.default_base_score

        # Extract signal data
        signal_data = self._extract_signal_data(signal)

        # Check cache
        cache_key = self._get_cache_key(signal_data)
        if self.config.enable_caching and cache_key in self._score_cache:
            cached = self._score_cache[cache_key]
            return cached.total_score

        # Calculate score
        priority_score = await self._evaluate_rules(signal_data)

        # Cache result
        if self.config.enable_caching:
            self._score_cache[cache_key] = priority_score

        return priority_score.total_score

    def _extract_signal_data(self, signal: Any) -> dict[str, Any]:
        """Extract data from signal for rule evaluation."""
        if isinstance(signal, dict):
            return signal

        if hasattr(signal, "data"):
            data = signal.data if isinstance(signal.data, dict) else {}
        else:
            data = {}

        # Add signal attributes
        if hasattr(signal, "source"):
            data["source"] = signal.source.value if hasattr(signal.source, "value") else str(signal.source)
        if hasattr(signal, "category"):
            data["category"] = signal.category.value if hasattr(signal.category, "value") else str(signal.category)
        if hasattr(signal, "confidence"):
            data["confidence"] = signal.confidence
        if hasattr(signal, "jurisdiction"):
            data["jurisdiction"] = signal.jurisdiction
        if hasattr(signal, "priority_modifiers"):
            data["priority_modifiers"] = signal.priority_modifiers

        return data

    def _get_cache_key(self, data: dict[str, Any]) -> str:
        """Generate cache key from signal data."""
        import hashlib
        import json

        # Create deterministic string representation
        key_data = {
            "source": data.get("source"),
            "category": data.get("category"),
            "entity_id": data.get("entity", {}).get("id") if isinstance(data.get("entity"), dict) else None,
        }
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_str.encode()).hexdigest()

    async def _evaluate_rules(self, data: dict[str, Any]) -> PriorityScore:
        """Evaluate all rules against signal data."""
        base_score = self.config.default_base_score
        total_score = base_score
        rule_contributions: dict[str, float] = {}
        rules_applied: list[str] = []
        factors: list[str] = []

        # Sort rules by priority
        sorted_rules = sorted(
            self._rules.values(),
            key=lambda r: r.priority,
            reverse=True,
        )

        for rule in sorted_rules:
            if not rule.enabled:
                continue

            # Evaluate rule conditions
            if self._evaluate_conditions(rule.conditions, data):
                # Calculate contribution
                contribution = rule.score_modifier

                # Apply multiplier if set
                if rule.score_multiplier != 1.0:
                    contribution = total_score * (rule.score_multiplier - 1.0)

                # Clamp contribution
                contribution = max(
                    rule.min_contribution,
                    min(rule.max_contribution, contribution),
                )

                total_score += contribution
                rule_contributions[rule.id] = contribution
                rules_applied.append(rule.name)
                factors.append(rule.description)

        # Evaluate custom evaluators
        for name, evaluator in self._custom_evaluators.items():
            try:
                custom_score = await evaluator(data)
                if custom_score:
                    total_score += custom_score
                    rule_contributions[f"custom_{name}"] = custom_score
                    factors.append(f"Custom: {name}")
            except Exception as e:
                logger.error("Custom evaluator %s failed: %s", name, e)

        # Clamp final score
        total_score = max(
            self.config.min_score,
            min(self.config.max_score, total_score),
        )

        # Determine threat level
        threat_level = self._get_threat_level(total_score)

        # Calculate confidence based on rules applied
        confidence = min(1.0, len(rules_applied) / 5.0) if rules_applied else 0.5

        return PriorityScore(
            entity_id=data.get("entity", {}).get("id", "unknown"),
            total_score=total_score,
            base_score=base_score,
            rule_contributions=rule_contributions,
            rules_applied=rules_applied,
            threat_level=threat_level,
            confidence=confidence,
            factors=factors,
        )

    def _evaluate_conditions(
        self, conditions: list[dict[str, Any]], data: dict[str, Any]
    ) -> bool:
        """Evaluate all conditions (AND logic)."""
        if not conditions:
            return True

        for condition in conditions:
            if not self._evaluate_condition(condition, data):
                return False

        return True

    def _evaluate_condition(
        self, condition: dict[str, Any], data: dict[str, Any]
    ) -> bool:
        """Evaluate a single condition."""
        field = condition.get("field", "")
        operator = condition.get("operator", "equals")
        expected = condition.get("value")

        # Get actual value from data (supports nested fields)
        actual = self._get_nested_value(data, field)

        # Evaluate based on operator
        if operator == "equals":
            return actual == expected
        elif operator == "not_equals":
            return actual != expected
        elif operator == "greater_than":
            return actual is not None and actual > expected
        elif operator == "less_than":
            return actual is not None and actual < expected
        elif operator == "greater_or_equal":
            return actual is not None and actual >= expected
        elif operator == "less_or_equal":
            return actual is not None and actual <= expected
        elif operator == "contains":
            return expected in actual if actual else False
        elif operator == "not_contains":
            return expected not in actual if actual else True
        elif operator == "in":
            return actual in expected if expected else False
        elif operator == "not_in":
            return actual not in expected if expected else True
        elif operator == "exists":
            return actual is not None
        elif operator == "not_exists":
            return actual is None

        return False

    def _get_nested_value(self, data: dict[str, Any], field: str) -> Any:
        """Get value from nested dictionary using dot notation."""
        parts = field.split(".")
        value = data

        for part in parts:
            if isinstance(value, dict):
                value = value.get(part)
            else:
                return None

        return value

    def _get_threat_level(self, score: float) -> ThreatLevel:
        """Get threat level from score."""
        if score >= 85:
            return ThreatLevel.CRITICAL
        elif score >= 70:
            return ThreatLevel.HIGH
        elif score >= 50:
            return ThreatLevel.MEDIUM
        elif score >= 30:
            return ThreatLevel.LOW
        return ThreatLevel.MINIMAL

    async def assess_threat(
        self, entity_id: str, signal_data: dict[str, Any]
    ) -> ThreatAssessment:
        """Generate comprehensive threat assessment for an entity."""
        # Calculate priority score
        priority_score = await self._evaluate_rules(signal_data)

        # Get or create risk profile
        risk_profile = await self.get_risk_profile(entity_id)
        if not risk_profile:
            risk_profile = await self.create_risk_profile(entity_id, signal_data)

        # Update risk profile with new score
        risk_profile.historical_scores.append(priority_score.total_score)
        risk_profile.risk_score = priority_score.total_score
        risk_profile.risk_level = priority_score.threat_level
        risk_profile.last_updated = datetime.now(UTC)

        # Determine trend
        if len(risk_profile.historical_scores) >= 3:
            recent = risk_profile.historical_scores[-3:]
            if recent[-1] > recent[0]:
                risk_profile.trend = "increasing"
            elif recent[-1] < recent[0]:
                risk_profile.trend = "decreasing"
            else:
                risk_profile.trend = "stable"

        # Generate recommendations
        recommendations = self._generate_recommendations(priority_score)

        return ThreatAssessment(
            entity_id=entity_id,
            threat_level=priority_score.threat_level,
            priority_score=priority_score.total_score,
            risk_profile=risk_profile,
            contributing_factors=priority_score.factors,
            mitigating_factors=[],
            recommended_actions=recommendations,
            confidence=priority_score.confidence,
        )

    def _generate_recommendations(self, score: PriorityScore) -> list[str]:
        """Generate recommended actions based on score."""
        recommendations = []

        if score.threat_level == ThreatLevel.CRITICAL:
            recommendations.extend([
                "Immediate dispatch notification required",
                "Alert all units in vicinity",
                "Activate real-time tracking",
                "Notify command center",
            ])
        elif score.threat_level == ThreatLevel.HIGH:
            recommendations.extend([
                "Priority investigation assignment",
                "Enhanced surveillance recommended",
                "Cross-reference with active cases",
            ])
        elif score.threat_level == ThreatLevel.MEDIUM:
            recommendations.extend([
                "Add to active monitoring list",
                "Schedule follow-up analysis",
            ])
        else:
            recommendations.append("Archive for future reference")

        return recommendations

    async def get_risk_profile(self, entity_id: str) -> RiskProfile | None:
        """Get risk profile for an entity."""
        return self._risk_profiles.get(entity_id)

    async def create_risk_profile(
        self, entity_id: str, data: dict[str, Any]
    ) -> RiskProfile:
        """Create a new risk profile for an entity."""
        profile = RiskProfile(
            entity_id=entity_id,
            entity_type=data.get("entity_type", "unknown"),
            risk_score=self.config.default_base_score,
            risk_level=ThreatLevel.MEDIUM,
        )
        self._risk_profiles[entity_id] = profile
        return profile

    def add_rule(self, rule: ScoringRule):
        """Add a scoring rule."""
        self._rules[rule.id] = rule
        logger.info("Added rule: %s", rule.name)

    def remove_rule(self, rule_id: str):
        """Remove a scoring rule."""
        if rule_id in self._rules:
            del self._rules[rule_id]
            logger.info("Removed rule: %s", rule_id)

    def enable_rule(self, rule_id: str):
        """Enable a rule."""
        if rule_id in self._rules:
            self._rules[rule_id].enabled = True

    def disable_rule(self, rule_id: str):
        """Disable a rule."""
        if rule_id in self._rules:
            self._rules[rule_id].enabled = False

    def register_custom_evaluator(self, name: str, evaluator: Callable):
        """Register a custom score evaluator."""
        self._custom_evaluators[name] = evaluator

    def get_rules(self) -> list[ScoringRule]:
        """Get all rules."""
        return list(self._rules.values())

    def get_rule(self, rule_id: str) -> ScoringRule | None:
        """Get a specific rule."""
        return self._rules.get(rule_id)

    def clear_cache(self):
        """Clear score cache."""
        self._score_cache.clear()

    def get_stats(self) -> dict[str, Any]:
        """Get rules engine statistics."""
        return {
            "total_rules": len(self._rules),
            "enabled_rules": sum(1 for r in self._rules.values() if r.enabled),
            "custom_evaluators": len(self._custom_evaluators),
            "cached_scores": len(self._score_cache),
            "risk_profiles": len(self._risk_profiles),
            "config": self.config.model_dump(),
        }
