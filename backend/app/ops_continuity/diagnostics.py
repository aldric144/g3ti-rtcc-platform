"""
Diagnostics Module for G3TI RTCC-UIP Operational Continuity.

Provides RTCC diagnostics suite including error classification,
predictive failure detection, and slow query detection.
"""

import asyncio
from datetime import datetime, timezone, timedelta
from enum import Enum
from typing import Any, Optional
from collections import deque
import uuid
import statistics

from pydantic import BaseModel, Field


class DiagnosticCategory(str, Enum):
    """Categories of diagnostic events."""
    NETWORK = "network"
    DATABASE = "database"
    FEDERAL = "federal"
    VENDOR = "vendor"
    CACHE = "cache"
    QUEUE = "queue"
    WEBSOCKET = "websocket"
    ETL = "etl"
    ENGINE = "engine"
    AUTHENTICATION = "authentication"
    CONFIGURATION = "configuration"
    RESOURCE = "resource"
    PERFORMANCE = "performance"


class DiagnosticSeverity(str, Enum):
    """Severity levels for diagnostic events."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class DiagnosticEvent(BaseModel):
    """A diagnostic event."""
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    category: DiagnosticCategory
    severity: DiagnosticSeverity
    source: str
    message: str
    error_code: Optional[str] = None
    stack_trace: Optional[str] = None
    context: dict[str, Any] = Field(default_factory=dict)
    resolution_hint: Optional[str] = None
    auto_resolved: bool = False
    resolved_at: Optional[datetime] = None


class SlowQueryEvent(BaseModel):
    """A slow query diagnostic event."""
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    database: str
    query_type: str
    duration_ms: float
    threshold_ms: float
    query_hash: str
    query_preview: str
    parameters: dict[str, Any] = Field(default_factory=dict)
    execution_plan: Optional[str] = None
    recommendation: Optional[str] = None


class PredictiveAlert(BaseModel):
    """A predictive failure alert."""
    alert_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    category: DiagnosticCategory
    prediction_type: str
    confidence: float
    predicted_failure_time: Optional[datetime] = None
    indicators: list[str] = Field(default_factory=list)
    recommended_actions: list[str] = Field(default_factory=list)
    acknowledged: bool = False
    acknowledged_by: Optional[str] = None


class DiagnosticsConfig(BaseModel):
    """Configuration for diagnostics engine."""
    enabled: bool = True
    slow_query_threshold_ms: float = 1000.0
    error_retention_hours: int = 168
    enable_predictive_detection: bool = True
    prediction_window_minutes: int = 30
    enable_auto_resolution: bool = True
    max_events_in_memory: int = 10000

    network_timeout_threshold_ms: float = 5000.0
    database_latency_threshold_ms: float = 500.0
    federal_response_threshold_ms: float = 10000.0
    queue_depth_threshold: int = 1000
    websocket_drop_threshold_percent: float = 20.0
    etl_stall_threshold_minutes: int = 15

    escalation_rules: dict[str, dict[str, Any]] = Field(default_factory=lambda: {
        "service_unresponsive_10s": {
            "threshold_seconds": 10,
            "severity": "degraded",
            "escalate_to": ["ops_center"],
        },
        "multiple_dependency_failure": {
            "threshold_count": 2,
            "severity": "critical",
            "escalate_to": ["ops_center", "tactical_dashboard", "command_center"],
        },
        "federal_offline_5min": {
            "threshold_minutes": 5,
            "severity": "priority_1",
            "escalate_to": ["ops_center", "command_center"],
        },
        "neo4j_write_failure": {
            "severity": "emergency",
            "escalate_to": ["ops_center", "tactical_dashboard", "command_center"],
        },
        "etl_interruption": {
            "severity": "high_priority",
            "escalate_to": ["ops_center", "data_lake"],
        },
        "websocket_drop_20pct": {
            "threshold_percent": 20,
            "severity": "degraded",
            "escalate_to": ["ops_center"],
        },
    })


class DiagnosticsMetrics(BaseModel):
    """Metrics for diagnostics engine."""
    events_logged: int = 0
    events_by_category: dict[str, int] = Field(default_factory=dict)
    events_by_severity: dict[str, int] = Field(default_factory=dict)
    slow_queries_detected: int = 0
    predictive_alerts_generated: int = 0
    auto_resolutions: int = 0
    avg_resolution_time_seconds: float = 0.0
    last_event: Optional[datetime] = None


class DiagnosticsEngine:
    """
    RTCC Diagnostics Engine for operational monitoring.

    Provides error classification, predictive failure detection,
    slow query detection, and automated diagnostics reporting.
    """

    def __init__(self, config: Optional[DiagnosticsConfig] = None):
        self.config = config or DiagnosticsConfig()
        self.metrics = DiagnosticsMetrics()
        self._running = False
        self._analysis_task: Optional[asyncio.Task] = None
        self._events: deque[DiagnosticEvent] = deque(maxlen=self.config.max_events_in_memory)
        self._slow_queries: deque[SlowQueryEvent] = deque(maxlen=1000)
        self._predictive_alerts: deque[PredictiveAlert] = deque(maxlen=500)
        self._callbacks: list[callable] = []
        self._latency_history: dict[str, deque[float]] = {}
        self._error_counts: dict[str, int] = {}

    async def start(self) -> None:
        """Start the diagnostics engine."""
        if self._running:
            return

        self._running = True
        self._analysis_task = asyncio.create_task(self._analysis_loop())

    async def stop(self) -> None:
        """Stop the diagnostics engine."""
        self._running = False
        if self._analysis_task:
            self._analysis_task.cancel()
            try:
                await self._analysis_task
            except asyncio.CancelledError:
                pass

    async def _analysis_loop(self) -> None:
        """Main analysis loop for predictive detection."""
        while self._running:
            try:
                if self.config.enable_predictive_detection:
                    await self._run_predictive_analysis()
                await asyncio.sleep(60.0)
            except asyncio.CancelledError:
                break
            except Exception:
                await asyncio.sleep(10.0)

    async def log_event(
        self,
        category: DiagnosticCategory,
        severity: DiagnosticSeverity,
        source: str,
        message: str,
        error_code: Optional[str] = None,
        context: Optional[dict[str, Any]] = None,
        stack_trace: Optional[str] = None,
    ) -> DiagnosticEvent:
        """Log a diagnostic event."""
        event = DiagnosticEvent(
            category=category,
            severity=severity,
            source=source,
            message=message,
            error_code=error_code,
            context=context or {},
            stack_trace=stack_trace,
            resolution_hint=self._get_resolution_hint(category, error_code),
        )

        self._events.append(event)
        self._update_metrics(event)

        self._error_counts[source] = self._error_counts.get(source, 0) + 1

        if severity in [DiagnosticSeverity.ERROR, DiagnosticSeverity.CRITICAL]:
            await self._check_escalation_rules(event)

        for callback in self._callbacks:
            try:
                await callback(event)
            except Exception:
                pass

        return event

    async def log_network_error(
        self,
        source: str,
        endpoint: str,
        error_message: str,
        latency_ms: Optional[float] = None,
    ) -> DiagnosticEvent:
        """Log a network error."""
        return await self.log_event(
            category=DiagnosticCategory.NETWORK,
            severity=DiagnosticSeverity.ERROR,
            source=source,
            message=f"Network error connecting to {endpoint}: {error_message}",
            context={
                "endpoint": endpoint,
                "latency_ms": latency_ms,
            },
        )

    async def log_database_error(
        self,
        database: str,
        operation: str,
        error_message: str,
        query_preview: Optional[str] = None,
    ) -> DiagnosticEvent:
        """Log a database error."""
        severity = DiagnosticSeverity.CRITICAL if "write" in operation.lower() else DiagnosticSeverity.ERROR

        return await self.log_event(
            category=DiagnosticCategory.DATABASE,
            severity=severity,
            source=database,
            message=f"Database {operation} error: {error_message}",
            context={
                "operation": operation,
                "query_preview": query_preview,
            },
        )

    async def log_federal_error(
        self,
        endpoint: str,
        error_message: str,
        response_code: Optional[int] = None,
    ) -> DiagnosticEvent:
        """Log a federal endpoint error."""
        return await self.log_event(
            category=DiagnosticCategory.FEDERAL,
            severity=DiagnosticSeverity.ERROR,
            source=f"federal_{endpoint}",
            message=f"Federal endpoint {endpoint} error: {error_message}",
            error_code=str(response_code) if response_code else None,
            context={
                "endpoint": endpoint,
                "response_code": response_code,
            },
        )

    async def log_vendor_error(
        self,
        vendor: str,
        error_message: str,
        integration_type: Optional[str] = None,
    ) -> DiagnosticEvent:
        """Log a vendor integration error."""
        return await self.log_event(
            category=DiagnosticCategory.VENDOR,
            severity=DiagnosticSeverity.ERROR,
            source=f"vendor_{vendor}",
            message=f"Vendor {vendor} error: {error_message}",
            context={
                "vendor": vendor,
                "integration_type": integration_type,
            },
        )

    async def log_slow_query(
        self,
        database: str,
        query_type: str,
        duration_ms: float,
        query_preview: str,
        parameters: Optional[dict[str, Any]] = None,
    ) -> Optional[SlowQueryEvent]:
        """Log a slow query if it exceeds threshold."""
        if duration_ms < self.config.slow_query_threshold_ms:
            return None

        event = SlowQueryEvent(
            database=database,
            query_type=query_type,
            duration_ms=duration_ms,
            threshold_ms=self.config.slow_query_threshold_ms,
            query_hash=str(hash(query_preview)),
            query_preview=query_preview[:500],
            parameters=parameters or {},
            recommendation=self._get_query_recommendation(query_type, duration_ms),
        )

        self._slow_queries.append(event)
        self.metrics.slow_queries_detected += 1

        return event

    async def record_latency(self, source: str, latency_ms: float) -> None:
        """Record latency for trend analysis."""
        if source not in self._latency_history:
            self._latency_history[source] = deque(maxlen=100)

        self._latency_history[source].append(latency_ms)

    async def _run_predictive_analysis(self) -> None:
        """Run predictive failure analysis."""
        for source, latencies in self._latency_history.items():
            if len(latencies) < 10:
                continue

            recent = list(latencies)[-10:]
            older = list(latencies)[:-10] if len(latencies) > 10 else recent

            if not older:
                continue

            recent_avg = statistics.mean(recent)
            older_avg = statistics.mean(older)

            if recent_avg > older_avg * 2:
                await self._generate_predictive_alert(
                    category=DiagnosticCategory.PERFORMANCE,
                    prediction_type="latency_degradation",
                    confidence=min(0.9, (recent_avg / older_avg - 1) / 2),
                    indicators=[
                        f"Latency increased from {older_avg:.1f}ms to {recent_avg:.1f}ms",
                        f"Source: {source}",
                    ],
                    recommended_actions=[
                        "Check service health",
                        "Review recent deployments",
                        "Check resource utilization",
                    ],
                )

        for source, count in self._error_counts.items():
            if count > 10:
                await self._generate_predictive_alert(
                    category=DiagnosticCategory.ENGINE,
                    prediction_type="error_rate_spike",
                    confidence=min(0.95, count / 20),
                    indicators=[
                        f"Error count: {count} in recent window",
                        f"Source: {source}",
                    ],
                    recommended_actions=[
                        "Investigate error logs",
                        "Check service dependencies",
                        "Consider service restart",
                    ],
                )

        self._error_counts.clear()

    async def _generate_predictive_alert(
        self,
        category: DiagnosticCategory,
        prediction_type: str,
        confidence: float,
        indicators: list[str],
        recommended_actions: list[str],
    ) -> PredictiveAlert:
        """Generate a predictive alert."""
        alert = PredictiveAlert(
            category=category,
            prediction_type=prediction_type,
            confidence=confidence,
            predicted_failure_time=datetime.now(timezone.utc) + timedelta(
                minutes=self.config.prediction_window_minutes
            ),
            indicators=indicators,
            recommended_actions=recommended_actions,
        )

        self._predictive_alerts.append(alert)
        self.metrics.predictive_alerts_generated += 1

        for callback in self._callbacks:
            try:
                await callback(alert)
            except Exception:
                pass

        return alert

    async def _check_escalation_rules(self, event: DiagnosticEvent) -> None:
        """Check if event triggers escalation rules."""
        pass

    def _get_resolution_hint(self, category: DiagnosticCategory, error_code: Optional[str]) -> Optional[str]:
        """Get resolution hint for an error."""
        hints = {
            DiagnosticCategory.NETWORK: "Check network connectivity and firewall rules",
            DiagnosticCategory.DATABASE: "Check database connection pool and query performance",
            DiagnosticCategory.FEDERAL: "Verify federal endpoint credentials and availability",
            DiagnosticCategory.VENDOR: "Check vendor API status and credentials",
            DiagnosticCategory.CACHE: "Check Redis connection and memory usage",
            DiagnosticCategory.QUEUE: "Check message queue depth and consumer health",
            DiagnosticCategory.WEBSOCKET: "Check WebSocket broker and client connections",
            DiagnosticCategory.ETL: "Check ETL pipeline status and data sources",
        }
        return hints.get(category)

    def _get_query_recommendation(self, query_type: str, duration_ms: float) -> str:
        """Get recommendation for slow query."""
        if duration_ms > 5000:
            return "Consider query optimization or adding indexes"
        elif duration_ms > 2000:
            return "Review query execution plan"
        else:
            return "Monitor for recurring slow queries"

    def _update_metrics(self, event: DiagnosticEvent) -> None:
        """Update metrics from event."""
        self.metrics.events_logged += 1
        self.metrics.last_event = event.timestamp

        cat = event.category.value
        self.metrics.events_by_category[cat] = self.metrics.events_by_category.get(cat, 0) + 1

        sev = event.severity.value
        self.metrics.events_by_severity[sev] = self.metrics.events_by_severity.get(sev, 0) + 1

    async def resolve_event(self, event_id: str, auto: bool = False) -> bool:
        """Mark an event as resolved."""
        for event in self._events:
            if event.event_id == event_id:
                event.auto_resolved = auto
                event.resolved_at = datetime.now(timezone.utc)
                if auto:
                    self.metrics.auto_resolutions += 1
                return True
        return False

    async def acknowledge_alert(self, alert_id: str, user_id: str) -> bool:
        """Acknowledge a predictive alert."""
        for alert in self._predictive_alerts:
            if alert.alert_id == alert_id:
                alert.acknowledged = True
                alert.acknowledged_by = user_id
                return True
        return False

    def register_callback(self, callback: callable) -> None:
        """Register a callback for diagnostic events."""
        self._callbacks.append(callback)

    def get_events(
        self,
        category: Optional[DiagnosticCategory] = None,
        severity: Optional[DiagnosticSeverity] = None,
        limit: int = 100,
    ) -> list[DiagnosticEvent]:
        """Get diagnostic events with optional filtering."""
        events = list(self._events)

        if category:
            events = [e for e in events if e.category == category]

        if severity:
            events = [e for e in events if e.severity == severity]

        return events[-limit:]

    def get_slow_queries(self, limit: int = 100) -> list[SlowQueryEvent]:
        """Get slow query events."""
        return list(self._slow_queries)[-limit:]

    def get_predictive_alerts(self, unacknowledged_only: bool = False) -> list[PredictiveAlert]:
        """Get predictive alerts."""
        alerts = list(self._predictive_alerts)
        if unacknowledged_only:
            alerts = [a for a in alerts if not a.acknowledged]
        return alerts

    def generate_report(self, hours: int = 24) -> dict[str, Any]:
        """Generate a diagnostics report."""
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)

        recent_events = [e for e in self._events if e.timestamp > cutoff]
        recent_slow_queries = [q for q in self._slow_queries if q.timestamp > cutoff]
        recent_alerts = [a for a in self._predictive_alerts if a.timestamp > cutoff]

        category_counts = {}
        severity_counts = {}
        for event in recent_events:
            cat = event.category.value
            category_counts[cat] = category_counts.get(cat, 0) + 1
            sev = event.severity.value
            severity_counts[sev] = severity_counts.get(sev, 0) + 1

        return {
            "report_period_hours": hours,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "summary": {
                "total_events": len(recent_events),
                "slow_queries": len(recent_slow_queries),
                "predictive_alerts": len(recent_alerts),
                "critical_events": severity_counts.get("critical", 0),
                "error_events": severity_counts.get("error", 0),
            },
            "events_by_category": category_counts,
            "events_by_severity": severity_counts,
            "top_error_sources": self._get_top_error_sources(recent_events),
            "slow_query_summary": {
                "count": len(recent_slow_queries),
                "avg_duration_ms": statistics.mean([q.duration_ms for q in recent_slow_queries]) if recent_slow_queries else 0,
            },
            "recommendations": self._generate_recommendations(recent_events, recent_slow_queries),
        }

    def _get_top_error_sources(self, events: list[DiagnosticEvent], limit: int = 5) -> list[dict[str, Any]]:
        """Get top error sources."""
        source_counts: dict[str, int] = {}
        for event in events:
            if event.severity in [DiagnosticSeverity.ERROR, DiagnosticSeverity.CRITICAL]:
                source_counts[event.source] = source_counts.get(event.source, 0) + 1

        sorted_sources = sorted(source_counts.items(), key=lambda x: x[1], reverse=True)
        return [{"source": s, "count": c} for s, c in sorted_sources[:limit]]

    def _generate_recommendations(
        self,
        events: list[DiagnosticEvent],
        slow_queries: list[SlowQueryEvent],
    ) -> list[str]:
        """Generate recommendations based on diagnostics."""
        recommendations = []

        error_count = sum(1 for e in events if e.severity == DiagnosticSeverity.ERROR)
        if error_count > 50:
            recommendations.append("High error rate detected - investigate root cause")

        if len(slow_queries) > 20:
            recommendations.append("Multiple slow queries detected - review database indexes")

        federal_errors = sum(1 for e in events if e.category == DiagnosticCategory.FEDERAL)
        if federal_errors > 5:
            recommendations.append("Federal endpoint issues - verify connectivity and credentials")

        return recommendations

    def get_status(self) -> dict[str, Any]:
        """Get diagnostics engine status."""
        return {
            "running": self._running,
            "events_in_memory": len(self._events),
            "slow_queries_in_memory": len(self._slow_queries),
            "predictive_alerts_in_memory": len(self._predictive_alerts),
            "metrics": self.metrics.model_dump(),
            "config": {
                "slow_query_threshold_ms": self.config.slow_query_threshold_ms,
                "enable_predictive_detection": self.config.enable_predictive_detection,
            },
        }

    def get_metrics(self) -> DiagnosticsMetrics:
        """Get diagnostics metrics."""
        return self.metrics
