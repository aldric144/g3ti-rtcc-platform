"""
Test Suite 4: Event Correlation Engine Tests

Tests for Global Event Correlation Engine functionality.
"""

import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch


class TestEventCategories:
    """Tests for event category enumeration."""

    def test_event_category_political_exists(self):
        """Test that POLITICAL category is defined."""
        from backend.app.global_awareness.event_correlation_engine import EventCategory
        assert hasattr(EventCategory, "POLITICAL")

    def test_event_category_military_exists(self):
        """Test that MILITARY category is defined."""
        from backend.app.global_awareness.event_correlation_engine import EventCategory
        assert hasattr(EventCategory, "MILITARY")

    def test_event_category_economic_exists(self):
        """Test that ECONOMIC category is defined."""
        from backend.app.global_awareness.event_correlation_engine import EventCategory
        assert hasattr(EventCategory, "ECONOMIC")

    def test_event_category_social_exists(self):
        """Test that SOCIAL category is defined."""
        from backend.app.global_awareness.event_correlation_engine import EventCategory
        assert hasattr(EventCategory, "SOCIAL")

    def test_all_eight_categories_defined(self):
        """Test that all 8 event categories are defined."""
        from backend.app.global_awareness.event_correlation_engine import EventCategory
        categories = list(EventCategory)
        assert len(categories) == 8


class TestCorrelationTypes:
    """Tests for correlation type enumeration."""

    def test_correlation_type_causal_exists(self):
        """Test that CAUSAL correlation type is defined."""
        from backend.app.global_awareness.event_correlation_engine import CorrelationType
        assert hasattr(CorrelationType, "CAUSAL")

    def test_correlation_type_temporal_exists(self):
        """Test that TEMPORAL correlation type is defined."""
        from backend.app.global_awareness.event_correlation_engine import CorrelationType
        assert hasattr(CorrelationType, "TEMPORAL")

    def test_correlation_type_spatial_exists(self):
        """Test that SPATIAL correlation type is defined."""
        from backend.app.global_awareness.event_correlation_engine import CorrelationType
        assert hasattr(CorrelationType, "SPATIAL")

    def test_all_six_correlation_types_defined(self):
        """Test that all 6 correlation types are defined."""
        from backend.app.global_awareness.event_correlation_engine import CorrelationType
        types = list(CorrelationType)
        assert len(types) == 6


class TestCascadeTypes:
    """Tests for cascade type enumeration."""

    def test_cascade_type_linear_exists(self):
        """Test that LINEAR cascade type is defined."""
        from backend.app.global_awareness.event_correlation_engine import CascadeType
        assert hasattr(CascadeType, "LINEAR")

    def test_cascade_type_branching_exists(self):
        """Test that BRANCHING cascade type is defined."""
        from backend.app.global_awareness.event_correlation_engine import CascadeType
        assert hasattr(CascadeType, "BRANCHING")

    def test_cascade_type_feedback_loop_exists(self):
        """Test that FEEDBACK_LOOP cascade type is defined."""
        from backend.app.global_awareness.event_correlation_engine import CascadeType
        assert hasattr(CascadeType, "FEEDBACK_LOOP")

    def test_all_five_cascade_types_defined(self):
        """Test that all 5 cascade types are defined."""
        from backend.app.global_awareness.event_correlation_engine import CascadeType
        types = list(CascadeType)
        assert len(types) == 5


class TestGlobalEvent:
    """Tests for GlobalEvent data class."""

    def test_global_event_creation(self):
        """Test creating a GlobalEvent instance."""
        from backend.app.global_awareness.event_correlation_engine import (
            GlobalEvent,
            EventCategory,
            ImpactMagnitude,
        )

        event = GlobalEvent(
            event_id="GE-001",
            category=EventCategory.MILITARY,
            title="Military Escalation",
            description="Significant troop movements detected",
            timestamp=datetime.utcnow(),
            location={"lat": 50.0, "lon": 36.0},
            affected_regions=["Eastern Europe"],
            affected_countries=["Ukraine", "Russia"],
            actors=["Russian Federation", "Ukraine"],
            impact_magnitude=ImpactMagnitude.SEVERE,
            confidence_score=0.92,
            source_signals=[],
            chain_of_custody_hash="test_hash",
        )

        assert event.event_id == "GE-001"
        assert event.category == EventCategory.MILITARY
        assert event.impact_magnitude == ImpactMagnitude.SEVERE


class TestEventCorrelation:
    """Tests for EventCorrelation data class."""

    def test_event_correlation_creation(self):
        """Test creating an EventCorrelation instance."""
        from backend.app.global_awareness.event_correlation_engine import (
            EventCorrelation,
            CorrelationType,
        )

        correlation = EventCorrelation(
            correlation_id="EC-001",
            source_event_id="GE-001",
            target_event_id="GE-002",
            correlation_type=CorrelationType.CAUSAL,
            strength=0.85,
            time_lag_hours=48,
            mechanism="Economic impact of conflict",
            evidence=["Historical precedent"],
            confidence=0.80,
            chain_of_custody_hash="test_hash",
        )

        assert correlation.correlation_id == "EC-001"
        assert correlation.correlation_type == CorrelationType.CAUSAL
        assert correlation.strength == 0.85


class TestEventCorrelationEngine:
    """Tests for EventCorrelationEngine class."""

    def test_correlation_engine_singleton(self):
        """Test that EventCorrelationEngine is a singleton."""
        from backend.app.global_awareness.event_correlation_engine import EventCorrelationEngine

        engine1 = EventCorrelationEngine()
        engine2 = EventCorrelationEngine()
        assert engine1 is engine2

    def test_correlation_engine_has_events_storage(self):
        """Test that correlation engine has events storage."""
        from backend.app.global_awareness.event_correlation_engine import EventCorrelationEngine

        engine = EventCorrelationEngine()
        assert hasattr(engine, "events")

    def test_correlation_engine_has_correlations_storage(self):
        """Test that correlation engine has correlations storage."""
        from backend.app.global_awareness.event_correlation_engine import EventCorrelationEngine

        engine = EventCorrelationEngine()
        assert hasattr(engine, "correlations")

    def test_correlation_engine_has_cascade_templates(self):
        """Test that correlation engine has cascade templates."""
        from backend.app.global_awareness.event_correlation_engine import EventCorrelationEngine

        engine = EventCorrelationEngine()
        assert hasattr(engine, "cascade_templates")


class TestEventCreation:
    """Tests for event creation."""

    def test_create_event(self):
        """Test creating a new event."""
        from backend.app.global_awareness.event_correlation_engine import (
            EventCorrelationEngine,
            EventCategory,
        )

        engine = EventCorrelationEngine()
        event = engine.create_event(
            category=EventCategory.POLITICAL,
            title="Diplomatic Tensions Rise",
            description="Multiple countries recall ambassadors",
            lat=48.8,
            lon=2.3,
            affected_regions=["Western Europe"],
            affected_countries=["France", "Germany"],
            actors=["EU", "NATO"],
            impact_magnitude=4,
            source_signals=[],
        )

        assert event is not None
        assert event.event_id.startswith("GE-")

    def test_create_event_auto_correlates(self):
        """Test that creating an event triggers auto-correlation."""
        from backend.app.global_awareness.event_correlation_engine import (
            EventCorrelationEngine,
            EventCategory,
        )

        engine = EventCorrelationEngine()

        event1 = engine.create_event(
            category=EventCategory.MILITARY,
            title="Military Action",
            description="Test event 1",
            lat=50.0,
            lon=36.0,
            affected_regions=["Eastern Europe"],
            affected_countries=["Ukraine"],
            actors=["Actor 1"],
            impact_magnitude=5,
            source_signals=[],
        )

        event2 = engine.create_event(
            category=EventCategory.ECONOMIC,
            title="Economic Impact",
            description="Test event 2",
            lat=50.0,
            lon=36.0,
            affected_regions=["Eastern Europe"],
            affected_countries=["Ukraine"],
            actors=["Actor 1"],
            impact_magnitude=4,
            source_signals=[],
        )

        correlations = engine.get_correlations_for_event(event2.event_id)
        assert isinstance(correlations, list)


class TestCorrelationCreation:
    """Tests for correlation creation."""

    def test_create_correlation(self):
        """Test creating a correlation between events."""
        from backend.app.global_awareness.event_correlation_engine import (
            EventCorrelationEngine,
            EventCategory,
            CorrelationType,
        )

        engine = EventCorrelationEngine()

        event1 = engine.create_event(
            category=EventCategory.MILITARY,
            title="Event 1",
            description="Test",
            lat=0.0,
            lon=0.0,
            affected_regions=[],
            affected_countries=[],
            actors=[],
            impact_magnitude=3,
            source_signals=[],
        )

        event2 = engine.create_event(
            category=EventCategory.POLITICAL,
            title="Event 2",
            description="Test",
            lat=0.0,
            lon=0.0,
            affected_regions=[],
            affected_countries=[],
            actors=[],
            impact_magnitude=3,
            source_signals=[],
        )

        correlation = engine.create_correlation(
            source_event_id=event1.event_id,
            target_event_id=event2.event_id,
            correlation_type=CorrelationType.CAUSAL,
            mechanism="Direct causation",
            evidence=["Test evidence"],
        )

        assert correlation is not None
        assert correlation.correlation_id.startswith("EC-")


class TestCascadePrediction:
    """Tests for cascade effect prediction."""

    def test_predict_cascade(self):
        """Test predicting cascade effects."""
        from backend.app.global_awareness.event_correlation_engine import (
            EventCorrelationEngine,
            EventCategory,
        )

        engine = EventCorrelationEngine()

        event = engine.create_event(
            category=EventCategory.MILITARY,
            title="Trigger Event",
            description="Test trigger",
            lat=50.0,
            lon=36.0,
            affected_regions=["Eastern Europe"],
            affected_countries=["Ukraine"],
            actors=["Actor"],
            impact_magnitude=5,
            source_signals=[],
        )

        cascade = engine.predict_cascade(
            trigger_event_id=event.event_id,
            time_horizon_days=30,
        )

        assert cascade is not None
        assert cascade.cascade_id.startswith("CE-")
        assert cascade.trigger_event_id == event.event_id

    def test_cascade_includes_propagation_path(self):
        """Test that cascade includes propagation path."""
        from backend.app.global_awareness.event_correlation_engine import (
            EventCorrelationEngine,
            EventCategory,
        )

        engine = EventCorrelationEngine()

        event = engine.create_event(
            category=EventCategory.ECONOMIC,
            title="Economic Crisis",
            description="Test",
            lat=0.0,
            lon=0.0,
            affected_regions=["Global"],
            affected_countries=[],
            actors=[],
            impact_magnitude=5,
            source_signals=[],
        )

        cascade = engine.predict_cascade(
            trigger_event_id=event.event_id,
            time_horizon_days=60,
        )

        assert cascade.propagation_path is not None
        assert isinstance(cascade.propagation_path, list)

    def test_cascade_includes_mitigation_options(self):
        """Test that cascade includes mitigation options."""
        from backend.app.global_awareness.event_correlation_engine import (
            EventCorrelationEngine,
            EventCategory,
        )

        engine = EventCorrelationEngine()

        event = engine.create_event(
            category=EventCategory.HEALTH,
            title="Pandemic Outbreak",
            description="Test",
            lat=0.0,
            lon=0.0,
            affected_regions=["Global"],
            affected_countries=[],
            actors=[],
            impact_magnitude=5,
            source_signals=[],
        )

        cascade = engine.predict_cascade(
            trigger_event_id=event.event_id,
            time_horizon_days=90,
        )

        assert cascade.mitigation_options is not None
        assert isinstance(cascade.mitigation_options, list)


class TestPatternDetection:
    """Tests for pattern detection."""

    def test_detect_patterns(self):
        """Test detecting event patterns."""
        from backend.app.global_awareness.event_correlation_engine import EventCorrelationEngine

        engine = EventCorrelationEngine()
        patterns = engine.detect_patterns(min_frequency=2)

        assert isinstance(patterns, list)


class TestTimelineReconstruction:
    """Tests for timeline reconstruction."""

    def test_reconstruct_timeline(self):
        """Test reconstructing event timeline."""
        from backend.app.global_awareness.event_correlation_engine import (
            EventCorrelationEngine,
            EventCategory,
        )

        engine = EventCorrelationEngine()

        event_ids = []
        for i in range(3):
            event = engine.create_event(
                category=EventCategory.POLITICAL,
                title=f"Event {i}",
                description="Test",
                lat=0.0,
                lon=0.0,
                affected_regions=["Test Region"],
                affected_countries=[],
                actors=[],
                impact_magnitude=3,
                source_signals=[],
            )
            event_ids.append(event.event_id)

        timeline = engine.reconstruct_timeline(event_ids)

        assert timeline is not None
        assert hasattr(timeline, "events")
        assert hasattr(timeline, "narrative")


class TestEventQueries:
    """Tests for event query methods."""

    def test_get_event_by_id(self):
        """Test getting event by ID."""
        from backend.app.global_awareness.event_correlation_engine import (
            EventCorrelationEngine,
            EventCategory,
        )

        engine = EventCorrelationEngine()

        created = engine.create_event(
            category=EventCategory.SECURITY,
            title="Test Event",
            description="Test",
            lat=0.0,
            lon=0.0,
            affected_regions=[],
            affected_countries=[],
            actors=[],
            impact_magnitude=3,
            source_signals=[],
        )

        retrieved = engine.get_event(created.event_id)
        assert retrieved is not None
        assert retrieved.event_id == created.event_id

    def test_get_recent_events(self):
        """Test getting recent events."""
        from backend.app.global_awareness.event_correlation_engine import EventCorrelationEngine

        engine = EventCorrelationEngine()
        events = engine.get_recent_events(hours=24)
        assert isinstance(events, list)

    def test_get_events_by_category(self):
        """Test getting events by category."""
        from backend.app.global_awareness.event_correlation_engine import (
            EventCorrelationEngine,
            EventCategory,
        )

        engine = EventCorrelationEngine()
        events = engine.get_events_by_category(EventCategory.MILITARY)
        assert isinstance(events, list)
