"""
Swarm Coordination Module

Provides multi-robot swarm coordination capabilities including:
- SwarmRouter: Multi-unit role assignment (scout, follow, flank)
- SwarmFormationEngine: Formation patterns (triangle, line, surround)
- TaskAllocator: Task assignment based on proximity and capability
- SwarmTelemetrySynchronizer: Synchronized telemetry across swarm
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
import uuid
import math


class SwarmRole(Enum):
    """Roles for swarm units."""
    SCOUT = "scout"
    FOLLOW = "follow"
    FLANK_LEFT = "flank_left"
    FLANK_RIGHT = "flank_right"
    REAR_GUARD = "rear_guard"
    LEADER = "leader"
    SUPPORT = "support"
    OVERWATCH = "overwatch"
    RESERVE = "reserve"


class FormationType(Enum):
    """Swarm formation types."""
    TRIANGLE = "triangle"
    LINE = "line"
    SURROUND = "surround"
    WEDGE = "wedge"
    COLUMN = "column"
    ECHELON_LEFT = "echelon_left"
    ECHELON_RIGHT = "echelon_right"
    DIAMOND = "diamond"
    SPREAD = "spread"


class TaskPriority(Enum):
    """Task priority levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    ROUTINE = "routine"


class TaskStatus(Enum):
    """Task status."""
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class SwarmUnit:
    """Unit in a swarm."""
    unit_id: str
    robot_id: str
    swarm_id: str
    role: SwarmRole
    position: Dict[str, float]
    heading: float
    speed: float
    target_position: Optional[Dict[str, float]]
    formation_offset: Dict[str, float]
    is_active: bool
    battery_level: float
    capabilities: List[str]
    last_update: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SwarmFormation:
    """Swarm formation configuration."""
    formation_id: str
    swarm_id: str
    formation_type: FormationType
    center_position: Dict[str, float]
    heading: float
    spacing: float
    unit_positions: Dict[str, Dict[str, float]]
    is_active: bool
    created_at: str
    updated_at: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SwarmTask:
    """Task assigned to swarm or unit."""
    task_id: str
    swarm_id: Optional[str]
    unit_id: Optional[str]
    task_type: str
    priority: TaskPriority
    status: TaskStatus
    target_position: Optional[Dict[str, float]]
    parameters: Dict[str, Any]
    assigned_at: str
    started_at: Optional[str]
    completed_at: Optional[str]
    result: Optional[Dict[str, Any]]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Swarm:
    """Swarm of robots."""
    swarm_id: str
    name: str
    units: List[str]
    leader_id: Optional[str]
    formation: Optional[FormationType]
    mission_id: Optional[str]
    status: str
    created_at: str
    updated_at: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class SwarmRouter:
    """Service for routing and role assignment in swarms."""

    def __init__(self):
        self.swarms: Dict[str, Swarm] = {}
        self.units: Dict[str, SwarmUnit] = {}
        self.role_assignments: Dict[str, Dict[str, SwarmRole]] = {}

    def create_swarm(
        self,
        name: str,
        robot_ids: List[str],
        leader_id: Optional[str] = None,
    ) -> Swarm:
        """Create a new swarm from robots."""
        swarm_id = f"swarm-{uuid.uuid4().hex[:12]}"
        timestamp = datetime.utcnow().isoformat() + "Z"

        swarm = Swarm(
            swarm_id=swarm_id,
            name=name,
            units=[],
            leader_id=leader_id,
            formation=None,
            mission_id=None,
            status="forming",
            created_at=timestamp,
            updated_at=timestamp,
            metadata={},
        )

        self.swarms[swarm_id] = swarm
        self.role_assignments[swarm_id] = {}

        for i, robot_id in enumerate(robot_ids):
            role = SwarmRole.LEADER if robot_id == leader_id else SwarmRole.FOLLOW
            unit = self._create_unit(swarm_id, robot_id, role)
            swarm.units.append(unit.unit_id)

        if not leader_id and robot_ids:
            swarm.leader_id = robot_ids[0]
            if swarm.units:
                first_unit = self.units.get(swarm.units[0])
                if first_unit:
                    first_unit.role = SwarmRole.LEADER
                    self.role_assignments[swarm_id][first_unit.unit_id] = SwarmRole.LEADER

        swarm.status = "ready"

        return swarm

    def _create_unit(
        self,
        swarm_id: str,
        robot_id: str,
        role: SwarmRole,
    ) -> SwarmUnit:
        """Create a swarm unit."""
        unit_id = f"unit-{uuid.uuid4().hex[:12]}"
        timestamp = datetime.utcnow().isoformat() + "Z"

        unit = SwarmUnit(
            unit_id=unit_id,
            robot_id=robot_id,
            swarm_id=swarm_id,
            role=role,
            position={'x': 0, 'y': 0, 'z': 0},
            heading=0.0,
            speed=0.0,
            target_position=None,
            formation_offset={'x': 0, 'y': 0, 'z': 0},
            is_active=True,
            battery_level=100.0,
            capabilities=[],
            last_update=timestamp,
            metadata={},
        )

        self.units[unit_id] = unit
        self.role_assignments[swarm_id][unit_id] = role

        return unit

    def assign_roles(
        self,
        swarm_id: str,
        role_assignments: Dict[str, SwarmRole],
    ) -> bool:
        """Assign roles to units in a swarm."""
        swarm = self.swarms.get(swarm_id)
        if not swarm:
            return False

        for unit_id, role in role_assignments.items():
            unit = self.units.get(unit_id)
            if unit and unit.swarm_id == swarm_id:
                unit.role = role
                self.role_assignments[swarm_id][unit_id] = role

                if role == SwarmRole.LEADER:
                    swarm.leader_id = unit.robot_id

        swarm.updated_at = datetime.utcnow().isoformat() + "Z"

        return True

    def auto_assign_roles(
        self,
        swarm_id: str,
        mission_type: str = "patrol",
    ) -> Dict[str, SwarmRole]:
        """Automatically assign roles based on mission type."""
        swarm = self.swarms.get(swarm_id)
        if not swarm:
            return {}

        units = [self.units[uid] for uid in swarm.units if uid in self.units]
        if not units:
            return {}

        assignments = {}

        units_sorted = sorted(units, key=lambda u: u.battery_level, reverse=True)

        if mission_type == "patrol":
            for i, unit in enumerate(units_sorted):
                if i == 0:
                    assignments[unit.unit_id] = SwarmRole.LEADER
                elif i == 1:
                    assignments[unit.unit_id] = SwarmRole.SCOUT
                elif i % 2 == 0:
                    assignments[unit.unit_id] = SwarmRole.FLANK_LEFT
                else:
                    assignments[unit.unit_id] = SwarmRole.FLANK_RIGHT

        elif mission_type == "search":
            for i, unit in enumerate(units_sorted):
                if i == 0:
                    assignments[unit.unit_id] = SwarmRole.LEADER
                elif i < len(units_sorted) // 2:
                    assignments[unit.unit_id] = SwarmRole.SCOUT
                else:
                    assignments[unit.unit_id] = SwarmRole.SUPPORT

        elif mission_type == "surround":
            for i, unit in enumerate(units_sorted):
                if i == 0:
                    assignments[unit.unit_id] = SwarmRole.OVERWATCH
                else:
                    assignments[unit.unit_id] = SwarmRole.FOLLOW

        elif mission_type == "escort":
            for i, unit in enumerate(units_sorted):
                if i == 0:
                    assignments[unit.unit_id] = SwarmRole.LEADER
                elif i == 1:
                    assignments[unit.unit_id] = SwarmRole.SCOUT
                elif i == len(units_sorted) - 1:
                    assignments[unit.unit_id] = SwarmRole.REAR_GUARD
                else:
                    assignments[unit.unit_id] = SwarmRole.FLANK_LEFT if i % 2 == 0 else SwarmRole.FLANK_RIGHT

        else:
            for i, unit in enumerate(units_sorted):
                if i == 0:
                    assignments[unit.unit_id] = SwarmRole.LEADER
                else:
                    assignments[unit.unit_id] = SwarmRole.FOLLOW

        self.assign_roles(swarm_id, assignments)

        return assignments

    def route_swarm(
        self,
        swarm_id: str,
        target_position: Dict[str, float],
        formation: Optional[FormationType] = None,
    ) -> Dict[str, Dict[str, float]]:
        """Route swarm to target position with formation."""
        swarm = self.swarms.get(swarm_id)
        if not swarm:
            return {}

        unit_targets = {}

        for unit_id in swarm.units:
            unit = self.units.get(unit_id)
            if not unit or not unit.is_active:
                continue

            offset = unit.formation_offset
            unit_target = {
                'x': target_position.get('x', 0) + offset.get('x', 0),
                'y': target_position.get('y', 0) + offset.get('y', 0),
                'z': target_position.get('z', 0) + offset.get('z', 0),
            }

            unit.target_position = unit_target
            unit_targets[unit_id] = unit_target

        swarm.updated_at = datetime.utcnow().isoformat() + "Z"

        return unit_targets

    def get_swarm(self, swarm_id: str) -> Optional[Swarm]:
        """Get a swarm by ID."""
        return self.swarms.get(swarm_id)

    def get_swarms(
        self,
        status: Optional[str] = None,
    ) -> List[Swarm]:
        """Get swarms with optional filtering."""
        swarms = list(self.swarms.values())

        if status:
            swarms = [s for s in swarms if s.status == status]

        return swarms

    def get_unit(self, unit_id: str) -> Optional[SwarmUnit]:
        """Get a unit by ID."""
        return self.units.get(unit_id)

    def get_swarm_units(self, swarm_id: str) -> List[SwarmUnit]:
        """Get all units in a swarm."""
        swarm = self.swarms.get(swarm_id)
        if not swarm:
            return []

        return [self.units[uid] for uid in swarm.units if uid in self.units]

    def disband_swarm(self, swarm_id: str) -> bool:
        """Disband a swarm."""
        swarm = self.swarms.get(swarm_id)
        if not swarm:
            return False

        for unit_id in swarm.units:
            if unit_id in self.units:
                del self.units[unit_id]

        if swarm_id in self.role_assignments:
            del self.role_assignments[swarm_id]

        del self.swarms[swarm_id]

        return True


class SwarmFormationEngine:
    """Engine for managing swarm formations."""

    def __init__(self):
        self.formations: Dict[str, SwarmFormation] = {}
        self.formation_templates: Dict[FormationType, List[Dict[str, float]]] = {}
        self._init_templates()

    def _init_templates(self):
        """Initialize formation templates."""
        self.formation_templates = {
            FormationType.TRIANGLE: [
                {'x': 0, 'y': 2, 'z': 0},
                {'x': -1.5, 'y': 0, 'z': 0},
                {'x': 1.5, 'y': 0, 'z': 0},
            ],
            FormationType.LINE: [
                {'x': -3, 'y': 0, 'z': 0},
                {'x': -1, 'y': 0, 'z': 0},
                {'x': 1, 'y': 0, 'z': 0},
                {'x': 3, 'y': 0, 'z': 0},
            ],
            FormationType.SURROUND: [
                {'x': 0, 'y': 2, 'z': 0},
                {'x': 2, 'y': 0, 'z': 0},
                {'x': 0, 'y': -2, 'z': 0},
                {'x': -2, 'y': 0, 'z': 0},
            ],
            FormationType.WEDGE: [
                {'x': 0, 'y': 2, 'z': 0},
                {'x': -1, 'y': 1, 'z': 0},
                {'x': 1, 'y': 1, 'z': 0},
                {'x': -2, 'y': 0, 'z': 0},
                {'x': 2, 'y': 0, 'z': 0},
            ],
            FormationType.COLUMN: [
                {'x': 0, 'y': 3, 'z': 0},
                {'x': 0, 'y': 1, 'z': 0},
                {'x': 0, 'y': -1, 'z': 0},
                {'x': 0, 'y': -3, 'z': 0},
            ],
            FormationType.DIAMOND: [
                {'x': 0, 'y': 2, 'z': 0},
                {'x': -2, 'y': 0, 'z': 0},
                {'x': 2, 'y': 0, 'z': 0},
                {'x': 0, 'y': -2, 'z': 0},
            ],
            FormationType.ECHELON_LEFT: [
                {'x': 0, 'y': 0, 'z': 0},
                {'x': -1.5, 'y': -1.5, 'z': 0},
                {'x': -3, 'y': -3, 'z': 0},
                {'x': -4.5, 'y': -4.5, 'z': 0},
            ],
            FormationType.ECHELON_RIGHT: [
                {'x': 0, 'y': 0, 'z': 0},
                {'x': 1.5, 'y': -1.5, 'z': 0},
                {'x': 3, 'y': -3, 'z': 0},
                {'x': 4.5, 'y': -4.5, 'z': 0},
            ],
            FormationType.SPREAD: [
                {'x': -4, 'y': 0, 'z': 0},
                {'x': -2, 'y': 0, 'z': 0},
                {'x': 0, 'y': 0, 'z': 0},
                {'x': 2, 'y': 0, 'z': 0},
                {'x': 4, 'y': 0, 'z': 0},
            ],
        }

    def create_formation(
        self,
        swarm_id: str,
        formation_type: FormationType,
        center_position: Dict[str, float],
        heading: float = 0.0,
        spacing: float = 2.0,
        unit_ids: Optional[List[str]] = None,
    ) -> SwarmFormation:
        """Create a formation for a swarm."""
        formation_id = f"formation-{uuid.uuid4().hex[:12]}"
        timestamp = datetime.utcnow().isoformat() + "Z"

        template = self.formation_templates.get(formation_type, [])
        unit_positions = {}

        if unit_ids:
            for i, unit_id in enumerate(unit_ids):
                if i < len(template):
                    offset = template[i]
                else:
                    offset = {'x': i * spacing, 'y': 0, 'z': 0}

                rotated = self._rotate_offset(offset, heading)
                scaled = {
                    'x': rotated['x'] * spacing,
                    'y': rotated['y'] * spacing,
                    'z': rotated['z'] * spacing,
                }

                position = {
                    'x': center_position.get('x', 0) + scaled['x'],
                    'y': center_position.get('y', 0) + scaled['y'],
                    'z': center_position.get('z', 0) + scaled['z'],
                }

                unit_positions[unit_id] = position

        formation = SwarmFormation(
            formation_id=formation_id,
            swarm_id=swarm_id,
            formation_type=formation_type,
            center_position=center_position,
            heading=heading,
            spacing=spacing,
            unit_positions=unit_positions,
            is_active=True,
            created_at=timestamp,
            updated_at=timestamp,
            metadata={},
        )

        self.formations[formation_id] = formation

        return formation

    def _rotate_offset(
        self,
        offset: Dict[str, float],
        heading: float,
    ) -> Dict[str, float]:
        """Rotate an offset by heading angle."""
        rad = math.radians(heading)
        cos_h = math.cos(rad)
        sin_h = math.sin(rad)

        x = offset.get('x', 0)
        y = offset.get('y', 0)

        return {
            'x': x * cos_h - y * sin_h,
            'y': x * sin_h + y * cos_h,
            'z': offset.get('z', 0),
        }

    def update_formation(
        self,
        formation_id: str,
        center_position: Optional[Dict[str, float]] = None,
        heading: Optional[float] = None,
        spacing: Optional[float] = None,
    ) -> bool:
        """Update formation parameters."""
        formation = self.formations.get(formation_id)
        if not formation:
            return False

        if center_position:
            formation.center_position = center_position
        if heading is not None:
            formation.heading = heading
        if spacing is not None:
            formation.spacing = spacing

        self._recalculate_positions(formation)
        formation.updated_at = datetime.utcnow().isoformat() + "Z"

        return True

    def _recalculate_positions(self, formation: SwarmFormation) -> None:
        """Recalculate unit positions based on formation parameters."""
        template = self.formation_templates.get(formation.formation_type, [])

        for i, unit_id in enumerate(formation.unit_positions.keys()):
            if i < len(template):
                offset = template[i]
            else:
                offset = {'x': i * formation.spacing, 'y': 0, 'z': 0}

            rotated = self._rotate_offset(offset, formation.heading)
            scaled = {
                'x': rotated['x'] * formation.spacing,
                'y': rotated['y'] * formation.spacing,
                'z': rotated['z'] * formation.spacing,
            }

            position = {
                'x': formation.center_position.get('x', 0) + scaled['x'],
                'y': formation.center_position.get('y', 0) + scaled['y'],
                'z': formation.center_position.get('z', 0) + scaled['z'],
            }

            formation.unit_positions[unit_id] = position

    def change_formation(
        self,
        formation_id: str,
        new_formation_type: FormationType,
    ) -> bool:
        """Change formation type."""
        formation = self.formations.get(formation_id)
        if not formation:
            return False

        formation.formation_type = new_formation_type
        self._recalculate_positions(formation)
        formation.updated_at = datetime.utcnow().isoformat() + "Z"

        return True

    def get_formation(self, formation_id: str) -> Optional[SwarmFormation]:
        """Get a formation by ID."""
        return self.formations.get(formation_id)

    def get_swarm_formation(self, swarm_id: str) -> Optional[SwarmFormation]:
        """Get active formation for a swarm."""
        for formation in self.formations.values():
            if formation.swarm_id == swarm_id and formation.is_active:
                return formation
        return None

    def get_unit_target_position(
        self,
        formation_id: str,
        unit_id: str,
    ) -> Optional[Dict[str, float]]:
        """Get target position for a unit in formation."""
        formation = self.formations.get(formation_id)
        if not formation:
            return None

        return formation.unit_positions.get(unit_id)

    def dissolve_formation(self, formation_id: str) -> bool:
        """Dissolve a formation."""
        formation = self.formations.get(formation_id)
        if not formation:
            return False

        formation.is_active = False
        formation.updated_at = datetime.utcnow().isoformat() + "Z"

        return True


class TaskAllocator:
    """Service for allocating tasks to swarm units."""

    def __init__(self):
        self.tasks: Dict[str, SwarmTask] = {}
        self.unit_tasks: Dict[str, List[str]] = {}
        self.swarm_tasks: Dict[str, List[str]] = {}

    def create_task(
        self,
        task_type: str,
        priority: TaskPriority,
        target_position: Optional[Dict[str, float]] = None,
        parameters: Optional[Dict[str, Any]] = None,
        swarm_id: Optional[str] = None,
    ) -> SwarmTask:
        """Create a new task."""
        task_id = f"task-{uuid.uuid4().hex[:12]}"
        timestamp = datetime.utcnow().isoformat() + "Z"

        task = SwarmTask(
            task_id=task_id,
            swarm_id=swarm_id,
            unit_id=None,
            task_type=task_type,
            priority=priority,
            status=TaskStatus.PENDING,
            target_position=target_position,
            parameters=parameters or {},
            assigned_at=timestamp,
            started_at=None,
            completed_at=None,
            result=None,
            metadata={},
        )

        self.tasks[task_id] = task

        if swarm_id:
            if swarm_id not in self.swarm_tasks:
                self.swarm_tasks[swarm_id] = []
            self.swarm_tasks[swarm_id].append(task_id)

        return task

    def allocate_task(
        self,
        task_id: str,
        unit_id: str,
    ) -> bool:
        """Allocate a task to a specific unit."""
        task = self.tasks.get(task_id)
        if not task:
            return False

        task.unit_id = unit_id
        task.status = TaskStatus.ASSIGNED
        task.assigned_at = datetime.utcnow().isoformat() + "Z"

        if unit_id not in self.unit_tasks:
            self.unit_tasks[unit_id] = []
        self.unit_tasks[unit_id].append(task_id)

        return True

    def auto_allocate(
        self,
        task_id: str,
        available_units: List[SwarmUnit],
        unit_positions: Dict[str, Dict[str, float]],
    ) -> Optional[str]:
        """Automatically allocate task to best available unit."""
        task = self.tasks.get(task_id)
        if not task or not available_units:
            return None

        if not task.target_position:
            best_unit = max(available_units, key=lambda u: u.battery_level)
            self.allocate_task(task_id, best_unit.unit_id)
            return best_unit.unit_id

        best_unit = None
        best_score = float('-inf')

        for unit in available_units:
            position = unit_positions.get(unit.unit_id, unit.position)

            dx = position.get('x', 0) - task.target_position.get('x', 0)
            dy = position.get('y', 0) - task.target_position.get('y', 0)
            distance = math.sqrt(dx**2 + dy**2)

            distance_score = 100 - min(100, distance)
            battery_score = unit.battery_level
            capability_score = 50

            if task.task_type in unit.capabilities:
                capability_score = 100

            total_score = (
                distance_score * 0.4 +
                battery_score * 0.3 +
                capability_score * 0.3
            )

            if total_score > best_score:
                best_score = total_score
                best_unit = unit

        if best_unit:
            self.allocate_task(task_id, best_unit.unit_id)
            return best_unit.unit_id

        return None

    def start_task(self, task_id: str) -> bool:
        """Mark a task as started."""
        task = self.tasks.get(task_id)
        if not task:
            return False

        task.status = TaskStatus.IN_PROGRESS
        task.started_at = datetime.utcnow().isoformat() + "Z"

        return True

    def complete_task(
        self,
        task_id: str,
        result: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Mark a task as completed."""
        task = self.tasks.get(task_id)
        if not task:
            return False

        task.status = TaskStatus.COMPLETED
        task.completed_at = datetime.utcnow().isoformat() + "Z"
        task.result = result

        return True

    def fail_task(
        self,
        task_id: str,
        reason: str,
    ) -> bool:
        """Mark a task as failed."""
        task = self.tasks.get(task_id)
        if not task:
            return False

        task.status = TaskStatus.FAILED
        task.completed_at = datetime.utcnow().isoformat() + "Z"
        task.result = {"failure_reason": reason}

        return True

    def cancel_task(self, task_id: str) -> bool:
        """Cancel a task."""
        task = self.tasks.get(task_id)
        if not task:
            return False

        if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
            return False

        task.status = TaskStatus.CANCELLED
        task.completed_at = datetime.utcnow().isoformat() + "Z"

        return True

    def get_task(self, task_id: str) -> Optional[SwarmTask]:
        """Get a task by ID."""
        return self.tasks.get(task_id)

    def get_unit_tasks(
        self,
        unit_id: str,
        status: Optional[TaskStatus] = None,
    ) -> List[SwarmTask]:
        """Get tasks for a unit."""
        task_ids = self.unit_tasks.get(unit_id, [])
        tasks = [self.tasks[tid] for tid in task_ids if tid in self.tasks]

        if status:
            tasks = [t for t in tasks if t.status == status]

        return tasks

    def get_swarm_tasks(
        self,
        swarm_id: str,
        status: Optional[TaskStatus] = None,
    ) -> List[SwarmTask]:
        """Get tasks for a swarm."""
        task_ids = self.swarm_tasks.get(swarm_id, [])
        tasks = [self.tasks[tid] for tid in task_ids if tid in self.tasks]

        if status:
            tasks = [t for t in tasks if t.status == status]

        return tasks

    def get_pending_tasks(
        self,
        priority: Optional[TaskPriority] = None,
    ) -> List[SwarmTask]:
        """Get pending tasks."""
        tasks = [t for t in self.tasks.values() if t.status == TaskStatus.PENDING]

        if priority:
            tasks = [t for t in tasks if t.priority == priority]

        priority_order = {
            TaskPriority.CRITICAL: 0,
            TaskPriority.HIGH: 1,
            TaskPriority.MEDIUM: 2,
            TaskPriority.LOW: 3,
            TaskPriority.ROUTINE: 4,
        }
        tasks.sort(key=lambda t: priority_order.get(t.priority, 5))

        return tasks

    def get_metrics(self) -> Dict[str, Any]:
        """Get task allocation metrics."""
        total = len(self.tasks)
        by_status = {}
        by_priority = {}

        for task in self.tasks.values():
            status_key = task.status.value
            by_status[status_key] = by_status.get(status_key, 0) + 1

            priority_key = task.priority.value
            by_priority[priority_key] = by_priority.get(priority_key, 0) + 1

        return {
            "total_tasks": total,
            "by_status": by_status,
            "by_priority": by_priority,
            "pending_count": by_status.get("pending", 0),
            "in_progress_count": by_status.get("in_progress", 0),
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }


class SwarmTelemetrySynchronizer:
    """Service for synchronizing telemetry across swarm units."""

    def __init__(self):
        self.swarm_telemetry: Dict[str, Dict[str, Dict[str, Any]]] = {}
        self.sync_timestamps: Dict[str, str] = {}
        self.telemetry_history: Dict[str, List[Dict[str, Any]]] = {}

    def sync_unit_telemetry(
        self,
        swarm_id: str,
        unit_id: str,
        position: Dict[str, float],
        heading: float,
        speed: float,
        battery_level: float,
        status: str,
        sensor_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Synchronize telemetry from a unit."""
        timestamp = datetime.utcnow().isoformat() + "Z"

        if swarm_id not in self.swarm_telemetry:
            self.swarm_telemetry[swarm_id] = {}

        telemetry = {
            "unit_id": unit_id,
            "position": position,
            "heading": heading,
            "speed": speed,
            "battery_level": battery_level,
            "status": status,
            "sensor_data": sensor_data or {},
            "timestamp": timestamp,
        }

        self.swarm_telemetry[swarm_id][unit_id] = telemetry
        self.sync_timestamps[swarm_id] = timestamp

        if swarm_id not in self.telemetry_history:
            self.telemetry_history[swarm_id] = []

        self.telemetry_history[swarm_id].append({
            "unit_id": unit_id,
            "telemetry": telemetry,
        })

        if len(self.telemetry_history[swarm_id]) > 10000:
            self.telemetry_history[swarm_id] = self.telemetry_history[swarm_id][-10000:]

        return telemetry

    def get_swarm_telemetry(
        self,
        swarm_id: str,
    ) -> Dict[str, Dict[str, Any]]:
        """Get current telemetry for all units in a swarm."""
        return self.swarm_telemetry.get(swarm_id, {})

    def get_unit_telemetry(
        self,
        swarm_id: str,
        unit_id: str,
    ) -> Optional[Dict[str, Any]]:
        """Get current telemetry for a specific unit."""
        swarm_data = self.swarm_telemetry.get(swarm_id, {})
        return swarm_data.get(unit_id)

    def get_swarm_positions(
        self,
        swarm_id: str,
    ) -> Dict[str, Dict[str, float]]:
        """Get positions of all units in a swarm."""
        swarm_data = self.swarm_telemetry.get(swarm_id, {})
        return {
            unit_id: data["position"]
            for unit_id, data in swarm_data.items()
        }

    def get_swarm_status_summary(
        self,
        swarm_id: str,
    ) -> Dict[str, Any]:
        """Get status summary for a swarm."""
        swarm_data = self.swarm_telemetry.get(swarm_id, {})

        if not swarm_data:
            return {
                "swarm_id": swarm_id,
                "unit_count": 0,
                "status": "no_data",
            }

        total_battery = 0.0
        statuses = {}
        positions = []

        for unit_id, data in swarm_data.items():
            total_battery += data.get("battery_level", 0)
            status = data.get("status", "unknown")
            statuses[status] = statuses.get(status, 0) + 1
            positions.append(data.get("position", {}))

        center = {'x': 0, 'y': 0, 'z': 0}
        if positions:
            center = {
                'x': sum(p.get('x', 0) for p in positions) / len(positions),
                'y': sum(p.get('y', 0) for p in positions) / len(positions),
                'z': sum(p.get('z', 0) for p in positions) / len(positions),
            }

        return {
            "swarm_id": swarm_id,
            "unit_count": len(swarm_data),
            "average_battery": total_battery / max(1, len(swarm_data)),
            "status_breakdown": statuses,
            "center_position": center,
            "last_sync": self.sync_timestamps.get(swarm_id),
        }

    def get_telemetry_history(
        self,
        swarm_id: str,
        unit_id: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Get telemetry history for a swarm."""
        history = self.telemetry_history.get(swarm_id, [])

        if unit_id:
            history = [h for h in history if h["unit_id"] == unit_id]

        return history[-limit:]

    def calculate_swarm_spread(
        self,
        swarm_id: str,
    ) -> float:
        """Calculate the spread (max distance between units) of a swarm."""
        positions = self.get_swarm_positions(swarm_id)

        if len(positions) < 2:
            return 0.0

        max_distance = 0.0
        position_list = list(positions.values())

        for i in range(len(position_list)):
            for j in range(i + 1, len(position_list)):
                dx = position_list[i].get('x', 0) - position_list[j].get('x', 0)
                dy = position_list[i].get('y', 0) - position_list[j].get('y', 0)
                distance = math.sqrt(dx**2 + dy**2)

                if distance > max_distance:
                    max_distance = distance

        return max_distance


__all__ = [
    "SwarmRouter",
    "SwarmFormationEngine",
    "TaskAllocator",
    "SwarmTelemetrySynchronizer",
    "SwarmUnit",
    "SwarmFormation",
    "SwarmTask",
    "Swarm",
    "SwarmRole",
    "FormationType",
    "TaskPriority",
    "TaskStatus",
]
