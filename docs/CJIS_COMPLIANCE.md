# CJIS Security Policy Compliance

## Overview

The G3TI RTCC-UIP Federal Integration Readiness Framework implements comprehensive CJIS Security Policy compliance across all federal operations. This document details the compliance measures for Policy Areas 5, 7, 8, and 10.

## Policy Area 5: Access Control

### Role-Based Access Control (RBAC)

The framework implements role-based access control with the following predefined roles:

| Role | Federal Access | N-DEx Export | NCIC Query | eTrace Export | SAR Submit | Audit Logs |
|------|---------------|--------------|------------|---------------|------------|------------|
| Admin | Yes | Yes | Yes | Yes | Yes | Yes |
| Supervisor | Yes | Yes | Yes | Yes | Yes | Yes |
| Detective | Yes | Yes | Yes | Yes | Yes | No |
| RTCC Analyst | Yes | Yes | No | No | Yes | No |
| Officer | No | No | No | No | No | No |

### Permission Management

```python
from app.federal.cjis import cjis_access_control

# Set user role
cjis_access_control.set_user_role("user-001", "detective")

# Grant specific permission
cjis_access_control.grant_permission("user-001", "can_view_audit_logs")

# Revoke specific permission
cjis_access_control.revoke_permission("user-001", "can_query_ncic")

# Check permission
has_access = cjis_access_control.has_permission("user-001", "can_export_ndex")
```

### Access Control Enforcement

All federal endpoints enforce access control:

```python
from app.federal.cjis import cjis_compliance_manager, CJISResourceType

# Check access before operation
has_access, error = cjis_compliance_manager.check_federal_access(
    user_id="user-001",
    user_name="John Smith",
    agency_id="FL0000000",
    operation="ndex_export",
    resource_type=CJISResourceType.NDEX_EXPORT,
    resource_id="export-123",
    ip_address="192.168.1.100",
)

if not has_access:
    raise PermissionError(error)
```

### Access Denied Logging

All access denied events are logged:

```python
from app.federal.cjis import cjis_audit_logger, CJISResourceType

cjis_audit_logger.log_access_denied(
    user_id="user-003",
    user_name="Bob Wilson",
    agency_id="FL0000000",
    resource_type=CJISResourceType.FEDERAL_DATA,
    resource_id=None,
    reason="Missing permission: federal_access",
    ip_address="192.168.1.102",
)
```

## Policy Area 7: Encryption

### Encryption at Rest

All federal data exports are encrypted using AES-256-GCM:

- **Algorithm**: AES-256-GCM (Galois/Counter Mode)
- **Key Size**: 256 bits
- **IV Size**: 96 bits (12 bytes)
- **Authentication Tag**: 128 bits (16 bytes)

### Key Management

Symmetric encryption keys are wrapped using RSA-OAEP:

- **Algorithm**: RSA-OAEP
- **Padding**: OAEP with SHA-256
- **Key Size**: 2048+ bits recommended

### Encryption Implementation

```python
from app.federal.secure_packaging import secure_packaging_manager

# Create encrypted package
package = secure_packaging_manager.create_secure_package(
    payload={"person_id": "123", "name": "John Smith"},
    message_type="ndex_person",
    originating_agency="FL0000000",
    destination_system="ndex",
)

# Package contains:
# - encrypted_payload: AES-256-GCM encrypted data
# - wrapped_key: RSA-OAEP wrapped symmetric key
# - signature: SHA-256 signature
# - nonce: Replay protection nonce
# - iv: Initialization vector
# - auth_tag: GCM authentication tag
```

### Encryption Status

```python
status = secure_packaging_manager.get_encryption_status()
# Returns:
# {
#     "status": "ready",
#     "encryption": {"algorithm": "AES-256-GCM", "key_size": "256 bits"},
#     "key_wrapping": {"algorithm": "RSA-OAEP"},
#     "signature": {"algorithm": "SHA-256"},
#     "replay_protection": {"method": "Cryptographic nonce"},
#     "cjis_compliance": {"area_7_encryption": "compliant"}
# }
```

## Policy Area 8: Auditing and Accountability

### Audit Log Requirements

All federal operations are logged with the following information:

| Field | Description |
|-------|-------------|
| `id` | Unique audit entry ID |
| `user_id` | User performing the action |
| `user_name` | User's display name |
| `agency_id` | Agency ORI code |
| `action` | Action performed (query, export, create, etc.) |
| `resource_type` | Type of resource accessed |
| `resource_id` | ID of specific resource |
| `ip_address` | Client IP address |
| `user_agent` | Client user agent |
| `session_id` | Session identifier |
| `success` | Whether action succeeded |
| `error_message` | Error message if failed |
| `details` | Additional action details |
| `policy_areas` | CJIS policy areas involved |
| `timestamp` | UTC timestamp |
| `retention_until` | Retention expiration date |

### Audit Actions

The following actions are logged:

- `login` - User login
- `logout` - User logout
- `query` - Data query
- `view` - Data view
- `create` - Record creation
- `update` - Record update
- `delete` - Record deletion
- `export` - Data export
- `import` - Data import
- `print` - Data print
- `download` - Data download
- `share` - Data sharing
- `access_denied` - Access denied
- `authentication_failure` - Authentication failure
- `authorization_failure` - Authorization failure

### Audit Logging Implementation

```python
from app.federal.cjis import cjis_audit_logger, CJISAuditAction, CJISResourceType

# Log federal export
entry = cjis_audit_logger.log_federal_export(
    user_id="user-001",
    user_name="John Smith",
    agency_id="FL0000000",
    export_type="ndex",
    resource_id="export-123",
    ip_address="192.168.1.100",
    success=True,
)

# Query audit log
entries = cjis_audit_logger.get_audit_log(
    agency_id="FL0000000",
    action=CJISAuditAction.EXPORT,
    since=datetime(2024, 1, 1),
    limit=100,
)

# Get failed access attempts
failed = cjis_audit_logger.get_failed_access_attempts(
    agency_id="FL0000000",
    since=datetime(2024, 1, 1),
)
```

### Retention Policy

Audit logs are retained for **7 years** per CJIS requirements:

```python
entry = CJISAuditEntry(...)
print(entry.retention_years)  # 7
print(entry.retention_until)  # 7 years from creation
```

### Compliance Reporting

Generate CJIS compliance reports:

```python
report = cjis_audit_logger.generate_compliance_report(
    agency_id="FL0000000",
    start_date=datetime(2024, 1, 1),
    end_date=datetime(2024, 12, 31),
)

# Report includes:
# - Total events
# - Events by action type
# - Events by resource type
# - Events by policy area
# - Success/failure counts
# - Unique user count
# - Federal export count
# - Compliance status for each policy area
```

## Policy Area 10: System and Communications Protection

### Sensitive Field Masking

The framework automatically masks sensitive fields:

```python
from app.federal.cjis import cjis_field_masker

# Mask individual fields
masked_ssn = cjis_field_masker.mask_ssn("123-45-6789")  # ***-**-6789
masked_dob = cjis_field_masker.mask_dob("1990-01-15")  # ****-**-15
masked_dl = cjis_field_masker.mask_drivers_license("D123456789")  # ******6789
masked_phone = cjis_field_masker.mask_phone("555-123-4567")  # ***-***-4567
masked_email = cjis_field_masker.mask_email("john@example.com")  # [EMAIL REDACTED]

# Mask entire dictionary
data = {
    "name": "John Smith",
    "ssn": "123-45-6789",
    "date_of_birth": "1990-01-15",
    "phone": "555-123-4567",
}
masked_data = cjis_field_masker.mask_dict(data)
```

### Narrative Sanitization

Narratives are automatically sanitized to remove sensitive information:

```python
narrative = "Subject John Smith, SSN 123-45-6789, phone 555-123-4567"
sanitized = cjis_field_masker.mask_narrative(narrative)
# "Subject John Smith, SSN [SSN REDACTED], phone [PHONE REDACTED]"
```

### Identifier Hashing

For secure comparison without exposure:

```python
hash1 = cjis_field_masker.hash_identifier("123-45-6789")
hash2 = cjis_field_masker.hash_identifier("123-45-6789")
assert hash1 == hash2  # Same input produces same hash
```

### Replay Protection

All secure packages include nonce-based replay protection:

```python
from app.federal.secure_packaging import NonceManager

nonce_manager = NonceManager()

# Generate unique nonce
nonce = nonce_manager.generate_nonce()

# Mark nonce as used (returns False if already used)
success = nonce_manager.use_nonce(nonce)

# Check if nonce was used
is_used = nonce_manager.is_nonce_used(nonce)
```

## Compliance Status API

Get overall compliance status:

```python
from app.federal.cjis import cjis_compliance_manager

status = cjis_compliance_manager.get_compliance_status()
# Returns:
# {
#     "status": "compliant",
#     "policy_areas": {
#         "area_5_access_control": {"status": "enforced", ...},
#         "area_7_encryption": {"status": "ready", ...},
#         "area_8_auditing": {"status": "active", ...},
#         "area_10_system_protection": {"status": "enforced", ...}
#     },
#     "last_audit": "2024-01-15T12:00:00Z"
# }
```

## REST API Endpoints

### Audit Log Endpoints

- `GET /api/federal/cjis/audit-log` - Query audit log with filters
- `GET /api/federal/cjis/compliance-report` - Generate compliance report
- `GET /api/federal/cjis/status` - Get compliance status

### Access Requirements

- Audit log access requires `can_view_audit_logs` permission
- Only supervisors and administrators have this permission by default

## Best Practices

1. **Principle of Least Privilege**: Grant only necessary permissions
2. **Regular Audits**: Review audit logs regularly for anomalies
3. **Access Reviews**: Periodically review user access levels
4. **Incident Response**: Have procedures for security incidents
5. **Training**: Ensure users understand CJIS requirements
6. **Documentation**: Maintain records of compliance activities
