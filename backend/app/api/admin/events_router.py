"""
Events Admin API Router
Tab 12: Special Events
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException

from ...admin.events_admin import event_admin, EventModel, EventCreate, EventUpdate, EventType, EventStatus
from ...admin.validation import ValidationEngine
from ...admin.audit_log import audit_logger
from .base_router import CurrentUser, get_current_user, require_supervisor, get_pagination, PaginationParams

router = APIRouter()


@router.get("/", response_model=List[EventModel])
async def list_events(
    pagination: PaginationParams = Depends(get_pagination),
    event_type: Optional[EventType] = None,
    status: Optional[EventStatus] = None,
    current_user: CurrentUser = Depends(get_current_user),
):
    """List all events"""
    filters = {}
    if event_type:
        filters["event_type"] = event_type
    if status:
        filters["status"] = status
    return await event_admin.get_all(skip=pagination.skip, limit=pagination.limit, filters=filters if filters else None)


@router.get("/active", response_model=List[EventModel])
async def get_active_events(current_user: CurrentUser = Depends(get_current_user)):
    """Get all active events"""
    return await event_admin.get_active()


@router.get("/upcoming", response_model=List[EventModel])
async def get_upcoming_events(days: int = 7, current_user: CurrentUser = Depends(get_current_user)):
    """Get upcoming events within specified days"""
    return await event_admin.get_upcoming(days)


@router.get("/{event_id}", response_model=EventModel)
async def get_event(event_id: str, current_user: CurrentUser = Depends(get_current_user)):
    """Get a specific event"""
    event = await event_admin.get_by_id(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.post("/", response_model=EventModel)
async def create_event(data: EventCreate, current_user: CurrentUser = Depends(require_supervisor())):
    """Create a new event"""
    validation = ValidationEngine.validate_event(data.model_dump())
    if not validation.is_valid:
        raise HTTPException(status_code=400, detail={"errors": validation.errors})
    
    event = await event_admin.create(data, current_user.user_id)
    audit_logger.log_create(user_id=current_user.user_id, table_name="events", record_id=event.id, data=event)
    return event


@router.patch("/{event_id}", response_model=EventModel)
async def update_event(event_id: str, data: EventUpdate, current_user: CurrentUser = Depends(require_supervisor())):
    """Update an event"""
    existing = await event_admin.get_by_id(event_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Event not found")
    
    event = await event_admin.update(event_id, data, current_user.user_id)
    audit_logger.log_update(user_id=current_user.user_id, table_name="events", record_id=event_id, before=existing, after=event)
    return event


@router.delete("/{event_id}")
async def delete_event(event_id: str, current_user: CurrentUser = Depends(require_supervisor())):
    """Delete an event"""
    existing = await event_admin.get_by_id(event_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Event not found")
    
    await event_admin.delete(event_id, current_user.user_id)
    audit_logger.log_delete(user_id=current_user.user_id, table_name="events", record_id=event_id, data=existing)
    return {"message": "Event deleted successfully"}
