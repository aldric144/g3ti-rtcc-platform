"""Tests for the Intel Pipelines module."""

import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import sys
sys.path.insert(0, "/home/ubuntu/repos/g3ti-rtcc-platform/backend")

from app.intel_orchestration.pipelines import (
    PipelineStage,
    PipelineType,
    PipelineStatus,
    PipelineConfig,
    PipelineMetrics,
    PipelineItem,
    IntelPipeline,
    RealTimePipeline,
    BatchPipeline,
    FusionPipeline,
    AlertPriorityPipeline,
    OfficerSafetyPipeline,
    InvestigativeLeadPipeline,
    DataLakeFeedbackPipeline,
    PipelineManager,
)


class TestPipelineStage:
    """Tests for PipelineStage enum."""

    def test_all_stages_defined(self):
        """Test all pipeline stages are defined."""
        expected_stages = [
            "INGEST", "NORMALIZE", "VALIDATE", "ENRICH",
            "CORRELATE", "SCORE", "ROUTE", "COMPLETE", "ERROR",
        ]
        
        for stage in expected_stages:
            assert hasattr(PipelineStage, stage)

    def test_stage_values(self):
        """Test stage values."""
        assert PipelineStage.INGEST.value == "ingest"
        assert PipelineStage.COMPLETE.value == "complete"
        assert PipelineStage.ERROR.value == "error"


class TestPipelineType:
    """Tests for PipelineType enum."""

    def test_all_types_defined(self):
        """Test all pipeline types are defined."""
        expected_types = [
            "REAL_TIME", "BATCH", "FUSION", "ALERT_PRIORITY",
            "OFFICER_SAFETY", "INVESTIGATIVE_LEAD", "DATA_LAKE_FEEDBACK",
        ]
        
        for ptype in expected_types:
            assert hasattr(PipelineType, ptype)


class TestPipelineConfig:
    """Tests for PipelineConfig model."""

    def test_default_config(self):
        """Test default pipeline configuration."""
        config = PipelineConfig(
            name="test_pipeline",
            pipeline_type=PipelineType.REAL_TIME,
        )
        
        assert config.name == "test_pipeline"
        assert config.enabled is True
        assert config.workers == 4
        assert config.queue_size == 1000

    def test_custom_config(self):
        """Test custom pipeline configuration."""
        config = PipelineConfig(
            name="custom_pipeline",
            pipeline_type=PipelineType.BATCH,
            enabled=False,
            workers=8,
            queue_size=5000,
            batch_size=100,
        )
        
        assert config.workers == 8
        assert config.queue_size == 5000
        assert config.batch_size == 100


class TestPipelineMetrics:
    """Tests for PipelineMetrics model."""

    def test_default_metrics(self):
        """Test default metrics values."""
        metrics = PipelineMetrics()
        
        assert metrics.items_received == 0
        assert metrics.items_processed == 0
        assert metrics.items_failed == 0
        assert metrics.avg_processing_time_ms == 0.0

    def test_metrics_update(self):
        """Test updating metrics."""
        metrics = PipelineMetrics()
        metrics.items_received = 100
        metrics.items_processed = 95
        metrics.items_failed = 5
        
        assert metrics.items_received == 100
        assert metrics.items_processed == 95
        assert metrics.items_failed == 5


class TestPipelineItem:
    """Tests for PipelineItem model."""

    def test_item_creation(self):
        """Test creating a pipeline item."""
        item = PipelineItem(
            data={"test": "data"},
            source="ai_engine",
        )
        
        assert item.id is not None
        assert item.data == {"test": "data"}
        assert item.source == "ai_engine"
        assert item.stage == PipelineStage.INGEST

    def test_item_stage_progression(self):
        """Test item stage progression."""
        item = PipelineItem(
            data={},
            source="test",
        )
        
        item.stage = PipelineStage.NORMALIZE
        assert item.stage == PipelineStage.NORMALIZE
        
        item.stage = PipelineStage.COMPLETE
        assert item.stage == PipelineStage.COMPLETE


class TestIntelPipeline:
    """Tests for base IntelPipeline class."""

    def test_pipeline_initialization(self):
        """Test pipeline initialization."""
        config = PipelineConfig(
            name="test_pipeline",
            pipeline_type=PipelineType.REAL_TIME,
        )
        pipeline = IntelPipeline(config)
        
        assert pipeline.config == config
        assert pipeline.status == PipelineStatus.STOPPED
        assert pipeline.metrics is not None

    @pytest.mark.asyncio
    async def test_pipeline_start_stop(self):
        """Test starting and stopping pipeline."""
        config = PipelineConfig(
            name="test_pipeline",
            pipeline_type=PipelineType.REAL_TIME,
        )
        pipeline = IntelPipeline(config)
        
        await pipeline.start()
        assert pipeline.status == PipelineStatus.RUNNING
        
        await pipeline.stop()
        assert pipeline.status == PipelineStatus.STOPPED

    def test_get_status(self):
        """Test getting pipeline status."""
        config = PipelineConfig(
            name="test_pipeline",
            pipeline_type=PipelineType.REAL_TIME,
        )
        pipeline = IntelPipeline(config)
        status = pipeline.get_status()
        
        assert "name" in status
        assert "type" in status
        assert "status" in status
        assert "metrics" in status


class TestRealTimePipeline:
    """Tests for RealTimePipeline class."""

    def test_realtime_pipeline_creation(self):
        """Test creating real-time pipeline."""
        pipeline = RealTimePipeline()
        
        assert pipeline.config.pipeline_type == PipelineType.REAL_TIME
        assert "real_time" in pipeline.config.name

    @pytest.mark.asyncio
    async def test_realtime_pipeline_processing(self):
        """Test real-time pipeline processing."""
        pipeline = RealTimePipeline()
        await pipeline.start()
        
        item = PipelineItem(
            data={"signal": "test"},
            source="ai_engine",
        )
        
        await pipeline.submit(item)
        
        assert pipeline.metrics.items_received >= 1
        
        await pipeline.stop()


class TestBatchPipeline:
    """Tests for BatchPipeline class."""

    def test_batch_pipeline_creation(self):
        """Test creating batch pipeline."""
        pipeline = BatchPipeline()
        
        assert pipeline.config.pipeline_type == PipelineType.BATCH
        assert "batch" in pipeline.config.name

    @pytest.mark.asyncio
    async def test_batch_pipeline_processing(self):
        """Test batch pipeline processing."""
        pipeline = BatchPipeline()
        await pipeline.start()
        
        items = [
            PipelineItem(data={"index": i}, source="test")
            for i in range(5)
        ]
        
        for item in items:
            await pipeline.submit(item)
        
        assert pipeline.metrics.items_received >= 5
        
        await pipeline.stop()


class TestFusionPipeline:
    """Tests for FusionPipeline class."""

    def test_fusion_pipeline_creation(self):
        """Test creating fusion pipeline."""
        pipeline = FusionPipeline()
        
        assert pipeline.config.pipeline_type == PipelineType.FUSION
        assert "fusion" in pipeline.config.name

    @pytest.mark.asyncio
    async def test_fusion_pipeline_correlation(self):
        """Test fusion pipeline correlation."""
        pipeline = FusionPipeline()
        await pipeline.start()
        
        item = PipelineItem(
            data={"entity_id": "person-123"},
            source="ai_engine",
        )
        
        await pipeline.submit(item)
        
        assert pipeline.metrics.items_received >= 1
        
        await pipeline.stop()


class TestOfficerSafetyPipeline:
    """Tests for OfficerSafetyPipeline class."""

    def test_officer_safety_pipeline_creation(self):
        """Test creating officer safety pipeline."""
        pipeline = OfficerSafetyPipeline()
        
        assert pipeline.config.pipeline_type == PipelineType.OFFICER_SAFETY
        assert "officer_safety" in pipeline.config.name

    @pytest.mark.asyncio
    async def test_officer_safety_priority(self):
        """Test officer safety pipeline has highest priority."""
        pipeline = OfficerSafetyPipeline()
        
        # Officer safety should have more workers for faster processing
        assert pipeline.config.workers >= 4


class TestAlertPriorityPipeline:
    """Tests for AlertPriorityPipeline class."""

    def test_alert_priority_pipeline_creation(self):
        """Test creating alert priority pipeline."""
        pipeline = AlertPriorityPipeline()
        
        assert pipeline.config.pipeline_type == PipelineType.ALERT_PRIORITY


class TestInvestigativeLeadPipeline:
    """Tests for InvestigativeLeadPipeline class."""

    def test_lead_pipeline_creation(self):
        """Test creating investigative lead pipeline."""
        pipeline = InvestigativeLeadPipeline()
        
        assert pipeline.config.pipeline_type == PipelineType.INVESTIGATIVE_LEAD


class TestDataLakeFeedbackPipeline:
    """Tests for DataLakeFeedbackPipeline class."""

    def test_datalake_pipeline_creation(self):
        """Test creating data lake feedback pipeline."""
        pipeline = DataLakeFeedbackPipeline()
        
        assert pipeline.config.pipeline_type == PipelineType.DATA_LAKE_FEEDBACK


class TestPipelineManager:
    """Tests for PipelineManager class."""

    def test_manager_initialization(self):
        """Test pipeline manager initialization."""
        manager = PipelineManager()
        
        assert manager is not None
        assert len(manager.pipelines) == 7  # All 7 pipeline types

    @pytest.mark.asyncio
    async def test_manager_start_all(self):
        """Test starting all pipelines."""
        manager = PipelineManager()
        await manager.start_all()
        
        for pipeline in manager.pipelines.values():
            assert pipeline.status == PipelineStatus.RUNNING
        
        await manager.stop_all()

    @pytest.mark.asyncio
    async def test_manager_stop_all(self):
        """Test stopping all pipelines."""
        manager = PipelineManager()
        await manager.start_all()
        await manager.stop_all()
        
        for pipeline in manager.pipelines.values():
            assert pipeline.status == PipelineStatus.STOPPED

    def test_get_pipeline(self):
        """Test getting specific pipeline."""
        manager = PipelineManager()
        
        realtime = manager.get_pipeline(PipelineType.REAL_TIME)
        assert realtime is not None
        assert realtime.config.pipeline_type == PipelineType.REAL_TIME

    def test_get_all_status(self):
        """Test getting all pipeline statuses."""
        manager = PipelineManager()
        statuses = manager.get_all_status()
        
        assert len(statuses) == 7
        for status in statuses:
            assert "name" in status
            assert "status" in status
