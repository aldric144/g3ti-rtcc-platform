"""
Public Data Access Validator

Phase 36: Public Safety Guardian
Ensures all public-facing analytics are compliant with CJIS, VAWA, HIPAA,
FERPA, and Florida Public Records laws. Automatically removes sensitive
identifiers and protected information.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set
import hashlib
import re
import uuid


class ComplianceFramework(Enum):
    CJIS = "cjis"
    VAWA = "vawa"
    HIPAA = "hipaa"
    FERPA = "ferpa"
    FLORIDA_PUBLIC_RECORDS = "florida_public_records"
    ADA = "ada"
    FCRA = "fcra"


class RedactionType(Enum):
    JUVENILE_IDENTIFIER = "juvenile_identifier"
    DOMESTIC_VIOLENCE_LOCATION = "domestic_violence_location"
    VICTIM_DATA = "victim_data"
    MENTAL_HEALTH_INFO = "mental_health_info"
    MEDICAL_INFO = "medical_info"
    EDUCATIONAL_RECORD = "educational_record"
    SSN = "ssn"
    FINANCIAL_INFO = "financial_info"
    OFFICER_HOME_ADDRESS = "officer_home_address"
    WITNESS_IDENTITY = "witness_identity"
    INFORMANT_INFO = "informant_info"
    ONGOING_INVESTIGATION = "ongoing_investigation"
    PERSONAL_IDENTIFIER = "personal_identifier"
    PHONE_NUMBER = "phone_number"
    EMAIL_ADDRESS = "email_address"
    DATE_OF_BIRTH = "date_of_birth"
    EXACT_LOCATION = "exact_location"


class ValidationStatus(Enum):
    PASSED = "passed"
    FAILED = "failed"
    REQUIRES_REDACTION = "requires_redaction"
    BLOCKED = "blocked"


@dataclass
class RedactionRule:
    rule_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    redaction_type: RedactionType = RedactionType.PERSONAL_IDENTIFIER
    frameworks: List[ComplianceFramework] = field(default_factory=list)
    pattern: str = ""
    replacement: str = "[REDACTED]"
    priority: int = 1
    active: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "name": self.name,
            "description": self.description,
            "redaction_type": self.redaction_type.value,
            "frameworks": [f.value for f in self.frameworks],
            "pattern": self.pattern,
            "replacement": self.replacement,
            "priority": self.priority,
            "active": self.active,
        }


@dataclass
class RedactionResult:
    original_length: int = 0
    redacted_length: int = 0
    redactions_applied: List[str] = field(default_factory=list)
    redaction_count: int = 0
    frameworks_enforced: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "original_length": self.original_length,
            "redacted_length": self.redacted_length,
            "redactions_applied": self.redactions_applied,
            "redaction_count": self.redaction_count,
            "frameworks_enforced": self.frameworks_enforced,
        }


@dataclass
class ValidationResult:
    validation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: ValidationStatus = ValidationStatus.PASSED
    data_type: str = ""
    frameworks_checked: List[ComplianceFramework] = field(default_factory=list)
    violations: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    redaction_result: Optional[RedactionResult] = None
    validated_at: datetime = field(default_factory=datetime.utcnow)
    validation_hash: str = ""

    def __post_init__(self):
        if not self.validation_hash:
            self.validation_hash = self._generate_hash()

    def _generate_hash(self) -> str:
        content = f"{self.validation_id}{self.status.value}{self.validated_at.isoformat()}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "validation_id": self.validation_id,
            "status": self.status.value,
            "data_type": self.data_type,
            "frameworks_checked": [f.value for f in self.frameworks_checked],
            "violations": self.violations,
            "warnings": self.warnings,
            "redaction_result": self.redaction_result.to_dict() if self.redaction_result else None,
            "validated_at": self.validated_at.isoformat(),
            "validation_hash": self.validation_hash,
        }


class PublicDataAccessValidator:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.rules: Dict[str, RedactionRule] = {}
        self.validation_history: List[ValidationResult] = []
        self.statistics = {
            "validations_performed": 0,
            "validations_passed": 0,
            "validations_failed": 0,
            "redactions_applied": 0,
            "blocked_requests": 0,
        }
        self._initialize_redaction_rules()

    def _initialize_redaction_rules(self):
        rules = [
            RedactionRule(
                name="SSN Pattern",
                description="Social Security Number pattern detection",
                redaction_type=RedactionType.SSN,
                frameworks=[ComplianceFramework.CJIS, ComplianceFramework.HIPAA],
                pattern=r"\b\d{3}-\d{2}-\d{4}\b",
                replacement="[SSN REDACTED]",
                priority=1,
            ),
            RedactionRule(
                name="Phone Number",
                description="Phone number pattern detection",
                redaction_type=RedactionType.PHONE_NUMBER,
                frameworks=[ComplianceFramework.FLORIDA_PUBLIC_RECORDS],
                pattern=r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",
                replacement="[PHONE REDACTED]",
                priority=2,
            ),
            RedactionRule(
                name="Email Address",
                description="Email address pattern detection",
                redaction_type=RedactionType.EMAIL_ADDRESS,
                frameworks=[ComplianceFramework.FLORIDA_PUBLIC_RECORDS],
                pattern=r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
                replacement="[EMAIL REDACTED]",
                priority=2,
            ),
            RedactionRule(
                name="Date of Birth",
                description="Date of birth pattern detection",
                redaction_type=RedactionType.DATE_OF_BIRTH,
                frameworks=[ComplianceFramework.HIPAA, ComplianceFramework.FERPA],
                pattern=r"\b(0[1-9]|1[0-2])/(0[1-9]|[12]\d|3[01])/\d{4}\b",
                replacement="[DOB REDACTED]",
                priority=2,
            ),
            RedactionRule(
                name="Juvenile Indicator",
                description="Juvenile/minor indicator keywords",
                redaction_type=RedactionType.JUVENILE_IDENTIFIER,
                frameworks=[ComplianceFramework.CJIS, ComplianceFramework.FERPA],
                pattern=r"\b(juvenile|minor|child|youth|teen|adolescent)\s+(name|id|identifier):\s*\w+",
                replacement="[JUVENILE INFO REDACTED]",
                priority=1,
            ),
            RedactionRule(
                name="Domestic Violence Location",
                description="DV shelter and victim location",
                redaction_type=RedactionType.DOMESTIC_VIOLENCE_LOCATION,
                frameworks=[ComplianceFramework.VAWA],
                pattern=r"\b(dv|domestic violence|shelter|safe house)\s+(address|location):\s*[^,\n]+",
                replacement="[DV LOCATION REDACTED]",
                priority=1,
            ),
            RedactionRule(
                name="Mental Health Call",
                description="Mental health related identifiable info",
                redaction_type=RedactionType.MENTAL_HEALTH_INFO,
                frameworks=[ComplianceFramework.HIPAA],
                pattern=r"\b(baker act|mental health|psychiatric|suicide attempt)\s+(patient|subject|individual):\s*\w+",
                replacement="[MENTAL HEALTH INFO REDACTED]",
                priority=1,
            ),
            RedactionRule(
                name="Medical Information",
                description="Medical and health information",
                redaction_type=RedactionType.MEDICAL_INFO,
                frameworks=[ComplianceFramework.HIPAA],
                pattern=r"\b(diagnosis|medical record|treatment|medication|hospital):\s*[^,\n]+",
                replacement="[MEDICAL INFO REDACTED]",
                priority=1,
            ),
            RedactionRule(
                name="Victim Identity",
                description="Victim name and identifying information",
                redaction_type=RedactionType.VICTIM_DATA,
                frameworks=[ComplianceFramework.VAWA, ComplianceFramework.FLORIDA_PUBLIC_RECORDS],
                pattern=r"\bvictim\s+(name|id|address|phone):\s*[^,\n]+",
                replacement="[VICTIM INFO REDACTED]",
                priority=1,
            ),
            RedactionRule(
                name="Witness Identity",
                description="Witness name and contact information",
                redaction_type=RedactionType.WITNESS_IDENTITY,
                frameworks=[ComplianceFramework.FLORIDA_PUBLIC_RECORDS],
                pattern=r"\bwitness\s+(name|id|address|phone):\s*[^,\n]+",
                replacement="[WITNESS INFO REDACTED]",
                priority=2,
            ),
            RedactionRule(
                name="Exact Address",
                description="Exact street addresses for sensitive calls",
                redaction_type=RedactionType.EXACT_LOCATION,
                frameworks=[ComplianceFramework.VAWA, ComplianceFramework.HIPAA],
                pattern=r"\b\d+\s+[A-Za-z]+\s+(St|Street|Ave|Avenue|Blvd|Boulevard|Dr|Drive|Rd|Road|Ln|Lane|Ct|Court)\b[^,]*",
                replacement="[ADDRESS REDACTED]",
                priority=3,
            ),
        ]

        for rule in rules:
            self.rules[rule.rule_id] = rule

    def validate_data(
        self,
        data: Any,
        data_type: str = "general",
        frameworks: Optional[List[ComplianceFramework]] = None,
        auto_redact: bool = True,
    ) -> ValidationResult:
        if frameworks is None:
            frameworks = list(ComplianceFramework)

        result = ValidationResult(
            data_type=data_type,
            frameworks_checked=frameworks,
        )

        if isinstance(data, dict):
            data_str = str(data)
        elif isinstance(data, str):
            data_str = data
        else:
            data_str = str(data)

        violations = []
        warnings = []

        for rule in sorted(self.rules.values(), key=lambda r: r.priority):
            if not rule.active:
                continue

            if not any(f in frameworks for f in rule.frameworks):
                continue

            if re.search(rule.pattern, data_str, re.IGNORECASE):
                if rule.priority == 1:
                    violations.append(f"{rule.name}: {rule.description}")
                else:
                    warnings.append(f"{rule.name}: {rule.description}")

        result.violations = violations
        result.warnings = warnings

        if violations:
            if auto_redact:
                result.status = ValidationStatus.REQUIRES_REDACTION
            else:
                result.status = ValidationStatus.FAILED
        elif warnings:
            result.status = ValidationStatus.REQUIRES_REDACTION if auto_redact else ValidationStatus.PASSED
        else:
            result.status = ValidationStatus.PASSED

        self.validation_history.append(result)
        self.statistics["validations_performed"] += 1

        if result.status == ValidationStatus.PASSED:
            self.statistics["validations_passed"] += 1
        elif result.status == ValidationStatus.FAILED:
            self.statistics["validations_failed"] += 1

        return result

    def redact_data(
        self,
        data: str,
        frameworks: Optional[List[ComplianceFramework]] = None,
    ) -> tuple:
        if frameworks is None:
            frameworks = list(ComplianceFramework)

        original_length = len(data)
        redacted_data = data
        redactions_applied = []
        redaction_count = 0
        frameworks_enforced = set()

        for rule in sorted(self.rules.values(), key=lambda r: r.priority):
            if not rule.active:
                continue

            if not any(f in frameworks for f in rule.frameworks):
                continue

            matches = re.findall(rule.pattern, redacted_data, re.IGNORECASE)
            if matches:
                redacted_data = re.sub(rule.pattern, rule.replacement, redacted_data, flags=re.IGNORECASE)
                redactions_applied.append(rule.redaction_type.value)
                redaction_count += len(matches)
                frameworks_enforced.update(f.value for f in rule.frameworks)

        redaction_result = RedactionResult(
            original_length=original_length,
            redacted_length=len(redacted_data),
            redactions_applied=list(set(redactions_applied)),
            redaction_count=redaction_count,
            frameworks_enforced=list(frameworks_enforced),
        )

        self.statistics["redactions_applied"] += redaction_count

        return redacted_data, redaction_result

    def validate_and_redact(
        self,
        data: str,
        data_type: str = "general",
        frameworks: Optional[List[ComplianceFramework]] = None,
    ) -> tuple:
        validation_result = self.validate_data(data, data_type, frameworks, auto_redact=True)

        if validation_result.status in [ValidationStatus.REQUIRES_REDACTION, ValidationStatus.FAILED]:
            redacted_data, redaction_result = self.redact_data(data, frameworks)
            validation_result.redaction_result = redaction_result
            validation_result.status = ValidationStatus.PASSED
            return redacted_data, validation_result
        else:
            return data, validation_result

    def check_public_release_eligibility(
        self,
        data: Any,
        data_type: str = "report",
    ) -> Dict[str, Any]:
        all_frameworks = list(ComplianceFramework)
        validation = self.validate_data(data, data_type, all_frameworks, auto_redact=False)

        eligible = validation.status == ValidationStatus.PASSED
        requires_redaction = len(validation.violations) > 0 or len(validation.warnings) > 0

        return {
            "eligible_for_release": eligible,
            "requires_redaction": requires_redaction,
            "blocking_violations": validation.violations,
            "warnings": validation.warnings,
            "frameworks_checked": [f.value for f in all_frameworks],
            "recommendation": "approve" if eligible else ("redact_and_release" if requires_redaction else "block"),
        }

    def get_rule(self, rule_id: str) -> Optional[RedactionRule]:
        return self.rules.get(rule_id)

    def get_all_rules(self) -> List[RedactionRule]:
        return list(self.rules.values())

    def get_rules_by_framework(self, framework: ComplianceFramework) -> List[RedactionRule]:
        return [r for r in self.rules.values() if framework in r.frameworks]

    def add_rule(self, rule: RedactionRule) -> RedactionRule:
        self.rules[rule.rule_id] = rule
        return rule

    def update_rule(self, rule_id: str, **kwargs) -> Optional[RedactionRule]:
        rule = self.rules.get(rule_id)
        if not rule:
            return None

        for key, value in kwargs.items():
            if hasattr(rule, key):
                setattr(rule, key, value)

        return rule

    def deactivate_rule(self, rule_id: str) -> bool:
        rule = self.rules.get(rule_id)
        if rule:
            rule.active = False
            return True
        return False

    def get_validation_history(self, limit: int = 100) -> List[ValidationResult]:
        return self.validation_history[-limit:]

    def get_compliance_summary(self) -> Dict[str, Any]:
        framework_counts = {f.value: 0 for f in ComplianceFramework}
        for rule in self.rules.values():
            for framework in rule.frameworks:
                framework_counts[framework.value] += 1

        return {
            "total_rules": len(self.rules),
            "active_rules": sum(1 for r in self.rules.values() if r.active),
            "rules_by_framework": framework_counts,
            "redaction_types_covered": len(set(r.redaction_type for r in self.rules.values())),
            "frameworks_supported": len(ComplianceFramework),
        }

    def get_statistics(self) -> Dict[str, Any]:
        return {
            **self.statistics,
            "total_rules": len(self.rules),
            "active_rules": sum(1 for r in self.rules.values() if r.active),
            "validation_history_size": len(self.validation_history),
            "compliance_summary": self.get_compliance_summary(),
        }
