"""
Phase 37: Master UI Integration & System Orchestration Shell
Unified orchestration layer for all RTCC modules (Phases 1-36).
"""

from .event_bus import (
    MasterEventBus,
    EventType,
    EventPriority,
    EventSource,
    MasterEvent,
    EventSubscription,
)
from .alert_aggregator import (
    UnifiedAlertStream,
    AlertSeverity,
    AlertSource,
    UnifiedAlert,
    AlertFilter,
)
from .module_heartbeat import (
    ModuleHeartbeatChecker,
    ModuleStatus,
    ModuleHealth,
    HeartbeatResult,
)
from .state_synchronizer import (
    CrossModuleStateSynchronizer,
    StateChangeType,
    StateChange,
    SyncTarget,
)
from .permissions_manager import (
    GlobalPermissionsManager,
    PermissionAction,
    PermissionScope,
    RolePermission,
)

__all__ = [
    "MasterEventBus",
    "EventType",
    "EventPriority",
    "EventSource",
    "MasterEvent",
    "EventSubscription",
    "UnifiedAlertStream",
    "AlertSeverity",
    "AlertSource",
    "UnifiedAlert",
    "AlertFilter",
    "ModuleHeartbeatChecker",
    "ModuleStatus",
    "ModuleHealth",
    "HeartbeatResult",
    "CrossModuleStateSynchronizer",
    "StateChangeType",
    "StateChange",
    "SyncTarget",
    "GlobalPermissionsManager",
    "PermissionAction",
    "PermissionScope",
    "RolePermission",
]
