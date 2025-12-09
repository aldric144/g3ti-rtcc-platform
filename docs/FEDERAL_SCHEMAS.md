# Federal Data Schemas

## Overview

This document describes the data schemas used for federal system integration in the G3TI RTCC-UIP platform. All schemas are designed to be compatible with federal standards while providing flexibility for local data mapping.

## N-DEx Schemas

### NDExPersonSchema

Maps person data to FBI N-DEx Person entity format.

```json
{
  "schema_name": "NDEx_Person_v5",
  "schema_version": "5.0",
  "federal_system": "ndex",
  "required_fields": [
    "person_id",
    "last_name",
    "first_name"
  ],
  "optional_fields": [
    "middle_name",
    "suffix",
    "date_of_birth",
    "sex",
    "race",
    "ethnicity",
    "height",
    "weight",
    "hair_color",
    "eye_color",
    "ssn",
    "drivers_license",
    "drivers_license_state",
    "fbi_number",
    "state_id",
    "address",
    "city",
    "state",
    "zip_code",
    "phone",
    "email",
    "scars_marks_tattoos",
    "photo_url"
  ],
  "sensitive_fields": [
    "date_of_birth",
    "ssn",
    "drivers_license",
    "address",
    "phone",
    "email"
  ]
}
```

**Role Types:**
- `Subject` - Primary subject of investigation
- `Victim` - Victim of crime
- `Witness` - Witness to incident
- `Suspect` - Suspected perpetrator
- `Arrestee` - Person arrested
- `MissingPerson` - Missing person
- `WantedPerson` - Wanted individual
- `RegisteredOffender` - Registered offender
- `Other` - Other role

### NDExIncidentSchema

Maps incident data to FBI N-DEx Incident entity format.

```json
{
  "schema_name": "NDEx_Incident_v5",
  "schema_version": "5.0",
  "federal_system": "ndex",
  "required_fields": [
    "incident_id",
    "incident_number",
    "incident_date",
    "reporting_agency_ori"
  ],
  "optional_fields": [
    "incident_time",
    "incident_type",
    "status",
    "location",
    "narrative",
    "offenses",
    "persons",
    "vehicles",
    "property",
    "firearms",
    "disposition"
  ],
  "sensitive_fields": [
    "narrative"
  ]
}
```

**Incident Types:**
- `Criminal` - Criminal incident
- `Traffic` - Traffic incident
- `Civil` - Civil matter
- `ServiceCall` - Service call
- `FieldInterview` - Field interview
- `MissingPerson` - Missing person report
- `DeathInvestigation` - Death investigation
- `Other` - Other type

### NDExVehicleSchema

Maps vehicle data to FBI N-DEx Vehicle entity format.

```json
{
  "schema_name": "NDEx_Vehicle_v5",
  "schema_version": "5.0",
  "federal_system": "ndex",
  "required_fields": [
    "vehicle_id"
  ],
  "optional_fields": [
    "vin",
    "license_plate",
    "license_state",
    "year",
    "make",
    "model",
    "color",
    "body_style",
    "vehicle_type",
    "status"
  ],
  "sensitive_fields": [
    "vin",
    "license_plate"
  ]
}
```

### NDExFirearmSchema

Maps firearm data to FBI N-DEx Firearm entity format.

```json
{
  "schema_name": "NDEx_Firearm_v5",
  "schema_version": "5.0",
  "federal_system": "ndex",
  "required_fields": [
    "firearm_id"
  ],
  "optional_fields": [
    "serial_number",
    "make",
    "model",
    "caliber",
    "firearm_type",
    "barrel_length",
    "finish",
    "country_of_origin",
    "importer",
    "ncic_gun_type",
    "status"
  ],
  "sensitive_fields": [
    "serial_number"
  ]
}
```

**NCIC Gun Types:**
- `P` - Pistol
- `R` - Revolver
- `S` - Shotgun
- `L` - Rifle
- `C` - Combination
- `D` - Derringer
- `G` - Machine Gun
- `B` - Submachine Gun
- `T` - Silencer
- `Z` - Other

## NCIC Query Schemas

### NCICVehicleQuerySchema

Structure for NCIC vehicle queries (stub only).

```json
{
  "schema_name": "NCIC_Vehicle_Query",
  "schema_version": "1.0",
  "federal_system": "ncic",
  "required_fields": [],
  "search_fields": [
    "vin",
    "license_plate",
    "license_state"
  ],
  "optional_fields": [
    "make",
    "model",
    "year",
    "color",
    "purpose"
  ]
}
```

**Validation Rules:**
- At least one of: VIN, license plate, or make+model+year required
- VIN must be 17 characters if provided
- License state must be valid 2-letter code

### NCICPersonQuerySchema

Structure for NCIC person queries (stub only).

```json
{
  "schema_name": "NCIC_Person_Query",
  "schema_version": "1.0",
  "federal_system": "ncic",
  "required_fields": [],
  "search_fields": [
    "last_name",
    "first_name",
    "date_of_birth",
    "ssn",
    "drivers_license",
    "fbi_number"
  ],
  "optional_fields": [
    "middle_name",
    "sex",
    "race",
    "purpose"
  ]
}
```

**Validation Rules:**
- At least one of: name+DOB, SSN, driver's license, or FBI number required
- Date of birth must be valid date format (YYYY-MM-DD)
- SSN must be 9 digits

### NCICGunQuerySchema

Structure for NCIC gun queries (stub only).

```json
{
  "schema_name": "NCIC_Gun_Query",
  "schema_version": "1.0",
  "federal_system": "ncic",
  "required_fields": [],
  "search_fields": [
    "serial_number"
  ],
  "optional_fields": [
    "make",
    "model",
    "caliber",
    "gun_type",
    "purpose"
  ]
}
```

**Validation Rules:**
- Serial number required for gun queries
- Gun type must be valid NCIC code if provided

## ATF eTrace Schemas

### ETraceTraceSchema

Structure for ATF eTrace trace requests.

```json
{
  "schema_name": "ATF_eTrace_Request",
  "schema_version": "1.0",
  "federal_system": "etrace",
  "required_fields": [
    "trace_id",
    "requesting_agency_ori",
    "requesting_officer",
    "recovery_date",
    "recovery_location",
    "firearm_type"
  ],
  "optional_fields": [
    "serial_number",
    "make",
    "model",
    "caliber",
    "barrel_length",
    "importer",
    "country_of_origin",
    "condition",
    "crime_code",
    "incident_id",
    "case_number",
    "possessor_info",
    "notes"
  ],
  "sensitive_fields": [
    "serial_number",
    "possessor_info"
  ]
}
```

**Firearm Types:**
- `pistol` - Pistol
- `revolver` - Revolver
- `rifle` - Rifle
- `shotgun` - Shotgun
- `derringer` - Derringer
- `machine_gun` - Machine Gun
- `submachine_gun` - Submachine Gun
- `silencer` - Silencer
- `destructive_device` - Destructive Device
- `any_other_weapon` - Any Other Weapon
- `unknown` - Unknown

**Recovery Types:**
- `crime_gun` - Crime Gun
- `found_firearm` - Found Firearm
- `safekeeping` - Safekeeping
- `voluntary_surrender` - Voluntary Surrender
- `buyback` - Buyback Program
- `other` - Other

## DHS SAR Schemas

### SARSchema

Structure for DHS Suspicious Activity Reports (ISE-SAR v1.5).

```json
{
  "schema_name": "DHS_SAR_ISE_v1.5",
  "schema_version": "1.5",
  "federal_system": "dhs_sar",
  "required_fields": [
    "sar_id",
    "reporting_agency_ori",
    "reporting_officer",
    "behavior_category",
    "activity_date",
    "activity_location",
    "narrative"
  ],
  "optional_fields": [
    "behavior_indicators",
    "subject_info",
    "vehicle_info",
    "threat_assessment",
    "related_incidents",
    "supporting_documents",
    "witness_info",
    "additional_notes"
  ],
  "sensitive_fields": [
    "subject_info",
    "witness_info",
    "narrative"
  ]
}
```

**Behavior Categories:**
- `acquisition_expertise` - Acquisition of Expertise
- `breach_intrusion` - Breach/Intrusion
- `elicitation` - Elicitation
- `misrepresentation` - Misrepresentation
- `observation_surveillance` - Observation/Surveillance
- `photography` - Photography
- `sabotage_tampering` - Sabotage/Tampering
- `sector_specific` - Sector-Specific Incident
- `testing_security` - Testing Security
- `theft_loss` - Theft/Loss/Diversion
- `weapons_explosives` - Weapons/Explosives
- `cyber_attack` - Cyber Attack
- `aviation` - Aviation Activity
- `chemical_biological` - Chemical/Biological
- `critical_infrastructure` - Critical Infrastructure
- `expressed_threat` - Expressed Threat
- `financing` - Financing
- `materials_acquisition` - Materials Acquisition
- `recruiting` - Recruiting
- `other` - Other

**Threat Levels:**
- `critical` - Critical/Imminent
- `high` - High/Severe
- `medium` - Medium/Moderate
- `low` - Low/Minor
- `unknown` - Unknown

## Secure Package Schema

### SecurePackageHeader

Header structure for encrypted federal message packages.

```json
{
  "package_id": "uuid",
  "message_type": "ndex_person|ndex_incident|ncic_query|etrace_request|dhs_sar",
  "originating_agency": "ORI code",
  "destination_system": "ndex|ncic|etrace|dhs_sar",
  "encryption_algorithm": "AES-256-GCM",
  "key_wrapping_algorithm": "RSA-OAEP",
  "signature_algorithm": "SHA-256",
  "created_at": "ISO 8601 timestamp",
  "version": "1.0"
}
```

### SecurePackage

Complete encrypted package structure.

```json
{
  "header": { /* SecurePackageHeader */ },
  "payload_encrypted": "base64 encoded encrypted payload",
  "wrapped_key": "base64 encoded RSA-wrapped AES key",
  "signature": "SHA-256 signature hex",
  "nonce": "base64 encoded nonce",
  "iv": "base64 encoded initialization vector",
  "auth_tag": "base64 encoded GCM authentication tag",
  "status": "created|encrypted|signed|ready|transmitted|failed"
}
```

## Data Transformation

### Field Normalization

The framework automatically normalizes data fields:

- **Names**: Converted to uppercase, trimmed
- **Dates**: Converted to ISO 8601 format (YYYY-MM-DD)
- **Addresses**: Normalized using standard abbreviations
- **Phone Numbers**: Formatted as (XXX) XXX-XXXX
- **SSN**: Validated as 9 digits, masked as ***-**-XXXX

### Sensitive Field Masking

Sensitive fields are automatically masked in exports:

| Field Type | Masking Pattern |
|------------|-----------------|
| SSN | ***-**-XXXX (last 4 visible) |
| DOB | ****-**-DD (day visible) |
| Driver's License | ***XXXX (last 4 visible) |
| Phone | ***-***-XXXX (last 4 visible) |
| Email | [EMAIL REDACTED] |
| Address | [ADDRESS REDACTED] |
| Criminal History | [CRIMINAL HISTORY REDACTED] |

### Identifier Hashing

For comparison without exposure, identifiers can be hashed:

```python
from app.federal.cjis import cjis_field_masker

hashed_ssn = cjis_field_masker.hash_identifier("123-45-6789")
# Returns SHA-256 hash for secure comparison
```
