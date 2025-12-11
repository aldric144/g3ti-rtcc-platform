"""
Phase 30: Privacy Guard Tests

Tests for:
- Query validation
- Privacy violation detection
- Anonymization enforcement
- Compliance checks (HIPAA, FERPA, VAWA)
"""

import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))


class TestPrivacyGuard:
    """Tests for PrivacyGuard"""
    
    def test_guard_singleton(self):
        """Test that guard is a singleton"""
        from backend.app.human_intel.privacy_guard import PrivacyGuard
        
        guard1 = PrivacyGuard()
        guard2 = PrivacyGuard()
        
        assert guard1 is guard2
    
    def test_guard_initialization(self):
        """Test guard initializes with correct agency config"""
        from backend.app.human_intel.privacy_guard import PrivacyGuard
        
        guard = PrivacyGuard()
        
        assert guard.agency_config["ori"] == "FL0500400"
        assert guard.agency_config["city"] == "Riviera Beach"
    
    def test_privacy_violation_type_enum(self):
        """Test PrivacyViolationType enum values"""
        from backend.app.human_intel.privacy_guard import PrivacyViolationType
        
        assert PrivacyViolationType.PROHIBITED_DATA_SOURCE.value == "prohibited_data_source"
        assert PrivacyViolationType.DEMOGRAPHIC_PROFILING.value == "demographic_profiling"
        assert PrivacyViolationType.INDIVIDUAL_TARGETING.value == "individual_targeting"
    
    def test_anonymization_level_enum(self):
        """Test AnonymizationLevel enum values"""
        from backend.app.human_intel.privacy_guard import AnonymizationLevel
        
        assert AnonymizationLevel.NONE.value == 0
        assert AnonymizationLevel.MINIMAL.value == 1
        assert AnonymizationLevel.PARTIAL.value == 2
        assert AnonymizationLevel.SUBSTANTIAL.value == 3
        assert AnonymizationLevel.FULL.value == 4
        assert AnonymizationLevel.AGGREGATED.value == 5
    
    def test_data_category_enum(self):
        """Test DataCategory enum values"""
        from backend.app.human_intel.privacy_guard import DataCategory
        
        assert DataCategory.MENTAL_HEALTH.value == "mental_health"
        assert DataCategory.DOMESTIC_VIOLENCE.value == "domestic_violence"
        assert DataCategory.JUVENILE.value == "juvenile"
    
    def test_protected_class_enum(self):
        """Test ProtectedClass enum values"""
        from backend.app.human_intel.privacy_guard import ProtectedClass
        
        assert ProtectedClass.RACE.value == "race"
        assert ProtectedClass.ETHNICITY.value == "ethnicity"
        assert ProtectedClass.RELIGION.value == "religion"
        assert ProtectedClass.SEX.value == "sex"
    
    def test_privacy_check_result_dataclass(self):
        """Test PrivacyCheckResult dataclass"""
        from backend.app.human_intel.privacy_guard import PrivacyCheckResult
        
        result = PrivacyCheckResult(
            check_id="PC-TEST001",
            timestamp=datetime.utcnow(),
            query_allowed=True,
            violations=[],
            warnings=["Minor concern"],
            required_anonymization_level="FULL",
            data_categories_involved=["mental_health"],
            compliance_checks_passed=["HIPAA"],
            compliance_checks_failed=[],
            recommendations=["Continue monitoring"],
        )
        
        assert result.check_id == "PC-TEST001"
        assert result.query_allowed == True
    
    def test_ethics_audit_result_dataclass(self):
        """Test EthicsAuditResult dataclass"""
        from backend.app.human_intel.privacy_guard import EthicsAuditResult
        
        result = EthicsAuditResult(
            audit_id="EA-TEST001",
            timestamp=datetime.utcnow(),
            model_name="test_model",
            fairness_score=0.95,
            bias_detected=False,
            bias_categories=[],
            protected_classes_affected=[],
            recommendations=[],
            audit_passed=True,
            next_audit_due=datetime.utcnow(),
        )
        
        assert result.audit_id == "EA-TEST001"
        assert result.audit_passed == True


class TestQueryValidation:
    """Tests for query validation"""
    
    def test_check_query_allowed(self):
        """Test allowed query"""
        from backend.app.human_intel.privacy_guard import PrivacyGuard
        
        guard = PrivacyGuard()
        
        result = guard.check_query(
            query_type="suicide_risk_assessment",
            data_sources=["911_call_narrative"],
            filters={},
        )
        
        assert result is not None
        assert result.query_allowed == True
    
    def test_check_query_blocked_private_social_media(self):
        """Test query blocked for private social media"""
        from backend.app.human_intel.privacy_guard import PrivacyGuard, PrivacyViolationType
        
        guard = PrivacyGuard()
        
        result = guard.check_query(
            query_type="risk_assessment",
            data_sources=["private_social_media"],
            filters={},
        )
        
        assert result is not None
        assert result.query_allowed == False
        assert any(v.violation_type == PrivacyViolationType.PROHIBITED_DATA_SOURCE for v in result.violations)
    
    def test_check_query_blocked_demographic_profiling(self):
        """Test query blocked for demographic profiling"""
        from backend.app.human_intel.privacy_guard import PrivacyGuard, PrivacyViolationType
        
        guard = PrivacyGuard()
        
        result = guard.check_query(
            query_type="risk_assessment",
            data_sources=["911_call_narrative"],
            filters={"race": "any_value"},
        )
        
        assert result is not None
        assert result.query_allowed == False
        assert any(v.violation_type == PrivacyViolationType.DEMOGRAPHIC_PROFILING for v in result.violations)
    
    def test_check_query_blocked_individual_targeting(self):
        """Test query blocked for individual targeting"""
        from backend.app.human_intel.privacy_guard import PrivacyGuard, PrivacyViolationType
        
        guard = PrivacyGuard()
        
        result = guard.check_query(
            query_type="predictive_policing",
            data_sources=["911_call_narrative"],
            filters={"individual_id": "12345"},
        )
        
        assert result is not None
        assert result.query_allowed == False
        assert any(v.violation_type == PrivacyViolationType.INDIVIDUAL_TARGETING for v in result.violations)
    
    def test_check_query_blocked_protected_class_filter(self):
        """Test query blocked for protected class filter"""
        from backend.app.human_intel.privacy_guard import PrivacyGuard
        
        guard = PrivacyGuard()
        
        for protected_class in ["race", "ethnicity", "religion", "sex", "gender_identity", "sexual_orientation"]:
            result = guard.check_query(
                query_type="risk_assessment",
                data_sources=["911_call_narrative"],
                filters={protected_class: "any_value"},
            )
            
            assert result.query_allowed == False


class TestAnonymization:
    """Tests for anonymization"""
    
    def test_anonymize_data_full(self):
        """Test full anonymization"""
        from backend.app.human_intel.privacy_guard import PrivacyGuard, AnonymizationLevel
        
        guard = PrivacyGuard()
        
        data = {
            "name": "John Doe",
            "address": "123 Main St",
            "phone": "555-1234",
            "ssn": "123-45-6789",
            "risk_score": 0.75,
        }
        
        anonymized = guard.anonymize_data(data, AnonymizationLevel.FULL)
        
        assert anonymized is not None
        assert "name" not in anonymized or anonymized["name"] == "[REDACTED]"
        assert "ssn" not in anonymized or anonymized["ssn"] == "[REDACTED]"
        assert "risk_score" in anonymized
    
    def test_anonymize_data_aggregated(self):
        """Test aggregated anonymization"""
        from backend.app.human_intel.privacy_guard import PrivacyGuard, AnonymizationLevel
        
        guard = PrivacyGuard()
        
        data = {
            "zone": "Zone_A",
            "individual_count": 5,
            "risk_level": "HIGH",
        }
        
        anonymized = guard.anonymize_data(data, AnonymizationLevel.AGGREGATED)
        
        assert anonymized is not None
        assert "zone" in anonymized
    
    def test_anonymize_data_minimal(self):
        """Test minimal anonymization"""
        from backend.app.human_intel.privacy_guard import PrivacyGuard, AnonymizationLevel
        
        guard = PrivacyGuard()
        
        data = {
            "zone": "Zone_A",
            "risk_score": 0.75,
        }
        
        anonymized = guard.anonymize_data(data, AnonymizationLevel.MINIMAL)
        
        assert anonymized is not None


class TestComplianceValidation:
    """Tests for compliance validation"""
    
    def test_validate_hipaa_compliance_pass(self):
        """Test HIPAA compliance validation pass"""
        from backend.app.human_intel.privacy_guard import PrivacyGuard
        
        guard = PrivacyGuard()
        
        result = guard.validate_hipaa_compliance(
            data_category="mental_health",
            access_purpose="crisis_response",
            minimum_necessary=True,
        )
        
        assert result is not None
        assert result["compliant"] == True
    
    def test_validate_hipaa_compliance_fail(self):
        """Test HIPAA compliance validation fail"""
        from backend.app.human_intel.privacy_guard import PrivacyGuard
        
        guard = PrivacyGuard()
        
        result = guard.validate_hipaa_compliance(
            data_category="mental_health",
            access_purpose="general_inquiry",
            minimum_necessary=False,
        )
        
        assert result is not None
        assert result["compliant"] == False
    
    def test_validate_ferpa_compliance_pass(self):
        """Test FERPA compliance validation pass"""
        from backend.app.human_intel.privacy_guard import PrivacyGuard
        
        guard = PrivacyGuard()
        
        result = guard.validate_ferpa_compliance(
            data_category="school_records",
            access_purpose="health_safety_emergency",
            parental_consent=False,
        )
        
        assert result is not None
        assert result["compliant"] == True
    
    def test_validate_ferpa_compliance_fail(self):
        """Test FERPA compliance validation fail"""
        from backend.app.human_intel.privacy_guard import PrivacyGuard
        
        guard = PrivacyGuard()
        
        result = guard.validate_ferpa_compliance(
            data_category="school_records",
            access_purpose="general_inquiry",
            parental_consent=False,
        )
        
        assert result is not None
        assert result["compliant"] == False
    
    def test_validate_vawa_compliance_pass(self):
        """Test VAWA compliance validation pass"""
        from backend.app.human_intel.privacy_guard import PrivacyGuard
        
        guard = PrivacyGuard()
        
        result = guard.validate_vawa_compliance(
            data_category="domestic_violence",
            victim_consent=True,
            disclosure_type="victim_services",
        )
        
        assert result is not None
        assert result["compliant"] == True
    
    def test_validate_vawa_compliance_fail(self):
        """Test VAWA compliance validation fail"""
        from backend.app.human_intel.privacy_guard import PrivacyGuard
        
        guard = PrivacyGuard()
        
        result = guard.validate_vawa_compliance(
            data_category="domestic_violence",
            victim_consent=False,
            disclosure_type="perpetrator_notification",
        )
        
        assert result is not None
        assert result["compliant"] == False


class TestFairnessAudit:
    """Tests for fairness audit"""
    
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
    
    def test_audit_model_fairness_bias_detected(self):
        """Test model fairness audit with bias detected"""
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
    
    def test_get_privacy_report(self):
        """Test get_privacy_report method"""
        from backend.app.human_intel.privacy_guard import PrivacyGuard
        
        guard = PrivacyGuard()
        report = guard.get_privacy_report()
        
        assert "total_queries_checked" in report
        assert "total_violations_detected" in report
        assert "compliance_summary" in report
    
    def test_get_statistics(self):
        """Test get_statistics method"""
        from backend.app.human_intel.privacy_guard import PrivacyGuard
        
        guard = PrivacyGuard()
        stats = guard.get_statistics()
        
        assert "total_queries_checked" in stats
        assert "total_violations_detected" in stats
        assert "agency" in stats
