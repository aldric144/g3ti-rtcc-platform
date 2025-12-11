"""
Phase 30: Crisis Routing Tests

Tests for:
- Co-responder routing decisions
- Priority determination
- De-escalation prompts
- Responder type selection
"""

import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))


class TestCrisisRouting:
    """Tests for crisis routing functionality"""
    
    def test_route_welfare_check(self):
        """Test routing for welfare check"""
        from backend.app.human_intel.crisis_intervention_engine import (
            CrisisInterventionEngine, InterventionPriority
        )
        
        engine = CrisisInterventionEngine()
        
        decision = engine.route_crisis_call(
            call_narrative="Neighbor hasn't been seen in days",
            call_type="welfare_check",
        )
        
        assert decision is not None
        assert decision.priority == InterventionPriority.ROUTINE
    
    def test_route_mental_health_crisis(self):
        """Test routing for mental health crisis"""
        from backend.app.human_intel.crisis_intervention_engine import (
            CrisisInterventionEngine, InterventionPriority, ResponderType
        )
        
        engine = CrisisInterventionEngine()
        
        decision = engine.route_crisis_call(
            call_narrative="Subject having mental health crisis",
            call_type="mental_health",
        )
        
        assert decision is not None
        assert decision.priority.value >= InterventionPriority.ELEVATED.value
        assert ResponderType.MENTAL_HEALTH_CLINICIAN in decision.co_responder_recommendation.co_responders
    
    def test_route_suicide_ideation(self):
        """Test routing for suicide ideation"""
        from backend.app.human_intel.crisis_intervention_engine import (
            CrisisInterventionEngine, InterventionPriority, ResponderType
        )
        
        engine = CrisisInterventionEngine()
        
        decision = engine.route_crisis_call(
            call_narrative="Subject threatening suicide",
            call_type="suicide_ideation",
        )
        
        assert decision is not None
        assert decision.priority == InterventionPriority.CRITICAL
        assert decision.co_responder_recommendation.primary_responder == ResponderType.CRISIS_INTERVENTION_TEAM
    
    def test_route_domestic_violence(self):
        """Test routing for domestic violence"""
        from backend.app.human_intel.crisis_intervention_engine import (
            CrisisInterventionEngine, ResponderType
        )
        
        engine = CrisisInterventionEngine()
        
        decision = engine.route_crisis_call(
            call_narrative="Domestic violence in progress",
            call_type="domestic_violence",
            violence_mentioned=True,
        )
        
        assert decision is not None
        assert ResponderType.DV_ADVOCATE in decision.co_responder_recommendation.co_responders
    
    def test_route_substance_crisis(self):
        """Test routing for substance crisis"""
        from backend.app.human_intel.crisis_intervention_engine import (
            CrisisInterventionEngine, InterventionPriority, ResponderType
        )
        
        engine = CrisisInterventionEngine()
        
        decision = engine.route_crisis_call(
            call_narrative="Possible overdose",
            call_type="substance_crisis",
            substance_involved=True,
        )
        
        assert decision is not None
        assert decision.priority == InterventionPriority.EMERGENCY
        assert decision.co_responder_recommendation.primary_responder == ResponderType.FIRE_RESCUE
    
    def test_route_behavioral_disturbance(self):
        """Test routing for behavioral disturbance"""
        from backend.app.human_intel.crisis_intervention_engine import (
            CrisisInterventionEngine, InterventionPriority
        )
        
        engine = CrisisInterventionEngine()
        
        decision = engine.route_crisis_call(
            call_narrative="Subject acting erratically",
            call_type="behavioral_disturbance",
        )
        
        assert decision is not None
        assert decision.priority.value >= InterventionPriority.ELEVATED.value
    
    def test_route_youth_crisis(self):
        """Test routing for youth crisis"""
        from backend.app.human_intel.crisis_intervention_engine import (
            CrisisInterventionEngine, ResponderType
        )
        
        engine = CrisisInterventionEngine()
        
        decision = engine.route_crisis_call(
            call_narrative="Youth in crisis",
            call_type="youth_crisis",
            youth_involved=True,
        )
        
        assert decision is not None
        assert "Youth involved" in str(decision.co_responder_recommendation.special_considerations)
    
    def test_route_with_weapons(self):
        """Test routing with weapons mentioned"""
        from backend.app.human_intel.crisis_intervention_engine import (
            CrisisInterventionEngine, InterventionPriority, ResponderType
        )
        
        engine = CrisisInterventionEngine()
        
        decision = engine.route_crisis_call(
            call_narrative="Subject has a gun",
            call_type="behavioral_disturbance",
            weapons_mentioned=True,
        )
        
        assert decision is not None
        assert decision.priority == InterventionPriority.CRITICAL
        assert ResponderType.POLICE in decision.co_responder_recommendation.co_responders
    
    def test_route_with_violence(self):
        """Test routing with violence mentioned"""
        from backend.app.human_intel.crisis_intervention_engine import (
            CrisisInterventionEngine, InterventionPriority
        )
        
        engine = CrisisInterventionEngine()
        
        decision = engine.route_crisis_call(
            call_narrative="Subject is violent",
            call_type="behavioral_disturbance",
            violence_mentioned=True,
        )
        
        assert decision is not None
        assert decision.priority.value >= InterventionPriority.URGENT.value
    
    def test_route_elderly_involved(self):
        """Test routing with elderly involved"""
        from backend.app.human_intel.crisis_intervention_engine import CrisisInterventionEngine
        
        engine = CrisisInterventionEngine()
        
        decision = engine.route_crisis_call(
            call_narrative="Elderly person in distress",
            call_type="welfare_check",
            elderly_involved=True,
        )
        
        assert decision is not None
        assert "Elderly involved" in str(decision.co_responder_recommendation.special_considerations)


class TestDeEscalationPrompts:
    """Tests for de-escalation prompts"""
    
    def test_de_escalation_prompts_mental_health(self):
        """Test de-escalation prompts for mental health"""
        from backend.app.human_intel.crisis_intervention_engine import CrisisInterventionEngine
        
        engine = CrisisInterventionEngine()
        
        decision = engine.route_crisis_call(
            call_narrative="Mental health crisis",
            call_type="mental_health",
        )
        
        assert decision is not None
        assert len(decision.trauma_informed_guidance.de_escalation_prompts) > 0
    
    def test_de_escalation_prompts_suicide(self):
        """Test de-escalation prompts for suicide"""
        from backend.app.human_intel.crisis_intervention_engine import CrisisInterventionEngine
        
        engine = CrisisInterventionEngine()
        
        decision = engine.route_crisis_call(
            call_narrative="Suicide ideation",
            call_type="suicide_ideation",
        )
        
        assert decision is not None
        assert len(decision.trauma_informed_guidance.de_escalation_prompts) > 0
    
    def test_de_escalation_prompts_dv(self):
        """Test de-escalation prompts for DV"""
        from backend.app.human_intel.crisis_intervention_engine import CrisisInterventionEngine
        
        engine = CrisisInterventionEngine()
        
        decision = engine.route_crisis_call(
            call_narrative="Domestic violence",
            call_type="domestic_violence",
        )
        
        assert decision is not None
        assert len(decision.trauma_informed_guidance.de_escalation_prompts) > 0
    
    def test_communication_strategies_provided(self):
        """Test communication strategies are provided"""
        from backend.app.human_intel.crisis_intervention_engine import CrisisInterventionEngine
        
        engine = CrisisInterventionEngine()
        
        decision = engine.route_crisis_call(
            call_narrative="Crisis call",
            call_type="mental_health",
        )
        
        assert decision is not None
        assert len(decision.trauma_informed_guidance.communication_strategies) > 0
    
    def test_safety_considerations_provided(self):
        """Test safety considerations are provided"""
        from backend.app.human_intel.crisis_intervention_engine import CrisisInterventionEngine
        
        engine = CrisisInterventionEngine()
        
        decision = engine.route_crisis_call(
            call_narrative="Crisis call",
            call_type="mental_health",
        )
        
        assert decision is not None
        assert len(decision.trauma_informed_guidance.safety_considerations) > 0
    
    def test_resources_provided(self):
        """Test resources are provided"""
        from backend.app.human_intel.crisis_intervention_engine import CrisisInterventionEngine
        
        engine = CrisisInterventionEngine()
        
        decision = engine.route_crisis_call(
            call_narrative="Crisis call",
            call_type="welfare_check",
        )
        
        assert decision is not None
        assert len(decision.trauma_informed_guidance.resources_to_provide) > 0
        assert "988 Suicide & Crisis Lifeline" in decision.trauma_informed_guidance.resources_to_provide


class TestResponderSelection:
    """Tests for responder selection"""
    
    def test_primary_responder_cit_for_suicide(self):
        """Test CIT is primary for suicide"""
        from backend.app.human_intel.crisis_intervention_engine import (
            CrisisInterventionEngine, ResponderType
        )
        
        engine = CrisisInterventionEngine()
        
        decision = engine.route_crisis_call(
            call_narrative="Suicide threat",
            call_type="suicide_ideation",
        )
        
        assert decision is not None
        assert decision.co_responder_recommendation.primary_responder == ResponderType.CRISIS_INTERVENTION_TEAM
    
    def test_primary_responder_fire_rescue_for_overdose(self):
        """Test Fire/Rescue is primary for overdose"""
        from backend.app.human_intel.crisis_intervention_engine import (
            CrisisInterventionEngine, ResponderType
        )
        
        engine = CrisisInterventionEngine()
        
        decision = engine.route_crisis_call(
            call_narrative="Overdose",
            call_type="substance_crisis",
            substance_involved=True,
        )
        
        assert decision is not None
        assert decision.co_responder_recommendation.primary_responder == ResponderType.FIRE_RESCUE
    
    def test_co_responder_dv_advocate_for_dv(self):
        """Test DV advocate is co-responder for DV"""
        from backend.app.human_intel.crisis_intervention_engine import (
            CrisisInterventionEngine, ResponderType
        )
        
        engine = CrisisInterventionEngine()
        
        decision = engine.route_crisis_call(
            call_narrative="Domestic violence",
            call_type="domestic_violence",
        )
        
        assert decision is not None
        assert ResponderType.DV_ADVOCATE in decision.co_responder_recommendation.co_responders
    
    def test_co_responder_clinician_for_mental_health(self):
        """Test clinician is co-responder for mental health"""
        from backend.app.human_intel.crisis_intervention_engine import (
            CrisisInterventionEngine, ResponderType
        )
        
        engine = CrisisInterventionEngine()
        
        decision = engine.route_crisis_call(
            call_narrative="Mental health crisis",
            call_type="mental_health",
        )
        
        assert decision is not None
        assert ResponderType.MENTAL_HEALTH_CLINICIAN in decision.co_responder_recommendation.co_responders
    
    def test_police_included_when_weapons(self):
        """Test police included when weapons mentioned"""
        from backend.app.human_intel.crisis_intervention_engine import (
            CrisisInterventionEngine, ResponderType
        )
        
        engine = CrisisInterventionEngine()
        
        decision = engine.route_crisis_call(
            call_narrative="Subject has weapon",
            call_type="behavioral_disturbance",
            weapons_mentioned=True,
        )
        
        assert decision is not None
        assert ResponderType.POLICE in decision.co_responder_recommendation.co_responders
