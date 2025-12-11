"""
Service Registry Module

Implements service discovery and registry for the G3TI RTCC-UIP platform.
Tracks:
- Backend microservices
- WebSocket services
- Predictive engines
- Drone/robotics services
- Threat intel services
- Digital twin engine
- Fusion cloud services

Provides:
- Health status
- Version information
- Endpoint lists
- Dependencies
- Last-updated timestamps
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional
import uuid


class ServiceStatus(Enum):
    """Service status types"""
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    UNHEALTHY = "UNHEALTHY"
    OFFLINE = "OFFLINE"
    STARTING = "STARTING"
    STOPPING = "STOPPING"
    MAINTENANCE = "MAINTENANCE"


class ServiceType(Enum):
    """Service type categories"""
    BACKEND_API = "BACKEND_API"
    WEBSOCKET = "WEBSOCKET"
    PREDICTIVE_ENGINE = "PREDICTIVE_ENGINE"
    DRONE_SERVICE = "DRONE_SERVICE"
    ROBOTICS_SERVICE = "ROBOTICS_SERVICE"
    THREAT_INTEL = "THREAT_INTEL"
    DIGITAL_TWIN = "DIGITAL_TWIN"
    FUSION_CLOUD = "FUSION_CLOUD"
    DATABASE = "DATABASE"
    CACHE = "CACHE"
    MESSAGE_QUEUE = "MESSAGE_QUEUE"
    ETL_PIPELINE = "ETL_PIPELINE"
    AI_ENGINE = "AI_ENGINE"
    ANALYTICS = "ANALYTICS"
    AUTHENTICATION = "AUTHENTICATION"
    GATEWAY = "GATEWAY"


@dataclass
class ServiceEndpoint:
    """Service endpoint configuration"""
    endpoint_id: str
    protocol: str
    host: str
    port: int
    path: str
    health_check_path: str
    is_public: bool = False
    requires_auth: bool = True
    tls_enabled: bool = True


@dataclass
class ServiceDependency:
    """Service dependency definition"""
    service_name: str
    required: bool
    min_version: Optional[str] = None
    health_impact: str = "degraded"


@dataclass
class ServiceInfo:
    """Complete service information"""
    service_id: str
    service_name: str
    service_type: ServiceType
    version: str
    status: ServiceStatus
    description: str
    endpoints: list[ServiceEndpoint]
    dependencies: list[ServiceDependency]
    instances: int = 1
    healthy_instances: int = 1
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    request_rate: float = 0.0
    error_rate: float = 0.0
    avg_latency_ms: float = 0.0
    registered_at: Optional[datetime] = None
    last_updated: Optional[datetime] = None
    last_health_check: Optional[datetime] = None
    metadata: dict = field(default_factory=dict)
    tags: list = field(default_factory=list)


@dataclass
class ServiceHealthCheck:
    """Service health check result"""
    check_id: str
    service_id: str
    timestamp: datetime
    status: ServiceStatus
    response_time_ms: int
    checks_passed: list
    checks_failed: list
    details: dict = field(default_factory=dict)


class ServiceRegistry:
    """
    Service Registry for G3TI RTCC-UIP
    
    Central registry for all platform services including:
    - Service discovery
    - Health monitoring
    - Version tracking
    - Dependency management
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
        
        self.services: dict[str, ServiceInfo] = {}
        self.health_history: dict[str, list[ServiceHealthCheck]] = {}
        self.service_events: list[dict] = []
        
        self._init_riviera_beach_services()
    
    def _init_riviera_beach_services(self):
        """Initialize Riviera Beach RTCC services"""
        self._register_core_services()
        self._register_ai_services()
        self._register_operational_services()
        self._register_infrastructure_services()
    
    def _register_core_services(self):
        """Register core platform services"""
        core_services = [
            ServiceInfo(
                service_id="api-gateway-001",
                service_name="api-gateway",
                service_type=ServiceType.GATEWAY,
                version="2.5.0",
                status=ServiceStatus.HEALTHY,
                description="Main API Gateway for RTCC-UIP",
                endpoints=[
                    ServiceEndpoint(
                        endpoint_id="api-main",
                        protocol="https",
                        host="api.rtcc.rivierabeach.gov",
                        port=443,
                        path="/api/v1",
                        health_check_path="/health",
                        is_public=True,
                    ),
                ],
                dependencies=[
                    ServiceDependency(service_name="auth-service", required=True),
                    ServiceDependency(service_name="redis-cluster", required=True),
                ],
                instances=3,
                healthy_instances=3,
                tags=["core", "gateway", "public"],
            ),
            ServiceInfo(
                service_id="auth-service-001",
                service_name="auth-service",
                service_type=ServiceType.AUTHENTICATION,
                version="1.8.0",
                status=ServiceStatus.HEALTHY,
                description="Authentication and Authorization Service",
                endpoints=[
                    ServiceEndpoint(
                        endpoint_id="auth-main",
                        protocol="https",
                        host="auth.rtcc.rivierabeach.gov",
                        port=443,
                        path="/auth",
                        health_check_path="/health",
                    ),
                ],
                dependencies=[
                    ServiceDependency(service_name="postgres-primary", required=True),
                    ServiceDependency(service_name="redis-cluster", required=True),
                ],
                instances=2,
                healthy_instances=2,
                tags=["core", "security", "cjis"],
            ),
            ServiceInfo(
                service_id="websocket-broker-001",
                service_name="websocket-broker",
                service_type=ServiceType.WEBSOCKET,
                version="1.5.0",
                status=ServiceStatus.HEALTHY,
                description="WebSocket Message Broker",
                endpoints=[
                    ServiceEndpoint(
                        endpoint_id="ws-main",
                        protocol="wss",
                        host="ws.rtcc.rivierabeach.gov",
                        port=443,
                        path="/ws",
                        health_check_path="/health",
                    ),
                ],
                dependencies=[
                    ServiceDependency(service_name="redis-cluster", required=True),
                ],
                instances=2,
                healthy_instances=2,
                tags=["core", "realtime"],
            ),
        ]
        
        for service in core_services:
            service.registered_at = datetime.utcnow()
            service.last_updated = datetime.utcnow()
            self.services[service.service_name] = service
    
    def _register_ai_services(self):
        """Register AI and predictive services"""
        ai_services = [
            ServiceInfo(
                service_id="ai-engine-001",
                service_name="ai-engine",
                service_type=ServiceType.AI_ENGINE,
                version="3.2.0",
                status=ServiceStatus.HEALTHY,
                description="Core AI Intelligence Engine",
                endpoints=[
                    ServiceEndpoint(
                        endpoint_id="ai-main",
                        protocol="https",
                        host="ai.rtcc.rivierabeach.gov",
                        port=443,
                        path="/ai",
                        health_check_path="/health",
                    ),
                ],
                dependencies=[
                    ServiceDependency(service_name="postgres-primary", required=True),
                    ServiceDependency(service_name="elasticsearch-cluster", required=True),
                    ServiceDependency(service_name="neo4j-cluster", required=True),
                ],
                instances=2,
                healthy_instances=2,
                tags=["ai", "predictive", "gpu"],
            ),
            ServiceInfo(
                service_id="predictive-engine-001",
                service_name="predictive-engine",
                service_type=ServiceType.PREDICTIVE_ENGINE,
                version="2.1.0",
                status=ServiceStatus.HEALTHY,
                description="Predictive Policing 3.0 Engine",
                endpoints=[
                    ServiceEndpoint(
                        endpoint_id="predict-main",
                        protocol="https",
                        host="predict.rtcc.rivierabeach.gov",
                        port=443,
                        path="/predict",
                        health_check_path="/health",
                    ),
                ],
                dependencies=[
                    ServiceDependency(service_name="ai-engine", required=True),
                    ServiceDependency(service_name="data-lake", required=True),
                ],
                instances=2,
                healthy_instances=2,
                tags=["ai", "predictive", "gpu", "ethics-monitored"],
            ),
            ServiceInfo(
                service_id="threat-intel-001",
                service_name="threat-intel",
                service_type=ServiceType.THREAT_INTEL,
                version="1.7.0",
                status=ServiceStatus.HEALTHY,
                description="Global Threat Intelligence Engine",
                endpoints=[
                    ServiceEndpoint(
                        endpoint_id="threat-main",
                        protocol="https",
                        host="threat.rtcc.rivierabeach.gov",
                        port=443,
                        path="/threat",
                        health_check_path="/health",
                    ),
                ],
                dependencies=[
                    ServiceDependency(service_name="ai-engine", required=True),
                    ServiceDependency(service_name="fusion-cloud", required=False),
                ],
                instances=1,
                healthy_instances=1,
                tags=["intel", "federal", "classified"],
            ),
            ServiceInfo(
                service_id="digital-twin-001",
                service_name="digital-twin",
                service_type=ServiceType.DIGITAL_TWIN,
                version="1.3.0",
                status=ServiceStatus.HEALTHY,
                description="City Digital Twin Engine",
                endpoints=[
                    ServiceEndpoint(
                        endpoint_id="twin-main",
                        protocol="https",
                        host="twin.rtcc.rivierabeach.gov",
                        port=443,
                        path="/twin",
                        health_check_path="/health",
                    ),
                ],
                dependencies=[
                    ServiceDependency(service_name="sensor-grid", required=True),
                    ServiceDependency(service_name="ai-engine", required=True),
                ],
                instances=1,
                healthy_instances=1,
                tags=["simulation", "3d", "gpu"],
            ),
        ]
        
        for service in ai_services:
            service.registered_at = datetime.utcnow()
            service.last_updated = datetime.utcnow()
            self.services[service.service_name] = service
    
    def _register_operational_services(self):
        """Register operational services"""
        ops_services = [
            ServiceInfo(
                service_id="drone-service-001",
                service_name="drone-service",
                service_type=ServiceType.DRONE_SERVICE,
                version="1.4.0",
                status=ServiceStatus.HEALTHY,
                description="Autonomous Drone Task Force Engine",
                endpoints=[
                    ServiceEndpoint(
                        endpoint_id="drone-main",
                        protocol="https",
                        host="drone.rtcc.rivierabeach.gov",
                        port=443,
                        path="/drone",
                        health_check_path="/health",
                    ),
                ],
                dependencies=[
                    ServiceDependency(service_name="websocket-broker", required=True),
                    ServiceDependency(service_name="ai-engine", required=True),
                ],
                instances=1,
                healthy_instances=1,
                tags=["autonomous", "aerial", "realtime"],
            ),
            ServiceInfo(
                service_id="robotics-service-001",
                service_name="robotics-service",
                service_type=ServiceType.ROBOTICS_SERVICE,
                version="1.2.0",
                status=ServiceStatus.HEALTHY,
                description="Autonomous Tactical Robotics Engine",
                endpoints=[
                    ServiceEndpoint(
                        endpoint_id="robotics-main",
                        protocol="https",
                        host="robotics.rtcc.rivierabeach.gov",
                        port=443,
                        path="/robotics",
                        health_check_path="/health",
                    ),
                ],
                dependencies=[
                    ServiceDependency(service_name="websocket-broker", required=True),
                    ServiceDependency(service_name="ai-engine", required=True),
                ],
                instances=1,
                healthy_instances=1,
                tags=["autonomous", "ground", "realtime"],
            ),
            ServiceInfo(
                service_id="fusion-cloud-001",
                service_name="fusion-cloud",
                service_type=ServiceType.FUSION_CLOUD,
                version="1.6.0",
                status=ServiceStatus.HEALTHY,
                description="Multi-City/Multi-Agency Fusion Cloud",
                endpoints=[
                    ServiceEndpoint(
                        endpoint_id="fusion-main",
                        protocol="https",
                        host="fusion.rtcc.rivierabeach.gov",
                        port=443,
                        path="/fusion",
                        health_check_path="/health",
                    ),
                ],
                dependencies=[
                    ServiceDependency(service_name="auth-service", required=True),
                    ServiceDependency(service_name="postgres-primary", required=True),
                ],
                instances=2,
                healthy_instances=2,
                tags=["federation", "multi-agency", "cjis"],
            ),
            ServiceInfo(
                service_id="dispatch-service-001",
                service_name="dispatch-service",
                service_type=ServiceType.BACKEND_API,
                version="2.3.0",
                status=ServiceStatus.HEALTHY,
                description="CAD/Dispatch Integration Service",
                endpoints=[
                    ServiceEndpoint(
                        endpoint_id="dispatch-main",
                        protocol="https",
                        host="dispatch.rtcc.rivierabeach.gov",
                        port=443,
                        path="/dispatch",
                        health_check_path="/health",
                    ),
                ],
                dependencies=[
                    ServiceDependency(service_name="postgres-primary", required=True),
                    ServiceDependency(service_name="websocket-broker", required=True),
                ],
                instances=2,
                healthy_instances=2,
                tags=["dispatch", "cad", "realtime"],
            ),
        ]
        
        for service in ops_services:
            service.registered_at = datetime.utcnow()
            service.last_updated = datetime.utcnow()
            self.services[service.service_name] = service
    
    def _register_infrastructure_services(self):
        """Register infrastructure services"""
        infra_services = [
            ServiceInfo(
                service_id="postgres-primary-001",
                service_name="postgres-primary",
                service_type=ServiceType.DATABASE,
                version="15.4",
                status=ServiceStatus.HEALTHY,
                description="PostgreSQL Primary Database",
                endpoints=[
                    ServiceEndpoint(
                        endpoint_id="pg-main",
                        protocol="postgresql",
                        host="pg-primary.rtcc.rivierabeach.gov",
                        port=5432,
                        path="/rtcc",
                        health_check_path="/health",
                        is_public=False,
                    ),
                ],
                dependencies=[],
                instances=1,
                healthy_instances=1,
                tags=["database", "primary", "cjis"],
            ),
            ServiceInfo(
                service_id="redis-cluster-001",
                service_name="redis-cluster",
                service_type=ServiceType.CACHE,
                version="7.2",
                status=ServiceStatus.HEALTHY,
                description="Redis Cache Cluster",
                endpoints=[
                    ServiceEndpoint(
                        endpoint_id="redis-main",
                        protocol="redis",
                        host="redis.rtcc.rivierabeach.gov",
                        port=6379,
                        path="/",
                        health_check_path="/health",
                        is_public=False,
                    ),
                ],
                dependencies=[],
                instances=3,
                healthy_instances=3,
                tags=["cache", "cluster", "session"],
            ),
            ServiceInfo(
                service_id="elasticsearch-cluster-001",
                service_name="elasticsearch-cluster",
                service_type=ServiceType.DATABASE,
                version="8.11",
                status=ServiceStatus.HEALTHY,
                description="Elasticsearch Search Cluster",
                endpoints=[
                    ServiceEndpoint(
                        endpoint_id="es-main",
                        protocol="https",
                        host="es.rtcc.rivierabeach.gov",
                        port=9200,
                        path="/",
                        health_check_path="/_cluster/health",
                        is_public=False,
                    ),
                ],
                dependencies=[],
                instances=3,
                healthy_instances=3,
                tags=["search", "cluster", "analytics"],
            ),
            ServiceInfo(
                service_id="neo4j-cluster-001",
                service_name="neo4j-cluster",
                service_type=ServiceType.DATABASE,
                version="5.15",
                status=ServiceStatus.HEALTHY,
                description="Neo4j Graph Database Cluster",
                endpoints=[
                    ServiceEndpoint(
                        endpoint_id="neo4j-main",
                        protocol="bolt",
                        host="neo4j.rtcc.rivierabeach.gov",
                        port=7687,
                        path="/",
                        health_check_path="/health",
                        is_public=False,
                    ),
                ],
                dependencies=[],
                instances=3,
                healthy_instances=3,
                tags=["graph", "cluster", "relationships"],
            ),
        ]
        
        for service in infra_services:
            service.registered_at = datetime.utcnow()
            service.last_updated = datetime.utcnow()
            self.services[service.service_name] = service
    
    def register_service(self, service: ServiceInfo) -> bool:
        """Register a new service"""
        if service.service_name in self.services:
            return False
        
        service.registered_at = datetime.utcnow()
        service.last_updated = datetime.utcnow()
        self.services[service.service_name] = service
        
        self.service_events.append({
            "event_type": "service_registered",
            "service_name": service.service_name,
            "timestamp": datetime.utcnow().isoformat(),
        })
        
        return True
    
    def deregister_service(self, service_name: str) -> bool:
        """Deregister a service"""
        if service_name not in self.services:
            return False
        
        del self.services[service_name]
        
        self.service_events.append({
            "event_type": "service_deregistered",
            "service_name": service_name,
            "timestamp": datetime.utcnow().isoformat(),
        })
        
        return True
    
    def update_service_status(
        self,
        service_name: str,
        status: ServiceStatus,
        details: Optional[dict] = None,
    ) -> bool:
        """Update service status"""
        service = self.services.get(service_name)
        if not service:
            return False
        
        old_status = service.status
        service.status = status
        service.last_updated = datetime.utcnow()
        
        if details:
            service.metadata.update(details)
        
        self.service_events.append({
            "event_type": "status_changed",
            "service_name": service_name,
            "old_status": old_status.value,
            "new_status": status.value,
            "timestamp": datetime.utcnow().isoformat(),
        })
        
        return True
    
    def record_health_check(self, health_check: ServiceHealthCheck) -> bool:
        """Record a health check result"""
        service = self.services.get(health_check.service_id)
        if not service:
            service_by_name = next(
                (s for s in self.services.values() if s.service_id == health_check.service_id),
                None
            )
            if not service_by_name:
                return False
            service = service_by_name
        
        if service.service_name not in self.health_history:
            self.health_history[service.service_name] = []
        
        self.health_history[service.service_name].append(health_check)
        
        if len(self.health_history[service.service_name]) > 1000:
            self.health_history[service.service_name] = \
                self.health_history[service.service_name][-500:]
        
        service.status = health_check.status
        service.last_health_check = health_check.timestamp
        service.last_updated = datetime.utcnow()
        
        return True
    
    def get_service(self, service_name: str) -> Optional[ServiceInfo]:
        """Get service information"""
        return self.services.get(service_name)
    
    def get_all_services(self) -> dict[str, ServiceInfo]:
        """Get all registered services"""
        return self.services.copy()
    
    def get_services_by_type(self, service_type: ServiceType) -> list[ServiceInfo]:
        """Get services by type"""
        return [s for s in self.services.values() if s.service_type == service_type]
    
    def get_services_by_status(self, status: ServiceStatus) -> list[ServiceInfo]:
        """Get services by status"""
        return [s for s in self.services.values() if s.status == status]
    
    def get_service_dependencies(self, service_name: str) -> list[dict]:
        """Get service dependencies with their status"""
        service = self.services.get(service_name)
        if not service:
            return []
        
        deps = []
        for dep in service.dependencies:
            dep_service = self.services.get(dep.service_name)
            deps.append({
                "service_name": dep.service_name,
                "required": dep.required,
                "min_version": dep.min_version,
                "health_impact": dep.health_impact,
                "status": dep_service.status.value if dep_service else "NOT_FOUND",
                "version": dep_service.version if dep_service else None,
            })
        
        return deps
    
    def get_dependent_services(self, service_name: str) -> list[str]:
        """Get services that depend on this service"""
        dependents = []
        for name, service in self.services.items():
            for dep in service.dependencies:
                if dep.service_name == service_name:
                    dependents.append(name)
                    break
        return dependents
    
    def get_health_summary(self) -> dict:
        """Get overall health summary"""
        total = len(self.services)
        healthy = len([s for s in self.services.values() if s.status == ServiceStatus.HEALTHY])
        degraded = len([s for s in self.services.values() if s.status == ServiceStatus.DEGRADED])
        unhealthy = len([s for s in self.services.values() if s.status == ServiceStatus.UNHEALTHY])
        offline = len([s for s in self.services.values() if s.status == ServiceStatus.OFFLINE])
        
        if healthy == total:
            overall_status = "HEALTHY"
        elif healthy > total * 0.8:
            overall_status = "MOSTLY_HEALTHY"
        elif healthy > total * 0.5:
            overall_status = "DEGRADED"
        else:
            overall_status = "CRITICAL"
        
        return {
            "overall_status": overall_status,
            "total_services": total,
            "healthy": healthy,
            "degraded": degraded,
            "unhealthy": unhealthy,
            "offline": offline,
            "health_percentage": (healthy / total * 100) if total > 0 else 0,
            "timestamp": datetime.utcnow().isoformat(),
        }
    
    def get_service_events(
        self,
        limit: int = 100,
        service_name: Optional[str] = None,
    ) -> list[dict]:
        """Get service events"""
        events = self.service_events
        
        if service_name:
            events = [e for e in events if e.get("service_name") == service_name]
        
        return events[-limit:]


_service_registry: Optional[ServiceRegistry] = None


def get_service_registry() -> ServiceRegistry:
    """Get singleton instance of ServiceRegistry"""
    global _service_registry
    if _service_registry is None:
        _service_registry = ServiceRegistry()
    return _service_registry
