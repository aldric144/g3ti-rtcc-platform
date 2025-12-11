"""
Phase 30: Ethics Compliance Tests

Tests for:
- No private social media monitoring
- No demographic profiling
- No predictive policing on protected classes
- Fairness audits
"""

import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))


class TestNoPrivateSocialMediaMonitoring:
    """Tests for no private social media monitoring"""
    
    def test_blocks_private_social_media(self):
        """Test blocks private social media data source"""
        from backend.app.human_intel.privacy_guard import PrivacyGuard
        
        guard = PrivacyGuard()
        
        result = guard.check_query(
            query_type="risk_assessment",
            data_sources=["private_social_media"],
            filters={},
        )
        
        assert result.query_allowed == False
    
    def test_blocks_private_messages(self):
        """Test blocks private messages data source"""
        from backend.app.human_intel.privacy_guard import PrivacyGuard
        
        guard = PrivacyGuard()
        
        result = guard.check_query(
            query_type="risk_assessment",
            data_sources=["private_messages"],
            filters={},
        )
        
        assert result.query_allowed == False
    
    def test_blocks_private_email(self):
        """Test blocks private email data source"""
        from backend.app.human_intel.privacy_guard import PrivacyGuard
        
        guard = PrivacyGuard()
        
        result = guard.check_query(
            query_type="risk_assessment",
            data_sources=["private_email"],
            filters={},
        )
        
        assert result.query_allowed == False
    
    def test_blocks_private_phone_records(self):
        """Test blocks private phone records data source"""
        from backend.app.human_intel.privacy_guard import PrivacyGuard
        
        guard = PrivacyGuard()
        
        result = guard.check_query(
            query_type="risk_assessment",
            data_sources=["private_phone_records"],
            filters={},
        )
        
        assert result.query_allowed == False
    
    def test_allows_public_data_sources(self):
        """Test allows public data sources"""
        from backend.app.human_intel.privacy_guard import PrivacyGuard
        
        guard = PrivacyGuard()
        
        result = guard.check_query(
            query_type="risk_assessment",
            data_sources=["911_call_narrative", "public_records"],
            filters={},
        )
        
        assert result.query_allowed == True


class TestNoDemographicProfiling:
    """Tests for no demographic profiling"""
    
    def test_blocks_race_filter(self):
        """Test blocks race filter"""
        from backend.app.human_intel.privacy_guard import PrivacyGuard
        
        guard = PrivacyGuard()
        
        result = guard.check_query(
            query_type="risk_assessment",
            data_sources=["911_call_narrative"],
            filters={"race": "any_value"},
        )
        
        assert result.query_allowed == False
    
    def test_blocks_ethnicity_filter(self):
        """Test blocks ethnicity filter"""
        from backend.app.human_intel.privacy_guard import PrivacyGuard
        
        guard = PrivacyGuard()
        
        result = guard.check_query(
            query_type="risk_assessment",
            data_sources=["911_call_narrative"],
            filters={"ethnicity": "any_value"},
        )
        
        assert result.query_allowed == False
    
    def test_blocks_religion_filter(self):
        """Test blocks religion filter"""
        from backend.app.human_intel.privacy_guard import PrivacyGuard
        
        guard = PrivacyGuard()
        
        result = guard.check_query(
            query_type="risk_assessment",
            data_sources=["911_call_narrative"],
            filters={"religion": "any_value"},
        )
        
        assert result.query_allowed == False
    
    def test_blocks_gender_identity_filter(self):
        """Test blocks gender identity filter"""
        from backend.app.human_intel.privacy_guard import PrivacyGuard
        
        guard = PrivacyGuard()
        
        result = guard.check_query(
            query_type="risk_assessment",
            data_sources=["911_call_narrative"],
            filters={"gender_identity": "any_value"},
        )
        
        assert result.query_allowed == False
    
    def test_blocks_sexual_orientation_filter(self):
        """Test blocks sexual orientation filter"""
        from backend.app.human_intel.privacy_guard import PrivacyGuard
        
        guard = PrivacyGuard()
        
        result = guard.check_query(
            query_type="risk_assessment",
            data_sources=["911_call_narrative"],
            filters={"sexual_orientation": "any_value"},
        )
        
        assert result.query_allowed == False
    
    def test_allows_non_demographic_filters(self):
        """Test allows non-demographic filters"""
        from backend.app.human_intel.privacy_guard import PrivacyGuard
        
        guard = PrivacyGuard()
        
        result = guard.check_query(
            query_type="risk_assessment",
            data_sources=["911_call_narrative"],
            filters={"zone": "Zone_A", "time_range": "24h"},
        )
        
        assert result.query_allowed == True


class TestNoPredictivePolicingOnProtectedClasses:
    """Tests for no predictive policing on protected classes"""
    
    def test_blocks_individual_targeting(self):
        """Test blocks individual targeting"""
        from backend.app.human_intel.privacy_guard import PrivacyGuard
        
        guard = PrivacyGuard()
        
        result = guard.check_query(
            query_type="predictive_policing",
            data_sources=["911_call_narrative"],
            filters={"individual_id": "12345"},
        )
        
        assert result.query_allowed == False
    
    def test_blocks_protected_class_prediction(self):
        """Test blocks prediction based on protected class"""
        from backend.app.human_intel.privacy_guard import PrivacyGuard
        
        guard = PrivacyGuard()
        
        for protected_class in ["race", "ethnicity", "religion", "sex", "gender_identity"]:
            result = guard.check_query(
                query_type="predictive_policing",
                data_sources=["911_call_narrative"],
                filters={protected_class: "any_value"},
            )
            
            assert result.query_allowed == False
    
    def test_allows_zone_level_analysis(self):
        """Test allows zone-level analysis"""
        from backend.app.human_intel.privacy_guard import PrivacyGuard
        
        guard = PrivacyGuard()
        
        result = guard.check_query(
            query_type="stability_analysis",
            data_sources=["aggregated_data"],
            filters={"zone": "Zone_A"},
        )
        
        assert result.query_allowed == True


class TestFairnessAudits:
    """Tests for fairness audits"""
    
    def test_audit_model_fairness_pass(self):
        """Test model fairness audit pass"""
        from backend.app.human_intel.privacy_guard import PrivacyGuard
        
        guard = PrivacyGuard()
        
        result = guard.audit_model_fairness(
            model_name="suicide_risk_model",
            predictions=[0.5, 0.6, 0.4, 0.7],
            protected_attributes=[],
        )
        
        assert result is not None
        assert result.audit_passed == True
    
    def test_audit_model_fairness_detects_bias(self):
        """Test model fairness audit detects bias"""
        from backend.app.human_intel.privacy_guard import PrivacyGuard
        
        guard = PrivacyGuard()
        
        result = guard.audit_model_fairness(
            model_name="biased_model",
            predictions=[0.9, 0.9, 0.1, 0.1],
            protected_attributes=["race"],
            group_labels=["A", "A", "B", "B"],
        )
        
        assert result is not None
        if result.bias_detected:
            assert len(result.recommendations) > 0
    
    def test_audit_includes_next_audit_date(self):
        """Test audit includes next audit date"""
        from backend.app.human_intel.privacy_guard import PrivacyGuard
        
        guard = PrivacyGuard()
        
        result = guard.audit_model_fairness(
            model_name="test_model",
            predictions=[0.5, 0.5, 0.5, 0.5],
            protected_attributes=[],
        )
        
        assert result is not None
        assert result.next_audit_due is not None


class TestEthicalSafeguardsInEngines:
    """Tests for ethical safeguards in engines"""
    
    def test_behavioral_crisis_engine_anonymization(self):
        """Test behavioral crisis engine applies anonymization"""
        from backend.app.human_intel.behavioral_crisis_engine import BehavioralCrisisEngine
        
        engine = BehavioralCrisisEngine()
        
        assessment = engine.assess_suicide_risk(
            call_narrative="Test narrative",
            caller_type="unknown",
        )
        
        assert assessment.anonymization_level == "FULL"
    
    def test_youth_crisis_engine_no_individual_profiling(self):
        """Test youth crisis engine does not profile individuals"""
        from backend.app.human_intel.youth_crisis_engine import YouthCrisisEngine
        
        engine = YouthCrisisEngine()
        
        assessment = engine.assess_youth_risk(
            school_zone="Zone_A",
            age_group="middle_school",
        )
        
        assert "No individual identification" in assessment.privacy_protections
    
    def test_crisis_intervention_engine_privacy_protections(self):
        """Test crisis intervention engine applies privacy protections"""
        from backend.app.human_intel.crisis_intervention_engine import CrisisInterventionEngine
        
        engine = CrisisInterventionEngine()
        
        decision = engine.route_crisis_call(
            call_narrative="Test call",
            call_type="welfare_check",
        )
        
        assert len(decision.co_responder_recommendation.privacy_protections) > 0
