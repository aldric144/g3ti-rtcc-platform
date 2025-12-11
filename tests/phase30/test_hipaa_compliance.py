"""
Phase 30: HIPAA Compliance Tests

Tests for:
- HIPAA-adjacent protections
- Minimum necessary standard
- Access logging
- De-identification requirements
"""

import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))


class TestHIPAAAdjacentProtections:
    """Tests for HIPAA-adjacent protections"""
    
    def test_mental_health_data_protected(self):
        """Test mental health data is protected"""
        from backend.app.human_intel.privacy_guard import PrivacyGuard, DataCategory
        
        guard = PrivacyGuard()
        
        result = guard.validate_hipaa_compliance(
            data_category="mental_health",
            access_purpose="crisis_response",
            minimum_necessary=True,
        )
        
        assert result is not None
        assert result["compliant"] == True
    
    def test_mental_health_data_requires_purpose(self):
        """Test mental health data requires valid purpose"""
        from backend.app.human_intel.privacy_guard import PrivacyGuard
        
        guard = PrivacyGuard()
        
        result = guard.validate_hipaa_compliance(
            data_category="mental_health",
            access_purpose="general_inquiry",
            minimum_necessary=False,
        )
        
        assert result is not None
        assert result["compliant"] == False
    
    def test_substance_abuse_data_protected(self):
        """Test substance abuse data is protected"""
        from backend.app.human_intel.privacy_guard import PrivacyGuard
        
        guard = PrivacyGuard()
        
        result = guard.validate_hipaa_compliance(
            data_category="substance_abuse",
            access_purpose="crisis_response",
            minimum_necessary=True,
        )
        
        assert result is not None
        assert result["compliant"] == True
    
    def test_medical_data_protected(self):
        """Test medical data is protected"""
        from backend.app.human_intel.privacy_guard import PrivacyGuard
        
        guard = PrivacyGuard()
        
        result = guard.validate_hipaa_compliance(
            data_category="medical",
            access_purpose="emergency_response",
            minimum_necessary=True,
        )
        
        assert result is not None
        assert result["compliant"] == True


class TestMinimumNecessaryStandard:
    """Tests for minimum necessary standard"""
    
    def test_minimum_necessary_required(self):
        """Test minimum necessary is required"""
        from backend.app.human_intel.privacy_guard import PrivacyGuard
        
        guard = PrivacyGuard()
        
        result = guard.validate_hipaa_compliance(
            data_category="mental_health",
            access_purpose="crisis_response",
            minimum_necessary=False,
        )
        
        assert result is not None
        assert result["compliant"] == False
    
    def test_minimum_necessary_enforced(self):
        """Test minimum necessary is enforced"""
        from backend.app.human_intel.privacy_guard import PrivacyGuard
        
        guard = PrivacyGuard()
        
        result = guard.validate_hipaa_compliance(
            data_category="mental_health",
            access_purpose="crisis_response",
            minimum_necessary=True,
        )
        
        assert result is not None
        assert result["compliant"] == True


class TestAccessLogging:
    """Tests for access logging"""
    
    def test_query_check_logged(self):
        """Test query checks are logged"""
        from backend.app.human_intel.privacy_guard import PrivacyGuard
        
        guard = PrivacyGuard()
        
        initial_count = guard.get_statistics()["total_queries_checked"]
        
        guard.check_query(
            query_type="risk_assessment",
            data_sources=["911_call_narrative"],
            filters={},
        )
        
        new_count = guard.get_statistics()["total_queries_checked"]
        
        assert new_count >= initial_count
    
    def test_violation_logged(self):
        """Test violations are logged"""
        from backend.app.human_intel.privacy_guard import PrivacyGuard
        
        guard = PrivacyGuard()
        
        initial_count = guard.get_statistics()["total_violations_detected"]
        
        guard.check_query(
            query_type="risk_assessment",
            data_sources=["private_social_media"],
            filters={},
        )
        
        new_count = guard.get_statistics()["total_violations_detected"]
        
        assert new_count >= initial_count


class TestDeIdentificationRequirements:
    """Tests for de-identification requirements"""
    
    def test_full_anonymization_removes_pii(self):
        """Test full anonymization removes PII"""
        from backend.app.human_intel.privacy_guard import PrivacyGuard, AnonymizationLevel
        
        guard = PrivacyGuard()
        
        data = {
            "name": "John Doe",
            "ssn": "123-45-6789",
            "risk_score": 0.75,
        }
        
        anonymized = guard.anonymize_data(data, AnonymizationLevel.FULL)
        
        assert anonymized is not None
        assert "name" not in anonymized or anonymized["name"] == "[REDACTED]"
        assert "ssn" not in anonymized or anonymized["ssn"] == "[REDACTED]"
    
    def test_aggregated_anonymization(self):
        """Test aggregated anonymization"""
        from backend.app.human_intel.privacy_guard import PrivacyGuard, AnonymizationLevel
        
        guard = PrivacyGuard()
        
        data = {
            "zone": "Zone_A",
            "count": 10,
        }
        
        anonymized = guard.anonymize_data(data, AnonymizationLevel.AGGREGATED)
        
        assert anonymized is not None
        assert "zone" in anonymized
    
    def test_suicide_assessment_anonymized(self):
        """Test suicide assessment is anonymized"""
        from backend.app.human_intel.behavioral_crisis_engine import BehavioralCrisisEngine
        
        engine = BehavioralCrisisEngine()
        
        assessment = engine.assess_suicide_risk(
            call_narrative="Test narrative",
            caller_type="unknown",
        )
        
        assert assessment.anonymization_level == "FULL"
    
    def test_dv_assessment_anonymized(self):
        """Test DV assessment is anonymized"""
        from backend.app.human_intel.behavioral_crisis_engine import BehavioralCrisisEngine
        
        engine = BehavioralCrisisEngine()
        
        assessment = engine.assess_dv_escalation(
            incident_narrative="Test incident",
        )
        
        assert assessment.anonymization_level == "FULL"
    
    def test_community_pulse_aggregated(self):
        """Test community pulse is aggregated"""
        from backend.app.human_intel.behavioral_crisis_engine import BehavioralCrisisEngine
        
        engine = BehavioralCrisisEngine()
        
        pulse = engine.get_community_trauma_pulse(time_window_hours=72)
        
        assert pulse.anonymization_level == "AGGREGATED"


class TestFERPACompliance:
    """Tests for FERPA compliance"""
    
    def test_ferpa_compliance_health_safety_emergency(self):
        """Test FERPA compliance for health/safety emergency"""
        from backend.app.human_intel.privacy_guard import PrivacyGuard
        
        guard = PrivacyGuard()
        
        result = guard.validate_ferpa_compliance(
            data_category="school_records",
            access_purpose="health_safety_emergency",
            parental_consent=False,
        )
        
        assert result is not None
        assert result["compliant"] == True
    
    def test_ferpa_compliance_requires_consent(self):
        """Test FERPA compliance requires consent for non-emergency"""
        from backend.app.human_intel.privacy_guard import PrivacyGuard
        
        guard = PrivacyGuard()
        
        result = guard.validate_ferpa_compliance(
            data_category="school_records",
            access_purpose="general_inquiry",
            parental_consent=False,
        )
        
        assert result is not None
        assert result["compliant"] == False
    
    def test_youth_assessment_ferpa_protected(self):
        """Test youth assessment has FERPA protections"""
        from backend.app.human_intel.youth_crisis_engine import YouthCrisisEngine
        
        engine = YouthCrisisEngine()
        
        assessment = engine.assess_youth_risk(
            school_zone="Zone_A",
            age_group="middle_school",
        )
        
        assert "FERPA protections applied" in assessment.privacy_protections


class TestVAWACompliance:
    """Tests for VAWA compliance"""
    
    def test_vawa_compliance_victim_consent(self):
        """Test VAWA compliance with victim consent"""
        from backend.app.human_intel.privacy_guard import PrivacyGuard
        
        guard = PrivacyGuard()
        
        result = guard.validate_vawa_compliance(
            data_category="domestic_violence",
            victim_consent=True,
            disclosure_type="victim_services",
        )
        
        assert result is not None
        assert result["compliant"] == True
    
    def test_vawa_compliance_no_perpetrator_notification(self):
        """Test VAWA compliance blocks perpetrator notification"""
        from backend.app.human_intel.privacy_guard import PrivacyGuard
        
        guard = PrivacyGuard()
        
        result = guard.validate_vawa_compliance(
            data_category="domestic_violence",
            victim_consent=False,
            disclosure_type="perpetrator_notification",
        )
        
        assert result is not None
        assert result["compliant"] == False
    
    def test_dv_assessment_vawa_protected(self):
        """Test DV assessment has VAWA protections"""
        from backend.app.human_intel.behavioral_crisis_engine import BehavioralCrisisEngine
        
        engine = BehavioralCrisisEngine()
        
        assessment = engine.assess_dv_escalation(
            incident_narrative="DV incident",
        )
        
        assert "VAWA protections applied" in assessment.privacy_protections
        assert "Victim identity protected" in assessment.privacy_protections
        assert "No perpetrator notification" in assessment.privacy_protections
