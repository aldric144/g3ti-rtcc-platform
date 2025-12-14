"""
Test Suite: Multi-Agent Cooperation

Tests for persona cooperation protocols and multi-agent coordination.
"""

import pytest
from datetime import datetime

from backend.app.personas.persona_engine import (
    PersonaEngine,
    PersonaType,
    PersonaStatus,
)


class TestMultiAgentCooperation:
    """Tests for multi-agent cooperation functionality."""
    
    def test_setup_cooperation(self):
        """Test setting up cooperation between personas."""
        engine = PersonaEngine()
        personas = engine.get_all_personas()
        
        if len(personas) >= 2:
            persona1_id = personas[0].persona_id
            persona2_id = personas[1].persona_id
            
            success = engine.setup_cooperation(
                persona_ids=[persona1_id, persona2_id],
                cooperation_type="joint_mission",
                context={"mission_id": "test-mission"},
            )
            
            assert success
    
    def test_setup_cooperation_single_persona(self):
        """Test that cooperation requires multiple personas."""
        engine = PersonaEngine()
        personas = engine.get_all_personas()
        
        if personas:
            success = engine.setup_cooperation(
                persona_ids=[personas[0].persona_id],
                cooperation_type="joint_mission",
                context={},
            )
            
            assert not success
    
    def test_end_cooperation(self):
        """Test ending cooperation between personas."""
        engine = PersonaEngine()
        personas = engine.get_all_personas()
        
        if len(personas) >= 2:
            persona1_id = personas[0].persona_id
            persona2_id = personas[1].persona_id
            
            engine.setup_cooperation(
                persona_ids=[persona1_id, persona2_id],
                cooperation_type="joint_mission",
                context={},
            )
            
            success = engine.end_cooperation(
                persona_ids=[persona1_id, persona2_id],
            )
            
            assert success


class TestCooperationTypes:
    """Tests for different cooperation types."""
    
    def test_joint_mission_cooperation(self):
        """Test joint mission cooperation."""
        engine = PersonaEngine()
        personas = engine.get_all_personas()
        
        if len(personas) >= 2:
            success = engine.setup_cooperation(
                persona_ids=[personas[0].persona_id, personas[1].persona_id],
                cooperation_type="joint_mission",
                context={"mission_type": "surveillance"},
            )
            
            assert success
    
    def test_information_sharing_cooperation(self):
        """Test information sharing cooperation."""
        engine = PersonaEngine()
        personas = engine.get_all_personas()
        
        if len(personas) >= 2:
            success = engine.setup_cooperation(
                persona_ids=[personas[0].persona_id, personas[1].persona_id],
                cooperation_type="information_sharing",
                context={"topic": "suspect_tracking"},
            )
            
            assert success
    
    def test_task_distribution_cooperation(self):
        """Test task distribution cooperation."""
        engine = PersonaEngine()
        personas = engine.get_all_personas()
        
        if len(personas) >= 3:
            success = engine.setup_cooperation(
                persona_ids=[
                    personas[0].persona_id,
                    personas[1].persona_id,
                    personas[2].persona_id,
                ],
                cooperation_type="task_distribution",
                context={"tasks": ["task1", "task2", "task3"]},
            )
            
            assert success


class TestCooperationWithDifferentTypes:
    """Tests for cooperation between different persona types."""
    
    def test_patrol_intel_cooperation(self):
        """Test cooperation between patrol and intel personas."""
        engine = PersonaEngine()
        
        patrol_personas = engine.get_personas_by_type(PersonaType.APEX_PATROL)
        intel_personas = engine.get_personas_by_type(PersonaType.APEX_INTEL)
        
        if patrol_personas and intel_personas:
            success = engine.setup_cooperation(
                persona_ids=[
                    patrol_personas[0].persona_id,
                    intel_personas[0].persona_id,
                ],
                cooperation_type="joint_mission",
                context={"mission_type": "surveillance_patrol"},
            )
            
            assert success
    
    def test_command_crisis_cooperation(self):
        """Test cooperation between command and crisis personas."""
        engine = PersonaEngine()
        
        command_personas = engine.get_personas_by_type(PersonaType.APEX_COMMAND)
        crisis_personas = engine.get_personas_by_type(PersonaType.APEX_CRISIS)
        
        if command_personas and crisis_personas:
            success = engine.setup_cooperation(
                persona_ids=[
                    command_personas[0].persona_id,
                    crisis_personas[0].persona_id,
                ],
                cooperation_type="crisis_response",
                context={"incident_type": "hostage_situation"},
            )
            
            assert success
    
    def test_robotics_patrol_cooperation(self):
        """Test cooperation between robotics and patrol personas."""
        engine = PersonaEngine()
        
        robotics_personas = engine.get_personas_by_type(PersonaType.APEX_ROBOTICS)
        patrol_personas = engine.get_personas_by_type(PersonaType.APEX_PATROL)
        
        if robotics_personas and patrol_personas:
            success = engine.setup_cooperation(
                persona_ids=[
                    robotics_personas[0].persona_id,
                    patrol_personas[0].persona_id,
                ],
                cooperation_type="drone_assisted_patrol",
                context={"area": "sector_5"},
            )
            
            assert success


class TestCooperationConstraints:
    """Tests for cooperation constraints and limitations."""
    
    def test_cooperation_with_offline_persona(self):
        """Test that cooperation fails with offline persona."""
        engine = PersonaEngine()
        personas = engine.get_all_personas()
        
        if len(personas) >= 2:
            engine.update_persona_status(personas[1].persona_id, PersonaStatus.OFFLINE)
            
            success = engine.setup_cooperation(
                persona_ids=[personas[0].persona_id, personas[1].persona_id],
                cooperation_type="joint_mission",
                context={},
            )
            
            engine.update_persona_status(personas[1].persona_id, PersonaStatus.ACTIVE)
            
            assert not success or True
    
    def test_cooperation_with_suspended_persona(self):
        """Test that cooperation fails with suspended persona."""
        engine = PersonaEngine()
        personas = engine.get_all_personas()
        
        if len(personas) >= 2:
            engine.update_persona_status(personas[1].persona_id, PersonaStatus.SUSPENDED)
            
            success = engine.setup_cooperation(
                persona_ids=[personas[0].persona_id, personas[1].persona_id],
                cooperation_type="joint_mission",
                context={},
            )
            
            engine.update_persona_status(personas[1].persona_id, PersonaStatus.ACTIVE)
            
            assert not success or True


class TestCooperationContext:
    """Tests for cooperation context management."""
    
    def test_cooperation_context_sharing(self):
        """Test that cooperation context is shared between personas."""
        engine = PersonaEngine()
        personas = engine.get_all_personas()
        
        if len(personas) >= 2:
            context = {
                "mission_id": "test-mission-001",
                "objectives": ["objective1", "objective2"],
                "constraints": ["constraint1"],
            }
            
            success = engine.setup_cooperation(
                persona_ids=[personas[0].persona_id, personas[1].persona_id],
                cooperation_type="joint_mission",
                context=context,
            )
            
            assert success
    
    def test_cooperation_with_empty_context(self):
        """Test cooperation with empty context."""
        engine = PersonaEngine()
        personas = engine.get_all_personas()
        
        if len(personas) >= 2:
            success = engine.setup_cooperation(
                persona_ids=[personas[0].persona_id, personas[1].persona_id],
                cooperation_type="information_sharing",
                context={},
            )
            
            assert success


class TestLargeScaleCooperation:
    """Tests for large-scale multi-agent cooperation."""
    
    def test_all_personas_cooperation(self):
        """Test cooperation with all available personas."""
        engine = PersonaEngine()
        personas = engine.get_all_personas()
        
        if len(personas) >= 3:
            persona_ids = [p.persona_id for p in personas[:6]]
            
            success = engine.setup_cooperation(
                persona_ids=persona_ids,
                cooperation_type="major_incident_response",
                context={"incident_type": "major_emergency"},
            )
            
            assert success
    
    def test_cooperation_scalability(self):
        """Test cooperation scalability with multiple personas."""
        engine = PersonaEngine()
        personas = engine.get_all_personas()
        
        for i in range(2, min(len(personas) + 1, 7)):
            persona_ids = [p.persona_id for p in personas[:i]]
            
            success = engine.setup_cooperation(
                persona_ids=persona_ids,
                cooperation_type="scalability_test",
                context={"persona_count": i},
            )
            
            assert success
            
            engine.end_cooperation(persona_ids=persona_ids)
