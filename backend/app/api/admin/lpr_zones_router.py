"""
LPR Zones Admin API Router
Tab 4: LPR Zones
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException

from ...admin.lpr_zones_admin import lpr_zone_admin, LPRZoneModel, LPRZoneCreate, LPRZoneUpdate
from ...admin.audit_log import audit_logger
from .base_router import CurrentUser, get_current_user, require_supervisor, get_pagination, PaginationParams

router = APIRouter()


@router.get("/", response_model=List[LPRZoneModel])
async def list_lpr_zones(
    pagination: PaginationParams = Depends(get_pagination),
    current_user: CurrentUser = Depends(get_current_user),
):
    """List all LPR zones"""
    return await lpr_zone_admin.get_all(skip=pagination.skip, limit=pagination.limit)


@router.get("/{zone_id}", response_model=LPRZoneModel)
async def get_lpr_zone(zone_id: str, current_user: CurrentUser = Depends(get_current_user)):
    """Get a specific LPR zone"""
    zone = await lpr_zone_admin.get_by_id(zone_id)
    if not zone:
        raise HTTPException(status_code=404, detail="LPR zone not found")
    return zone


@router.post("/", response_model=LPRZoneModel)
async def create_lpr_zone(data: LPRZoneCreate, current_user: CurrentUser = Depends(require_supervisor())):
    """Create a new LPR zone"""
    zone = await lpr_zone_admin.create(data, current_user.user_id)
    audit_logger.log_create(user_id=current_user.user_id, table_name="lpr_zones", record_id=zone.id, data=zone)
    return zone


@router.patch("/{zone_id}", response_model=LPRZoneModel)
async def update_lpr_zone(zone_id: str, data: LPRZoneUpdate, current_user: CurrentUser = Depends(require_supervisor())):
    """Update an LPR zone"""
    existing = await lpr_zone_admin.get_by_id(zone_id)
    if not existing:
        raise HTTPException(status_code=404, detail="LPR zone not found")
    
    zone = await lpr_zone_admin.update(zone_id, data, current_user.user_id)
    audit_logger.log_update(user_id=current_user.user_id, table_name="lpr_zones", record_id=zone_id, before=existing, after=zone)
    return zone


@router.delete("/{zone_id}")
async def delete_lpr_zone(zone_id: str, current_user: CurrentUser = Depends(require_supervisor())):
    """Delete an LPR zone"""
    existing = await lpr_zone_admin.get_by_id(zone_id)
    if not existing:
        raise HTTPException(status_code=404, detail="LPR zone not found")
    
    await lpr_zone_admin.delete(zone_id, current_user.user_id)
    audit_logger.log_delete(user_id=current_user.user_id, table_name="lpr_zones", record_id=zone_id, data=existing)
    return {"message": "LPR zone deleted successfully"}


@router.post("/{zone_id}/cameras/{camera_id}")
async def add_camera_to_zone(zone_id: str, camera_id: str, current_user: CurrentUser = Depends(require_supervisor())):
    """Add a camera to an LPR zone"""
    zone = await lpr_zone_admin.add_camera(zone_id, camera_id)
    if not zone:
        raise HTTPException(status_code=404, detail="LPR zone not found")
    return zone


@router.delete("/{zone_id}/cameras/{camera_id}")
async def remove_camera_from_zone(zone_id: str, camera_id: str, current_user: CurrentUser = Depends(require_supervisor())):
    """Remove a camera from an LPR zone"""
    zone = await lpr_zone_admin.remove_camera(zone_id, camera_id)
    if not zone:
        raise HTTPException(status_code=404, detail="LPR zone not found")
    return zone
