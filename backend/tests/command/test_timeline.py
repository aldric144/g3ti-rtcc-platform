"""Tests for Operational Timeline Engine."""


import pytest

from app.command.timeline import (
    EventPriority,
    EventSource,
    EventType,
    TimelineManager,
)


class TestTimelineManager:
    """Test cases for TimelineManager."""

    @pytest.fixture
    def manager(self):
        """Create a TimelineManager instance."""
        return TimelineManager()

    @pytest.mark.asyncio
    async def test_add_event(self, manager):
        """Test adding an event to the timeline."""
        event = await manager.add_event(
            incident_id="inc-001",
            event_type=EventType.INCIDENT_CREATED,
            source=EventSource.CAD,
            title="Incident Created",
            description="Major incident created from CAD call",
            priority=EventPriority.HIGH,
            created_by="system",
        )

        assert event is not None
        assert event.event_type == EventType.INCIDENT_CREATED
        assert event.source == EventSource.CAD
        assert event.timestamp is not None

    @pytest.mark.asyncio
    async def test_get_timeline(self, manager):
        """Test getting the timeline for an incident."""
        incident_id = "inc-002"

        # Add multiple events
        await manager.add_event(
            incident_id=incident_id,
            event_type=EventType.INCIDENT_CREATED,
            source=EventSource.CAD,
            title="Incident Created",
            description="Test event 1",
            priority=EventPriority.HIGH,
            created_by="system",
        )
        await manager.add_event(
            incident_id=incident_id,
            event_type=EventType.UNIT_DISPATCHED,
            source=EventSource.CAD,
            title="Unit Dispatched",
            description="Test event 2",
            priority=EventPriority.MEDIUM,
            created_by="dispatch-001",
        )

        timeline = await manager.get_timeline(incident_id)

        assert len(timeline) >= 2
        # Events should be in chronological order
        assert timeline[0].timestamp <= timeline[1].timestamp

    @pytest.mark.asyncio
    async def test_pin_event(self, manager):
        """Test pinning an event."""
        event = await manager.add_event(
            incident_id="inc-001",
            event_type=EventType.GUNFIRE_DETECTED,
            source=EventSource.SHOTSPOTTER,
            title="Gunfire Detected",
            description="3 rounds detected",
            priority=EventPriority.CRITICAL,
            created_by="system",
        )

        pinned = await manager.pin_event(
            incident_id="inc-001",
            event_id=event.id,
            pinned_by="commander-001",
        )

        assert pinned.is_pinned is True

    @pytest.mark.asyncio
    async def test_unpin_event(self, manager):
        """Test unpinning an event."""
        event = await manager.add_event(
            incident_id="inc-001",
            event_type=EventType.PERIMETER_ESTABLISHED,
            source=EventSource.TACTICAL,
            title="Perimeter Established",
            description="Outer perimeter set",
            priority=EventPriority.HIGH,
            created_by="commander-001",
        )

        await manager.pin_event("inc-001", event.id, "commander-001")
        unpinned = await manager.unpin_event("inc-001", event.id, "commander-001")

        assert unpinned.is_pinned is False

    @pytest.mark.asyncio
    async def test_get_critical_events(self, manager):
        """Test getting critical events."""
        incident_id = "inc-003"

        await manager.add_event(
            incident_id=incident_id,
            event_type=EventType.GUNFIRE_DETECTED,
            source=EventSource.SHOTSPOTTER,
            title="Gunfire",
            description="Critical event",
            priority=EventPriority.CRITICAL,
            created_by="system",
        )
        await manager.add_event(
            incident_id=incident_id,
            event_type=EventType.UNIT_ARRIVED,
            source=EventSource.CAD,
            title="Unit Arrived",
            description="Normal event",
            priority=EventPriority.MEDIUM,
            created_by="system",
        )

        critical = await manager.get_critical_events(incident_id)

        assert len(critical) >= 1
        assert all(e.priority == EventPriority.CRITICAL for e in critical)

    @pytest.mark.asyncio
    async def test_add_command_note(self, manager):
        """Test adding a command note to the timeline."""
        event = await manager.add_command_note(
            incident_id="inc-001",
            title="Commander Update",
            content="All units hold position. Entry team preparing.",
            priority=EventPriority.HIGH,
            created_by="commander-001",
        )

        assert event is not None
        assert event.event_type == EventType.COMMAND_NOTE
        assert event.source == EventSource.COMMAND

    @pytest.mark.asyncio
    async def test_event_types(self, manager):
        """Test all event types can be added."""
        incident_id = "inc-004"

        for event_type in EventType:
            event = await manager.add_event(
                incident_id=incident_id,
                event_type=event_type,
                source=EventSource.COMMAND,
                title=f"Test {event_type.value}",
                description=f"Testing {event_type.value}",
                priority=EventPriority.MEDIUM,
                created_by="test-user",
            )
            assert event.event_type == event_type

    @pytest.mark.asyncio
    async def test_event_sources(self, manager):
        """Test all event sources can be used."""
        incident_id = "inc-005"

        for source in EventSource:
            event = await manager.add_event(
                incident_id=incident_id,
                event_type=EventType.COMMAND_NOTE,
                source=source,
                title=f"Test from {source.value}",
                description=f"Testing source {source.value}",
                priority=EventPriority.LOW,
                created_by="test-user",
            )
            assert event.source == source

    @pytest.mark.asyncio
    async def test_get_events_by_source(self, manager):
        """Test filtering events by source."""
        incident_id = "inc-006"

        await manager.add_event(
            incident_id=incident_id,
            event_type=EventType.GUNFIRE_DETECTED,
            source=EventSource.SHOTSPOTTER,
            title="Gunfire 1",
            description="From ShotSpotter",
            priority=EventPriority.CRITICAL,
            created_by="system",
        )
        await manager.add_event(
            incident_id=incident_id,
            event_type=EventType.UNIT_DISPATCHED,
            source=EventSource.CAD,
            title="Unit Dispatch",
            description="From CAD",
            priority=EventPriority.MEDIUM,
            created_by="dispatch",
        )

        shotspotter_events = await manager.get_events_by_source(
            incident_id, EventSource.SHOTSPOTTER
        )

        assert len(shotspotter_events) >= 1
        assert all(e.source == EventSource.SHOTSPOTTER for e in shotspotter_events)

    @pytest.mark.asyncio
    async def test_redact_event(self, manager):
        """Test redacting an event."""
        event = await manager.add_event(
            incident_id="inc-001",
            event_type=EventType.COMMAND_NOTE,
            source=EventSource.COMMAND,
            title="Sensitive Info",
            description="Contains sensitive information",
            priority=EventPriority.HIGH,
            created_by="commander-001",
        )

        redacted = await manager.redact_event(
            incident_id="inc-001",
            event_id=event.id,
            redacted_by="admin-001",
            reason="Contains PII",
        )

        assert redacted.is_redacted is True

    @pytest.mark.asyncio
    async def test_get_pinned_events(self, manager):
        """Test getting pinned events."""
        incident_id = "inc-007"

        event1 = await manager.add_event(
            incident_id=incident_id,
            event_type=EventType.INCIDENT_ACTIVATED,
            source=EventSource.COMMAND,
            title="Activated",
            description="Incident activated",
            priority=EventPriority.HIGH,
            created_by="commander-001",
        )
        await manager.pin_event(incident_id, event1.id, "commander-001")

        await manager.add_event(
            incident_id=incident_id,
            event_type=EventType.UNIT_ARRIVED,
            source=EventSource.CAD,
            title="Unit Arrived",
            description="Not pinned",
            priority=EventPriority.MEDIUM,
            created_by="system",
        )

        pinned = await manager.get_pinned_events(incident_id)

        assert len(pinned) >= 1
        assert all(e.is_pinned for e in pinned)
