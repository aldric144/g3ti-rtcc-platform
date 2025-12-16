"""
Global Permissions Manager - RBAC permissions for 2,000+ actions across all RTCC modules.
Phase 37: Master UI Integration & System Orchestration Shell
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set
import uuid


class PermissionScope(Enum):
    GLOBAL = "global"
    MODULE = "module"
    FEATURE = "feature"
    DATA = "data"
    ACTION = "action"


class PermissionAction(Enum):
    VIEW = "view"
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    EXECUTE = "execute"
    APPROVE = "approve"
    EXPORT = "export"
    IMPORT = "import"
    CONFIGURE = "configure"
    ADMIN = "admin"


@dataclass
class RolePermission:
    permission_id: str = field(default_factory=lambda: f"perm-{uuid.uuid4().hex[:12]}")
    role: str = ""
    module: str = ""
    feature: str = ""
    action: PermissionAction = PermissionAction.VIEW
    scope: PermissionScope = PermissionScope.FEATURE
    allowed: bool = True
    conditions: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "permission_id": self.permission_id,
            "role": self.role,
            "module": self.module,
            "feature": self.feature,
            "action": self.action.value,
            "scope": self.scope.value,
            "allowed": self.allowed,
            "conditions": self.conditions,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "metadata": self.metadata,
        }


class GlobalPermissionsManager:
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

        self._permissions: Dict[str, RolePermission] = {}
        self._roles: Dict[str, Dict[str, Any]] = {}
        self._user_roles: Dict[str, List[str]] = {}
        self._statistics = {
            "permissions_created": 0,
            "permissions_checked": 0,
            "permissions_granted": 0,
            "permissions_denied": 0,
        }
        self._initialize_roles()
        self._initialize_permissions()

    def _initialize_roles(self):
        self._roles = {
            "system-integrator": {
                "name": "System Integrator",
                "level": 100,
                "description": "Full system access for integration and configuration",
            },
            "super_admin": {
                "name": "Super Administrator",
                "level": 95,
                "description": "Full system access",
            },
            "admin": {
                "name": "Administrator",
                "level": 90,
                "description": "Administrative access",
            },
            "commander": {
                "name": "Commander",
                "level": 80,
                "description": "Command-level access",
            },
            "supervisor": {
                "name": "Supervisor",
                "level": 70,
                "description": "Supervisory access",
            },
            "analyst": {
                "name": "Analyst",
                "level": 60,
                "description": "Analytical access",
            },
            "investigator": {
                "name": "Investigator",
                "level": 55,
                "description": "Investigation access",
            },
            "officer": {
                "name": "Officer",
                "level": 50,
                "description": "Officer-level access",
            },
            "dispatcher": {
                "name": "Dispatcher",
                "level": 45,
                "description": "Dispatch access",
            },
            "operator": {
                "name": "Operator",
                "level": 40,
                "description": "Operator access",
            },
            "viewer": {
                "name": "Viewer",
                "level": 10,
                "description": "View-only access",
            },
            "public": {
                "name": "Public",
                "level": 5,
                "description": "Public access",
            },
        }

    def _initialize_permissions(self):
        modules = [
            "master_dashboard", "real_time_ops", "investigations", "tactical_analytics",
            "officer_safety", "communications", "robotics", "drone_ops", "digital_twin",
            "predictive_intel", "human_stability", "moral_compass", "global_awareness",
            "ai_city_brain", "governance_engine", "fusion_cloud", "autonomous_ops",
            "city_autonomy", "public_guardian", "officer_assist", "cyber_intel",
            "emergency_mgmt", "sentinel_supervisor", "ai_personas", "ethics_guardian",
            "constitution_engine", "data_lake", "intel_orchestration", "ops_continuity",
            "enterprise_infra", "threat_intel", "national_security", "detective_ai",
            "sensor_grid", "logs", "system_health", "redundancy", "failover", "configurations",
        ]

        features = [
            "dashboard", "alerts", "incidents", "reports", "analytics", "maps",
            "heatmaps", "predictions", "investigations", "cases", "evidence",
            "officers", "units", "resources", "drones", "robots", "sensors",
            "events", "notifications", "settings", "users", "roles", "permissions",
            "audit_logs", "exports", "imports", "integrations", "api", "webhooks",
        ]

        actions = list(PermissionAction)

        role_levels = {
            "super_admin": 100,
            "admin": 90,
            "commander": 80,
            "supervisor": 70,
            "analyst": 60,
            "investigator": 55,
            "officer": 50,
            "dispatcher": 45,
            "operator": 40,
            "viewer": 10,
            "public": 5,
        }

        action_min_levels = {
            PermissionAction.VIEW: 5,
            PermissionAction.CREATE: 40,
            PermissionAction.UPDATE: 50,
            PermissionAction.DELETE: 70,
            PermissionAction.EXECUTE: 50,
            PermissionAction.APPROVE: 70,
            PermissionAction.EXPORT: 40,
            PermissionAction.IMPORT: 60,
            PermissionAction.CONFIGURE: 80,
            PermissionAction.ADMIN: 90,
        }

        sensitive_modules = {
            "national_security", "cyber_intel", "human_stability", "moral_compass",
            "ethics_guardian", "constitution_engine", "sentinel_supervisor",
        }

        for role, level in role_levels.items():
            for module in modules:
                module_min_level = 60 if module in sensitive_modules else 5

                for feature in features:
                    for action in actions:
                        action_level = action_min_levels[action]
                        required_level = max(module_min_level, action_level)

                        if module in sensitive_modules and action != PermissionAction.VIEW:
                            required_level = max(required_level, 70)

                        allowed = level >= required_level

                        if role == "public" and module != "public_guardian":
                            allowed = False

                        if role == "public" and module == "public_guardian" and action == PermissionAction.VIEW:
                            allowed = True

                        perm = RolePermission(
                            role=role,
                            module=module,
                            feature=feature,
                            action=action,
                            scope=PermissionScope.FEATURE,
                            allowed=allowed,
                        )
                        key = f"{role}:{module}:{feature}:{action.value}"
                        self._permissions[key] = perm
                        self._statistics["permissions_created"] += 1

    def check_permission(
        self,
        user_id: str,
        module: str,
        feature: str,
        action: PermissionAction,
    ) -> bool:
        self._statistics["permissions_checked"] += 1

        user_roles = self._user_roles.get(user_id, ["viewer"])

        for role in user_roles:
            key = f"{role}:{module}:{feature}:{action.value}"
            perm = self._permissions.get(key)

            if perm and perm.allowed:
                if perm.expires_at and perm.expires_at < datetime.utcnow():
                    continue

                self._statistics["permissions_granted"] += 1
                return True

        self._statistics["permissions_denied"] += 1
        return False

    def check_permission_by_role(
        self,
        role: str,
        module: str,
        feature: str,
        action: PermissionAction,
    ) -> bool:
        key = f"{role}:{module}:{feature}:{action.value}"
        perm = self._permissions.get(key)
        return perm.allowed if perm else False

    def assign_role(self, user_id: str, role: str) -> bool:
        if role not in self._roles:
            return False

        if user_id not in self._user_roles:
            self._user_roles[user_id] = []

        if role not in self._user_roles[user_id]:
            self._user_roles[user_id].append(role)

        return True

    def remove_role(self, user_id: str, role: str) -> bool:
        if user_id in self._user_roles and role in self._user_roles[user_id]:
            self._user_roles[user_id].remove(role)
            return True
        return False

    def get_user_roles(self, user_id: str) -> List[str]:
        return self._user_roles.get(user_id, ["viewer"])

    def get_user_permissions(self, user_id: str) -> List[RolePermission]:
        user_roles = self._user_roles.get(user_id, ["viewer"])
        permissions = []

        for perm in self._permissions.values():
            if perm.role in user_roles and perm.allowed:
                permissions.append(perm)

        return permissions

    def get_role_permissions(self, role: str) -> List[RolePermission]:
        return [p for p in self._permissions.values() if p.role == role and p.allowed]

    def get_module_permissions(self, module: str) -> List[RolePermission]:
        return [p for p in self._permissions.values() if p.module == module]

    def add_permission(
        self,
        role: str,
        module: str,
        feature: str,
        action: PermissionAction,
        allowed: bool = True,
        conditions: Optional[Dict[str, Any]] = None,
        expires_at: Optional[datetime] = None,
    ) -> RolePermission:
        perm = RolePermission(
            role=role,
            module=module,
            feature=feature,
            action=action,
            allowed=allowed,
            conditions=conditions or {},
            expires_at=expires_at,
        )
        key = f"{role}:{module}:{feature}:{action.value}"
        self._permissions[key] = perm
        self._statistics["permissions_created"] += 1
        return perm

    def revoke_permission(
        self,
        role: str,
        module: str,
        feature: str,
        action: PermissionAction,
    ) -> bool:
        key = f"{role}:{module}:{feature}:{action.value}"
        if key in self._permissions:
            self._permissions[key].allowed = False
            return True
        return False

    def get_all_roles(self) -> Dict[str, Dict[str, Any]]:
        return self._roles.copy()

    def get_role(self, role: str) -> Optional[Dict[str, Any]]:
        return self._roles.get(role)

    def create_role(
        self,
        role_id: str,
        name: str,
        level: int,
        description: str = "",
    ) -> bool:
        if role_id in self._roles:
            return False

        self._roles[role_id] = {
            "name": name,
            "level": level,
            "description": description,
        }
        return True

    def get_statistics(self) -> Dict[str, Any]:
        return {
            **self._statistics,
            "total_permissions": len(self._permissions),
            "total_roles": len(self._roles),
            "total_users_with_roles": len(self._user_roles),
            "allowed_permissions": len([p for p in self._permissions.values() if p.allowed]),
            "denied_permissions": len([p for p in self._permissions.values() if not p.allowed]),
        }

    def get_permissions_map(self) -> Dict[str, List[str]]:
        perm_map: Dict[str, List[str]] = {}

        for perm in self._permissions.values():
            if perm.allowed:
                key = f"{perm.module}:{perm.feature}"
                if key not in perm_map:
                    perm_map[key] = []
                if perm.role not in perm_map[key]:
                    perm_map[key].append(perm.role)

        return perm_map

    def get_action_count(self) -> int:
        return len(self._permissions)
