"""
Robots Admin API Router
Tab 3: Quadruped Robot Admin
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException

from ...admin.robots_admin import robot_admin, RobotModel, RobotCreate, RobotUpdate, RobotStatus
from ...admin.validation import ValidationEngine
from ...admin.audit_log import audit_logger
from .base_router import CurrentUser, get_current_user, require_supervisor, get_pagination, PaginationParams

router = APIRouter()


@router.get("/", response_model=List[RobotModel])
async def list_robots(
    pagination: PaginationParams = Depends(get_pagination),
    status: Optional[RobotStatus] = None,
    current_user: CurrentUser = Depends(get_current_user),
):
    """List all robots"""
    filters = {"status": status} if status else None
    return await robot_admin.get_all(skip=pagination.skip, limit=pagination.limit, filters=filters)


@router.get("/active", response_model=List[RobotModel])
async def get_active_robots(current_user: CurrentUser = Depends(get_current_user)):
    """Get all active/deployed robots"""
    return await robot_admin.get_active_robots()


@router.get("/{robot_id}", response_model=RobotModel)
async def get_robot(robot_id: str, current_user: CurrentUser = Depends(get_current_user)):
    """Get a specific robot"""
    robot = await robot_admin.get_by_id(robot_id)
    if not robot:
        raise HTTPException(status_code=404, detail="Robot not found")
    return robot


@router.post("/", response_model=RobotModel)
async def create_robot(data: RobotCreate, current_user: CurrentUser = Depends(require_supervisor())):
    """Create a new robot"""
    robot = await robot_admin.create(data, current_user.user_id)
    audit_logger.log_create(user_id=current_user.user_id, table_name="robots", record_id=robot.id, data=robot)
    return robot


@router.patch("/{robot_id}", response_model=RobotModel)
async def update_robot(robot_id: str, data: RobotUpdate, current_user: CurrentUser = Depends(require_supervisor())):
    """Update a robot"""
    existing = await robot_admin.get_by_id(robot_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Robot not found")
    
    robot = await robot_admin.update(robot_id, data, current_user.user_id)
    audit_logger.log_update(user_id=current_user.user_id, table_name="robots", record_id=robot_id, before=existing, after=robot)
    return robot


@router.delete("/{robot_id}")
async def delete_robot(robot_id: str, current_user: CurrentUser = Depends(require_supervisor())):
    """Delete a robot"""
    existing = await robot_admin.get_by_id(robot_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Robot not found")
    
    await robot_admin.delete(robot_id, current_user.user_id)
    audit_logger.log_delete(user_id=current_user.user_id, table_name="robots", record_id=robot_id, data=existing)
    return {"message": "Robot deleted successfully"}


@router.post("/{robot_id}/telemetry")
async def update_telemetry(
    robot_id: str,
    lat: float,
    lng: float,
    battery: int,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Update robot telemetry"""
    robot = await robot_admin.update_telemetry(robot_id, lat, lng, battery)
    if not robot:
        raise HTTPException(status_code=404, detail="Robot not found")
    return robot
