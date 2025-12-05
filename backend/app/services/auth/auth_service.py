"""
Authentication service for the G3TI RTCC-UIP Backend.

This service handles authentication operations including login,
token management, and session handling.

CJIS Compliance Note:
- All authentication attempts must be logged
- Failed attempts must trigger lockout after threshold
- Sessions must have configurable timeouts
"""

from datetime import UTC, datetime

from app.core.config import settings
from app.core.exceptions import (
    AccountLockedError,
    InvalidCredentialsError,
    InvalidTokenError,
    TokenExpiredError,
)
from app.core.logging import audit_logger, get_logger
from app.core.security import (
    SecurityManager,
    login_rate_limiter,
)
from app.schemas.auth import (
    LoginRequest,
    Role,
    Token,
    TokenPayload,
    UserInDB,
)
from app.services.auth.user_service import UserService, get_user_service

logger = get_logger(__name__)


class AuthService:
    """
    Service for authentication operations.

    Provides methods for user authentication, token management,
    and session handling with CJIS-compliant audit logging.
    """

    def __init__(self, user_service: UserService | None = None) -> None:
        """
        Initialize the authentication service.

        Args:
            user_service: User service instance (optional, will use global if not provided)
        """
        self._user_service = user_service or get_user_service()
        self._security = SecurityManager()
        self._revoked_tokens: set[str] = set()  # In production, use Redis

    async def authenticate(
        self, login_data: LoginRequest, ip_address: str, user_agent: str | None = None
    ) -> Token:
        """
        Authenticate a user and return tokens.

        Args:
            login_data: Login credentials
            ip_address: Client IP address
            user_agent: Client user agent string

        Returns:
            Token: Access and refresh tokens

        Raises:
            InvalidCredentialsError: If credentials are invalid
            AccountLockedError: If account is locked
        """
        username = login_data.username

        # Check rate limiting
        if login_rate_limiter.is_locked_out(username):
            audit_logger.log_authentication(
                user_id=None,
                username=username,
                success=False,
                ip_address=ip_address,
                user_agent=user_agent,
                failure_reason="account_locked",
            )
            raise AccountLockedError(
                "Account is temporarily locked due to too many failed attempts"
            )

        # Look up user by username or email
        user = await self._user_service.get_user_by_username(username)
        if not user:
            user = await self._user_service.get_user_by_email(username)

        if not user:
            login_rate_limiter.record_attempt(username, success=False)
            audit_logger.log_authentication(
                user_id=None,
                username=username,
                success=False,
                ip_address=ip_address,
                user_agent=user_agent,
                failure_reason="user_not_found",
            )
            raise InvalidCredentialsError()

        # Check if account is active
        if not user.is_active:
            audit_logger.log_authentication(
                user_id=user.id,
                username=username,
                success=False,
                ip_address=ip_address,
                user_agent=user_agent,
                failure_reason="account_inactive",
            )
            raise InvalidCredentialsError("Account is inactive")

        # Check if account is locked
        if user.locked_until and datetime.now(UTC) < user.locked_until:
            remaining_minutes = int(
                (user.locked_until - datetime.now(UTC)).total_seconds() / 60
            )
            audit_logger.log_authentication(
                user_id=user.id,
                username=username,
                success=False,
                ip_address=ip_address,
                user_agent=user_agent,
                failure_reason="account_locked",
            )
            raise AccountLockedError(
                f"Account is locked. Try again in {remaining_minutes} minutes.",
                lockout_remaining_minutes=remaining_minutes,
            )

        # Verify password
        if not self._security.verify_password(login_data.password, user.hashed_password):
            login_rate_limiter.record_attempt(username, success=False)
            await self._user_service.record_login(user.id, success=False, ip_address=ip_address)

            audit_logger.log_authentication(
                user_id=user.id,
                username=username,
                success=False,
                ip_address=ip_address,
                user_agent=user_agent,
                failure_reason="invalid_password",
            )
            raise InvalidCredentialsError()

        # TODO: Handle MFA if enabled
        # if user.mfa_enabled and not login_data.mfa_code:
        #     raise MFARequiredError()

        # Successful authentication
        login_rate_limiter.record_attempt(username, success=True)
        await self._user_service.record_login(user.id, success=True, ip_address=ip_address)

        # Generate tokens
        tokens = self._generate_tokens(user)

        audit_logger.log_authentication(
            user_id=user.id,
            username=username,
            success=True,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        logger.info("user_authenticated", user_id=user.id, username=username, ip_address=ip_address)

        return tokens

    async def refresh_token(self, refresh_token: str) -> Token:
        """
        Refresh access token using refresh token.

        Args:
            refresh_token: Valid refresh token

        Returns:
            Token: New access and refresh tokens

        Raises:
            InvalidTokenError: If token is invalid or revoked
            TokenExpiredError: If token has expired
        """
        # Decode token
        payload = self._security.decode_token(refresh_token)

        if not payload:
            raise InvalidTokenError("Invalid refresh token")

        # Verify token type
        if payload.get("type") != "refresh":
            raise InvalidTokenError("Invalid token type")

        # Check if token is revoked
        jti = payload.get("jti")
        if jti and jti in self._revoked_tokens:
            raise InvalidTokenError("Token has been revoked")

        # Get user
        user_id = payload.get("sub")
        user = await self._user_service.get_user_by_username(payload.get("username", ""))

        if not user or user.id != user_id:
            raise InvalidTokenError("User not found")

        if not user.is_active:
            raise InvalidTokenError("Account is inactive")

        # Revoke old refresh token
        if jti:
            self._revoked_tokens.add(jti)

        # Generate new tokens
        tokens = self._generate_tokens(user)

        logger.info("token_refreshed", user_id=user_id)

        return tokens

    async def logout(self, token: str) -> bool:
        """
        Logout user by revoking their token.

        Args:
            token: Token to revoke

        Returns:
            bool: True if logout successful
        """
        payload = self._security.decode_token(token)

        if payload:
            jti = payload.get("jti")
            if jti:
                self._revoked_tokens.add(jti)

            user_id = payload.get("sub")
            logger.info("user_logged_out", user_id=user_id)

        return True

    async def validate_token(self, token: str) -> TokenPayload:
        """
        Validate an access token and return its payload.

        Args:
            token: Access token to validate

        Returns:
            TokenPayload: Decoded token payload

        Raises:
            InvalidTokenError: If token is invalid
            TokenExpiredError: If token has expired
        """
        payload = self._security.decode_token(token)

        if not payload:
            raise InvalidTokenError("Invalid token")

        # Check token type
        if payload.get("type") != "access":
            raise InvalidTokenError("Invalid token type")

        # Check expiration
        exp = payload.get("exp")
        if exp:
            exp_datetime = datetime.fromtimestamp(exp, tz=UTC)
            if datetime.now(UTC) > exp_datetime:
                raise TokenExpiredError()

        return TokenPayload(
            sub=payload["sub"],
            username=payload["username"],
            role=Role(payload["role"]),
            exp=datetime.fromtimestamp(payload["exp"], tz=UTC),
            iat=datetime.fromtimestamp(payload["iat"], tz=UTC),
            type=payload["type"],
            jti=payload.get("jti"),
        )

    def _generate_tokens(self, user: UserInDB) -> Token:
        """
        Generate access and refresh tokens for a user.

        Args:
            user: User to generate tokens for

        Returns:
            Token: Access and refresh tokens
        """
        token_data = {
            "sub": user.id,
            "username": user.username,
            "role": user.role.value,
        }

        access_token = self._security.create_access_token(token_data)
        refresh_token = self._security.create_refresh_token(token_data)

        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60,
        )


# Global auth service instance
_auth_service: AuthService | None = None


def get_auth_service() -> AuthService:
    """Get the authentication service instance."""
    global _auth_service
    if _auth_service is None:
        _auth_service = AuthService()
    return _auth_service
