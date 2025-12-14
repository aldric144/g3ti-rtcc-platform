"""
Test Suite: Interaction Engine

Tests for InteractionEngine, intent analysis, and conversation management.
"""

import pytest
from datetime import datetime

from backend.app.personas.interaction_engine import (
    InteractionEngine,
    InteractionType,
    IntentCategory,
    UrgencyLevel,
    EmotionDetected,
    DomainType,
    IntentAnalysis,
    ConversationTurn,
    ExplainabilityTrace,
    InteractionSession,
    PersonaResponse,
)
from backend.app.personas.persona_engine import PersonaEngine


class TestInteractionEngine:
    """Tests for InteractionEngine singleton."""
    
    def test_singleton_pattern(self):
        """Test that InteractionEngine follows singleton pattern."""
        engine1 = InteractionEngine()
        engine2 = InteractionEngine()
        assert engine1 is engine2
    
    def test_create_session(self):
        """Test creating an interaction session."""
        engine = InteractionEngine()
        persona_engine = PersonaEngine()
        
        personas = persona_engine.get_all_personas()
        if personas:
            session = engine.create_session(
                persona_id=personas[0].persona_id,
                user_id="test-user",
                interaction_type=InteractionType.RTCC_CONSOLE,
            )
            
            assert session is not None
            assert session.persona_id == personas[0].persona_id
            assert session.user_id == "test-user"
            assert session.interaction_type == InteractionType.RTCC_CONSOLE
            assert session.is_active
    
    def test_get_session(self):
        """Test getting an existing session."""
        engine = InteractionEngine()
        persona_engine = PersonaEngine()
        
        personas = persona_engine.get_all_personas()
        if personas:
            session = engine.create_session(
                persona_id=personas[0].persona_id,
                user_id="test-user-2",
                interaction_type=InteractionType.API,
            )
            
            retrieved = engine.get_session(session.session_id)
            assert retrieved is not None
            assert retrieved.session_id == session.session_id
    
    def test_get_nonexistent_session(self):
        """Test getting non-existent session returns None."""
        engine = InteractionEngine()
        session = engine.get_session("nonexistent-session")
        assert session is None
    
    def test_end_session(self):
        """Test ending a session."""
        engine = InteractionEngine()
        persona_engine = PersonaEngine()
        
        personas = persona_engine.get_all_personas()
        if personas:
            session = engine.create_session(
                persona_id=personas[0].persona_id,
                user_id="test-user-3",
                interaction_type=InteractionType.WEBSOCKET,
            )
            
            success = engine.end_session(session.session_id)
            assert success
            
            ended_session = engine.get_session(session.session_id)
            assert ended_session is None or not ended_session.is_active
    
    def test_get_active_sessions(self):
        """Test getting active sessions."""
        engine = InteractionEngine()
        active = engine.get_active_sessions()
        
        for session in active:
            assert session.is_active
    
    def test_get_statistics(self):
        """Test getting engine statistics."""
        engine = InteractionEngine()
        stats = engine.get_statistics()
        
        assert "total_sessions" in stats
        assert "active_sessions" in stats


class TestIntentAnalysis:
    """Tests for intent analysis functionality."""
    
    def test_analyze_query_intent(self):
        """Test analyzing query intent."""
        engine = InteractionEngine()
        
        analysis = engine.analyze_intent("What is the current status of unit 5?")
        
        assert analysis is not None
        assert analysis.category == IntentCategory.QUERY
    
    def test_analyze_command_intent(self):
        """Test analyzing command intent."""
        engine = InteractionEngine()
        
        analysis = engine.analyze_intent("Deploy drone to sector 7")
        
        assert analysis is not None
        assert analysis.category in [IntentCategory.COMMAND, IntentCategory.TACTICAL]
    
    def test_analyze_alert_intent(self):
        """Test analyzing alert intent."""
        engine = InteractionEngine()
        
        analysis = engine.analyze_intent("URGENT: Shots fired at Main Street")
        
        assert analysis is not None
        assert analysis.urgency in [UrgencyLevel.HIGH, UrgencyLevel.CRITICAL]
    
    def test_analyze_crisis_intent(self):
        """Test analyzing crisis intent."""
        engine = InteractionEngine()
        
        analysis = engine.analyze_intent("Subject threatening suicide, need crisis intervention")
        
        assert analysis is not None
        assert analysis.category in [IntentCategory.CRISIS, IntentCategory.ASSISTANCE]
    
    def test_urgency_detection(self):
        """Test urgency level detection."""
        engine = InteractionEngine()
        
        low_urgency = engine.analyze_intent("Can you check the weather forecast?")
        assert low_urgency.urgency in [UrgencyLevel.LOW, UrgencyLevel.ROUTINE]
        
        high_urgency = engine.analyze_intent("EMERGENCY: Officer down!")
        assert high_urgency.urgency in [UrgencyLevel.HIGH, UrgencyLevel.CRITICAL]
    
    def test_emotion_detection(self):
        """Test emotion detection."""
        engine = InteractionEngine()
        
        neutral = engine.analyze_intent("Please provide the report.")
        assert neutral.emotion in [EmotionDetected.NEUTRAL, EmotionDetected.CALM]
        
        urgent = engine.analyze_intent("Help! I need backup immediately!")
        assert urgent.emotion in [EmotionDetected.URGENT, EmotionDetected.STRESSED, EmotionDetected.FEARFUL]


class TestDomainRouting:
    """Tests for domain routing functionality."""
    
    def test_route_to_patrol(self):
        """Test routing to patrol domain."""
        engine = InteractionEngine()
        
        domain = engine.route_to_persona("Traffic stop guidance needed")
        assert domain in [DomainType.PATROL, DomainType.TACTICAL]
    
    def test_route_to_intel(self):
        """Test routing to intel domain."""
        engine = InteractionEngine()
        
        domain = engine.route_to_persona("Analyze the suspect's pattern of movement")
        assert domain in [DomainType.INTEL, DomainType.INVESTIGATIONS]
    
    def test_route_to_crisis(self):
        """Test routing to crisis domain."""
        engine = InteractionEngine()
        
        domain = engine.route_to_persona("Mental health crisis, subject is agitated")
        assert domain == DomainType.CRISIS
    
    def test_route_to_robotics(self):
        """Test routing to robotics domain."""
        engine = InteractionEngine()
        
        domain = engine.route_to_persona("Deploy surveillance drone to the area")
        assert domain == DomainType.ROBOTICS


class TestProcessInput:
    """Tests for input processing and response generation."""
    
    def test_process_simple_query(self):
        """Test processing a simple query."""
        engine = InteractionEngine()
        persona_engine = PersonaEngine()
        
        personas = persona_engine.get_all_personas()
        if personas:
            session = engine.create_session(
                persona_id=personas[0].persona_id,
                user_id="test-user",
                interaction_type=InteractionType.RTCC_CONSOLE,
            )
            
            response = engine.process_input(session.session_id, "What is your status?")
            
            assert response is not None
            assert response.content
            assert response.confidence > 0
    
    def test_process_generates_response_id(self):
        """Test that processing generates a response ID."""
        engine = InteractionEngine()
        persona_engine = PersonaEngine()
        
        personas = persona_engine.get_all_personas()
        if personas:
            session = engine.create_session(
                persona_id=personas[0].persona_id,
                user_id="test-user",
                interaction_type=InteractionType.API,
            )
            
            response = engine.process_input(session.session_id, "Hello")
            
            assert response.response_id
            assert len(response.response_id) > 0
    
    def test_process_tracks_response_time(self):
        """Test that processing tracks response time."""
        engine = InteractionEngine()
        persona_engine = PersonaEngine()
        
        personas = persona_engine.get_all_personas()
        if personas:
            session = engine.create_session(
                persona_id=personas[0].persona_id,
                user_id="test-user",
                interaction_type=InteractionType.MOBILE_MDT,
            )
            
            response = engine.process_input(session.session_id, "Test message")
            
            assert response.response_time_ms >= 0
    
    def test_multi_turn_conversation(self):
        """Test multi-turn conversation tracking."""
        engine = InteractionEngine()
        persona_engine = PersonaEngine()
        
        personas = persona_engine.get_all_personas()
        if personas:
            session = engine.create_session(
                persona_id=personas[0].persona_id,
                user_id="test-user",
                interaction_type=InteractionType.RTCC_CONSOLE,
            )
            
            engine.process_input(session.session_id, "First message")
            engine.process_input(session.session_id, "Second message")
            engine.process_input(session.session_id, "Third message")
            
            updated_session = engine.get_session(session.session_id)
            assert len(updated_session.turns) >= 3


class TestExplainabilityTrace:
    """Tests for explainability trace generation."""
    
    def test_trace_includes_reasoning_steps(self):
        """Test that trace includes reasoning steps."""
        engine = InteractionEngine()
        persona_engine = PersonaEngine()
        
        personas = persona_engine.get_all_personas()
        if personas:
            session = engine.create_session(
                persona_id=personas[0].persona_id,
                user_id="test-user",
                interaction_type=InteractionType.RTCC_CONSOLE,
            )
            
            response = engine.process_input(session.session_id, "Analyze this situation")
            
            assert response.explainability_trace is not None
            assert len(response.explainability_trace.reasoning_steps) > 0
    
    def test_trace_includes_constraints_checked(self):
        """Test that trace includes constraints checked."""
        engine = InteractionEngine()
        persona_engine = PersonaEngine()
        
        personas = persona_engine.get_all_personas()
        if personas:
            session = engine.create_session(
                persona_id=personas[0].persona_id,
                user_id="test-user",
                interaction_type=InteractionType.RTCC_CONSOLE,
            )
            
            response = engine.process_input(session.session_id, "Request action")
            
            assert response.explainability_trace is not None
            assert len(response.explainability_trace.constraints_checked) > 0


class TestInteractionSession:
    """Tests for InteractionSession dataclass."""
    
    def test_session_to_dict(self):
        """Test session serialization."""
        session = InteractionSession(
            session_id="test-session",
            persona_id="persona-001",
            user_id="user-001",
            interaction_type=InteractionType.RTCC_CONSOLE,
        )
        
        data = session.to_dict()
        
        assert data["session_id"] == "test-session"
        assert data["persona_id"] == "persona-001"
        assert data["user_id"] == "user-001"
        assert "interaction_type" in data
        assert "is_active" in data


class TestConversationTurn:
    """Tests for ConversationTurn dataclass."""
    
    def test_turn_creation(self):
        """Test creating a conversation turn."""
        turn = ConversationTurn(
            turn_id="turn-001",
            user_input="Hello",
            persona_response="Hi, how can I help?",
            intent_analysis=IntentAnalysis(
                category=IntentCategory.GREETING,
                confidence=0.9,
                urgency=UrgencyLevel.LOW,
                emotion=EmotionDetected.NEUTRAL,
                domain=DomainType.GENERAL,
                keywords=[],
                entities={},
            ),
        )
        
        assert turn.turn_id == "turn-001"
        assert turn.user_input == "Hello"
        assert turn.persona_response == "Hi, how can I help?"
    
    def test_turn_to_dict(self):
        """Test turn serialization."""
        turn = ConversationTurn(
            turn_id="turn-002",
            user_input="Test",
            persona_response="Response",
            intent_analysis=IntentAnalysis(
                category=IntentCategory.QUERY,
                confidence=0.8,
                urgency=UrgencyLevel.MEDIUM,
                emotion=EmotionDetected.NEUTRAL,
                domain=DomainType.PATROL,
                keywords=["test"],
                entities={},
            ),
        )
        
        data = turn.to_dict()
        
        assert data["turn_id"] == "turn-002"
        assert "user_input" in data
        assert "persona_response" in data
        assert "intent_analysis" in data
