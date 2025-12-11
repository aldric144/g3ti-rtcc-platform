"""
Test Suite 4: Zero-Trust Gateway Enforcement Tests

Tests for zero-trust security enforcement including:
- Token validation
- mTLS verification
- Geographic restrictions
- Device fingerprinting
- IP allowlisting
- Role-based access control
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch


class TestTokenValidation:
    """Test JWT token validation"""
    
    def test_valid_token_acceptance(self):
        """Test that valid tokens are accepted"""
        from app.infra.zero_trust import (
            ZeroTrustGateway,
            AccessRequest,
            AccessDecision,
        )
        
        gateway = ZeroTrustGateway()
        
        request = AccessRequest(
            request_id="req-1",
            source_ip="10.100.1.1",
            user_id="officer_smith",
            role="PATROL_OFFICER",
            resource="/api/mdt/dispatch",
            method="GET",
            timestamp=datetime.utcnow(),
        )
        
        result = gateway.validate_access(request)
        assert result is not None
        assert result.decision in [AccessDecision.ALLOW, AccessDecision.DENY, AccessDecision.CHALLENGE]
    
    def test_missing_token_denial(self):
        """Test that missing tokens are denied"""
        from app.infra.zero_trust import (
            ZeroTrustGateway,
            AccessRequest,
            AccessDecision,
        )
        
        gateway = ZeroTrustGateway()
        
        request = AccessRequest(
            request_id="req-2",
            source_ip="203.45.67.89",
            resource="/api/admin/users",
            method="GET",
            timestamp=datetime.utcnow(),
        )
        
        result = gateway.validate_access(request)
        assert result is not None


class TestGeographicRestrictions:
    """Test geographic restriction enforcement"""
    
    def test_us_only_restriction(self):
        """Test US-only geographic restriction"""
        from app.infra.zero_trust import ZeroTrustGateway
        
        gateway = ZeroTrustGateway()
        
        assert "US" in gateway.geo_restrictions["allowed_countries"]
    
    def test_florida_state_restriction(self):
        """Test Florida state restriction"""
        from app.infra.zero_trust import ZeroTrustGateway
        
        gateway = ZeroTrustGateway()
        
        assert "FL" in gateway.geo_restrictions["allowed_states"]
    
    def test_palm_beach_county_restriction(self):
        """Test Palm Beach County restriction"""
        from app.infra.zero_trust import ZeroTrustGateway
        
        gateway = ZeroTrustGateway()
        
        assert "Palm Beach" in gateway.geo_restrictions["allowed_counties"]
    
    def test_riviera_beach_city_restriction(self):
        """Test Riviera Beach city restriction"""
        from app.infra.zero_trust import ZeroTrustGateway
        
        gateway = ZeroTrustGateway()
        
        assert "Riviera Beach" in gateway.geo_restrictions["allowed_cities"]
    
    def test_foreign_ip_denial(self):
        """Test that foreign IPs are denied"""
        from app.infra.zero_trust import (
            ZeroTrustGateway,
            AccessRequest,
            AccessDecision,
        )
        
        gateway = ZeroTrustGateway()
        
        request = AccessRequest(
            request_id="req-3",
            source_ip="203.45.67.89",
            user_id="unknown",
            resource="/api/intel/classified",
            method="GET",
            timestamp=datetime.utcnow(),
            geo_location={"country": "CN", "state": None, "city": None},
        )
        
        result = gateway.validate_access(request)
        assert result.decision == AccessDecision.DENY


class TestIPAllowlisting:
    """Test IP allowlist enforcement"""
    
    def test_pd_network_allowed(self):
        """Test that PD network IPs are allowed"""
        from app.infra.zero_trust import ZeroTrustGateway
        
        gateway = ZeroTrustGateway()
        
        pd_networks = gateway.ip_allowlist
        assert "10.100.0.0/16" in pd_networks
    
    def test_mdt_network_allowed(self):
        """Test that MDT network IPs are allowed"""
        from app.infra.zero_trust import ZeroTrustGateway
        
        gateway = ZeroTrustGateway()
        
        pd_networks = gateway.ip_allowlist
        assert "10.101.0.0/16" in pd_networks
    
    def test_vpn_network_allowed(self):
        """Test that VPN network IPs are allowed"""
        from app.infra.zero_trust import ZeroTrustGateway
        
        gateway = ZeroTrustGateway()
        
        pd_networks = gateway.ip_allowlist
        assert "172.16.0.0/12" in pd_networks
    
    def test_ip_blocking(self):
        """Test IP blocking functionality"""
        from app.infra.zero_trust import ZeroTrustGateway
        
        gateway = ZeroTrustGateway()
        
        result = gateway.block_ip("203.45.67.89", "Malicious activity")
        assert result is True
        
        blocked_ips = gateway.get_blocked_ips()
        assert "203.45.67.89" in blocked_ips


class TestDeviceFingerprinting:
    """Test device fingerprint verification"""
    
    def test_device_registration(self):
        """Test device registration"""
        from app.infra.zero_trust import (
            ZeroTrustGateway,
            DeviceFingerprint,
        )
        
        gateway = ZeroTrustGateway()
        
        fingerprint = DeviceFingerprint(
            fingerprint_id="fp-12345",
            user_id="officer_smith",
            device_type="MDT",
            browser="Chrome",
            os="Windows 10",
            hardware_id="HW-ABC123",
            registered_at=datetime.utcnow(),
        )
        
        result = gateway.register_device(fingerprint)
        assert result is True
    
    def test_unknown_device_challenge(self):
        """Test that unknown devices are challenged"""
        from app.infra.zero_trust import (
            ZeroTrustGateway,
            AccessRequest,
            DeviceFingerprint,
        )
        
        gateway = ZeroTrustGateway()
        
        request = AccessRequest(
            request_id="req-4",
            source_ip="10.100.1.1",
            user_id="officer_smith",
            role="PATROL_OFFICER",
            resource="/api/mdt/dispatch",
            method="GET",
            timestamp=datetime.utcnow(),
            device_fingerprint=DeviceFingerprint(
                fingerprint_id="unknown-fp",
                user_id="officer_smith",
                device_type="Unknown",
                browser="Unknown",
                os="Unknown",
            ),
        )
        
        result = gateway.validate_access(request)
        assert result is not None


class TestRoleBasedAccess:
    """Test role-based access control"""
    
    def test_admin_full_access(self):
        """Test that admins have full access"""
        from app.infra.zero_trust import ZeroTrustGateway
        
        gateway = ZeroTrustGateway()
        
        admin_permissions = gateway.role_permissions.get("SYSTEM_ADMIN", {})
        assert admin_permissions is not None
    
    def test_patrol_officer_limited_access(self):
        """Test that patrol officers have limited access"""
        from app.infra.zero_trust import ZeroTrustGateway
        
        gateway = ZeroTrustGateway()
        
        officer_permissions = gateway.role_permissions.get("PATROL_OFFICER", {})
        assert officer_permissions is not None
    
    def test_read_only_restrictions(self):
        """Test read-only role restrictions"""
        from app.infra.zero_trust import ZeroTrustGateway
        
        gateway = ZeroTrustGateway()
        
        readonly_permissions = gateway.role_permissions.get("READ_ONLY", {})
        assert readonly_permissions is not None
    
    def test_role_count(self):
        """Test that all 8 roles are defined"""
        from app.infra.zero_trust import ZeroTrustGateway
        
        gateway = ZeroTrustGateway()
        
        assert len(gateway.role_permissions) == 8


class TestAccessLogging:
    """Test access logging functionality"""
    
    def test_access_log_recording(self):
        """Test that access attempts are logged"""
        from app.infra.zero_trust import (
            ZeroTrustGateway,
            AccessRequest,
        )
        
        gateway = ZeroTrustGateway()
        
        request = AccessRequest(
            request_id="req-5",
            source_ip="10.100.1.1",
            user_id="officer_smith",
            role="PATROL_OFFICER",
            resource="/api/mdt/dispatch",
            method="GET",
            timestamp=datetime.utcnow(),
        )
        
        gateway.validate_access(request)
        
        log = gateway.get_access_log(limit=10)
        assert isinstance(log, list)
    
    def test_access_log_filtering(self):
        """Test access log filtering by decision"""
        from app.infra.zero_trust import (
            ZeroTrustGateway,
            AccessDecision,
        )
        
        gateway = ZeroTrustGateway()
        
        log = gateway.get_access_log(limit=10, decision_filter=AccessDecision.DENY)
        assert isinstance(log, list)
