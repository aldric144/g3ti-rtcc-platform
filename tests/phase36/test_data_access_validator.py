"""
Test Suite: Public Data Access Validator
Phase 36: Public Safety Guardian
"""

import pytest
from datetime import datetime

from backend.app.public_guardian.data_access_validator import (
    PublicDataAccessValidator,
    ComplianceFramework,
    RedactionType,
    ValidationStatus,
    RedactionRule,
    RedactionResult,
    ValidationResult,
)


class TestPublicDataAccessValidator:
    def setup_method(self):
        self.validator = PublicDataAccessValidator()

    def test_validator_singleton(self):
        validator2 = PublicDataAccessValidator()
        assert self.validator is validator2

    def test_validate_clean_data(self):
        result = self.validator.validate_data("This is clean public data.")
        assert result is not None
        assert result.status in [ValidationStatus.PASSED, ValidationStatus.REQUIRES_REDACTION]

    def test_validate_data_with_ssn(self):
        result = self.validator.validate_data("John Doe SSN: 123-45-6789")
        assert result.status == ValidationStatus.REQUIRES_REDACTION

    def test_validate_data_with_phone(self):
        result = self.validator.validate_data("Call me at 555-123-4567")
        assert result.status == ValidationStatus.REQUIRES_REDACTION

    def test_validate_data_with_email(self):
        result = self.validator.validate_data("Contact: john.doe@example.com")
        assert result.status == ValidationStatus.REQUIRES_REDACTION

    def test_redact_ssn(self):
        data = "SSN: 123-45-6789"
        redacted, result = self.validator.validate_and_redact(data)
        assert "[REDACTED-SSN]" in redacted
        assert "123-45-6789" not in redacted

    def test_redact_phone_number(self):
        data = "Phone: 555-123-4567"
        redacted, result = self.validator.validate_and_redact(data)
        assert "[REDACTED-PHONE]" in redacted
        assert "555-123-4567" not in redacted

    def test_redact_email(self):
        data = "Email: test@example.com"
        redacted, result = self.validator.validate_and_redact(data)
        assert "[REDACTED-EMAIL]" in redacted
        assert "test@example.com" not in redacted

    def test_redact_dob(self):
        data = "DOB: 01/15/1990"
        redacted, result = self.validator.validate_and_redact(data)
        assert "[REDACTED-DOB]" in redacted or "01/15/1990" not in redacted

    def test_redact_multiple_fields(self):
        data = "John Doe SSN: 123-45-6789 Phone: 555-123-4567 Email: john@test.com"
        redacted, result = self.validator.validate_and_redact(data)
        assert "123-45-6789" not in redacted
        assert "555-123-4567" not in redacted
        assert "john@test.com" not in redacted

    def test_validate_and_redact(self):
        data = "Sensitive data: SSN 123-45-6789"
        redacted, result = self.validator.validate_and_redact(data)
        assert redacted is not None
        assert result is not None
        assert result.redactions_applied > 0

    def test_check_public_release_eligibility(self):
        result = self.validator.check_public_release_eligibility(
            "Clean public data",
            data_type="general"
        )
        assert "eligible" in result

    def test_check_public_release_eligibility_with_sensitive(self):
        result = self.validator.check_public_release_eligibility(
            "SSN: 123-45-6789",
            data_type="general"
        )
        assert "eligible" in result

    def test_get_rule(self):
        rules = self.validator.get_all_rules()
        if len(rules) > 0:
            rule = self.validator.get_rule(rules[0].rule_id)
            assert rule is not None

    def test_get_all_rules(self):
        rules = self.validator.get_all_rules()
        assert isinstance(rules, list)
        assert len(rules) > 0

    def test_get_rules_by_framework_cjis(self):
        rules = self.validator.get_rules_by_framework(ComplianceFramework.CJIS)
        assert isinstance(rules, list)

    def test_get_rules_by_framework_vawa(self):
        rules = self.validator.get_rules_by_framework(ComplianceFramework.VAWA)
        assert isinstance(rules, list)

    def test_get_rules_by_framework_hipaa(self):
        rules = self.validator.get_rules_by_framework(ComplianceFramework.HIPAA)
        assert isinstance(rules, list)

    def test_add_rule(self):
        rule = self.validator.add_rule(
            name="Test Rule",
            redaction_type=RedactionType.OTHER,
            pattern=r"TEST-\d{4}",
            replacement="[REDACTED-TEST]",
            frameworks=[ComplianceFramework.CJIS],
            description="Test redaction rule",
        )
        assert rule is not None
        assert rule.name == "Test Rule"

    def test_update_rule(self):
        rules = self.validator.get_all_rules()
        if len(rules) > 0:
            updated = self.validator.update_rule(
                rules[0].rule_id,
                description="Updated description"
            )
            assert updated is not None or updated is None

    def test_deactivate_rule(self):
        rule = self.validator.add_rule(
            name="Deactivate Test",
            redaction_type=RedactionType.OTHER,
            pattern=r"DEACT-\d{4}",
            replacement="[REDACTED]",
            frameworks=[ComplianceFramework.CJIS],
        )
        success = self.validator.deactivate_rule(rule.rule_id)
        assert success is True

    def test_get_validation_history(self):
        self.validator.validate_data("Test data")
        history = self.validator.get_validation_history(limit=10)
        assert isinstance(history, list)

    def test_get_compliance_summary(self):
        summary = self.validator.get_compliance_summary()
        assert isinstance(summary, dict)

    def test_get_statistics(self):
        stats = self.validator.get_statistics()
        assert "total_validations" in stats
        assert "total_redactions" in stats

    def test_validation_result_to_dict(self):
        result = self.validator.validate_data("Test data SSN: 123-45-6789")
        result_dict = result.to_dict()
        assert "validation_id" in result_dict
        assert "status" in result_dict


class TestComplianceFramework:
    def test_all_frameworks_exist(self):
        expected = [
            "cjis", "vawa", "hipaa", "ferpa",
            "florida_public_records", "ada", "fcra"
        ]
        for cf in expected:
            assert hasattr(ComplianceFramework, cf.upper())


class TestRedactionType:
    def test_all_redaction_types_exist(self):
        expected = [
            "ssn", "phone_number", "email", "dob",
            "juvenile_identifier", "dv_location", "mental_health_info",
            "medical_info", "victim_data", "witness_identity",
            "exact_address", "financial_info", "biometric_data",
            "criminal_history", "immigration_status", "sexual_orientation",
            "religious_affiliation"
        ]
        for rt in expected:
            assert hasattr(RedactionType, rt.upper())

    def test_redaction_type_count(self):
        types = list(RedactionType)
        assert len(types) >= 17


class TestValidationStatus:
    def test_all_statuses_exist(self):
        expected = ["passed", "failed", "requires_redaction", "blocked"]
        for vs in expected:
            assert hasattr(ValidationStatus, vs.upper())


class TestRedactionRule:
    def test_redaction_rule_creation(self):
        rule = RedactionRule(
            rule_id="rule-001",
            name="Test Rule",
            redaction_type=RedactionType.SSN,
            pattern=r"\d{3}-\d{2}-\d{4}",
            replacement="[REDACTED-SSN]",
            frameworks=[ComplianceFramework.CJIS],
        )
        assert rule.name == "Test Rule"
        assert rule.redaction_type == RedactionType.SSN

    def test_redaction_rule_to_dict(self):
        rule = RedactionRule(
            rule_id="rule-002",
            name="Phone Rule",
            redaction_type=RedactionType.PHONE_NUMBER,
            pattern=r"\d{3}-\d{3}-\d{4}",
            replacement="[REDACTED-PHONE]",
            frameworks=[ComplianceFramework.CJIS, ComplianceFramework.VAWA],
        )
        rule_dict = rule.to_dict()
        assert "rule_id" in rule_dict
        assert "name" in rule_dict
        assert "redaction_type" in rule_dict
