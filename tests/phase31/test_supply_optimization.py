"""
Phase 31: Supply Optimization Tests
"""

import pytest
from backend.app.emergency_ai.recovery_planner import (
    RecoveryPlanner,
    SupplyType,
)


class TestSupplyOptimization:
    """Test suite for supply optimization"""

    def setup_method(self):
        """Setup test fixtures"""
        self.planner = RecoveryPlanner()

    def test_optimize_water_allocation(self):
        """Test water supply allocation"""
        allocation = self.planner.optimize_supply_allocation(
            zone="Zone_A",
            supply_type=SupplyType.WATER,
            population_served=1000,
            days_needed=3.0,
        )
        
        assert allocation is not None
        assert allocation.supply_type == SupplyType.WATER
        assert allocation.quantity > 0

    def test_optimize_food_allocation(self):
        """Test food supply allocation"""
        allocation = self.planner.optimize_supply_allocation(
            zone="Zone_B",
            supply_type=SupplyType.FOOD,
            population_served=1500,
            days_needed=5.0,
        )
        
        assert allocation.supply_type == SupplyType.FOOD
        assert allocation.quantity > 0

    def test_optimize_medical_allocation(self):
        """Test medical supply allocation"""
        allocation = self.planner.optimize_supply_allocation(
            zone="Zone_C",
            supply_type=SupplyType.MEDICAL,
            population_served=500,
            days_needed=7.0,
        )
        
        assert allocation.supply_type == SupplyType.MEDICAL
        assert allocation.quantity > 0

    def test_optimize_generator_allocation(self):
        """Test generator allocation"""
        allocation = self.planner.optimize_supply_allocation(
            zone="Zone_D",
            supply_type=SupplyType.GENERATOR,
            population_served=2000,
            days_needed=10.0,
        )
        
        assert allocation.supply_type == SupplyType.GENERATOR
        assert allocation.quantity > 0

    def test_optimize_fuel_allocation(self):
        """Test fuel allocation"""
        allocation = self.planner.optimize_supply_allocation(
            zone="Zone_E",
            supply_type=SupplyType.FUEL,
            population_served=1000,
            days_needed=5.0,
        )
        
        assert allocation.supply_type == SupplyType.FUEL
        assert allocation.quantity > 0

    def test_optimize_shelter_kit_allocation(self):
        """Test shelter kit allocation"""
        allocation = self.planner.optimize_supply_allocation(
            zone="Zone_F",
            supply_type=SupplyType.SHELTER_KIT,
            population_served=500,
            days_needed=14.0,
        )
        
        assert allocation.supply_type == SupplyType.SHELTER_KIT
        assert allocation.quantity > 0

    def test_supply_allocation_cost(self):
        """Test supply allocation cost calculation"""
        allocation = self.planner.optimize_supply_allocation(
            zone="Zone_G",
            supply_type=SupplyType.WATER,
            population_served=1000,
            days_needed=3.0,
        )
        
        assert allocation.estimated_cost > 0

    def test_supply_allocation_source(self):
        """Test supply allocation source assignment"""
        allocation = self.planner.optimize_supply_allocation(
            zone="Zone_H",
            supply_type=SupplyType.FOOD,
            population_served=1000,
            days_needed=3.0,
        )
        
        assert allocation.source_location is not None

    def test_supply_allocation_delivery_time(self):
        """Test supply allocation delivery time"""
        allocation = self.planner.optimize_supply_allocation(
            zone="Zone_I",
            supply_type=SupplyType.MEDICAL,
            population_served=500,
            days_needed=5.0,
        )
        
        assert allocation.estimated_delivery_hours > 0

    def test_supply_allocation_chain_of_custody(self):
        """Test supply allocation chain of custody"""
        allocation = self.planner.optimize_supply_allocation(
            zone="Zone_J",
            supply_type=SupplyType.WATER,
            population_served=1000,
            days_needed=3.0,
        )
        
        assert allocation.chain_of_custody_hash is not None
        assert len(allocation.chain_of_custody_hash) == 64

    def test_supply_quantity_scales_with_population(self):
        """Test supply quantity scales with population"""
        allocation_small = self.planner.optimize_supply_allocation(
            zone="Zone_A",
            supply_type=SupplyType.WATER,
            population_served=500,
            days_needed=3.0,
        )
        
        allocation_large = self.planner.optimize_supply_allocation(
            zone="Zone_A",
            supply_type=SupplyType.WATER,
            population_served=2000,
            days_needed=3.0,
        )
        
        assert allocation_large.quantity > allocation_small.quantity

    def test_supply_quantity_scales_with_days(self):
        """Test supply quantity scales with days needed"""
        allocation_short = self.planner.optimize_supply_allocation(
            zone="Zone_B",
            supply_type=SupplyType.FOOD,
            population_served=1000,
            days_needed=2.0,
        )
        
        allocation_long = self.planner.optimize_supply_allocation(
            zone="Zone_B",
            supply_type=SupplyType.FOOD,
            population_served=1000,
            days_needed=7.0,
        )
        
        assert allocation_long.quantity > allocation_short.quantity

    def test_supply_sources_configuration(self):
        """Test supply sources are configured"""
        assert len(self.planner.supply_sources) == 4

    def test_supply_source_names(self):
        """Test supply source names"""
        source_names = [s["name"] for s in self.planner.supply_sources]
        assert "Palm Beach County EOC" in source_names
        assert "FEMA Distribution Center" in source_names

    def test_all_supply_types(self):
        """Test all supply types can be allocated"""
        supply_types = [
            SupplyType.FOOD, SupplyType.WATER, SupplyType.MEDICAL,
            SupplyType.GENERATOR, SupplyType.FUEL, SupplyType.SHELTER_KIT,
            SupplyType.HYGIENE_KIT, SupplyType.BLANKETS, SupplyType.TARPS,
            SupplyType.TOOLS,
        ]
        
        for supply_type in supply_types:
            allocation = self.planner.optimize_supply_allocation(
                zone="Zone_A",
                supply_type=supply_type,
                population_served=1000,
                days_needed=3.0,
            )
            assert allocation.supply_type == supply_type
