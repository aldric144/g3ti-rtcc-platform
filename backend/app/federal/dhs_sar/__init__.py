"""
G3TI RTCC-UIP DHS Suspicious Activity Reporting (SAR)
Phase 11: ISE-SAR Functional Standard v1.5 mapping and submission framework
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


class SARBehaviorCategory(str, Enum):
    """ISE-SAR Behavior Categories"""
    ACQUISITION_EXPERTISE = "acquisition_expertise"
    BREACH_INTRUSION = "breach_intrusion"
    ELICITATION = "elicitation"
    MISREPRESENTATION = "misrepresentation"
    OBSERVATION_SURVEILLANCE = "observation_surveillance"
    PHOTOGRAPHY = "photography"
    SABOTAGE_TAMPERING = "sabotage_tampering"
    SECTOR_SPECIFIC = "sector_specific"
    TESTING_SECURITY = "testing_security"
    THEFT_LOSS = "theft_loss"
    WEAPONS_EXPLOSIVES = "weapons_explosives"
    CYBER_ATTACK = "cyber_attack"
    AVIATION = "aviation"
    CHEMICAL_BIOLOGICAL = "chemical_biological"
    CRITICAL_INFRASTRUCTURE = "critical_infrastructure"
    EXPRESSED_THREAT = "expressed_threat"
    FINANCING = "financing"
    MATERIALS_ACQUISITION = "materials_acquisition"
    RECRUITING = "recruiting"
    OTHER = "other"


class SARBehaviorIndicator(str, Enum):
    """ISE-SAR Behavior Indicators"""
    # Acquisition/Expertise
    ACQUIRING_EXPERTISE = "acquiring_expertise"
    ACQUIRING_SUPPLIES = "acquiring_supplies"
    ACQUIRING_UNIFORMS = "acquiring_uniforms"
    ACQUIRING_CREDENTIALS = "acquiring_credentials"

    # Breach/Intrusion
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    TRESPASSING = "trespassing"
    FORCED_ENTRY = "forced_entry"

    # Elicitation
    QUESTIONING_EMPLOYEES = "questioning_employees"
    QUESTIONING_SECURITY = "questioning_security"
    SEEKING_INFO_OPERATIONS = "seeking_info_operations"

    # Observation/Surveillance
    PHOTOGRAPHING_FACILITIES = "photographing_facilities"
    RECORDING_ACTIVITIES = "recording_activities"
    MONITORING_PERSONNEL = "monitoring_personnel"
    TIMING_OPERATIONS = "timing_operations"
    MAPPING_ROUTES = "mapping_routes"

    # Testing Security
    PROBING_SECURITY = "probing_security"
    TESTING_RESPONSE = "testing_response"
    ATTEMPTING_ACCESS = "attempting_access"

    # Weapons/Explosives
    WEAPONS_DISCOVERY = "weapons_discovery"
    EXPLOSIVES_DISCOVERY = "explosives_discovery"
    BOMB_THREAT = "bomb_threat"
    SUSPICIOUS_PACKAGE = "suspicious_package"

    # Cyber
    NETWORK_INTRUSION = "network_intrusion"
    MALWARE_DISCOVERY = "malware_discovery"
    PHISHING_ATTEMPT = "phishing_attempt"

    # Expressed Threat
    VERBAL_THREAT = "verbal_threat"
    WRITTEN_THREAT = "written_threat"
    ONLINE_THREAT = "online_threat"

    # Other
    SUSPICIOUS_BEHAVIOR = "suspicious_behavior"
    UNUSUAL_ACTIVITY = "unusual_activity"
    OTHER = "other"


class SARThreatLevel(str, Enum):
    """SAR Threat Assessment Levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"


class SARStatus(str, Enum):
    """SAR Status"""
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    SUBMITTED = "submitted"
    REJECTED = "rejected"
    ARCHIVED = "archived"


class SARSubjectType(str, Enum):
    """SAR Subject Types"""
    INDIVIDUAL = "individual"
    ORGANIZATION = "organization"
    VEHICLE = "vehicle"
    UNKNOWN = "unknown"


class SARSchema(FederalSchema):
    """DHS SAR schema based on ISE-SAR Functional Standard v1.5"""

    def __init__(self):
        super().__init__(
            schema_name="DHS_SAR_ISE_v1.5",
            schema_version="1.5",
            federal_system=FederalSystem.DHS_SAR,
            required_fields=[
                "sar_id",
                "reporting_agency_ori",
                "reporting_officer",
                "behavior_category",
                "activity_date",
                "activity_location",
                "narrative",
            ],
            optional_fields=[
                "behavior_indicators",
                "subject_info",
                "vehicle_info",
                "threat_assessment",
                "related_incidents",
                "supporting_documents",
                "witness_info",
                "additional_notes",
            ],
            sensitive_fields=[
                "subject_info",
                "witness_info",
                "narrative",
            ],
        )


class SARSubject:
    """SAR Subject information"""

    def __init__(
        self,
        subject_type: SARSubjectType = SARSubjectType.INDIVIDUAL,
        last_name: str | None = None,
        first_name: str | None = None,
        middle_name: str | None = None,
        date_of_birth: str | None = None,
        sex: str | None = None,
        race: str | None = None,
        height: str | None = None,
        weight: str | None = None,
        hair_color: str | None = None,
        eye_color: str | None = None,
        identifying_marks: str | None = None,
        clothing_description: str | None = None,
        organization_name: str | None = None,
        address: str | None = None,
        city: str | None = None,
        state: str | None = None,
        zip_code: str | None = None,
        phone: str | None = None,
        email: str | None = None,
        additional_info: str | None = None,
    ):
        self.id = str(uuid4())
        self.subject_type = subject_type
        self.last_name = last_name
        self.first_name = first_name
        self.middle_name = middle_name
        self.date_of_birth = date_of_birth
        self.sex = sex
        self.race = race
        self.height = height
        self.weight = weight
        self.hair_color = hair_color
        self.eye_color = eye_color
        self.identifying_marks = identifying_marks
        self.clothing_description = clothing_description
        self.organization_name = organization_name
        self.address = address
        self.city = city
        self.state = state
        self.zip_code = zip_code
        self.phone = phone
        self.email = email
        self.additional_info = additional_info

    def to_dict(self, mask_sensitive: bool = True) -> dict[str, Any]:
        """Convert to dictionary with optional masking"""
        data = {
            "id": self.id,
            "subject_type": self.subject_type.value,
            "last_name": self.last_name.upper() if self.last_name else None,
            "first_name": self.first_name.upper() if self.first_name else None,
            "middle_name": self.middle_name.upper() if self.middle_name else None,
            "sex": self.sex,
            "race": self.race,
            "height": self.height,
            "weight": self.weight,
            "hair_color": self.hair_color,
            "eye_color": self.eye_color,
            "identifying_marks": self.identifying_marks,
            "clothing_description": self.clothing_description,
            "organization_name": self.organization_name,
            "city": self.city,
            "state": self.state,
            "additional_info": self.additional_info,
        }

        if mask_sensitive:
            # Mask DOB
            if self.date_of_birth:
                data["date_of_birth"] = f"****-**-{self.date_of_birth[-2:]}" if len(self.date_of_birth) >= 2 else "****"
            # Mask address
            data["address"] = "*** REDACTED ***" if self.address else None
            data["zip_code"] = self.zip_code[:3] + "**" if self.zip_code and len(self.zip_code) >= 3 else self.zip_code
            data["phone"] = "*** REDACTED ***" if self.phone else None
            data["email"] = "*** REDACTED ***" if self.email else None
        else:
            data["date_of_birth"] = self.date_of_birth
            data["address"] = self.address
            data["zip_code"] = self.zip_code
            data["phone"] = self.phone
            data["email"] = self.email

        return data


class SARVehicle:
    """SAR Vehicle information"""

    def __init__(
        self,
        make: str | None = None,
        model: str | None = None,
        year: str | None = None,
        color: str | None = None,
        license_plate: str | None = None,
        license_state: str | None = None,
        vin: str | None = None,
        vehicle_type: str | None = None,
        distinguishing_features: str | None = None,
    ):
        self.id = str(uuid4())
        self.make = make
        self.model = model
        self.year = year
        self.color = color
        self.license_plate = license_plate
        self.license_state = license_state
        self.vin = vin
        self.vehicle_type = vehicle_type
        self.distinguishing_features = distinguishing_features

    def to_dict(self, mask_sensitive: bool = True) -> dict[str, Any]:
        """Convert to dictionary with optional masking"""
        data = {
            "id": self.id,
            "make": self.make,
            "model": self.model,
            "year": self.year,
            "color": self.color,
            "vehicle_type": self.vehicle_type,
            "distinguishing_features": self.distinguishing_features,
        }

        if mask_sensitive:
            data["license_plate"] = self._mask_plate(self.license_plate)
            data["license_state"] = self.license_state
            data["vin"] = self._mask_vin(self.vin)
        else:
            data["license_plate"] = self.license_plate
            data["license_state"] = self.license_state
            data["vin"] = self.vin

        return data

    def _mask_plate(self, plate: str | None) -> str | None:
        """Mask license plate"""
        if not plate:
            return None
        if len(plate) <= 3:
            return "***"
        return "***" + plate[-3:]

    def _mask_vin(self, vin: str | None) -> str | None:
        """Mask VIN"""
        if not vin:
            return None
        if len(vin) <= 4:
            return "****"
        return "*" * (len(vin) - 4) + vin[-4:]


class SARLocation:
    """SAR Location information"""

    def __init__(
        self,
        street_address: str | None = None,
        city: str | None = None,
        state: str | None = None,
        zip_code: str | None = None,
        county: str | None = None,
        country: str = "US",
        latitude: float | None = None,
        longitude: float | None = None,
        location_type: str | None = None,
        location_name: str | None = None,
        location_description: str | None = None,
    ):
        self.id = str(uuid4())
        self.street_address = street_address
        self.city = city
        self.state = state
        self.zip_code = zip_code
        self.county = county
        self.country = country
        self.latitude = latitude
        self.longitude = longitude
        self.location_type = location_type
        self.location_name = location_name
        self.location_description = location_description

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "street_address": self.street_address,
            "city": self.city,
            "state": self.state,
            "zip_code": self.zip_code,
            "county": self.county,
            "country": self.country,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "location_type": self.location_type,
            "location_name": self.location_name,
            "location_description": self.location_description,
        }


class SARReport:
    """Suspicious Activity Report"""

    def __init__(
        self,
        reporting_agency_ori: str,
        reporting_officer: str,
        behavior_category: SARBehaviorCategory,
        activity_date: str,
        activity_time: str | None,
        activity_location: SARLocation,
        narrative: str,
        behavior_indicators: list[SARBehaviorIndicator] | None = None,
        subjects: list[SARSubject] | None = None,
        vehicles: list[SARVehicle] | None = None,
        threat_assessment: SARThreatLevel = SARThreatLevel.UNKNOWN,
        related_incidents: list[str] | None = None,
        supporting_documents: list[str] | None = None,
        additional_notes: str | None = None,
    ):
        self.id = str(uuid4())
        self.sar_number = f"SAR-{datetime.utcnow().strftime('%Y%m%d')}-{self.id[:8].upper()}"
        self.reporting_agency_ori = reporting_agency_ori
        self.reporting_officer = reporting_officer
        self.behavior_category = behavior_category
        self.behavior_indicators = behavior_indicators or []
        self.activity_date = activity_date
        self.activity_time = activity_time
        self.activity_location = activity_location
        self.narrative = narrative
        self.subjects = subjects or []
        self.vehicles = vehicles or []
        self.threat_assessment = threat_assessment
        self.related_incidents = related_incidents or []
        self.supporting_documents = supporting_documents or []
        self.additional_notes = additional_notes
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.status = SARStatus.DRAFT
        self.validation_result: FederalValidationResult | None = None
        self.submitted_at: datetime | None = None
        self.approved_by: str | None = None
        self.approved_at: datetime | None = None

    def to_dict(self, mask_sensitive: bool = True) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "sar_number": self.sar_number,
            "reporting_agency_ori": self.reporting_agency_ori,
            "reporting_officer": self.reporting_officer,
            "behavior_category": self.behavior_category.value,
            "behavior_indicators": [bi.value for bi in self.behavior_indicators],
            "activity_date": self.activity_date,
            "activity_time": self.activity_time,
            "activity_location": self.activity_location.to_dict(),
            "narrative": self._sanitize_narrative(self.narrative) if mask_sensitive else self.narrative,
            "subjects": [s.to_dict(mask_sensitive) for s in self.subjects],
            "vehicles": [v.to_dict(mask_sensitive) for v in self.vehicles],
            "threat_assessment": self.threat_assessment.value,
            "related_incidents": self.related_incidents,
            "supporting_documents": self.supporting_documents,
            "additional_notes": self.additional_notes,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "status": self.status.value,
            "submitted_at": self.submitted_at.isoformat() if self.submitted_at else None,
            "approved_by": self.approved_by,
            "approved_at": self.approved_at.isoformat() if self.approved_at else None,
        }

    def _sanitize_narrative(self, narrative: str) -> str:
        """Sanitize narrative for export"""
        import re

        # Mask SSN patterns
        narrative = re.sub(r"\b\d{3}-\d{2}-\d{4}\b", "[SSN REDACTED]", narrative)

        # Mask phone patterns
        narrative = re.sub(
            r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",
            "[PHONE REDACTED]",
            narrative,
        )

        # Mask email patterns
        narrative = re.sub(
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
            "[EMAIL REDACTED]",
            narrative,
        )

        return narrative


class SARDataMapper:
    """Maps internal data to SAR format"""

    def __init__(self):
        self.validator = FederalValidator()
        self.validator.add_rule("activity_date", FederalValidator.validate_date)
        self.validator.add_rule("date_of_birth", FederalValidator.validate_date)
        self.validator.add_rule("state", FederalValidator.validate_state_code)
        self.validator.add_rule("license_state", FederalValidator.validate_state_code)

    def map_behavior_category(
        self,
        activity_type: str | None,
    ) -> SARBehaviorCategory:
        """Map activity type to SAR behavior category"""
        if not activity_type:
            return SARBehaviorCategory.OTHER

        type_lower = activity_type.lower()
        category_mapping = {
            "surveillance": SARBehaviorCategory.OBSERVATION_SURVEILLANCE,
            "observation": SARBehaviorCategory.OBSERVATION_SURVEILLANCE,
            "watching": SARBehaviorCategory.OBSERVATION_SURVEILLANCE,
            "photography": SARBehaviorCategory.PHOTOGRAPHY,
            "photo": SARBehaviorCategory.PHOTOGRAPHY,
            "recording": SARBehaviorCategory.PHOTOGRAPHY,
            "breach": SARBehaviorCategory.BREACH_INTRUSION,
            "intrusion": SARBehaviorCategory.BREACH_INTRUSION,
            "trespass": SARBehaviorCategory.BREACH_INTRUSION,
            "elicitation": SARBehaviorCategory.ELICITATION,
            "questioning": SARBehaviorCategory.ELICITATION,
            "weapon": SARBehaviorCategory.WEAPONS_EXPLOSIVES,
            "explosive": SARBehaviorCategory.WEAPONS_EXPLOSIVES,
            "bomb": SARBehaviorCategory.WEAPONS_EXPLOSIVES,
            "cyber": SARBehaviorCategory.CYBER_ATTACK,
            "hack": SARBehaviorCategory.CYBER_ATTACK,
            "network": SARBehaviorCategory.CYBER_ATTACK,
            "threat": SARBehaviorCategory.EXPRESSED_THREAT,
            "threatening": SARBehaviorCategory.EXPRESSED_THREAT,
            "theft": SARBehaviorCategory.THEFT_LOSS,
            "stolen": SARBehaviorCategory.THEFT_LOSS,
            "sabotage": SARBehaviorCategory.SABOTAGE_TAMPERING,
            "tampering": SARBehaviorCategory.SABOTAGE_TAMPERING,
            "test": SARBehaviorCategory.TESTING_SECURITY,
            "probing": SARBehaviorCategory.TESTING_SECURITY,
            "aviation": SARBehaviorCategory.AVIATION,
            "aircraft": SARBehaviorCategory.AVIATION,
            "drone": SARBehaviorCategory.AVIATION,
            "chemical": SARBehaviorCategory.CHEMICAL_BIOLOGICAL,
            "biological": SARBehaviorCategory.CHEMICAL_BIOLOGICAL,
            "infrastructure": SARBehaviorCategory.CRITICAL_INFRASTRUCTURE,
            "utility": SARBehaviorCategory.CRITICAL_INFRASTRUCTURE,
            "financing": SARBehaviorCategory.FINANCING,
            "money": SARBehaviorCategory.FINANCING,
            "recruit": SARBehaviorCategory.RECRUITING,
        }

        for key, category in category_mapping.items():
            if key in type_lower:
                return category

        return SARBehaviorCategory.OTHER

    def map_threat_level(
        self,
        threat_info: str | None,
    ) -> SARThreatLevel:
        """Map threat information to SAR threat level"""
        if not threat_info:
            return SARThreatLevel.UNKNOWN

        threat_lower = threat_info.lower()
        if "critical" in threat_lower or "imminent" in threat_lower:
            return SARThreatLevel.CRITICAL
        elif "high" in threat_lower or "severe" in threat_lower:
            return SARThreatLevel.HIGH
        elif "medium" in threat_lower or "moderate" in threat_lower:
            return SARThreatLevel.MEDIUM
        elif "low" in threat_lower or "minor" in threat_lower:
            return SARThreatLevel.LOW

        return SARThreatLevel.UNKNOWN

    def map_subject_from_internal(
        self,
        person_data: dict[str, Any],
    ) -> SARSubject:
        """Map internal person data to SAR subject"""
        return SARSubject(
            subject_type=SARSubjectType.INDIVIDUAL,
            last_name=person_data.get("last_name"),
            first_name=person_data.get("first_name"),
            middle_name=person_data.get("middle_name"),
            date_of_birth=person_data.get("date_of_birth") or person_data.get("dob"),
            sex=person_data.get("sex") or person_data.get("gender"),
            race=person_data.get("race"),
            height=person_data.get("height"),
            weight=person_data.get("weight"),
            hair_color=person_data.get("hair_color"),
            eye_color=person_data.get("eye_color"),
            identifying_marks=person_data.get("identifying_marks") or person_data.get("scars_marks_tattoos"),
            clothing_description=person_data.get("clothing") or person_data.get("clothing_description"),
            address=person_data.get("address") or person_data.get("street"),
            city=person_data.get("city"),
            state=person_data.get("state"),
            zip_code=person_data.get("zip_code") or person_data.get("zip"),
            phone=person_data.get("phone"),
            email=person_data.get("email"),
            additional_info=person_data.get("notes") or person_data.get("additional_info"),
        )

    def map_vehicle_from_internal(
        self,
        vehicle_data: dict[str, Any],
    ) -> SARVehicle:
        """Map internal vehicle data to SAR vehicle"""
        return SARVehicle(
            make=vehicle_data.get("make"),
            model=vehicle_data.get("model"),
            year=vehicle_data.get("year"),
            color=vehicle_data.get("color"),
            license_plate=vehicle_data.get("license_plate") or vehicle_data.get("plate"),
            license_state=vehicle_data.get("license_state") or vehicle_data.get("state"),
            vin=vehicle_data.get("vin"),
            vehicle_type=vehicle_data.get("type") or vehicle_data.get("vehicle_type"),
            distinguishing_features=vehicle_data.get("features") or vehicle_data.get("distinguishing_features"),
        )

    def map_location_from_internal(
        self,
        location_data: dict[str, Any],
    ) -> SARLocation:
        """Map internal location data to SAR location"""
        if isinstance(location_data, str):
            return SARLocation(street_address=location_data)

        return SARLocation(
            street_address=location_data.get("street") or location_data.get("address"),
            city=location_data.get("city"),
            state=location_data.get("state"),
            zip_code=location_data.get("zip_code") or location_data.get("zip"),
            county=location_data.get("county"),
            country=location_data.get("country") or "US",
            latitude=location_data.get("latitude") or location_data.get("lat"),
            longitude=location_data.get("longitude") or location_data.get("lng") or location_data.get("lon"),
            location_type=location_data.get("type") or location_data.get("location_type"),
            location_name=location_data.get("name") or location_data.get("location_name"),
            location_description=location_data.get("description"),
        )


class SARManager:
    """Manager for DHS Suspicious Activity Reports"""

    def __init__(self, audit_logger: FederalAuditLogger):
        self.audit_logger = audit_logger
        self.mapper = SARDataMapper()
        self.reports: dict[str, SARReport] = {}
        self.schema = SARSchema()

    def create_sar(
        self,
        agency_ori: str,
        officer_name: str,
        user_id: str,
        behavior_category: SARBehaviorCategory,
        activity_date: str,
        activity_location: dict[str, Any],
        narrative: str,
        activity_time: str | None = None,
        behavior_indicators: list[SARBehaviorIndicator] | None = None,
        subjects: list[dict[str, Any]] | None = None,
        vehicles: list[dict[str, Any]] | None = None,
        threat_assessment: SARThreatLevel = SARThreatLevel.UNKNOWN,
        related_incidents: list[str] | None = None,
        additional_notes: str | None = None,
    ) -> SARReport:
        """Create a new SAR"""
        # Map location
        location = self.mapper.map_location_from_internal(activity_location)

        # Map subjects
        mapped_subjects = []
        if subjects:
            for subject_data in subjects:
                mapped_subjects.append(
                    self.mapper.map_subject_from_internal(subject_data),
                )

        # Map vehicles
        mapped_vehicles = []
        if vehicles:
            for vehicle_data in vehicles:
                mapped_vehicles.append(
                    self.mapper.map_vehicle_from_internal(vehicle_data),
                )

        # Create report
        report = SARReport(
            reporting_agency_ori=agency_ori,
            reporting_officer=officer_name,
            behavior_category=behavior_category,
            activity_date=activity_date,
            activity_time=activity_time,
            activity_location=location,
            narrative=narrative,
            behavior_indicators=behavior_indicators,
            subjects=mapped_subjects,
            vehicles=mapped_vehicles,
            threat_assessment=threat_assessment,
            related_incidents=related_incidents,
            additional_notes=additional_notes,
        )

        # Validate
        validation = self._validate_sar(report)
        report.validation_result = validation

        # Log creation
        self.audit_logger.log_sar_submission(
            agency_id=agency_ori,
            user_id=user_id,
            user_name=officer_name,
            sar_id=report.id,
        )

        self.reports[report.id] = report
        return report

    def create_sar_from_incident(
        self,
        incident_data: dict[str, Any],
        agency_ori: str,
        officer_name: str,
        user_id: str,
        behavior_category: SARBehaviorCategory | None = None,
        threat_assessment: SARThreatLevel = SARThreatLevel.UNKNOWN,
        additional_narrative: str | None = None,
    ) -> SARReport:
        """Create SAR from incident data"""
        # Determine behavior category
        if not behavior_category:
            behavior_category = self.mapper.map_behavior_category(
                incident_data.get("type") or incident_data.get("incident_type"),
            )

        # Build narrative
        narrative = incident_data.get("narrative") or incident_data.get("description") or ""
        if additional_narrative:
            narrative = f"{narrative}\n\nAdditional Information:\n{additional_narrative}"

        # Get location
        location_data = incident_data.get("location") or {
            "street": incident_data.get("address"),
            "city": incident_data.get("city"),
            "state": incident_data.get("state"),
        }

        # Get subjects from persons
        subjects = incident_data.get("persons") or incident_data.get("subjects") or []

        # Get vehicles
        vehicles = incident_data.get("vehicles") or []

        return self.create_sar(
            agency_ori=agency_ori,
            officer_name=officer_name,
            user_id=user_id,
            behavior_category=behavior_category,
            activity_date=incident_data.get("date") or incident_data.get("incident_date") or datetime.utcnow().strftime("%Y-%m-%d"),
            activity_time=incident_data.get("time") or incident_data.get("incident_time"),
            activity_location=location_data,
            narrative=narrative,
            subjects=subjects,
            vehicles=vehicles,
            threat_assessment=threat_assessment,
            related_incidents=[incident_data.get("id")] if incident_data.get("id") else None,
        )

    def update_sar(
        self,
        sar_id: str,
        updates: dict[str, Any],
    ) -> SARReport | None:
        """Update an existing SAR"""
        report = self.reports.get(sar_id)
        if not report:
            return None

        # Only allow updates if not submitted
        if report.status in [SARStatus.SUBMITTED, SARStatus.ARCHIVED]:
            return None

        # Apply updates
        if "narrative" in updates:
            report.narrative = updates["narrative"]
        if "threat_assessment" in updates:
            report.threat_assessment = SARThreatLevel(updates["threat_assessment"])
        if "behavior_category" in updates:
            report.behavior_category = SARBehaviorCategory(updates["behavior_category"])
        if "behavior_indicators" in updates:
            report.behavior_indicators = [
                SARBehaviorIndicator(bi) for bi in updates["behavior_indicators"]
            ]
        if "additional_notes" in updates:
            report.additional_notes = updates["additional_notes"]

        report.updated_at = datetime.utcnow()

        # Re-validate
        report.validation_result = self._validate_sar(report)

        return report

    def submit_sar(
        self,
        sar_id: str,
        approver_id: str,
        approver_name: str,
    ) -> SARReport | None:
        """Submit SAR for federal reporting"""
        report = self.reports.get(sar_id)
        if not report:
            return None

        # Validate before submission
        validation = self._validate_sar(report)
        if not validation.is_valid:
            report.validation_result = validation
            return report

        # Update status
        report.status = SARStatus.SUBMITTED
        report.submitted_at = datetime.utcnow()
        report.approved_by = approver_name
        report.approved_at = datetime.utcnow()

        return report

    def get_sar(self, sar_id: str) -> SARReport | None:
        """Get SAR by ID"""
        return self.reports.get(sar_id)

    def get_sars_by_agency(
        self,
        agency_ori: str,
        status: SARStatus | None = None,
        limit: int = 100,
    ) -> list[SARReport]:
        """Get SARs for an agency"""
        reports = [
            r for r in self.reports.values()
            if r.reporting_agency_ori == agency_ori
        ]

        if status:
            reports = [r for r in reports if r.status == status]

        reports.sort(key=lambda r: r.created_at, reverse=True)
        return reports[:limit]

    def export_sar(
        self,
        sar_id: str,
        agency_id: str,
        user_id: str,
    ) -> FederalMessagePackage | None:
        """Export SAR as federal message package"""
        report = self.reports.get(sar_id)
        if not report:
            return None

        package = FederalMessagePackage(
            message_type=FederalMessageType.DHS_SAR,
            federal_system=FederalSystem.DHS_SAR,
            payload=report.to_dict(),
            originating_agency=agency_id,
            originating_user=user_id,
        )

        if report.validation_result and report.validation_result.is_valid:
            package.status = FederalExportStatus.READY
        else:
            package.status = FederalExportStatus.FAILED

        return package

    def _validate_sar(self, report: SARReport) -> FederalValidationResult:
        """Validate SAR"""
        errors = []
        warnings = []

        # Check required fields
        if not report.reporting_agency_ori:
            errors.append("Reporting agency ORI is required")
        if not report.reporting_officer:
            errors.append("Reporting officer is required")
        if not report.activity_date:
            errors.append("Activity date is required")
        if not report.narrative or len(report.narrative.strip()) < 50:
            errors.append("Narrative must be at least 50 characters")

        # Validate activity date
        if report.activity_date:
            date_result = FederalValidator.validate_date(report.activity_date)
            if date_result is not True:
                errors.append(f"Invalid activity date: {date_result}")

        # Validate location
        location = report.activity_location
        if not location.city and not location.state:
            errors.append("Activity location (city/state) is required")
        if location.state:
            state_result = FederalValidator.validate_state_code(location.state)
            if state_result is not True:
                errors.append(f"Invalid location state: {state_result}")

        # Warnings
        if not report.subjects:
            warnings.append("No subjects identified - consider adding subject information")
        if report.threat_assessment == SARThreatLevel.UNKNOWN:
            warnings.append("Threat assessment not specified")
        if not report.behavior_indicators:
            warnings.append("No behavior indicators specified")

        return FederalValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            validated_data=report.to_dict() if len(errors) == 0 else None,
        )

    def get_statistics(
        self,
        agency_ori: str | None = None,
    ) -> dict[str, Any]:
        """Get SAR statistics"""
        reports = list(self.reports.values())
        if agency_ori:
            reports = [r for r in reports if r.reporting_agency_ori == agency_ori]

        stats = {
            "total_reports": len(reports),
            "by_status": {},
            "by_behavior_category": {},
            "by_threat_level": {},
            "submitted": 0,
            "pending": 0,
        }

        for report in reports:
            # Count by status
            status = report.status.value
            stats["by_status"][status] = stats["by_status"].get(status, 0) + 1

            # Count by behavior category
            category = report.behavior_category.value
            stats["by_behavior_category"][category] = (
                stats["by_behavior_category"].get(category, 0) + 1
            )

            # Count by threat level
            threat = report.threat_assessment.value
            stats["by_threat_level"][threat] = (
                stats["by_threat_level"].get(threat, 0) + 1
            )

            # Count submitted/pending
            if report.status == SARStatus.SUBMITTED:
                stats["submitted"] += 1
            elif report.status in [SARStatus.DRAFT, SARStatus.PENDING_REVIEW]:
                stats["pending"] += 1

        return stats


# Create singleton instance
sar_manager = SARManager(
    audit_logger=FederalAuditLogger(),
)
