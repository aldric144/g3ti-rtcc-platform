"""
Phase 38: Event Router Tests
Tests for event normalization and routing.
"""

import pytest
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../backend'))


class TestEventRouter:
    """Test suite for EventRouter functionality."""

    def test_event_router_singleton(self):
        """Test that EventRouter follows singleton pattern."""
        from app.orchestration.event_router import EventRouter
        router1 = EventRouter()
        router2 = EventRouter()
        assert router1 is router2

    def test_event_category_enum(self):
        """Test EventCategory enum values."""
        from app.orchestration.event_router import EventCategory
        assert EventCategory.INCIDENT.value == "incident"
        assert EventCategory.ALERT.value == "alert"
        assert EventCategory.TACTICAL.value == "tactical"
        assert EventCategory.OFFICER.value == "officer"
        assert EventCategory.DRONE.value == "drone"

    def test_event_priority_enum(self):
        """Test EventPriority enum values."""
        from app.orchestration.event_router import EventPriority
        assert EventPriority.CRITICAL.value == 1
        assert EventPriority.HIGH.value == 2
        assert EventPriority.MEDIUM.value == 3
        assert EventPriority.LOW.value == 4
        assert EventPriority.INFO.value == 5

    def test_event_schema_creation(self):
        """Test EventSchema dataclass creation."""
        from app.orchestration.event_router import EventSchema, EventCategory, EventPriority
        schema = EventSchema(
            event_type="gunshot_detected",
            category=EventCategory.INCIDENT,
            priority=EventPriority.CRITICAL,
            required_fields=["location", "timestamp"],
            optional_fields=["confidence"],
        )
        assert schema.event_type == "gunshot_detected"
        assert schema.category == EventCategory.INCIDENT

    def test_normalized_event_creation(self):
        """Test NormalizedEvent dataclass creation."""
        from app.orchestration.event_router import (
            NormalizedEvent, EventCategory, EventPriority
        )
        event = NormalizedEvent(
            original_event_id="orig-001",
            source_channel="gunshot_detection",
            event_type="gunshot_detected",
            category=EventCategory.INCIDENT,
            priority=EventPriority.CRITICAL,
            timestamp=datetime.utcnow(),
            location={"lat": 26.7753, "lng": -80.0589},
            entities=[],
            data={"confidence": 0.95},
            metadata={},
        )
        assert event.event_type == "gunshot_detected"
        assert event.normalized_event_id is not None

    def test_routing_rule_creation(self):
        """Test RoutingRule dataclass creation."""
        from app.orchestration.event_router import RoutingRule, EventCategory
        rule = RoutingRule(
            name="Incident Router",
            description="Routes incident events",
            source_channels=["gunshot_detection", "dispatch"],
            categories=[EventCategory.INCIDENT],
            priority_threshold=3,
            target_pipelines=["incident_response"],
            enabled=True,
        )
        assert rule.name == "Incident Router"
        assert rule.rule_id is not None

    def test_get_routing_rules(self):
        """Test getting routing rules."""
        from app.orchestration.event_router import EventRouter
        router = EventRouter()
        rules = router.get_routing_rules()
        assert isinstance(rules, list)

    def test_get_channels(self):
        """Test getting subscribed channels."""
        from app.orchestration.event_router import EventRouter
        router = EventRouter()
        channels = router.get_channels()
        assert isinstance(channels, list)

    def test_get_pipelines(self):
        """Test getting registered pipelines."""
        from app.orchestration.event_router import EventRouter
        router = EventRouter()
        pipelines = router.get_pipelines()
        assert isinstance(pipelines, list)

    def test_get_statistics(self):
        """Test getting router statistics."""
        from app.orchestration.event_router import EventRouter
        router = EventRouter()
        stats = router.get_statistics()
        assert "total_events_routed" in stats
        assert "active_rules" in stats


class TestEventNormalization:
    """Test suite for event normalization."""

    @pytest.mark.asyncio
    async def test_normalize_event(self):
        """Test event normalization."""
        from app.orchestration.event_router import EventRouter
        router = EventRouter()
        raw_event = {
            "event_id": "raw-001",
            "type": "gunshot_detected",
            "location": {"lat": 26.7753, "lng": -80.0589},
            "timestamp": datetime.utcnow().isoformat(),
            "data": {"confidence": 0.95},
        }
        normalized = await router.normalize_event("gunshot_detection", raw_event)
        assert normalized is not None

    def test_event_schema_validation(self):
        """Test event schema validation."""
        from app.orchestration.event_router import EventSchema, EventCategory, EventPriority
        schema = EventSchema(
            event_type="test_event",
            category=EventCategory.SYSTEM,
            priority=EventPriority.INFO,
            required_fields=["field1", "field2"],
            optional_fields=[],
        )
        valid_event = {"field1": "value1", "field2": "value2"}
        invalid_event = {"field1": "value1"}
        assert schema.validate(valid_event) is True
        assert schema.validate(invalid_event) is False


class TestEventRouting:
    """Test suite for event routing."""

    @pytest.mark.asyncio
    async def test_route_event(self):
        """Test event routing to pipelines."""
        from app.orchestration.event_router import EventRouter
        router = EventRouter()
        event = {
            "event_id": "route-001",
            "type": "test_event",
            "data": {},
        }
        await router.route_event("test_channel", event)

    def test_routing_rule_matching(self):
        """Test routing rule matching logic."""
        from app.orchestration.event_router import RoutingRule, EventCategory
        rule = RoutingRule(
            name="Test Rule",
            description="Test",
            source_channels=["channel_a", "channel_b"],
            categories=[EventCategory.INCIDENT],
            priority_threshold=3,
            target_pipelines=["pipeline_a"],
            enabled=True,
        )
        assert rule.matches("channel_a", EventCategory.INCIDENT, 2) is True
        assert rule.matches("channel_c", EventCategory.INCIDENT, 2) is False


class TestDefaultConfiguration:
    """Test suite for default router configuration."""

    def test_default_channels_subscribed(self):
        """Test that default channels are subscribed."""
        from app.orchestration.event_router import EventRouter
        router = EventRouter()
        channels = router.get_channels()
        assert len(channels) > 0

    def test_default_rules_registered(self):
        """Test that default routing rules are registered."""
        from app.orchestration.event_router import EventRouter
        router = EventRouter()
        rules = router.get_routing_rules()
        assert len(rules) > 0

    def test_default_pipelines_registered(self):
        """Test that default pipelines are registered."""
        from app.orchestration.event_router import EventRouter
        router = EventRouter()
        pipelines = router.get_pipelines()
        assert len(pipelines) > 0
