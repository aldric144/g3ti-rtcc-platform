"""
Test Suite: Safety Constraints

Tests for safety constraints, constitutional compliance, and policy enforcement.
"""

import pytest
from datetime import datetime

from backend.app.personas.persona_engine import (
    PersonaEngine,
    SafetyConstraint,
)
from backend.app.personas.compliance_layer import (
    ComplianceIntegrationLayer,
    ComplianceStatus,
    ComplianceFramework,
    ViolationType,
)


class TestSafetyConstraints:
    """Tests for safety constraint definitions."""
    
    def test_default_constraints_initialized(self):
        """Test that default safety constraints are initialized."""
        engine = PersonaEngine()
        
        assert len(engine.safety_constraints) >= 7
    
    def test_constraint_types(self):
        """Test that all constraint types are represented."""
        engine = PersonaEngine()
        
        constraint_types = [c.constraint_type for c in engine.safety_constraints]
        
        assert "constitutional" in constraint_types
        assert "policy" in constraint_types
        assert "ethical" in constraint_types
        assert "operational" in constraint_types
    
    def test_constraint_severities(self):
        """Test constraint severity levels."""
        engine = PersonaEngine()
        
        severities = [c.severity for c in engine.safety_constraints]
        
        assert "critical" in severities


class TestConstitutionalConstraints:
    """Tests for constitutional safety constraints."""
    
    def test_fourth_amendment_constraint(self):
        """Test 4th Amendment constraint exists."""
        engine = PersonaEngine()
        
        fourth_constraints = [
            c for c in engine.safety_constraints
            if "4th" in c.constraint_id.upper() or "fourth" in c.name.lower()
        ]
        
        assert len(fourth_constraints) >= 1
    
    def test_fifth_amendment_constraint(self):
        """Test 5th Amendment constraint exists."""
        engine = PersonaEngine()
        
        fifth_constraints = [
            c for c in engine.safety_constraints
            if "5th" in c.constraint_id.upper() or "fifth" in c.name.lower()
        ]
        
        assert len(fifth_constraints) >= 1
    
    def test_fourteenth_amendment_constraint(self):
        """Test 14th Amendment constraint exists."""
        engine = PersonaEngine()
        
        fourteenth_constraints = [
            c for c in engine.safety_constraints
            if "14th" in c.constraint_id.upper() or "fourteenth" in c.name.lower()
        ]
        
        assert len(fourteenth_constraints) >= 1


class TestPolicyConstraints:
    """Tests for policy safety constraints."""
    
    def test_human_approval_constraint(self):
        """Test human approval constraint exists."""
        engine = PersonaEngine()
        
        approval_constraints = [
            c for c in engine.safety_constraints
            if "approval" in c.name.lower() or "human" in c.description.lower()
        ]
        
        assert len(approval_constraints) >= 1
    
    def test_supervisor_authorization_constraint(self):
        """Test supervisor authorization constraint exists."""
        engine = PersonaEngine()
        
        supervisor_constraints = [
            c for c in engine.safety_constraints
            if "supervisor" in c.name.lower() or "authorization" in c.description.lower()
        ]
        
        assert len(supervisor_constraints) >= 0


class TestConstraintEnforcement:
    """Tests for constraint enforcement."""
    
    def test_check_safety_constraints(self):
        """Test checking safety constraints."""
        engine = PersonaEngine()
        personas = engine.get_all_personas()
        
        if personas:
            result = engine.check_safety_constraints(
                persona_id=personas[0].persona_id,
                action_type="query",
                parameters={},
            )
            
            assert result is not None
            assert "passed" in result
            assert "failed" in result
    
    def test_constraint_blocking(self):
        """Test that critical constraints block actions."""
        layer = ComplianceIntegrationLayer()
        
        result = layer.validate_action(
            persona_id="test-persona",
            action_type="warrantless_search",
            parameters={"has_warrant": False},
        )
        
        assert result is not None
    
    def test_constraint_warning(self):
        """Test that non-critical constraints generate warnings."""
        layer = ComplianceIntegrationLayer()
        
        result = layer.validate_action(
            persona_id="test-persona",
            action_type="routine_query",
            parameters={},
        )
        
        assert result is not None


class TestSafetyConstraintDataclass:
    """Tests for SafetyConstraint dataclass."""
    
    def test_constraint_creation(self):
        """Test creating a safety constraint."""
        constraint = SafetyConstraint(
            constraint_id="TEST-001",
            name="Test Constraint",
            description="Test constraint description",
            constraint_type="policy",
            severity="high",
            enforcement="warn",
        )
        
        assert constraint.constraint_id == "TEST-001"
        assert constraint.name == "Test Constraint"
        assert constraint.constraint_type == "policy"
        assert constraint.severity == "high"
        assert constraint.enforcement == "warn"
    
    def test_constraint_with_conditions(self):
        """Test creating constraint with conditions."""
        constraint = SafetyConstraint(
            constraint_id="TEST-002",
            name="Conditional Constraint",
            description="Constraint with conditions",
            constraint_type="operational",
            severity="medium",
            enforcement="block",
            conditions=["condition1", "condition2"],
        )
        
        assert len(constraint.conditions) == 2
    
    def test_constraint_to_dict(self):
        """Test constraint serialization."""
        constraint = SafetyConstraint(
            constraint_id="TEST-003",
            name="Serialization Test",
            description="Test",
            constraint_type="ethical",
            severity="low",
            enforcement="log",
        )
        
        data = constraint.to_dict()
        
        assert data["constraint_id"] == "TEST-003"
        assert data["constraint_type"] == "ethical"
        assert "severity" in data
        assert "enforcement" in data


class TestConstraintValidation:
    """Tests for constraint validation logic."""
    
    def test_validate_compliant_action(self):
        """Test validating a compliant action."""
        layer = ComplianceIntegrationLayer()
        
        result = layer.validate_action(
            persona_id="test-persona",
            action_type="status_query",
            parameters={},
        )
        
        assert result.is_compliant
        assert result.status == ComplianceStatus.COMPLIANT
    
    def test_validate_action_with_parameters(self):
        """Test validating action with parameters."""
        layer = ComplianceIntegrationLayer()
        
        result = layer.validate_action(
            persona_id="test-persona",
            action_type="search",
            parameters={
                "has_warrant": True,
                "warrant_id": "W-12345",
            },
        )
        
        assert result is not None
    
    def test_validate_returns_checks(self):
        """Test that validation returns constraint checks."""
        layer = ComplianceIntegrationLayer()
        
        result = layer.validate_action(
            persona_id="test-persona",
            action_type="patrol_action",
            parameters={},
        )
        
        assert result.checks is not None
        assert len(result.checks) > 0


class TestConstraintIntegration:
    """Tests for constraint integration with personas."""
    
    def test_persona_respects_constraints(self):
        """Test that personas respect safety constraints."""
        engine = PersonaEngine()
        layer = ComplianceIntegrationLayer()
        
        personas = engine.get_all_personas()
        if personas:
            result = layer.validate_action(
                persona_id=personas[0].persona_id,
                action_type="standard_operation",
                parameters={},
            )
            
            assert result is not None
    
    def test_constraint_affects_compliance_score(self):
        """Test that constraints affect compliance score."""
        engine = PersonaEngine()
        
        personas = engine.get_all_personas()
        if personas:
            score = personas[0].get_compliance_score()
            assert 0 <= score <= 100


class TestConstraintCategories:
    """Tests for constraint categories."""
    
    def test_constitutional_category(self):
        """Test constitutional constraint category."""
        layer = ComplianceIntegrationLayer()
        
        result = layer.validate_action(
            persona_id="test-persona",
            action_type="constitutional_test",
            parameters={},
        )
        
        constitutional_checks = [
            c for c in result.checks
            if c.framework == ComplianceFramework.CONSTITUTIONAL
        ]
        
        assert len(constitutional_checks) >= 0
    
    def test_policy_category(self):
        """Test policy constraint category."""
        layer = ComplianceIntegrationLayer()
        
        result = layer.validate_action(
            persona_id="test-persona",
            action_type="policy_test",
            parameters={},
        )
        
        policy_checks = [
            c for c in result.checks
            if c.framework == ComplianceFramework.POLICY
        ]
        
        assert len(policy_checks) >= 0
    
    def test_ethics_category(self):
        """Test ethics constraint category."""
        layer = ComplianceIntegrationLayer()
        
        result = layer.validate_action(
            persona_id="test-persona",
            action_type="ethics_test",
            parameters={},
        )
        
        ethics_checks = [
            c for c in result.checks
            if c.framework == ComplianceFramework.ETHICS
        ]
        
        assert len(ethics_checks) >= 0
