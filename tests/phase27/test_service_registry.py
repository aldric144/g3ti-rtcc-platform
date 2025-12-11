"""
Test Suite 9: Service Registry Tests

Tests for service registry functionality including:
- Service registration
- Service discovery
- Health monitoring
- Dependency management
- Version tracking
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch


class TestServiceRegistration:
    """Test service registration functionality"""
    
    def test_register_new_service(self):
        """Test registering a new service"""
        from app.infra.service_registry import (
            ServiceRegistry,
            ServiceInfo,
            ServiceType,
            ServiceStatus,
            ServiceEndpoint,
        )
        
        registry = ServiceRegistry()
        
        service = ServiceInfo(
            service_id="svc-test-001",
            service_name="test-service",
            service_type=ServiceType.CORE,
            version="1.0.0",
            status=ServiceStatus.HEALTHY,
            endpoints=[
                ServiceEndpoint(
                    endpoint_id="ep-1",
                    protocol="http",
                    host="10.0.1.1",
                    port=8080,
                    path="/api",
                )
            ],
        )
        
        result = registry.register_service(service)
        assert result is True
    
    def test_deregister_service(self):
        """Test deregistering a service"""
        from app.infra.service_registry import ServiceRegistry
        
        registry = ServiceRegistry()
        
        result = registry.deregister_service("nonexistent-service")
        assert result is False
    
    def test_update_service_status(self):
        """Test updating service status"""
        from app.infra.service_registry import (
            ServiceRegistry,
            ServiceStatus,
        )
        
        registry = ServiceRegistry()
        
        result = registry.update_service_status(
            "api-gateway",
            ServiceStatus.DEGRADED,
            {"reason": "High latency"},
        )
        assert isinstance(result, bool)


class TestServiceDiscovery:
    """Test service discovery functionality"""
    
    def test_get_service_by_name(self):
        """Test getting service by name"""
        from app.infra.service_registry import ServiceRegistry
        
        registry = ServiceRegistry()
        
        service = registry.get_service("api-gateway")
        assert service is not None
        assert service.service_name == "api-gateway"
    
    def test_get_all_services(self):
        """Test getting all services"""
        from app.infra.service_registry import ServiceRegistry
        
        registry = ServiceRegistry()
        
        services = registry.get_all_services()
        assert isinstance(services, dict)
        assert len(services) > 0
    
    def test_get_services_by_type(self):
        """Test getting services by type"""
        from app.infra.service_registry import (
            ServiceRegistry,
            ServiceType,
        )
        
        registry = ServiceRegistry()
        
        core_services = registry.get_services_by_type(ServiceType.CORE)
        assert isinstance(core_services, list)
    
    def test_get_services_by_status(self):
        """Test getting services by status"""
        from app.infra.service_registry import (
            ServiceRegistry,
            ServiceStatus,
        )
        
        registry = ServiceRegistry()
        
        healthy_services = registry.get_services_by_status(ServiceStatus.HEALTHY)
        assert isinstance(healthy_services, list)


class TestHealthMonitoring:
    """Test service health monitoring"""
    
    def test_record_health_check(self):
        """Test recording health check result"""
        from app.infra.service_registry import (
            ServiceRegistry,
            ServiceHealthCheck,
        )
        
        registry = ServiceRegistry()
        
        health_check = ServiceHealthCheck(
            check_id="hc-001",
            service_name="api-gateway",
            timestamp=datetime.utcnow(),
            healthy=True,
            response_time_ms=15.0,
            details={"status": "ok"},
        )
        
        result = registry.record_health_check(health_check)
        assert result is True
    
    def test_get_health_summary(self):
        """Test getting health summary"""
        from app.infra.service_registry import ServiceRegistry
        
        registry = ServiceRegistry()
        
        summary = registry.get_health_summary()
        assert "total_services" in summary
        assert "healthy" in summary
        assert "degraded" in summary
        assert "unhealthy" in summary
        assert "offline" in summary
    
    def test_overall_status_calculation(self):
        """Test overall status calculation"""
        from app.infra.service_registry import ServiceRegistry
        
        registry = ServiceRegistry()
        
        summary = registry.get_health_summary()
        assert "overall_status" in summary


class TestDependencyManagement:
    """Test service dependency management"""
    
    def test_get_service_dependencies(self):
        """Test getting service dependencies"""
        from app.infra.service_registry import ServiceRegistry
        
        registry = ServiceRegistry()
        
        deps = registry.get_service_dependencies("api-gateway")
        assert isinstance(deps, list)
    
    def test_get_dependent_services(self):
        """Test getting dependent services"""
        from app.infra.service_registry import ServiceRegistry
        
        registry = ServiceRegistry()
        
        dependents = registry.get_dependent_services("postgres-primary")
        assert isinstance(dependents, list)
    
    def test_dependency_required_flag(self):
        """Test dependency required flag"""
        from app.infra.service_registry import ServiceRegistry
        
        registry = ServiceRegistry()
        
        deps = registry.get_service_dependencies("api-gateway")
        
        for dep in deps:
            assert "required" in dep
            assert isinstance(dep["required"], bool)


class TestVersionTracking:
    """Test service version tracking"""
    
    def test_service_version_stored(self):
        """Test that service version is stored"""
        from app.infra.service_registry import ServiceRegistry
        
        registry = ServiceRegistry()
        
        service = registry.get_service("api-gateway")
        assert service is not None
        assert hasattr(service, "version")
    
    def test_service_events_tracking(self):
        """Test service events tracking"""
        from app.infra.service_registry import ServiceRegistry
        
        registry = ServiceRegistry()
        
        events = registry.get_service_events(limit=10)
        assert isinstance(events, list)
    
    def test_service_events_filtering(self):
        """Test service events filtering by service"""
        from app.infra.service_registry import ServiceRegistry
        
        registry = ServiceRegistry()
        
        events = registry.get_service_events(limit=10, service_name="api-gateway")
        assert isinstance(events, list)


class TestPreInitializedServices:
    """Test pre-initialized services"""
    
    def test_core_services_initialized(self):
        """Test core services are initialized"""
        from app.infra.service_registry import ServiceRegistry
        
        registry = ServiceRegistry()
        
        core_services = ["api-gateway", "auth-service", "websocket-broker"]
        
        for service_name in core_services:
            service = registry.get_service(service_name)
            assert service is not None
    
    def test_ai_services_initialized(self):
        """Test AI services are initialized"""
        from app.infra.service_registry import ServiceRegistry
        
        registry = ServiceRegistry()
        
        ai_services = ["ai-engine", "predictive-engine", "threat-intel", "digital-twin"]
        
        for service_name in ai_services:
            service = registry.get_service(service_name)
            assert service is not None
    
    def test_infrastructure_services_initialized(self):
        """Test infrastructure services are initialized"""
        from app.infra.service_registry import ServiceRegistry
        
        registry = ServiceRegistry()
        
        infra_services = ["postgres-primary", "redis-cluster", "elasticsearch-cluster", "neo4j-cluster"]
        
        for service_name in infra_services:
            service = registry.get_service(service_name)
            assert service is not None
