"""
Test Suite: Personas API

Tests for REST API endpoints.
"""

import pytest
from datetime import datetime

from backend.app.api.personas.persona_router import (
    get_all_personas,
    get_persona,
    get_persona_status,
    update_persona_status,
    update_emotional_state,
    ask_persona,
    create_mission,
    get_mission,
    get_all_missions,
    get_pending_approvals,
    validate_action,
    get_compliance_summary,
    clear_persona_memory,
    get_persona_statistics,
    PersonaStatusUpdate,
    PersonaEmotionalStateUpdate,
    AskRequest,
    MissionCreateRequest,
    ComplianceValidationRequest,
    MemoryClearRequest,
)
from backend.app.personas.persona_engine import PersonaEngine


class TestPersonaEndpoints:
    """Tests for persona management endpoints."""
    
    def test_get_all_personas(self):
        """Test GET /api/personas endpoint."""
        response = get_all_personas()
        
        assert response is not None
        assert "personas" in response.dict()
        assert "total" in response.dict()
        assert response.total >= 6
    
    def test_get_persona(self):
        """Test GET /api/personas/{id} endpoint."""
        engine = PersonaEngine()
        personas = engine.get_all_personas()
        
        if personas:
            response = get_persona(personas[0].persona_id)
            
            assert response is not None
            assert "persona" in response.dict()
            assert "memory_load" in response.dict()
            assert "compliance_score" in response.dict()
    
    def test_get_persona_not_found(self):
        """Test GET /api/personas/{id} with non-existent ID."""
        with pytest.raises(ValueError) as exc_info:
            get_persona("nonexistent-id")
        
        assert "not found" in str(exc_info.value).lower()
    
    def test_get_persona_status(self):
        """Test GET /api/personas/{id}/status endpoint."""
        engine = PersonaEngine()
        personas = engine.get_all_personas()
        
        if personas:
            response = get_persona_status(personas[0].persona_id)
            
            assert response is not None
            assert "persona_id" in response
            assert "status" in response
            assert "emotional_state" in response
    
    def test_update_persona_status(self):
        """Test PUT /api/personas/{id}/status endpoint."""
        engine = PersonaEngine()
        personas = engine.get_all_personas()
        
        if personas:
            request = PersonaStatusUpdate(status="standby")
            response = update_persona_status(personas[0].persona_id, request)
            
            assert response["success"] == True
            assert response["new_status"] == "standby"
            
            request = PersonaStatusUpdate(status="active")
            update_persona_status(personas[0].persona_id, request)
    
    def test_update_persona_status_invalid(self):
        """Test PUT /api/personas/{id}/status with invalid status."""
        engine = PersonaEngine()
        personas = engine.get_all_personas()
        
        if personas:
            request = PersonaStatusUpdate(status="invalid_status")
            with pytest.raises(ValueError):
                update_persona_status(personas[0].persona_id, request)
    
    def test_update_emotional_state(self):
        """Test PUT /api/personas/{id}/emotional-state endpoint."""
        engine = PersonaEngine()
        personas = engine.get_all_personas()
        
        if personas:
            request = PersonaEmotionalStateUpdate(emotional_state="calm")
            response = update_emotional_state(personas[0].persona_id, request)
            
            assert response["success"] == True
            assert response["new_emotional_state"] == "calm"


class TestInteractionEndpoints:
    """Tests for interaction endpoints."""
    
    def test_ask_persona(self):
        """Test POST /api/personas/{id}/ask endpoint."""
        engine = PersonaEngine()
        personas = engine.get_all_personas()
        
        if personas:
            request = AskRequest(
                message="What is your current status?",
                user_id="test-user",
                interaction_type="rtcc_console",
            )
            
            response = ask_persona(personas[0].persona_id, request)
            
            assert response is not None
            assert response.response_id
            assert response.session_id
            assert response.content
            assert response.confidence > 0
    
    def test_ask_persona_with_session(self):
        """Test POST /api/personas/{id}/ask with existing session."""
        engine = PersonaEngine()
        personas = engine.get_all_personas()
        
        if personas:
            request1 = AskRequest(
                message="Hello",
                user_id="test-user",
                interaction_type="rtcc_console",
            )
            response1 = ask_persona(personas[0].persona_id, request1)
            
            request2 = AskRequest(
                message="Follow up question",
                user_id="test-user",
                interaction_type="rtcc_console",
                session_id=response1.session_id,
            )
            response2 = ask_persona(personas[0].persona_id, request2)
            
            assert response2.session_id == response1.session_id
    
    def test_ask_persona_not_found(self):
        """Test POST /api/personas/{id}/ask with non-existent persona."""
        request = AskRequest(
            message="Hello",
            user_id="test-user",
            interaction_type="rtcc_console",
        )
        
        with pytest.raises(ValueError) as exc_info:
            ask_persona("nonexistent-id", request)
        
        assert "not found" in str(exc_info.value).lower()


class TestMissionEndpoints:
    """Tests for mission endpoints."""
    
    def test_create_mission(self):
        """Test POST /api/personas/{id}/mission endpoint."""
        engine = PersonaEngine()
        personas = engine.get_all_personas()
        
        if personas:
            request = MissionCreateRequest(
                title="Test Mission",
                description="Test mission description",
                mission_type="patrol",
                priority="medium",
                objectives=["Objective 1", "Objective 2"],
            )
            
            response = create_mission(personas[0].persona_id, request)
            
            assert response is not None
            assert "mission" in response.dict()
            assert response.status
    
    def test_get_mission(self):
        """Test GET /api/missions/{id} endpoint."""
        engine = PersonaEngine()
        personas = engine.get_all_personas()
        
        if personas:
            request = MissionCreateRequest(
                title="Get Test Mission",
                description="Test",
                mission_type="investigation",
                priority="high",
                objectives=["Test"],
            )
            
            created = create_mission(personas[0].persona_id, request)
            mission_id = created.mission["mission_id"]
            
            response = get_mission(mission_id)
            
            assert response is not None
            assert response.mission["mission_id"] == mission_id
    
    def test_get_all_missions(self):
        """Test GET /api/missions endpoint."""
        response = get_all_missions()
        
        assert response is not None
        assert "missions" in response
        assert "total" in response
    
    def test_get_pending_approvals(self):
        """Test GET /api/approvals/pending endpoint."""
        response = get_pending_approvals()
        
        assert response is not None
        assert "approvals" in response
        assert "total" in response


class TestComplianceEndpoints:
    """Tests for compliance endpoints."""
    
    def test_validate_action(self):
        """Test POST /api/personas/{id}/validate endpoint."""
        engine = PersonaEngine()
        personas = engine.get_all_personas()
        
        if personas:
            request = ComplianceValidationRequest(
                action_type="query",
                parameters={"query": "status check"},
            )
            
            response = validate_action(personas[0].persona_id, request)
            
            assert response is not None
            assert "is_compliant" in response
            assert "status" in response
    
    def test_get_compliance_summary(self):
        """Test GET /api/compliance/summary endpoint."""
        response = get_compliance_summary()
        
        assert response is not None
        assert "compliance_rate" in response


class TestMemoryEndpoints:
    """Tests for memory endpoints."""
    
    def test_clear_persona_memory(self):
        """Test POST /api/personas/{id}/memory/clear endpoint."""
        engine = PersonaEngine()
        personas = engine.get_all_personas()
        
        if personas:
            request = MemoryClearRequest(memory_type="short_term")
            response = clear_persona_memory(personas[0].persona_id, request)
            
            assert response is not None
            assert response["success"] == True
            assert "entries_cleared" in response
    
    def test_clear_all_memory(self):
        """Test clearing all memory types."""
        engine = PersonaEngine()
        personas = engine.get_all_personas()
        
        if personas:
            request = MemoryClearRequest()
            response = clear_persona_memory(personas[0].persona_id, request)
            
            assert response["success"] == True
            assert response["memory_type"] == "all"


class TestStatisticsEndpoints:
    """Tests for statistics endpoints."""
    
    def test_get_persona_statistics(self):
        """Test GET /api/personas/statistics endpoint."""
        response = get_persona_statistics()
        
        assert response is not None
        assert "personas" in response
        assert "interactions" in response
        assert "missions" in response
        assert "compliance" in response
