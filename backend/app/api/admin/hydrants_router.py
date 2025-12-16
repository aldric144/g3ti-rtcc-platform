"""
Hydrants Admin API Router
Tab 13: Hydrants
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException

from ...admin.hydrants_admin import hydrant_admin, HydrantModel, HydrantCreate, HydrantUpdate, HydrantStatus, HydrantType
from ...admin.audit_log import audit_logger
from .base_router import CurrentUser, get_current_user, require_supervisor, get_pagination, PaginationParams

router = APIRouter()


@router.get("/", response_model=List[HydrantModel])
async def list_hydrants(
    pagination: PaginationParams = Depends(get_pagination),
    status: Optional[HydrantStatus] = None,
    hydrant_type: Optional[HydrantType] = None,
    sector: Optional[str] = None,
    current_user: CurrentUser = Depends(get_current_user),
):
    """List all hydrants"""
    filters = {}
    if status:
        filters["status"] = status
    if hydrant_type:
        filters["hydrant_type"] = hydrant_type
    if sector:
        filters["sector"] = sector
    return await hydrant_admin.get_all(skip=pagination.skip, limit=pagination.limit, filters=filters if filters else None)


@router.get("/out-of-service", response_model=List[HydrantModel])
async def get_out_of_service(current_user: CurrentUser = Depends(get_current_user)):
    """Get all out of service hydrants"""
    return await hydrant_admin.get_out_of_service()


@router.get("/nearby")
async def get_nearby_hydrants(lat: float, lng: float, radius_km: float = 0.5, current_user: CurrentUser = Depends(get_current_user)):
    """Get hydrants near a location"""
    return await hydrant_admin.get_nearby(lat, lng, radius_km)


@router.get("/sector/{sector}", response_model=List[HydrantModel])
async def get_by_sector(sector: str, current_user: CurrentUser = Depends(get_current_user)):
    """Get hydrants by sector"""
    return await hydrant_admin.get_by_sector(sector)


@router.get("/{hydrant_id}", response_model=HydrantModel)
async def get_hydrant(hydrant_id: str, current_user: CurrentUser = Depends(get_current_user)):
    """Get a specific hydrant"""
    hydrant = await hydrant_admin.get_by_id(hydrant_id)
    if not hydrant:
        raise HTTPException(status_code=404, detail="Hydrant not found")
    return hydrant


@router.post("/", response_model=HydrantModel)
async def create_hydrant(data: HydrantCreate, current_user: CurrentUser = Depends(require_supervisor())):
    """Create a new hydrant"""
    hydrant = await hydrant_admin.create(data, current_user.user_id)
    audit_logger.log_create(user_id=current_user.user_id, table_name="hydrants", record_id=hydrant.id, data=hydrant)
    return hydrant


@router.patch("/{hydrant_id}", response_model=HydrantModel)
async def update_hydrant(hydrant_id: str, data: HydrantUpdate, current_user: CurrentUser = Depends(require_supervisor())):
    """Update a hydrant"""
    existing = await hydrant_admin.get_by_id(hydrant_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Hydrant not found")
    
    hydrant = await hydrant_admin.update(hydrant_id, data, current_user.user_id)
    audit_logger.log_update(user_id=current_user.user_id, table_name="hydrants", record_id=hydrant_id, before=existing, after=hydrant)
    return hydrant


@router.delete("/{hydrant_id}")
async def delete_hydrant(hydrant_id: str, current_user: CurrentUser = Depends(require_supervisor())):
    """Delete a hydrant"""
    existing = await hydrant_admin.get_by_id(hydrant_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Hydrant not found")
    
    await hydrant_admin.delete(hydrant_id, current_user.user_id)
    audit_logger.log_delete(user_id=current_user.user_id, table_name="hydrants", record_id=hydrant_id, data=existing)
    return {"message": "Hydrant deleted successfully"}


@router.post("/{hydrant_id}/inspection")
async def record_inspection(hydrant_id: str, psi: Optional[int] = None, current_user: CurrentUser = Depends(require_supervisor())):
    """Record a hydrant inspection"""
    hydrant = await hydrant_admin.record_inspection(hydrant_id, current_user.user_id, psi)
    if not hydrant:
        raise HTTPException(status_code=404, detail="Hydrant not found")
    return hydrant


@router.post("/{hydrant_id}/flow-test")
async def record_flow_test(hydrant_id: str, flow_rate: int, psi: int, current_user: CurrentUser = Depends(require_supervisor())):
    """Record a hydrant flow test"""
    hydrant = await hydrant_admin.record_flow_test(hydrant_id, current_user.user_id, flow_rate, psi)
    if not hydrant:
        raise HTTPException(status_code=404, detail="Hydrant not found")
    return hydrant
