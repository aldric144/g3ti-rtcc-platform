"""
Shift Model - RTCC Shift Management Data Structures

Defines the data models for shift management and supervisor tools.
"""

from datetime import datetime, UTC
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field
import uuid


class OperatorRole(str, Enum):
    """Roles for RTCC operators."""
    OPERATOR = "operator"
    SUPERVISOR = "supervisor"
    ANALYST = "analyst"


class ShiftOperator(BaseModel):
    """Model for an operator assigned to a shift."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str
    name: str
    role: OperatorRole
    assigned_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    notes: Optional[str] = None


class MajorEvent(BaseModel):
    """Model for major events during a shift."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str  # e.g., "10-33", "Priority 1 Assist", "Officer Down"
    description: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    recorded_by: str
    case_number: Optional[str] = None
    units_involved: List[str] = Field(default_factory=list)


class ShiftBase(BaseModel):
    """Base model for shift data."""
    notes: Optional[str] = None


class ShiftCreate(ShiftBase):
    """Model for opening a new shift."""
    supervisor: str


class ShiftClose(BaseModel):
    """Model for closing a shift."""
    closing_notes: Optional[str] = None
    supervisor_signoff: str


class Shift(ShiftBase):
    """Complete shift record with metadata."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    start_time: datetime = Field(default_factory=lambda: datetime.now(UTC))
    end_time: Optional[datetime] = None
    supervisor: str
    operators: List[ShiftOperator] = Field(default_factory=list)
    major_events: List[MajorEvent] = Field(default_factory=list)
    is_active: bool = True
    closing_notes: Optional[str] = None
    supervisor_signoff: Optional[str] = None
    
    class Config:
        from_attributes = True


class AddOperatorRequest(BaseModel):
    """Request to add an operator to a shift."""
    username: str
    name: str
    role: OperatorRole
    notes: Optional[str] = None


class RecordMajorEventRequest(BaseModel):
    """Request to record a major event."""
    event_type: str
    description: str
    case_number: Optional[str] = None
    units_involved: List[str] = Field(default_factory=list)


class ShiftSummary(BaseModel):
    """Summary of a shift for history view."""
    id: str
    start_time: datetime
    end_time: Optional[datetime]
    supervisor: str
    operator_count: int
    major_event_count: int
    is_active: bool
