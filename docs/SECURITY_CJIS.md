# G3TI RTCC-UIP Security & CJIS Compliance

## Overview

The RTCC-UIP platform is designed to handle Criminal Justice Information (CJI) and must comply with the FBI's Criminal Justice Information Services (CJIS) Security Policy. This document outlines the security architecture and compliance measures implemented in the platform.

## CJIS Security Policy Requirements

The CJIS Security Policy establishes minimum security requirements for access to FBI CJIS systems and information. The platform addresses the following policy areas:

### Policy Area 1: Information Exchange Agreements

**Requirement**: Formal agreements must exist between agencies sharing CJI.

**Implementation**:
- API access requires agency-level authentication
- Data sharing agreements tracked in system configuration
- Audit logs capture all inter-agency data access

### Policy Area 2: Security Awareness Training

**Requirement**: All personnel with access to CJI must complete security awareness training.

**Implementation**:
- User accounts require training completion flag
- System can enforce training expiration dates
- Training status visible in user management

### Policy Area 3: Incident Response

**Requirement**: Agencies must have incident response capabilities.

**Implementation**:
- Comprehensive audit logging for forensic analysis
- Automated alerts for suspicious activity
- System health monitoring and alerting
- Documented incident response procedures

### Policy Area 4: Auditing and Accountability

**Requirement**: Systems must log and audit all access to CJI.

**Implementation**:
```python
class AuditLog:
    timestamp: datetime
    event_type: str        # LOGIN, LOGOUT, ACCESS, MODIFY, DELETE
    user_id: str
    username: str
    role: str
    action: str
    resource_type: str
    resource_id: str
    ip_address: str
    user_agent: str
    success: bool
    failure_reason: str    # If applicable
    details: dict          # Additional context
```

**Logged Events**:
- All authentication attempts (success/failure)
- All CJI access (view, search, export)
- All data modifications (create, update, delete)
- Administrative actions (user management, config changes)
- System events (startup, shutdown, errors)

**Retention**: Audit logs retained for minimum 1 year (configurable up to 7 years).

### Policy Area 5: Access Control

**Requirement**: Access to CJI must be restricted to authorized personnel.

**Implementation**:

#### Role-Based Access Control (RBAC)

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Role Hierarchy                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  admin (Level 5)                                                    │
│    ├── Full system access                                           │
│    ├── User management                                              │
│    ├── System configuration                                         │
│    └── All lower role permissions                                   │
│                                                                      │
│  supervisor (Level 4)                                               │
│    ├── Team management                                              │
│    ├── Report generation                                            │
│    ├── Investigation oversight                                      │
│    └── All lower role permissions                                   │
│                                                                      │
│  detective (Level 3)                                                │
│    ├── Full investigation access                                    │
│    ├── Entity creation/modification                                 │
│    ├── Advanced search                                              │
│    └── All lower role permissions                                   │
│                                                                      │
│  rtcc_analyst (Level 2)                                             │
│    ├── Real-time monitoring                                         │
│    ├── Event acknowledgment                                         │
│    ├── Basic search                                                 │
│    └── All lower role permissions                                   │
│                                                                      │
│  officer (Level 1)                                                  │
│    ├── View-only access                                             │
│    ├── Limited search                                               │
│    └── Event viewing                                                │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

#### Permission Matrix

| Resource | Officer | Analyst | Detective | Supervisor | Admin |
|----------|---------|---------|-----------|------------|-------|
| Events (View) | Yes | Yes | Yes | Yes | Yes |
| Events (Acknowledge) | No | Yes | Yes | Yes | Yes |
| Entities (View) | Yes | Yes | Yes | Yes | Yes |
| Entities (Create) | No | No | Yes | Yes | Yes |
| Entities (Modify) | No | No | Yes | Yes | Yes |
| Entities (Delete) | No | No | No | Yes | Yes |
| Investigations (View) | No | Yes | Yes | Yes | Yes |
| Investigations (Create) | No | No | Yes | Yes | Yes |
| Users (View) | No | No | No | Yes | Yes |
| Users (Manage) | No | No | No | No | Yes |
| System Config | No | No | No | No | Yes |

### Policy Area 6: Identification and Authentication

**Requirement**: Users must be uniquely identified and authenticated.

**Implementation**:

#### Password Requirements (CJIS Compliant)

```python
PASSWORD_REQUIREMENTS = {
    "min_length": 12,           # Minimum 12 characters
    "require_uppercase": True,   # At least 1 uppercase
    "require_lowercase": True,   # At least 1 lowercase
    "require_digit": True,       # At least 1 number
    "require_special": True,     # At least 1 special character
    "max_age_days": 90,         # Password expires after 90 days
    "history_count": 10,        # Cannot reuse last 10 passwords
    "lockout_threshold": 5,     # Lock after 5 failed attempts
    "lockout_duration_minutes": 15,  # 15-minute lockout
}
```

#### Password Hashing

```python
# bcrypt with 12 rounds (CJIS requirement)
BCRYPT_ROUNDS = 12

def hash_password(password: str) -> str:
    return bcrypt.hashpw(
        password.encode(),
        bcrypt.gensalt(rounds=BCRYPT_ROUNDS)
    ).decode()
```

#### Multi-Factor Authentication (MFA)

The platform supports MFA for enhanced security:
- TOTP (Time-based One-Time Password)
- SMS verification (optional)
- Hardware tokens (future)

### Policy Area 7: Configuration Management

**Requirement**: Systems must maintain secure configurations.

**Implementation**:
- Environment-based configuration
- Secrets management (no hardcoded credentials)
- Configuration change auditing
- Secure defaults

### Policy Area 8: Media Protection

**Requirement**: CJI must be protected on all media.

**Implementation**:
- Encryption at rest (AES-256)
- Encryption in transit (TLS 1.3)
- Secure file handling
- Data sanitization procedures

### Policy Area 9: Physical Protection

**Requirement**: Physical access to CJI systems must be controlled.

**Implementation**:
- Deployment in secure data centers
- Access logging at infrastructure level
- Environmental controls

### Policy Area 10: Systems and Communications Protection

**Requirement**: Systems must protect CJI during transmission.

**Implementation**:

#### Encryption Standards

```
┌─────────────────────────────────────────────────────────────────────┐
│                     Encryption Configuration                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Transport Layer Security (TLS)                                     │
│  ├── Minimum Version: TLS 1.2                                       │
│  ├── Preferred Version: TLS 1.3                                     │
│  └── Cipher Suites: FIPS 140-2 approved                            │
│                                                                      │
│  Data at Rest                                                       │
│  ├── Algorithm: AES-256-GCM                                         │
│  ├── Key Management: Secure key storage                             │
│  └── Database Encryption: Transparent Data Encryption               │
│                                                                      │
│  JWT Tokens                                                         │
│  ├── Algorithm: HS256 (HMAC-SHA256)                                │
│  ├── Access Token Expiry: 30 minutes                               │
│  └── Refresh Token Expiry: 7 days                                  │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

#### Network Security

- API endpoints require HTTPS
- WebSocket connections use WSS
- CORS configured for allowed origins only
- Rate limiting to prevent abuse

### Policy Area 11: Formal Audits

**Requirement**: Regular security audits must be conducted.

**Implementation**:
- Automated security scanning
- Vulnerability assessments
- Penetration testing support
- Compliance reporting

### Policy Area 12: Personnel Security

**Requirement**: Personnel with CJI access must be vetted.

**Implementation**:
- User account approval workflow
- Background check tracking
- Access termination procedures

### Policy Area 13: Mobile Devices

**Requirement**: Mobile devices accessing CJI must be secured.

**Implementation**:
- Responsive web design (no native app required)
- Session timeout on inactivity
- Secure cookie handling

## Security Architecture

### Defense in Depth

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Security Layers                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Layer 1: Network Security                                          │
│  ├── Firewall rules                                                 │
│  ├── Network segmentation                                           │
│  ├── DDoS protection                                                │
│  └── VPN for administrative access                                  │
│                                                                      │
│  Layer 2: Application Security                                      │
│  ├── Input validation                                               │
│  ├── Output encoding                                                │
│  ├── CSRF protection                                                │
│  ├── SQL injection prevention                                       │
│  └── XSS prevention                                                 │
│                                                                      │
│  Layer 3: Authentication & Authorization                            │
│  ├── JWT token validation                                           │
│  ├── Role-based access control                                      │
│  ├── Session management                                             │
│  └── MFA enforcement                                                │
│                                                                      │
│  Layer 4: Data Security                                             │
│  ├── Encryption at rest                                             │
│  ├── Encryption in transit                                          │
│  ├── Data masking                                                   │
│  └── Secure key management                                          │
│                                                                      │
│  Layer 5: Monitoring & Response                                     │
│  ├── Audit logging                                                  │
│  ├── Intrusion detection                                            │
│  ├── Anomaly detection                                              │
│  └── Incident response                                              │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Security Headers

```python
SECURITY_HEADERS = {
    "X-Frame-Options": "DENY",
    "X-Content-Type-Options": "nosniff",
    "X-XSS-Protection": "1; mode=block",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "Content-Security-Policy": "default-src 'self'",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "geolocation=(self)",
}
```

### Rate Limiting

```python
RATE_LIMITS = {
    "login": "5/minute",           # 5 login attempts per minute
    "api_general": "100/minute",   # 100 API calls per minute
    "search": "30/minute",         # 30 searches per minute
    "export": "10/hour",           # 10 exports per hour
}
```

## Incident Response

### Security Event Categories

| Category | Severity | Response Time | Examples |
|----------|----------|---------------|----------|
| Critical | P1 | Immediate | Data breach, system compromise |
| High | P2 | 1 hour | Failed intrusion attempt, malware |
| Medium | P3 | 4 hours | Policy violation, suspicious activity |
| Low | P4 | 24 hours | Minor policy deviation |

### Incident Response Workflow

```
┌─────────────────┐
│    Detection    │
│  (Automated/    │
│   Manual)       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Assessment    │
│  (Severity,     │
│   Scope)        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Containment    │
│  (Isolate,      │
│   Preserve)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Eradication    │
│  (Remove        │
│   Threat)       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Recovery      │
│  (Restore       │
│   Services)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Post-Incident  │
│  (Review,       │
│   Improve)      │
└─────────────────┘
```

## Compliance Checklist

### Pre-Deployment

- [ ] Security assessment completed
- [ ] Penetration testing performed
- [ ] CJIS Security Addendum signed
- [ ] Personnel background checks completed
- [ ] Security awareness training completed
- [ ] Incident response plan documented
- [ ] Data backup procedures tested

### Ongoing

- [ ] Monthly security reviews
- [ ] Quarterly access reviews
- [ ] Annual penetration testing
- [ ] Annual CJIS audit
- [ ] Continuous monitoring active
- [ ] Patch management current

## Contact Information

For security concerns or incident reporting:
- Security Team: security@g3ti.com
- Emergency: [Emergency Contact Number]
- CJIS ISO: [CJIS Information Security Officer]
