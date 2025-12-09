"""
G3TI RTCC-UIP Federal Data Readiness Layer
Phase 10: Data structures for federal system integration (N-DEx, NCIC, ATF eTrace, DHS SAR)

Note: This module provides structure only - no live integration with federal systems.
"""

import hashlib
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import uuid4


class FederalSystem(str, Enum):
    """Federal systems for data exchange"""
    NDEX = "ndex"  # National Data Exchange
    NCIC = "ncic"  # National Crime Information Center
    ATF_ETRACE = "atf_etrace"  # ATF eTrace
    DHS_SAR = "dhs_sar"  # DHS Suspicious Activity Reporting


class NDExRecordType(str, Enum):
    """N-DEx record types"""
    PERSON = "person"
    ORGANIZATION = "organization"
    ITEM = "item"
    LOCATION = "location"
    ACTIVITY = "activity"
    ASSOCIATION = "association"


class NCICRecordType(str, Enum):
    """NCIC record types"""
    WANTED_PERSON = "wanted_person"
    MISSING_PERSON = "missing_person"
    STOLEN_VEHICLE = "stolen_vehicle"
    STOLEN_ARTICLE = "stolen_article"
    STOLEN_GUN = "stolen_gun"
    STOLEN_BOAT = "stolen_boat"
    STOLEN_SECURITIES = "stolen_securities"
    GANG_MEMBER = "gang_member"
    FOREIGN_FUGITIVE = "foreign_fugitive"
    IMMIGRATION_VIOLATOR = "immigration_violator"
    PROTECTION_ORDER = "protection_order"
    SUPERVISED_RELEASE = "supervised_release"
    UNIDENTIFIED_PERSON = "unidentified_person"
    VIOLENT_PERSON = "violent_person"


class SARActivityType(str, Enum):
    """DHS SAR activity types"""
    ACQUISITION_EXPERTISE = "acquisition_expertise"
    BREACH_SECURITY = "breach_security"
    ELICITING_INFORMATION = "eliciting_information"
    MISREPRESENTATION = "misrepresentation"
    OBSERVATION_SURVEILLANCE = "observation_surveillance"
    PHOTOGRAPHY = "photography"
    RECRUITING = "recruiting"
    SABOTAGE_TAMPERING = "sabotage_tampering"
    TESTING_SECURITY = "testing_security"
    THEFT_LOSS = "theft_loss"
    WEAPONS_DISCOVERY = "weapons_discovery"
    SECTOR_SPECIFIC = "sector_specific"


class ETraceRequestType(str, Enum):
    """ATF eTrace request types"""
    STANDARD_TRACE = "standard_trace"
    URGENT_TRACE = "urgent_trace"
    MULTIPLE_SALES = "multiple_sales"
    SUSPECT_GUN = "suspect_gun"


class PseudonymizationMethod(str, Enum):
    """Methods for pseudonymizing sensitive data"""
    SHA256_HASH = "sha256_hash"
    HMAC_SHA256 = "hmac_sha256"
    TRUNCATION = "truncation"
    GENERALIZATION = "generalization"
    SUPPRESSION = "suppression"


class NDExPersonRecord:
    """N-DEx Person record structure"""

    def __init__(
        self,
        person_id: str,
        first_name: str,
        last_name: str,
        middle_name: str | None = None,
        date_of_birth: str | None = None,
        gender: str | None = None,
        race: str | None = None,
        ethnicity: str | None = None,
        height: str | None = None,
        weight: str | None = None,
        eye_color: str | None = None,
        hair_color: str | None = None,
        ssn_hash: str | None = None,
        fbi_number: str | None = None,
        state_id: str | None = None,
        drivers_license: str | None = None,
        aliases: list[str] | None = None,
        scars_marks_tattoos: list[str] | None = None,
    ):
        self.id = str(uuid4())
        self.person_id = person_id
        self.first_name = first_name
        self.last_name = last_name
        self.middle_name = middle_name
        self.date_of_birth = date_of_birth
        self.gender = gender
        self.race = race
        self.ethnicity = ethnicity
        self.height = height
        self.weight = weight
        self.eye_color = eye_color
        self.hair_color = hair_color
        self.ssn_hash = ssn_hash
        self.fbi_number = fbi_number
        self.state_id = state_id
        self.drivers_license = drivers_license
        self.aliases = aliases or []
        self.scars_marks_tattoos = scars_marks_tattoos or []
        self.created_at = datetime.utcnow()

    def to_ndex_format(self) -> dict[str, Any]:
        """Convert to N-DEx XML-compatible format"""
        return {
            "PersonAugmentation": {
                "PersonID": self.person_id,
                "PersonName": {
                    "PersonGivenName": self.first_name,
                    "PersonMiddleName": self.middle_name,
                    "PersonSurName": self.last_name,
                },
                "PersonBirthDate": {"Date": self.date_of_birth},
                "PersonSexCode": self.gender,
                "PersonRaceCode": self.race,
                "PersonEthnicityCode": self.ethnicity,
                "PersonHeightMeasure": self.height,
                "PersonWeightMeasure": self.weight,
                "PersonEyeColorCode": self.eye_color,
                "PersonHairColorCode": self.hair_color,
                "PersonSSNIdentification": {"IdentificationID": self.ssn_hash},
                "PersonFBIIdentification": {"IdentificationID": self.fbi_number},
                "PersonStateIdentification": {"IdentificationID": self.state_id},
                "PersonAlternateName": self.aliases,
                "PersonPhysicalFeature": self.scars_marks_tattoos,
            }
        }


class NDExActivityRecord:
    """N-DEx Activity record structure"""

    def __init__(
        self,
        activity_id: str,
        activity_type: str,
        activity_date: datetime,
        location: dict[str, Any],
        description: str,
        involved_persons: list[str],
        involved_items: list[str],
        reporting_agency: str,
        case_number: str | None = None,
    ):
        self.id = str(uuid4())
        self.activity_id = activity_id
        self.activity_type = activity_type
        self.activity_date = activity_date
        self.location = location
        self.description = description
        self.involved_persons = involved_persons
        self.involved_items = involved_items
        self.reporting_agency = reporting_agency
        self.case_number = case_number
        self.created_at = datetime.utcnow()

    def to_ndex_format(self) -> dict[str, Any]:
        """Convert to N-DEx XML-compatible format"""
        return {
            "ActivityAugmentation": {
                "ActivityID": self.activity_id,
                "ActivityCategoryText": self.activity_type,
                "ActivityDate": {"Date": self.activity_date.isoformat()},
                "ActivityDescriptionText": self.description,
                "ActivityLocation": self.location,
                "ActivityInvolvedPerson": self.involved_persons,
                "ActivityInvolvedItem": self.involved_items,
                "ActivityReportingOrganization": self.reporting_agency,
                "CaseNumberText": self.case_number,
            }
        }


class NCICQueryStructure:
    """NCIC query structure (query format only, no live integration)"""

    def __init__(
        self,
        record_type: NCICRecordType,
        query_params: dict[str, Any],
        requesting_agency: str,
        requesting_officer: str,
        purpose: str,
    ):
        self.id = str(uuid4())
        self.record_type = record_type
        self.query_params = query_params
        self.requesting_agency = requesting_agency
        self.requesting_officer = requesting_officer
        self.purpose = purpose
        self.created_at = datetime.utcnow()

    def to_ncic_format(self) -> dict[str, Any]:
        """Convert to NCIC query format"""
        return {
            "NCICQuery": {
                "RecordType": self.record_type.value,
                "QueryParameters": self.query_params,
                "RequestingAgency": {
                    "ORI": self.requesting_agency,
                    "OfficerID": self.requesting_officer,
                },
                "Purpose": self.purpose,
                "Timestamp": self.created_at.isoformat(),
            }
        }


class NCICWantedPersonQuery(NCICQueryStructure):
    """NCIC Wanted Person query structure"""

    def __init__(
        self,
        requesting_agency: str,
        requesting_officer: str,
        purpose: str,
        name: str | None = None,
        date_of_birth: str | None = None,
        ssn: str | None = None,
        drivers_license: str | None = None,
        state: str | None = None,
    ):
        query_params = {
            "Name": name,
            "DateOfBirth": date_of_birth,
            "SSN": ssn,
            "DriversLicense": drivers_license,
            "State": state,
        }
        query_params = {k: v for k, v in query_params.items() if v is not None}

        super().__init__(
            record_type=NCICRecordType.WANTED_PERSON,
            query_params=query_params,
            requesting_agency=requesting_agency,
            requesting_officer=requesting_officer,
            purpose=purpose,
        )


class NCICStolenVehicleQuery(NCICQueryStructure):
    """NCIC Stolen Vehicle query structure"""

    def __init__(
        self,
        requesting_agency: str,
        requesting_officer: str,
        purpose: str,
        license_plate: str | None = None,
        vin: str | None = None,
        state: str | None = None,
    ):
        query_params = {
            "LicensePlate": license_plate,
            "VIN": vin,
            "State": state,
        }
        query_params = {k: v for k, v in query_params.items() if v is not None}

        super().__init__(
            record_type=NCICRecordType.STOLEN_VEHICLE,
            query_params=query_params,
            requesting_agency=requesting_agency,
            requesting_officer=requesting_officer,
            purpose=purpose,
        )


class NCICStolenGunQuery(NCICQueryStructure):
    """NCIC Stolen Gun query structure"""

    def __init__(
        self,
        requesting_agency: str,
        requesting_officer: str,
        purpose: str,
        serial_number: str | None = None,
        make: str | None = None,
        model: str | None = None,
        caliber: str | None = None,
    ):
        query_params = {
            "SerialNumber": serial_number,
            "Make": make,
            "Model": model,
            "Caliber": caliber,
        }
        query_params = {k: v for k, v in query_params.items() if v is not None}

        super().__init__(
            record_type=NCICRecordType.STOLEN_GUN,
            query_params=query_params,
            requesting_agency=requesting_agency,
            requesting_officer=requesting_officer,
            purpose=purpose,
        )


class ATFETraceRequest:
    """ATF eTrace request structure"""

    def __init__(
        self,
        request_type: ETraceRequestType,
        firearm_serial: str,
        firearm_make: str,
        firearm_model: str,
        firearm_caliber: str,
        firearm_type: str,
        recovery_date: datetime,
        recovery_location: dict[str, Any],
        recovery_circumstances: str,
        requesting_agency: str,
        requesting_officer: str,
        case_number: str,
        associated_crime: str | None = None,
        suspect_info: dict[str, Any] | None = None,
    ):
        self.id = str(uuid4())
        self.request_type = request_type
        self.firearm_serial = firearm_serial
        self.firearm_make = firearm_make
        self.firearm_model = firearm_model
        self.firearm_caliber = firearm_caliber
        self.firearm_type = firearm_type
        self.recovery_date = recovery_date
        self.recovery_location = recovery_location
        self.recovery_circumstances = recovery_circumstances
        self.requesting_agency = requesting_agency
        self.requesting_officer = requesting_officer
        self.case_number = case_number
        self.associated_crime = associated_crime
        self.suspect_info = suspect_info
        self.created_at = datetime.utcnow()

    def to_etrace_format(self) -> dict[str, Any]:
        """Convert to ATF eTrace format"""
        return {
            "ETraceRequest": {
                "RequestID": self.id,
                "RequestType": self.request_type.value,
                "Firearm": {
                    "SerialNumber": self.firearm_serial,
                    "Manufacturer": self.firearm_make,
                    "Model": self.firearm_model,
                    "Caliber": self.firearm_caliber,
                    "Type": self.firearm_type,
                },
                "Recovery": {
                    "Date": self.recovery_date.isoformat(),
                    "Location": self.recovery_location,
                    "Circumstances": self.recovery_circumstances,
                },
                "RequestingAgency": {
                    "ORI": self.requesting_agency,
                    "OfficerID": self.requesting_officer,
                },
                "CaseNumber": self.case_number,
                "AssociatedCrime": self.associated_crime,
                "SuspectInformation": self.suspect_info,
                "Timestamp": self.created_at.isoformat(),
            }
        }


class DHSSARReport:
    """DHS Suspicious Activity Report structure"""

    def __init__(
        self,
        activity_type: SARActivityType,
        activity_date: datetime,
        activity_location: dict[str, Any],
        activity_description: str,
        subject_description: str | None = None,
        vehicle_description: str | None = None,
        reporting_agency: str = "",
        reporting_officer: str = "",
        witness_info: list[dict[str, Any]] | None = None,
        evidence_collected: list[str] | None = None,
        threat_assessment: str | None = None,
        recommended_action: str | None = None,
    ):
        self.id = str(uuid4())
        self.activity_type = activity_type
        self.activity_date = activity_date
        self.activity_location = activity_location
        self.activity_description = activity_description
        self.subject_description = subject_description
        self.vehicle_description = vehicle_description
        self.reporting_agency = reporting_agency
        self.reporting_officer = reporting_officer
        self.witness_info = witness_info or []
        self.evidence_collected = evidence_collected or []
        self.threat_assessment = threat_assessment
        self.recommended_action = recommended_action
        self.created_at = datetime.utcnow()

    def to_sar_format(self) -> dict[str, Any]:
        """Convert to DHS SAR format"""
        return {
            "SuspiciousActivityReport": {
                "ReportID": self.id,
                "ActivityType": self.activity_type.value,
                "ActivityDateTime": self.activity_date.isoformat(),
                "ActivityLocation": self.activity_location,
                "ActivityDescription": self.activity_description,
                "SubjectDescription": self.subject_description,
                "VehicleDescription": self.vehicle_description,
                "ReportingAgency": {
                    "ORI": self.reporting_agency,
                    "OfficerID": self.reporting_officer,
                },
                "WitnessInformation": self.witness_info,
                "EvidenceCollected": self.evidence_collected,
                "ThreatAssessment": self.threat_assessment,
                "RecommendedAction": self.recommended_action,
                "ReportTimestamp": self.created_at.isoformat(),
            }
        }


class DataPseudonymizer:
    """Utility for pseudonymizing sensitive data for federal sharing"""

    def __init__(self, secret_key: str = "default_secret_key"):
        self.secret_key = secret_key

    def hash_value(
        self,
        value: str,
        method: PseudonymizationMethod = PseudonymizationMethod.SHA256_HASH,
    ) -> str:
        """Hash a value using specified method"""
        if method == PseudonymizationMethod.SHA256_HASH:
            return hashlib.sha256(value.encode()).hexdigest()
        elif method == PseudonymizationMethod.HMAC_SHA256:
            import hmac
            return hmac.new(
                self.secret_key.encode(),
                value.encode(),
                hashlib.sha256
            ).hexdigest()
        elif method == PseudonymizationMethod.TRUNCATION:
            return value[:4] + "****" if len(value) > 4 else "****"
        elif method == PseudonymizationMethod.GENERALIZATION:
            # For dates, generalize to year only
            if len(value) == 10 and "-" in value:  # YYYY-MM-DD format
                return value[:4] + "-XX-XX"
            return value
        elif method == PseudonymizationMethod.SUPPRESSION:
            return "[SUPPRESSED]"
        return value

    def pseudonymize_ssn(self, ssn: str) -> str:
        """Pseudonymize SSN"""
        return self.hash_value(ssn, PseudonymizationMethod.SHA256_HASH)

    def pseudonymize_dob(self, dob: str) -> str:
        """Pseudonymize date of birth"""
        return self.hash_value(dob, PseudonymizationMethod.GENERALIZATION)

    def pseudonymize_name(self, name: str) -> str:
        """Pseudonymize name (keep first initial)"""
        parts = name.split()
        if parts:
            return parts[0][0] + "." + " " + "*" * 5
        return "*****"

    def pseudonymize_record(
        self,
        record: dict[str, Any],
        fields_to_hash: list[str],
        fields_to_suppress: list[str],
    ) -> dict[str, Any]:
        """Pseudonymize a record"""
        result = record.copy()

        for field in fields_to_hash:
            if field in result and result[field]:
                result[field] = self.hash_value(str(result[field]))

        for field in fields_to_suppress:
            if field in result:
                result[field] = "[SUPPRESSED]"

        return result


class FederalDataMapper:
    """Maps local data to federal system formats"""

    def __init__(self):
        self.pseudonymizer = DataPseudonymizer()

    def map_person_to_ndex(
        self,
        local_person: dict[str, Any],
        pseudonymize: bool = True,
    ) -> NDExPersonRecord:
        """Map local person record to N-DEx format"""
        ssn_hash = None
        if "ssn" in local_person and local_person["ssn"]:
            ssn_hash = self.pseudonymizer.pseudonymize_ssn(local_person["ssn"])

        return NDExPersonRecord(
            person_id=local_person.get("id", str(uuid4())),
            first_name=local_person.get("first_name", ""),
            last_name=local_person.get("last_name", ""),
            middle_name=local_person.get("middle_name"),
            date_of_birth=local_person.get("date_of_birth"),
            gender=local_person.get("gender"),
            race=local_person.get("race"),
            ethnicity=local_person.get("ethnicity"),
            height=local_person.get("height"),
            weight=local_person.get("weight"),
            eye_color=local_person.get("eye_color"),
            hair_color=local_person.get("hair_color"),
            ssn_hash=ssn_hash,
            fbi_number=local_person.get("fbi_number"),
            state_id=local_person.get("state_id"),
            drivers_license=local_person.get("drivers_license"),
            aliases=local_person.get("aliases", []),
            scars_marks_tattoos=local_person.get("scars_marks_tattoos", []),
        )

    def map_incident_to_ndex(
        self,
        local_incident: dict[str, Any],
    ) -> NDExActivityRecord:
        """Map local incident to N-DEx activity format"""
        return NDExActivityRecord(
            activity_id=local_incident.get("id", str(uuid4())),
            activity_type=local_incident.get("incident_type", ""),
            activity_date=local_incident.get("incident_date", datetime.utcnow()),
            location=local_incident.get("location", {}),
            description=local_incident.get("description", ""),
            involved_persons=local_incident.get("involved_persons", []),
            involved_items=local_incident.get("involved_items", []),
            reporting_agency=local_incident.get("reporting_agency", ""),
            case_number=local_incident.get("case_number"),
        )

    def map_firearm_to_etrace(
        self,
        local_firearm: dict[str, Any],
        recovery_info: dict[str, Any],
        requesting_agency: str,
        requesting_officer: str,
        case_number: str,
    ) -> ATFETraceRequest:
        """Map local firearm to ATF eTrace request"""
        return ATFETraceRequest(
            request_type=ETraceRequestType.STANDARD_TRACE,
            firearm_serial=local_firearm.get("serial_number", ""),
            firearm_make=local_firearm.get("make", ""),
            firearm_model=local_firearm.get("model", ""),
            firearm_caliber=local_firearm.get("caliber", ""),
            firearm_type=local_firearm.get("firearm_type", ""),
            recovery_date=recovery_info.get("date", datetime.utcnow()),
            recovery_location=recovery_info.get("location", {}),
            recovery_circumstances=recovery_info.get("circumstances", ""),
            requesting_agency=requesting_agency,
            requesting_officer=requesting_officer,
            case_number=case_number,
            associated_crime=recovery_info.get("associated_crime"),
            suspect_info=recovery_info.get("suspect_info"),
        )

    def map_suspicious_activity_to_sar(
        self,
        local_activity: dict[str, Any],
        reporting_agency: str,
        reporting_officer: str,
    ) -> DHSSARReport:
        """Map local suspicious activity to DHS SAR format"""
        activity_type = SARActivityType.SECTOR_SPECIFIC
        activity_type_str = local_activity.get("activity_type", "")
        for sat in SARActivityType:
            if sat.value == activity_type_str:
                activity_type = sat
                break

        return DHSSARReport(
            activity_type=activity_type,
            activity_date=local_activity.get("activity_date", datetime.utcnow()),
            activity_location=local_activity.get("location", {}),
            activity_description=local_activity.get("description", ""),
            subject_description=local_activity.get("subject_description"),
            vehicle_description=local_activity.get("vehicle_description"),
            reporting_agency=reporting_agency,
            reporting_officer=reporting_officer,
            witness_info=local_activity.get("witnesses", []),
            evidence_collected=local_activity.get("evidence", []),
            threat_assessment=local_activity.get("threat_assessment"),
            recommended_action=local_activity.get("recommended_action"),
        )


class FederalDataReadinessManager:
    """Manager for federal data readiness operations"""

    def __init__(self):
        self.data_mapper = FederalDataMapper()
        self.prepared_records: dict[FederalSystem, list[dict[str, Any]]] = {
            FederalSystem.NDEX: [],
            FederalSystem.NCIC: [],
            FederalSystem.ATF_ETRACE: [],
            FederalSystem.DHS_SAR: [],
        }
        self.export_history: list[dict[str, Any]] = []

    def prepare_ndex_person(
        self,
        local_person: dict[str, Any],
        pseudonymize: bool = True,
    ) -> dict[str, Any]:
        """Prepare person record for N-DEx"""
        record = self.data_mapper.map_person_to_ndex(local_person, pseudonymize)
        formatted = record.to_ndex_format()
        self.prepared_records[FederalSystem.NDEX].append(formatted)
        return formatted

    def prepare_ndex_activity(
        self,
        local_incident: dict[str, Any],
    ) -> dict[str, Any]:
        """Prepare activity record for N-DEx"""
        record = self.data_mapper.map_incident_to_ndex(local_incident)
        formatted = record.to_ndex_format()
        self.prepared_records[FederalSystem.NDEX].append(formatted)
        return formatted

    def prepare_ncic_query(
        self,
        record_type: NCICRecordType,
        query_params: dict[str, Any],
        requesting_agency: str,
        requesting_officer: str,
        purpose: str,
    ) -> dict[str, Any]:
        """Prepare NCIC query structure"""
        query = NCICQueryStructure(
            record_type=record_type,
            query_params=query_params,
            requesting_agency=requesting_agency,
            requesting_officer=requesting_officer,
            purpose=purpose,
        )
        formatted = query.to_ncic_format()
        self.prepared_records[FederalSystem.NCIC].append(formatted)
        return formatted

    def prepare_etrace_request(
        self,
        local_firearm: dict[str, Any],
        recovery_info: dict[str, Any],
        requesting_agency: str,
        requesting_officer: str,
        case_number: str,
    ) -> dict[str, Any]:
        """Prepare ATF eTrace request"""
        request = self.data_mapper.map_firearm_to_etrace(
            local_firearm,
            recovery_info,
            requesting_agency,
            requesting_officer,
            case_number,
        )
        formatted = request.to_etrace_format()
        self.prepared_records[FederalSystem.ATF_ETRACE].append(formatted)
        return formatted

    def prepare_sar_report(
        self,
        local_activity: dict[str, Any],
        reporting_agency: str,
        reporting_officer: str,
    ) -> dict[str, Any]:
        """Prepare DHS SAR report"""
        report = self.data_mapper.map_suspicious_activity_to_sar(
            local_activity,
            reporting_agency,
            reporting_officer,
        )
        formatted = report.to_sar_format()
        self.prepared_records[FederalSystem.DHS_SAR].append(formatted)
        return formatted

    def get_prepared_records(
        self,
        system: FederalSystem,
    ) -> list[dict[str, Any]]:
        """Get all prepared records for a federal system"""
        return self.prepared_records.get(system, [])

    def clear_prepared_records(
        self,
        system: FederalSystem | None = None,
    ) -> None:
        """Clear prepared records"""
        if system:
            self.prepared_records[system] = []
        else:
            for sys in FederalSystem:
                self.prepared_records[sys] = []

    def export_records(
        self,
        system: FederalSystem,
        format_type: str = "json",
    ) -> dict[str, Any]:
        """Export prepared records (structure only, no actual transmission)"""
        records = self.prepared_records.get(system, [])

        export_entry = {
            "id": str(uuid4()),
            "system": system.value,
            "format": format_type,
            "record_count": len(records),
            "timestamp": datetime.utcnow().isoformat(),
            "status": "prepared",
        }
        self.export_history.append(export_entry)

        return {
            "export_id": export_entry["id"],
            "system": system.value,
            "format": format_type,
            "record_count": len(records),
            "records": records,
            "note": "Structure only - no live federal system integration",
        }

    def get_export_history(
        self,
        system: FederalSystem | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Get export history"""
        history = self.export_history.copy()
        if system:
            history = [h for h in history if h["system"] == system.value]
        return history[-limit:]


# Create singleton instance
federal_data_manager = FederalDataReadinessManager()
