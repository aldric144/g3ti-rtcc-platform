"""
DV Risk Homes Admin API Router
Tab 9: DV Risk Homes (REDACTED)

SECURITY: This router handles sensitive domestic violence data.
Full addresses are NEVER stored or transmitted.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException

from ...admin.dv_risk_homes_admin import dv_risk_home_admin, DVRiskHomeModel, DVRiskHomeCreate, DVRiskHomeUpdate, RiskLevel
from ...admin.validation import ValidationEngine
from ...admin.audit_log import audit_logger
from .base_router import CurrentUser, get_current_user, require_supervisor, require_admin, get_pagination, PaginationParams

router = APIRouter()


@router.get("/", response_model=List[DVRiskHomeModel])
async def list_dv_risk_homes(
    pagination: PaginationParams = Depends(get_pagination),
    risk_level: Optional[RiskLevel] = None,
    sector: Optional[str] = None,
    current_user: CurrentUser = Depends(require_supervisor()),
):
    """List all DV risk homes (supervisor+ only)"""
    filters = {}
    if risk_level:
        filters["risk_level"] = risk_level
    if sector:
        filters["sector"] = sector
    
    audit_logger.log_read(user_id=current_user.user_id, table_name="dv_risk_homes", username=current_user.username)
    return await dv_risk_home_admin.get_all(skip=pagination.skip, limit=pagination.limit, filters=filters if filters else None)


@router.get("/high-risk", response_model=List[DVRiskHomeModel])
async def get_high_risk_homes(current_user: CurrentUser = Depends(require_supervisor())):
    """Get high/critical risk homes"""
    return await dv_risk_home_admin.get_high_risk()


@router.get("/sector/{sector}", response_model=List[DVRiskHomeModel])
async def get_by_sector(sector: str, current_user: CurrentUser = Depends(require_supervisor())):
    """Get DV risk homes by sector"""
    return await dv_risk_home_admin.get_by_sector(sector)


@router.get("/{home_id}", response_model=DVRiskHomeModel)
async def get_dv_risk_home(home_id: str, current_user: CurrentUser = Depends(require_supervisor())):
    """Get a specific DV risk home"""
    home = await dv_risk_home_admin.get_by_id(home_id)
    if not home:
        raise HTTPException(status_code=404, detail="DV risk home not found")
    
    audit_logger.log_read(user_id=current_user.user_id, table_name="dv_risk_homes", record_id=home_id, username=current_user.username)
    return home


@router.get("/{home_id}/notes")
async def get_decrypted_notes(home_id: str, current_user: CurrentUser = Depends(require_admin())):
    """Get decrypted notes (admin only)"""
    notes = await dv_risk_home_admin.get_decrypted_notes(home_id, current_user.user_id)
    if notes is None:
        raise HTTPException(status_code=404, detail="DV risk home not found")
    
    audit_logger.log(
        user_id=current_user.user_id,
        action=audit_logger._logs[0].action if audit_logger._logs else None,
        table_name="dv_risk_homes",
        record_id=home_id,
        metadata={"action": "decrypt_notes"},
        username=current_user.username,
    )
    return {"notes": notes}


@router.post("/", response_model=DVRiskHomeModel)
async def create_dv_risk_home(data: DVRiskHomeCreate, current_user: CurrentUser = Depends(require_supervisor())):
    """Create a new DV risk home entry"""
    validation = ValidationEngine.validate_dv_risk_home(data.model_dump())
    if not validation.is_valid:
        raise HTTPException(status_code=400, detail={"errors": validation.errors, "security_violation": True})
    
    home = await dv_risk_home_admin.create(data, current_user.user_id)
    audit_logger.log_create(user_id=current_user.user_id, table_name="dv_risk_homes", record_id=home.id, data=home)
    return home


@router.patch("/{home_id}", response_model=DVRiskHomeModel)
async def update_dv_risk_home(home_id: str, data: DVRiskHomeUpdate, current_user: CurrentUser = Depends(require_supervisor())):
    """Update a DV risk home entry"""
    existing = await dv_risk_home_admin.get_by_id(home_id)
    if not existing:
        raise HTTPException(status_code=404, detail="DV risk home not found")
    
    validation = ValidationEngine.validate_dv_risk_home(data.model_dump(exclude_unset=True))
    if not validation.is_valid:
        raise HTTPException(status_code=400, detail={"errors": validation.errors, "security_violation": True})
    
    home = await dv_risk_home_admin.update(home_id, data, current_user.user_id)
    audit_logger.log_update(user_id=current_user.user_id, table_name="dv_risk_homes", record_id=home_id, before=existing, after=home)
    return home


@router.delete("/{home_id}")
async def delete_dv_risk_home(home_id: str, current_user: CurrentUser = Depends(require_admin())):
    """Delete a DV risk home entry (admin only)"""
    existing = await dv_risk_home_admin.get_by_id(home_id)
    if not existing:
        raise HTTPException(status_code=404, detail="DV risk home not found")
    
    await dv_risk_home_admin.delete(home_id, current_user.user_id)
    audit_logger.log_delete(user_id=current_user.user_id, table_name="dv_risk_homes", record_id=home_id, data=existing)
    return {"message": "DV risk home deleted successfully"}


@router.post("/{home_id}/incident")
async def record_incident(home_id: str, current_user: CurrentUser = Depends(require_supervisor())):
    """Record a new incident for a DV risk home"""
    home = await dv_risk_home_admin.record_incident(home_id, current_user.user_id)
    if not home:
        raise HTTPException(status_code=404, detail="DV risk home not found")
    return home
