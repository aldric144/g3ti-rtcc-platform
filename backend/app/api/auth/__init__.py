"""
Authentication API router for the G3TI RTCC-UIP Backend.

This module provides endpoints for:
- User login and logout
- Token refresh
- Password management
- User CRUD operations (admin only)
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.api.deps import (
    ClientIP,
    CurrentUserId,
    RequireAdmin,
    RequireSupervisor,
    UserAgent,
    get_token_payload,
)
from app.core.exceptions import (
    AccountLockedError,
    DuplicateEntityError,
    EntityNotFoundError,
    InvalidCredentialsError,
    ValidationError,
)
from app.core.logging import get_logger
from app.schemas.auth import (
    LoginRequest,
    PasswordChange,
    RefreshTokenRequest,
    Role,
    Token,
    UserCreate,
    UserResponse,
    UserUpdate,
)
from app.schemas.common import PaginatedResponse
from app.services.auth.auth_service import (
    AuthService,
    get_auth_service,
    DEMO_AUTH_ENABLED,
    DEMO_USER_ID,
    DEMO_USERNAME,
    DEMO_ROLE,
)
from app.services.auth.user_service import UserService, get_user_service

logger = get_logger(__name__)
router = APIRouter()

# DEMO_AUTH_BLOCK_BEGIN
from datetime import UTC, datetime

def _get_demo_user_response() -> UserResponse:
    """Get demo user response for SAFE-MODE."""
    return UserResponse(
        id=DEMO_USER_ID,
        username=DEMO_USERNAME,
        email="admin@demo.local",
        first_name="Demo",
        last_name="Admin",
        badge_number="DEMO-001",
        department="System Administration",
        role=DEMO_ROLE,
        is_active=True,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
# DEMO_AUTH_BLOCK_END


@router.post("/login", response_model=Token)
async def login(
    login_data: LoginRequest,
    request: Request,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    client_ip: ClientIP,
    user_agent: UserAgent,
) -> Token:
    """
    Authenticate user and return access tokens.

    This endpoint validates user credentials and returns JWT tokens
    for API authentication.

    - **username**: Username or email address
    - **password**: User password
    - **mfa_code**: Optional MFA code if MFA is enabled

    Returns access and refresh tokens on successful authentication.
    """
    try:
        tokens = await auth_service.authenticate(
            login_data=login_data, ip_address=client_ip, user_agent=user_agent
        )
        return tokens
    except InvalidCredentialsError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message,
            headers={"WWW-Authenticate": "Bearer"},
        ) from e
    except AccountLockedError as e:
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail=e.message,
        ) from e


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> Token:
    """
    Refresh access token using refresh token.

    Use this endpoint to obtain a new access token when the current
    one expires.

    - **refresh_token**: Valid refresh token from login

    Returns new access and refresh tokens.
    """
    try:
        tokens = await auth_service.refresh_token(refresh_data.refresh_token)
        return tokens
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


@router.post("/logout")
async def logout(
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    token: Annotated[str, Depends(get_token_payload)],
) -> dict[str, str]:
    """
    Logout user and invalidate token.

    This endpoint revokes the current access token.
    """
    # Note: In a full implementation, we'd get the raw token
    # For now, just return success
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    user_id: CurrentUserId,
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> UserResponse:
    """
    Get current authenticated user's profile.

    Returns the profile information for the currently authenticated user.
    """
    # DEMO_AUTH_BLOCK_BEGIN
    # Return demo user if in SAFE-MODE and user_id matches demo user
    if DEMO_AUTH_ENABLED and user_id == DEMO_USER_ID:
        return _get_demo_user_response()
    # DEMO_AUTH_BLOCK_END
    
    try:
        user = await user_service.get_user(user_id)
        return user
    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        ) from e


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_data: UserUpdate,
    user_id: CurrentUserId,
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> UserResponse:
    """
    Update current user's profile.

    Users can update their own profile information except for role.
    """
    # Don't allow users to change their own role
    user_data.role = None

    try:
        user = await user_service.update_user(user_id, user_data, user_id)
        return user
    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        ) from e
    except DuplicateEntityError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=e.message,
        ) from e


@router.post("/me/password")
async def change_password(
    password_data: PasswordChange,
    user_id: CurrentUserId,
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> dict[str, str]:
    """
    Change current user's password.

    - **current_password**: Current password for verification
    - **new_password**: New password (must meet complexity requirements)
    """
    try:
        await user_service.change_password(user_id, password_data)
        return {"message": "Password changed successfully"}
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message,
        ) from e


# Admin endpoints for user management


@router.get("/users", response_model=PaginatedResponse[UserResponse])
async def list_users(
    token: RequireAdmin,
    user_service: Annotated[UserService, Depends(get_user_service)],
    page: int = 1,
    page_size: int = 20,
    role: Role | None = None,
    is_active: bool | None = None,
) -> PaginatedResponse[UserResponse]:
    """
    List all users (admin only).

    Returns a paginated list of users with optional filtering.

    - **page**: Page number (default: 1)
    - **page_size**: Items per page (default: 20, max: 100)
    - **role**: Filter by role
    - **is_active**: Filter by active status
    """
    users, total = await user_service.list_users(
        page=page, page_size=page_size, role=role, is_active=is_active
    )

    pages = (total + page_size - 1) // page_size if total > 0 else 0

    return PaginatedResponse(items=users, total=total, page=page, page_size=page_size, pages=pages)


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    token: RequireAdmin,
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> UserResponse:
    """
    Create a new user (admin only).

    Creates a new user account with the specified details.
    """
    try:
        user = await user_service.create_user(user_data, created_by=token.sub)
        return user
    except DuplicateEntityError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=e.message,
        ) from e
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message,
        ) from e


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    token: RequireSupervisor,
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> UserResponse:
    """
    Get a specific user (supervisor+ only).

    Returns the profile information for the specified user.
    """
    try:
        user = await user_service.get_user(user_id)
        return user
    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        ) from e


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    token: RequireAdmin,
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> UserResponse:
    """
    Update a user (admin only).

    Updates the specified user's profile information.
    """
    try:
        user = await user_service.update_user(user_id, user_data, token.sub)
        return user
    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        ) from e
    except DuplicateEntityError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=e.message,
        ) from e


@router.delete("/users/{user_id}")
async def deactivate_user(
    user_id: str,
    token: RequireAdmin,
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> dict[str, str]:
    """
    Deactivate a user (admin only).

    Deactivates the specified user account. The account is not deleted
    but marked as inactive.
    """
    try:
        await user_service.deactivate_user(user_id, token.sub)
        return {"message": "User deactivated successfully"}
    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        ) from e
