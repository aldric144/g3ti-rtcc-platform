"""
Test Suite 11: Infrastructure API Endpoint Tests

Tests for infrastructure API endpoints including:
- Health endpoints
- Failover endpoints
- Audit endpoints
- Service registry endpoints
- Region status endpoints
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch


class TestHealthEndpoints:
    """Test health API endpoints"""
    
    def test_get_all_health(self):
        """Test GET /api/infra/health/all endpoint"""
        from app.api.infra.infra_router import InfraRouter
        
        router = InfraRouter()
        
        response = router.get_all_health()
        
        assert response is not None
        assert hasattr(response, "overall_status")
        assert hasattr(response, "services")
        assert hasattr(response, "timestamp")
    
    def test_health_response_structure(self):
        """Test health response structure"""
        from app.api.infra.infra_router import InfraRouter
        
        router = InfraRouter()
        
        response = router.get_all_health()
        
        assert hasattr(response, "neo4j_cluster")
        assert hasattr(response, "elasticsearch_cluster")
        assert hasattr(response, "redis_cluster")
        assert hasattr(response, "postgres_cluster")
    
    def test_health_includes_federal_integrations(self):
        """Test health includes federal integrations"""
        from app.api.infra.infra_router import InfraRouter
        
        router = InfraRouter()
        
        response = router.get_all_health()
        
        assert hasattr(response, "federal_integrations")


class TestFailoverEndpoints:
    """Test failover API endpoints"""
    
    def test_trigger_failover(self):
        """Test POST /api/infra/failover/switch endpoint"""
        from app.api.infra.infra_router import (
            InfraRouter,
            FailoverRequest,
        )
        
        router = InfraRouter()
        
        request = FailoverRequest(
            from_region="us-gov-east-1",
            to_region="us-gov-west-1",
            reason="Test failover",
            operator_id="test-operator",
        )
        
        response = router.trigger_failover(request)
        
        assert response is not None
        assert hasattr(response, "success")
        assert hasattr(response, "event_id")
        assert hasattr(response, "duration_ms")
    
    def test_failover_response_structure(self):
        """Test failover response structure"""
        from app.api.infra.infra_router import (
            InfraRouter,
            FailoverRequest,
        )
        
        router = InfraRouter()
        
        request = FailoverRequest(
            from_region="us-gov-east-1",
            to_region="us-gov-west-1",
            reason="Test failover",
            operator_id="test-operator",
        )
        
        response = router.trigger_failover(request)
        
        assert hasattr(response, "from_region")
        assert hasattr(response, "to_region")
        assert hasattr(response, "timestamp")


class TestAuditEndpoints:
    """Test audit API endpoints"""
    
    def test_log_audit_event(self):
        """Test POST /api/infra/audit endpoint"""
        from app.api.infra.infra_router import (
            InfraRouter,
            AuditLogRequest,
        )
        
        router = InfraRouter()
        
        request = AuditLogRequest(
            event_type="CONFIG_CHANGE",
            resource="api-gateway",
            action="update",
            operator_id="admin-001",
            details={"setting": "timeout", "old_value": 30, "new_value": 60},
            severity="INFO",
        )
        
        response = router.log_audit_event(request)
        
        assert response is not None
        assert hasattr(response, "audit_id")
        assert hasattr(response, "recorded")
        assert response.recorded is True
    
    def test_get_audit_log(self):
        """Test GET /api/infra/audit endpoint"""
        from app.api.infra.infra_router import InfraRouter
        
        router = InfraRouter()
        
        log = router.get_audit_log(limit=10)
        
        assert isinstance(log, list)


class TestServiceRegistryEndpoints:
    """Test service registry API endpoints"""
    
    def test_get_services(self):
        """Test GET /api/infra/services endpoint"""
        from app.api.infra.infra_router import InfraRouter
        
        router = InfraRouter()
        
        response = router.get_services()
        
        assert response is not None
        assert hasattr(response, "total_services")
        assert hasattr(response, "healthy")
        assert hasattr(response, "services")
    
    def test_services_response_structure(self):
        """Test services response structure"""
        from app.api.infra.infra_router import InfraRouter
        
        router = InfraRouter()
        
        response = router.get_services()
        
        assert hasattr(response, "degraded")
        assert hasattr(response, "unhealthy")
        assert hasattr(response, "offline")
    
    def test_services_list_not_empty(self):
        """Test services list is not empty"""
        from app.api.infra.infra_router import InfraRouter
        
        router = InfraRouter()
        
        response = router.get_services()
        
        assert len(response.services) > 0


class TestRegionStatusEndpoints:
    """Test region status API endpoints"""
    
    def test_get_regions(self):
        """Test GET /api/infra/regions endpoint"""
        from app.api.infra.infra_router import InfraRouter
        
        router = InfraRouter()
        
        response = router.get_regions()
        
        assert response is not None
        assert hasattr(response, "failover_mode")
        assert hasattr(response, "total_regions")
        assert hasattr(response, "regions")
    
    def test_regions_response_structure(self):
        """Test regions response structure"""
        from app.api.infra.infra_router import InfraRouter
        
        router = InfraRouter()
        
        response = router.get_regions()
        
        assert hasattr(response, "primary_region")
        assert hasattr(response, "active_regions")
        assert hasattr(response, "failover_readiness")


class TestCJISStatusEndpoints:
    """Test CJIS status API endpoints"""
    
    def test_get_cjis_status(self):
        """Test GET /api/infra/cjis/status endpoint"""
        from app.api.infra.infra_router import InfraRouter
        
        router = InfraRouter()
        
        response = router.get_cjis_status()
        
        assert response is not None
        assert hasattr(response, "overall_compliant")
        assert hasattr(response, "compliance_score")
    
    def test_cjis_policies_included(self):
        """Test CJIS policies are included"""
        from app.api.infra.infra_router import InfraRouter
        
        router = InfraRouter()
        
        response = router.get_cjis_status()
        
        assert hasattr(response, "password_policy")
        assert hasattr(response, "mfa_policy")
        assert hasattr(response, "session_policy")
        assert hasattr(response, "encryption_policy")


class TestZeroTrustEndpoints:
    """Test zero-trust API endpoints"""
    
    def test_get_access_log(self):
        """Test GET /api/infra/zero-trust/access-log endpoint"""
        from app.api.infra.infra_router import InfraRouter
        
        router = InfraRouter()
        
        response = router.get_zero_trust_access_log(limit=100)
        
        assert response is not None
        assert hasattr(response, "total_requests")
        assert hasattr(response, "allowed")
        assert hasattr(response, "denied")
    
    def test_access_log_response_structure(self):
        """Test access log response structure"""
        from app.api.infra.infra_router import InfraRouter
        
        router = InfraRouter()
        
        response = router.get_zero_trust_access_log(limit=100)
        
        assert hasattr(response, "challenged")
        assert hasattr(response, "blocked_ips")
        assert hasattr(response, "blocked_devices")
        assert hasattr(response, "recent_access")


class TestHAStatusEndpoints:
    """Test HA status API endpoints"""
    
    def test_get_ha_status(self):
        """Test GET /api/infra/ha/status endpoint"""
        from app.api.infra.infra_router import InfraRouter
        
        router = InfraRouter()
        
        response = router.get_ha_status()
        
        assert response is not None
        assert "services" in response
        assert "failure_predictions" in response
        assert "recent_failovers" in response
