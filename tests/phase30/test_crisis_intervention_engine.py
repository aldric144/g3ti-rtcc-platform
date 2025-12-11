"""
Phase 30: Crisis Intervention Routing Engine Tests

Tests for:
- Co-responder routing
- Trauma-informed guidance
- Repeat crisis flagging
- Crisis routing decisions
"""

import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))


class TestCrisisInterventionEngine:
    """Tests for CrisisInterventionEngine"""
    
    def test_engine_singleton(self):
        """Test that engine is a singleton"""
        from backend.app.human_intel.crisis_intervention_engine import CrisisInterventionEngine
        
        engine1 = CrisisInterventionEngine()
        engine2 = CrisisInterventionEngine()
        
        assert engine1 is engine2
    
    def test_engine_initialization(self):
        """Test engine initializes with correct agency config"""
        from backend.app.human_intel.crisis_intervention_engine import CrisisInterventionEngine
        
        engine = CrisisInterventionEngine()
        
        assert engine.agency_config["ori"] == "FL0500400"
        assert engine.agency_config["city"] == "Riviera Beach"
    
    def test_responder_type_enum(self):
        """Test ResponderType enum values"""
        from backend.app.human_intel.crisis_intervention_engine import ResponderType
        
        assert ResponderType.POLICE.value == "police"
        assert ResponderType.MENTAL_HEALTH_CLINICIAN.value == "mental_health_clinician"
        assert ResponderType.DV_ADVOCATE.value == "dv_advocate"
        assert ResponderType.CRISIS_INTERVENTION_TEAM.value == "crisis_intervention_team"
    
    def test_intervention_priority_enum(self):
        """Test InterventionPriority enum values"""
        from backend.app.human_intel.crisis_intervention_engine import InterventionPriority
        
        assert InterventionPriority.ROUTINE.value == 1
        assert InterventionPriority.ELEVATED.value == 2
        assert InterventionPriority.URGENT.value == 3
        assert InterventionPriority.EMERGENCY.value == 4
        assert InterventionPriority.CRITICAL.value == 5
    
    def test_crisis_category_enum(self):
        """Test CrisisCategory enum values"""
        from backend.app.human_intel.crisis_intervention_engine import CrisisCategory
        
        assert CrisisCategory.MENTAL_HEALTH.value == "mental_health"
        assert CrisisCategory.SUICIDE_IDEATION.value == "suicide_ideation"
        assert CrisisCategory.DOMESTIC_VIOLENCE.value == "domestic_violence"
    
    def test_co_responder_recommendation_dataclass(self):
        """Test CoResponderRecommendation dataclass"""
        from backend.app.human_intel.crisis_intervention_engine import (
            CoResponderRecommendation, CrisisCategory, InterventionPriority, ResponderType
        )
        
        rec = CoResponderRecommendation(
            recommendation_id="CR-TEST001",
            timestamp=datetime.utcnow(),
            crisis_category=CrisisCategory.MENTAL_HEALTH,
            priority=InterventionPriority.URGENT,
            primary_responder=ResponderType.CRISIS_INTERVENTION_TEAM,
            co_responders=[ResponderType.MENTAL_HEALTH_CLINICIAN],
            rationale="Mental health crisis detected",
            special_considerations=["Approach with caution"],
            estimated_response_time=8,
            recommended_approach="Trauma-informed",
            anonymization_level="FULL",
            privacy_protections=["No PII"],
        )
        
        assert rec.recommendation_id == "CR-TEST001"
        assert rec.priority == InterventionPriority.URGENT
    
    def test_trauma_informed_guidance_dataclass(self):
        """Test TraumaInformedGuidance dataclass"""
        from backend.app.human_intel.crisis_intervention_engine import TraumaInformedGuidance
        
        guidance = TraumaInformedGuidance(
            guidance_id="TIG-TEST001",
            timestamp=datetime.utcnow(),
            crisis_type="mental_health_crisis",
            de_escalation_prompts=["Use calm tone"],
            communication_strategies=["Listen actively"],
            clinician_involvement="RECOMMENDED",
            safety_considerations=["Assess for weapons"],
            cultural_considerations=["Be aware of differences"],
            follow_up_recommendations=["Document thoroughly"],
            resources_to_provide=["988 Lifeline"],
        )
        
        assert guidance.guidance_id == "TIG-TEST001"
        assert len(guidance.de_escalation_prompts) > 0
    
    def test_repeat_crisis_flag_dataclass(self):
        """Test RepeatCrisisFlag dataclass"""
        from backend.app.human_intel.crisis_intervention_engine import (
            RepeatCrisisFlag, RepeatCrisisType
        )
        
        flag = RepeatCrisisFlag(
            flag_id="RCF-TEST001",
            timestamp=datetime.utcnow(),
            crisis_type=RepeatCrisisType.WELFARE_CHECK,
            occurrence_count=5,
            time_span_days=90,
            pattern_description="Repeat welfare check pattern",
            escalation_trend="stable",
            intervention_history=["Prior responses"],
            recommended_intervention="Case management",
            case_management_referral=True,
            anonymization_level="FULL",
            privacy_protections=["No PII"],
        )
        
        assert flag.flag_id == "RCF-TEST001"
        assert flag.case_management_referral == True


class TestCrisisRouting:
    """Tests for crisis routing functionality"""
    
    def test_route_crisis_call_welfare_check(self):
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
    
    def test_route_crisis_call_suicide(self):
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
    
    def test_route_crisis_call_dv(self):
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
    
    def test_route_crisis_call_weapons(self):
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
    
    def test_route_crisis_call_youth(self):
        """Test routing with youth involved"""
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
    
    def test_route_crisis_call_substance(self):
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


class TestTraumaInformedGuidance:
    """Tests for trauma-informed guidance"""
    
    def test_de_escalation_prompts_mental_health(self):
        """Test de-escalation prompts for mental health crisis"""
        from backend.app.human_intel.crisis_intervention_engine import CrisisInterventionEngine
        
        engine = CrisisInterventionEngine()
        
        decision = engine.route_crisis_call(
            call_narrative="Mental health crisis",
            call_type="mental_health",
        )
        
        assert decision is not None
        assert len(decision.trauma_informed_guidance.de_escalation_prompts) > 0
    
    def test_clinician_involvement_suicide(self):
        """Test clinician involvement for suicide"""
        from backend.app.human_intel.crisis_intervention_engine import CrisisInterventionEngine
        
        engine = CrisisInterventionEngine()
        
        decision = engine.route_crisis_call(
            call_narrative="Suicide ideation",
            call_type="suicide_ideation",
        )
        
        assert decision is not None
        assert "IMMEDIATE" in decision.trauma_informed_guidance.clinician_involvement
    
    def test_resources_provided(self):
        """Test that resources are provided"""
        from backend.app.human_intel.crisis_intervention_engine import CrisisInterventionEngine
        
        engine = CrisisInterventionEngine()
        
        decision = engine.route_crisis_call(
            call_narrative="Crisis call",
            call_type="welfare_check",
        )
        
        assert decision is not None
        assert len(decision.trauma_informed_guidance.resources_to_provide) > 0
        assert "988 Suicide & Crisis Lifeline" in decision.trauma_informed_guidance.resources_to_provide


class TestRepeatCrisisDetection:
    """Tests for repeat crisis detection"""
    
    def test_detect_repeat_crisis(self):
        """Test repeat crisis detection"""
        from backend.app.human_intel.crisis_intervention_engine import CrisisInterventionEngine
        
        engine = CrisisInterventionEngine()
        
        flag = engine.detect_repeat_crisis(
            location_zone="Zone_A",
            crisis_type="welfare_check",
            time_window_days=90,
        )
        
        assert flag is not None
        assert flag.occurrence_count >= 3
    
    def test_repeat_crisis_case_management_referral(self):
        """Test case management referral for repeat crisis"""
        from backend.app.human_intel.crisis_intervention_engine import CrisisInterventionEngine
        
        engine = CrisisInterventionEngine()
        
        decision = engine.route_crisis_call(
            call_narrative="Repeat welfare check",
            call_type="welfare_check",
            prior_calls_count=5,
        )
        
        assert decision is not None
        if decision.repeat_crisis_flag:
            assert decision.repeat_crisis_flag.case_management_referral == True
    
    def test_get_statistics(self):
        """Test get_statistics method"""
        from backend.app.human_intel.crisis_intervention_engine import CrisisInterventionEngine
        
        engine = CrisisInterventionEngine()
        stats = engine.get_statistics()
        
        assert "total_routing_decisions" in stats
        assert "total_repeat_crisis_flags" in stats
        assert "agency" in stats
