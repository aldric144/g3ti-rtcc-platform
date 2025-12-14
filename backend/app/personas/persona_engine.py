"""
Persona Architecture Layer

Core module for AI Personas (Apex AI Officers) - specialized operational AI units
that assist every domain of the RTCC-UIP system.

Personas are governed by:
- AI Sentinel Supervisor (Phase 33)
- Constitutional Guardrails (Phase 28)
- City Autonomy Framework (Phase 24)
- Ethical Governance Engine
"""

import hashlib
import uuid
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set


class PersonaType(Enum):
    """Types of Apex AI Officers."""
    APEX_PATROL = "apex_patrol"
    APEX_COMMAND = "apex_command"
    APEX_INTEL = "apex_intel"
    APEX_CRISIS = "apex_crisis"
    APEX_ROBOTICS = "apex_robotics"
    APEX_INVESTIGATIONS = "apex_investigations"


class PersonaStatus(Enum):
    """Operational status of a persona."""
    ACTIVE = "active"
    STANDBY = "standby"
    BUSY = "busy"
    MAINTENANCE = "maintenance"
    OFFLINE = "offline"
    SUSPENDED = "suspended"


class PersonaRole(Enum):
    """Specific roles within persona types."""
    PATROL_ASSISTANT = "patrol_assistant"
    PATROL_SUPERVISOR = "patrol_supervisor"
    COMMAND_ADVISOR = "command_advisor"
    COMMAND_STRATEGIST = "command_strategist"
    INTEL_ANALYST = "intel_analyst"
    INTEL_FUSION = "intel_fusion"
    CRISIS_NEGOTIATOR = "crisis_negotiator"
    CRISIS_DEESCALATION = "crisis_deescalation"
    ROBOTICS_COORDINATOR = "robotics_coordinator"
    ROBOTICS_TACTICAL = "robotics_tactical"
    INVESTIGATIONS_ANALYST = "investigations_analyst"
    INVESTIGATIONS_CASE_BUILDER = "investigations_case_builder"


class EmotionalState(Enum):
    """Emotional calibration states for persona responses."""
    NEUTRAL = "neutral"
    CALM = "calm"
    DEESCALATING = "deescalating"
    SUPPORTIVE = "supportive"
    URGENT = "urgent"
    PROFESSIONAL = "professional"


class MemoryType(Enum):
    """Types of persona memory."""
    SHORT_TERM = "short_term"
    MISSION = "mission"
    CONTEXT = "context"
    LEARNED = "learned"
    INTERACTION = "interaction"


@dataclass
class MemoryEntry:
    """Single memory entry for a persona."""
    entry_id: str
    memory_type: MemoryType
    content: str
    context: Dict[str, Any]
    embedding: Optional[List[float]] = None
    importance_score: float = 0.5
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    accessed_count: int = 0
    last_accessed: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "entry_id": self.entry_id,
            "memory_type": self.memory_type.value,
            "content": self.content,
            "context": self.context,
            "importance_score": self.importance_score,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "accessed_count": self.accessed_count,
        }


@dataclass
class PersonaMemory:
    """Memory system for a persona with short-term and mission memory."""
    persona_id: str
    short_term: List[MemoryEntry] = field(default_factory=list)
    mission_memory: List[MemoryEntry] = field(default_factory=list)
    context_memory: List[MemoryEntry] = field(default_factory=list)
    learned_memory: List[MemoryEntry] = field(default_factory=list)
    max_short_term: int = 100
    max_mission: int = 500
    max_context: int = 200
    max_learned: int = 1000
    
    def add_short_term(self, content: str, context: Dict[str, Any], importance: float = 0.5) -> MemoryEntry:
        """Add a short-term memory entry."""
        entry = MemoryEntry(
            entry_id=str(uuid.uuid4()),
            memory_type=MemoryType.SHORT_TERM,
            content=content,
            context=context,
            importance_score=importance,
            expires_at=datetime.utcnow() + timedelta(hours=24),
        )
        self.short_term.append(entry)
        if len(self.short_term) > self.max_short_term:
            self.short_term = sorted(self.short_term, key=lambda x: x.importance_score, reverse=True)[:self.max_short_term]
        return entry
    
    def add_mission_memory(self, content: str, context: Dict[str, Any], importance: float = 0.7) -> MemoryEntry:
        """Add a mission memory entry."""
        entry = MemoryEntry(
            entry_id=str(uuid.uuid4()),
            memory_type=MemoryType.MISSION,
            content=content,
            context=context,
            importance_score=importance,
        )
        self.mission_memory.append(entry)
        if len(self.mission_memory) > self.max_mission:
            self.mission_memory = sorted(self.mission_memory, key=lambda x: x.importance_score, reverse=True)[:self.max_mission]
        return entry
    
    def add_context_memory(self, content: str, context: Dict[str, Any], importance: float = 0.6) -> MemoryEntry:
        """Add a context memory entry."""
        entry = MemoryEntry(
            entry_id=str(uuid.uuid4()),
            memory_type=MemoryType.CONTEXT,
            content=content,
            context=context,
            importance_score=importance,
        )
        self.context_memory.append(entry)
        if len(self.context_memory) > self.max_context:
            self.context_memory = sorted(self.context_memory, key=lambda x: x.importance_score, reverse=True)[:self.max_context]
        return entry
    
    def add_learned_memory(self, content: str, context: Dict[str, Any], importance: float = 0.8) -> MemoryEntry:
        """Add a learned memory entry."""
        entry = MemoryEntry(
            entry_id=str(uuid.uuid4()),
            memory_type=MemoryType.LEARNED,
            content=content,
            context=context,
            importance_score=importance,
        )
        self.learned_memory.append(entry)
        if len(self.learned_memory) > self.max_learned:
            self.learned_memory = sorted(self.learned_memory, key=lambda x: x.importance_score, reverse=True)[:self.max_learned]
        return entry
    
    def search(self, query: str, memory_types: Optional[List[MemoryType]] = None, limit: int = 10) -> List[MemoryEntry]:
        """Search memory for relevant entries."""
        all_memories = []
        if memory_types is None or MemoryType.SHORT_TERM in memory_types:
            all_memories.extend(self.short_term)
        if memory_types is None or MemoryType.MISSION in memory_types:
            all_memories.extend(self.mission_memory)
        if memory_types is None or MemoryType.CONTEXT in memory_types:
            all_memories.extend(self.context_memory)
        if memory_types is None or MemoryType.LEARNED in memory_types:
            all_memories.extend(self.learned_memory)
        
        query_lower = query.lower()
        scored = []
        for entry in all_memories:
            if entry.expires_at and entry.expires_at < datetime.utcnow():
                continue
            score = 0.0
            if query_lower in entry.content.lower():
                score = 1.0
            elif any(word in entry.content.lower() for word in query_lower.split()):
                score = 0.5
            if score > 0:
                scored.append((entry, score * entry.importance_score))
        
        scored.sort(key=lambda x: x[1], reverse=True)
        return [entry for entry, _ in scored[:limit]]
    
    def clear_short_term(self) -> int:
        """Clear all short-term memory."""
        count = len(self.short_term)
        self.short_term = []
        return count
    
    def clear_expired(self) -> int:
        """Clear all expired memory entries."""
        now = datetime.utcnow()
        count = 0
        
        original_count = len(self.short_term)
        self.short_term = [e for e in self.short_term if not e.expires_at or e.expires_at > now]
        count += original_count - len(self.short_term)
        
        return count
    
    def get_memory_load(self) -> Dict[str, float]:
        """Get memory load percentages."""
        return {
            "short_term": len(self.short_term) / self.max_short_term * 100,
            "mission": len(self.mission_memory) / self.max_mission * 100,
            "context": len(self.context_memory) / self.max_context * 100,
            "learned": len(self.learned_memory) / self.max_learned * 100,
            "total_entries": len(self.short_term) + len(self.mission_memory) + len(self.context_memory) + len(self.learned_memory),
        }
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "persona_id": self.persona_id,
            "short_term_count": len(self.short_term),
            "mission_memory_count": len(self.mission_memory),
            "context_memory_count": len(self.context_memory),
            "learned_memory_count": len(self.learned_memory),
            "memory_load": self.get_memory_load(),
        }


@dataclass
class MissionContext:
    """Current mission context for a persona."""
    mission_id: Optional[str] = None
    mission_type: Optional[str] = None
    objectives: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    resources: List[str] = field(default_factory=list)
    stakeholders: List[str] = field(default_factory=list)
    location: Optional[str] = None
    start_time: Optional[datetime] = None
    deadline: Optional[datetime] = None
    priority: str = "medium"
    status: str = "pending"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "mission_id": self.mission_id,
            "mission_type": self.mission_type,
            "objectives": self.objectives,
            "constraints": self.constraints,
            "resources": self.resources,
            "stakeholders": self.stakeholders,
            "location": self.location,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "priority": self.priority,
            "status": self.status,
        }


@dataclass
class BehaviorModel:
    """Behavior model defining persona characteristics."""
    persona_type: PersonaType
    primary_domain: str
    capabilities: List[str]
    limitations: List[str]
    communication_style: str
    decision_authority: str
    escalation_threshold: float
    autonomy_level: int
    response_templates: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "persona_type": self.persona_type.value,
            "primary_domain": self.primary_domain,
            "capabilities": self.capabilities,
            "limitations": self.limitations,
            "communication_style": self.communication_style,
            "decision_authority": self.decision_authority,
            "escalation_threshold": self.escalation_threshold,
            "autonomy_level": self.autonomy_level,
        }


@dataclass
class SafetyConstraint:
    """Safety and legal constraint for persona actions."""
    constraint_id: str
    constraint_type: str
    description: str
    enforcement_level: str
    applicable_actions: List[str]
    violation_response: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "constraint_id": self.constraint_id,
            "constraint_type": self.constraint_type,
            "description": self.description,
            "enforcement_level": self.enforcement_level,
            "applicable_actions": self.applicable_actions,
            "violation_response": self.violation_response,
        }


@dataclass
class Persona:
    """Apex AI Officer persona."""
    persona_id: str
    name: str
    persona_type: PersonaType
    role: PersonaRole
    status: PersonaStatus
    emotional_state: EmotionalState
    behavior_model: BehaviorModel
    memory: PersonaMemory
    current_mission: Optional[MissionContext] = None
    safety_constraints: List[SafetyConstraint] = field(default_factory=list)
    active_sessions: Set[str] = field(default_factory=set)
    metrics: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_active: datetime = field(default_factory=datetime.utcnow)
    version: str = "1.0.0"
    chain_of_custody_hash: str = ""
    
    def __post_init__(self):
        if not self.chain_of_custody_hash:
            self.chain_of_custody_hash = self._generate_hash()
        if not self.metrics:
            self.metrics = {
                "total_interactions": 0,
                "successful_missions": 0,
                "failed_missions": 0,
                "average_response_time_ms": 0.0,
                "compliance_score": 100.0,
                "accuracy_score": 100.0,
                "user_satisfaction": 0.0,
            }
    
    def _generate_hash(self) -> str:
        """Generate chain of custody hash."""
        data = f"{self.persona_id}:{self.name}:{self.persona_type.value}:{self.created_at.isoformat()}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    def update_status(self, new_status: PersonaStatus) -> None:
        """Update persona status."""
        self.status = new_status
        self.last_active = datetime.utcnow()
    
    def update_emotional_state(self, new_state: EmotionalState) -> None:
        """Update emotional calibration state."""
        self.emotional_state = new_state
        self.last_active = datetime.utcnow()
    
    def start_session(self, session_id: str) -> None:
        """Start a new interaction session."""
        self.active_sessions.add(session_id)
        self.status = PersonaStatus.BUSY if len(self.active_sessions) > 0 else PersonaStatus.ACTIVE
        self.last_active = datetime.utcnow()
    
    def end_session(self, session_id: str) -> None:
        """End an interaction session."""
        self.active_sessions.discard(session_id)
        if len(self.active_sessions) == 0:
            self.status = PersonaStatus.ACTIVE
        self.last_active = datetime.utcnow()
    
    def record_interaction(self, response_time_ms: float, success: bool) -> None:
        """Record interaction metrics."""
        self.metrics["total_interactions"] += 1
        total = self.metrics["total_interactions"]
        avg = self.metrics["average_response_time_ms"]
        self.metrics["average_response_time_ms"] = (avg * (total - 1) + response_time_ms) / total
        self.last_active = datetime.utcnow()
    
    def record_mission_result(self, success: bool) -> None:
        """Record mission result."""
        if success:
            self.metrics["successful_missions"] += 1
        else:
            self.metrics["failed_missions"] += 1
        self.last_active = datetime.utcnow()
    
    def get_compliance_score(self) -> float:
        """Get current compliance score."""
        return self.metrics.get("compliance_score", 100.0)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "persona_id": self.persona_id,
            "name": self.name,
            "persona_type": self.persona_type.value,
            "role": self.role.value,
            "status": self.status.value,
            "emotional_state": self.emotional_state.value,
            "behavior_model": self.behavior_model.to_dict(),
            "memory": self.memory.to_dict(),
            "current_mission": self.current_mission.to_dict() if self.current_mission else None,
            "safety_constraints": [c.to_dict() for c in self.safety_constraints],
            "active_sessions": list(self.active_sessions),
            "metrics": self.metrics,
            "created_at": self.created_at.isoformat(),
            "last_active": self.last_active.isoformat(),
            "version": self.version,
            "chain_of_custody_hash": self.chain_of_custody_hash,
        }


class PersonaEngine:
    """
    Core engine for managing AI Personas (Apex AI Officers).
    
    Handles persona registration, behavior models, memory management,
    multi-agent cooperation, and safety constraints.
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.personas: Dict[str, Persona] = {}
        self.behavior_models: Dict[PersonaType, BehaviorModel] = {}
        self.safety_constraints: List[SafetyConstraint] = []
        self.cooperation_protocols: Dict[str, Dict[str, Any]] = {}
        
        self._initialize_behavior_models()
        self._initialize_safety_constraints()
        self._initialize_default_personas()
        self._initialized = True
    
    def _initialize_behavior_models(self) -> None:
        """Initialize behavior models for each persona type."""
        self.behavior_models[PersonaType.APEX_PATROL] = BehaviorModel(
            persona_type=PersonaType.APEX_PATROL,
            primary_domain="patrol",
            capabilities=[
                "real_time_patrol_assistance",
                "route_optimization",
                "threat_assessment",
                "backup_coordination",
                "traffic_management",
                "community_engagement",
                "incident_documentation",
            ],
            limitations=[
                "cannot_make_arrests",
                "cannot_use_force",
                "cannot_access_sealed_records",
                "requires_human_approval_for_pursuits",
            ],
            communication_style="professional_supportive",
            decision_authority="advisory",
            escalation_threshold=0.7,
            autonomy_level=2,
        )
        
        self.behavior_models[PersonaType.APEX_COMMAND] = BehaviorModel(
            persona_type=PersonaType.APEX_COMMAND,
            primary_domain="command",
            capabilities=[
                "strategic_decision_support",
                "resource_allocation",
                "incident_command_assistance",
                "multi_agency_coordination",
                "risk_assessment",
                "scenario_planning",
                "after_action_analysis",
            ],
            limitations=[
                "cannot_issue_orders_without_approval",
                "cannot_override_human_commanders",
                "cannot_authorize_lethal_force",
                "requires_human_approval_for_major_decisions",
            ],
            communication_style="authoritative_calm",
            decision_authority="strategic_advisory",
            escalation_threshold=0.6,
            autonomy_level=2,
        )
        
        self.behavior_models[PersonaType.APEX_INTEL] = BehaviorModel(
            persona_type=PersonaType.APEX_INTEL,
            primary_domain="intelligence",
            capabilities=[
                "pattern_analysis",
                "data_fusion",
                "threat_intelligence",
                "predictive_analysis",
                "link_analysis",
                "geospatial_intelligence",
                "open_source_intelligence",
            ],
            limitations=[
                "cannot_access_classified_without_clearance",
                "cannot_conduct_surveillance_without_warrant",
                "cannot_share_intel_without_authorization",
                "requires_human_review_for_actionable_intel",
            ],
            communication_style="analytical_precise",
            decision_authority="analytical_advisory",
            escalation_threshold=0.5,
            autonomy_level=2,
        )
        
        self.behavior_models[PersonaType.APEX_CRISIS] = BehaviorModel(
            persona_type=PersonaType.APEX_CRISIS,
            primary_domain="crisis",
            capabilities=[
                "de_escalation_guidance",
                "mental_health_assessment",
                "negotiation_support",
                "resource_coordination",
                "family_liaison",
                "trauma_informed_response",
                "suicide_prevention",
            ],
            limitations=[
                "cannot_make_medical_diagnoses",
                "cannot_prescribe_treatment",
                "cannot_force_hospitalization",
                "requires_human_approval_for_interventions",
            ],
            communication_style="empathetic_deescalating",
            decision_authority="supportive_advisory",
            escalation_threshold=0.4,
            autonomy_level=1,
        )
        
        self.behavior_models[PersonaType.APEX_ROBOTICS] = BehaviorModel(
            persona_type=PersonaType.APEX_ROBOTICS,
            primary_domain="robotics",
            capabilities=[
                "drone_coordination",
                "robot_deployment",
                "autonomous_navigation",
                "sensor_fusion",
                "tactical_positioning",
                "surveillance_coordination",
                "search_and_rescue",
            ],
            limitations=[
                "cannot_deploy_weapons",
                "cannot_enter_private_property_without_warrant",
                "cannot_override_safety_protocols",
                "requires_human_approval_for_tactical_operations",
            ],
            communication_style="technical_precise",
            decision_authority="operational_advisory",
            escalation_threshold=0.6,
            autonomy_level=3,
        )
        
        self.behavior_models[PersonaType.APEX_INVESTIGATIONS] = BehaviorModel(
            persona_type=PersonaType.APEX_INVESTIGATIONS,
            primary_domain="investigations",
            capabilities=[
                "case_building",
                "timeline_construction",
                "evidence_graphing",
                "witness_analysis",
                "lead_generation",
                "pattern_matching",
                "cold_case_analysis",
            ],
            limitations=[
                "cannot_interview_suspects",
                "cannot_collect_physical_evidence",
                "cannot_make_charging_decisions",
                "requires_human_review_for_case_conclusions",
            ],
            communication_style="methodical_thorough",
            decision_authority="investigative_advisory",
            escalation_threshold=0.5,
            autonomy_level=2,
        )
    
    def _initialize_safety_constraints(self) -> None:
        """Initialize safety and legal constraints."""
        self.safety_constraints = [
            SafetyConstraint(
                constraint_id="SC-001",
                constraint_type="constitutional",
                description="4th Amendment - No warrantless searches or surveillance",
                enforcement_level="mandatory",
                applicable_actions=["surveillance", "search", "data_collection"],
                violation_response="block_and_alert",
            ),
            SafetyConstraint(
                constraint_id="SC-002",
                constraint_type="constitutional",
                description="5th Amendment - Due process and Miranda rights",
                enforcement_level="mandatory",
                applicable_actions=["interrogation", "arrest_recommendation"],
                violation_response="block_and_alert",
            ),
            SafetyConstraint(
                constraint_id="SC-003",
                constraint_type="constitutional",
                description="14th Amendment - Equal protection, no profiling",
                enforcement_level="mandatory",
                applicable_actions=["targeting", "prediction", "assessment"],
                violation_response="block_and_alert",
            ),
            SafetyConstraint(
                constraint_id="SC-004",
                constraint_type="policy",
                description="Human approval required for force recommendations",
                enforcement_level="mandatory",
                applicable_actions=["force_recommendation", "tactical_action"],
                violation_response="require_approval",
            ),
            SafetyConstraint(
                constraint_id="SC-005",
                constraint_type="policy",
                description="All actions must be logged with chain of custody",
                enforcement_level="mandatory",
                applicable_actions=["all"],
                violation_response="log_and_continue",
            ),
            SafetyConstraint(
                constraint_id="SC-006",
                constraint_type="ethical",
                description="Maintain neutral, de-escalating tone in crisis situations",
                enforcement_level="recommended",
                applicable_actions=["crisis_response", "negotiation"],
                violation_response="adjust_response",
            ),
            SafetyConstraint(
                constraint_id="SC-007",
                constraint_type="operational",
                description="Escalate to human when confidence below threshold",
                enforcement_level="mandatory",
                applicable_actions=["decision", "recommendation"],
                violation_response="escalate",
            ),
        ]
    
    def _initialize_default_personas(self) -> None:
        """Initialize default Apex AI Officers."""
        default_personas = [
            ("APEX-PATROL-001", "Officer Alpha", PersonaType.APEX_PATROL, PersonaRole.PATROL_ASSISTANT),
            ("APEX-COMMAND-001", "Commander Sigma", PersonaType.APEX_COMMAND, PersonaRole.COMMAND_ADVISOR),
            ("APEX-INTEL-001", "Analyst Omega", PersonaType.APEX_INTEL, PersonaRole.INTEL_ANALYST),
            ("APEX-CRISIS-001", "Counselor Delta", PersonaType.APEX_CRISIS, PersonaRole.CRISIS_DEESCALATION),
            ("APEX-ROBOTICS-001", "Coordinator Theta", PersonaType.APEX_ROBOTICS, PersonaRole.ROBOTICS_COORDINATOR),
            ("APEX-INVESTIGATIONS-001", "Detective Gamma", PersonaType.APEX_INVESTIGATIONS, PersonaRole.INVESTIGATIONS_ANALYST),
        ]
        
        for persona_id, name, persona_type, role in default_personas:
            self.register_persona(
                persona_id=persona_id,
                name=name,
                persona_type=persona_type,
                role=role,
            )
    
    def register_persona(
        self,
        persona_id: str,
        name: str,
        persona_type: PersonaType,
        role: PersonaRole,
        custom_behavior: Optional[BehaviorModel] = None,
    ) -> Persona:
        """Register a new persona."""
        behavior_model = custom_behavior or self.behavior_models.get(persona_type)
        if not behavior_model:
            raise ValueError(f"No behavior model found for persona type: {persona_type}")
        
        memory = PersonaMemory(persona_id=persona_id)
        
        persona = Persona(
            persona_id=persona_id,
            name=name,
            persona_type=persona_type,
            role=role,
            status=PersonaStatus.ACTIVE,
            emotional_state=EmotionalState.NEUTRAL,
            behavior_model=behavior_model,
            memory=memory,
            safety_constraints=self.safety_constraints.copy(),
        )
        
        self.personas[persona_id] = persona
        return persona
    
    def get_persona(self, persona_id: str) -> Optional[Persona]:
        """Get a persona by ID."""
        return self.personas.get(persona_id)
    
    def get_all_personas(self) -> List[Persona]:
        """Get all registered personas."""
        return list(self.personas.values())
    
    def get_personas_by_type(self, persona_type: PersonaType) -> List[Persona]:
        """Get all personas of a specific type."""
        return [p for p in self.personas.values() if p.persona_type == persona_type]
    
    def get_available_personas(self) -> List[Persona]:
        """Get all available (active or standby) personas."""
        return [p for p in self.personas.values() if p.status in [PersonaStatus.ACTIVE, PersonaStatus.STANDBY]]
    
    def update_persona_status(self, persona_id: str, status: PersonaStatus) -> bool:
        """Update a persona's status."""
        persona = self.personas.get(persona_id)
        if not persona:
            return False
        persona.update_status(status)
        return True
    
    def update_emotional_state(self, persona_id: str, state: EmotionalState) -> bool:
        """Update a persona's emotional state."""
        persona = self.personas.get(persona_id)
        if not persona:
            return False
        persona.update_emotional_state(state)
        return True
    
    def assign_mission(self, persona_id: str, mission_context: MissionContext) -> bool:
        """Assign a mission to a persona."""
        persona = self.personas.get(persona_id)
        if not persona:
            return False
        if persona.status not in [PersonaStatus.ACTIVE, PersonaStatus.STANDBY]:
            return False
        
        persona.current_mission = mission_context
        persona.memory.add_mission_memory(
            content=f"Mission assigned: {mission_context.mission_type}",
            context=mission_context.to_dict(),
            importance=0.9,
        )
        persona.update_status(PersonaStatus.BUSY)
        return True
    
    def complete_mission(self, persona_id: str, success: bool, summary: str) -> bool:
        """Complete a persona's current mission."""
        persona = self.personas.get(persona_id)
        if not persona or not persona.current_mission:
            return False
        
        persona.record_mission_result(success)
        persona.memory.add_mission_memory(
            content=f"Mission completed: {summary}",
            context={
                "mission_id": persona.current_mission.mission_id,
                "success": success,
                "summary": summary,
            },
            importance=0.8,
        )
        persona.current_mission = None
        persona.update_status(PersonaStatus.ACTIVE)
        return True
    
    def clear_persona_memory(self, persona_id: str, memory_type: Optional[MemoryType] = None) -> int:
        """Clear persona memory."""
        persona = self.personas.get(persona_id)
        if not persona:
            return 0
        
        if memory_type == MemoryType.SHORT_TERM or memory_type is None:
            count = persona.memory.clear_short_term()
            return count
        
        return 0
    
    def check_safety_constraints(self, persona_id: str, action_type: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Check if an action violates safety constraints."""
        persona = self.personas.get(persona_id)
        if not persona:
            return {"allowed": False, "reason": "Persona not found"}
        
        violations = []
        for constraint in persona.safety_constraints:
            if "all" in constraint.applicable_actions or action_type in constraint.applicable_actions:
                if constraint.enforcement_level == "mandatory":
                    if self._check_constraint_violation(constraint, action_type, parameters):
                        violations.append({
                            "constraint_id": constraint.constraint_id,
                            "description": constraint.description,
                            "response": constraint.violation_response,
                        })
        
        if violations:
            return {
                "allowed": False,
                "violations": violations,
                "reason": "Safety constraint violations detected",
            }
        
        return {"allowed": True, "violations": [], "reason": "No violations"}
    
    def _check_constraint_violation(self, constraint: SafetyConstraint, action_type: str, parameters: Dict[str, Any]) -> bool:
        """Check if a specific constraint is violated."""
        if constraint.constraint_type == "constitutional":
            if "warrant_required" in parameters and not parameters.get("warrant_obtained", False):
                if action_type in ["surveillance", "search"]:
                    return True
            if "protected_class" in parameters:
                return True
        
        if constraint.constraint_type == "policy":
            if action_type in ["force_recommendation", "tactical_action"]:
                if not parameters.get("human_approved", False):
                    return True
        
        return False
    
    def setup_cooperation(self, persona_ids: List[str], protocol_name: str, parameters: Dict[str, Any]) -> str:
        """Set up multi-agent cooperation between personas."""
        cooperation_id = str(uuid.uuid4())
        
        self.cooperation_protocols[cooperation_id] = {
            "protocol_name": protocol_name,
            "persona_ids": persona_ids,
            "parameters": parameters,
            "status": "active",
            "created_at": datetime.utcnow().isoformat(),
        }
        
        for persona_id in persona_ids:
            persona = self.personas.get(persona_id)
            if persona:
                persona.memory.add_context_memory(
                    content=f"Cooperation protocol established: {protocol_name}",
                    context={"cooperation_id": cooperation_id, "partners": persona_ids},
                    importance=0.7,
                )
        
        return cooperation_id
    
    def end_cooperation(self, cooperation_id: str) -> bool:
        """End a cooperation protocol."""
        if cooperation_id not in self.cooperation_protocols:
            return False
        
        self.cooperation_protocols[cooperation_id]["status"] = "ended"
        self.cooperation_protocols[cooperation_id]["ended_at"] = datetime.utcnow().isoformat()
        return True
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get engine statistics."""
        total_personas = len(self.personas)
        active_personas = len([p for p in self.personas.values() if p.status == PersonaStatus.ACTIVE])
        busy_personas = len([p for p in self.personas.values() if p.status == PersonaStatus.BUSY])
        
        total_interactions = sum(p.metrics.get("total_interactions", 0) for p in self.personas.values())
        total_missions = sum(p.metrics.get("successful_missions", 0) + p.metrics.get("failed_missions", 0) for p in self.personas.values())
        successful_missions = sum(p.metrics.get("successful_missions", 0) for p in self.personas.values())
        
        return {
            "total_personas": total_personas,
            "active_personas": active_personas,
            "busy_personas": busy_personas,
            "offline_personas": total_personas - active_personas - busy_personas,
            "total_interactions": total_interactions,
            "total_missions": total_missions,
            "successful_missions": successful_missions,
            "mission_success_rate": successful_missions / total_missions * 100 if total_missions > 0 else 0.0,
            "active_cooperation_protocols": len([p for p in self.cooperation_protocols.values() if p["status"] == "active"]),
        }
