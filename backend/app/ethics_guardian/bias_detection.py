"""
Phase 26: Bias Detection Engine

Detects bias in AI outputs including:
- Predictive AI outputs
- Risk scores
- Patrol routing
- Entity correlations
- Surveillance triggers
- Enforcement recommendations

Computes fairness metrics:
- Disparate Impact Ratio
- Demographic Parity
- Equal Opportunity Difference
- Predictive Equality
- Calibration Fairness
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
import uuid
import math


class BiasStatus(Enum):
    """Bias detection status."""
    NO_BIAS_DETECTED = "NO_BIAS_DETECTED"
    POSSIBLE_BIAS_FLAG_REVIEW = "POSSIBLE_BIAS_FLAG_REVIEW"
    BIAS_DETECTED_BLOCKED = "BIAS_DETECTED_BLOCKED"


class BiasCategory(Enum):
    """Categories of potential bias."""
    RACIAL = "RACIAL"
    ETHNIC = "ETHNIC"
    GENDER = "GENDER"
    AGE = "AGE"
    SOCIOECONOMIC = "SOCIOECONOMIC"
    GEOGRAPHIC = "GEOGRAPHIC"
    DISABILITY = "DISABILITY"
    RELIGION = "RELIGION"


class AnalysisType(Enum):
    """Types of AI outputs to analyze for bias."""
    PREDICTIVE_AI = "PREDICTIVE_AI"
    RISK_SCORE = "RISK_SCORE"
    PATROL_ROUTING = "PATROL_ROUTING"
    ENTITY_CORRELATION = "ENTITY_CORRELATION"
    SURVEILLANCE_TRIGGER = "SURVEILLANCE_TRIGGER"
    ENFORCEMENT_RECOMMENDATION = "ENFORCEMENT_RECOMMENDATION"


@dataclass
class BiasMetric:
    """Individual bias metric measurement."""
    metric_id: str
    name: str
    value: float
    threshold: float
    is_passing: bool
    description: str
    protected_group: str
    reference_group: str
    sample_size_protected: int
    sample_size_reference: int
    confidence_interval: tuple
    statistical_significance: float


@dataclass
class StatisticalEvidence:
    """Statistical evidence for bias detection."""
    evidence_id: str
    metric_name: str
    observed_value: float
    expected_value: float
    deviation: float
    p_value: float
    effect_size: float
    interpretation: str
    data_points: int
    time_period: str


@dataclass
class BiasResult:
    """Result of bias detection analysis."""
    result_id: str
    analysis_type: AnalysisType
    status: BiasStatus
    metrics: List[BiasMetric]
    statistical_evidence: List[StatisticalEvidence]
    affected_groups: List[str]
    recommendations: List[str]
    timestamp: datetime
    model_version: str
    data_source: str
    geographic_scope: str
    confidence_score: float
    requires_human_review: bool
    blocked: bool
    explanation: str


@dataclass
class DemographicData:
    """Demographic data for bias analysis."""
    group_name: str
    population_count: int
    positive_outcomes: int
    negative_outcomes: int
    total_interactions: int
    average_risk_score: float
    enforcement_rate: float
    surveillance_rate: float


class BiasDetectionEngine:
    """
    Engine for detecting bias in AI outputs.
    
    Implements fairness metrics:
    - Disparate Impact Ratio (80% rule)
    - Demographic Parity
    - Equal Opportunity Difference
    - Predictive Equality
    - Calibration Fairness
    """
    
    _instance = None
    
    DISPARATE_IMPACT_THRESHOLD = 0.8
    DEMOGRAPHIC_PARITY_THRESHOLD = 0.1
    EQUAL_OPPORTUNITY_THRESHOLD = 0.1
    PREDICTIVE_EQUALITY_THRESHOLD = 0.1
    CALIBRATION_THRESHOLD = 0.1
    
    RIVIERA_BEACH_DEMOGRAPHICS = {
        "Black": 0.66,
        "White": 0.22,
        "Hispanic": 0.08,
        "Asian": 0.02,
        "Other": 0.02,
    }
    
    def __init__(self):
        self._analysis_history: List[BiasResult] = []
        self._demographic_baselines: Dict[str, DemographicData] = {}
        self._initialize_baselines()
    
    @classmethod
    def get_instance(cls) -> "BiasDetectionEngine":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def _initialize_baselines(self):
        """Initialize demographic baselines for Riviera Beach."""
        population = 37964
        
        for group, proportion in self.RIVIERA_BEACH_DEMOGRAPHICS.items():
            pop_count = int(population * proportion)
            self._demographic_baselines[group] = DemographicData(
                group_name=group,
                population_count=pop_count,
                positive_outcomes=0,
                negative_outcomes=0,
                total_interactions=0,
                average_risk_score=50.0,
                enforcement_rate=0.0,
                surveillance_rate=0.0,
            )
    
    def analyze_for_bias(
        self,
        analysis_type: AnalysisType,
        data: Dict[str, Any],
        model_version: str = "1.0",
        geographic_scope: str = "Riviera Beach",
    ) -> BiasResult:
        """
        Analyze AI output for potential bias.
        
        Args:
            analysis_type: Type of AI output being analyzed
            data: Data containing outcomes by demographic group
            model_version: Version of the AI model
            geographic_scope: Geographic area of analysis
            
        Returns:
            BiasResult with status, metrics, and recommendations
        """
        result_id = f"bias-{uuid.uuid4().hex[:12]}"
        metrics = []
        evidence = []
        affected_groups = []
        recommendations = []
        
        demographic_outcomes = data.get("demographic_outcomes", {})
        reference_group = data.get("reference_group", "White")
        
        dir_metric = self._calculate_disparate_impact(
            demographic_outcomes, reference_group
        )
        metrics.append(dir_metric)
        if not dir_metric.is_passing:
            affected_groups.append(dir_metric.protected_group)
            evidence.append(self._create_evidence(dir_metric, "Disparate Impact"))
        
        dp_metric = self._calculate_demographic_parity(
            demographic_outcomes, reference_group
        )
        metrics.append(dp_metric)
        if not dp_metric.is_passing:
            if dp_metric.protected_group not in affected_groups:
                affected_groups.append(dp_metric.protected_group)
            evidence.append(self._create_evidence(dp_metric, "Demographic Parity"))
        
        eod_metric = self._calculate_equal_opportunity(
            demographic_outcomes, reference_group
        )
        metrics.append(eod_metric)
        if not eod_metric.is_passing:
            if eod_metric.protected_group not in affected_groups:
                affected_groups.append(eod_metric.protected_group)
            evidence.append(self._create_evidence(eod_metric, "Equal Opportunity"))
        
        pe_metric = self._calculate_predictive_equality(
            demographic_outcomes, reference_group
        )
        metrics.append(pe_metric)
        if not pe_metric.is_passing:
            if pe_metric.protected_group not in affected_groups:
                affected_groups.append(pe_metric.protected_group)
            evidence.append(self._create_evidence(pe_metric, "Predictive Equality"))
        
        cf_metric = self._calculate_calibration_fairness(
            demographic_outcomes, reference_group
        )
        metrics.append(cf_metric)
        if not cf_metric.is_passing:
            if cf_metric.protected_group not in affected_groups:
                affected_groups.append(cf_metric.protected_group)
            evidence.append(self._create_evidence(cf_metric, "Calibration Fairness"))
        
        status, blocked, requires_review = self._determine_status(metrics)
        
        recommendations = self._generate_recommendations(
            status, metrics, affected_groups, analysis_type
        )
        
        confidence = self._calculate_confidence(metrics)
        explanation = self._generate_explanation(status, metrics, affected_groups)
        
        result = BiasResult(
            result_id=result_id,
            analysis_type=analysis_type,
            status=status,
            metrics=metrics,
            statistical_evidence=evidence,
            affected_groups=affected_groups,
            recommendations=recommendations,
            timestamp=datetime.now(),
            model_version=model_version,
            data_source=data.get("data_source", "RTCC-UIP"),
            geographic_scope=geographic_scope,
            confidence_score=confidence,
            requires_human_review=requires_review,
            blocked=blocked,
            explanation=explanation,
        )
        
        self._analysis_history.append(result)
        return result
    
    def _calculate_disparate_impact(
        self,
        outcomes: Dict[str, Dict],
        reference_group: str,
    ) -> BiasMetric:
        """Calculate Disparate Impact Ratio (80% rule)."""
        metric_id = f"dir-{uuid.uuid4().hex[:8]}"
        
        ref_data = outcomes.get(reference_group, {})
        ref_rate = ref_data.get("positive_rate", 0.5)
        
        worst_ratio = 1.0
        worst_group = reference_group
        
        for group, data in outcomes.items():
            if group == reference_group:
                continue
            group_rate = data.get("positive_rate", 0.5)
            if ref_rate > 0:
                ratio = group_rate / ref_rate
                if ratio < worst_ratio:
                    worst_ratio = ratio
                    worst_group = group
        
        is_passing = worst_ratio >= self.DISPARATE_IMPACT_THRESHOLD
        
        return BiasMetric(
            metric_id=metric_id,
            name="Disparate Impact Ratio",
            value=worst_ratio,
            threshold=self.DISPARATE_IMPACT_THRESHOLD,
            is_passing=is_passing,
            description=f"Ratio of positive outcome rates between {worst_group} and {reference_group}",
            protected_group=worst_group,
            reference_group=reference_group,
            sample_size_protected=outcomes.get(worst_group, {}).get("sample_size", 100),
            sample_size_reference=ref_data.get("sample_size", 100),
            confidence_interval=(worst_ratio * 0.95, worst_ratio * 1.05),
            statistical_significance=0.95 if not is_passing else 0.5,
        )
    
    def _calculate_demographic_parity(
        self,
        outcomes: Dict[str, Dict],
        reference_group: str,
    ) -> BiasMetric:
        """Calculate Demographic Parity difference."""
        metric_id = f"dp-{uuid.uuid4().hex[:8]}"
        
        ref_data = outcomes.get(reference_group, {})
        ref_rate = ref_data.get("positive_rate", 0.5)
        
        worst_diff = 0.0
        worst_group = reference_group
        
        for group, data in outcomes.items():
            if group == reference_group:
                continue
            group_rate = data.get("positive_rate", 0.5)
            diff = abs(group_rate - ref_rate)
            if diff > worst_diff:
                worst_diff = diff
                worst_group = group
        
        is_passing = worst_diff <= self.DEMOGRAPHIC_PARITY_THRESHOLD
        
        return BiasMetric(
            metric_id=metric_id,
            name="Demographic Parity",
            value=worst_diff,
            threshold=self.DEMOGRAPHIC_PARITY_THRESHOLD,
            is_passing=is_passing,
            description=f"Difference in positive outcome rates between {worst_group} and {reference_group}",
            protected_group=worst_group,
            reference_group=reference_group,
            sample_size_protected=outcomes.get(worst_group, {}).get("sample_size", 100),
            sample_size_reference=ref_data.get("sample_size", 100),
            confidence_interval=(worst_diff * 0.9, worst_diff * 1.1),
            statistical_significance=0.95 if not is_passing else 0.5,
        )
    
    def _calculate_equal_opportunity(
        self,
        outcomes: Dict[str, Dict],
        reference_group: str,
    ) -> BiasMetric:
        """Calculate Equal Opportunity Difference (TPR parity)."""
        metric_id = f"eod-{uuid.uuid4().hex[:8]}"
        
        ref_data = outcomes.get(reference_group, {})
        ref_tpr = ref_data.get("true_positive_rate", 0.8)
        
        worst_diff = 0.0
        worst_group = reference_group
        
        for group, data in outcomes.items():
            if group == reference_group:
                continue
            group_tpr = data.get("true_positive_rate", 0.8)
            diff = abs(group_tpr - ref_tpr)
            if diff > worst_diff:
                worst_diff = diff
                worst_group = group
        
        is_passing = worst_diff <= self.EQUAL_OPPORTUNITY_THRESHOLD
        
        return BiasMetric(
            metric_id=metric_id,
            name="Equal Opportunity Difference",
            value=worst_diff,
            threshold=self.EQUAL_OPPORTUNITY_THRESHOLD,
            is_passing=is_passing,
            description=f"Difference in true positive rates between {worst_group} and {reference_group}",
            protected_group=worst_group,
            reference_group=reference_group,
            sample_size_protected=outcomes.get(worst_group, {}).get("sample_size", 100),
            sample_size_reference=ref_data.get("sample_size", 100),
            confidence_interval=(worst_diff * 0.9, worst_diff * 1.1),
            statistical_significance=0.95 if not is_passing else 0.5,
        )
    
    def _calculate_predictive_equality(
        self,
        outcomes: Dict[str, Dict],
        reference_group: str,
    ) -> BiasMetric:
        """Calculate Predictive Equality (FPR parity)."""
        metric_id = f"pe-{uuid.uuid4().hex[:8]}"
        
        ref_data = outcomes.get(reference_group, {})
        ref_fpr = ref_data.get("false_positive_rate", 0.1)
        
        worst_diff = 0.0
        worst_group = reference_group
        
        for group, data in outcomes.items():
            if group == reference_group:
                continue
            group_fpr = data.get("false_positive_rate", 0.1)
            diff = abs(group_fpr - ref_fpr)
            if diff > worst_diff:
                worst_diff = diff
                worst_group = group
        
        is_passing = worst_diff <= self.PREDICTIVE_EQUALITY_THRESHOLD
        
        return BiasMetric(
            metric_id=metric_id,
            name="Predictive Equality",
            value=worst_diff,
            threshold=self.PREDICTIVE_EQUALITY_THRESHOLD,
            is_passing=is_passing,
            description=f"Difference in false positive rates between {worst_group} and {reference_group}",
            protected_group=worst_group,
            reference_group=reference_group,
            sample_size_protected=outcomes.get(worst_group, {}).get("sample_size", 100),
            sample_size_reference=ref_data.get("sample_size", 100),
            confidence_interval=(worst_diff * 0.9, worst_diff * 1.1),
            statistical_significance=0.95 if not is_passing else 0.5,
        )
    
    def _calculate_calibration_fairness(
        self,
        outcomes: Dict[str, Dict],
        reference_group: str,
    ) -> BiasMetric:
        """Calculate Calibration Fairness."""
        metric_id = f"cf-{uuid.uuid4().hex[:8]}"
        
        ref_data = outcomes.get(reference_group, {})
        ref_calibration = ref_data.get("calibration_score", 0.9)
        
        worst_diff = 0.0
        worst_group = reference_group
        
        for group, data in outcomes.items():
            if group == reference_group:
                continue
            group_calibration = data.get("calibration_score", 0.9)
            diff = abs(group_calibration - ref_calibration)
            if diff > worst_diff:
                worst_diff = diff
                worst_group = group
        
        is_passing = worst_diff <= self.CALIBRATION_THRESHOLD
        
        return BiasMetric(
            metric_id=metric_id,
            name="Calibration Fairness",
            value=worst_diff,
            threshold=self.CALIBRATION_THRESHOLD,
            is_passing=is_passing,
            description=f"Difference in calibration between {worst_group} and {reference_group}",
            protected_group=worst_group,
            reference_group=reference_group,
            sample_size_protected=outcomes.get(worst_group, {}).get("sample_size", 100),
            sample_size_reference=ref_data.get("sample_size", 100),
            confidence_interval=(worst_diff * 0.9, worst_diff * 1.1),
            statistical_significance=0.95 if not is_passing else 0.5,
        )
    
    def _create_evidence(
        self,
        metric: BiasMetric,
        metric_name: str,
    ) -> StatisticalEvidence:
        """Create statistical evidence for a failing metric."""
        return StatisticalEvidence(
            evidence_id=f"ev-{uuid.uuid4().hex[:8]}",
            metric_name=metric_name,
            observed_value=metric.value,
            expected_value=metric.threshold,
            deviation=abs(metric.value - metric.threshold),
            p_value=1.0 - metric.statistical_significance,
            effect_size=abs(metric.value - metric.threshold) / metric.threshold if metric.threshold > 0 else 0,
            interpretation=f"{metric_name} violation detected for {metric.protected_group}",
            data_points=metric.sample_size_protected + metric.sample_size_reference,
            time_period="Last 30 days",
        )
    
    def _determine_status(
        self,
        metrics: List[BiasMetric],
    ) -> tuple:
        """Determine overall bias status from metrics."""
        failing_count = sum(1 for m in metrics if not m.is_passing)
        
        if failing_count == 0:
            return BiasStatus.NO_BIAS_DETECTED, False, False
        elif failing_count <= 2:
            return BiasStatus.POSSIBLE_BIAS_FLAG_REVIEW, False, True
        else:
            return BiasStatus.BIAS_DETECTED_BLOCKED, True, True
    
    def _generate_recommendations(
        self,
        status: BiasStatus,
        metrics: List[BiasMetric],
        affected_groups: List[str],
        analysis_type: AnalysisType,
    ) -> List[str]:
        """Generate recommendations based on bias analysis."""
        recommendations = []
        
        if status == BiasStatus.NO_BIAS_DETECTED:
            recommendations.append("Continue monitoring for bias drift")
            recommendations.append("Schedule quarterly fairness audit")
            return recommendations
        
        for metric in metrics:
            if not metric.is_passing:
                if metric.name == "Disparate Impact Ratio":
                    recommendations.append(
                        f"Review {analysis_type.value} model for disparate impact on {metric.protected_group}"
                    )
                    recommendations.append(
                        "Consider retraining with balanced dataset"
                    )
                elif metric.name == "Demographic Parity":
                    recommendations.append(
                        f"Investigate outcome rate differences for {metric.protected_group}"
                    )
                elif metric.name == "Equal Opportunity Difference":
                    recommendations.append(
                        f"Review true positive rate disparities for {metric.protected_group}"
                    )
                elif metric.name == "Predictive Equality":
                    recommendations.append(
                        f"Address false positive rate imbalance for {metric.protected_group}"
                    )
                elif metric.name == "Calibration Fairness":
                    recommendations.append(
                        f"Recalibrate model predictions for {metric.protected_group}"
                    )
        
        if status == BiasStatus.BIAS_DETECTED_BLOCKED:
            recommendations.append("IMMEDIATE: Suspend automated decisions pending review")
            recommendations.append("Escalate to Civil Rights Compliance Officer")
            recommendations.append("Document incident for DOJ reporting")
        
        return recommendations
    
    def _calculate_confidence(self, metrics: List[BiasMetric]) -> float:
        """Calculate overall confidence score."""
        if not metrics:
            return 0.5
        
        total_samples = sum(m.sample_size_protected + m.sample_size_reference for m in metrics)
        avg_significance = sum(m.statistical_significance for m in metrics) / len(metrics)
        
        sample_factor = min(1.0, total_samples / 1000)
        confidence = (avg_significance + sample_factor) / 2
        
        return round(confidence, 3)
    
    def _generate_explanation(
        self,
        status: BiasStatus,
        metrics: List[BiasMetric],
        affected_groups: List[str],
    ) -> str:
        """Generate human-readable explanation."""
        if status == BiasStatus.NO_BIAS_DETECTED:
            return "All fairness metrics are within acceptable thresholds. No bias detected."
        
        failing_metrics = [m for m in metrics if not m.is_passing]
        metric_names = [m.name for m in failing_metrics]
        
        if status == BiasStatus.POSSIBLE_BIAS_FLAG_REVIEW:
            return (
                f"Possible bias detected. {len(failing_metrics)} metric(s) failed: "
                f"{', '.join(metric_names)}. Affected groups: {', '.join(affected_groups)}. "
                "Human review required before proceeding."
            )
        else:
            return (
                f"BIAS DETECTED - ACTION BLOCKED. {len(failing_metrics)} metric(s) failed: "
                f"{', '.join(metric_names)}. Affected groups: {', '.join(affected_groups)}. "
                "This action has been blocked pending civil rights review."
            )
    
    def get_analysis_history(
        self,
        analysis_type: Optional[AnalysisType] = None,
        status: Optional[BiasStatus] = None,
        limit: int = 100,
    ) -> List[BiasResult]:
        """Get bias analysis history with optional filters."""
        results = self._analysis_history
        
        if analysis_type:
            results = [r for r in results if r.analysis_type == analysis_type]
        if status:
            results = [r for r in results if r.status == status]
        
        return results[-limit:]
    
    def get_demographic_baselines(self) -> Dict[str, DemographicData]:
        """Get demographic baselines for Riviera Beach."""
        return self._demographic_baselines
    
    def update_demographic_data(
        self,
        group: str,
        interactions: int,
        positive_outcomes: int,
        negative_outcomes: int,
    ):
        """Update demographic data for ongoing monitoring."""
        if group in self._demographic_baselines:
            baseline = self._demographic_baselines[group]
            baseline.total_interactions += interactions
            baseline.positive_outcomes += positive_outcomes
            baseline.negative_outcomes += negative_outcomes
            
            if baseline.total_interactions > 0:
                baseline.enforcement_rate = (
                    baseline.negative_outcomes / baseline.total_interactions
                )


def get_bias_detection_engine() -> BiasDetectionEngine:
    """Get the singleton BiasDetectionEngine instance."""
    return BiasDetectionEngine.get_instance()
