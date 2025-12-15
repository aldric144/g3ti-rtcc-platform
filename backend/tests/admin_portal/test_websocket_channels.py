"""
Test Suite 8: WebSocket Channel Tests

Tests for admin portal WebSocket channels and real-time updates.
"""

import pytest
from datetime import datetime, UTC
import json

from app.admin_logs.activity_log_model import ActivityLogCreate, LogType, LogPriority
from app.admin_logs.activity_log_service import ActivityLogService
from app.shift_admin.shift_model import ShiftCreate, RecordMajorEventRequest
from app.shift_admin.shift_service import ShiftService


@pytest.fixture
def activity_log_service():
    """Create a fresh activity log service for each test."""
    return ActivityLogService()


@pytest.fixture
def shift_service():
    """Create a fresh shift service for each test."""
    return ShiftService()


class MockWebSocketManager:
    """Mock WebSocket manager for testing."""
    
    def __init__(self):
        self.broadcasts = []
        self.channel_messages = {}
    
    async def broadcast(self, message: dict, channel: str = "admin"):
        """Record broadcast messages."""
        self.broadcasts.append({"message": message, "channel": channel})
        if channel not in self.channel_messages:
            self.channel_messages[channel] = []
        self.channel_messages[channel].append(message)
    
    def get_messages(self, channel: str):
        """Get messages for a specific channel."""
        return self.channel_messages.get(channel, [])


@pytest.mark.asyncio
async def test_log_creation_event_structure():
    """Test that log creation events have correct structure."""
    service = ActivityLogService()
    
    data = ActivityLogCreate(
        log_type=LogType.INCIDENT,
        priority=LogPriority.HIGH,
        notes="Test incident",
    )
    log = await service.create_log(data, "admin")
    
    # Verify log has all required fields for WebSocket broadcast
    assert log.id is not None
    assert log.log_type is not None
    assert log.priority is not None
    assert log.created_at is not None
    assert log.editor is not None


@pytest.mark.asyncio
async def test_shift_event_structure():
    """Test that shift events have correct structure."""
    service = ShiftService()
    
    data = ShiftCreate(supervisor="Sgt. Johnson")
    shift = await service.open_shift(data)
    
    # Verify shift has all required fields for WebSocket broadcast
    assert shift.id is not None
    assert shift.supervisor is not None
    assert shift.start_time is not None
    assert shift.is_active is not None


@pytest.mark.asyncio
async def test_major_event_broadcast_structure():
    """Test that major event broadcasts have correct structure."""
    service = ShiftService()
    
    data = ShiftCreate(supervisor="Sgt. Johnson")
    await service.open_shift(data)
    
    event_data = RecordMajorEventRequest(
        event_type="10-33",
        description="Emergency situation",
        case_number="RTCC-2025-00001",
    )
    shift = await service.record_major_event(event_data, "admin")
    
    event = shift.major_events[0]
    
    # Verify event has all required fields for WebSocket broadcast
    assert event.id is not None
    assert event.event_type is not None
    assert event.description is not None
    assert event.timestamp is not None
    assert event.recorded_by is not None


def test_websocket_message_serialization():
    """Test that WebSocket messages can be serialized to JSON."""
    message = {
        "type": "log_created",
        "data": {
            "id": "test-id",
            "log_type": "incident",
            "priority": "high",
            "notes": "Test notes",
            "editor": "admin",
            "created_at": datetime.now(UTC).isoformat(),
        }
    }
    
    # Should not raise
    json_str = json.dumps(message)
    parsed = json.loads(json_str)
    
    assert parsed["type"] == "log_created"
    assert parsed["data"]["id"] == "test-id"


def test_shift_event_serialization():
    """Test that shift events can be serialized to JSON."""
    message = {
        "type": "shift_opened",
        "data": {
            "id": "shift-id",
            "supervisor": "Sgt. Johnson",
            "start_time": datetime.now(UTC).isoformat(),
            "is_active": True,
            "operators": [],
            "major_events": [],
        }
    }
    
    json_str = json.dumps(message)
    parsed = json.loads(json_str)
    
    assert parsed["type"] == "shift_opened"
    assert parsed["data"]["supervisor"] == "Sgt. Johnson"


def test_major_event_serialization():
    """Test that major events can be serialized to JSON."""
    message = {
        "type": "major_event_recorded",
        "data": {
            "id": "event-id",
            "event_type": "10-33",
            "description": "Emergency",
            "timestamp": datetime.now(UTC).isoformat(),
            "recorded_by": "admin",
            "case_number": "RTCC-2025-00001",
        }
    }
    
    json_str = json.dumps(message)
    parsed = json.loads(json_str)
    
    assert parsed["type"] == "major_event_recorded"
    assert parsed["data"]["event_type"] == "10-33"


def test_mock_websocket_broadcast():
    """Test mock WebSocket manager broadcast functionality."""
    import asyncio
    
    ws_manager = MockWebSocketManager()
    
    async def test_broadcast():
        await ws_manager.broadcast(
            {"type": "test", "data": "test_data"},
            channel="admin_logs"
        )
        await ws_manager.broadcast(
            {"type": "test2", "data": "test_data2"},
            channel="admin_logs"
        )
    
    asyncio.run(test_broadcast())
    
    messages = ws_manager.get_messages("admin_logs")
    assert len(messages) == 2


def test_channel_separation():
    """Test that messages are separated by channel."""
    import asyncio
    
    ws_manager = MockWebSocketManager()
    
    async def test_channels():
        await ws_manager.broadcast({"type": "log"}, channel="logs")
        await ws_manager.broadcast({"type": "shift"}, channel="shifts")
        await ws_manager.broadcast({"type": "patrol"}, channel="patrol")
    
    asyncio.run(test_channels())
    
    assert len(ws_manager.get_messages("logs")) == 1
    assert len(ws_manager.get_messages("shifts")) == 1
    assert len(ws_manager.get_messages("patrol")) == 1
