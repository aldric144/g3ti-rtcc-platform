"""
G3TI RTCC-UIP MDT API Endpoints
REST API for Mobile Data Terminal integration.
"""

from datetime import datetime
from typing import Any

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.mdt import (
    CADCall,
    CADCallPriority,
    CADNote,
    MDTMessage,
    MDTUnit,
    MDTUnitStatus,
    SceneCoordination,
    SceneRole,
    mdt_manager,
)

router = APIRouter(prefix="/api/mdt", tags=["mdt"])


# ============== Request/Response Models ==============

class RegisterUnitRequest(BaseModel):
    """Unit registration request."""
    unit_id: str
    badge_number: str
    officer_name: str
    call_sign: str
    vehicle_id: str | None = None
    radio_id: str | None = None
    district: str | None = None
    beat: str | None = None
    shift: str | None = None


class UpdateStatusRequest(BaseModel):
    """Unit status update request."""
    status: str
    call_id: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    location_description: str | None = None
    notes: str | None = None


class AddCallNoteRequest(BaseModel):
    """Add call note request."""
    content: str
    note_type: str = "general"
    is_rtcc: bool = False


class AssignSceneRoleRequest(BaseModel):
    """Assign scene role request."""
    unit_id: str
    badge_number: str
    officer_name: str
    role: str
    notes: str | None = None


class UpdateSceneRequest(BaseModel):
    """Update scene coordination request."""
    incident_commander: str | None = None
    staging_location: str | None = None
    staging_lat: float | None = None
    staging_lng: float | None = None
    perimeter_established: bool | None = None
    perimeter_notes: str | None = None
    resources_requested: list[str] | None = None
    resources_on_scene: list[str] | None = None
    tactical_notes: list[str] | None = None


class SendMessageRequest(BaseModel):
    """Send MDT message request."""
    content: str
    recipient_badges: list[str] = Field(default_factory=list)
    recipient_units: list[str] = Field(default_factory=list)
    call_id: str | None = None
    priority: str = "normal"
    is_broadcast: bool = False


class CreateCallRequest(BaseModel):
    """Create CAD call request."""
    call_number: str
    call_type: str
    call_type_code: str | None = None
    priority: str = "3"
    location: str
    address: str | None = None
    apartment: str | None = None
    city: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    cross_streets: str | None = None
    common_place: str | None = None
    description: str | None = None
    caller_name: str | None = None
    caller_phone: str | None = None
    hazards: list[str] = Field(default_factory=list)


# ============== Unit Endpoints ==============

@router.post("/unit/register", response_model=dict)
async def register_unit(request: RegisterUnitRequest) -> dict[str, Any]:
    """Register or update an MDT unit."""
    unit = await mdt_manager.register_unit(
        unit_id=request.unit_id,
        badge_number=request.badge_number,
        officer_name=request.officer_name,
        call_sign=request.call_sign,
        vehicle_id=request.vehicle_id,
        radio_id=request.radio_id,
        district=request.district,
        beat=request.beat,
        shift=request.shift,
    )
    return {
        "success": True,
        "unit": unit.model_dump(),
    }


@router.post("/unit/status/update", response_model=dict)
async def update_unit_status(
    badge_number: str,
    request: UpdateStatusRequest,
    changed_by: str | None = None,
) -> dict[str, Any]:
    """Update unit status."""
    status = MDTUnitStatus(request.status) if request.status in [e.value for e in MDTUnitStatus] else MDTUnitStatus.AVAILABLE

    unit = await mdt_manager.update_unit_status(
        badge_number=badge_number,
        status=status,
        call_id=request.call_id,
        latitude=request.latitude,
        longitude=request.longitude,
        location_description=request.location_description,
        notes=request.notes,
        changed_by=changed_by,
    )

    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")

    return {
        "success": True,
        "unit": unit.model_dump(),
    }


@router.get("/unit/status/{badge_number}", response_model=MDTUnit | None)
async def get_unit_status(badge_number: str) -> MDTUnit | None:
    """Get unit status by badge number."""
    return await mdt_manager.get_unit_status(badge_number)


@router.get("/units", response_model=list[MDTUnit])
async def get_all_units(
    status: str | None = None,
    district: str | None = None,
) -> list[MDTUnit]:
    """Get all units with optional filters."""
    status_enum = MDTUnitStatus(status) if status and status in [e.value for e in MDTUnitStatus] else None
    return await mdt_manager.get_all_units(status=status_enum, district=district)


@router.get("/units/available", response_model=list[MDTUnit])
async def get_available_units(
    district: str | None = None,
    exclude_units: str | None = None,
) -> list[MDTUnit]:
    """Get available units for dispatch."""
    exclude = exclude_units.split(",") if exclude_units else None
    return await mdt_manager.get_available_units(district=district, exclude_units=exclude)


@router.get("/unit/history/{badge_number}")
async def get_status_history(
    badge_number: str,
    limit: int = Query(default=50, le=200),
    since: datetime | None = None,
) -> list[dict[str, Any]]:
    """Get unit status history."""
    history = await mdt_manager.get_status_history(
        badge_number=badge_number,
        limit=limit,
        since=since,
    )
    return [h.model_dump() for h in history]


# ============== Dispatch Endpoints ==============

@router.get("/dispatch/active")
async def get_active_dispatch(
    badge_number: str | None = None,
    unit_id: str | None = None,
    district: str | None = None,
    priority: str | None = None,
) -> list[dict[str, Any]]:
    """Get active dispatch calls."""
    priority_enum = CADCallPriority(priority) if priority and priority in [e.value for e in CADCallPriority] else None

    calls = await mdt_manager.get_active_dispatch(
        badge_number=badge_number,
        unit_id=unit_id,
        district=district,
        priority=priority_enum,
    )
    return [call.model_dump() for call in calls]


@router.get("/dispatch/call/{call_id}", response_model=CADCall | None)
async def get_cad_call(call_id: str) -> CADCall | None:
    """Get a CAD call by ID."""
    return await mdt_manager.get_cad_call(call_id)


@router.post("/dispatch/call", response_model=dict)
async def create_cad_call(request: CreateCallRequest) -> dict[str, Any]:
    """Create a new CAD call."""
    priority = CADCallPriority(request.priority) if request.priority in [e.value for e in CADCallPriority] else CADCallPriority.PRIORITY_3

    call = CADCall(
        call_number=request.call_number,
        call_type=request.call_type,
        call_type_code=request.call_type_code,
        priority=priority,
        location=request.location,
        address=request.address,
        apartment=request.apartment,
        city=request.city,
        latitude=request.latitude,
        longitude=request.longitude,
        cross_streets=request.cross_streets,
        common_place=request.common_place,
        description=request.description,
        caller_name=request.caller_name,
        caller_phone=request.caller_phone,
        hazards=request.hazards,
    )

    call = await mdt_manager.add_cad_call(call)
    return {
        "success": True,
        "call": call.model_dump(),
    }


@router.post("/dispatch/call/{call_id}/assign")
async def assign_unit_to_call(
    call_id: str,
    unit_id: str,
    is_primary: bool = False,
) -> dict[str, Any]:
    """Assign a unit to a call."""
    call = await mdt_manager.assign_unit_to_call(
        call_id=call_id,
        unit_id=unit_id,
        is_primary=is_primary,
    )

    if not call:
        raise HTTPException(status_code=404, detail="Call not found")

    return {
        "success": True,
        "call": call.model_dump(),
    }


@router.post("/dispatch/call/{call_id}/remove")
async def remove_unit_from_call(
    call_id: str,
    unit_id: str,
) -> dict[str, Any]:
    """Remove a unit from a call."""
    call = await mdt_manager.remove_unit_from_call(call_id=call_id, unit_id=unit_id)

    if not call:
        raise HTTPException(status_code=404, detail="Call not found")

    return {
        "success": True,
        "call": call.model_dump(),
    }


@router.post("/dispatch/call/{call_id}/clear")
async def clear_call(
    call_id: str,
    disposition: str,
    cleared_by: str | None = None,
) -> dict[str, Any]:
    """Clear a CAD call."""
    call = await mdt_manager.clear_call(
        call_id=call_id,
        disposition=disposition,
        cleared_by=cleared_by,
    )

    if not call:
        raise HTTPException(status_code=404, detail="Call not found")

    return {
        "success": True,
        "call": call.model_dump(),
    }


@router.post("/dispatch/call/{call_id}/note", response_model=dict)
async def add_call_note(
    call_id: str,
    author_badge: str,
    author_name: str,
    request: AddCallNoteRequest,
) -> dict[str, Any]:
    """Add a note to a CAD call."""
    note = await mdt_manager.add_call_note(
        call_id=call_id,
        author_badge=author_badge,
        author_name=author_name,
        content=request.content,
        note_type=request.note_type,
        is_rtcc=request.is_rtcc,
    )

    if not note:
        raise HTTPException(status_code=404, detail="Call not found")

    return {
        "success": True,
        "note": note.model_dump(),
    }


@router.get("/dispatch/call/{call_id}/notes", response_model=list[CADNote])
async def get_call_notes(call_id: str) -> list[CADNote]:
    """Get notes for a call."""
    return await mdt_manager.get_call_notes(call_id)


@router.get("/dispatch/premise-history")
async def get_premise_history(
    address: str,
    limit: int = Query(default=10, le=50),
) -> list[str]:
    """Get premise history for an address."""
    return await mdt_manager.get_premise_history(address=address, limit=limit)


# ============== Scene Coordination Endpoints ==============

@router.get("/scene/{call_id}", response_model=SceneCoordination | None)
async def get_scene_coordination(call_id: str) -> SceneCoordination | None:
    """Get scene coordination for a call."""
    return await mdt_manager.get_scene_coordination(call_id)


@router.post("/scene/{call_id}/create", response_model=dict)
async def create_scene_coordination(
    call_id: str,
    incident_commander: str | None = None,
    staging_location: str | None = None,
    staging_lat: float | None = None,
    staging_lng: float | None = None,
) -> dict[str, Any]:
    """Create scene coordination for a call."""
    coordination = await mdt_manager.create_scene_coordination(
        call_id=call_id,
        incident_commander=incident_commander,
        staging_location=staging_location,
        staging_lat=staging_lat,
        staging_lng=staging_lng,
    )

    if not coordination:
        raise HTTPException(status_code=404, detail="Call not found")

    return {
        "success": True,
        "coordination": coordination.model_dump(),
    }


@router.post("/scene/{call_id}/assign-role", response_model=dict)
async def assign_scene_role(
    call_id: str,
    request: AssignSceneRoleRequest,
    assigned_by: str | None = None,
) -> dict[str, Any]:
    """Assign a scene role to a unit."""
    role = SceneRole(request.role) if request.role in [e.value for e in SceneRole] else SceneRole.OTHER

    assignment = await mdt_manager.assign_scene_role(
        call_id=call_id,
        unit_id=request.unit_id,
        badge_number=request.badge_number,
        officer_name=request.officer_name,
        role=role,
        assigned_by=assigned_by,
        notes=request.notes,
    )

    if not assignment:
        raise HTTPException(status_code=404, detail="Call not found")

    return {
        "success": True,
        "assignment": assignment.model_dump(),
    }


@router.put("/scene/{call_id}", response_model=dict)
async def update_scene_coordination(
    call_id: str,
    request: UpdateSceneRequest,
) -> dict[str, Any]:
    """Update scene coordination."""
    coordination = await mdt_manager.update_scene_coordination(
        call_id=call_id,
        incident_commander=request.incident_commander,
        staging_location=request.staging_location,
        staging_lat=request.staging_lat,
        staging_lng=request.staging_lng,
        perimeter_established=request.perimeter_established,
        perimeter_notes=request.perimeter_notes,
        resources_requested=request.resources_requested,
        resources_on_scene=request.resources_on_scene,
        tactical_notes=request.tactical_notes,
    )

    if not coordination:
        raise HTTPException(status_code=404, detail="Scene coordination not found")

    return {
        "success": True,
        "coordination": coordination.model_dump(),
    }


# ============== Messaging Endpoints ==============

@router.post("/messages/send", response_model=dict)
async def send_mdt_message(
    sender_badge: str,
    sender_name: str,
    request: SendMessageRequest,
    sender_type: str = "officer",
) -> dict[str, Any]:
    """Send an MDT message."""
    message = await mdt_manager.send_mdt_message(
        sender_badge=sender_badge,
        sender_name=sender_name,
        content=request.content,
        recipient_badges=request.recipient_badges,
        recipient_units=request.recipient_units,
        call_id=request.call_id,
        priority=request.priority,
        is_broadcast=request.is_broadcast,
        sender_type=sender_type,
    )

    return {
        "success": True,
        "message": message.model_dump(),
    }


@router.get("/messages", response_model=list[MDTMessage])
async def get_mdt_messages(
    badge_number: str,
    unit_id: str | None = None,
    call_id: str | None = None,
    limit: int = Query(default=100, le=500),
    since: datetime | None = None,
) -> list[MDTMessage]:
    """Get MDT messages for a unit."""
    return await mdt_manager.get_mdt_messages(
        badge_number=badge_number,
        unit_id=unit_id,
        call_id=call_id,
        limit=limit,
        since=since,
    )


@router.post("/messages/{message_id}/read")
async def mark_message_read(
    message_id: str,
    badge_number: str,
) -> dict[str, bool]:
    """Mark a message as read."""
    success = await mdt_manager.mark_message_read(message_id, badge_number)
    return {"success": success}
