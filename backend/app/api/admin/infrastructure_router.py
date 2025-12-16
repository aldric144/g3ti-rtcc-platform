"""
Infrastructure Admin API Router
Tab 7: Critical Infrastructure
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException

from ...admin.infrastructure_admin import infrastructure_admin, InfrastructureModel, InfrastructureCreate, InfrastructureUpdate, InfrastructureType, InfrastructureStatus
from ...admin.audit_log import audit_logger
from .base_router import CurrentUser, get_current_user, require_supervisor, get_pagination, PaginationParams

router = APIRouter()


@router.get("/", response_model=List[InfrastructureModel])
async def list_infrastructure(
    pagination: PaginationParams = Depends(get_pagination),
    infra_type: Optional[InfrastructureType] = None,
    status: Optional[InfrastructureStatus] = None,
    current_user: CurrentUser = Depends(get_current_user),
):
    """List all infrastructure"""
    filters = {}
    if infra_type:
        filters["infra_type"] = infra_type
    if status:
        filters["status"] = status
    return await infrastructure_admin.get_all(skip=pagination.skip, limit=pagination.limit, filters=filters if filters else None)


@router.get("/critical", response_model=List[InfrastructureModel])
async def get_critical_infrastructure(current_user: CurrentUser = Depends(get_current_user)):
    """Get infrastructure with non-operational status"""
    return await infrastructure_admin.get_critical()


@router.get("/type/{infra_type}", response_model=List[InfrastructureModel])
async def get_by_type(infra_type: InfrastructureType, current_user: CurrentUser = Depends(get_current_user)):
    """Get infrastructure by type"""
    return await infrastructure_admin.get_by_type(infra_type)


@router.get("/{infra_id}", response_model=InfrastructureModel)
async def get_infrastructure(infra_id: str, current_user: CurrentUser = Depends(get_current_user)):
    """Get specific infrastructure"""
    infra = await infrastructure_admin.get_by_id(infra_id)
    if not infra:
        raise HTTPException(status_code=404, detail="Infrastructure not found")
    return infra


@router.post("/", response_model=InfrastructureModel)
async def create_infrastructure(data: InfrastructureCreate, current_user: CurrentUser = Depends(require_supervisor())):
    """Create new infrastructure"""
    infra = await infrastructure_admin.create(data, current_user.user_id)
    audit_logger.log_create(user_id=current_user.user_id, table_name="infrastructure", record_id=infra.id, data=infra)
    return infra


@router.patch("/{infra_id}", response_model=InfrastructureModel)
async def update_infrastructure(infra_id: str, data: InfrastructureUpdate, current_user: CurrentUser = Depends(require_supervisor())):
    """Update infrastructure"""
    existing = await infrastructure_admin.get_by_id(infra_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Infrastructure not found")
    
    infra = await infrastructure_admin.update(infra_id, data, current_user.user_id)
    audit_logger.log_update(user_id=current_user.user_id, table_name="infrastructure", record_id=infra_id, before=existing, after=infra)
    return infra


@router.delete("/{infra_id}")
async def delete_infrastructure(infra_id: str, current_user: CurrentUser = Depends(require_supervisor())):
    """Delete infrastructure"""
    existing = await infrastructure_admin.get_by_id(infra_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Infrastructure not found")
    
    await infrastructure_admin.delete(infra_id, current_user.user_id)
    audit_logger.log_delete(user_id=current_user.user_id, table_name="infrastructure", record_id=infra_id, data=existing)
    return {"message": "Infrastructure deleted successfully"}
