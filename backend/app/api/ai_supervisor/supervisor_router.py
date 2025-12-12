"""
AI Supervisor API Router

REST API endpoints for the AI Sentinel Supervisor system:
- System health and monitoring
- Auto-correction management
- Ethics and compliance validation
- Sentinel decision engine
- Alert management
- Recommendation handling
"""

from datetime import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from backend.app.ai_supervisor.system_monitor import (
    SystemMonitor,
    EngineType,
    HealthStatus,
    AlertSeverity,
    IssueType,
)
from backend.app.ai_supervisor.auto_corrector import (
    AutoCorrector,
    CorrectionType,
    CorrectionPriority,
)
from backend.app.ai_supervisor.ethics_guard import (
    EthicsGuard,
    ViolationSeverity,
    ActionDecision,
)
from backend.app.ai_supervisor.sentinel_engine import (
    SentinelEngine,
    AlertPriority,
    AlertSource,
    AutonomyLevel,
    RecommendationType,
)

router = APIRouter(prefix="/api/supervisor", tags=["AI Supervisor"])


system_monitor = SystemMonitor()
auto_corrector = AutoCorrector()
ethics_guard = EthicsGuard()
sentinel_engine = SentinelEngine()


class EngineMetricsUpdate(BaseModel):
    """Request model for updating engine metrics."""
    engine_type: str
    cpu_percent: Optional[float] = None
    memory_percent: Optional[float] = None
    gpu_percent: Optional[float] = None
    queue_depth: Optional[int] = None
    active_tasks: Optional[int] = None
    latency_ms: Optional[float] = None
    error_rate: Optional[float] = None
    throughput_per_sec: Optional[float] = None


class DataCorruptionCheck(BaseModel):
    """Request model for data corruption check."""
    engine_type: str
    data_source: str
    expected_checksum: str
    actual_checksum: str


class FeedbackLoopDetection(BaseModel):
    """Request model for feedback loop detection."""
    source_engine: str
    target_engine: str
    cycle_time_ms: float
    amplification_factor: float


class OverloadPredictionRequest(BaseModel):
    """Request model for overload prediction."""
    engine_type: str
    time_horizon_hours: int = 24


class CorrectionActionRequest(BaseModel):
    """Request model for creating a correction action."""
    correction_type: str
    target_engine: str
    target_component: str
    priority: str
    description: str
    parameters: dict = Field(default_factory=dict)
    estimated_duration_seconds: int = 60


class PipelineRepairRequest(BaseModel):
    """Request model for pipeline repair."""
    pipeline_id: str


class ServiceRestartRequest(BaseModel):
    """Request model for service restart."""
    engine: str
    service_name: str
    force: bool = False


class CacheRebuildRequest(BaseModel):
    """Request model for cache rebuild."""
    engine: str
    cache_name: str


class LoadRebalanceRequest(BaseModel):
    """Request model for load rebalancing."""
    source_engine: str
    target_engine: str
    load_percent: float


class ModelDriftCheckRequest(BaseModel):
    """Request model for model drift check."""
    model_name: str
    engine: str
    baseline_metrics: dict
    current_metrics: dict


class DataFeedRecoveryRequest(BaseModel):
    """Request model for data feed recovery."""
    engine: str
    feed_name: str
    fallback_source: Optional[str] = None


class ActionValidationRequest(BaseModel):
    """Request model for action validation."""
    action_type: str
    engine: str
    target: str
    parameters: dict = Field(default_factory=dict)
    warrant_obtained: bool = False
    human_approved: bool = False
    approved_by: Optional[str] = None


class BiasAuditRequest(BaseModel):
    """Request model for bias audit."""
    engine: str
    model_name: str
    predictions: list = Field(default_factory=list)


class ViolationReviewRequest(BaseModel):
    """Request model for violation review."""
    violation_id: str
    reviewed_by: str
    decision: str


class AlertConsolidationRequest(BaseModel):
    """Request model for alert consolidation."""
    sources: list[str]
    title: str
    description: str
    affected_systems: list[str]
    affected_areas: list[str]
    metrics: dict = Field(default_factory=dict)
    severity_score: float


class AutonomousActionRequest(BaseModel):
    """Request model for autonomous action request."""
    source_engine: str
    action_type: str
    autonomy_level: int
    target: str
    parameters: dict = Field(default_factory=dict)
    justification: str
    risk_score: float


class CascadePredictionRequest(BaseModel):
    """Request model for cascade prediction."""
    trigger_event: str
    trigger_source: str
    initial_severity: float
    time_horizon_hours: int = 24


class RecommendationRequest(BaseModel):
    """Request model for creating a recommendation."""
    recommendation_type: str
    priority: int
    title: str
    description: str
    rationale: str
    affected_systems: list[str]
    implementation_steps: list[str]
    expected_outcome: str
    risk_if_ignored: str
    deadline_hours: Optional[int] = None


class AlertAcknowledgeRequest(BaseModel):
    """Request model for acknowledging an alert."""
    alert_id: str
    acknowledged_by: str


class AlertResolveRequest(BaseModel):
    """Request model for resolving an alert."""
    alert_id: str
    resolution_notes: str


class CommandAlertAcknowledgeRequest(BaseModel):
    """Request model for acknowledging a command alert."""
    alert_id: str
    response: str


@router.get("/health")
async def get_system_health():
    """Get overall system health status."""
    return system_monitor.get_system_health_summary()


@router.get("/system-load")
async def get_system_load():
    """Get current system load across all engines."""
    metrics = system_monitor.get_all_engine_metrics()
    return {
        "engines": [
            {
                "engine_type": m.engine_type.value,
                "cpu_percent": m.cpu_percent,
                "memory_percent": m.memory_percent,
                "gpu_percent": m.gpu_percent,
                "queue_depth": m.queue_depth,
                "latency_ms": m.latency_ms,
                "status": m.status.value,
            }
            for m in metrics
        ],
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/engines")
async def get_all_engines():
    """Get metrics for all monitored engines."""
    metrics = system_monitor.get_all_engine_metrics()
    return {
        "engines": [
            {
                "engine_type": m.engine_type.value,
                "cpu_percent": m.cpu_percent,
                "memory_percent": m.memory_percent,
                "gpu_percent": m.gpu_percent,
                "queue_depth": m.queue_depth,
                "active_tasks": m.active_tasks,
                "latency_ms": m.latency_ms,
                "error_rate": m.error_rate,
                "throughput_per_sec": m.throughput_per_sec,
                "uptime_seconds": m.uptime_seconds,
                "status": m.status.value,
                "version": m.version,
                "instance_count": m.instance_count,
                "last_heartbeat": m.last_heartbeat.isoformat(),
            }
            for m in metrics
        ],
        "total": len(metrics),
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/engines/{engine_type}")
async def get_engine_metrics(engine_type: str):
    """Get metrics for a specific engine."""
    try:
        engine = EngineType(engine_type)
        metrics = system_monitor.get_engine_metrics(engine)
        if not metrics:
            raise HTTPException(status_code=404, detail="Engine not found")
        return {
            "engine_type": metrics.engine_type.value,
            "cpu_percent": metrics.cpu_percent,
            "memory_percent": metrics.memory_percent,
            "gpu_percent": metrics.gpu_percent,
            "queue_depth": metrics.queue_depth,
            "active_tasks": metrics.active_tasks,
            "latency_ms": metrics.latency_ms,
            "error_rate": metrics.error_rate,
            "throughput_per_sec": metrics.throughput_per_sec,
            "uptime_seconds": metrics.uptime_seconds,
            "status": metrics.status.value,
            "version": metrics.version,
            "instance_count": metrics.instance_count,
            "last_heartbeat": metrics.last_heartbeat.isoformat(),
        }
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid engine type")


@router.post("/engines/update")
async def update_engine_metrics(request: EngineMetricsUpdate):
    """Update metrics for an engine."""
    try:
        engine = EngineType(request.engine_type)
        metrics = system_monitor.update_engine_metrics(
            engine_type=engine,
            cpu_percent=request.cpu_percent,
            memory_percent=request.memory_percent,
            gpu_percent=request.gpu_percent,
            queue_depth=request.queue_depth,
            active_tasks=request.active_tasks,
            latency_ms=request.latency_ms,
            error_rate=request.error_rate,
            throughput_per_sec=request.throughput_per_sec,
        )
        return {"status": "updated", "engine_type": metrics.engine_type.value, "new_status": metrics.status.value}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/detect/corruption")
async def detect_data_corruption(request: DataCorruptionCheck):
    """Detect data corruption."""
    try:
        engine = EngineType(request.engine_type)
        alert = system_monitor.detect_data_corruption(
            engine_type=engine,
            data_source=request.data_source,
            expected_checksum=request.expected_checksum,
            actual_checksum=request.actual_checksum,
        )
        if alert:
            return {"corruption_detected": True, "alert_id": alert.alert_id, "severity": alert.severity.value}
        return {"corruption_detected": False}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/detect/feedback-loop")
async def detect_feedback_loop(request: FeedbackLoopDetection):
    """Detect feedback loop between engines."""
    try:
        source = EngineType(request.source_engine)
        target = EngineType(request.target_engine)
        detection = system_monitor.detect_feedback_loop(
            source_engine=source,
            target_engine=target,
            cycle_time_ms=request.cycle_time_ms,
            amplification_factor=request.amplification_factor,
        )
        return {
            "detection_id": detection.detection_id,
            "loop_type": detection.loop_type,
            "risk_level": detection.risk_level,
            "mitigation_strategy": detection.mitigation_strategy,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/predict/overload")
async def predict_overload(request: OverloadPredictionRequest):
    """Predict system overload."""
    try:
        engine = EngineType(request.engine_type)
        prediction = system_monitor.predict_system_overload(
            engine_type=engine,
            time_horizon_hours=request.time_horizon_hours,
        )
        return {
            "prediction_id": prediction.prediction_id,
            "predicted_overload_time": prediction.predicted_overload_time.isoformat(),
            "confidence": prediction.confidence,
            "current_load_percent": prediction.current_load_percent,
            "projected_load_percent": prediction.projected_load_percent,
            "contributing_factors": prediction.contributing_factors,
            "recommended_actions": prediction.recommended_actions,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/alerts")
async def get_alerts(severity: Optional[str] = None):
    """Get active system alerts."""
    sev = AlertSeverity(severity) if severity else None
    alerts = system_monitor.get_active_alerts(severity=sev)
    return {
        "alerts": [
            {
                "alert_id": a.alert_id,
                "engine_type": a.engine_type.value,
                "issue_type": a.issue_type.value,
                "severity": a.severity.value,
                "title": a.title,
                "description": a.description,
                "recommended_action": a.recommended_action,
                "auto_correctable": a.auto_correctable,
                "timestamp": a.timestamp.isoformat(),
            }
            for a in alerts
        ],
        "total": len(alerts),
    }


@router.post("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(alert_id: str):
    """Acknowledge an alert."""
    success = system_monitor.acknowledge_alert(alert_id)
    if not success:
        raise HTTPException(status_code=404, detail="Alert not found")
    return {"status": "acknowledged", "alert_id": alert_id}


@router.post("/alerts/{alert_id}/resolve")
async def resolve_alert(alert_id: str):
    """Resolve an alert."""
    success = system_monitor.resolve_alert(alert_id)
    if not success:
        raise HTTPException(status_code=404, detail="Alert not found")
    return {"status": "resolved", "alert_id": alert_id}


@router.post("/corrections/create")
async def create_correction(request: CorrectionActionRequest):
    """Create a correction action."""
    try:
        correction_type = CorrectionType(request.correction_type)
        priority = CorrectionPriority[request.priority.upper()]
        action = auto_corrector.create_correction_action(
            correction_type=correction_type,
            target_engine=request.target_engine,
            target_component=request.target_component,
            priority=priority,
            description=request.description,
            parameters=request.parameters,
            estimated_duration_seconds=request.estimated_duration_seconds,
        )
        return {
            "action_id": action.action_id,
            "status": action.status.value,
            "requires_approval": action.requires_approval,
        }
    except (ValueError, KeyError) as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/corrections/{action_id}/approve")
async def approve_correction(action_id: str, approved_by: str = Query(...)):
    """Approve a correction action."""
    success = auto_corrector.approve_correction(action_id, approved_by)
    if not success:
        raise HTTPException(status_code=404, detail="Action not found or not pending approval")
    return {"status": "approved", "action_id": action_id, "approved_by": approved_by}


@router.post("/corrections/{action_id}/execute")
async def execute_correction(action_id: str):
    """Execute a correction action."""
    try:
        result = auto_corrector.execute_correction(action_id)
        return {
            "result_id": result.result_id,
            "action_id": result.action_id,
            "success": result.success,
            "message": result.message,
            "duration_seconds": result.duration_seconds,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/corrections/pipeline/repair")
async def repair_pipeline(request: PipelineRepairRequest):
    """Repair a stalled pipeline."""
    try:
        result = auto_corrector.repair_stalled_pipeline(request.pipeline_id)
        return {
            "result_id": result.result_id,
            "success": result.success,
            "message": result.message,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/corrections/service/restart")
async def restart_service(request: ServiceRestartRequest):
    """Restart a failed service."""
    result = auto_corrector.restart_failed_service(
        engine=request.engine,
        service_name=request.service_name,
        force=request.force,
    )
    return {
        "result_id": result.result_id,
        "action_id": result.action_id,
        "success": result.success,
        "message": result.message,
    }


@router.post("/corrections/cache/rebuild")
async def rebuild_cache(request: CacheRebuildRequest):
    """Rebuild a corrupted cache."""
    result = auto_corrector.rebuild_corrupted_cache(
        engine=request.engine,
        cache_name=request.cache_name,
    )
    return {
        "result_id": result.result_id,
        "success": result.success,
        "message": result.message,
    }


@router.post("/corrections/load/rebalance")
async def rebalance_load(request: LoadRebalanceRequest):
    """Rebalance compute load."""
    result = auto_corrector.rebalance_compute_load(
        source_engine=request.source_engine,
        target_engine=request.target_engine,
        load_percent=request.load_percent,
    )
    return {
        "result_id": result.result_id,
        "success": result.success,
        "message": result.message,
    }


@router.post("/corrections/model/drift-check")
async def check_model_drift(request: ModelDriftCheckRequest):
    """Check for model drift."""
    report = auto_corrector.detect_model_drift(
        model_name=request.model_name,
        engine=request.engine,
        baseline_metrics=request.baseline_metrics,
        current_metrics=request.current_metrics,
    )
    return {
        "report_id": report.report_id,
        "drift_score": report.drift_score,
        "drift_type": report.drift_type,
        "recommended_action": report.recommended_action,
        "auto_corrected": report.auto_corrected,
    }


@router.post("/corrections/feed/recover")
async def recover_data_feed(request: DataFeedRecoveryRequest):
    """Recover a missing data feed."""
    result = auto_corrector.recover_data_feed(
        engine=request.engine,
        feed_name=request.feed_name,
        fallback_source=request.fallback_source,
    )
    return {
        "result_id": result.result_id,
        "success": result.success,
        "message": result.message,
    }


@router.post("/corrections/{action_id}/rollback")
async def rollback_correction(action_id: str):
    """Rollback a correction action."""
    try:
        result = auto_corrector.rollback_correction(action_id)
        return {
            "result_id": result.result_id,
            "success": result.success,
            "message": result.message,
            "rollback_performed": result.rollback_performed,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/corrections/pending")
async def get_pending_corrections():
    """Get pending correction actions."""
    actions = auto_corrector.get_pending_corrections()
    return {
        "actions": [
            {
                "action_id": a.action_id,
                "correction_type": a.correction_type.value,
                "target_engine": a.target_engine,
                "target_component": a.target_component,
                "priority": a.priority.value,
                "status": a.status.value,
                "requires_approval": a.requires_approval,
            }
            for a in actions
        ],
        "total": len(actions),
    }


@router.get("/corrections/history")
async def get_correction_history(limit: int = 100):
    """Get correction history."""
    actions = auto_corrector.get_correction_history(limit=limit)
    return {
        "actions": [
            {
                "action_id": a.action_id,
                "correction_type": a.correction_type.value,
                "target_engine": a.target_engine,
                "status": a.status.value,
                "created_at": a.created_at.isoformat(),
            }
            for a in actions
        ],
        "total": len(actions),
    }


@router.get("/pipelines")
async def get_pipelines():
    """Get all pipeline statuses."""
    pipelines = auto_corrector.get_pipeline_statuses()
    return {
        "pipelines": [
            {
                "pipeline_id": p.pipeline_id,
                "name": p.name,
                "engine": p.engine,
                "status": p.status,
                "last_run": p.last_run.isoformat(),
                "records_processed": p.records_processed,
                "error_count": p.error_count,
                "stalled": p.stalled,
            }
            for p in pipelines
        ],
        "total": len(pipelines),
    }


@router.get("/pipelines/stalled")
async def get_stalled_pipelines():
    """Get stalled pipelines."""
    pipelines = auto_corrector.get_stalled_pipelines()
    return {
        "pipelines": [
            {
                "pipeline_id": p.pipeline_id,
                "name": p.name,
                "engine": p.engine,
                "stall_duration_seconds": p.stall_duration_seconds,
            }
            for p in pipelines
        ],
        "total": len(pipelines),
    }


@router.post("/validate-action")
async def validate_action(request: ActionValidationRequest):
    """Validate an action against ethics and compliance rules."""
    validation = ethics_guard.validate_action(
        action_type=request.action_type,
        engine=request.engine,
        target=request.target,
        parameters=request.parameters,
        warrant_obtained=request.warrant_obtained,
        human_approved=request.human_approved,
        approved_by=request.approved_by,
    )
    return {
        "validation_id": validation.validation_id,
        "decision": validation.decision.value,
        "violations": validation.violations,
        "conditions": validation.conditions,
        "explainability_score": validation.explainability_score,
        "bias_score": validation.bias_score,
        "legal_basis": validation.legal_basis,
        "requires_warrant": validation.requires_warrant,
        "human_approval_required": validation.human_approval_required,
    }


@router.post("/ethics/audit")
async def conduct_bias_audit(request: BiasAuditRequest):
    """Conduct a bias audit on model predictions."""
    audit = ethics_guard.conduct_bias_audit(
        engine=request.engine,
        model_name=request.model_name,
        predictions=request.predictions,
    )
    return {
        "audit_id": audit.audit_id,
        "overall_bias_score": audit.overall_bias_score,
        "bias_detected": audit.bias_detected,
        "disparate_impact_scores": audit.disparate_impact_scores,
        "recommendations": audit.recommendations,
    }


@router.get("/ethics/audit")
async def get_bias_audits():
    """Get all bias audit results."""
    audits = list(ethics_guard.bias_audits.values())
    return {
        "audits": [
            {
                "audit_id": a.audit_id,
                "engine": a.engine,
                "model_name": a.model_name,
                "overall_bias_score": a.overall_bias_score,
                "bias_detected": a.bias_detected,
                "timestamp": a.timestamp.isoformat(),
            }
            for a in audits
        ],
        "total": len(audits),
    }


@router.get("/violations")
async def get_violations(severity: Optional[str] = None):
    """Get ethics violations."""
    sev = ViolationSeverity(severity) if severity else None
    violations = ethics_guard.get_active_violations(severity=sev)
    return {
        "violations": [
            {
                "violation_id": v.violation_id,
                "violation_type": v.violation_type.value,
                "severity": v.severity.value,
                "framework": v.framework.value,
                "engine": v.engine,
                "action_attempted": v.action_attempted,
                "description": v.description,
                "blocked": v.blocked,
                "escalated": v.escalated,
                "timestamp": v.timestamp.isoformat(),
            }
            for v in violations
        ],
        "total": len(violations),
    }


@router.get("/violations/escalated")
async def get_escalated_violations():
    """Get escalated violations."""
    violations = ethics_guard.get_escalated_violations()
    return {
        "violations": [
            {
                "violation_id": v.violation_id,
                "violation_type": v.violation_type.value,
                "severity": v.severity.value,
                "engine": v.engine,
                "description": v.description,
                "timestamp": v.timestamp.isoformat(),
            }
            for v in violations
        ],
        "total": len(violations),
    }


@router.post("/violations/review")
async def review_violation(request: ViolationReviewRequest):
    """Review a violation."""
    success = ethics_guard.review_violation(
        violation_id=request.violation_id,
        reviewed_by=request.reviewed_by,
        decision=request.decision,
    )
    if not success:
        raise HTTPException(status_code=404, detail="Violation not found")
    return {"status": "reviewed", "violation_id": request.violation_id}


@router.get("/compliance/summary")
async def get_compliance_summary():
    """Get compliance summary."""
    return ethics_guard.get_compliance_summary()


@router.post("/recommendation")
async def create_recommendation(request: RecommendationRequest):
    """Create a sentinel recommendation."""
    try:
        rec_type = RecommendationType(request.recommendation_type)
        priority = AlertPriority(request.priority)
        recommendation = sentinel_engine.create_recommendation(
            recommendation_type=rec_type,
            priority=priority,
            title=request.title,
            description=request.description,
            rationale=request.rationale,
            affected_systems=request.affected_systems,
            implementation_steps=request.implementation_steps,
            expected_outcome=request.expected_outcome,
            risk_if_ignored=request.risk_if_ignored,
            deadline_hours=request.deadline_hours,
        )
        return {
            "recommendation_id": recommendation.recommendation_id,
            "recommendation_type": recommendation.recommendation_type.value,
            "priority": recommendation.priority.value,
            "title": recommendation.title,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/recommendations")
async def get_recommendations():
    """Get pending recommendations."""
    recommendations = sentinel_engine.get_pending_recommendations()
    return {
        "recommendations": [
            {
                "recommendation_id": r.recommendation_id,
                "recommendation_type": r.recommendation_type.value,
                "priority": r.priority.value,
                "title": r.title,
                "description": r.description,
                "deadline": r.deadline.isoformat() if r.deadline else None,
                "accepted": r.accepted,
                "implemented": r.implemented,
            }
            for r in recommendations
        ],
        "total": len(recommendations),
    }


@router.post("/recommendations/{recommendation_id}/accept")
async def accept_recommendation(recommendation_id: str):
    """Accept a recommendation."""
    success = sentinel_engine.accept_recommendation(recommendation_id)
    if not success:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    return {"status": "accepted", "recommendation_id": recommendation_id}


@router.post("/recommendations/{recommendation_id}/implement")
async def implement_recommendation(recommendation_id: str):
    """Mark a recommendation as implemented."""
    success = sentinel_engine.implement_recommendation(recommendation_id)
    if not success:
        raise HTTPException(status_code=400, detail="Recommendation not found or not accepted")
    return {"status": "implemented", "recommendation_id": recommendation_id}


@router.post("/alerts/consolidate")
async def consolidate_alerts(request: AlertConsolidationRequest):
    """Consolidate alerts from multiple sources."""
    try:
        sources = [AlertSource(s) for s in request.sources]
        alert = sentinel_engine.consolidate_alert(
            sources=sources,
            title=request.title,
            description=request.description,
            affected_systems=request.affected_systems,
            affected_areas=request.affected_areas,
            metrics=request.metrics,
            severity_score=request.severity_score,
        )
        return {
            "alert_id": alert.alert_id,
            "priority": alert.priority.value,
            "auto_response_triggered": alert.auto_response_triggered,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/sentinel/alerts")
async def get_sentinel_alerts(priority: Optional[int] = None):
    """Get consolidated alerts."""
    p = AlertPriority(priority) if priority else None
    alerts = sentinel_engine.get_active_alerts(priority=p)
    return {
        "alerts": [
            {
                "alert_id": a.alert_id,
                "priority": a.priority.value,
                "sources": [s.value for s in a.sources],
                "title": a.title,
                "description": a.description,
                "affected_systems": a.affected_systems,
                "recommended_actions": a.recommended_actions,
                "acknowledged": a.acknowledged,
                "assigned_to": a.assigned_to,
                "timestamp": a.timestamp.isoformat(),
            }
            for a in alerts
        ],
        "total": len(alerts),
    }


@router.post("/sentinel/alerts/acknowledge")
async def acknowledge_sentinel_alert(request: AlertAcknowledgeRequest):
    """Acknowledge a consolidated alert."""
    success = sentinel_engine.acknowledge_alert(request.alert_id, request.acknowledged_by)
    if not success:
        raise HTTPException(status_code=404, detail="Alert not found")
    return {"status": "acknowledged", "alert_id": request.alert_id}


@router.post("/sentinel/alerts/resolve")
async def resolve_sentinel_alert(request: AlertResolveRequest):
    """Resolve a consolidated alert."""
    success = sentinel_engine.resolve_alert(request.alert_id, request.resolution_notes)
    if not success:
        raise HTTPException(status_code=404, detail="Alert not found")
    return {"status": "resolved", "alert_id": request.alert_id}


@router.post("/autonomous/request")
async def request_autonomous_action(request: AutonomousActionRequest):
    """Request approval for an autonomous action."""
    try:
        autonomy = AutonomyLevel(request.autonomy_level)
        action_request = sentinel_engine.request_autonomous_action(
            source_engine=request.source_engine,
            action_type=request.action_type,
            autonomy_level=autonomy,
            target=request.target,
            parameters=request.parameters,
            justification=request.justification,
            risk_score=request.risk_score,
        )
        return {
            "request_id": action_request.request_id,
            "approval_status": action_request.approval_status.value,
            "denial_reason": action_request.denial_reason,
            "conditions": action_request.conditions,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/autonomous/pending")
async def get_pending_autonomous_requests():
    """Get pending autonomous action requests."""
    requests = sentinel_engine.get_pending_action_requests()
    return {
        "requests": [
            {
                "request_id": r.request_id,
                "source_engine": r.source_engine,
                "action_type": r.action_type,
                "autonomy_level": r.autonomy_level.value,
                "target": r.target,
                "justification": r.justification,
                "risk_assessment": r.risk_assessment,
                "approval_status": r.approval_status.value,
                "timestamp": r.timestamp.isoformat(),
            }
            for r in requests
        ],
        "total": len(requests),
    }


@router.post("/cascade/predict")
async def predict_cascade(request: CascadePredictionRequest):
    """Predict cascading outcomes."""
    try:
        source = AlertSource(request.trigger_source)
        prediction = sentinel_engine.predict_cascade(
            trigger_event=request.trigger_event,
            trigger_source=source,
            initial_severity=request.initial_severity,
            time_horizon_hours=request.time_horizon_hours,
        )
        return {
            "prediction_id": prediction.prediction_id,
            "predicted_outcomes": prediction.predicted_outcomes,
            "probability": prediction.probability,
            "affected_systems": prediction.affected_systems,
            "mitigation_options": prediction.mitigation_options,
            "confidence": prediction.confidence,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/command/alerts")
async def get_command_alerts(unacknowledged_only: bool = False):
    """Get command staff alerts."""
    alerts = sentinel_engine.get_command_alerts(unacknowledged_only=unacknowledged_only)
    return {
        "alerts": [
            {
                "alert_id": a.alert_id,
                "priority": a.priority.value,
                "recipient_role": a.recipient_role,
                "title": a.title,
                "summary": a.summary,
                "required_action": a.required_action,
                "deadline": a.deadline.isoformat() if a.deadline else None,
                "acknowledged": a.acknowledged,
                "sent_at": a.sent_at.isoformat(),
            }
            for a in alerts
        ],
        "total": len(alerts),
    }


@router.post("/command/alerts/acknowledge")
async def acknowledge_command_alert(request: CommandAlertAcknowledgeRequest):
    """Acknowledge a command staff alert."""
    success = sentinel_engine.acknowledge_command_alert(request.alert_id, request.response)
    if not success:
        raise HTTPException(status_code=404, detail="Alert not found")
    return {"status": "acknowledged", "alert_id": request.alert_id}


@router.get("/dashboard")
async def get_dashboard_summary():
    """Get supervisor dashboard summary."""
    return sentinel_engine.get_dashboard_summary()


@router.get("/statistics")
async def get_statistics():
    """Get comprehensive statistics from all supervisor components."""
    return {
        "system_monitor": system_monitor.get_statistics(),
        "auto_corrector": auto_corrector.get_statistics(),
        "ethics_guard": ethics_guard.get_statistics(),
        "sentinel_engine": sentinel_engine.get_statistics(),
        "timestamp": datetime.utcnow().isoformat(),
    }
