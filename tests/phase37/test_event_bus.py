"""
Phase 37: Master Event Bus Tests
Tests for the Master Event Bus functionality.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

from backend.app.master_orchestration.event_bus import (
    MasterEventBus,
    EventType,
    EventPriority,
    EventSource,
    MasterEvent,
    EventSubscription,
)


class TestMasterEventBus:
    """Test suite for MasterEventBus."""

    def setup_method(self):
        """Reset singleton for each test."""
        MasterEventBus._instance = None
        self.event_bus = MasterEventBus()

    def test_singleton_pattern(self):
        """Test that MasterEventBus follows singleton pattern."""
        bus1 = MasterEventBus()
        bus2 = MasterEventBus()
        assert bus1 is bus2

    def test_create_event(self):
        """Test event creation with all fields."""
        event = self.event_bus.create_event(
            event_type=EventType.ALERT,
            source=EventSource.OFFICER_SAFETY,
            title="Test Alert",
            summary="Test summary",
            priority=EventPriority.HIGH,
            details={"key": "value"},
            geolocation={"lat": 26.7753, "lng": -80.0589},
            constitutional_compliance=True,
            moral_compass_tag="compliant",
            public_safety_audit_ref="audit-001",
            affected_modules=["module1", "module2"],
            requires_acknowledgment=True,
        )

        assert event.event_id is not None
        assert event.event_type == EventType.ALERT
        assert event.source == EventSource.OFFICER_SAFETY
        assert event.title == "Test Alert"
        assert event.priority == EventPriority.HIGH
        assert event.constitutional_compliance is True
        assert event.requires_acknowledgment is True

    def test_event_to_dict(self):
        """Test event serialization to dictionary."""
        event = self.event_bus.create_event(
            event_type=EventType.SYSTEM_MESSAGE,
            source=EventSource.SYSTEM,
            title="System Message",
        )

        event_dict = event.to_dict()

        assert "event_id" in event_dict
        assert event_dict["event_type"] == "system_message"
        assert event_dict["source"] == "system"
        assert event_dict["title"] == "System Message"

    @pytest.mark.asyncio
    async def test_publish_event(self):
        """Test async event publishing."""
        event = self.event_bus.create_event(
            event_type=EventType.TACTICAL_EVENT,
            source=EventSource.TACTICAL_ANALYTICS,
            title="Tactical Update",
        )

        await self.event_bus.publish(event)

        retrieved = self.event_bus.get_event(event.event_id)
        assert retrieved is not None
        assert retrieved.event_id == event.event_id

    def test_publish_sync(self):
        """Test synchronous event publishing."""
        event = self.event_bus.create_event(
            event_type=EventType.DRONE_TELEMETRY,
            source=EventSource.DRONE_OPS,
            title="Drone Update",
        )

        self.event_bus.publish_sync(event)

        retrieved = self.event_bus.get_event(event.event_id)
        assert retrieved is not None

    def test_subscribe_to_events(self):
        """Test event subscription."""
        callback = MagicMock()

        subscription = self.event_bus.subscribe(
            subscriber_id="test-subscriber",
            event_types=[EventType.ALERT],
            sources=[EventSource.OFFICER_SAFETY],
            callback=callback,
        )

        assert subscription.subscription_id is not None
        assert subscription.subscriber_id == "test-subscriber"
        assert EventType.ALERT in subscription.event_types

    def test_unsubscribe(self):
        """Test event unsubscription."""
        callback = MagicMock()

        subscription = self.event_bus.subscribe(
            subscriber_id="test-subscriber",
            event_types=[EventType.ALERT],
            callback=callback,
        )

        result = self.event_bus.unsubscribe(subscription.subscription_id)
        assert result is True

        sub = self.event_bus.get_subscription(subscription.subscription_id)
        assert sub is None or sub.active is False

    def test_get_recent_events(self):
        """Test retrieving recent events."""
        for i in range(5):
            event = self.event_bus.create_event(
                event_type=EventType.ALERT,
                source=EventSource.SYSTEM,
                title=f"Event {i}",
            )
            self.event_bus.publish_sync(event)

        events = self.event_bus.get_recent_events(limit=3)
        assert len(events) <= 3

    def test_get_events_by_type(self):
        """Test filtering events by type."""
        alert_event = self.event_bus.create_event(
            event_type=EventType.ALERT,
            source=EventSource.SYSTEM,
            title="Alert Event",
        )
        self.event_bus.publish_sync(alert_event)

        tactical_event = self.event_bus.create_event(
            event_type=EventType.TACTICAL_EVENT,
            source=EventSource.TACTICAL_ANALYTICS,
            title="Tactical Event",
        )
        self.event_bus.publish_sync(tactical_event)

        alerts = self.event_bus.get_events_by_type(EventType.ALERT)
        assert all(e.event_type == EventType.ALERT for e in alerts)

    def test_get_events_by_source(self):
        """Test filtering events by source."""
        event = self.event_bus.create_event(
            event_type=EventType.OFFICER_SAFETY,
            source=EventSource.OFFICER_SAFETY,
            title="Officer Safety Event",
        )
        self.event_bus.publish_sync(event)

        events = self.event_bus.get_events_by_source(EventSource.OFFICER_SAFETY)
        assert all(e.source == EventSource.OFFICER_SAFETY for e in events)

    def test_acknowledge_event(self):
        """Test event acknowledgment."""
        event = self.event_bus.create_event(
            event_type=EventType.ALERT,
            source=EventSource.SYSTEM,
            title="Acknowledgment Test",
            requires_acknowledgment=True,
        )
        self.event_bus.publish_sync(event)

        result = self.event_bus.acknowledge_event(event.event_id, "operator-001")
        assert result is True

        updated = self.event_bus.get_event(event.event_id)
        assert updated.acknowledged_by == "operator-001"
        assert updated.acknowledged_at is not None

    def test_get_unacknowledged_events(self):
        """Test retrieving unacknowledged events."""
        event = self.event_bus.create_event(
            event_type=EventType.ALERT,
            source=EventSource.SYSTEM,
            title="Unacknowledged Event",
            requires_acknowledgment=True,
        )
        self.event_bus.publish_sync(event)

        unacked = self.event_bus.get_unacknowledged_events()
        assert any(e.event_id == event.event_id for e in unacked)

    def test_get_statistics(self):
        """Test statistics retrieval."""
        stats = self.event_bus.get_statistics()

        assert "total_events" in stats
        assert "events_by_type" in stats
        assert "events_by_source" in stats
        assert "events_by_priority" in stats

    def test_event_priority_ordering(self):
        """Test that events are ordered by priority."""
        low_event = self.event_bus.create_event(
            event_type=EventType.ALERT,
            source=EventSource.SYSTEM,
            title="Low Priority",
            priority=EventPriority.LOW,
        )
        self.event_bus.publish_sync(low_event)

        critical_event = self.event_bus.create_event(
            event_type=EventType.ALERT,
            source=EventSource.SYSTEM,
            title="Critical Priority",
            priority=EventPriority.CRITICAL,
        )
        self.event_bus.publish_sync(critical_event)

        events = self.event_bus.get_recent_events(
            min_priority=EventPriority.HIGH
        )
        assert all(
            e.priority in [EventPriority.CRITICAL, EventPriority.HIGH]
            for e in events
        )

    def test_event_types_enum(self):
        """Test all event types are defined."""
        assert len(EventType) >= 25
        assert EventType.ALERT.value == "alert"
        assert EventType.TACTICAL_EVENT.value == "tactical_event"
        assert EventType.DRONE_TELEMETRY.value == "drone_telemetry"

    def test_event_sources_enum(self):
        """Test all event sources are defined."""
        assert len(EventSource) >= 30
        assert EventSource.OFFICER_SAFETY.value == "officer_safety"
        assert EventSource.DRONE_OPS.value == "drone_ops"
        assert EventSource.MORAL_COMPASS.value == "moral_compass"
