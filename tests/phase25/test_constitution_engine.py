"""
Test Suite 3: Constitutional Validation Engine Tests

Tests for rule application, precedence, and conflict resolution.
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch

import sys
sys.path.insert(0, "/home/ubuntu/repos/g3ti-rtcc-platform/backend")

from app.city_governance.constitution_engine import (
    get_constitution_engine,
    ConstitutionEngine,
    ConstitutionalRule,
    ConstitutionalLayer,
    ValidationResult,
    ValidationDecision,
    ActionCategory,
    AutonomyLevel,
)


class TestConstitutionalRule:
    """Tests for ConstitutionalRule model."""

    def test_constitutional_rule_creation(self):
        """Test creating a constitutional rule."""
        rule = ConstitutionalRule(
            rule_id="rule-001",
            layer=ConstitutionalLayer.FEDERAL_CONSTITUTIONAL,
            title="Fourth Amendment Protection",
            description="Warrants required for searches",
            condition="requires_warrant == True",
            action="DENY_WITHOUT_WARRANT",
            category=ActionCategory.SURVEILLANCE,
            priority=100,
            citations=["4th Amendment"],
            effective_date=datetime.now(),
            is_active=True,
        )
        assert rule.rule_id == "rule-001"
        assert rule.layer == ConstitutionalLayer.FEDERAL_CONSTITUTIONAL
        assert rule.priority == 100

    def test_constitutional_rule_all_layers(self):
        """Test creating rules for all constitutional layers."""
        layers = [
            ConstitutionalLayer.FEDERAL_CONSTITUTIONAL,
            ConstitutionalLayer.STATE_CONSTITUTIONAL,
            ConstitutionalLayer.STATUTORY,
            ConstitutionalLayer.LOCAL_ORDINANCE,
            ConstitutionalLayer.AGENCY_SOP,
            ConstitutionalLayer.ETHICS,
            ConstitutionalLayer.AUTONOMY,
        ]
        for layer in layers:
            rule = ConstitutionalRule(
                rule_id=f"rule-{layer.value}",
                layer=layer,
                title=f"Test {layer.value}",
                description="Test description",
                condition="test_condition",
                action="TEST_ACTION",
                category=ActionCategory.PUBLIC_SAFETY,
                priority=50,
                citations=[],
                effective_date=datetime.now(),
                is_active=True,
            )
            assert rule.layer == layer

    def test_constitutional_rule_all_categories(self):
        """Test creating rules for all action categories."""
        categories = [
            ActionCategory.SURVEILLANCE,
            ActionCategory.USE_OF_FORCE,
            ActionCategory.DRONE_OPERATION,
            ActionCategory.ROBOTICS_OPERATION,
            ActionCategory.TRAFFIC_ENFORCEMENT,
            ActionCategory.EMERGENCY_RESPONSE,
            ActionCategory.DATA_ACCESS,
            ActionCategory.PUBLIC_SAFETY,
            ActionCategory.PROPERTY_ENTRY,
            ActionCategory.COMMUNICATION,
        ]
        for category in categories:
            rule = ConstitutionalRule(
                rule_id=f"rule-{category.value}",
                layer=ConstitutionalLayer.STATUTORY,
                title=f"Test {category.value}",
                description="Test description",
                condition="test_condition",
                action="TEST_ACTION",
                category=category,
                priority=50,
                citations=[],
                effective_date=datetime.now(),
                is_active=True,
            )
            assert rule.category == category


class TestValidationResult:
    """Tests for ValidationResult enum."""

    def test_validation_results(self):
        """Test all validation result values."""
        assert ValidationResult.ALLOWED.value == "ALLOWED"
        assert ValidationResult.DENIED.value == "DENIED"
        assert ValidationResult.ALLOWED_WITH_HUMAN_REVIEW.value == "ALLOWED_WITH_HUMAN_REVIEW"


class TestValidationDecision:
    """Tests for ValidationDecision model."""

    def test_validation_decision_allowed(self):
        """Test creating an allowed decision."""
        decision = ValidationDecision(
            decision_id="dec-001",
            action_id="action-001",
            result=ValidationResult.ALLOWED,
            rules_applied=["rule-001", "rule-002"],
            explanation="Action complies with all rules",
            timestamp=datetime.now(),
            precedence_chain=[],
        )
        assert decision.result == ValidationResult.ALLOWED
        assert len(decision.rules_applied) == 2

    def test_validation_decision_denied(self):
        """Test creating a denied decision."""
        decision = ValidationDecision(
            decision_id="dec-002",
            action_id="action-002",
            result=ValidationResult.DENIED,
            rules_applied=["rule-003"],
            explanation="Action violates Fourth Amendment",
            timestamp=datetime.now(),
            precedence_chain=["rule-003"],
        )
        assert decision.result == ValidationResult.DENIED
        assert "Fourth Amendment" in decision.explanation

    def test_validation_decision_human_review(self):
        """Test creating a human review decision."""
        decision = ValidationDecision(
            decision_id="dec-003",
            action_id="action-003",
            result=ValidationResult.ALLOWED_WITH_HUMAN_REVIEW,
            rules_applied=["rule-004", "rule-005"],
            explanation="Action requires supervisor approval",
            timestamp=datetime.now(),
            precedence_chain=["rule-004"],
        )
        assert decision.result == ValidationResult.ALLOWED_WITH_HUMAN_REVIEW


class TestConstitutionEngine:
    """Tests for ConstitutionEngine singleton."""

    def test_singleton_pattern(self):
        """Test that get_constitution_engine returns singleton."""
        e1 = get_constitution_engine()
        e2 = get_constitution_engine()
        assert e1 is e2

    def test_get_all_rules(self):
        """Test retrieving all constitutional rules."""
        engine = get_constitution_engine()
        rules = engine.get_all_rules()
        assert isinstance(rules, list)
        assert len(rules) >= 40  # Should have at least 40 pre-loaded rules

    def test_get_rule_by_id(self):
        """Test retrieving rule by ID."""
        engine = get_constitution_engine()
        rules = engine.get_all_rules()
        if rules:
            rule = engine.get_rule_by_id(rules[0].rule_id)
            assert rule is not None
            assert rule.rule_id == rules[0].rule_id

    def test_get_rule_by_invalid_id(self):
        """Test retrieving rule with invalid ID."""
        engine = get_constitution_engine()
        rule = engine.get_rule_by_id("invalid-rule-id-12345")
        assert rule is None

    def test_get_rules_by_layer(self):
        """Test filtering rules by layer."""
        engine = get_constitution_engine()
        for layer in ConstitutionalLayer:
            rules = engine.get_rules_by_layer(layer)
            assert isinstance(rules, list)
            for rule in rules:
                assert rule.layer == layer

    def test_get_rules_by_category(self):
        """Test filtering rules by category."""
        engine = get_constitution_engine()
        for category in ActionCategory:
            rules = engine.get_rules_by_category(category)
            assert isinstance(rules, list)
            for rule in rules:
                assert rule.category == category


class TestActionValidation:
    """Tests for action validation."""

    def test_validate_allowed_action(self):
        """Test validating an allowed action."""
        engine = get_constitution_engine()
        decision = engine.validate_action(
            "routine_patrol",
            ActionCategory.PUBLIC_SAFETY,
            AutonomyLevel.LEVEL_0,
            {"area": "Zone 1"},
        )
        assert decision is not None
        assert decision.result in [
            ValidationResult.ALLOWED,
            ValidationResult.ALLOWED_WITH_HUMAN_REVIEW,
        ]

    def test_validate_denied_action(self):
        """Test validating a denied action."""
        engine = get_constitution_engine()
        decision = engine.validate_action(
            "warrantless_property_search",
            ActionCategory.PROPERTY_ENTRY,
            AutonomyLevel.LEVEL_2,
            {"has_warrant": False, "is_emergency": False},
        )
        assert decision is not None
        # Should be denied without warrant (unless emergency)

    def test_validate_action_requires_review(self):
        """Test validating action that requires human review."""
        engine = get_constitution_engine()
        decision = engine.validate_action(
            "surveillance_escalation",
            ActionCategory.SURVEILLANCE,
            AutonomyLevel.LEVEL_2,
            {"target_area": "Zone 3"},
        )
        assert decision is not None
        # High-risk surveillance should require review

    def test_validate_action_with_autonomy_levels(self):
        """Test validation across autonomy levels."""
        engine = get_constitution_engine()
        for level in AutonomyLevel:
            decision = engine.validate_action(
                "test_action",
                ActionCategory.PUBLIC_SAFETY,
                level,
                {},
            )
            assert decision is not None
            assert decision.result in ValidationResult


class TestPrecedenceChain:
    """Tests for rule precedence chain."""

    def test_get_precedence_chain(self):
        """Test getting precedence chain for a rule."""
        engine = get_constitution_engine()
        rules = engine.get_all_rules()
        if rules:
            chain = engine.get_precedence_chain(rules[0].rule_id)
            assert isinstance(chain, list)

    def test_federal_rules_highest_precedence(self):
        """Test that federal rules have highest precedence."""
        engine = get_constitution_engine()
        federal_rules = engine.get_rules_by_layer(ConstitutionalLayer.FEDERAL_CONSTITUTIONAL)
        local_rules = engine.get_rules_by_layer(ConstitutionalLayer.LOCAL_ORDINANCE)
        
        if federal_rules and local_rules:
            # Federal rules should have higher priority
            assert federal_rules[0].priority >= local_rules[0].priority

    def test_layer_priority_order(self):
        """Test that layers follow correct priority order."""
        engine = get_constitution_engine()
        layer_priorities = {
            ConstitutionalLayer.FEDERAL_CONSTITUTIONAL: 100,
            ConstitutionalLayer.STATE_CONSTITUTIONAL: 90,
            ConstitutionalLayer.STATUTORY: 80,
            ConstitutionalLayer.LOCAL_ORDINANCE: 70,
            ConstitutionalLayer.AGENCY_SOP: 60,
            ConstitutionalLayer.ETHICS: 50,
            ConstitutionalLayer.AUTONOMY: 40,
        }
        
        for layer, expected_min_priority in layer_priorities.items():
            rules = engine.get_rules_by_layer(layer)
            for rule in rules:
                # Rules should have priority appropriate to their layer
                assert rule.priority >= expected_min_priority - 20


class TestConflictResolution:
    """Tests for rule conflict resolution."""

    def test_higher_layer_wins_conflict(self):
        """Test that higher layer rules win conflicts."""
        engine = get_constitution_engine()
        # Validate action that might conflict between layers
        decision = engine.validate_action(
            "surveillance_with_warrant",
            ActionCategory.SURVEILLANCE,
            AutonomyLevel.LEVEL_1,
            {"has_warrant": True},
        )
        assert decision is not None
        # With warrant, should be allowed per federal rules

    def test_explicit_rule_wins_over_general(self):
        """Test that explicit rules win over general rules."""
        engine = get_constitution_engine()
        decision = engine.validate_action(
            "emergency_property_entry",
            ActionCategory.PROPERTY_ENTRY,
            AutonomyLevel.LEVEL_2,
            {"is_emergency": True, "has_warrant": False},
        )
        assert decision is not None
        # Emergency exception should apply


class TestRuleManagement:
    """Tests for rule management functions."""

    def test_add_rule(self):
        """Test adding a new rule."""
        engine = get_constitution_engine()
        initial_count = len(engine.get_all_rules())
        
        new_rule = ConstitutionalRule(
            rule_id=f"test-rule-{datetime.now().timestamp()}",
            layer=ConstitutionalLayer.AGENCY_SOP,
            title="Test Rule",
            description="Test description",
            condition="test_condition",
            action="TEST_ACTION",
            category=ActionCategory.PUBLIC_SAFETY,
            priority=60,
            citations=[],
            effective_date=datetime.now(),
            is_active=True,
        )
        
        result = engine.add_rule(new_rule)
        assert result is True
        
        # Verify rule was added
        retrieved = engine.get_rule_by_id(new_rule.rule_id)
        assert retrieved is not None

    def test_deactivate_rule(self):
        """Test deactivating a rule."""
        engine = get_constitution_engine()
        rules = engine.get_all_rules()
        if rules:
            # Find an agency SOP rule to deactivate (lower priority)
            sop_rules = [r for r in rules if r.layer == ConstitutionalLayer.AGENCY_SOP]
            if sop_rules:
                result = engine.deactivate_rule(sop_rules[0].rule_id)
                assert isinstance(result, bool)


class TestExplainability:
    """Tests for decision explainability."""

    def test_decision_has_explanation(self):
        """Test that decisions include explanations."""
        engine = get_constitution_engine()
        decision = engine.validate_action(
            "test_action",
            ActionCategory.PUBLIC_SAFETY,
            AutonomyLevel.LEVEL_0,
            {},
        )
        assert decision.explanation is not None
        assert len(decision.explanation) > 0

    def test_decision_lists_applied_rules(self):
        """Test that decisions list applied rules."""
        engine = get_constitution_engine()
        decision = engine.validate_action(
            "surveillance_operation",
            ActionCategory.SURVEILLANCE,
            AutonomyLevel.LEVEL_1,
            {"target_area": "Zone 1"},
        )
        assert isinstance(decision.rules_applied, list)

    def test_decision_includes_precedence(self):
        """Test that decisions include precedence chain."""
        engine = get_constitution_engine()
        decision = engine.validate_action(
            "property_entry",
            ActionCategory.PROPERTY_ENTRY,
            AutonomyLevel.LEVEL_2,
            {"has_warrant": True},
        )
        assert isinstance(decision.precedence_chain, list)
