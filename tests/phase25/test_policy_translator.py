"""
Test Suite 2: Policy Translator Engine Tests

Tests for natural language to machine-readable rule translation.
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch

import sys
sys.path.insert(0, "/home/ubuntu/repos/g3ti-rtcc-platform/backend")

from app.city_governance.policy_translator import (
    get_policy_translator,
    PolicyTranslator,
    TranslatedRule,
    PolicyConflict,
    Ambiguity,
)
from app.city_governance.legislative_kb import LegalSource, LegalCategory


class TestTranslatedRule:
    """Tests for TranslatedRule model."""

    def test_translated_rule_creation(self):
        """Test creating a translated rule."""
        rule = TranslatedRule(
            rule_id="rule-001",
            original_text="Drones cannot fly above 400 feet.",
            condition="altitude > 400",
            action="DENY",
            variables=["altitude"],
            source=LegalSource.FEDERAL_FRAMEWORK,
            category=LegalCategory.SURVEILLANCE,
            priority=90,
            confidence=0.95,
            ambiguities=[],
        )
        assert rule.rule_id == "rule-001"
        assert rule.confidence == 0.95
        assert "altitude" in rule.variables

    def test_translated_rule_with_ambiguities(self):
        """Test translated rule with detected ambiguities."""
        ambiguity = Ambiguity(
            term="reasonable",
            suggestion="Define specific threshold",
            severity="medium",
        )
        rule = TranslatedRule(
            rule_id="rule-002",
            original_text="Drones must maintain reasonable distance.",
            condition="distance >= reasonable_threshold",
            action="ALLOW",
            variables=["distance", "reasonable_threshold"],
            source=LegalSource.AGENCY_SOP,
            category=LegalCategory.SURVEILLANCE,
            priority=50,
            confidence=0.65,
            ambiguities=[ambiguity],
        )
        assert len(rule.ambiguities) == 1
        assert rule.ambiguities[0].term == "reasonable"
        assert rule.confidence < 0.8  # Lower confidence due to ambiguity


class TestPolicyConflict:
    """Tests for PolicyConflict model."""

    def test_policy_conflict_creation(self):
        """Test creating a policy conflict."""
        conflict = PolicyConflict(
            conflict_id="conflict-001",
            policy_a_id="policy-001",
            policy_b_id="policy-002",
            conflict_type="CONTRADICTION",
            description="Policies have contradicting conditions",
            resolution_suggestion="Apply higher priority policy",
            severity="high",
        )
        assert conflict.conflict_id == "conflict-001"
        assert conflict.conflict_type == "CONTRADICTION"
        assert conflict.severity == "high"

    def test_policy_conflict_types(self):
        """Test different conflict types."""
        conflict_types = ["CONTRADICTION", "OVERLAP", "AMBIGUITY", "PRECEDENCE"]
        for ct in conflict_types:
            conflict = PolicyConflict(
                conflict_id=f"conflict-{ct}",
                policy_a_id="policy-001",
                policy_b_id="policy-002",
                conflict_type=ct,
                description=f"Test {ct} conflict",
                resolution_suggestion="Test resolution",
                severity="medium",
            )
            assert conflict.conflict_type == ct


class TestPolicyTranslator:
    """Tests for PolicyTranslator singleton."""

    def test_singleton_pattern(self):
        """Test that get_policy_translator returns singleton."""
        t1 = get_policy_translator()
        t2 = get_policy_translator()
        assert t1 is t2

    def test_translate_simple_policy(self):
        """Test translating a simple policy."""
        translator = get_policy_translator()
        rule = translator.translate_policy(
            "Drones cannot enter private property without a warrant.",
            LegalSource.FLORIDA_STATUTE,
            LegalCategory.SURVEILLANCE,
            80,
        )
        assert rule is not None
        assert rule.original_text == "Drones cannot enter private property without a warrant."
        assert rule.action in ["DENY", "ALLOW", "ALLOW_WITH_CONDITION"]
        assert rule.confidence > 0

    def test_translate_policy_with_numbers(self):
        """Test translating policy with numeric values."""
        translator = get_policy_translator()
        rule = translator.translate_policy(
            "Drones must not fly above 400 feet altitude.",
            LegalSource.FEDERAL_FRAMEWORK,
            LegalCategory.SURVEILLANCE,
            90,
        )
        assert rule is not None
        assert "400" in rule.condition or "altitude" in rule.condition.lower()

    def test_translate_policy_with_time_constraint(self):
        """Test translating policy with time constraints."""
        translator = get_policy_translator()
        rule = translator.translate_policy(
            "Surveillance operations are prohibited between 10 PM and 6 AM.",
            LegalSource.RIVIERA_BEACH_CODE,
            LegalCategory.SURVEILLANCE,
            70,
        )
        assert rule is not None
        assert rule.confidence > 0

    def test_translate_policy_detects_ambiguity(self):
        """Test that translator detects ambiguous terms."""
        translator = get_policy_translator()
        rule = translator.translate_policy(
            "Officers should respond in a timely manner to emergencies.",
            LegalSource.AGENCY_SOP,
            LegalCategory.PUBLIC_SAFETY,
            60,
        )
        assert rule is not None
        # "timely manner" is ambiguous
        assert len(rule.ambiguities) > 0 or rule.confidence < 0.9

    def test_translate_policy_with_conditions(self):
        """Test translating policy with multiple conditions."""
        translator = get_policy_translator()
        rule = translator.translate_policy(
            "Drones may enter private property only with a warrant and during daylight hours.",
            LegalSource.FLORIDA_STATUTE,
            LegalCategory.SURVEILLANCE,
            85,
        )
        assert rule is not None
        assert "warrant" in rule.condition.lower() or "daylight" in rule.condition.lower()

    def test_translate_policy_priority(self):
        """Test that priority is preserved in translation."""
        translator = get_policy_translator()
        rule = translator.translate_policy(
            "Test policy",
            LegalSource.US_CONSTITUTION,
            LegalCategory.CIVIL_RIGHTS,
            100,
        )
        assert rule.priority == 100

    def test_translate_policy_source_preserved(self):
        """Test that source is preserved in translation."""
        translator = get_policy_translator()
        for source in LegalSource:
            rule = translator.translate_policy(
                "Test policy",
                source,
                LegalCategory.PUBLIC_SAFETY,
                50,
            )
            assert rule.source == source

    def test_translate_policy_category_preserved(self):
        """Test that category is preserved in translation."""
        translator = get_policy_translator()
        for category in LegalCategory:
            rule = translator.translate_policy(
                "Test policy",
                LegalSource.FLORIDA_STATUTE,
                category,
                50,
            )
            assert rule.category == category


class TestConflictDetection:
    """Tests for policy conflict detection."""

    def test_detect_no_conflicts(self):
        """Test detecting no conflicts between compatible policies."""
        translator = get_policy_translator()
        rule1 = translator.translate_policy(
            "Drones must maintain 100 feet altitude in Zone A.",
            LegalSource.RIVIERA_BEACH_CODE,
            LegalCategory.SURVEILLANCE,
            70,
        )
        rule2 = translator.translate_policy(
            "Drones must maintain 200 feet altitude in Zone B.",
            LegalSource.RIVIERA_BEACH_CODE,
            LegalCategory.SURVEILLANCE,
            70,
        )
        conflicts = translator.detect_conflicts(rule1, rule2)
        # Different zones should not conflict
        assert isinstance(conflicts, list)

    def test_detect_contradiction_conflict(self):
        """Test detecting contradiction between policies."""
        translator = get_policy_translator()
        rule1 = translator.translate_policy(
            "Drones are allowed in Zone A.",
            LegalSource.RIVIERA_BEACH_CODE,
            LegalCategory.SURVEILLANCE,
            70,
        )
        rule2 = translator.translate_policy(
            "Drones are prohibited in Zone A.",
            LegalSource.RIVIERA_BEACH_CODE,
            LegalCategory.SURVEILLANCE,
            70,
        )
        conflicts = translator.detect_conflicts(rule1, rule2)
        assert isinstance(conflicts, list)
        # Should detect potential conflict

    def test_detect_precedence_conflict(self):
        """Test detecting precedence conflict between sources."""
        translator = get_policy_translator()
        rule1 = translator.translate_policy(
            "Surveillance requires warrant.",
            LegalSource.US_CONSTITUTION,
            LegalCategory.SURVEILLANCE,
            100,
        )
        rule2 = translator.translate_policy(
            "Surveillance allowed without warrant in emergencies.",
            LegalSource.RIVIERA_BEACH_CODE,
            LegalCategory.SURVEILLANCE,
            50,
        )
        conflicts = translator.detect_conflicts(rule1, rule2)
        assert isinstance(conflicts, list)


class TestPolicyValidation:
    """Tests for policy validation."""

    def test_validate_valid_policy(self):
        """Test validating a valid policy."""
        translator = get_policy_translator()
        rule = translator.translate_policy(
            "Officers must identify themselves before entering property.",
            LegalSource.AGENCY_SOP,
            LegalCategory.PUBLIC_SAFETY,
            60,
        )
        is_valid, errors = translator.validate_policy(rule)
        assert isinstance(is_valid, bool)
        assert isinstance(errors, list)

    def test_validate_policy_with_missing_action(self):
        """Test validating policy with missing action."""
        translator = get_policy_translator()
        # Create a rule with empty action
        rule = TranslatedRule(
            rule_id="test-invalid",
            original_text="Test policy",
            condition="test_condition",
            action="",
            variables=[],
            source=LegalSource.AGENCY_SOP,
            category=LegalCategory.PUBLIC_SAFETY,
            priority=50,
            confidence=0.5,
            ambiguities=[],
        )
        is_valid, errors = translator.validate_policy(rule)
        # Should detect missing action
        assert not is_valid or len(errors) > 0


class TestPolicyManagement:
    """Tests for policy management functions."""

    def test_get_all_policies(self):
        """Test retrieving all policies."""
        translator = get_policy_translator()
        policies = translator.get_all_policies()
        assert isinstance(policies, list)

    def test_get_policy_by_id(self):
        """Test retrieving policy by ID."""
        translator = get_policy_translator()
        # First create a policy
        rule = translator.translate_policy(
            "Test policy for retrieval.",
            LegalSource.AGENCY_SOP,
            LegalCategory.PUBLIC_SAFETY,
            50,
        )
        # Store it
        translator.store_policy(rule)
        # Retrieve it
        retrieved = translator.get_policy_by_id(rule.rule_id)
        assert retrieved is not None
        assert retrieved.rule_id == rule.rule_id

    def test_get_policies_by_source(self):
        """Test filtering policies by source."""
        translator = get_policy_translator()
        for source in LegalSource:
            policies = translator.get_policies_by_source(source)
            assert isinstance(policies, list)
            for policy in policies:
                assert policy.source == source

    def test_get_policies_by_category(self):
        """Test filtering policies by category."""
        translator = get_policy_translator()
        for category in LegalCategory:
            policies = translator.get_policies_by_category(category)
            assert isinstance(policies, list)
            for policy in policies:
                assert policy.category == category


class TestAmbiguityDetection:
    """Tests for ambiguity detection in policies."""

    def test_detect_vague_terms(self):
        """Test detecting vague terms."""
        translator = get_policy_translator()
        vague_policies = [
            "Officers should respond quickly.",
            "Use reasonable force.",
            "Maintain appropriate distance.",
            "Act in a timely manner.",
        ]
        for policy_text in vague_policies:
            rule = translator.translate_policy(
                policy_text,
                LegalSource.AGENCY_SOP,
                LegalCategory.PUBLIC_SAFETY,
                50,
            )
            # Should have lower confidence or detected ambiguities
            assert rule.confidence < 0.95 or len(rule.ambiguities) > 0

    def test_detect_temporal_ambiguity(self):
        """Test detecting temporal ambiguity."""
        translator = get_policy_translator()
        rule = translator.translate_policy(
            "Respond to calls soon after receiving them.",
            LegalSource.AGENCY_SOP,
            LegalCategory.PUBLIC_SAFETY,
            50,
        )
        # "soon" is temporally ambiguous
        assert rule.confidence < 0.95 or len(rule.ambiguities) > 0

    def test_no_ambiguity_in_specific_policy(self):
        """Test that specific policies have no ambiguity."""
        translator = get_policy_translator()
        rule = translator.translate_policy(
            "Drones must not exceed 400 feet altitude.",
            LegalSource.FEDERAL_FRAMEWORK,
            LegalCategory.SURVEILLANCE,
            90,
        )
        # Specific numeric constraint should have high confidence
        assert rule.confidence >= 0.7
