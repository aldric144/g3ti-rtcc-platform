"""
Incidents Admin API Router
Tab 10: Incident Feed
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException

from ...admin.incidents_admin import incident_admin, IncidentModel, IncidentCreate, IncidentUpdate, IncidentType, IncidentPriority, IncidentStatus
from ...admin.audit_log import audit_logger
from .base_router import CurrentUser, get_current_user, require_supervisor, get_pagination, PaginationParams

router = APIRouter()


@router.get("/", response_model=List[IncidentModel])
async def list_incidents(
    pagination: PaginationParams = Depends(get_pagination),
    incident_type: Optional[IncidentType] = None,
    priority: Optional[IncidentPriority] = None,
    status: Optional[IncidentStatus] = None,
    sector: Optional[str] = None,
    current_user: CurrentUser = Depends(get_current_user),
):
    """List all incidents"""
    filters = {}
    if incident_type:
        filters["incident_type"] = incident_type
    if priority:
        filters["priority"] = priority
    if status:
        filters["status"] = status
    if sector:
        filters["sector"] = sector
    return await incident_admin.get_all(skip=pagination.skip, limit=pagination.limit, filters=filters if filters else None)


@router.get("/active", response_model=List[IncidentModel])
async def get_active_incidents(current_user: CurrentUser = Depends(get_current_user)):
    """Get all active (non-closed) incidents"""
    return await incident_admin.get_active()


@router.get("/critical", response_model=List[IncidentModel])
async def get_critical_incidents(current_user: CurrentUser = Depends(get_current_user)):
    """Get critical priority incidents"""
    return await incident_admin.get_critical()


@router.get("/type/{incident_type}", response_model=List[IncidentModel])
async def get_by_type(incident_type: IncidentType, current_user: CurrentUser = Depends(get_current_user)):
    """Get incidents by type"""
    return await incident_admin.get_by_type(incident_type)


@router.get("/sector/{sector}", response_model=List[IncidentModel])
async def get_by_sector(sector: str, current_user: CurrentUser = Depends(get_current_user)):
    """Get incidents by sector"""
    return await incident_admin.get_by_sector(sector)


@router.get("/{incident_id}", response_model=IncidentModel)
async def get_incident(incident_id: str, current_user: CurrentUser = Depends(get_current_user)):
    """Get a specific incident"""
    incident = await incident_admin.get_by_id(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident


@router.post("/", response_model=IncidentModel)
async def create_incident(data: IncidentCreate, current_user: CurrentUser = Depends(get_current_user)):
    """Create a new incident"""
    incident = await incident_admin.create(data, current_user.user_id)
    audit_logger.log_create(user_id=current_user.user_id, table_name="incidents", record_id=incident.id, data=incident)
    return incident


@router.patch("/{incident_id}", response_model=IncidentModel)
async def update_incident(incident_id: str, data: IncidentUpdate, current_user: CurrentUser = Depends(get_current_user)):
    """Update an incident"""
    existing = await incident_admin.get_by_id(incident_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    incident = await incident_admin.update(incident_id, data, current_user.user_id)
    audit_logger.log_update(user_id=current_user.user_id, table_name="incidents", record_id=incident_id, before=existing, after=incident)
    return incident


@router.delete("/{incident_id}")
async def delete_incident(incident_id: str, current_user: CurrentUser = Depends(require_supervisor())):
    """Delete an incident"""
    existing = await incident_admin.get_by_id(incident_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    await incident_admin.delete(incident_id, current_user.user_id)
    audit_logger.log_delete(user_id=current_user.user_id, table_name="incidents", record_id=incident_id, data=existing)
    return {"message": "Incident deleted successfully"}
