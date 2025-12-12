"""
Test Suite: Ethical & Legal Governance Layer

Tests for the ethics guard functionality including:
- Action validation
- Compliance rule enforcement
- Violation detection
- Bias auditing
- Data retention compliance
- Constitutional protections
"""

import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch

import sys
sys.path.insert(0, "/home/ubuntu/repos/g3ti-rtcc-platform")

from backend.app.ai_supervisor.ethics_guard import (
    EthicsGuard,
    ComplianceFramework,
    ViolationType,
    ViolationSeverity,
    ActionDecision,
    ProtectedClass,
    ComplianceRule,
    EthicsViolation,
    ActionValidation,
    BiasAuditResult,
    DataRetentionPolicy,
)


class TestEthicsGuard:
    """Test cases for EthicsGuard class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.guard = EthicsGuard()

    def test_singleton_pattern(self):
        """Test that EthicsGuard follows singleton pattern."""
        guard1 = EthicsGuard()
        guard2 = EthicsGuard()
        assert guard1 is guard2

    def test_compliance_rules_initialized(self):
        """Test that compliance rules are initialized."""
        assert len(self.guard.compliance_rules) > 0

    def test_validate_action_approved(self):
        """Test validating an approved action."""
        validation = self.guard.validate_action(
            action_type="data_query",
            engine="intel_orchestration",
            target="public_records",
            parameters={"query_type": "license_plate"},
            warrant_obtained=False,
            human_approved=True,
            approved_by="Sgt. Johnson",
        )
        assert validation is not None
        assert validation.decision in [ActionDecision.APPROVED, ActionDecision.APPROVED_WITH_CONDITIONS]

    def test_validate_action_blocked_no_warrant(self):
        """Test that surveillance without warrant is blocked."""
        validation = self.guard.validate_action(
            action_type="facial_recognition",
            engine="intel_orchestration",
            target="private_residence",
            parameters={"duration": "24h"},
            warrant_obtained=False,
            human_approved=False,
        )
        assert validation.decision == ActionDecision.BLOCKED
        assert len(validation.violations) > 0

    def test_validate_action_requires_warrant(self):
        """Test that certain actions require warrant."""
        validation = self.guard.validate_action(
            action_type="surveillance",
            engine="drone_task_force",
            target="private_property",
            parameters={},
            warrant_obtained=False,
        )
        assert validation.requires_warrant is True

    def test_validate_action_with_warrant(self):
        """Test that action with warrant is approved."""
        validation = self.guard.validate_action(
            action_type="surveillance",
            engine="drone_task_force",
            target="private_property",
            parameters={},
            warrant_obtained=True,
            human_approved=True,
            approved_by="Judge Smith",
        )
        assert validation.decision in [ActionDecision.APPROVED, ActionDecision.APPROVED_WITH_CONDITIONS]

    def test_conduct_bias_audit(self):
        """Test conducting a bias audit."""
        predictions = [
            {"id": 1, "score": 0.8, "demographics": {"race": "white"}},
            {"id": 2, "score": 0.7, "demographics": {"race": "black"}},
            {"id": 3, "score": 0.9, "demographics": {"race": "white"}},
            {"id": 4, "score": 0.6, "demographics": {"race": "black"}},
        ]
        audit = self.guard.conduct_bias_audit(
            engine="predictive_ai",
            model_name="crime_forecast",
            predictions=predictions,
        )
        assert audit is not None
        assert audit.engine == "predictive_ai"
        assert audit.model_name == "crime_forecast"
        assert "overall_bias_score" in dir(audit)

    def test_conduct_bias_audit_detects_bias(self):
        """Test that bias audit detects significant bias."""
        predictions = [
            {"id": i, "score": 0.9 if i % 2 == 0 else 0.3, "demographics": {"race": "white" if i % 2 == 0 else "black"}}
            for i in range(100)
        ]
        audit = self.guard.conduct_bias_audit(
            engine="predictive_ai",
            model_name="biased_model",
            predictions=predictions,
        )
        assert audit.bias_detected is True

    def test_check_data_retention_compliance(self):
        """Test checking data retention compliance."""
        result = self.guard.check_data_retention_compliance(
            engine="data_lake",
            data_type="surveillance_footage",
            retention_days=30,
        )
        assert result is not None
        assert "compliant" in result

    def test_check_data_retention_violation(self):
        """Test that excessive retention triggers violation."""
        result = self.guard.check_data_retention_compliance(
            engine="data_lake",
            data_type="surveillance_footage",
            retention_days=365,
        )
        assert result["compliant"] is False or "violation" in str(result).lower()

    def test_get_active_violations(self):
        """Test getting active violations."""
        self.guard.validate_action(
            action_type="racial_profiling",
            engine="predictive_ai",
            target="demographic_group",
            parameters={"protected_class": "race"},
            warrant_obtained=False,
        )
        violations = self.guard.get_active_violations()
        assert isinstance(violations, list)

    def test_get_active_violations_by_severity(self):
        """Test filtering violations by severity."""
        violations = self.guard.get_active_violations(severity=ViolationSeverity.CRITICAL)
        assert all(v.severity == ViolationSeverity.CRITICAL for v in violations)

    def test_get_escalated_violations(self):
        """Test getting escalated violations."""
        escalated = self.guard.get_escalated_violations()
        assert isinstance(escalated, list)

    def test_review_violation(self):
        """Test reviewing a violation."""
        self.guard.validate_action(
            action_type="unauthorized_access",
            engine="officer_assist",
            target="restricted_records",
            parameters={},
            warrant_obtained=False,
        )
        violations = self.guard.get_active_violations()
        if violations:
            success = self.guard.review_violation(
                violation_id=violations[0].violation_id,
                reviewed_by="Lt. Commander",
                decision="dismissed",
            )
            assert success is True

    def test_get_compliance_summary(self):
        """Test getting compliance summary."""
        summary = self.guard.get_compliance_summary()
        assert "total_validations" in summary
        assert "approved" in summary
        assert "blocked" in summary
        assert "approval_rate" in summary

    def test_violation_chain_of_custody(self):
        """Test that violations have chain of custody hash."""
        self.guard.validate_action(
            action_type="unlawful_surveillance",
            engine="drone_task_force",
            target="private_residence",
            parameters={},
            warrant_obtained=False,
        )
        violations = self.guard.get_active_violations()
        if violations:
            assert violations[0].chain_of_custody_hash is not None
            assert len(violations[0].chain_of_custody_hash) == 64

    def test_validation_chain_of_custody(self):
        """Test that validations have chain of custody hash."""
        validation = self.guard.validate_action(
            action_type="data_query",
            engine="intel_orchestration",
            target="public_records",
            parameters={},
            warrant_obtained=False,
            human_approved=True,
            approved_by="Admin",
        )
        assert validation.chain_of_custody_hash is not None
        assert len(validation.chain_of_custody_hash) == 64

    def test_get_statistics(self):
        """Test getting guard statistics."""
        stats = self.guard.get_statistics()
        assert "total_validations" in stats
        assert "total_violations" in stats
        assert "bias_audits_conducted" in stats


class TestComplianceFramework:
    """Test cases for ComplianceFramework enum."""

    def test_compliance_framework_values(self):
        """Test compliance framework enum values."""
        assert ComplianceFramework.FOURTH_AMENDMENT.value == "4th_amendment"
        assert ComplianceFramework.FIFTH_AMENDMENT.value == "5th_amendment"
        assert ComplianceFramework.FOURTEENTH_AMENDMENT.value == "14th_amendment"
        assert ComplianceFramework.FLORIDA_STATUTES.value == "florida_statutes"
        assert ComplianceFramework.CJIS_SECURITY_POLICY.value == "cjis_security_policy"


class TestViolationType:
    """Test cases for ViolationType enum."""

    def test_violation_type_values(self):
        """Test violation type enum values."""
        assert ViolationType.UNLAWFUL_SURVEILLANCE.value == "unlawful_surveillance"
        assert ViolationType.WARRANTLESS_SEARCH.value == "warrantless_search"
        assert ViolationType.RACIAL_PROFILING.value == "racial_profiling"
        assert ViolationType.BIAS_DETECTION.value == "bias_detection"


class TestViolationSeverity:
    """Test cases for ViolationSeverity enum."""

    def test_violation_severity_values(self):
        """Test violation severity enum values."""
        assert ViolationSeverity.INFO.value == "info"
        assert ViolationSeverity.WARNING.value == "warning"
        assert ViolationSeverity.VIOLATION.value == "violation"
        assert ViolationSeverity.CRITICAL.value == "critical"
        assert ViolationSeverity.EMERGENCY.value == "emergency"


class TestActionDecision:
    """Test cases for ActionDecision enum."""

    def test_action_decision_values(self):
        """Test action decision enum values."""
        assert ActionDecision.APPROVED.value == "approved"
        assert ActionDecision.APPROVED_WITH_CONDITIONS.value == "approved_with_conditions"
        assert ActionDecision.REQUIRES_REVIEW.value == "requires_review"
        assert ActionDecision.BLOCKED.value == "blocked"
        assert ActionDecision.ESCALATED.value == "escalated"


class TestProtectedClass:
    """Test cases for ProtectedClass enum."""

    def test_protected_class_values(self):
        """Test protected class enum values."""
        assert ProtectedClass.RACE.value == "race"
        assert ProtectedClass.ETHNICITY.value == "ethnicity"
        assert ProtectedClass.RELIGION.value == "religion"
        assert ProtectedClass.GENDER.value == "gender"
        assert ProtectedClass.DISABILITY.value == "disability"
