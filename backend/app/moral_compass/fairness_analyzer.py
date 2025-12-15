"""
Fairness & Bias Analyzer

Phase 35: AI Moral Compass & Societal Ethics Reasoning Engine
Evaluates AI suggestions against fairness metrics and detects bias.
"""

import hashlib
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class FairnessMetric(Enum):
    """Types of fairness metrics."""
    DEMOGRAPHIC_PARITY = "demographic_parity"
    EQUALIZED_ODDS = "equalized_odds"
    EQUAL_OPPORTUNITY = "equal_opportunity"
    PREDICTIVE_PARITY = "predictive_parity"
    CALIBRATION = "calibration"
    INDIVIDUAL_FAIRNESS = "individual_fairness"
    COUNTERFACTUAL_FAIRNESS = "counterfactual_fairness"


class BiasType(Enum):
    """Types of bias."""
    SELECTION = "selection"
    MEASUREMENT = "measurement"
    ALGORITHMIC = "algorithmic"
    HISTORICAL = "historical"
    REPRESENTATION = "representation"
    AGGREGATION = "aggregation"
    EVALUATION = "evaluation"
    DEPLOYMENT = "deployment"


class DisparityLevel(Enum):
    """Levels of disparity."""
    NONE = "none"
    MINIMAL = "minimal"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    SEVERE = "severe"


class ProtectedAttribute(Enum):
    """Protected attributes for fairness analysis."""
    RACE = "race"
    ETHNICITY = "ethnicity"
    GENDER = "gender"
    AGE = "age"
    RELIGION = "religion"
    DISABILITY = "disability"
    NATIONAL_ORIGIN = "national_origin"
    SOCIOECONOMIC = "socioeconomic"
    GEOGRAPHIC = "geographic"


@dataclass
class FairnessScore:
    """Fairness score for a specific metric."""
    metric: FairnessMetric = FairnessMetric.DEMOGRAPHIC_PARITY
    score: float = 1.0
    threshold: float = 0.8
    passed: bool = True
    details: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "metric": self.metric.value,
            "score": self.score,
            "threshold": self.threshold,
            "passed": self.passed,
            "details": self.details,
        }


@dataclass
class DisparityAlert:
    """Alert for detected disparity."""
    alert_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    disparity_type: str = ""
    protected_attribute: ProtectedAttribute = ProtectedAttribute.RACE
    disparity_level: DisparityLevel = DisparityLevel.NONE
    affected_groups: List[str] = field(default_factory=list)
    disparity_ratio: float = 1.0
    description: str = ""
    recommendations: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    acknowledged: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "alert_id": self.alert_id,
            "disparity_type": self.disparity_type,
            "protected_attribute": self.protected_attribute.value,
            "disparity_level": self.disparity_level.value,
            "affected_groups": self.affected_groups,
            "disparity_ratio": self.disparity_ratio,
            "description": self.description,
            "recommendations": self.recommendations,
            "created_at": self.created_at.isoformat(),
            "acknowledged": self.acknowledged,
        }


@dataclass
class BiasDetection:
    """Result of bias detection."""
    detection_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    bias_type: BiasType = BiasType.ALGORITHMIC
    detected: bool = False
    confidence: float = 0.0
    source: str = ""
    impact: str = ""
    mitigation_strategies: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "detection_id": self.detection_id,
            "bias_type": self.bias_type.value,
            "detected": self.detected,
            "confidence": self.confidence,
            "source": self.source,
            "impact": self.impact,
            "mitigation_strategies": self.mitigation_strategies,
        }


@dataclass
class FairnessAssessment:
    """Complete fairness assessment."""
    assessment_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    action_type: str = ""
    requester_id: str = ""
    fairness_scores: List[FairnessScore] = field(default_factory=list)
    bias_detections: List[BiasDetection] = field(default_factory=list)
    disparity_alerts: List[DisparityAlert] = field(default_factory=list)
    overall_fairness_score: float = 1.0
    passed: bool = True
    requires_review: bool = False
    recommendations: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    assessment_hash: str = ""
    
    def __post_init__(self):
        if not self.assessment_hash:
            self.assessment_hash = self._compute_hash()
    
    def _compute_hash(self) -> str:
        content = f"{self.assessment_id}:{self.action_type}:{self.overall_fairness_score}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "assessment_id": self.assessment_id,
            "action_type": self.action_type,
            "requester_id": self.requester_id,
            "fairness_scores": [s.to_dict() for s in self.fairness_scores],
            "bias_detections": [b.to_dict() for b in self.bias_detections],
            "disparity_alerts": [a.to_dict() for a in self.disparity_alerts],
            "overall_fairness_score": self.overall_fairness_score,
            "passed": self.passed,
            "requires_review": self.requires_review,
            "recommendations": self.recommendations,
            "created_at": self.created_at.isoformat(),
            "assessment_hash": self.assessment_hash,
        }


class FairnessAnalyzer:
    """
    Fairness & Bias Analyzer.
    
    Evaluates AI suggestions against fairness metrics,
    detects bias, and ensures equitable outcomes.
    
    Note: This module does NOT perform demographic prediction.
    It only safeguards fairness in AI outputs.
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
        self.assessments: Dict[str, FairnessAssessment] = {}
        self.alerts: Dict[str, DisparityAlert] = {}
        self.statistics = {
            "total_assessments": 0,
            "passed": 0,
            "failed": 0,
            "bias_detected": 0,
            "disparities_found": 0,
        }
        
        self._fairness_thresholds = self._initialize_thresholds()
        self._bias_indicators = self._initialize_bias_indicators()
    
    def _initialize_thresholds(self) -> Dict[FairnessMetric, float]:
        """Initialize fairness thresholds."""
        return {
            FairnessMetric.DEMOGRAPHIC_PARITY: 0.8,
            FairnessMetric.EQUALIZED_ODDS: 0.8,
            FairnessMetric.EQUAL_OPPORTUNITY: 0.8,
            FairnessMetric.PREDICTIVE_PARITY: 0.8,
            FairnessMetric.CALIBRATION: 0.85,
            FairnessMetric.INDIVIDUAL_FAIRNESS: 0.9,
            FairnessMetric.COUNTERFACTUAL_FAIRNESS: 0.85,
        }
    
    def _initialize_bias_indicators(self) -> Dict[BiasType, List[str]]:
        """Initialize bias indicators."""
        return {
            BiasType.SELECTION: [
                "non_representative_sample",
                "exclusion_criteria",
                "sampling_bias",
            ],
            BiasType.MEASUREMENT: [
                "inconsistent_measurement",
                "proxy_variables",
                "measurement_error",
            ],
            BiasType.ALGORITHMIC: [
                "feature_importance_disparity",
                "model_complexity",
                "optimization_bias",
            ],
            BiasType.HISTORICAL: [
                "historical_discrimination",
                "legacy_patterns",
                "past_inequities",
            ],
            BiasType.REPRESENTATION: [
                "underrepresentation",
                "overrepresentation",
                "stereotype_reinforcement",
            ],
            BiasType.AGGREGATION: [
                "group_averaging",
                "simpson_paradox",
                "ecological_fallacy",
            ],
            BiasType.EVALUATION: [
                "benchmark_bias",
                "metric_selection",
                "evaluation_criteria",
            ],
            BiasType.DEPLOYMENT: [
                "context_mismatch",
                "feedback_loops",
                "usage_patterns",
            ],
        }
    
    def assess_fairness(
        self,
        action_type: str,
        requester_id: str,
        context: Optional[Dict[str, Any]] = None,
        historical_data: Optional[Dict[str, Any]] = None,
    ) -> FairnessAssessment:
        """
        Perform comprehensive fairness assessment.
        
        Args:
            action_type: Type of action being assessed
            requester_id: ID of requester
            context: Additional context
            historical_data: Historical data for disparity analysis
        
        Returns:
            FairnessAssessment with scores and recommendations
        """
        context = context or {}
        historical_data = historical_data or {}
        
        assessment = FairnessAssessment(
            action_type=action_type,
            requester_id=requester_id,
        )
        
        assessment.fairness_scores = self._calculate_fairness_scores(
            action_type, context, historical_data
        )
        
        assessment.bias_detections = self._detect_bias(
            action_type, context, historical_data
        )
        
        assessment.disparity_alerts = self._check_disparities(
            action_type, context, historical_data
        )
        
        for alert in assessment.disparity_alerts:
            self.alerts[alert.alert_id] = alert
        
        assessment.overall_fairness_score = self._calculate_overall_score(
            assessment.fairness_scores
        )
        
        assessment.passed = (
            assessment.overall_fairness_score >= 0.8 and
            not any(b.detected for b in assessment.bias_detections) and
            not any(a.disparity_level.value in ["high", "severe"] for a in assessment.disparity_alerts)
        )
        
        assessment.requires_review = (
            not assessment.passed or
            any(a.disparity_level.value in ["moderate", "high", "severe"] for a in assessment.disparity_alerts)
        )
        
        assessment.recommendations = self._generate_recommendations(assessment)
        assessment.assessment_hash = assessment._compute_hash()
        
        self.assessments[assessment.assessment_id] = assessment
        self._update_statistics(assessment)
        
        return assessment
    
    def _calculate_fairness_scores(
        self,
        action_type: str,
        context: Dict[str, Any],
        historical_data: Dict[str, Any],
    ) -> List[FairnessScore]:
        """Calculate fairness scores for all metrics."""
        scores = []
        
        dp_score = 1.0
        if historical_data.get("demographic_disparity", False):
            dp_score = 0.6
        elif context.get("potential_disparity", False):
            dp_score = 0.75
        
        scores.append(FairnessScore(
            metric=FairnessMetric.DEMOGRAPHIC_PARITY,
            score=dp_score,
            threshold=self._fairness_thresholds[FairnessMetric.DEMOGRAPHIC_PARITY],
            passed=dp_score >= self._fairness_thresholds[FairnessMetric.DEMOGRAPHIC_PARITY],
            details="Demographic parity assessment",
        ))
        
        eo_score = 1.0
        if historical_data.get("outcome_disparity", False):
            eo_score = 0.65
        
        scores.append(FairnessScore(
            metric=FairnessMetric.EQUALIZED_ODDS,
            score=eo_score,
            threshold=self._fairness_thresholds[FairnessMetric.EQUALIZED_ODDS],
            passed=eo_score >= self._fairness_thresholds[FairnessMetric.EQUALIZED_ODDS],
            details="Equalized odds assessment",
        ))
        
        if_score = 1.0
        if context.get("similar_cases_different_outcomes", False):
            if_score = 0.7
        
        scores.append(FairnessScore(
            metric=FairnessMetric.INDIVIDUAL_FAIRNESS,
            score=if_score,
            threshold=self._fairness_thresholds[FairnessMetric.INDIVIDUAL_FAIRNESS],
            passed=if_score >= self._fairness_thresholds[FairnessMetric.INDIVIDUAL_FAIRNESS],
            details="Individual fairness assessment",
        ))
        
        cf_score = 1.0
        if context.get("counterfactual_disparity", False):
            cf_score = 0.6
        
        scores.append(FairnessScore(
            metric=FairnessMetric.COUNTERFACTUAL_FAIRNESS,
            score=cf_score,
            threshold=self._fairness_thresholds[FairnessMetric.COUNTERFACTUAL_FAIRNESS],
            passed=cf_score >= self._fairness_thresholds[FairnessMetric.COUNTERFACTUAL_FAIRNESS],
            details="Counterfactual fairness assessment",
        ))
        
        return scores
    
    def _detect_bias(
        self,
        action_type: str,
        context: Dict[str, Any],
        historical_data: Dict[str, Any],
    ) -> List[BiasDetection]:
        """Detect various types of bias."""
        detections = []
        
        if historical_data.get("historical_discrimination", False):
            detections.append(BiasDetection(
                bias_type=BiasType.HISTORICAL,
                detected=True,
                confidence=0.8,
                source="Historical data patterns",
                impact="May perpetuate past inequities",
                mitigation_strategies=[
                    "Apply bias correction",
                    "Use fairness-aware algorithms",
                    "Review historical patterns",
                ],
            ))
        
        if context.get("non_representative_data", False):
            detections.append(BiasDetection(
                bias_type=BiasType.SELECTION,
                detected=True,
                confidence=0.75,
                source="Data selection process",
                impact="Results may not generalize fairly",
                mitigation_strategies=[
                    "Ensure representative sampling",
                    "Validate across subgroups",
                    "Collect additional data",
                ],
            ))
        
        if context.get("proxy_variables", False):
            detections.append(BiasDetection(
                bias_type=BiasType.MEASUREMENT,
                detected=True,
                confidence=0.7,
                source="Proxy variable usage",
                impact="May indirectly discriminate",
                mitigation_strategies=[
                    "Review feature selection",
                    "Remove proxy variables",
                    "Use direct measurements",
                ],
            ))
        
        if action_type in ["predictive_targeting", "risk_scoring", "pattern_analysis"]:
            detections.append(BiasDetection(
                bias_type=BiasType.ALGORITHMIC,
                detected=False,
                confidence=0.5,
                source="Algorithm type",
                impact="Potential for algorithmic bias",
                mitigation_strategies=[
                    "Regular bias audits",
                    "Fairness constraints",
                    "Human oversight",
                ],
            ))
        
        if not detections:
            detections.append(BiasDetection(
                bias_type=BiasType.ALGORITHMIC,
                detected=False,
                confidence=0.0,
                source="Standard assessment",
                impact="No significant bias detected",
                mitigation_strategies=[],
            ))
        
        return detections
    
    def _check_disparities(
        self,
        action_type: str,
        context: Dict[str, Any],
        historical_data: Dict[str, Any],
    ) -> List[DisparityAlert]:
        """Check for disparities across protected attributes."""
        alerts = []
        
        if historical_data.get("geographic_disparity", False):
            alerts.append(DisparityAlert(
                disparity_type="geographic_concentration",
                protected_attribute=ProtectedAttribute.GEOGRAPHIC,
                disparity_level=DisparityLevel.MODERATE,
                affected_groups=historical_data.get("affected_areas", []),
                disparity_ratio=historical_data.get("geographic_ratio", 1.5),
                description="Geographic concentration detected in action patterns",
                recommendations=[
                    "Review geographic distribution",
                    "Ensure equitable coverage",
                    "Document justification",
                ],
            ))
        
        if historical_data.get("demographic_disparity", False):
            alerts.append(DisparityAlert(
                disparity_type="demographic_impact",
                protected_attribute=ProtectedAttribute.RACE,
                disparity_level=DisparityLevel.HIGH,
                affected_groups=historical_data.get("affected_demographics", []),
                disparity_ratio=historical_data.get("demographic_ratio", 2.0),
                description="Demographic disparity detected",
                recommendations=[
                    "Conduct disparate impact analysis",
                    "Review for discrimination",
                    "Implement corrective measures",
                ],
            ))
        
        if historical_data.get("socioeconomic_disparity", False):
            alerts.append(DisparityAlert(
                disparity_type="socioeconomic_impact",
                protected_attribute=ProtectedAttribute.SOCIOECONOMIC,
                disparity_level=DisparityLevel.MODERATE,
                affected_groups=["low_income"],
                disparity_ratio=historical_data.get("socioeconomic_ratio", 1.3),
                description="Socioeconomic disparity detected",
                recommendations=[
                    "Review for economic bias",
                    "Ensure equitable treatment",
                ],
            ))
        
        return alerts
    
    def _calculate_overall_score(self, scores: List[FairnessScore]) -> float:
        """Calculate overall fairness score."""
        if not scores:
            return 1.0
        
        return sum(s.score for s in scores) / len(scores)
    
    def _generate_recommendations(self, assessment: FairnessAssessment) -> List[str]:
        """Generate recommendations based on assessment."""
        recommendations = []
        
        for score in assessment.fairness_scores:
            if not score.passed:
                recommendations.append(f"Improve {score.metric.value} score (current: {score.score:.2f})")
        
        for detection in assessment.bias_detections:
            if detection.detected:
                recommendations.extend(detection.mitigation_strategies[:2])
        
        for alert in assessment.disparity_alerts:
            recommendations.extend(alert.recommendations[:2])
        
        return list(set(recommendations))[:5]
    
    def _update_statistics(self, assessment: FairnessAssessment) -> None:
        """Update statistics."""
        self.statistics["total_assessments"] += 1
        
        if assessment.passed:
            self.statistics["passed"] += 1
        else:
            self.statistics["failed"] += 1
        
        if any(b.detected for b in assessment.bias_detections):
            self.statistics["bias_detected"] += 1
        
        self.statistics["disparities_found"] += len(assessment.disparity_alerts)
    
    def detect_real_time_disparity(
        self,
        action_type: str,
        current_data: Dict[str, Any],
        baseline_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Detect disparity in real-time.
        
        Args:
            action_type: Type of action
            current_data: Current action data
            baseline_data: Baseline for comparison
        
        Returns:
            Dict with disparity analysis
        """
        baseline_data = baseline_data or {}
        
        disparities = []
        
        current_distribution = current_data.get("distribution", {})
        baseline_distribution = baseline_data.get("distribution", {})
        
        for key in current_distribution:
            current_rate = current_distribution.get(key, 0)
            baseline_rate = baseline_distribution.get(key, current_rate)
            
            if baseline_rate > 0:
                ratio = current_rate / baseline_rate
                if ratio > 1.5 or ratio < 0.67:
                    disparities.append({
                        "category": key,
                        "current_rate": current_rate,
                        "baseline_rate": baseline_rate,
                        "ratio": ratio,
                        "direction": "over" if ratio > 1 else "under",
                    })
        
        return {
            "disparities_detected": len(disparities) > 0,
            "disparity_count": len(disparities),
            "disparities": disparities,
            "action_required": "Review required" if disparities else "None",
        }
    
    def balance_geographic_fairness(
        self,
        action_type: str,
        geographic_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Balance geographic fairness.
        
        Args:
            action_type: Type of action
            geographic_data: Geographic distribution data
        
        Returns:
            Dict with balancing recommendations
        """
        areas = geographic_data.get("areas", {})
        
        if not areas:
            return {
                "balanced": True,
                "recommendations": [],
            }
        
        total = sum(areas.values())
        if total == 0:
            return {
                "balanced": True,
                "recommendations": [],
            }
        
        expected_rate = total / len(areas)
        imbalanced_areas = []
        
        for area, count in areas.items():
            ratio = count / expected_rate if expected_rate > 0 else 1
            if ratio > 1.5:
                imbalanced_areas.append({
                    "area": area,
                    "count": count,
                    "expected": expected_rate,
                    "ratio": ratio,
                    "status": "over_represented",
                })
            elif ratio < 0.5:
                imbalanced_areas.append({
                    "area": area,
                    "count": count,
                    "expected": expected_rate,
                    "ratio": ratio,
                    "status": "under_represented",
                })
        
        return {
            "balanced": len(imbalanced_areas) == 0,
            "imbalanced_areas": imbalanced_areas,
            "recommendations": [
                f"Review activity in {a['area']}" for a in imbalanced_areas
            ],
        }
    
    def identify_harmful_patterns(
        self,
        historical_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Identify harmful historical patterns.
        
        Args:
            historical_data: Historical pattern data
        
        Returns:
            Dict with harmful pattern analysis
        """
        harmful_patterns = []
        
        if historical_data.get("repeat_targeting", False):
            harmful_patterns.append({
                "pattern": "repeat_targeting",
                "description": "Same individuals/areas repeatedly targeted",
                "harm_level": "high",
                "recommendation": "Review targeting criteria",
            })
        
        if historical_data.get("escalation_pattern", False):
            harmful_patterns.append({
                "pattern": "escalation_pattern",
                "description": "Pattern of escalating responses",
                "harm_level": "high",
                "recommendation": "Implement de-escalation protocols",
            })
        
        if historical_data.get("demographic_concentration", False):
            harmful_patterns.append({
                "pattern": "demographic_concentration",
                "description": "Actions concentrated on specific demographics",
                "harm_level": "severe",
                "recommendation": "Conduct civil rights review",
            })
        
        if historical_data.get("time_of_day_bias", False):
            harmful_patterns.append({
                "pattern": "time_of_day_bias",
                "description": "Biased activity based on time of day",
                "harm_level": "moderate",
                "recommendation": "Review temporal patterns",
            })
        
        return {
            "harmful_patterns_found": len(harmful_patterns) > 0,
            "pattern_count": len(harmful_patterns),
            "patterns": harmful_patterns,
            "overall_risk": "high" if any(p["harm_level"] == "severe" for p in harmful_patterns) else "moderate" if harmful_patterns else "low",
        }
    
    def normalize_outputs(
        self,
        outputs: Dict[str, Any],
        fairness_constraints: Optional[Dict[str, float]] = None,
    ) -> Dict[str, Any]:
        """
        Normalize outputs to prevent bias leakage.
        
        Args:
            outputs: Raw outputs to normalize
            fairness_constraints: Fairness constraints to apply
        
        Returns:
            Dict with normalized outputs
        """
        fairness_constraints = fairness_constraints or {}
        
        normalized = outputs.copy()
        adjustments = []
        
        if "scores" in normalized:
            scores = normalized["scores"]
            if isinstance(scores, dict):
                max_disparity = fairness_constraints.get("max_disparity", 0.2)
                
                values = list(scores.values())
                if values:
                    mean_score = sum(values) / len(values)
                    
                    for key, value in scores.items():
                        if abs(value - mean_score) > max_disparity:
                            adjusted = mean_score + (max_disparity if value > mean_score else -max_disparity)
                            adjustments.append({
                                "key": key,
                                "original": value,
                                "adjusted": adjusted,
                            })
                            scores[key] = adjusted
        
        return {
            "normalized_outputs": normalized,
            "adjustments_made": len(adjustments),
            "adjustments": adjustments,
        }
    
    def get_assessment(self, assessment_id: str) -> Optional[FairnessAssessment]:
        """Get assessment by ID."""
        return self.assessments.get(assessment_id)
    
    def get_active_alerts(self) -> List[DisparityAlert]:
        """Get unacknowledged alerts."""
        return [a for a in self.alerts.values() if not a.acknowledged]
    
    def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge an alert."""
        alert = self.alerts.get(alert_id)
        if alert:
            alert.acknowledged = True
            return True
        return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get analyzer statistics."""
        return {
            **self.statistics,
            "active_alerts": len(self.get_active_alerts()),
            "pass_rate": (
                self.statistics["passed"] / max(1, self.statistics["total_assessments"])
            ) * 100,
        }
