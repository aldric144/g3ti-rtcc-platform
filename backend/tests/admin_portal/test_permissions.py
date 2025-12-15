"""
Test Suite 6: Permission Tests

Tests for role-based access control and permission enforcement.
"""

import pytest
from datetime import datetime, UTC

from app.admin_logs.activity_log_model import ActivityLogCreate, LogType, LogPriority
from app.admin_logs.activity_log_service import ActivityLogService
from app.shift_admin.shift_model import ShiftCreate, AddOperatorRequest, OperatorRole
from app.shift_admin.shift_service import ShiftService


@pytest.fixture
def activity_log_service():
    """Create a fresh activity log service for each test."""
    return ActivityLogService()


@pytest.fixture
def shift_service():
    """Create a fresh shift service for each test."""
    return ShiftService()


@pytest.mark.asyncio
async def test_log_editor_tracking(activity_log_service):
    """Test that the editor is properly tracked on log entries."""
    data = ActivityLogCreate(
        log_type=LogType.INCIDENT,
        priority=LogPriority.MEDIUM,
        notes="Test log",
    )
    
    log = await activity_log_service.create_log(data, "supervisor_user")
    
    assert log.editor == "supervisor_user"


@pytest.mark.asyncio
async def test_audit_trail_creation(activity_log_service):
    """Test that audit trail entries are created."""
    data = ActivityLogCreate(
        log_type=LogType.INCIDENT,
        priority=LogPriority.MEDIUM,
        notes="Test log",
    )
    
    log = await activity_log_service.create_log(data, "admin")
    
    audit_trail = await activity_log_service.get_audit_trail(log.id)
    
    assert len(audit_trail) >= 1
    assert audit_trail[0]["action"] == "CREATE"
    assert audit_trail[0]["editor"] == "admin"


@pytest.mark.asyncio
async def test_audit_trail_on_update(activity_log_service):
    """Test that audit trail is updated on log updates."""
    from app.admin_logs.activity_log_model import ActivityLogUpdate
    
    data = ActivityLogCreate(
        log_type=LogType.INCIDENT,
        priority=LogPriority.MEDIUM,
        notes="Original",
    )
    log = await activity_log_service.create_log(data, "admin")
    
    update_data = ActivityLogUpdate(notes="Updated")
    await activity_log_service.update_log(log.id, update_data, "supervisor")
    
    audit_trail = await activity_log_service.get_audit_trail(log.id)
    
    assert len(audit_trail) >= 2
    update_entry = [e for e in audit_trail if e["action"] == "UPDATE"][0]
    assert update_entry["editor"] == "supervisor"


@pytest.mark.asyncio
async def test_audit_trail_on_archive(activity_log_service):
    """Test that audit trail is updated on log archive."""
    data = ActivityLogCreate(
        log_type=LogType.INCIDENT,
        priority=LogPriority.MEDIUM,
        notes="To archive",
    )
    log = await activity_log_service.create_log(data, "admin")
    
    await activity_log_service.archive_log(log.id, "supervisor")
    
    audit_trail = await activity_log_service.get_audit_trail(log.id)
    
    archive_entry = [e for e in audit_trail if e["action"] == "ARCHIVE"][0]
    assert archive_entry["editor"] == "supervisor"


@pytest.mark.asyncio
async def test_audit_trail_on_delete(activity_log_service):
    """Test that audit trail is updated on log delete."""
    data = ActivityLogCreate(
        log_type=LogType.INCIDENT,
        priority=LogPriority.MEDIUM,
        notes="To delete",
    )
    log = await activity_log_service.create_log(data, "admin")
    log_id = log.id
    
    await activity_log_service.delete_log(log_id, "supervisor")
    
    # Audit trail should still exist even after deletion
    audit_trail = await activity_log_service.get_audit_trail(log_id)
    
    delete_entry = [e for e in audit_trail if e["action"] == "DELETE"][0]
    assert delete_entry["editor"] == "supervisor"


@pytest.mark.asyncio
async def test_operator_role_assignment(shift_service):
    """Test that operator roles are properly assigned."""
    data = ShiftCreate(supervisor="Sgt. Johnson")
    await shift_service.open_shift(data)
    
    for role in OperatorRole:
        operator_data = AddOperatorRequest(
            username=f"user_{role.value}",
            name=f"User {role.value}",
            role=role,
        )
        shift = await shift_service.add_operator(operator_data, "admin")
        
        added_operator = [op for op in shift.operators if op.role == role][0]
        assert added_operator.role == role


@pytest.mark.asyncio
async def test_shift_supervisor_tracking(shift_service):
    """Test that shift supervisor is properly tracked."""
    data = ShiftCreate(supervisor="Lt. Martinez")
    shift = await shift_service.open_shift(data)
    
    assert shift.supervisor == "Lt. Martinez"


@pytest.mark.asyncio
async def test_major_event_recorder_tracking(shift_service):
    """Test that major event recorder is tracked."""
    from app.shift_admin.shift_model import RecordMajorEventRequest
    
    data = ShiftCreate(supervisor="Sgt. Johnson")
    await shift_service.open_shift(data)
    
    event_data = RecordMajorEventRequest(
        event_type="10-33",
        description="Emergency",
    )
    shift = await shift_service.record_major_event(event_data, "analyst_user")
    
    assert shift.major_events[0].recorded_by == "analyst_user"


@pytest.mark.asyncio
async def test_full_audit_trail_retrieval(activity_log_service):
    """Test retrieving full audit trail without log ID filter."""
    # Create multiple logs
    for i in range(3):
        data = ActivityLogCreate(
            log_type=LogType.INCIDENT,
            priority=LogPriority.MEDIUM,
            notes=f"Log {i}",
        )
        await activity_log_service.create_log(data, f"user_{i}")
    
    full_audit = await activity_log_service.get_audit_trail()
    
    assert len(full_audit) >= 3
