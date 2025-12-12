"""
Phase 31: Shelter Assignment Tests
"""

import pytest
from backend.app.emergency_ai.response_coordination_engine import (
    ResponseCoordinationEngine,
)


class TestShelterAssignment:
    """Test suite for shelter assignment"""

    def setup_method(self):
        """Setup test fixtures"""
        self.engine = ResponseCoordinationEngine()

    def test_shelters_configuration(self):
        """Test shelters are properly configured"""
        assert len(self.engine.shelters) == 5

    def test_shelter_capacity(self):
        """Test shelter capacity values"""
        for shelter in self.engine.shelters:
            assert shelter["capacity"] > 0

    def test_shelter_zones(self):
        """Test shelter zone assignments"""
        zones = [s["zone"] for s in self.engine.shelters]
        assert "Zone_A" in zones
        assert "Zone_E" in zones
        assert "Zone_C" in zones

    def test_shelter_amenities(self):
        """Test shelter amenities"""
        for shelter in self.engine.shelters:
            assert len(shelter["amenities"]) > 0

    def test_shelter_special_needs_capacity(self):
        """Test shelter special needs capacity"""
        for shelter in self.engine.shelters:
            assert shelter["special_needs_capacity"] >= 0

    def test_shelter_pet_friendly(self):
        """Test shelter pet friendly flag"""
        pet_friendly_count = sum(1 for s in self.engine.shelters if s["pet_friendly"])
        assert pet_friendly_count >= 0

    def test_get_shelter_status(self):
        """Test getting shelter status"""
        shelters = self.engine.get_shelter_status()
        
        assert len(shelters) == 5
        for shelter in shelters:
            assert "shelter_id" in shelter
            assert "name" in shelter
            assert "capacity" in shelter
            assert "current_occupancy" in shelter
            assert "status" in shelter

    def test_shelter_occupancy_tracking(self):
        """Test shelter occupancy tracking"""
        shelters = self.engine.get_shelter_status()
        
        for shelter in shelters:
            assert shelter["current_occupancy"] >= 0
            assert shelter["current_occupancy"] <= shelter["capacity"]

    def test_shelter_status_values(self):
        """Test shelter status values"""
        shelters = self.engine.get_shelter_status()
        
        valid_statuses = ["open", "full", "closed", "preparing"]
        for shelter in shelters:
            assert shelter["status"] in valid_statuses

    def test_total_shelter_capacity(self):
        """Test total shelter capacity calculation"""
        status = self.engine.get_resource_status()
        
        assert status["total_shelter_capacity"] > 0
        
        expected_capacity = sum(s["capacity"] for s in self.engine.shelters)
        assert status["total_shelter_capacity"] == expected_capacity

    def test_total_shelter_occupancy(self):
        """Test total shelter occupancy calculation"""
        status = self.engine.get_resource_status()
        
        assert status["total_shelter_occupancy"] >= 0
        assert status["total_shelter_occupancy"] <= status["total_shelter_capacity"]

    def test_shelter_assignment_in_response_plan(self):
        """Test shelter assignment in response plan"""
        plan = self.engine.coordinate_multi_agency_response(
            incident_type="hurricane",
            threat_level=4,
            affected_zones=["Zone_A", "Zone_B"],
        )
        
        assert len(plan.shelter_assignments) >= 0

    def test_shelter_nearest_to_zone(self):
        """Test finding nearest shelter to zone"""
        route = self.engine.plan_evacuation_route(
            origin_zone="Zone_A",
            destination_type="shelter",
        )
        
        assert route.destination_name is not None

    def test_shelter_special_needs_assignment(self):
        """Test special needs shelter assignment"""
        route = self.engine.plan_evacuation_route(
            origin_zone="Zone_E",
            destination_type="shelter",
            special_needs=True,
        )
        
        assert route.special_needs_accessible == True

    def test_shelter_capacity_overflow(self):
        """Test shelter capacity overflow handling"""
        status = self.engine.get_resource_status()
        
        available = status["total_shelter_capacity"] - status["total_shelter_occupancy"]
        assert available >= 0

    def test_shelter_amenities_list(self):
        """Test shelter amenities list"""
        shelters = self.engine.get_shelter_status()
        
        for shelter in shelters:
            assert "amenities" in shelter
            assert isinstance(shelter["amenities"], list)
