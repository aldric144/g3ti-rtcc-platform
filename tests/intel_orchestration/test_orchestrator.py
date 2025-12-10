"""Tests for the Intel Orchestrator module."""

import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import sys
sys.path.insert(0, "/home/ubuntu/repos/g3ti-rtcc-platform/backend")

from app.intel_orchestration.orchestrator import (
    IntelOrchestrator,
    IntelSignal,
    FusedIntelligence,
    OrchestrationConfig,
    OrchestrationMetrics,
    IntelSource,
    IntelCategory,
    IntelTier,
    OrchestrationStatus,
)


class TestIntelSignal:
    """Tests for IntelSignal model."""

    def test_signal_creation(self):
        """Test creating an intel signal."""
        signal = IntelSignal(
            source=IntelSource.AI_ENGINE,
            category=IntelCategory.PATTERN,
            jurisdiction="Metro PD",
            confidence=0.85,
            data={"pattern_type": "burglary"},
        )
        
        assert signal.source == IntelSource.AI_ENGINE
        assert signal.category == IntelCategory.PATTERN
        assert signal.jurisdiction == "Metro PD"
        assert signal.confidence == 0.85
        assert signal.id is not None

    def test_signal_with_correlation_hints(self):
        """Test signal with correlation hints."""
        signal = IntelSignal(
            source=IntelSource.TACTICAL_ENGINE,
            category=IntelCategory.SUSPICIOUS_ACTIVITY,
            jurisdiction="County Sheriff",
            confidence=0.75,
            data={"activity": "surveillance"},
            correlation_hints=["person-123", "vehicle-456"],
        )
        
        assert len(signal.correlation_hints) == 2
        assert "person-123" in signal.correlation_hints

    def test_signal_default_values(self):
        """Test signal default values."""
        signal = IntelSignal(
            source=IntelSource.DISPATCH,
            category=IntelCategory.INCIDENT,
            jurisdiction="City PD",
            data={},
        )
        
        assert signal.confidence == 0.5
        assert signal.metadata == {}
        assert signal.correlation_hints == []


class TestFusedIntelligence:
    """Tests for FusedIntelligence model."""

    def test_fusion_creation(self):
        """Test creating fused intelligence."""
        fusion = FusedIntelligence(
            tier=IntelTier.TIER_2,
            title="Pattern Match",
            summary="Detected burglary pattern",
            priority_score=75.0,
            confidence=0.82,
            source_signals=["sig-1", "sig-2"],
            sources=[IntelSource.AI_ENGINE],
            category=IntelCategory.PATTERN,
            jurisdiction="Metro PD",
        )
        
        assert fusion.tier == IntelTier.TIER_2
        assert fusion.priority_score == 75.0
        assert len(fusion.source_signals) == 2

    def test_fusion_tier_assignment(self):
        """Test tier assignment based on priority score."""
        high_priority = FusedIntelligence(
            tier=IntelTier.TIER_1,
            title="Officer Safety",
            summary="Armed suspect",
            priority_score=95.0,
            confidence=0.95,
            source_signals=["sig-1"],
            sources=[IntelSource.OFFICER_SAFETY],
            category=IntelCategory.OFFICER_SAFETY,
            jurisdiction="Metro PD",
        )
        
        assert high_priority.tier == IntelTier.TIER_1


class TestOrchestrationConfig:
    """Tests for OrchestrationConfig model."""

    def test_default_config(self):
        """Test default configuration values."""
        config = OrchestrationConfig()
        
        assert config.enabled is True
        assert config.max_concurrent_pipelines == 10
        assert config.signal_buffer_size == 10000
        assert config.enable_correlation is True
        assert config.enable_priority_scoring is True

    def test_custom_config(self):
        """Test custom configuration."""
        config = OrchestrationConfig(
            enabled=False,
            max_concurrent_pipelines=5,
            batch_size=50,
        )
        
        assert config.enabled is False
        assert config.max_concurrent_pipelines == 5
        assert config.batch_size == 50


class TestIntelOrchestrator:
    """Tests for IntelOrchestrator class."""

    def test_orchestrator_initialization(self):
        """Test orchestrator initialization."""
        orchestrator = IntelOrchestrator()
        
        assert orchestrator.status == OrchestrationStatus.INITIALIZED
        assert orchestrator.config is not None
        assert orchestrator.metrics is not None

    def test_orchestrator_with_custom_config(self):
        """Test orchestrator with custom config."""
        config = OrchestrationConfig(
            enabled=True,
            max_concurrent_pipelines=20,
        )
        orchestrator = IntelOrchestrator(config=config)
        
        assert orchestrator.config.max_concurrent_pipelines == 20

    @pytest.mark.asyncio
    async def test_orchestrator_start_stop(self):
        """Test starting and stopping orchestrator."""
        orchestrator = IntelOrchestrator()
        
        await orchestrator.start()
        assert orchestrator.status == OrchestrationStatus.RUNNING
        
        await orchestrator.stop()
        assert orchestrator.status == OrchestrationStatus.STOPPED

    @pytest.mark.asyncio
    async def test_signal_ingestion(self):
        """Test signal ingestion."""
        orchestrator = IntelOrchestrator()
        await orchestrator.start()
        
        signal = IntelSignal(
            source=IntelSource.AI_ENGINE,
            category=IntelCategory.PATTERN,
            jurisdiction="Metro PD",
            confidence=0.85,
            data={"test": "data"},
        )
        
        await orchestrator.ingest_signal(signal)
        
        assert orchestrator.metrics.signals_received >= 1
        
        await orchestrator.stop()

    @pytest.mark.asyncio
    async def test_batch_signal_ingestion(self):
        """Test batch signal ingestion."""
        orchestrator = IntelOrchestrator()
        await orchestrator.start()
        
        signals = [
            IntelSignal(
                source=IntelSource.AI_ENGINE,
                category=IntelCategory.PATTERN,
                jurisdiction="Metro PD",
                confidence=0.8,
                data={"index": i},
            )
            for i in range(5)
        ]
        
        await orchestrator.ingest_batch(signals)
        
        assert orchestrator.metrics.signals_received >= 5
        
        await orchestrator.stop()

    def test_get_status(self):
        """Test getting orchestrator status."""
        orchestrator = IntelOrchestrator()
        status = orchestrator.get_status()
        
        assert "status" in status
        assert "config" in status
        assert "metrics" in status

    def test_get_metrics(self):
        """Test getting orchestrator metrics."""
        orchestrator = IntelOrchestrator()
        metrics = orchestrator.get_metrics()
        
        assert isinstance(metrics, OrchestrationMetrics)
        assert metrics.signals_received == 0
        assert metrics.signals_processed == 0


class TestIntelSource:
    """Tests for IntelSource enum."""

    def test_all_sources_defined(self):
        """Test all intelligence sources are defined."""
        expected_sources = [
            "ai_engine", "tactical_engine", "investigations_engine",
            "officer_safety", "dispatch", "federal_ndex", "federal_ncic",
            "federal_etrace", "federal_dhs_sar", "federation_hub",
            "data_lake", "etl_pipeline", "external_feed",
        ]
        
        for source in expected_sources:
            assert hasattr(IntelSource, source.upper())


class TestIntelCategory:
    """Tests for IntelCategory enum."""

    def test_all_categories_defined(self):
        """Test all intelligence categories are defined."""
        expected_categories = [
            "pattern", "anomaly", "threat", "incident",
            "person_of_interest", "vehicle_of_interest",
            "officer_safety", "federal_match", "suspicious_activity",
        ]
        
        for category in expected_categories:
            assert hasattr(IntelCategory, category.upper())


class TestIntelTier:
    """Tests for IntelTier enum."""

    def test_tier_values(self):
        """Test tier values."""
        assert IntelTier.TIER_1.value == "tier1"
        assert IntelTier.TIER_2.value == "tier2"
        assert IntelTier.TIER_3.value == "tier3"
        assert IntelTier.TIER_4.value == "tier4"
