"""
Cameras Admin API Router
Tab 1: Camera Admin
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query

from ...admin.cameras_admin import camera_admin, CameraModel, CameraCreate, CameraUpdate, CameraType, CameraStatus
from ...admin.validation import ValidationEngine
from ...admin.audit_log import audit_logger, AuditAction
from .base_router import CurrentUser, get_current_user, require_supervisor, get_pagination, PaginationParams, UserRole

router = APIRouter()


@router.get("/", response_model=List[CameraModel])
async def list_cameras(
    pagination: PaginationParams = Depends(get_pagination),
    camera_type: Optional[CameraType] = None,
    status: Optional[CameraStatus] = None,
    sector: Optional[str] = None,
    current_user: CurrentUser = Depends(get_current_user),
):
    """List all cameras with optional filters"""
    filters = {}
    if camera_type:
        filters["camera_type"] = camera_type
    if status:
        filters["status"] = status
    if sector:
        filters["sector"] = sector
    
    cameras = await camera_admin.get_all(
        skip=pagination.skip,
        limit=pagination.limit,
        filters=filters if filters else None
    )
    
    audit_logger.log_read(
        user_id=current_user.user_id,
        table_name="cameras",
        username=current_user.username,
        ip_address=current_user.ip_address,
    )
    
    return cameras


@router.get("/{camera_id}", response_model=CameraModel)
async def get_camera(
    camera_id: str,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Get a specific camera by ID"""
    camera = await camera_admin.get_by_id(camera_id)
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    
    audit_logger.log_read(
        user_id=current_user.user_id,
        table_name="cameras",
        record_id=camera_id,
        username=current_user.username,
        ip_address=current_user.ip_address,
    )
    
    return camera


@router.post("/", response_model=CameraModel)
async def create_camera(
    data: CameraCreate,
    current_user: CurrentUser = Depends(require_supervisor()),
):
    """Create a new camera"""
    # Validate data
    validation = ValidationEngine.validate_camera(data.model_dump())
    if not validation.is_valid:
        raise HTTPException(status_code=400, detail={"errors": validation.errors})
    
    camera = await camera_admin.create(data, current_user.user_id)
    
    audit_logger.log_create(
        user_id=current_user.user_id,
        table_name="cameras",
        record_id=camera.id,
        data=camera,
        username=current_user.username,
        ip_address=current_user.ip_address,
    )
    
    return camera


@router.patch("/{camera_id}", response_model=CameraModel)
async def update_camera(
    camera_id: str,
    data: CameraUpdate,
    current_user: CurrentUser = Depends(require_supervisor()),
):
    """Update an existing camera"""
    existing = await camera_admin.get_by_id(camera_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Camera not found")
    
    # Validate data
    validation = ValidationEngine.validate_camera(data.model_dump(exclude_unset=True))
    if not validation.is_valid:
        raise HTTPException(status_code=400, detail={"errors": validation.errors})
    
    camera = await camera_admin.update(camera_id, data, current_user.user_id)
    
    audit_logger.log_update(
        user_id=current_user.user_id,
        table_name="cameras",
        record_id=camera_id,
        before=existing,
        after=camera,
        username=current_user.username,
        ip_address=current_user.ip_address,
    )
    
    return camera


@router.delete("/{camera_id}")
async def delete_camera(
    camera_id: str,
    current_user: CurrentUser = Depends(require_supervisor()),
):
    """Delete a camera"""
    existing = await camera_admin.get_by_id(camera_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Camera not found")
    
    await camera_admin.delete(camera_id, current_user.user_id)
    
    audit_logger.log_delete(
        user_id=current_user.user_id,
        table_name="cameras",
        record_id=camera_id,
        data=existing,
        username=current_user.username,
        ip_address=current_user.ip_address,
    )
    
    return {"message": "Camera deleted successfully"}


@router.post("/{camera_id}/health-check")
async def check_camera_health(
    camera_id: str,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Check camera stream health"""
    result = await camera_admin.check_camera_health(camera_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@router.get("/sector/{sector}", response_model=List[CameraModel])
async def get_cameras_by_sector(
    sector: str,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Get all cameras in a sector"""
    return await camera_admin.get_by_sector(sector)


@router.get("/type/{camera_type}", response_model=List[CameraModel])
async def get_cameras_by_type(
    camera_type: CameraType,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Get all cameras of a specific type"""
    return await camera_admin.get_by_type(camera_type)
