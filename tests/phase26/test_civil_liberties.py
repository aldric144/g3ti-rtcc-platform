"""
Test Suite 2: Civil Liberties Engine Tests
Tests for civil rights validation
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../backend'))

from app.ethics_guardian.civil_liberties import (
    get_civil_liberties_engine,
    CivilLibertiesEngine,
    ComplianceStatus,
    ViolationType,
)


class TestCivilLibertiesEngine:
    """Tests for CivilLibertiesEngine"""

    def setup_method(self):
        """Setup test fixtures"""
        self.engine = get_civil_liberties_engine()

    def test_singleton_pattern(self):
        """Test that engine follows singleton pattern"""
        engine1 = get_civil_liberties_engine()
        engine2 = get_civil_liberties_engine()
        assert engine1 is engine2

    def test_thirteen_compliance_rules(self):
        """Test that 13 compliance rules are defined"""
        assert len(self.engine.compliance_rules) == 13


class TestFourthAmendment:
    """Tests for Fourth Amendment compliance"""

    def setup_method(self):
        """Setup test fixtures"""
        self.engine = get_civil_liberties_engine()

    def test_search_with_warrant_compliant(self):
        """Test search with valid warrant is compliant"""
        context = {"has_warrant": True, "consent": False}
        result = self.engine.check_compliance("test-001", "search", context)
        assert result.status == ComplianceStatus.COMPLIANT
        assert result.blocked is False

    def test_search_with_consent_compliant(self):
        """Test search with consent is compliant"""
        context = {"has_warrant": False, "consent": True}
        result = self.engine.check_compliance("test-002", "search", context)
        assert result.status == ComplianceStatus.COMPLIANT

    def test_search_exigent_circumstances_compliant(self):
        """Test search with exigent circumstances is compliant"""
        context = {
            "has_warrant": False,
            "consent": False,
            "exigent_circumstances": True,
        }
        result = self.engine.check_compliance("test-003", "search", context)
        assert result.status in [ComplianceStatus.COMPLIANT, ComplianceStatus.CONDITIONAL_APPROVAL]

    def test_warrantless_search_blocked(self):
        """Test warrantless search without exception is blocked"""
        context = {
            "has_warrant": False,
            "consent": False,
            "exigent_circumstances": False,
            "plain_view": False,
            "search_incident_to_arrest": False,
            "automobile_exception": False,
            "hot_pursuit": False,
            "community_caretaking": False,
        }
        result = self.engine.check_compliance("test-004", "search", context)
        assert result.status in [
            ComplianceStatus.NON_COMPLIANT_BLOCKED,
            ComplianceStatus.REQUIRES_REVIEW,
        ]

    def test_probable_cause_requirement(self):
        """Test probable cause requirement for searches"""
        context = {
            "has_warrant": True,
            "probable_cause": True,
        }
        result = self.engine.check_compliance("test-005", "search", context)
        assert result.status == ComplianceStatus.COMPLIANT


class TestFirstAmendment:
    """Tests for First Amendment compliance"""

    def setup_method(self):
        """Setup test fixtures"""
        self.engine = get_civil_liberties_engine()

    def test_targeting_speech_blocked(self):
        """Test that targeting protected speech is blocked"""
        context = {"targeting_speech": True}
        result = self.engine.check_compliance("test-006", "surveillance", context)
        assert result.blocked is True
        assert any(v.type == ViolationType.FREE_SPEECH_INFRINGEMENT for v in result.violations)

    def test_targeting_assembly_blocked(self):
        """Test that targeting peaceful assembly is blocked"""
        context = {"targeting_assembly": True, "peaceful_assembly": True}
        result = self.engine.check_compliance("test-007", "surveillance", context)
        assert result.blocked is True

    def test_targeting_religion_blocked(self):
        """Test that targeting religious practice is blocked"""
        context = {"targeting_religion": True}
        result = self.engine.check_compliance("test-008", "surveillance", context)
        assert result.blocked is True


class TestFourteenthAmendment:
    """Tests for Fourteenth Amendment compliance"""

    def setup_method(self):
        """Setup test fixtures"""
        self.engine = get_civil_liberties_engine()

    def test_equal_protection_violation(self):
        """Test equal protection violation detection"""
        context = {"demographic_targeting": True, "target_group": "Black"}
        result = self.engine.check_compliance("test-009", "enforcement", context)
        assert any(v.type == ViolationType.DEMOGRAPHIC_SKEW for v in result.violations)

    def test_due_process_violation(self):
        """Test due process violation detection"""
        context = {"due_process_followed": False}
        result = self.engine.check_compliance("test-010", "enforcement", context)
        assert result.status != ComplianceStatus.COMPLIANT


class TestFloridaLaw:
    """Tests for Florida state law compliance"""

    def setup_method(self):
        """Setup test fixtures"""
        self.engine = get_civil_liberties_engine()

    def test_drone_surveillance_limit(self):
        """Test Florida drone surveillance time limit"""
        context = {"drone_surveillance_hours": 30}
        result = self.engine.check_compliance("test-011", "drone_surveillance", context)
        assert result.blocked is True

    def test_drone_surveillance_within_limit(self):
        """Test drone surveillance within Florida limit"""
        context = {"drone_surveillance_hours": 20, "has_warrant": True}
        result = self.engine.check_compliance("test-012", "drone_surveillance", context)
        assert result.status in [ComplianceStatus.COMPLIANT, ComplianceStatus.CONDITIONAL_APPROVAL]

    def test_biometric_compliance(self):
        """Test biometric data compliance"""
        context = {"biometric_collection": True, "consent": False, "warrant": False}
        result = self.engine.check_compliance("test-013", "facial_recognition", context)
        assert result.status != ComplianceStatus.COMPLIANT


class TestDataRetention:
    """Tests for data retention compliance"""

    def setup_method(self):
        """Setup test fixtures"""
        self.engine = get_civil_liberties_engine()

    def test_retention_limits_defined(self):
        """Test that retention limits are defined"""
        limits = self.engine.get_retention_limits()
        assert "surveillance_footage" in limits
        assert "drone_footage" in limits
        assert "license_plate_data" in limits
        assert "facial_recognition_queries" in limits
        assert "predictive_analytics" in limits
        assert "general_records" in limits

    def test_surveillance_footage_limit(self):
        """Test surveillance footage retention limit"""
        limits = self.engine.get_retention_limits()
        assert limits["surveillance_footage"] == 30

    def test_license_plate_limit(self):
        """Test license plate data retention limit"""
        limits = self.engine.get_retention_limits()
        assert limits["license_plate_data"] == 90

    def test_facial_recognition_limit(self):
        """Test facial recognition queries retention limit"""
        limits = self.engine.get_retention_limits()
        assert limits["facial_recognition_queries"] == 365

    def test_general_records_limit(self):
        """Test general records retention limit (7 years)"""
        limits = self.engine.get_retention_limits()
        assert limits["general_records"] == 2555


class TestComplianceHistory:
    """Tests for compliance check history"""

    def setup_method(self):
        """Setup test fixtures"""
        self.engine = get_civil_liberties_engine()

    def test_compliance_history_tracking(self):
        """Test that compliance checks are tracked in history"""
        initial_count = len(self.engine.compliance_history)
        context = {"has_warrant": True}
        self.engine.check_compliance("test-history-001", "search", context)
        assert len(self.engine.compliance_history) == initial_count + 1

    def test_compliance_result_fields(self):
        """Test that compliance result has all required fields"""
        context = {"has_warrant": True}
        result = self.engine.check_compliance("test-fields-001", "search", context)
        assert hasattr(result, "action_id")
        assert hasattr(result, "action_type")
        assert hasattr(result, "status")
        assert hasattr(result, "violations")
        assert hasattr(result, "blocked")
        assert hasattr(result, "timestamp")
