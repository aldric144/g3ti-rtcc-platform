"""
Phase 27: Enterprise Deployment Infrastructure

This module provides enterprise-grade deployment architecture for the G3TI RTCC-UIP platform,
including CJIS controls, Zero-Trust networking, high-availability clusters, and multi-region failover.

Modules:
- ZeroTrustGateway: Token validation, mTLS, geo-restrictions, device fingerprinting
- CJISComplianceLayer: CJIS 5.9 compliance checks and enforcement
- HighAvailabilityManager: Load balancing, failover, auto-restart
- MultiRegionFailoverEngine: Active/active and active/passive cluster models
- ServiceRegistry: Microservice tracking and health monitoring
"""

from app.infra.zero_trust import (
    ZeroTrustGateway,
    get_zero_trust_gateway,
    AccessDecision,
    GeoRestriction,
    DeviceFingerprint,
)
from app.infra.cjis_compliance import (
    CJISComplianceLayer,
    get_cjis_compliance_layer,
    ComplianceResult,
    CJISViolationType,
)
from app.infra.high_availability import (
    HighAvailabilityManager,
    get_ha_manager,
    NodeStatus,
    FailoverEvent,
)
from app.infra.multi_region_failover import (
    MultiRegionFailoverEngine,
    get_failover_engine,
    RegionStatus,
    FailoverMode,
)
from app.infra.service_registry import (
    ServiceRegistry,
    get_service_registry,
    ServiceStatus,
    ServiceType,
)

__all__ = [
    "ZeroTrustGateway",
    "get_zero_trust_gateway",
    "AccessDecision",
    "GeoRestriction",
    "DeviceFingerprint",
    "CJISComplianceLayer",
    "get_cjis_compliance_layer",
    "ComplianceResult",
    "CJISViolationType",
    "HighAvailabilityManager",
    "get_ha_manager",
    "NodeStatus",
    "FailoverEvent",
    "MultiRegionFailoverEngine",
    "get_failover_engine",
    "RegionStatus",
    "FailoverMode",
    "ServiceRegistry",
    "get_service_registry",
    "ServiceStatus",
    "ServiceType",
]
