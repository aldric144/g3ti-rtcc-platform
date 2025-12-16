"""
Sectors Admin API Router
Tab 5: Sectors (Beats)
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException

from ...admin.sectors_admin import sector_admin, SectorModel, SectorCreate, SectorUpdate
from ...admin.validation import ValidationEngine
from ...admin.audit_log import audit_logger
from .base_router import CurrentUser, get_current_user, require_supervisor, get_pagination, PaginationParams

router = APIRouter()


@router.get("/", response_model=List[SectorModel])
async def list_sectors(
    pagination: PaginationParams = Depends(get_pagination),
    current_user: CurrentUser = Depends(get_current_user),
):
    """List all sectors"""
    return await sector_admin.get_all(skip=pagination.skip, limit=pagination.limit)


@router.get("/{sector_id}", response_model=SectorModel)
async def get_sector(sector_id: str, current_user: CurrentUser = Depends(get_current_user)):
    """Get a specific sector"""
    sector = await sector_admin.get_by_id(sector_id)
    if not sector:
        raise HTTPException(status_code=404, detail="Sector not found")
    return sector


@router.post("/", response_model=SectorModel)
async def create_sector(data: SectorCreate, current_user: CurrentUser = Depends(require_supervisor())):
    """Create a new sector"""
    validation = ValidationEngine.validate_sector(data.model_dump())
    if not validation.is_valid:
        raise HTTPException(status_code=400, detail={"errors": validation.errors})
    
    sector = await sector_admin.create(data, current_user.user_id)
    audit_logger.log_create(user_id=current_user.user_id, table_name="sectors", record_id=sector.id, data=sector)
    return sector


@router.patch("/{sector_id}", response_model=SectorModel)
async def update_sector(sector_id: str, data: SectorUpdate, current_user: CurrentUser = Depends(require_supervisor())):
    """Update a sector"""
    existing = await sector_admin.get_by_id(sector_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Sector not found")
    
    sector = await sector_admin.update(sector_id, data, current_user.user_id)
    audit_logger.log_update(user_id=current_user.user_id, table_name="sectors", record_id=sector_id, before=existing, after=sector)
    return sector


@router.delete("/{sector_id}")
async def delete_sector(sector_id: str, current_user: CurrentUser = Depends(require_supervisor())):
    """Delete a sector"""
    existing = await sector_admin.get_by_id(sector_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Sector not found")
    
    await sector_admin.delete(sector_id, current_user.user_id)
    audit_logger.log_delete(user_id=current_user.user_id, table_name="sectors", record_id=sector_id, data=existing)
    return {"message": "Sector deleted successfully"}


@router.get("/find/point")
async def find_sector_for_point(lat: float, lng: float, current_user: CurrentUser = Depends(get_current_user)):
    """Find which sector contains a GPS point"""
    sector = await sector_admin.find_sector_for_point(lat, lng)
    if not sector:
        return {"message": "No sector found for this location"}
    return sector


@router.post("/{sector_id}/officers/{officer}")
async def assign_officer(sector_id: str, officer: str, current_user: CurrentUser = Depends(require_supervisor())):
    """Assign an officer to a sector"""
    sector = await sector_admin.assign_officer(sector_id, officer)
    if not sector:
        raise HTTPException(status_code=404, detail="Sector not found")
    return sector


@router.delete("/{sector_id}/officers/{officer}")
async def remove_officer(sector_id: str, officer: str, current_user: CurrentUser = Depends(require_supervisor())):
    """Remove an officer from a sector"""
    sector = await sector_admin.remove_officer(sector_id, officer)
    if not sector:
        raise HTTPException(status_code=404, detail="Sector not found")
    return sector
