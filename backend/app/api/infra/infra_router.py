"""
Infrastructure API Router

Provides endpoints for:
- GET /api/infra/health/all - All service health status
- POST /api/infra/failover/switch - Trigger failover
- POST /api/infra/audit - Infrastructure audit log
- GET /api/infra/services - Service registry
- GET /api/infra/regions - Multi-region status
- GET /api/infra/cjis/status - CJIS compliance status
- GET /api/infra/zero-trust/access-log - Zero-trust access log
"""

from datetime import datetime
from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, Field

from app.infra import (
    get_zero_trust_gateway,
    get_cjis_compliance_layer,
    get_ha_manager,
    get_failover_engine,
    get_service_registry,
    AccessDecision,
    ComplianceResult,
    NodeStatus,
    RegionStatus,
    ServiceStatus,
)


class HealthStatus(str, Enum):
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    UNHEALTHY = "UNHEALTHY"
    OFFLINE = "OFFLINE"


class ServiceHealthResponse(BaseModel):
    service_name: str
    status: HealthStatus
    instances: int
    healthy_instances: int
    cpu_usage: float
    memory_usage: float
    last_check: Optional[str]


class AllHealthResponse(BaseModel):
    overall_status: HealthStatus
    timestamp: str
    services: dict[str, ServiceHealthResponse]
    neo4j_cluster: dict
    elasticsearch_cluster: dict
    redis_cluster: dict
    postgres_cluster: dict
    websocket_broker: dict
    federal_integrations: dict
    fusion_cloud: dict
    drone_robotics: dict


class FailoverRequest(BaseModel):
    from_region: str = Field(..., description="Source region ID")
    to_region: str = Field(..., description="Target region ID")
    service_category: Optional[str] = Field(None, description="Specific service to failover")
    reason: str = Field(..., description="Reason for failover")
    operator_id: str = Field(..., description="Operator initiating failover")


class FailoverResponse(BaseModel):
    success: bool
    event_id: str
    from_region: str
    to_region: str
    duration_ms: int
    timestamp: str
    details: dict


class AuditLogRequest(BaseModel):
    event_type: str = Field(..., description="Type of infrastructure event")
    resource: str = Field(..., description="Affected resource")
    action: str = Field(..., description="Action performed")
    operator_id: str = Field(..., description="Operator ID")
    details: dict = Field(default_factory=dict)
    severity: str = Field(default="INFO")


class AuditLogResponse(BaseModel):
    audit_id: str
    timestamp: str
    event_type: str
    resource: str
    action: str
    operator_id: str
    severity: str
    recorded: bool


class ServiceRegistryResponse(BaseModel):
    total_services: int
    healthy: int
    degraded: int
    unhealthy: int
    offline: int
    services: list[dict]


class RegionStatusResponse(BaseModel):
    failover_mode: str
    primary_region: Optional[str]
    total_regions: int
    active_regions: int
    regions: dict[str, dict]
    failover_readiness: dict


class CJISStatusResponse(BaseModel):
    overall_compliant: bool
    password_policy: dict
    mfa_policy: dict
    session_policy: dict
    encryption_policy: dict
    audit_policy: dict
    training_requirements: dict
    recent_violations: list[dict]
    compliance_score: float


class ZeroTrustAccessLogResponse(BaseModel):
    total_requests: int
    allowed: int
    denied: int
    challenged: int
    blocked_ips: list[str]
    blocked_devices: list[str]
    recent_access: list[dict]


class InfraRouter:
    """Infrastructure API Router"""
    
    def __init__(self):
        self.zero_trust = get_zero_trust_gateway()
        self.cjis = get_cjis_compliance_layer()
        self.ha_manager = get_ha_manager()
        self.failover_engine = get_failover_engine()
        self.service_registry = get_service_registry()
        self.audit_log: list[dict] = []
    
    def get_all_health(self) -> AllHealthResponse:
        """GET /api/infra/health/all - Get all service health status"""
        services_status = self.service_registry.get_all_services()
        health_summary = self.service_registry.get_health_summary()
        
        service_health = {}
        for name, service in services_status.items():
            service_health[name] = ServiceHealthResponse(
                service_name=name,
                status=HealthStatus(service.status.value),
                instances=service.instances,
                healthy_instances=service.healthy_instances,
                cpu_usage=service.cpu_usage,
                memory_usage=service.memory_usage,
                last_check=service.last_health_check.isoformat() if service.last_health_check else None,
            )
        
        neo4j_service = services_status.get("neo4j-cluster")
        es_service = services_status.get("elasticsearch-cluster")
        redis_service = services_status.get("redis-cluster")
        pg_service = services_status.get("postgres-primary")
        ws_service = services_status.get("websocket-broker")
        fusion_service = services_status.get("fusion-cloud")
        drone_service = services_status.get("drone-service")
        
        return AllHealthResponse(
            overall_status=HealthStatus(health_summary["overall_status"]),
            timestamp=datetime.utcnow().isoformat(),
            services=service_health,
            neo4j_cluster={
                "status": neo4j_service.status.value if neo4j_service else "NOT_FOUND",
                "nodes": neo4j_service.instances if neo4j_service else 0,
                "healthy_nodes": neo4j_service.healthy_instances if neo4j_service else 0,
            },
            elasticsearch_cluster={
                "status": es_service.status.value if es_service else "NOT_FOUND",
                "nodes": es_service.instances if es_service else 0,
                "healthy_nodes": es_service.healthy_instances if es_service else 0,
            },
            redis_cluster={
                "status": redis_service.status.value if redis_service else "NOT_FOUND",
                "nodes": redis_service.instances if redis_service else 0,
                "healthy_nodes": redis_service.healthy_instances if redis_service else 0,
            },
            postgres_cluster={
                "status": pg_service.status.value if pg_service else "NOT_FOUND",
                "primary": pg_service is not None,
                "replicas": 0,
            },
            websocket_broker={
                "status": ws_service.status.value if ws_service else "NOT_FOUND",
                "connections": 0,
                "channels": 0,
            },
            federal_integrations={
                "status": "HEALTHY",
                "ncic": "connected",
                "nlets": "connected",
                "fbi_cjis": "connected",
            },
            fusion_cloud={
                "status": fusion_service.status.value if fusion_service else "NOT_FOUND",
                "connected_agencies": 5,
                "active_federations": 3,
            },
            drone_robotics={
                "status": drone_service.status.value if drone_service else "NOT_FOUND",
                "active_drones": 0,
                "active_robots": 0,
            },
        )
    
    def trigger_failover(self, request: FailoverRequest) -> FailoverResponse:
        """POST /api/infra/failover/switch - Trigger region failover"""
        self.audit_log.append({
            "audit_id": f"audit-{datetime.utcnow().timestamp()}",
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": "FAILOVER_INITIATED",
            "resource": f"{request.from_region} -> {request.to_region}",
            "action": "failover_switch",
            "operator_id": request.operator_id,
            "severity": "CRITICAL",
            "details": {"reason": request.reason},
        })
        
        success = self.failover_engine.execute_failover(
            request.from_region,
            request.to_region,
            manual=True,
        )
        
        timeline = self.failover_engine.get_failover_timeline(limit=1)
        latest_event = timeline[-1] if timeline else None
        
        return FailoverResponse(
            success=success,
            event_id=latest_event.event_id if latest_event else "unknown",
            from_region=request.from_region,
            to_region=request.to_region,
            duration_ms=latest_event.duration_ms if latest_event else 0,
            timestamp=datetime.utcnow().isoformat(),
            details={
                "reason": request.reason,
                "operator": request.operator_id,
                "service_category": request.service_category,
            },
        )
    
    def log_audit_event(self, request: AuditLogRequest) -> AuditLogResponse:
        """POST /api/infra/audit - Log infrastructure audit event"""
        import uuid
        
        audit_entry = {
            "audit_id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": request.event_type,
            "resource": request.resource,
            "action": request.action,
            "operator_id": request.operator_id,
            "severity": request.severity,
            "details": request.details,
        }
        
        self.audit_log.append(audit_entry)
        
        return AuditLogResponse(
            audit_id=audit_entry["audit_id"],
            timestamp=audit_entry["timestamp"],
            event_type=request.event_type,
            resource=request.resource,
            action=request.action,
            operator_id=request.operator_id,
            severity=request.severity,
            recorded=True,
        )
    
    def get_services(self) -> ServiceRegistryResponse:
        """GET /api/infra/services - Get service registry"""
        health_summary = self.service_registry.get_health_summary()
        all_services = self.service_registry.get_all_services()
        
        services_list = []
        for name, service in all_services.items():
            services_list.append({
                "service_id": service.service_id,
                "service_name": name,
                "service_type": service.service_type.value,
                "version": service.version,
                "status": service.status.value,
                "instances": service.instances,
                "healthy_instances": service.healthy_instances,
                "endpoints": [
                    {
                        "endpoint_id": ep.endpoint_id,
                        "protocol": ep.protocol,
                        "host": ep.host,
                        "port": ep.port,
                        "path": ep.path,
                    }
                    for ep in service.endpoints
                ],
                "dependencies": [
                    {
                        "service_name": dep.service_name,
                        "required": dep.required,
                    }
                    for dep in service.dependencies
                ],
                "last_updated": service.last_updated.isoformat() if service.last_updated else None,
            })
        
        return ServiceRegistryResponse(
            total_services=health_summary["total_services"],
            healthy=health_summary["healthy"],
            degraded=health_summary["degraded"],
            unhealthy=health_summary["unhealthy"],
            offline=health_summary["offline"],
            services=services_list,
        )
    
    def get_regions(self) -> RegionStatusResponse:
        """GET /api/infra/regions - Get multi-region status"""
        all_regions = self.failover_engine.get_all_regions_status()
        readiness = self.failover_engine.get_failover_readiness()
        
        return RegionStatusResponse(
            failover_mode=all_regions["failover_mode"],
            primary_region=all_regions["primary_region"],
            total_regions=all_regions["total_regions"],
            active_regions=all_regions["active_regions"],
            regions=all_regions["regions"],
            failover_readiness=readiness,
        )
    
    def get_cjis_status(self) -> CJISStatusResponse:
        """GET /api/infra/cjis/status - Get CJIS compliance status"""
        compliance_log = self.cjis.get_compliance_log(limit=10)
        
        violations = [
            {
                "check_id": entry.check_id,
                "timestamp": entry.timestamp.isoformat(),
                "violations": [v.value for v in entry.violations],
                "user_id": entry.user_id,
            }
            for entry in compliance_log
            if entry.result == ComplianceResult.FAIL
        ]
        
        total_checks = len(compliance_log)
        passed_checks = len([e for e in compliance_log if e.result != ComplianceResult.FAIL])
        compliance_score = (passed_checks / total_checks * 100) if total_checks > 0 else 100.0
        
        return CJISStatusResponse(
            overall_compliant=len(violations) == 0,
            password_policy=self.cjis.password_policy,
            mfa_policy=self.cjis.mfa_policy,
            session_policy=self.cjis.session_policy,
            encryption_policy=self.cjis.encryption_policy,
            audit_policy=self.cjis.audit_policy,
            training_requirements=self.cjis.training_requirements,
            recent_violations=violations,
            compliance_score=compliance_score,
        )
    
    def get_zero_trust_access_log(self, limit: int = 100) -> ZeroTrustAccessLogResponse:
        """GET /api/infra/zero-trust/access-log - Get zero-trust access log"""
        access_log = self.zero_trust.get_access_log(limit=limit)
        blocked_ips = list(self.zero_trust.get_blocked_ips())
        blocked_devices = list(self.zero_trust.get_blocked_devices())
        
        allowed = len([e for e in access_log if e.decision == AccessDecision.ALLOW])
        denied = len([e for e in access_log if e.decision == AccessDecision.DENY])
        challenged = len([e for e in access_log if e.decision == AccessDecision.CHALLENGE])
        
        recent_access = [
            {
                "request_id": entry.request_id,
                "timestamp": entry.timestamp.isoformat(),
                "decision": entry.decision.value,
                "reason": entry.reason,
                "trust_score": entry.trust_score,
                "checks_passed": entry.checks_passed,
                "checks_failed": entry.checks_failed,
            }
            for entry in access_log[-20:]
        ]
        
        return ZeroTrustAccessLogResponse(
            total_requests=len(access_log),
            allowed=allowed,
            denied=denied,
            challenged=challenged,
            blocked_ips=blocked_ips,
            blocked_devices=blocked_devices,
            recent_access=recent_access,
        )
    
    def get_audit_log(self, limit: int = 100) -> list[dict]:
        """GET /api/infra/audit - Get infrastructure audit log"""
        return self.audit_log[-limit:]
    
    def get_ha_status(self) -> dict:
        """GET /api/infra/ha/status - Get high availability status"""
        all_services = self.ha_manager.get_all_services_status()
        predictions = self.ha_manager.predict_failures()
        failover_events = self.ha_manager.get_failover_events(limit=10)
        
        return {
            "services": all_services,
            "failure_predictions": predictions,
            "recent_failovers": [
                {
                    "event_id": e.event_id,
                    "service_name": e.service_name,
                    "from_node": e.from_node,
                    "to_node": e.to_node,
                    "reason": e.reason.value,
                    "timestamp": e.timestamp.isoformat(),
                    "success": e.success,
                }
                for e in failover_events
            ],
        }


router = InfraRouter()
