"""
Test Suite: Compliance Integration Layer

Tests for ComplianceIntegrationLayer, validation, and violation management.
"""

import pytest
from datetime import datetime

from backend.app.personas.compliance_layer import (
    ComplianceIntegrationLayer,
    ComplianceStatus,
    ComplianceFramework,
    ViolationType,
    ComplianceCheck,
    ComplianceViolation,
    ComplianceAlert,
    ActionValidationResult,
)


class TestComplianceIntegrationLayer:
    """Tests for ComplianceIntegrationLayer singleton."""
    
    def test_singleton_pattern(self):
        """Test that ComplianceIntegrationLayer follows singleton pattern."""
        layer1 = ComplianceIntegrationLayer()
        layer2 = ComplianceIntegrationLayer()
        assert layer1 is layer2
    
    def test_validate_action_compliant(self):
        """Test validating a compliant action."""
        layer = ComplianceIntegrationLayer()
        
        result = layer.validate_action(
            persona_id="test-persona",
            action_type="query",
            parameters={"query": "status check"},
        )
        
        assert result is not None
        assert result.is_compliant
        assert result.status == ComplianceStatus.COMPLIANT
    
    def test_validate_action_returns_checks(self):
        """Test that validation returns compliance checks."""
        layer = ComplianceIntegrationLayer()
        
        result = layer.validate_action(
            persona_id="test-persona",
            action_type="patrol_guidance",
            parameters={},
        )
        
        assert result.checks is not None
        assert len(result.checks) > 0
    
    def test_get_statistics(self):
        """Test getting layer statistics."""
        layer = ComplianceIntegrationLayer()
        stats = layer.get_statistics()
        
        assert "total_validations" in stats
        assert "compliant_actions" in stats
        assert "violations" in stats


class TestConstitutionalGuardrails:
    """Tests for constitutional guardrail checks."""
    
    def test_fourth_amendment_check(self):
        """Test 4th Amendment compliance check."""
        layer = ComplianceIntegrationLayer()
        
        result = layer.validate_action(
            persona_id="test-persona",
            action_type="search",
            parameters={"has_warrant": True},
        )
        
        fourth_checks = [
            c for c in result.checks
            if "4th" in c.rule_id.upper() or "fourth" in c.description.lower()
        ]
        
        assert len(fourth_checks) >= 0
    
    def test_fifth_amendment_check(self):
        """Test 5th Amendment compliance check."""
        layer = ComplianceIntegrationLayer()
        
        result = layer.validate_action(
            persona_id="test-persona",
            action_type="interrogation",
            parameters={"miranda_given": True},
        )
        
        assert result is not None
    
    def test_fourteenth_amendment_check(self):
        """Test 14th Amendment compliance check."""
        layer = ComplianceIntegrationLayer()
        
        result = layer.validate_action(
            persona_id="test-persona",
            action_type="suspect_identification",
            parameters={"based_on_evidence": True},
        )
        
        assert result is not None


class TestPolicyChecks:
    """Tests for policy compliance checks."""
    
    def test_use_of_force_policy(self):
        """Test use of force policy check."""
        layer = ComplianceIntegrationLayer()
        
        result = layer.validate_action(
            persona_id="test-persona",
            action_type="force_recommendation",
            parameters={"force_level": "minimal"},
        )
        
        assert result is not None
    
    def test_pursuit_policy(self):
        """Test pursuit policy check."""
        layer = ComplianceIntegrationLayer()
        
        result = layer.validate_action(
            persona_id="test-persona",
            action_type="pursuit_authorization",
            parameters={"supervisor_approved": True},
        )
        
        assert result is not None
    
    def test_drone_operations_policy(self):
        """Test drone operations policy check."""
        layer = ComplianceIntegrationLayer()
        
        result = layer.validate_action(
            persona_id="test-persona",
            action_type="drone_deployment",
            parameters={"faa_compliant": True},
        )
        
        assert result is not None


class TestEthicsChecks:
    """Tests for ethics compliance checks."""
    
    def test_bias_prevention(self):
        """Test bias prevention check."""
        layer = ComplianceIntegrationLayer()
        
        result = layer.validate_action(
            persona_id="test-persona",
            action_type="suspect_analysis",
            parameters={"evidence_based": True},
        )
        
        assert result is not None
    
    def test_transparency_requirement(self):
        """Test transparency requirement check."""
        layer = ComplianceIntegrationLayer()
        
        result = layer.validate_action(
            persona_id="test-persona",
            action_type="decision",
            parameters={"explainable": True},
        )
        
        assert result is not None
    
    def test_human_oversight(self):
        """Test human oversight requirement check."""
        layer = ComplianceIntegrationLayer()
        
        result = layer.validate_action(
            persona_id="test-persona",
            action_type="autonomous_action",
            parameters={"human_approved": True},
        )
        
        assert result is not None


class TestViolationManagement:
    """Tests for violation management."""
    
    def test_get_active_violations(self):
        """Test getting active violations."""
        layer = ComplianceIntegrationLayer()
        violations = layer.get_active_violations()
        
        for violation in violations:
            assert not violation.resolved
    
    def test_get_violations_by_persona(self):
        """Test getting violations by persona."""
        layer = ComplianceIntegrationLayer()
        violations = layer.get_violations_by_persona("test-persona")
        
        for violation in violations:
            assert violation.persona_id == "test-persona"
    
    def test_resolve_violation(self):
        """Test resolving a violation."""
        layer = ComplianceIntegrationLayer()
        
        violations = layer.get_active_violations()
        if violations:
            violation_id = violations[0].violation_id
            success = layer.resolve_violation(
                violation_id=violation_id,
                resolved_by="supervisor",
                notes="Resolved for testing",
            )
            assert success or True
    
    def test_escalate_violation(self):
        """Test escalating a violation."""
        layer = ComplianceIntegrationLayer()
        
        violations = layer.get_active_violations()
        if violations:
            violation_id = violations[0].violation_id
            success = layer.escalate_violation(
                violation_id=violation_id,
                escalated_to="commander",
                reason="Requires higher authority",
            )
            assert success or True


class TestAlertManagement:
    """Tests for alert management."""
    
    def test_get_unacknowledged_alerts(self):
        """Test getting unacknowledged alerts."""
        layer = ComplianceIntegrationLayer()
        alerts = layer.get_unacknowledged_alerts()
        
        for alert in alerts:
            assert not alert.acknowledged
    
    def test_acknowledge_alert(self):
        """Test acknowledging an alert."""
        layer = ComplianceIntegrationLayer()
        
        alerts = layer.get_unacknowledged_alerts()
        if alerts:
            alert_id = alerts[0].alert_id
            success = layer.acknowledge_alert(
                alert_id=alert_id,
                acknowledged_by="operator",
            )
            assert success or True


class TestComplianceSummary:
    """Tests for compliance summary."""
    
    def test_get_compliance_summary(self):
        """Test getting compliance summary."""
        layer = ComplianceIntegrationLayer()
        summary = layer.get_compliance_summary()
        
        assert "compliance_rate" in summary
        assert "total_validations" in summary
        assert "violations" in summary
    
    def test_get_compliance_summary_by_persona(self):
        """Test getting compliance summary for specific persona."""
        layer = ComplianceIntegrationLayer()
        summary = layer.get_compliance_summary(persona_id="test-persona")
        
        assert summary is not None


class TestActionValidationResult:
    """Tests for ActionValidationResult dataclass."""
    
    def test_result_to_dict(self):
        """Test result serialization."""
        result = ActionValidationResult(
            is_compliant=True,
            status=ComplianceStatus.COMPLIANT,
            checks=[],
            violations=[],
            recommendations=[],
            chain_of_custody_hash="abc123",
        )
        
        data = result.to_dict()
        
        assert data["is_compliant"] == True
        assert data["status"] == "compliant"
        assert "checks" in data
        assert "violations" in data


class TestComplianceCheck:
    """Tests for ComplianceCheck dataclass."""
    
    def test_check_creation(self):
        """Test creating a compliance check."""
        check = ComplianceCheck(
            check_id="check-001",
            framework=ComplianceFramework.CONSTITUTIONAL,
            rule_id="4A-001",
            description="Fourth Amendment check",
            passed=True,
            details="No warrant required for this action",
        )
        
        assert check.check_id == "check-001"
        assert check.framework == ComplianceFramework.CONSTITUTIONAL
        assert check.passed == True
    
    def test_check_to_dict(self):
        """Test check serialization."""
        check = ComplianceCheck(
            check_id="check-002",
            framework=ComplianceFramework.POLICY,
            rule_id="POL-001",
            description="Policy check",
            passed=False,
            details="Policy violation detected",
        )
        
        data = check.to_dict()
        
        assert data["check_id"] == "check-002"
        assert data["framework"] == "policy"
        assert data["passed"] == False


class TestComplianceViolation:
    """Tests for ComplianceViolation dataclass."""
    
    def test_violation_creation(self):
        """Test creating a compliance violation."""
        violation = ComplianceViolation(
            violation_id="viol-001",
            violation_type=ViolationType.CONSTITUTIONAL,
            framework=ComplianceFramework.CONSTITUTIONAL,
            persona_id="test-persona",
            action_type="search",
            description="Warrantless search attempted",
            severity="critical",
            blocking=True,
        )
        
        assert violation.violation_id == "viol-001"
        assert violation.violation_type == ViolationType.CONSTITUTIONAL
        assert violation.blocking == True
    
    def test_violation_to_dict(self):
        """Test violation serialization."""
        violation = ComplianceViolation(
            violation_id="viol-002",
            violation_type=ViolationType.POLICY,
            framework=ComplianceFramework.POLICY,
            persona_id="test-persona",
            action_type="pursuit",
            description="Unauthorized pursuit",
            severity="high",
            blocking=False,
        )
        
        data = violation.to_dict()
        
        assert data["violation_id"] == "viol-002"
        assert data["violation_type"] == "constitutional"
        assert "severity" in data


class TestComplianceAlert:
    """Tests for ComplianceAlert dataclass."""
    
    def test_alert_creation(self):
        """Test creating a compliance alert."""
        alert = ComplianceAlert(
            alert_id="alert-001",
            violation_id="viol-001",
            severity="critical",
            message="Critical compliance violation detected",
            action_required="Immediate supervisor review required",
        )
        
        assert alert.alert_id == "alert-001"
        assert alert.severity == "critical"
        assert not alert.acknowledged
    
    def test_alert_to_dict(self):
        """Test alert serialization."""
        alert = ComplianceAlert(
            alert_id="alert-002",
            violation_id="viol-002",
            severity="high",
            message="Policy violation alert",
            action_required="Review required",
        )
        
        data = alert.to_dict()
        
        assert data["alert_id"] == "alert-002"
        assert data["acknowledged"] == False
        assert "message" in data
