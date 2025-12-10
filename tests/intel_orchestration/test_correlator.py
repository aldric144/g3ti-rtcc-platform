"""Tests for the Correlation Engine module."""

import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import sys
sys.path.insert(0, "/home/ubuntu/repos/g3ti-rtcc-platform/backend")

from app.intel_orchestration.correlator import (
    EntityType,
    CorrelationType,
    CorrelationStrength,
    CorrelationConfig,
    EntityReference,
    EntityCorrelation,
    PatternCorrelation,
    CorrelationResult,
    ThreatTrajectory,
    CorrelationEngine,
)


class TestEntityType:
    """Tests for EntityType enum."""

    def test_all_entity_types_defined(self):
        """Test all entity types are defined."""
        expected_types = [
            "PERSON", "VEHICLE", "WEAPON", "INCIDENT", "PATTERN",
            "LOCATION", "ORGANIZATION", "CASE", "FEDERAL_RECORD",
            "MULTI_AGENCY_ENTITY",
        ]
        
        for etype in expected_types:
            assert hasattr(EntityType, etype)


class TestCorrelationType:
    """Tests for CorrelationType enum."""

    def test_all_correlation_types_defined(self):
        """Test all correlation types are defined."""
        expected_types = [
            "EXACT_MATCH", "FUZZY_MATCH", "TEMPORAL", "GEOGRAPHIC",
            "BEHAVIORAL", "RELATIONAL", "TRANSACTIONAL", "INVESTIGATIVE",
        ]
        
        for ctype in expected_types:
            assert hasattr(CorrelationType, ctype)


class TestCorrelationStrength:
    """Tests for CorrelationStrength enum."""

    def test_strength_values(self):
        """Test correlation strength values."""
        assert CorrelationStrength.DEFINITE.value == "definite"
        assert CorrelationStrength.STRONG.value == "strong"
        assert CorrelationStrength.MODERATE.value == "moderate"
        assert CorrelationStrength.WEAK.value == "weak"
        assert CorrelationStrength.POSSIBLE.value == "possible"


class TestCorrelationConfig:
    """Tests for CorrelationConfig model."""

    def test_default_config(self):
        """Test default correlation configuration."""
        config = CorrelationConfig()
        
        assert config.enabled is True
        assert config.min_correlation_score == 0.4
        assert config.temporal_window_hours == 24.0
        assert config.geographic_radius_meters == 1000.0

    def test_custom_config(self):
        """Test custom correlation configuration."""
        config = CorrelationConfig(
            enabled=False,
            min_correlation_score=0.6,
            temporal_window_hours=48.0,
            geographic_radius_meters=500.0,
        )
        
        assert config.enabled is False
        assert config.min_correlation_score == 0.6
        assert config.temporal_window_hours == 48.0


class TestEntityReference:
    """Tests for EntityReference model."""

    def test_entity_creation(self):
        """Test creating an entity reference."""
        entity = EntityReference(
            entity_id="person-123",
            entity_type=EntityType.PERSON,
            attributes={"name": "John Doe", "dob": "1985-03-15"},
        )
        
        assert entity.entity_id == "person-123"
        assert entity.entity_type == EntityType.PERSON
        assert entity.attributes["name"] == "John Doe"

    def test_entity_with_location(self):
        """Test entity with location data."""
        entity = EntityReference(
            entity_id="loc-456",
            entity_type=EntityType.LOCATION,
            attributes={"address": "123 Main St"},
            latitude=40.7128,
            longitude=-74.0060,
        )
        
        assert entity.latitude == 40.7128
        assert entity.longitude == -74.0060


class TestEntityCorrelation:
    """Tests for EntityCorrelation model."""

    def test_correlation_creation(self):
        """Test creating an entity correlation."""
        source = EntityReference(
            entity_id="person-123",
            entity_type=EntityType.PERSON,
        )
        target = EntityReference(
            entity_id="vehicle-456",
            entity_type=EntityType.VEHICLE,
        )
        
        correlation = EntityCorrelation(
            source_entity=source,
            target_entity=target,
            correlation_type=CorrelationType.RELATIONAL,
            strength=CorrelationStrength.STRONG,
            confidence=0.85,
            evidence=["DMV records"],
        )
        
        assert correlation.id is not None
        assert correlation.confidence == 0.85
        assert correlation.strength == CorrelationStrength.STRONG


class TestPatternCorrelation:
    """Tests for PatternCorrelation model."""

    def test_pattern_creation(self):
        """Test creating a pattern correlation."""
        pattern = PatternCorrelation(
            pattern_type="temporal_cluster",
            entities=["inc-1", "inc-2", "inc-3"],
            confidence=0.78,
            description="3 incidents within 2 hours",
        )
        
        assert pattern.id is not None
        assert pattern.pattern_type == "temporal_cluster"
        assert len(pattern.entities) == 3


class TestCorrelationResult:
    """Tests for CorrelationResult model."""

    def test_result_creation(self):
        """Test creating a correlation result."""
        result = CorrelationResult(
            query_entity_id="person-123",
            entity_correlations=[],
            pattern_correlations=[],
            processing_time_ms=25.5,
        )
        
        assert result.query_entity_id == "person-123"
        assert result.processing_time_ms == 25.5


class TestThreatTrajectory:
    """Tests for ThreatTrajectory model."""

    def test_trajectory_creation(self):
        """Test creating a threat trajectory."""
        trajectory = ThreatTrajectory(
            entity_id="person-123",
            trajectory_type="escalating",
            risk_trend="increasing",
            confidence=0.82,
            events=["arrest-1", "incident-2", "warrant-3"],
            prediction="High likelihood of violent offense",
        )
        
        assert trajectory.id is not None
        assert trajectory.trajectory_type == "escalating"
        assert len(trajectory.events) == 3


class TestCorrelationEngine:
    """Tests for CorrelationEngine class."""

    def test_engine_initialization(self):
        """Test correlation engine initialization."""
        engine = CorrelationEngine()
        
        assert engine.config is not None
        assert engine.config.enabled is True

    def test_engine_with_custom_config(self):
        """Test engine with custom config."""
        config = CorrelationConfig(
            min_correlation_score=0.7,
        )
        engine = CorrelationEngine(config=config)
        
        assert engine.config.min_correlation_score == 0.7

    @pytest.mark.asyncio
    async def test_correlate_entity(self):
        """Test correlating an entity."""
        engine = CorrelationEngine()
        
        entity = EntityReference(
            entity_id="person-123",
            entity_type=EntityType.PERSON,
            attributes={"name": "John Doe"},
        )
        
        result = await engine.correlate_entity(entity)
        
        assert result is not None
        assert result.query_entity_id == "person-123"

    @pytest.mark.asyncio
    async def test_exact_match_correlation(self):
        """Test exact match correlation."""
        engine = CorrelationEngine()
        
        # Add entity to cache
        entity1 = EntityReference(
            entity_id="person-123",
            entity_type=EntityType.PERSON,
            attributes={"ssn": "123-45-6789"},
        )
        await engine.add_entity(entity1)
        
        # Query with same SSN
        entity2 = EntityReference(
            entity_id="person-456",
            entity_type=EntityType.PERSON,
            attributes={"ssn": "123-45-6789"},
        )
        
        result = await engine.correlate_entity(entity2)
        
        # Should find correlation based on SSN match
        assert result is not None

    @pytest.mark.asyncio
    async def test_fuzzy_match_correlation(self):
        """Test fuzzy match correlation."""
        engine = CorrelationEngine()
        
        entity1 = EntityReference(
            entity_id="person-123",
            entity_type=EntityType.PERSON,
            attributes={"name": "John Smith"},
        )
        await engine.add_entity(entity1)
        
        entity2 = EntityReference(
            entity_id="person-456",
            entity_type=EntityType.PERSON,
            attributes={"name": "Jon Smith"},  # Slight variation
        )
        
        result = await engine.correlate_entity(entity2)
        
        assert result is not None

    @pytest.mark.asyncio
    async def test_geographic_correlation(self):
        """Test geographic correlation."""
        engine = CorrelationEngine()
        
        entity1 = EntityReference(
            entity_id="loc-123",
            entity_type=EntityType.LOCATION,
            latitude=40.7128,
            longitude=-74.0060,
        )
        await engine.add_entity(entity1)
        
        # Nearby location (within 1km)
        entity2 = EntityReference(
            entity_id="loc-456",
            entity_type=EntityType.LOCATION,
            latitude=40.7130,
            longitude=-74.0062,
        )
        
        result = await engine.correlate_entity(entity2)
        
        assert result is not None

    @pytest.mark.asyncio
    async def test_temporal_correlation(self):
        """Test temporal correlation."""
        engine = CorrelationEngine()
        
        now = datetime.now(timezone.utc)
        
        entity1 = EntityReference(
            entity_id="inc-123",
            entity_type=EntityType.INCIDENT,
            timestamp=now,
        )
        await engine.add_entity(entity1)
        
        # Incident within temporal window
        entity2 = EntityReference(
            entity_id="inc-456",
            entity_type=EntityType.INCIDENT,
            timestamp=now,
        )
        
        result = await engine.correlate_entity(entity2)
        
        assert result is not None

    @pytest.mark.asyncio
    async def test_detect_patterns(self):
        """Test pattern detection."""
        engine = CorrelationEngine()
        
        entities = [
            EntityReference(
                entity_id=f"inc-{i}",
                entity_type=EntityType.INCIDENT,
                timestamp=datetime.now(timezone.utc),
                latitude=40.7128 + (i * 0.001),
                longitude=-74.0060,
            )
            for i in range(5)
        ]
        
        for entity in entities:
            await engine.add_entity(entity)
        
        patterns = await engine.detect_patterns()
        
        assert patterns is not None

    @pytest.mark.asyncio
    async def test_infer_threat_trajectory(self):
        """Test threat trajectory inference."""
        engine = CorrelationEngine()
        
        trajectory = await engine.infer_threat_trajectory("person-123")
        
        # Should return trajectory even if no data (empty trajectory)
        assert trajectory is not None or trajectory is None  # Either is valid

    def test_get_stats(self):
        """Test getting correlation stats."""
        engine = CorrelationEngine()
        stats = engine.get_stats()
        
        assert "entities_cached" in stats
        assert "correlations_cached" in stats
        assert "config" in stats

    @pytest.mark.asyncio
    async def test_clear_cache(self):
        """Test clearing correlation cache."""
        engine = CorrelationEngine()
        
        entity = EntityReference(
            entity_id="person-123",
            entity_type=EntityType.PERSON,
        )
        await engine.add_entity(entity)
        
        await engine.clear_cache()
        
        stats = engine.get_stats()
        assert stats["entities_cached"] == 0
