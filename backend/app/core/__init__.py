"""
Core module for the G3TI RTCC-UIP Backend.

This module contains foundational components including:
- Configuration management and environment variable loading
- Security utilities and cryptographic functions
- Logging infrastructure with structured logging
- Exception handling and error definitions
- Database connection managers
"""

from app.core.config import settings
from app.core.logging import get_logger, setup_logging
from app.core.security import SecurityManager

__all__ = ["settings", "get_logger", "setup_logging", "SecurityManager"]
