"""
Test Suite 7: Case Quick Tools Tests

Tests for case management shortcuts and rapid case tools.
"""

import pytest
from datetime import datetime, UTC

from app.case_tools.case_tools_model import (
    CaseNote,
    CaseNoteCreate,
    CaseFlag,
    CaseFlagCreate,
    UnitRequest,
    UnitRequestCreate,
    CaseShell,
    CaseShellCreate,
    BOLOZone,
    BOLOZoneCreate,
    FlagType,
    CasePriority,
)
from app.case_tools.case_tools_service import CaseToolsService


@pytest.fixture
def case_tools_service():
    """Create a fresh case tools service for each test."""
    return CaseToolsService()


@pytest.mark.asyncio
async def test_create_case_note(case_tools_service):
    """Test creating a case note."""
    data = CaseNoteCreate(
        case_id="RTCC-2025-00001",
        content="Test case note content",
        is_rtcc_support=True,
        tags=["test", "rtcc"],
    )
    
    note = await case_tools_service.create_note(data, "admin")
    
    assert note.id is not None
    assert note.case_id == "RTCC-2025-00001"
    assert note.content == "Test case note content"
    assert note.is_rtcc_support is True


@pytest.mark.asyncio
async def test_create_note_without_case_id(case_tools_service):
    """Test creating a note without case ID assigns temporary ID."""
    data = CaseNoteCreate(
        content="Note without case ID",
    )
    
    note = await case_tools_service.create_note(data, "admin")
    
    assert note.case_id.startswith("TEMP-")


@pytest.mark.asyncio
async def test_get_notes_for_case(case_tools_service):
    """Test retrieving notes for a specific case."""
    case_id = "RTCC-2025-00002"
    
    # Create multiple notes
    for i in range(3):
        data = CaseNoteCreate(
            case_id=case_id,
            content=f"Note {i}",
        )
        await case_tools_service.create_note(data, "admin")
    
    notes = await case_tools_service.get_notes_for_case(case_id)
    
    assert len(notes) == 3


@pytest.mark.asyncio
async def test_create_case_flag(case_tools_service):
    """Test flagging a case."""
    data = CaseFlagCreate(
        case_id="RTCC-2025-00003",
        flag_type=FlagType.RTCC_ASSISTED,
        reason="RTCC provided camera support",
    )
    
    flag = await case_tools_service.create_flag(data, "admin")
    
    assert flag.id is not None
    assert flag.flag_type == FlagType.RTCC_ASSISTED
    assert flag.is_active is True


@pytest.mark.asyncio
async def test_all_flag_types(case_tools_service):
    """Test creating flags with all flag types."""
    for flag_type in FlagType:
        data = CaseFlagCreate(
            case_id=f"CASE-{flag_type.value}",
            flag_type=flag_type,
        )
        flag = await case_tools_service.create_flag(data, "admin")
        assert flag.flag_type == flag_type


@pytest.mark.asyncio
async def test_create_unit_request(case_tools_service):
    """Test creating a unit follow-up request."""
    data = UnitRequestCreate(
        case_id="RTCC-2025-00004",
        request_type="follow_up",
        priority=CasePriority.HIGH,
        details="Follow up with witness",
        location="1200 Blue Heron Blvd",
    )
    
    request = await case_tools_service.create_unit_request(data, "admin")
    
    assert request.id is not None
    assert request.request_type == "follow_up"
    assert request.priority == CasePriority.HIGH
    assert request.status == "pending"


@pytest.mark.asyncio
async def test_get_pending_unit_requests(case_tools_service):
    """Test retrieving pending unit requests."""
    # Create multiple requests
    for i in range(3):
        data = UnitRequestCreate(
            case_id=f"CASE-{i}",
            request_type="follow_up",
            priority=CasePriority.MEDIUM,
            details=f"Request {i}",
        )
        await case_tools_service.create_unit_request(data, "admin")
    
    pending = await case_tools_service.get_pending_unit_requests()
    
    assert len(pending) == 3


@pytest.mark.asyncio
async def test_update_unit_request_status(case_tools_service):
    """Test updating unit request status."""
    data = UnitRequestCreate(
        case_id="RTCC-2025-00005",
        request_type="scene_check",
        priority=CasePriority.HIGH,
        details="Check scene",
    )
    request = await case_tools_service.create_unit_request(data, "admin")
    
    updated = await case_tools_service.update_unit_request_status(
        request.id, "completed", "patrol_unit"
    )
    
    assert updated.status == "completed"


@pytest.mark.asyncio
async def test_create_case_shell(case_tools_service):
    """Test creating a case shell."""
    data = CaseShellCreate(
        title="Armed Robbery - Blue Heron",
        description="Armed robbery at convenience store",
        priority=CasePriority.HIGH,
        incident_type="robbery",
        location="1200 Blue Heron Blvd",
        initial_notes="RTCC providing camera support",
    )
    
    shell = await case_tools_service.create_case_shell(data, "admin")
    
    assert shell.id is not None
    assert shell.case_number.startswith("RTCC-")
    assert shell.title == "Armed Robbery - Blue Heron"
    assert len(shell.notes) == 1  # Initial note


@pytest.mark.asyncio
async def test_case_number_generation(case_tools_service):
    """Test that case numbers are unique and sequential."""
    case_numbers = []
    
    for i in range(5):
        data = CaseShellCreate(
            title=f"Case {i}",
            priority=CasePriority.MEDIUM,
        )
        shell = await case_tools_service.create_case_shell(data, "admin")
        case_numbers.append(shell.case_number)
    
    # All case numbers should be unique
    assert len(set(case_numbers)) == 5


@pytest.mark.asyncio
async def test_create_bolo_zone(case_tools_service):
    """Test creating a BOLO zone."""
    data = BOLOZoneCreate(
        case_id="RTCC-2025-00006",
        zone_name="Marina District Alert",
        description="Suspect vehicle last seen in area",
        lat=26.7754,
        lng=-80.0583,
        radius_meters=500,
        alert_types=["lpr", "camera"],
    )
    
    zone = await case_tools_service.create_bolo_zone(data, "admin")
    
    assert zone.id is not None
    assert zone.zone_name == "Marina District Alert"
    assert zone.is_active is True


@pytest.mark.asyncio
async def test_get_active_bolo_zones(case_tools_service):
    """Test retrieving active BOLO zones."""
    # Create multiple zones
    for i in range(3):
        data = BOLOZoneCreate(
            case_id=f"CASE-{i}",
            zone_name=f"Zone {i}",
            description=f"Description {i}",
            lat=26.7754 + i * 0.01,
            lng=-80.0583,
        )
        await case_tools_service.create_bolo_zone(data, "admin")
    
    active = await case_tools_service.get_active_bolo_zones()
    
    assert len(active) == 3


@pytest.mark.asyncio
async def test_deactivate_bolo_zone(case_tools_service):
    """Test deactivating a BOLO zone."""
    data = BOLOZoneCreate(
        case_id="RTCC-2025-00007",
        zone_name="Test Zone",
        description="Zone to deactivate",
        lat=26.7754,
        lng=-80.0583,
    )
    zone = await case_tools_service.create_bolo_zone(data, "admin")
    
    deactivated = await case_tools_service.deactivate_bolo_zone(zone.id, "admin")
    
    assert deactivated.is_active is False
