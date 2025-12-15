"""
Cross-Module State Synchronizer - Synchronizes state changes across all RTCC modules.
Phase 37: Master UI Integration & System Orchestration Shell
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set
import uuid
import json
import asyncio


class StateChangeType(Enum):
    MAP_UPDATE = "map_update"
    ALERT_UPDATE = "alert_update"
    INVESTIGATION_UPDATE = "investigation_update"
    TACTICAL_HEATMAP_UPDATE = "tactical_heatmap_update"
    PREDICTIVE_MODEL_REFRESH = "predictive_model_refresh"
    OPERATOR_HUD_UPDATE = "operator_hud_update"
    PUBLIC_SAFETY_LOG = "public_safety_log"
    OFFICER_STATUS_UPDATE = "officer_status_update"
    DRONE_TELEMETRY_UPDATE = "drone_telemetry_update"
    ROBOT_TELEMETRY_UPDATE = "robot_telemetry_update"
    INCIDENT_UPDATE = "incident_update"
    RESOURCE_UPDATE = "resource_update"
    THREAT_UPDATE = "threat_update"
    COMPLIANCE_UPDATE = "compliance_update"
    TRUST_SCORE_UPDATE = "trust_score_update"
    CITY_BRAIN_UPDATE = "city_brain_update"
    GOVERNANCE_UPDATE = "governance_update"
    EMERGENCY_UPDATE = "emergency_update"
    SENSOR_UPDATE = "sensor_update"
    DIGITAL_TWIN_UPDATE = "digital_twin_update"
    MODULE_STATUS_UPDATE = "module_status_update"


class SyncTarget(Enum):
    MAPS = "maps"
    ALERTS = "alerts"
    INVESTIGATIONS = "investigations"
    TACTICAL_HEATMAPS = "tactical_heatmaps"
    PREDICTIVE_MODELS = "predictive_models"
    OPERATOR_HUD = "operator_hud"
    PUBLIC_SAFETY_LOGS = "public_safety_logs"
    OFFICER_STATUS = "officer_status"
    DRONE_DASHBOARD = "drone_dashboard"
    ROBOT_DASHBOARD = "robot_dashboard"
    INCIDENT_TRACKER = "incident_tracker"
    RESOURCE_MANAGER = "resource_manager"
    THREAT_DASHBOARD = "threat_dashboard"
    COMPLIANCE_DASHBOARD = "compliance_dashboard"
    TRUST_SCORE_DASHBOARD = "trust_score_dashboard"
    CITY_BRAIN_DASHBOARD = "city_brain_dashboard"
    GOVERNANCE_DASHBOARD = "governance_dashboard"
    EMERGENCY_DASHBOARD = "emergency_dashboard"
    SENSOR_DASHBOARD = "sensor_dashboard"
    DIGITAL_TWIN_VIEW = "digital_twin_view"
    MODULE_STATUS_PANEL = "module_status_panel"
    MASTER_DASHBOARD = "master_dashboard"
    ALL = "all"


@dataclass
class StateChange:
    change_id: str = field(default_factory=lambda: f"sc-{uuid.uuid4().hex[:12]}")
    change_type: StateChangeType = StateChangeType.MAP_UPDATE
    source_module: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    targets: List[SyncTarget] = field(default_factory=list)
    data: Dict[str, Any] = field(default_factory=dict)
    priority: int = 5
    requires_acknowledgment: bool = False
    acknowledged_by: List[str] = field(default_factory=list)
    propagated: bool = False
    propagated_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "change_id": self.change_id,
            "change_type": self.change_type.value,
            "source_module": self.source_module,
            "timestamp": self.timestamp.isoformat(),
            "targets": [t.value for t in self.targets],
            "data": self.data,
            "priority": self.priority,
            "requires_acknowledgment": self.requires_acknowledgment,
            "acknowledged_by": self.acknowledged_by,
            "propagated": self.propagated,
            "propagated_at": self.propagated_at.isoformat() if self.propagated_at else None,
            "metadata": self.metadata,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict())


class CrossModuleStateSynchronizer:
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

        self._state_changes: Dict[str, StateChange] = {}
        self._change_history: List[StateChange] = []
        self._max_history = 5000
        self._subscribers: Dict[SyncTarget, List[Callable[[StateChange], None]]] = {}
        self._async_subscribers: Dict[SyncTarget, List[Callable[[StateChange], Any]]] = {}
        self._statistics = {
            "changes_published": 0,
            "changes_propagated": 0,
            "subscribers_notified": 0,
        }

        self._sync_rules: Dict[StateChangeType, List[SyncTarget]] = {
            StateChangeType.MAP_UPDATE: [
                SyncTarget.MAPS, SyncTarget.OPERATOR_HUD, SyncTarget.MASTER_DASHBOARD,
                SyncTarget.DIGITAL_TWIN_VIEW,
            ],
            StateChangeType.ALERT_UPDATE: [
                SyncTarget.ALERTS, SyncTarget.OPERATOR_HUD, SyncTarget.MASTER_DASHBOARD,
                SyncTarget.OFFICER_STATUS, SyncTarget.INCIDENT_TRACKER,
            ],
            StateChangeType.INVESTIGATION_UPDATE: [
                SyncTarget.INVESTIGATIONS, SyncTarget.MASTER_DASHBOARD,
                SyncTarget.THREAT_DASHBOARD,
            ],
            StateChangeType.TACTICAL_HEATMAP_UPDATE: [
                SyncTarget.TACTICAL_HEATMAPS, SyncTarget.MAPS, SyncTarget.MASTER_DASHBOARD,
                SyncTarget.PREDICTIVE_MODELS,
            ],
            StateChangeType.PREDICTIVE_MODEL_REFRESH: [
                SyncTarget.PREDICTIVE_MODELS, SyncTarget.TACTICAL_HEATMAPS,
                SyncTarget.MASTER_DASHBOARD, SyncTarget.OPERATOR_HUD,
            ],
            StateChangeType.OPERATOR_HUD_UPDATE: [
                SyncTarget.OPERATOR_HUD, SyncTarget.MASTER_DASHBOARD,
            ],
            StateChangeType.PUBLIC_SAFETY_LOG: [
                SyncTarget.PUBLIC_SAFETY_LOGS, SyncTarget.COMPLIANCE_DASHBOARD,
                SyncTarget.TRUST_SCORE_DASHBOARD,
            ],
            StateChangeType.OFFICER_STATUS_UPDATE: [
                SyncTarget.OFFICER_STATUS, SyncTarget.MAPS, SyncTarget.OPERATOR_HUD,
                SyncTarget.MASTER_DASHBOARD, SyncTarget.RESOURCE_MANAGER,
            ],
            StateChangeType.DRONE_TELEMETRY_UPDATE: [
                SyncTarget.DRONE_DASHBOARD, SyncTarget.MAPS, SyncTarget.DIGITAL_TWIN_VIEW,
                SyncTarget.MASTER_DASHBOARD,
            ],
            StateChangeType.ROBOT_TELEMETRY_UPDATE: [
                SyncTarget.ROBOT_DASHBOARD, SyncTarget.MAPS, SyncTarget.DIGITAL_TWIN_VIEW,
                SyncTarget.MASTER_DASHBOARD,
            ],
            StateChangeType.INCIDENT_UPDATE: [
                SyncTarget.INCIDENT_TRACKER, SyncTarget.MAPS, SyncTarget.ALERTS,
                SyncTarget.MASTER_DASHBOARD, SyncTarget.OPERATOR_HUD,
            ],
            StateChangeType.RESOURCE_UPDATE: [
                SyncTarget.RESOURCE_MANAGER, SyncTarget.OPERATOR_HUD,
                SyncTarget.MASTER_DASHBOARD,
            ],
            StateChangeType.THREAT_UPDATE: [
                SyncTarget.THREAT_DASHBOARD, SyncTarget.ALERTS, SyncTarget.MAPS,
                SyncTarget.MASTER_DASHBOARD, SyncTarget.OPERATOR_HUD,
            ],
            StateChangeType.COMPLIANCE_UPDATE: [
                SyncTarget.COMPLIANCE_DASHBOARD, SyncTarget.PUBLIC_SAFETY_LOGS,
                SyncTarget.GOVERNANCE_DASHBOARD,
            ],
            StateChangeType.TRUST_SCORE_UPDATE: [
                SyncTarget.TRUST_SCORE_DASHBOARD, SyncTarget.PUBLIC_SAFETY_LOGS,
                SyncTarget.MASTER_DASHBOARD,
            ],
            StateChangeType.CITY_BRAIN_UPDATE: [
                SyncTarget.CITY_BRAIN_DASHBOARD, SyncTarget.DIGITAL_TWIN_VIEW,
                SyncTarget.MASTER_DASHBOARD, SyncTarget.GOVERNANCE_DASHBOARD,
            ],
            StateChangeType.GOVERNANCE_UPDATE: [
                SyncTarget.GOVERNANCE_DASHBOARD, SyncTarget.COMPLIANCE_DASHBOARD,
                SyncTarget.MASTER_DASHBOARD,
            ],
            StateChangeType.EMERGENCY_UPDATE: [
                SyncTarget.EMERGENCY_DASHBOARD, SyncTarget.ALERTS, SyncTarget.MAPS,
                SyncTarget.MASTER_DASHBOARD, SyncTarget.OPERATOR_HUD, SyncTarget.ALL,
            ],
            StateChangeType.SENSOR_UPDATE: [
                SyncTarget.SENSOR_DASHBOARD, SyncTarget.DIGITAL_TWIN_VIEW,
                SyncTarget.MAPS,
            ],
            StateChangeType.DIGITAL_TWIN_UPDATE: [
                SyncTarget.DIGITAL_TWIN_VIEW, SyncTarget.MAPS, SyncTarget.MASTER_DASHBOARD,
                SyncTarget.CITY_BRAIN_DASHBOARD,
            ],
            StateChangeType.MODULE_STATUS_UPDATE: [
                SyncTarget.MODULE_STATUS_PANEL, SyncTarget.MASTER_DASHBOARD,
            ],
        }

    def subscribe(
        self,
        target: SyncTarget,
        callback: Callable[[StateChange], None],
    ) -> str:
        if target not in self._subscribers:
            self._subscribers[target] = []
        self._subscribers[target].append(callback)
        return f"sub-{target.value}-{len(self._subscribers[target])}"

    def subscribe_async(
        self,
        target: SyncTarget,
        callback: Callable[[StateChange], Any],
    ) -> str:
        if target not in self._async_subscribers:
            self._async_subscribers[target] = []
        self._async_subscribers[target].append(callback)
        return f"async-sub-{target.value}-{len(self._async_subscribers[target])}"

    async def publish_change(self, change: StateChange) -> bool:
        self._state_changes[change.change_id] = change
        self._change_history.append(change)
        self._statistics["changes_published"] += 1

        if len(self._change_history) > self._max_history:
            self._change_history = self._change_history[-self._max_history:]

        if not change.targets:
            change.targets = self._sync_rules.get(change.change_type, [SyncTarget.MASTER_DASHBOARD])

        await self._propagate_change(change)
        return True

    def publish_change_sync(self, change: StateChange) -> bool:
        self._state_changes[change.change_id] = change
        self._change_history.append(change)
        self._statistics["changes_published"] += 1

        if len(self._change_history) > self._max_history:
            self._change_history = self._change_history[-self._max_history:]

        if not change.targets:
            change.targets = self._sync_rules.get(change.change_type, [SyncTarget.MASTER_DASHBOARD])

        self._propagate_change_sync(change)
        return True

    async def _propagate_change(self, change: StateChange):
        targets_to_notify = set(change.targets)

        if SyncTarget.ALL in targets_to_notify:
            targets_to_notify = set(SyncTarget)
            targets_to_notify.remove(SyncTarget.ALL)

        for target in targets_to_notify:
            if target in self._async_subscribers:
                for callback in self._async_subscribers[target]:
                    try:
                        await callback(change)
                        self._statistics["subscribers_notified"] += 1
                    except Exception:
                        pass

            if target in self._subscribers:
                for callback in self._subscribers[target]:
                    try:
                        callback(change)
                        self._statistics["subscribers_notified"] += 1
                    except Exception:
                        pass

        change.propagated = True
        change.propagated_at = datetime.utcnow()
        self._statistics["changes_propagated"] += 1

    def _propagate_change_sync(self, change: StateChange):
        targets_to_notify = set(change.targets)

        if SyncTarget.ALL in targets_to_notify:
            targets_to_notify = set(SyncTarget)
            targets_to_notify.remove(SyncTarget.ALL)

        for target in targets_to_notify:
            if target in self._subscribers:
                for callback in self._subscribers[target]:
                    try:
                        callback(change)
                        self._statistics["subscribers_notified"] += 1
                    except Exception:
                        pass

        change.propagated = True
        change.propagated_at = datetime.utcnow()
        self._statistics["changes_propagated"] += 1

    def create_change(
        self,
        change_type: StateChangeType,
        source_module: str,
        data: Dict[str, Any],
        targets: Optional[List[SyncTarget]] = None,
        priority: int = 5,
        requires_acknowledgment: bool = False,
    ) -> StateChange:
        return StateChange(
            change_type=change_type,
            source_module=source_module,
            data=data,
            targets=targets or [],
            priority=priority,
            requires_acknowledgment=requires_acknowledgment,
        )

    def get_change(self, change_id: str) -> Optional[StateChange]:
        return self._state_changes.get(change_id)

    def get_recent_changes(
        self,
        limit: int = 100,
        change_type: Optional[StateChangeType] = None,
        source_module: Optional[str] = None,
    ) -> List[StateChange]:
        changes = list(reversed(self._change_history))

        if change_type:
            changes = [c for c in changes if c.change_type == change_type]

        if source_module:
            changes = [c for c in changes if c.source_module == source_module]

        return changes[:limit]

    def get_changes_by_target(self, target: SyncTarget, limit: int = 100) -> List[StateChange]:
        changes = [c for c in reversed(self._change_history) if target in c.targets]
        return changes[:limit]

    def get_pending_acknowledgments(self) -> List[StateChange]:
        return [
            c for c in self._state_changes.values()
            if c.requires_acknowledgment and not c.acknowledged_by
        ]

    def acknowledge_change(self, change_id: str, acknowledged_by: str) -> bool:
        change = self._state_changes.get(change_id)
        if change and change.requires_acknowledgment:
            if acknowledged_by not in change.acknowledged_by:
                change.acknowledged_by.append(acknowledged_by)
            return True
        return False

    def get_sync_rules(self) -> Dict[str, List[str]]:
        return {
            k.value: [t.value for t in v]
            for k, v in self._sync_rules.items()
        }

    def add_sync_rule(self, change_type: StateChangeType, targets: List[SyncTarget]):
        if change_type not in self._sync_rules:
            self._sync_rules[change_type] = []
        self._sync_rules[change_type].extend(targets)

    def get_statistics(self) -> Dict[str, Any]:
        return {
            **self._statistics,
            "total_changes": len(self._state_changes),
            "history_count": len(self._change_history),
            "subscriber_count": sum(len(v) for v in self._subscribers.values()),
            "async_subscriber_count": sum(len(v) for v in self._async_subscribers.values()),
            "pending_acknowledgments": len(self.get_pending_acknowledgments()),
        }

    def get_current_state_summary(self) -> Dict[str, Any]:
        recent = self.get_recent_changes(limit=50)
        by_type: Dict[str, int] = {}
        by_source: Dict[str, int] = {}

        for change in recent:
            by_type[change.change_type.value] = by_type.get(change.change_type.value, 0) + 1
            by_source[change.source_module] = by_source.get(change.source_module, 0) + 1

        return {
            "recent_changes_count": len(recent),
            "changes_by_type": by_type,
            "changes_by_source": by_source,
            "last_change": recent[0].to_dict() if recent else None,
            "statistics": self.get_statistics(),
        }
