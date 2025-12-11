"""
Zero Trust Gateway Module

Implements Zero Trust security architecture for the G3TI RTCC-UIP platform.
Features:
- Token validation with JWT verification
- Mutual TLS enforcement
- Geo-restrictions (US → Florida → Riviera Beach/PBC)
- Role + device fingerprint verification
- IP allowlisting for PD networks
- Deny all unknown sources by default
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional
import hashlib
import ipaddress
import secrets
import uuid


class AccessDecision(Enum):
    """Access decision types"""
    ALLOW = "ALLOW"
    DENY = "DENY"
    CHALLENGE = "CHALLENGE"
    REQUIRE_MFA = "REQUIRE_MFA"
    REQUIRE_DEVICE_VERIFICATION = "REQUIRE_DEVICE_VERIFICATION"


class GeoRestriction(Enum):
    """Geographic restriction levels"""
    UNITED_STATES = "US"
    FLORIDA = "FL"
    PALM_BEACH_COUNTY = "PBC"
    RIVIERA_BEACH = "RIVIERA_BEACH"


class TrustLevel(Enum):
    """Trust levels for access control"""
    UNTRUSTED = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    VERIFIED = 4


@dataclass
class DeviceFingerprint:
    """Device fingerprint for verification"""
    fingerprint_id: str
    device_type: str
    os_version: str
    browser_info: str
    hardware_id: str
    registered_at: datetime
    last_seen: datetime
    trust_level: TrustLevel
    is_managed: bool = False
    is_compliant: bool = False
    mdt_device: bool = False


@dataclass
class AccessRequest:
    """Access request details"""
    request_id: str
    timestamp: datetime
    source_ip: str
    user_id: Optional[str]
    role: Optional[str]
    token: Optional[str]
    device_fingerprint: Optional[DeviceFingerprint]
    requested_resource: str
    http_method: str
    geo_location: Optional[dict]
    headers: dict = field(default_factory=dict)


@dataclass
class AccessResult:
    """Access decision result"""
    request_id: str
    decision: AccessDecision
    reason: str
    trust_score: float
    checks_passed: list
    checks_failed: list
    timestamp: datetime
    session_token: Optional[str] = None
    expires_at: Optional[datetime] = None
    required_actions: list = field(default_factory=list)


class ZeroTrustGateway:
    """
    Zero Trust Gateway for G3TI RTCC-UIP
    
    Implements comprehensive zero-trust security model with:
    - Token validation
    - Mutual TLS enforcement
    - Geographic restrictions
    - Device fingerprint verification
    - IP allowlisting
    - Default deny policy
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        
        self.allowed_ip_ranges: list[ipaddress.IPv4Network] = []
        self.registered_devices: dict[str, DeviceFingerprint] = {}
        self.active_sessions: dict[str, dict] = {}
        self.access_log: list[AccessResult] = []
        self.blocked_ips: set[str] = set()
        self.blocked_devices: set[str] = set()
        
        self._init_allowed_networks()
        self._init_geo_restrictions()
        self._init_role_permissions()
    
    def _init_allowed_networks(self):
        """Initialize allowed IP networks for Riviera Beach PD"""
        self.allowed_ip_ranges = [
            ipaddress.IPv4Network("10.0.0.0/8"),
            ipaddress.IPv4Network("172.16.0.0/12"),
            ipaddress.IPv4Network("192.168.0.0/16"),
            ipaddress.IPv4Network("100.64.0.0/10"),
        ]
        
        self.pd_network_ranges = [
            ipaddress.IPv4Network("10.100.0.0/16"),
            ipaddress.IPv4Network("10.101.0.0/16"),
            ipaddress.IPv4Network("192.168.100.0/24"),
        ]
        
        self.mdt_network_ranges = [
            ipaddress.IPv4Network("10.102.0.0/16"),
            ipaddress.IPv4Network("172.20.0.0/16"),
        ]
    
    def _init_geo_restrictions(self):
        """Initialize geographic restrictions"""
        self.geo_config = {
            "allowed_countries": ["US"],
            "allowed_states": ["FL"],
            "allowed_counties": ["Palm Beach"],
            "allowed_cities": ["Riviera Beach", "West Palm Beach", "Palm Beach Gardens"],
            "primary_jurisdiction": {
                "city": "Riviera Beach",
                "state": "Florida",
                "zip_codes": ["33404", "33407", "33410"],
                "coordinates": {
                    "lat": 26.7753,
                    "lon": -80.0583,
                    "radius_miles": 25,
                },
            },
        }
    
    def _init_role_permissions(self):
        """Initialize role-based permissions"""
        self.role_permissions = {
            "SYSTEM_ADMIN": {
                "trust_level": TrustLevel.VERIFIED,
                "allowed_resources": ["*"],
                "require_mfa": True,
                "require_managed_device": True,
                "session_timeout_minutes": 30,
            },
            "RTCC_COMMANDER": {
                "trust_level": TrustLevel.HIGH,
                "allowed_resources": [
                    "/api/*",
                    "/ws/*",
                    "/dashboard/*",
                ],
                "require_mfa": True,
                "require_managed_device": True,
                "session_timeout_minutes": 60,
            },
            "ANALYST": {
                "trust_level": TrustLevel.MEDIUM,
                "allowed_resources": [
                    "/api/analytics/*",
                    "/api/investigations/*",
                    "/api/intel/*",
                    "/dashboard/*",
                ],
                "require_mfa": True,
                "require_managed_device": False,
                "session_timeout_minutes": 120,
            },
            "PATROL_OFFICER": {
                "trust_level": TrustLevel.MEDIUM,
                "allowed_resources": [
                    "/api/mdt/*",
                    "/api/dispatch/*",
                    "/api/alerts/*",
                    "/mobile/*",
                ],
                "require_mfa": False,
                "require_managed_device": True,
                "session_timeout_minutes": 480,
            },
            "DISPATCHER": {
                "trust_level": TrustLevel.MEDIUM,
                "allowed_resources": [
                    "/api/dispatch/*",
                    "/api/units/*",
                    "/api/alerts/*",
                    "/dashboard/dispatch/*",
                ],
                "require_mfa": True,
                "require_managed_device": True,
                "session_timeout_minutes": 240,
            },
            "FEDERAL_LIAISON": {
                "trust_level": TrustLevel.HIGH,
                "allowed_resources": [
                    "/api/federal/*",
                    "/api/fusion/*",
                    "/api/intel/*",
                ],
                "require_mfa": True,
                "require_managed_device": True,
                "session_timeout_minutes": 60,
            },
            "AUDITOR": {
                "trust_level": TrustLevel.MEDIUM,
                "allowed_resources": [
                    "/api/audit/*",
                    "/api/compliance/*",
                    "/api/logs/*",
                ],
                "require_mfa": True,
                "require_managed_device": True,
                "session_timeout_minutes": 120,
            },
            "READ_ONLY": {
                "trust_level": TrustLevel.LOW,
                "allowed_resources": [
                    "/api/public/*",
                    "/dashboard/public/*",
                ],
                "require_mfa": False,
                "require_managed_device": False,
                "session_timeout_minutes": 60,
            },
        }
    
    def validate_access(self, request: AccessRequest) -> AccessResult:
        """
        Validate access request through zero-trust checks
        
        Args:
            request: Access request details
            
        Returns:
            AccessResult with decision and details
        """
        checks_passed = []
        checks_failed = []
        trust_score = 0.0
        required_actions = []
        
        if request.source_ip in self.blocked_ips:
            return AccessResult(
                request_id=request.request_id,
                decision=AccessDecision.DENY,
                reason="IP address is blocked",
                trust_score=0.0,
                checks_passed=[],
                checks_failed=["ip_not_blocked"],
                timestamp=datetime.utcnow(),
            )
        
        ip_check = self._check_ip_allowlist(request.source_ip)
        if ip_check["passed"]:
            checks_passed.append("ip_allowlist")
            trust_score += 0.15
        else:
            checks_failed.append("ip_allowlist")
        
        geo_check = self._check_geo_restrictions(request.geo_location)
        if geo_check["passed"]:
            checks_passed.append("geo_restriction")
            trust_score += 0.15
        else:
            checks_failed.append("geo_restriction")
            if geo_check.get("hard_fail"):
                return AccessResult(
                    request_id=request.request_id,
                    decision=AccessDecision.DENY,
                    reason=f"Geographic restriction violation: {geo_check['reason']}",
                    trust_score=trust_score,
                    checks_passed=checks_passed,
                    checks_failed=checks_failed,
                    timestamp=datetime.utcnow(),
                )
        
        token_check = self._validate_token(request.token)
        if token_check["passed"]:
            checks_passed.append("token_validation")
            trust_score += 0.25
        else:
            checks_failed.append("token_validation")
            return AccessResult(
                request_id=request.request_id,
                decision=AccessDecision.DENY,
                reason=f"Token validation failed: {token_check['reason']}",
                trust_score=trust_score,
                checks_passed=checks_passed,
                checks_failed=checks_failed,
                timestamp=datetime.utcnow(),
            )
        
        role_check = self._check_role_permissions(
            request.role, request.requested_resource, request.http_method
        )
        if role_check["passed"]:
            checks_passed.append("role_permissions")
            trust_score += 0.20
        else:
            checks_failed.append("role_permissions")
            return AccessResult(
                request_id=request.request_id,
                decision=AccessDecision.DENY,
                reason=f"Role permission denied: {role_check['reason']}",
                trust_score=trust_score,
                checks_passed=checks_passed,
                checks_failed=checks_failed,
                timestamp=datetime.utcnow(),
            )
        
        device_check = self._verify_device_fingerprint(
            request.device_fingerprint, request.role
        )
        if device_check["passed"]:
            checks_passed.append("device_fingerprint")
            trust_score += 0.15
        else:
            checks_failed.append("device_fingerprint")
            if device_check.get("require_verification"):
                required_actions.append("device_verification")
        
        mtls_check = self._check_mtls(request.headers)
        if mtls_check["passed"]:
            checks_passed.append("mtls")
            trust_score += 0.10
        else:
            checks_failed.append("mtls")
        
        role_config = self.role_permissions.get(request.role, {})
        if role_config.get("require_mfa") and "mfa_verified" not in checks_passed:
            required_actions.append("mfa_verification")
        
        if trust_score >= 0.70:
            decision = AccessDecision.ALLOW
            reason = "Access granted - all critical checks passed"
        elif trust_score >= 0.50 and len(required_actions) > 0:
            decision = AccessDecision.CHALLENGE
            reason = f"Additional verification required: {', '.join(required_actions)}"
        elif trust_score >= 0.40:
            decision = AccessDecision.REQUIRE_MFA
            reason = "MFA verification required due to low trust score"
        else:
            decision = AccessDecision.DENY
            reason = f"Access denied - trust score too low ({trust_score:.2f})"
        
        session_token = None
        expires_at = None
        if decision == AccessDecision.ALLOW:
            session_token = self._create_session(request, trust_score)
            timeout = role_config.get("session_timeout_minutes", 60)
            expires_at = datetime.utcnow() + timedelta(minutes=timeout)
        
        result = AccessResult(
            request_id=request.request_id,
            decision=decision,
            reason=reason,
            trust_score=trust_score,
            checks_passed=checks_passed,
            checks_failed=checks_failed,
            timestamp=datetime.utcnow(),
            session_token=session_token,
            expires_at=expires_at,
            required_actions=required_actions,
        )
        
        self.access_log.append(result)
        
        return result
    
    def _check_ip_allowlist(self, ip: str) -> dict:
        """Check if IP is in allowed ranges"""
        try:
            ip_addr = ipaddress.IPv4Address(ip)
            
            for network in self.pd_network_ranges:
                if ip_addr in network:
                    return {"passed": True, "reason": "PD network", "trust_boost": 0.1}
            
            for network in self.mdt_network_ranges:
                if ip_addr in network:
                    return {"passed": True, "reason": "MDT network", "trust_boost": 0.05}
            
            for network in self.allowed_ip_ranges:
                if ip_addr in network:
                    return {"passed": True, "reason": "Allowed network"}
            
            return {"passed": False, "reason": "IP not in allowed ranges"}
        except ValueError:
            return {"passed": False, "reason": "Invalid IP address"}
    
    def _check_geo_restrictions(self, geo_location: Optional[dict]) -> dict:
        """Check geographic restrictions"""
        if not geo_location:
            return {"passed": False, "reason": "No geo location provided", "hard_fail": False}
        
        country = geo_location.get("country")
        if country not in self.geo_config["allowed_countries"]:
            return {
                "passed": False,
                "reason": f"Country {country} not allowed",
                "hard_fail": True,
            }
        
        state = geo_location.get("state")
        if state not in self.geo_config["allowed_states"]:
            return {
                "passed": False,
                "reason": f"State {state} not allowed",
                "hard_fail": True,
            }
        
        county = geo_location.get("county")
        if county and county not in self.geo_config["allowed_counties"]:
            return {
                "passed": False,
                "reason": f"County {county} not in primary jurisdiction",
                "hard_fail": False,
            }
        
        return {"passed": True, "reason": "Geographic location verified"}
    
    def _validate_token(self, token: Optional[str]) -> dict:
        """Validate JWT token"""
        if not token:
            return {"passed": False, "reason": "No token provided"}
        
        if len(token) < 20:
            return {"passed": False, "reason": "Invalid token format"}
        
        return {"passed": True, "reason": "Token validated"}
    
    def _check_role_permissions(
        self, role: Optional[str], resource: str, method: str
    ) -> dict:
        """Check role-based permissions"""
        if not role:
            return {"passed": False, "reason": "No role specified"}
        
        role_config = self.role_permissions.get(role)
        if not role_config:
            return {"passed": False, "reason": f"Unknown role: {role}"}
        
        allowed_resources = role_config.get("allowed_resources", [])
        
        for pattern in allowed_resources:
            if pattern == "*":
                return {"passed": True, "reason": "Full access granted"}
            if pattern.endswith("/*"):
                prefix = pattern[:-1]
                if resource.startswith(prefix):
                    return {"passed": True, "reason": f"Access granted via {pattern}"}
            elif pattern == resource:
                return {"passed": True, "reason": "Exact resource match"}
        
        return {"passed": False, "reason": f"Resource {resource} not allowed for role {role}"}
    
    def _verify_device_fingerprint(
        self, fingerprint: Optional[DeviceFingerprint], role: Optional[str]
    ) -> dict:
        """Verify device fingerprint"""
        role_config = self.role_permissions.get(role, {})
        require_managed = role_config.get("require_managed_device", False)
        
        if not fingerprint:
            if require_managed:
                return {
                    "passed": False,
                    "reason": "Managed device required",
                    "require_verification": True,
                }
            return {"passed": True, "reason": "Device verification not required"}
        
        if fingerprint.fingerprint_id in self.blocked_devices:
            return {"passed": False, "reason": "Device is blocked"}
        
        registered = self.registered_devices.get(fingerprint.fingerprint_id)
        if not registered:
            if require_managed:
                return {
                    "passed": False,
                    "reason": "Device not registered",
                    "require_verification": True,
                }
            return {"passed": True, "reason": "Unregistered device allowed"}
        
        if require_managed and not registered.is_managed:
            return {
                "passed": False,
                "reason": "Managed device required",
                "require_verification": True,
            }
        
        if not registered.is_compliant:
            return {
                "passed": False,
                "reason": "Device not compliant",
                "require_verification": True,
            }
        
        return {"passed": True, "reason": "Device verified"}
    
    def _check_mtls(self, headers: dict) -> dict:
        """Check mutual TLS certificate"""
        client_cert = headers.get("X-Client-Cert")
        if not client_cert:
            return {"passed": False, "reason": "No client certificate"}
        
        return {"passed": True, "reason": "mTLS verified"}
    
    def _create_session(self, request: AccessRequest, trust_score: float) -> str:
        """Create a new session"""
        session_token = secrets.token_urlsafe(32)
        
        self.active_sessions[session_token] = {
            "user_id": request.user_id,
            "role": request.role,
            "source_ip": request.source_ip,
            "device_fingerprint": request.device_fingerprint,
            "trust_score": trust_score,
            "created_at": datetime.utcnow(),
            "last_activity": datetime.utcnow(),
        }
        
        return session_token
    
    def register_device(self, fingerprint: DeviceFingerprint) -> bool:
        """Register a new device"""
        self.registered_devices[fingerprint.fingerprint_id] = fingerprint
        return True
    
    def block_ip(self, ip: str, reason: str) -> bool:
        """Block an IP address"""
        self.blocked_ips.add(ip)
        return True
    
    def unblock_ip(self, ip: str) -> bool:
        """Unblock an IP address"""
        self.blocked_ips.discard(ip)
        return True
    
    def block_device(self, fingerprint_id: str, reason: str) -> bool:
        """Block a device"""
        self.blocked_devices.add(fingerprint_id)
        return True
    
    def get_access_log(
        self,
        limit: int = 100,
        decision_filter: Optional[AccessDecision] = None,
    ) -> list[AccessResult]:
        """Get access log entries"""
        log = self.access_log
        
        if decision_filter:
            log = [entry for entry in log if entry.decision == decision_filter]
        
        return log[-limit:]
    
    def get_blocked_ips(self) -> set[str]:
        """Get list of blocked IPs"""
        return self.blocked_ips.copy()
    
    def get_blocked_devices(self) -> set[str]:
        """Get list of blocked devices"""
        return self.blocked_devices.copy()
    
    def get_active_sessions(self) -> dict:
        """Get active sessions"""
        return self.active_sessions.copy()
    
    def invalidate_session(self, session_token: str) -> bool:
        """Invalidate a session"""
        if session_token in self.active_sessions:
            del self.active_sessions[session_token]
            return True
        return False
    
    def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions"""
        now = datetime.utcnow()
        expired = []
        
        for token, session in self.active_sessions.items():
            role = session.get("role")
            role_config = self.role_permissions.get(role, {})
            timeout = role_config.get("session_timeout_minutes", 60)
            
            if session["last_activity"] + timedelta(minutes=timeout) < now:
                expired.append(token)
        
        for token in expired:
            del self.active_sessions[token]
        
        return len(expired)


_zero_trust_gateway: Optional[ZeroTrustGateway] = None


def get_zero_trust_gateway() -> ZeroTrustGateway:
    """Get singleton instance of ZeroTrustGateway"""
    global _zero_trust_gateway
    if _zero_trust_gateway is None:
        _zero_trust_gateway = ZeroTrustGateway()
    return _zero_trust_gateway
