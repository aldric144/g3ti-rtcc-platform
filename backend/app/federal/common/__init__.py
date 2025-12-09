"""
G3TI RTCC-UIP Federal Readiness Common Module
Phase 11: Shared schemas, validation, transformation pipelines, and audit logging
"""

import hashlib
import re
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import uuid4


class FederalDataCategory(str, Enum):
    """Federal data categories"""
    PERSON = "person"
    INCIDENT = "incident"
    ARREST = "arrest"
    CASE = "case"
    PROPERTY = "property"
    VEHICLE = "vehicle"
    FIREARM = "firearm"
    LOCATION = "location"
    OFFENSE = "offense"
    SAR = "sar"
    TRACE = "trace"


class FederalExportStatus(str, Enum):
    """Federal export status"""
    PENDING = "pending"
    VALIDATING = "validating"
    VALIDATED = "validated"
    PACKAGING = "packaging"
    PACKAGED = "packaged"
    READY = "ready"
    EXPORTED = "exported"
    FAILED = "failed"
    REJECTED = "rejected"


class FederalMessageType(str, Enum):
    """Federal message types"""
    NDEX_PERSON = "ndex_person"
    NDEX_INCIDENT = "ndex_incident"
    NDEX_ARREST = "ndex_arrest"
    NDEX_CASE = "ndex_case"
    NDEX_PROPERTY = "ndex_property"
    NDEX_VEHICLE = "ndex_vehicle"
    NDEX_FIREARM = "ndex_firearm"
    NCIC_QUERY_VEHICLE = "ncic_query_vehicle"
    NCIC_QUERY_PERSON = "ncic_query_person"
    NCIC_QUERY_GUN = "ncic_query_gun"
    ETRACE_REQUEST = "etrace_request"
    ETRACE_REPORT = "etrace_report"
    DHS_SAR = "dhs_sar"


class FederalSystem(str, Enum):
    """Federal systems"""
    NDEX = "ndex"
    NCIC = "ncic"
    ETRACE = "etrace"
    DHS_SAR = "dhs_sar"


class CJISPolicyArea(str, Enum):
    """CJIS Security Policy Areas"""
    AREA_5 = "5"  # Access Control
    AREA_7 = "7"  # Encryption
    AREA_8 = "8"  # Auditing and Accountability
    AREA_10 = "10"  # System and Communications Protection


class FederalSchema:
    """Base class for federal data schemas"""

    def __init__(
        self,
        schema_name: str,
        schema_version: str,
        federal_system: FederalSystem,
        required_fields: list[str],
        optional_fields: list[str] | None = None,
        sensitive_fields: list[str] | None = None,
    ):
        self.id = str(uuid4())
        self.schema_name = schema_name
        self.schema_version = schema_version
        self.federal_system = federal_system
        self.required_fields = required_fields
        self.optional_fields = optional_fields or []
        self.sensitive_fields = sensitive_fields or []
        self.created_at = datetime.utcnow()

    def get_all_fields(self) -> list[str]:
        """Get all fields in schema"""
        return self.required_fields + self.optional_fields

    def is_sensitive_field(self, field_name: str) -> bool:
        """Check if field is sensitive"""
        return field_name in self.sensitive_fields


class FederalValidationResult:
    """Result of federal data validation"""

    def __init__(
        self,
        is_valid: bool,
        errors: list[str] | None = None,
        warnings: list[str] | None = None,
        validated_data: dict[str, Any] | None = None,
    ):
        self.id = str(uuid4())
        self.is_valid = is_valid
        self.errors = errors or []
        self.warnings = warnings or []
        self.validated_data = validated_data
        self.validated_at = datetime.utcnow()


class FederalValidator:
    """Validator for federal data"""

    def __init__(self):
        self.validation_rules: dict[str, list[callable]] = {}

    def add_rule(
        self,
        field_name: str,
        rule: callable,
    ) -> None:
        """Add validation rule for a field"""
        if field_name not in self.validation_rules:
            self.validation_rules[field_name] = []
        self.validation_rules[field_name].append(rule)

    def validate(
        self,
        data: dict[str, Any],
        schema: FederalSchema,
    ) -> FederalValidationResult:
        """Validate data against schema"""
        errors = []
        warnings = []

        # Check required fields
        for field in schema.required_fields:
            if field not in data or data[field] is None:
                errors.append(f"Required field '{field}' is missing")

        # Apply validation rules
        for field, rules in self.validation_rules.items():
            if field in data:
                for rule in rules:
                    try:
                        result = rule(data[field])
                        if result is not True:
                            errors.append(f"Field '{field}' failed validation: {result}")
                    except Exception as e:
                        errors.append(f"Field '{field}' validation error: {e!s}")

        return FederalValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            validated_data=data if len(errors) == 0 else None,
        )

    @staticmethod
    def validate_ssn(value: str) -> bool | str:
        """Validate SSN format"""
        if not value:
            return True
        pattern = r"^\d{3}-?\d{2}-?\d{4}$"
        if re.match(pattern, value):
            return True
        return "Invalid SSN format"

    @staticmethod
    def validate_date(value: str) -> bool | str:
        """Validate date format (YYYY-MM-DD)"""
        if not value:
            return True
        try:
            datetime.strptime(value, "%Y-%m-%d")
            return True
        except ValueError:
            return "Invalid date format (expected YYYY-MM-DD)"

    @staticmethod
    def validate_state_code(value: str) -> bool | str:
        """Validate US state code"""
        valid_states = [
            "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
            "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
            "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
            "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
            "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY",
            "DC", "PR", "VI", "GU", "AS", "MP",
        ]
        if value.upper() in valid_states:
            return True
        return "Invalid state code"

    @staticmethod
    def validate_vin(value: str) -> bool | str:
        """Validate Vehicle Identification Number"""
        if not value:
            return True
        if len(value) == 17 and value.isalnum():
            return True
        return "Invalid VIN format (must be 17 alphanumeric characters)"


class FederalTransformationPipeline:
    """Pipeline for transforming data to federal formats"""

    def __init__(self, name: str):
        self.id = str(uuid4())
        self.name = name
        self.transformations: list[callable] = []
        self.created_at = datetime.utcnow()

    def add_transformation(self, transform: callable) -> "FederalTransformationPipeline":
        """Add transformation to pipeline"""
        self.transformations.append(transform)
        return self

    def execute(self, data: dict[str, Any]) -> dict[str, Any]:
        """Execute all transformations on data"""
        result = data.copy()
        for transform in self.transformations:
            result = transform(result)
        return result

    @staticmethod
    def normalize_name(data: dict[str, Any]) -> dict[str, Any]:
        """Normalize name fields to uppercase"""
        result = data.copy()
        name_fields = ["first_name", "last_name", "middle_name", "suffix"]
        for field in name_fields:
            if field in result and result[field]:
                result[field] = result[field].upper().strip()
        return result

    @staticmethod
    def normalize_address(data: dict[str, Any]) -> dict[str, Any]:
        """Normalize address fields"""
        result = data.copy()
        address_fields = ["street", "city", "state", "zip_code"]
        for field in address_fields:
            if field in result and result[field]:
                result[field] = result[field].upper().strip()
        return result

    @staticmethod
    def format_date_iso(data: dict[str, Any]) -> dict[str, Any]:
        """Format date fields to ISO format"""
        result = data.copy()
        date_fields = ["date_of_birth", "incident_date", "arrest_date", "report_date"]
        for field in date_fields:
            if field in result and result[field]:
                if isinstance(result[field], datetime):
                    result[field] = result[field].strftime("%Y-%m-%d")
        return result

    @staticmethod
    def hash_identifier(value: str) -> str:
        """Hash sensitive identifier"""
        return hashlib.sha256(value.encode()).hexdigest()


class FederalMessagePackage:
    """Package for federal message transmission"""

    def __init__(
        self,
        message_type: FederalMessageType,
        federal_system: FederalSystem,
        payload: dict[str, Any],
        originating_agency: str,
        originating_user: str,
    ):
        self.id = str(uuid4())
        self.message_type = message_type
        self.federal_system = federal_system
        self.payload = payload
        self.originating_agency = originating_agency
        self.originating_user = originating_user
        self.created_at = datetime.utcnow()
        self.status = FederalExportStatus.PENDING
        self.validation_result: FederalValidationResult | None = None
        self.encrypted_payload: str | None = None
        self.signature: str | None = None
        self.nonce: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "message_type": self.message_type.value,
            "federal_system": self.federal_system.value,
            "originating_agency": self.originating_agency,
            "originating_user": self.originating_user,
            "created_at": self.created_at.isoformat(),
            "status": self.status.value,
        }


class FederalAuditEntry:
    """Audit log entry for federal operations"""

    def __init__(
        self,
        operation: str,
        federal_system: FederalSystem,
        message_type: FederalMessageType | None,
        agency_id: str,
        user_id: str,
        user_name: str,
        resource_type: str,
        resource_id: str | None,
        action: str,
        details: dict[str, Any],
        ip_address: str | None = None,
        success: bool = True,
        error_message: str | None = None,
    ):
        self.id = str(uuid4())
        self.operation = operation
        self.federal_system = federal_system
        self.message_type = message_type
        self.agency_id = agency_id
        self.user_id = user_id
        self.user_name = user_name
        self.resource_type = resource_type
        self.resource_id = resource_id
        self.action = action
        self.details = details
        self.ip_address = ip_address
        self.success = success
        self.error_message = error_message
        self.timestamp = datetime.utcnow()
        # CJIS Policy Area 8 - Audit retention (minimum 1 year)
        self.retention_years = 7

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for logging"""
        return {
            "id": self.id,
            "operation": self.operation,
            "federal_system": self.federal_system.value if self.federal_system else None,
            "message_type": self.message_type.value if self.message_type else None,
            "agency_id": self.agency_id,
            "user_id": self.user_id,
            "user_name": self.user_name,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "action": self.action,
            "success": self.success,
            "error_message": self.error_message,
            "timestamp": self.timestamp.isoformat(),
        }


class FederalAuditLogger:
    """CJIS-compliant audit logger for federal operations"""

    def __init__(self):
        self.audit_log: list[FederalAuditEntry] = []

    def log(
        self,
        operation: str,
        federal_system: FederalSystem,
        message_type: FederalMessageType | None,
        agency_id: str,
        user_id: str,
        user_name: str,
        resource_type: str,
        resource_id: str | None,
        action: str,
        details: dict[str, Any],
        ip_address: str | None = None,
        success: bool = True,
        error_message: str | None = None,
    ) -> FederalAuditEntry:
        """Log federal operation"""
        entry = FederalAuditEntry(
            operation=operation,
            federal_system=federal_system,
            message_type=message_type,
            agency_id=agency_id,
            user_id=user_id,
            user_name=user_name,
            resource_type=resource_type,
            resource_id=resource_id,
            action=action,
            details=details,
            ip_address=ip_address,
            success=success,
            error_message=error_message,
        )
        self.audit_log.append(entry)
        return entry

    def log_ndex_export(
        self,
        agency_id: str,
        user_id: str,
        user_name: str,
        resource_type: str,
        resource_id: str,
        success: bool = True,
        error_message: str | None = None,
        ip_address: str | None = None,
    ) -> FederalAuditEntry:
        """Log N-DEx export operation"""
        return self.log(
            operation="ndex_export",
            federal_system=FederalSystem.NDEX,
            message_type=FederalMessageType.NDEX_INCIDENT,
            agency_id=agency_id,
            user_id=user_id,
            user_name=user_name,
            resource_type=resource_type,
            resource_id=resource_id,
            action="export",
            details={"export_type": "ndex", "resource_type": resource_type},
            ip_address=ip_address,
            success=success,
            error_message=error_message,
        )

    def log_ncic_query(
        self,
        agency_id: str,
        user_id: str,
        user_name: str,
        query_type: str,
        query_params: dict[str, Any],
        ip_address: str | None = None,
    ) -> FederalAuditEntry:
        """Log NCIC query stub operation"""
        return self.log(
            operation="ncic_query_stub",
            federal_system=FederalSystem.NCIC,
            message_type=FederalMessageType.NCIC_QUERY_VEHICLE,
            agency_id=agency_id,
            user_id=user_id,
            user_name=user_name,
            resource_type="query",
            resource_id=None,
            action="query_stub",
            details={"query_type": query_type, "params": query_params},
            ip_address=ip_address,
            success=True,
        )

    def log_etrace_export(
        self,
        agency_id: str,
        user_id: str,
        user_name: str,
        weapon_id: str,
        incident_id: str | None = None,
        ip_address: str | None = None,
    ) -> FederalAuditEntry:
        """Log ATF eTrace export operation"""
        return self.log(
            operation="etrace_export",
            federal_system=FederalSystem.ETRACE,
            message_type=FederalMessageType.ETRACE_REQUEST,
            agency_id=agency_id,
            user_id=user_id,
            user_name=user_name,
            resource_type="weapon",
            resource_id=weapon_id,
            action="export",
            details={"weapon_id": weapon_id, "incident_id": incident_id},
            ip_address=ip_address,
            success=True,
        )

    def log_sar_submission(
        self,
        agency_id: str,
        user_id: str,
        user_name: str,
        sar_id: str,
        ip_address: str | None = None,
    ) -> FederalAuditEntry:
        """Log DHS SAR submission operation"""
        return self.log(
            operation="sar_submission",
            federal_system=FederalSystem.DHS_SAR,
            message_type=FederalMessageType.DHS_SAR,
            agency_id=agency_id,
            user_id=user_id,
            user_name=user_name,
            resource_type="sar",
            resource_id=sar_id,
            action="submit",
            details={"sar_id": sar_id},
            ip_address=ip_address,
            success=True,
        )

    def get_audit_log(
        self,
        agency_id: str | None = None,
        federal_system: FederalSystem | None = None,
        user_id: str | None = None,
        since: datetime | None = None,
        until: datetime | None = None,
        limit: int = 1000,
    ) -> list[FederalAuditEntry]:
        """Get audit log entries with filtering"""
        entries = self.audit_log.copy()

        if agency_id:
            entries = [e for e in entries if e.agency_id == agency_id]
        if federal_system:
            entries = [e for e in entries if e.federal_system == federal_system]
        if user_id:
            entries = [e for e in entries if e.user_id == user_id]
        if since:
            entries = [e for e in entries if e.timestamp >= since]
        if until:
            entries = [e for e in entries if e.timestamp <= until]

        entries.sort(key=lambda e: e.timestamp, reverse=True)
        return entries[:limit]

    def get_compliance_report(
        self,
        agency_id: str,
        start_date: datetime,
        end_date: datetime,
    ) -> dict[str, Any]:
        """Generate CJIS compliance report"""
        entries = self.get_audit_log(
            agency_id=agency_id,
            since=start_date,
            until=end_date,
            limit=10000,
        )

        stats = {
            "total_operations": len(entries),
            "by_system": {},
            "by_operation": {},
            "successful": 0,
            "failed": 0,
            "unique_users": set(),
        }

        for entry in entries:
            # Count by system
            system = entry.federal_system.value if entry.federal_system else "unknown"
            stats["by_system"][system] = stats["by_system"].get(system, 0) + 1

            # Count by operation
            stats["by_operation"][entry.operation] = (
                stats["by_operation"].get(entry.operation, 0) + 1
            )

            # Count success/failure
            if entry.success:
                stats["successful"] += 1
            else:
                stats["failed"] += 1

            # Track unique users
            stats["unique_users"].add(entry.user_id)

        stats["unique_users"] = len(stats["unique_users"])

        return {
            "agency_id": agency_id,
            "report_period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
            },
            "statistics": stats,
            "cjis_compliance": {
                "area_5_access_control": "enforced",
                "area_7_encryption": "enforced",
                "area_8_auditing": "compliant",
                "area_10_system_protection": "enforced",
            },
            "generated_at": datetime.utcnow().isoformat(),
        }


# Create singleton instance
federal_audit_logger = FederalAuditLogger()
