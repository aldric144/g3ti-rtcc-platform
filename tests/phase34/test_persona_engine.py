"""
Test Suite: Persona Engine

Tests for PersonaEngine, PersonaMemory, and persona lifecycle management.
"""

import pytest
from datetime import datetime, timedelta

from backend.app.personas.persona_engine import (
    PersonaEngine,
    PersonaType,
    PersonaStatus,
    PersonaRole,
    EmotionalState,
    MemoryType,
    MemoryEntry,
    PersonaMemory,
    MissionContext,
    BehaviorModel,
    SafetyConstraint,
    Persona,
)


class TestPersonaEngine:
    """Tests for PersonaEngine singleton."""
    
    def test_singleton_pattern(self):
        """Test that PersonaEngine follows singleton pattern."""
        engine1 = PersonaEngine()
        engine2 = PersonaEngine()
        assert engine1 is engine2
    
    def test_default_personas_initialized(self):
        """Test that default Apex AI Officers are initialized."""
        engine = PersonaEngine()
        personas = engine.get_all_personas()
        assert len(personas) >= 6
        
        persona_types = [p.persona_type for p in personas]
        assert PersonaType.APEX_PATROL in persona_types
        assert PersonaType.APEX_COMMAND in persona_types
        assert PersonaType.APEX_INTEL in persona_types
        assert PersonaType.APEX_CRISIS in persona_types
        assert PersonaType.APEX_ROBOTICS in persona_types
        assert PersonaType.APEX_INVESTIGATIONS in persona_types
    
    def test_get_persona_by_id(self):
        """Test getting persona by ID."""
        engine = PersonaEngine()
        personas = engine.get_all_personas()
        
        if personas:
            persona = engine.get_persona(personas[0].persona_id)
            assert persona is not None
            assert persona.persona_id == personas[0].persona_id
    
    def test_get_nonexistent_persona(self):
        """Test getting non-existent persona returns None."""
        engine = PersonaEngine()
        persona = engine.get_persona("nonexistent-id")
        assert persona is None
    
    def test_get_personas_by_type(self):
        """Test filtering personas by type."""
        engine = PersonaEngine()
        patrol_personas = engine.get_personas_by_type(PersonaType.APEX_PATROL)
        
        for persona in patrol_personas:
            assert persona.persona_type == PersonaType.APEX_PATROL
    
    def test_get_available_personas(self):
        """Test getting available personas."""
        engine = PersonaEngine()
        available = engine.get_available_personas()
        
        for persona in available:
            assert persona.status in [PersonaStatus.ACTIVE, PersonaStatus.STANDBY]
    
    def test_update_persona_status(self):
        """Test updating persona status."""
        engine = PersonaEngine()
        personas = engine.get_all_personas()
        
        if personas:
            persona_id = personas[0].persona_id
            original_status = personas[0].status
            
            engine.update_persona_status(persona_id, PersonaStatus.MAINTENANCE)
            updated = engine.get_persona(persona_id)
            assert updated.status == PersonaStatus.MAINTENANCE
            
            engine.update_persona_status(persona_id, original_status)
    
    def test_update_emotional_state(self):
        """Test updating persona emotional state."""
        engine = PersonaEngine()
        personas = engine.get_all_personas()
        
        if personas:
            persona_id = personas[0].persona_id
            
            engine.update_emotional_state(persona_id, EmotionalState.CALM)
            updated = engine.get_persona(persona_id)
            assert updated.emotional_state == EmotionalState.CALM
    
    def test_get_statistics(self):
        """Test getting engine statistics."""
        engine = PersonaEngine()
        stats = engine.get_statistics()
        
        assert "total_personas" in stats
        assert "active_personas" in stats
        assert "personas_by_type" in stats
        assert stats["total_personas"] >= 6


class TestPersonaMemory:
    """Tests for PersonaMemory system."""
    
    def test_memory_initialization(self):
        """Test memory initialization."""
        memory = PersonaMemory()
        
        assert memory.short_term == []
        assert memory.mission_memory == []
        assert memory.context_memory == []
        assert memory.learned_memory == []
    
    def test_add_short_term_memory(self):
        """Test adding short-term memory."""
        memory = PersonaMemory()
        
        entry = memory.add_short_term(
            content="Test memory content",
            importance=0.8,
        )
        
        assert entry is not None
        assert entry.content == "Test memory content"
        assert entry.importance == 0.8
        assert entry.memory_type == MemoryType.SHORT_TERM
        assert len(memory.short_term) == 1
    
    def test_add_mission_memory(self):
        """Test adding mission memory."""
        memory = PersonaMemory()
        
        entry = memory.add_mission_memory(
            content="Mission objective completed",
            mission_id="mission-001",
            importance=0.9,
        )
        
        assert entry is not None
        assert entry.memory_type == MemoryType.MISSION
        assert entry.metadata.get("mission_id") == "mission-001"
    
    def test_add_context_memory(self):
        """Test adding context memory."""
        memory = PersonaMemory()
        
        entry = memory.add_context_memory(
            content="Operational context",
            context_type="situational",
            importance=0.7,
        )
        
        assert entry is not None
        assert entry.memory_type == MemoryType.CONTEXT
    
    def test_add_learned_memory(self):
        """Test adding learned memory."""
        memory = PersonaMemory()
        
        entry = memory.add_learned_memory(
            content="Learned pattern",
            source="interaction",
            importance=0.6,
        )
        
        assert entry is not None
        assert entry.memory_type == MemoryType.LEARNED
    
    def test_memory_search(self):
        """Test memory search functionality."""
        memory = PersonaMemory()
        
        memory.add_short_term("Traffic stop procedure", importance=0.8)
        memory.add_short_term("Suspicious vehicle report", importance=0.7)
        memory.add_short_term("Weather conditions clear", importance=0.3)
        
        results = memory.search("traffic")
        assert len(results) >= 1
        assert any("traffic" in r.content.lower() for r in results)
    
    def test_clear_short_term_memory(self):
        """Test clearing short-term memory."""
        memory = PersonaMemory()
        
        memory.add_short_term("Test 1", importance=0.5)
        memory.add_short_term("Test 2", importance=0.5)
        
        assert len(memory.short_term) == 2
        
        count = memory.clear_short_term()
        assert count == 2
        assert len(memory.short_term) == 0
    
    def test_memory_load(self):
        """Test memory load calculation."""
        memory = PersonaMemory()
        
        for i in range(10):
            memory.add_short_term(f"Memory {i}", importance=0.5)
        
        load = memory.get_memory_load()
        
        assert "short_term" in load
        assert "mission" in load
        assert "context" in load
        assert "learned" in load
        assert load["short_term"] > 0


class TestPersona:
    """Tests for Persona dataclass."""
    
    def test_persona_creation(self):
        """Test creating a persona."""
        persona = Persona(
            persona_id="test-001",
            name="Test Persona",
            persona_type=PersonaType.APEX_PATROL,
            role=PersonaRole.PATROL_ASSISTANT,
            description="Test persona description",
        )
        
        assert persona.persona_id == "test-001"
        assert persona.name == "Test Persona"
        assert persona.persona_type == PersonaType.APEX_PATROL
        assert persona.status == PersonaStatus.ACTIVE
        assert persona.emotional_state == EmotionalState.NEUTRAL
    
    def test_persona_to_dict(self):
        """Test persona serialization."""
        persona = Persona(
            persona_id="test-002",
            name="Test Persona 2",
            persona_type=PersonaType.APEX_INTEL,
            role=PersonaRole.INTEL_ANALYST,
            description="Test description",
        )
        
        data = persona.to_dict()
        
        assert data["persona_id"] == "test-002"
        assert data["name"] == "Test Persona 2"
        assert data["persona_type"] == "apex_intel"
        assert "status" in data
        assert "emotional_state" in data
    
    def test_persona_compliance_score(self):
        """Test persona compliance score calculation."""
        persona = Persona(
            persona_id="test-003",
            name="Test Persona 3",
            persona_type=PersonaType.APEX_COMMAND,
            role=PersonaRole.COMMAND_ADVISOR,
            description="Test description",
        )
        
        score = persona.get_compliance_score()
        assert 0 <= score <= 100


class TestBehaviorModel:
    """Tests for BehaviorModel."""
    
    def test_behavior_model_creation(self):
        """Test creating a behavior model."""
        model = BehaviorModel(
            role=PersonaRole.PATROL_ASSISTANT,
            capabilities=["traffic_guidance", "backup_coordination"],
            limitations=["no_force_authorization"],
            communication_style="professional",
            decision_authority="advisory",
            escalation_threshold=0.7,
        )
        
        assert model.role == PersonaRole.PATROL_ASSISTANT
        assert "traffic_guidance" in model.capabilities
        assert "no_force_authorization" in model.limitations
        assert model.escalation_threshold == 0.7


class TestSafetyConstraint:
    """Tests for SafetyConstraint."""
    
    def test_safety_constraint_creation(self):
        """Test creating a safety constraint."""
        constraint = SafetyConstraint(
            constraint_id="4A-001",
            name="Fourth Amendment",
            description="No warrantless searches",
            constraint_type="constitutional",
            severity="critical",
            enforcement="block",
        )
        
        assert constraint.constraint_id == "4A-001"
        assert constraint.constraint_type == "constitutional"
        assert constraint.severity == "critical"
        assert constraint.enforcement == "block"


class TestMissionContext:
    """Tests for MissionContext."""
    
    def test_mission_context_creation(self):
        """Test creating a mission context."""
        context = MissionContext(
            mission_id="mission-001",
            mission_type="patrol",
            objectives=["Monitor area", "Report suspicious activity"],
            constraints=["No pursuit"],
            priority="high",
        )
        
        assert context.mission_id == "mission-001"
        assert context.mission_type == "patrol"
        assert len(context.objectives) == 2
        assert context.priority == "high"
    
    def test_mission_context_to_dict(self):
        """Test mission context serialization."""
        context = MissionContext(
            mission_id="mission-002",
            mission_type="investigation",
            objectives=["Gather evidence"],
            constraints=[],
            priority="medium",
        )
        
        data = context.to_dict()
        
        assert data["mission_id"] == "mission-002"
        assert data["mission_type"] == "investigation"
        assert "objectives" in data
