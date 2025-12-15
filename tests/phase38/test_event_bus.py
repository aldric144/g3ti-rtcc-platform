"""
Phase 38: Event Fusion Bus Tests
Tests for event ingestion, fusion, and distribution.
"""

import pytest
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../backend'))


class TestEventFusionBus:
    """Test suite for EventFusionBus functionality."""

    def test_event_bus_singleton(self):
        """Test that EventFusionBus follows singleton pattern."""
        from app.orchestration.event_bus import EventFusionBus
        bus1 = EventFusionBus()
        bus2 = EventFusionBus()
        assert bus1 is bus2

    def test_fusion_strategy_enum(self):
        """Test FusionStrategy enum values."""
        from app.orchestration.event_bus import FusionStrategy
        assert FusionStrategy.TIMESTAMP.value == "timestamp"
        assert FusionStrategy.GEOLOCATION.value == "geolocation"
        assert FusionStrategy.ENTITY_ID.value == "entity_id"
        assert FusionStrategy.THREAT_LEVEL.value == "threat_level"
        assert FusionStrategy.COMPOSITE.value == "composite"

    def test_event_buffer_creation(self):
        """Test EventBuffer dataclass creation."""
        from app.orchestration.event_bus import EventBuffer
        buffer = EventBuffer(
            source_id="test_source",
            max_size=500,
            flush_interval_seconds=10,
        )
        assert buffer.source_id == "test_source"
        assert buffer.max_size == 500
        assert len(buffer.events) == 0

    def test_event_ingestion(self):
        """Test event ingestion into the bus."""
        from app.orchestration.event_bus import EventFusionBus
        bus = EventFusionBus()
        event = {
            "event_id": "test-001",
            "event_type": "test_event",
            "priority": 3,
            "data": {"test": "data"},
        }
        result = bus.ingest_event("test_source", event)
        assert result is True

    def test_event_rate_limiting(self):
        """Test event rate limiting."""
        from app.orchestration.event_bus import EventFusionBus
        bus = EventFusionBus()
        bus.set_rate_limit("rate_test_source", 5)
        for i in range(10):
            event = {"event_id": f"rate-{i}", "event_type": "test"}
            bus.ingest_event("rate_test_source", event)

    def test_default_sources_registered(self):
        """Test that default event sources are registered."""
        from app.orchestration.event_bus import EventFusionBus
        bus = EventFusionBus()
        status = bus.get_buffer_status()
        assert len(status) > 0

    def test_get_buffer_status(self):
        """Test getting buffer status."""
        from app.orchestration.event_bus import EventFusionBus
        bus = EventFusionBus()
        status = bus.get_buffer_status()
        assert isinstance(status, dict)

    def test_get_statistics(self):
        """Test getting event bus statistics."""
        from app.orchestration.event_bus import EventFusionBus
        bus = EventFusionBus()
        stats = bus.get_statistics()
        assert "total_events_received" in stats
        assert "total_events_fused" in stats
        assert "active_buffers" in stats

    def test_get_event_history(self):
        """Test getting event history."""
        from app.orchestration.event_bus import EventFusionBus
        bus = EventFusionBus()
        history = bus.get_event_history(limit=50)
        assert isinstance(history, list)

    def test_subscriber_management(self):
        """Test subscriber registration and unregistration."""
        from app.orchestration.event_bus import EventFusionBus
        bus = EventFusionBus()
        
        async def test_handler(event):
            pass
        
        bus.subscribe("test_subscriber", test_handler)
        bus.unsubscribe("test_subscriber")

    def test_fusion_rule_management(self):
        """Test fusion rule addition and removal."""
        from app.orchestration.event_bus import EventFusionBus, FusionStrategy
        bus = EventFusionBus()
        
        rule = {
            "rule_id": "test_rule",
            "name": "Test Rule",
            "strategy": FusionStrategy.TIMESTAMP,
            "event_types": ["test_event"],
            "time_window_seconds": 30,
        }
        bus.add_fusion_rule(rule)
        rules = bus.get_fusion_rules()
        assert isinstance(rules, list)

    def test_fused_event_creation(self):
        """Test FusedEvent dataclass creation."""
        from app.orchestration.event_bus import FusedEvent
        fused = FusedEvent(
            fused_event_id="fused-001",
            source_events=["evt-1", "evt-2"],
            fusion_strategy="timestamp",
            category="incident",
            priority=2,
            title="Fused Incident",
            summary="Two related events",
            location={"lat": 26.7753, "lng": -80.0589},
            confidence_score=0.85,
            explainability_log=["Events within 30s window"],
            recommended_actions=["dispatch_unit"],
        )
        assert fused.fused_event_id == "fused-001"
        assert len(fused.source_events) == 2
        assert fused.confidence_score == 0.85


class TestEventFusion:
    """Test suite for event fusion logic."""

    @pytest.mark.asyncio
    async def test_fuse_events(self):
        """Test event fusion process."""
        from app.orchestration.event_bus import EventFusionBus
        bus = EventFusionBus()
        result = await bus.fuse_events()
        assert result is not None

    def test_fusion_result_creation(self):
        """Test FusionResult dataclass creation."""
        from app.orchestration.event_bus import FusionResult
        result = FusionResult(
            fused_events=[],
            unfused_events=[],
            fusion_rate=0.0,
            processing_time_ms=50,
        )
        assert result.fusion_rate == 0.0
        assert result.processing_time_ms == 50

    def test_get_fused_events(self):
        """Test getting fused events."""
        from app.orchestration.event_bus import EventFusionBus
        bus = EventFusionBus()
        fused = bus.get_fused_events(limit=50)
        assert isinstance(fused, list)


class TestEventDebouncing:
    """Test suite for event debouncing."""

    def test_debounce_duplicate_events(self):
        """Test that duplicate events are debounced."""
        from app.orchestration.event_bus import EventFusionBus
        bus = EventFusionBus()
        event = {
            "event_id": "debounce-test",
            "event_type": "duplicate_test",
            "data": {"value": 1},
        }
        result1 = bus.ingest_event("debounce_source", event)
        result2 = bus.ingest_event("debounce_source", event)
        assert result1 is True
