"""
Tests for ETL Pipeline module.
"""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import sys
sys.path.insert(0, "/home/ubuntu/repos/g3ti-rtcc-platform/backend")

from app.etl.pipeline import (
    ETLPipeline,
    PipelineConfig,
    PipelineStatus,
    PipelineStage,
    PipelineMetrics,
    PipelineRun,
    PipelineManager,
)


class TestPipelineConfig:
    """Tests for PipelineConfig model."""

    def test_default_config(self):
        """Test default pipeline configuration."""
        config = PipelineConfig()

        assert config.batch_size == 1000
        assert config.max_retries == 3
        assert config.timeout_seconds == 300
        assert config.parallel_workers == 4
        assert config.validation_enabled is True
        assert config.deduplication_enabled is True
        assert config.quality_threshold == 0.95

    def test_custom_config(self):
        """Test custom pipeline configuration."""
        config = PipelineConfig(
            batch_size=500,
            max_retries=5,
            timeout_seconds=600,
            parallel_workers=8,
            validation_enabled=False,
            quality_threshold=0.90,
        )

        assert config.batch_size == 500
        assert config.max_retries == 5
        assert config.parallel_workers == 8
        assert config.validation_enabled is False


class TestPipelineMetrics:
    """Tests for PipelineMetrics model."""

    def test_create_metrics(self):
        """Test creating pipeline metrics."""
        metrics = PipelineMetrics(
            records_extracted=1000,
            records_transformed=980,
            records_validated=950,
            records_loaded=950,
            errors=50,
            duration_seconds=120.5,
        )

        assert metrics.records_extracted == 1000
        assert metrics.records_loaded == 950
        assert metrics.errors == 50

    def test_metrics_throughput(self):
        """Test throughput calculation."""
        metrics = PipelineMetrics(
            records_extracted=1000,
            records_loaded=1000,
            duration_seconds=100.0,
        )

        assert metrics.throughput == 10.0  # 1000 / 100


class TestPipelineRun:
    """Tests for PipelineRun model."""

    def test_create_run(self):
        """Test creating a pipeline run."""
        run = PipelineRun(
            id="run-001",
            pipeline_name="test_pipeline",
            status=PipelineStatus.RUNNING,
            stage=PipelineStage.EXTRACT,
        )

        assert run.id == "run-001"
        assert run.status == PipelineStatus.RUNNING
        assert run.stage == PipelineStage.EXTRACT

    def test_run_with_metrics(self):
        """Test run with metrics."""
        metrics = PipelineMetrics(
            records_extracted=500,
            records_loaded=480,
        )

        run = PipelineRun(
            id="run-002",
            pipeline_name="test_pipeline",
            status=PipelineStatus.COMPLETED,
            stage=PipelineStage.COMPLETE,
            metrics=metrics,
        )

        assert run.metrics.records_extracted == 500
        assert run.metrics.records_loaded == 480


class TestETLPipeline:
    """Tests for ETLPipeline class."""

    def test_pipeline_initialization(self):
        """Test pipeline initialization."""
        config = PipelineConfig(batch_size=500)
        pipeline = ETLPipeline(
            name="test_pipeline",
            config=config,
        )

        assert pipeline.name == "test_pipeline"
        assert pipeline.config.batch_size == 500

    @pytest.mark.asyncio
    async def test_pipeline_execute_success(self):
        """Test successful pipeline execution."""
        config = PipelineConfig()
        pipeline = ETLPipeline(name="test_pipeline", config=config)

        # Mock the stage methods
        pipeline._execute_extract = AsyncMock(return_value=[{"id": 1}, {"id": 2}])
        pipeline._execute_transform = AsyncMock(return_value=[{"id": 1}, {"id": 2}])
        pipeline._execute_validate = AsyncMock(return_value=[{"id": 1}, {"id": 2}])
        pipeline._execute_load = AsyncMock(return_value=2)

        result = await pipeline.execute(
            source_params={"source": "test"},
            target_params={"target": "test"},
        )

        assert result.status == PipelineStatus.COMPLETED
        assert result.metrics.records_loaded == 2

    @pytest.mark.asyncio
    async def test_pipeline_execute_with_errors(self):
        """Test pipeline execution with errors."""
        config = PipelineConfig()
        pipeline = ETLPipeline(name="test_pipeline", config=config)

        # Mock extract to raise an error
        pipeline._execute_extract = AsyncMock(side_effect=Exception("Extract failed"))

        result = await pipeline.execute(
            source_params={"source": "test"},
            target_params={"target": "test"},
        )

        assert result.status == PipelineStatus.FAILED
        assert len(result.errors) > 0

    def test_pipeline_stop(self):
        """Test stopping a pipeline."""
        pipeline = ETLPipeline(name="test_pipeline")
        pipeline._running = True

        pipeline.stop()

        assert pipeline._running is False


class TestPipelineManager:
    """Tests for PipelineManager class."""

    def test_register_pipeline(self):
        """Test registering a pipeline."""
        manager = PipelineManager()
        pipeline = ETLPipeline(name="test_pipeline")

        manager.register_pipeline(pipeline)

        assert "test_pipeline" in manager._pipelines
        assert manager._pipelines["test_pipeline"] == pipeline

    def test_get_pipeline(self):
        """Test getting a registered pipeline."""
        manager = PipelineManager()
        pipeline = ETLPipeline(name="test_pipeline")
        manager.register_pipeline(pipeline)

        result = manager.get_pipeline("test_pipeline")

        assert result == pipeline

    def test_get_nonexistent_pipeline(self):
        """Test getting a non-existent pipeline."""
        manager = PipelineManager()

        result = manager.get_pipeline("nonexistent")

        assert result is None

    @pytest.mark.asyncio
    async def test_execute_pipeline(self):
        """Test executing a pipeline through manager."""
        manager = PipelineManager()
        pipeline = ETLPipeline(name="test_pipeline")
        pipeline.execute = AsyncMock(return_value=PipelineRun(
            id="run-001",
            pipeline_name="test_pipeline",
            status=PipelineStatus.COMPLETED,
            stage=PipelineStage.COMPLETE,
        ))
        manager.register_pipeline(pipeline)

        result = await manager.execute_pipeline(
            "test_pipeline",
            source_params={},
            target_params={},
        )

        assert result.status == PipelineStatus.COMPLETED

    def test_get_run_history(self):
        """Test getting run history."""
        manager = PipelineManager()

        # Add some mock runs
        manager._run_history["test_pipeline"] = [
            PipelineRun(
                id="run-001",
                pipeline_name="test_pipeline",
                status=PipelineStatus.COMPLETED,
                stage=PipelineStage.COMPLETE,
            ),
            PipelineRun(
                id="run-002",
                pipeline_name="test_pipeline",
                status=PipelineStatus.FAILED,
                stage=PipelineStage.TRANSFORM,
            ),
        ]

        history = manager.get_run_history("test_pipeline")

        assert len(history) == 2
        assert history[0].id == "run-001"
