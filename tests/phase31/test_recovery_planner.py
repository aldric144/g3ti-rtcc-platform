"""
Phase 31: Recovery Planner Tests
"""

import pytest
from datetime import datetime
from backend.app.emergency_ai.recovery_planner import (
    RecoveryPlanner,
    DamageTier,
    RecoveryPhase,
    FEMACategory,
    SupplyType,
    InfrastructureType,
    StructureDamage,
    DamageAssessment,
    SupplyAllocation,
    InfrastructureRepair,
    RecoveryTimeline,
    RecoveryPlan,
)


class TestRecoveryPlanner:
    """Test suite for RecoveryPlanner"""

    def setup_method(self):
        """Setup test fixtures"""
        self.planner = RecoveryPlanner()

    def test_singleton_pattern(self):
        """Test that planner follows singleton pattern"""
        planner1 = RecoveryPlanner()
        planner2 = RecoveryPlanner()
        assert planner1 is planner2

    def test_agency_config(self):
        """Test agency configuration"""
        assert self.planner.agency_config["ori"] == "FL0500400"
        assert self.planner.agency_config["city"] == "Riviera Beach"
        assert self.planner.agency_config["county"] == "Palm Beach"

    def test_zone_populations(self):
        """Test zone population data"""
        assert self.planner.zone_populations["Zone_A"] == 3500
        assert self.planner.zone_populations["Zone_E"] == 4500

    def test_zone_structures(self):
        """Test zone structure data"""
        assert self.planner.zone_structures["Zone_A"] == 1200
        assert self.planner.zone_structures["Zone_E"] == 1600

    def test_supply_sources(self):
        """Test supply sources configuration"""
        assert len(self.planner.supply_sources) == 4
        source_names = [s["name"] for s in self.planner.supply_sources]
        assert "Palm Beach County EOC" in source_names
        assert "FEMA Distribution Center" in source_names

    def test_assess_structure_damage(self):
        """Test structure damage assessment"""
        damage = self.planner.assess_structure_damage(
            structure_id="STR-001",
            structure_type="residential",
            address="123 Main St",
            zone="Zone_A",
            damage_indicators={
                "roof_damage": True,
                "roof_damage_percent": 30,
                "wall_damage": True,
                "wall_damage_percent": 20,
            },
        )
        
        assert damage is not None
        assert damage.assessment_id.startswith("SD-")
        assert damage.structure_id == "STR-001"
        assert damage.damage_percent == 50
        assert damage.damage_tier == DamageTier.MAJOR
        assert damage.chain_of_custody_hash is not None

    def test_assess_zone_damage(self):
        """Test zone-level damage assessment"""
        assessment = self.planner.assess_zone_damage(
            zone="Zone_A",
            incident_type="hurricane",
            severity_factor=0.5,
        )
        
        assert assessment is not None
        assert assessment.assessment_id.startswith("DA-")
        assert assessment.zone == "Zone_A"
        assert assessment.total_structures_assessed > 0
        assert assessment.disaster_impact_index >= 0
        assert assessment.chain_of_custody_hash is not None

    def test_optimize_supply_allocation(self):
        """Test supply allocation optimization"""
        allocation = self.planner.optimize_supply_allocation(
            zone="Zone_B",
            supply_type=SupplyType.WATER,
            population_served=1000,
            days_needed=3.0,
        )
        
        assert allocation is not None
        assert allocation.allocation_id.startswith("SA-")
        assert allocation.supply_type == SupplyType.WATER
        assert allocation.destination_zone == "Zone_B"
        assert allocation.quantity > 0
        assert allocation.chain_of_custody_hash is not None

    def test_plan_infrastructure_repair(self):
        """Test infrastructure repair planning"""
        repair = self.planner.plan_infrastructure_repair(
            infrastructure_type=InfrastructureType.BRIDGE,
            infrastructure_name="Test Bridge",
            zone="Zone_C",
            damage_description="Major structural damage",
            priority=1,
        )
        
        assert repair is not None
        assert repair.repair_id.startswith("IR-")
        assert repair.infrastructure_type == InfrastructureType.BRIDGE
        assert repair.estimated_cost > 0
        assert repair.estimated_days > 0
        assert repair.fema_category == FEMACategory.CATEGORY_C
        assert repair.chain_of_custody_hash is not None

    def test_estimate_recovery_timeline(self):
        """Test recovery timeline estimation"""
        assessment = self.planner.assess_zone_damage(
            zone="Zone_A",
            incident_type="hurricane",
            severity_factor=0.5,
        )
        
        timeline = self.planner.estimate_recovery_timeline(
            zone="Zone_A",
            incident_type="hurricane",
            damage_assessment=assessment,
        )
        
        assert timeline is not None
        assert timeline.timeline_id.startswith("RT-")
        assert timeline.immediate_phase_days > 0
        assert timeline.short_term_phase_days > 0
        assert timeline.total_recovery_days > 0
        assert len(timeline.milestones) > 0

    def test_create_recovery_plan(self):
        """Test comprehensive recovery plan creation"""
        plan = self.planner.create_recovery_plan(
            incident_type="hurricane",
            affected_zones=["Zone_A", "Zone_B"],
            severity_factor=0.5,
        )
        
        assert plan is not None
        assert plan.plan_id.startswith("RP-")
        assert plan.incident_type == "hurricane"
        assert len(plan.affected_zones) == 2
        assert len(plan.damage_assessments) == 2
        assert len(plan.supply_allocations) > 0
        assert plan.total_estimated_cost > 0
        assert plan.federal_assistance_estimate > 0
        assert plan.chain_of_custody_hash is not None

    def test_fema_cost_sharing(self):
        """Test FEMA cost sharing calculations"""
        plan = self.planner.create_recovery_plan(
            incident_type="hurricane",
            affected_zones=["Zone_A"],
            severity_factor=0.5,
        )
        
        total = plan.total_estimated_cost
        federal = plan.federal_assistance_estimate
        state = plan.state_assistance_estimate
        local = plan.local_cost_share
        
        assert abs(federal - total * 0.75) < 1
        assert abs(state - total * 0.125) < 1
        assert abs(local - total * 0.125) < 1

    def test_damage_tier_enum(self):
        """Test damage tier enumeration"""
        assert DamageTier.NONE.value == 0
        assert DamageTier.MINOR.value == 1
        assert DamageTier.MODERATE.value == 2
        assert DamageTier.MAJOR.value == 3
        assert DamageTier.DESTROYED.value == 4

    def test_fema_category_enum(self):
        """Test FEMA category enumeration"""
        assert FEMACategory.CATEGORY_A.value == "debris_removal"
        assert FEMACategory.CATEGORY_B.value == "emergency_protective_measures"
        assert FEMACategory.CATEGORY_C.value == "roads_bridges"

    def test_supply_type_enum(self):
        """Test supply type enumeration"""
        assert SupplyType.FOOD.value == "food"
        assert SupplyType.WATER.value == "water"
        assert SupplyType.MEDICAL.value == "medical"
        assert SupplyType.GENERATOR.value == "generator"

    def test_infrastructure_type_enum(self):
        """Test infrastructure type enumeration"""
        assert InfrastructureType.ROAD.value == "road"
        assert InfrastructureType.BRIDGE.value == "bridge"
        assert InfrastructureType.POWER_LINE.value == "power_line"

    def test_chain_of_custody_hash_format(self):
        """Test chain of custody hash format"""
        plan = self.planner.create_recovery_plan(
            incident_type="flooding",
            affected_zones=["Zone_E"],
            severity_factor=0.3,
        )
        assert len(plan.chain_of_custody_hash) == 64
        assert all(c in "0123456789abcdef" for c in plan.chain_of_custody_hash)

    def test_statistics_tracking(self):
        """Test statistics tracking"""
        initial_stats = self.planner.get_statistics()
        
        self.planner.create_recovery_plan(
            incident_type="fire",
            affected_zones=["Zone_C"],
            severity_factor=0.4,
        )
        
        updated_stats = self.planner.get_statistics()
        assert updated_stats["total_recovery_plans"] >= initial_stats["total_recovery_plans"]
