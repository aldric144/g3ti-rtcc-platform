"""
Phase 24: PolicyEngine - City Operation Rules and Emergency Thresholds

This module manages city operation policies with support for:
- Policy hierarchy: Global → City → Department → Scenario
- Policy version control and testing sandbox
- Conflict rule resolver
- Emergency overrides for hurricanes, flooding, mass casualty, power outages
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Callable
import uuid
import json
import copy


class PolicyScope(Enum):
    """Policy scope levels in hierarchy."""
    GLOBAL = "global"
    CITY = "city"
    DEPARTMENT = "department"
    SCENARIO = "scenario"


class PolicyType(Enum):
    """Types of policies."""
    TRAFFIC = "traffic"
    PATROL = "patrol"
    EMS = "ems"
    FIRE = "fire"
    UTILITY = "utility"
    EMERGENCY = "emergency"
    RESOURCE = "resource"
    NOTIFICATION = "notification"
    CROWD = "crowd"
    EVACUATION = "evacuation"


class PolicyStatus(Enum):
    """Policy status."""
    DRAFT = "draft"
    ACTIVE = "active"
    TESTING = "testing"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"


class EmergencyType(Enum):
    """Types of emergencies that trigger overrides."""
    HURRICANE = "hurricane"
    FLOODING = "flooding"
    MASS_CASUALTY = "mass_casualty"
    POWER_OUTAGE = "power_outage"
    CITY_WIDE_ALERT = "city_wide_alert"
    ACTIVE_SHOOTER = "active_shooter"
    CIVIL_UNREST = "civil_unrest"
    HAZMAT = "hazmat"
    TORNADO = "tornado"
    WILDFIRE = "wildfire"


class ConflictResolution(Enum):
    """Conflict resolution strategies."""
    HIGHER_SCOPE_WINS = "higher_scope_wins"
    LOWER_SCOPE_WINS = "lower_scope_wins"
    MOST_RESTRICTIVE = "most_restrictive"
    LEAST_RESTRICTIVE = "least_restrictive"
    MOST_RECENT = "most_recent"
    MANUAL = "manual"


@dataclass
class PolicyRule:
    """Individual policy rule."""
    rule_id: str
    name: str
    description: str
    condition: str
    action: str
    parameters: Dict[str, Any]
    priority: int = 5
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "name": self.name,
            "description": self.description,
            "condition": self.condition,
            "action": self.action,
            "parameters": self.parameters,
            "priority": self.priority,
            "enabled": self.enabled,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


@dataclass
class PolicyThreshold:
    """Threshold configuration for policy triggers."""
    threshold_id: str
    name: str
    metric: str
    operator: str  # gt, lt, gte, lte, eq, neq
    value: float
    unit: str
    action_on_breach: str
    cooldown_minutes: int = 15
    enabled: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "threshold_id": self.threshold_id,
            "name": self.name,
            "metric": self.metric,
            "operator": self.operator,
            "value": self.value,
            "unit": self.unit,
            "action_on_breach": self.action_on_breach,
            "cooldown_minutes": self.cooldown_minutes,
            "enabled": self.enabled,
        }

    def evaluate(self, current_value: float) -> bool:
        """Evaluate if threshold is breached."""
        ops = {
            "gt": lambda a, b: a > b,
            "lt": lambda a, b: a < b,
            "gte": lambda a, b: a >= b,
            "lte": lambda a, b: a <= b,
            "eq": lambda a, b: a == b,
            "neq": lambda a, b: a != b,
        }
        op_func = ops.get(self.operator, lambda a, b: False)
        return op_func(current_value, self.value)


@dataclass
class EmergencyOverride:
    """Emergency override configuration."""
    override_id: str
    emergency_type: EmergencyType
    name: str
    description: str
    affected_policies: List[str]
    override_rules: List[PolicyRule]
    auto_activate: bool = True
    requires_confirmation: bool = False
    duration_hours: Optional[int] = None
    activated_at: Optional[datetime] = None
    deactivated_at: Optional[datetime] = None
    activated_by: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "override_id": self.override_id,
            "emergency_type": self.emergency_type.value,
            "name": self.name,
            "description": self.description,
            "affected_policies": self.affected_policies,
            "override_rules": [r.to_dict() for r in self.override_rules],
            "auto_activate": self.auto_activate,
            "requires_confirmation": self.requires_confirmation,
            "duration_hours": self.duration_hours,
            "activated_at": self.activated_at.isoformat() if self.activated_at else None,
            "deactivated_at": self.deactivated_at.isoformat() if self.deactivated_at else None,
            "activated_by": self.activated_by,
        }


@dataclass
class PolicyVersion:
    """Version information for a policy."""
    version_id: str
    version_number: int
    created_at: datetime
    created_by: str
    change_summary: str
    policy_snapshot: Dict[str, Any]
    is_current: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "version_id": self.version_id,
            "version_number": self.version_number,
            "created_at": self.created_at.isoformat(),
            "created_by": self.created_by,
            "change_summary": self.change_summary,
            "policy_snapshot": self.policy_snapshot,
            "is_current": self.is_current,
        }


@dataclass
class Policy:
    """City operation policy."""
    policy_id: str
    name: str
    description: str
    policy_type: PolicyType
    scope: PolicyScope
    scope_id: Optional[str]  # department_id or scenario_id if applicable
    rules: List[PolicyRule]
    thresholds: List[PolicyThreshold]
    status: PolicyStatus
    conflict_resolution: ConflictResolution
    parent_policy_id: Optional[str] = None
    child_policy_ids: List[str] = field(default_factory=list)
    version: int = 1
    versions: List[PolicyVersion] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    created_by: str = "system"
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "policy_id": self.policy_id,
            "name": self.name,
            "description": self.description,
            "policy_type": self.policy_type.value,
            "scope": self.scope.value,
            "scope_id": self.scope_id,
            "rules": [r.to_dict() for r in self.rules],
            "thresholds": [t.to_dict() for t in self.thresholds],
            "status": self.status.value,
            "conflict_resolution": self.conflict_resolution.value,
            "parent_policy_id": self.parent_policy_id,
            "child_policy_ids": self.child_policy_ids,
            "version": self.version,
            "versions": [v.to_dict() for v in self.versions],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "created_by": self.created_by,
            "tags": self.tags,
            "metadata": self.metadata,
        }


@dataclass
class PolicyConflict:
    """Represents a conflict between policies."""
    conflict_id: str
    policy_ids: List[str]
    conflict_type: str
    description: str
    severity: str  # low, medium, high
    suggested_resolution: str
    resolved: bool = False
    resolution_notes: Optional[str] = None
    detected_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "conflict_id": self.conflict_id,
            "policy_ids": self.policy_ids,
            "conflict_type": self.conflict_type,
            "description": self.description,
            "severity": self.severity,
            "suggested_resolution": self.suggested_resolution,
            "resolved": self.resolved,
            "resolution_notes": self.resolution_notes,
            "detected_at": self.detected_at.isoformat(),
        }


@dataclass
class SimulationResult:
    """Result of policy simulation."""
    simulation_id: str
    policy_id: str
    scenario: Dict[str, Any]
    triggered_rules: List[str]
    actions_generated: List[Dict[str, Any]]
    conflicts_detected: List[PolicyConflict]
    metrics: Dict[str, float]
    success: bool
    error_message: Optional[str] = None
    executed_at: datetime = field(default_factory=datetime.utcnow)
    duration_ms: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "simulation_id": self.simulation_id,
            "policy_id": self.policy_id,
            "scenario": self.scenario,
            "triggered_rules": self.triggered_rules,
            "actions_generated": self.actions_generated,
            "conflicts_detected": [c.to_dict() for c in self.conflicts_detected],
            "metrics": self.metrics,
            "success": self.success,
            "error_message": self.error_message,
            "executed_at": self.executed_at.isoformat(),
            "duration_ms": self.duration_ms,
        }


class PolicyEngine:
    """
    Engine for managing city operation policies.
    
    Handles policy hierarchy, version control, conflict resolution,
    and emergency overrides for Riviera Beach operations.
    """

    def __init__(self):
        self._policies: Dict[str, Policy] = {}
        self._emergency_overrides: Dict[str, EmergencyOverride] = {}
        self._active_overrides: Set[str] = set()
        self._conflicts: Dict[str, PolicyConflict] = {}
        self._simulation_results: Dict[str, SimulationResult] = {}
        self._initialize_default_policies()
        self._initialize_emergency_overrides()

    def _initialize_default_policies(self):
        """Initialize default Riviera Beach policies."""
        # Global Traffic Policy
        traffic_policy = Policy(
            policy_id="policy-traffic-global",
            name="Global Traffic Management Policy",
            description="City-wide traffic management rules for Riviera Beach",
            policy_type=PolicyType.TRAFFIC,
            scope=PolicyScope.GLOBAL,
            scope_id=None,
            rules=[
                PolicyRule(
                    rule_id="rule-traffic-001",
                    name="Peak Hour Signal Optimization",
                    description="Optimize traffic signals during peak hours",
                    condition="time_of_day in ['07:00-09:00', '16:00-18:00']",
                    action="optimize_signal_timing",
                    parameters={"optimization_mode": "peak_flow", "cycle_adjustment": 15},
                    priority=8,
                ),
                PolicyRule(
                    rule_id="rule-traffic-002",
                    name="Congestion Response",
                    description="Respond to traffic congestion above threshold",
                    condition="congestion_level > 0.7",
                    action="activate_alternate_routes",
                    parameters={"notification": True, "signal_preemption": True},
                    priority=9,
                ),
            ],
            thresholds=[
                PolicyThreshold(
                    threshold_id="thresh-traffic-001",
                    name="High Congestion Alert",
                    metric="congestion_index",
                    operator="gt",
                    value=0.8,
                    unit="ratio",
                    action_on_breach="alert_traffic_management",
                ),
            ],
            status=PolicyStatus.ACTIVE,
            conflict_resolution=ConflictResolution.HIGHER_SCOPE_WINS,
            created_by="system",
            tags=["traffic", "riviera-beach", "global"],
        )
        self._policies[traffic_policy.policy_id] = traffic_policy

        # Global Patrol Policy
        patrol_policy = Policy(
            policy_id="policy-patrol-global",
            name="Global Patrol Deployment Policy",
            description="City-wide patrol deployment rules for Riviera Beach PD",
            policy_type=PolicyType.PATROL,
            scope=PolicyScope.GLOBAL,
            scope_id=None,
            rules=[
                PolicyRule(
                    rule_id="rule-patrol-001",
                    name="Crime Hotspot Response",
                    description="Increase patrol presence in crime hotspots",
                    condition="crime_density > threshold",
                    action="increase_patrol_coverage",
                    parameters={"coverage_increase": 0.25, "duration_hours": 4},
                    priority=8,
                ),
                PolicyRule(
                    rule_id="rule-patrol-002",
                    name="Event Coverage",
                    description="Deploy additional units for special events",
                    condition="event_type in ['large_gathering', 'parade', 'festival']",
                    action="deploy_event_units",
                    parameters={"min_units": 4, "perimeter_setup": True},
                    priority=7,
                ),
            ],
            thresholds=[
                PolicyThreshold(
                    threshold_id="thresh-patrol-001",
                    name="Critical Incident Response",
                    metric="active_incidents",
                    operator="gt",
                    value=5,
                    unit="count",
                    action_on_breach="activate_mutual_aid",
                ),
            ],
            status=PolicyStatus.ACTIVE,
            conflict_resolution=ConflictResolution.MOST_RESTRICTIVE,
            created_by="system",
            tags=["patrol", "riviera-beach", "law-enforcement"],
        )
        self._policies[patrol_policy.policy_id] = patrol_policy

        # EMS Policy
        ems_policy = Policy(
            policy_id="policy-ems-global",
            name="Global EMS Response Policy",
            description="Emergency Medical Services response rules",
            policy_type=PolicyType.EMS,
            scope=PolicyScope.GLOBAL,
            scope_id=None,
            rules=[
                PolicyRule(
                    rule_id="rule-ems-001",
                    name="Multi-Casualty Response",
                    description="Activate MCI protocol for multiple casualties",
                    condition="casualty_count >= 3",
                    action="activate_mci_protocol",
                    parameters={"triage_setup": True, "mutual_aid": True},
                    priority=10,
                ),
                PolicyRule(
                    rule_id="rule-ems-002",
                    name="Heat Emergency Response",
                    description="Deploy cooling stations during heat emergencies",
                    condition="heat_index > 105",
                    action="activate_heat_protocol",
                    parameters={"cooling_stations": True, "wellness_checks": True},
                    priority=8,
                ),
            ],
            thresholds=[
                PolicyThreshold(
                    threshold_id="thresh-ems-001",
                    name="Response Time Alert",
                    metric="avg_response_time_minutes",
                    operator="gt",
                    value=8,
                    unit="minutes",
                    action_on_breach="reposition_units",
                ),
            ],
            status=PolicyStatus.ACTIVE,
            conflict_resolution=ConflictResolution.MOST_RESTRICTIVE,
            created_by="system",
            tags=["ems", "riviera-beach", "medical"],
        )
        self._policies[ems_policy.policy_id] = ems_policy

        # Utility Policy
        utility_policy = Policy(
            policy_id="policy-utility-global",
            name="Global Utility Management Policy",
            description="City utility management rules",
            policy_type=PolicyType.UTILITY,
            scope=PolicyScope.GLOBAL,
            scope_id=None,
            rules=[
                PolicyRule(
                    rule_id="rule-utility-001",
                    name="Peak Load Management",
                    description="Manage grid load during peak demand",
                    condition="grid_load > 0.85",
                    action="activate_load_shedding",
                    parameters={"priority_areas": ["hospitals", "emergency_services"]},
                    priority=9,
                ),
                PolicyRule(
                    rule_id="rule-utility-002",
                    name="Water Pressure Management",
                    description="Maintain water pressure during high demand",
                    condition="water_pressure < 40",
                    action="activate_backup_pumps",
                    parameters={"pump_stations": ["north", "south"]},
                    priority=8,
                ),
            ],
            thresholds=[
                PolicyThreshold(
                    threshold_id="thresh-utility-001",
                    name="Grid Overload Warning",
                    metric="grid_load_percentage",
                    operator="gt",
                    value=90,
                    unit="percent",
                    action_on_breach="emergency_load_reduction",
                ),
            ],
            status=PolicyStatus.ACTIVE,
            conflict_resolution=ConflictResolution.HIGHER_SCOPE_WINS,
            created_by="system",
            tags=["utility", "riviera-beach", "infrastructure"],
        )
        self._policies[utility_policy.policy_id] = utility_policy

    def _initialize_emergency_overrides(self):
        """Initialize emergency override configurations."""
        # Hurricane Override
        hurricane_override = EmergencyOverride(
            override_id="override-hurricane",
            emergency_type=EmergencyType.HURRICANE,
            name="Hurricane Emergency Override",
            description="Activates hurricane response protocols for Riviera Beach",
            affected_policies=["policy-traffic-global", "policy-patrol-global", "policy-ems-global"],
            override_rules=[
                PolicyRule(
                    rule_id="rule-hurricane-001",
                    name="Evacuation Route Priority",
                    description="Prioritize evacuation routes",
                    condition="hurricane_warning_active",
                    action="activate_evacuation_routes",
                    parameters={"contraflow": True, "signal_override": True},
                    priority=10,
                ),
                PolicyRule(
                    rule_id="rule-hurricane-002",
                    name="Emergency Shelter Activation",
                    description="Open emergency shelters",
                    condition="hurricane_warning_active",
                    action="activate_shelters",
                    parameters={"shelters": ["riviera_beach_high", "community_center"]},
                    priority=10,
                ),
            ],
            auto_activate=False,
            requires_confirmation=True,
            duration_hours=72,
        )
        self._emergency_overrides[hurricane_override.override_id] = hurricane_override

        # Flooding Override
        flooding_override = EmergencyOverride(
            override_id="override-flooding",
            emergency_type=EmergencyType.FLOODING,
            name="Flooding Emergency Override",
            description="Activates flood response protocols",
            affected_policies=["policy-traffic-global", "policy-utility-global"],
            override_rules=[
                PolicyRule(
                    rule_id="rule-flood-001",
                    name="Flood Route Closure",
                    description="Close flooded roadways",
                    condition="flood_level > 6",
                    action="close_flooded_routes",
                    parameters={"barricade_deployment": True, "detour_activation": True},
                    priority=10,
                ),
                PolicyRule(
                    rule_id="rule-flood-002",
                    name="Pump Station Activation",
                    description="Activate all pump stations",
                    condition="flood_level > 4",
                    action="activate_all_pumps",
                    parameters={"max_capacity": True},
                    priority=9,
                ),
            ],
            auto_activate=True,
            requires_confirmation=False,
            duration_hours=24,
        )
        self._emergency_overrides[flooding_override.override_id] = flooding_override

        # Mass Casualty Override
        mci_override = EmergencyOverride(
            override_id="override-mci",
            emergency_type=EmergencyType.MASS_CASUALTY,
            name="Mass Casualty Incident Override",
            description="Activates MCI response protocols",
            affected_policies=["policy-ems-global", "policy-patrol-global", "policy-traffic-global"],
            override_rules=[
                PolicyRule(
                    rule_id="rule-mci-001",
                    name="Hospital Alert",
                    description="Alert all area hospitals",
                    condition="mci_declared",
                    action="hospital_mass_casualty_alert",
                    parameters={"hospitals": ["st_marys", "palm_beach_gardens", "jfk"]},
                    priority=10,
                ),
                PolicyRule(
                    rule_id="rule-mci-002",
                    name="Traffic Corridor Clear",
                    description="Clear traffic corridors to hospitals",
                    condition="mci_declared",
                    action="clear_hospital_corridors",
                    parameters={"signal_preemption": True, "route_priority": True},
                    priority=10,
                ),
            ],
            auto_activate=True,
            requires_confirmation=False,
            duration_hours=12,
        )
        self._emergency_overrides[mci_override.override_id] = mci_override

        # Power Outage Override
        power_override = EmergencyOverride(
            override_id="override-power",
            emergency_type=EmergencyType.POWER_OUTAGE,
            name="Power Outage Emergency Override",
            description="Activates power outage response protocols",
            affected_policies=["policy-utility-global", "policy-traffic-global"],
            override_rules=[
                PolicyRule(
                    rule_id="rule-power-001",
                    name="Generator Activation",
                    description="Activate backup generators for critical facilities",
                    condition="power_outage_detected",
                    action="activate_backup_power",
                    parameters={"facilities": ["city_hall", "police_station", "fire_stations"]},
                    priority=10,
                ),
                PolicyRule(
                    rule_id="rule-power-002",
                    name="Traffic Signal Backup",
                    description="Deploy officers to major intersections",
                    condition="traffic_signals_down",
                    action="deploy_traffic_control",
                    parameters={"intersections": ["blue_heron", "broadway", "us1"]},
                    priority=9,
                ),
            ],
            auto_activate=True,
            requires_confirmation=False,
            duration_hours=24,
        )
        self._emergency_overrides[power_override.override_id] = power_override

        # City-Wide Alert Override
        alert_override = EmergencyOverride(
            override_id="override-citywide",
            emergency_type=EmergencyType.CITY_WIDE_ALERT,
            name="City-Wide Alert Override",
            description="Activates city-wide emergency alert protocols",
            affected_policies=["policy-patrol-global", "policy-ems-global", "policy-traffic-global"],
            override_rules=[
                PolicyRule(
                    rule_id="rule-alert-001",
                    name="Mass Notification",
                    description="Send mass notification to all residents",
                    condition="citywide_alert_declared",
                    action="send_mass_notification",
                    parameters={"channels": ["sms", "email", "siren", "social_media"]},
                    priority=10,
                ),
                PolicyRule(
                    rule_id="rule-alert-002",
                    name="All Units Response",
                    description="All available units respond",
                    condition="citywide_alert_declared",
                    action="all_units_response",
                    parameters={"cancel_leave": True, "recall_off_duty": True},
                    priority=10,
                ),
            ],
            auto_activate=False,
            requires_confirmation=True,
            duration_hours=6,
        )
        self._emergency_overrides[alert_override.override_id] = alert_override

    def create_policy(
        self,
        name: str,
        description: str,
        policy_type: PolicyType,
        scope: PolicyScope,
        rules: List[PolicyRule],
        thresholds: List[PolicyThreshold],
        created_by: str,
        scope_id: Optional[str] = None,
        parent_policy_id: Optional[str] = None,
        conflict_resolution: ConflictResolution = ConflictResolution.HIGHER_SCOPE_WINS,
        tags: Optional[List[str]] = None,
    ) -> Policy:
        """Create a new policy."""
        policy = Policy(
            policy_id=f"policy-{uuid.uuid4().hex[:12]}",
            name=name,
            description=description,
            policy_type=policy_type,
            scope=scope,
            scope_id=scope_id,
            rules=rules,
            thresholds=thresholds,
            status=PolicyStatus.DRAFT,
            conflict_resolution=conflict_resolution,
            parent_policy_id=parent_policy_id,
            created_by=created_by,
            tags=tags or [],
        )

        # Create initial version
        version = PolicyVersion(
            version_id=f"ver-{uuid.uuid4().hex[:8]}",
            version_number=1,
            created_at=datetime.utcnow(),
            created_by=created_by,
            change_summary="Initial policy creation",
            policy_snapshot=policy.to_dict(),
            is_current=True,
        )
        policy.versions.append(version)

        # Link to parent if specified
        if parent_policy_id and parent_policy_id in self._policies:
            self._policies[parent_policy_id].child_policy_ids.append(policy.policy_id)

        self._policies[policy.policy_id] = policy
        return policy

    def update_policy(
        self,
        policy_id: str,
        updated_by: str,
        change_summary: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        rules: Optional[List[PolicyRule]] = None,
        thresholds: Optional[List[PolicyThreshold]] = None,
        status: Optional[PolicyStatus] = None,
        tags: Optional[List[str]] = None,
    ) -> Optional[Policy]:
        """Update an existing policy with version control."""
        policy = self._policies.get(policy_id)
        if not policy:
            return None

        # Mark current version as not current
        for v in policy.versions:
            v.is_current = False

        # Apply updates
        if name:
            policy.name = name
        if description:
            policy.description = description
        if rules is not None:
            policy.rules = rules
        if thresholds is not None:
            policy.thresholds = thresholds
        if status:
            policy.status = status
        if tags is not None:
            policy.tags = tags

        policy.version += 1
        policy.updated_at = datetime.utcnow()

        # Create new version
        version = PolicyVersion(
            version_id=f"ver-{uuid.uuid4().hex[:8]}",
            version_number=policy.version,
            created_at=datetime.utcnow(),
            created_by=updated_by,
            change_summary=change_summary,
            policy_snapshot=policy.to_dict(),
            is_current=True,
        )
        policy.versions.append(version)

        return policy

    def get_policy(self, policy_id: str) -> Optional[Policy]:
        """Get a policy by ID."""
        return self._policies.get(policy_id)

    def get_policies(
        self,
        policy_type: Optional[PolicyType] = None,
        scope: Optional[PolicyScope] = None,
        status: Optional[PolicyStatus] = None,
    ) -> List[Policy]:
        """Get policies with optional filters."""
        policies = list(self._policies.values())

        if policy_type:
            policies = [p for p in policies if p.policy_type == policy_type]
        if scope:
            policies = [p for p in policies if p.scope == scope]
        if status:
            policies = [p for p in policies if p.status == status]

        return policies

    def activate_policy(self, policy_id: str) -> bool:
        """Activate a policy."""
        policy = self._policies.get(policy_id)
        if not policy:
            return False

        policy.status = PolicyStatus.ACTIVE
        policy.updated_at = datetime.utcnow()
        return True

    def deactivate_policy(self, policy_id: str) -> bool:
        """Deactivate a policy."""
        policy = self._policies.get(policy_id)
        if not policy:
            return False

        policy.status = PolicyStatus.DEPRECATED
        policy.updated_at = datetime.utcnow()
        return True

    def rollback_policy(self, policy_id: str, version_number: int) -> Optional[Policy]:
        """Rollback a policy to a previous version."""
        policy = self._policies.get(policy_id)
        if not policy:
            return None

        target_version = None
        for v in policy.versions:
            if v.version_number == version_number:
                target_version = v
                break

        if not target_version:
            return None

        # Restore from snapshot
        snapshot = target_version.policy_snapshot
        policy.name = snapshot["name"]
        policy.description = snapshot["description"]
        policy.rules = [
            PolicyRule(
                rule_id=r["rule_id"],
                name=r["name"],
                description=r["description"],
                condition=r["condition"],
                action=r["action"],
                parameters=r["parameters"],
                priority=r["priority"],
                enabled=r["enabled"],
            )
            for r in snapshot.get("rules", [])
        ]
        policy.thresholds = [
            PolicyThreshold(
                threshold_id=t["threshold_id"],
                name=t["name"],
                metric=t["metric"],
                operator=t["operator"],
                value=t["value"],
                unit=t["unit"],
                action_on_breach=t["action_on_breach"],
                cooldown_minutes=t.get("cooldown_minutes", 15),
                enabled=t.get("enabled", True),
            )
            for t in snapshot.get("thresholds", [])
        ]

        policy.version += 1
        policy.updated_at = datetime.utcnow()

        # Mark all versions as not current
        for v in policy.versions:
            v.is_current = False

        # Create rollback version
        rollback_version = PolicyVersion(
            version_id=f"ver-{uuid.uuid4().hex[:8]}",
            version_number=policy.version,
            created_at=datetime.utcnow(),
            created_by="system",
            change_summary=f"Rollback to version {version_number}",
            policy_snapshot=policy.to_dict(),
            is_current=True,
        )
        policy.versions.append(rollback_version)

        return policy

    def activate_emergency_override(
        self,
        override_id: str,
        activated_by: str,
    ) -> bool:
        """Activate an emergency override."""
        override = self._emergency_overrides.get(override_id)
        if not override:
            return False

        if override.requires_confirmation and not activated_by:
            return False

        override.activated_at = datetime.utcnow()
        override.activated_by = activated_by
        self._active_overrides.add(override_id)
        return True

    def deactivate_emergency_override(self, override_id: str) -> bool:
        """Deactivate an emergency override."""
        override = self._emergency_overrides.get(override_id)
        if not override:
            return False

        override.deactivated_at = datetime.utcnow()
        self._active_overrides.discard(override_id)
        return True

    def get_active_overrides(self) -> List[EmergencyOverride]:
        """Get all active emergency overrides."""
        return [
            self._emergency_overrides[oid]
            for oid in self._active_overrides
            if oid in self._emergency_overrides
        ]

    def get_emergency_override(self, override_id: str) -> Optional[EmergencyOverride]:
        """Get an emergency override by ID."""
        return self._emergency_overrides.get(override_id)

    def get_all_emergency_overrides(self) -> List[EmergencyOverride]:
        """Get all emergency overrides."""
        return list(self._emergency_overrides.values())

    def detect_conflicts(self, policy_ids: Optional[List[str]] = None) -> List[PolicyConflict]:
        """Detect conflicts between policies."""
        conflicts = []
        policies = [
            self._policies[pid] for pid in (policy_ids or self._policies.keys())
            if pid in self._policies
        ]

        # Check for rule conflicts
        for i, p1 in enumerate(policies):
            for p2 in policies[i + 1:]:
                if p1.policy_type == p2.policy_type:
                    for r1 in p1.rules:
                        for r2 in p2.rules:
                            if r1.condition == r2.condition and r1.action != r2.action:
                                conflict = PolicyConflict(
                                    conflict_id=f"conflict-{uuid.uuid4().hex[:8]}",
                                    policy_ids=[p1.policy_id, p2.policy_id],
                                    conflict_type="rule_action_conflict",
                                    description=f"Rules '{r1.name}' and '{r2.name}' have same condition but different actions",
                                    severity="medium",
                                    suggested_resolution=f"Apply {p1.conflict_resolution.value} resolution",
                                )
                                conflicts.append(conflict)
                                self._conflicts[conflict.conflict_id] = conflict

        return conflicts

    def resolve_conflict(
        self,
        conflict_id: str,
        resolution_notes: str,
    ) -> bool:
        """Mark a conflict as resolved."""
        conflict = self._conflicts.get(conflict_id)
        if not conflict:
            return False

        conflict.resolved = True
        conflict.resolution_notes = resolution_notes
        return True

    def simulate_policy(
        self,
        policy_id: str,
        scenario: Dict[str, Any],
    ) -> SimulationResult:
        """Simulate a policy against a scenario."""
        import time
        start_time = time.time()

        policy = self._policies.get(policy_id)
        if not policy:
            return SimulationResult(
                simulation_id=f"sim-{uuid.uuid4().hex[:8]}",
                policy_id=policy_id,
                scenario=scenario,
                triggered_rules=[],
                actions_generated=[],
                conflicts_detected=[],
                metrics={},
                success=False,
                error_message="Policy not found",
            )

        triggered_rules = []
        actions_generated = []

        # Evaluate rules against scenario
        for rule in policy.rules:
            if rule.enabled:
                # Simple condition evaluation (in production, use proper expression parser)
                condition_met = self._evaluate_condition(rule.condition, scenario)
                if condition_met:
                    triggered_rules.append(rule.rule_id)
                    actions_generated.append({
                        "rule_id": rule.rule_id,
                        "action": rule.action,
                        "parameters": rule.parameters,
                        "priority": rule.priority,
                    })

        # Check thresholds
        for threshold in policy.thresholds:
            if threshold.enabled:
                metric_value = scenario.get(threshold.metric, 0)
                if threshold.evaluate(metric_value):
                    actions_generated.append({
                        "threshold_id": threshold.threshold_id,
                        "action": threshold.action_on_breach,
                        "metric": threshold.metric,
                        "value": metric_value,
                        "threshold_value": threshold.value,
                    })

        # Detect conflicts
        conflicts = self.detect_conflicts([policy_id])

        duration_ms = (time.time() - start_time) * 1000

        result = SimulationResult(
            simulation_id=f"sim-{uuid.uuid4().hex[:8]}",
            policy_id=policy_id,
            scenario=scenario,
            triggered_rules=triggered_rules,
            actions_generated=actions_generated,
            conflicts_detected=conflicts,
            metrics={
                "rules_evaluated": len(policy.rules),
                "rules_triggered": len(triggered_rules),
                "thresholds_evaluated": len(policy.thresholds),
                "actions_generated": len(actions_generated),
            },
            success=True,
            duration_ms=duration_ms,
        )

        self._simulation_results[result.simulation_id] = result
        return result

    def _evaluate_condition(self, condition: str, scenario: Dict[str, Any]) -> bool:
        """Evaluate a condition against scenario data."""
        # Simple evaluation - in production use proper expression parser
        try:
            # Handle simple comparisons
            if ">" in condition:
                parts = condition.split(">")
                metric = parts[0].strip()
                value = float(parts[1].strip())
                return scenario.get(metric, 0) > value
            elif "<" in condition:
                parts = condition.split("<")
                metric = parts[0].strip()
                value = float(parts[1].strip())
                return scenario.get(metric, 0) < value
            elif "==" in condition:
                parts = condition.split("==")
                metric = parts[0].strip()
                value = parts[1].strip().strip("'\"")
                return str(scenario.get(metric, "")) == value
            elif " in " in condition:
                parts = condition.split(" in ")
                metric = parts[0].strip()
                values = eval(parts[1].strip())
                return scenario.get(metric, "") in values
            else:
                return scenario.get(condition, False)
        except Exception:
            return False

    def get_effective_rules(
        self,
        policy_type: PolicyType,
        scope_id: Optional[str] = None,
    ) -> List[PolicyRule]:
        """Get effective rules considering hierarchy and overrides."""
        rules = []

        # Get rules from hierarchy (Global → City → Department → Scenario)
        for scope in [PolicyScope.GLOBAL, PolicyScope.CITY, PolicyScope.DEPARTMENT, PolicyScope.SCENARIO]:
            for policy in self._policies.values():
                if policy.policy_type == policy_type and policy.scope == scope:
                    if policy.status == PolicyStatus.ACTIVE:
                        if scope_id is None or policy.scope_id == scope_id:
                            rules.extend([r for r in policy.rules if r.enabled])

        # Apply active emergency overrides
        for override_id in self._active_overrides:
            override = self._emergency_overrides.get(override_id)
            if override:
                rules.extend(override.override_rules)

        # Sort by priority (higher priority first)
        rules.sort(key=lambda r: r.priority, reverse=True)
        return rules

    def get_statistics(self) -> Dict[str, Any]:
        """Get policy engine statistics."""
        return {
            "total_policies": len(self._policies),
            "active_policies": len([p for p in self._policies.values() if p.status == PolicyStatus.ACTIVE]),
            "draft_policies": len([p for p in self._policies.values() if p.status == PolicyStatus.DRAFT]),
            "policies_by_type": {
                pt.value: len([p for p in self._policies.values() if p.policy_type == pt])
                for pt in PolicyType
            },
            "policies_by_scope": {
                ps.value: len([p for p in self._policies.values() if p.scope == ps])
                for ps in PolicyScope
            },
            "total_emergency_overrides": len(self._emergency_overrides),
            "active_overrides": len(self._active_overrides),
            "total_conflicts": len(self._conflicts),
            "unresolved_conflicts": len([c for c in self._conflicts.values() if not c.resolved]),
            "total_simulations": len(self._simulation_results),
        }


_policy_engine: Optional[PolicyEngine] = None


def get_policy_engine() -> PolicyEngine:
    """Get the singleton PolicyEngine instance."""
    global _policy_engine
    if _policy_engine is None:
        _policy_engine = PolicyEngine()
    return _policy_engine
