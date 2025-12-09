"""
G3TI RTCC-UIP NCIC Query Structure (STUB ONLY)
Phase 11: Non-operational NCIC query scaffolding for readiness purposes
NOTE: This is a STUB implementation for federal readiness only.
      It does NOT perform actual NCIC queries.
"""

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import uuid4

from app.federal.common import (
    FederalAuditLogger,
    FederalSchema,
    FederalSystem,
    FederalValidationResult,
    FederalValidator,
)


# NCIC Query Types
class NCICQueryType(str, Enum):
    """NCIC query types"""
    VEHICLE = "vehicle"
    PERSON = "person"
    GUN = "gun"
    ARTICLE = "article"
    BOAT = "boat"
    SECURITIES = "securities"
    LICENSE_PLATE = "license_plate"
    WANTED_PERSON = "wanted_person"
    MISSING_PERSON = "missing_person"


class NCICFileType(str, Enum):
    """NCIC file types"""
    VEHICLE = "V"  # Vehicle File
    LICENSE_PLATE = "L"  # License Plate File
    BOAT = "B"  # Boat File
    GUN = "G"  # Gun File
    ARTICLE = "A"  # Article File
    SECURITIES = "S"  # Securities File
    WANTED_PERSON = "W"  # Wanted Person File
    MISSING_PERSON = "M"  # Missing Person File
    FOREIGN_FUGITIVE = "F"  # Foreign Fugitive File
    IDENTITY_THEFT = "I"  # Identity Theft File
    GANG = "GG"  # Gang File
    KNOWN_SUSPECTED_TERRORIST = "KST"  # Known/Suspected Terrorist File
    SUPERVISED_RELEASE = "SR"  # Supervised Release File
    NICS_DENIED = "ND"  # NICS Denied Transaction File
    PROTECTION_ORDER = "PO"  # Protection Order File
    SEX_OFFENDER = "SO"  # Sex Offender Registry File


class NCICResponseCode(str, Enum):
    """NCIC response codes"""
    HIT = "HIT"
    NO_HIT = "NO HIT"
    ERROR = "ERROR"
    INVALID = "INVALID"
    STUB = "STUB"  # For readiness stub responses


# NCIC Query Schemas
class NCICVehicleQuerySchema(FederalSchema):
    """NCIC Vehicle Query schema"""

    def __init__(self):
        super().__init__(
            schema_name="NCIC_Vehicle_Query",
            schema_version="1.0",
            federal_system=FederalSystem.NCIC,
            required_fields=[
                "query_type",
                "requesting_agency_ori",
                "requesting_officer",
            ],
            optional_fields=[
                "vin",
                "license_plate",
                "license_state",
                "make",
                "model",
                "year",
                "color",
                "owner_name",
            ],
            sensitive_fields=[
                "vin",
                "license_plate",
                "owner_name",
            ],
        )


class NCICPersonQuerySchema(FederalSchema):
    """NCIC Person Query schema"""

    def __init__(self):
        super().__init__(
            schema_name="NCIC_Person_Query",
            schema_version="1.0",
            federal_system=FederalSystem.NCIC,
            required_fields=[
                "query_type",
                "requesting_agency_ori",
                "requesting_officer",
            ],
            optional_fields=[
                "last_name",
                "first_name",
                "middle_name",
                "date_of_birth",
                "sex",
                "race",
                "ssn",
                "drivers_license",
                "drivers_license_state",
                "fbi_number",
                "state_id",
                "miscellaneous_id",
            ],
            sensitive_fields=[
                "ssn",
                "drivers_license",
                "date_of_birth",
            ],
        )


class NCICGunQuerySchema(FederalSchema):
    """NCIC Gun Query schema"""

    def __init__(self):
        super().__init__(
            schema_name="NCIC_Gun_Query",
            schema_version="1.0",
            federal_system=FederalSystem.NCIC,
            required_fields=[
                "query_type",
                "requesting_agency_ori",
                "requesting_officer",
            ],
            optional_fields=[
                "serial_number",
                "make",
                "model",
                "caliber",
                "gun_type",
                "barrel_length",
            ],
            sensitive_fields=[
                "serial_number",
            ],
        )


class NCICQueryRequest:
    """NCIC query request structure"""

    def __init__(
        self,
        query_type: NCICQueryType,
        requesting_agency_ori: str,
        requesting_officer: str,
        query_params: dict[str, Any],
        purpose: str | None = None,
    ):
        self.id = str(uuid4())
        self.query_type = query_type
        self.requesting_agency_ori = requesting_agency_ori
        self.requesting_officer = requesting_officer
        self.query_params = query_params
        self.purpose = purpose or "Law Enforcement Investigation"
        self.created_at = datetime.utcnow()
        self.status = "pending"
        self.validation_result: FederalValidationResult | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "query_type": self.query_type.value,
            "requesting_agency_ori": self.requesting_agency_ori,
            "requesting_officer": self.requesting_officer,
            "query_params": self.query_params,
            "purpose": self.purpose,
            "created_at": self.created_at.isoformat(),
            "status": self.status,
        }


class NCICStubResponse:
    """NCIC stub response for readiness purposes"""

    STUB_MESSAGE = (
        "This is a non-operational NCIC request stub for readiness purposes only. "
        "No actual NCIC query was performed. This response demonstrates the "
        "data structure and format that would be returned from an actual NCIC query."
    )

    def __init__(
        self,
        query_request: NCICQueryRequest,
        response_code: NCICResponseCode = NCICResponseCode.STUB,
    ):
        self.id = str(uuid4())
        self.query_id = query_request.id
        self.query_type = query_request.query_type
        self.response_code = response_code
        self.message = self.STUB_MESSAGE
        self.created_at = datetime.utcnow()
        self.is_stub = True
        self.sample_data = self._generate_sample_data(query_request.query_type)

    def _generate_sample_data(self, query_type: NCICQueryType) -> dict[str, Any]:
        """Generate sample response data for demonstration"""
        if query_type == NCICQueryType.VEHICLE:
            return {
                "file_type": NCICFileType.VEHICLE.value,
                "record_type": "SAMPLE",
                "vin": "SAMPLE_VIN_REDACTED",
                "license_plate": "SAMPLE_PLATE",
                "license_state": "XX",
                "make": "SAMPLE_MAKE",
                "model": "SAMPLE_MODEL",
                "year": "2024",
                "color": "SAMPLE_COLOR",
                "status": "SAMPLE_STATUS",
                "entry_date": "2024-01-01",
                "originating_agency": "SAMPLE_ORI",
                "note": "This is sample data for readiness demonstration only",
            }
        elif query_type == NCICQueryType.PERSON:
            return {
                "file_type": NCICFileType.WANTED_PERSON.value,
                "record_type": "SAMPLE",
                "last_name": "SAMPLE_LAST",
                "first_name": "SAMPLE_FIRST",
                "date_of_birth": "REDACTED",
                "sex": "X",
                "race": "X",
                "height": "000",
                "weight": "000",
                "eye_color": "XXX",
                "hair_color": "XXX",
                "warrant_number": "SAMPLE_WARRANT",
                "offense": "SAMPLE_OFFENSE",
                "entry_date": "2024-01-01",
                "originating_agency": "SAMPLE_ORI",
                "note": "This is sample data for readiness demonstration only",
            }
        elif query_type == NCICQueryType.GUN:
            return {
                "file_type": NCICFileType.GUN.value,
                "record_type": "SAMPLE",
                "serial_number": "SAMPLE_SN_REDACTED",
                "make": "SAMPLE_MAKE",
                "model": "SAMPLE_MODEL",
                "caliber": "SAMPLE_CAL",
                "gun_type": "SAMPLE_TYPE",
                "status": "SAMPLE_STATUS",
                "entry_date": "2024-01-01",
                "originating_agency": "SAMPLE_ORI",
                "note": "This is sample data for readiness demonstration only",
            }
        else:
            return {
                "file_type": "UNKNOWN",
                "record_type": "SAMPLE",
                "note": "This is sample data for readiness demonstration only",
            }

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "query_id": self.query_id,
            "query_type": self.query_type.value,
            "response_code": self.response_code.value,
            "message": self.message,
            "is_stub": self.is_stub,
            "sample_data": self.sample_data,
            "created_at": self.created_at.isoformat(),
        }


class NCICQueryValidator:
    """Validator for NCIC query requests"""

    def __init__(self):
        self.validator = FederalValidator()
        self.vehicle_schema = NCICVehicleQuerySchema()
        self.person_schema = NCICPersonQuerySchema()
        self.gun_schema = NCICGunQuerySchema()

        # Add validation rules
        self.validator.add_rule("date_of_birth", FederalValidator.validate_date)
        self.validator.add_rule("drivers_license_state", FederalValidator.validate_state_code)
        self.validator.add_rule("license_state", FederalValidator.validate_state_code)
        self.validator.add_rule("vin", FederalValidator.validate_vin)

    def validate_vehicle_query(
        self,
        query_params: dict[str, Any],
    ) -> FederalValidationResult:
        """Validate vehicle query parameters"""
        errors = []
        warnings = []

        # At least one search parameter required
        search_fields = ["vin", "license_plate", "make", "model"]
        if not any(query_params.get(f) for f in search_fields):
            errors.append(
                "At least one search parameter required: vin, license_plate, make, or model",
            )

        # Validate VIN if provided
        if query_params.get("vin"):
            vin_result = FederalValidator.validate_vin(query_params["vin"])
            if vin_result is not True:
                errors.append(f"VIN validation failed: {vin_result}")

        # Validate state if provided
        if query_params.get("license_state"):
            state_result = FederalValidator.validate_state_code(
                query_params["license_state"],
            )
            if state_result is not True:
                errors.append(f"License state validation failed: {state_result}")

        return FederalValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            validated_data=query_params if len(errors) == 0 else None,
        )

    def validate_person_query(
        self,
        query_params: dict[str, Any],
    ) -> FederalValidationResult:
        """Validate person query parameters"""
        errors = []
        warnings = []

        # At least one search parameter required
        search_fields = [
            "last_name",
            "ssn",
            "drivers_license",
            "fbi_number",
            "state_id",
        ]
        if not any(query_params.get(f) for f in search_fields):
            errors.append(
                "At least one search parameter required: last_name, ssn, "
                "drivers_license, fbi_number, or state_id",
            )

        # Validate SSN if provided
        if query_params.get("ssn"):
            ssn_result = FederalValidator.validate_ssn(query_params["ssn"])
            if ssn_result is not True:
                errors.append(f"SSN validation failed: {ssn_result}")

        # Validate DOB if provided
        if query_params.get("date_of_birth"):
            dob_result = FederalValidator.validate_date(query_params["date_of_birth"])
            if dob_result is not True:
                errors.append(f"Date of birth validation failed: {dob_result}")

        # Validate state if provided
        if query_params.get("drivers_license_state"):
            state_result = FederalValidator.validate_state_code(
                query_params["drivers_license_state"],
            )
            if state_result is not True:
                errors.append(f"Driver's license state validation failed: {state_result}")

        return FederalValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            validated_data=query_params if len(errors) == 0 else None,
        )

    def validate_gun_query(
        self,
        query_params: dict[str, Any],
    ) -> FederalValidationResult:
        """Validate gun query parameters"""
        errors = []
        warnings = []

        # At least one search parameter required
        search_fields = ["serial_number", "make", "model"]
        if not any(query_params.get(f) for f in search_fields):
            errors.append(
                "At least one search parameter required: serial_number, make, or model",
            )

        # Serial number is strongly recommended
        if not query_params.get("serial_number"):
            warnings.append(
                "Serial number is strongly recommended for accurate gun queries",
            )

        return FederalValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            validated_data=query_params if len(errors) == 0 else None,
        )


class NCICQueryManager:
    """
    Manager for NCIC query stubs (NON-OPERATIONAL)

    This manager provides the scaffolding for NCIC queries but does NOT
    perform actual queries. It is designed for federal readiness purposes
    to demonstrate data structures and validation rules.
    """

    STUB_DISCLAIMER = (
        "IMPORTANT: This is a non-operational NCIC query stub for federal "
        "readiness purposes only. No actual NCIC queries are performed. "
        "This system demonstrates the required data structures, validation "
        "rules, and message formats needed for future NCIC integration."
    )

    def __init__(self, audit_logger: FederalAuditLogger):
        self.audit_logger = audit_logger
        self.validator = NCICQueryValidator()
        self.queries: dict[str, NCICQueryRequest] = {}
        self.responses: dict[str, NCICStubResponse] = {}

    def create_vehicle_query(
        self,
        agency_ori: str,
        officer_name: str,
        query_params: dict[str, Any],
        user_id: str,
        purpose: str | None = None,
    ) -> tuple[NCICQueryRequest, NCICStubResponse]:
        """
        Create a vehicle query stub (NON-OPERATIONAL)

        Returns a stub response - no actual NCIC query is performed.
        """
        # Validate query
        validation = self.validator.validate_vehicle_query(query_params)

        # Create query request
        query = NCICQueryRequest(
            query_type=NCICQueryType.VEHICLE,
            requesting_agency_ori=agency_ori,
            requesting_officer=officer_name,
            query_params=query_params,
            purpose=purpose,
        )
        query.validation_result = validation

        if validation.is_valid:
            query.status = "validated"
        else:
            query.status = "validation_failed"

        # Create stub response
        response = NCICStubResponse(
            query_request=query,
            response_code=NCICResponseCode.STUB,
        )

        # Log the query attempt
        self.audit_logger.log_ncic_query(
            agency_id=agency_ori,
            user_id=user_id,
            user_name=officer_name,
            query_type="vehicle",
            query_params=query_params,
        )

        # Store
        self.queries[query.id] = query
        self.responses[response.id] = response

        return query, response

    def create_person_query(
        self,
        agency_ori: str,
        officer_name: str,
        query_params: dict[str, Any],
        user_id: str,
        purpose: str | None = None,
    ) -> tuple[NCICQueryRequest, NCICStubResponse]:
        """
        Create a person query stub (NON-OPERATIONAL)

        Returns a stub response - no actual NCIC query is performed.
        """
        # Validate query
        validation = self.validator.validate_person_query(query_params)

        # Create query request
        query = NCICQueryRequest(
            query_type=NCICQueryType.PERSON,
            requesting_agency_ori=agency_ori,
            requesting_officer=officer_name,
            query_params=query_params,
            purpose=purpose,
        )
        query.validation_result = validation

        if validation.is_valid:
            query.status = "validated"
        else:
            query.status = "validation_failed"

        # Create stub response
        response = NCICStubResponse(
            query_request=query,
            response_code=NCICResponseCode.STUB,
        )

        # Log the query attempt
        self.audit_logger.log_ncic_query(
            agency_id=agency_ori,
            user_id=user_id,
            user_name=officer_name,
            query_type="person",
            query_params=query_params,
        )

        # Store
        self.queries[query.id] = query
        self.responses[response.id] = response

        return query, response

    def create_gun_query(
        self,
        agency_ori: str,
        officer_name: str,
        query_params: dict[str, Any],
        user_id: str,
        purpose: str | None = None,
    ) -> tuple[NCICQueryRequest, NCICStubResponse]:
        """
        Create a gun query stub (NON-OPERATIONAL)

        Returns a stub response - no actual NCIC query is performed.
        """
        # Validate query
        validation = self.validator.validate_gun_query(query_params)

        # Create query request
        query = NCICQueryRequest(
            query_type=NCICQueryType.GUN,
            requesting_agency_ori=agency_ori,
            requesting_officer=officer_name,
            query_params=query_params,
            purpose=purpose,
        )
        query.validation_result = validation

        if validation.is_valid:
            query.status = "validated"
        else:
            query.status = "validation_failed"

        # Create stub response
        response = NCICStubResponse(
            query_request=query,
            response_code=NCICResponseCode.STUB,
        )

        # Log the query attempt
        self.audit_logger.log_ncic_query(
            agency_id=agency_ori,
            user_id=user_id,
            user_name=officer_name,
            query_type="gun",
            query_params=query_params,
        )

        # Store
        self.queries[query.id] = query
        self.responses[response.id] = response

        return query, response

    def get_query(self, query_id: str) -> NCICQueryRequest | None:
        """Get query by ID"""
        return self.queries.get(query_id)

    def get_response(self, response_id: str) -> NCICStubResponse | None:
        """Get response by ID"""
        return self.responses.get(response_id)

    def get_queries_by_agency(
        self,
        agency_ori: str,
        limit: int = 100,
    ) -> list[NCICQueryRequest]:
        """Get queries for an agency"""
        queries = [
            q for q in self.queries.values()
            if q.requesting_agency_ori == agency_ori
        ]
        queries.sort(key=lambda q: q.created_at, reverse=True)
        return queries[:limit]

    def get_readiness_status(self) -> dict[str, Any]:
        """Get NCIC readiness status"""
        return {
            "status": "ready_for_integration",
            "is_operational": False,
            "disclaimer": self.STUB_DISCLAIMER,
            "supported_query_types": [qt.value for qt in NCICQueryType],
            "supported_file_types": [ft.value for ft in NCICFileType],
            "validation_rules": {
                "vehicle": {
                    "required_fields": ["query_type", "requesting_agency_ori", "requesting_officer"],
                    "search_fields": ["vin", "license_plate", "make", "model"],
                    "validation": ["vin_format", "state_code"],
                },
                "person": {
                    "required_fields": ["query_type", "requesting_agency_ori", "requesting_officer"],
                    "search_fields": ["last_name", "ssn", "drivers_license", "fbi_number", "state_id"],
                    "validation": ["ssn_format", "date_format", "state_code"],
                },
                "gun": {
                    "required_fields": ["query_type", "requesting_agency_ori", "requesting_officer"],
                    "search_fields": ["serial_number", "make", "model"],
                    "validation": ["serial_number_recommended"],
                },
            },
            "cjis_compliance": {
                "area_5_access_control": "enforced",
                "area_7_encryption": "ready",
                "area_8_auditing": "active",
                "area_10_system_protection": "enforced",
            },
            "total_stub_queries": len(self.queries),
        }

    def format_ncic_message(
        self,
        query: NCICQueryRequest,
    ) -> str:
        """Format query as NCIC-style message (for demonstration)"""
        lines = [
            f"MKE/{query.query_type.value.upper()}",
            f"ORI/{query.requesting_agency_ori}",
            f"NAM/{query.requesting_officer}",
        ]

        for key, value in query.query_params.items():
            if value:
                field_code = self._get_ncic_field_code(key)
                lines.append(f"{field_code}/{value}")

        lines.append(f"PUR/{query.purpose}")
        lines.append("EOM")

        return "\n".join(lines)

    def _get_ncic_field_code(self, field_name: str) -> str:
        """Map field name to NCIC field code"""
        field_codes = {
            "vin": "VIN",
            "license_plate": "LIC",
            "license_state": "LIS",
            "make": "MAK",
            "model": "MOD",
            "year": "VYR",
            "color": "VCO",
            "last_name": "NAM",
            "first_name": "NAM",
            "date_of_birth": "DOB",
            "sex": "SEX",
            "race": "RAC",
            "ssn": "SOC",
            "drivers_license": "OLN",
            "drivers_license_state": "OLS",
            "fbi_number": "FBI",
            "serial_number": "SER",
            "caliber": "CAL",
            "gun_type": "TYP",
        }
        return field_codes.get(field_name, field_name.upper()[:3])


# Create singleton instance
ncic_query_manager = NCICQueryManager(
    audit_logger=FederalAuditLogger(),
)
