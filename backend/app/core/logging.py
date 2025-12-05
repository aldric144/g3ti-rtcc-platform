"""
Structured logging infrastructure for the G3TI RTCC-UIP Backend.

This module provides a comprehensive logging system using structlog for
structured logging with JSON output, suitable for log aggregation and
analysis in production environments.

CJIS Compliance Note:
- All security-relevant events must be logged
- Logs must include timestamp, user identity, and action details
- Sensitive data (passwords, tokens) must never be logged
- Log integrity must be maintained
"""

import logging
import sys
from datetime import UTC, datetime
from typing import Any

import structlog
from structlog.types import EventDict, Processor


def add_timestamp(logger: logging.Logger, method_name: str, event_dict: EventDict) -> EventDict:
    """
    Add ISO 8601 timestamp to log events.

    Args:
        logger: The logger instance
        method_name: The logging method name
        event_dict: The event dictionary

    Returns:
        EventDict: Updated event dictionary with timestamp
    """
    event_dict["timestamp"] = datetime.now(UTC).isoformat()
    return event_dict


def add_service_context(
    logger: logging.Logger, method_name: str, event_dict: EventDict
) -> EventDict:
    """
    Add service context information to log events.

    Args:
        logger: The logger instance
        method_name: The logging method name
        event_dict: The event dictionary

    Returns:
        EventDict: Updated event dictionary with service context
    """
    event_dict["service"] = "g3ti-rtcc-backend"
    event_dict["version"] = "1.0.0"
    return event_dict


def sanitize_sensitive_data(
    logger: logging.Logger, method_name: str, event_dict: EventDict
) -> EventDict:
    """
    Remove or mask sensitive data from log events.

    This processor ensures CJIS compliance by preventing sensitive
    information from being logged.

    Args:
        logger: The logger instance
        method_name: The logging method name
        event_dict: The event dictionary

    Returns:
        EventDict: Sanitized event dictionary
    """
    sensitive_keys = {
        "password",
        "token",
        "secret",
        "api_key",
        "authorization",
        "credit_card",
        "ssn",
        "social_security",
        "bearer",
    }

    def mask_value(key: str, value: Any) -> Any:
        """Mask sensitive values."""
        key_lower = key.lower()
        for sensitive in sensitive_keys:
            if sensitive in key_lower:
                if isinstance(value, str) and len(value) > 4:
                    return f"***{value[-4:]}"
                return "***REDACTED***"
        return value

    def sanitize_dict(d: dict[str, Any]) -> dict[str, Any]:
        """Recursively sanitize dictionary."""
        result = {}
        for key, value in d.items():
            if isinstance(value, dict):
                result[key] = sanitize_dict(value)
            else:
                result[key] = mask_value(key, value)
        return result

    return sanitize_dict(event_dict)


def setup_logging(
    log_level: str = "INFO", json_logs: bool = True, log_file: str | None = None
) -> None:
    """
    Configure the logging system for the application.

    Sets up structlog with appropriate processors for development or
    production environments.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_logs: Whether to output logs as JSON (recommended for production)
        log_file: Optional file path for log output
    """
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper()),
    )

    # Define processors for structlog
    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        add_timestamp,
        add_service_context,
        sanitize_sensitive_data,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
    ]

    if json_logs:
        # Production: JSON output for log aggregation
        shared_processors.append(structlog.processors.JSONRenderer())
    else:
        # Development: Human-readable colored output
        shared_processors.append(structlog.dev.ConsoleRenderer(colors=True))

    structlog.configure(
        processors=shared_processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """
    Get a configured logger instance.

    Args:
        name: Optional logger name (defaults to calling module)

    Returns:
        BoundLogger: Configured structlog logger instance
    """
    return structlog.get_logger(name)


class AuditLogger:
    """
    Specialized logger for CJIS-compliant audit logging.

    This logger ensures all security-relevant events are captured with
    the required metadata for compliance and forensic analysis.
    """

    def __init__(self) -> None:
        """Initialize the audit logger."""
        self._logger = get_logger("audit")

    def log_authentication(
        self,
        user_id: str | None,
        username: str,
        success: bool,
        ip_address: str,
        user_agent: str | None = None,
        failure_reason: str | None = None,
    ) -> None:
        """
        Log authentication attempt.

        Args:
            user_id: User ID if known
            username: Username attempted
            success: Whether authentication succeeded
            ip_address: Client IP address
            user_agent: Client user agent string
            failure_reason: Reason for failure if applicable
        """
        self._logger.info(
            "authentication_attempt",
            event_type="authentication",
            user_id=user_id,
            username=username,
            success=success,
            ip_address=ip_address,
            user_agent=user_agent,
            failure_reason=failure_reason,
        )

    def log_authorization(
        self,
        user_id: str,
        resource: str,
        action: str,
        allowed: bool,
        required_role: str | None = None,
    ) -> None:
        """
        Log authorization decision.

        Args:
            user_id: User ID
            resource: Resource being accessed
            action: Action being performed
            allowed: Whether access was allowed
            required_role: Role required for access
        """
        self._logger.info(
            "authorization_decision",
            event_type="authorization",
            user_id=user_id,
            resource=resource,
            action=action,
            allowed=allowed,
            required_role=required_role,
        )

    def log_data_access(
        self,
        user_id: str,
        entity_type: str,
        entity_id: str,
        action: str,
        fields_accessed: list[str] | None = None,
    ) -> None:
        """
        Log data access event.

        Args:
            user_id: User ID
            entity_type: Type of entity accessed
            entity_id: ID of entity accessed
            action: Action performed (read, create, update, delete)
            fields_accessed: List of fields accessed
        """
        self._logger.info(
            "data_access",
            event_type="data_access",
            user_id=user_id,
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            fields_accessed=fields_accessed,
        )

    def log_system_event(
        self, event_name: str, details: dict[str, Any] | None = None, severity: str = "info"
    ) -> None:
        """
        Log system event.

        Args:
            event_name: Name of the system event
            details: Additional event details
            severity: Event severity level
        """
        log_method = getattr(self._logger, severity, self._logger.info)
        log_method(
            event_name,
            event_type="system",
            details=details or {},
        )


# Global audit logger instance
audit_logger = AuditLogger()
