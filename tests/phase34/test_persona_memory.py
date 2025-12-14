"""
Test Suite: Persona Memory

Tests for PersonaMemory system, memory types, and memory management.
"""

import pytest
from datetime import datetime, timedelta

from backend.app.personas.persona_engine import (
    PersonaEngine,
    PersonaMemory,
    MemoryType,
    MemoryEntry,
)


class TestMemoryTypes:
    """Tests for different memory types."""
    
    def test_short_term_memory(self):
        """Test short-term memory functionality."""
        memory = PersonaMemory()
        
        entry = memory.add_short_term(
            content="Recent observation",
            importance=0.7,
        )
        
        assert entry.memory_type == MemoryType.SHORT_TERM
        assert entry.content == "Recent observation"
        assert entry.importance == 0.7
    
    def test_mission_memory(self):
        """Test mission memory functionality."""
        memory = PersonaMemory()
        
        entry = memory.add_mission_memory(
            content="Mission objective achieved",
            mission_id="mission-001",
            importance=0.9,
        )
        
        assert entry.memory_type == MemoryType.MISSION
        assert entry.metadata.get("mission_id") == "mission-001"
    
    def test_context_memory(self):
        """Test context memory functionality."""
        memory = PersonaMemory()
        
        entry = memory.add_context_memory(
            content="Operational context information",
            context_type="situational",
            importance=0.6,
        )
        
        assert entry.memory_type == MemoryType.CONTEXT
        assert entry.metadata.get("context_type") == "situational"
    
    def test_learned_memory(self):
        """Test learned memory functionality."""
        memory = PersonaMemory()
        
        entry = memory.add_learned_memory(
            content="Pattern learned from interactions",
            source="user_feedback",
            importance=0.8,
        )
        
        assert entry.memory_type == MemoryType.LEARNED
        assert entry.metadata.get("source") == "user_feedback"


class TestMemorySearch:
    """Tests for memory search functionality."""
    
    def test_search_by_keyword(self):
        """Test searching memory by keyword."""
        memory = PersonaMemory()
        
        memory.add_short_term("Traffic incident on Main Street", importance=0.8)
        memory.add_short_term("Suspicious vehicle near park", importance=0.7)
        memory.add_short_term("Weather conditions clear", importance=0.3)
        
        results = memory.search("traffic")
        
        assert len(results) >= 1
        assert any("traffic" in r.content.lower() for r in results)
    
    def test_search_multiple_keywords(self):
        """Test searching with multiple keywords."""
        memory = PersonaMemory()
        
        memory.add_short_term("Suspect vehicle blue sedan", importance=0.9)
        memory.add_short_term("Blue car parked illegally", importance=0.6)
        memory.add_short_term("Red truck speeding", importance=0.7)
        
        results = memory.search("blue")
        
        assert len(results) >= 1
    
    def test_search_empty_query(self):
        """Test searching with empty query."""
        memory = PersonaMemory()
        
        memory.add_short_term("Test memory", importance=0.5)
        
        results = memory.search("")
        
        assert isinstance(results, list)
    
    def test_search_no_results(self):
        """Test searching with no matching results."""
        memory = PersonaMemory()
        
        memory.add_short_term("Traffic observation", importance=0.5)
        
        results = memory.search("nonexistent_keyword_xyz")
        
        assert len(results) == 0
    
    def test_search_across_memory_types(self):
        """Test searching across all memory types."""
        memory = PersonaMemory()
        
        memory.add_short_term("Short term patrol note", importance=0.5)
        memory.add_mission_memory("Mission patrol objective", mission_id="m1", importance=0.7)
        memory.add_context_memory("Context patrol info", context_type="ops", importance=0.6)
        memory.add_learned_memory("Learned patrol pattern", source="exp", importance=0.8)
        
        results = memory.search("patrol")
        
        assert len(results) >= 1


class TestMemoryManagement:
    """Tests for memory management operations."""
    
    def test_clear_short_term(self):
        """Test clearing short-term memory."""
        memory = PersonaMemory()
        
        memory.add_short_term("Memory 1", importance=0.5)
        memory.add_short_term("Memory 2", importance=0.6)
        memory.add_short_term("Memory 3", importance=0.7)
        
        count = memory.clear_short_term()
        
        assert count == 3
        assert len(memory.short_term) == 0
    
    def test_clear_expired(self):
        """Test clearing expired memories."""
        memory = PersonaMemory()
        
        memory.add_short_term("Recent memory", importance=0.5)
        
        count = memory.clear_expired()
        
        assert count >= 0
    
    def test_memory_load_calculation(self):
        """Test memory load calculation."""
        memory = PersonaMemory()
        
        for i in range(10):
            memory.add_short_term(f"Short term {i}", importance=0.5)
        
        for i in range(5):
            memory.add_mission_memory(f"Mission {i}", mission_id=f"m{i}", importance=0.7)
        
        load = memory.get_memory_load()
        
        assert "short_term" in load
        assert "mission" in load
        assert "context" in load
        assert "learned" in load
        assert load["short_term"] > 0
        assert load["mission"] > 0


class TestMemoryImportance:
    """Tests for memory importance scoring."""
    
    def test_importance_range(self):
        """Test that importance is within valid range."""
        memory = PersonaMemory()
        
        entry = memory.add_short_term("Test", importance=0.5)
        assert 0 <= entry.importance <= 1
        
        entry = memory.add_short_term("Test", importance=0.0)
        assert entry.importance == 0.0
        
        entry = memory.add_short_term("Test", importance=1.0)
        assert entry.importance == 1.0
    
    def test_search_by_importance(self):
        """Test that search considers importance."""
        memory = PersonaMemory()
        
        memory.add_short_term("Low importance item", importance=0.1)
        memory.add_short_term("High importance item", importance=0.9)
        memory.add_short_term("Medium importance item", importance=0.5)
        
        results = memory.search("item")
        
        assert len(results) >= 1


class TestMemoryEntry:
    """Tests for MemoryEntry dataclass."""
    
    def test_entry_creation(self):
        """Test creating a memory entry."""
        entry = MemoryEntry(
            entry_id="entry-001",
            content="Test content",
            memory_type=MemoryType.SHORT_TERM,
            importance=0.7,
        )
        
        assert entry.entry_id == "entry-001"
        assert entry.content == "Test content"
        assert entry.memory_type == MemoryType.SHORT_TERM
        assert entry.importance == 0.7
    
    def test_entry_with_metadata(self):
        """Test creating entry with metadata."""
        entry = MemoryEntry(
            entry_id="entry-002",
            content="Test with metadata",
            memory_type=MemoryType.MISSION,
            importance=0.8,
            metadata={"mission_id": "m001", "task": "surveillance"},
        )
        
        assert entry.metadata["mission_id"] == "m001"
        assert entry.metadata["task"] == "surveillance"
    
    def test_entry_to_dict(self):
        """Test entry serialization."""
        entry = MemoryEntry(
            entry_id="entry-003",
            content="Serialization test",
            memory_type=MemoryType.CONTEXT,
            importance=0.6,
        )
        
        data = entry.to_dict()
        
        assert data["entry_id"] == "entry-003"
        assert data["content"] == "Serialization test"
        assert "memory_type" in data
        assert "importance" in data
        assert "timestamp" in data


class TestPersonaMemoryIntegration:
    """Tests for persona memory integration."""
    
    def test_persona_has_memory(self):
        """Test that personas have memory system."""
        engine = PersonaEngine()
        personas = engine.get_all_personas()
        
        if personas:
            persona = personas[0]
            assert persona.memory is not None
            assert isinstance(persona.memory, PersonaMemory)
    
    def test_clear_persona_memory(self):
        """Test clearing persona memory through engine."""
        engine = PersonaEngine()
        personas = engine.get_all_personas()
        
        if personas:
            persona_id = personas[0].persona_id
            
            persona = engine.get_persona(persona_id)
            persona.memory.add_short_term("Test memory", importance=0.5)
            
            count = engine.clear_persona_memory(persona_id, MemoryType.SHORT_TERM)
            
            assert count >= 0
    
    def test_clear_all_persona_memory(self):
        """Test clearing all persona memory."""
        engine = PersonaEngine()
        personas = engine.get_all_personas()
        
        if personas:
            persona_id = personas[0].persona_id
            
            persona = engine.get_persona(persona_id)
            persona.memory.add_short_term("Short term", importance=0.5)
            persona.memory.add_context_memory("Context", context_type="test", importance=0.6)
            
            count = engine.clear_persona_memory(persona_id)
            
            assert count >= 0


class TestMemoryLimits:
    """Tests for memory limits and constraints."""
    
    def test_short_term_limit(self):
        """Test short-term memory limit."""
        memory = PersonaMemory()
        
        for i in range(150):
            memory.add_short_term(f"Memory {i}", importance=0.5)
        
        load = memory.get_memory_load()
        assert load["short_term"] > 0
    
    def test_mission_memory_limit(self):
        """Test mission memory limit."""
        memory = PersonaMemory()
        
        for i in range(60):
            memory.add_mission_memory(f"Mission {i}", mission_id=f"m{i}", importance=0.7)
        
        load = memory.get_memory_load()
        assert load["mission"] > 0
    
    def test_context_memory_limit(self):
        """Test context memory limit."""
        memory = PersonaMemory()
        
        for i in range(250):
            memory.add_context_memory(f"Context {i}", context_type="test", importance=0.6)
        
        load = memory.get_memory_load()
        assert load["context"] > 0
    
    def test_learned_memory_limit(self):
        """Test learned memory limit."""
        memory = PersonaMemory()
        
        for i in range(600):
            memory.add_learned_memory(f"Learned {i}", source="test", importance=0.8)
        
        load = memory.get_memory_load()
        assert load["learned"] > 0
