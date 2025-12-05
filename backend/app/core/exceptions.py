"""
Custom exceptions for the G3TI RTCC-UIP Backend.

This module defines application-specific exceptions that provide
meaningful error messages and appropriate HTTP status codes.

All exceptions are designed to be caught by FastAPI's exception handlers
and converted to appropriate API responses.
"""

from typing import Any


class RTCCBaseException(Exception):
    """
    Base exception for all RTCC-UIP application exceptions.

    Attributes:
        message: Human-readable error message
        error_code: Machine-readable error code
        details: Additional error details
    """

    def __init__(
        self, message: str, error_code: str = "RTCC_ERROR", details: dict[str, Any] | None = None
    ) -> None:
        """
        Initialize the exception.

        Args:
            message: Human-readable error message
            error_code: Machine-readable error code
            details: Additional error details
        """
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


# Authentication Exceptions
class AuthenticationError(RTCCBaseException):
    """Raised when authentication fails."""

    def __init__(
        self, message: str = "Authentication failed", details: dict[str, Any] | None = None
    ) -> None:
        super().__init__(message, "AUTH_ERROR", details)


class InvalidCredentialsError(AuthenticationError):
    """Raised when credentials are invalid."""

    def __init__(self, message: str = "Invalid username or password") -> None:
        super().__init__(message, {"reason": "invalid_credentials"})


class TokenExpiredError(AuthenticationError):
    """Raised when a token has expired."""

    def __init__(self, message: str = "Token has expired") -> None:
        super().__init__(message, {"reason": "token_expired"})


class InvalidTokenError(AuthenticationError):
    """Raised when a token is invalid."""

    def __init__(self, message: str = "Invalid token") -> None:
        super().__init__(message, {"reason": "invalid_token"})


class AccountLockedError(AuthenticationError):
    """Raised when an account is locked due to too many failed attempts."""

    def __init__(
        self,
        message: str = "Account is temporarily locked",
        lockout_remaining_minutes: int | None = None,
    ) -> None:
        details = {"reason": "account_locked"}
        if lockout_remaining_minutes:
            details["lockout_remaining_minutes"] = lockout_remaining_minutes
        super().__init__(message, details)


# Authorization Exceptions
class AuthorizationError(RTCCBaseException):
    """Raised when authorization fails."""

    def __init__(
        self,
        message: str = "Access denied",
        required_role: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        error_details = details or {}
        if required_role:
            error_details["required_role"] = required_role
        super().__init__(message, "AUTHZ_ERROR", error_details)


class InsufficientPermissionsError(AuthorizationError):
    """Raised when user lacks required permissions."""

    def __init__(
        self, message: str = "Insufficient permissions", required_role: str | None = None
    ) -> None:
        super().__init__(message, required_role, {"reason": "insufficient_permissions"})


# Database Exceptions
class DatabaseError(RTCCBaseException):
    """Base exception for database errors."""

    def __init__(
        self, message: str = "Database error occurred", details: dict[str, Any] | None = None
    ) -> None:
        super().__init__(message, "DB_ERROR", details)


class Neo4jConnectionError(DatabaseError):
    """Raised when Neo4j connection fails."""

    def __init__(self, message: str = "Failed to connect to Neo4j database") -> None:
        super().__init__(message, {"database": "neo4j"})


class ElasticsearchConnectionError(DatabaseError):
    """Raised when Elasticsearch connection fails."""

    def __init__(self, message: str = "Failed to connect to Elasticsearch") -> None:
        super().__init__(message, {"database": "elasticsearch"})


class RedisConnectionError(DatabaseError):
    """Raised when Redis connection fails."""

    def __init__(self, message: str = "Failed to connect to Redis") -> None:
        super().__init__(message, {"database": "redis"})


class EntityNotFoundError(DatabaseError):
    """Raised when a requested entity is not found."""

    def __init__(self, entity_type: str, entity_id: str, message: str | None = None) -> None:
        msg = message or f"{entity_type} with ID '{entity_id}' not found"
        super().__init__(msg, {"entity_type": entity_type, "entity_id": entity_id})


class DuplicateEntityError(DatabaseError):
    """Raised when attempting to create a duplicate entity."""

    def __init__(self, entity_type: str, identifier: str, message: str | None = None) -> None:
        msg = message or f"{entity_type} with identifier '{identifier}' already exists"
        super().__init__(msg, {"entity_type": entity_type, "identifier": identifier})


# Validation Exceptions
class ValidationError(RTCCBaseException):
    """Raised when validation fails."""

    def __init__(
        self,
        message: str = "Validation error",
        field: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        error_details = details or {}
        if field:
            error_details["field"] = field
        super().__init__(message, "VALIDATION_ERROR", error_details)


class InvalidInputError(ValidationError):
    """Raised when input data is invalid."""

    def __init__(self, message: str = "Invalid input data", field: str | None = None) -> None:
        super().__init__(message, field, {"reason": "invalid_input"})


# Integration Exceptions
class IntegrationError(RTCCBaseException):
    """Base exception for external integration errors."""

    def __init__(
        self,
        message: str = "Integration error occurred",
        integration_name: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        error_details = details or {}
        if integration_name:
            error_details["integration"] = integration_name
        super().__init__(message, "INTEGRATION_ERROR", error_details)


class IntegrationConnectionError(IntegrationError):
    """Raised when connection to external system fails."""

    def __init__(self, integration_name: str, message: str | None = None) -> None:
        msg = message or f"Failed to connect to {integration_name}"
        super().__init__(msg, integration_name, {"reason": "connection_failed"})


class IntegrationAuthenticationError(IntegrationError):
    """Raised when authentication with external system fails."""

    def __init__(self, integration_name: str, message: str | None = None) -> None:
        msg = message or f"Authentication failed for {integration_name}"
        super().__init__(msg, integration_name, {"reason": "authentication_failed"})


# WebSocket Exceptions
class WebSocketError(RTCCBaseException):
    """Base exception for WebSocket errors."""

    def __init__(
        self, message: str = "WebSocket error occurred", details: dict[str, Any] | None = None
    ) -> None:
        super().__init__(message, "WS_ERROR", details)


class WebSocketConnectionError(WebSocketError):
    """Raised when WebSocket connection fails."""

    def __init__(self, message: str = "WebSocket connection failed") -> None:
        super().__init__(message, {"reason": "connection_failed"})


class WebSocketAuthenticationError(WebSocketError):
    """Raised when WebSocket authentication fails."""

    def __init__(self, message: str = "WebSocket authentication failed") -> None:
        super().__init__(message, {"reason": "authentication_failed"})


# Rate Limiting Exceptions
class RateLimitExceededError(RTCCBaseException):
    """Raised when rate limit is exceeded."""

    def __init__(
        self, message: str = "Rate limit exceeded", retry_after_seconds: int | None = None
    ) -> None:
        details = {"reason": "rate_limit_exceeded"}
        if retry_after_seconds:
            details["retry_after_seconds"] = retry_after_seconds
        super().__init__(message, "RATE_LIMIT_ERROR", details)
