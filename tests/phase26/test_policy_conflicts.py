"""
Test Suite 8: Policy Conflicts Tests
Tests for policy conflict detection
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../backend'))

from app.ethics_guardian.civil_liberties import (
    get_civil_liberties_engine,
    ComplianceStatus,
)
from app.ethics_guardian.ethics_score import (
    get_ethics_score_engine,
    RequiredAction,
)
from app.ethics_guardian.bias_detection import (
    get_bias_detection_engine,
    BiasStatus,
    AnalysisType,
)


class TestConstitutionalConflicts:
    """Tests for constitutional policy conflicts"""

    def setup_method(self):
        """Setup test fixtures"""
        self.civil_engine = get_civil_liberties_engine()

    def test_fourth_first_amendment_conflict(self):
        """Test conflict between Fourth and First Amendment concerns"""
        context = {
            "has_warrant": True,
            "targeting_speech": True,
        }
        result = self.civil_engine.check_compliance("test-conflict-001", "surveillance", context)
        assert result.blocked is True

    def test_surveillance_privacy_conflict(self):
        """Test conflict between surveillance need and privacy rights"""
        context = {
            "has_warrant": False,
            "consent": False,
            "public_safety_emergency": True,
        }
        result = self.civil_engine.check_compliance("test-conflict-002", "surveillance", context)
        assert result.status in [ComplianceStatus.REQUIRES_REVIEW, ComplianceStatus.CONDITIONAL_APPROVAL]


class TestFederalStateConflicts:
    """Tests for federal vs state law conflicts"""

    def setup_method(self):
        """Setup test fixtures"""
        self.civil_engine = get_civil_liberties_engine()

    def test_federal_state_drone_conflict(self):
        """Test conflict between federal and Florida drone regulations"""
        context = {
            "drone_surveillance_hours": 25,
            "federal_authorization": True,
            "state_authorization": False,
        }
        result = self.civil_engine.check_compliance("test-fed-state-001", "drone_surveillance", context)
        assert result.status != ComplianceStatus.COMPLIANT

    def test_biometric_federal_state_conflict(self):
        """Test conflict between federal and state biometric rules"""
        context = {
            "biometric_collection": True,
            "federal_database_query": True,
            "state_consent_obtained": False,
        }
        result = self.civil_engine.check_compliance("test-bio-conflict", "facial_recognition", context)
        assert result.status != ComplianceStatus.COMPLIANT


class TestBiasEthicsConflicts:
    """Tests for bias detection vs ethics score conflicts"""

    def setup_method(self):
        """Setup test fixtures"""
        self.bias_engine = get_bias_detection_engine()
        self.ethics_engine = get_ethics_score_engine()

    def test_marginal_bias_high_ethics(self):
        """Test marginal bias with otherwise high ethics score"""
        bias_data = {
            "demographic_outcomes": {
                "Black": {"positive": 75, "negative": 25},
                "White": {"positive": 85, "negative": 15},
            },
            "reference_group": "White",
        }
        bias_result = self.bias_engine.analyze_for_bias(AnalysisType.PREDICTIVE_AI, bias_data)

        ethics_context = {
            "bias_detected": bias_result.status == BiasStatus.BIAS_DETECTED_BLOCKED,
            "civil_rights_compliant": True,
            "force_risk": 10,
            "policy_compliant": True,
            "transparency_score": 0.90,
        }
        ethics_result = self.ethics_engine.compute_ethics_score("test-marginal", "patrol", ethics_context)

        if bias_result.status == BiasStatus.POSSIBLE_BIAS_FLAG_REVIEW:
            assert ethics_result.human_review_required is True

    def test_no_bias_low_ethics(self):
        """Test no bias but low ethics score from other factors"""
        bias_data = {
            "demographic_outcomes": {
                "Black": {"positive": 85, "negative": 15},
                "White": {"positive": 85, "negative": 15},
            },
            "reference_group": "White",
        }
        bias_result = self.bias_engine.analyze_for_bias(AnalysisType.PREDICTIVE_AI, bias_data)
        assert bias_result.status == BiasStatus.NO_BIAS_DETECTED

        ethics_context = {
            "bias_detected": False,
            "civil_rights_compliant": False,
            "force_risk": 80,
            "policy_compliant": False,
            "transparency_score": 0.30,
        }
        ethics_result = self.ethics_engine.compute_ethics_score("test-low-ethics", "enforcement", ethics_context)
        assert ethics_result.required_action in [RequiredAction.REVIEW, RequiredAction.BLOCK]


class TestCommunityPolicyConflicts:
    """Tests for protected community policy conflicts"""

    def setup_method(self):
        """Setup test fixtures"""
        self.civil_engine = get_civil_liberties_engine()

    def test_enforcement_community_conflict(self):
        """Test conflict between enforcement need and community protection"""
        context = {
            "has_warrant": True,
            "protected_community_area": True,
            "community_liaison_notified": False,
        }
        result = self.civil_engine.check_compliance("test-comm-conflict", "enforcement", context)
        assert result.status in [ComplianceStatus.REQUIRES_REVIEW, ComplianceStatus.CONDITIONAL_APPROVAL, ComplianceStatus.COMPLIANT]


class TestRetentionPolicyConflicts:
    """Tests for data retention policy conflicts"""

    def setup_method(self):
        """Setup test fixtures"""
        self.civil_engine = get_civil_liberties_engine()

    def test_retention_investigation_conflict(self):
        """Test conflict between retention limits and ongoing investigation"""
        context = {
            "data_type": "surveillance_footage",
            "retention_days": 45,
            "ongoing_investigation": True,
        }
        result = self.civil_engine.check_compliance("test-retention-conflict", "data_retention", context)
        assert result.status in [ComplianceStatus.REQUIRES_REVIEW, ComplianceStatus.CONDITIONAL_APPROVAL, ComplianceStatus.COMPLIANT]


class TestMultipleViolationConflicts:
    """Tests for multiple simultaneous violations"""

    def setup_method(self):
        """Setup test fixtures"""
        self.civil_engine = get_civil_liberties_engine()

    def test_multiple_constitutional_violations(self):
        """Test handling of multiple constitutional violations"""
        context = {
            "has_warrant": False,
            "consent": False,
            "targeting_speech": True,
            "demographic_targeting": True,
        }
        result = self.civil_engine.check_compliance("test-multi-violation", "surveillance", context)
        assert result.blocked is True
        assert len(result.violations) >= 1

    def test_violation_priority(self):
        """Test that most severe violation takes priority"""
        context = {
            "has_warrant": False,
            "consent": False,
            "targeting_speech": True,
        }
        result = self.civil_engine.check_compliance("test-priority", "surveillance", context)
        assert result.status == ComplianceStatus.NON_COMPLIANT_BLOCKED


class TestPolicyOverrideConflicts:
    """Tests for policy override scenarios"""

    def setup_method(self):
        """Setup test fixtures"""
        self.civil_engine = get_civil_liberties_engine()

    def test_emergency_override(self):
        """Test emergency override of standard policies"""
        context = {
            "has_warrant": False,
            "consent": False,
            "imminent_threat_to_life": True,
        }
        result = self.civil_engine.check_compliance("test-emergency", "search", context)
        assert result.status in [ComplianceStatus.CONDITIONAL_APPROVAL, ComplianceStatus.REQUIRES_REVIEW, ComplianceStatus.COMPLIANT]

    def test_supervisor_override_tracking(self):
        """Test that supervisor overrides are tracked"""
        context = {
            "has_warrant": False,
            "consent": False,
            "supervisor_override": True,
            "override_justification": "Exigent circumstances",
        }
        result = self.civil_engine.check_compliance("test-override", "search", context)
        assert result is not None


class TestCrossEngineConflicts:
    """Tests for conflicts across multiple engines"""

    def setup_method(self):
        """Setup test fixtures"""
        self.bias_engine = get_bias_detection_engine()
        self.civil_engine = get_civil_liberties_engine()
        self.ethics_engine = get_ethics_score_engine()

    def test_all_engines_agree_allow(self):
        """Test when all engines agree to allow"""
        bias_data = {
            "demographic_outcomes": {
                "Black": {"positive": 88, "negative": 12},
                "White": {"positive": 90, "negative": 10},
            },
            "reference_group": "White",
        }
        bias_result = self.bias_engine.analyze_for_bias(AnalysisType.PREDICTIVE_AI, bias_data)

        civil_context = {"has_warrant": True, "consent": True}
        civil_result = self.civil_engine.check_compliance("test-agree-allow", "search", civil_context)

        ethics_context = {
            "bias_detected": False,
            "civil_rights_compliant": True,
            "force_risk": 10,
            "policy_compliant": True,
        }
        ethics_result = self.ethics_engine.compute_ethics_score("test-agree-allow", "search", ethics_context)

        assert bias_result.blocked is False
        assert civil_result.blocked is False
        assert ethics_result.required_action == RequiredAction.ALLOW

    def test_all_engines_agree_block(self):
        """Test when all engines agree to block"""
        bias_data = {
            "demographic_outcomes": {
                "Black": {"positive": 30, "negative": 70},
                "White": {"positive": 90, "negative": 10},
            },
            "reference_group": "White",
        }
        bias_result = self.bias_engine.analyze_for_bias(AnalysisType.ENFORCEMENT_RECOMMENDATION, bias_data)

        civil_context = {
            "has_warrant": False,
            "consent": False,
            "targeting_speech": True,
        }
        civil_result = self.civil_engine.check_compliance("test-agree-block", "surveillance", civil_context)

        ethics_context = {
            "bias_detected": True,
            "civil_rights_violation": True,
            "force_risk": 90,
            "policy_compliant": False,
        }
        ethics_result = self.ethics_engine.compute_ethics_score("test-agree-block", "enforcement", ethics_context)

        assert bias_result.blocked is True
        assert civil_result.blocked is True
        assert ethics_result.required_action == RequiredAction.BLOCK
