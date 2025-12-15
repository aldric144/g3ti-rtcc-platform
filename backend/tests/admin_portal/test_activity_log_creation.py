"""
Test Suite 1: Activity Log Creation Tests

Tests for creating, updating, and managing activity log entries.
"""

import pytest
from datetime import datetime, UTC

from app.admin_logs.activity_log_model import (
    ActivityLog,
    ActivityLogCreate,
    ActivityLogUpdate,
    LogType,
    LogPriority,
)
from app.admin_logs.activity_log_service import ActivityLogService


@pytest.fixture
def activity_log_service():
    """Create a fresh activity log service for each test."""
    return ActivityLogService()


@pytest.mark.asyncio
async def test_create_activity_log(activity_log_service):
    """Test creating a new activity log entry."""
    data = ActivityLogCreate(
        log_type=LogType.INCIDENT,
        priority=LogPriority.HIGH,
        notes="Test incident log entry",
        tags=["test", "incident"],
    )
    
    log = await activity_log_service.create_log(data, "test_user")
    
    assert log.id is not None
    assert log.log_type == LogType.INCIDENT
    assert log.priority == LogPriority.HIGH
    assert log.notes == "Test incident log entry"
    assert log.editor == "test_user"
    assert log.archived is False


@pytest.mark.asyncio
async def test_create_log_with_all_types(activity_log_service):
    """Test creating logs with all available log types."""
    for log_type in LogType:
        data = ActivityLogCreate(
            log_type=log_type,
            priority=LogPriority.MEDIUM,
            notes=f"Test {log_type.value} log",
        )
        
        log = await activity_log_service.create_log(data, "test_user")
        assert log.log_type == log_type


@pytest.mark.asyncio
async def test_create_log_with_all_priorities(activity_log_service):
    """Test creating logs with all priority levels."""
    for priority in LogPriority:
        data = ActivityLogCreate(
            log_type=LogType.INCIDENT,
            priority=priority,
            notes=f"Test {priority.value} priority log",
        )
        
        log = await activity_log_service.create_log(data, "test_user")
        assert log.priority == priority


@pytest.mark.asyncio
async def test_update_activity_log(activity_log_service):
    """Test updating an existing activity log entry."""
    # Create initial log
    create_data = ActivityLogCreate(
        log_type=LogType.INCIDENT,
        priority=LogPriority.LOW,
        notes="Original notes",
    )
    log = await activity_log_service.create_log(create_data, "test_user")
    
    # Update the log
    update_data = ActivityLogUpdate(
        priority=LogPriority.HIGH,
        notes="Updated notes",
    )
    updated_log = await activity_log_service.update_log(log.id, update_data, "test_user")
    
    assert updated_log is not None
    assert updated_log.priority == LogPriority.HIGH
    assert updated_log.notes == "Updated notes"
    assert updated_log.updated_at > log.created_at


@pytest.mark.asyncio
async def test_archive_activity_log(activity_log_service):
    """Test archiving an activity log entry."""
    data = ActivityLogCreate(
        log_type=LogType.INCIDENT,
        priority=LogPriority.MEDIUM,
        notes="Log to be archived",
    )
    log = await activity_log_service.create_log(data, "test_user")
    
    archived_log = await activity_log_service.archive_log(log.id, "test_user")
    
    assert archived_log is not None
    assert archived_log.archived is True


@pytest.mark.asyncio
async def test_delete_activity_log(activity_log_service):
    """Test deleting an activity log entry."""
    data = ActivityLogCreate(
        log_type=LogType.INCIDENT,
        priority=LogPriority.MEDIUM,
        notes="Log to be deleted",
    )
    log = await activity_log_service.create_log(data, "test_user")
    
    success = await activity_log_service.delete_log(log.id, "test_user")
    assert success is True
    
    # Verify deletion
    deleted_log = await activity_log_service.get_log(log.id)
    assert deleted_log is None


@pytest.mark.asyncio
async def test_get_activity_log(activity_log_service):
    """Test retrieving a specific activity log by ID."""
    data = ActivityLogCreate(
        log_type=LogType.SHOTSPOTTER,
        priority=LogPriority.CRITICAL,
        notes="ShotSpotter activation",
    )
    created_log = await activity_log_service.create_log(data, "test_user")
    
    retrieved_log = await activity_log_service.get_log(created_log.id)
    
    assert retrieved_log is not None
    assert retrieved_log.id == created_log.id
    assert retrieved_log.notes == "ShotSpotter activation"


@pytest.mark.asyncio
async def test_log_timestamps(activity_log_service):
    """Test that timestamps are properly set on log entries."""
    data = ActivityLogCreate(
        log_type=LogType.INCIDENT,
        priority=LogPriority.MEDIUM,
        notes="Test timestamps",
    )
    
    before_create = datetime.now(UTC)
    log = await activity_log_service.create_log(data, "test_user")
    after_create = datetime.now(UTC)
    
    assert before_create <= log.created_at <= after_create
    assert before_create <= log.updated_at <= after_create


@pytest.mark.asyncio
async def test_log_tags(activity_log_service):
    """Test that tags are properly stored and retrieved."""
    tags = ["urgent", "follow-up", "patrol"]
    data = ActivityLogCreate(
        log_type=LogType.PATROL_REQUEST,
        priority=LogPriority.HIGH,
        notes="Patrol request with tags",
        tags=tags,
    )
    
    log = await activity_log_service.create_log(data, "test_user")
    
    assert log.tags == tags
