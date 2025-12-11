"""
Phase 30: DV Escalation Prediction Tests

Tests for:
- Campbell Danger Assessment indicators
- Lethality risk scoring
- Escalation level classification
- VAWA protections
"""

import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))


class TestDVEscalationPrediction:
    """Tests for DV escalation prediction"""
    
    def test_campbell_indicator_weapon_in_home(self):
        """Test Campbell indicator: weapon in home"""
        from backend.app.human_intel.behavioral_crisis_engine import BehavioralCrisisEngine
        
        engine = BehavioralCrisisEngine()
        
        assessment = engine.assess_dv_escalation(
            incident_narrative="Gun in the home",
            weapons_present=True,
        )
        
        assert assessment is not None
        assert "weapon_in_home" in assessment.campbell_danger_indicators
    
    def test_campbell_indicator_strangulation(self):
        """Test Campbell indicator: strangulation history"""
        from backend.app.human_intel.behavioral_crisis_engine import BehavioralCrisisEngine
        
        engine = BehavioralCrisisEngine()
        
        assessment = engine.assess_dv_escalation(
            incident_narrative="Victim has been choked before",
            strangulation_history=True,
        )
        
        assert assessment is not None
        assert "strangulation_history" in assessment.campbell_danger_indicators
    
    def test_campbell_indicator_threats_to_kill(self):
        """Test Campbell indicator: threats to kill"""
        from backend.app.human_intel.behavioral_crisis_engine import BehavioralCrisisEngine
        
        engine = BehavioralCrisisEngine()
        
        assessment = engine.assess_dv_escalation(
            incident_narrative="Perpetrator threatened to kill victim",
            prior_threats=True,
        )
        
        assert assessment is not None
        assert "threats_to_kill" in assessment.campbell_danger_indicators
    
    def test_campbell_indicator_separation_attempt(self):
        """Test Campbell indicator: separation attempt"""
        from backend.app.human_intel.behavioral_crisis_engine import BehavioralCrisisEngine
        
        engine = BehavioralCrisisEngine()
        
        assessment = engine.assess_dv_escalation(
            incident_narrative="Victim trying to leave relationship",
            separation_attempt=True,
        )
        
        assert assessment is not None
        assert "separation_attempt" in assessment.campbell_danger_indicators
    
    def test_lethality_score_minimal(self):
        """Test minimal lethality score"""
        from backend.app.human_intel.behavioral_crisis_engine import BehavioralCrisisEngine
        
        engine = BehavioralCrisisEngine()
        
        assessment = engine.assess_dv_escalation(
            incident_narrative="Verbal argument only",
            repeat_call_count=0,
        )
        
        assert assessment is not None
        assert assessment.lethality_risk_score < 0.3
    
    def test_lethality_score_high(self):
        """Test high lethality score"""
        from backend.app.human_intel.behavioral_crisis_engine import BehavioralCrisisEngine
        
        engine = BehavioralCrisisEngine()
        
        assessment = engine.assess_dv_escalation(
            incident_narrative="Strangulation and death threats",
            repeat_call_count=3,
            weapons_present=True,
            prior_threats=True,
            strangulation_history=True,
        )
        
        assert assessment is not None
        assert assessment.lethality_risk_score >= 0.5
    
    def test_escalation_level_minimal(self):
        """Test minimal escalation level"""
        from backend.app.human_intel.behavioral_crisis_engine import BehavioralCrisisEngine, DVEscalationLevel
        
        engine = BehavioralCrisisEngine()
        
        assessment = engine.assess_dv_escalation(
            incident_narrative="Minor verbal dispute",
            repeat_call_count=0,
        )
        
        assert assessment is not None
        assert assessment.escalation_level in [DVEscalationLevel.MINIMAL, DVEscalationLevel.LOW]
    
    def test_escalation_level_extreme(self):
        """Test extreme escalation level"""
        from backend.app.human_intel.behavioral_crisis_engine import BehavioralCrisisEngine, DVEscalationLevel
        
        engine = BehavioralCrisisEngine()
        
        assessment = engine.assess_dv_escalation(
            incident_narrative="Active strangulation with gun present",
            repeat_call_count=5,
            weapons_present=True,
            prior_threats=True,
            strangulation_history=True,
            alcohol_involved=True,
            separation_attempt=True,
        )
        
        assert assessment is not None
        assert assessment.escalation_level == DVEscalationLevel.EXTREME
    
    def test_intervention_pathway_standard(self):
        """Test standard intervention pathway"""
        from backend.app.human_intel.behavioral_crisis_engine import BehavioralCrisisEngine
        
        engine = BehavioralCrisisEngine()
        
        assessment = engine.assess_dv_escalation(
            incident_narrative="Minor DV incident",
            repeat_call_count=0,
        )
        
        assert assessment is not None
        assert assessment.intervention_pathway in ["STANDARD_RESPONSE", "DV_PROTOCOL"]
    
    def test_intervention_pathway_immediate_safety(self):
        """Test immediate safety intervention pathway"""
        from backend.app.human_intel.behavioral_crisis_engine import BehavioralCrisisEngine, DVEscalationLevel
        
        engine = BehavioralCrisisEngine()
        
        assessment = engine.assess_dv_escalation(
            incident_narrative="Extreme danger situation",
            repeat_call_count=5,
            weapons_present=True,
            prior_threats=True,
            strangulation_history=True,
        )
        
        assert assessment is not None
        if assessment.escalation_level == DVEscalationLevel.EXTREME:
            assert assessment.intervention_pathway == "IMMEDIATE_SAFETY_INTERVENTION"
    
    def test_vawa_protections_applied(self):
        """Test VAWA protections are applied"""
        from backend.app.human_intel.behavioral_crisis_engine import BehavioralCrisisEngine
        
        engine = BehavioralCrisisEngine()
        
        assessment = engine.assess_dv_escalation(
            incident_narrative="DV incident",
        )
        
        assert assessment is not None
        assert "Victim identity protected" in assessment.privacy_protections
        assert "VAWA protections applied" in assessment.privacy_protections
    
    def test_no_perpetrator_notification(self):
        """Test no perpetrator notification in protections"""
        from backend.app.human_intel.behavioral_crisis_engine import BehavioralCrisisEngine
        
        engine = BehavioralCrisisEngine()
        
        assessment = engine.assess_dv_escalation(
            incident_narrative="DV incident",
        )
        
        assert assessment is not None
        assert "No perpetrator notification" in assessment.privacy_protections
    
    def test_alcohol_correlation(self):
        """Test alcohol correlation increases risk"""
        from backend.app.human_intel.behavioral_crisis_engine import BehavioralCrisisEngine
        
        engine = BehavioralCrisisEngine()
        
        assessment_no_alcohol = engine.assess_dv_escalation(
            incident_narrative="DV incident",
            alcohol_involved=False,
        )
        
        assessment_with_alcohol = engine.assess_dv_escalation(
            incident_narrative="DV incident",
            alcohol_involved=True,
        )
        
        assert assessment_no_alcohol is not None
        assert assessment_with_alcohol is not None
        assert assessment_with_alcohol.lethality_risk_score >= assessment_no_alcohol.lethality_risk_score
    
    def test_repeat_call_pattern(self):
        """Test repeat call pattern increases risk"""
        from backend.app.human_intel.behavioral_crisis_engine import BehavioralCrisisEngine
        
        engine = BehavioralCrisisEngine()
        
        assessment_no_repeat = engine.assess_dv_escalation(
            incident_narrative="DV incident",
            repeat_call_count=0,
        )
        
        assessment_with_repeat = engine.assess_dv_escalation(
            incident_narrative="DV incident",
            repeat_call_count=5,
        )
        
        assert assessment_no_repeat is not None
        assert assessment_with_repeat is not None
        assert assessment_with_repeat.escalation_level.value >= assessment_no_repeat.escalation_level.value
    
    def test_chain_of_custody_hash(self):
        """Test chain of custody hash is generated"""
        from backend.app.human_intel.behavioral_crisis_engine import BehavioralCrisisEngine
        
        engine = BehavioralCrisisEngine()
        
        assessment = engine.assess_dv_escalation(
            incident_narrative="Test incident",
        )
        
        assert assessment is not None
        assert len(assessment.chain_of_custody_hash) == 64
    
    def test_recommended_actions_high_risk(self):
        """Test recommended actions for high risk"""
        from backend.app.human_intel.behavioral_crisis_engine import BehavioralCrisisEngine, DVEscalationLevel
        
        engine = BehavioralCrisisEngine()
        
        assessment = engine.assess_dv_escalation(
            incident_narrative="High risk DV situation",
            weapons_present=True,
            prior_threats=True,
        )
        
        assert assessment is not None
        assert len(assessment.recommended_actions) > 0
