"""
Phase 30: End-to-End Integration Tests

Tests for:
- Full workflow integration
- Cross-engine communication
- Privacy enforcement across all components
- Chain of custody verification
"""

import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))


class TestFullWorkflowIntegration:
    """Tests for full workflow integration"""
    
    def test_suicide_risk_to_crisis_routing(self):
        """Test suicide risk assessment flows to crisis routing"""
        from backend.app.human_intel.behavioral_crisis_engine import BehavioralCrisisEngine, SuicideRiskLevel
        from backend.app.human_intel.crisis_intervention_engine import CrisisInterventionEngine
        
        behavioral_engine = BehavioralCrisisEngine()
        crisis_engine = CrisisInterventionEngine()
        
        suicide_assessment = behavioral_engine.assess_suicide_risk(
            call_narrative="Subject threatening suicide",
            caller_type="family",
        )
        
        routing_decision = crisis_engine.route_crisis_call(
            call_narrative="Subject threatening suicide",
            call_type="suicide_ideation",
        )
        
        assert suicide_assessment is not None
        assert routing_decision is not None
        
        if suicide_assessment.risk_level.value >= SuicideRiskLevel.HIGH.value:
            assert routing_decision.priority.value >= 4
    
    def test_dv_assessment_to_crisis_routing(self):
        """Test DV assessment flows to crisis routing"""
        from backend.app.human_intel.behavioral_crisis_engine import BehavioralCrisisEngine, DVEscalationLevel
        from backend.app.human_intel.crisis_intervention_engine import CrisisInterventionEngine, ResponderType
        
        behavioral_engine = BehavioralCrisisEngine()
        crisis_engine = CrisisInterventionEngine()
        
        dv_assessment = behavioral_engine.assess_dv_escalation(
            incident_narrative="DV incident with weapon",
            weapons_present=True,
        )
        
        routing_decision = crisis_engine.route_crisis_call(
            call_narrative="DV incident with weapon",
            call_type="domestic_violence",
            weapons_mentioned=True,
        )
        
        assert dv_assessment is not None
        assert routing_decision is not None
        assert ResponderType.DV_ADVOCATE in routing_decision.co_responder_recommendation.co_responders
    
    def test_youth_risk_to_intervention_plan(self):
        """Test youth risk assessment flows to intervention plan"""
        from backend.app.human_intel.youth_crisis_engine import YouthCrisisEngine
        
        engine = YouthCrisisEngine()
        
        assessment = engine.assess_youth_risk(
            school_zone="Zone_A",
            age_group="middle_school",
            truancy_indicators=["chronic_absences"],
        )
        
        plan = engine.create_intervention_plan(assessment)
        
        assert assessment is not None
        assert plan is not None
        assert plan.primary_intervention is not None


class TestCrossEnginePrivacyEnforcement:
    """Tests for privacy enforcement across all engines"""
    
    def test_privacy_guard_blocks_all_engines(self):
        """Test privacy guard blocks prohibited queries in all engines"""
        from backend.app.human_intel.privacy_guard import PrivacyGuard
        
        guard = PrivacyGuard()
        
        result = guard.check_query(
            query_type="suicide_risk",
            data_sources=["private_social_media"],
            filters={},
        )
        
        assert result.query_allowed == False
        
        result = guard.check_query(
            query_type="dv_escalation",
            data_sources=["private_messages"],
            filters={},
        )
        
        assert result.query_allowed == False
        
        result = guard.check_query(
            query_type="youth_risk",
            data_sources=["private_email"],
            filters={},
        )
        
        assert result.query_allowed == False
    
    def test_all_engines_apply_anonymization(self):
        """Test all engines apply anonymization"""
        from backend.app.human_intel.behavioral_crisis_engine import BehavioralCrisisEngine
        from backend.app.human_intel.crisis_intervention_engine import CrisisInterventionEngine
        from backend.app.human_intel.youth_crisis_engine import YouthCrisisEngine
        
        behavioral_engine = BehavioralCrisisEngine()
        crisis_engine = CrisisInterventionEngine()
        youth_engine = YouthCrisisEngine()
        
        suicide_assessment = behavioral_engine.assess_suicide_risk(
            call_narrative="Test",
            caller_type="unknown",
        )
        assert suicide_assessment.anonymization_level == "FULL"
        
        dv_assessment = behavioral_engine.assess_dv_escalation(
            incident_narrative="Test",
        )
        assert dv_assessment.anonymization_level == "FULL"
        
        routing_decision = crisis_engine.route_crisis_call(
            call_narrative="Test",
            call_type="welfare_check",
        )
        assert len(routing_decision.co_responder_recommendation.privacy_protections) > 0
        
        youth_assessment = youth_engine.assess_youth_risk(
            school_zone="Zone_A",
            age_group="middle_school",
        )
        assert youth_assessment.anonymization_level == "FULL"
    
    def test_no_demographic_profiling_across_engines(self):
        """Test no demographic profiling across all engines"""
        from backend.app.human_intel.privacy_guard import PrivacyGuard
        
        guard = PrivacyGuard()
        
        for query_type in ["suicide_risk", "dv_escalation", "youth_risk", "crisis_routing"]:
            for protected_class in ["race", "ethnicity", "religion", "sex"]:
                result = guard.check_query(
                    query_type=query_type,
                    data_sources=["911_call_narrative"],
                    filters={protected_class: "any_value"},
                )
                
                assert result.query_allowed == False


class TestChainOfCustodyVerification:
    """Tests for chain of custody verification"""
    
    def test_suicide_assessment_has_hash(self):
        """Test suicide assessment has chain of custody hash"""
        from backend.app.human_intel.behavioral_crisis_engine import BehavioralCrisisEngine
        
        engine = BehavioralCrisisEngine()
        
        assessment = engine.assess_suicide_risk(
            call_narrative="Test",
            caller_type="unknown",
        )
        
        assert assessment.chain_of_custody_hash is not None
        assert len(assessment.chain_of_custody_hash) == 64
    
    def test_dv_assessment_has_hash(self):
        """Test DV assessment has chain of custody hash"""
        from backend.app.human_intel.behavioral_crisis_engine import BehavioralCrisisEngine
        
        engine = BehavioralCrisisEngine()
        
        assessment = engine.assess_dv_escalation(
            incident_narrative="Test",
        )
        
        assert assessment.chain_of_custody_hash is not None
        assert len(assessment.chain_of_custody_hash) == 64
    
    def test_hash_is_sha256(self):
        """Test hash is SHA256 format"""
        from backend.app.human_intel.behavioral_crisis_engine import BehavioralCrisisEngine
        import re
        
        engine = BehavioralCrisisEngine()
        
        assessment = engine.assess_suicide_risk(
            call_narrative="Test",
            caller_type="unknown",
        )
        
        assert re.match(r'^[a-f0-9]{64}$', assessment.chain_of_custody_hash)
    
    def test_different_assessments_have_different_hashes(self):
        """Test different assessments have different hashes"""
        from backend.app.human_intel.behavioral_crisis_engine import BehavioralCrisisEngine
        
        engine = BehavioralCrisisEngine()
        
        assessment1 = engine.assess_suicide_risk(
            call_narrative="Test 1",
            caller_type="unknown",
        )
        
        assessment2 = engine.assess_suicide_risk(
            call_narrative="Test 2",
            caller_type="family",
        )
        
        assert assessment1.chain_of_custody_hash != assessment2.chain_of_custody_hash


class TestComplianceIntegration:
    """Tests for compliance integration"""
    
    def test_hipaa_compliance_in_mental_health_flow(self):
        """Test HIPAA compliance in mental health flow"""
        from backend.app.human_intel.behavioral_crisis_engine import BehavioralCrisisEngine
        from backend.app.human_intel.privacy_guard import PrivacyGuard
        
        engine = BehavioralCrisisEngine()
        guard = PrivacyGuard()
        
        assessment = engine.assess_suicide_risk(
            call_narrative="Mental health crisis",
            caller_type="family",
        )
        
        hipaa_result = guard.validate_hipaa_compliance(
            data_category="mental_health",
            access_purpose="crisis_response",
            minimum_necessary=True,
        )
        
        assert assessment is not None
        assert hipaa_result["compliant"] == True
    
    def test_ferpa_compliance_in_youth_flow(self):
        """Test FERPA compliance in youth flow"""
        from backend.app.human_intel.youth_crisis_engine import YouthCrisisEngine
        from backend.app.human_intel.privacy_guard import PrivacyGuard
        
        engine = YouthCrisisEngine()
        guard = PrivacyGuard()
        
        assessment = engine.assess_youth_risk(
            school_zone="Zone_A",
            age_group="middle_school",
        )
        
        ferpa_result = guard.validate_ferpa_compliance(
            data_category="school_records",
            access_purpose="health_safety_emergency",
            parental_consent=False,
        )
        
        assert assessment is not None
        assert "FERPA protections applied" in assessment.privacy_protections
        assert ferpa_result["compliant"] == True
    
    def test_vawa_compliance_in_dv_flow(self):
        """Test VAWA compliance in DV flow"""
        from backend.app.human_intel.behavioral_crisis_engine import BehavioralCrisisEngine
        from backend.app.human_intel.privacy_guard import PrivacyGuard
        
        engine = BehavioralCrisisEngine()
        guard = PrivacyGuard()
        
        assessment = engine.assess_dv_escalation(
            incident_narrative="DV incident",
        )
        
        vawa_result = guard.validate_vawa_compliance(
            data_category="domestic_violence",
            victim_consent=True,
            disclosure_type="victim_services",
        )
        
        assert assessment is not None
        assert "VAWA protections applied" in assessment.privacy_protections
        assert vawa_result["compliant"] == True


class TestStatisticsIntegration:
    """Tests for statistics integration"""
    
    def test_behavioral_engine_statistics(self):
        """Test behavioral engine statistics"""
        from backend.app.human_intel.behavioral_crisis_engine import BehavioralCrisisEngine
        
        engine = BehavioralCrisisEngine()
        stats = engine.get_statistics()
        
        assert "total_suicide_assessments" in stats
        assert "total_dv_assessments" in stats
        assert "agency" in stats
    
    def test_crisis_engine_statistics(self):
        """Test crisis engine statistics"""
        from backend.app.human_intel.crisis_intervention_engine import CrisisInterventionEngine
        
        engine = CrisisInterventionEngine()
        stats = engine.get_statistics()
        
        assert "total_routing_decisions" in stats
        assert "total_repeat_crisis_flags" in stats
    
    def test_youth_engine_statistics(self):
        """Test youth engine statistics"""
        from backend.app.human_intel.youth_crisis_engine import YouthCrisisEngine
        
        engine = YouthCrisisEngine()
        stats = engine.get_statistics()
        
        assert "total_risk_assessments" in stats
        assert "total_incident_clusters" in stats
    
    def test_privacy_guard_statistics(self):
        """Test privacy guard statistics"""
        from backend.app.human_intel.privacy_guard import PrivacyGuard
        
        guard = PrivacyGuard()
        stats = guard.get_statistics()
        
        assert "total_queries_checked" in stats
        assert "total_violations_detected" in stats


class TestAgencyConfiguration:
    """Tests for agency configuration"""
    
    def test_all_engines_have_agency_config(self):
        """Test all engines have agency configuration"""
        from backend.app.human_intel.behavioral_crisis_engine import BehavioralCrisisEngine
        from backend.app.human_intel.crisis_intervention_engine import CrisisInterventionEngine
        from backend.app.human_intel.youth_crisis_engine import YouthCrisisEngine
        from backend.app.human_intel.privacy_guard import PrivacyGuard
        
        behavioral_engine = BehavioralCrisisEngine()
        crisis_engine = CrisisInterventionEngine()
        youth_engine = YouthCrisisEngine()
        guard = PrivacyGuard()
        
        assert behavioral_engine.agency_config["ori"] == "FL0500400"
        assert crisis_engine.agency_config["ori"] == "FL0500400"
        assert youth_engine.agency_config["ori"] == "FL0500400"
        assert guard.agency_config["ori"] == "FL0500400"
    
    def test_all_engines_have_city_config(self):
        """Test all engines have city configuration"""
        from backend.app.human_intel.behavioral_crisis_engine import BehavioralCrisisEngine
        from backend.app.human_intel.crisis_intervention_engine import CrisisInterventionEngine
        from backend.app.human_intel.youth_crisis_engine import YouthCrisisEngine
        
        behavioral_engine = BehavioralCrisisEngine()
        crisis_engine = CrisisInterventionEngine()
        youth_engine = YouthCrisisEngine()
        
        assert behavioral_engine.agency_config["city"] == "Riviera Beach"
        assert crisis_engine.agency_config["city"] == "Riviera Beach"
        assert youth_engine.agency_config["city"] == "Riviera Beach"
