"""
Phase 38: System-Wide Orchestration Engine (SWOE)
The Brainstem of the Entire RTCC Platform

This module provides unified orchestration across all RTCC subsystems:
- Drones, Robotics, Dispatch, Investigations
- AI, City Autonomy, Threat Intelligence
- Digital Twin, Human Stability Engine
- Officer Assist, Predictive Analytics

Components:
- OrchestrationKernel: Master orchestrator managing workflows
- EventRouter: Subscribes to all WebSocket channels, normalizes events
- WorkflowEngine: Implements multi-step automated workflows
- PolicyBindingEngine: Binds workflows to governance and legal guardrails
- ResourceManager: Manages shared assets across subsystems
- EventFusionBus: Central nervous system for event processing
"""

from .orchestration_kernel import (
    OrchestrationKernel,
    OrchestrationStatus,
    OrchestrationAction,
    OrchestrationResult,
)
from .event_router import (
    EventRouter,
    NormalizedEvent,
    EventSchema,
    RoutingRule,
)
from .workflow_engine import (
    WorkflowEngine,
    Workflow,
    WorkflowStep,
    WorkflowStatus,
    WorkflowTrigger,
)
from .policy_binding_engine import (
    PolicyBindingEngine,
    PolicyBinding,
    PolicyType,
    GuardrailCheck,
)
from .resource_manager import (
    ResourceManager,
    ResourceType,
    ResourceAllocation,
    ResourceStatus,
)
from .event_bus import (
    EventFusionBus,
    FusedEvent,
    EventBuffer,
    FusionResult,
)

__all__ = [
    "OrchestrationKernel",
    "OrchestrationStatus",
    "OrchestrationAction",
    "OrchestrationResult",
    "EventRouter",
    "NormalizedEvent",
    "EventSchema",
    "RoutingRule",
    "WorkflowEngine",
    "Workflow",
    "WorkflowStep",
    "WorkflowStatus",
    "WorkflowTrigger",
    "PolicyBindingEngine",
    "PolicyBinding",
    "PolicyType",
    "GuardrailCheck",
    "ResourceManager",
    "ResourceType",
    "ResourceAllocation",
    "ResourceStatus",
    "EventFusionBus",
    "FusedEvent",
    "EventBuffer",
    "FusionResult",
]
