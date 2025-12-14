"""
Phase 34: AI Personas Framework

Operational AI Personas (Apex AI Officers) - Multi-Role Autonomous Assistants
for Command, Patrol, Intel & Crisis operations.

Modules:
- persona_engine: Core persona architecture and management
- interaction_engine: Natural language interaction and routing
- mission_reasoner: Mission planning and task execution
- compliance_layer: Integration with governance frameworks
"""

from backend.app.personas.persona_engine import (
    PersonaEngine,
    PersonaType,
    PersonaStatus,
    PersonaRole,
    EmotionalState,
    Persona,
    PersonaMemory,
    MissionContext,
)
from backend.app.personas.interaction_engine import (
    InteractionEngine,
    InteractionType,
    IntentCategory,
    UrgencyLevel,
    ConversationTurn,
    InteractionSession,
)
from backend.app.personas.mission_reasoner import (
    MissionReasoner,
    MissionStatus,
    MissionPriority,
    TaskType,
    Mission,
    MissionTask,
    MissionOutcome,
)

__all__ = [
    "PersonaEngine",
    "PersonaType",
    "PersonaStatus",
    "PersonaRole",
    "EmotionalState",
    "Persona",
    "PersonaMemory",
    "MissionContext",
    "InteractionEngine",
    "InteractionType",
    "IntentCategory",
    "UrgencyLevel",
    "ConversationTurn",
    "InteractionSession",
    "MissionReasoner",
    "MissionStatus",
    "MissionPriority",
    "TaskType",
    "Mission",
    "MissionTask",
    "MissionOutcome",
]
