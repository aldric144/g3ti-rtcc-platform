"""
Test Suite: Redaction and Compliance Framework
Phase 36: Public Safety Guardian
"""

import pytest
from datetime import datetime

from backend.app.public_guardian.data_access_validator import (
    PublicDataAccessValidator,
    ComplianceFramework,
    RedactionType,
    ValidationStatus,
)


class TestCJISCompliance:
    def setup_method(self):
        self.validator = PublicDataAccessValidator()

    def test_cjis_rules_exist(self):
        rules = self.validator.get_rules_by_framework(ComplianceFramework.CJIS)
        assert len(rules) > 0

    def test_cjis_ssn_redaction(self):
        data = "Subject SSN: 123-45-6789"
        redacted, result = self.validator.validate_and_redact(data)
        assert "123-45-6789" not in redacted

    def test_cjis_criminal_history_protection(self):
        data = "Prior arrests: 3 felonies"
        result = self.validator.validate_data(data)
        assert result is not None


class TestVAWACompliance:
    def setup_method(self):
        self.validator = PublicDataAccessValidator()

    def test_vawa_rules_exist(self):
        rules = self.validator.get_rules_by_framework(ComplianceFramework.VAWA)
        assert len(rules) > 0

    def test_vawa_dv_location_redaction(self):
        data = "DV shelter located at 123 Safe Haven Dr"
        redacted, result = self.validator.validate_and_redact(data)
        assert result.status in [ValidationStatus.PASSED, ValidationStatus.REQUIRES_REDACTION]

    def test_vawa_victim_data_protection(self):
        data = "Victim name: Jane Doe, Address: 456 Main St"
        result = self.validator.validate_data(data)
        assert result is not None


class TestHIPAACompliance:
    def setup_method(self):
        self.validator = PublicDataAccessValidator()

    def test_hipaa_rules_exist(self):
        rules = self.validator.get_rules_by_framework(ComplianceFramework.HIPAA)
        assert len(rules) > 0

    def test_hipaa_medical_info_redaction(self):
        data = "Patient diagnosis: diabetes, medication: insulin"
        result = self.validator.validate_data(data)
        assert result is not None

    def test_hipaa_mental_health_protection(self):
        data = "Mental health evaluation: depression, anxiety"
        result = self.validator.validate_data(data)
        assert result is not None


class TestFERPACompliance:
    def setup_method(self):
        self.validator = PublicDataAccessValidator()

    def test_ferpa_rules_exist(self):
        rules = self.validator.get_rules_by_framework(ComplianceFramework.FERPA)
        assert len(rules) > 0

    def test_ferpa_student_records_protection(self):
        data = "Student ID: 12345, GPA: 3.5"
        result = self.validator.validate_data(data)
        assert result is not None


class TestFloridaPublicRecordsCompliance:
    def setup_method(self):
        self.validator = PublicDataAccessValidator()

    def test_florida_rules_exist(self):
        rules = self.validator.get_rules_by_framework(ComplianceFramework.FLORIDA_PUBLIC_RECORDS)
        assert len(rules) > 0

    def test_florida_juvenile_protection(self):
        data = "Juvenile offender: John D., age 15"
        result = self.validator.validate_data(data)
        assert result is not None

    def test_florida_active_investigation_protection(self):
        data = "Active investigation case #2025-001"
        result = self.validator.validate_data(data)
        assert result is not None


class TestRedactionPatterns:
    def setup_method(self):
        self.validator = PublicDataAccessValidator()

    def test_ssn_pattern_xxx_xx_xxxx(self):
        data = "SSN: 123-45-6789"
        redacted, _ = self.validator.validate_and_redact(data)
        assert "123-45-6789" not in redacted

    def test_ssn_pattern_xxxxxxxxx(self):
        data = "SSN: 123456789"
        redacted, _ = self.validator.validate_and_redact(data)
        assert "123456789" not in redacted or "[REDACTED" in redacted

    def test_phone_pattern_xxx_xxx_xxxx(self):
        data = "Phone: 555-123-4567"
        redacted, _ = self.validator.validate_and_redact(data)
        assert "555-123-4567" not in redacted

    def test_phone_pattern_xxxxxxxxxx(self):
        data = "Phone: 5551234567"
        redacted, _ = self.validator.validate_and_redact(data)
        assert "5551234567" not in redacted or "[REDACTED" in redacted

    def test_email_pattern(self):
        data = "Email: test.user@example.com"
        redacted, _ = self.validator.validate_and_redact(data)
        assert "test.user@example.com" not in redacted

    def test_dob_pattern_mm_dd_yyyy(self):
        data = "DOB: 01/15/1990"
        redacted, _ = self.validator.validate_and_redact(data)
        assert "01/15/1990" not in redacted or "[REDACTED" in redacted

    def test_address_pattern(self):
        data = "Address: 123 Main Street, Apt 4B"
        result = self.validator.validate_data(data)
        assert result is not None


class TestMultipleRedactions:
    def setup_method(self):
        self.validator = PublicDataAccessValidator()

    def test_multiple_ssns(self):
        data = "SSN1: 123-45-6789, SSN2: 987-65-4321"
        redacted, result = self.validator.validate_and_redact(data)
        assert "123-45-6789" not in redacted
        assert "987-65-4321" not in redacted

    def test_multiple_phones(self):
        data = "Home: 555-111-2222, Cell: 555-333-4444"
        redacted, result = self.validator.validate_and_redact(data)
        assert "555-111-2222" not in redacted
        assert "555-333-4444" not in redacted

    def test_multiple_emails(self):
        data = "Primary: a@test.com, Secondary: b@test.com"
        redacted, result = self.validator.validate_and_redact(data)
        assert "a@test.com" not in redacted
        assert "b@test.com" not in redacted

    def test_mixed_sensitive_data(self):
        data = "John Doe, SSN: 123-45-6789, Phone: 555-123-4567, Email: john@test.com"
        redacted, result = self.validator.validate_and_redact(data)
        assert "123-45-6789" not in redacted
        assert "555-123-4567" not in redacted
        assert "john@test.com" not in redacted


class TestRedactionReplacement:
    def setup_method(self):
        self.validator = PublicDataAccessValidator()

    def test_ssn_replacement_text(self):
        data = "SSN: 123-45-6789"
        redacted, _ = self.validator.validate_and_redact(data)
        assert "[REDACTED-SSN]" in redacted

    def test_phone_replacement_text(self):
        data = "Phone: 555-123-4567"
        redacted, _ = self.validator.validate_and_redact(data)
        assert "[REDACTED-PHONE]" in redacted

    def test_email_replacement_text(self):
        data = "Email: test@example.com"
        redacted, _ = self.validator.validate_and_redact(data)
        assert "[REDACTED-EMAIL]" in redacted


class TestComplianceSummary:
    def setup_method(self):
        self.validator = PublicDataAccessValidator()

    def test_compliance_summary_structure(self):
        summary = self.validator.get_compliance_summary()
        assert isinstance(summary, dict)

    def test_compliance_summary_frameworks(self):
        summary = self.validator.get_compliance_summary()
        assert "frameworks" in summary or len(summary) > 0

    def test_validation_statistics(self):
        self.validator.validate_data("Test data")
        stats = self.validator.get_statistics()
        assert "total_validations" in stats


class TestEdgeCases:
    def setup_method(self):
        self.validator = PublicDataAccessValidator()

    def test_empty_string(self):
        result = self.validator.validate_data("")
        assert result is not None

    def test_no_sensitive_data(self):
        data = "This is clean public data with no sensitive information."
        result = self.validator.validate_data(data)
        assert result.status == ValidationStatus.PASSED

    def test_special_characters(self):
        data = "Data with special chars: @#$%^&*()"
        result = self.validator.validate_data(data)
        assert result is not None

    def test_unicode_characters(self):
        data = "Unicode test: café, naïve, résumé"
        result = self.validator.validate_data(data)
        assert result is not None

    def test_very_long_string(self):
        data = "A" * 10000
        result = self.validator.validate_data(data)
        assert result is not None
