"""
G3TI RTCC-UIP N-DEx Data Exchange Structures
Phase 11: FBI N-DEx v5.x schema mapping and export functionality
"""

import hashlib
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
    FederalTransformationPipeline,
    FederalValidationResult,
    FederalValidator,
)


class NDExEntityType(str, Enum):
    """N-DEx entity types"""
    PERSON = "Person"
    INCIDENT = "Incident"
    ARREST = "Arrest"
    CASE = "Case"
    PROPERTY = "Property"
    VEHICLE = "Vehicle"
    FIREARM = "Firearm"
    LOCATION = "Location"
    OFFENSE = "Offense"
    ORGANIZATION = "Organization"
    DOCUMENT = "Document"


class NDExRoleType(str, Enum):
    """N-DEx person role types"""
    SUBJECT = "Subject"
    VICTIM = "Victim"
    WITNESS = "Witness"
    SUSPECT = "Suspect"
    ARRESTEE = "Arrestee"
    MISSING_PERSON = "MissingPerson"
    WANTED_PERSON = "WantedPerson"
    REGISTERED_OFFENDER = "RegisteredOffender"
    OTHER = "Other"


class NDExIncidentType(str, Enum):
    """N-DEx incident types"""
    CRIMINAL = "Criminal"
    TRAFFIC = "Traffic"
    CIVIL = "Civil"
    SERVICE_CALL = "ServiceCall"
    FIELD_INTERVIEW = "FieldInterview"
    MISSING_PERSON = "MissingPerson"
    DEATH_INVESTIGATION = "DeathInvestigation"
    OTHER = "Other"


class NIBRSOffenseCode(str, Enum):
    """NIBRS offense codes (subset)"""
    MURDER = "09A"
    MANSLAUGHTER = "09B"
    RAPE = "11A"
    ROBBERY = "120"
    AGGRAVATED_ASSAULT = "13A"
    SIMPLE_ASSAULT = "13B"
    BURGLARY = "220"
    LARCENY = "23A"
    MOTOR_VEHICLE_THEFT = "240"
    ARSON = "200"
    DRUG_VIOLATION = "35A"
    WEAPON_VIOLATION = "520"
    FRAUD = "26A"
    VANDALISM = "290"
    KIDNAPPING = "100"
    SEX_OFFENSE = "36A"
    GAMBLING = "39A"
    PROSTITUTION = "40A"
    DUI = "90D"
    DISORDERLY_CONDUCT = "90C"
    TRESPASS = "90J"
    ALL_OTHER = "90Z"


class NDExPersonSchema(FederalSchema):
    """N-DEx Person schema v5.x"""

    def __init__(self):
        super().__init__(
            schema_name="NDEx_Person",
            schema_version="5.0",
            federal_system=FederalSystem.NDEX,
            required_fields=[
                "person_id",
                "last_name",
                "role_type",
            ],
            optional_fields=[
                "first_name",
                "middle_name",
                "suffix",
                "date_of_birth",
                "sex",
                "race",
                "ethnicity",
                "height",
                "weight",
                "eye_color",
                "hair_color",
                "ssn_hash",
                "drivers_license_hash",
                "state_id_hash",
                "fbi_number",
                "state_id_number",
                "address",
                "phone_numbers",
                "aliases",
                "scars_marks_tattoos",
                "photo_available",
            ],
            sensitive_fields=[
                "ssn_hash",
                "drivers_license_hash",
                "state_id_hash",
                "date_of_birth",
                "address",
            ],
        )


class NDExIncidentSchema(FederalSchema):
    """N-DEx Incident schema v5.x"""

    def __init__(self):
        super().__init__(
            schema_name="NDEx_Incident",
            schema_version="5.0",
            federal_system=FederalSystem.NDEX,
            required_fields=[
                "incident_id",
                "incident_number",
                "incident_date",
                "incident_type",
                "reporting_agency_ori",
            ],
            optional_fields=[
                "incident_time",
                "incident_end_date",
                "incident_end_time",
                "location",
                "narrative",
                "offenses",
                "persons_involved",
                "vehicles_involved",
                "property_involved",
                "firearms_involved",
                "status",
                "disposition",
                "cleared_exceptionally",
                "reporting_officer",
                "approving_officer",
            ],
            sensitive_fields=[
                "narrative",
                "persons_involved",
            ],
        )


class NDExArrestSchema(FederalSchema):
    """N-DEx Arrest schema v5.x"""

    def __init__(self):
        super().__init__(
            schema_name="NDEx_Arrest",
            schema_version="5.0",
            federal_system=FederalSystem.NDEX,
            required_fields=[
                "arrest_id",
                "arrest_date",
                "arrestee_person_id",
                "arresting_agency_ori",
            ],
            optional_fields=[
                "arrest_time",
                "arrest_location",
                "charges",
                "booking_number",
                "arresting_officer",
                "related_incident_id",
                "bail_amount",
                "disposition",
            ],
            sensitive_fields=[
                "arrestee_person_id",
            ],
        )


class NDExCaseSchema(FederalSchema):
    """N-DEx Case schema v5.x"""

    def __init__(self):
        super().__init__(
            schema_name="NDEx_Case",
            schema_version="5.0",
            federal_system=FederalSystem.NDEX,
            required_fields=[
                "case_id",
                "case_number",
                "case_type",
                "originating_agency_ori",
            ],
            optional_fields=[
                "case_title",
                "case_status",
                "open_date",
                "close_date",
                "assigned_investigator",
                "related_incidents",
                "related_arrests",
                "related_persons",
                "narrative",
                "priority",
            ],
            sensitive_fields=[
                "narrative",
                "related_persons",
            ],
        )


class NDExPropertySchema(FederalSchema):
    """N-DEx Property schema v5.x"""

    def __init__(self):
        super().__init__(
            schema_name="NDEx_Property",
            schema_version="5.0",
            federal_system=FederalSystem.NDEX,
            required_fields=[
                "property_id",
                "property_type",
                "property_status",
            ],
            optional_fields=[
                "description",
                "serial_number",
                "make",
                "model",
                "value",
                "quantity",
                "owner_person_id",
                "related_incident_id",
                "recovery_date",
                "recovery_location",
            ],
            sensitive_fields=[
                "serial_number",
                "owner_person_id",
            ],
        )


class NDExVehicleSchema(FederalSchema):
    """N-DEx Vehicle schema v5.x"""

    def __init__(self):
        super().__init__(
            schema_name="NDEx_Vehicle",
            schema_version="5.0",
            federal_system=FederalSystem.NDEX,
            required_fields=[
                "vehicle_id",
                "vehicle_type",
            ],
            optional_fields=[
                "vin",
                "license_plate",
                "license_state",
                "make",
                "model",
                "year",
                "color",
                "style",
                "owner_person_id",
                "registered_owner",
                "vehicle_status",
                "related_incident_id",
            ],
            sensitive_fields=[
                "vin",
                "license_plate",
                "owner_person_id",
            ],
        )


class NDExFirearmSchema(FederalSchema):
    """N-DEx Firearm schema v5.x"""

    def __init__(self):
        super().__init__(
            schema_name="NDEx_Firearm",
            schema_version="5.0",
            federal_system=FederalSystem.NDEX,
            required_fields=[
                "firearm_id",
                "firearm_type",
            ],
            optional_fields=[
                "serial_number",
                "make",
                "model",
                "caliber",
                "barrel_length",
                "finish",
                "firearm_status",
                "owner_person_id",
                "related_incident_id",
                "ncic_gun_type",
                "recovery_date",
                "recovery_location",
            ],
            sensitive_fields=[
                "serial_number",
                "owner_person_id",
            ],
        )


class NDExLocationSchema(FederalSchema):
    """N-DEx Location schema v5.x"""

    def __init__(self):
        super().__init__(
            schema_name="NDEx_Location",
            schema_version="5.0",
            federal_system=FederalSystem.NDEX,
            required_fields=[
                "location_id",
            ],
            optional_fields=[
                "street_address",
                "city",
                "state",
                "zip_code",
                "county",
                "country",
                "latitude",
                "longitude",
                "location_type",
                "location_description",
            ],
            sensitive_fields=[
                "street_address",
            ],
        )


class NDExDataMapper:
    """Maps internal data to N-DEx format"""

    def __init__(self, audit_logger: FederalAuditLogger):
        self.audit_logger = audit_logger
        self.person_schema = NDExPersonSchema()
        self.incident_schema = NDExIncidentSchema()
        self.arrest_schema = NDExArrestSchema()
        self.case_schema = NDExCaseSchema()
        self.property_schema = NDExPropertySchema()
        self.vehicle_schema = NDExVehicleSchema()
        self.firearm_schema = NDExFirearmSchema()
        self.location_schema = NDExLocationSchema()
        self.validator = FederalValidator()

        # Set up validation rules
        self.validator.add_rule("date_of_birth", FederalValidator.validate_date)
        self.validator.add_rule("incident_date", FederalValidator.validate_date)
        self.validator.add_rule("arrest_date", FederalValidator.validate_date)
        self.validator.add_rule("state", FederalValidator.validate_state_code)
        self.validator.add_rule("license_state", FederalValidator.validate_state_code)
        self.validator.add_rule("vin", FederalValidator.validate_vin)

    def _hash_sensitive_field(self, value: str | None) -> str | None:
        """Hash sensitive field for CJIS compliance"""
        if not value:
            return None
        return hashlib.sha256(value.encode()).hexdigest()

    def _mask_sensitive_field(
        self,
        value: str | None,
        visible_chars: int = 4,
    ) -> str | None:
        """Mask sensitive field showing only last N characters"""
        if not value:
            return None
        if len(value) <= visible_chars:
            return "*" * len(value)
        return "*" * (len(value) - visible_chars) + value[-visible_chars:]

    def map_person(
        self,
        person_data: dict[str, Any],
        role_type: NDExRoleType = NDExRoleType.SUBJECT,
        mask_sensitive: bool = True,
    ) -> dict[str, Any]:
        """Map internal person data to N-DEx Person format"""
        ndex_person = {
            "person_id": person_data.get("id") or str(uuid4()),
            "last_name": person_data.get("last_name", "").upper(),
            "first_name": person_data.get("first_name", "").upper() if person_data.get("first_name") else None,
            "middle_name": person_data.get("middle_name", "").upper() if person_data.get("middle_name") else None,
            "suffix": person_data.get("suffix"),
            "role_type": role_type.value,
            "sex": person_data.get("sex") or person_data.get("gender"),
            "race": person_data.get("race"),
            "ethnicity": person_data.get("ethnicity"),
            "height": person_data.get("height"),
            "weight": person_data.get("weight"),
            "eye_color": person_data.get("eye_color"),
            "hair_color": person_data.get("hair_color"),
            "photo_available": bool(person_data.get("photo_url")),
        }

        # Handle sensitive fields
        if mask_sensitive:
            ndex_person["date_of_birth"] = self._mask_sensitive_field(
                person_data.get("date_of_birth"),
                visible_chars=4,
            )
            ndex_person["ssn_hash"] = self._hash_sensitive_field(
                person_data.get("ssn"),
            )
            ndex_person["drivers_license_hash"] = self._hash_sensitive_field(
                person_data.get("drivers_license"),
            )
            ndex_person["state_id_hash"] = self._hash_sensitive_field(
                person_data.get("state_id"),
            )
        else:
            ndex_person["date_of_birth"] = person_data.get("date_of_birth")
            ndex_person["ssn_hash"] = self._hash_sensitive_field(person_data.get("ssn"))
            ndex_person["drivers_license_hash"] = self._hash_sensitive_field(
                person_data.get("drivers_license"),
            )

        # Handle address
        if person_data.get("address"):
            addr = person_data["address"]
            if isinstance(addr, dict):
                ndex_person["address"] = {
                    "street": addr.get("street", "").upper() if addr.get("street") else None,
                    "city": addr.get("city", "").upper() if addr.get("city") else None,
                    "state": addr.get("state", "").upper() if addr.get("state") else None,
                    "zip_code": addr.get("zip_code"),
                }
            else:
                ndex_person["address"] = {"street": str(addr).upper()}

        # Handle aliases
        if person_data.get("aliases"):
            ndex_person["aliases"] = [
                alias.upper() for alias in person_data["aliases"]
            ]

        # Handle scars/marks/tattoos
        if person_data.get("scars_marks_tattoos"):
            ndex_person["scars_marks_tattoos"] = person_data["scars_marks_tattoos"]

        return ndex_person

    def map_incident(
        self,
        incident_data: dict[str, Any],
        include_persons: bool = True,
        include_vehicles: bool = True,
        include_property: bool = True,
        include_firearms: bool = True,
    ) -> dict[str, Any]:
        """Map internal incident data to N-DEx Incident format"""
        ndex_incident = {
            "incident_id": incident_data.get("id") or str(uuid4()),
            "incident_number": incident_data.get("incident_number") or incident_data.get("case_number"),
            "incident_date": incident_data.get("incident_date") or incident_data.get("date"),
            "incident_time": incident_data.get("incident_time") or incident_data.get("time"),
            "incident_type": self._map_incident_type(incident_data.get("type")),
            "reporting_agency_ori": incident_data.get("agency_ori") or incident_data.get("ori"),
            "status": incident_data.get("status"),
            "disposition": incident_data.get("disposition"),
            "reporting_officer": incident_data.get("reporting_officer"),
            "approving_officer": incident_data.get("approving_officer"),
        }

        # Handle location
        if incident_data.get("location"):
            ndex_incident["location"] = self.map_location(incident_data["location"])

        # Handle narrative (sanitized)
        if incident_data.get("narrative"):
            ndex_incident["narrative"] = self._sanitize_narrative(
                incident_data["narrative"],
            )

        # Handle offenses
        if incident_data.get("offenses"):
            ndex_incident["offenses"] = [
                self._map_offense(offense) for offense in incident_data["offenses"]
            ]

        # Handle related entities
        if include_persons and incident_data.get("persons"):
            ndex_incident["persons_involved"] = [
                self.map_person(person, NDExRoleType(person.get("role", "Subject")))
                for person in incident_data["persons"]
            ]

        if include_vehicles and incident_data.get("vehicles"):
            ndex_incident["vehicles_involved"] = [
                self.map_vehicle(vehicle) for vehicle in incident_data["vehicles"]
            ]

        if include_property and incident_data.get("property"):
            ndex_incident["property_involved"] = [
                self.map_property(prop) for prop in incident_data["property"]
            ]

        if include_firearms and incident_data.get("firearms"):
            ndex_incident["firearms_involved"] = [
                self.map_firearm(firearm) for firearm in incident_data["firearms"]
            ]

        return ndex_incident

    def map_arrest(self, arrest_data: dict[str, Any]) -> dict[str, Any]:
        """Map internal arrest data to N-DEx Arrest format"""
        ndex_arrest = {
            "arrest_id": arrest_data.get("id") or str(uuid4()),
            "arrest_date": arrest_data.get("arrest_date") or arrest_data.get("date"),
            "arrest_time": arrest_data.get("arrest_time") or arrest_data.get("time"),
            "arrestee_person_id": arrest_data.get("person_id") or arrest_data.get("arrestee_id"),
            "arresting_agency_ori": arrest_data.get("agency_ori") or arrest_data.get("ori"),
            "booking_number": arrest_data.get("booking_number"),
            "arresting_officer": arrest_data.get("arresting_officer"),
            "related_incident_id": arrest_data.get("incident_id"),
            "bail_amount": arrest_data.get("bail_amount"),
            "disposition": arrest_data.get("disposition"),
        }

        # Handle arrest location
        if arrest_data.get("location"):
            ndex_arrest["arrest_location"] = self.map_location(arrest_data["location"])

        # Handle charges
        if arrest_data.get("charges"):
            ndex_arrest["charges"] = [
                {
                    "charge_code": charge.get("code"),
                    "charge_description": charge.get("description"),
                    "charge_class": charge.get("class"),
                    "nibrs_code": self._map_to_nibrs(charge.get("code")),
                }
                for charge in arrest_data["charges"]
            ]

        return ndex_arrest

    def map_case(self, case_data: dict[str, Any]) -> dict[str, Any]:
        """Map internal case data to N-DEx Case format"""
        ndex_case = {
            "case_id": case_data.get("id") or str(uuid4()),
            "case_number": case_data.get("case_number"),
            "case_type": case_data.get("case_type") or "Investigation",
            "case_title": case_data.get("title"),
            "case_status": case_data.get("status"),
            "originating_agency_ori": case_data.get("agency_ori") or case_data.get("ori"),
            "open_date": case_data.get("open_date") or case_data.get("created_at"),
            "close_date": case_data.get("close_date"),
            "assigned_investigator": case_data.get("assigned_to"),
            "priority": case_data.get("priority"),
        }

        # Handle related entities
        if case_data.get("incidents"):
            ndex_case["related_incidents"] = case_data["incidents"]
        if case_data.get("arrests"):
            ndex_case["related_arrests"] = case_data["arrests"]
        if case_data.get("persons"):
            ndex_case["related_persons"] = [
                self.map_person(person) for person in case_data["persons"]
            ]

        # Handle narrative (sanitized)
        if case_data.get("narrative"):
            ndex_case["narrative"] = self._sanitize_narrative(case_data["narrative"])

        return ndex_case

    def map_property(self, property_data: dict[str, Any]) -> dict[str, Any]:
        """Map internal property data to N-DEx Property format"""
        return {
            "property_id": property_data.get("id") or str(uuid4()),
            "property_type": property_data.get("type") or property_data.get("property_type"),
            "property_status": property_data.get("status") or "Unknown",
            "description": property_data.get("description"),
            "serial_number": self._mask_sensitive_field(
                property_data.get("serial_number"),
                visible_chars=4,
            ),
            "make": property_data.get("make"),
            "model": property_data.get("model"),
            "value": property_data.get("value"),
            "quantity": property_data.get("quantity") or 1,
            "owner_person_id": property_data.get("owner_id"),
            "related_incident_id": property_data.get("incident_id"),
            "recovery_date": property_data.get("recovery_date"),
        }

    def map_vehicle(self, vehicle_data: dict[str, Any]) -> dict[str, Any]:
        """Map internal vehicle data to N-DEx Vehicle format"""
        return {
            "vehicle_id": vehicle_data.get("id") or str(uuid4()),
            "vehicle_type": vehicle_data.get("type") or vehicle_data.get("vehicle_type") or "Automobile",
            "vin": self._mask_sensitive_field(vehicle_data.get("vin"), visible_chars=4),
            "license_plate": self._mask_sensitive_field(
                vehicle_data.get("license_plate") or vehicle_data.get("plate"),
                visible_chars=3,
            ),
            "license_state": vehicle_data.get("license_state") or vehicle_data.get("state"),
            "make": vehicle_data.get("make"),
            "model": vehicle_data.get("model"),
            "year": vehicle_data.get("year"),
            "color": vehicle_data.get("color"),
            "style": vehicle_data.get("style") or vehicle_data.get("body_style"),
            "owner_person_id": vehicle_data.get("owner_id"),
            "vehicle_status": vehicle_data.get("status"),
            "related_incident_id": vehicle_data.get("incident_id"),
        }

    def map_firearm(self, firearm_data: dict[str, Any]) -> dict[str, Any]:
        """Map internal firearm data to N-DEx Firearm format"""
        return {
            "firearm_id": firearm_data.get("id") or str(uuid4()),
            "firearm_type": firearm_data.get("type") or firearm_data.get("weapon_type") or "Unknown",
            "serial_number": self._mask_sensitive_field(
                firearm_data.get("serial_number"),
                visible_chars=4,
            ),
            "make": firearm_data.get("make") or firearm_data.get("manufacturer"),
            "model": firearm_data.get("model"),
            "caliber": firearm_data.get("caliber"),
            "barrel_length": firearm_data.get("barrel_length"),
            "finish": firearm_data.get("finish"),
            "firearm_status": firearm_data.get("status"),
            "owner_person_id": firearm_data.get("owner_id"),
            "related_incident_id": firearm_data.get("incident_id"),
            "ncic_gun_type": self._map_to_ncic_gun_type(firearm_data.get("type")),
            "recovery_date": firearm_data.get("recovery_date"),
        }

    def map_location(self, location_data: dict[str, Any]) -> dict[str, Any]:
        """Map internal location data to N-DEx Location format"""
        if isinstance(location_data, str):
            return {
                "location_id": str(uuid4()),
                "street_address": location_data.upper(),
            }

        return {
            "location_id": location_data.get("id") or str(uuid4()),
            "street_address": location_data.get("street", "").upper() if location_data.get("street") else None,
            "city": location_data.get("city", "").upper() if location_data.get("city") else None,
            "state": location_data.get("state", "").upper() if location_data.get("state") else None,
            "zip_code": location_data.get("zip_code") or location_data.get("zip"),
            "county": location_data.get("county"),
            "country": location_data.get("country") or "US",
            "latitude": location_data.get("latitude") or location_data.get("lat"),
            "longitude": location_data.get("longitude") or location_data.get("lng") or location_data.get("lon"),
            "location_type": location_data.get("type") or location_data.get("location_type"),
            "location_description": location_data.get("description"),
        }

    def _map_incident_type(self, incident_type: str | None) -> str:
        """Map internal incident type to N-DEx incident type"""
        if not incident_type:
            return NDExIncidentType.OTHER.value

        type_mapping = {
            "crime": NDExIncidentType.CRIMINAL.value,
            "criminal": NDExIncidentType.CRIMINAL.value,
            "traffic": NDExIncidentType.TRAFFIC.value,
            "accident": NDExIncidentType.TRAFFIC.value,
            "civil": NDExIncidentType.CIVIL.value,
            "service": NDExIncidentType.SERVICE_CALL.value,
            "call": NDExIncidentType.SERVICE_CALL.value,
            "field_interview": NDExIncidentType.FIELD_INTERVIEW.value,
            "fi": NDExIncidentType.FIELD_INTERVIEW.value,
            "missing": NDExIncidentType.MISSING_PERSON.value,
            "death": NDExIncidentType.DEATH_INVESTIGATION.value,
        }

        return type_mapping.get(incident_type.lower(), NDExIncidentType.OTHER.value)

    def _map_offense(self, offense_data: dict[str, Any]) -> dict[str, Any]:
        """Map offense data to N-DEx format with NIBRS code"""
        return {
            "offense_code": offense_data.get("code"),
            "offense_description": offense_data.get("description"),
            "nibrs_code": self._map_to_nibrs(offense_data.get("code")),
            "attempted_completed": offense_data.get("attempted_completed") or "Completed",
            "offense_count": offense_data.get("count") or 1,
        }

    def _map_to_nibrs(self, offense_code: str | None) -> str | None:
        """Map offense code to NIBRS code"""
        if not offense_code:
            return None

        # Simplified mapping - in production would use full UCR/NIBRS crosswalk
        nibrs_mapping = {
            "murder": NIBRSOffenseCode.MURDER.value,
            "homicide": NIBRSOffenseCode.MURDER.value,
            "manslaughter": NIBRSOffenseCode.MANSLAUGHTER.value,
            "rape": NIBRSOffenseCode.RAPE.value,
            "robbery": NIBRSOffenseCode.ROBBERY.value,
            "assault": NIBRSOffenseCode.AGGRAVATED_ASSAULT.value,
            "burglary": NIBRSOffenseCode.BURGLARY.value,
            "theft": NIBRSOffenseCode.LARCENY.value,
            "larceny": NIBRSOffenseCode.LARCENY.value,
            "auto_theft": NIBRSOffenseCode.MOTOR_VEHICLE_THEFT.value,
            "vehicle_theft": NIBRSOffenseCode.MOTOR_VEHICLE_THEFT.value,
            "arson": NIBRSOffenseCode.ARSON.value,
            "drug": NIBRSOffenseCode.DRUG_VIOLATION.value,
            "narcotics": NIBRSOffenseCode.DRUG_VIOLATION.value,
            "weapon": NIBRSOffenseCode.WEAPON_VIOLATION.value,
            "fraud": NIBRSOffenseCode.FRAUD.value,
            "vandalism": NIBRSOffenseCode.VANDALISM.value,
            "kidnapping": NIBRSOffenseCode.KIDNAPPING.value,
            "dui": NIBRSOffenseCode.DUI.value,
            "dwi": NIBRSOffenseCode.DUI.value,
        }

        code_lower = offense_code.lower()
        for key, nibrs in nibrs_mapping.items():
            if key in code_lower:
                return nibrs

        return NIBRSOffenseCode.ALL_OTHER.value

    def _map_to_ncic_gun_type(self, firearm_type: str | None) -> str | None:
        """Map firearm type to NCIC gun type code"""
        if not firearm_type:
            return None

        ncic_mapping = {
            "pistol": "P",
            "handgun": "P",
            "revolver": "R",
            "rifle": "RF",
            "shotgun": "SG",
            "machine_gun": "MG",
            "submachine": "SM",
            "derringer": "D",
            "other": "OT",
        }

        type_lower = firearm_type.lower()
        for key, code in ncic_mapping.items():
            if key in type_lower:
                return code

        return "OT"

    def _sanitize_narrative(self, narrative: str) -> str:
        """Sanitize narrative for federal export"""
        if not narrative:
            return ""

        # Remove potential PII patterns
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


class NDExExportManager:
    """Manager for N-DEx data exports"""

    def __init__(self, audit_logger: FederalAuditLogger):
        self.audit_logger = audit_logger
        self.mapper = NDExDataMapper(audit_logger)
        self.exports: dict[str, FederalMessagePackage] = {}
        self.transformation_pipeline = FederalTransformationPipeline("ndex_export")
        self.transformation_pipeline.add_transformation(
            FederalTransformationPipeline.normalize_name,
        )
        self.transformation_pipeline.add_transformation(
            FederalTransformationPipeline.normalize_address,
        )
        self.transformation_pipeline.add_transformation(
            FederalTransformationPipeline.format_date_iso,
        )

    def export_person(
        self,
        person_data: dict[str, Any],
        role_type: NDExRoleType,
        agency_id: str,
        user_id: str,
        user_name: str,
    ) -> FederalMessagePackage:
        """Export person to N-DEx format"""
        # Transform data
        transformed = self.transformation_pipeline.execute(person_data)

        # Map to N-DEx format
        ndex_person = self.mapper.map_person(transformed, role_type)

        # Create message package
        package = FederalMessagePackage(
            message_type=FederalMessageType.NDEX_PERSON,
            federal_system=FederalSystem.NDEX,
            payload=ndex_person,
            originating_agency=agency_id,
            originating_user=user_id,
        )
        package.status = FederalExportStatus.READY

        # Log export
        self.audit_logger.log_ndex_export(
            agency_id=agency_id,
            user_id=user_id,
            user_name=user_name,
            resource_type="person",
            resource_id=ndex_person["person_id"],
        )

        self.exports[package.id] = package
        return package

    def export_incident(
        self,
        incident_data: dict[str, Any],
        agency_id: str,
        user_id: str,
        user_name: str,
        include_related: bool = True,
    ) -> FederalMessagePackage:
        """Export incident to N-DEx format"""
        # Transform data
        transformed = self.transformation_pipeline.execute(incident_data)

        # Map to N-DEx format
        ndex_incident = self.mapper.map_incident(
            transformed,
            include_persons=include_related,
            include_vehicles=include_related,
            include_property=include_related,
            include_firearms=include_related,
        )

        # Create message package
        package = FederalMessagePackage(
            message_type=FederalMessageType.NDEX_INCIDENT,
            federal_system=FederalSystem.NDEX,
            payload=ndex_incident,
            originating_agency=agency_id,
            originating_user=user_id,
        )
        package.status = FederalExportStatus.READY

        # Log export
        self.audit_logger.log_ndex_export(
            agency_id=agency_id,
            user_id=user_id,
            user_name=user_name,
            resource_type="incident",
            resource_id=ndex_incident["incident_id"],
        )

        self.exports[package.id] = package
        return package

    def export_arrest(
        self,
        arrest_data: dict[str, Any],
        agency_id: str,
        user_id: str,
        user_name: str,
    ) -> FederalMessagePackage:
        """Export arrest to N-DEx format"""
        # Transform data
        transformed = self.transformation_pipeline.execute(arrest_data)

        # Map to N-DEx format
        ndex_arrest = self.mapper.map_arrest(transformed)

        # Create message package
        package = FederalMessagePackage(
            message_type=FederalMessageType.NDEX_ARREST,
            federal_system=FederalSystem.NDEX,
            payload=ndex_arrest,
            originating_agency=agency_id,
            originating_user=user_id,
        )
        package.status = FederalExportStatus.READY

        # Log export
        self.audit_logger.log_ndex_export(
            agency_id=agency_id,
            user_id=user_id,
            user_name=user_name,
            resource_type="arrest",
            resource_id=ndex_arrest["arrest_id"],
        )

        self.exports[package.id] = package
        return package

    def export_case(
        self,
        case_data: dict[str, Any],
        agency_id: str,
        user_id: str,
        user_name: str,
    ) -> FederalMessagePackage:
        """Export case to N-DEx format"""
        # Transform data
        transformed = self.transformation_pipeline.execute(case_data)

        # Map to N-DEx format
        ndex_case = self.mapper.map_case(transformed)

        # Create message package
        package = FederalMessagePackage(
            message_type=FederalMessageType.NDEX_CASE,
            federal_system=FederalSystem.NDEX,
            payload=ndex_case,
            originating_agency=agency_id,
            originating_user=user_id,
        )
        package.status = FederalExportStatus.READY

        # Log export
        self.audit_logger.log_ndex_export(
            agency_id=agency_id,
            user_id=user_id,
            user_name=user_name,
            resource_type="case",
            resource_id=ndex_case["case_id"],
        )

        self.exports[package.id] = package
        return package

    def export_vehicle(
        self,
        vehicle_data: dict[str, Any],
        agency_id: str,
        user_id: str,
        user_name: str,
    ) -> FederalMessagePackage:
        """Export vehicle to N-DEx format"""
        # Map to N-DEx format
        ndex_vehicle = self.mapper.map_vehicle(vehicle_data)

        # Create message package
        package = FederalMessagePackage(
            message_type=FederalMessageType.NDEX_VEHICLE,
            federal_system=FederalSystem.NDEX,
            payload=ndex_vehicle,
            originating_agency=agency_id,
            originating_user=user_id,
        )
        package.status = FederalExportStatus.READY

        # Log export
        self.audit_logger.log_ndex_export(
            agency_id=agency_id,
            user_id=user_id,
            user_name=user_name,
            resource_type="vehicle",
            resource_id=ndex_vehicle["vehicle_id"],
        )

        self.exports[package.id] = package
        return package

    def export_firearm(
        self,
        firearm_data: dict[str, Any],
        agency_id: str,
        user_id: str,
        user_name: str,
    ) -> FederalMessagePackage:
        """Export firearm to N-DEx format"""
        # Map to N-DEx format
        ndex_firearm = self.mapper.map_firearm(firearm_data)

        # Create message package
        package = FederalMessagePackage(
            message_type=FederalMessageType.NDEX_FIREARM,
            federal_system=FederalSystem.NDEX,
            payload=ndex_firearm,
            originating_agency=agency_id,
            originating_user=user_id,
        )
        package.status = FederalExportStatus.READY

        # Log export
        self.audit_logger.log_ndex_export(
            agency_id=agency_id,
            user_id=user_id,
            user_name=user_name,
            resource_type="firearm",
            resource_id=ndex_firearm["firearm_id"],
        )

        self.exports[package.id] = package
        return package

    def get_export(self, export_id: str) -> FederalMessagePackage | None:
        """Get export by ID"""
        return self.exports.get(export_id)

    def get_exports_by_agency(
        self,
        agency_id: str,
        limit: int = 100,
    ) -> list[FederalMessagePackage]:
        """Get exports for an agency"""
        exports = [
            e for e in self.exports.values()
            if e.originating_agency == agency_id
        ]
        exports.sort(key=lambda e: e.created_at, reverse=True)
        return exports[:limit]

    def validate_export(
        self,
        export_id: str,
    ) -> FederalValidationResult:
        """Validate an export package"""
        package = self.exports.get(export_id)
        if not package:
            return FederalValidationResult(
                is_valid=False,
                errors=["Export not found"],
            )

        # Get appropriate schema
        schema_map = {
            FederalMessageType.NDEX_PERSON: self.mapper.person_schema,
            FederalMessageType.NDEX_INCIDENT: self.mapper.incident_schema,
            FederalMessageType.NDEX_ARREST: self.mapper.arrest_schema,
            FederalMessageType.NDEX_CASE: self.mapper.case_schema,
            FederalMessageType.NDEX_VEHICLE: self.mapper.vehicle_schema,
            FederalMessageType.NDEX_FIREARM: self.mapper.firearm_schema,
        }

        schema = schema_map.get(package.message_type)
        if not schema:
            return FederalValidationResult(
                is_valid=False,
                errors=["Unknown message type"],
            )

        # Validate
        result = self.mapper.validator.validate(package.payload, schema)
        package.validation_result = result

        if result.is_valid:
            package.status = FederalExportStatus.VALIDATED
        else:
            package.status = FederalExportStatus.FAILED

        return result


# Create singleton instances
ndex_export_manager = NDExExportManager(
    audit_logger=FederalAuditLogger(),
)
