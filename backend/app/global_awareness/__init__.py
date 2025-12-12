"""
Phase 32: Global Situation Awareness Engine (GSAE)

Multi-Domain Fusion Layer for global intelligence and risk assessment.

Modules:
- global_sensor_layer: Multi-domain global sensor ingestion
- knowledge_graph_engine: Entity relationships and influence mapping
- risk_fusion_engine: Global risk scoring across domains
- event_correlation_engine: Cause-effect cascade modeling
- satellite_analysis_layer: AI-based satellite imagery analysis
"""

from backend.app.global_awareness.global_sensor_layer import GlobalSensorLayer
from backend.app.global_awareness.knowledge_graph_engine import KnowledgeGraphEngine
from backend.app.global_awareness.risk_fusion_engine import RiskFusionEngine
from backend.app.global_awareness.event_correlation_engine import EventCorrelationEngine
from backend.app.global_awareness.satellite_analysis_layer import SatelliteAnalysisLayer

__all__ = [
    "GlobalSensorLayer",
    "KnowledgeGraphEngine",
    "RiskFusionEngine",
    "EventCorrelationEngine",
    "SatelliteAnalysisLayer",
]
