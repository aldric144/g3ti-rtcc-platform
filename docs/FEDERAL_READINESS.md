# Federal Integration Readiness Framework

## Overview

The G3TI RTCC-UIP Federal Integration Readiness Framework (Phase 11) provides the data structures, validation rules, auditing frameworks, and secure communication scaffolding required for agencies to connect to federal law enforcement systems. This framework is designed for **readiness purposes only** and does not perform live federal integration.

## Supported Federal Systems

### FBI N-DEx (National Data Exchange)
The N-DEx module provides complete data mapping structures for exchanging criminal justice information with the FBI's National Data Exchange system.

**Capabilities:**
- Person profile mapping with role types (Subject, Victim, Witness, Suspect, Arrestee)
- Incident/arrest mapping with NIBRS offense code normalization
- Case summary mapping with related entity linking
- Property, Vehicle, and Firearms mapping
- Location mapping with address normalization
- Sensitive field masking (DOB, SSN, Driver's License)

**Endpoints:**
- `GET /api/federal/ndex/export/person/{id}` - Export person to N-DEx format
- `POST /api/federal/ndex/export/person` - Export person data to N-DEx format
- `GET /api/federal/ndex/export/incident/{id}` - Export incident to N-DEx format
- `POST /api/federal/ndex/export/incident` - Export incident data to N-DEx format

### FBI NCIC (National Crime Information Center)
The NCIC module provides query structure stubs for vehicle, person, and gun queries. **These are non-operational stubs for readiness testing only.**

**Capabilities:**
- Vehicle query structure (VIN, license plate, make/model)
- Person query structure (name, DOB, identifiers)
- Gun query structure (serial number, make/model, caliber)
- Local pre-validation engine
- NCIC-style message formatting

**Endpoints (STUB ONLY):**
- `POST /api/federal/ncic/query/vehicle` - Vehicle query stub
- `POST /api/federal/ncic/query/person` - Person query stub
- `POST /api/federal/ncic/query/gun` - Gun query stub
- `GET /api/federal/ncic/readiness` - Get NCIC readiness status

**Important:** All NCIC endpoints return stub responses with the disclaimer: "This is a non-operational NCIC request stub for readiness purposes only."

### ATF eTrace
The eTrace module provides firearms intelligence export capabilities for ATF trace requests.

**Capabilities:**
- Firearm trace request generation
- Firearm data normalization (make, model, caliber)
- Weapon-to-incident-to-suspect association mapping
- Recovery information mapping
- Possessor data mapping with sensitive field masking

**Endpoints:**
- `GET /api/federal/etrace/export/weapon/{id}` - Export weapon to eTrace format
- `POST /api/federal/etrace/export/weapon` - Export weapon data to eTrace format
- `GET /api/federal/etrace/export/incident/{id}` - Export all weapons from incident
- `GET /api/federal/etrace/statistics` - Get eTrace export statistics

### DHS SAR (Suspicious Activity Reporting)
The SAR module implements the ISE-SAR Functional Standard v1.5 for suspicious activity reporting.

**Capabilities:**
- 20 behavior categories (surveillance, photography, breach/intrusion, etc.)
- 30+ behavior indicators
- Subject and vehicle information mapping
- Geo-temporal attributes
- Threat assessment rating (Critical, High, Medium, Low, Unknown)
- Narrative sanitization for sensitive information

**Endpoints:**
- `POST /api/federal/sar/create` - Create new SAR
- `GET /api/federal/sar/{id}` - Get SAR by ID
- `PUT /api/federal/sar/{id}` - Update existing SAR
- `POST /api/federal/sar/{id}/submit` - Submit SAR for federal reporting
- `GET /api/federal/sar/list` - List SARs for agency
- `GET /api/federal/sar/statistics` - Get SAR statistics

## CJIS Compliance

The framework enforces CJIS Security Policy compliance across all federal operations:

### Policy Area 5: Access Control
- Role-based access control with federal_access permission
- User-specific permission overrides
- Access attempt logging
- Denied access tracking

### Policy Area 7: Encryption
- AES-256-GCM payload encryption
- RSA-OAEP key wrapping
- SHA-256 digital signatures
- Nonce-based replay protection

### Policy Area 8: Auditing and Accountability
- Comprehensive audit logging for all federal operations
- User identification and timestamp recording
- Success/failure tracking
- 7-year retention policy

### Policy Area 10: System and Communications Protection
- Sensitive field masking (SSN, DOB, Driver's License, Criminal History)
- Narrative sanitization
- Secure message packaging

## Architecture

```
backend/app/federal/
├── __init__.py              # Main federal module exports
├── common/
│   └── __init__.py          # Shared schemas, validation, transformation, auditing
├── ndex/
│   └── __init__.py          # N-DEx data exchange structures
├── ncic/
│   └── __init__.py          # NCIC query stubs (non-operational)
├── etrace/
│   └── __init__.py          # ATF eTrace firearms export
├── dhs_sar/
│   └── __init__.py          # DHS Suspicious Activity Reporting
├── cjis/
│   └── __init__.py          # CJIS compliance enforcement
└── secure_packaging/
    └── __init__.py          # Encryption and secure packaging

backend/app/api/federal/
└── __init__.py              # REST API endpoints

frontend/app/federal/
├── page.tsx                 # Federal Readiness Dashboard
└── components/
    ├── index.ts
    ├── FederalExportPanel.tsx
    ├── NDExExportViewer.tsx
    ├── ETraceExportViewer.tsx
    ├── SARSubmissionPanel.tsx
    ├── NCICReadinessPanel.tsx
    ├── CJISAuditLogViewer.tsx
    └── AccessControlManager.tsx
```

## Getting Started

### Prerequisites
- Users must have the `federal_access` role permission to access federal endpoints
- All federal operations are logged per CJIS Policy Area 8

### Configuration
Federal system configuration is managed through environment variables and the secure packaging manager. In production, register actual federal system public keys:

```python
from app.federal.secure_packaging import secure_packaging_manager

secure_packaging_manager.register_recipient_key(
    system_id="ndex",
    public_key_pem="-----BEGIN PUBLIC KEY-----\n...\n-----END PUBLIC KEY-----"
)
```

### Usage Example

```python
from app.federal.ndex import ndex_export_manager, NDExRoleType

# Export a person to N-DEx format
package = ndex_export_manager.export_person(
    person_data={
        "id": "person-123",
        "last_name": "Smith",
        "first_name": "John",
        "date_of_birth": "1990-01-15",
    },
    role_type=NDExRoleType.SUBJECT,
    agency_id="FL0000000",
    user_id="user-001",
    user_name="Officer Smith",
)

# Validate the export
validation = ndex_export_manager.validate_export(package.id)
if validation.is_valid:
    print(f"Export ready: {package.id}")
```

## Security Considerations

1. **No Live Integration**: This framework is for readiness purposes only. No actual federal queries or submissions are performed.

2. **Sensitive Data Masking**: All sensitive fields (SSN, DOB, Driver's License, Criminal History) are automatically masked in exports.

3. **Audit Logging**: All federal operations are logged with user identification, timestamps, and success/failure status.

4. **Access Control**: Only users with appropriate permissions can access federal endpoints.

5. **Encryption**: All federal message packages are encrypted using AES-256-GCM with RSA key wrapping.

## Future Integration

When ready for live federal integration:

1. Obtain appropriate federal system credentials and certificates
2. Register actual federal system public keys
3. Configure network connectivity to federal systems
4. Complete CJIS Security Addendum requirements
5. Conduct security assessment and penetration testing
6. Obtain authorization to operate (ATO)
