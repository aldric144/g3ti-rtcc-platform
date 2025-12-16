"""
Drones Admin API Router
Tab 2: Drones Admin
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException

from ...admin.drones_admin import drone_admin, DroneModel, DroneCreate, DroneUpdate, DroneStatus
from ...admin.validation import ValidationEngine
from ...admin.audit_log import audit_logger
from .base_router import CurrentUser, get_current_user, require_supervisor, get_pagination, PaginationParams

router = APIRouter()


@router.get("/", response_model=List[DroneModel])
async def list_drones(
    pagination: PaginationParams = Depends(get_pagination),
    status: Optional[DroneStatus] = None,
    current_user: CurrentUser = Depends(get_current_user),
):
    """List all drones"""
    filters = {"status": status} if status else None
    return await drone_admin.get_all(skip=pagination.skip, limit=pagination.limit, filters=filters)


@router.get("/active", response_model=List[DroneModel])
async def get_active_drones(current_user: CurrentUser = Depends(get_current_user)):
    """Get all active/deployed drones"""
    return await drone_admin.get_active_drones()


@router.get("/{drone_id}", response_model=DroneModel)
async def get_drone(drone_id: str, current_user: CurrentUser = Depends(get_current_user)):
    """Get a specific drone"""
    drone = await drone_admin.get_by_id(drone_id)
    if not drone:
        raise HTTPException(status_code=404, detail="Drone not found")
    return drone


@router.post("/", response_model=DroneModel)
async def create_drone(data: DroneCreate, current_user: CurrentUser = Depends(require_supervisor())):
    """Create a new drone"""
    validation = ValidationEngine.validate_telemetry(data.model_dump())
    if not validation.is_valid:
        raise HTTPException(status_code=400, detail={"errors": validation.errors})
    
    drone = await drone_admin.create(data, current_user.user_id)
    audit_logger.log_create(user_id=current_user.user_id, table_name="drones", record_id=drone.id, data=drone)
    return drone


@router.patch("/{drone_id}", response_model=DroneModel)
async def update_drone(drone_id: str, data: DroneUpdate, current_user: CurrentUser = Depends(require_supervisor())):
    """Update a drone"""
    existing = await drone_admin.get_by_id(drone_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Drone not found")
    
    drone = await drone_admin.update(drone_id, data, current_user.user_id)
    audit_logger.log_update(user_id=current_user.user_id, table_name="drones", record_id=drone_id, before=existing, after=drone)
    return drone


@router.delete("/{drone_id}")
async def delete_drone(drone_id: str, current_user: CurrentUser = Depends(require_supervisor())):
    """Delete a drone"""
    existing = await drone_admin.get_by_id(drone_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Drone not found")
    
    await drone_admin.delete(drone_id, current_user.user_id)
    audit_logger.log_delete(user_id=current_user.user_id, table_name="drones", record_id=drone_id, data=existing)
    return {"message": "Drone deleted successfully"}


@router.post("/{drone_id}/telemetry")
async def update_telemetry(
    drone_id: str,
    lat: float,
    lng: float,
    altitude: float,
    battery: int,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Update drone telemetry"""
    drone = await drone_admin.update_telemetry(drone_id, lat, lng, altitude, battery)
    if not drone:
        raise HTTPException(status_code=404, detail="Drone not found")
    return drone
