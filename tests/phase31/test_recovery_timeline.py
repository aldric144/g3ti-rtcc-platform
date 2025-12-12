"""
Phase 31: Recovery Timeline Tests
"""

import pytest
from backend.app.emergency_ai.recovery_planner import (
    RecoveryPlanner,
    RecoveryPhase,
)


class TestRecoveryTimeline:
    """Test suite for recovery timeline estimation"""

    def setup_method(self):
        """Setup test fixtures"""
        self.planner = RecoveryPlanner()

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

    def test_recovery_phases(self):
        """Test recovery phases are defined"""
        assessment = self.planner.assess_zone_damage(
            zone="Zone_B",
            incident_type="hurricane",
            severity_factor=0.5,
        )
        
        timeline = self.planner.estimate_recovery_timeline(
            zone="Zone_B",
            incident_type="hurricane",
            damage_assessment=assessment,
        )
        
        assert timeline.immediate_phase_days > 0
        assert timeline.short_term_phase_days > 0
        assert timeline.intermediate_phase_days > 0
        assert timeline.long_term_phase_days > 0

    def test_total_recovery_days(self):
        """Test total recovery days calculation"""
        assessment = self.planner.assess_zone_damage(
            zone="Zone_C",
            incident_type="hurricane",
            severity_factor=0.5,
        )
        
        timeline = self.planner.estimate_recovery_timeline(
            zone="Zone_C",
            incident_type="hurricane",
            damage_assessment=assessment,
        )
        
        expected_total = (
            timeline.immediate_phase_days +
            timeline.short_term_phase_days +
            timeline.intermediate_phase_days +
            timeline.long_term_phase_days
        )
        
        assert timeline.total_recovery_days == expected_total

    def test_recovery_milestones(self):
        """Test recovery milestones"""
        assessment = self.planner.assess_zone_damage(
            zone="Zone_D",
            incident_type="hurricane",
            severity_factor=0.5,
        )
        
        timeline = self.planner.estimate_recovery_timeline(
            zone="Zone_D",
            incident_type="hurricane",
            damage_assessment=assessment,
        )
        
        assert len(timeline.milestones) > 0

    def test_recovery_timeline_severity_impact(self):
        """Test severity impact on recovery timeline"""
        assessment_low = self.planner.assess_zone_damage(
            zone="Zone_E",
            incident_type="hurricane",
            severity_factor=0.2,
        )
        
        assessment_high = self.planner.assess_zone_damage(
            zone="Zone_E",
            incident_type="hurricane",
            severity_factor=0.8,
        )
        
        timeline_low = self.planner.estimate_recovery_timeline(
            zone="Zone_E",
            incident_type="hurricane",
            damage_assessment=assessment_low,
        )
        
        timeline_high = self.planner.estimate_recovery_timeline(
            zone="Zone_E",
            incident_type="hurricane",
            damage_assessment=assessment_high,
        )
        
        assert timeline_high.total_recovery_days >= timeline_low.total_recovery_days

    def test_recovery_plan_timeline(self):
        """Test recovery plan includes timeline"""
        plan = self.planner.create_recovery_plan(
            incident_type="hurricane",
            affected_zones=["Zone_F"],
            severity_factor=0.5,
        )
        
        assert plan.recovery_timeline_days > 0

    def test_recovery_plan_multiple_zones(self):
        """Test recovery plan for multiple zones"""
        plan = self.planner.create_recovery_plan(
            incident_type="hurricane",
            affected_zones=["Zone_G", "Zone_H", "Zone_I"],
            severity_factor=0.5,
        )
        
        assert len(plan.damage_assessments) == 3
        assert plan.recovery_timeline_days > 0

    def test_recovery_phase_enum(self):
        """Test recovery phase enumeration"""
        assert RecoveryPhase.IMMEDIATE.value == "immediate"
        assert RecoveryPhase.SHORT_TERM.value == "short_term"
        assert RecoveryPhase.INTERMEDIATE.value == "intermediate"
        assert RecoveryPhase.LONG_TERM.value == "long_term"

    def test_recovery_plan_cost_estimates(self):
        """Test recovery plan cost estimates"""
        plan = self.planner.create_recovery_plan(
            incident_type="hurricane",
            affected_zones=["Zone_J"],
            severity_factor=0.5,
        )
        
        assert plan.total_estimated_cost > 0
        assert plan.federal_assistance_estimate > 0
        assert plan.state_assistance_estimate > 0
        assert plan.local_cost_share > 0

    def test_recovery_plan_economic_impact(self):
        """Test recovery plan economic impact"""
        plan = self.planner.create_recovery_plan(
            incident_type="hurricane",
            affected_zones=["Zone_A", "Zone_B"],
            severity_factor=0.6,
        )
        
        assert plan.economic_impact_estimate > 0
        assert plan.population_affected > 0
        assert plan.housing_units_damaged >= 0
        assert plan.businesses_affected >= 0
        assert plan.jobs_impacted >= 0

    def test_recovery_plan_infrastructure_repairs(self):
        """Test recovery plan infrastructure repairs"""
        plan = self.planner.create_recovery_plan(
            incident_type="hurricane",
            affected_zones=["Zone_C"],
            severity_factor=0.5,
        )
        
        assert len(plan.infrastructure_repairs) >= 0

    def test_recovery_plan_chain_of_custody(self):
        """Test recovery plan chain of custody"""
        plan = self.planner.create_recovery_plan(
            incident_type="flooding",
            affected_zones=["Zone_D"],
            severity_factor=0.4,
        )
        
        assert plan.chain_of_custody_hash is not None
        assert len(plan.chain_of_custody_hash) == 64
