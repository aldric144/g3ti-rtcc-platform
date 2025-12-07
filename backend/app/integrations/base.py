"""
Base integration class for the G3TI RTCC-UIP Backend.

This module provides the abstract base class for all external
system integrations with common functionality for:
- Connection management
- Authentication
- Error handling
- Event normalization
- Audit logging
"""

from abc import ABC, abstractmethod
from datetime import UTC, datetime
from enum import Enum
from typing import Any, Generic, TypeVar

import httpx

from app.core.config import settings
from app.core.exceptions import (
    IntegrationAuthenticationError,
    IntegrationConnectionError,
    IntegrationError,
)
from app.core.logging import audit_logger, get_logger
from app.schemas.events import EventSource

logger = get_logger(__name__)

T = TypeVar("T")


class IntegrationStatus(str, Enum):
    """Integration connection status."""

    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    ERROR = "error"
    DISABLED = "disabled"


class BaseIntegration(ABC, Generic[T]):
    """
    Abstract base class for external system integrations.

    Provides common functionality for all integrations including
    HTTP client management, authentication, and error handling.

    Subclasses must implement:
    - source: EventSource property
    - connect(): Establish connection
    - disconnect(): Close connection
    - health_check(): Verify connectivity
    - normalize_event(): Convert raw data to standard format
    """

    def __init__(
        self, base_url: str | None = None, api_key: str | None = None, timeout: float = 30.0
    ) -> None:
        """
        Initialize the integration.

        Args:
            base_url: API base URL
            api_key: API key for authentication
            timeout: Request timeout in seconds
        """
        self._base_url = base_url
        self._api_key = api_key
        self._timeout = timeout
        self._client: httpx.AsyncClient | None = None
        self._status = IntegrationStatus.DISCONNECTED
        self._last_error: str | None = None
        self._connected_at: datetime | None = None
        self._request_count = 0
        self._error_count = 0

    @property
    @abstractmethod
    def source(self) -> EventSource:
        """Get the event source for this integration."""
        pass

    @property
    def name(self) -> str:
        """Get the integration name."""
        return self.source.value

    @property
    def status(self) -> IntegrationStatus:
        """Get the current connection status."""
        return self._status

    @property
    def is_connected(self) -> bool:
        """Check if integration is connected."""
        return self._status == IntegrationStatus.CONNECTED

    @property
    def is_configured(self) -> bool:
        """Check if integration is configured."""
        return self._base_url is not None

    async def connect(self) -> bool:
        """
        Establish connection to the external system.

        Returns:
            bool: True if connected successfully

        Raises:
            IntegrationConnectionError: If connection fails
        """
        if not self.is_configured:
            self._status = IntegrationStatus.DISABLED
            logger.info(f"{self.name}_integration_disabled", reason="not_configured")
            return False

        self._status = IntegrationStatus.CONNECTING

        try:
            # Create HTTP client
            headers = self._get_auth_headers()
            self._client = httpx.AsyncClient(
                base_url=self._base_url, headers=headers, timeout=self._timeout
            )

            # Verify connection
            if await self.health_check():
                self._status = IntegrationStatus.CONNECTED
                self._connected_at = datetime.now(UTC)
                self._last_error = None

                logger.info(f"{self.name}_connected", base_url=self._base_url)

                audit_logger.log_system_event(
                    event_type="integration_connected", details={"integration": self.name}
                )

                return True
            else:
                raise IntegrationConnectionError(self.name, "Health check failed")

        except Exception as e:
            self._status = IntegrationStatus.ERROR
            self._last_error = str(e)
            self._error_count += 1

            logger.error(f"{self.name}_connection_failed", error=str(e))

            if self._client:
                await self._client.aclose()
                self._client = None

            raise IntegrationConnectionError(self.name, str(e)) from e

    async def disconnect(self) -> None:
        """Close connection to the external system."""
        if self._client:
            await self._client.aclose()
            self._client = None

        self._status = IntegrationStatus.DISCONNECTED

        logger.info(f"{self.name}_disconnected")

    @abstractmethod
    async def health_check(self) -> bool:
        """
        Verify connectivity to the external system.

        Returns:
            bool: True if system is reachable and responding
        """
        pass

    @abstractmethod
    async def normalize_event(self, raw_data: dict[str, Any]) -> T:
        """
        Normalize raw event data to standard format.

        Args:
            raw_data: Raw event data from external system

        Returns:
            Normalized event data
        """
        pass

    async def _request(self, method: str, endpoint: str, **kwargs: Any) -> dict[str, Any]:
        """
        Make an HTTP request to the external system.

        Args:
            method: HTTP method
            endpoint: API endpoint
            **kwargs: Additional request arguments

        Returns:
            dict: Response data

        Raises:
            IntegrationError: If request fails
        """
        if not self._client:
            raise IntegrationError(self.name, "Not connected")

        self._request_count += 1

        try:
            response = await self._client.request(method, endpoint, **kwargs)
            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            self._error_count += 1

            if e.response.status_code == 401:
                raise IntegrationAuthenticationError(self.name) from e

            raise IntegrationError(self.name, f"HTTP {e.response.status_code}: {e.response.text}") from e

        except httpx.RequestError as e:
            self._error_count += 1
            raise IntegrationConnectionError(self.name, str(e)) from e

    async def get(self, endpoint: str, **kwargs: Any) -> dict[str, Any]:
        """Make a GET request."""
        return await self._request("GET", endpoint, **kwargs)

    async def post(
        self, endpoint: str, data: dict[str, Any] | None = None, **kwargs: Any
    ) -> dict[str, Any]:
        """Make a POST request."""
        return await self._request("POST", endpoint, json=data, **kwargs)

    def _get_auth_headers(self) -> dict[str, str]:
        """
        Get authentication headers for requests.

        Override in subclasses for custom authentication.

        Returns:
            dict: Headers with authentication
        """
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": f"G3TI-RTCC/{settings.app_version}",
        }

        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"

        return headers

    def get_stats(self) -> dict[str, Any]:
        """
        Get integration statistics.

        Returns:
            dict: Integration statistics
        """
        return {
            "name": self.name,
            "status": self._status.value,
            "is_configured": self.is_configured,
            "connected_at": self._connected_at.isoformat() if self._connected_at else None,
            "request_count": self._request_count,
            "error_count": self._error_count,
            "last_error": self._last_error,
        }
