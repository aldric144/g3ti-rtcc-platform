"""
Bias Safeguard Engine.

Provides bias detection, fairness monitoring, and transparent audit logging
for all predictive AI operations.
"""

import uuid
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Callable, Optional
from collections import deque
from pydantic import BaseModel, Field


class BiasCategory(str, Enum):
    """Categories of potential bias."""
    GEOGRAPHIC = "geographic"
    TEMPORAL = "temporal"
    SOCIOECONOMIC = "socioeconomic"
    HISTORICAL = "historical"
    ALGORITHMIC = "algorithmic"
    DATA_QUALITY = "data_quality"
    SAMPLING = "sampling"


class FairnessMetricType(str, Enum):
    """Types of fairness metrics."""
    GEOGRAPHIC_PARITY = "geographic_parity"
    TEMPORAL_CONSISTENCY = "temporal_consistency"
    PREDICTION_CALIBRATION = "prediction_calibration"
    FALSE_POSITIVE_RATE = "false_positive_rate"
    FALSE_NEGATIVE_RATE = "false_negative_rate"
    COVERAGE_EQUITY = "coverage_equity"
    RESOURCE_DISTRIBUTION = "resource_distribution"


class AlertSeverity(str, Enum):
    """Severity levels for bias alerts."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AuditAction(str, Enum):
    """Types of auditable actions."""
    PREDICTION_GENERATED = "prediction_generated"
    RISK_CALCULATED = "risk_calculated"
    PATROL_OPTIMIZED = "patrol_optimized"
    CLUSTER_IDENTIFIED = "cluster_identified"
    TRAJECTORY_PREDICTED = "trajectory_predicted"
    MODEL_UPDATED = "model_updated"
    FACTOR_ADDED = "factor_added"
    FACTOR_REMOVED = "factor_removed"
    MANUAL_OVERRIDE = "manual_override"
    BIAS_DETECTED = "bias_detected"
    FAIRNESS_CHECK = "fairness_check"


class AuditRecord(BaseModel):
    """Audit record for predictive AI operations."""
    record_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    action: AuditAction
    module: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    input_data: dict[str, Any] = Field(default_factory=dict)
    output_data: dict[str, Any] = Field(default_factory=dict)
    factors_used: list[str] = Field(default_factory=list)
    excluded_factors: list[str] = Field(default_factory=list)
    confidence_score: Optional[float] = None
    bias_flags: list[str] = Field(default_factory=list)
    fairness_scores: dict[str, float] = Field(default_factory=dict)
    justification: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)


class BiasMetric(BaseModel):
    """Metric for measuring bias."""
    metric_id: str
    category: BiasCategory
    name: str
    description: str = ""
    value: float = 0.0
    threshold: float = 0.0
    exceeds_threshold: bool = False
    trend: str = "stable"
    measured_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    zone_id: Optional[str] = None
    time_period: Optional[str] = None
    sample_size: int = 0
    metadata: dict[str, Any] = Field(default_factory=dict)


class BiasAlert(BaseModel):
    """Alert for detected bias."""
    alert_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    category: BiasCategory
    severity: AlertSeverity
    metric_id: str
    metric_value: float
    threshold: float
    message: str
    affected_zones: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    acknowledged: bool = False
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class FairnessReport(BaseModel):
    """Fairness assessment report."""
    report_id: str
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    period_start: datetime
    period_end: datetime
    overall_fairness_score: float = 0.0
    metrics: list[BiasMetric] = Field(default_factory=list)
    alerts: list[BiasAlert] = Field(default_factory=list)
    zone_scores: dict[str, float] = Field(default_factory=dict)
    recommendations: list[str] = Field(default_factory=list)
    excluded_factors: list[str] = Field(default_factory=list)
    audit_summary: dict[str, int] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ProhibitedFactor(BaseModel):
    """Factor that is prohibited from use in predictions."""
    factor_id: str
    name: str
    category: str
    reason: str
    added_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    added_by: str = "system"


class SafeguardConfig(BaseModel):
    """Configuration for bias safeguard engine."""
    max_audit_records: int = 1000000
    max_alerts: int = 10000
    geographic_parity_threshold: float = 0.3
    temporal_consistency_threshold: float = 0.2
    false_positive_threshold: float = 0.15
    coverage_equity_threshold: float = 0.25
    audit_retention_days: int = 365
    prohibited_factors: list[str] = Field(default_factory=lambda: [
        "race",
        "ethnicity",
        "religion",
        "national_origin",
        "gender",
        "sexual_orientation",
        "disability",
        "age",
        "income_level",
        "education_level",
        "employment_status",
        "housing_status",
        "family_status",
        "political_affiliation",
    ])


class SafeguardMetrics(BaseModel):
    """Metrics for bias safeguard engine."""
    total_audit_records: int = 0
    records_by_action: dict[str, int] = Field(default_factory=dict)
    total_bias_alerts: int = 0
    active_alerts: int = 0
    alerts_by_category: dict[str, int] = Field(default_factory=dict)
    avg_fairness_score: float = 0.0
    prohibited_factor_violations: int = 0


class BiasSafeguardEngine:
    """
    Bias Safeguard Engine.
    
    Provides bias detection, fairness monitoring, and transparent audit logging
    for all predictive AI operations.
    """
    
    def __init__(self, config: Optional[SafeguardConfig] = None):
        self.config = config or SafeguardConfig()
        self._audit_records: deque[AuditRecord] = deque(maxlen=self.config.max_audit_records)
        self._alerts: deque[BiasAlert] = deque(maxlen=self.config.max_alerts)
        self._metrics: dict[str, BiasMetric] = {}
        self._prohibited_factors: dict[str, ProhibitedFactor] = {}
        self._callbacks: list[Callable] = []
        self._running = False
        self._engine_metrics = SafeguardMetrics()
        
        self._initialize_prohibited_factors()
    
    def _initialize_prohibited_factors(self) -> None:
        """Initialize prohibited factors from config."""
        for factor in self.config.prohibited_factors:
            self._prohibited_factors[factor] = ProhibitedFactor(
                factor_id=f"prohibited-{uuid.uuid4().hex[:8]}",
                name=factor,
                category="identity",
                reason="Protected characteristic - prohibited by policy",
            )
    
    async def start(self) -> None:
        """Start the bias safeguard engine."""
        self._running = True
    
    async def stop(self) -> None:
        """Stop the bias safeguard engine."""
        self._running = False
    
    def log_audit(
        self,
        action: AuditAction,
        module: str,
        input_data: Optional[dict[str, Any]] = None,
        output_data: Optional[dict[str, Any]] = None,
        factors_used: Optional[list[str]] = None,
        confidence_score: Optional[float] = None,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        justification: str = "",
        metadata: Optional[dict[str, Any]] = None,
    ) -> AuditRecord:
        """Log an audit record for a predictive AI operation."""
        factors = factors_used or []
        excluded = []
        bias_flags = []
        
        for factor in factors:
            if factor.lower() in self._prohibited_factors:
                excluded.append(factor)
                bias_flags.append(f"Prohibited factor detected: {factor}")
                self._engine_metrics.prohibited_factor_violations += 1
        
        record = AuditRecord(
            record_id=f"audit-{uuid.uuid4().hex[:12]}",
            action=action,
            module=module,
            user_id=user_id,
            session_id=session_id,
            input_data=input_data or {},
            output_data=output_data or {},
            factors_used=[f for f in factors if f.lower() not in self._prohibited_factors],
            excluded_factors=excluded,
            confidence_score=confidence_score,
            bias_flags=bias_flags,
            justification=justification,
            metadata=metadata or {},
        )
        
        self._audit_records.append(record)
        self._update_metrics()
        
        return record
    
    def get_audit_records(
        self,
        action: Optional[AuditAction] = None,
        module: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100,
    ) -> list[AuditRecord]:
        """Get audit records with optional filters."""
        records = list(self._audit_records)
        
        if action:
            records = [r for r in records if r.action == action]
        
        if module:
            records = [r for r in records if r.module == module]
        
        if start_time:
            records = [r for r in records if r.timestamp >= start_time]
        
        if end_time:
            records = [r for r in records if r.timestamp <= end_time]
        
        records.reverse()
        return records[:limit]
    
    def is_factor_allowed(self, factor_name: str) -> bool:
        """Check if a factor is allowed for use in predictions."""
        return factor_name.lower() not in self._prohibited_factors
    
    def filter_prohibited_factors(
        self,
        factors: list[str],
    ) -> tuple[list[str], list[str]]:
        """Filter out prohibited factors and return allowed and excluded lists."""
        allowed = []
        excluded = []
        
        for factor in factors:
            if self.is_factor_allowed(factor):
                allowed.append(factor)
            else:
                excluded.append(factor)
        
        return allowed, excluded
    
    def add_prohibited_factor(
        self,
        name: str,
        category: str,
        reason: str,
        added_by: str = "admin",
    ) -> ProhibitedFactor:
        """Add a new prohibited factor."""
        factor = ProhibitedFactor(
            factor_id=f"prohibited-{uuid.uuid4().hex[:8]}",
            name=name.lower(),
            category=category,
            reason=reason,
            added_by=added_by,
        )
        
        self._prohibited_factors[name.lower()] = factor
        return factor
    
    def get_prohibited_factors(self) -> list[ProhibitedFactor]:
        """Get all prohibited factors."""
        return list(self._prohibited_factors.values())
    
    async def measure_geographic_parity(
        self,
        zone_predictions: dict[str, int],
        zone_populations: dict[str, int],
    ) -> BiasMetric:
        """Measure geographic parity in predictions."""
        if not zone_predictions or not zone_populations:
            return BiasMetric(
                metric_id=f"metric-{uuid.uuid4().hex[:8]}",
                category=BiasCategory.GEOGRAPHIC,
                name="Geographic Parity",
                value=1.0,
                threshold=self.config.geographic_parity_threshold,
            )
        
        rates = []
        for zone_id in zone_predictions:
            if zone_id in zone_populations and zone_populations[zone_id] > 0:
                rate = zone_predictions[zone_id] / zone_populations[zone_id]
                rates.append(rate)
        
        if not rates:
            disparity = 0.0
        else:
            avg_rate = sum(rates) / len(rates)
            if avg_rate > 0:
                disparity = max(abs(r - avg_rate) / avg_rate for r in rates)
            else:
                disparity = 0.0
        
        metric = BiasMetric(
            metric_id=f"metric-{uuid.uuid4().hex[:8]}",
            category=BiasCategory.GEOGRAPHIC,
            name="Geographic Parity",
            description="Measures disparity in prediction rates across zones",
            value=disparity,
            threshold=self.config.geographic_parity_threshold,
            exceeds_threshold=disparity > self.config.geographic_parity_threshold,
            sample_size=len(rates),
        )
        
        self._metrics[metric.metric_id] = metric
        
        if metric.exceeds_threshold:
            await self._create_bias_alert(metric)
        
        return metric
    
    async def measure_temporal_consistency(
        self,
        predictions_by_period: dict[str, int],
    ) -> BiasMetric:
        """Measure temporal consistency in predictions."""
        if not predictions_by_period or len(predictions_by_period) < 2:
            return BiasMetric(
                metric_id=f"metric-{uuid.uuid4().hex[:8]}",
                category=BiasCategory.TEMPORAL,
                name="Temporal Consistency",
                value=0.0,
                threshold=self.config.temporal_consistency_threshold,
            )
        
        values = list(predictions_by_period.values())
        avg = sum(values) / len(values)
        
        if avg > 0:
            variance = sum((v - avg) ** 2 for v in values) / len(values)
            cv = (variance ** 0.5) / avg
        else:
            cv = 0.0
        
        metric = BiasMetric(
            metric_id=f"metric-{uuid.uuid4().hex[:8]}",
            category=BiasCategory.TEMPORAL,
            name="Temporal Consistency",
            description="Measures variation in prediction rates over time",
            value=cv,
            threshold=self.config.temporal_consistency_threshold,
            exceeds_threshold=cv > self.config.temporal_consistency_threshold,
            sample_size=len(values),
        )
        
        self._metrics[metric.metric_id] = metric
        
        if metric.exceeds_threshold:
            await self._create_bias_alert(metric)
        
        return metric
    
    async def measure_false_positive_rate(
        self,
        predictions: int,
        actual_incidents: int,
    ) -> BiasMetric:
        """Measure false positive rate."""
        if predictions == 0:
            fpr = 0.0
        else:
            fpr = max(0, predictions - actual_incidents) / predictions
        
        metric = BiasMetric(
            metric_id=f"metric-{uuid.uuid4().hex[:8]}",
            category=BiasCategory.ALGORITHMIC,
            name="False Positive Rate",
            description="Rate of predictions that did not result in incidents",
            value=fpr,
            threshold=self.config.false_positive_threshold,
            exceeds_threshold=fpr > self.config.false_positive_threshold,
            sample_size=predictions,
        )
        
        self._metrics[metric.metric_id] = metric
        
        if metric.exceeds_threshold:
            await self._create_bias_alert(metric)
        
        return metric
    
    async def measure_coverage_equity(
        self,
        zone_coverage: dict[str, float],
    ) -> BiasMetric:
        """Measure equity in patrol coverage across zones."""
        if not zone_coverage:
            return BiasMetric(
                metric_id=f"metric-{uuid.uuid4().hex[:8]}",
                category=BiasCategory.GEOGRAPHIC,
                name="Coverage Equity",
                value=0.0,
                threshold=self.config.coverage_equity_threshold,
            )
        
        values = list(zone_coverage.values())
        avg = sum(values) / len(values)
        
        if avg > 0:
            max_deviation = max(abs(v - avg) / avg for v in values)
        else:
            max_deviation = 0.0
        
        metric = BiasMetric(
            metric_id=f"metric-{uuid.uuid4().hex[:8]}",
            category=BiasCategory.GEOGRAPHIC,
            name="Coverage Equity",
            description="Measures equity in patrol coverage across zones",
            value=max_deviation,
            threshold=self.config.coverage_equity_threshold,
            exceeds_threshold=max_deviation > self.config.coverage_equity_threshold,
            sample_size=len(values),
        )
        
        self._metrics[metric.metric_id] = metric
        
        if metric.exceeds_threshold:
            await self._create_bias_alert(metric)
        
        return metric
    
    async def _create_bias_alert(self, metric: BiasMetric) -> BiasAlert:
        """Create a bias alert for a metric that exceeds threshold."""
        severity = AlertSeverity.WARNING
        if metric.value > metric.threshold * 1.5:
            severity = AlertSeverity.CRITICAL
        
        recommendations = self._generate_recommendations(metric)
        
        alert = BiasAlert(
            alert_id=f"alert-{uuid.uuid4().hex[:8]}",
            category=metric.category,
            severity=severity,
            metric_id=metric.metric_id,
            metric_value=metric.value,
            threshold=metric.threshold,
            message=f"{metric.name} ({metric.value:.2f}) exceeds threshold ({metric.threshold:.2f})",
            recommendations=recommendations,
        )
        
        self._alerts.append(alert)
        self._update_metrics()
        
        await self._notify_callbacks(alert, "bias_alert")
        
        return alert
    
    def _generate_recommendations(self, metric: BiasMetric) -> list[str]:
        """Generate recommendations for addressing bias."""
        recommendations = []
        
        if metric.category == BiasCategory.GEOGRAPHIC:
            recommendations.append("Review geographic distribution of risk factors")
            recommendations.append("Consider adjusting zone boundaries or weights")
            recommendations.append("Audit historical data for geographic bias")
        
        elif metric.category == BiasCategory.TEMPORAL:
            recommendations.append("Review temporal patterns in training data")
            recommendations.append("Consider seasonal adjustments to models")
            recommendations.append("Verify data collection consistency over time")
        
        elif metric.category == BiasCategory.ALGORITHMIC:
            recommendations.append("Review model calibration and thresholds")
            recommendations.append("Consider additional validation data")
            recommendations.append("Audit feature importance for bias indicators")
        
        recommendations.append("Document findings and remediation steps")
        recommendations.append("Schedule follow-up fairness assessment")
        
        return recommendations
    
    def acknowledge_alert(
        self,
        alert_id: str,
        acknowledged_by: str,
    ) -> bool:
        """Acknowledge a bias alert."""
        for alert in self._alerts:
            if alert.alert_id == alert_id:
                alert.acknowledged = True
                alert.acknowledged_by = acknowledged_by
                alert.acknowledged_at = datetime.now(timezone.utc)
                self._update_metrics()
                return True
        return False
    
    def resolve_alert(
        self,
        alert_id: str,
    ) -> bool:
        """Resolve a bias alert."""
        for alert in self._alerts:
            if alert.alert_id == alert_id:
                alert.resolved = True
                alert.resolved_at = datetime.now(timezone.utc)
                self._update_metrics()
                return True
        return False
    
    def get_active_alerts(self) -> list[BiasAlert]:
        """Get active (unresolved) alerts."""
        return [a for a in self._alerts if not a.resolved]
    
    def get_alerts(
        self,
        category: Optional[BiasCategory] = None,
        severity: Optional[AlertSeverity] = None,
        limit: int = 100,
    ) -> list[BiasAlert]:
        """Get alerts with optional filters."""
        alerts = list(self._alerts)
        
        if category:
            alerts = [a for a in alerts if a.category == category]
        
        if severity:
            alerts = [a for a in alerts if a.severity == severity]
        
        alerts.reverse()
        return alerts[:limit]
    
    async def generate_fairness_report(
        self,
        period_days: int = 30,
    ) -> FairnessReport:
        """Generate a comprehensive fairness report."""
        now = datetime.now(timezone.utc)
        start = now - timedelta(days=period_days)
        
        recent_records = [
            r for r in self._audit_records
            if r.timestamp >= start
        ]
        
        recent_alerts = [
            a for a in self._alerts
            if a.timestamp >= start
        ]
        
        recent_metrics = [
            m for m in self._metrics.values()
            if m.measured_at >= start
        ]
        
        action_counts: dict[str, int] = {}
        for record in recent_records:
            action_counts[record.action.value] = action_counts.get(record.action.value, 0) + 1
        
        if recent_metrics:
            avg_fairness = 1.0 - (
                sum(m.value for m in recent_metrics if m.exceeds_threshold)
                / len(recent_metrics)
            )
        else:
            avg_fairness = 1.0
        
        recommendations = []
        if len([a for a in recent_alerts if a.severity == AlertSeverity.CRITICAL]) > 0:
            recommendations.append("Address critical bias alerts immediately")
        
        if self._engine_metrics.prohibited_factor_violations > 0:
            recommendations.append("Review and remove prohibited factors from data sources")
        
        if avg_fairness < 0.8:
            recommendations.append("Conduct comprehensive bias audit of predictive models")
        
        report = FairnessReport(
            report_id=f"report-{uuid.uuid4().hex[:8]}",
            period_start=start,
            period_end=now,
            overall_fairness_score=avg_fairness,
            metrics=recent_metrics,
            alerts=recent_alerts,
            recommendations=recommendations,
            excluded_factors=list(self._prohibited_factors.keys()),
            audit_summary=action_counts,
        )
        
        self.log_audit(
            action=AuditAction.FAIRNESS_CHECK,
            module="bias_safeguards",
            output_data={"report_id": report.report_id, "fairness_score": avg_fairness},
            justification="Automated fairness report generation",
        )
        
        return report
    
    def get_metrics(self) -> SafeguardMetrics:
        """Get safeguard metrics."""
        return self._engine_metrics
    
    def get_status(self) -> dict[str, Any]:
        """Get engine status."""
        return {
            "running": self._running,
            "total_audit_records": len(self._audit_records),
            "total_alerts": len(self._alerts),
            "active_alerts": len(self.get_active_alerts()),
            "prohibited_factors": len(self._prohibited_factors),
            "metrics": self._engine_metrics.model_dump(),
        }
    
    def register_callback(self, callback: Callable) -> None:
        """Register a callback for safeguard events."""
        if callback not in self._callbacks:
            self._callbacks.append(callback)
    
    def unregister_callback(self, callback: Callable) -> None:
        """Unregister a callback."""
        if callback in self._callbacks:
            self._callbacks.remove(callback)
    
    def _update_metrics(self) -> None:
        """Update safeguard metrics."""
        action_counts: dict[str, int] = {}
        for record in self._audit_records:
            action_counts[record.action.value] = action_counts.get(record.action.value, 0) + 1
        
        category_counts: dict[str, int] = {}
        active = 0
        for alert in self._alerts:
            category_counts[alert.category.value] = category_counts.get(alert.category.value, 0) + 1
            if not alert.resolved:
                active += 1
        
        recent_metrics = list(self._metrics.values())[-100:]
        if recent_metrics:
            avg_fairness = 1.0 - (
                sum(1 for m in recent_metrics if m.exceeds_threshold)
                / len(recent_metrics)
            )
        else:
            avg_fairness = 1.0
        
        self._engine_metrics.total_audit_records = len(self._audit_records)
        self._engine_metrics.records_by_action = action_counts
        self._engine_metrics.total_bias_alerts = len(self._alerts)
        self._engine_metrics.active_alerts = active
        self._engine_metrics.alerts_by_category = category_counts
        self._engine_metrics.avg_fairness_score = avg_fairness
    
    async def _notify_callbacks(self, data: Any, event_type: str) -> None:
        """Notify registered callbacks."""
        for callback in self._callbacks:
            try:
                if callable(callback):
                    result = callback(data, event_type)
                    if hasattr(result, "__await__"):
                        await result
            except Exception:
                pass
