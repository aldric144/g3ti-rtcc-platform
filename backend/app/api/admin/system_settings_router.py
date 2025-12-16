"""
System Settings Admin API Router
Tab 15: System Settings
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException

from ...admin.system_settings_admin import system_settings_admin, SystemSettingsModel, SystemSettingsCreate, SystemSettingsUpdate
from ...admin.audit_log import audit_logger
from .base_router import CurrentUser, get_current_user, require_admin, get_pagination, PaginationParams

router = APIRouter()


@router.get("/", response_model=List[SystemSettingsModel])
async def list_settings(
    pagination: PaginationParams = Depends(get_pagination),
    category: Optional[str] = None,
    current_user: CurrentUser = Depends(get_current_user),
):
    """List all system settings"""
    filters = {"category": category} if category else None
    return await system_settings_admin.get_all(skip=pagination.skip, limit=pagination.limit, filters=filters)


@router.get("/category/{category}", response_model=List[SystemSettingsModel])
async def get_by_category(category: str, current_user: CurrentUser = Depends(get_current_user)):
    """Get settings by category"""
    return await system_settings_admin.get_by_category(category)


@router.get("/key/{key}")
async def get_by_key(key: str, current_user: CurrentUser = Depends(get_current_user)):
    """Get setting by key"""
    setting = await system_settings_admin.get_by_key(key)
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    return setting


@router.get("/value/{key}")
async def get_value(key: str, default: Optional[str] = None, current_user: CurrentUser = Depends(get_current_user)):
    """Get setting value by key"""
    value = await system_settings_admin.get_value(key, default)
    return {"key": key, "value": value}


@router.get("/video-wall-config")
async def get_video_wall_config(current_user: CurrentUser = Depends(get_current_user)):
    """Get video wall configuration"""
    return await system_settings_admin.get_video_wall_config()


@router.get("/alert-thresholds")
async def get_alert_thresholds(current_user: CurrentUser = Depends(get_current_user)):
    """Get alert threshold configuration"""
    return await system_settings_admin.get_alert_thresholds()


@router.get("/{setting_id}", response_model=SystemSettingsModel)
async def get_setting(setting_id: str, current_user: CurrentUser = Depends(get_current_user)):
    """Get a specific setting"""
    setting = await system_settings_admin.get_by_id(setting_id)
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    return setting


@router.post("/", response_model=SystemSettingsModel)
async def create_setting(data: SystemSettingsCreate, current_user: CurrentUser = Depends(require_admin())):
    """Create a new setting"""
    try:
        setting = await system_settings_admin.create(data, current_user.user_id)
        audit_logger.log_create(user_id=current_user.user_id, table_name="system_settings", record_id=setting.id, data=setting)
        return setting
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{setting_id}", response_model=SystemSettingsModel)
async def update_setting(setting_id: str, data: SystemSettingsUpdate, current_user: CurrentUser = Depends(require_admin())):
    """Update a setting"""
    existing = await system_settings_admin.get_by_id(setting_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Setting not found")
    
    setting = await system_settings_admin.update(setting_id, data, current_user.user_id)
    audit_logger.log_update(user_id=current_user.user_id, table_name="system_settings", record_id=setting_id, before=existing, after=setting)
    return setting


@router.put("/key/{key}")
async def set_value(key: str, value: str, current_user: CurrentUser = Depends(require_admin())):
    """Set setting value by key"""
    setting = await system_settings_admin.set_value(key, value, current_user.user_id)
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    return setting


@router.delete("/{setting_id}")
async def delete_setting(setting_id: str, current_user: CurrentUser = Depends(require_admin())):
    """Delete a setting"""
    existing = await system_settings_admin.get_by_id(setting_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Setting not found")
    
    await system_settings_admin.delete(setting_id, current_user.user_id)
    audit_logger.log_delete(user_id=current_user.user_id, table_name="system_settings", record_id=setting_id, data=existing)
    return {"message": "Setting deleted successfully"}
