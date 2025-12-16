"""
Users Admin API Router
Tab 14: Users
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException

from ...admin.users_admin import user_admin, UserModel, UserCreate, UserUpdate, UserRole, UserStatus
from ...admin.audit_log import audit_logger
from .base_router import CurrentUser, get_current_user, require_admin, get_pagination, PaginationParams

router = APIRouter()


@router.get("/", response_model=List[UserModel])
async def list_users(
    pagination: PaginationParams = Depends(get_pagination),
    role: Optional[UserRole] = None,
    status: Optional[UserStatus] = None,
    sector: Optional[str] = None,
    current_user: CurrentUser = Depends(require_admin()),
):
    """List all users (admin only)"""
    filters = {}
    if role:
        filters["role"] = role
    if status:
        filters["status"] = status
    if sector:
        filters["assigned_sector"] = sector
    return await user_admin.get_all(skip=pagination.skip, limit=pagination.limit, filters=filters if filters else None)


@router.get("/role/{role}", response_model=List[UserModel])
async def get_by_role(role: UserRole, current_user: CurrentUser = Depends(require_admin())):
    """Get users by role"""
    return await user_admin.get_by_role(role)


@router.get("/sector/{sector}", response_model=List[UserModel])
async def get_by_sector(sector: str, current_user: CurrentUser = Depends(require_admin())):
    """Get users by assigned sector"""
    return await user_admin.get_by_sector(sector)


@router.get("/{user_id}", response_model=UserModel)
async def get_user(user_id: str, current_user: CurrentUser = Depends(require_admin())):
    """Get a specific user"""
    user = await user_admin.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/username/{username}", response_model=UserModel)
async def get_by_username(username: str, current_user: CurrentUser = Depends(require_admin())):
    """Get user by username"""
    user = await user_admin.get_by_username(username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/", response_model=UserModel)
async def create_user(data: UserCreate, current_user: CurrentUser = Depends(require_admin())):
    """Create a new user"""
    try:
        user = await user_admin.create(data, current_user.user_id)
        audit_logger.log_create(user_id=current_user.user_id, table_name="users", record_id=user.id, data=user)
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{user_id}", response_model=UserModel)
async def update_user(user_id: str, data: UserUpdate, current_user: CurrentUser = Depends(require_admin())):
    """Update a user"""
    existing = await user_admin.get_by_id(user_id)
    if not existing:
        raise HTTPException(status_code=404, detail="User not found")
    
    user = await user_admin.update(user_id, data, current_user.user_id)
    audit_logger.log_update(user_id=current_user.user_id, table_name="users", record_id=user_id, before=existing, after=user)
    return user


@router.delete("/{user_id}")
async def delete_user(user_id: str, current_user: CurrentUser = Depends(require_admin())):
    """Delete a user"""
    existing = await user_admin.get_by_id(user_id)
    if not existing:
        raise HTTPException(status_code=404, detail="User not found")
    
    await user_admin.delete(user_id, current_user.user_id)
    audit_logger.log_delete(user_id=current_user.user_id, table_name="users", record_id=user_id, data=existing)
    return {"message": "User deleted successfully"}


@router.post("/{user_id}/unlock")
async def unlock_user(user_id: str, current_user: CurrentUser = Depends(require_admin())):
    """Unlock a locked user account"""
    user = await user_admin.unlock_user(user_id, current_user.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/{user_id}/reset-mfa")
async def reset_mfa(user_id: str, current_user: CurrentUser = Depends(require_admin())):
    """Reset MFA for a user"""
    user = await user_admin.reset_mfa(user_id, current_user.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
