"""
Operational Continuity Module for G3TI RTCC-UIP.

Phase 14: 24/7 operational continuity with redundancy, failover,
health checks, diagnostics, and distributed uptime guarantees.
"""

from app.ops_continuity.healthchecks import (
    ServiceType,
    HealthStatus,
    ServiceHealth,
    HealthSnapshot,
    HealthConfig,
    HealthMetrics,
    HealthCheckService,
)
from app.ops_continuity.failover_manager import (
    FailoverMode,
    FailoverState,
    FailoverEvent,
    FailoverConfig,
    FailoverMetrics,
    FailoverManager,
)
from app.ops_continuity.redundancy_manager import (
    RedundancyMode,
    ConnectionState,
    ServiceInstance,
    ConnectionPool,
    RedundancyConfig,
    RedundancyMetrics,
    RedundancyManager,
)
from app.ops_continuity.diagnostics import (
    DiagnosticCategory,
    DiagnosticSeverity,
    DiagnosticEvent,
    SlowQueryEvent,
    PredictiveAlert,
    DiagnosticsConfig,
    DiagnosticsMetrics,
    DiagnosticsEngine,
)
from app.ops_continuity.ops_audit_log import (
    OpsAuditAction,
    OpsAuditSeverity,
    OpsAuditEntry,
    OpsAuditConfig,
    OpsAuditMetrics,
    OpsAuditLog,
)

__all__ = [
    "ServiceType",
    "HealthStatus",
    "ServiceHealth",
    "HealthSnapshot",
    "HealthConfig",
    "HealthMetrics",
    "HealthCheckService",
    "FailoverMode",
    "FailoverState",
    "FailoverEvent",
    "FailoverConfig",
    "FailoverMetrics",
    "FailoverManager",
    "RedundancyMode",
    "ConnectionState",
    "ServiceInstance",
    "ConnectionPool",
    "RedundancyConfig",
    "RedundancyMetrics",
    "RedundancyManager",
    "DiagnosticCategory",
    "DiagnosticSeverity",
    "DiagnosticEvent",
    "SlowQueryEvent",
    "PredictiveAlert",
    "DiagnosticsConfig",
    "DiagnosticsMetrics",
    "DiagnosticsEngine",
    "OpsAuditAction",
    "OpsAuditSeverity",
    "OpsAuditEntry",
    "OpsAuditConfig",
    "OpsAuditMetrics",
    "OpsAuditLog",
]
