# Federal Message Formats

## Overview

This document describes the message formats used for federal system communication in the G3TI RTCC-UIP platform. All messages follow standardized formats compatible with federal system requirements.

## N-DEx Message Format

### Person Export Format

```json
{
  "message_type": "ndex_person",
  "federal_system": "ndex",
  "schema_version": "5.0",
  "payload": {
    "entity_type": "Person",
    "person_id": "uuid",
    "role_type": "Subject|Victim|Witness|Suspect|Arrestee",
    "name": {
      "last_name": "SMITH",
      "first_name": "JOHN",
      "middle_name": "WILLIAM",
      "suffix": "JR"
    },
    "identifiers": {
      "date_of_birth": "****-**-15",
      "sex": "M",
      "race": "W",
      "ethnicity": "N",
      "ssn_hash": "sha256_hash",
      "drivers_license_hash": "sha256_hash",
      "fbi_number": "123456A",
      "state_id": "FL12345678"
    },
    "physical_description": {
      "height": "511",
      "weight": "180",
      "hair_color": "BRO",
      "eye_color": "BLU",
      "scars_marks_tattoos": "Tattoo on left arm"
    },
    "location": {
      "address": "*** REDACTED ***",
      "city": "MIAMI",
      "state": "FL",
      "zip_code": "331**"
    },
    "contact": {
      "phone": "*** REDACTED ***",
      "email": "*** REDACTED ***"
    }
  },
  "metadata": {
    "originating_agency": "FL0000000",
    "export_timestamp": "2024-01-15T12:00:00Z",
    "export_id": "uuid"
  }
}
```

### Incident Export Format

```json
{
  "message_type": "ndex_incident",
  "federal_system": "ndex",
  "schema_version": "5.0",
  "payload": {
    "entity_type": "Incident",
    "incident_id": "uuid",
    "incident_number": "2024-00001234",
    "incident_date": "2024-01-15",
    "incident_time": "14:30:00",
    "incident_type": "Criminal",
    "status": "Active",
    "reporting_agency_ori": "FL0000000",
    "location": {
      "street_address": "123 MAIN ST",
      "city": "MIAMI",
      "state": "FL",
      "zip_code": "33101",
      "latitude": 25.7617,
      "longitude": -80.1918
    },
    "narrative": "[SANITIZED NARRATIVE]",
    "offenses": [
      {
        "offense_code": "13A",
        "offense_description": "Aggravated Assault",
        "nibrs_code": "13A",
        "attempted_completed": "C"
      }
    ],
    "persons": [
      {
        "person_id": "uuid",
        "role_type": "Subject",
        "name": "SMITH, JOHN"
      }
    ],
    "vehicles": [
      {
        "vehicle_id": "uuid",
        "description": "2020 TOYOTA CAMRY BLK"
      }
    ],
    "property": [],
    "firearms": []
  },
  "metadata": {
    "originating_agency": "FL0000000",
    "export_timestamp": "2024-01-15T12:00:00Z",
    "export_id": "uuid",
    "include_related": true
  }
}
```

## NCIC Message Format (Stub)

### Vehicle Query Format

```
MKE/QV
ORI/FL0000000
VIN/1HGBH41JXMN109186
LIC/ABC123
LIS/FL
VMA/TOYOTA
VMO/CAMRY
VYR/2020
VCO/BLK
PUR/C
EOM
```

**Field Codes:**
- `MKE` - Message Key (QV = Query Vehicle)
- `ORI` - Originating Agency Identifier
- `VIN` - Vehicle Identification Number
- `LIC` - License Plate Number
- `LIS` - License Plate State
- `VMA` - Vehicle Make
- `VMO` - Vehicle Model
- `VYR` - Vehicle Year
- `VCO` - Vehicle Color
- `PUR` - Purpose Code
- `EOM` - End of Message

### Person Query Format

```
MKE/QW
ORI/FL0000000
NAM/SMITH,JOHN,WILLIAM
DOB/19900115
SEX/M
RAC/W
OLN/D123456789
OLS/FL
PUR/C
EOM
```

**Field Codes:**
- `MKE` - Message Key (QW = Query Wanted Person)
- `NAM` - Name (Last,First,Middle)
- `DOB` - Date of Birth (YYYYMMDD)
- `SEX` - Sex
- `RAC` - Race
- `OLN` - Operator License Number
- `OLS` - Operator License State

### Gun Query Format

```
MKE/QG
ORI/FL0000000
SER/ABC123456
GMA/GLOCK
GMO/17
GCA/9MM
GTY/P
PUR/C
EOM
```

**Field Codes:**
- `MKE` - Message Key (QG = Query Gun)
- `SER` - Serial Number
- `GMA` - Gun Make
- `GMO` - Gun Model
- `GCA` - Gun Caliber
- `GTY` - Gun Type (P=Pistol, R=Revolver, etc.)

### Stub Response Format

```json
{
  "response_code": "STUB",
  "query_id": "uuid",
  "response_id": "uuid",
  "message": "This is a non-operational NCIC request stub for readiness purposes only. No actual NCIC query was performed.",
  "is_stub": true,
  "formatted_message": "MKE/QV.ORI/FL0000000.LIC/ABC123.LIS/FL.PUR/C.EOM",
  "sample_data": {
    "hit_status": "NO HIT",
    "response_time_ms": 0,
    "disclaimer": "NON-OPERATIONAL - READINESS TESTING ONLY"
  }
}
```

## ATF eTrace Message Format

### Trace Request Format

```json
{
  "message_type": "etrace_request",
  "federal_system": "etrace",
  "schema_version": "1.0",
  "payload": {
    "trace_number": "TR-2024-ABCD1234",
    "request_type": "trace_request",
    "requesting_agency": {
      "ori": "FL0000000",
      "name": "Sample Police Department",
      "officer": "Det. John Smith",
      "badge_number": "12345"
    },
    "firearm": {
      "type": "pistol",
      "make": "GLOCK",
      "model": "17",
      "caliber": "9MM",
      "serial_number": "***MASKED***",
      "barrel_length": "4.49",
      "importer": null,
      "country_of_origin": "Austria",
      "condition": "used",
      "obliterated_serial": false
    },
    "recovery": {
      "date": "2024-01-15",
      "type": "crime_gun",
      "location": {
        "street_address": "123 Main St",
        "city": "Miami",
        "state": "FL",
        "zip_code": "33101",
        "county": "Miami-Dade"
      },
      "description": "Recovered during traffic stop"
    },
    "possessor": {
      "last_name": "***MASKED***",
      "first_name": "***MASKED***",
      "date_of_birth": "****-**-**",
      "relationship_to_crime": "suspect"
    },
    "crime_info": {
      "crime_code": "13A",
      "incident_id": "INC-2024-001234",
      "case_number": "CASE-2024-5678"
    },
    "notes": "Additional investigative notes"
  },
  "metadata": {
    "created_at": "2024-01-15T12:00:00Z",
    "status": "ready",
    "validation_result": {
      "is_valid": true,
      "errors": [],
      "warnings": []
    }
  }
}
```

### Trace Report Format

```json
{
  "message_type": "etrace_report",
  "federal_system": "etrace",
  "report_number": "RPT-2024-EFGH5678",
  "trace_request_id": "uuid",
  "agency_id": "FL0000000",
  "export_format": "json",
  "created_at": "2024-01-15T12:00:00Z",
  "trace_data": {
    /* Full trace request data */
  }
}
```

## DHS SAR Message Format

### SAR Submission Format (ISE-SAR v1.5)

```json
{
  "message_type": "dhs_sar",
  "federal_system": "dhs_sar",
  "schema_version": "1.5",
  "payload": {
    "sar_number": "SAR-20240115-ABCD1234",
    "reporting_agency": {
      "ori": "FL0000000",
      "name": "Sample Police Department",
      "officer": "Officer Jane Doe",
      "badge_number": "54321"
    },
    "activity": {
      "behavior_category": "observation_surveillance",
      "behavior_indicators": [
        "photographing_facilities",
        "monitoring_personnel",
        "timing_operations"
      ],
      "date": "2024-01-15",
      "time": "14:30:00",
      "location": {
        "street_address": "456 Government Plaza",
        "city": "Miami",
        "state": "FL",
        "zip_code": "33101",
        "county": "Miami-Dade",
        "latitude": 25.7617,
        "longitude": -80.1918,
        "location_type": "government_building",
        "location_name": "Federal Courthouse"
      }
    },
    "narrative": "[SANITIZED NARRATIVE - Sensitive information redacted]",
    "threat_assessment": "medium",
    "subjects": [
      {
        "subject_type": "individual",
        "last_name": "***MASKED***",
        "first_name": "***MASKED***",
        "date_of_birth": "****-**-**",
        "sex": "M",
        "race": "W",
        "height": "5'10\"",
        "weight": "175",
        "hair_color": "Brown",
        "eye_color": "Blue",
        "clothing_description": "Dark jacket, jeans",
        "identifying_marks": "None observed"
      }
    ],
    "vehicles": [
      {
        "make": "Toyota",
        "model": "Camry",
        "year": "2020",
        "color": "Black",
        "license_plate": "***ABC",
        "license_state": "FL"
      }
    ],
    "related_incidents": ["INC-2024-001234"],
    "supporting_documents": [],
    "additional_notes": "Subject observed for approximately 30 minutes"
  },
  "metadata": {
    "created_at": "2024-01-15T15:00:00Z",
    "updated_at": "2024-01-15T15:30:00Z",
    "status": "submitted",
    "submitted_at": "2024-01-15T16:00:00Z",
    "approved_by": "Sgt. John Smith",
    "approved_at": "2024-01-15T15:45:00Z",
    "validation_result": {
      "is_valid": true,
      "errors": [],
      "warnings": ["Threat assessment not specified"]
    }
  }
}
```

## Secure Package Envelope

All federal messages are wrapped in a secure package envelope:

```json
{
  "header": {
    "package_id": "uuid",
    "message_type": "ndex_person|ndex_incident|ncic_query|etrace_request|dhs_sar",
    "originating_agency": "FL0000000",
    "destination_system": "ndex|ncic|etrace|dhs_sar",
    "encryption_algorithm": "AES-256-GCM",
    "key_wrapping_algorithm": "RSA-OAEP",
    "signature_algorithm": "SHA-256",
    "created_at": "2024-01-15T12:00:00Z",
    "version": "1.0"
  },
  "payload_encrypted": "base64_encoded_aes_encrypted_payload",
  "wrapped_key": "base64_encoded_rsa_wrapped_key",
  "signature": "sha256_hex_signature",
  "nonce": "base64_encoded_nonce",
  "iv": "base64_encoded_iv",
  "auth_tag": "base64_encoded_gcm_auth_tag",
  "status": "ready"
}
```

## Message Validation

### Validation Result Format

```json
{
  "is_valid": true,
  "errors": [],
  "warnings": [
    "Optional field 'middle_name' not provided",
    "Threat assessment defaulted to 'unknown'"
  ],
  "validated_data": {
    /* Validated and normalized data */
  }
}
```

### Common Validation Errors

| Error | Description |
|-------|-------------|
| `Missing required field: {field}` | Required field not provided |
| `Invalid date format: {value}` | Date not in YYYY-MM-DD format |
| `Invalid state code: {value}` | State not valid 2-letter code |
| `Invalid SSN format` | SSN not 9 digits |
| `Invalid VIN format` | VIN not 17 characters |
| `Narrative too short` | Narrative less than 50 characters |
| `No search parameters provided` | Query has no search criteria |

## Error Response Format

```json
{
  "success": false,
  "error_code": "VALIDATION_ERROR",
  "message": "Export validation failed",
  "details": {
    "errors": [
      "Missing required field: incident_date",
      "Invalid state code: XX"
    ],
    "warnings": []
  },
  "timestamp": "2024-01-15T12:00:00Z"
}
```

## API Response Formats

### Success Response

```json
{
  "success": true,
  "export_id": "uuid",
  "message": "Person exported to N-DEx format successfully",
  "data": {
    /* Masked export data */
  },
  "validation_errors": null,
  "validation_warnings": ["Optional field not provided"]
}
```

### Error Response

```json
{
  "success": false,
  "export_id": null,
  "message": "Validation failed",
  "data": null,
  "validation_errors": ["Missing required field: last_name"],
  "validation_warnings": []
}
```
