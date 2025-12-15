"""
Test Suite 5: Admin Update Tests

Tests for admin console updates and metrics editing.
"""

import pytest
from datetime import datetime, UTC

from app.admin_logs.activity_log_model import (
    ActivityLog,
    ActivityLogCreate,
    ActivityLogUpdate,
    LogType,
    LogPriority,
    ActivityLogSearchParams,
)
from app.admin_logs.activity_log_service import ActivityLogService


@pytest.fixture
def activity_log_service():
    """Create a fresh activity log service for each test."""
    return ActivityLogService()


@pytest.mark.asyncio
async def test_update_log_type(activity_log_service):
    """Test updating the log type of an entry."""
    create_data = ActivityLogCreate(
        log_type=LogType.INCIDENT,
        priority=LogPriority.MEDIUM,
        notes="Original log",
    )
    log = await activity_log_service.create_log(create_data, "admin")
    
    update_data = ActivityLogUpdate(log_type=LogType.SHOTSPOTTER)
    updated = await activity_log_service.update_log(log.id, update_data, "admin")
    
    assert updated.log_type == LogType.SHOTSPOTTER


@pytest.mark.asyncio
async def test_update_priority(activity_log_service):
    """Test updating the priority of an entry."""
    create_data = ActivityLogCreate(
        log_type=LogType.INCIDENT,
        priority=LogPriority.LOW,
        notes="Low priority log",
    )
    log = await activity_log_service.create_log(create_data, "admin")
    
    update_data = ActivityLogUpdate(priority=LogPriority.CRITICAL)
    updated = await activity_log_service.update_log(log.id, update_data, "admin")
    
    assert updated.priority == LogPriority.CRITICAL


@pytest.mark.asyncio
async def test_update_notes(activity_log_service):
    """Test updating the notes of an entry."""
    create_data = ActivityLogCreate(
        log_type=LogType.INCIDENT,
        priority=LogPriority.MEDIUM,
        notes="Original notes",
    )
    log = await activity_log_service.create_log(create_data, "admin")
    
    update_data = ActivityLogUpdate(notes="Updated notes with more detail")
    updated = await activity_log_service.update_log(log.id, update_data, "admin")
    
    assert updated.notes == "Updated notes with more detail"


@pytest.mark.asyncio
async def test_update_tags(activity_log_service):
    """Test updating the tags of an entry."""
    create_data = ActivityLogCreate(
        log_type=LogType.INCIDENT,
        priority=LogPriority.MEDIUM,
        notes="Log with tags",
        tags=["original"],
    )
    log = await activity_log_service.create_log(create_data, "admin")
    
    update_data = ActivityLogUpdate(tags=["updated", "new-tag"])
    updated = await activity_log_service.update_log(log.id, update_data, "admin")
    
    assert updated.tags == ["updated", "new-tag"]


@pytest.mark.asyncio
async def test_partial_update(activity_log_service):
    """Test partial update (only some fields)."""
    create_data = ActivityLogCreate(
        log_type=LogType.INCIDENT,
        priority=LogPriority.MEDIUM,
        notes="Original notes",
        tags=["original"],
    )
    log = await activity_log_service.create_log(create_data, "admin")
    
    # Only update priority
    update_data = ActivityLogUpdate(priority=LogPriority.HIGH)
    updated = await activity_log_service.update_log(log.id, update_data, "admin")
    
    # Priority should change, others should remain
    assert updated.priority == LogPriority.HIGH
    assert updated.notes == "Original notes"
    assert updated.tags == ["original"]


@pytest.mark.asyncio
async def test_update_nonexistent_log(activity_log_service):
    """Test updating a non-existent log returns None."""
    update_data = ActivityLogUpdate(notes="New notes")
    result = await activity_log_service.update_log("nonexistent-id", update_data, "admin")
    
    assert result is None


@pytest.mark.asyncio
async def test_update_timestamp_changes(activity_log_service):
    """Test that updated_at timestamp changes on update."""
    create_data = ActivityLogCreate(
        log_type=LogType.INCIDENT,
        priority=LogPriority.MEDIUM,
        notes="Original notes",
    )
    log = await activity_log_service.create_log(create_data, "admin")
    original_updated_at = log.updated_at
    
    update_data = ActivityLogUpdate(notes="Updated notes")
    updated = await activity_log_service.update_log(log.id, update_data, "admin")
    
    assert updated.updated_at >= original_updated_at


@pytest.mark.asyncio
async def test_multiple_updates(activity_log_service):
    """Test multiple sequential updates."""
    create_data = ActivityLogCreate(
        log_type=LogType.INCIDENT,
        priority=LogPriority.LOW,
        notes="Version 1",
    )
    log = await activity_log_service.create_log(create_data, "admin")
    
    # First update
    update1 = ActivityLogUpdate(notes="Version 2")
    log = await activity_log_service.update_log(log.id, update1, "admin")
    
    # Second update
    update2 = ActivityLogUpdate(priority=LogPriority.HIGH)
    log = await activity_log_service.update_log(log.id, update2, "admin")
    
    # Third update
    update3 = ActivityLogUpdate(notes="Version 3", tags=["final"])
    log = await activity_log_service.update_log(log.id, update3, "admin")
    
    assert log.notes == "Version 3"
    assert log.priority == LogPriority.HIGH
    assert log.tags == ["final"]
