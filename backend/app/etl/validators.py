"""
Data Validators for ETL Pipelines.

This module provides data validation utilities including:
- Schema validation
- Data quality checks
- Business rule validation
- Anomaly detection
"""

import logging
import re
from datetime import datetime
from enum import Enum
from typing import Any, Callable

from pydantic import BaseModel, ConfigDict, Field

logger = logging.getLogger(__name__)


class ValidationSeverity(str, Enum):
    """Validation issue severity levels."""

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class ValidationRule(BaseModel):
    """Definition of a validation rule."""

    model_config = ConfigDict(from_attributes=True)

    name: str = Field(description="Rule name")
    description: str = Field(description="Rule description")
    field: str | None = Field(default=None, description="Field to validate")
    severity: ValidationSeverity = Field(
        default=ValidationSeverity.ERROR, description="Issue severity"
    )
    enabled: bool = Field(default=True, description="Whether rule is enabled")


class ValidationIssue(BaseModel):
    """A validation issue found in data."""

    model_config = ConfigDict(from_attributes=True)

    rule_name: str = Field(description="Rule that was violated")
    field: str | None = Field(default=None, description="Field with issue")
    message: str = Field(description="Issue description")
    severity: ValidationSeverity = Field(description="Issue severity")
    value: Any = Field(default=None, description="Problematic value")


class ValidationResult(BaseModel):
    """Result of validating a record."""

    model_config = ConfigDict(from_attributes=True)

    is_valid: bool = Field(description="Whether record passed validation")
    record_id: str | None = Field(default=None, description="Record identifier")
    issues: list[ValidationIssue] = Field(default_factory=list, description="Validation issues")
    warnings: int = Field(default=0, description="Warning count")
    errors: int = Field(default=0, description="Error count")
    validated_at: datetime = Field(default_factory=datetime.utcnow)

    @property
    def has_errors(self) -> bool:
        """Check if there are any errors."""
        return self.errors > 0

    @property
    def has_warnings(self) -> bool:
        """Check if there are any warnings."""
        return self.warnings > 0


class DataValidator:
    """
    Data validator for ETL pipelines.

    Provides comprehensive validation of incident records including:
    - Required field validation
    - Data type validation
    - Range and format validation
    - Business rule validation
    """

    # Required fields for incident records
    REQUIRED_FIELDS = [
        "source_system",
        "source_id",
        "timestamp",
    ]

    # Optional but recommended fields
    RECOMMENDED_FIELDS = [
        "incident_number",
        "crime_type",
        "latitude",
        "longitude",
        "jurisdiction",
    ]

    # Field type specifications
    FIELD_TYPES = {
        "latitude": (float, int),
        "longitude": (float, int),
        "timestamp": (datetime, str),
        "reported_at": (datetime, str),
        "suspect_count": (int,),
        "victim_count": (int,),
        "arrest_made": (bool,),
        "weapon_involved": (bool,),
        "domestic_violence": (bool,),
        "gang_related": (bool,),
    }

    # Field range specifications
    FIELD_RANGES = {
        "latitude": (-90, 90),
        "longitude": (-180, 180),
        "suspect_count": (0, 100),
        "victim_count": (0, 1000),
    }

    def __init__(
        self,
        custom_rules: list[ValidationRule] | None = None,
        strict_mode: bool = False,
    ):
        """
        Initialize the validator.

        Args:
            custom_rules: Additional custom validation rules
            strict_mode: If True, warnings are treated as errors
        """
        self.custom_rules = custom_rules or []
        self.strict_mode = strict_mode
        self._custom_validators: dict[str, Callable[[Any], bool]] = {}

        logger.info(f"DataValidator initialized (strict_mode={strict_mode})")

    def add_custom_validator(
        self,
        name: str,
        validator: Callable[[dict[str, Any]], ValidationIssue | None],
    ) -> None:
        """
        Add a custom validation function.

        Args:
            name: Validator name
            validator: Function that returns ValidationIssue if invalid, None if valid
        """
        self._custom_validators[name] = validator
        logger.info(f"Added custom validator: {name}")

    def validate(self, record: dict[str, Any]) -> ValidationResult:
        """
        Validate a record.

        Args:
            record: Record to validate

        Returns:
            Validation result
        """
        issues: list[ValidationIssue] = []
        record_id = record.get("source_id", record.get("id", "unknown"))

        # Required field validation
        issues.extend(self._validate_required_fields(record))

        # Recommended field validation
        issues.extend(self._validate_recommended_fields(record))

        # Type validation
        issues.extend(self._validate_types(record))

        # Range validation
        issues.extend(self._validate_ranges(record))

        # Format validation
        issues.extend(self._validate_formats(record))

        # Business rule validation
        issues.extend(self._validate_business_rules(record))

        # Custom validators
        for name, validator in self._custom_validators.items():
            try:
                issue = validator(record)
                if issue:
                    issues.append(issue)
            except Exception as e:
                logger.warning(f"Custom validator '{name}' failed: {e}")

        # Count errors and warnings
        errors = sum(1 for i in issues if i.severity == ValidationSeverity.ERROR)
        warnings = sum(1 for i in issues if i.severity == ValidationSeverity.WARNING)

        # Determine validity
        is_valid = errors == 0
        if self.strict_mode:
            is_valid = is_valid and warnings == 0

        return ValidationResult(
            is_valid=is_valid,
            record_id=record_id,
            issues=issues,
            warnings=warnings,
            errors=errors,
        )

    def validate_batch(
        self,
        records: list[dict[str, Any]],
    ) -> tuple[list[dict[str, Any]], list[ValidationResult]]:
        """
        Validate a batch of records.

        Args:
            records: Records to validate

        Returns:
            Tuple of (valid records, all validation results)
        """
        valid_records = []
        results = []

        for record in records:
            result = self.validate(record)
            results.append(result)

            if result.is_valid:
                valid_records.append(record)

        logger.info(
            f"Batch validation: {len(valid_records)}/{len(records)} valid"
        )

        return valid_records, results

    def _validate_required_fields(
        self, record: dict[str, Any]
    ) -> list[ValidationIssue]:
        """Validate required fields are present."""
        issues = []

        for field in self.REQUIRED_FIELDS:
            if field not in record or record[field] is None:
                issues.append(
                    ValidationIssue(
                        rule_name="required_field",
                        field=field,
                        message=f"Required field '{field}' is missing",
                        severity=ValidationSeverity.ERROR,
                    )
                )
            elif isinstance(record[field], str) and not record[field].strip():
                issues.append(
                    ValidationIssue(
                        rule_name="required_field",
                        field=field,
                        message=f"Required field '{field}' is empty",
                        severity=ValidationSeverity.ERROR,
                    )
                )

        return issues

    def _validate_recommended_fields(
        self, record: dict[str, Any]
    ) -> list[ValidationIssue]:
        """Validate recommended fields are present."""
        issues = []

        for field in self.RECOMMENDED_FIELDS:
            if field not in record or record[field] is None:
                issues.append(
                    ValidationIssue(
                        rule_name="recommended_field",
                        field=field,
                        message=f"Recommended field '{field}' is missing",
                        severity=ValidationSeverity.WARNING,
                    )
                )

        return issues

    def _validate_types(self, record: dict[str, Any]) -> list[ValidationIssue]:
        """Validate field types."""
        issues = []

        for field, expected_types in self.FIELD_TYPES.items():
            if field in record and record[field] is not None:
                value = record[field]
                if not isinstance(value, expected_types):
                    issues.append(
                        ValidationIssue(
                            rule_name="type_validation",
                            field=field,
                            message=(
                                f"Field '{field}' has invalid type. "
                                f"Expected {expected_types}, got {type(value).__name__}"
                            ),
                            severity=ValidationSeverity.ERROR,
                            value=str(value)[:100],
                        )
                    )

        return issues

    def _validate_ranges(self, record: dict[str, Any]) -> list[ValidationIssue]:
        """Validate field value ranges."""
        issues = []

        for field, (min_val, max_val) in self.FIELD_RANGES.items():
            if field in record and record[field] is not None:
                value = record[field]
                try:
                    num_value = float(value)
                    if num_value < min_val or num_value > max_val:
                        issues.append(
                            ValidationIssue(
                                rule_name="range_validation",
                                field=field,
                                message=(
                                    f"Field '{field}' value {num_value} is out of range "
                                    f"[{min_val}, {max_val}]"
                                ),
                                severity=ValidationSeverity.ERROR,
                                value=num_value,
                            )
                        )
                except (ValueError, TypeError):
                    pass  # Type validation will catch this

        return issues

    def _validate_formats(self, record: dict[str, Any]) -> list[ValidationIssue]:
        """Validate field formats."""
        issues = []

        # Validate timestamp format
        for field in ["timestamp", "reported_at"]:
            if field in record and record[field] is not None:
                value = record[field]
                if isinstance(value, str):
                    if not self._is_valid_timestamp(value):
                        issues.append(
                            ValidationIssue(
                                rule_name="format_validation",
                                field=field,
                                message=f"Field '{field}' has invalid timestamp format",
                                severity=ValidationSeverity.ERROR,
                                value=value[:50] if len(value) > 50 else value,
                            )
                        )

        # Validate incident number format (if present)
        if "incident_number" in record and record["incident_number"]:
            value = record["incident_number"]
            if isinstance(value, str) and len(value) < 3:
                issues.append(
                    ValidationIssue(
                        rule_name="format_validation",
                        field="incident_number",
                        message="Incident number is too short",
                        severity=ValidationSeverity.WARNING,
                        value=value,
                    )
                )

        return issues

    def _validate_business_rules(
        self, record: dict[str, Any]
    ) -> list[ValidationIssue]:
        """Validate business rules."""
        issues = []

        # Rule: If arrest_made is True, there should be suspects
        if record.get("arrest_made") and record.get("suspect_count", 0) == 0:
            issues.append(
                ValidationIssue(
                    rule_name="business_rule",
                    field="suspect_count",
                    message="Arrest made but no suspects recorded",
                    severity=ValidationSeverity.WARNING,
                )
            )

        # Rule: Timestamp should not be in the future
        timestamp = record.get("timestamp")
        if timestamp:
            if isinstance(timestamp, datetime):
                if timestamp > datetime.utcnow():
                    issues.append(
                        ValidationIssue(
                            rule_name="business_rule",
                            field="timestamp",
                            message="Timestamp is in the future",
                            severity=ValidationSeverity.ERROR,
                            value=timestamp.isoformat(),
                        )
                    )

        # Rule: Location should be valid if provided
        lat = record.get("latitude", 0)
        lon = record.get("longitude", 0)
        if lat == 0 and lon == 0:
            issues.append(
                ValidationIssue(
                    rule_name="business_rule",
                    field="location",
                    message="Location coordinates are (0, 0) - likely invalid",
                    severity=ValidationSeverity.WARNING,
                )
            )

        # Rule: Weapon type should be specified if weapon_involved is True
        if record.get("weapon_involved") and not record.get("weapon_type"):
            issues.append(
                ValidationIssue(
                    rule_name="business_rule",
                    field="weapon_type",
                    message="Weapon involved but weapon type not specified",
                    severity=ValidationSeverity.INFO,
                )
            )

        return issues

    def _is_valid_timestamp(self, value: str) -> bool:
        """Check if string is a valid timestamp."""
        try:
            datetime.fromisoformat(value.replace("Z", "+00:00"))
            return True
        except ValueError:
            return False

    def get_validation_summary(
        self, results: list[ValidationResult]
    ) -> dict[str, Any]:
        """
        Get summary of validation results.

        Args:
            results: List of validation results

        Returns:
            Summary statistics
        """
        total = len(results)
        valid = sum(1 for r in results if r.is_valid)
        invalid = total - valid

        total_errors = sum(r.errors for r in results)
        total_warnings = sum(r.warnings for r in results)

        # Count issues by rule
        issues_by_rule: dict[str, int] = {}
        for result in results:
            for issue in result.issues:
                issues_by_rule[issue.rule_name] = (
                    issues_by_rule.get(issue.rule_name, 0) + 1
                )

        return {
            "total_records": total,
            "valid_records": valid,
            "invalid_records": invalid,
            "validation_rate": valid / total if total > 0 else 0,
            "total_errors": total_errors,
            "total_warnings": total_warnings,
            "issues_by_rule": issues_by_rule,
        }


class IncidentValidator(DataValidator):
    """
    Specialized validator for incident records.

    Extends base validator with incident-specific rules.
    """

    # Valid crime categories
    VALID_CRIME_CATEGORIES = [
        "violent",
        "property",
        "drug",
        "traffic",
        "disorder",
        "other",
    ]

    # Valid severity levels
    VALID_SEVERITY_LEVELS = ["critical", "high", "medium", "low"]

    def __init__(self, strict_mode: bool = False):
        """Initialize incident validator."""
        super().__init__(strict_mode=strict_mode)

        # Add incident-specific validators
        self.add_custom_validator("crime_category", self._validate_crime_category)
        self.add_custom_validator("severity", self._validate_severity)
        self.add_custom_validator("source_system", self._validate_source_system)

    def _validate_crime_category(
        self, record: dict[str, Any]
    ) -> ValidationIssue | None:
        """Validate crime category."""
        category = record.get("crime_category")
        if category and category not in self.VALID_CRIME_CATEGORIES:
            return ValidationIssue(
                rule_name="crime_category",
                field="crime_category",
                message=f"Invalid crime category: {category}",
                severity=ValidationSeverity.WARNING,
                value=category,
            )
        return None

    def _validate_severity(self, record: dict[str, Any]) -> ValidationIssue | None:
        """Validate severity level."""
        severity = record.get("severity")
        if severity and severity not in self.VALID_SEVERITY_LEVELS:
            return ValidationIssue(
                rule_name="severity",
                field="severity",
                message=f"Invalid severity level: {severity}",
                severity=ValidationSeverity.WARNING,
                value=severity,
            )
        return None

    def _validate_source_system(
        self, record: dict[str, Any]
    ) -> ValidationIssue | None:
        """Validate source system."""
        valid_sources = ["CAD", "RMS", "ShotSpotter", "LPR", "manual"]
        source = record.get("source_system")
        if source and source not in valid_sources:
            return ValidationIssue(
                rule_name="source_system",
                field="source_system",
                message=f"Unknown source system: {source}",
                severity=ValidationSeverity.INFO,
                value=source,
            )
        return None
