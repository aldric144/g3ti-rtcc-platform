"""
Phase 21: Multi-Incident Command Tests

Tests for incident room management, AI briefing,
task assignment, timeline sync, and EOC coordination.
"""

import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch

import sys
sys.path.insert(0, '/home/ubuntu/repos/g3ti-rtcc-platform/backend')

from app.emergency.multi_incident_command import (
    IncidentRoomManager,
    AIIncidentBriefBuilder,
    TaskAssignmentEngine,
    TimelineSync,
    MultiAgencyEOCCoordinator,
    MultiIncidentCommandManager,
    IncidentStatus,
    IncidentPriority,
    TaskStatus,
    TaskPriority,
    AgencyType,
)


class TestIncidentRoomManager:
    """Tests for IncidentRoomManager class."""

    def test_manager_initialization(self):
        """Test IncidentRoomManager initializes correctly."""
        manager = IncidentRoomManager()
        assert manager is not None
        assert hasattr(manager, '_rooms')

    def test_create_room(self):
        """Test creating an incident room."""
        manager = IncidentRoomManager()
        room = manager.create_room(
            incident_name="Hurricane Response",
            incident_type="hurricane",
            priority=IncidentPriority.CRITICAL,
            location={"lat": 25.7617, "lng": -80.1918, "address": "Miami, FL"},
            commander="Chief Smith",
            affected_population=150000,
        )
        
        assert room is not None
        assert room.incident_name == "Hurricane Response"
        assert room.priority == IncidentPriority.CRITICAL
        assert room.status == IncidentStatus.ACTIVE

    def test_update_room_status(self):
        """Test updating room status."""
        manager = IncidentRoomManager()
        room = manager.create_room(
            incident_name="Flood Response",
            incident_type="flood",
            priority=IncidentPriority.HIGH,
            location={"lat": 29.7604, "lng": -95.3698},
            commander="Chief Johnson",
        )
        
        updated = manager.update_status(room.room_id, IncidentStatus.CONTAINED)
        assert updated is not None
        assert updated.status == IncidentStatus.CONTAINED

    def test_add_agency_to_room(self):
        """Test adding agency to room."""
        manager = IncidentRoomManager()
        room = manager.create_room(
            incident_name="Fire Response",
            incident_type="fire",
            priority=IncidentPriority.HIGH,
            location={"lat": 34.0522, "lng": -118.2437},
            commander="Chief Williams",
        )
        
        updated = manager.add_agency(room.room_id, "Fire Department")
        assert "Fire Department" in updated.agencies_involved

    def test_update_casualties(self):
        """Test updating casualties."""
        manager = IncidentRoomManager()
        room = manager.create_room(
            incident_name="Explosion Response",
            incident_type="explosion",
            priority=IncidentPriority.CRITICAL,
            location={"lat": 40.7128, "lng": -74.0060},
            commander="Chief Brown",
        )
        
        updated = manager.update_casualties(
            room.room_id,
            fatalities=5,
            injuries=20,
            missing=10,
        )
        
        assert updated is not None
        assert updated.casualties["fatalities"] == 5

    def test_get_active_rooms(self):
        """Test getting active rooms."""
        manager = IncidentRoomManager()
        manager.create_room(
            incident_name="Active Incident",
            incident_type="storm",
            priority=IncidentPriority.MEDIUM,
            location={"lat": 25.0, "lng": -80.0},
            commander="Chief Davis",
        )
        
        active = manager.get_active_rooms()
        assert len(active) >= 1


class TestAIIncidentBriefBuilder:
    """Tests for AIIncidentBriefBuilder class."""

    def test_builder_initialization(self):
        """Test AIIncidentBriefBuilder initializes correctly."""
        builder = AIIncidentBriefBuilder()
        assert builder is not None

    def test_generate_brief(self):
        """Test generating incident brief."""
        builder = AIIncidentBriefBuilder()
        brief = builder.generate_brief(
            room_id="room-001",
            incident_name="Hurricane Alpha",
            incident_type="hurricane",
            current_status="active",
            affected_population=100000,
            casualties={"fatalities": 0, "injuries": 10, "missing": 5},
            resources_deployed=50,
            key_actions=["Evacuation in progress", "Shelters opened"],
        )
        
        assert brief is not None
        assert hasattr(brief, 'brief_id')
        assert hasattr(brief, 'summary')
        assert hasattr(brief, 'recommendations')

    def test_update_brief(self):
        """Test updating brief."""
        builder = AIIncidentBriefBuilder()
        brief = builder.generate_brief(
            room_id="room-002",
            incident_name="Flood Event",
            incident_type="flood",
            current_status="active",
            affected_population=50000,
        )
        
        updated = builder.update_brief(
            brief.brief_id,
            new_developments=["Water levels rising", "Additional evacuations ordered"],
        )
        
        assert updated is not None


class TestTaskAssignmentEngine:
    """Tests for TaskAssignmentEngine class."""

    def test_engine_initialization(self):
        """Test TaskAssignmentEngine initializes correctly."""
        engine = TaskAssignmentEngine()
        assert engine is not None
        assert hasattr(engine, '_tasks')

    def test_create_task(self):
        """Test creating a task."""
        engine = TaskAssignmentEngine()
        task = engine.create_task(
            room_id="room-001",
            title="Establish evacuation routes",
            description="Set up and mark evacuation routes for Zone A",
            priority=TaskPriority.HIGH,
            assigned_to="Officer Smith",
            assigned_agency="Police Department",
        )
        
        assert task is not None
        assert task.title == "Establish evacuation routes"
        assert task.priority == TaskPriority.HIGH
        assert task.status == TaskStatus.ASSIGNED

    def test_update_task_status(self):
        """Test updating task status."""
        engine = TaskAssignmentEngine()
        task = engine.create_task(
            room_id="room-001",
            title="Set up shelter",
            priority=TaskPriority.MEDIUM,
            assigned_to="Team Alpha",
            assigned_agency="Red Cross",
        )
        
        updated = engine.update_status(task.task_id, TaskStatus.IN_PROGRESS)
        assert updated is not None
        assert updated.status == TaskStatus.IN_PROGRESS

    def test_complete_task(self):
        """Test completing a task."""
        engine = TaskAssignmentEngine()
        task = engine.create_task(
            room_id="room-001",
            title="Deploy medical team",
            priority=TaskPriority.HIGH,
            assigned_to="Medical Team 1",
            assigned_agency="EMS",
        )
        
        completed = engine.complete_task(task.task_id)
        assert completed is not None
        assert completed.status == TaskStatus.COMPLETED

    def test_get_tasks_by_room(self):
        """Test getting tasks by room."""
        engine = TaskAssignmentEngine()
        engine.create_task(
            room_id="room-002",
            title="Task 1",
            priority=TaskPriority.LOW,
            assigned_to="Person A",
            assigned_agency="Agency A",
        )
        
        tasks = engine.get_tasks_by_room("room-002")
        assert len(tasks) >= 1

    def test_get_tasks_by_agency(self):
        """Test getting tasks by agency."""
        engine = TaskAssignmentEngine()
        engine.create_task(
            room_id="room-003",
            title="Fire suppression",
            priority=TaskPriority.CRITICAL,
            assigned_to="Engine 1",
            assigned_agency="Fire Department",
        )
        
        tasks = engine.get_tasks_by_agency("Fire Department")
        assert len(tasks) >= 1


class TestTimelineSync:
    """Tests for TimelineSync class."""

    def test_sync_initialization(self):
        """Test TimelineSync initializes correctly."""
        sync = TimelineSync()
        assert sync is not None
        assert hasattr(sync, '_events')

    def test_add_event(self):
        """Test adding timeline event."""
        sync = TimelineSync()
        event = sync.add_event(
            room_id="room-001",
            event_type="status_update",
            title="Evacuation Started",
            description="Evacuation of Zone A has begun",
            source="Incident Commander",
        )
        
        assert event is not None
        assert event.title == "Evacuation Started"
        assert hasattr(event, 'timestamp')

    def test_get_timeline(self):
        """Test getting timeline for room."""
        sync = TimelineSync()
        sync.add_event(
            room_id="room-002",
            event_type="resource_deployed",
            title="Medical Team Deployed",
            description="Medical team deployed to shelter",
            source="Operations",
        )
        
        timeline = sync.get_timeline("room-002")
        assert len(timeline) >= 1

    def test_get_recent_events(self):
        """Test getting recent events."""
        sync = TimelineSync()
        sync.add_event(
            room_id="room-003",
            event_type="alert",
            title="Weather Update",
            description="Storm intensifying",
            source="Weather Service",
        )
        
        recent = sync.get_recent_events(hours=1)
        assert isinstance(recent, list)


class TestMultiAgencyEOCCoordinator:
    """Tests for MultiAgencyEOCCoordinator class."""

    def test_coordinator_initialization(self):
        """Test MultiAgencyEOCCoordinator initializes correctly."""
        coordinator = MultiAgencyEOCCoordinator()
        assert coordinator is not None
        assert hasattr(coordinator, '_agencies')
        assert hasattr(coordinator, '_eocs')

    def test_register_agency(self):
        """Test registering an agency."""
        coordinator = MultiAgencyEOCCoordinator()
        agency = coordinator.register_agency(
            name="Miami-Dade Fire Rescue",
            agency_type=AgencyType.FIRE,
            contact="Chief Martinez",
            contact_phone="555-1234",
        )
        
        assert agency is not None
        assert agency.name == "Miami-Dade Fire Rescue"
        assert agency.agency_type == AgencyType.FIRE

    def test_activate_eoc(self):
        """Test activating EOC."""
        coordinator = MultiAgencyEOCCoordinator()
        eoc = coordinator.activate_eoc(
            name="Miami-Dade EOC",
            activation_level=3,
            agencies_present=["Fire", "Police", "EMS", "Public Works"],
            personnel_on_duty=50,
        )
        
        assert eoc is not None
        assert eoc.activation_level == 3
        assert eoc.status == "active"

    def test_update_eoc_level(self):
        """Test updating EOC activation level."""
        coordinator = MultiAgencyEOCCoordinator()
        eoc = coordinator.activate_eoc(
            name="County EOC",
            activation_level=2,
            agencies_present=["Fire", "Police"],
            personnel_on_duty=25,
        )
        
        updated = coordinator.update_eoc_level(eoc.eoc_id, 3)
        assert updated is not None
        assert updated.activation_level == 3

    def test_get_eoc_status(self):
        """Test getting EOC status."""
        coordinator = MultiAgencyEOCCoordinator()
        eoc = coordinator.activate_eoc(
            name="State EOC",
            activation_level=1,
            agencies_present=["Emergency Management"],
            personnel_on_duty=10,
        )
        
        status = coordinator.get_eoc_status(eoc.eoc_id)
        assert status is not None


class TestMultiIncidentCommandManager:
    """Tests for MultiIncidentCommandManager class."""

    def test_manager_initialization(self):
        """Test MultiIncidentCommandManager initializes correctly."""
        manager = MultiIncidentCommandManager()
        assert manager is not None
        assert hasattr(manager, 'room_manager')
        assert hasattr(manager, 'brief_builder')
        assert hasattr(manager, 'task_engine')
        assert hasattr(manager, 'timeline_sync')
        assert hasattr(manager, 'eoc_coordinator')

    def test_get_command_metrics(self):
        """Test getting command metrics."""
        manager = MultiIncidentCommandManager()
        metrics = manager.get_metrics()
        
        assert metrics is not None
        assert "active_incidents" in metrics
        assert "total_tasks" in metrics
        assert "agencies_involved" in metrics

    def test_get_command_summary(self):
        """Test getting command summary."""
        manager = MultiIncidentCommandManager()
        summary = manager.get_summary()
        
        assert summary is not None
        assert "active_incidents" in summary
        assert "critical_incidents" in summary
        assert "total_affected_population" in summary
        assert "total_casualties" in summary

    def test_coordinate_incident(self):
        """Test coordinating an incident."""
        manager = MultiIncidentCommandManager()
        result = manager.coordinate_incident(
            incident_name="Major Fire",
            incident_type="fire",
            priority="critical",
            location={"lat": 34.0522, "lng": -118.2437},
            commander="Chief Anderson",
        )
        
        assert result is not None
