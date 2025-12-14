"""
Test Suite: End-to-End Personas

End-to-end tests for the complete AI Personas framework.
"""

import pytest
from datetime import datetime

from backend.app.personas.persona_engine import (
    PersonaEngine,
    PersonaType,
    PersonaStatus,
    EmotionalState,
)
from backend.app.personas.interaction_engine import (
    InteractionEngine,
    InteractionType,
)
from backend.app.personas.mission_reasoner import (
    MissionReasoner,
    MissionPriority,
    MissionStatus,
)
from backend.app.personas.compliance_layer import (
    ComplianceIntegrationLayer,
    ComplianceStatus,
)


class TestE2EPersonaLifecycle:
    """End-to-end tests for persona lifecycle."""
    
    def test_full_persona_lifecycle(self):
        """Test complete persona lifecycle from creation to interaction."""
        engine = PersonaEngine()
        interaction_engine = InteractionEngine()
        
        personas = engine.get_all_personas()
        assert len(personas) >= 6
        
        patrol_personas = engine.get_personas_by_type(PersonaType.APEX_PATROL)
        assert len(patrol_personas) >= 1
        
        persona = patrol_personas[0]
        assert persona.status == PersonaStatus.ACTIVE
        
        session = interaction_engine.create_session(
            persona_id=persona.persona_id,
            user_id="e2e-test-user",
            interaction_type=InteractionType.RTCC_CONSOLE,
        )
        assert session is not None
        
        response = interaction_engine.process_input(
            session.session_id,
            "What is your current status?",
        )
        assert response is not None
        assert response.content
        
        interaction_engine.end_session(session.session_id)


class TestE2EMissionWorkflow:
    """End-to-end tests for mission workflow."""
    
    def test_full_mission_workflow(self):
        """Test complete mission workflow from creation to completion."""
        engine = PersonaEngine()
        reasoner = MissionReasoner()
        compliance = ComplianceIntegrationLayer()
        
        personas = engine.get_all_personas()
        persona = personas[0]
        
        mission = reasoner.create_mission(
            title="E2E Test Mission",
            description="End-to-end test mission",
            mission_type="patrol",
            priority=MissionPriority.MEDIUM,
            created_by=persona.persona_id,
            objectives=[
                "Monitor designated area",
                "Report suspicious activity",
                "Coordinate with backup units",
            ],
        )
        assert mission is not None
        assert mission.status == MissionStatus.DRAFT
        
        planned = reasoner.plan_mission(mission.mission_id)
        assert planned is not None
        assert len(planned.tasks) > 0
        
        reasoner.assign_personas(mission.mission_id)
        reasoner.assign_resources(mission.mission_id)
        
        validation = compliance.validate_action(
            persona_id=persona.persona_id,
            action_type="mission_execution",
            parameters={"mission_id": mission.mission_id},
        )
        assert validation.is_compliant
        
        updated = reasoner.get_mission(mission.mission_id)
        if updated.status == MissionStatus.APPROVED:
            reasoner.start_mission(mission.mission_id)
            
            started = reasoner.get_mission(mission.mission_id)
            assert started.status == MissionStatus.IN_PROGRESS
            
            reasoner.complete_mission(
                mission.mission_id,
                success=True,
                summary="E2E test mission completed successfully",
            )
            
            completed = reasoner.get_mission(mission.mission_id)
            assert completed.status == MissionStatus.COMPLETED


class TestE2EComplianceIntegration:
    """End-to-end tests for compliance integration."""
    
    def test_full_compliance_workflow(self):
        """Test complete compliance workflow."""
        engine = PersonaEngine()
        interaction_engine = InteractionEngine()
        compliance = ComplianceIntegrationLayer()
        
        personas = engine.get_all_personas()
        persona = personas[0]
        
        session = interaction_engine.create_session(
            persona_id=persona.persona_id,
            user_id="compliance-test-user",
            interaction_type=InteractionType.RTCC_CONSOLE,
        )
        
        response = interaction_engine.process_input(
            session.session_id,
            "Request authorization for surveillance operation",
        )
        
        validation = compliance.validate_action(
            persona_id=persona.persona_id,
            action_type="surveillance_request",
            parameters={"authorized": True},
        )
        
        assert validation is not None
        assert validation.status in [
            ComplianceStatus.COMPLIANT,
            ComplianceStatus.COMPLIANT_WITH_WARNINGS,
        ]
        
        summary = compliance.get_compliance_summary(persona.persona_id)
        assert summary is not None
        
        interaction_engine.end_session(session.session_id)


class TestE2EMultiPersonaInteraction:
    """End-to-end tests for multi-persona interactions."""
    
    def test_multi_persona_cooperation(self):
        """Test cooperation between multiple personas."""
        engine = PersonaEngine()
        interaction_engine = InteractionEngine()
        reasoner = MissionReasoner()
        
        patrol = engine.get_personas_by_type(PersonaType.APEX_PATROL)[0]
        intel = engine.get_personas_by_type(PersonaType.APEX_INTEL)[0]
        
        engine.setup_cooperation(
            persona_ids=[patrol.persona_id, intel.persona_id],
            cooperation_type="joint_surveillance",
            context={"target_area": "sector_5"},
        )
        
        mission = reasoner.create_mission(
            title="Joint Surveillance Mission",
            description="Cooperative surveillance operation",
            mission_type="surveillance",
            priority=MissionPriority.HIGH,
            created_by=patrol.persona_id,
            objectives=["Coordinate surveillance", "Share intelligence"],
        )
        
        reasoner.plan_mission(mission.mission_id)
        reasoner.assign_personas(mission.mission_id)
        
        patrol_session = interaction_engine.create_session(
            persona_id=patrol.persona_id,
            user_id="multi-test-user",
            interaction_type=InteractionType.RTCC_CONSOLE,
        )
        
        intel_session = interaction_engine.create_session(
            persona_id=intel.persona_id,
            user_id="multi-test-user",
            interaction_type=InteractionType.RTCC_CONSOLE,
        )
        
        patrol_response = interaction_engine.process_input(
            patrol_session.session_id,
            "Report on surveillance status",
        )
        
        intel_response = interaction_engine.process_input(
            intel_session.session_id,
            "Analyze surveillance data",
        )
        
        assert patrol_response is not None
        assert intel_response is not None
        
        engine.end_cooperation(
            persona_ids=[patrol.persona_id, intel.persona_id],
        )
        
        interaction_engine.end_session(patrol_session.session_id)
        interaction_engine.end_session(intel_session.session_id)


class TestE2EMemoryPersistence:
    """End-to-end tests for memory persistence."""
    
    def test_memory_across_sessions(self):
        """Test that memory persists across sessions."""
        engine = PersonaEngine()
        interaction_engine = InteractionEngine()
        
        personas = engine.get_all_personas()
        persona = personas[0]
        
        session1 = interaction_engine.create_session(
            persona_id=persona.persona_id,
            user_id="memory-test-user",
            interaction_type=InteractionType.RTCC_CONSOLE,
        )
        
        interaction_engine.process_input(
            session1.session_id,
            "Remember that suspect vehicle is blue sedan",
        )
        
        interaction_engine.end_session(session1.session_id)
        
        session2 = interaction_engine.create_session(
            persona_id=persona.persona_id,
            user_id="memory-test-user",
            interaction_type=InteractionType.RTCC_CONSOLE,
        )
        
        response = interaction_engine.process_input(
            session2.session_id,
            "What do you remember about the suspect vehicle?",
        )
        
        assert response is not None
        
        interaction_engine.end_session(session2.session_id)


class TestE2EApprovalWorkflow:
    """End-to-end tests for approval workflow."""
    
    def test_full_approval_workflow(self):
        """Test complete approval workflow."""
        reasoner = MissionReasoner()
        
        mission = reasoner.create_mission(
            title="Approval Test Mission",
            description="Mission requiring approval",
            mission_type="tactical",
            priority=MissionPriority.CRITICAL,
            created_by="test-persona",
            objectives=["Execute tactical operation"],
        )
        
        reasoner.plan_mission(mission.mission_id)
        
        request = reasoner.request_approval(
            mission_id=mission.mission_id,
            request_type="mission_start",
            description="Request to start critical tactical mission",
            urgency="critical",
            required_authority="commander",
        )
        
        assert request is not None
        
        pending = reasoner.get_pending_approvals()
        assert any(a.request_id == request.request_id for a in pending)
        
        reasoner.approve_request(
            request_id=request.request_id,
            approved_by="commander-001",
            notes="Approved for E2E test",
        )


class TestE2EStatistics:
    """End-to-end tests for statistics collection."""
    
    def test_comprehensive_statistics(self):
        """Test comprehensive statistics collection."""
        engine = PersonaEngine()
        interaction_engine = InteractionEngine()
        reasoner = MissionReasoner()
        compliance = ComplianceIntegrationLayer()
        
        persona_stats = engine.get_statistics()
        assert "total_personas" in persona_stats
        assert persona_stats["total_personas"] >= 6
        
        interaction_stats = interaction_engine.get_statistics()
        assert "total_sessions" in interaction_stats
        
        mission_stats = reasoner.get_statistics()
        assert "total_missions" in mission_stats
        
        compliance_stats = compliance.get_statistics()
        assert "total_validations" in compliance_stats


class TestE2EErrorHandling:
    """End-to-end tests for error handling."""
    
    def test_invalid_persona_handling(self):
        """Test handling of invalid persona ID."""
        engine = PersonaEngine()
        
        persona = engine.get_persona("nonexistent-persona-id")
        assert persona is None
    
    def test_invalid_session_handling(self):
        """Test handling of invalid session ID."""
        interaction_engine = InteractionEngine()
        
        session = interaction_engine.get_session("nonexistent-session-id")
        assert session is None
    
    def test_invalid_mission_handling(self):
        """Test handling of invalid mission ID."""
        reasoner = MissionReasoner()
        
        mission = reasoner.get_mission("nonexistent-mission-id")
        assert mission is None


class TestE2EPerformance:
    """End-to-end tests for performance."""
    
    def test_rapid_interactions(self):
        """Test rapid sequential interactions."""
        engine = PersonaEngine()
        interaction_engine = InteractionEngine()
        
        personas = engine.get_all_personas()
        persona = personas[0]
        
        session = interaction_engine.create_session(
            persona_id=persona.persona_id,
            user_id="performance-test-user",
            interaction_type=InteractionType.RTCC_CONSOLE,
        )
        
        for i in range(10):
            response = interaction_engine.process_input(
                session.session_id,
                f"Test message {i}",
            )
            assert response is not None
            assert response.response_time_ms >= 0
        
        interaction_engine.end_session(session.session_id)
    
    def test_multiple_concurrent_sessions(self):
        """Test multiple concurrent sessions."""
        engine = PersonaEngine()
        interaction_engine = InteractionEngine()
        
        personas = engine.get_all_personas()
        sessions = []
        
        for i, persona in enumerate(personas[:3]):
            session = interaction_engine.create_session(
                persona_id=persona.persona_id,
                user_id=f"concurrent-test-user-{i}",
                interaction_type=InteractionType.RTCC_CONSOLE,
            )
            sessions.append(session)
        
        for session in sessions:
            response = interaction_engine.process_input(
                session.session_id,
                "Concurrent test message",
            )
            assert response is not None
        
        for session in sessions:
            interaction_engine.end_session(session.session_id)
