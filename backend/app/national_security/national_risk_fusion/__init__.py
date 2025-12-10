"""
National Risk Fusion Module

Provides deep fusion capabilities combining:
- Cyber threat intelligence
- Geopolitical risk signals
- Financial crime intelligence
- Insider threat indicators
- National Stability Score (NSS)
- Early-warning prediction timeline
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
import uuid
import statistics


class StabilityLevel(Enum):
    """National stability levels."""
    OPTIMAL = "optimal"
    STABLE = "stable"
    ELEVATED_CONCERN = "elevated_concern"
    UNSTABLE = "unstable"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class RiskDomain(Enum):
    """Risk domains for fusion."""
    CYBER = "cyber"
    GEOPOLITICAL = "geopolitical"
    FINANCIAL = "financial"
    INSIDER = "insider"
    TERRORISM = "terrorism"
    INFRASTRUCTURE = "infrastructure"
    ECONOMIC = "economic"
    SOCIAL = "social"
    ENVIRONMENTAL = "environmental"
    HEALTH = "health"


class FusionMethod(Enum):
    """Methods for fusing risk signals."""
    WEIGHTED_AVERAGE = "weighted_average"
    MAX_RISK = "max_risk"
    BAYESIAN = "bayesian"
    ENSEMBLE = "ensemble"
    NEURAL = "neural"
    RULE_BASED = "rule_based"


class TrendDirection(Enum):
    """Direction of risk trends."""
    IMPROVING = "improving"
    STABLE = "stable"
    DEGRADING = "degrading"
    RAPIDLY_DEGRADING = "rapidly_degrading"


class AlertUrgency(Enum):
    """Urgency levels for early warnings."""
    ROUTINE = "routine"
    PRIORITY = "priority"
    IMMEDIATE = "immediate"
    FLASH = "flash"
    EMERGENCY = "emergency"


@dataclass
class DomainRiskScore:
    """Risk score for a specific domain."""
    domain: RiskDomain
    score: float
    confidence: float
    trend: TrendDirection
    contributing_factors: List[str]
    last_updated: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class NationalStabilityScore:
    """National Stability Score (NSS) assessment."""
    assessment_id: str
    timestamp: datetime
    overall_score: float
    stability_level: StabilityLevel
    domain_scores: Dict[str, DomainRiskScore]
    fusion_method: FusionMethod
    confidence_level: float
    trend: TrendDirection
    key_drivers: List[str]
    risk_factors: List[Dict[str, Any]]
    recommendations: List[str]
    forecast_24h: float
    forecast_7d: float
    forecast_30d: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RiskFusionResult:
    """Result of risk fusion analysis."""
    fusion_id: str
    timestamp: datetime
    domains_fused: List[RiskDomain]
    fusion_method: FusionMethod
    fused_score: float
    confidence: float
    correlations: Dict[str, float]
    amplification_factors: List[str]
    mitigation_factors: List[str]
    cross_domain_patterns: List[Dict[str, Any]]
    anomalies_detected: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EarlyWarningSignal:
    """Early warning signal for emerging threats."""
    signal_id: str
    title: str
    description: str
    urgency: AlertUrgency
    domains_affected: List[RiskDomain]
    risk_score: float
    probability: float
    time_horizon_hours: int
    indicators: List[str]
    potential_impacts: List[str]
    recommended_actions: List[str]
    related_signals: List[str]
    source_signals: List[str]
    confidence_level: float
    is_active: bool
    created_at: datetime
    expires_at: datetime
    acknowledged: bool
    acknowledged_by: Optional[str]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TrendPrediction:
    """Prediction of risk trends."""
    prediction_id: str
    domain: RiskDomain
    current_score: float
    predicted_score: float
    prediction_horizon_hours: int
    confidence: float
    trend_direction: TrendDirection
    key_factors: List[str]
    scenarios: List[Dict[str, Any]]
    created_at: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FusionEvent:
    """Event in the fusion timeline."""
    event_id: str
    timestamp: datetime
    event_type: str
    domain: RiskDomain
    severity: float
    description: str
    impact_assessment: str
    related_events: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)


class NationalRiskFusionEngine:
    """
    National Risk Fusion Engine.
    
    Provides deep fusion capabilities for:
    - Multi-domain risk correlation
    - National Stability Score calculation
    - Early warning signal generation
    - Trend prediction and forecasting
    """

    def __init__(self):
        self.stability_scores: Dict[str, NationalStabilityScore] = {}
        self.fusion_results: Dict[str, RiskFusionResult] = {}
        self.early_warnings: Dict[str, EarlyWarningSignal] = {}
        self.trend_predictions: Dict[str, TrendPrediction] = {}
        self.fusion_events: Dict[str, FusionEvent] = {}
        self.domain_weights: Dict[RiskDomain, float] = {
            RiskDomain.CYBER: 0.18,
            RiskDomain.GEOPOLITICAL: 0.15,
            RiskDomain.FINANCIAL: 0.15,
            RiskDomain.INSIDER: 0.12,
            RiskDomain.TERRORISM: 0.15,
            RiskDomain.INFRASTRUCTURE: 0.10,
            RiskDomain.ECONOMIC: 0.08,
            RiskDomain.SOCIAL: 0.04,
            RiskDomain.ENVIRONMENTAL: 0.02,
            RiskDomain.HEALTH: 0.01,
        }
        self.correlation_matrix: Dict[Tuple[RiskDomain, RiskDomain], float] = {}
        self._initialize_correlation_matrix()

    def _initialize_correlation_matrix(self) -> None:
        """Initialize domain correlation matrix."""
        correlations = [
            (RiskDomain.CYBER, RiskDomain.INFRASTRUCTURE, 0.8),
            (RiskDomain.CYBER, RiskDomain.FINANCIAL, 0.6),
            (RiskDomain.CYBER, RiskDomain.INSIDER, 0.5),
            (RiskDomain.GEOPOLITICAL, RiskDomain.TERRORISM, 0.7),
            (RiskDomain.GEOPOLITICAL, RiskDomain.ECONOMIC, 0.6),
            (RiskDomain.FINANCIAL, RiskDomain.ECONOMIC, 0.8),
            (RiskDomain.FINANCIAL, RiskDomain.INSIDER, 0.5),
            (RiskDomain.TERRORISM, RiskDomain.INFRASTRUCTURE, 0.6),
            (RiskDomain.SOCIAL, RiskDomain.TERRORISM, 0.4),
            (RiskDomain.ENVIRONMENTAL, RiskDomain.INFRASTRUCTURE, 0.5),
            (RiskDomain.HEALTH, RiskDomain.ECONOMIC, 0.5),
            (RiskDomain.HEALTH, RiskDomain.SOCIAL, 0.6),
        ]
        
        for d1, d2, corr in correlations:
            self.correlation_matrix[(d1, d2)] = corr
            self.correlation_matrix[(d2, d1)] = corr

    def calculate_national_stability_score(
        self,
        domain_scores: Dict[RiskDomain, Tuple[float, float]],
        fusion_method: FusionMethod = FusionMethod.WEIGHTED_AVERAGE,
    ) -> NationalStabilityScore:
        """
        Calculate the National Stability Score (NSS).
        
        Args:
            domain_scores: Dict mapping domain to (score, confidence) tuple
            fusion_method: Method to use for fusion
        
        Returns:
            NationalStabilityScore assessment
        """
        assessment_id = f"nss-{uuid.uuid4().hex[:12]}"
        now = datetime.utcnow()
        
        processed_domains: Dict[str, DomainRiskScore] = {}
        for domain, (score, confidence) in domain_scores.items():
            trend = self._calculate_domain_trend(domain)
            processed_domains[domain.value] = DomainRiskScore(
                domain=domain,
                score=score,
                confidence=confidence,
                trend=trend,
                contributing_factors=[],
                last_updated=now,
            )
        
        if fusion_method == FusionMethod.WEIGHTED_AVERAGE:
            overall_score = self._weighted_average_fusion(domain_scores)
        elif fusion_method == FusionMethod.MAX_RISK:
            overall_score = self._max_risk_fusion(domain_scores)
        elif fusion_method == FusionMethod.ENSEMBLE:
            overall_score = self._ensemble_fusion(domain_scores)
        else:
            overall_score = self._weighted_average_fusion(domain_scores)
        
        stability_level = self._score_to_stability_level(overall_score)
        
        confidence_level = statistics.mean([conf for _, conf in domain_scores.values()])
        
        trend = self._calculate_overall_trend()
        
        key_drivers = self._identify_key_drivers(domain_scores)
        risk_factors = self._identify_risk_factors(domain_scores)
        recommendations = self._generate_recommendations(stability_level, key_drivers)
        
        forecast_24h = self._forecast_score(overall_score, 24)
        forecast_7d = self._forecast_score(overall_score, 168)
        forecast_30d = self._forecast_score(overall_score, 720)
        
        nss = NationalStabilityScore(
            assessment_id=assessment_id,
            timestamp=now,
            overall_score=overall_score,
            stability_level=stability_level,
            domain_scores=processed_domains,
            fusion_method=fusion_method,
            confidence_level=confidence_level,
            trend=trend,
            key_drivers=key_drivers,
            risk_factors=risk_factors,
            recommendations=recommendations,
            forecast_24h=forecast_24h,
            forecast_7d=forecast_7d,
            forecast_30d=forecast_30d,
        )
        
        self.stability_scores[assessment_id] = nss
        return nss

    def _weighted_average_fusion(
        self,
        domain_scores: Dict[RiskDomain, Tuple[float, float]],
    ) -> float:
        """Calculate weighted average of domain scores."""
        total_weight = 0
        weighted_sum = 0
        
        for domain, (score, confidence) in domain_scores.items():
            weight = self.domain_weights.get(domain, 0.1) * confidence
            weighted_sum += score * weight
            total_weight += weight
        
        return weighted_sum / total_weight if total_weight > 0 else 50

    def _max_risk_fusion(
        self,
        domain_scores: Dict[RiskDomain, Tuple[float, float]],
    ) -> float:
        """Return maximum risk score across domains."""
        if not domain_scores:
            return 50
        return max(score for score, _ in domain_scores.values())

    def _ensemble_fusion(
        self,
        domain_scores: Dict[RiskDomain, Tuple[float, float]],
    ) -> float:
        """Ensemble fusion combining multiple methods."""
        weighted_avg = self._weighted_average_fusion(domain_scores)
        max_risk = self._max_risk_fusion(domain_scores)
        
        return weighted_avg * 0.7 + max_risk * 0.3

    def _score_to_stability_level(self, score: float) -> StabilityLevel:
        """Convert numeric score to stability level."""
        if score < 20:
            return StabilityLevel.OPTIMAL
        elif score < 35:
            return StabilityLevel.STABLE
        elif score < 50:
            return StabilityLevel.ELEVATED_CONCERN
        elif score < 70:
            return StabilityLevel.UNSTABLE
        elif score < 85:
            return StabilityLevel.CRITICAL
        else:
            return StabilityLevel.EMERGENCY

    def _calculate_domain_trend(self, domain: RiskDomain) -> TrendDirection:
        """Calculate trend for a specific domain."""
        recent_scores = [
            nss for nss in self.stability_scores.values()
            if domain.value in nss.domain_scores
        ]
        
        if len(recent_scores) < 2:
            return TrendDirection.STABLE
        
        recent_scores.sort(key=lambda x: x.timestamp)
        recent = recent_scores[-3:] if len(recent_scores) >= 3 else recent_scores
        
        scores = [nss.domain_scores[domain.value].score for nss in recent]
        
        if len(scores) >= 2:
            change = scores[-1] - scores[0]
            if change > 10:
                return TrendDirection.RAPIDLY_DEGRADING
            elif change > 3:
                return TrendDirection.DEGRADING
            elif change < -3:
                return TrendDirection.IMPROVING
        
        return TrendDirection.STABLE

    def _calculate_overall_trend(self) -> TrendDirection:
        """Calculate overall stability trend."""
        recent_scores = sorted(
            self.stability_scores.values(),
            key=lambda x: x.timestamp
        )[-5:]
        
        if len(recent_scores) < 2:
            return TrendDirection.STABLE
        
        scores = [nss.overall_score for nss in recent_scores]
        change = scores[-1] - scores[0]
        
        if change > 15:
            return TrendDirection.RAPIDLY_DEGRADING
        elif change > 5:
            return TrendDirection.DEGRADING
        elif change < -5:
            return TrendDirection.IMPROVING
        
        return TrendDirection.STABLE

    def _identify_key_drivers(
        self,
        domain_scores: Dict[RiskDomain, Tuple[float, float]],
    ) -> List[str]:
        """Identify key drivers of risk."""
        drivers = []
        
        sorted_domains = sorted(
            domain_scores.items(),
            key=lambda x: x[1][0],
            reverse=True
        )
        
        for domain, (score, _) in sorted_domains[:3]:
            if score >= 50:
                drivers.append(f"High {domain.value} risk ({score:.1f})")
        
        return drivers

    def _identify_risk_factors(
        self,
        domain_scores: Dict[RiskDomain, Tuple[float, float]],
    ) -> List[Dict[str, Any]]:
        """Identify specific risk factors."""
        factors = []
        
        for domain, (score, confidence) in domain_scores.items():
            if score >= 60:
                factors.append({
                    "domain": domain.value,
                    "score": score,
                    "confidence": confidence,
                    "severity": "high" if score >= 75 else "elevated",
                })
        
        return factors

    def _generate_recommendations(
        self,
        stability_level: StabilityLevel,
        key_drivers: List[str],
    ) -> List[str]:
        """Generate recommendations based on stability assessment."""
        recommendations = []
        
        if stability_level in [StabilityLevel.CRITICAL, StabilityLevel.EMERGENCY]:
            recommendations.append("Activate emergency response protocols")
            recommendations.append("Brief senior leadership immediately")
            recommendations.append("Increase monitoring frequency to real-time")
        elif stability_level == StabilityLevel.UNSTABLE:
            recommendations.append("Elevate alert status")
            recommendations.append("Prepare contingency plans")
            recommendations.append("Increase cross-domain coordination")
        elif stability_level == StabilityLevel.ELEVATED_CONCERN:
            recommendations.append("Monitor key indicators closely")
            recommendations.append("Review response procedures")
        else:
            recommendations.append("Maintain standard monitoring")
        
        return recommendations

    def _forecast_score(self, current_score: float, hours: int) -> float:
        """Forecast future stability score."""
        trend = self._calculate_overall_trend()
        
        trend_adjustments = {
            TrendDirection.IMPROVING: -0.1,
            TrendDirection.STABLE: 0,
            TrendDirection.DEGRADING: 0.1,
            TrendDirection.RAPIDLY_DEGRADING: 0.2,
        }
        
        adjustment = trend_adjustments.get(trend, 0) * (hours / 24)
        forecast = current_score + adjustment * current_score
        
        return max(0, min(100, forecast))

    def perform_risk_fusion(
        self,
        domain_scores: Dict[RiskDomain, float],
        fusion_method: FusionMethod = FusionMethod.WEIGHTED_AVERAGE,
    ) -> RiskFusionResult:
        """Perform multi-domain risk fusion analysis."""
        fusion_id = f"fus-{uuid.uuid4().hex[:12]}"
        now = datetime.utcnow()
        
        domain_scores_with_conf = {d: (s, 0.8) for d, s in domain_scores.items()}
        
        if fusion_method == FusionMethod.WEIGHTED_AVERAGE:
            fused_score = self._weighted_average_fusion(domain_scores_with_conf)
        elif fusion_method == FusionMethod.MAX_RISK:
            fused_score = self._max_risk_fusion(domain_scores_with_conf)
        else:
            fused_score = self._ensemble_fusion(domain_scores_with_conf)
        
        correlations = self._calculate_correlations(domain_scores)
        
        amplification_factors = self._identify_amplification_factors(domain_scores, correlations)
        mitigation_factors = self._identify_mitigation_factors(domain_scores)
        
        cross_domain_patterns = self._detect_cross_domain_patterns(domain_scores)
        
        anomalies = self._detect_anomalies(domain_scores)
        
        result = RiskFusionResult(
            fusion_id=fusion_id,
            timestamp=now,
            domains_fused=list(domain_scores.keys()),
            fusion_method=fusion_method,
            fused_score=fused_score,
            confidence=0.8,
            correlations=correlations,
            amplification_factors=amplification_factors,
            mitigation_factors=mitigation_factors,
            cross_domain_patterns=cross_domain_patterns,
            anomalies_detected=anomalies,
        )
        
        self.fusion_results[fusion_id] = result
        return result

    def _calculate_correlations(
        self,
        domain_scores: Dict[RiskDomain, float],
    ) -> Dict[str, float]:
        """Calculate correlations between domain risks."""
        correlations = {}
        domains = list(domain_scores.keys())
        
        for i, d1 in enumerate(domains):
            for d2 in domains[i+1:]:
                key = f"{d1.value}-{d2.value}"
                base_corr = self.correlation_matrix.get((d1, d2), 0.3)
                
                score_similarity = 1 - abs(domain_scores[d1] - domain_scores[d2]) / 100
                adjusted_corr = base_corr * score_similarity
                
                correlations[key] = round(adjusted_corr, 3)
        
        return correlations

    def _identify_amplification_factors(
        self,
        domain_scores: Dict[RiskDomain, float],
        correlations: Dict[str, float],
    ) -> List[str]:
        """Identify factors that amplify risk."""
        factors = []
        
        high_risk_domains = [d for d, s in domain_scores.items() if s >= 60]
        if len(high_risk_domains) >= 2:
            factors.append(f"Multiple high-risk domains: {', '.join(d.value for d in high_risk_domains)}")
        
        for pair, corr in correlations.items():
            if corr >= 0.6:
                d1, d2 = pair.split("-")
                if domain_scores.get(RiskDomain(d1), 0) >= 50 and domain_scores.get(RiskDomain(d2), 0) >= 50:
                    factors.append(f"Correlated risks in {d1} and {d2}")
        
        return factors

    def _identify_mitigation_factors(
        self,
        domain_scores: Dict[RiskDomain, float],
    ) -> List[str]:
        """Identify factors that mitigate risk."""
        factors = []
        
        low_risk_domains = [d for d, s in domain_scores.items() if s < 30]
        if low_risk_domains:
            factors.append(f"Low risk in: {', '.join(d.value for d in low_risk_domains)}")
        
        return factors

    def _detect_cross_domain_patterns(
        self,
        domain_scores: Dict[RiskDomain, float],
    ) -> List[Dict[str, Any]]:
        """Detect patterns across domains."""
        patterns = []
        
        if (domain_scores.get(RiskDomain.CYBER, 0) >= 60 and 
            domain_scores.get(RiskDomain.INFRASTRUCTURE, 0) >= 60):
            patterns.append({
                "pattern": "cyber_infrastructure_convergence",
                "description": "High cyber and infrastructure risks indicate potential coordinated attack",
                "severity": "high",
            })
        
        if (domain_scores.get(RiskDomain.GEOPOLITICAL, 0) >= 50 and 
            domain_scores.get(RiskDomain.ECONOMIC, 0) >= 50):
            patterns.append({
                "pattern": "geopolitical_economic_stress",
                "description": "Combined geopolitical and economic pressures",
                "severity": "elevated",
            })
        
        return patterns

    def _detect_anomalies(
        self,
        domain_scores: Dict[RiskDomain, float],
    ) -> List[str]:
        """Detect anomalies in risk patterns."""
        anomalies = []
        
        for domain, score in domain_scores.items():
            if score >= 80:
                anomalies.append(f"Extreme risk level in {domain.value}: {score}")
        
        return anomalies

    def generate_early_warning(
        self,
        title: str,
        description: str,
        urgency: AlertUrgency,
        domains_affected: List[RiskDomain],
        risk_score: float,
        probability: float,
        time_horizon_hours: int,
        indicators: List[str],
        potential_impacts: List[str],
        recommended_actions: List[str],
        source_signals: Optional[List[str]] = None,
        confidence_level: float = 0.7,
    ) -> EarlyWarningSignal:
        """Generate an early warning signal."""
        signal_id = f"ew-{uuid.uuid4().hex[:12]}"
        now = datetime.utcnow()
        
        signal = EarlyWarningSignal(
            signal_id=signal_id,
            title=title,
            description=description,
            urgency=urgency,
            domains_affected=domains_affected,
            risk_score=risk_score,
            probability=probability,
            time_horizon_hours=time_horizon_hours,
            indicators=indicators,
            potential_impacts=potential_impacts,
            recommended_actions=recommended_actions,
            related_signals=[],
            source_signals=source_signals or [],
            confidence_level=confidence_level,
            is_active=True,
            created_at=now,
            expires_at=now + timedelta(hours=time_horizon_hours),
            acknowledged=False,
            acknowledged_by=None,
        )
        
        self.early_warnings[signal_id] = signal
        return signal

    def get_early_warnings(
        self,
        urgency: Optional[AlertUrgency] = None,
        domain: Optional[RiskDomain] = None,
        active_only: bool = False,
        min_risk_score: float = 0,
        limit: int = 100,
    ) -> List[EarlyWarningSignal]:
        """Retrieve early warning signals with optional filtering."""
        warnings = list(self.early_warnings.values())
        
        if urgency:
            urgency_order = list(AlertUrgency)
            min_index = urgency_order.index(urgency)
            warnings = [w for w in warnings if urgency_order.index(w.urgency) >= min_index]
        
        if domain:
            warnings = [w for w in warnings if domain in w.domains_affected]
        
        if active_only:
            now = datetime.utcnow()
            warnings = [w for w in warnings if w.is_active and w.expires_at > now]
        
        warnings = [w for w in warnings if w.risk_score >= min_risk_score]
        
        warnings.sort(key=lambda x: (list(AlertUrgency).index(x.urgency), -x.risk_score), reverse=True)
        return warnings[:limit]

    def create_trend_prediction(
        self,
        domain: RiskDomain,
        current_score: float,
        prediction_horizon_hours: int = 24,
        key_factors: Optional[List[str]] = None,
    ) -> TrendPrediction:
        """Create a trend prediction for a domain."""
        prediction_id = f"tp-{uuid.uuid4().hex[:12]}"
        now = datetime.utcnow()
        
        trend = self._calculate_domain_trend(domain)
        predicted_score = self._forecast_score(current_score, prediction_horizon_hours)
        
        confidence = 0.9 - (prediction_horizon_hours / 720) * 0.4
        
        scenarios = self._generate_scenarios(domain, current_score, prediction_horizon_hours)
        
        prediction = TrendPrediction(
            prediction_id=prediction_id,
            domain=domain,
            current_score=current_score,
            predicted_score=predicted_score,
            prediction_horizon_hours=prediction_horizon_hours,
            confidence=confidence,
            trend_direction=trend,
            key_factors=key_factors or [],
            scenarios=scenarios,
            created_at=now,
        )
        
        self.trend_predictions[prediction_id] = prediction
        return prediction

    def _generate_scenarios(
        self,
        domain: RiskDomain,
        current_score: float,
        horizon_hours: int,
    ) -> List[Dict[str, Any]]:
        """Generate risk scenarios."""
        return [
            {
                "name": "best_case",
                "probability": 0.2,
                "score": max(0, current_score - 15),
                "description": "Significant improvement in conditions",
            },
            {
                "name": "baseline",
                "probability": 0.5,
                "score": current_score,
                "description": "Conditions remain stable",
            },
            {
                "name": "worst_case",
                "probability": 0.3,
                "score": min(100, current_score + 20),
                "description": "Deterioration of conditions",
            },
        ]

    def record_fusion_event(
        self,
        event_type: str,
        domain: RiskDomain,
        severity: float,
        description: str,
        impact_assessment: str = "",
        related_events: Optional[List[str]] = None,
    ) -> FusionEvent:
        """Record an event in the fusion timeline."""
        event_id = f"fe-{uuid.uuid4().hex[:12]}"
        
        event = FusionEvent(
            event_id=event_id,
            timestamp=datetime.utcnow(),
            event_type=event_type,
            domain=domain,
            severity=severity,
            description=description,
            impact_assessment=impact_assessment,
            related_events=related_events or [],
        )
        
        self.fusion_events[event_id] = event
        return event

    def get_fusion_timeline(
        self,
        domain: Optional[RiskDomain] = None,
        min_severity: float = 0,
        hours: int = 24,
        limit: int = 100,
    ) -> List[FusionEvent]:
        """Get fusion events timeline."""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        events = [e for e in self.fusion_events.values() if e.timestamp >= cutoff]
        
        if domain:
            events = [e for e in events if e.domain == domain]
        
        events = [e for e in events if e.severity >= min_severity]
        
        events.sort(key=lambda x: x.timestamp, reverse=True)
        return events[:limit]

    def get_latest_stability_score(self) -> Optional[NationalStabilityScore]:
        """Get the most recent stability score."""
        if not self.stability_scores:
            return None
        return max(self.stability_scores.values(), key=lambda x: x.timestamp)

    def acknowledge_warning(
        self,
        signal_id: str,
        acknowledged_by: str,
    ) -> bool:
        """Acknowledge an early warning signal."""
        warning = self.early_warnings.get(signal_id)
        if not warning:
            return False
        
        warning.acknowledged = True
        warning.acknowledged_by = acknowledged_by
        return True

    def get_metrics(self) -> Dict[str, Any]:
        """Get national risk fusion metrics."""
        latest_nss = self.get_latest_stability_score()
        active_warnings = self.get_early_warnings(active_only=True)
        
        urgency_distribution = {}
        for urgency in AlertUrgency:
            urgency_distribution[urgency.value] = len([
                w for w in active_warnings if w.urgency == urgency
            ])
        
        return {
            "total_stability_assessments": len(self.stability_scores),
            "latest_stability_score": latest_nss.overall_score if latest_nss else None,
            "latest_stability_level": latest_nss.stability_level.value if latest_nss else None,
            "current_trend": latest_nss.trend.value if latest_nss else None,
            "total_fusion_results": len(self.fusion_results),
            "total_early_warnings": len(self.early_warnings),
            "active_warnings": len(active_warnings),
            "unacknowledged_warnings": len([w for w in active_warnings if not w.acknowledged]),
            "total_trend_predictions": len(self.trend_predictions),
            "total_fusion_events": len(self.fusion_events),
            "urgency_distribution": urgency_distribution,
        }
