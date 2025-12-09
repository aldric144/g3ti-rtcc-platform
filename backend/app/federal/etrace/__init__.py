"""
G3TI RTCC-UIP ATF eTrace Firearms Intelligence Export
Phase 11: ATF eTrace trace request generation and export functionality
"""

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import uuid4

from app.federal.common import (
    FederalAuditLogger,
    FederalExportStatus,
    FederalMessagePackage,
    FederalMessageType,
    FederalSchema,
    FederalSystem,
    FederalValidationResult,
    FederalValidator,
)


class ETraceRequestType(str, Enum):
    """eTrace request types"""
    TRACE_REQUEST = "trace_request"
    MULTIPLE_SALES = "multiple_sales"
    SUSPECT_GUN = "suspect_gun"
    TIME_TO_CRIME = "time_to_crime"
    INTERSTATE = "interstate"


class ETraceRecoveryType(str, Enum):
    """eTrace firearm recovery types"""
    CRIME_GUN = "crime_gun"
    FOUND_FIREARM = "found_firearm"
    SAFEKEEPING = "safekeeping"
    VOLUNTARY_SURRENDER = "voluntary_surrender"
    BUYBACK = "buyback"
    OTHER = "other"


class ETraceFirearmType(str, Enum):
    """eTrace firearm types"""
    PISTOL = "pistol"
    REVOLVER = "revolver"
    RIFLE = "rifle"
    SHOTGUN = "shotgun"
    DERRINGER = "derringer"
    MACHINE_GUN = "machine_gun"
    SUBMACHINE_GUN = "submachine_gun"
    SILENCER = "silencer"
    DESTRUCTIVE_DEVICE = "destructive_device"
    ANY_OTHER_WEAPON = "any_other_weapon"
    UNKNOWN = "unknown"


class ETraceFirearmCondition(str, Enum):
    """eTrace firearm condition"""
    NEW = "new"
    USED = "used"
    DAMAGED = "damaged"
    DESTROYED = "destroyed"
    UNKNOWN = "unknown"


class ETraceTraceSchema(FederalSchema):
    """ATF eTrace Trace Request schema"""

    def __init__(self):
        super().__init__(
            schema_name="ATF_eTrace_Request",
            schema_version="1.0",
            federal_system=FederalSystem.ETRACE,
            required_fields=[
                "trace_id",
                "requesting_agency_ori",
                "requesting_officer",
                "recovery_date",
                "recovery_location",
                "firearm_type",
            ],
            optional_fields=[
                "serial_number",
                "make",
                "model",
                "caliber",
                "barrel_length",
                "importer",
                "country_of_origin",
                "firearm_condition",
                "recovery_type",
                "crime_code",
                "possessor_info",
                "incident_id",
                "case_number",
                "additional_marks",
                "obliterated_serial",
            ],
            sensitive_fields=[
                "serial_number",
                "possessor_info",
            ],
        )


class ETraceFirearmData:
    """eTrace firearm data structure"""

    def __init__(
        self,
        firearm_type: ETraceFirearmType,
        serial_number: str | None = None,
        make: str | None = None,
        model: str | None = None,
        caliber: str | None = None,
        barrel_length: str | None = None,
        importer: str | None = None,
        country_of_origin: str | None = None,
        condition: ETraceFirearmCondition = ETraceFirearmCondition.UNKNOWN,
        additional_marks: str | None = None,
        obliterated_serial: bool = False,
    ):
        self.id = str(uuid4())
        self.firearm_type = firearm_type
        self.serial_number = serial_number
        self.make = make
        self.model = model
        self.caliber = caliber
        self.barrel_length = barrel_length
        self.importer = importer
        self.country_of_origin = country_of_origin
        self.condition = condition
        self.additional_marks = additional_marks
        self.obliterated_serial = obliterated_serial

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "firearm_type": self.firearm_type.value,
            "serial_number": self.serial_number,
            "make": self.make,
            "model": self.model,
            "caliber": self.caliber,
            "barrel_length": self.barrel_length,
            "importer": self.importer,
            "country_of_origin": self.country_of_origin,
            "condition": self.condition.value,
            "additional_marks": self.additional_marks,
            "obliterated_serial": self.obliterated_serial,
        }


class ETraceRecoveryData:
    """eTrace recovery data structure"""

    def __init__(
        self,
        recovery_date: str,
        recovery_type: ETraceRecoveryType,
        street_address: str | None = None,
        city: str | None = None,
        state: str | None = None,
        zip_code: str | None = None,
        county: str | None = None,
        latitude: float | None = None,
        longitude: float | None = None,
        location_description: str | None = None,
    ):
        self.id = str(uuid4())
        self.recovery_date = recovery_date
        self.recovery_type = recovery_type
        self.street_address = street_address
        self.city = city
        self.state = state
        self.zip_code = zip_code
        self.county = county
        self.latitude = latitude
        self.longitude = longitude
        self.location_description = location_description

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "recovery_date": self.recovery_date,
            "recovery_type": self.recovery_type.value,
            "street_address": self.street_address,
            "city": self.city,
            "state": self.state,
            "zip_code": self.zip_code,
            "county": self.county,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "location_description": self.location_description,
        }


class ETracePossessorData:
    """eTrace possessor data structure"""

    def __init__(
        self,
        last_name: str | None = None,
        first_name: str | None = None,
        middle_name: str | None = None,
        date_of_birth: str | None = None,
        sex: str | None = None,
        race: str | None = None,
        address: str | None = None,
        city: str | None = None,
        state: str | None = None,
        zip_code: str | None = None,
        relationship_to_crime: str | None = None,
    ):
        self.id = str(uuid4())
        self.last_name = last_name
        self.first_name = first_name
        self.middle_name = middle_name
        self.date_of_birth = date_of_birth
        self.sex = sex
        self.race = race
        self.address = address
        self.city = city
        self.state = state
        self.zip_code = zip_code
        self.relationship_to_crime = relationship_to_crime

    def to_dict(self, mask_sensitive: bool = True) -> dict[str, Any]:
        """Convert to dictionary with optional masking"""
        data = {
            "id": self.id,
            "last_name": self.last_name.upper() if self.last_name else None,
            "first_name": self.first_name.upper() if self.first_name else None,
            "middle_name": self.middle_name.upper() if self.middle_name else None,
            "sex": self.sex,
            "race": self.race,
            "relationship_to_crime": self.relationship_to_crime,
        }

        if mask_sensitive:
            # Mask DOB
            if self.date_of_birth:
                data["date_of_birth"] = f"****-**-{self.date_of_birth[-2:]}" if len(self.date_of_birth) >= 2 else "****"
            # Mask address
            if self.address:
                data["address"] = "*** REDACTED ***"
            data["city"] = self.city
            data["state"] = self.state
            data["zip_code"] = self.zip_code[:3] + "**" if self.zip_code and len(self.zip_code) >= 3 else self.zip_code
        else:
            data["date_of_birth"] = self.date_of_birth
            data["address"] = self.address
            data["city"] = self.city
            data["state"] = self.state
            data["zip_code"] = self.zip_code

        return data


class ETraceRequest:
    """eTrace trace request"""

    def __init__(
        self,
        requesting_agency_ori: str,
        requesting_officer: str,
        firearm_data: ETraceFirearmData,
        recovery_data: ETraceRecoveryData,
        crime_code: str | None = None,
        incident_id: str | None = None,
        case_number: str | None = None,
        possessor_data: ETracePossessorData | None = None,
        request_type: ETraceRequestType = ETraceRequestType.TRACE_REQUEST,
        notes: str | None = None,
    ):
        self.id = str(uuid4())
        self.trace_number = f"TR-{datetime.utcnow().strftime('%Y%m%d')}-{self.id[:8].upper()}"
        self.requesting_agency_ori = requesting_agency_ori
        self.requesting_officer = requesting_officer
        self.firearm_data = firearm_data
        self.recovery_data = recovery_data
        self.crime_code = crime_code
        self.incident_id = incident_id
        self.case_number = case_number
        self.possessor_data = possessor_data
        self.request_type = request_type
        self.notes = notes
        self.created_at = datetime.utcnow()
        self.status = FederalExportStatus.PENDING
        self.validation_result: FederalValidationResult | None = None

    def to_dict(self, mask_sensitive: bool = True) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "trace_number": self.trace_number,
            "requesting_agency_ori": self.requesting_agency_ori,
            "requesting_officer": self.requesting_officer,
            "request_type": self.request_type.value,
            "firearm": self.firearm_data.to_dict(),
            "recovery": self.recovery_data.to_dict(),
            "crime_code": self.crime_code,
            "incident_id": self.incident_id,
            "case_number": self.case_number,
            "possessor": self.possessor_data.to_dict(mask_sensitive) if self.possessor_data else None,
            "notes": self.notes,
            "created_at": self.created_at.isoformat(),
            "status": self.status.value,
        }


class ETraceReport:
    """eTrace trace report (export format)"""

    def __init__(
        self,
        trace_request: ETraceRequest,
        agency_id: str,
        user_id: str,
    ):
        self.id = str(uuid4())
        self.report_number = f"RPT-{datetime.utcnow().strftime('%Y%m%d')}-{self.id[:8].upper()}"
        self.trace_request = trace_request
        self.agency_id = agency_id
        self.user_id = user_id
        self.created_at = datetime.utcnow()
        self.export_format = "etrace_json_v1"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "report_number": self.report_number,
            "trace_request": self.trace_request.to_dict(),
            "agency_id": self.agency_id,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat(),
            "export_format": self.export_format,
        }


class ETraceDataMapper:
    """Maps internal data to eTrace format"""

    def __init__(self):
        self.validator = FederalValidator()
        self.validator.add_rule("recovery_date", FederalValidator.validate_date)
        self.validator.add_rule("date_of_birth", FederalValidator.validate_date)
        self.validator.add_rule("state", FederalValidator.validate_state_code)

    def map_firearm_type(self, weapon_type: str | None) -> ETraceFirearmType:
        """Map internal weapon type to eTrace firearm type"""
        if not weapon_type:
            return ETraceFirearmType.UNKNOWN

        type_lower = weapon_type.lower()
        type_mapping = {
            "pistol": ETraceFirearmType.PISTOL,
            "handgun": ETraceFirearmType.PISTOL,
            "semi-auto": ETraceFirearmType.PISTOL,
            "revolver": ETraceFirearmType.REVOLVER,
            "rifle": ETraceFirearmType.RIFLE,
            "shotgun": ETraceFirearmType.SHOTGUN,
            "derringer": ETraceFirearmType.DERRINGER,
            "machine": ETraceFirearmType.MACHINE_GUN,
            "submachine": ETraceFirearmType.SUBMACHINE_GUN,
            "smg": ETraceFirearmType.SUBMACHINE_GUN,
            "silencer": ETraceFirearmType.SILENCER,
            "suppressor": ETraceFirearmType.SILENCER,
        }

        for key, firearm_type in type_mapping.items():
            if key in type_lower:
                return firearm_type

        return ETraceFirearmType.UNKNOWN

    def map_recovery_type(self, recovery_context: str | None) -> ETraceRecoveryType:
        """Map recovery context to eTrace recovery type"""
        if not recovery_context:
            return ETraceRecoveryType.CRIME_GUN

        context_lower = recovery_context.lower()
        if "found" in context_lower:
            return ETraceRecoveryType.FOUND_FIREARM
        elif "safekeeping" in context_lower:
            return ETraceRecoveryType.SAFEKEEPING
        elif "surrender" in context_lower or "voluntary" in context_lower:
            return ETraceRecoveryType.VOLUNTARY_SURRENDER
        elif "buyback" in context_lower:
            return ETraceRecoveryType.BUYBACK
        elif "crime" in context_lower or "evidence" in context_lower:
            return ETraceRecoveryType.CRIME_GUN

        return ETraceRecoveryType.OTHER

    def map_firearm_from_internal(
        self,
        weapon_data: dict[str, Any],
    ) -> ETraceFirearmData:
        """Map internal weapon data to eTrace firearm data"""
        return ETraceFirearmData(
            firearm_type=self.map_firearm_type(
                weapon_data.get("type") or weapon_data.get("weapon_type"),
            ),
            serial_number=weapon_data.get("serial_number"),
            make=weapon_data.get("make") or weapon_data.get("manufacturer"),
            model=weapon_data.get("model"),
            caliber=weapon_data.get("caliber"),
            barrel_length=weapon_data.get("barrel_length"),
            importer=weapon_data.get("importer"),
            country_of_origin=weapon_data.get("country_of_origin") or weapon_data.get("origin"),
            condition=ETraceFirearmCondition(
                weapon_data.get("condition", "unknown"),
            ) if weapon_data.get("condition") in [e.value for e in ETraceFirearmCondition] else ETraceFirearmCondition.UNKNOWN,
            additional_marks=weapon_data.get("additional_marks") or weapon_data.get("markings"),
            obliterated_serial=weapon_data.get("obliterated_serial", False),
        )

    def map_recovery_from_internal(
        self,
        recovery_data: dict[str, Any],
    ) -> ETraceRecoveryData:
        """Map internal recovery data to eTrace recovery data"""
        return ETraceRecoveryData(
            recovery_date=recovery_data.get("recovery_date") or recovery_data.get("date") or datetime.utcnow().strftime("%Y-%m-%d"),
            recovery_type=self.map_recovery_type(recovery_data.get("recovery_type") or recovery_data.get("context")),
            street_address=recovery_data.get("street") or recovery_data.get("address"),
            city=recovery_data.get("city"),
            state=recovery_data.get("state"),
            zip_code=recovery_data.get("zip_code") or recovery_data.get("zip"),
            county=recovery_data.get("county"),
            latitude=recovery_data.get("latitude") or recovery_data.get("lat"),
            longitude=recovery_data.get("longitude") or recovery_data.get("lng") or recovery_data.get("lon"),
            location_description=recovery_data.get("description") or recovery_data.get("location_description"),
        )

    def map_possessor_from_internal(
        self,
        person_data: dict[str, Any],
    ) -> ETracePossessorData:
        """Map internal person data to eTrace possessor data"""
        return ETracePossessorData(
            last_name=person_data.get("last_name"),
            first_name=person_data.get("first_name"),
            middle_name=person_data.get("middle_name"),
            date_of_birth=person_data.get("date_of_birth") or person_data.get("dob"),
            sex=person_data.get("sex") or person_data.get("gender"),
            race=person_data.get("race"),
            address=person_data.get("address") or person_data.get("street"),
            city=person_data.get("city"),
            state=person_data.get("state"),
            zip_code=person_data.get("zip_code") or person_data.get("zip"),
            relationship_to_crime=person_data.get("role") or person_data.get("relationship"),
        )

    def normalize_caliber(self, caliber: str | None) -> str | None:
        """Normalize caliber format"""
        if not caliber:
            return None

        # Common caliber normalizations
        caliber_map = {
            "9mm": "9MM",
            "9 mm": "9MM",
            ".45": ".45 ACP",
            "45": ".45 ACP",
            ".40": ".40 S&W",
            "40": ".40 S&W",
            ".380": ".380 ACP",
            "380": ".380 ACP",
            ".22": ".22 LR",
            "22": ".22 LR",
            ".38": ".38 SPL",
            "38": ".38 SPL",
            ".357": ".357 MAG",
            "357": ".357 MAG",
            "5.56": "5.56MM",
            ".223": ".223 REM",
            "223": ".223 REM",
            "7.62": "7.62MM",
            ".308": ".308 WIN",
            "308": ".308 WIN",
            "12ga": "12 GA",
            "12 gauge": "12 GA",
            "20ga": "20 GA",
            "20 gauge": "20 GA",
        }

        caliber_lower = caliber.lower().strip()
        return caliber_map.get(caliber_lower, caliber.upper())


class ETraceExportManager:
    """Manager for ATF eTrace exports"""

    def __init__(self, audit_logger: FederalAuditLogger):
        self.audit_logger = audit_logger
        self.mapper = ETraceDataMapper()
        self.trace_requests: dict[str, ETraceRequest] = {}
        self.reports: dict[str, ETraceReport] = {}
        self.schema = ETraceTraceSchema()

    def create_trace_request(
        self,
        weapon_data: dict[str, Any],
        recovery_data: dict[str, Any],
        agency_ori: str,
        officer_name: str,
        user_id: str,
        crime_code: str | None = None,
        incident_id: str | None = None,
        case_number: str | None = None,
        possessor_data: dict[str, Any] | None = None,
        request_type: ETraceRequestType = ETraceRequestType.TRACE_REQUEST,
        notes: str | None = None,
    ) -> ETraceRequest:
        """Create an eTrace trace request"""
        # Map data
        firearm = self.mapper.map_firearm_from_internal(weapon_data)
        recovery = self.mapper.map_recovery_from_internal(recovery_data)
        possessor = self.mapper.map_possessor_from_internal(possessor_data) if possessor_data else None

        # Normalize caliber
        if firearm.caliber:
            firearm.caliber = self.mapper.normalize_caliber(firearm.caliber)

        # Create request
        request = ETraceRequest(
            requesting_agency_ori=agency_ori,
            requesting_officer=officer_name,
            firearm_data=firearm,
            recovery_data=recovery,
            crime_code=crime_code,
            incident_id=incident_id,
            case_number=case_number,
            possessor_data=possessor,
            request_type=request_type,
            notes=notes,
        )

        # Validate
        validation = self._validate_request(request)
        request.validation_result = validation

        if validation.is_valid:
            request.status = FederalExportStatus.VALIDATED
        else:
            request.status = FederalExportStatus.FAILED

        # Log
        self.audit_logger.log_etrace_export(
            agency_id=agency_ori,
            user_id=user_id,
            user_name=officer_name,
            weapon_id=firearm.id,
            incident_id=incident_id,
        )

        self.trace_requests[request.id] = request
        return request

    def export_weapon(
        self,
        weapon_id: str,
        weapon_data: dict[str, Any],
        recovery_data: dict[str, Any],
        agency_id: str,
        user_id: str,
        user_name: str,
    ) -> FederalMessagePackage:
        """Export weapon to eTrace format"""
        # Create trace request
        request = self.create_trace_request(
            weapon_data=weapon_data,
            recovery_data=recovery_data,
            agency_ori=agency_id,
            officer_name=user_name,
            user_id=user_id,
            incident_id=weapon_data.get("incident_id"),
        )

        # Create message package
        package = FederalMessagePackage(
            message_type=FederalMessageType.ETRACE_REQUEST,
            federal_system=FederalSystem.ETRACE,
            payload=request.to_dict(),
            originating_agency=agency_id,
            originating_user=user_id,
        )

        if request.validation_result and request.validation_result.is_valid:
            package.status = FederalExportStatus.READY
        else:
            package.status = FederalExportStatus.FAILED

        return package

    def export_incident_weapons(
        self,
        incident_id: str,
        incident_data: dict[str, Any],
        agency_id: str,
        user_id: str,
        user_name: str,
    ) -> list[FederalMessagePackage]:
        """Export all weapons from an incident to eTrace format"""
        packages = []

        weapons = incident_data.get("weapons") or incident_data.get("firearms") or []
        recovery_data = {
            "recovery_date": incident_data.get("date") or incident_data.get("incident_date"),
            "city": incident_data.get("city"),
            "state": incident_data.get("state"),
            "street": incident_data.get("address") or incident_data.get("location"),
            "context": "crime",
        }

        # Get location from incident
        if incident_data.get("location"):
            loc = incident_data["location"]
            if isinstance(loc, dict):
                recovery_data.update({
                    "street": loc.get("street") or loc.get("address"),
                    "city": loc.get("city"),
                    "state": loc.get("state"),
                    "zip_code": loc.get("zip_code") or loc.get("zip"),
                    "latitude": loc.get("latitude") or loc.get("lat"),
                    "longitude": loc.get("longitude") or loc.get("lng"),
                })

        for weapon in weapons:
            weapon["incident_id"] = incident_id
            package = self.export_weapon(
                weapon_id=weapon.get("id") or str(uuid4()),
                weapon_data=weapon,
                recovery_data=recovery_data,
                agency_id=agency_id,
                user_id=user_id,
                user_name=user_name,
            )
            packages.append(package)

        return packages

    def generate_report(
        self,
        trace_request_id: str,
        agency_id: str,
        user_id: str,
    ) -> ETraceReport | None:
        """Generate eTrace report from trace request"""
        request = self.trace_requests.get(trace_request_id)
        if not request:
            return None

        report = ETraceReport(
            trace_request=request,
            agency_id=agency_id,
            user_id=user_id,
        )

        self.reports[report.id] = report
        return report

    def get_trace_request(self, request_id: str) -> ETraceRequest | None:
        """Get trace request by ID"""
        return self.trace_requests.get(request_id)

    def get_report(self, report_id: str) -> ETraceReport | None:
        """Get report by ID"""
        return self.reports.get(report_id)

    def get_requests_by_agency(
        self,
        agency_ori: str,
        limit: int = 100,
    ) -> list[ETraceRequest]:
        """Get trace requests for an agency"""
        requests = [
            r for r in self.trace_requests.values()
            if r.requesting_agency_ori == agency_ori
        ]
        requests.sort(key=lambda r: r.created_at, reverse=True)
        return requests[:limit]

    def get_requests_by_incident(
        self,
        incident_id: str,
    ) -> list[ETraceRequest]:
        """Get trace requests for an incident"""
        return [
            r for r in self.trace_requests.values()
            if r.incident_id == incident_id
        ]

    def _validate_request(
        self,
        request: ETraceRequest,
    ) -> FederalValidationResult:
        """Validate trace request"""
        errors = []
        warnings = []

        # Check required fields
        if not request.requesting_agency_ori:
            errors.append("Requesting agency ORI is required")
        if not request.requesting_officer:
            errors.append("Requesting officer is required")
        if not request.recovery_data.recovery_date:
            errors.append("Recovery date is required")

        # Validate firearm data
        firearm = request.firearm_data
        if not firearm.serial_number and not firearm.obliterated_serial:
            warnings.append("Serial number is recommended for accurate tracing")
        if not firearm.make:
            warnings.append("Firearm make is recommended")
        if not firearm.model:
            warnings.append("Firearm model is recommended")

        # Validate recovery location
        recovery = request.recovery_data
        if not recovery.city and not recovery.state:
            errors.append("Recovery location (city/state) is required")

        # Validate state code
        if recovery.state:
            state_result = FederalValidator.validate_state_code(recovery.state)
            if state_result is not True:
                errors.append(f"Invalid recovery state: {state_result}")

        # Validate date
        if recovery.recovery_date:
            date_result = FederalValidator.validate_date(recovery.recovery_date)
            if date_result is not True:
                errors.append(f"Invalid recovery date: {date_result}")

        return FederalValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            validated_data=request.to_dict() if len(errors) == 0 else None,
        )

    def get_statistics(
        self,
        agency_ori: str | None = None,
    ) -> dict[str, Any]:
        """Get eTrace export statistics"""
        requests = list(self.trace_requests.values())
        if agency_ori:
            requests = [r for r in requests if r.requesting_agency_ori == agency_ori]

        stats = {
            "total_requests": len(requests),
            "by_status": {},
            "by_firearm_type": {},
            "by_recovery_type": {},
            "validated": 0,
            "failed": 0,
        }

        for request in requests:
            # Count by status
            status = request.status.value
            stats["by_status"][status] = stats["by_status"].get(status, 0) + 1

            # Count by firearm type
            firearm_type = request.firearm_data.firearm_type.value
            stats["by_firearm_type"][firearm_type] = (
                stats["by_firearm_type"].get(firearm_type, 0) + 1
            )

            # Count by recovery type
            recovery_type = request.recovery_data.recovery_type.value
            stats["by_recovery_type"][recovery_type] = (
                stats["by_recovery_type"].get(recovery_type, 0) + 1
            )

            # Count validated/failed
            if request.status == FederalExportStatus.VALIDATED:
                stats["validated"] += 1
            elif request.status == FederalExportStatus.FAILED:
                stats["failed"] += 1

        return stats


# Create singleton instance
etrace_export_manager = ETraceExportManager(
    audit_logger=FederalAuditLogger(),
)
