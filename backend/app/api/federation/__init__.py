"""
G3TI RTCC-UIP Federation API Endpoints
Phase 10: Multi-Agency Intelligence Hub REST API
"""

from datetime import datetime
from typing import Any

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.federation import (
    AgencyStatus,
    AgencyType,
    DataCategory,
    DataSharingLevel,
    federation_manager,
)
from app.federation.analytics import (
    AnalyticsTimeRange,
    analytics_engine,
)
from app.federation.mission_rooms import (
    MessageType,
    MissionRoomStatus,
    MissionType,
    mission_room_manager,
)
from app.federation.notifications import (
    NotificationPriority,
    NotificationType,
    notification_engine,
)
from app.federation.search import SearchEntityType, federated_search_engine
from app.federation.security import (
    AuditEventType,
    security_manager,
)

router = APIRouter(prefix="/federation", tags=["federation"])


# ==================== Request/Response Models ====================


class AgencyRegisterRequest(BaseModel):
    """Request to register a partner agency"""
    agency_name: str
    agency_type: str
    jurisdiction: str
    contact_email: str
    contact_phone: str | None = None
    api_endpoint: str | None = None
    data_sharing_level: str = "basic"


class AgencyConfigureRequest(BaseModel):
    """Request to configure agency settings"""
    agency_id: str
    settings: dict[str, Any]


class FederatedQueryRequest(BaseModel):
    """Request for federated query"""
    query_type: str
    parameters: dict[str, Any]
    target_agencies: list[str] | None = None


class FederatedSearchRequest(BaseModel):
    """Request for federated search"""
    query: str
    entity_types: list[str] | None = None
    target_agencies: list[str] | None = None
    max_results: int = 100
    include_masked: bool = False


class NotificationRequest(BaseModel):
    """Request to send notification"""
    notification_type: str
    priority: str = "medium"
    title: str
    content: str
    target_agencies: list[str]
    target_roles: list[str] | None = None
    location: dict[str, Any] | None = None
    expires_at: str | None = None
    requires_acknowledgment: bool = False


class BOLOBroadcastRequest(BaseModel):
    """Request to broadcast BOLO"""
    bolo_type: str
    priority: str = "high"
    title: str
    description: str
    target_agencies: list[str]
    person_description: dict[str, Any] | None = None
    vehicle_description: dict[str, Any] | None = None
    last_known_location: dict[str, Any] | None = None
    direction_of_travel: str | None = None
    armed_dangerous: bool = False
    case_number: str | None = None
    contact_info: str | None = None


class MissionCreateRequest(BaseModel):
    """Request to create mission room"""
    name: str
    mission_type: str
    description: str
    participating_agencies: list[str]
    start_time: str | None = None
    end_time: str | None = None
    location: dict[str, Any] | None = None
    related_incident_id: str | None = None


class MissionInviteRequest(BaseModel):
    """Request to invite agency to mission"""
    mission_id: str
    agency_id: str


class MissionNoteRequest(BaseModel):
    """Request to add note to mission"""
    mission_id: str
    title: str
    content: str
    note_type: str = "general"
    is_pinned: bool = False


class MissionMessageRequest(BaseModel):
    """Request to send message in mission room"""
    mission_id: str
    message_type: str = "chat"
    content: str
    priority: str = "normal"
    mentions: list[str] | None = None


class HandoffRequest(BaseModel):
    """Request to initiate incident handoff"""
    mission_id: str
    incident_id: str
    to_agency: str
    reason: str
    handoff_notes: str | None = None
    resources_transferred: list[str] | None = None


class HeatmapRequest(BaseModel):
    """Request to generate heatmap"""
    name: str
    participating_agencies: list[str]
    time_range: str = "last_30_days"
    bounds: dict[str, float] | None = None
    resolution: float = 0.01


class PatternDetectionRequest(BaseModel):
    """Request to detect patterns"""
    participating_agencies: list[str]
    time_range: str = "last_30_days"
    pattern_types: list[str] | None = None
    min_confidence: float = 0.7


# ==================== Agency Management Endpoints ====================


@router.post("/agency/register")
async def register_agency(request: AgencyRegisterRequest) -> dict[str, Any]:
    """Register a new partner agency"""
    try:
        agency_type = AgencyType(request.agency_type)
    except ValueError:
        agency_type = AgencyType.LOCAL_PD

    try:
        sharing_level = DataSharingLevel(request.data_sharing_level)
    except ValueError:
        sharing_level = DataSharingLevel.BASIC

    agency = federation_manager.registry.register_agency(
        agency_name=request.agency_name,
        agency_type=agency_type,
        jurisdiction=request.jurisdiction,
        contact_email=request.contact_email,
        contact_phone=request.contact_phone,
        api_endpoint=request.api_endpoint,
        data_sharing_level=sharing_level,
    )

    return {
        "success": True,
        "agency_id": agency.id,
        "agency_name": agency.name,
        "status": agency.status.value,
    }


@router.post("/agency/configure")
async def configure_agency(request: AgencyConfigureRequest) -> dict[str, Any]:
    """Configure agency settings"""
    agency = federation_manager.registry.get_agency(request.agency_id)
    if not agency:
        raise HTTPException(status_code=404, detail="Agency not found")

    # Update settings
    for key, value in request.settings.items():
        if hasattr(agency, key):
            setattr(agency, key, value)

    return {
        "success": True,
        "agency_id": agency.id,
        "updated_settings": list(request.settings.keys()),
    }


@router.get("/agency/list")
async def list_agencies(
    agency_type: str | None = None,
    status: str | None = None,
) -> dict[str, Any]:
    """List all registered agencies"""
    filter_type = None
    filter_status = None

    if agency_type:
        try:
            filter_type = AgencyType(agency_type)
        except ValueError:
            pass

    if status:
        try:
            filter_status = AgencyStatus(status)
        except ValueError:
            pass

    agencies = federation_manager.registry.list_agencies(
        agency_type=filter_type,
        status=filter_status,
    )

    return {
        "agencies": [
            {
                "id": a.id,
                "name": a.name,
                "type": a.agency_type.value,
                "status": a.status.value,
                "jurisdiction": a.jurisdiction,
                "data_sharing_level": a.data_sharing_level.value,
            }
            for a in agencies
        ],
        "total": len(agencies),
    }


@router.get("/agency/{agency_id}")
async def get_agency(agency_id: str) -> dict[str, Any]:
    """Get agency details"""
    agency = federation_manager.registry.get_agency(agency_id)
    if not agency:
        raise HTTPException(status_code=404, detail="Agency not found")

    return {
        "id": agency.id,
        "name": agency.name,
        "type": agency.agency_type.value,
        "status": agency.status.value,
        "jurisdiction": agency.jurisdiction,
        "contact_email": agency.contact_email,
        "contact_phone": agency.contact_phone,
        "data_sharing_level": agency.data_sharing_level.value,
        "created_at": agency.created_at.isoformat(),
    }


# ==================== Federated Query Endpoints ====================


@router.post("/query")
async def execute_federated_query(request: FederatedQueryRequest) -> dict[str, Any]:
    """Execute a federated query across agencies"""
    result = await federation_manager.execute_federated_query(
        query_type=request.query_type,
        parameters=request.parameters,
        requesting_agency="local",
        requesting_user="system",
        target_agencies=request.target_agencies,
    )

    return {
        "query_id": result.id,
        "status": result.status,
        "results": result.results,
        "agencies_queried": result.agencies_queried,
        "execution_time_ms": result.execution_time_ms,
    }


@router.post("/search")
async def federated_search(request: FederatedSearchRequest) -> dict[str, Any]:
    """Execute federated search across agencies"""
    entity_types = None
    if request.entity_types:
        entity_types = []
        for et in request.entity_types:
            try:
                entity_types.append(SearchEntityType(et))
            except ValueError:
                pass

    results = await federated_search_engine.search(
        query=request.query,
        entity_types=entity_types,
        requesting_agency="local",
        requesting_user="system",
        max_results=request.max_results,
    )

    return {
        "query": request.query,
        "results": [
            {
                "id": r.id,
                "entity_type": r.entity_type.value,
                "source": r.source.value,
                "data": r.data,
                "confidence_score": r.confidence_score,
                "agency_id": r.agency_id,
            }
            for r in results
        ],
        "total": len(results),
    }


# ==================== Sync Endpoints ====================


@router.post("/sync/pull")
async def sync_pull(
    agency_id: str,
    data_types: list[str] | None = None,
) -> dict[str, Any]:
    """Pull data from partner agency"""
    categories = None
    if data_types:
        categories = []
        for dt in data_types:
            try:
                categories.append(DataCategory(dt))
            except ValueError:
                pass

    result = await federation_manager.sync_from_agency(
        agency_id=agency_id,
        data_categories=categories,
    )

    return {
        "sync_id": result.id,
        "agency_id": agency_id,
        "direction": result.direction.value,
        "status": result.status,
        "records_synced": result.records_synced,
    }


@router.post("/sync/push")
async def sync_push(
    agency_id: str,
    data_types: list[str] | None = None,
) -> dict[str, Any]:
    """Push data to partner agency"""
    categories = None
    if data_types:
        categories = []
        for dt in data_types:
            try:
                categories.append(DataCategory(dt))
            except ValueError:
                pass

    result = await federation_manager.sync_to_agency(
        agency_id=agency_id,
        data_categories=categories,
    )

    return {
        "sync_id": result.id,
        "agency_id": agency_id,
        "direction": result.direction.value,
        "status": result.status,
        "records_synced": result.records_synced,
    }


# ==================== Notification Endpoints ====================


@router.post("/notify")
async def send_notification(request: NotificationRequest) -> dict[str, Any]:
    """Send multi-agency notification"""
    try:
        notification_type = NotificationType(request.notification_type)
    except ValueError:
        notification_type = NotificationType.GENERAL_BROADCAST

    try:
        priority = NotificationPriority(request.priority)
    except ValueError:
        priority = NotificationPriority.MEDIUM

    expires_at = None
    if request.expires_at:
        expires_at = datetime.fromisoformat(request.expires_at)

    notification = notification_engine.send_notification(
        notification_type=notification_type,
        priority=priority,
        title=request.title,
        content=request.content,
        sender_agency="local",
        sender_user="system",
        target_agencies=request.target_agencies,
        target_roles=request.target_roles,
        location=request.location,
        expires_at=expires_at,
        requires_acknowledgment=request.requires_acknowledgment,
    )

    return {
        "notification_id": notification.id,
        "type": notification.notification_type.value,
        "priority": notification.priority.value,
        "target_agencies": notification.target_agencies,
        "created_at": notification.created_at.isoformat(),
    }


@router.get("/notifications/{agency_id}")
async def get_notifications(
    agency_id: str,
    notification_type: str | None = None,
    priority: str | None = None,
    limit: int = Query(default=100, le=500),
) -> dict[str, Any]:
    """Get notifications for an agency"""
    filter_type = None
    filter_priority = None

    if notification_type:
        try:
            filter_type = NotificationType(notification_type)
        except ValueError:
            pass

    if priority:
        try:
            filter_priority = NotificationPriority(priority)
        except ValueError:
            pass

    notifications = notification_engine.get_notifications_for_agency(
        agency_id=agency_id,
        notification_type=filter_type,
        priority=filter_priority,
        limit=limit,
    )

    return {
        "agency_id": agency_id,
        "notifications": [
            {
                "id": n.id,
                "type": n.notification_type.value,
                "priority": n.priority.value,
                "title": n.title,
                "content": n.content,
                "sender_agency": n.sender_agency,
                "created_at": n.created_at.isoformat(),
                "requires_acknowledgment": n.requires_acknowledgment,
            }
            for n in notifications
        ],
        "total": len(notifications),
    }


@router.post("/notify/bolo")
async def broadcast_bolo(request: BOLOBroadcastRequest) -> dict[str, Any]:
    """Broadcast BOLO to multiple agencies"""
    try:
        priority = NotificationPriority(request.priority)
    except ValueError:
        priority = NotificationPriority.HIGH

    bolo = notification_engine.broadcast_bolo(
        bolo_type=request.bolo_type,
        priority=priority,
        title=request.title,
        description=request.description,
        sender_agency="local",
        sender_user="system",
        target_agencies=request.target_agencies,
        person_description=request.person_description,
        vehicle_description=request.vehicle_description,
        last_known_location=request.last_known_location,
        direction_of_travel=request.direction_of_travel,
        armed_dangerous=request.armed_dangerous,
        case_number=request.case_number,
        contact_info=request.contact_info,
    )

    return {
        "bolo_id": bolo.id,
        "type": bolo.bolo_type,
        "priority": bolo.priority.value,
        "target_agencies": bolo.target_agencies,
        "is_active": bolo.is_active,
        "created_at": bolo.created_at.isoformat(),
    }


@router.post("/notify/bolo/{bolo_id}/cancel")
async def cancel_bolo(
    bolo_id: str,
    reason: str,
) -> dict[str, Any]:
    """Cancel an active BOLO"""
    bolo = notification_engine.cancel_bolo(
        bolo_id=bolo_id,
        cancelled_by="system",
        cancel_reason=reason,
    )

    if not bolo:
        raise HTTPException(status_code=404, detail="BOLO not found or already cancelled")

    return {
        "bolo_id": bolo.id,
        "is_active": bolo.is_active,
        "cancelled_at": bolo.cancelled_at.isoformat() if bolo.cancelled_at else None,
        "cancel_reason": bolo.cancel_reason,
    }


@router.get("/bolos/active")
async def get_active_bolos(
    agency_id: str | None = None,
) -> dict[str, Any]:
    """Get active BOLOs"""
    bolos = notification_engine.get_active_bolos(agency_id=agency_id)

    return {
        "bolos": [
            {
                "id": b.id,
                "type": b.bolo_type,
                "priority": b.priority.value,
                "title": b.title,
                "description": b.description,
                "armed_dangerous": b.armed_dangerous,
                "target_agencies": b.target_agencies,
                "created_at": b.created_at.isoformat(),
            }
            for b in bolos
        ],
        "total": len(bolos),
    }


# ==================== Mission Room Endpoints ====================


@router.post("/mission/create")
async def create_mission(request: MissionCreateRequest) -> dict[str, Any]:
    """Create a new mission room"""
    try:
        mission_type = MissionType(request.mission_type)
    except ValueError:
        mission_type = MissionType.JOINT_OPERATION

    start_time = None
    end_time = None
    if request.start_time:
        start_time = datetime.fromisoformat(request.start_time)
    if request.end_time:
        end_time = datetime.fromisoformat(request.end_time)

    mission = mission_room_manager.create_mission(
        name=request.name,
        mission_type=mission_type,
        description=request.description,
        lead_agency="local",
        created_by="system",
        participating_agencies=request.participating_agencies,
        start_time=start_time,
        end_time=end_time,
        location=request.location,
        related_incident_id=request.related_incident_id,
    )

    return {
        "mission_id": mission.id,
        "name": mission.name,
        "type": mission.mission_type.value,
        "status": mission.status.value,
        "participating_agencies": mission.participating_agencies,
        "created_at": mission.created_at.isoformat(),
    }


@router.post("/mission/invite")
async def invite_to_mission(request: MissionInviteRequest) -> dict[str, Any]:
    """Invite an agency to join a mission"""
    success = mission_room_manager.invite_agency(
        mission_id=request.mission_id,
        agency_id=request.agency_id,
        invited_by="system",
    )

    if not success:
        raise HTTPException(
            status_code=400,
            detail="Failed to invite agency (mission not found or agency already invited)",
        )

    return {
        "success": True,
        "mission_id": request.mission_id,
        "invited_agency": request.agency_id,
    }


@router.post("/mission/add-note")
async def add_mission_note(request: MissionNoteRequest) -> dict[str, Any]:
    """Add a note to a mission room"""
    note = mission_room_manager.add_note(
        mission_id=request.mission_id,
        author_agency="local",
        author_user="system",
        author_name="System",
        title=request.title,
        content=request.content,
        note_type=request.note_type,
        is_pinned=request.is_pinned,
    )

    if not note:
        raise HTTPException(status_code=404, detail="Mission not found")

    return {
        "note_id": note.id,
        "mission_id": note.mission_id,
        "title": note.title,
        "created_at": note.created_at.isoformat(),
    }


@router.post("/mission/message")
async def send_mission_message(request: MissionMessageRequest) -> dict[str, Any]:
    """Send a message in a mission room"""
    try:
        message_type = MessageType(request.message_type)
    except ValueError:
        message_type = MessageType.CHAT

    message = mission_room_manager.send_message(
        mission_id=request.mission_id,
        sender_agency="local",
        sender_user="system",
        sender_name="System",
        message_type=message_type,
        content=request.content,
        priority=request.priority,
        mentions=request.mentions,
    )

    if not message:
        raise HTTPException(status_code=404, detail="Mission not found")

    return {
        "message_id": message.id,
        "mission_id": message.mission_id,
        "type": message.message_type.value,
        "created_at": message.created_at.isoformat(),
    }


@router.get("/mission/{mission_id}")
async def get_mission(mission_id: str) -> dict[str, Any]:
    """Get mission room details"""
    mission = mission_room_manager.get_mission(mission_id)
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")

    return {
        "id": mission.id,
        "name": mission.name,
        "type": mission.mission_type.value,
        "status": mission.status.value,
        "description": mission.description,
        "lead_agency": mission.lead_agency,
        "participating_agencies": mission.participating_agencies,
        "participant_count": len([p for p in mission.participants if p.is_active]),
        "message_count": len(mission.messages),
        "file_count": len(mission.files),
        "note_count": len(mission.notes),
        "created_at": mission.created_at.isoformat(),
    }


@router.get("/mission/{mission_id}/messages")
async def get_mission_messages(
    mission_id: str,
    limit: int = Query(default=100, le=500),
) -> dict[str, Any]:
    """Get messages from a mission room"""
    messages = mission_room_manager.get_messages(
        mission_id=mission_id,
        limit=limit,
    )

    return {
        "mission_id": mission_id,
        "messages": [
            {
                "id": m.id,
                "type": m.message_type.value,
                "sender_agency": m.sender_agency,
                "sender_name": m.sender_name,
                "content": m.content,
                "priority": m.priority,
                "created_at": m.created_at.isoformat(),
            }
            for m in messages
        ],
        "total": len(messages),
    }


@router.get("/missions")
async def list_missions(
    agency_id: str | None = None,
    status: str | None = None,
    mission_type: str | None = None,
) -> dict[str, Any]:
    """List mission rooms"""
    filter_status = None
    filter_type = None

    if status:
        try:
            filter_status = MissionRoomStatus(status)
        except ValueError:
            pass

    if mission_type:
        try:
            filter_type = MissionType(mission_type)
        except ValueError:
            pass

    missions = mission_room_manager.list_missions(
        agency_id=agency_id,
        status=filter_status,
        mission_type=filter_type,
    )

    return {
        "missions": [
            {
                "id": m.id,
                "name": m.name,
                "type": m.mission_type.value,
                "status": m.status.value,
                "lead_agency": m.lead_agency,
                "participating_agencies": m.participating_agencies,
                "created_at": m.created_at.isoformat(),
            }
            for m in missions
        ],
        "total": len(missions),
    }


@router.post("/mission/handoff")
async def initiate_handoff(request: HandoffRequest) -> dict[str, Any]:
    """Initiate incident handoff between agencies"""
    handoff = mission_room_manager.initiate_handoff(
        mission_id=request.mission_id,
        incident_id=request.incident_id,
        from_agency="local",
        to_agency=request.to_agency,
        initiated_by="system",
        reason=request.reason,
        handoff_notes=request.handoff_notes,
        resources_transferred=request.resources_transferred,
    )

    if not handoff:
        raise HTTPException(status_code=404, detail="Mission not found")

    return {
        "handoff_id": handoff.id,
        "mission_id": handoff.mission_id,
        "incident_id": handoff.incident_id,
        "from_agency": handoff.from_agency,
        "to_agency": handoff.to_agency,
        "status": handoff.status.value,
        "initiated_at": handoff.initiated_at.isoformat(),
    }


# ==================== Analytics Endpoints ====================


@router.get("/analytics/heatmap")
async def generate_heatmap(
    name: str = "Cross-Jurisdiction Heatmap",
    agencies: str = "",
    time_range: str = "last_30_days",
) -> dict[str, Any]:
    """Generate cross-jurisdiction heatmap"""
    participating_agencies = [a.strip() for a in agencies.split(",") if a.strip()]

    try:
        tr = AnalyticsTimeRange(time_range)
    except ValueError:
        tr = AnalyticsTimeRange.LAST_30_DAYS

    heatmap = analytics_engine.generate_cross_jurisdiction_heatmap(
        name=name,
        participating_agencies=participating_agencies,
        time_range=tr,
    )

    return {
        "heatmap_id": heatmap.id,
        "name": heatmap.name,
        "participating_agencies": heatmap.participating_agencies,
        "time_range": heatmap.time_range.value,
        "total_incidents": heatmap.total_incidents,
        "agency_totals": heatmap.agency_totals,
        "cell_count": len(heatmap.cells),
        "created_at": heatmap.created_at.isoformat(),
    }


@router.get("/analytics/patterns")
async def detect_patterns(
    agencies: str = "",
    time_range: str = "last_30_days",
    min_confidence: float = 0.7,
) -> dict[str, Any]:
    """Detect regional patterns across jurisdictions"""
    participating_agencies = [a.strip() for a in agencies.split(",") if a.strip()]

    try:
        tr = AnalyticsTimeRange(time_range)
    except ValueError:
        tr = AnalyticsTimeRange.LAST_30_DAYS

    patterns = analytics_engine.detect_regional_patterns(
        participating_agencies=participating_agencies,
        time_range=tr,
        min_confidence=min_confidence,
    )

    return {
        "patterns": [
            {
                "id": p.id,
                "type": p.pattern_type.value,
                "name": p.name,
                "description": p.description,
                "confidence_score": p.confidence_score,
                "affected_agencies": p.affected_agencies,
                "risk_level": p.risk_level.value,
                "detected_at": p.detected_at.isoformat(),
            }
            for p in patterns
        ],
        "total": len(patterns),
    }


@router.get("/analytics/hotspot-comparison")
async def compare_hotspots(
    agencies: str = "",
    time_range: str = "last_30_days",
) -> dict[str, Any]:
    """Compare hotspots between agencies"""
    agency_list = [a.strip() for a in agencies.split(",") if a.strip()]

    try:
        tr = AnalyticsTimeRange(time_range)
    except ValueError:
        tr = AnalyticsTimeRange.LAST_30_DAYS

    comparison = analytics_engine.compare_hotspots(
        agencies=agency_list,
        time_range=tr,
    )

    return {
        "comparison_id": comparison.id,
        "agencies": comparison.agencies,
        "time_range": comparison.time_range.value,
        "shared_hotspots": comparison.shared_hotspots,
        "correlation_matrix": comparison.correlation_matrix,
        "created_at": comparison.created_at.isoformat(),
    }


@router.get("/analytics/summary/{agency_id}")
async def get_analytics_summary(
    agency_id: str,
    time_range: str = "last_30_days",
) -> dict[str, Any]:
    """Get analytics summary for an agency"""
    try:
        tr = AnalyticsTimeRange(time_range)
    except ValueError:
        tr = AnalyticsTimeRange.LAST_30_DAYS

    return analytics_engine.get_analytics_summary(
        agency_id=agency_id,
        time_range=tr,
    )


# ==================== Security & Audit Endpoints ====================


@router.get("/audit/log")
async def get_audit_log(
    agency_id: str | None = None,
    event_type: str | None = None,
    user_id: str | None = None,
    limit: int = Query(default=100, le=1000),
) -> dict[str, Any]:
    """Get federated audit log"""
    filter_event_type = None
    if event_type:
        try:
            filter_event_type = AuditEventType(event_type)
        except ValueError:
            pass

    entries = security_manager.get_audit_log(
        agency_id=agency_id,
        event_type=filter_event_type,
        user_id=user_id,
        limit=limit,
    )

    return {
        "entries": [
            {
                "id": e.id,
                "event_type": e.event_type.value,
                "agency_id": e.agency_id,
                "user_id": e.user_id,
                "resource_type": e.resource_type,
                "action": e.action,
                "access_decision": e.access_decision.value if e.access_decision else None,
                "timestamp": e.timestamp.isoformat(),
            }
            for e in entries
        ],
        "total": len(entries),
    }


@router.get("/audit/compliance/{agency_id}")
async def get_compliance_report(
    agency_id: str,
    start_date: str | None = None,
    end_date: str | None = None,
) -> dict[str, Any]:
    """Get CJIS compliance report for an agency"""
    if end_date:
        end_dt = datetime.fromisoformat(end_date)
    else:
        end_dt = datetime.utcnow()

    if start_date:
        start_dt = datetime.fromisoformat(start_date)
    else:
        from datetime import timedelta
        start_dt = end_dt - timedelta(days=30)

    return security_manager.get_compliance_report(
        agency_id=agency_id,
        start_date=start_dt,
        end_date=end_dt,
    )


@router.post("/security/grant-permission")
async def grant_permission(
    requesting_agency: str,
    target_agency: str,
    resource_types: list[str],
) -> dict[str, Any]:
    """Grant permission for agency to access another agency's data"""
    security_manager.grant_agency_permission(
        requesting_agency=requesting_agency,
        target_agency=target_agency,
        resource_types=resource_types,
        granted_by="system",
    )

    return {
        "success": True,
        "requesting_agency": requesting_agency,
        "target_agency": target_agency,
        "resource_types": resource_types,
    }


@router.post("/security/revoke-permission")
async def revoke_permission(
    requesting_agency: str,
    target_agency: str,
) -> dict[str, Any]:
    """Revoke permission for agency"""
    security_manager.revoke_agency_permission(
        requesting_agency=requesting_agency,
        target_agency=target_agency,
        revoked_by="system",
    )

    return {
        "success": True,
        "requesting_agency": requesting_agency,
        "target_agency": target_agency,
    }
