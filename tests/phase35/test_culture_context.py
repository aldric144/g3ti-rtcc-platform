"""
Test Suite: Cultural Context Engine

Phase 35: AI Moral Compass & Societal Ethics Reasoning Engine
Tests for cultural context and community sentiment modeling.
"""

import pytest
from datetime import datetime, timedelta

from backend.app.moral_compass.culture_context_engine import (
    CultureContextEngine,
    TrustLevel,
    VulnerabilityFactor,
    EventType,
    SentimentLevel,
    CulturalFactor,
    LocalEvent,
    NeighborhoodProfile,
    CommunityContext,
)


class TestTrustLevel:
    """Tests for TrustLevel enum."""

    def test_trust_levels_exist(self):
        levels = [
            TrustLevel.VERY_LOW,
            TrustLevel.LOW,
            TrustLevel.MODERATE,
            TrustLevel.HIGH,
            TrustLevel.VERY_HIGH,
        ]
        assert len(levels) == 5


class TestEventType:
    """Tests for EventType enum."""

    def test_event_types_exist(self):
        types = [
            EventType.FESTIVAL,
            EventType.FUNERAL,
            EventType.VIGIL,
            EventType.PROTEST,
            EventType.CELEBRATION,
            EventType.RELIGIOUS,
            EventType.COMMUNITY_MEETING,
            EventType.SPORTS,
            EventType.SCHOOL,
            EventType.EMERGENCY,
        ]
        assert len(types) == 10


class TestCultureContextEngine:
    """Tests for CultureContextEngine singleton."""

    def test_singleton_pattern(self):
        engine1 = CultureContextEngine()
        engine2 = CultureContextEngine()
        assert engine1 is engine2

    def test_initialization(self):
        engine = CultureContextEngine()
        assert engine._initialized is True
        assert len(engine.neighborhoods) > 0
        assert len(engine.cultural_factors) > 0

    def test_get_context_basic(self):
        engine = CultureContextEngine()
        context = engine.get_context(location="Downtown Riviera Beach")
        assert context is not None
        assert context.context_id is not None
        assert context.location == "Downtown Riviera Beach"

    def test_get_context_with_action(self):
        engine = CultureContextEngine()
        context = engine.get_context(
            location="Singer Island",
            action_type="patrol",
        )
        assert context is not None
        assert context.recommended_approach is not None

    def test_add_event(self):
        engine = CultureContextEngine()
        event = engine.add_event(
            name="Community Festival",
            event_type=EventType.FESTIVAL,
            location="Downtown Riviera Beach",
            start_time=datetime.utcnow(),
            end_time=datetime.utcnow() + timedelta(hours=4),
            expected_attendance=500,
            community_significance="high",
        )
        assert event is not None
        assert event.event_id is not None
        assert event.name == "Community Festival"

    def test_get_active_events(self):
        engine = CultureContextEngine()
        engine.add_event(
            name="Test Event",
            event_type=EventType.COMMUNITY_MEETING,
            location="West Riviera Beach",
            start_time=datetime.utcnow(),
        )
        events = engine.get_active_events_all()
        assert isinstance(events, list)

    def test_deactivate_event(self):
        engine = CultureContextEngine()
        event = engine.add_event(
            name="Temporary Event",
            event_type=EventType.SPORTS,
            location="Riviera Beach Heights",
            start_time=datetime.utcnow(),
        )
        result = engine.deactivate_event(event.event_id)
        assert result is True

    def test_update_neighborhood_trust(self):
        engine = CultureContextEngine()
        neighborhoods = engine.get_all_neighborhoods()
        if neighborhoods:
            result = engine.update_neighborhood_trust(
                neighborhood_id=neighborhoods[0].neighborhood_id,
                trust_level=TrustLevel.HIGH,
                reason="Community engagement success",
            )
            assert result is True

    def test_get_youth_vulnerability_context(self):
        engine = CultureContextEngine()
        context = engine.get_youth_vulnerability_context("Downtown Riviera Beach")
        assert context is not None
        assert "youth_vulnerability_score" in context
        assert "risk_factors" in context
        assert "protective_factors" in context

    def test_get_domestic_violence_context(self):
        engine = CultureContextEngine()
        context = engine.get_domestic_violence_context("West Riviera Beach")
        assert context is not None
        assert "cultural_barriers" in context
        assert "recommended_approach" in context

    def test_get_historical_trauma_context(self):
        engine = CultureContextEngine()
        context = engine.get_historical_trauma_context("Downtown Riviera Beach")
        assert context is not None
        assert "trauma_present" in context
        assert "trauma_factors" in context

    def test_model_community_sentiment(self):
        engine = CultureContextEngine()
        sentiment = engine.model_community_sentiment(
            location="Singer Island",
            recent_events=["positive_engagement"],
        )
        assert sentiment is not None
        assert "sentiment_level" in sentiment
        assert "confidence" in sentiment

    def test_get_all_neighborhoods(self):
        engine = CultureContextEngine()
        neighborhoods = engine.get_all_neighborhoods()
        assert isinstance(neighborhoods, list)
        assert len(neighborhoods) >= 5

    def test_get_neighborhood(self):
        engine = CultureContextEngine()
        neighborhoods = engine.get_all_neighborhoods()
        if neighborhoods:
            neighborhood = engine.get_neighborhood(neighborhoods[0].neighborhood_id)
            assert neighborhood is not None
            assert neighborhood.name is not None

    def test_get_statistics(self):
        engine = CultureContextEngine()
        stats = engine.get_statistics()
        assert "contexts_generated" in stats
        assert "events_tracked" in stats
        assert "neighborhoods_profiled" in stats


class TestCulturalFactor:
    """Tests for CulturalFactor dataclass."""

    def test_factor_creation(self):
        factor = CulturalFactor(
            factor_id="CF-001",
            name="Test Factor",
            description="A test cultural factor",
            weight=0.5,
            considerations=["consideration_1"],
        )
        assert factor.factor_id == "CF-001"
        assert factor.weight == 0.5

    def test_factor_to_dict(self):
        factor = CulturalFactor(
            factor_id="CF-002",
            name="Another Factor",
            description="Another test",
            weight=0.7,
            considerations=[],
        )
        data = factor.to_dict()
        assert data["factor_id"] == "CF-002"
        assert data["weight"] == 0.7


class TestLocalEvent:
    """Tests for LocalEvent dataclass."""

    def test_event_creation(self):
        event = LocalEvent(
            name="Test Event",
            event_type=EventType.FESTIVAL,
            location="Test Location",
            start_time=datetime.utcnow(),
        )
        assert event.event_id is not None
        assert event.active is True

    def test_event_to_dict(self):
        event = LocalEvent(
            name="Dict Event",
            event_type=EventType.VIGIL,
            location="Memorial Park",
            start_time=datetime.utcnow(),
            expected_attendance=100,
        )
        data = event.to_dict()
        assert data["name"] == "Dict Event"
        assert data["event_type"] == "vigil"


class TestNeighborhoodProfile:
    """Tests for NeighborhoodProfile dataclass."""

    def test_profile_creation(self):
        profile = NeighborhoodProfile(
            name="Test Neighborhood",
            trust_level=TrustLevel.MODERATE,
        )
        assert profile.neighborhood_id is not None
        assert profile.trust_level == TrustLevel.MODERATE

    def test_profile_to_dict(self):
        profile = NeighborhoodProfile(
            name="Dict Neighborhood",
            trust_level=TrustLevel.HIGH,
            vulnerability_factors=[VulnerabilityFactor.YOUTH],
            historical_trauma_score=0.3,
        )
        data = profile.to_dict()
        assert data["name"] == "Dict Neighborhood"
        assert data["trust_level"] == "high"


class TestCommunityContext:
    """Tests for CommunityContext dataclass."""

    def test_context_creation(self):
        context = CommunityContext(
            location="Test Location",
            trust_level=TrustLevel.MODERATE,
            sentiment=SentimentLevel.NEUTRAL,
        )
        assert context.context_id is not None
        assert context.trust_level == TrustLevel.MODERATE

    def test_context_hash(self):
        context = CommunityContext(
            location="Hash Test",
            trust_level=TrustLevel.LOW,
            sentiment=SentimentLevel.NEGATIVE,
        )
        assert context.context_hash is not None
        assert len(context.context_hash) == 16
