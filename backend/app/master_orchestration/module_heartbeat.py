"""
Module Heartbeat Checker - Monitors health status of all RTCC modules.
Phase 37: Master UI Integration & System Orchestration Shell
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional
import uuid
import asyncio


class ModuleStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    OFFLINE = "offline"
    UNKNOWN = "unknown"


@dataclass
class ModuleHealth:
    module_id: str
    module_name: str
    status: ModuleStatus = ModuleStatus.UNKNOWN
    last_heartbeat: Optional[datetime] = None
    response_time_ms: float = 0.0
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    error_count: int = 0
    warning_count: int = 0
    uptime_seconds: float = 0.0
    version: str = "1.0.0"
    dependencies: List[str] = field(default_factory=list)
    endpoints_healthy: int = 0
    endpoints_total: int = 0
    websocket_connections: int = 0
    last_error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "module_id": self.module_id,
            "module_name": self.module_name,
            "status": self.status.value,
            "last_heartbeat": self.last_heartbeat.isoformat() if self.last_heartbeat else None,
            "response_time_ms": self.response_time_ms,
            "cpu_usage": self.cpu_usage,
            "memory_usage": self.memory_usage,
            "error_count": self.error_count,
            "warning_count": self.warning_count,
            "uptime_seconds": self.uptime_seconds,
            "version": self.version,
            "dependencies": self.dependencies,
            "endpoints_healthy": self.endpoints_healthy,
            "endpoints_total": self.endpoints_total,
            "websocket_connections": self.websocket_connections,
            "last_error": self.last_error,
            "metadata": self.metadata,
        }


@dataclass
class HeartbeatResult:
    result_id: str = field(default_factory=lambda: f"hb-{uuid.uuid4().hex[:12]}")
    timestamp: datetime = field(default_factory=datetime.utcnow)
    modules_checked: int = 0
    modules_healthy: int = 0
    modules_degraded: int = 0
    modules_unhealthy: int = 0
    modules_offline: int = 0
    overall_status: ModuleStatus = ModuleStatus.UNKNOWN
    duration_ms: float = 0.0
    details: Dict[str, ModuleHealth] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "result_id": self.result_id,
            "timestamp": self.timestamp.isoformat(),
            "modules_checked": self.modules_checked,
            "modules_healthy": self.modules_healthy,
            "modules_degraded": self.modules_degraded,
            "modules_unhealthy": self.modules_unhealthy,
            "modules_offline": self.modules_offline,
            "overall_status": self.overall_status.value,
            "duration_ms": self.duration_ms,
            "details": {k: v.to_dict() for k, v in self.details.items()},
        }


class ModuleHeartbeatChecker:
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

        self._modules: Dict[str, ModuleHealth] = {}
        self._heartbeat_history: List[HeartbeatResult] = []
        self._max_history = 1000
        self._heartbeat_interval = 30
        self._unhealthy_threshold = 90
        self._degraded_threshold = 60
        self._statistics = {
            "heartbeats_performed": 0,
            "modules_registered": 0,
        }
        self._initialize_modules()

    def _initialize_modules(self):
        modules = [
            ("real_time_ops", "Real-Time Operations", ["communications", "cad"]),
            ("investigations", "Investigations", ["data_lake", "intel_orchestration"]),
            ("tactical_analytics", "Tactical Analytics", ["data_lake", "predictive_intel"]),
            ("officer_safety", "Officer Safety", ["communications", "real_time_ops"]),
            ("communications", "Communications & Dispatch", []),
            ("robotics", "Robotics", ["tactical_analytics"]),
            ("drone_ops", "Drone Operations", ["tactical_analytics", "digital_twin"]),
            ("digital_twin", "Digital Twin", ["data_lake", "sensor_grid"]),
            ("predictive_intel", "Predictive Intelligence", ["data_lake", "tactical_analytics"]),
            ("human_stability", "Human Stability Intel", ["investigations", "ethics_guardian"]),
            ("moral_compass", "Moral Compass HQ", ["ethics_guardian", "constitution_engine"]),
            ("global_awareness", "Global Awareness", ["threat_intel", "fusion_cloud"]),
            ("ai_city_brain", "AI City Brain", ["digital_twin", "governance_engine"]),
            ("governance_engine", "Governance Engine", ["constitution_engine", "ethics_guardian"]),
            ("fusion_cloud", "Fusion Cloud", ["data_lake", "intel_orchestration"]),
            ("autonomous_ops", "Autonomous Ops", ["ai_city_brain", "robotics", "drone_ops"]),
            ("city_autonomy", "City Autonomy (Level 2)", ["ai_city_brain", "governance_engine"]),
            ("public_guardian", "Public Safety Guardian", ["ethics_guardian", "data_lake"]),
            ("officer_assist", "Officer Assist Suite", ["officer_safety", "constitution_engine"]),
            ("cyber_intel", "Cyber Intelligence", ["threat_intel", "global_awareness"]),
            ("emergency_mgmt", "Emergency Management", ["communications", "real_time_ops"]),
            ("sentinel_supervisor", "AI Sentinel Supervisor", ["ethics_guardian", "moral_compass"]),
            ("ai_personas", "AI Personas", ["intel_orchestration", "communications"]),
            ("ethics_guardian", "Ethics Guardian", []),
            ("constitution_engine", "Constitution Engine", ["ethics_guardian"]),
            ("data_lake", "Data Lake", []),
            ("intel_orchestration", "Intel Orchestration", ["data_lake"]),
            ("ops_continuity", "Ops Continuity", []),
            ("enterprise_infra", "Enterprise Infrastructure", ["ops_continuity"]),
            ("threat_intel", "Threat Intelligence", ["data_lake"]),
            ("national_security", "National Security Engine", ["threat_intel", "global_awareness"]),
            ("detective_ai", "Detective AI", ["investigations", "intel_orchestration"]),
            ("sensor_grid", "Sensor Grid", ["data_lake"]),
        ]

        for module_id, module_name, dependencies in modules:
            self._modules[module_id] = ModuleHealth(
                module_id=module_id,
                module_name=module_name,
                status=ModuleStatus.HEALTHY,
                last_heartbeat=datetime.utcnow(),
                response_time_ms=25.0 + (hash(module_id) % 50),
                cpu_usage=10.0 + (hash(module_id) % 30),
                memory_usage=20.0 + (hash(module_id) % 40),
                uptime_seconds=86400.0 + (hash(module_id) % 86400),
                dependencies=dependencies,
                endpoints_healthy=5,
                endpoints_total=5,
                websocket_connections=hash(module_id) % 10,
            )
            self._statistics["modules_registered"] += 1

    def register_module(
        self,
        module_id: str,
        module_name: str,
        dependencies: Optional[List[str]] = None,
        version: str = "1.0.0",
    ) -> ModuleHealth:
        module = ModuleHealth(
            module_id=module_id,
            module_name=module_name,
            status=ModuleStatus.UNKNOWN,
            dependencies=dependencies or [],
            version=version,
        )
        self._modules[module_id] = module
        self._statistics["modules_registered"] += 1
        return module

    def unregister_module(self, module_id: str) -> bool:
        if module_id in self._modules:
            del self._modules[module_id]
            return True
        return False

    def update_heartbeat(
        self,
        module_id: str,
        response_time_ms: float = 0.0,
        cpu_usage: float = 0.0,
        memory_usage: float = 0.0,
        error_count: int = 0,
        warning_count: int = 0,
        endpoints_healthy: int = 0,
        endpoints_total: int = 0,
        websocket_connections: int = 0,
        last_error: Optional[str] = None,
    ) -> Optional[ModuleHealth]:
        module = self._modules.get(module_id)
        if not module:
            return None

        module.last_heartbeat = datetime.utcnow()
        module.response_time_ms = response_time_ms
        module.cpu_usage = cpu_usage
        module.memory_usage = memory_usage
        module.error_count = error_count
        module.warning_count = warning_count
        module.endpoints_healthy = endpoints_healthy
        module.endpoints_total = endpoints_total
        module.websocket_connections = websocket_connections
        module.last_error = last_error

        module.status = self._calculate_status(module)
        return module

    def _calculate_status(self, module: ModuleHealth) -> ModuleStatus:
        if module.last_heartbeat is None:
            return ModuleStatus.UNKNOWN

        time_since_heartbeat = (datetime.utcnow() - module.last_heartbeat).total_seconds()

        if time_since_heartbeat > self._unhealthy_threshold:
            return ModuleStatus.OFFLINE

        if module.error_count > 10:
            return ModuleStatus.UNHEALTHY

        if module.response_time_ms > 1000:
            return ModuleStatus.UNHEALTHY

        if time_since_heartbeat > self._degraded_threshold:
            return ModuleStatus.DEGRADED

        if module.error_count > 5 or module.warning_count > 20:
            return ModuleStatus.DEGRADED

        if module.cpu_usage > 90 or module.memory_usage > 90:
            return ModuleStatus.DEGRADED

        if module.endpoints_total > 0 and module.endpoints_healthy < module.endpoints_total:
            return ModuleStatus.DEGRADED

        return ModuleStatus.HEALTHY

    async def perform_heartbeat_check(self) -> HeartbeatResult:
        start_time = datetime.utcnow()
        result = HeartbeatResult()

        for module_id, module in self._modules.items():
            module.status = self._calculate_status(module)
            result.details[module_id] = module
            result.modules_checked += 1

            if module.status == ModuleStatus.HEALTHY:
                result.modules_healthy += 1
            elif module.status == ModuleStatus.DEGRADED:
                result.modules_degraded += 1
            elif module.status == ModuleStatus.UNHEALTHY:
                result.modules_unhealthy += 1
            elif module.status == ModuleStatus.OFFLINE:
                result.modules_offline += 1

        if result.modules_unhealthy > 0 or result.modules_offline > 0:
            result.overall_status = ModuleStatus.UNHEALTHY
        elif result.modules_degraded > 0:
            result.overall_status = ModuleStatus.DEGRADED
        else:
            result.overall_status = ModuleStatus.HEALTHY

        result.duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
        self._heartbeat_history.append(result)
        self._statistics["heartbeats_performed"] += 1

        if len(self._heartbeat_history) > self._max_history:
            self._heartbeat_history = self._heartbeat_history[-self._max_history:]

        return result

    def perform_heartbeat_check_sync(self) -> HeartbeatResult:
        start_time = datetime.utcnow()
        result = HeartbeatResult()

        for module_id, module in self._modules.items():
            module.status = self._calculate_status(module)
            result.details[module_id] = module
            result.modules_checked += 1

            if module.status == ModuleStatus.HEALTHY:
                result.modules_healthy += 1
            elif module.status == ModuleStatus.DEGRADED:
                result.modules_degraded += 1
            elif module.status == ModuleStatus.UNHEALTHY:
                result.modules_unhealthy += 1
            elif module.status == ModuleStatus.OFFLINE:
                result.modules_offline += 1

        if result.modules_unhealthy > 0 or result.modules_offline > 0:
            result.overall_status = ModuleStatus.UNHEALTHY
        elif result.modules_degraded > 0:
            result.overall_status = ModuleStatus.DEGRADED
        else:
            result.overall_status = ModuleStatus.HEALTHY

        result.duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
        self._heartbeat_history.append(result)
        self._statistics["heartbeats_performed"] += 1

        if len(self._heartbeat_history) > self._max_history:
            self._heartbeat_history = self._heartbeat_history[-self._max_history:]

        return result

    def get_module_health(self, module_id: str) -> Optional[ModuleHealth]:
        return self._modules.get(module_id)

    def get_all_module_health(self) -> Dict[str, ModuleHealth]:
        return self._modules.copy()

    def get_modules_by_status(self, status: ModuleStatus) -> List[ModuleHealth]:
        return [m for m in self._modules.values() if m.status == status]

    def get_healthy_modules(self) -> List[ModuleHealth]:
        return self.get_modules_by_status(ModuleStatus.HEALTHY)

    def get_unhealthy_modules(self) -> List[ModuleHealth]:
        unhealthy = self.get_modules_by_status(ModuleStatus.UNHEALTHY)
        offline = self.get_modules_by_status(ModuleStatus.OFFLINE)
        return unhealthy + offline

    def get_degraded_modules(self) -> List[ModuleHealth]:
        return self.get_modules_by_status(ModuleStatus.DEGRADED)

    def get_heartbeat_history(self, limit: int = 100) -> List[HeartbeatResult]:
        return list(reversed(self._heartbeat_history))[:limit]

    def get_module_dependencies(self, module_id: str) -> List[str]:
        module = self._modules.get(module_id)
        return module.dependencies if module else []

    def get_dependent_modules(self, module_id: str) -> List[str]:
        dependents = []
        for mid, module in self._modules.items():
            if module_id in module.dependencies:
                dependents.append(mid)
        return dependents

    def get_statistics(self) -> Dict[str, Any]:
        healthy = len(self.get_healthy_modules())
        degraded = len(self.get_degraded_modules())
        unhealthy = len(self.get_unhealthy_modules())

        return {
            **self._statistics,
            "total_modules": len(self._modules),
            "healthy_modules": healthy,
            "degraded_modules": degraded,
            "unhealthy_modules": unhealthy,
            "health_percentage": (healthy / len(self._modules) * 100) if self._modules else 0,
            "heartbeat_history_count": len(self._heartbeat_history),
        }

    def get_system_overview(self) -> Dict[str, Any]:
        result = self.perform_heartbeat_check_sync()
        return {
            "overall_status": result.overall_status.value,
            "modules_checked": result.modules_checked,
            "modules_healthy": result.modules_healthy,
            "modules_degraded": result.modules_degraded,
            "modules_unhealthy": result.modules_unhealthy,
            "modules_offline": result.modules_offline,
            "timestamp": result.timestamp.isoformat(),
            "modules": {k: v.to_dict() for k, v in result.details.items()},
        }
