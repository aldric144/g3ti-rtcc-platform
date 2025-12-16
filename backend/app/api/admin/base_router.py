"""
Base Router - Common dependencies and utilities for admin routers
"""

from enum import Enum
from typing import Optional
from fastapi import Depends, HTTPException, Header, Request
from pydantic import BaseModel


class UserRole(str, Enum):
    VIEWER = "viewer"
    ANALYST = "analyst"
    SUPERVISOR = "supervisor"
    ADMIN = "admin"
    COMMANDER = "commander"
    SYSTEM_INTEGRATOR = "system-integrator"


class CurrentUser(BaseModel):
    """Current authenticated user"""
    user_id: str
    username: str
    role: UserRole
    ip_address: Optional[str] = None


# Role hierarchy for permission checks
ROLE_HIERARCHY = {
    UserRole.VIEWER: 1,
    UserRole.ANALYST: 2,
    UserRole.SUPERVISOR: 3,
    UserRole.ADMIN: 4,
    UserRole.COMMANDER: 5,
    UserRole.SYSTEM_INTEGRATOR: 6,
}


def get_current_user(
    request: Request,
    x_user_id: Optional[str] = Header(None, alias="X-User-ID"),
    x_username: Optional[str] = Header(None, alias="X-Username"),
    x_user_role: Optional[str] = Header(None, alias="X-User-Role"),
) -> CurrentUser:
    """Get current user from request headers (demo mode)"""
    # In production, this would validate JWT tokens
    # For demo, we accept headers or use defaults
    
    user_id = x_user_id or "demo-user"
    username = x_username or "admin"
    role_str = x_user_role or "admin"
    
    try:
        role = UserRole(role_str.lower())
    except ValueError:
        role = UserRole.VIEWER
    
    # Get client IP
    ip_address = request.client.host if request.client else None
    
    return CurrentUser(
        user_id=user_id,
        username=username,
        role=role,
        ip_address=ip_address,
    )


def require_role(min_role: UserRole):
    """Dependency to require minimum role level"""
    def check_role(current_user: CurrentUser = Depends(get_current_user)):
        user_level = ROLE_HIERARCHY.get(current_user.role, 0)
        required_level = ROLE_HIERARCHY.get(min_role, 0)
        
        if user_level < required_level:
            raise HTTPException(
                status_code=403,
                detail=f"Insufficient permissions. Required role: {min_role.value} or higher"
            )
        return current_user
    return check_role


def require_admin():
    """Require admin role or higher"""
    return require_role(UserRole.ADMIN)


def require_supervisor():
    """Require supervisor role or higher"""
    return require_role(UserRole.SUPERVISOR)


def require_analyst():
    """Require analyst role or higher"""
    return require_role(UserRole.ANALYST)


class PaginationParams(BaseModel):
    """Pagination parameters"""
    skip: int = 0
    limit: int = 100


def get_pagination(skip: int = 0, limit: int = 100) -> PaginationParams:
    """Get pagination parameters"""
    if limit > 1000:
        limit = 1000
    return PaginationParams(skip=skip, limit=limit)
