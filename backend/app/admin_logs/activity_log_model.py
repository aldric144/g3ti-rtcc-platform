"""
Activity Log Model - RTCC Logbook Data Structures

Defines the data models for the Daily Activity Log System.
"""

from datetime import datetime, UTC
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field
import uuid


class LogType(str, Enum):
    """Types of activity log entries."""
    INCIDENT = "incident"
    SHOTSPOTTER = "shotspotter"
    LPR = "lpr"
    CAMERA_ALERT = "camera_alert"
    CAD_ASSIST = "cad_assist"
    PATROL_REQUEST = "patrol_request"
    CASE_SUPPORT = "case_support"
    SUPERVISOR_NOTICE = "supervisor_notice"


class LogPriority(str, Enum):
    """Priority levels for log entries."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ActivityLogBase(BaseModel):
    """Base model for activity log entries."""
    log_type: LogType
    priority: LogPriority = LogPriority.MEDIUM
    notes: str = Field(..., min_length=1, max_length=5000)
    tags: List[str] = Field(default_factory=list)


class ActivityLogCreate(ActivityLogBase):
    """Model for creating a new activity log entry."""
    pass


class ActivityLogUpdate(BaseModel):
    """Model for updating an existing activity log entry."""
    log_type: Optional[LogType] = None
    priority: Optional[LogPriority] = None
    notes: Optional[str] = Field(None, min_length=1, max_length=5000)
    tags: Optional[List[str]] = None


class ActivityLog(ActivityLogBase):
    """Complete activity log entry with metadata."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    editor: str = Field(..., description="Username of the editor")
    archived: bool = False
    
    class Config:
        from_attributes = True


class ActivityLogSearchParams(BaseModel):
    """Parameters for searching activity logs."""
    keyword: Optional[str] = None
    log_type: Optional[LogType] = None
    priority: Optional[LogPriority] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    editor: Optional[str] = None
    include_archived: bool = False
    limit: int = Field(default=50, ge=1, le=500)
    offset: int = Field(default=0, ge=0)


class ActivityLogExportFormat(str, Enum):
    """Export formats for activity logs."""
    JSON = "json"
    CSV = "csv"
