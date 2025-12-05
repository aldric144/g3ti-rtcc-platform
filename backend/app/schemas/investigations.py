"""
Investigation schemas for the G3TI RTCC-UIP Backend.

This module defines schemas for investigation management, case tracking,
and investigative search functionality.

Investigations are the primary organizational unit for linking entities,
evidence, and events related to a specific case or inquiry.
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import Field

from app.schemas.common import GeoLocation, RTCCBaseModel, TimestampMixin


class InvestigationStatus(str, Enum):
    """Investigation status values."""

    OPEN = "open"
    ACTIVE = "active"
    PENDING = "pending"
    SUSPENDED = "suspended"
    CLOSED_CLEARED = "closed_cleared"
    CLOSED_UNFOUNDED = "closed_unfounded"
    CLOSED_EXCEPTIONALLY = "closed_exceptionally"
    COLD_CASE = "cold_case"


class InvestigationPriority(str, Enum):
    """Investigation priority levels."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class InvestigationType(str, Enum):
    """Types of investigations."""

    CRIMINAL = "criminal"
    INTELLIGENCE = "intelligence"
    SURVEILLANCE = "surveillance"
    BACKGROUND = "background"
    INTERNAL = "internal"
    TASK_FORCE = "task_force"


class InvestigationBase(RTCCBaseModel):
    """Base schema for Investigation entity."""

    case_number: str = Field(max_length=50, description="Case/investigation number")
    title: str = Field(max_length=200, description="Investigation title")
    investigation_type: InvestigationType = Field(
        default=InvestigationType.CRIMINAL, description="Type of investigation"
    )
    status: InvestigationStatus = Field(
        default=InvestigationStatus.OPEN, description="Investigation status"
    )
    priority: InvestigationPriority = Field(
        default=InvestigationPriority.MEDIUM, description="Investigation priority"
    )
    narrative: str | None = Field(
        default=None, max_length=50000, description="Investigation narrative/summary"
    )
    synopsis: str | None = Field(default=None, max_length=2000, description="Brief synopsis")
    assigned_to: str | None = Field(
        default=None, description="Primary assigned investigator user ID"
    )
    assigned_unit: str | None = Field(
        default=None, max_length=100, description="Assigned unit/division"
    )
    secondary_investigators: list[str] = Field(
        default_factory=list, description="Secondary investigator user IDs"
    )
    opened_date: datetime = Field(description="Date investigation was opened")
    closed_date: datetime | None = Field(default=None, description="Date investigation was closed")
    due_date: datetime | None = Field(default=None, description="Due date for investigation")
    location: GeoLocation | None = Field(default=None, description="Primary investigation location")
    jurisdiction: str | None = Field(default=None, max_length=100, description="Jurisdiction")
    tags: list[str] = Field(default_factory=list, description="Investigation tags")
    is_confidential: bool = Field(default=False, description="Confidential investigation flag")


class InvestigationCreate(InvestigationBase):
    """Schema for creating an Investigation."""

    linked_incident_ids: list[str] = Field(
        default_factory=list, description="IDs of linked incidents"
    )
    linked_person_ids: list[str] = Field(default_factory=list, description="IDs of linked persons")
    linked_vehicle_ids: list[str] = Field(
        default_factory=list, description="IDs of linked vehicles"
    )


class InvestigationUpdate(RTCCBaseModel):
    """Schema for updating an Investigation."""

    title: str | None = Field(default=None, max_length=200)
    investigation_type: InvestigationType | None = None
    status: InvestigationStatus | None = None
    priority: InvestigationPriority | None = None
    narrative: str | None = None
    synopsis: str | None = None
    assigned_to: str | None = None
    assigned_unit: str | None = None
    secondary_investigators: list[str] | None = None
    closed_date: datetime | None = None
    due_date: datetime | None = None
    location: GeoLocation | None = None
    jurisdiction: str | None = None
    tags: list[str] | None = None
    is_confidential: bool | None = None


class InvestigationResponse(InvestigationBase, TimestampMixin):
    """Schema for Investigation response."""

    id: str = Field(description="Unique investigation identifier")
    assigned_to_name: str | None = Field(default=None, description="Assigned investigator name")
    incident_count: int = Field(default=0, description="Number of linked incidents")
    person_count: int = Field(default=0, description="Number of linked persons")
    vehicle_count: int = Field(default=0, description="Number of linked vehicles")
    evidence_count: int = Field(default=0, description="Number of evidence items")
    note_count: int = Field(default=0, description="Number of case notes")
    days_open: int = Field(default=0, description="Days since investigation opened")


class InvestigationNote(RTCCBaseModel):
    """Schema for investigation notes."""

    id: str = Field(description="Note identifier")
    investigation_id: str = Field(description="Parent investigation ID")
    content: str = Field(max_length=10000, description="Note content")
    note_type: str = Field(
        default="general", max_length=50, description="Note type (general, lead, interview, etc.)"
    )
    created_by: str = Field(description="User ID who created the note")
    created_by_name: str | None = Field(default=None, description="Creator name")
    created_at: datetime = Field(description="Creation timestamp")
    is_private: bool = Field(default=False, description="Private note flag")


class InvestigationTimeline(RTCCBaseModel):
    """Schema for investigation timeline entry."""

    id: str = Field(description="Timeline entry identifier")
    investigation_id: str = Field(description="Parent investigation ID")
    timestamp: datetime = Field(description="Event timestamp")
    event_type: str = Field(description="Type of timeline event")
    title: str = Field(max_length=200, description="Event title")
    description: str | None = Field(default=None, max_length=2000)
    user_id: str | None = Field(default=None, description="Associated user ID")
    entity_type: str | None = Field(default=None, description="Associated entity type")
    entity_id: str | None = Field(default=None, description="Associated entity ID")


# Search Schemas


class SearchQuery(RTCCBaseModel):
    """Schema for investigative search query."""

    query: str = Field(min_length=1, max_length=500, description="Search query string")
    entity_types: list[str] = Field(
        default_factory=list, description="Entity types to search (empty = all)"
    )
    date_from: datetime | None = Field(default=None, description="Start date filter")
    date_to: datetime | None = Field(default=None, description="End date filter")
    location: GeoLocation | None = Field(default=None, description="Center point for geo search")
    radius_miles: float | None = Field(
        default=None, ge=0, le=100, description="Search radius in miles"
    )
    filters: dict[str, Any] = Field(default_factory=dict, description="Additional filters")
    include_related: bool = Field(default=False, description="Include related entities in results")
    page: int = Field(default=1, ge=1, description="Page number")
    page_size: int = Field(default=20, ge=1, le=100, description="Results per page")


class SearchResultItem(RTCCBaseModel):
    """Schema for a single search result item."""

    id: str = Field(description="Entity identifier")
    entity_type: str = Field(description="Entity type")
    title: str = Field(description="Result title/name")
    description: str | None = Field(default=None, description="Result description")
    score: float = Field(description="Relevance score")
    highlights: dict[str, list[str]] = Field(
        default_factory=dict, description="Highlighted matching text"
    )
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    location: GeoLocation | None = Field(default=None, description="Entity location")
    timestamp: datetime | None = Field(default=None, description="Relevant timestamp")


class SearchResult(RTCCBaseModel):
    """Schema for search results."""

    query: str = Field(description="Original search query")
    total: int = Field(description="Total matching results")
    page: int = Field(description="Current page")
    page_size: int = Field(description="Results per page")
    pages: int = Field(description="Total pages")
    items: list[SearchResultItem] = Field(description="Search result items")
    facets: dict[str, dict[str, int]] = Field(
        default_factory=dict, description="Faceted counts by field"
    )
    suggestions: list[str] = Field(default_factory=list, description="Search suggestions")
    took_ms: int = Field(description="Search execution time in milliseconds")


class SavedSearch(RTCCBaseModel):
    """Schema for saved search configuration."""

    id: str = Field(description="Saved search identifier")
    name: str = Field(max_length=100, description="Search name")
    description: str | None = Field(default=None, max_length=500)
    query: SearchQuery = Field(description="Search query configuration")
    user_id: str = Field(description="Owner user ID")
    is_shared: bool = Field(default=False, description="Shared with team flag")
    alert_enabled: bool = Field(default=False, description="Enable alerts for new matches")
    created_at: datetime = Field(description="Creation timestamp")
    last_run_at: datetime | None = Field(default=None, description="Last execution timestamp")


class SearchAlert(RTCCBaseModel):
    """Schema for search alert notification."""

    id: str = Field(description="Alert identifier")
    saved_search_id: str = Field(description="Associated saved search ID")
    saved_search_name: str = Field(description="Saved search name")
    new_results_count: int = Field(description="Number of new results")
    sample_results: list[SearchResultItem] = Field(description="Sample of new results")
    triggered_at: datetime = Field(description="Alert trigger timestamp")
