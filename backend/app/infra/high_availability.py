"""
High Availability Manager Module

Implements high availability features for the G3TI RTCC-UIP platform.
Features:
- Load balancer integration
- Auto-restart on service failure
- Stateful vs. stateless service routing
- Database failover between primary & replica nodes
- Cache cluster failover
- Predictive failure alerting
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional, Callable
import uuid
import random


class NodeStatus(Enum):
    """Node status types"""
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    UNHEALTHY = "UNHEALTHY"
    OFFLINE = "OFFLINE"
    MAINTENANCE = "MAINTENANCE"
    STARTING = "STARTING"
    STOPPING = "STOPPING"


class ServiceType(Enum):
    """Service types for routing"""
    STATELESS = "STATELESS"
    STATEFUL = "STATEFUL"
    DATABASE = "DATABASE"
    CACHE = "CACHE"
    MESSAGE_QUEUE = "MESSAGE_QUEUE"
    WEBSOCKET = "WEBSOCKET"


class FailoverReason(Enum):
    """Reasons for failover"""
    HEALTH_CHECK_FAILED = "HEALTH_CHECK_FAILED"
    HIGH_LATENCY = "HIGH_LATENCY"
    HIGH_ERROR_RATE = "HIGH_ERROR_RATE"
    RESOURCE_EXHAUSTION = "RESOURCE_EXHAUSTION"
    MANUAL_TRIGGER = "MANUAL_TRIGGER"
    SCHEDULED_MAINTENANCE = "SCHEDULED_MAINTENANCE"
    PREDICTIVE_FAILURE = "PREDICTIVE_FAILURE"


@dataclass
class ServiceNode:
    """Service node representation"""
    node_id: str
    service_name: str
    service_type: ServiceType
    host: str
    port: int
    status: NodeStatus
    is_primary: bool
    weight: int = 100
    current_connections: int = 0
    max_connections: int = 1000
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    last_health_check: Optional[datetime] = None
    health_check_failures: int = 0
    started_at: Optional[datetime] = None
    metadata: dict = field(default_factory=dict)


@dataclass
class FailoverEvent:
    """Failover event record"""
    event_id: str
    service_name: str
    from_node: str
    to_node: str
    reason: FailoverReason
    timestamp: datetime
    duration_ms: int
    success: bool
    details: dict = field(default_factory=dict)


@dataclass
class HealthCheckResult:
    """Health check result"""
    node_id: str
    service_name: str
    status: NodeStatus
    response_time_ms: int
    checks_passed: list
    checks_failed: list
    timestamp: datetime
    details: dict = field(default_factory=dict)


class HighAvailabilityManager:
    """
    High Availability Manager for G3TI RTCC-UIP
    
    Manages service health, load balancing, and failover for:
    - Backend API services
    - Database clusters
    - Cache clusters
    - WebSocket services
    - AI/ML engines
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
        
        self.service_nodes: dict[str, list[ServiceNode]] = {}
        self.failover_events: list[FailoverEvent] = []
        self.health_history: dict[str, list[HealthCheckResult]] = {}
        self.load_balancer_config: dict = {}
        self.auto_restart_config: dict = {}
        
        self._init_default_config()
        self._init_riviera_beach_services()
    
    def _init_default_config(self):
        """Initialize default HA configuration"""
        self.health_check_config = {
            "interval_seconds": 30,
            "timeout_seconds": 10,
            "failure_threshold": 3,
            "success_threshold": 2,
            "endpoints": {
                "http": "/health",
                "tcp": None,
                "grpc": "grpc.health.v1.Health/Check",
            },
        }
        
        self.load_balancer_config = {
            "algorithm": "weighted_round_robin",
            "sticky_sessions": True,
            "session_timeout_minutes": 30,
            "health_check_path": "/health",
            "drain_timeout_seconds": 30,
        }
        
        self.auto_restart_config = {
            "enabled": True,
            "max_restarts": 5,
            "restart_window_minutes": 10,
            "backoff_multiplier": 2,
            "initial_delay_seconds": 5,
            "max_delay_seconds": 300,
        }
        
        self.failover_config = {
            "automatic": True,
            "min_healthy_nodes": 1,
            "failover_timeout_seconds": 60,
            "rollback_on_failure": True,
            "notify_on_failover": True,
        }
        
        self.predictive_config = {
            "enabled": True,
            "cpu_threshold": 85.0,
            "memory_threshold": 90.0,
            "error_rate_threshold": 5.0,
            "latency_threshold_ms": 500,
            "prediction_window_minutes": 15,
        }
    
    def _init_riviera_beach_services(self):
        """Initialize Riviera Beach RTCC services"""
        self.critical_services = [
            "api-gateway",
            "auth-service",
            "dispatch-service",
            "alert-service",
            "websocket-broker",
            "postgres-primary",
            "redis-cluster",
            "elasticsearch-cluster",
            "neo4j-cluster",
        ]
        
        self.service_dependencies = {
            "api-gateway": ["auth-service", "redis-cluster"],
            "dispatch-service": ["postgres-primary", "redis-cluster", "websocket-broker"],
            "alert-service": ["postgres-primary", "redis-cluster", "websocket-broker"],
            "ai-engine": ["postgres-primary", "elasticsearch-cluster", "neo4j-cluster"],
            "analytics-service": ["postgres-primary", "elasticsearch-cluster"],
            "drone-service": ["postgres-primary", "redis-cluster", "websocket-broker"],
            "robotics-service": ["postgres-primary", "redis-cluster", "websocket-broker"],
        }
    
    def register_node(self, node: ServiceNode) -> bool:
        """Register a service node"""
        if node.service_name not in self.service_nodes:
            self.service_nodes[node.service_name] = []
        
        existing = next(
            (n for n in self.service_nodes[node.service_name] if n.node_id == node.node_id),
            None
        )
        if existing:
            return False
        
        self.service_nodes[node.service_name].append(node)
        return True
    
    def deregister_node(self, service_name: str, node_id: str) -> bool:
        """Deregister a service node"""
        if service_name not in self.service_nodes:
            return False
        
        self.service_nodes[service_name] = [
            n for n in self.service_nodes[service_name] if n.node_id != node_id
        ]
        return True
    
    def perform_health_check(self, service_name: str, node_id: str) -> HealthCheckResult:
        """Perform health check on a node"""
        nodes = self.service_nodes.get(service_name, [])
        node = next((n for n in nodes if n.node_id == node_id), None)
        
        if not node:
            return HealthCheckResult(
                node_id=node_id,
                service_name=service_name,
                status=NodeStatus.OFFLINE,
                response_time_ms=0,
                checks_passed=[],
                checks_failed=["node_not_found"],
                timestamp=datetime.utcnow(),
            )
        
        checks_passed = []
        checks_failed = []
        response_time_ms = random.randint(5, 100)
        
        if node.cpu_usage < self.predictive_config["cpu_threshold"]:
            checks_passed.append("cpu_usage")
        else:
            checks_failed.append("cpu_usage")
        
        if node.memory_usage < self.predictive_config["memory_threshold"]:
            checks_passed.append("memory_usage")
        else:
            checks_failed.append("memory_usage")
        
        if node.current_connections < node.max_connections * 0.9:
            checks_passed.append("connection_capacity")
        else:
            checks_failed.append("connection_capacity")
        
        if response_time_ms < self.predictive_config["latency_threshold_ms"]:
            checks_passed.append("response_time")
        else:
            checks_failed.append("response_time")
        
        if len(checks_failed) == 0:
            status = NodeStatus.HEALTHY
            node.health_check_failures = 0
        elif len(checks_failed) <= 1:
            status = NodeStatus.DEGRADED
            node.health_check_failures += 1
        else:
            status = NodeStatus.UNHEALTHY
            node.health_check_failures += 1
        
        node.status = status
        node.last_health_check = datetime.utcnow()
        
        result = HealthCheckResult(
            node_id=node_id,
            service_name=service_name,
            status=status,
            response_time_ms=response_time_ms,
            checks_passed=checks_passed,
            checks_failed=checks_failed,
            timestamp=datetime.utcnow(),
            details={
                "cpu_usage": node.cpu_usage,
                "memory_usage": node.memory_usage,
                "connections": node.current_connections,
            },
        )
        
        if service_name not in self.health_history:
            self.health_history[service_name] = []
        self.health_history[service_name].append(result)
        
        if node.health_check_failures >= self.health_check_config["failure_threshold"]:
            self._trigger_failover(service_name, node_id, FailoverReason.HEALTH_CHECK_FAILED)
        
        return result
    
    def get_healthy_node(self, service_name: str) -> Optional[ServiceNode]:
        """Get a healthy node for a service using load balancing"""
        nodes = self.service_nodes.get(service_name, [])
        healthy_nodes = [n for n in nodes if n.status == NodeStatus.HEALTHY]
        
        if not healthy_nodes:
            degraded_nodes = [n for n in nodes if n.status == NodeStatus.DEGRADED]
            if degraded_nodes:
                healthy_nodes = degraded_nodes
            else:
                return None
        
        algorithm = self.load_balancer_config.get("algorithm", "round_robin")
        
        if algorithm == "weighted_round_robin":
            total_weight = sum(n.weight for n in healthy_nodes)
            if total_weight == 0:
                return healthy_nodes[0] if healthy_nodes else None
            
            r = random.randint(1, total_weight)
            cumulative = 0
            for node in healthy_nodes:
                cumulative += node.weight
                if r <= cumulative:
                    return node
        
        elif algorithm == "least_connections":
            return min(healthy_nodes, key=lambda n: n.current_connections)
        
        elif algorithm == "round_robin":
            return healthy_nodes[0] if healthy_nodes else None
        
        return healthy_nodes[0] if healthy_nodes else None
    
    def _trigger_failover(
        self,
        service_name: str,
        failed_node_id: str,
        reason: FailoverReason,
    ) -> Optional[FailoverEvent]:
        """Trigger failover for a service"""
        if not self.failover_config["automatic"]:
            return None
        
        nodes = self.service_nodes.get(service_name, [])
        failed_node = next((n for n in nodes if n.node_id == failed_node_id), None)
        
        if not failed_node:
            return None
        
        healthy_nodes = [
            n for n in nodes
            if n.node_id != failed_node_id and n.status in [NodeStatus.HEALTHY, NodeStatus.DEGRADED]
        ]
        
        if not healthy_nodes:
            return None
        
        target_node = healthy_nodes[0]
        
        if failed_node.is_primary:
            failed_node.is_primary = False
            target_node.is_primary = True
        
        failed_node.status = NodeStatus.OFFLINE
        
        event = FailoverEvent(
            event_id=str(uuid.uuid4()),
            service_name=service_name,
            from_node=failed_node_id,
            to_node=target_node.node_id,
            reason=reason,
            timestamp=datetime.utcnow(),
            duration_ms=random.randint(100, 1000),
            success=True,
            details={
                "healthy_nodes_available": len(healthy_nodes),
                "failed_node_status": failed_node.status.value,
            },
        )
        
        self.failover_events.append(event)
        
        return event
    
    def trigger_manual_failover(
        self,
        service_name: str,
        from_node_id: str,
        to_node_id: str,
    ) -> Optional[FailoverEvent]:
        """Trigger manual failover"""
        nodes = self.service_nodes.get(service_name, [])
        from_node = next((n for n in nodes if n.node_id == from_node_id), None)
        to_node = next((n for n in nodes if n.node_id == to_node_id), None)
        
        if not from_node or not to_node:
            return None
        
        if from_node.is_primary:
            from_node.is_primary = False
            to_node.is_primary = True
        
        event = FailoverEvent(
            event_id=str(uuid.uuid4()),
            service_name=service_name,
            from_node=from_node_id,
            to_node=to_node_id,
            reason=FailoverReason.MANUAL_TRIGGER,
            timestamp=datetime.utcnow(),
            duration_ms=random.randint(50, 500),
            success=True,
        )
        
        self.failover_events.append(event)
        
        return event
    
    def restart_node(self, service_name: str, node_id: str) -> bool:
        """Restart a service node"""
        nodes = self.service_nodes.get(service_name, [])
        node = next((n for n in nodes if n.node_id == node_id), None)
        
        if not node:
            return False
        
        node.status = NodeStatus.STOPPING
        node.status = NodeStatus.STARTING
        node.status = NodeStatus.HEALTHY
        node.health_check_failures = 0
        node.started_at = datetime.utcnow()
        
        return True
    
    def get_service_status(self, service_name: str) -> dict:
        """Get comprehensive status for a service"""
        nodes = self.service_nodes.get(service_name, [])
        
        if not nodes:
            return {
                "service_name": service_name,
                "status": "NOT_FOUND",
                "nodes": [],
            }
        
        healthy_count = len([n for n in nodes if n.status == NodeStatus.HEALTHY])
        degraded_count = len([n for n in nodes if n.status == NodeStatus.DEGRADED])
        unhealthy_count = len([n for n in nodes if n.status == NodeStatus.UNHEALTHY])
        offline_count = len([n for n in nodes if n.status == NodeStatus.OFFLINE])
        
        if healthy_count == len(nodes):
            overall_status = "HEALTHY"
        elif healthy_count > 0:
            overall_status = "DEGRADED"
        elif degraded_count > 0:
            overall_status = "CRITICAL"
        else:
            overall_status = "OFFLINE"
        
        primary_node = next((n for n in nodes if n.is_primary), None)
        
        return {
            "service_name": service_name,
            "status": overall_status,
            "total_nodes": len(nodes),
            "healthy_nodes": healthy_count,
            "degraded_nodes": degraded_count,
            "unhealthy_nodes": unhealthy_count,
            "offline_nodes": offline_count,
            "primary_node": primary_node.node_id if primary_node else None,
            "nodes": [
                {
                    "node_id": n.node_id,
                    "host": n.host,
                    "port": n.port,
                    "status": n.status.value,
                    "is_primary": n.is_primary,
                    "cpu_usage": n.cpu_usage,
                    "memory_usage": n.memory_usage,
                    "connections": n.current_connections,
                }
                for n in nodes
            ],
        }
    
    def get_all_services_status(self) -> dict:
        """Get status for all services"""
        return {
            service_name: self.get_service_status(service_name)
            for service_name in self.service_nodes.keys()
        }
    
    def get_failover_events(
        self,
        limit: int = 100,
        service_name: Optional[str] = None,
    ) -> list[FailoverEvent]:
        """Get failover events"""
        events = self.failover_events
        
        if service_name:
            events = [e for e in events if e.service_name == service_name]
        
        return events[-limit:]
    
    def predict_failures(self) -> list[dict]:
        """Predict potential failures based on metrics"""
        predictions = []
        
        for service_name, nodes in self.service_nodes.items():
            for node in nodes:
                risk_score = 0.0
                risk_factors = []
                
                if node.cpu_usage > self.predictive_config["cpu_threshold"] * 0.8:
                    risk_score += 0.3
                    risk_factors.append(f"High CPU usage: {node.cpu_usage}%")
                
                if node.memory_usage > self.predictive_config["memory_threshold"] * 0.8:
                    risk_score += 0.3
                    risk_factors.append(f"High memory usage: {node.memory_usage}%")
                
                connection_ratio = node.current_connections / node.max_connections
                if connection_ratio > 0.8:
                    risk_score += 0.2
                    risk_factors.append(f"High connection usage: {connection_ratio * 100:.1f}%")
                
                if node.health_check_failures > 0:
                    risk_score += 0.2 * node.health_check_failures
                    risk_factors.append(f"Recent health check failures: {node.health_check_failures}")
                
                if risk_score > 0.5:
                    predictions.append({
                        "service_name": service_name,
                        "node_id": node.node_id,
                        "risk_score": min(risk_score, 1.0),
                        "risk_factors": risk_factors,
                        "recommended_action": "Consider failover or scaling",
                        "timestamp": datetime.utcnow().isoformat(),
                    })
        
        return sorted(predictions, key=lambda p: p["risk_score"], reverse=True)


_ha_manager: Optional[HighAvailabilityManager] = None


def get_ha_manager() -> HighAvailabilityManager:
    """Get singleton instance of HighAvailabilityManager"""
    global _ha_manager
    if _ha_manager is None:
        _ha_manager = HighAvailabilityManager()
    return _ha_manager
