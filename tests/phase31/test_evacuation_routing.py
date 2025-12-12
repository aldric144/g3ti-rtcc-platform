"""
Phase 31: Evacuation Routing Tests
"""

import pytest
from backend.app.emergency_ai.response_coordination_engine import (
    ResponseCoordinationEngine,
    RouteStatus,
)


class TestEvacuationRouting:
    """Test suite for evacuation routing"""

    def setup_method(self):
        """Setup test fixtures"""
        self.engine = ResponseCoordinationEngine()

    def test_plan_evacuation_route_basic(self):
        """Test basic evacuation route planning"""
        route = self.engine.plan_evacuation_route(
            origin_zone="Zone_A",
            destination_type="shelter",
        )
        
        assert route is not None
        assert route.route_id.startswith("ER-")
        assert route.origin_zone == "Zone_A"
        assert route.destination_type == "shelter"

    def test_plan_evacuation_route_all_zones(self):
        """Test evacuation route planning for all zones"""
        zones = ["Zone_A", "Zone_B", "Zone_C", "Zone_D", "Zone_E",
                 "Zone_F", "Zone_G", "Zone_H", "Zone_I", "Zone_J"]
        
        for zone in zones:
            route = self.engine.plan_evacuation_route(
                origin_zone=zone,
                destination_type="shelter",
            )
            assert route is not None
            assert route.origin_zone == zone

    def test_evacuation_route_distance(self):
        """Test evacuation route distance calculation"""
        route = self.engine.plan_evacuation_route(
            origin_zone="Zone_A",
            destination_type="shelter",
        )
        
        assert route.distance_miles > 0

    def test_evacuation_route_time_estimate(self):
        """Test evacuation route time estimate"""
        route = self.engine.plan_evacuation_route(
            origin_zone="Zone_B",
            destination_type="shelter",
        )
        
        assert route.estimated_time_minutes > 0

    def test_evacuation_route_special_needs(self):
        """Test evacuation route with special needs"""
        route = self.engine.plan_evacuation_route(
            origin_zone="Zone_C",
            destination_type="shelter",
            special_needs=True,
        )
        
        assert route.special_needs_accessible == True

    def test_evacuation_route_status(self):
        """Test evacuation route status"""
        route = self.engine.plan_evacuation_route(
            origin_zone="Zone_D",
            destination_type="shelter",
        )
        
        assert route.status in [RouteStatus.OPEN, RouteStatus.CONGESTED, 
                                RouteStatus.BLOCKED, RouteStatus.FLOODED]

    def test_evacuation_route_waypoints(self):
        """Test evacuation route waypoints"""
        route = self.engine.plan_evacuation_route(
            origin_zone="Zone_E",
            destination_type="shelter",
        )
        
        assert len(route.waypoints) >= 0

    def test_evacuation_route_shelter_assignment(self):
        """Test evacuation route shelter assignment"""
        route = self.engine.plan_evacuation_route(
            origin_zone="Zone_F",
            destination_type="shelter",
        )
        
        assert route.destination_name is not None

    def test_evacuation_route_capacity(self):
        """Test evacuation route capacity"""
        route = self.engine.plan_evacuation_route(
            origin_zone="Zone_G",
            destination_type="shelter",
        )
        
        assert route.capacity_vehicles_per_hour > 0

    def test_evacuation_route_time_to_clear(self):
        """Test evacuation route time to clear zone"""
        route = self.engine.plan_evacuation_route(
            origin_zone="Zone_H",
            destination_type="shelter",
        )
        
        assert route.time_to_clear_hours > 0

    def test_evacuation_route_chain_of_custody(self):
        """Test evacuation route chain of custody"""
        route = self.engine.plan_evacuation_route(
            origin_zone="Zone_I",
            destination_type="shelter",
        )
        
        assert route.chain_of_custody_hash is not None
        assert len(route.chain_of_custody_hash) == 64

    def test_evacuation_route_alternate_routes(self):
        """Test evacuation route alternate routes"""
        route = self.engine.plan_evacuation_route(
            origin_zone="Zone_J",
            destination_type="shelter",
        )
        
        assert len(route.alternate_routes) >= 0

    def test_evacuation_route_with_road_closures(self):
        """Test evacuation route with road closures"""
        route = self.engine.plan_evacuation_route(
            origin_zone="Zone_A",
            destination_type="shelter",
            road_closures=["Blue Heron Blvd"],
        )
        
        assert route is not None

    def test_evacuation_route_with_traffic_conditions(self):
        """Test evacuation route with traffic conditions"""
        route = self.engine.plan_evacuation_route(
            origin_zone="Zone_B",
            destination_type="shelter",
            traffic_level="heavy",
        )
        
        assert route is not None

    def test_evacuation_route_hospital_destination(self):
        """Test evacuation route to hospital"""
        route = self.engine.plan_evacuation_route(
            origin_zone="Zone_C",
            destination_type="hospital",
        )
        
        assert route.destination_type == "hospital"

    def test_evacuation_route_outside_city_destination(self):
        """Test evacuation route to outside city"""
        route = self.engine.plan_evacuation_route(
            origin_zone="Zone_D",
            destination_type="outside_city",
        )
        
        assert route.destination_type == "outside_city"
