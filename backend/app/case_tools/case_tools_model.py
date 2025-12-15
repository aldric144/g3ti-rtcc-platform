"""
Case Tools Model - Data Structures for Case Management

Defines the data models for case shortcuts and rapid tools.
"""

from datetime import datetime, UTC
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
import uuid


class CasePriority(str, Enum):
    """Priority levels for cases."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class CaseStatus(str, Enum):
    """Status of a case."""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    PENDING_REVIEW = "pending_review"
    CLOSED = "closed"


class FlagType(str, Enum):
    """Types of case flags."""
    RTCC_ASSISTED = "rtcc_assisted"
    INTELLIGENCE_REVIEW = "intelligence_review"
    SUPERVISOR_ATTENTION = "supervisor_attention"
    FOLLOW_UP_REQUIRED = "follow_up_required"
    BOLO_ACTIVE = "bolo_active"


class CaseNoteCreate(BaseModel):
    """Request to create a case note."""
    case_id: Optional[str] = None  # If None, assigns temporary UUID
    content: str = Field(..., min_length=1, max_length=10000)
    is_rtcc_support: bool = False
    tags: List[str] = Field(default_factory=list)


class CaseNote(BaseModel):
    """Model for a case note."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    case_id: str  # Actual case ID or temporary UUID
    content: str
    is_rtcc_support: bool = False
    tags: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    created_by: str
    
    class Config:
        from_attributes = True


class CaseFlagCreate(BaseModel):
    """Request to flag a case."""
    case_id: str
    flag_type: FlagType
    reason: Optional[str] = None


class CaseFlag(BaseModel):
    """Model for a case flag."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    case_id: str
    flag_type: FlagType
    reason: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    created_by: str
    is_active: bool = True
    
    class Config:
        from_attributes = True


class UnitRequestCreate(BaseModel):
    """Request for unit follow-up."""
    case_id: str
    unit_id: Optional[str] = None
    request_type: str  # e.g., "follow_up", "scene_check", "interview"
    priority: CasePriority = CasePriority.MEDIUM
    details: str
    location: Optional[str] = None


class UnitRequest(BaseModel):
    """Model for a unit follow-up request."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    case_id: str
    unit_id: Optional[str] = None
    request_type: str
    priority: CasePriority
    details: str
    location: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    created_by: str
    status: str = "pending"  # pending, assigned, completed, cancelled
    
    class Config:
        from_attributes = True


class CaseShellCreate(BaseModel):
    """Request to create a case shell."""
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    priority: CasePriority = CasePriority.MEDIUM
    incident_type: Optional[str] = None
    location: Optional[str] = None
    initial_notes: Optional[str] = None


class CaseShell(BaseModel):
    """Model for a case shell (placeholder case)."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    case_number: str  # Generated case number
    title: str
    description: Optional[str] = None
    priority: CasePriority
    status: CaseStatus = CaseStatus.OPEN
    incident_type: Optional[str] = None
    location: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    created_by: str
    notes: List[CaseNote] = Field(default_factory=list)
    flags: List[CaseFlag] = Field(default_factory=list)
    
    class Config:
        from_attributes = True


class BOLOZoneCreate(BaseModel):
    """Request to create a BOLO zone."""
    case_id: str
    zone_name: str
    description: str
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)
    radius_meters: float = Field(default=500, ge=100, le=10000)
    alert_types: List[str] = Field(default_factory=lambda: ["lpr", "camera"])
    expires_at: Optional[datetime] = None


class BOLOZone(BaseModel):
    """Model for a BOLO (Be On the Lookout) zone."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    case_id: str
    zone_name: str
    description: str
    lat: float
    lng: float
    radius_meters: float
    alert_types: List[str]
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    created_by: str
    expires_at: Optional[datetime] = None
    is_active: bool = True
    
    class Config:
        from_attributes = True
