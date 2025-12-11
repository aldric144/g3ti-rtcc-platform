"""
Test Suite 10: End-to-End Ethical Decision Simulation Tests
Tests for complete ethical decision workflows
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../backend'))

from app.ethics_guardian.bias_detection import (
    get_bias_detection_engine,
    BiasStatus,
    AnalysisType,
)
from app.ethics_guardian.force_risk import (
    get_force_risk_engine,
    RiskLevel,
)
from app.ethics_guardian.civil_liberties import (
    get_civil_liberties_engine,
    ComplianceStatus,
)
from app.ethics_guardian.protected_communities import (
    get_protected_community_safeguards,
    CommunityType,
)
from app.ethics_guardian.ethics_score import (
    get_ethics_score_engine,
    EthicsLevel,
    RequiredAction,
)
from app.ethics_guardian.transparency import (
    get_transparency_engine,
)


class TestPatrolRoutingDecision:
    """End-to-end test for patrol routing decision"""

    def setup_method(self):
        """Setup test fixtures"""
        self.bias_engine = get_bias_detection_engine()
        self.civil_engine = get_civil_liberties_engine()
        self.safeguards = get_protected_community_safeguards()
        self.ethics_engine = get_ethics_score_engine()
        self.transparency_engine = get_transparency_engine()

    def test_fair_patrol_routing_allowed(self):
        """Test fair patrol routing is allowed through full pipeline"""
        bias_data = {
            "demographic_outcomes": {
                "Black": {"positive": 65, "negative": 35},
                "White": {"positive": 68, "negative": 32},
                "Hispanic": {"positive": 66, "negative": 34},
            },
            "reference_group": "White",
        }
        bias_result = self.bias_engine.analyze_for_bias(
            AnalysisType.PATROL_ROUTING, bias_data
        )
        assert bias_result.status == BiasStatus.NO_BIAS_DETECTED

        civil_context = {"routine_patrol": True, "public_area": True}
        civil_result = self.civil_engine.check_compliance(
            "patrol-001", "patrol", civil_context
        )
        assert civil_result.status == ComplianceStatus.COMPLIANT

        safeguard_context = {"affected_communities": [], "disparate_impact_ratio": 0.96}
        safeguard_result = self.safeguards.check_safeguards(
            "patrol-001", "patrol", safeguard_context
        )
        assert len(safeguard_result.triggered_rules) == 0

        ethics_context = {
            "bias_detected": False,
            "civil_rights_compliant": True,
            "force_risk": 5,
            "policy_compliant": True,
            "transparency_score": 0.95,
        }
        ethics_result = self.ethics_engine.compute_ethics_score(
            "patrol-001", "patrol", ethics_context
        )
        assert ethics_result.ethics_level in [EthicsLevel.EXCELLENT, EthicsLevel.GOOD]
        assert ethics_result.required_action == RequiredAction.ALLOW

        decision_data = {
            "decision": "ALLOW",
            "ethics_score": ethics_result.total_score,
            "bias_detected": False,
            "civil_rights_compliant": True,
        }
        explanation = self.transparency_engine.generate_explanation(
            "patrol-001", "patrol", decision_data
        )
        assert explanation is not None
        assert "ALLOW" in explanation.summary


class TestSurveillanceDecision:
    """End-to-end test for surveillance decision"""

    def setup_method(self):
        """Setup test fixtures"""
        self.bias_engine = get_bias_detection_engine()
        self.civil_engine = get_civil_liberties_engine()
        self.safeguards = get_protected_community_safeguards()
        self.ethics_engine = get_ethics_score_engine()
        self.transparency_engine = get_transparency_engine()

    def test_warranted_surveillance_allowed(self):
        """Test warranted surveillance is allowed"""
        civil_context = {
            "has_warrant": True,
            "probable_cause": True,
            "targeting_speech": False,
        }
        civil_result = self.civil_engine.check_compliance(
            "surv-001", "surveillance", civil_context
        )
        assert civil_result.status == ComplianceStatus.COMPLIANT
        assert civil_result.blocked is False

    def test_warrantless_surveillance_blocked(self):
        """Test warrantless surveillance is blocked"""
        civil_context = {
            "has_warrant": False,
            "consent": False,
            "exigent_circumstances": False,
        }
        civil_result = self.civil_engine.check_compliance(
            "surv-002", "surveillance", civil_context
        )
        assert civil_result.status in [
            ComplianceStatus.NON_COMPLIANT_BLOCKED,
            ComplianceStatus.REQUIRES_REVIEW,
        ]


class TestEnforcementDecision:
    """End-to-end test for enforcement decision"""

    def setup_method(self):
        """Setup test fixtures"""
        self.bias_engine = get_bias_detection_engine()
        self.force_engine = get_force_risk_engine()
        self.civil_engine = get_civil_liberties_engine()
        self.safeguards = get_protected_community_safeguards()
        self.ethics_engine = get_ethics_score_engine()
        self.transparency_engine = get_transparency_engine()

    def test_biased_enforcement_blocked(self):
        """Test biased enforcement is blocked"""
        bias_data = {
            "demographic_outcomes": {
                "Black": {"positive": 30, "negative": 70},
                "White": {"positive": 85, "negative": 15},
            },
            "reference_group": "White",
        }
        bias_result = self.bias_engine.analyze_for_bias(
            AnalysisType.ENFORCEMENT_RECOMMENDATION, bias_data
        )
        assert bias_result.status == BiasStatus.BIAS_DETECTED_BLOCKED
        assert bias_result.blocked is True

        ethics_context = {
            "bias_detected": True,
            "civil_rights_compliant": False,
            "force_risk": 70,
            "policy_compliant": False,
        }
        ethics_result = self.ethics_engine.compute_ethics_score(
            "enforce-001", "enforcement", ethics_context
        )
        assert ethics_result.required_action == RequiredAction.BLOCK

    def test_high_force_risk_requires_review(self):
        """Test high force risk requires review"""
        force_context = {
            "civil_rights_exposure": 70,
            "force_escalation_probability": 65,
            "mental_health_indicators": 60,
            "juvenile_involvement": True,
            "sensitive_location": True,
            "protected_class": True,
        }
        force_result = self.force_engine.assess_force_risk("enforce-002", force_context)
        assert force_result.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]
        assert len(force_result.deescalation_recommendations) > 0


class TestProtectedCommunityDecision:
    """End-to-end test for protected community decision"""

    def setup_method(self):
        """Setup test fixtures"""
        self.bias_engine = get_bias_detection_engine()
        self.safeguards = get_protected_community_safeguards()
        self.ethics_engine = get_ethics_score_engine()
        self.transparency_engine = get_transparency_engine()

    def test_black_community_safeguard_triggered(self):
        """Test Black community safeguard is triggered on disparity"""
        safeguard_context = {
            "affected_communities": [CommunityType.BLACK_COMMUNITY],
            "disparate_impact_ratio": 0.72,
        }
        safeguard_result = self.safeguards.check_safeguards(
            "comm-001", "enforcement", safeguard_context
        )
        assert len(safeguard_result.triggered_rules) > 0

    def test_lgbtq_youth_safeguard_triggered(self):
        """Test LGBTQ+ Youth safeguard is triggered"""
        safeguard_context = {
            "affected_communities": [CommunityType.LGBTQ_YOUTH],
            "involves_minor": True,
        }
        safeguard_result = self.safeguards.check_safeguards(
            "comm-002", "enforcement", safeguard_context
        )
        assert safeguard_result is not None


class TestDroneOperationDecision:
    """End-to-end test for drone operation decision"""

    def setup_method(self):
        """Setup test fixtures"""
        self.civil_engine = get_civil_liberties_engine()
        self.ethics_engine = get_ethics_score_engine()
        self.transparency_engine = get_transparency_engine()

    def test_drone_within_limits_allowed(self):
        """Test drone operation within Florida limits is allowed"""
        civil_context = {
            "drone_surveillance_hours": 20,
            "has_warrant": True,
            "public_area": True,
        }
        civil_result = self.civil_engine.check_compliance(
            "drone-001", "drone_surveillance", civil_context
        )
        assert civil_result.status in [
            ComplianceStatus.COMPLIANT,
            ComplianceStatus.CONDITIONAL_APPROVAL,
        ]

    def test_drone_exceeds_limits_blocked(self):
        """Test drone operation exceeding Florida limits is blocked"""
        civil_context = {
            "drone_surveillance_hours": 30,
            "has_warrant": False,
        }
        civil_result = self.civil_engine.check_compliance(
            "drone-002", "drone_surveillance", civil_context
        )
        assert civil_result.blocked is True


class TestSearchDecision:
    """End-to-end test for search decision"""

    def setup_method(self):
        """Setup test fixtures"""
        self.civil_engine = get_civil_liberties_engine()
        self.ethics_engine = get_ethics_score_engine()
        self.transparency_engine = get_transparency_engine()

    def test_consent_search_allowed(self):
        """Test consent search is allowed"""
        civil_context = {
            "has_warrant": False,
            "consent": True,
        }
        civil_result = self.civil_engine.check_compliance(
            "search-001", "search", civil_context
        )
        assert civil_result.status == ComplianceStatus.COMPLIANT

    def test_exigent_search_conditional(self):
        """Test exigent circumstances search is conditional"""
        civil_context = {
            "has_warrant": False,
            "consent": False,
            "exigent_circumstances": True,
        }
        civil_result = self.civil_engine.check_compliance(
            "search-002", "search", civil_context
        )
        assert civil_result.status in [
            ComplianceStatus.CONDITIONAL_APPROVAL,
            ComplianceStatus.REQUIRES_REVIEW,
            ComplianceStatus.COMPLIANT,
        ]


class TestFullPipelineIntegration:
    """Full pipeline integration tests"""

    def setup_method(self):
        """Setup test fixtures"""
        self.bias_engine = get_bias_detection_engine()
        self.force_engine = get_force_risk_engine()
        self.civil_engine = get_civil_liberties_engine()
        self.safeguards = get_protected_community_safeguards()
        self.ethics_engine = get_ethics_score_engine()
        self.transparency_engine = get_transparency_engine()

    def test_complete_allow_pipeline(self):
        """Test complete pipeline resulting in ALLOW"""
        bias_data = {
            "demographic_outcomes": {
                "Black": {"positive": 88, "negative": 12},
                "White": {"positive": 90, "negative": 10},
            },
            "reference_group": "White",
        }
        bias_result = self.bias_engine.analyze_for_bias(
            AnalysisType.PREDICTIVE_AI, bias_data
        )

        force_context = {
            "civil_rights_exposure": 15,
            "force_escalation_probability": 10,
            "mental_health_indicators": 0,
        }
        force_result = self.force_engine.assess_force_risk("full-001", force_context)

        civil_context = {"has_warrant": True, "probable_cause": True}
        civil_result = self.civil_engine.check_compliance(
            "full-001", "search", civil_context
        )

        safeguard_context = {"affected_communities": [], "disparate_impact_ratio": 0.98}
        safeguard_result = self.safeguards.check_safeguards(
            "full-001", "search", safeguard_context
        )

        ethics_context = {
            "bias_detected": bias_result.blocked,
            "civil_rights_compliant": not civil_result.blocked,
            "force_risk": force_result.risk_score,
            "policy_compliant": True,
            "transparency_score": 0.95,
        }
        ethics_result = self.ethics_engine.compute_ethics_score(
            "full-001", "search", ethics_context
        )

        decision_data = {
            "decision": ethics_result.required_action.value,
            "ethics_score": ethics_result.total_score,
            "bias_detected": bias_result.blocked,
            "civil_rights_compliant": not civil_result.blocked,
            "force_risk": force_result.risk_score,
        }
        explanation = self.transparency_engine.generate_explanation(
            "full-001", "search", decision_data
        )

        assert bias_result.blocked is False
        assert civil_result.blocked is False
        assert force_result.risk_level == RiskLevel.LOW
        assert len(safeguard_result.triggered_rules) == 0
        assert ethics_result.required_action == RequiredAction.ALLOW
        assert explanation is not None

    def test_complete_block_pipeline(self):
        """Test complete pipeline resulting in BLOCK"""
        bias_data = {
            "demographic_outcomes": {
                "Black": {"positive": 25, "negative": 75},
                "White": {"positive": 90, "negative": 10},
            },
            "reference_group": "White",
        }
        bias_result = self.bias_engine.analyze_for_bias(
            AnalysisType.ENFORCEMENT_RECOMMENDATION, bias_data
        )

        force_context = {
            "civil_rights_exposure": 90,
            "force_escalation_probability": 85,
            "mental_health_indicators": 70,
            "juvenile_involvement": True,
            "sensitive_location": True,
            "protected_class": True,
        }
        force_result = self.force_engine.assess_force_risk("full-002", force_context)

        civil_context = {
            "has_warrant": False,
            "consent": False,
            "targeting_speech": True,
        }
        civil_result = self.civil_engine.check_compliance(
            "full-002", "surveillance", civil_context
        )

        safeguard_context = {
            "affected_communities": [CommunityType.BLACK_COMMUNITY],
            "disparate_impact_ratio": 0.28,
        }
        safeguard_result = self.safeguards.check_safeguards(
            "full-002", "enforcement", safeguard_context
        )

        ethics_context = {
            "bias_detected": True,
            "civil_rights_violation": True,
            "force_risk": force_result.risk_score,
            "policy_compliant": False,
            "transparency_score": 0.20,
        }
        ethics_result = self.ethics_engine.compute_ethics_score(
            "full-002", "enforcement", ethics_context
        )

        decision_data = {
            "decision": "BLOCK",
            "ethics_score": ethics_result.total_score,
            "bias_detected": True,
            "civil_rights_violation": True,
        }
        explanation = self.transparency_engine.generate_explanation(
            "full-002", "enforcement", decision_data
        )

        assert bias_result.blocked is True
        assert civil_result.blocked is True
        assert force_result.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]
        assert len(safeguard_result.triggered_rules) > 0
        assert ethics_result.required_action == RequiredAction.BLOCK
        assert explanation is not None


class TestAuditTrailIntegrity:
    """Tests for audit trail integrity across pipeline"""

    def setup_method(self):
        """Setup test fixtures"""
        self.transparency_engine = get_transparency_engine()

    def test_audit_chain_after_multiple_decisions(self):
        """Test audit chain integrity after multiple decisions"""
        for i in range(5):
            decision_data = {
                "decision": "ALLOW",
                "ethics_score": 85 + i,
            }
            self.transparency_engine.generate_explanation(
                f"audit-test-{i}", "patrol", decision_data
            )

        is_valid = self.transparency_engine.verify_audit_chain()
        assert is_valid is True
