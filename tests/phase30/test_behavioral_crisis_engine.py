"""
Phase 30: Behavioral Crisis Detection Engine Tests

Tests for:
- Suicide risk detection
- DV escalation prediction
- Community trauma pulse monitoring
- Stability index calculation
"""

import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))


class TestBehavioralCrisisEngine:
    """Tests for BehavioralCrisisEngine"""
    
    def test_engine_singleton(self):
        """Test that engine is a singleton"""
        from backend.app.human_intel.behavioral_crisis_engine import BehavioralCrisisEngine
        
        engine1 = BehavioralCrisisEngine()
        engine2 = BehavioralCrisisEngine()
        
        assert engine1 is engine2
    
    def test_engine_initialization(self):
        """Test engine initializes with correct agency config"""
        from backend.app.human_intel.behavioral_crisis_engine import BehavioralCrisisEngine
        
        engine = BehavioralCrisisEngine()
        
        assert engine.agency_config["ori"] == "FL0500400"
        assert engine.agency_config["city"] == "Riviera Beach"
        assert engine.agency_config["state"] == "FL"
    
    def test_suicide_risk_levels_enum(self):
        """Test SuicideRiskLevel enum values"""
        from backend.app.human_intel.behavioral_crisis_engine import SuicideRiskLevel
        
        assert SuicideRiskLevel.LOW.value == 1
        assert SuicideRiskLevel.MODERATE.value == 2
        assert SuicideRiskLevel.HIGH.value == 3
        assert SuicideRiskLevel.IMMEDIATE_DANGER.value == 4
    
    def test_dv_escalation_levels_enum(self):
        """Test DVEscalationLevel enum values"""
        from backend.app.human_intel.behavioral_crisis_engine import DVEscalationLevel
        
        assert DVEscalationLevel.MINIMAL.value == 1
        assert DVEscalationLevel.LOW.value == 2
        assert DVEscalationLevel.MODERATE.value == 3
        assert DVEscalationLevel.HIGH.value == 4
        assert DVEscalationLevel.EXTREME.value == 5
    
    def test_crisis_type_enum(self):
        """Test CrisisType enum values"""
        from backend.app.human_intel.behavioral_crisis_engine import CrisisType
        
        assert CrisisType.SUICIDE_IDEATION.value == "suicide_ideation"
        assert CrisisType.DOMESTIC_VIOLENCE.value == "domestic_violence"
        assert CrisisType.MENTAL_HEALTH_CRISIS.value == "mental_health_crisis"
    
    def test_suicide_risk_assessment_dataclass(self):
        """Test SuicideRiskAssessment dataclass"""
        from backend.app.human_intel.behavioral_crisis_engine import (
            SuicideRiskAssessment, SuicideRiskLevel
        )
        
        assessment = SuicideRiskAssessment(
            assessment_id="SR-TEST001",
            timestamp=datetime.utcnow(),
            risk_level=SuicideRiskLevel.HIGH,
            confidence_score=0.85,
            risk_factors=["crisis_language_detected"],
            protective_factors=["support_system_present"],
            crisis_phrases_detected=["want to die"],
            prior_welfare_checks=2,
            call_escalation_pattern=True,
            recommended_actions=["Dispatch crisis team"],
            auto_alert_triggered=True,
            alert_recipients=["RTCC"],
            anonymization_level="FULL",
            privacy_protections=["No PII stored"],
            data_sources_used=["911_call"],
        )
        
        assert assessment.assessment_id == "SR-TEST001"
        assert assessment.risk_level == SuicideRiskLevel.HIGH
        assert len(assessment.chain_of_custody_hash) == 64
    
    def test_dv_escalation_assessment_dataclass(self):
        """Test DVEscalationAssessment dataclass"""
        from backend.app.human_intel.behavioral_crisis_engine import (
            DVEscalationAssessment, DVEscalationLevel
        )
        
        assessment = DVEscalationAssessment(
            assessment_id="DV-TEST001",
            timestamp=datetime.utcnow(),
            escalation_level=DVEscalationLevel.HIGH,
            lethality_risk_score=0.65,
            confidence_score=0.80,
            risk_factors=["weapon_present"],
            repeat_call_count=3,
            time_pattern_risk=True,
            alcohol_related=True,
            weapons_present=True,
            prior_threats=True,
            aggressor_behavior_signatures=["strangulation"],
            intervention_pathway="ENHANCED_RESPONSE",
            recommended_actions=["Priority dispatch"],
            campbell_danger_indicators=["weapon_in_home"],
            anonymization_level="FULL",
            privacy_protections=["Victim identity protected"],
            data_sources_used=["911_call"],
        )
        
        assert assessment.assessment_id == "DV-TEST001"
        assert assessment.escalation_level == DVEscalationLevel.HIGH
        assert assessment.lethality_risk_score == 0.65
    
    def test_community_trauma_pulse_dataclass(self):
        """Test CommunityTraumaPulse dataclass"""
        from backend.app.human_intel.behavioral_crisis_engine import CommunityTraumaPulse
        
        pulse = CommunityTraumaPulse(
            pulse_id="CTP-TEST001",
            timestamp=datetime.utcnow(),
            stability_index=75.0,
            trauma_clusters=[{"cluster_id": "TC-001"}],
            community_shock_level=0.25,
            school_disturbances=[],
            youth_violence_warnings=[],
            at_risk_polygons=[],
            trend_direction="stable",
            recommended_interventions=["Community outreach"],
            anonymization_level="AGGREGATED",
            privacy_protections=["All data aggregated"],
        )
        
        assert pulse.pulse_id == "CTP-TEST001"
        assert pulse.stability_index == 75.0
    
    def test_stability_index_dataclass(self):
        """Test StabilityIndex dataclass"""
        from backend.app.human_intel.behavioral_crisis_engine import StabilityIndex
        
        index = StabilityIndex(
            index_id="SI-TEST001",
            timestamp=datetime.utcnow(),
            overall_score=74.5,
            mental_health_score=72.0,
            violence_score=78.0,
            community_cohesion_score=70.0,
            youth_stability_score=68.0,
            trend_7_day=0.5,
            trend_30_day=1.2,
            high_risk_areas=[],
        )
        
        assert index.index_id == "SI-TEST001"
        assert index.overall_score == 74.5
    
    def test_get_stability_index(self):
        """Test get_stability_index method"""
        from backend.app.human_intel.behavioral_crisis_engine import BehavioralCrisisEngine
        
        engine = BehavioralCrisisEngine()
        index = engine.get_stability_index()
        
        assert index is not None
        assert 0 <= index.overall_score <= 100
        assert 0 <= index.mental_health_score <= 100
        assert 0 <= index.violence_score <= 100
    
    def test_get_community_trauma_pulse(self):
        """Test get_community_trauma_pulse method"""
        from backend.app.human_intel.behavioral_crisis_engine import BehavioralCrisisEngine
        
        engine = BehavioralCrisisEngine()
        pulse = engine.get_community_trauma_pulse(time_window_hours=72)
        
        assert pulse is not None
        assert 0 <= pulse.stability_index <= 100
        assert pulse.anonymization_level == "AGGREGATED"
    
    def test_get_statistics(self):
        """Test get_statistics method"""
        from backend.app.human_intel.behavioral_crisis_engine import BehavioralCrisisEngine
        
        engine = BehavioralCrisisEngine()
        stats = engine.get_statistics()
        
        assert "total_suicide_assessments" in stats
        assert "total_dv_assessments" in stats
        assert "agency" in stats
        assert stats["agency"]["ori"] == "FL0500400"


class TestSuicideRiskAssessment:
    """Tests for suicide risk assessment functionality"""
    
    def test_assess_suicide_risk_low(self):
        """Test low risk assessment"""
        from backend.app.human_intel.behavioral_crisis_engine import BehavioralCrisisEngine, SuicideRiskLevel
        
        engine = BehavioralCrisisEngine()
        
        assessment = engine.assess_suicide_risk(
            call_narrative="Caller reports neighbor hasn't been seen in a few days",
            caller_type="neighbor",
            prior_welfare_checks=0,
            prior_crisis_calls=0,
        )
        
        assert assessment is not None
        assert assessment.risk_level == SuicideRiskLevel.LOW
    
    def test_assess_suicide_risk_high(self):
        """Test high risk assessment with crisis phrases"""
        from backend.app.human_intel.behavioral_crisis_engine import BehavioralCrisisEngine, SuicideRiskLevel
        
        engine = BehavioralCrisisEngine()
        
        assessment = engine.assess_suicide_risk(
            call_narrative="Subject says they want to die and can't go on anymore",
            caller_type="family",
            prior_welfare_checks=2,
            prior_crisis_calls=1,
        )
        
        assert assessment is not None
        assert assessment.risk_level in [SuicideRiskLevel.HIGH, SuicideRiskLevel.IMMEDIATE_DANGER]
        assert len(assessment.crisis_phrases_detected) > 0
    
    def test_assess_suicide_risk_immediate_danger(self):
        """Test immediate danger assessment"""
        from backend.app.human_intel.behavioral_crisis_engine import BehavioralCrisisEngine, SuicideRiskLevel
        
        engine = BehavioralCrisisEngine()
        
        assessment = engine.assess_suicide_risk(
            call_narrative="Subject is threatening suicide and has a weapon",
            caller_type="self",
            prior_welfare_checks=3,
            prior_crisis_calls=2,
        )
        
        assert assessment is not None
        assert assessment.risk_level == SuicideRiskLevel.IMMEDIATE_DANGER
        assert assessment.auto_alert_triggered == True
    
    def test_assess_suicide_risk_privacy_protections(self):
        """Test that privacy protections are applied"""
        from backend.app.human_intel.behavioral_crisis_engine import BehavioralCrisisEngine
        
        engine = BehavioralCrisisEngine()
        
        assessment = engine.assess_suicide_risk(
            call_narrative="Test narrative",
            caller_type="unknown",
        )
        
        assert assessment is not None
        assert assessment.anonymization_level == "FULL"
        assert len(assessment.privacy_protections) > 0
        assert "No PII stored" in assessment.privacy_protections


class TestDVEscalationAssessment:
    """Tests for DV escalation assessment functionality"""
    
    def test_assess_dv_escalation_minimal(self):
        """Test minimal escalation assessment"""
        from backend.app.human_intel.behavioral_crisis_engine import BehavioralCrisisEngine, DVEscalationLevel
        
        engine = BehavioralCrisisEngine()
        
        assessment = engine.assess_dv_escalation(
            incident_narrative="Verbal argument between couple, no violence",
            repeat_call_count=0,
        )
        
        assert assessment is not None
        assert assessment.escalation_level in [DVEscalationLevel.MINIMAL, DVEscalationLevel.LOW]
    
    def test_assess_dv_escalation_high(self):
        """Test high escalation assessment with Campbell indicators"""
        from backend.app.human_intel.behavioral_crisis_engine import BehavioralCrisisEngine, DVEscalationLevel
        
        engine = BehavioralCrisisEngine()
        
        assessment = engine.assess_dv_escalation(
            incident_narrative="Subject has been strangled before and threatened to kill victim",
            repeat_call_count=3,
            alcohol_involved=True,
            weapons_present=True,
            prior_threats=True,
            strangulation_history=True,
        )
        
        assert assessment is not None
        assert assessment.escalation_level in [DVEscalationLevel.HIGH, DVEscalationLevel.EXTREME]
        assert assessment.lethality_risk_score >= 0.5
        assert len(assessment.campbell_danger_indicators) > 0
    
    def test_assess_dv_escalation_extreme(self):
        """Test extreme escalation assessment"""
        from backend.app.human_intel.behavioral_crisis_engine import BehavioralCrisisEngine, DVEscalationLevel
        
        engine = BehavioralCrisisEngine()
        
        assessment = engine.assess_dv_escalation(
            incident_narrative="Victim being choked, gun in home, death threats made",
            repeat_call_count=5,
            alcohol_involved=True,
            weapons_present=True,
            prior_threats=True,
            strangulation_history=True,
            separation_attempt=True,
            victim_pregnant=True,
        )
        
        assert assessment is not None
        assert assessment.escalation_level == DVEscalationLevel.EXTREME
        assert assessment.intervention_pathway == "IMMEDIATE_SAFETY_INTERVENTION"
    
    def test_assess_dv_escalation_vawa_protections(self):
        """Test that VAWA protections are applied"""
        from backend.app.human_intel.behavioral_crisis_engine import BehavioralCrisisEngine
        
        engine = BehavioralCrisisEngine()
        
        assessment = engine.assess_dv_escalation(
            incident_narrative="Test DV incident",
        )
        
        assert assessment is not None
        assert "Victim identity protected" in assessment.privacy_protections
        assert "VAWA protections applied" in assessment.privacy_protections
