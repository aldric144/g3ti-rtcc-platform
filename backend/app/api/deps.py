"""
API dependencies for the G3TI RTCC-UIP Backend.

This module provides FastAPI dependencies for:
- Authentication and authorization
- Database connections
- Service instances
- Request validation
"""

from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.exceptions import (
    InvalidTokenError,
    TokenExpiredError,
)
from app.core.logging import audit_logger, get_logger
from app.schemas.auth import Role, TokenPayload
from app.services.auth.auth_service import AuthService, get_auth_service

logger = get_logger(__name__)

# Security scheme
security = HTTPBearer(auto_error=False)


async def get_token_payload(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> TokenPayload:
    """
    Validate JWT token and return payload.

    This dependency extracts and validates the JWT token from the
    Authorization header.

    Args:
        credentials: HTTP Bearer credentials
        auth_service: Authentication service

    Returns:
        TokenPayload: Decoded token payload

    Raises:
        HTTPException: If token is missing, invalid, or expired
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = await auth_service.validate_token(credentials.credentials)
        return payload
    except TokenExpiredError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


async def get_current_user_id(token: Annotated[TokenPayload, Depends(get_token_payload)]) -> str:
    """
    Get the current authenticated user's ID.

    Args:
        token: Validated token payload

    Returns:
        str: User ID
    """
    return token.sub


async def get_current_user_role(token: Annotated[TokenPayload, Depends(get_token_payload)]) -> Role:
    """
    Get the current authenticated user's role.

    Args:
        token: Validated token payload

    Returns:
        Role: User role
    """
    return token.role


async def get_current_user(token: Annotated[TokenPayload, Depends(get_token_payload)]) -> "UserInDB":
    """
    Get the current authenticated user.

    Args:
        token: Validated token payload

    Returns:
        UserInDB: User object with id, username, and role
    """
    from app.schemas.auth import UserInDB
    
    return UserInDB(
        id=token.sub,
        username=token.sub,
        role=token.role,
        email=f"{token.sub}@rtcc.local",
        hashed_password="",
        is_active=True,
    )


def require_role(required_role: Role):
    """
    Create a dependency that requires a specific role or higher.

    Args:
        required_role: Minimum required role

    Returns:
        Dependency function
    """

    async def role_checker(
        token: Annotated[TokenPayload, Depends(get_token_payload)], request: Request
    ) -> TokenPayload:
        """Check if user has required role."""
        if not token.role.has_permission(required_role):
            # Log authorization failure
            audit_logger.log_authorization(
                user_id=token.sub,
                resource=str(request.url.path),
                action=request.method,
                allowed=False,
                required_role=required_role.value,
            )

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required role: {required_role.value}",
            )

        # Log successful authorization
        audit_logger.log_authorization(
            user_id=token.sub,
            resource=str(request.url.path),
            action=request.method,
            allowed=True,
            required_role=required_role.value,
        )

        return token

    return role_checker


# Pre-defined role dependencies
RequireAdmin = Annotated[TokenPayload, Depends(require_role(Role.ADMIN))]
RequireSupervisor = Annotated[TokenPayload, Depends(require_role(Role.SUPERVISOR))]
RequireDetective = Annotated[TokenPayload, Depends(require_role(Role.DETECTIVE))]
RequireAnalyst = Annotated[TokenPayload, Depends(require_role(Role.RTCC_ANALYST))]
RequireOfficer = Annotated[TokenPayload, Depends(require_role(Role.OFFICER))]


def get_client_ip(request: Request) -> str:
    """
    Get the client IP address from the request.

    Handles X-Forwarded-For header for proxied requests.

    Args:
        request: FastAPI request

    Returns:
        str: Client IP address
    """
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # Get the first IP in the chain (original client)
        return forwarded_for.split(",")[0].strip()

    if request.client:
        return request.client.host

    return "unknown"


def get_user_agent(request: Request) -> str | None:
    """
    Get the user agent from the request.

    Args:
        request: FastAPI request

    Returns:
        str or None: User agent string
    """
    return request.headers.get("User-Agent")


# Type aliases for common dependencies
CurrentUserId = Annotated[str, Depends(get_current_user_id)]
CurrentUserRole = Annotated[Role, Depends(get_current_user_role)]
ClientIP = Annotated[str, Depends(get_client_ip)]
UserAgent = Annotated[str | None, Depends(get_user_agent)]
