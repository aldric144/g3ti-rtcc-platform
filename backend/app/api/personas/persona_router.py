"""
Persona API Router

REST API endpoints for AI Personas including:
- Persona management
- Interaction sessions
- Mission operations
- Compliance validation
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

from backend.app.personas.persona_engine import (
    PersonaEngine,
    PersonaType,
    PersonaStatus,
    PersonaRole,
    EmotionalState,
    MissionContext,
)
from backend.app.personas.interaction_engine import (
    InteractionEngine,
    InteractionType,
)
from backend.app.personas.mission_reasoner import (
    MissionReasoner,
    MissionPriority,
)
from backend.app.personas.compliance_layer import (
    ComplianceIntegrationLayer,
)


class PersonaListResponse(BaseModel):
    """Response model for persona list."""
    personas: List[Dict[str, Any]]
    total: int
    active: int
    busy: int


class PersonaDetailResponse(BaseModel):
    """Response model for persona details."""
    persona: Dict[str, Any]
    memory_load: Dict[str, float]
    active_sessions: int
    compliance_score: float


class PersonaStatusUpdate(BaseModel):
    """Request model for updating persona status."""
    status: str = Field(..., description="New status: active, standby, maintenance, offline, suspended")


class PersonaEmotionalStateUpdate(BaseModel):
    """Request model for updating emotional state."""
    emotional_state: str = Field(..., description="New emotional state: neutral, calm, deescalating, supportive, urgent, professional")


class AskRequest(BaseModel):
    """Request model for asking a persona."""
    message: str = Field(..., description="Message to send to persona")
    user_id: str = Field(..., description="User ID")
    interaction_type: str = Field(default="rtcc_console", description="Interaction type: rtcc_console, mobile_mdt, voice_radio, websocket, api")
    session_id: Optional[str] = Field(default=None, description="Existing session ID to continue conversation")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Additional context")


class AskResponse(BaseModel):
    """Response model for persona response."""
    response_id: str
    session_id: str
    persona_id: str
    persona_name: str
    content: str
    emotional_tone: str
    confidence: float
    action_items: List[Dict[str, Any]]
    follow_up_questions: List[str]
    escalation_required: bool
    escalation_reason: Optional[str]
    response_time_ms: float


class MissionCreateRequest(BaseModel):
    """Request model for creating a mission."""
    title: str = Field(..., description="Mission title")
    description: str = Field(..., description="Mission description")
    mission_type: str = Field(..., description="Type of mission")
    priority: str = Field(default="medium", description="Priority: critical, high, medium, low, routine")
    objectives: List[str] = Field(..., description="Mission objectives")
    constraints: Optional[List[str]] = Field(default=None, description="Mission constraints")
    location: Optional[str] = Field(default=None, description="Mission location")
    deadline: Optional[str] = Field(default=None, description="Mission deadline (ISO format)")


class MissionResponse(BaseModel):
    """Response model for mission."""
    mission: Dict[str, Any]
    status: str
    progress: Dict[str, Any]


class ApprovalRequest(BaseModel):
    """Request model for approval."""
    approved_by: str = Field(..., description="Approver ID")
    notes: Optional[str] = Field(default=None, description="Approval notes")
    conditions: Optional[List[str]] = Field(default=None, description="Approval conditions")


class DenialRequest(BaseModel):
    """Request model for denial."""
    denied_by: str = Field(..., description="Denier ID")
    reason: str = Field(..., description="Denial reason")


class ComplianceValidationRequest(BaseModel):
    """Request model for compliance validation."""
    action_type: str = Field(..., description="Type of action to validate")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Action parameters")


class MemoryClearRequest(BaseModel):
    """Request model for clearing memory."""
    memory_type: Optional[str] = Field(default=None, description="Memory type to clear: short_term, mission, context, learned")


persona_engine = PersonaEngine()
interaction_engine = InteractionEngine()
mission_reasoner = MissionReasoner()
compliance_layer = ComplianceIntegrationLayer()


def get_all_personas() -> PersonaListResponse:
    """Get all registered personas."""
    personas = persona_engine.get_all_personas()
    active = len([p for p in personas if p.status == PersonaStatus.ACTIVE])
    busy = len([p for p in personas if p.status == PersonaStatus.BUSY])
    
    return PersonaListResponse(
        personas=[p.to_dict() for p in personas],
        total=len(personas),
        active=active,
        busy=busy,
    )


def get_persona(persona_id: str) -> PersonaDetailResponse:
    """Get persona details."""
    persona = persona_engine.get_persona(persona_id)
    if not persona:
        raise ValueError(f"Persona not found: {persona_id}")
    
    return PersonaDetailResponse(
        persona=persona.to_dict(),
        memory_load=persona.memory.get_memory_load(),
        active_sessions=len(persona.active_sessions),
        compliance_score=persona.get_compliance_score(),
    )


def get_persona_status(persona_id: str) -> Dict[str, Any]:
    """Get persona status."""
    persona = persona_engine.get_persona(persona_id)
    if not persona:
        raise ValueError(f"Persona not found: {persona_id}")
    
    return {
        "persona_id": persona.persona_id,
        "name": persona.name,
        "status": persona.status.value,
        "emotional_state": persona.emotional_state.value,
        "active_sessions": len(persona.active_sessions),
        "current_mission": persona.current_mission.to_dict() if persona.current_mission else None,
        "last_active": persona.last_active.isoformat(),
        "metrics": persona.metrics,
    }


def update_persona_status(persona_id: str, request: PersonaStatusUpdate) -> Dict[str, Any]:
    """Update persona status."""
    try:
        status = PersonaStatus(request.status)
    except ValueError:
        raise ValueError(f"Invalid status: {request.status}")
    
    success = persona_engine.update_persona_status(persona_id, status)
    if not success:
        raise ValueError(f"Failed to update persona status: {persona_id}")
    
    return {"success": True, "persona_id": persona_id, "new_status": status.value}


def update_emotional_state(persona_id: str, request: PersonaEmotionalStateUpdate) -> Dict[str, Any]:
    """Update persona emotional state."""
    try:
        state = EmotionalState(request.emotional_state)
    except ValueError:
        raise ValueError(f"Invalid emotional state: {request.emotional_state}")
    
    success = persona_engine.update_emotional_state(persona_id, state)
    if not success:
        raise ValueError(f"Failed to update emotional state: {persona_id}")
    
    return {"success": True, "persona_id": persona_id, "new_emotional_state": state.value}


def ask_persona(persona_id: str, request: AskRequest) -> AskResponse:
    """Send a message to a persona and get response."""
    persona = persona_engine.get_persona(persona_id)
    if not persona:
        raise ValueError(f"Persona not found: {persona_id}")
    
    try:
        interaction_type = InteractionType(request.interaction_type)
    except ValueError:
        interaction_type = InteractionType.API
    
    if request.session_id:
        session = interaction_engine.get_session(request.session_id)
        if not session:
            session = interaction_engine.create_session(
                persona_id=persona_id,
                user_id=request.user_id,
                interaction_type=interaction_type,
                initial_context=request.context,
            )
    else:
        session = interaction_engine.create_session(
            persona_id=persona_id,
            user_id=request.user_id,
            interaction_type=interaction_type,
            initial_context=request.context,
        )
    
    response = interaction_engine.process_input(session.session_id, request.message)
    
    return AskResponse(
        response_id=response.response_id,
        session_id=session.session_id,
        persona_id=persona.persona_id,
        persona_name=persona.name,
        content=response.content,
        emotional_tone=response.emotional_tone.value,
        confidence=response.confidence,
        action_items=response.action_items,
        follow_up_questions=response.follow_up_questions,
        escalation_required=response.escalation_required,
        escalation_reason=response.escalation_reason,
        response_time_ms=response.response_time_ms,
    )


def create_mission(persona_id: str, request: MissionCreateRequest) -> MissionResponse:
    """Create a mission for a persona."""
    persona = persona_engine.get_persona(persona_id)
    if not persona:
        raise ValueError(f"Persona not found: {persona_id}")
    
    try:
        priority = MissionPriority(request.priority)
    except ValueError:
        priority = MissionPriority.MEDIUM
    
    deadline = None
    if request.deadline:
        deadline = datetime.fromisoformat(request.deadline)
    
    mission = mission_reasoner.create_mission(
        title=request.title,
        description=request.description,
        mission_type=request.mission_type,
        priority=priority,
        created_by=persona_id,
        objectives=request.objectives,
        constraints=request.constraints,
        location=request.location,
        deadline=deadline,
    )
    
    mission = mission_reasoner.plan_mission(mission.mission_id)
    
    mission_reasoner.assign_personas(mission.mission_id)
    mission_reasoner.assign_resources(mission.mission_id)
    
    return MissionResponse(
        mission=mission.to_dict(),
        status=mission.status.value,
        progress=mission.get_progress(),
    )


def get_mission(mission_id: str) -> MissionResponse:
    """Get mission details."""
    mission = mission_reasoner.get_mission(mission_id)
    if not mission:
        raise ValueError(f"Mission not found: {mission_id}")
    
    return MissionResponse(
        mission=mission.to_dict(),
        status=mission.status.value,
        progress=mission.get_progress(),
    )


def start_mission(mission_id: str) -> Dict[str, Any]:
    """Start a mission."""
    success = mission_reasoner.start_mission(mission_id)
    if not success:
        raise ValueError(f"Failed to start mission: {mission_id}")
    
    mission = mission_reasoner.get_mission(mission_id)
    return {
        "success": True,
        "mission_id": mission_id,
        "status": mission.status.value if mission else "unknown",
    }


def complete_mission(mission_id: str, success: bool, summary: str) -> Dict[str, Any]:
    """Complete a mission."""
    result = mission_reasoner.complete_mission(mission_id, success, summary)
    if not result:
        raise ValueError(f"Failed to complete mission: {mission_id}")
    
    mission = mission_reasoner.get_mission(mission_id)
    return {
        "success": True,
        "mission_id": mission_id,
        "status": mission.status.value if mission else "unknown",
        "outcome": "success" if success else "failure",
    }


def get_all_missions() -> Dict[str, Any]:
    """Get all missions."""
    missions = mission_reasoner.get_all_missions()
    active = mission_reasoner.get_active_missions()
    
    return {
        "missions": [m.to_dict() for m in missions],
        "total": len(missions),
        "active": len(active),
    }


def get_pending_approvals() -> Dict[str, Any]:
    """Get all pending approval requests."""
    approvals = mission_reasoner.get_pending_approvals()
    
    return {
        "approvals": [a.to_dict() for a in approvals],
        "total": len(approvals),
    }


def approve_request(request_id: str, request: ApprovalRequest) -> Dict[str, Any]:
    """Approve an approval request."""
    success = mission_reasoner.approve_request(
        request_id=request_id,
        approved_by=request.approved_by,
        notes=request.notes,
        conditions=request.conditions,
    )
    
    if not success:
        raise ValueError(f"Failed to approve request: {request_id}")
    
    return {"success": True, "request_id": request_id, "status": "approved"}


def deny_request(request_id: str, request: DenialRequest) -> Dict[str, Any]:
    """Deny an approval request."""
    success = mission_reasoner.deny_request(
        request_id=request_id,
        denied_by=request.denied_by,
        reason=request.reason,
    )
    
    if not success:
        raise ValueError(f"Failed to deny request: {request_id}")
    
    return {"success": True, "request_id": request_id, "status": "denied"}


def validate_action(persona_id: str, request: ComplianceValidationRequest) -> Dict[str, Any]:
    """Validate a persona action against compliance frameworks."""
    result = compliance_layer.validate_action(
        persona_id=persona_id,
        action_type=request.action_type,
        parameters=request.parameters,
    )
    
    return result.to_dict()


def get_compliance_summary(persona_id: Optional[str] = None) -> Dict[str, Any]:
    """Get compliance summary."""
    return compliance_layer.get_compliance_summary(persona_id)


def get_active_violations() -> Dict[str, Any]:
    """Get all active violations."""
    violations = compliance_layer.get_active_violations()
    
    return {
        "violations": [v.to_dict() for v in violations],
        "total": len(violations),
    }


def resolve_violation(violation_id: str, resolved_by: str, notes: str) -> Dict[str, Any]:
    """Resolve a violation."""
    success = compliance_layer.resolve_violation(violation_id, resolved_by, notes)
    
    if not success:
        raise ValueError(f"Failed to resolve violation: {violation_id}")
    
    return {"success": True, "violation_id": violation_id, "status": "resolved"}


def clear_persona_memory(persona_id: str, request: MemoryClearRequest) -> Dict[str, Any]:
    """Clear persona memory."""
    from backend.app.personas.persona_engine import MemoryType
    
    memory_type = None
    if request.memory_type:
        try:
            memory_type = MemoryType(request.memory_type)
        except ValueError:
            raise ValueError(f"Invalid memory type: {request.memory_type}")
    
    count = persona_engine.clear_persona_memory(persona_id, memory_type)
    
    return {
        "success": True,
        "persona_id": persona_id,
        "entries_cleared": count,
        "memory_type": request.memory_type or "all",
    }


def get_session_history(session_id: str) -> Dict[str, Any]:
    """Get session conversation history."""
    session = interaction_engine.get_session(session_id)
    if not session:
        raise ValueError(f"Session not found: {session_id}")
    
    return {
        "session": session.to_dict(),
        "turns": [t.to_dict() for t in session.turns],
        "total_turns": len(session.turns),
    }


def end_session(session_id: str) -> Dict[str, Any]:
    """End an interaction session."""
    success = interaction_engine.end_session(session_id)
    
    if not success:
        raise ValueError(f"Failed to end session: {session_id}")
    
    return {"success": True, "session_id": session_id, "status": "ended"}


def get_active_sessions() -> Dict[str, Any]:
    """Get all active sessions."""
    sessions = interaction_engine.get_active_sessions()
    
    return {
        "sessions": [s.to_dict() for s in sessions],
        "total": len(sessions),
    }


def get_persona_statistics() -> Dict[str, Any]:
    """Get overall persona statistics."""
    persona_stats = persona_engine.get_statistics()
    interaction_stats = interaction_engine.get_statistics()
    mission_stats = mission_reasoner.get_statistics()
    compliance_stats = compliance_layer.get_statistics()
    
    return {
        "personas": persona_stats,
        "interactions": interaction_stats,
        "missions": mission_stats,
        "compliance": compliance_stats,
    }


def get_personas_by_type(persona_type: str) -> Dict[str, Any]:
    """Get personas by type."""
    try:
        ptype = PersonaType(persona_type)
    except ValueError:
        raise ValueError(f"Invalid persona type: {persona_type}")
    
    personas = persona_engine.get_personas_by_type(ptype)
    
    return {
        "personas": [p.to_dict() for p in personas],
        "total": len(personas),
        "type": persona_type,
    }


def get_available_personas() -> Dict[str, Any]:
    """Get all available personas."""
    personas = persona_engine.get_available_personas()
    
    return {
        "personas": [p.to_dict() for p in personas],
        "total": len(personas),
    }


router_endpoints = {
    "GET /api/personas": get_all_personas,
    "GET /api/personas/available": get_available_personas,
    "GET /api/personas/statistics": get_persona_statistics,
    "GET /api/personas/type/{persona_type}": get_personas_by_type,
    "GET /api/personas/{persona_id}": get_persona,
    "GET /api/personas/{persona_id}/status": get_persona_status,
    "PUT /api/personas/{persona_id}/status": update_persona_status,
    "PUT /api/personas/{persona_id}/emotional-state": update_emotional_state,
    "POST /api/personas/{persona_id}/ask": ask_persona,
    "POST /api/personas/{persona_id}/mission": create_mission,
    "POST /api/personas/{persona_id}/memory/clear": clear_persona_memory,
    "POST /api/personas/{persona_id}/validate": validate_action,
    "GET /api/missions": get_all_missions,
    "GET /api/missions/{mission_id}": get_mission,
    "POST /api/missions/{mission_id}/start": start_mission,
    "POST /api/missions/{mission_id}/complete": complete_mission,
    "GET /api/approvals/pending": get_pending_approvals,
    "POST /api/approvals/{request_id}/approve": approve_request,
    "POST /api/approvals/{request_id}/deny": deny_request,
    "GET /api/sessions/active": get_active_sessions,
    "GET /api/sessions/{session_id}": get_session_history,
    "POST /api/sessions/{session_id}/end": end_session,
    "GET /api/compliance/summary": get_compliance_summary,
    "GET /api/compliance/violations": get_active_violations,
    "POST /api/compliance/violations/{violation_id}/resolve": resolve_violation,
}


router = router_endpoints
