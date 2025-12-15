"""
Security utilities for the G3TI RTCC-UIP Backend.

This module provides cryptographic functions, password hashing, and
security-related utilities required for authentication and data protection.

CJIS Compliance Note:
- Passwords must be hashed using approved algorithms (bcrypt)
- Minimum password complexity requirements must be enforced
- Failed login attempts must be tracked and limited
- Session tokens must be securely generated and validated
"""

import secrets
from datetime import UTC, datetime, timedelta
from typing import Any

from jose import JWTError, jwt

from app.core.config import settings

# DEMO_AUTH_BLOCK_BEGIN
# In SAFE-MODE, use a lightweight dummy context to avoid bcrypt memory overhead
# This is only for demo/preview purposes - production should always use bcrypt
import sys
print(f"[SECURITY_INIT] safe_mode={settings.safe_mode}", file=sys.stderr, flush=True)

if settings.safe_mode:
    print("[SECURITY_INIT] Using DummyContext - bcrypt NOT loaded", file=sys.stderr, flush=True)
    class DummyContext:
        """Lightweight password context for SAFE-MODE demo authentication."""
        def hash(self, password: str) -> str:
            # Not used in demo mode - demo auth bypasses password verification
            return f"demo_hash_{password}"
        
        def verify(self, plain_password: str, hashed_password: str) -> bool:
            # Not used in demo mode - demo auth bypasses password verification
            return False
    
    pwd_context = DummyContext()
else:
    print("[SECURITY_INIT] Loading bcrypt CryptContext", file=sys.stderr, flush=True)
    from passlib.context import CryptContext
    # Password hashing context using bcrypt
    pwd_context = CryptContext(
        schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12  # CJIS-compliant work factor
    )
# DEMO_AUTH_BLOCK_END


class SecurityManager:
    """
    Centralized security manager for cryptographic operations.

    Provides methods for password hashing, token generation, and
    other security-related functions.
    """

    # Minimum password requirements for CJIS compliance
    MIN_PASSWORD_LENGTH = 12
    REQUIRE_UPPERCASE = True
    REQUIRE_LOWERCASE = True
    REQUIRE_DIGIT = True
    REQUIRE_SPECIAL = True
    SPECIAL_CHARACTERS = "!@#$%^&*()_+-=[]{}|;:,.<>?"

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a password using bcrypt.

        Args:
            password: Plain text password

        Returns:
            str: Hashed password
        """
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash.

        Args:
            plain_password: Plain text password to verify
            hashed_password: Stored password hash

        Returns:
            bool: True if password matches, False otherwise
        """
        return pwd_context.verify(plain_password, hashed_password)

    @classmethod
    def validate_password_strength(cls, password: str) -> tuple[bool, list[str]]:
        """
        Validate password meets CJIS complexity requirements.

        Args:
            password: Password to validate

        Returns:
            tuple: (is_valid, list of validation errors)
        """
        errors: list[str] = []

        if len(password) < cls.MIN_PASSWORD_LENGTH:
            errors.append(f"Password must be at least {cls.MIN_PASSWORD_LENGTH} characters long")

        if cls.REQUIRE_UPPERCASE and not any(c.isupper() for c in password):
            errors.append("Password must contain at least one uppercase letter")

        if cls.REQUIRE_LOWERCASE and not any(c.islower() for c in password):
            errors.append("Password must contain at least one lowercase letter")

        if cls.REQUIRE_DIGIT and not any(c.isdigit() for c in password):
            errors.append("Password must contain at least one digit")

        if cls.REQUIRE_SPECIAL and not any(c in cls.SPECIAL_CHARACTERS for c in password):
            errors.append(
                f"Password must contain at least one special character: {cls.SPECIAL_CHARACTERS}"
            )

        return len(errors) == 0, errors

    @staticmethod
    def create_access_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
        """
        Create a JWT access token.

        Args:
            data: Data to encode in the token
            expires_delta: Optional custom expiration time

        Returns:
            str: Encoded JWT token
        """
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.now(UTC) + expires_delta
        else:
            expire = datetime.now(UTC) + timedelta(minutes=settings.access_token_expire_minutes)

        to_encode.update({"exp": expire, "iat": datetime.now(UTC), "type": "access"})

        return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)

    @staticmethod
    def create_refresh_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
        """
        Create a JWT refresh token.

        Args:
            data: Data to encode in the token
            expires_delta: Optional custom expiration time

        Returns:
            str: Encoded JWT refresh token
        """
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.now(UTC) + expires_delta
        else:
            expire = datetime.now(UTC) + timedelta(days=settings.refresh_token_expire_days)

        to_encode.update(
            {
                "exp": expire,
                "iat": datetime.now(UTC),
                "type": "refresh",
                "jti": secrets.token_urlsafe(32),  # Unique token ID for revocation
            }
        )

        return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)

    @staticmethod
    def decode_token(token: str) -> dict[str, Any] | None:
        """
        Decode and validate a JWT token.

        Args:
            token: JWT token to decode

        Returns:
            dict or None: Decoded token payload or None if invalid
        """
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
            return payload
        except JWTError:
            return None

    @staticmethod
    def generate_secure_token(length: int = 32) -> str:
        """
        Generate a cryptographically secure random token.

        Args:
            length: Length of the token in bytes

        Returns:
            str: URL-safe base64 encoded token
        """
        return secrets.token_urlsafe(length)

    @staticmethod
    def generate_api_key() -> str:
        """
        Generate a secure API key.

        Returns:
            str: API key in format 'rtcc_xxxx...'
        """
        return f"rtcc_{secrets.token_urlsafe(32)}"


class RateLimiter:
    """
    Rate limiter for protecting against brute force attacks.

    Tracks failed attempts and implements exponential backoff.
    Note: In production, this should use Redis for distributed rate limiting.
    """

    def __init__(self, max_attempts: int = 5, lockout_duration_minutes: int = 15) -> None:
        """
        Initialize rate limiter.

        Args:
            max_attempts: Maximum failed attempts before lockout
            lockout_duration_minutes: Lockout duration in minutes
        """
        self.max_attempts = max_attempts
        self.lockout_duration = timedelta(minutes=lockout_duration_minutes)
        self._attempts: dict[str, list[datetime]] = {}
        self._lockouts: dict[str, datetime] = {}

    def is_locked_out(self, identifier: str) -> bool:
        """
        Check if an identifier is currently locked out.

        Args:
            identifier: User identifier (username, IP, etc.)

        Returns:
            bool: True if locked out, False otherwise
        """
        if identifier not in self._lockouts:
            return False

        lockout_until = self._lockouts[identifier]
        if datetime.now(UTC) > lockout_until:
            del self._lockouts[identifier]
            self._attempts.pop(identifier, None)
            return False

        return True

    def record_attempt(self, identifier: str, success: bool) -> None:
        """
        Record an authentication attempt.

        Args:
            identifier: User identifier
            success: Whether the attempt was successful
        """
        if success:
            self._attempts.pop(identifier, None)
            self._lockouts.pop(identifier, None)
            return

        now = datetime.now(UTC)

        if identifier not in self._attempts:
            self._attempts[identifier] = []

        # Clean old attempts (older than lockout duration)
        cutoff = now - self.lockout_duration
        self._attempts[identifier] = [
            attempt for attempt in self._attempts[identifier] if attempt > cutoff
        ]

        self._attempts[identifier].append(now)

        if len(self._attempts[identifier]) >= self.max_attempts:
            self._lockouts[identifier] = now + self.lockout_duration

    def get_remaining_attempts(self, identifier: str) -> int:
        """
        Get remaining attempts before lockout.

        Args:
            identifier: User identifier

        Returns:
            int: Number of remaining attempts
        """
        if identifier not in self._attempts:
            return self.max_attempts

        return max(0, self.max_attempts - len(self._attempts[identifier]))


# Global security manager instance
security_manager = SecurityManager()

# Global rate limiter for login attempts
login_rate_limiter = RateLimiter(max_attempts=5, lockout_duration_minutes=15)


# FastAPI dependency functions for authentication
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

security_bearer = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security_bearer)],
) -> "UserInDB":
    """
    Get the current authenticated user from JWT token.
    
    Args:
        credentials: HTTP Bearer credentials
        
    Returns:
        UserInDB: User object with id, username, and role
        
    Raises:
        HTTPException: If token is missing or invalid
    """
    from app.schemas.auth import Role, UserInDB
    
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    payload = security_manager.decode_token(credentials.credentials)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub", "unknown")
    role_str = payload.get("role", "officer")
    
    try:
        role = Role(role_str)
    except ValueError:
        role = Role.OFFICER
    
    return UserInDB(
        id=user_id,
        username=user_id,
        role=role,
        email=f"{user_id}@rtcc.local",
        hashed_password="",
        is_active=True,
    )


def require_roles(*required_roles: str):
    """
    Create a dependency that requires specific roles.
    
    Args:
        required_roles: List of required role names
        
    Returns:
        Dependency function
    """
    from app.schemas.auth import Role
    
    async def role_checker(
        credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security_bearer)],
    ) -> "UserInDB":
        user = await get_current_user(credentials)
        
        if user.role.value not in required_roles and user.role.value != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required roles: {required_roles}",
            )
        
        return user
    
    return role_checker
