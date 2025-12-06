"""
AI Engine Pipelines.

This module contains the base pipeline classes and implementations for
processing data through the AI Intelligence Engine.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Generic, TypeVar

from app.core.logging import get_logger

logger = get_logger(__name__)

InputT = TypeVar("InputT")
OutputT = TypeVar("OutputT")


@dataclass
class PipelineContext:
    """Context passed through pipeline stages."""

    request_id: str
    user_id: str | None = None
    role: str | None = None
    started_at: datetime = field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def add_error(self, error: str) -> None:
        """Add an error to the context."""
        self.errors.append(error)
        logger.error("pipeline_error", request_id=self.request_id, error=error)

    def add_warning(self, warning: str) -> None:
        """Add a warning to the context."""
        self.warnings.append(warning)
        logger.warning("pipeline_warning", request_id=self.request_id, warning=warning)


class BasePipeline(ABC, Generic[InputT, OutputT]):
    """
    Abstract base class for all AI pipelines.

    Pipelines process input data through a series of stages to produce
    output results. They support dependency injection for swappable components.
    """

    def __init__(self, name: str) -> None:
        """Initialize the pipeline."""
        self.name = name
        self._stages: list[PipelineStage[Any, Any]] = []
        self._initialized = False

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the pipeline and its dependencies."""
        pass

    @abstractmethod
    async def process(self, input_data: InputT, context: PipelineContext) -> OutputT:
        """
        Process input data through the pipeline.

        Args:
            input_data: The input data to process
            context: Pipeline context with request metadata

        Returns:
            The processed output
        """
        pass

    @abstractmethod
    async def shutdown(self) -> None:
        """Shutdown the pipeline and release resources."""
        pass

    def add_stage(self, stage: "PipelineStage[Any, Any]") -> None:
        """Add a stage to the pipeline."""
        self._stages.append(stage)

    async def run_stages(self, data: Any, context: PipelineContext) -> Any:
        """Run all stages in sequence."""
        current_data = data
        for stage in self._stages:
            try:
                current_data = await stage.execute(current_data, context)
            except Exception as e:
                context.add_error(f"Stage {stage.name} failed: {str(e)}")
                if stage.required:
                    raise
        return current_data


class PipelineStage(ABC, Generic[InputT, OutputT]):
    """
    Abstract base class for pipeline stages.

    Each stage performs a specific transformation or analysis on the data.
    """

    def __init__(self, name: str, required: bool = True) -> None:
        """Initialize the stage."""
        self.name = name
        self.required = required

    @abstractmethod
    async def execute(self, input_data: InputT, context: PipelineContext) -> OutputT:
        """
        Execute the stage on input data.

        Args:
            input_data: The input data to process
            context: Pipeline context

        Returns:
            The processed output
        """
        pass


class BaseResolver(ABC):
    """
    Abstract base class for entity resolvers.

    Resolvers match and merge entities across different data sources.
    """

    def __init__(self, name: str) -> None:
        """Initialize the resolver."""
        self.name = name

    @abstractmethod
    async def resolve(
        self, entities: list[dict[str, Any]], context: PipelineContext
    ) -> list[dict[str, Any]]:
        """
        Resolve and merge entities.

        Args:
            entities: List of entities to resolve
            context: Pipeline context

        Returns:
            List of resolved entities with merge candidates
        """
        pass

    @abstractmethod
    async def calculate_similarity(
        self, entity1: dict[str, Any], entity2: dict[str, Any]
    ) -> float:
        """
        Calculate similarity between two entities.

        Args:
            entity1: First entity
            entity2: Second entity

        Returns:
            Similarity score between 0 and 1
        """
        pass


class BasePredictor(ABC):
    """
    Abstract base class for predictive models.

    Predictors analyze historical data to make predictions about future events.
    """

    def __init__(self, name: str) -> None:
        """Initialize the predictor."""
        self.name = name
        self._model_loaded = False

    @abstractmethod
    async def load_model(self) -> None:
        """Load the prediction model."""
        pass

    @abstractmethod
    async def predict(
        self, input_data: dict[str, Any], context: PipelineContext
    ) -> dict[str, Any]:
        """
        Make a prediction based on input data.

        Args:
            input_data: Input features for prediction
            context: Pipeline context

        Returns:
            Prediction results
        """
        pass

    @abstractmethod
    async def train(self, training_data: list[dict[str, Any]]) -> None:
        """
        Train or update the model with new data.

        Args:
            training_data: Training data
        """
        pass


class BaseDetector(ABC):
    """
    Abstract base class for anomaly detectors.

    Detectors identify unusual patterns or deviations in data.
    """

    def __init__(self, name: str) -> None:
        """Initialize the detector."""
        self.name = name

    @abstractmethod
    async def detect(
        self, data: list[dict[str, Any]], context: PipelineContext
    ) -> list[dict[str, Any]]:
        """
        Detect anomalies in the data.

        Args:
            data: Data to analyze
            context: Pipeline context

        Returns:
            List of detected anomalies
        """
        pass

    @abstractmethod
    async def update_baseline(self, data: list[dict[str, Any]]) -> None:
        """
        Update the baseline for anomaly detection.

        Args:
            data: New baseline data
        """
        pass


class QueryPipeline(BasePipeline[str, dict[str, Any]]):
    """Pipeline for processing natural language queries."""

    def __init__(self) -> None:
        """Initialize the query pipeline."""
        super().__init__("query_pipeline")

    async def initialize(self) -> None:
        """Initialize the query pipeline."""
        self._initialized = True
        logger.info("query_pipeline_initialized")

    async def process(
        self, input_data: str, context: PipelineContext
    ) -> dict[str, Any]:
        """Process a natural language query."""
        return await self.run_stages(input_data, context)

    async def shutdown(self) -> None:
        """Shutdown the query pipeline."""
        self._initialized = False
        logger.info("query_pipeline_shutdown")


class AnalysisPipeline(BasePipeline[dict[str, Any], dict[str, Any]]):
    """Pipeline for analyzing entities and events."""

    def __init__(self) -> None:
        """Initialize the analysis pipeline."""
        super().__init__("analysis_pipeline")

    async def initialize(self) -> None:
        """Initialize the analysis pipeline."""
        self._initialized = True
        logger.info("analysis_pipeline_initialized")

    async def process(
        self, input_data: dict[str, Any], context: PipelineContext
    ) -> dict[str, Any]:
        """Process analysis request."""
        return await self.run_stages(input_data, context)

    async def shutdown(self) -> None:
        """Shutdown the analysis pipeline."""
        self._initialized = False
        logger.info("analysis_pipeline_shutdown")


__all__ = [
    "PipelineContext",
    "BasePipeline",
    "PipelineStage",
    "BaseResolver",
    "BasePredictor",
    "BaseDetector",
    "QueryPipeline",
    "AnalysisPipeline",
]
