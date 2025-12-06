"""
G3TI RTCC-UIP AI Intelligence Engine.

This module provides the unified AI Intelligence Layer for the Real Time Crime Center,
enabling correlation, entity resolution, pattern discovery, anomaly detection,
and natural-language investigative queries.

Components:
- ai_manager: Central orchestrator for all AI operations
- models: Data classes for AI results and entities
- pipelines: Analysis pipelines for processing data
- nlp: LLM-based query interpreter for natural language queries
- anomaly_detection: Anomaly detection engine
- pattern_recognition: Pattern recognition and prediction
- entity_resolution: Entity resolution and alias matching
- predictive_models: Predictive intelligence modules
"""

from app.ai_engine.ai_manager import AIManager, get_ai_manager
from app.ai_engine.models import (
    AIQueryResult,
    AnomalyResult,
    EntityMatch,
    PatternResult,
    PredictionResult,
    RiskScore,
)

__all__ = [
    "AIManager",
    "get_ai_manager",
    "AIQueryResult",
    "AnomalyResult",
    "EntityMatch",
    "PatternResult",
    "PredictionResult",
    "RiskScore",
]
