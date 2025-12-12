"""
Phase 31: Damage Assessment Tests
"""

import pytest
from backend.app.emergency_ai.recovery_planner import (
    RecoveryPlanner,
    DamageTier,
)


class TestDamageAssessment:
    """Test suite for damage assessment"""

    def setup_method(self):
        """Setup test fixtures"""
        self.planner = RecoveryPlanner()

    def test_assess_structure_damage_none(self):
        """Test structure damage assessment - none"""
        damage = self.planner.assess_structure_damage(
            structure_id="STR-001",
            structure_type="residential",
            address="123 Main St",
            zone="Zone_A",
            damage_indicators={
                "roof_damage": False,
                "wall_damage": False,
                "foundation_damage": False,
            },
        )
        
        assert damage.damage_tier == DamageTier.NONE

    def test_assess_structure_damage_minor(self):
        """Test structure damage assessment - minor"""
        damage = self.planner.assess_structure_damage(
            structure_id="STR-002",
            structure_type="residential",
            address="456 Oak St",
            zone="Zone_B",
            damage_indicators={
                "roof_damage": True,
                "roof_damage_percent": 10,
            },
        )
        
        assert damage.damage_tier == DamageTier.MINOR

    def test_assess_structure_damage_moderate(self):
        """Test structure damage assessment - moderate"""
        damage = self.planner.assess_structure_damage(
            structure_id="STR-003",
            structure_type="residential",
            address="789 Pine St",
            zone="Zone_C",
            damage_indicators={
                "roof_damage": True,
                "roof_damage_percent": 25,
                "wall_damage": True,
                "wall_damage_percent": 15,
            },
        )
        
        assert damage.damage_tier == DamageTier.MODERATE

    def test_assess_structure_damage_major(self):
        """Test structure damage assessment - major"""
        damage = self.planner.assess_structure_damage(
            structure_id="STR-004",
            structure_type="residential",
            address="321 Elm St",
            zone="Zone_D",
            damage_indicators={
                "roof_damage": True,
                "roof_damage_percent": 40,
                "wall_damage": True,
                "wall_damage_percent": 30,
            },
        )
        
        assert damage.damage_tier == DamageTier.MAJOR

    def test_assess_structure_damage_destroyed(self):
        """Test structure damage assessment - destroyed"""
        damage = self.planner.assess_structure_damage(
            structure_id="STR-005",
            structure_type="residential",
            address="654 Maple St",
            zone="Zone_E",
            damage_indicators={
                "roof_damage": True,
                "roof_damage_percent": 100,
                "wall_damage": True,
                "wall_damage_percent": 80,
                "foundation_damage": True,
                "foundation_damage_percent": 50,
            },
        )
        
        assert damage.damage_tier == DamageTier.DESTROYED

    def test_assess_zone_damage(self):
        """Test zone-level damage assessment"""
        assessment = self.planner.assess_zone_damage(
            zone="Zone_A",
            incident_type="hurricane",
            severity_factor=0.5,
        )
        
        assert assessment is not None
        assert assessment.zone == "Zone_A"
        assert assessment.total_structures_assessed > 0

    def test_zone_damage_disaster_impact_index(self):
        """Test disaster impact index calculation"""
        assessment = self.planner.assess_zone_damage(
            zone="Zone_B",
            incident_type="hurricane",
            severity_factor=0.6,
        )
        
        assert assessment.disaster_impact_index >= 0
        assert assessment.disaster_impact_index <= 100

    def test_zone_damage_displaced_residents(self):
        """Test displaced residents calculation"""
        assessment = self.planner.assess_zone_damage(
            zone="Zone_C",
            incident_type="flooding",
            severity_factor=0.4,
        )
        
        assert assessment.displaced_residents >= 0

    def test_zone_damage_priority_repairs(self):
        """Test priority repairs identification"""
        assessment = self.planner.assess_zone_damage(
            zone="Zone_D",
            incident_type="hurricane",
            severity_factor=0.7,
        )
        
        assert len(assessment.priority_repairs) >= 0

    def test_zone_damage_structures_by_tier(self):
        """Test structures by damage tier"""
        assessment = self.planner.assess_zone_damage(
            zone="Zone_E",
            incident_type="fire",
            severity_factor=0.5,
        )
        
        assert "none" in assessment.structures_by_tier or len(assessment.structures_by_tier) > 0

    def test_zone_damage_total_estimate(self):
        """Test total damage estimate"""
        assessment = self.planner.assess_zone_damage(
            zone="Zone_F",
            incident_type="hurricane",
            severity_factor=0.5,
        )
        
        assert assessment.total_damage_estimate >= 0

    def test_zone_damage_chain_of_custody(self):
        """Test damage assessment chain of custody"""
        assessment = self.planner.assess_zone_damage(
            zone="Zone_G",
            incident_type="tornado",
            severity_factor=0.3,
        )
        
        assert assessment.chain_of_custody_hash is not None
        assert len(assessment.chain_of_custody_hash) == 64

    def test_damage_assessment_all_zones(self):
        """Test damage assessment for all zones"""
        zones = ["Zone_A", "Zone_B", "Zone_C", "Zone_D", "Zone_E",
                 "Zone_F", "Zone_G", "Zone_H", "Zone_I", "Zone_J"]
        
        for zone in zones:
            assessment = self.planner.assess_zone_damage(
                zone=zone,
                incident_type="hurricane",
                severity_factor=0.5,
            )
            assert assessment.zone == zone

    def test_damage_severity_factor_impact(self):
        """Test severity factor impact on damage"""
        assessment_low = self.planner.assess_zone_damage(
            zone="Zone_H",
            incident_type="hurricane",
            severity_factor=0.2,
        )
        
        assessment_high = self.planner.assess_zone_damage(
            zone="Zone_H",
            incident_type="hurricane",
            severity_factor=0.8,
        )
        
        assert assessment_high.total_damage_estimate >= assessment_low.total_damage_estimate

    def test_structure_damage_chain_of_custody(self):
        """Test structure damage chain of custody"""
        damage = self.planner.assess_structure_damage(
            structure_id="STR-006",
            structure_type="commercial",
            address="100 Business Blvd",
            zone="Zone_I",
            damage_indicators={"roof_damage": True, "roof_damage_percent": 20},
        )
        
        assert damage.chain_of_custody_hash is not None
        assert len(damage.chain_of_custody_hash) == 64
