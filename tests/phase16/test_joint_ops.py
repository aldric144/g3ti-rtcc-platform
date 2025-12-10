"""
Tests for JointOpsManager

Tests joint operation creation, lifecycle management, agency participation,
unit deployment, objectives, and timeline events.
"""

import pytest
from datetime import datetime

from app.fusion_cloud.joint_ops import (
    JointOpsManager,
    JointOperation,
    OperationType,
    OperationStatus,
    OperationRoom,
    OperationRole,
    SharedTimeline,
    TimelineEvent,
    TimelineEventType,
    WhiteboardItemType,
    AgencyParticipation,
    OperationUnit,
    OperationObjective,
)


@pytest.fixture
def joint_ops_manager():
    """Create a fresh JointOpsManager for each test"""
    return JointOpsManager()


class TestOperationCreation:
    """Tests for operation creation"""

    def test_create_operation_basic(self, joint_ops_manager):
        """Test basic operation creation"""
        operation = joint_ops_manager.create_operation(
            name="Operation Thunder",
            operation_type=OperationType.RAID,
            lead_tenant_id="tenant-001",
            lead_agency_name="Metro PD",
            commander_name="Captain Smith",
        )

        assert operation is not None
        assert operation.name == "Operation Thunder"
        assert operation.operation_type == OperationType.RAID
        assert operation.status == OperationStatus.PLANNING
        assert operation.lead_tenant_id == "tenant-001"

    def test_create_operation_with_jurisdiction(self, joint_ops_manager):
        """Test operation creation with jurisdiction codes"""
        operation = joint_ops_manager.create_operation(
            name="Regional Task Force Op",
            operation_type=OperationType.TASK_FORCE,
            lead_tenant_id="tenant-001",
            lead_agency_name="Metro PD",
            commander_name="Captain Smith",
            jurisdiction_codes=["CA-METRO", "CA-COUNTY", "CA-EAST"],
        )

        assert operation is not None
        assert "CA-METRO" in operation.jurisdiction_codes
        assert len(operation.jurisdiction_codes) == 3

    def test_create_operation_with_description(self, joint_ops_manager):
        """Test operation creation with description"""
        operation = joint_ops_manager.create_operation(
            name="Operation Thunder",
            operation_type=OperationType.RAID,
            lead_tenant_id="tenant-001",
            lead_agency_name="Metro PD",
            commander_name="Captain Smith",
            description="Multi-agency raid on suspected drug operation",
        )

        assert operation is not None
        assert operation.description == "Multi-agency raid on suspected drug operation"

    def test_create_operation_types(self, joint_ops_manager):
        """Test creating different operation types"""
        types = [
            OperationType.PURSUIT,
            OperationType.INVESTIGATION,
            OperationType.SURVEILLANCE,
            OperationType.RAID,
            OperationType.SEARCH,
            OperationType.RESCUE,
        ]

        for i, op_type in enumerate(types):
            operation = joint_ops_manager.create_operation(
                name=f"Operation {i}",
                operation_type=op_type,
                lead_tenant_id="tenant-001",
                lead_agency_name="Metro PD",
                commander_name="Captain Smith",
            )
            assert operation is not None
            assert operation.operation_type == op_type


class TestOperationLifecycle:
    """Tests for operation lifecycle management"""

    def test_start_operation(self, joint_ops_manager):
        """Test starting an operation"""
        operation = joint_ops_manager.create_operation(
            name="Operation Thunder",
            operation_type=OperationType.RAID,
            lead_tenant_id="tenant-001",
            lead_agency_name="Metro PD",
            commander_name="Captain Smith",
        )

        success = joint_ops_manager.start_operation(operation.operation_id)
        assert success is True

        updated = joint_ops_manager.get_operation(operation.operation_id)
        assert updated.status == OperationStatus.ACTIVE

    def test_pause_operation(self, joint_ops_manager):
        """Test pausing an operation"""
        operation = joint_ops_manager.create_operation(
            name="Operation Thunder",
            operation_type=OperationType.RAID,
            lead_tenant_id="tenant-001",
            lead_agency_name="Metro PD",
            commander_name="Captain Smith",
        )
        joint_ops_manager.start_operation(operation.operation_id)

        success = joint_ops_manager.pause_operation(operation.operation_id)
        assert success is True

        updated = joint_ops_manager.get_operation(operation.operation_id)
        assert updated.status == OperationStatus.PAUSED

    def test_resume_operation(self, joint_ops_manager):
        """Test resuming an operation"""
        operation = joint_ops_manager.create_operation(
            name="Operation Thunder",
            operation_type=OperationType.RAID,
            lead_tenant_id="tenant-001",
            lead_agency_name="Metro PD",
            commander_name="Captain Smith",
        )
        joint_ops_manager.start_operation(operation.operation_id)
        joint_ops_manager.pause_operation(operation.operation_id)

        success = joint_ops_manager.resume_operation(operation.operation_id)
        assert success is True

        updated = joint_ops_manager.get_operation(operation.operation_id)
        assert updated.status == OperationStatus.ACTIVE

    def test_complete_operation(self, joint_ops_manager):
        """Test completing an operation"""
        operation = joint_ops_manager.create_operation(
            name="Operation Thunder",
            operation_type=OperationType.RAID,
            lead_tenant_id="tenant-001",
            lead_agency_name="Metro PD",
            commander_name="Captain Smith",
        )
        joint_ops_manager.start_operation(operation.operation_id)

        success = joint_ops_manager.complete_operation(operation.operation_id)
        assert success is True

        updated = joint_ops_manager.get_operation(operation.operation_id)
        assert updated.status == OperationStatus.COMPLETED

    def test_abort_operation(self, joint_ops_manager):
        """Test aborting an operation"""
        operation = joint_ops_manager.create_operation(
            name="Operation Thunder",
            operation_type=OperationType.RAID,
            lead_tenant_id="tenant-001",
            lead_agency_name="Metro PD",
            commander_name="Captain Smith",
        )
        joint_ops_manager.start_operation(operation.operation_id)

        success = joint_ops_manager.abort_operation(
            operation.operation_id, "Safety concerns"
        )
        assert success is True

        updated = joint_ops_manager.get_operation(operation.operation_id)
        assert updated.status == OperationStatus.ABORTED


class TestOperationRetrieval:
    """Tests for operation retrieval"""

    def test_get_operation(self, joint_ops_manager):
        """Test getting an operation by ID"""
        operation = joint_ops_manager.create_operation(
            name="Operation Thunder",
            operation_type=OperationType.RAID,
            lead_tenant_id="tenant-001",
            lead_agency_name="Metro PD",
            commander_name="Captain Smith",
        )

        retrieved = joint_ops_manager.get_operation(operation.operation_id)
        assert retrieved is not None
        assert retrieved.operation_id == operation.operation_id

    def test_get_all_operations(self, joint_ops_manager):
        """Test getting all operations"""
        for i in range(3):
            joint_ops_manager.create_operation(
                name=f"Operation {i}",
                operation_type=OperationType.RAID,
                lead_tenant_id="tenant-001",
                lead_agency_name="Metro PD",
                commander_name="Captain Smith",
            )

        operations = joint_ops_manager.get_all_operations()
        assert len(operations) == 3

    def test_get_active_operations(self, joint_ops_manager):
        """Test getting active operations"""
        op1 = joint_ops_manager.create_operation(
            name="Operation 1",
            operation_type=OperationType.RAID,
            lead_tenant_id="tenant-001",
            lead_agency_name="Metro PD",
            commander_name="Captain Smith",
        )
        op2 = joint_ops_manager.create_operation(
            name="Operation 2",
            operation_type=OperationType.RAID,
            lead_tenant_id="tenant-001",
            lead_agency_name="Metro PD",
            commander_name="Captain Smith",
        )

        joint_ops_manager.start_operation(op1.operation_id)

        active = joint_ops_manager.get_active_operations()
        assert len(active) == 1
        assert active[0].operation_id == op1.operation_id

    def test_get_operations_for_tenant(self, joint_ops_manager):
        """Test getting operations for a tenant"""
        operation = joint_ops_manager.create_operation(
            name="Operation Thunder",
            operation_type=OperationType.RAID,
            lead_tenant_id="tenant-001",
            lead_agency_name="Metro PD",
            commander_name="Captain Smith",
        )
        joint_ops_manager.add_agency(
            operation.operation_id, "tenant-002", "County SO", OperationRole.TEAM_LEADER
        )

        operations = joint_ops_manager.get_operations_for_tenant("tenant-002")
        assert len(operations) == 1


class TestAgencyManagement:
    """Tests for agency participation management"""

    def test_add_agency(self, joint_ops_manager):
        """Test adding an agency to an operation"""
        operation = joint_ops_manager.create_operation(
            name="Operation Thunder",
            operation_type=OperationType.RAID,
            lead_tenant_id="tenant-001",
            lead_agency_name="Metro PD",
            commander_name="Captain Smith",
        )

        success = joint_ops_manager.add_agency(
            operation.operation_id,
            "tenant-002",
            "County SO",
            OperationRole.TEAM_LEADER,
        )
        assert success is True

        updated = joint_ops_manager.get_operation(operation.operation_id)
        assert len(updated.participating_agencies) == 1
        assert updated.participating_agencies[0].tenant_id == "tenant-002"

    def test_remove_agency(self, joint_ops_manager):
        """Test removing an agency from an operation"""
        operation = joint_ops_manager.create_operation(
            name="Operation Thunder",
            operation_type=OperationType.RAID,
            lead_tenant_id="tenant-001",
            lead_agency_name="Metro PD",
            commander_name="Captain Smith",
        )
        joint_ops_manager.add_agency(
            operation.operation_id, "tenant-002", "County SO", OperationRole.TEAM_LEADER
        )

        success = joint_ops_manager.remove_agency(operation.operation_id, "tenant-002")
        assert success is True

        updated = joint_ops_manager.get_operation(operation.operation_id)
        assert len(updated.participating_agencies) == 0

    def test_assign_role(self, joint_ops_manager):
        """Test assigning a role to an agency"""
        operation = joint_ops_manager.create_operation(
            name="Operation Thunder",
            operation_type=OperationType.RAID,
            lead_tenant_id="tenant-001",
            lead_agency_name="Metro PD",
            commander_name="Captain Smith",
        )
        joint_ops_manager.add_agency(
            operation.operation_id, "tenant-002", "County SO", OperationRole.TEAM_LEADER
        )

        success = joint_ops_manager.assign_role(
            operation.operation_id, "tenant-002", OperationRole.OPERATIONS_CHIEF
        )
        assert success is True


class TestUnitDeployment:
    """Tests for unit deployment"""

    def test_deploy_unit(self, joint_ops_manager):
        """Test deploying a unit"""
        operation = joint_ops_manager.create_operation(
            name="Operation Thunder",
            operation_type=OperationType.RAID,
            lead_tenant_id="tenant-001",
            lead_agency_name="Metro PD",
            commander_name="Captain Smith",
        )

        unit = joint_ops_manager.deploy_unit(
            operation_id=operation.operation_id,
            tenant_id="tenant-001",
            agency_name="Metro PD",
            call_sign="SWAT-1",
            unit_type="swat",
            latitude=34.0522,
            longitude=-118.2437,
        )

        assert unit is not None
        assert unit.call_sign == "SWAT-1"
        assert unit.unit_type == "swat"

    def test_update_unit_position(self, joint_ops_manager):
        """Test updating unit position"""
        operation = joint_ops_manager.create_operation(
            name="Operation Thunder",
            operation_type=OperationType.RAID,
            lead_tenant_id="tenant-001",
            lead_agency_name="Metro PD",
            commander_name="Captain Smith",
        )
        unit = joint_ops_manager.deploy_unit(
            operation_id=operation.operation_id,
            tenant_id="tenant-001",
            agency_name="Metro PD",
            call_sign="SWAT-1",
            unit_type="swat",
            latitude=34.0522,
            longitude=-118.2437,
        )

        success = joint_ops_manager.update_unit_position(
            operation.operation_id, unit.unit_id, 34.0530, -118.2450
        )
        assert success is True

    def test_update_unit_status(self, joint_ops_manager):
        """Test updating unit status"""
        operation = joint_ops_manager.create_operation(
            name="Operation Thunder",
            operation_type=OperationType.RAID,
            lead_tenant_id="tenant-001",
            lead_agency_name="Metro PD",
            commander_name="Captain Smith",
        )
        unit = joint_ops_manager.deploy_unit(
            operation_id=operation.operation_id,
            tenant_id="tenant-001",
            agency_name="Metro PD",
            call_sign="SWAT-1",
            unit_type="swat",
            latitude=34.0522,
            longitude=-118.2437,
        )

        success = joint_ops_manager.update_unit_status(
            operation.operation_id, unit.unit_id, "in_position"
        )
        assert success is True

    def test_get_deployed_units(self, joint_ops_manager):
        """Test getting deployed units"""
        operation = joint_ops_manager.create_operation(
            name="Operation Thunder",
            operation_type=OperationType.RAID,
            lead_tenant_id="tenant-001",
            lead_agency_name="Metro PD",
            commander_name="Captain Smith",
        )

        for i in range(3):
            joint_ops_manager.deploy_unit(
                operation_id=operation.operation_id,
                tenant_id="tenant-001",
                agency_name="Metro PD",
                call_sign=f"UNIT-{i}",
                unit_type="patrol",
                latitude=34.0522 + i * 0.001,
                longitude=-118.2437,
            )

        units = joint_ops_manager.get_deployed_units(operation.operation_id)
        assert len(units) == 3


class TestObjectives:
    """Tests for operation objectives"""

    def test_add_objective(self, joint_ops_manager):
        """Test adding an objective"""
        operation = joint_ops_manager.create_operation(
            name="Operation Thunder",
            operation_type=OperationType.RAID,
            lead_tenant_id="tenant-001",
            lead_agency_name="Metro PD",
            commander_name="Captain Smith",
        )

        objective = joint_ops_manager.add_objective(
            operation_id=operation.operation_id,
            title="Secure perimeter",
            description="Establish perimeter around target location",
            priority=1,
        )

        assert objective is not None
        assert objective.title == "Secure perimeter"
        assert objective.priority == 1

    def test_complete_objective(self, joint_ops_manager):
        """Test completing an objective"""
        operation = joint_ops_manager.create_operation(
            name="Operation Thunder",
            operation_type=OperationType.RAID,
            lead_tenant_id="tenant-001",
            lead_agency_name="Metro PD",
            commander_name="Captain Smith",
        )
        objective = joint_ops_manager.add_objective(
            operation_id=operation.operation_id,
            title="Secure perimeter",
            description="Establish perimeter",
            priority=1,
        )

        success = joint_ops_manager.complete_objective(
            operation.operation_id, objective.objective_id
        )
        assert success is True

    def test_get_objectives(self, joint_ops_manager):
        """Test getting operation objectives"""
        operation = joint_ops_manager.create_operation(
            name="Operation Thunder",
            operation_type=OperationType.RAID,
            lead_tenant_id="tenant-001",
            lead_agency_name="Metro PD",
            commander_name="Captain Smith",
        )

        for i in range(3):
            joint_ops_manager.add_objective(
                operation_id=operation.operation_id,
                title=f"Objective {i}",
                description=f"Description {i}",
                priority=i + 1,
            )

        objectives = joint_ops_manager.get_objectives(operation.operation_id)
        assert len(objectives) == 3


class TestTimeline:
    """Tests for operation timeline"""

    def test_add_timeline_event(self, joint_ops_manager):
        """Test adding a timeline event"""
        operation = joint_ops_manager.create_operation(
            name="Operation Thunder",
            operation_type=OperationType.RAID,
            lead_tenant_id="tenant-001",
            lead_agency_name="Metro PD",
            commander_name="Captain Smith",
        )

        event = joint_ops_manager.add_timeline_event(
            operation_id=operation.operation_id,
            event_type=TimelineEventType.BRIEFING,
            title="Pre-operation briefing",
            description="All units briefed on operation plan",
            source_tenant_id="tenant-001",
            source_agency_name="Metro PD",
        )

        assert event is not None
        assert event.event_type == TimelineEventType.BRIEFING
        assert event.title == "Pre-operation briefing"

    def test_get_timeline(self, joint_ops_manager):
        """Test getting operation timeline"""
        operation = joint_ops_manager.create_operation(
            name="Operation Thunder",
            operation_type=OperationType.RAID,
            lead_tenant_id="tenant-001",
            lead_agency_name="Metro PD",
            commander_name="Captain Smith",
        )

        event_types = [
            TimelineEventType.BRIEFING,
            TimelineEventType.DEPLOYMENT,
            TimelineEventType.CONTACT,
        ]

        for i, event_type in enumerate(event_types):
            joint_ops_manager.add_timeline_event(
                operation_id=operation.operation_id,
                event_type=event_type,
                title=f"Event {i}",
                description=f"Description {i}",
                source_tenant_id="tenant-001",
                source_agency_name="Metro PD",
            )

        timeline = joint_ops_manager.get_timeline(operation.operation_id)
        assert len(timeline) == 3


class TestWhiteboard:
    """Tests for operation whiteboard"""

    def test_add_whiteboard_item(self, joint_ops_manager):
        """Test adding a whiteboard item"""
        operation = joint_ops_manager.create_operation(
            name="Operation Thunder",
            operation_type=OperationType.RAID,
            lead_tenant_id="tenant-001",
            lead_agency_name="Metro PD",
            commander_name="Captain Smith",
        )

        item = joint_ops_manager.add_whiteboard_item(
            operation_id=operation.operation_id,
            item_type=WhiteboardItemType.NOTE,
            content="Important note about target",
            author_tenant_id="tenant-001",
            author_name="Sgt. Johnson",
        )

        assert item is not None
        assert item.item_type == WhiteboardItemType.NOTE
        assert item.content == "Important note about target"

    def test_get_whiteboard(self, joint_ops_manager):
        """Test getting operation whiteboard"""
        operation = joint_ops_manager.create_operation(
            name="Operation Thunder",
            operation_type=OperationType.RAID,
            lead_tenant_id="tenant-001",
            lead_agency_name="Metro PD",
            commander_name="Captain Smith",
        )

        for i in range(3):
            joint_ops_manager.add_whiteboard_item(
                operation_id=operation.operation_id,
                item_type=WhiteboardItemType.NOTE,
                content=f"Note {i}",
                author_tenant_id="tenant-001",
                author_name="Sgt. Johnson",
            )

        whiteboard = joint_ops_manager.get_whiteboard(operation.operation_id)
        assert len(whiteboard) == 3


class TestMetrics:
    """Tests for joint ops metrics"""

    def test_get_metrics(self, joint_ops_manager):
        """Test getting joint ops metrics"""
        op1 = joint_ops_manager.create_operation(
            name="Operation 1",
            operation_type=OperationType.RAID,
            lead_tenant_id="tenant-001",
            lead_agency_name="Metro PD",
            commander_name="Captain Smith",
        )
        op2 = joint_ops_manager.create_operation(
            name="Operation 2",
            operation_type=OperationType.SURVEILLANCE,
            lead_tenant_id="tenant-001",
            lead_agency_name="Metro PD",
            commander_name="Captain Smith",
        )

        joint_ops_manager.start_operation(op1.operation_id)

        metrics = joint_ops_manager.get_metrics()
        assert metrics["total_operations"] == 2
        assert metrics["active_operations"] == 1
