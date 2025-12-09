"""
Command Operations API endpoints for G3TI RTCC-UIP.

Phase 8: Mission Management & Command Operations Suite
"""

from typing import Any

import structlog
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.command.briefing import (
    BriefingGenerator,
    ExportFormat,
    NotePriority,
    NoteType,
)
from app.command.ics import ICSManager, ICSRole
from app.command.major_incident import (
    GeoLocation,
    IncidentPriority,
    IncidentStatus,
    IncidentType,
    MajorIncidentEngine,
)
from app.command.multiagency import (
    AccessLevel,
    AgencyType,
    DataCategory,
    MultiAgencyCoordinator,
)
from app.command.resources import (
    ResourceManager,
    ResourceType,
)
from app.command.strategy_map import (
    GeoPoint,
    MarkerType,
    OverlayType,
    ShapeType,
    StrategyMapManager,
)
from app.command.timeline import (
    EventPriority,
    EventSource,
    TimelineEngine,
    TimelineEventType,
)

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/api/command", tags=["command"])

# Initialize managers (in production, use dependency injection)
incident_engine = MajorIncidentEngine()
ics_manager = ICSManager()
strategy_map_manager = StrategyMapManager()
resource_manager = ResourceManager()
timeline_engine = TimelineEngine()
briefing_generator = BriefingGenerator()
multiagency_coordinator = MultiAgencyCoordinator()


# ============================================================
# Request/Response Models
# ============================================================


class CreateIncidentRequest(BaseModel):
    """Request to create a major incident."""

    incident_type: IncidentType
    title: str
    description: str | None = None
    priority: IncidentPriority = IncidentPriority.HIGH
    latitude: float | None = None
    longitude: float | None = None
    address: str | None = None
    created_by: str | None = None


class ActivateIncidentRequest(BaseModel):
    """Request to activate an incident."""

    activated_by: str | None = None


class CloseIncidentRequest(BaseModel):
    """Request to close an incident."""

    closed_by: str | None = None
    resolution: str | None = None


class AssignCommanderRequest(BaseModel):
    """Request to assign a commander."""

    badge: str
    name: str | None = None
    assigned_by: str | None = None


class AssignICSRoleRequest(BaseModel):
    """Request to assign an ICS role."""

    role: ICSRole
    badge: str
    name: str | None = None
    assigned_by: str | None = None


class ReassignICSRoleRequest(BaseModel):
    """Request to reassign an ICS role."""

    role: ICSRole
    new_badge: str
    new_name: str | None = None
    reassigned_by: str | None = None


class UpdateMapRequest(BaseModel):
    """Request to update strategy map."""

    center_lat: float | None = None
    center_lng: float | None = None
    zoom: int | None = None
    updated_by: str | None = None


class AddMarkerRequest(BaseModel):
    """Request to add a map marker."""

    layer_id: str
    marker_type: MarkerType
    latitude: float
    longitude: float
    label: str | None = None
    description: str | None = None
    color: str | None = None
    created_by: str | None = None


class AddShapeRequest(BaseModel):
    """Request to add a map shape."""

    layer_id: str
    shape_type: ShapeType
    overlay_type: OverlayType
    coordinates: list[dict[str, float]] | None = None
    center_lat: float | None = None
    center_lng: float | None = None
    radius_meters: float | None = None
    label: str | None = None
    stroke_color: str = "#FF0000"
    fill_color: str | None = "#FF000033"
    created_by: str | None = None


class DrawPerimeterRequest(BaseModel):
    """Request to draw a perimeter."""

    coordinates: list[dict[str, float]]
    label: str = "Perimeter"
    perimeter_type: str = "outer"
    created_by: str | None = None


class AssignResourceRequest(BaseModel):
    """Request to assign a resource."""

    resource_id: str
    role: str | None = None
    assigned_by: str | None = None


class ReleaseResourceRequest(BaseModel):
    """Request to release a resource."""

    resource_id: str
    released_by: str | None = None


class AddTimelineEventRequest(BaseModel):
    """Request to add a timeline event."""

    event_type: TimelineEventType
    source: EventSource
    title: str
    description: str | None = None
    priority: EventPriority = EventPriority.MEDIUM
    user_id: str | None = None
    user_name: str | None = None


class AddCommandNoteRequest(BaseModel):
    """Request to add a command note."""

    content: str
    note_type: NoteType = NoteType.GENERAL
    priority: NotePriority = NotePriority.MEDIUM
    title: str | None = None
    tags: list[str] | None = None
    created_by: str | None = None
    created_by_name: str | None = None


class GenerateBriefingRequest(BaseModel):
    """Request to generate a briefing."""

    generated_by: str | None = None


class ExportBriefingRequest(BaseModel):
    """Request to export a briefing."""

    format: ExportFormat


class AddAgencyRequest(BaseModel):
    """Request to add an agency to incident."""

    agency_id: str
    access_level: AccessLevel | None = None
    liaison_badge: str | None = None
    liaison_name: str | None = None
    added_by: str | None = None


class UpdateAgencyAccessRequest(BaseModel):
    """Request to update agency access."""

    access_level: AccessLevel | None = None
    allowed_data: list[DataCategory] | None = None
    denied_data: list[DataCategory] | None = None
    updated_by: str | None = None


# ============================================================
# Incident Endpoints
# ============================================================


@router.post("/incident/create")
async def create_incident(request: CreateIncidentRequest) -> dict[str, Any]:
    """Create a new major incident."""
    location = None
    if request.latitude and request.longitude:
        location = GeoLocation(
            latitude=request.latitude,
            longitude=request.longitude,
            address=request.address,
        )

    incident = await incident_engine.create_incident(
        incident_type=request.incident_type,
        title=request.title,
        description=request.description,
        priority=request.priority,
        location=location,
        created_by=request.created_by,
    )

    # Create strategy map for incident
    center = GeoPoint(latitude=request.latitude, longitude=request.longitude) if request.latitude else None
    await strategy_map_manager.create_map(
        incident_id=incident.id,
        center=center,
        created_by=request.created_by,
    )

    logger.info("incident_created_via_api", incident_id=incident.id)
    return {"success": True, "incident": incident.model_dump()}


@router.post("/incident/activate")
async def activate_incident(
    incident_id: str = Query(...),
    request: ActivateIncidentRequest = None,
) -> dict[str, Any]:
    """Activate a major incident."""
    activated_by = request.activated_by if request else None
    incident = await incident_engine.activate_incident(
        incident_id=incident_id,
        activated_by=activated_by,
    )

    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    # Log to timeline
    await timeline_engine.add_event(
        incident_id=incident_id,
        event_type=TimelineEventType.INCIDENT_ACTIVATED,
        source=EventSource.COMMAND,
        title="Incident Activated",
        description=f"Incident activated by {activated_by or 'system'}",
        priority=EventPriority.HIGH,
        user_id=activated_by,
    )

    return {"success": True, "incident": incident.model_dump()}


@router.post("/incident/close")
async def close_incident(
    incident_id: str = Query(...),
    request: CloseIncidentRequest = None,
) -> dict[str, Any]:
    """Close a major incident."""
    closed_by = request.closed_by if request else None
    resolution = request.resolution if request else None

    incident = await incident_engine.close_incident(
        incident_id=incident_id,
        closed_by=closed_by,
        resolution=resolution,
    )

    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    # Log to timeline
    await timeline_engine.add_event(
        incident_id=incident_id,
        event_type=TimelineEventType.INCIDENT_CLOSED,
        source=EventSource.COMMAND,
        title="Incident Closed",
        description=resolution or f"Incident closed by {closed_by or 'system'}",
        priority=EventPriority.HIGH,
        user_id=closed_by,
    )

    return {"success": True, "incident": incident.model_dump()}


@router.get("/incident/{incident_id}")
async def get_incident(incident_id: str) -> dict[str, Any]:
    """Get incident details."""
    incident = incident_engine.get_incident(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    return {"success": True, "incident": incident.model_dump()}


@router.get("/incidents/active")
async def get_active_incidents() -> dict[str, Any]:
    """Get all active incidents."""
    incidents = await incident_engine.get_active_incidents()
    return {
        "success": True,
        "incidents": [i.model_dump() for i in incidents],
        "count": len(incidents),
    }


@router.get("/incidents")
async def get_all_incidents(
    status: IncidentStatus | None = None,
    incident_type: IncidentType | None = None,
    limit: int = 50,
) -> dict[str, Any]:
    """Get all incidents with optional filters."""
    incidents = await incident_engine.get_all_incidents(
        status=status,
        incident_type=incident_type,
        limit=limit,
    )
    return {
        "success": True,
        "incidents": [i.model_dump() for i in incidents],
        "count": len(incidents),
    }


@router.post("/incident/{incident_id}/commander")
async def assign_commander(
    incident_id: str,
    request: AssignCommanderRequest,
) -> dict[str, Any]:
    """Assign incident commander."""
    incident = await incident_engine.assign_commander(
        incident_id=incident_id,
        badge=request.badge,
        name=request.name,
        assigned_by=request.assigned_by,
    )

    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    # Also assign ICS role
    await ics_manager.assign_role(
        incident_id=incident_id,
        role=ICSRole.INCIDENT_COMMANDER,
        badge=request.badge,
        name=request.name,
        assigned_by=request.assigned_by,
    )

    # Log to timeline
    await timeline_engine.log_ics_change(
        incident_id=incident_id,
        event_type=TimelineEventType.COMMANDER_CHANGE,
        role="incident_commander",
        badge=request.badge,
        name=request.name,
        assigned_by=request.assigned_by,
    )

    return {"success": True, "incident": incident.model_dump()}


# ============================================================
# ICS Endpoints
# ============================================================


@router.post("/ics/assign_role")
async def assign_ics_role(
    incident_id: str = Query(...),
    request: AssignICSRoleRequest = None,
) -> dict[str, Any]:
    """Assign an ICS role."""
    if not request:
        raise HTTPException(status_code=400, detail="Request body required")

    assignment = await ics_manager.assign_role(
        incident_id=incident_id,
        role=request.role,
        badge=request.badge,
        name=request.name,
        assigned_by=request.assigned_by,
    )

    # Log to timeline
    await timeline_engine.log_ics_change(
        incident_id=incident_id,
        event_type=TimelineEventType.ICS_ROLE_ASSIGNED,
        role=request.role.value if isinstance(request.role, ICSRole) else request.role,
        badge=request.badge,
        name=request.name,
        assigned_by=request.assigned_by,
    )

    return {"success": True, "assignment": assignment.model_dump()}


@router.post("/ics/reassign_role")
async def reassign_ics_role(
    incident_id: str = Query(...),
    request: ReassignICSRoleRequest = None,
) -> dict[str, Any]:
    """Reassign an ICS role."""
    if not request:
        raise HTTPException(status_code=400, detail="Request body required")

    assignment = await ics_manager.reassign_role(
        incident_id=incident_id,
        role=request.role,
        new_badge=request.new_badge,
        new_name=request.new_name,
        reassigned_by=request.reassigned_by,
    )

    if not assignment:
        raise HTTPException(status_code=404, detail="Role not found")

    # Log to timeline
    await timeline_engine.log_ics_change(
        incident_id=incident_id,
        event_type=TimelineEventType.ICS_ROLE_CHANGED,
        role=request.role.value if isinstance(request.role, ICSRole) else request.role,
        badge=request.new_badge,
        name=request.new_name,
        assigned_by=request.reassigned_by,
    )

    return {"success": True, "assignment": assignment.model_dump()}


@router.get("/ics/structure/{incident_id}")
async def get_ics_structure(incident_id: str) -> dict[str, Any]:
    """Get ICS structure for an incident."""
    org_chart = await ics_manager.get_org_chart(incident_id)
    return {"success": True, "org_chart": org_chart.model_dump()}


@router.get("/ics/checklist/{incident_id}/{role}")
async def get_ics_checklist(incident_id: str, role: ICSRole) -> dict[str, Any]:
    """Get checklist for an ICS role."""
    checklist = await ics_manager.get_role_checklist(incident_id, role)
    return {
        "success": True,
        "checklist": [item.model_dump() for item in checklist],
    }


# ============================================================
# Strategy Map Endpoints
# ============================================================


@router.post("/strategy/map/update")
async def update_strategy_map(
    incident_id: str = Query(...),
    request: UpdateMapRequest = None,
) -> dict[str, Any]:
    """Update strategy map center/zoom."""
    if not request:
        raise HTTPException(status_code=400, detail="Request body required")

    center = None
    if request.center_lat and request.center_lng:
        center = GeoPoint(latitude=request.center_lat, longitude=request.center_lng)

    strategy_map = await strategy_map_manager.update_map_center(
        incident_id=incident_id,
        center=center,
        zoom=request.zoom,
        updated_by=request.updated_by,
    )

    if not strategy_map:
        raise HTTPException(status_code=404, detail="Strategy map not found")

    return {"success": True, "map": strategy_map.model_dump()}


@router.get("/strategy/map/{incident_id}")
async def get_strategy_map(incident_id: str) -> dict[str, Any]:
    """Get strategy map for an incident."""
    strategy_map = await strategy_map_manager.get_map(incident_id)
    if not strategy_map:
        raise HTTPException(status_code=404, detail="Strategy map not found")

    return {"success": True, "map": strategy_map.model_dump()}


@router.post("/strategy/map/{incident_id}/marker")
async def add_map_marker(
    incident_id: str,
    request: AddMarkerRequest,
) -> dict[str, Any]:
    """Add a marker to the strategy map."""
    position = GeoPoint(latitude=request.latitude, longitude=request.longitude)

    marker = await strategy_map_manager.add_marker(
        incident_id=incident_id,
        layer_id=request.layer_id,
        marker_type=request.marker_type,
        position=position,
        label=request.label,
        description=request.description,
        color=request.color,
        created_by=request.created_by,
    )

    if not marker:
        raise HTTPException(status_code=404, detail="Map or layer not found")

    return {"success": True, "marker": marker.model_dump()}


@router.post("/strategy/map/{incident_id}/shape")
async def add_map_shape(
    incident_id: str,
    request: AddShapeRequest,
) -> dict[str, Any]:
    """Add a shape to the strategy map."""
    coordinates = None
    if request.coordinates:
        coordinates = [GeoPoint(latitude=c["latitude"], longitude=c["longitude"]) for c in request.coordinates]

    center = None
    if request.center_lat and request.center_lng:
        center = GeoPoint(latitude=request.center_lat, longitude=request.center_lng)

    shape = await strategy_map_manager.add_shape(
        incident_id=incident_id,
        layer_id=request.layer_id,
        shape_type=request.shape_type,
        overlay_type=request.overlay_type,
        coordinates=coordinates,
        center=center,
        radius_meters=request.radius_meters,
        label=request.label,
        stroke_color=request.stroke_color,
        fill_color=request.fill_color,
        created_by=request.created_by,
    )

    if not shape:
        raise HTTPException(status_code=404, detail="Map or layer not found")

    return {"success": True, "shape": shape.model_dump()}


@router.post("/strategy/map/{incident_id}/perimeter")
async def draw_perimeter(
    incident_id: str,
    request: DrawPerimeterRequest,
) -> dict[str, Any]:
    """Draw a perimeter on the strategy map."""
    coordinates = [GeoPoint(latitude=c["latitude"], longitude=c["longitude"]) for c in request.coordinates]

    shape = await strategy_map_manager.draw_perimeter(
        incident_id=incident_id,
        coordinates=coordinates,
        label=request.label,
        perimeter_type=request.perimeter_type,
        created_by=request.created_by,
    )

    if not shape:
        raise HTTPException(status_code=404, detail="Strategy map not found")

    # Log to timeline
    await timeline_engine.add_event(
        incident_id=incident_id,
        event_type=TimelineEventType.PERIMETER_ESTABLISHED,
        source=EventSource.TACTICAL,
        title=f"Perimeter Established: {request.label}",
        description=f"{request.perimeter_type.title()} perimeter established",
        priority=EventPriority.HIGH,
        user_id=request.created_by,
    )

    return {"success": True, "shape": shape.model_dump()}


# ============================================================
# Resource Endpoints
# ============================================================


@router.post("/resources/assign")
async def assign_resource(
    incident_id: str = Query(...),
    request: AssignResourceRequest = None,
) -> dict[str, Any]:
    """Assign a resource to an incident."""
    if not request:
        raise HTTPException(status_code=400, detail="Request body required")

    assignment = await resource_manager.assign_resource(
        incident_id=incident_id,
        resource_id=request.resource_id,
        role=request.role,
        assigned_by=request.assigned_by,
    )

    if not assignment:
        raise HTTPException(status_code=404, detail="Resource not found")

    # Log to timeline
    resource = resource_manager.get_resource(request.resource_id)
    if resource:
        await timeline_engine.log_resource_event(
            incident_id=incident_id,
            event_type=TimelineEventType.RESOURCE_ASSIGNED,
            resource_id=request.resource_id,
            resource_name=resource.name,
            resource_type=resource.resource_type,
            user_id=request.assigned_by,
        )

    return {"success": True, "assignment": assignment.model_dump()}


@router.post("/resources/release")
async def release_resource(
    incident_id: str = Query(...),
    request: ReleaseResourceRequest = None,
) -> dict[str, Any]:
    """Release a resource from an incident."""
    if not request:
        raise HTTPException(status_code=400, detail="Request body required")

    assignment = await resource_manager.release_resource(
        incident_id=incident_id,
        resource_id=request.resource_id,
        released_by=request.released_by,
    )

    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    # Log to timeline
    resource = resource_manager.get_resource(request.resource_id)
    if resource:
        await timeline_engine.log_resource_event(
            incident_id=incident_id,
            event_type=TimelineEventType.RESOURCE_RELEASED,
            resource_id=request.resource_id,
            resource_name=resource.name,
            resource_type=resource.resource_type,
            user_id=request.released_by,
        )

    return {"success": True, "assignment": assignment.model_dump()}


@router.get("/resources/{incident_id}")
async def get_incident_resources(
    incident_id: str,
    active_only: bool = True,
) -> dict[str, Any]:
    """Get resources assigned to an incident."""
    assignments = await resource_manager.get_incident_resources(
        incident_id=incident_id,
        active_only=active_only,
    )
    return {
        "success": True,
        "assignments": [a.model_dump() for a in assignments],
        "count": len(assignments),
    }


@router.get("/resources/available")
async def get_available_resources(
    resource_type: ResourceType | None = None,
) -> dict[str, Any]:
    """Get available resources."""
    resources = await resource_manager.get_available_resources(
        resource_type=resource_type,
    )
    return {
        "success": True,
        "resources": [r.model_dump() for r in resources],
        "count": len(resources),
    }


# ============================================================
# Timeline Endpoints
# ============================================================


@router.post("/timeline/add")
async def add_timeline_event(
    incident_id: str = Query(...),
    request: AddTimelineEventRequest = None,
) -> dict[str, Any]:
    """Add an event to the timeline."""
    if not request:
        raise HTTPException(status_code=400, detail="Request body required")

    event = await timeline_engine.add_event(
        incident_id=incident_id,
        event_type=request.event_type,
        source=request.source,
        title=request.title,
        description=request.description,
        priority=request.priority,
        user_id=request.user_id,
        user_name=request.user_name,
    )

    return {"success": True, "event": event.model_dump()}


@router.get("/timeline/{incident_id}")
async def get_timeline(
    incident_id: str,
    limit: int = 100,
    offset: int = 0,
) -> dict[str, Any]:
    """Get timeline for an incident."""
    events = await timeline_engine.get_timeline(
        incident_id=incident_id,
        limit=limit,
        offset=offset,
    )
    return {
        "success": True,
        "events": [e.model_dump() for e in events],
        "count": len(events),
    }


@router.get("/timeline/{incident_id}/critical")
async def get_critical_events(
    incident_id: str,
    limit: int = 20,
) -> dict[str, Any]:
    """Get critical events from timeline."""
    events = await timeline_engine.get_critical_events(
        incident_id=incident_id,
        limit=limit,
    )
    return {
        "success": True,
        "events": [e.model_dump() for e in events],
        "count": len(events),
    }


# ============================================================
# Briefing Endpoints
# ============================================================


@router.post("/briefing/add_note")
async def add_command_note(
    incident_id: str = Query(...),
    request: AddCommandNoteRequest = None,
) -> dict[str, Any]:
    """Add a command note."""
    if not request:
        raise HTTPException(status_code=400, detail="Request body required")

    note = await briefing_generator.add_note(
        incident_id=incident_id,
        content=request.content,
        note_type=request.note_type,
        priority=request.priority,
        title=request.title,
        tags=request.tags,
        created_by=request.created_by,
        created_by_name=request.created_by_name,
    )

    return {"success": True, "note": note.model_dump()}


@router.post("/briefing/generate/{incident_id}")
async def generate_briefing(
    incident_id: str,
    request: GenerateBriefingRequest = None,
) -> dict[str, Any]:
    """Generate a command briefing."""
    # Gather data from all sources
    incident = incident_engine.get_incident(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    ics_chart = await ics_manager.get_org_chart(incident_id)
    timeline_events = await timeline_engine.get_timeline(incident_id, limit=50)
    resources = await resource_manager.get_incident_resources(incident_id)
    strategy_map = await strategy_map_manager.get_map(incident_id)

    generated_by = request.generated_by if request else None

    briefing = await briefing_generator.generate_briefing(
        incident_id=incident_id,
        incident_data=incident.model_dump(),
        ics_data=ics_chart.model_dump() if ics_chart else None,
        timeline_data=[e.model_dump() for e in timeline_events],
        resources_data=[r.model_dump() for r in resources],
        strategy_map_data=strategy_map.model_dump() if strategy_map else None,
        generated_by=generated_by,
    )

    return {"success": True, "briefing": briefing.model_dump()}


@router.get("/briefing/{incident_id}")
async def get_briefings(
    incident_id: str,
    limit: int = 10,
) -> dict[str, Any]:
    """Get briefings for an incident."""
    briefings = await briefing_generator.get_briefings(
        incident_id=incident_id,
        limit=limit,
    )
    return {
        "success": True,
        "briefings": [b.model_dump() for b in briefings],
        "count": len(briefings),
    }


@router.post("/briefing/export/{incident_id}/{briefing_id}")
async def export_briefing(
    incident_id: str,
    briefing_id: str,
    request: ExportBriefingRequest,
) -> dict[str, Any]:
    """Export a briefing to a specific format."""
    try:
        result = await briefing_generator.export_briefing(
            incident_id=incident_id,
            briefing_id=briefing_id,
            format_type=request.format,
        )
        return {"success": True, "export": result}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.get("/briefing/notes/{incident_id}")
async def get_command_notes(
    incident_id: str,
    note_type: NoteType | None = None,
    limit: int = 100,
) -> dict[str, Any]:
    """Get command notes for an incident."""
    notes = await briefing_generator.get_notes(
        incident_id=incident_id,
        note_type=note_type,
        limit=limit,
    )
    return {
        "success": True,
        "notes": [n.model_dump() for n in notes],
        "count": len(notes),
    }


# ============================================================
# Multi-Agency Endpoints
# ============================================================


@router.post("/agency/add")
async def add_agency_to_incident(
    incident_id: str = Query(...),
    request: AddAgencyRequest = None,
) -> dict[str, Any]:
    """Add an agency to an incident."""
    if not request:
        raise HTTPException(status_code=400, detail="Request body required")

    participation = await multiagency_coordinator.add_agency_to_incident(
        incident_id=incident_id,
        agency_id=request.agency_id,
        access_level=request.access_level,
        liaison_badge=request.liaison_badge,
        liaison_name=request.liaison_name,
        added_by=request.added_by,
    )

    if not participation:
        raise HTTPException(status_code=404, detail="Agency not found")

    # Also add to incident
    agency = multiagency_coordinator.get_agency(request.agency_id)
    if agency:
        await incident_engine.add_agency(incident_id, agency.name)

    return {"success": True, "participation": participation.model_dump()}


@router.get("/agency/list/{incident_id}")
async def get_incident_agencies(
    incident_id: str,
    active_only: bool = True,
) -> dict[str, Any]:
    """Get agencies participating in an incident."""
    participations = await multiagency_coordinator.get_incident_agencies(
        incident_id=incident_id,
        active_only=active_only,
    )
    return {
        "success": True,
        "agencies": [p.model_dump() for p in participations],
        "count": len(participations),
    }


@router.post("/agency/access")
async def update_agency_access(
    incident_id: str = Query(...),
    agency_id: str = Query(...),
    request: UpdateAgencyAccessRequest = None,
) -> dict[str, Any]:
    """Update agency access level."""
    if not request:
        raise HTTPException(status_code=400, detail="Request body required")

    participation = await multiagency_coordinator.update_agency_access(
        incident_id=incident_id,
        agency_id=agency_id,
        access_level=request.access_level,
        allowed_data=request.allowed_data,
        denied_data=request.denied_data,
        updated_by=request.updated_by,
    )

    if not participation:
        raise HTTPException(status_code=404, detail="Agency participation not found")

    return {"success": True, "participation": participation.model_dump()}


@router.get("/agency/all")
async def get_all_agencies(
    agency_type: AgencyType | None = None,
) -> dict[str, Any]:
    """Get all registered agencies."""
    agencies = await multiagency_coordinator.get_all_agencies(
        agency_type=agency_type,
    )
    return {
        "success": True,
        "agencies": [a.model_dump() for a in agencies],
        "count": len(agencies),
    }


# ============================================================
# Statistics Endpoints
# ============================================================


@router.get("/stats/incident/{incident_id}")
async def get_incident_statistics(incident_id: str) -> dict[str, Any]:
    """Get comprehensive statistics for an incident."""
    incident_stats = await incident_engine.get_incident_statistics(incident_id)
    ics_stats = await ics_manager.get_incident_statistics(incident_id)
    resource_stats = await resource_manager.get_resource_statistics(incident_id)
    timeline_stats = await timeline_engine.get_timeline_statistics(incident_id)
    note_stats = await briefing_generator.get_note_statistics(incident_id)
    agency_stats = await multiagency_coordinator.get_coordination_statistics(incident_id)

    return {
        "success": True,
        "incident": incident_stats,
        "ics": ics_stats,
        "resources": resource_stats,
        "timeline": timeline_stats,
        "notes": note_stats,
        "agencies": agency_stats,
    }
