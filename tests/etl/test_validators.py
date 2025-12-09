"""
Tests for ETL Validators module.
"""

import pytest
from datetime import datetime, timedelta

import sys
sys.path.insert(0, "/home/ubuntu/repos/g3ti-rtcc-platform/backend")

from app.etl.validators import (
    DataValidator,
    IncidentValidator,
    ValidationRule,
    ValidationResult,
    ValidationIssue,
    ValidationSeverity,
)


class TestValidationRule:
    """Tests for ValidationRule model."""

    def test_create_rule(self):
        """Test creating a validation rule."""
        rule = ValidationRule(
            name="required_field",
            description="Field must be present",
            field="timestamp",
            severity=ValidationSeverity.ERROR,
        )

        assert rule.name == "required_field"
        assert rule.field == "timestamp"
        assert rule.severity == ValidationSeverity.ERROR
        assert rule.enabled is True


class TestValidationIssue:
    """Tests for ValidationIssue model."""

    def test_create_issue(self):
        """Test creating a validation issue."""
        issue = ValidationIssue(
            rule_name="required_field",
            field="timestamp",
            message="Required field 'timestamp' is missing",
            severity=ValidationSeverity.ERROR,
        )

        assert issue.rule_name == "required_field"
        assert issue.severity == ValidationSeverity.ERROR


class TestValidationResult:
    """Tests for ValidationResult model."""

    def test_valid_result(self):
        """Test a valid result."""
        result = ValidationResult(
            is_valid=True,
            record_id="REC-001",
            issues=[],
            warnings=0,
            errors=0,
        )

        assert result.is_valid is True
        assert result.has_errors is False
        assert result.has_warnings is False

    def test_invalid_result(self):
        """Test an invalid result with errors."""
        result = ValidationResult(
            is_valid=False,
            record_id="REC-002",
            issues=[
                ValidationIssue(
                    rule_name="required_field",
                    field="timestamp",
                    message="Missing timestamp",
                    severity=ValidationSeverity.ERROR,
                )
            ],
            warnings=0,
            errors=1,
        )

        assert result.is_valid is False
        assert result.has_errors is True
        assert len(result.issues) == 1


class TestDataValidator:
    """Tests for DataValidator class."""

    def test_validator_initialization(self):
        """Test validator initialization."""
        validator = DataValidator()

        assert validator.strict_mode is False

    def test_validate_valid_record(self):
        """Test validating a valid record."""
        validator = DataValidator()

        record = {
            "source_system": "CAD",
            "source_id": "CAD-12345",
            "timestamp": datetime.utcnow(),
            "incident_number": "2024-001234",
            "crime_type": "theft",
            "latitude": 33.749,
            "longitude": -84.388,
            "jurisdiction": "ATL",
        }

        result = validator.validate(record)

        assert result.is_valid is True
        assert result.errors == 0

    def test_validate_missing_required_field(self):
        """Test validating record with missing required field."""
        validator = DataValidator()

        record = {
            "source_system": "CAD",
            # Missing source_id
            "timestamp": datetime.utcnow(),
        }

        result = validator.validate(record)

        assert result.is_valid is False
        assert result.errors > 0
        assert any(i.field == "source_id" for i in result.issues)

    def test_validate_invalid_latitude(self):
        """Test validating record with invalid latitude."""
        validator = DataValidator()

        record = {
            "source_system": "CAD",
            "source_id": "CAD-12345",
            "timestamp": datetime.utcnow(),
            "latitude": 100.0,  # Invalid
            "longitude": -84.388,
        }

        result = validator.validate(record)

        assert result.is_valid is False
        assert any(i.field == "latitude" for i in result.issues)

    def test_validate_invalid_longitude(self):
        """Test validating record with invalid longitude."""
        validator = DataValidator()

        record = {
            "source_system": "CAD",
            "source_id": "CAD-12345",
            "timestamp": datetime.utcnow(),
            "latitude": 33.749,
            "longitude": -200.0,  # Invalid
        }

        result = validator.validate(record)

        assert result.is_valid is False
        assert any(i.field == "longitude" for i in result.issues)

    def test_validate_future_timestamp(self):
        """Test validating record with future timestamp."""
        validator = DataValidator()

        record = {
            "source_system": "CAD",
            "source_id": "CAD-12345",
            "timestamp": datetime.utcnow() + timedelta(days=30),  # Future
            "latitude": 33.749,
            "longitude": -84.388,
        }

        result = validator.validate(record)

        assert result.is_valid is False
        assert any(i.field == "timestamp" for i in result.issues)

    def test_validate_batch(self):
        """Test batch validation."""
        validator = DataValidator()

        records = [
            {
                "source_system": "CAD",
                "source_id": "CAD-001",
                "timestamp": datetime.utcnow(),
            },
            {
                "source_system": "CAD",
                # Missing source_id - invalid
                "timestamp": datetime.utcnow(),
            },
            {
                "source_system": "CAD",
                "source_id": "CAD-003",
                "timestamp": datetime.utcnow(),
            },
        ]

        valid_records, results = validator.validate_batch(records)

        assert len(valid_records) == 2
        assert len(results) == 3
        assert results[1].is_valid is False

    def test_strict_mode(self):
        """Test strict mode treats warnings as errors."""
        validator = DataValidator(strict_mode=True)

        record = {
            "source_system": "CAD",
            "source_id": "CAD-12345",
            "timestamp": datetime.utcnow(),
            # Missing recommended fields will generate warnings
        }

        result = validator.validate(record)

        # In strict mode, warnings make the record invalid
        if result.warnings > 0:
            assert result.is_valid is False

    def test_custom_validator(self):
        """Test adding custom validator."""
        validator = DataValidator()

        def custom_check(record):
            if record.get("crime_type") == "invalid":
                return ValidationIssue(
                    rule_name="custom_crime_type",
                    field="crime_type",
                    message="Invalid crime type",
                    severity=ValidationSeverity.ERROR,
                )
            return None

        validator.add_custom_validator("custom_crime_type", custom_check)

        record = {
            "source_system": "CAD",
            "source_id": "CAD-12345",
            "timestamp": datetime.utcnow(),
            "crime_type": "invalid",
        }

        result = validator.validate(record)

        assert any(i.rule_name == "custom_crime_type" for i in result.issues)

    def test_validation_summary(self):
        """Test getting validation summary."""
        validator = DataValidator()

        results = [
            ValidationResult(is_valid=True, errors=0, warnings=0),
            ValidationResult(is_valid=False, errors=1, warnings=0),
            ValidationResult(is_valid=True, errors=0, warnings=2),
        ]

        summary = validator.get_validation_summary(results)

        assert summary["total_records"] == 3
        assert summary["valid_records"] == 2
        assert summary["invalid_records"] == 1
        assert summary["total_errors"] == 1
        assert summary["total_warnings"] == 2


class TestIncidentValidator:
    """Tests for IncidentValidator class."""

    def test_incident_validator_initialization(self):
        """Test incident validator initialization."""
        validator = IncidentValidator()

        assert validator.strict_mode is False

    def test_validate_valid_incident(self):
        """Test validating a valid incident."""
        validator = IncidentValidator()

        record = {
            "source_system": "CAD",
            "source_id": "CAD-12345",
            "timestamp": datetime.utcnow(),
            "crime_category": "property",
            "severity": "medium",
        }

        result = validator.validate(record)

        assert result.errors == 0

    def test_validate_invalid_crime_category(self):
        """Test validating invalid crime category."""
        validator = IncidentValidator()

        record = {
            "source_system": "CAD",
            "source_id": "CAD-12345",
            "timestamp": datetime.utcnow(),
            "crime_category": "invalid_category",
        }

        result = validator.validate(record)

        assert any(i.rule_name == "crime_category" for i in result.issues)

    def test_validate_invalid_severity(self):
        """Test validating invalid severity."""
        validator = IncidentValidator()

        record = {
            "source_system": "CAD",
            "source_id": "CAD-12345",
            "timestamp": datetime.utcnow(),
            "severity": "invalid_severity",
        }

        result = validator.validate(record)

        assert any(i.rule_name == "severity" for i in result.issues)

    def test_validate_unknown_source_system(self):
        """Test validating unknown source system."""
        validator = IncidentValidator()

        record = {
            "source_system": "UNKNOWN_SYSTEM",
            "source_id": "UNK-12345",
            "timestamp": datetime.utcnow(),
        }

        result = validator.validate(record)

        # Unknown source should generate info-level issue
        assert any(i.rule_name == "source_system" for i in result.issues)
