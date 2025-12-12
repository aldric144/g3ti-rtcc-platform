"""
Phase 31: Response Coordination Engine Tests
"""

import pytest
from datetime import datetime
from backend.app.emergency_ai.response_coordination_engine import (
    ResponseCoordinationEngine,
    AgencyType,
    ResourceType,
    TaskPriority,
    TaskStatus,
    RouteStatus,
    AgencyTask,
    ResourceAllocation,
    EvacuationRoute,
    ShelterStatus,
    ResponsePlan,
)


class TestResponseCoordinationEngine:
    """Test suite for ResponseCoordinationEngine"""

    def setup_method(self):
        """Setup test fixtures"""
        self.engine = ResponseCoordinationEngine()

    def test_singleton_pattern(self):
        """Test that engine follows singleton pattern"""
        engine1 = ResponseCoordinationEngine()
        engine2 = ResponseCoordinationEngine()
        assert engine1 is engine2

    def test_agency_config(self):
        """Test agency configuration"""
        assert self.engine.agency_config["ori"] == "FL0500400"
        assert self.engine.agency_config["city"] == "Riviera Beach"

    def test_shelters_configuration(self):
        """Test shelters configuration"""
        assert len(self.engine.shelters) == 5
        
        shelter_names = [s["name"] for s in self.engine.shelters]
        assert "Riviera Beach Community Center" in shelter_names
        assert "Marina Event Center" in shelter_names

    def test_evacuation_routes_configuration(self):
        """Test evacuation routes configuration"""
        assert len(self.engine.evacuation_routes) == 4
        
        route_names = [r["name"] for r in self.engine.evacuation_routes]
        assert "Blue Heron Blvd West" in route_names

    def test_available_resources(self):
        """Test available resources"""
        resources = self.engine.available_resources
        assert resources[ResourceType.PATROL_UNITS] == 25
        assert resources[ResourceType.FIRE_ENGINES] == 8
        assert resources[ResourceType.EVACUATION_BUSES] == 15

    def test_create_agency_task(self):
        """Test creating agency task"""
        task = self.engine.create_agency_task(
            agency_type=AgencyType.POLICE,
            priority=TaskPriority.HIGH,
            description="Secure evacuation route",
            location_zone="Zone_A",
        )
        
        assert task is not None
        assert task.task_id.startswith("AT-")
        assert task.agency_type == AgencyType.POLICE
        assert task.priority == TaskPriority.HIGH
        assert task.status == TaskStatus.PENDING
        assert task.chain_of_custody_hash is not None

    def test_allocate_resources(self):
        """Test resource allocation"""
        allocation = self.engine.allocate_resources(
            resource_type=ResourceType.PATROL_UNITS,
            quantity=5,
            zone="Zone_B",
            task_id="TEST-001",
        )
        
        assert allocation is not None
        assert allocation.allocation_id.startswith("RA-")
        assert allocation.resource_type == ResourceType.PATROL_UNITS
        assert allocation.assigned_zone == "Zone_B"
        assert allocation.chain_of_custody_hash is not None

    def test_plan_evacuation_route(self):
        """Test evacuation route planning"""
        route = self.engine.plan_evacuation_route(
            origin_zone="Zone_A",
            destination_type="shelter",
        )
        
        assert route is not None
        assert route.route_id.startswith("ER-")
        assert route.origin_zone == "Zone_A"
        assert route.destination_type == "shelter"
        assert route.distance_miles > 0
        assert route.estimated_time_minutes > 0
        assert route.chain_of_custody_hash is not None

    def test_plan_evacuation_route_special_needs(self):
        """Test evacuation route planning with special needs"""
        route = self.engine.plan_evacuation_route(
            origin_zone="Zone_E",
            destination_type="shelter",
            special_needs=True,
        )
        
        assert route is not None
        assert route.special_needs_accessible == True

    def test_coordinate_multi_agency_response(self):
        """Test multi-agency response coordination"""
        plan = self.engine.coordinate_multi_agency_response(
            incident_type="hurricane",
            threat_level=4,
            affected_zones=["Zone_A", "Zone_B"],
        )
        
        assert plan is not None
        assert plan.plan_id.startswith("RP-")
        assert plan.incident_type == "hurricane"
        assert plan.threat_level == 4
        assert len(plan.agency_tasks) > 0
        assert len(plan.resource_allocations) > 0
        assert plan.total_resources_deployed > 0
        assert plan.chain_of_custody_hash is not None

    def test_coordinate_response_high_threat(self):
        """Test response coordination for high threat level"""
        plan = self.engine.coordinate_multi_agency_response(
            incident_type="hurricane",
            threat_level=5,
            affected_zones=["Zone_A", "Zone_B", "Zone_C"],
        )
        
        agency_types = [task.agency_type for task in plan.agency_tasks]
        assert AgencyType.NATIONAL_GUARD in agency_types or len(plan.agency_tasks) > 5

    def test_get_resource_status(self):
        """Test getting resource status"""
        status = self.engine.get_resource_status()
        
        assert "available_resources" in status
        assert "total_shelter_capacity" in status
        assert "total_shelter_occupancy" in status
        assert "shelters" in status

    def test_get_shelter_status(self):
        """Test getting shelter status"""
        shelters = self.engine.get_shelter_status()
        
        assert len(shelters) == 5
        for shelter in shelters:
            assert "shelter_id" in shelter
            assert "name" in shelter
            assert "capacity" in shelter
            assert "current_occupancy" in shelter

    def test_agency_type_enum(self):
        """Test agency type enumeration"""
        assert AgencyType.POLICE.value == "police"
        assert AgencyType.FIRE_RESCUE.value == "fire_rescue"
        assert AgencyType.EMS.value == "ems"
        assert AgencyType.RED_CROSS.value == "red_cross"

    def test_resource_type_enum(self):
        """Test resource type enumeration"""
        assert ResourceType.PATROL_UNITS.value == "patrol_units"
        assert ResourceType.FIRE_ENGINES.value == "fire_engines"
        assert ResourceType.EVACUATION_BUSES.value == "evacuation_buses"

    def test_task_priority_enum(self):
        """Test task priority enumeration"""
        assert TaskPriority.CRITICAL.value == 5
        assert TaskPriority.HIGH.value == 4
        assert TaskPriority.MEDIUM.value == 3
        assert TaskPriority.LOW.value == 2
        assert TaskPriority.ROUTINE.value == 1

    def test_route_status_enum(self):
        """Test route status enumeration"""
        assert RouteStatus.OPEN.value == "open"
        assert RouteStatus.CONGESTED.value == "congested"
        assert RouteStatus.BLOCKED.value == "blocked"
        assert RouteStatus.FLOODED.value == "flooded"

    def test_chain_of_custody_hash_format(self):
        """Test chain of custody hash format"""
        task = self.engine.create_agency_task(
            agency_type=AgencyType.FIRE_RESCUE,
            priority=TaskPriority.MEDIUM,
            description="Test task",
            location_zone="Zone_C",
        )
        assert len(task.chain_of_custody_hash) == 64
        assert all(c in "0123456789abcdef" for c in task.chain_of_custody_hash)

    def test_statistics_tracking(self):
        """Test statistics tracking"""
        initial_stats = self.engine.get_statistics()
        
        self.engine.create_agency_task(
            agency_type=AgencyType.EMS,
            priority=TaskPriority.HIGH,
            description="Test",
            location_zone="Zone_D",
        )
        
        updated_stats = self.engine.get_statistics()
        assert updated_stats["total_tasks_created"] >= initial_stats["total_tasks_created"]
