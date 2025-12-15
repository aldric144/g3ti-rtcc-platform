"""
Test Suite 2: Shift Lifecycle Tests

Tests for shift open/close, personnel management, and major event recording.
"""

import pytest
from datetime import datetime, UTC

from app.shift_admin.shift_model import (
    Shift,
    ShiftCreate,
    ShiftClose,
    AddOperatorRequest,
    RecordMajorEventRequest,
    OperatorRole,
)
from app.shift_admin.shift_service import ShiftService


@pytest.fixture
def shift_service():
    """Create a fresh shift service for each test."""
    return ShiftService()


@pytest.mark.asyncio
async def test_open_shift(shift_service):
    """Test opening a new shift."""
    data = ShiftCreate(
        supervisor="Sgt. Johnson",
        notes="Day shift starting",
    )
    
    shift = await shift_service.open_shift(data)
    
    assert shift.id is not None
    assert shift.supervisor == "Sgt. Johnson"
    assert shift.is_active is True
    assert shift.notes == "Day shift starting"


@pytest.mark.asyncio
async def test_close_shift(shift_service):
    """Test closing an active shift."""
    # Open a shift first
    open_data = ShiftCreate(supervisor="Sgt. Johnson")
    await shift_service.open_shift(open_data)
    
    # Close the shift
    close_data = ShiftClose(
        closing_notes="Shift ended normally",
        supervisor_signoff="Sgt. Johnson",
    )
    closed_shift = await shift_service.close_shift(close_data)
    
    assert closed_shift is not None
    assert closed_shift.is_active is False
    assert closed_shift.end_time is not None
    assert closed_shift.closing_notes == "Shift ended normally"
    assert closed_shift.supervisor_signoff == "Sgt. Johnson"


@pytest.mark.asyncio
async def test_get_current_shift(shift_service):
    """Test retrieving the current active shift."""
    # Initially no shift
    current = await shift_service.get_current_shift()
    assert current is None
    
    # Open a shift
    data = ShiftCreate(supervisor="Sgt. Johnson")
    opened = await shift_service.open_shift(data)
    
    # Get current shift
    current = await shift_service.get_current_shift()
    assert current is not None
    assert current.id == opened.id


@pytest.mark.asyncio
async def test_add_operator_to_shift(shift_service):
    """Test adding an operator to the current shift."""
    # Open a shift
    data = ShiftCreate(supervisor="Sgt. Johnson")
    await shift_service.open_shift(data)
    
    # Add operator
    operator_data = AddOperatorRequest(
        username="jsmith",
        name="John Smith",
        role=OperatorRole.OPERATOR,
        notes="Assigned to camera monitoring",
    )
    shift = await shift_service.add_operator(operator_data, "admin")
    
    assert shift is not None
    assert len(shift.operators) == 1
    assert shift.operators[0].username == "jsmith"
    assert shift.operators[0].role == OperatorRole.OPERATOR


@pytest.mark.asyncio
async def test_add_multiple_operators(shift_service):
    """Test adding multiple operators to a shift."""
    data = ShiftCreate(supervisor="Sgt. Johnson")
    await shift_service.open_shift(data)
    
    operators = [
        AddOperatorRequest(username="op1", name="Operator 1", role=OperatorRole.OPERATOR),
        AddOperatorRequest(username="op2", name="Operator 2", role=OperatorRole.ANALYST),
        AddOperatorRequest(username="op3", name="Operator 3", role=OperatorRole.SUPERVISOR),
    ]
    
    for op in operators:
        await shift_service.add_operator(op, "admin")
    
    shift = await shift_service.get_current_shift()
    assert len(shift.operators) == 3


@pytest.mark.asyncio
async def test_remove_operator_from_shift(shift_service):
    """Test removing an operator from the current shift."""
    data = ShiftCreate(supervisor="Sgt. Johnson")
    await shift_service.open_shift(data)
    
    # Add operator
    operator_data = AddOperatorRequest(
        username="jsmith",
        name="John Smith",
        role=OperatorRole.OPERATOR,
    )
    shift = await shift_service.add_operator(operator_data, "admin")
    operator_id = shift.operators[0].id
    
    # Remove operator
    shift = await shift_service.remove_operator(operator_id, "admin")
    
    assert shift is not None
    assert len(shift.operators) == 0


@pytest.mark.asyncio
async def test_record_major_event(shift_service):
    """Test recording a major event during a shift."""
    data = ShiftCreate(supervisor="Sgt. Johnson")
    await shift_service.open_shift(data)
    
    event_data = RecordMajorEventRequest(
        event_type="10-33",
        description="Emergency - shots fired at Marina District",
        case_number="RTCC-2025-00042",
        units_involved=["Unit 45", "Unit 47"],
    )
    shift = await shift_service.record_major_event(event_data, "admin")
    
    assert shift is not None
    assert len(shift.major_events) == 1
    assert shift.major_events[0].event_type == "10-33"
    assert shift.major_events[0].case_number == "RTCC-2025-00042"


@pytest.mark.asyncio
async def test_shift_history(shift_service):
    """Test retrieving shift history."""
    # Create multiple shifts
    for i in range(3):
        open_data = ShiftCreate(supervisor=f"Supervisor {i}")
        await shift_service.open_shift(open_data)
        
        close_data = ShiftClose(
            closing_notes=f"Shift {i} closed",
            supervisor_signoff=f"Supervisor {i}",
        )
        await shift_service.close_shift(close_data)
    
    history = await shift_service.get_shift_history(limit=10)
    
    assert len(history) == 3


@pytest.mark.asyncio
async def test_auto_close_previous_shift(shift_service):
    """Test that opening a new shift auto-closes the previous one."""
    # Open first shift
    data1 = ShiftCreate(supervisor="Supervisor 1")
    shift1 = await shift_service.open_shift(data1)
    
    # Open second shift without closing first
    data2 = ShiftCreate(supervisor="Supervisor 2")
    shift2 = await shift_service.open_shift(data2)
    
    # First shift should be auto-closed
    old_shift = await shift_service.get_shift(shift1.id)
    assert old_shift.is_active is False
    
    # Second shift should be active
    current = await shift_service.get_current_shift()
    assert current.id == shift2.id
