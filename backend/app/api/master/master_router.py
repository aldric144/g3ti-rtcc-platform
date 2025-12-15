"""
Master Orchestration REST API Router
Phase 37: Master UI Integration & System Orchestration Shell
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from backend.app.master_orchestration.event_bus import (
    MasterEventBus,
    EventType,
    EventPriority,
    EventSource,
    MasterEvent,
)
from backend.app.master_orchestration.alert_aggregator import (
    UnifiedAlertStream,
    AlertSeverity,
    AlertSource,
    UnifiedAlert,
    AlertFilter,
)
from backend.app.master_orchestration.module_heartbeat import (
    ModuleHeartbeatChecker,
    ModuleStatus,
)
from backend.app.master_orchestration.state_synchronizer import (
    CrossModuleStateSynchronizer,
    StateChangeType,
    SyncTarget,
)
from backend.app.master_orchestration.permissions_manager import (
    GlobalPermissionsManager,
    PermissionAction,
)

router = APIRouter(prefix="/api/master", tags=["Master Orchestration"])

event_bus = MasterEventBus()
alert_stream = UnifiedAlertStream()
heartbeat_checker = ModuleHeartbeatChecker()
state_sync = CrossModuleStateSynchronizer()
permissions_manager = GlobalPermissionsManager()


class EventCreateRequest(BaseModel):
    event_type: str = Field(..., description="Type of event")
    source: str = Field(..., description="Source module")
    title: str = Field(..., description="Event title")
    summary: str = Field(default="", description="Event summary")
    priority: str = Field(default="medium", description="Event priority")
    details: Dict[str, Any] = Field(default_factory=dict)
    geolocation: Optional[Dict[str, float]] = None
    constitutional_compliance: bool = True
    moral_compass_tag: Optional[str] = None
    public_safety_audit_ref: Optional[str] = None
    affected_modules: List[str] = Field(default_factory=list)
    requires_acknowledgment: bool = False


class AlertCreateRequest(BaseModel):
    severity: str = Field(..., description="Alert severity")
    source: str = Field(..., description="Alert source")
    title: str = Field(..., description="Alert title")
    summary: str = Field(default="", description="Alert summary")
    full_details: Dict[str, Any] = Field(default_factory=dict)
    geolocation: Optional[Dict[str, float]] = None
    constitutional_compliance_tag: bool = True
    moral_compass_tag: Optional[str] = None
    public_safety_audit_ref: Optional[str] = None
    affected_areas: List[str] = Field(default_factory=list)
    affected_officers: List[str] = Field(default_factory=list)
    requires_action: bool = False


class HeartbeatUpdateRequest(BaseModel):
    module_id: str = Field(..., description="Module ID")
    response_time_ms: float = Field(default=0.0)
    cpu_usage: float = Field(default=0.0)
    memory_usage: float = Field(default=0.0)
    error_count: int = Field(default=0)
    warning_count: int = Field(default=0)
    endpoints_healthy: int = Field(default=0)
    endpoints_total: int = Field(default=0)
    websocket_connections: int = Field(default=0)
    last_error: Optional[str] = None


class StateChangeRequest(BaseModel):
    change_type: str = Field(..., description="Type of state change")
    source_module: str = Field(..., description="Source module")
    data: Dict[str, Any] = Field(default_factory=dict)
    targets: List[str] = Field(default_factory=list)
    priority: int = Field(default=5)
    requires_acknowledgment: bool = False


class PermissionCheckRequest(BaseModel):
    user_id: str = Field(..., description="User ID")
    module: str = Field(..., description="Module name")
    feature: str = Field(..., description="Feature name")
    action: str = Field(..., description="Action to check")


class StandardResponse(BaseModel):
    status: str = "ok"
    engine: str = "master_orchestration"
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    payload: Dict[str, Any] = Field(default_factory=dict)


@router.get("/events", response_model=StandardResponse)
async def get_recent_events(
    limit: int = Query(default=100, le=500),
    event_type: Optional[str] = None,
    source: Optional[str] = None,
    min_priority: Optional[str] = None,
):
    event_types = [EventType(event_type)] if event_type else None
    sources = [EventSource(source)] if source else None
    priority = EventPriority(min_priority) if min_priority else None

    events = event_bus.get_recent_events(
        limit=limit,
        event_types=event_types,
        sources=sources,
        min_priority=priority,
    )

    return StandardResponse(
        payload={
            "events": [e.to_dict() for e in events],
            "count": len(events),
        }
    )


@router.post("/events", response_model=StandardResponse)
async def create_event(request: EventCreateRequest):
    event = event_bus.create_event(
        event_type=EventType(request.event_type),
        source=EventSource(request.source),
        title=request.title,
        summary=request.summary,
        priority=EventPriority(request.priority),
        details=request.details,
        geolocation=request.geolocation,
        constitutional_compliance=request.constitutional_compliance,
        moral_compass_tag=request.moral_compass_tag,
        public_safety_audit_ref=request.public_safety_audit_ref,
        affected_modules=request.affected_modules,
        requires_acknowledgment=request.requires_acknowledgment,
    )

    await event_bus.publish(event)

    return StandardResponse(
        payload={
            "event": event.to_dict(),
            "published": True,
        }
    )


@router.get("/events/{event_id}", response_model=StandardResponse)
async def get_event(event_id: str):
    event = event_bus.get_event(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    return StandardResponse(
        payload={"event": event.to_dict()}
    )


@router.post("/events/{event_id}/acknowledge", response_model=StandardResponse)
async def acknowledge_event(event_id: str, acknowledged_by: str):
    success = event_bus.acknowledge_event(event_id, acknowledged_by)
    if not success:
        raise HTTPException(status_code=404, detail="Event not found or doesn't require acknowledgment")

    return StandardResponse(
        payload={"acknowledged": True, "event_id": event_id}
    )


@router.get("/events/unacknowledged", response_model=StandardResponse)
async def get_unacknowledged_events():
    events = event_bus.get_unacknowledged_events()
    return StandardResponse(
        payload={
            "events": [e.to_dict() for e in events],
            "count": len(events),
        }
    )


@router.get("/alerts", response_model=StandardResponse)
async def get_active_alerts(
    limit: int = Query(default=100, le=500),
    severity: Optional[str] = None,
    source: Optional[str] = None,
    requires_action: bool = False,
):
    if requires_action:
        alerts = alert_stream.get_alerts_requiring_action(limit=limit)
    elif severity:
        alerts = alert_stream.get_alerts_by_severity(AlertSeverity(severity), limit=limit)
    elif source:
        alerts = alert_stream.get_alerts_by_source(AlertSource(source), limit=limit)
    else:
        alerts = alert_stream.get_active_alerts(limit=limit)

    return StandardResponse(
        payload={
            "alerts": [a.to_dict() for a in alerts],
            "count": len(alerts),
        }
    )


@router.post("/alerts", response_model=StandardResponse)
async def create_alert(request: AlertCreateRequest):
    alert = alert_stream.create_alert(
        severity=AlertSeverity(request.severity),
        source=AlertSource(request.source),
        title=request.title,
        summary=request.summary,
        full_details=request.full_details,
        geolocation=request.geolocation,
        constitutional_compliance_tag=request.constitutional_compliance_tag,
        moral_compass_tag=request.moral_compass_tag,
        public_safety_audit_ref=request.public_safety_audit_ref,
        affected_areas=request.affected_areas,
        affected_officers=request.affected_officers,
        requires_action=request.requires_action,
    )

    return StandardResponse(
        payload={
            "alert": alert.to_dict(),
            "created": True,
        }
    )


@router.get("/alerts/{alert_id}", response_model=StandardResponse)
async def get_alert(alert_id: str):
    alert = alert_stream.get_alert(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    return StandardResponse(
        payload={"alert": alert.to_dict()}
    )


@router.post("/alerts/{alert_id}/action", response_model=StandardResponse)
async def take_alert_action(alert_id: str, action_by: str, action_notes: Optional[str] = None):
    alert = alert_stream.take_action(alert_id, action_by, action_notes)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    return StandardResponse(
        payload={"alert": alert.to_dict(), "action_taken": True}
    )


@router.post("/alerts/{alert_id}/resolve", response_model=StandardResponse)
async def resolve_alert(alert_id: str, resolved_by: str, notes: Optional[str] = None):
    success = alert_stream.resolve_alert(alert_id, resolved_by, notes)
    if not success:
        raise HTTPException(status_code=404, detail="Alert not found")

    return StandardResponse(
        payload={"resolved": True, "alert_id": alert_id}
    )


@router.post("/alerts/{alert_id}/escalate", response_model=StandardResponse)
async def escalate_alert(alert_id: str, escalation_notes: Optional[str] = None):
    alert = alert_stream.escalate_alert(alert_id, escalation_notes)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    return StandardResponse(
        payload={"alert": alert.to_dict(), "escalated": True}
    )


@router.get("/alerts/unified-feed", response_model=StandardResponse)
async def get_unified_alert_feed(limit: int = Query(default=50, le=200)):
    feed = alert_stream.get_unified_feed(limit=limit)
    return StandardResponse(
        payload={
            "feed": feed,
            "count": len(feed),
        }
    )


@router.get("/modules/health", response_model=StandardResponse)
async def get_all_module_health():
    result = heartbeat_checker.perform_heartbeat_check_sync()
    return StandardResponse(
        engine="module_heartbeat",
        payload=result.to_dict()
    )


@router.get("/modules/{module_id}/health", response_model=StandardResponse)
async def get_module_health(module_id: str):
    health = heartbeat_checker.get_module_health(module_id)
    if not health:
        raise HTTPException(status_code=404, detail="Module not found")

    return StandardResponse(
        engine="module_heartbeat",
        payload={"module": health.to_dict()}
    )


@router.post("/modules/heartbeat", response_model=StandardResponse)
async def update_module_heartbeat(request: HeartbeatUpdateRequest):
    health = heartbeat_checker.update_heartbeat(
        module_id=request.module_id,
        response_time_ms=request.response_time_ms,
        cpu_usage=request.cpu_usage,
        memory_usage=request.memory_usage,
        error_count=request.error_count,
        warning_count=request.warning_count,
        endpoints_healthy=request.endpoints_healthy,
        endpoints_total=request.endpoints_total,
        websocket_connections=request.websocket_connections,
        last_error=request.last_error,
    )

    if not health:
        raise HTTPException(status_code=404, detail="Module not found")

    return StandardResponse(
        engine="module_heartbeat",
        payload={"module": health.to_dict(), "updated": True}
    )


@router.get("/modules/overview", response_model=StandardResponse)
async def get_system_overview():
    overview = heartbeat_checker.get_system_overview()
    return StandardResponse(
        engine="module_heartbeat",
        payload=overview
    )


@router.get("/modules/unhealthy", response_model=StandardResponse)
async def get_unhealthy_modules():
    modules = heartbeat_checker.get_unhealthy_modules()
    return StandardResponse(
        engine="module_heartbeat",
        payload={
            "modules": [m.to_dict() for m in modules],
            "count": len(modules),
        }
    )


@router.get("/state/changes", response_model=StandardResponse)
async def get_recent_state_changes(
    limit: int = Query(default=100, le=500),
    change_type: Optional[str] = None,
    source_module: Optional[str] = None,
):
    ct = StateChangeType(change_type) if change_type else None
    changes = state_sync.get_recent_changes(
        limit=limit,
        change_type=ct,
        source_module=source_module,
    )

    return StandardResponse(
        engine="state_synchronizer",
        payload={
            "changes": [c.to_dict() for c in changes],
            "count": len(changes),
        }
    )


@router.post("/state/publish", response_model=StandardResponse)
async def publish_state_change(request: StateChangeRequest):
    targets = [SyncTarget(t) for t in request.targets] if request.targets else []

    change = state_sync.create_change(
        change_type=StateChangeType(request.change_type),
        source_module=request.source_module,
        data=request.data,
        targets=targets,
        priority=request.priority,
        requires_acknowledgment=request.requires_acknowledgment,
    )

    await state_sync.publish_change(change)

    return StandardResponse(
        engine="state_synchronizer",
        payload={
            "change": change.to_dict(),
            "published": True,
        }
    )


@router.get("/state/summary", response_model=StandardResponse)
async def get_state_summary():
    summary = state_sync.get_current_state_summary()
    return StandardResponse(
        engine="state_synchronizer",
        payload=summary
    )


@router.get("/state/sync-rules", response_model=StandardResponse)
async def get_sync_rules():
    rules = state_sync.get_sync_rules()
    return StandardResponse(
        engine="state_synchronizer",
        payload={"rules": rules}
    )


@router.post("/permissions/check", response_model=StandardResponse)
async def check_permission(request: PermissionCheckRequest):
    allowed = permissions_manager.check_permission(
        user_id=request.user_id,
        module=request.module,
        feature=request.feature,
        action=PermissionAction(request.action),
    )

    return StandardResponse(
        engine="permissions_manager",
        payload={
            "allowed": allowed,
            "user_id": request.user_id,
            "module": request.module,
            "feature": request.feature,
            "action": request.action,
        }
    )


@router.get("/permissions/roles", response_model=StandardResponse)
async def get_all_roles():
    roles = permissions_manager.get_all_roles()
    return StandardResponse(
        engine="permissions_manager",
        payload={"roles": roles}
    )


@router.get("/permissions/user/{user_id}", response_model=StandardResponse)
async def get_user_permissions(user_id: str):
    roles = permissions_manager.get_user_roles(user_id)
    permissions = permissions_manager.get_user_permissions(user_id)

    return StandardResponse(
        engine="permissions_manager",
        payload={
            "user_id": user_id,
            "roles": roles,
            "permissions_count": len(permissions),
        }
    )


@router.post("/permissions/user/{user_id}/role", response_model=StandardResponse)
async def assign_user_role(user_id: str, role: str):
    success = permissions_manager.assign_role(user_id, role)
    if not success:
        raise HTTPException(status_code=400, detail="Invalid role")

    return StandardResponse(
        engine="permissions_manager",
        payload={"assigned": True, "user_id": user_id, "role": role}
    )


@router.get("/permissions/map", response_model=StandardResponse)
async def get_permissions_map():
    perm_map = permissions_manager.get_permissions_map()
    return StandardResponse(
        engine="permissions_manager",
        payload={
            "permissions_map": perm_map,
            "total_actions": permissions_manager.get_action_count(),
        }
    )


@router.get("/statistics", response_model=StandardResponse)
async def get_master_statistics():
    return StandardResponse(
        payload={
            "event_bus": event_bus.get_statistics(),
            "alert_stream": alert_stream.get_statistics(),
            "heartbeat_checker": heartbeat_checker.get_statistics(),
            "state_synchronizer": state_sync.get_statistics(),
            "permissions_manager": permissions_manager.get_statistics(),
        }
    )


@router.get("/health", response_model=StandardResponse)
async def health_check():
    return StandardResponse(
        payload={
            "status": "healthy",
            "service": "master_orchestration",
            "components": {
                "event_bus": "operational",
                "alert_stream": "operational",
                "heartbeat_checker": "operational",
                "state_synchronizer": "operational",
                "permissions_manager": "operational",
            },
            "timestamp": datetime.utcnow().isoformat(),
        }
    )


@router.get("/dashboard-data", response_model=StandardResponse)
async def get_dashboard_data():
    alerts = alert_stream.get_active_alerts(limit=20)
    events = event_bus.get_recent_events(limit=20)
    module_health = heartbeat_checker.get_system_overview()
    state_summary = state_sync.get_current_state_summary()

    critical_alerts = [a for a in alerts if a.severity == AlertSeverity.CRITICAL]
    high_alerts = [a for a in alerts if a.severity == AlertSeverity.HIGH]

    return StandardResponse(
        payload={
            "alerts": {
                "total": len(alerts),
                "critical": len(critical_alerts),
                "high": len(high_alerts),
                "recent": [a.to_dict() for a in alerts[:10]],
            },
            "events": {
                "total": len(events),
                "recent": [e.to_dict() for e in events[:10]],
            },
            "modules": module_health,
            "state": state_summary,
            "timestamp": datetime.utcnow().isoformat(),
        }
    )
