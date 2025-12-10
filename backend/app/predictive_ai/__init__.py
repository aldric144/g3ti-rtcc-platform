"""
Predictive Policing 3.0.

Phase 15: Provides ethical, transparent, and non-biased predictive analytics
including risk terrain modeling, violence cluster forecasting, patrol route
optimization, and suspect behavior prediction (trajectory only).
"""

from app.predictive_ai.risk_terrain import (
    RiskTerrainEngine,
    RiskFactor,
    RiskCell,
    TerrainModel,
)
from app.predictive_ai.violence_forecast import (
    ViolenceForecastEngine,
    ViolenceCluster,
    ClusterPrediction,
    TrendAnalysis,
)
from app.predictive_ai.patrol_optimizer import (
    PatrolOptimizer,
    PatrolRoute,
    PatrolZone,
    OptimizationResult,
)
from app.predictive_ai.behavior_prediction import (
    BehaviorPredictionEngine,
    TrajectoryPrediction,
    MovementPattern,
    PredictionConfidence,
)
from app.predictive_ai.bias_safeguards import (
    BiasSafeguardEngine,
    AuditRecord,
    BiasMetric,
    FairnessReport,
)

__all__ = [
    "RiskTerrainEngine",
    "RiskFactor",
    "RiskCell",
    "TerrainModel",
    "ViolenceForecastEngine",
    "ViolenceCluster",
    "ClusterPrediction",
    "TrendAnalysis",
    "PatrolOptimizer",
    "PatrolRoute",
    "PatrolZone",
    "OptimizationResult",
    "BehaviorPredictionEngine",
    "TrajectoryPrediction",
    "MovementPattern",
    "PredictionConfidence",
    "BiasSafeguardEngine",
    "AuditRecord",
    "BiasMetric",
    "FairnessReport",
]
