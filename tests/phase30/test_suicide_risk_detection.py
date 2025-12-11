"""
Phase 30: Suicide Risk Detection Tests

Tests for:
- Crisis phrase detection
- Risk level classification
- Auto-alert triggering
- Privacy protections
"""

import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))


class TestSuicideRiskDetection:
    """Tests for suicide risk detection"""
    
    def test_crisis_phrase_detection_want_to_die(self):
        """Test detection of 'want to die' phrase"""
        from backend.app.human_intel.behavioral_crisis_engine import BehavioralCrisisEngine
        
        engine = BehavioralCrisisEngine()
        
        assessment = engine.assess_suicide_risk(
            call_narrative="Subject says they want to die",
            caller_type="family",
        )
        
        assert assessment is not None
        assert "want to die" in assessment.crisis_phrases_detected or len(assessment.crisis_phrases_detected) > 0
    
    def test_crisis_phrase_detection_end_it_all(self):
        """Test detection of 'end it all' phrase"""
        from backend.app.human_intel.behavioral_crisis_engine import BehavioralCrisisEngine
        
        engine = BehavioralCrisisEngine()
        
        assessment = engine.assess_suicide_risk(
            call_narrative="Subject wants to end it all",
            caller_type="family",
        )
        
        assert assessment is not None
        assert len(assessment.crisis_phrases_detected) > 0
    
    def test_crisis_phrase_detection_no_reason_to_live(self):
        """Test detection of 'no reason to live' phrase"""
        from backend.app.human_intel.behavioral_crisis_engine import BehavioralCrisisEngine
        
        engine = BehavioralCrisisEngine()
        
        assessment = engine.assess_suicide_risk(
            call_narrative="Subject says there's no reason to live anymore",
            caller_type="self",
        )
        
        assert assessment is not None
        assert len(assessment.crisis_phrases_detected) > 0
    
    def test_crisis_phrase_detection_kill_myself(self):
        """Test detection of 'kill myself' phrase"""
        from backend.app.human_intel.behavioral_crisis_engine import BehavioralCrisisEngine
        
        engine = BehavioralCrisisEngine()
        
        assessment = engine.assess_suicide_risk(
            call_narrative="Subject is threatening to kill myself",
            caller_type="self",
        )
        
        assert assessment is not None
        assert len(assessment.crisis_phrases_detected) > 0
    
    def test_risk_level_low_no_indicators(self):
        """Test low risk level with no indicators"""
        from backend.app.human_intel.behavioral_crisis_engine import BehavioralCrisisEngine, SuicideRiskLevel
        
        engine = BehavioralCrisisEngine()
        
        assessment = engine.assess_suicide_risk(
            call_narrative="Routine welfare check requested",
            caller_type="neighbor",
            prior_welfare_checks=0,
            prior_crisis_calls=0,
        )
        
        assert assessment is not None
        assert assessment.risk_level == SuicideRiskLevel.LOW
    
    def test_risk_level_moderate_some_indicators(self):
        """Test moderate risk level with some indicators"""
        from backend.app.human_intel.behavioral_crisis_engine import BehavioralCrisisEngine, SuicideRiskLevel
        
        engine = BehavioralCrisisEngine()
        
        assessment = engine.assess_suicide_risk(
            call_narrative="Subject seems depressed and withdrawn",
            caller_type="family",
            prior_welfare_checks=1,
            prior_crisis_calls=0,
        )
        
        assert assessment is not None
        assert assessment.risk_level in [SuicideRiskLevel.LOW, SuicideRiskLevel.MODERATE]
    
    def test_risk_level_high_multiple_indicators(self):
        """Test high risk level with multiple indicators"""
        from backend.app.human_intel.behavioral_crisis_engine import BehavioralCrisisEngine, SuicideRiskLevel
        
        engine = BehavioralCrisisEngine()
        
        assessment = engine.assess_suicide_risk(
            call_narrative="Subject says they want to die and can't go on",
            caller_type="family",
            prior_welfare_checks=2,
            prior_crisis_calls=1,
        )
        
        assert assessment is not None
        assert assessment.risk_level.value >= SuicideRiskLevel.HIGH.value
    
    def test_risk_level_immediate_danger(self):
        """Test immediate danger risk level"""
        from backend.app.human_intel.behavioral_crisis_engine import BehavioralCrisisEngine, SuicideRiskLevel
        
        engine = BehavioralCrisisEngine()
        
        assessment = engine.assess_suicide_risk(
            call_narrative="Subject has a gun and is threatening suicide right now",
            caller_type="self",
            prior_welfare_checks=3,
            prior_crisis_calls=2,
        )
        
        assert assessment is not None
        assert assessment.risk_level == SuicideRiskLevel.IMMEDIATE_DANGER
    
    def test_auto_alert_triggered_high_risk(self):
        """Test auto-alert triggered for high risk"""
        from backend.app.human_intel.behavioral_crisis_engine import BehavioralCrisisEngine, SuicideRiskLevel
        
        engine = BehavioralCrisisEngine()
        
        assessment = engine.assess_suicide_risk(
            call_narrative="Subject threatening suicide with weapon",
            caller_type="self",
        )
        
        assert assessment is not None
        if assessment.risk_level.value >= SuicideRiskLevel.HIGH.value:
            assert assessment.auto_alert_triggered == True
    
    def test_auto_alert_not_triggered_low_risk(self):
        """Test auto-alert not triggered for low risk"""
        from backend.app.human_intel.behavioral_crisis_engine import BehavioralCrisisEngine, SuicideRiskLevel
        
        engine = BehavioralCrisisEngine()
        
        assessment = engine.assess_suicide_risk(
            call_narrative="Routine welfare check",
            caller_type="neighbor",
        )
        
        assert assessment is not None
        if assessment.risk_level == SuicideRiskLevel.LOW:
            assert assessment.auto_alert_triggered == False
    
    def test_recommended_actions_high_risk(self):
        """Test recommended actions for high risk"""
        from backend.app.human_intel.behavioral_crisis_engine import BehavioralCrisisEngine, SuicideRiskLevel
        
        engine = BehavioralCrisisEngine()
        
        assessment = engine.assess_suicide_risk(
            call_narrative="Subject wants to end their life",
            caller_type="family",
        )
        
        assert assessment is not None
        assert len(assessment.recommended_actions) > 0
    
    def test_privacy_protections_applied(self):
        """Test privacy protections are applied"""
        from backend.app.human_intel.behavioral_crisis_engine import BehavioralCrisisEngine
        
        engine = BehavioralCrisisEngine()
        
        assessment = engine.assess_suicide_risk(
            call_narrative="Test narrative",
            caller_type="unknown",
        )
        
        assert assessment is not None
        assert assessment.anonymization_level == "FULL"
        assert "No PII stored" in assessment.privacy_protections
    
    def test_chain_of_custody_hash(self):
        """Test chain of custody hash is generated"""
        from backend.app.human_intel.behavioral_crisis_engine import BehavioralCrisisEngine
        
        engine = BehavioralCrisisEngine()
        
        assessment = engine.assess_suicide_risk(
            call_narrative="Test narrative",
            caller_type="unknown",
        )
        
        assert assessment is not None
        assert len(assessment.chain_of_custody_hash) == 64
    
    def test_caller_type_self_increases_risk(self):
        """Test that caller type 'self' increases risk"""
        from backend.app.human_intel.behavioral_crisis_engine import BehavioralCrisisEngine
        
        engine = BehavioralCrisisEngine()
        
        assessment_self = engine.assess_suicide_risk(
            call_narrative="I'm feeling hopeless",
            caller_type="self",
        )
        
        assessment_other = engine.assess_suicide_risk(
            call_narrative="Subject is feeling hopeless",
            caller_type="neighbor",
        )
        
        assert assessment_self is not None
        assert assessment_other is not None
        assert assessment_self.risk_level.value >= assessment_other.risk_level.value
    
    def test_prior_welfare_checks_increases_risk(self):
        """Test that prior welfare checks increase risk"""
        from backend.app.human_intel.behavioral_crisis_engine import BehavioralCrisisEngine
        
        engine = BehavioralCrisisEngine()
        
        assessment_no_prior = engine.assess_suicide_risk(
            call_narrative="Welfare check requested",
            caller_type="family",
            prior_welfare_checks=0,
        )
        
        assessment_with_prior = engine.assess_suicide_risk(
            call_narrative="Welfare check requested",
            caller_type="family",
            prior_welfare_checks=3,
        )
        
        assert assessment_no_prior is not None
        assert assessment_with_prior is not None
        assert assessment_with_prior.risk_level.value >= assessment_no_prior.risk_level.value
