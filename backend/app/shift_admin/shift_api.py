"""
Shift API - REST Endpoints for RTCC Shift Management

Provides CJIS-compliant API endpoints for shift management and supervisor tools.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query

from .shift_model import (
    Shift,
    ShiftCreate,
    ShiftClose,
    AddOperatorRequest,
    RecordMajorEventRequest,
    ShiftSummary,
)
from .shift_service import get_shift_service, ShiftService

router = APIRouter(prefix="/api/admin/shift", tags=["Shift Management"])


def get_current_user() -> str:
    """Get the current user from auth context."""
    return "admin"


@router.post("/open", response_model=Shift, status_code=201)
async def open_shift(
    data: ShiftCreate,
    service: ShiftService = Depends(get_shift_service),
):
    """Open a new shift."""
    return await service.open_shift(data)


@router.post("/close", response_model=Shift)
async def close_shift(
    data: ShiftClose,
    service: ShiftService = Depends(get_shift_service),
):
    """Close the current active shift."""
    shift = await service.close_shift(data)
    if not shift:
        raise HTTPException(status_code=404, detail="No active shift to close")
    return shift


@router.get("/current", response_model=Shift)
async def get_current_shift(
    service: ShiftService = Depends(get_shift_service),
):
    """Get the current active shift."""
    shift = await service.get_current_shift()
    if not shift:
        raise HTTPException(status_code=404, detail="No active shift")
    return shift


@router.get("/history", response_model=List[ShiftSummary])
async def get_shift_history(
    limit: int = Query(50, ge=1, le=500, description="Maximum results"),
    service: ShiftService = Depends(get_shift_service),
):
    """Get shift history summaries."""
    return await service.get_shift_history(limit)


@router.get("/{shift_id}", response_model=Shift)
async def get_shift(
    shift_id: str,
    service: ShiftService = Depends(get_shift_service),
):
    """Get a specific shift by ID."""
    shift = await service.get_shift(shift_id)
    if not shift:
        raise HTTPException(status_code=404, detail="Shift not found")
    return shift


@router.post("/add-operator", response_model=Shift)
async def add_operator(
    request: AddOperatorRequest,
    service: ShiftService = Depends(get_shift_service),
    user: str = Depends(get_current_user),
):
    """Add an operator to the current shift."""
    shift = await service.add_operator(request, user)
    if not shift:
        raise HTTPException(status_code=404, detail="No active shift")
    return shift


@router.delete("/operator/{operator_id}", response_model=Shift)
async def remove_operator(
    operator_id: str,
    service: ShiftService = Depends(get_shift_service),
    user: str = Depends(get_current_user),
):
    """Remove an operator from the current shift."""
    shift = await service.remove_operator(operator_id, user)
    if not shift:
        raise HTTPException(status_code=404, detail="No active shift or operator not found")
    return shift


@router.post("/major-event", response_model=Shift)
async def record_major_event(
    request: RecordMajorEventRequest,
    service: ShiftService = Depends(get_shift_service),
    user: str = Depends(get_current_user),
):
    """Record a major event during the current shift."""
    shift = await service.record_major_event(request, user)
    if not shift:
        raise HTTPException(status_code=404, detail="No active shift")
    return shift
