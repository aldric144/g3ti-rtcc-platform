"""
Phase 19: Swarm Coordination Module Tests

Tests for SwarmRouter, SwarmFormationEngine, TaskAllocator, and SwarmTelemetrySynchronizer.
"""

import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch


class TestSwarmRouter:
    """Tests for SwarmRouter."""

    def test_create_swarm(self):
        """Test swarm creation."""
        from backend.app.robotics.swarm_coordination import SwarmRouter

        router = SwarmRouter()
        swarm = router.create_swarm(
            name="Alpha Pack",
            robot_ids=["robot-001", "robot-002", "robot-003"],
            mission_type="patrol",
        )

        assert swarm is not None
        assert swarm.name == "Alpha Pack"
        assert len(swarm.units) == 3

    def test_assign_roles(self):
        """Test role assignment."""
        from backend.app.robotics.swarm_coordination import SwarmRouter, SwarmRole

        router = SwarmRouter()
        swarm = router.create_swarm("Role Test", ["robot-r1", "robot-r2"], "search")

        role_assignments = {
            swarm.units[0].unit_id: SwarmRole.LEADER,
            swarm.units[1].unit_id: SwarmRole.SCOUT,
        }

        updated = router.assign_roles(swarm.swarm_id, role_assignments)
        assert updated is not None

        leader_count = sum(1 for u in updated.units if u.role == SwarmRole.LEADER)
        assert leader_count == 1

    def test_auto_assign_roles(self):
        """Test automatic role assignment."""
        from backend.app.robotics.swarm_coordination import SwarmRouter

        router = SwarmRouter()
        swarm = router.create_swarm("Auto Role Test", ["robot-a1", "robot-a2", "robot-a3", "robot-a4"], "patrol")

        updated = router.auto_assign_roles(swarm.swarm_id, "patrol")
        assert updated is not None

        has_leader = any(u.role.value == "leader" for u in updated.units)
        assert has_leader is True

    def test_route_swarm(self):
        """Test swarm routing."""
        from backend.app.robotics.swarm_coordination import SwarmRouter

        router = SwarmRouter()
        swarm = router.create_swarm("Route Test", ["robot-rt1", "robot-rt2"], "respond")

        routed = router.route_swarm(
            swarm.swarm_id,
            target_position={"x": 200, "y": 200, "z": 0},
            formation="wedge",
        )

        assert routed is not None

    def test_get_swarm(self):
        """Test getting swarm by ID."""
        from backend.app.robotics.swarm_coordination import SwarmRouter

        router = SwarmRouter()
        swarm = router.create_swarm("Get Test", ["robot-g1"], "surveillance")

        retrieved = router.get_swarm(swarm.swarm_id)
        assert retrieved is not None
        assert retrieved.swarm_id == swarm.swarm_id

    def test_get_swarms(self):
        """Test getting swarms with filters."""
        from backend.app.robotics.swarm_coordination import SwarmRouter

        router = SwarmRouter()
        router.create_swarm("Swarm A", ["robot-sa1"], "patrol")
        router.create_swarm("Swarm B", ["robot-sb1"], "search")

        all_swarms = router.get_swarms()
        assert len(all_swarms) >= 2

    def test_disband_swarm(self):
        """Test disbanding swarm."""
        from backend.app.robotics.swarm_coordination import SwarmRouter

        router = SwarmRouter()
        swarm = router.create_swarm("Disband Test", ["robot-d1", "robot-d2"], "patrol")

        result = router.disband_swarm(swarm.swarm_id)
        assert result is True

        disbanded = router.get_swarm(swarm.swarm_id)
        assert disbanded.status == "disbanded"


class TestSwarmFormationEngine:
    """Tests for SwarmFormationEngine."""

    def test_create_formation(self):
        """Test formation creation."""
        from backend.app.robotics.swarm_coordination import SwarmFormationEngine, FormationType

        engine = SwarmFormationEngine()
        formation = engine.create_formation(
            swarm_id="swarm-001",
            formation_type=FormationType.TRIANGLE,
            center_position={"x": 100, "y": 100, "z": 0},
            spacing=10.0,
            heading=45.0,
        )

        assert formation is not None
        assert formation.formation_type == FormationType.TRIANGLE
        assert formation.spacing == 10.0

    def test_update_formation(self):
        """Test formation update."""
        from backend.app.robotics.swarm_coordination import SwarmFormationEngine, FormationType

        engine = SwarmFormationEngine()
        formation = engine.create_formation("swarm-002", FormationType.LINE, {"x": 50, "y": 50, "z": 0}, 8.0, 0.0)

        updated = engine.update_formation(
            formation.formation_id,
            center_position={"x": 75, "y": 75, "z": 0},
            heading=90.0,
        )

        assert updated is not None
        assert updated.center_position["x"] == 75
        assert updated.heading == 90.0

    def test_change_formation(self):
        """Test changing formation type."""
        from backend.app.robotics.swarm_coordination import SwarmFormationEngine, FormationType

        engine = SwarmFormationEngine()
        formation = engine.create_formation("swarm-003", FormationType.COLUMN, {"x": 0, "y": 0, "z": 0}, 5.0, 0.0)

        changed = engine.change_formation(formation.formation_id, FormationType.DIAMOND)
        assert changed is not None
        assert changed.formation_type == FormationType.DIAMOND

    def test_get_formation(self):
        """Test getting formation."""
        from backend.app.robotics.swarm_coordination import SwarmFormationEngine, FormationType

        engine = SwarmFormationEngine()
        formation = engine.create_formation("swarm-004", FormationType.SURROUND, {"x": 100, "y": 100, "z": 0}, 15.0, 0.0)

        retrieved = engine.get_formation(formation.formation_id)
        assert retrieved is not None
        assert retrieved.formation_id == formation.formation_id

    def test_get_unit_target_position(self):
        """Test getting unit target position in formation."""
        from backend.app.robotics.swarm_coordination import SwarmFormationEngine, FormationType

        engine = SwarmFormationEngine()
        formation = engine.create_formation("swarm-005", FormationType.WEDGE, {"x": 50, "y": 50, "z": 0}, 10.0, 0.0)

        position = engine.get_unit_target_position(formation.formation_id, "unit-001", 0)
        assert position is not None
        assert "x" in position
        assert "y" in position

    def test_dissolve_formation(self):
        """Test dissolving formation."""
        from backend.app.robotics.swarm_coordination import SwarmFormationEngine, FormationType

        engine = SwarmFormationEngine()
        formation = engine.create_formation("swarm-006", FormationType.SPREAD, {"x": 0, "y": 0, "z": 0}, 20.0, 0.0)

        result = engine.dissolve_formation(formation.formation_id)
        assert result is True


class TestTaskAllocator:
    """Tests for TaskAllocator."""

    def test_create_task(self):
        """Test task creation."""
        from backend.app.robotics.swarm_coordination import TaskAllocator, TaskPriority

        allocator = TaskAllocator()
        task = allocator.create_task(
            swarm_id="swarm-task-001",
            task_type="patrol_waypoint",
            target_position={"x": 100, "y": 100, "z": 0},
            priority=TaskPriority.HIGH,
            parameters={"duration": 60},
        )

        assert task is not None
        assert task.task_type == "patrol_waypoint"
        assert task.priority == TaskPriority.HIGH

    def test_allocate_task(self):
        """Test task allocation."""
        from backend.app.robotics.swarm_coordination import TaskAllocator, TaskPriority, TaskStatus

        allocator = TaskAllocator()
        task = allocator.create_task("swarm-alloc-001", "scan", {"x": 50, "y": 50, "z": 0}, TaskPriority.MEDIUM)

        allocated = allocator.allocate_task(task.task_id, "unit-001")
        assert allocated is not None
        assert allocated.assigned_unit_id == "unit-001"
        assert allocated.status == TaskStatus.ASSIGNED

    def test_auto_allocate(self):
        """Test automatic task allocation."""
        from backend.app.robotics.swarm_coordination import TaskAllocator, TaskPriority

        allocator = TaskAllocator()
        task = allocator.create_task("swarm-auto-001", "investigate", {"x": 75, "y": 75, "z": 0}, TaskPriority.CRITICAL)

        available_units = [
            {"unit_id": "unit-a1", "position": {"x": 70, "y": 70, "z": 0}, "capabilities": ["investigate"]},
            {"unit_id": "unit-a2", "position": {"x": 100, "y": 100, "z": 0}, "capabilities": ["patrol"]},
        ]

        allocated = allocator.auto_allocate(task.task_id, available_units)
        assert allocated is not None

    def test_complete_task(self):
        """Test task completion."""
        from backend.app.robotics.swarm_coordination import TaskAllocator, TaskPriority, TaskStatus

        allocator = TaskAllocator()
        task = allocator.create_task("swarm-complete-001", "deliver", {"x": 0, "y": 0, "z": 0}, TaskPriority.LOW)
        allocator.allocate_task(task.task_id, "unit-c1")
        allocator.start_task(task.task_id)

        completed = allocator.complete_task(task.task_id, result={"delivered": True})
        assert completed is not None
        assert completed.status == TaskStatus.COMPLETED

    def test_fail_task(self):
        """Test task failure."""
        from backend.app.robotics.swarm_coordination import TaskAllocator, TaskPriority, TaskStatus

        allocator = TaskAllocator()
        task = allocator.create_task("swarm-fail-001", "escort", {"x": 200, "y": 200, "z": 0}, TaskPriority.HIGH)
        allocator.allocate_task(task.task_id, "unit-f1")
        allocator.start_task(task.task_id)

        failed = allocator.fail_task(task.task_id, reason="Obstacle blocked path")
        assert failed is not None
        assert failed.status == TaskStatus.FAILED

    def test_get_pending_tasks(self):
        """Test getting pending tasks."""
        from backend.app.robotics.swarm_coordination import TaskAllocator, TaskPriority

        allocator = TaskAllocator()
        allocator.create_task("swarm-pending-001", "patrol", {"x": 10, "y": 10, "z": 0}, TaskPriority.MEDIUM)
        allocator.create_task("swarm-pending-001", "scan", {"x": 20, "y": 20, "z": 0}, TaskPriority.LOW)

        pending = allocator.get_pending_tasks("swarm-pending-001")
        assert len(pending) >= 2

    def test_get_metrics(self):
        """Test getting task allocation metrics."""
        from backend.app.robotics.swarm_coordination import TaskAllocator

        allocator = TaskAllocator()
        metrics = allocator.get_metrics()

        assert "total_tasks" in metrics
        assert "by_status" in metrics


class TestSwarmTelemetrySynchronizer:
    """Tests for SwarmTelemetrySynchronizer."""

    def test_sync_unit_telemetry(self):
        """Test unit telemetry synchronization."""
        from backend.app.robotics.swarm_coordination import SwarmTelemetrySynchronizer

        sync = SwarmTelemetrySynchronizer()
        result = sync.sync_unit_telemetry(
            swarm_id="swarm-sync-001",
            unit_id="unit-s1",
            position={"x": 100, "y": 100, "z": 0},
            heading=45.0,
            speed=1.5,
            battery_level=85.0,
            status="active",
        )

        assert result is not None
        assert result["unit_id"] == "unit-s1"

    def test_get_swarm_telemetry(self):
        """Test getting swarm telemetry."""
        from backend.app.robotics.swarm_coordination import SwarmTelemetrySynchronizer

        sync = SwarmTelemetrySynchronizer()
        sync.sync_unit_telemetry("swarm-tel-001", "unit-t1", {"x": 0, "y": 0, "z": 0}, 0.0, 0.0, 90.0, "active")
        sync.sync_unit_telemetry("swarm-tel-001", "unit-t2", {"x": 10, "y": 0, "z": 0}, 0.0, 0.0, 85.0, "active")

        telemetry = sync.get_swarm_telemetry("swarm-tel-001")
        assert len(telemetry) == 2

    def test_get_swarm_positions(self):
        """Test getting swarm positions."""
        from backend.app.robotics.swarm_coordination import SwarmTelemetrySynchronizer

        sync = SwarmTelemetrySynchronizer()
        sync.sync_unit_telemetry("swarm-pos-001", "unit-p1", {"x": 50, "y": 50, "z": 0}, 0.0, 1.0, 80.0, "moving")
        sync.sync_unit_telemetry("swarm-pos-001", "unit-p2", {"x": 60, "y": 50, "z": 0}, 0.0, 1.0, 75.0, "moving")

        positions = sync.get_swarm_positions("swarm-pos-001")
        assert len(positions) == 2
        assert "unit-p1" in positions

    def test_get_swarm_status_summary(self):
        """Test getting swarm status summary."""
        from backend.app.robotics.swarm_coordination import SwarmTelemetrySynchronizer

        sync = SwarmTelemetrySynchronizer()
        sync.sync_unit_telemetry("swarm-sum-001", "unit-ss1", {"x": 0, "y": 0, "z": 0}, 0.0, 0.0, 95.0, "active")
        sync.sync_unit_telemetry("swarm-sum-001", "unit-ss2", {"x": 10, "y": 0, "z": 0}, 0.0, 0.0, 25.0, "low_battery")

        summary = sync.get_swarm_status_summary("swarm-sum-001")
        assert "total_units" in summary
        assert summary["total_units"] == 2

    def test_calculate_swarm_spread(self):
        """Test calculating swarm spread."""
        from backend.app.robotics.swarm_coordination import SwarmTelemetrySynchronizer

        sync = SwarmTelemetrySynchronizer()
        sync.sync_unit_telemetry("swarm-spread-001", "unit-sp1", {"x": 0, "y": 0, "z": 0}, 0.0, 0.0, 90.0, "active")
        sync.sync_unit_telemetry("swarm-spread-001", "unit-sp2", {"x": 100, "y": 0, "z": 0}, 0.0, 0.0, 90.0, "active")
        sync.sync_unit_telemetry("swarm-spread-001", "unit-sp3", {"x": 50, "y": 50, "z": 0}, 0.0, 0.0, 90.0, "active")

        spread = sync.calculate_swarm_spread("swarm-spread-001")
        assert spread is not None
        assert spread > 0
