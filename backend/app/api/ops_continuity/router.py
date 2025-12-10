"""
REST API Router for Operations Continuity.

Provides endpoints for health checks, failover status, redundancy status,
diagnostics reports, and audit logs.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.ops_continuity.diagnostics import (
    DiagnosticCategory,
    DiagnosticsEngine,
    DiagnosticSeverity,
)
from app.ops_continuity.failover_manager import FailoverManager
from app.ops_continuity.healthchecks import HealthCheckService, ServiceType
from app.ops_continuity.ops_audit_log import (
    OpsAuditAction,
    OpsAuditLog,
    OpsAuditSeverity,
)
from app.ops_continuity.redundancy_manager import RedundancyManager


router = APIRouter(prefix="/api/ops", tags=["Operations Continuity"])

health_service = HealthCheckService()
failover_manager = FailoverManager()
redundancy_manager = RedundancyManager()
diagnostics_engine = DiagnosticsEngine()
ops_audit_log = OpsAuditLog()


class HealthResponse(BaseModel):
    """Response model for health endpoints."""
    status: str
    timestamp: str
    overall_status: str
    services_count: int
    healthy_count: int
    degraded_count: int
    unhealthy_count: int
    offline_count: int
    avg_latency_ms: float


class DeepHealthResponse(BaseModel):
    """Response model for deep health check."""
    status: str
    timestamp: str
    overall_status: str
    services: dict[str, Any]
    uptime_report: dict[str, Any]
    metrics: dict[str, Any]


class FailoverStatusResponse(BaseModel):
    """Response model for failover status."""
    status: str
    timestamp: str
    state: str
    mode: str
    active_failovers: int
    buffered_operations: int
    fallbacks: dict[str, Any]
    recent_events: list[dict[str, Any]]
    metrics: dict[str, Any]


class RedundancyStatusResponse(BaseModel):
    """Response model for redundancy status."""
    status: str
    timestamp: str
    pools_managed: int
    active_connections: int
    pools: dict[str, Any]
    metrics: dict[str, Any]


class DiagnosticsReportResponse(BaseModel):
    """Response model for diagnostics report."""
    status: str
    timestamp: str
    report: dict[str, Any]


class AuditLogsResponse(BaseModel):
    """Response model for audit logs."""
    status: str
    timestamp: str
    entries: list[dict[str, Any]]
    total_count: int
    metrics: dict[str, Any]


@router.get("/health", response_model=HealthResponse)
async def get_health():
    """
    Get current health status of all services.

    Returns a summary of service health including counts by status
    and average latency.
    """
    snapshot = health_service.get_current_snapshot()

    return HealthResponse(
        status="ok",
        timestamp=datetime.now(timezone.utc).isoformat(),
        overall_status=snapshot.overall_status.value,
        services_count=len(snapshot.services),
        healthy_count=snapshot.healthy_count,
        degraded_count=snapshot.degraded_count,
        unhealthy_count=snapshot.unhealthy_count,
        offline_count=snapshot.offline_count,
        avg_latency_ms=round(snapshot.avg_latency_ms, 2),
    )


@router.get("/health/deep", response_model=DeepHealthResponse)
async def get_deep_health():
    """
    Get detailed health status of all services.

    Performs a deep health check and returns detailed information
    about each service including latency, uptime, and metadata.
    """
    snapshot = await health_service.perform_full_check()
    uptime_report = health_service.get_uptime_report(hours=24)

    services_data = {}
    for sid, service in snapshot.services.items():
        services_data[sid] = {
            "service_id": service.service_id,
            "service_type": service.service_type.value,
            "service_name": service.service_name,
            "status": service.status.value,
            "latency_ms": round(service.latency_ms, 2),
            "last_check": service.last_check.isoformat() if service.last_check else None,
            "last_success": service.last_success.isoformat() if service.last_success else None,
            "consecutive_failures": service.consecutive_failures,
            "uptime_percent": service.uptime_percent,
            "error_message": service.error_message,
            "metadata": service.metadata,
        }

    return DeepHealthResponse(
        status="ok",
        timestamp=datetime.now(timezone.utc).isoformat(),
        overall_status=snapshot.overall_status.value,
        services=services_data,
        uptime_report=uptime_report,
        metrics=health_service.get_metrics().model_dump(),
    )


@router.get("/health/service/{service_type}")
async def get_service_health(service_type: str):
    """
    Get health status for a specific service type.

    Returns health information for all services of the specified type.
    """
    try:
        stype = ServiceType(service_type)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid service type: {service_type}")

    services = health_service.get_services_by_type(stype)

    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service_type": service_type,
        "services": [
            {
                "service_id": s.service_id,
                "service_name": s.service_name,
                "status": s.status.value,
                "latency_ms": round(s.latency_ms, 2),
                "last_check": s.last_check.isoformat() if s.last_check else None,
                "error_message": s.error_message,
            }
            for s in services
        ],
    }


@router.get("/health/snapshots")
async def get_health_snapshots(
    period: str = Query("1h", description="Period: 1h or 24h"),
):
    """
    Get rolling health snapshots.

    Returns historical health snapshots for trend analysis.
    """
    if period == "24h":
        snapshots = health_service.get_24h_snapshots()
    else:
        snapshots = health_service.get_1h_snapshots()

    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "period": period,
        "snapshots_count": len(snapshots),
        "snapshots": [
            {
                "snapshot_id": s.snapshot_id,
                "timestamp": s.timestamp.isoformat(),
                "overall_status": s.overall_status.value,
                "healthy_count": s.healthy_count,
                "degraded_count": s.degraded_count,
                "unhealthy_count": s.unhealthy_count,
                "avg_latency_ms": round(s.avg_latency_ms, 2),
            }
            for s in snapshots
        ],
    }


@router.get("/failover/status", response_model=FailoverStatusResponse)
async def get_failover_status():
    """
    Get current failover status.

    Returns information about active failovers, fallback configurations,
    and recent failover events.
    """
    status = failover_manager.get_status()
    recent_events = failover_manager.get_recent_events(limit=20)

    return FailoverStatusResponse(
        status="ok",
        timestamp=datetime.now(timezone.utc).isoformat(),
        state=status["state"],
        mode=status["mode"],
        active_failovers=status["active_failovers"],
        buffered_operations=status["buffered_operations"],
        fallbacks=status["fallbacks"],
        recent_events=[
            {
                "event_id": e.event_id,
                "timestamp": e.timestamp.isoformat(),
                "service_type": e.service_type.value,
                "from_state": e.from_state.value,
                "to_state": e.to_state.value,
                "trigger_reason": e.trigger_reason,
                "auto_triggered": e.auto_triggered,
            }
            for e in recent_events
        ],
        metrics=status["metrics"],
    )


@router.post("/failover/trigger/{service_type}")
async def trigger_manual_failover(
    service_type: str,
    reason: str = Query(..., description="Reason for manual failover"),
):
    """
    Manually trigger failover for a service.

    Activates failover to the secondary/fallback target for the specified service.
    """
    try:
        stype = ServiceType(service_type)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid service type: {service_type}")

    try:
        event = await failover_manager.manual_failover(stype, reason)
        return {
            "status": "ok",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_id": event.event_id,
            "service_type": service_type,
            "message": f"Failover triggered for {service_type}",
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/failover/recover/{service_type}")
async def trigger_manual_recovery(
    service_type: str,
    reason: str = Query(..., description="Reason for manual recovery"),
):
    """
    Manually trigger recovery for a service.

    Deactivates failover and returns to the primary target for the specified service.
    """
    try:
        stype = ServiceType(service_type)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid service type: {service_type}")

    try:
        event = await failover_manager.manual_recovery(stype, reason)
        return {
            "status": "ok",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_id": event.event_id,
            "service_type": service_type,
            "message": f"Recovery triggered for {service_type}",
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/redundancy/status", response_model=RedundancyStatusResponse)
async def get_redundancy_status():
    """
    Get current redundancy status.

    Returns information about connection pools, active connections,
    and redundancy configuration.
    """
    status = redundancy_manager.get_status()

    return RedundancyStatusResponse(
        status="ok",
        timestamp=datetime.now(timezone.utc).isoformat(),
        pools_managed=status["pools_managed"],
        active_connections=status["active_connections"],
        pools=status["pools"],
        metrics=status["metrics"],
    )


@router.get("/redundancy/pool/{pool_name}")
async def get_pool_status(pool_name: str):
    """
    Get status for a specific connection pool.

    Returns detailed information about the specified connection pool.
    """
    pool = redundancy_manager.get_pool(pool_name)
    if not pool:
        raise HTTPException(status_code=404, detail=f"Pool not found: {pool_name}")

    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "pool": {
            "pool_id": pool.pool_id,
            "service_name": pool.service_name,
            "mode": pool.mode.value,
            "active_instance": pool.active_instance_id,
            "primary": {
                "instance_id": pool.primary.instance_id if pool.primary else None,
                "endpoint": pool.primary.endpoint if pool.primary else None,
                "state": pool.primary.state.value if pool.primary else None,
                "is_healthy": pool.primary.is_healthy if pool.primary else False,
            } if pool.primary else None,
            "secondary": {
                "instance_id": pool.secondary.instance_id if pool.secondary else None,
                "endpoint": pool.secondary.endpoint if pool.secondary else None,
                "state": pool.secondary.state.value if pool.secondary else None,
                "is_healthy": pool.secondary.is_healthy if pool.secondary else False,
            } if pool.secondary else None,
            "active_connections": pool.active_connections,
            "last_failover": pool.last_failover.isoformat() if pool.last_failover else None,
        },
    }


@router.post("/redundancy/failover/{pool_name}")
async def trigger_pool_failover(pool_name: str):
    """
    Manually trigger failover for a connection pool.

    Switches the pool to use the secondary instance.
    """
    success = await redundancy_manager.manual_failover(pool_name)
    if not success:
        raise HTTPException(status_code=400, detail=f"Failover failed for pool: {pool_name}")

    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "pool_name": pool_name,
        "message": f"Failover triggered for pool {pool_name}",
    }


@router.post("/redundancy/failback/{pool_name}")
async def trigger_pool_failback(pool_name: str):
    """
    Manually trigger failback for a connection pool.

    Switches the pool back to use the primary instance.
    """
    success = await redundancy_manager.manual_failback(pool_name)
    if not success:
        raise HTTPException(status_code=400, detail=f"Failback failed for pool: {pool_name}")

    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "pool_name": pool_name,
        "message": f"Failback triggered for pool {pool_name}",
    }


@router.get("/diagnostics/report", response_model=DiagnosticsReportResponse)
async def get_diagnostics_report(
    hours: int = Query(24, description="Report period in hours"),
):
    """
    Get diagnostics report.

    Returns a comprehensive diagnostics report including error counts,
    slow queries, and recommendations.
    """
    report = diagnostics_engine.generate_report(hours=hours)

    return DiagnosticsReportResponse(
        status="ok",
        timestamp=datetime.now(timezone.utc).isoformat(),
        report=report,
    )


@router.get("/diagnostics/events")
async def get_diagnostic_events(
    category: Optional[str] = Query(None, description="Filter by category"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    limit: int = Query(100, description="Maximum events to return"),
):
    """
    Get diagnostic events.

    Returns recent diagnostic events with optional filtering.
    """
    cat = DiagnosticCategory(category) if category else None
    sev = DiagnosticSeverity(severity) if severity else None

    events = diagnostics_engine.get_events(category=cat, severity=sev, limit=limit)

    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "events_count": len(events),
        "events": [
            {
                "event_id": e.event_id,
                "timestamp": e.timestamp.isoformat(),
                "category": e.category.value,
                "severity": e.severity.value,
                "source": e.source,
                "message": e.message,
                "error_code": e.error_code,
                "resolution_hint": e.resolution_hint,
            }
            for e in events
        ],
    }


@router.get("/diagnostics/slow-queries")
async def get_slow_queries(
    limit: int = Query(100, description="Maximum queries to return"),
):
    """
    Get slow query events.

    Returns recent slow query events for performance analysis.
    """
    queries = diagnostics_engine.get_slow_queries(limit=limit)

    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "queries_count": len(queries),
        "queries": [
            {
                "event_id": q.event_id,
                "timestamp": q.timestamp.isoformat(),
                "database": q.database,
                "query_type": q.query_type,
                "duration_ms": q.duration_ms,
                "threshold_ms": q.threshold_ms,
                "query_preview": q.query_preview,
                "recommendation": q.recommendation,
            }
            for q in queries
        ],
    }


@router.get("/diagnostics/alerts")
async def get_predictive_alerts(
    unacknowledged_only: bool = Query(False, description="Only unacknowledged alerts"),
):
    """
    Get predictive alerts.

    Returns predictive failure alerts generated by the diagnostics engine.
    """
    alerts = diagnostics_engine.get_predictive_alerts(unacknowledged_only=unacknowledged_only)

    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "alerts_count": len(alerts),
        "alerts": [
            {
                "alert_id": a.alert_id,
                "timestamp": a.timestamp.isoformat(),
                "category": a.category.value,
                "prediction_type": a.prediction_type,
                "confidence": a.confidence,
                "predicted_failure_time": a.predicted_failure_time.isoformat() if a.predicted_failure_time else None,
                "indicators": a.indicators,
                "recommended_actions": a.recommended_actions,
                "acknowledged": a.acknowledged,
            }
            for a in alerts
        ],
    }


@router.post("/diagnostics/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: str,
    user_id: str = Query(..., description="User acknowledging the alert"),
):
    """
    Acknowledge a predictive alert.

    Marks the alert as acknowledged by the specified user.
    """
    success = await diagnostics_engine.acknowledge_alert(alert_id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Alert not found: {alert_id}")

    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "alert_id": alert_id,
        "acknowledged_by": user_id,
    }


@router.get("/audit/logs", response_model=AuditLogsResponse)
async def get_audit_logs(
    action: Optional[str] = Query(None, description="Filter by action"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    source: Optional[str] = Query(None, description="Filter by source"),
    hours: int = Query(24, description="Time range in hours"),
    limit: int = Query(100, description="Maximum entries to return"),
):
    """
    Get operations audit logs.

    Returns audit log entries with optional filtering.
    """
    start_time = datetime.now(timezone.utc) - timedelta(hours=hours)

    act = OpsAuditAction(action) if action else None
    sev = OpsAuditSeverity(severity) if severity else None

    entries = ops_audit_log.get_entries(
        action=act,
        severity=sev,
        source=source,
        start_time=start_time,
        limit=limit,
    )

    return AuditLogsResponse(
        status="ok",
        timestamp=datetime.now(timezone.utc).isoformat(),
        entries=[
            {
                "entry_id": e.entry_id,
                "timestamp": e.timestamp.isoformat(),
                "action": e.action.value,
                "severity": e.severity.value,
                "source": e.source,
                "target": e.target,
                "description": e.description,
                "outcome": e.outcome,
                "user_id": e.user_id,
                "duration_ms": e.duration_ms,
            }
            for e in entries
        ],
        total_count=len(entries),
        metrics=ops_audit_log.get_metrics().model_dump(),
    )


@router.get("/audit/report")
async def get_audit_report(
    hours: int = Query(24, description="Report period in hours"),
    report_type: str = Query("cjis", description="Report type"),
):
    """
    Get compliance audit report.

    Generates a compliance report for the specified period.
    """
    start_time = datetime.now(timezone.utc) - timedelta(hours=hours)
    end_time = datetime.now(timezone.utc)

    report = ops_audit_log.generate_compliance_report(
        start_time=start_time,
        end_time=end_time,
        report_type=report_type,
    )

    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "report": report,
    }


@router.get("/audit/status")
async def get_audit_status():
    """
    Get audit log service status.

    Returns status information about the audit log service.
    """
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        **ops_audit_log.get_status(),
    }


@router.get("/metrics")
async def get_all_metrics():
    """
    Get all operations metrics.

    Returns combined metrics from all operations continuity services.
    """
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "health_check": health_service.get_metrics().model_dump(),
        "failover": failover_manager.get_metrics().model_dump(),
        "redundancy": redundancy_manager.get_metrics().model_dump(),
        "diagnostics": diagnostics_engine.get_metrics().model_dump(),
        "audit": ops_audit_log.get_metrics().model_dump(),
    }


@router.get("/status")
async def get_overall_status():
    """
    Get overall operations continuity status.

    Returns a summary of all operations continuity services.
    """
    health_status = health_service.get_status()
    failover_status = failover_manager.get_status()
    redundancy_status = redundancy_manager.get_status()
    diagnostics_status = diagnostics_engine.get_status()
    audit_status = ops_audit_log.get_status()

    overall_healthy = (
        health_status["overall_status"] == "healthy"
        and failover_status["state"] == "normal"
    )

    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "overall_healthy": overall_healthy,
        "services": {
            "health_check": {
                "running": health_status["running"],
                "overall_status": health_status["overall_status"],
                "services_count": health_status["services_count"],
            },
            "failover": {
                "running": failover_status["running"],
                "state": failover_status["state"],
                "active_failovers": failover_status["active_failovers"],
            },
            "redundancy": {
                "running": redundancy_status["running"],
                "pools_managed": redundancy_status["pools_managed"],
                "active_connections": redundancy_status["active_connections"],
            },
            "diagnostics": {
                "running": diagnostics_status["running"],
                "events_in_memory": diagnostics_status["events_in_memory"],
            },
            "audit": {
                "running": audit_status["running"],
                "entries_in_memory": audit_status["entries_in_memory"],
                "chain_verified": audit_status["chain_verified"],
            },
        },
    }
