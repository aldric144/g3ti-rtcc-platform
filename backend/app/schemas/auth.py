"""
Authentication and user schemas for the G3TI RTCC-UIP Backend.

This module defines schemas for user management, authentication,
and role-based access control.

CJIS Compliance Note:
- User credentials must never be exposed in responses
- All authentication events must be auditable
- Role assignments must be tracked
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import ConfigDict, EmailStr, Field, field_validator

from app.schemas.common import RTCCBaseModel, TimestampMixin


class Role(str, Enum):
    """
    User roles for RBAC.

    Roles are hierarchical with admin having the highest privileges.
    """

    ADMIN = "admin"
    SUPERVISOR = "supervisor"
    DETECTIVE = "detective"
    RTCC_ANALYST = "rtcc_analyst"
    OFFICER = "officer"

    @classmethod
    def get_hierarchy(cls) -> dict[str, int]:
        """Get role hierarchy levels (higher = more privileges)."""
        return {
            cls.OFFICER.value: 1,
            cls.RTCC_ANALYST.value: 2,
            cls.DETECTIVE.value: 3,
            cls.SUPERVISOR.value: 4,
            cls.ADMIN.value: 5,
        }

    def has_permission(self, required_role: "Role") -> bool:
        """Check if this role has permission for the required role level."""
        hierarchy = self.get_hierarchy()
        return hierarchy.get(self.value, 0) >= hierarchy.get(required_role.value, 0)


class UserBase(RTCCBaseModel):
    """Base user schema with common fields."""

    username: str = Field(
        min_length=3,
        max_length=50,
        pattern=r"^[a-zA-Z0-9_]+$",
        description="Unique username (alphanumeric and underscores only)",
    )
    email: EmailStr = Field(description="User email address")
    first_name: str = Field(min_length=1, max_length=100, description="First name")
    last_name: str = Field(min_length=1, max_length=100, description="Last name")
    badge_number: str | None = Field(
        default=None, max_length=20, description="Officer badge number"
    )
    department: str | None = Field(default=None, max_length=100, description="Department or unit")
    role: Role = Field(default=Role.OFFICER, description="User role for RBAC")
    is_active: bool = Field(default=True, description="Whether user account is active")


class UserCreate(UserBase):
    """Schema for creating a new user."""

    password: str = Field(
        min_length=12,
        description="Password (minimum 12 characters, must meet complexity requirements)",
    )

    @field_validator("password")
    @classmethod
    def validate_password_complexity(cls, v: str) -> str:
        """Validate password meets CJIS complexity requirements."""
        errors = []

        if not any(c.isupper() for c in v):
            errors.append("must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            errors.append("must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            errors.append("must contain at least one digit")
        if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in v):
            errors.append("must contain at least one special character")

        if errors:
            raise ValueError(f"Password {', '.join(errors)}")

        return v


class UserUpdate(RTCCBaseModel):
    """Schema for updating an existing user."""

    email: EmailStr | None = None
    first_name: str | None = Field(default=None, min_length=1, max_length=100)
    last_name: str | None = Field(default=None, min_length=1, max_length=100)
    badge_number: str | None = Field(default=None, max_length=20)
    department: str | None = Field(default=None, max_length=100)
    role: Role | None = None
    is_active: bool | None = None


class UserResponse(UserBase, TimestampMixin):
    """Schema for user response (excludes sensitive data)."""

    id: str = Field(description="Unique user identifier")
    last_login: datetime | None = Field(default=None, description="Last successful login timestamp")
    failed_login_attempts: int = Field(
        default=0, description="Number of consecutive failed login attempts"
    )
    locked_until: datetime | None = Field(
        default=None, description="Account locked until this timestamp"
    )

    @property
    def full_name(self) -> str:
        """Get user's full name."""
        return f"{self.first_name} {self.last_name}"

    @property
    def is_locked(self) -> bool:
        """Check if account is currently locked."""
        if self.locked_until is None:
            return False
        return datetime.utcnow() < self.locked_until


class UserInDB(UserResponse):
    """
    Internal user schema with hashed password.

    This schema is used internally and should never be returned to clients.
    """

    model_config = ConfigDict(from_attributes=True)

    hashed_password: str = Field(description="Bcrypt hashed password")
    password_changed_at: datetime | None = Field(
        default=None, description="Last password change timestamp"
    )
    mfa_enabled: bool = Field(default=False, description="Whether MFA is enabled")
    mfa_secret: str | None = Field(default=None, description="MFA secret key")


class LoginRequest(RTCCBaseModel):
    """Schema for login request."""

    username: str = Field(description="Username or email")
    password: str = Field(description="Password")
    mfa_code: str | None = Field(
        default=None, pattern=r"^\d{6}$", description="6-digit MFA code if MFA is enabled"
    )


class Token(RTCCBaseModel):
    """Schema for authentication token response."""

    access_token: str = Field(description="JWT access token")
    refresh_token: str = Field(description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(description="Access token expiration time in seconds")


class TokenPayload(RTCCBaseModel):
    """Schema for decoded JWT token payload."""

    sub: str = Field(description="Subject (user ID)")
    username: str = Field(description="Username")
    role: Role = Field(description="User role")
    exp: datetime = Field(description="Expiration timestamp")
    iat: datetime = Field(description="Issued at timestamp")
    type: str = Field(description="Token type (access or refresh)")
    jti: str | None = Field(default=None, description="JWT ID for refresh tokens")


class PasswordChange(RTCCBaseModel):
    """Schema for password change request."""

    current_password: str = Field(description="Current password")
    new_password: str = Field(min_length=12, description="New password (minimum 12 characters)")

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        """Validate new password meets complexity requirements."""
        errors = []

        if not any(c.isupper() for c in v):
            errors.append("must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            errors.append("must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            errors.append("must contain at least one digit")
        if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in v):
            errors.append("must contain at least one special character")

        if errors:
            raise ValueError(f"Password {', '.join(errors)}")

        return v


class RefreshTokenRequest(RTCCBaseModel):
    """Schema for token refresh request."""

    refresh_token: str = Field(description="Refresh token")


class SessionInfo(RTCCBaseModel):
    """Schema for active session information."""

    session_id: str = Field(description="Session identifier")
    user_id: str = Field(description="User ID")
    ip_address: str = Field(description="Client IP address")
    user_agent: str | None = Field(default=None, description="Client user agent")
    created_at: datetime = Field(description="Session creation timestamp")
    last_activity: datetime = Field(description="Last activity timestamp")
    expires_at: datetime = Field(description="Session expiration timestamp")


class AuditLogEntry(RTCCBaseModel):
    """Schema for authentication audit log entry."""

    id: str = Field(description="Audit log entry ID")
    timestamp: datetime = Field(description="Event timestamp")
    user_id: str | None = Field(description="User ID if known")
    username: str = Field(description="Username attempted")
    event_type: str = Field(description="Event type (login, logout, failed_login, etc.)")
    ip_address: str = Field(description="Client IP address")
    user_agent: str | None = Field(default=None, description="Client user agent")
    success: bool = Field(description="Whether the event was successful")
    failure_reason: str | None = Field(default=None, description="Reason for failure if applicable")
    details: dict[str, Any] = Field(default_factory=dict, description="Additional event details")
