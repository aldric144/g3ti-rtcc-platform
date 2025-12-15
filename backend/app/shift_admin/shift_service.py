"""
Shift Service - Business Logic for RTCC Shift Management

Provides shift lifecycle management and supervisor tools.
"""

from datetime import datetime, UTC
from typing import List, Optional, Dict
import structlog

from .shift_model import (
    Shift,
    ShiftCreate,
    ShiftClose,
    ShiftOperator,
    MajorEvent,
    AddOperatorRequest,
    RecordMajorEventRequest,
    ShiftSummary,
    OperatorRole,
)

logger = structlog.get_logger(__name__)


class ShiftService:
    """Service for managing RTCC shifts."""
    
    def __init__(self):
        # In-memory storage for SAFE_MODE operation
        self._shifts: Dict[str, Shift] = {}
        self._current_shift_id: Optional[str] = None
    
    async def open_shift(self, data: ShiftCreate) -> Shift:
        """Open a new shift."""
        # Close any existing active shift
        if self._current_shift_id:
            current = self._shifts.get(self._current_shift_id)
            if current and current.is_active:
                logger.warning("auto_closing_previous_shift", shift_id=self._current_shift_id)
                current.is_active = False
                current.end_time = datetime.now(UTC)
                current.closing_notes = "Auto-closed due to new shift opening"
        
        shift = Shift(
            supervisor=data.supervisor,
            notes=data.notes,
        )
        
        self._shifts[shift.id] = shift
        self._current_shift_id = shift.id
        
        logger.info("shift_opened", shift_id=shift.id, supervisor=data.supervisor)
        return shift
    
    async def close_shift(self, data: ShiftClose) -> Optional[Shift]:
        """Close the current active shift."""
        if not self._current_shift_id:
            return None
        
        shift = self._shifts.get(self._current_shift_id)
        if not shift or not shift.is_active:
            return None
        
        shift.is_active = False
        shift.end_time = datetime.now(UTC)
        shift.closing_notes = data.closing_notes
        shift.supervisor_signoff = data.supervisor_signoff
        
        self._shifts[shift.id] = shift
        self._current_shift_id = None
        
        logger.info("shift_closed", shift_id=shift.id, supervisor_signoff=data.supervisor_signoff)
        return shift
    
    async def get_current_shift(self) -> Optional[Shift]:
        """Get the current active shift."""
        if not self._current_shift_id:
            return None
        return self._shifts.get(self._current_shift_id)
    
    async def get_shift(self, shift_id: str) -> Optional[Shift]:
        """Get a specific shift by ID."""
        return self._shifts.get(shift_id)
    
    async def add_operator(self, request: AddOperatorRequest, added_by: str) -> Optional[Shift]:
        """Add an operator to the current shift."""
        if not self._current_shift_id:
            return None
        
        shift = self._shifts.get(self._current_shift_id)
        if not shift or not shift.is_active:
            return None
        
        operator = ShiftOperator(
            username=request.username,
            name=request.name,
            role=request.role,
            notes=request.notes,
        )
        
        shift.operators.append(operator)
        self._shifts[shift.id] = shift
        
        logger.info("operator_added", shift_id=shift.id, operator=request.username, added_by=added_by)
        return shift
    
    async def remove_operator(self, operator_id: str, removed_by: str) -> Optional[Shift]:
        """Remove an operator from the current shift."""
        if not self._current_shift_id:
            return None
        
        shift = self._shifts.get(self._current_shift_id)
        if not shift or not shift.is_active:
            return None
        
        shift.operators = [op for op in shift.operators if op.id != operator_id]
        self._shifts[shift.id] = shift
        
        logger.info("operator_removed", shift_id=shift.id, operator_id=operator_id, removed_by=removed_by)
        return shift
    
    async def record_major_event(self, request: RecordMajorEventRequest, recorded_by: str) -> Optional[Shift]:
        """Record a major event during the current shift."""
        if not self._current_shift_id:
            return None
        
        shift = self._shifts.get(self._current_shift_id)
        if not shift or not shift.is_active:
            return None
        
        event = MajorEvent(
            event_type=request.event_type,
            description=request.description,
            recorded_by=recorded_by,
            case_number=request.case_number,
            units_involved=request.units_involved,
        )
        
        shift.major_events.append(event)
        self._shifts[shift.id] = shift
        
        logger.info("major_event_recorded", shift_id=shift.id, event_type=request.event_type, recorded_by=recorded_by)
        return shift
    
    async def get_shift_history(self, limit: int = 50) -> List[ShiftSummary]:
        """Get shift history summaries."""
        shifts = list(self._shifts.values())
        shifts.sort(key=lambda x: x.start_time, reverse=True)
        
        summaries = []
        for shift in shifts[:limit]:
            summaries.append(ShiftSummary(
                id=shift.id,
                start_time=shift.start_time,
                end_time=shift.end_time,
                supervisor=shift.supervisor,
                operator_count=len(shift.operators),
                major_event_count=len(shift.major_events),
                is_active=shift.is_active,
            ))
        
        return summaries


# Singleton instance for SAFE_MODE operation
_shift_service: Optional[ShiftService] = None


def get_shift_service() -> ShiftService:
    """Get the shift service instance."""
    global _shift_service
    if _shift_service is None:
        _shift_service = ShiftService()
    return _shift_service
