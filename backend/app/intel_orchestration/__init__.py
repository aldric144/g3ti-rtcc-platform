"""
Intelligence Orchestration Engine for G3TI RTCC-UIP.

This module provides the master fusion layer that coordinates all intelligence
sources, engines, and subsystems across the entire RTCC-UIP architecture.

Components:
- Orchestrator: Master controller for intelligence coordination
- Pipelines: Ingest, normalize, enrich, and route intelligence signals
- Correlator: Multi-engine entity and pattern fusion
- Rules Engine: Priority scoring and threat assessment
- Alerts Router: Routes intelligence to appropriate destinations
- Knowledge Graph Sync: Synchronizes output back to Neo4j
- Audit Log: CJIS-grade logging of all intelligence actions
"""

from .alerts_router import (
    AlertDestination,
    AlertPriority,
    AlertsRouter,
    RoutedAlert,
    RoutingConfig,
)
from .audit_log import (
    AuditAction,
    AuditConfig,
    AuditEntry,
    IntelAuditLog,
)
from .correlator import (
    CorrelationConfig,
    CorrelationEngine,
    CorrelationResult,
    EntityCorrelation,
    PatternCorrelation,
)
from .knowledge_graph_sync import (
    GraphSyncConfig,
    KnowledgeGraphSync,
    SyncOperation,
    SyncResult,
)
from .orchestrator import (
    FusedIntelligence,
    IntelOrchestrator,
    IntelSignal,
    OrchestrationConfig,
    OrchestrationStatus,
)
from .pipelines import (
    BatchPipeline,
    FusionPipeline,
    IntelPipeline,
    PipelineConfig,
    PipelineStage,
    RealTimePipeline,
)
from .rules_engine import (
    PriorityScore,
    RiskProfile,
    RulesEngine,
    ScoringRule,
    ThreatAssessment,
)

__all__ = [
    "IntelOrchestrator",
    "OrchestrationConfig",
    "OrchestrationStatus",
    "IntelSignal",
    "FusedIntelligence",
    "IntelPipeline",
    "PipelineConfig",
    "PipelineStage",
    "RealTimePipeline",
    "BatchPipeline",
    "FusionPipeline",
    "CorrelationEngine",
    "EntityCorrelation",
    "PatternCorrelation",
    "CorrelationResult",
    "CorrelationConfig",
    "RulesEngine",
    "PriorityScore",
    "ScoringRule",
    "ThreatAssessment",
    "RiskProfile",
    "AlertsRouter",
    "AlertDestination",
    "AlertPriority",
    "RoutedAlert",
    "RoutingConfig",
    "KnowledgeGraphSync",
    "GraphSyncConfig",
    "SyncOperation",
    "SyncResult",
    "IntelAuditLog",
    "AuditEntry",
    "AuditAction",
    "AuditConfig",
]
