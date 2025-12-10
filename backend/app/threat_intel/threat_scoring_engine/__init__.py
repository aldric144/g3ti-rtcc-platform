"""
Threat Scoring Engine Module

Provides capabilities for:
- 5-level threat scoring model
- Weighted ML rule engine
- Cross-domain fusion algorithm
- Alert trigger conditions
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Optional
import uuid


class ThreatLevel(Enum):
    """5-level threat scoring model"""
    LEVEL_1_MINIMAL = "level_1_minimal"
    LEVEL_2_LOW = "level_2_low"
    LEVEL_3_MODERATE = "level_3_moderate"
    LEVEL_4_HIGH = "level_4_high"
    LEVEL_5_CRITICAL = "level_5_critical"


class ThreatDomain(Enum):
    """Domains of threat intelligence"""
    DARK_WEB = "dark_web"
    OSINT = "osint"
    EXTREMIST_NETWORK = "extremist_network"
    GLOBAL_INCIDENT = "global_incident"
    LOCAL_CRIME = "local_crime"
    CYBER = "cyber"
    TERRORISM = "terrorism"
    GANG = "gang"
    DRUG = "drug"
    WEAPONS = "weapons"


class RuleType(Enum):
    """Types of scoring rules"""
    THRESHOLD = "threshold"
    PATTERN = "pattern"
    TEMPORAL = "temporal"
    GEOGRAPHIC = "geographic"
    ENTITY = "entity"
    COMPOSITE = "composite"
    ML_MODEL = "ml_model"


class TriggerAction(Enum):
    """Actions to take when trigger conditions are met"""
    ALERT = "alert"
    ESCALATE = "escalate"
    NOTIFY = "notify"
    LOG = "log"
    BLOCK = "block"
    INVESTIGATE = "investigate"
    MONITOR = "monitor"


class FusionMethod(Enum):
    """Methods for fusing scores from multiple domains"""
    WEIGHTED_AVERAGE = "weighted_average"
    MAX_SCORE = "max_score"
    BAYESIAN = "bayesian"
    ENSEMBLE = "ensemble"
    HIERARCHICAL = "hierarchical"


@dataclass
class ThreatScore:
    """A threat score for an entity or situation"""
    score_id: str = ""
    entity_id: str = ""
    entity_type: str = ""
    entity_name: str = ""
    overall_score: float = 0.0
    threat_level: ThreatLevel = ThreatLevel.LEVEL_1_MINIMAL
    domain_scores: dict[str, float] = field(default_factory=dict)
    contributing_factors: list[str] = field(default_factory=list)
    confidence: float = 0.0
    velocity: float = 0.0
    trend: str = "stable"
    jurisdiction_codes: list[str] = field(default_factory=list)
    calculated_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.score_id:
            self.score_id = f"score-{uuid.uuid4().hex[:12]}"


@dataclass
class ScoringRule:
    """A rule for calculating threat scores"""
    rule_id: str = ""
    name: str = ""
    description: str = ""
    rule_type: RuleType = RuleType.THRESHOLD
    domain: ThreatDomain = ThreatDomain.LOCAL_CRIME
    conditions: dict[str, Any] = field(default_factory=dict)
    score_contribution: float = 0.0
    weight: float = 1.0
    priority: int = 1
    enabled: bool = True
    trigger_actions: list[TriggerAction] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.rule_id:
            self.rule_id = f"rule-{uuid.uuid4().hex[:12]}"


@dataclass
class FusionResult:
    """Result of cross-domain threat fusion"""
    fusion_id: str = ""
    entity_id: str = ""
    entity_type: str = ""
    fusion_method: FusionMethod = FusionMethod.WEIGHTED_AVERAGE
    input_scores: list[ThreatScore] = field(default_factory=list)
    fused_score: float = 0.0
    fused_level: ThreatLevel = ThreatLevel.LEVEL_1_MINIMAL
    domain_weights: dict[str, float] = field(default_factory=dict)
    correlation_factors: list[str] = field(default_factory=list)
    amplification_factor: float = 1.0
    confidence: float = 0.0
    triggered_rules: list[str] = field(default_factory=list)
    triggered_actions: list[TriggerAction] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.fusion_id:
            self.fusion_id = f"fusion-{uuid.uuid4().hex[:12]}"


@dataclass
class TriggerCondition:
    """A condition that triggers an action"""
    condition_id: str = ""
    name: str = ""
    description: str = ""
    threshold_score: float = 0.0
    threshold_level: Optional[ThreatLevel] = None
    domains: list[ThreatDomain] = field(default_factory=list)
    entity_types: list[str] = field(default_factory=list)
    jurisdiction_codes: list[str] = field(default_factory=list)
    actions: list[TriggerAction] = field(default_factory=list)
    cooldown_minutes: int = 60
    last_triggered: Optional[datetime] = None
    trigger_count: int = 0
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        if not self.condition_id:
            self.condition_id = f"trigger-{uuid.uuid4().hex[:12]}"


@dataclass
class MLModel:
    """Configuration for an ML scoring model"""
    model_id: str = ""
    name: str = ""
    model_type: str = ""
    version: str = "1.0"
    domain: ThreatDomain = ThreatDomain.LOCAL_CRIME
    input_features: list[str] = field(default_factory=list)
    output_type: str = "score"
    accuracy: float = 0.0
    precision: float = 0.0
    recall: float = 0.0
    f1_score: float = 0.0
    trained_at: Optional[datetime] = None
    enabled: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.model_id:
            self.model_id = f"model-{uuid.uuid4().hex[:12]}"


class ThreatScoringEngine:
    """
    Threat Scoring Engine for calculating and fusing threat scores
    across multiple intelligence domains.
    """

    def __init__(self):
        self._scores: dict[str, ThreatScore] = {}
        self._rules: dict[str, ScoringRule] = {}
        self._triggers: dict[str, TriggerCondition] = {}
        self._fusions: dict[str, FusionResult] = {}
        self._models: dict[str, MLModel] = {}
        self._entity_scores: dict[str, list[str]] = {}
        self._callbacks: list[Callable[[Any], None]] = []
        self._events: list[dict[str, Any]] = []
        
        self._default_domain_weights = {
            ThreatDomain.DARK_WEB.value: 0.20,
            ThreatDomain.OSINT.value: 0.15,
            ThreatDomain.EXTREMIST_NETWORK.value: 0.20,
            ThreatDomain.GLOBAL_INCIDENT.value: 0.10,
            ThreatDomain.LOCAL_CRIME.value: 0.15,
            ThreatDomain.CYBER.value: 0.10,
            ThreatDomain.TERRORISM.value: 0.10,
        }
        
        self._level_thresholds = {
            ThreatLevel.LEVEL_1_MINIMAL: (0, 20),
            ThreatLevel.LEVEL_2_LOW: (20, 40),
            ThreatLevel.LEVEL_3_MODERATE: (40, 60),
            ThreatLevel.LEVEL_4_HIGH: (60, 80),
            ThreatLevel.LEVEL_5_CRITICAL: (80, 100),
        }

    def register_callback(self, callback: Callable[[Any], None]) -> None:
        """Register a callback for scoring events"""
        self._callbacks.append(callback)

    def _notify_callbacks(self, data: Any) -> None:
        """Notify all registered callbacks"""
        for callback in self._callbacks:
            try:
                callback(data)
            except Exception:
                pass

    def _record_event(self, event_type: str, data: dict[str, Any]) -> None:
        """Record an event for audit purposes"""
        self._events.append({
            "event_type": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data,
        })

    def _score_to_level(self, score: float) -> ThreatLevel:
        """Convert a numeric score to a threat level"""
        for level, (low, high) in self._level_thresholds.items():
            if low <= score < high:
                return level
        return ThreatLevel.LEVEL_5_CRITICAL if score >= 80 else ThreatLevel.LEVEL_1_MINIMAL

    def create_rule(
        self,
        name: str,
        rule_type: RuleType,
        domain: ThreatDomain,
        conditions: dict[str, Any],
        score_contribution: float,
        weight: float = 1.0,
        priority: int = 1,
        description: str = "",
        trigger_actions: Optional[list[TriggerAction]] = None,
    ) -> ScoringRule:
        """Create a scoring rule"""
        rule = ScoringRule(
            name=name,
            description=description,
            rule_type=rule_type,
            domain=domain,
            conditions=conditions,
            score_contribution=score_contribution,
            weight=weight,
            priority=priority,
            trigger_actions=trigger_actions or [],
        )
        
        self._rules[rule.rule_id] = rule
        self._record_event("rule_created", {"rule_id": rule.rule_id, "name": name})
        
        return rule

    def get_rule(self, rule_id: str) -> Optional[ScoringRule]:
        """Get a rule by ID"""
        return self._rules.get(rule_id)

    def get_all_rules(
        self,
        domain: Optional[ThreatDomain] = None,
        rule_type: Optional[RuleType] = None,
        enabled_only: bool = True,
    ) -> list[ScoringRule]:
        """Get all rules with optional filtering"""
        rules = list(self._rules.values())
        
        if domain:
            rules = [r for r in rules if r.domain == domain]
        if rule_type:
            rules = [r for r in rules if r.rule_type == rule_type]
        if enabled_only:
            rules = [r for r in rules if r.enabled]
        
        rules.sort(key=lambda r: r.priority)
        return rules

    def update_rule(
        self,
        rule_id: str,
        enabled: Optional[bool] = None,
        weight: Optional[float] = None,
        score_contribution: Optional[float] = None,
    ) -> bool:
        """Update a rule"""
        rule = self._rules.get(rule_id)
        if not rule:
            return False
        
        if enabled is not None:
            rule.enabled = enabled
        if weight is not None:
            rule.weight = weight
        if score_contribution is not None:
            rule.score_contribution = score_contribution
        
        rule.updated_at = datetime.utcnow()
        self._record_event("rule_updated", {"rule_id": rule_id})
        return True

    def delete_rule(self, rule_id: str) -> bool:
        """Delete a rule"""
        if rule_id in self._rules:
            del self._rules[rule_id]
            self._record_event("rule_deleted", {"rule_id": rule_id})
            return True
        return False

    def create_trigger(
        self,
        name: str,
        threshold_score: float,
        actions: list[TriggerAction],
        threshold_level: Optional[ThreatLevel] = None,
        domains: Optional[list[ThreatDomain]] = None,
        entity_types: Optional[list[str]] = None,
        jurisdiction_codes: Optional[list[str]] = None,
        cooldown_minutes: int = 60,
        description: str = "",
    ) -> TriggerCondition:
        """Create a trigger condition"""
        trigger = TriggerCondition(
            name=name,
            description=description,
            threshold_score=threshold_score,
            threshold_level=threshold_level,
            domains=domains or [],
            entity_types=entity_types or [],
            jurisdiction_codes=jurisdiction_codes or [],
            actions=actions,
            cooldown_minutes=cooldown_minutes,
        )
        
        self._triggers[trigger.condition_id] = trigger
        self._record_event("trigger_created", {
            "trigger_id": trigger.condition_id,
            "name": name,
        })
        
        return trigger

    def get_trigger(self, trigger_id: str) -> Optional[TriggerCondition]:
        """Get a trigger by ID"""
        return self._triggers.get(trigger_id)

    def get_all_triggers(self, enabled_only: bool = True) -> list[TriggerCondition]:
        """Get all triggers"""
        triggers = list(self._triggers.values())
        if enabled_only:
            triggers = [t for t in triggers if t.enabled]
        return triggers

    def register_ml_model(
        self,
        name: str,
        model_type: str,
        domain: ThreatDomain,
        input_features: list[str],
        version: str = "1.0",
        accuracy: float = 0.0,
    ) -> MLModel:
        """Register an ML model for scoring"""
        model = MLModel(
            name=name,
            model_type=model_type,
            domain=domain,
            input_features=input_features,
            version=version,
            accuracy=accuracy,
            trained_at=datetime.utcnow(),
        )
        
        self._models[model.model_id] = model
        self._record_event("model_registered", {
            "model_id": model.model_id,
            "name": name,
        })
        
        return model

    def get_model(self, model_id: str) -> Optional[MLModel]:
        """Get a model by ID"""
        return self._models.get(model_id)

    def get_all_models(self, domain: Optional[ThreatDomain] = None) -> list[MLModel]:
        """Get all models"""
        models = list(self._models.values())
        if domain:
            models = [m for m in models if m.domain == domain]
        return models

    def calculate_score(
        self,
        entity_id: str,
        entity_type: str,
        entity_name: str,
        domain_inputs: dict[str, dict[str, Any]],
        jurisdiction_codes: Optional[list[str]] = None,
    ) -> ThreatScore:
        """Calculate threat score for an entity"""
        domain_scores = {}
        contributing_factors = []
        total_weight = 0.0
        weighted_sum = 0.0
        
        for domain_str, inputs in domain_inputs.items():
            domain_score = self._calculate_domain_score(domain_str, inputs)
            domain_scores[domain_str] = domain_score
            
            weight = self._default_domain_weights.get(domain_str, 0.1)
            weighted_sum += domain_score * weight
            total_weight += weight
            
            if domain_score >= 50:
                contributing_factors.append(f"{domain_str}: {domain_score:.1f}")
        
        if total_weight > 0:
            overall_score = weighted_sum / total_weight
        else:
            overall_score = 0.0
        
        overall_score = self._apply_rules(entity_type, domain_scores, overall_score)
        overall_score = min(max(overall_score, 0), 100)
        
        threat_level = self._score_to_level(overall_score)
        
        velocity = 0.0
        trend = "stable"
        if entity_id in self._entity_scores:
            prev_score_ids = self._entity_scores[entity_id]
            if prev_score_ids:
                prev_score = self._scores.get(prev_score_ids[-1])
                if prev_score:
                    velocity = overall_score - prev_score.overall_score
                    if velocity > 5:
                        trend = "increasing"
                    elif velocity < -5:
                        trend = "decreasing"
        
        confidence = self._calculate_confidence(domain_inputs)
        
        score = ThreatScore(
            entity_id=entity_id,
            entity_type=entity_type,
            entity_name=entity_name,
            overall_score=overall_score,
            threat_level=threat_level,
            domain_scores=domain_scores,
            contributing_factors=contributing_factors,
            confidence=confidence,
            velocity=velocity,
            trend=trend,
            jurisdiction_codes=jurisdiction_codes or [],
        )
        
        self._scores[score.score_id] = score
        if entity_id not in self._entity_scores:
            self._entity_scores[entity_id] = []
        self._entity_scores[entity_id].append(score.score_id)
        
        self._record_event("score_calculated", {
            "score_id": score.score_id,
            "entity_id": entity_id,
            "overall_score": overall_score,
        })
        
        triggered_actions = self._check_triggers(score)
        if triggered_actions:
            self._notify_callbacks({
                "type": "trigger_activated",
                "score": score,
                "actions": triggered_actions,
            })
        
        return score

    def _calculate_domain_score(
        self,
        domain: str,
        inputs: dict[str, Any],
    ) -> float:
        """Calculate score for a specific domain"""
        score = 0.0
        
        if "signal_count" in inputs:
            score += min(inputs["signal_count"] * 5, 30)
        
        if "severity" in inputs:
            severity_scores = {
                "low": 10,
                "moderate": 25,
                "high": 50,
                "severe": 75,
                "critical": 100,
            }
            score += severity_scores.get(inputs["severity"], 0)
        
        if "confidence" in inputs:
            score *= inputs["confidence"]
        
        if "threat_indicators" in inputs:
            score += len(inputs["threat_indicators"]) * 3
        
        if "risk_score" in inputs:
            score = max(score, inputs["risk_score"])
        
        return min(score, 100)

    def _apply_rules(
        self,
        entity_type: str,
        domain_scores: dict[str, float],
        base_score: float,
    ) -> float:
        """Apply scoring rules to adjust the base score"""
        adjusted_score = base_score
        
        for rule in self._rules.values():
            if not rule.enabled:
                continue
            
            if rule.rule_type == RuleType.THRESHOLD:
                threshold = rule.conditions.get("threshold", 0)
                domain_score = domain_scores.get(rule.domain.value, 0)
                if domain_score >= threshold:
                    adjusted_score += rule.score_contribution * rule.weight
            
            elif rule.rule_type == RuleType.COMPOSITE:
                required_domains = rule.conditions.get("required_domains", [])
                min_score = rule.conditions.get("min_score", 50)
                matching = sum(
                    1 for d in required_domains
                    if domain_scores.get(d, 0) >= min_score
                )
                if matching >= len(required_domains):
                    adjusted_score += rule.score_contribution * rule.weight
            
            elif rule.rule_type == RuleType.PATTERN:
                pattern_domains = rule.conditions.get("pattern_domains", [])
                if all(domain_scores.get(d, 0) > 0 for d in pattern_domains):
                    adjusted_score += rule.score_contribution * rule.weight
        
        return adjusted_score

    def _calculate_confidence(self, domain_inputs: dict[str, dict[str, Any]]) -> float:
        """Calculate confidence score based on input quality"""
        if not domain_inputs:
            return 0.0
        
        total_confidence = 0.0
        count = 0
        
        for inputs in domain_inputs.values():
            if "confidence" in inputs:
                total_confidence += inputs["confidence"]
                count += 1
            elif "signal_count" in inputs:
                total_confidence += min(inputs["signal_count"] / 10, 1.0)
                count += 1
        
        if count > 0:
            base_confidence = total_confidence / count
        else:
            base_confidence = 0.5
        
        domain_coverage = len(domain_inputs) / len(self._default_domain_weights)
        
        return min(base_confidence * (0.5 + 0.5 * domain_coverage), 1.0)

    def _check_triggers(self, score: ThreatScore) -> list[TriggerAction]:
        """Check if any triggers should be activated"""
        triggered_actions = []
        now = datetime.utcnow()
        
        for trigger in self._triggers.values():
            if not trigger.enabled:
                continue
            
            if trigger.last_triggered:
                cooldown_elapsed = (now - trigger.last_triggered).total_seconds() / 60
                if cooldown_elapsed < trigger.cooldown_minutes:
                    continue
            
            if score.overall_score < trigger.threshold_score:
                continue
            
            if trigger.threshold_level and score.threat_level != trigger.threshold_level:
                continue
            
            if trigger.entity_types and score.entity_type not in trigger.entity_types:
                continue
            
            if trigger.jurisdiction_codes:
                if not any(j in score.jurisdiction_codes for j in trigger.jurisdiction_codes):
                    continue
            
            trigger.last_triggered = now
            trigger.trigger_count += 1
            triggered_actions.extend(trigger.actions)
            
            self._record_event("trigger_activated", {
                "trigger_id": trigger.condition_id,
                "score_id": score.score_id,
                "actions": [a.value for a in trigger.actions],
            })
        
        return list(set(triggered_actions))

    def fuse_scores(
        self,
        entity_id: str,
        entity_type: str,
        scores: list[ThreatScore],
        method: FusionMethod = FusionMethod.WEIGHTED_AVERAGE,
        custom_weights: Optional[dict[str, float]] = None,
    ) -> FusionResult:
        """Fuse multiple threat scores into a single result"""
        if not scores:
            return FusionResult(
                entity_id=entity_id,
                entity_type=entity_type,
                fusion_method=method,
            )
        
        domain_weights = custom_weights or self._default_domain_weights
        
        if method == FusionMethod.WEIGHTED_AVERAGE:
            fused_score = self._weighted_average_fusion(scores, domain_weights)
        elif method == FusionMethod.MAX_SCORE:
            fused_score = max(s.overall_score for s in scores)
        elif method == FusionMethod.BAYESIAN:
            fused_score = self._bayesian_fusion(scores)
        elif method == FusionMethod.ENSEMBLE:
            fused_score = self._ensemble_fusion(scores, domain_weights)
        else:
            fused_score = sum(s.overall_score for s in scores) / len(scores)
        
        amplification = self._calculate_amplification(scores)
        fused_score = min(fused_score * amplification, 100)
        
        fused_level = self._score_to_level(fused_score)
        
        correlation_factors = []
        for i, s1 in enumerate(scores):
            for s2 in scores[i+1:]:
                if s1.entity_id == s2.entity_id:
                    correlation_factors.append(f"Same entity across domains")
                    break
        
        confidence = sum(s.confidence for s in scores) / len(scores)
        
        triggered_rules = []
        triggered_actions = []
        for rule in self._rules.values():
            if rule.enabled and rule.rule_type == RuleType.COMPOSITE:
                triggered_rules.append(rule.rule_id)
                triggered_actions.extend(rule.trigger_actions)
        
        fusion = FusionResult(
            entity_id=entity_id,
            entity_type=entity_type,
            fusion_method=method,
            input_scores=scores,
            fused_score=fused_score,
            fused_level=fused_level,
            domain_weights=domain_weights,
            correlation_factors=correlation_factors,
            amplification_factor=amplification,
            confidence=confidence,
            triggered_rules=triggered_rules,
            triggered_actions=list(set(triggered_actions)),
        )
        
        self._fusions[fusion.fusion_id] = fusion
        self._record_event("scores_fused", {
            "fusion_id": fusion.fusion_id,
            "entity_id": entity_id,
            "fused_score": fused_score,
        })
        
        return fusion

    def _weighted_average_fusion(
        self,
        scores: list[ThreatScore],
        weights: dict[str, float],
    ) -> float:
        """Fuse scores using weighted average"""
        total_weight = 0.0
        weighted_sum = 0.0
        
        for score in scores:
            for domain, domain_score in score.domain_scores.items():
                weight = weights.get(domain, 0.1)
                weighted_sum += domain_score * weight
                total_weight += weight
        
        if total_weight > 0:
            return weighted_sum / total_weight
        return 0.0

    def _bayesian_fusion(self, scores: list[ThreatScore]) -> float:
        """Fuse scores using Bayesian approach"""
        prior = 0.5
        
        for score in scores:
            likelihood = score.overall_score / 100
            confidence = score.confidence
            
            posterior = (likelihood * prior) / (
                likelihood * prior + (1 - likelihood) * (1 - prior)
            )
            
            prior = prior * (1 - confidence) + posterior * confidence
        
        return prior * 100

    def _ensemble_fusion(
        self,
        scores: list[ThreatScore],
        weights: dict[str, float],
    ) -> float:
        """Fuse scores using ensemble method"""
        weighted_avg = self._weighted_average_fusion(scores, weights)
        max_score = max(s.overall_score for s in scores)
        bayesian = self._bayesian_fusion(scores)
        
        return (weighted_avg * 0.4 + max_score * 0.3 + bayesian * 0.3)

    def _calculate_amplification(self, scores: list[ThreatScore]) -> float:
        """Calculate amplification factor based on correlations"""
        amplification = 1.0
        
        if len(scores) >= 3:
            amplification += 0.1
        if len(scores) >= 5:
            amplification += 0.1
        
        high_scores = sum(1 for s in scores if s.overall_score >= 60)
        if high_scores >= 2:
            amplification += 0.15
        
        return min(amplification, 2.0)

    def get_score(self, score_id: str) -> Optional[ThreatScore]:
        """Get a score by ID"""
        return self._scores.get(score_id)

    def get_scores_for_entity(
        self,
        entity_id: str,
        limit: int = 10,
    ) -> list[ThreatScore]:
        """Get all scores for an entity"""
        score_ids = self._entity_scores.get(entity_id, [])
        scores = [self._scores[sid] for sid in score_ids if sid in self._scores]
        scores.sort(key=lambda s: s.calculated_at, reverse=True)
        return scores[:limit]

    def get_high_threat_scores(
        self,
        min_level: ThreatLevel = ThreatLevel.LEVEL_4_HIGH,
        limit: int = 50,
    ) -> list[ThreatScore]:
        """Get high threat scores"""
        level_order = [
            ThreatLevel.LEVEL_1_MINIMAL,
            ThreatLevel.LEVEL_2_LOW,
            ThreatLevel.LEVEL_3_MODERATE,
            ThreatLevel.LEVEL_4_HIGH,
            ThreatLevel.LEVEL_5_CRITICAL,
        ]
        min_index = level_order.index(min_level)
        
        high_scores = [
            s for s in self._scores.values()
            if level_order.index(s.threat_level) >= min_index
        ]
        high_scores.sort(key=lambda s: s.overall_score, reverse=True)
        return high_scores[:limit]

    def get_fusion(self, fusion_id: str) -> Optional[FusionResult]:
        """Get a fusion result by ID"""
        return self._fusions.get(fusion_id)

    def get_metrics(self) -> dict[str, Any]:
        """Get threat scoring engine metrics"""
        scores = list(self._scores.values())
        
        level_counts = {}
        for level in ThreatLevel:
            level_counts[level.value] = len([
                s for s in scores if s.threat_level == level
            ])
        
        domain_avg_scores = {}
        for domain in ThreatDomain:
            domain_scores = []
            for score in scores:
                if domain.value in score.domain_scores:
                    domain_scores.append(score.domain_scores[domain.value])
            if domain_scores:
                domain_avg_scores[domain.value] = sum(domain_scores) / len(domain_scores)
        
        return {
            "total_scores": len(scores),
            "total_rules": len(self._rules),
            "total_triggers": len(self._triggers),
            "total_fusions": len(self._fusions),
            "total_models": len(self._models),
            "scores_by_level": level_counts,
            "domain_average_scores": domain_avg_scores,
            "active_rules": len([r for r in self._rules.values() if r.enabled]),
            "active_triggers": len([t for t in self._triggers.values() if t.enabled]),
            "total_trigger_activations": sum(t.trigger_count for t in self._triggers.values()),
            "total_events": len(self._events),
        }
