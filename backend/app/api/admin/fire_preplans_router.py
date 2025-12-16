"""
Fire Preplans Admin API Router
Tab 6: Fire Preplans
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException

from ...admin.fire_preplans_admin import fire_preplan_admin, FirePreplanModel, FirePreplanCreate, FirePreplanUpdate
from ...admin.validation import ValidationEngine
from ...admin.audit_log import audit_logger
from .base_router import CurrentUser, get_current_user, require_supervisor, get_pagination, PaginationParams

router = APIRouter()


@router.get("/", response_model=List[FirePreplanModel])
async def list_fire_preplans(
    pagination: PaginationParams = Depends(get_pagination),
    current_user: CurrentUser = Depends(get_current_user),
):
    """List all fire preplans"""
    return await fire_preplan_admin.get_all(skip=pagination.skip, limit=pagination.limit)


@router.get("/nearby")
async def get_nearby_preplans(lat: float, lng: float, radius_km: float = 1.0, current_user: CurrentUser = Depends(get_current_user)):
    """Get fire preplans near a location"""
    return await fire_preplan_admin.get_nearby(lat, lng, radius_km)


@router.get("/{preplan_id}", response_model=FirePreplanModel)
async def get_fire_preplan(preplan_id: str, current_user: CurrentUser = Depends(get_current_user)):
    """Get a specific fire preplan"""
    preplan = await fire_preplan_admin.get_by_id(preplan_id)
    if not preplan:
        raise HTTPException(status_code=404, detail="Fire preplan not found")
    return preplan


@router.post("/", response_model=FirePreplanModel)
async def create_fire_preplan(data: FirePreplanCreate, current_user: CurrentUser = Depends(require_supervisor())):
    """Create a new fire preplan"""
    validation = ValidationEngine.validate_fire_preplan(data.model_dump())
    if not validation.is_valid:
        raise HTTPException(status_code=400, detail={"errors": validation.errors})
    
    preplan = await fire_preplan_admin.create(data, current_user.user_id)
    audit_logger.log_create(user_id=current_user.user_id, table_name="fire_preplans", record_id=preplan.id, data=preplan)
    return preplan


@router.patch("/{preplan_id}", response_model=FirePreplanModel)
async def update_fire_preplan(preplan_id: str, data: FirePreplanUpdate, current_user: CurrentUser = Depends(require_supervisor())):
    """Update a fire preplan"""
    existing = await fire_preplan_admin.get_by_id(preplan_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Fire preplan not found")
    
    preplan = await fire_preplan_admin.update(preplan_id, data, current_user.user_id)
    audit_logger.log_update(user_id=current_user.user_id, table_name="fire_preplans", record_id=preplan_id, before=existing, after=preplan)
    return preplan


@router.delete("/{preplan_id}")
async def delete_fire_preplan(preplan_id: str, current_user: CurrentUser = Depends(require_supervisor())):
    """Delete a fire preplan"""
    existing = await fire_preplan_admin.get_by_id(preplan_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Fire preplan not found")
    
    await fire_preplan_admin.delete(preplan_id, current_user.user_id)
    audit_logger.log_delete(user_id=current_user.user_id, table_name="fire_preplans", record_id=preplan_id, data=existing)
    return {"message": "Fire preplan deleted successfully"}
