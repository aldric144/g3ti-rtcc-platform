"""
Common schemas shared across the G3TI RTCC-UIP Backend.

This module contains base schemas and utility types used throughout
the application for consistent API responses.
"""

from datetime import datetime
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

# Generic type for paginated responses
T = TypeVar("T")


class RTCCBaseModel(BaseModel):
    """
    Base model for all RTCC-UIP schemas.

    Provides common configuration and utilities for all Pydantic models.
    """

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        str_strip_whitespace=True,
        validate_assignment=True,
    )


class TimestampMixin(BaseModel):
    """Mixin for models with timestamp fields."""

    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="Timestamp when the record was created"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow, description="Timestamp when the record was last updated"
    )


class PaginatedResponse(RTCCBaseModel, Generic[T]):
    """
    Generic paginated response wrapper.

    Used for all list endpoints that support pagination.
    """

    items: list[T] = Field(description="List of items in the current page")
    total: int = Field(description="Total number of items across all pages")
    page: int = Field(ge=1, description="Current page number (1-indexed)")
    page_size: int = Field(ge=1, le=100, description="Number of items per page")
    pages: int = Field(ge=0, description="Total number of pages")

    @property
    def has_next(self) -> bool:
        """Check if there is a next page."""
        return self.page < self.pages

    @property
    def has_prev(self) -> bool:
        """Check if there is a previous page."""
        return self.page > 1


class HealthCheck(RTCCBaseModel):
    """
    Health check response schema.

    Used by the /health endpoint to report system status.
    """

    status: str = Field(description="Overall system status (healthy, degraded, unhealthy)")
    version: str = Field(description="Application version")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Health check timestamp"
    )
    components: dict[str, dict[str, Any]] = Field(
        default_factory=dict, description="Status of individual components"
    )


class ErrorResponse(RTCCBaseModel):
    """
    Standard error response schema.

    Used for all API error responses to ensure consistent error format.
    """

    error_code: str = Field(description="Machine-readable error code")
    message: str = Field(description="Human-readable error message")
    details: dict[str, Any] = Field(default_factory=dict, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")
    request_id: str | None = Field(default=None, description="Request ID for tracing")


class GeoLocation(RTCCBaseModel):
    """Geographic location schema."""

    latitude: float = Field(ge=-90, le=90, description="Latitude coordinate")
    longitude: float = Field(ge=-180, le=180, description="Longitude coordinate")
    accuracy: float | None = Field(default=None, ge=0, description="Location accuracy in meters")
    altitude: float | None = Field(default=None, description="Altitude in meters")


class AuditInfo(RTCCBaseModel):
    """Audit information for CJIS compliance."""

    created_by: str = Field(description="User ID who created the record")
    created_at: datetime = Field(description="Creation timestamp")
    updated_by: str | None = Field(default=None, description="User ID who last updated")
    updated_at: datetime | None = Field(default=None, description="Last update timestamp")
    accessed_by: list[str] = Field(
        default_factory=list, description="List of user IDs who accessed this record"
    )
    access_count: int = Field(default=0, description="Number of times accessed")


class BulkOperationResult(RTCCBaseModel):
    """Result of a bulk operation."""

    total: int = Field(description="Total items processed")
    successful: int = Field(description="Number of successful operations")
    failed: int = Field(description="Number of failed operations")
    errors: list[dict[str, Any]] = Field(
        default_factory=list, description="Details of failed operations"
    )


class SortOrder(RTCCBaseModel):
    """Sort order specification."""

    field: str = Field(description="Field to sort by")
    direction: str = Field(
        default="asc", pattern="^(asc|desc)$", description="Sort direction (asc or desc)"
    )


class FilterCondition(RTCCBaseModel):
    """Filter condition for queries."""

    field: str = Field(description="Field to filter on")
    operator: str = Field(description="Filter operator (eq, ne, gt, lt, gte, lte, contains, in)")
    value: Any = Field(description="Filter value")


class QueryParams(RTCCBaseModel):
    """Common query parameters for list endpoints."""

    page: int = Field(default=1, ge=1, description="Page number")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page")
    sort: list[SortOrder] = Field(default_factory=list, description="Sort orders")
    filters: list[FilterCondition] = Field(default_factory=list, description="Filter conditions")
    search: str | None = Field(default=None, description="Full-text search query")
