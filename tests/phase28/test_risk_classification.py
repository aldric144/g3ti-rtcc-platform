"""
Test Suite 9: Risk Classification Tests

Tests for use-of-force risk classification algorithms.
"""

import pytest
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend', 'app'))

from officer_assist.use_of_force_monitor import (
    UseOfForceRiskMonitor,
    RiskLevel,
    SuspectBehaviorClass,
    SceneEscalationPattern,
    WeaponType,
    OfficerVitals,
    SceneContext,
)


class TestRiskLevelClassification:
    """Tests for risk level classification"""
    
    def setup_method(self):
        """Reset singleton for each test"""
        UseOfForceRiskMonitor._instance = None
        self.monitor = UseOfForceRiskMonitor()
    
    def test_green_level_threshold(self):
        """Test green level threshold (0.0 - 0.3)"""
        assessment = self.monitor.assess_risk(
            incident_id="INC-001",
            officer_id="RBPD-201",
            suspect_behavior=SuspectBehaviorClass.COMPLIANT,
            escalation_pattern=SceneEscalationPattern.STABLE,
        )
        
        assert assessment.risk_level == RiskLevel.GREEN
        assert assessment.risk_score < 0.3
    
    def test_yellow_level_threshold(self):
        """Test yellow level threshold (0.3 - 0.7)"""
        assessment = self.monitor.assess_risk(
            incident_id="INC-002",
            officer_id="RBPD-201",
            suspect_behavior=SuspectBehaviorClass.ACTIVE_RESISTANT,
            escalation_pattern=SceneEscalationPattern.SLOWLY_ESCALATING,
        )
        
        assert assessment.risk_level == RiskLevel.YELLOW
        assert 0.3 <= assessment.risk_score <= 0.7
    
    def test_red_level_threshold(self):
        """Test red level threshold (0.7 - 1.0)"""
        assessment = self.monitor.assess_risk(
            incident_id="INC-003",
            officer_id="RBPD-201",
            suspect_behavior=SuspectBehaviorClass.ASSAULTIVE,
            escalation_pattern=SceneEscalationPattern.RAPIDLY_ESCALATING,
            weapon_type=WeaponType.FIREARM,
            weapon_probability=0.8,
        )
        
        assert assessment.risk_level == RiskLevel.RED
        assert assessment.risk_score > 0.7


class TestSuspectBehaviorWeighting:
    """Tests for suspect behavior weighting in risk calculation"""
    
    def setup_method(self):
        """Reset singleton for each test"""
        UseOfForceRiskMonitor._instance = None
        self.monitor = UseOfForceRiskMonitor()
    
    def test_compliant_behavior_low_weight(self):
        """Test compliant behavior has low weight"""
        assessment = self.monitor.assess_risk(
            incident_id="INC-001",
            officer_id="RBPD-201",
            suspect_behavior=SuspectBehaviorClass.COMPLIANT,
        )
        
        assert assessment.risk_score < 0.2
    
    def test_passive_resistant_moderate_weight(self):
        """Test passive resistant has moderate weight"""
        assessment = self.monitor.assess_risk(
            incident_id="INC-002",
            officer_id="RBPD-201",
            suspect_behavior=SuspectBehaviorClass.PASSIVE_RESISTANT,
        )
        
        assert 0.1 <= assessment.risk_score <= 0.4
    
    def test_active_resistant_higher_weight(self):
        """Test active resistant has higher weight"""
        assessment = self.monitor.assess_risk(
            incident_id="INC-003",
            officer_id="RBPD-201",
            suspect_behavior=SuspectBehaviorClass.ACTIVE_RESISTANT,
        )
        
        assert assessment.risk_score >= 0.3
    
    def test_aggressive_high_weight(self):
        """Test aggressive has high weight"""
        assessment = self.monitor.assess_risk(
            incident_id="INC-004",
            officer_id="RBPD-201",
            suspect_behavior=SuspectBehaviorClass.AGGRESSIVE,
        )
        
        assert assessment.risk_score >= 0.4
    
    def test_assaultive_very_high_weight(self):
        """Test assaultive has very high weight"""
        assessment = self.monitor.assess_risk(
            incident_id="INC-005",
            officer_id="RBPD-201",
            suspect_behavior=SuspectBehaviorClass.ASSAULTIVE,
        )
        
        assert assessment.risk_score >= 0.6
    
    def test_life_threatening_maximum_weight(self):
        """Test life threatening has maximum weight"""
        assessment = self.monitor.assess_risk(
            incident_id="INC-006",
            officer_id="RBPD-201",
            suspect_behavior=SuspectBehaviorClass.LIFE_THREATENING,
        )
        
        assert assessment.risk_score >= 0.8
        assert assessment.risk_level == RiskLevel.RED


class TestEscalationPatternWeighting:
    """Tests for escalation pattern weighting"""
    
    def setup_method(self):
        """Reset singleton for each test"""
        UseOfForceRiskMonitor._instance = None
        self.monitor = UseOfForceRiskMonitor()
    
    def test_de_escalating_reduces_risk(self):
        """Test de-escalating pattern reduces risk"""
        assessment = self.monitor.assess_risk(
            incident_id="INC-001",
            officer_id="RBPD-201",
            suspect_behavior=SuspectBehaviorClass.ACTIVE_RESISTANT,
            escalation_pattern=SceneEscalationPattern.DE_ESCALATING,
        )
        
        assert "de-escalating" in " ".join(assessment.protective_factors).lower()
    
    def test_stable_neutral_weight(self):
        """Test stable pattern has neutral weight"""
        assessment = self.monitor.assess_risk(
            incident_id="INC-002",
            officer_id="RBPD-201",
            suspect_behavior=SuspectBehaviorClass.PASSIVE_RESISTANT,
            escalation_pattern=SceneEscalationPattern.STABLE,
        )
        
        assert assessment.risk_level == RiskLevel.GREEN
    
    def test_slowly_escalating_increases_risk(self):
        """Test slowly escalating increases risk"""
        assessment = self.monitor.assess_risk(
            incident_id="INC-003",
            officer_id="RBPD-201",
            suspect_behavior=SuspectBehaviorClass.ACTIVE_RESISTANT,
            escalation_pattern=SceneEscalationPattern.SLOWLY_ESCALATING,
        )
        
        assert assessment.risk_level in [RiskLevel.YELLOW, RiskLevel.RED]
    
    def test_rapidly_escalating_high_risk(self):
        """Test rapidly escalating is high risk"""
        assessment = self.monitor.assess_risk(
            incident_id="INC-004",
            officer_id="RBPD-201",
            suspect_behavior=SuspectBehaviorClass.AGGRESSIVE,
            escalation_pattern=SceneEscalationPattern.RAPIDLY_ESCALATING,
        )
        
        assert assessment.risk_level == RiskLevel.RED
    
    def test_critical_escalation_maximum_risk(self):
        """Test critical escalation is maximum risk"""
        assessment = self.monitor.assess_risk(
            incident_id="INC-005",
            officer_id="RBPD-201",
            suspect_behavior=SuspectBehaviorClass.AGGRESSIVE,
            escalation_pattern=SceneEscalationPattern.CRITICAL,
        )
        
        assert assessment.risk_level == RiskLevel.RED
        assert assessment.risk_score >= 0.8


class TestWeaponRiskWeighting:
    """Tests for weapon risk weighting"""
    
    def setup_method(self):
        """Reset singleton for each test"""
        UseOfForceRiskMonitor._instance = None
        self.monitor = UseOfForceRiskMonitor()
    
    def test_no_weapon_no_additional_risk(self):
        """Test no weapon adds no additional risk"""
        assessment = self.monitor.assess_risk(
            incident_id="INC-001",
            officer_id="RBPD-201",
            suspect_behavior=SuspectBehaviorClass.ACTIVE_RESISTANT,
            weapon_type=WeaponType.NONE,
        )
        
        assert not assessment.weapon_detected
    
    def test_blunt_object_moderate_risk(self):
        """Test blunt object adds moderate risk"""
        assessment = self.monitor.assess_risk(
            incident_id="INC-002",
            officer_id="RBPD-201",
            suspect_behavior=SuspectBehaviorClass.AGGRESSIVE,
            weapon_type=WeaponType.BLUNT_OBJECT,
            weapon_probability=0.8,
        )
        
        assert assessment.weapon_detected
    
    def test_edged_weapon_high_risk(self):
        """Test edged weapon adds high risk"""
        assessment = self.monitor.assess_risk(
            incident_id="INC-003",
            officer_id="RBPD-201",
            suspect_behavior=SuspectBehaviorClass.AGGRESSIVE,
            weapon_type=WeaponType.EDGED_WEAPON,
            weapon_probability=0.8,
        )
        
        assert assessment.weapon_detected
        assert assessment.risk_level in [RiskLevel.YELLOW, RiskLevel.RED]
    
    def test_firearm_maximum_risk(self):
        """Test firearm adds maximum risk"""
        assessment = self.monitor.assess_risk(
            incident_id="INC-004",
            officer_id="RBPD-201",
            suspect_behavior=SuspectBehaviorClass.AGGRESSIVE,
            weapon_type=WeaponType.FIREARM,
            weapon_probability=0.9,
        )
        
        assert assessment.weapon_detected
        assert assessment.risk_level == RiskLevel.RED
    
    def test_weapon_probability_affects_risk(self):
        """Test weapon probability affects risk calculation"""
        assessment_low_prob = self.monitor.assess_risk(
            incident_id="INC-005",
            officer_id="RBPD-201",
            suspect_behavior=SuspectBehaviorClass.AGGRESSIVE,
            weapon_type=WeaponType.FIREARM,
            weapon_probability=0.3,
        )
        
        UseOfForceRiskMonitor._instance = None
        monitor2 = UseOfForceRiskMonitor()
        
        assessment_high_prob = monitor2.assess_risk(
            incident_id="INC-006",
            officer_id="RBPD-201",
            suspect_behavior=SuspectBehaviorClass.AGGRESSIVE,
            weapon_type=WeaponType.FIREARM,
            weapon_probability=0.9,
        )
        
        assert assessment_high_prob.risk_score >= assessment_low_prob.risk_score


class TestProximityRiskWeighting:
    """Tests for officer proximity risk weighting"""
    
    def setup_method(self):
        """Reset singleton for each test"""
        UseOfForceRiskMonitor._instance = None
        self.monitor = UseOfForceRiskMonitor()
    
    def test_danger_zone_under_21_feet(self):
        """Test danger zone under 21 feet increases risk"""
        assessment = self.monitor.assess_risk(
            incident_id="INC-001",
            officer_id="RBPD-201",
            suspect_behavior=SuspectBehaviorClass.ACTIVE_RESISTANT,
            officer_proximity_feet=15,
        )
        
        assert "danger zone" in " ".join(assessment.risk_factors).lower()
    
    def test_caution_zone_21_to_50_feet(self):
        """Test caution zone 21-50 feet"""
        assessment = self.monitor.assess_risk(
            incident_id="INC-002",
            officer_id="RBPD-201",
            suspect_behavior=SuspectBehaviorClass.ACTIVE_RESISTANT,
            officer_proximity_feet=35,
        )
        
        assert "caution zone" in " ".join(assessment.risk_factors).lower()
    
    def test_safe_distance_over_50_feet(self):
        """Test safe distance over 50 feet is protective"""
        assessment = self.monitor.assess_risk(
            incident_id="INC-003",
            officer_id="RBPD-201",
            suspect_behavior=SuspectBehaviorClass.ACTIVE_RESISTANT,
            officer_proximity_feet=100,
        )
        
        assert "safe distance" in " ".join(assessment.protective_factors).lower()


class TestVitalsRiskWeighting:
    """Tests for officer vitals risk weighting"""
    
    def setup_method(self):
        """Reset singleton for each test"""
        UseOfForceRiskMonitor._instance = None
        self.monitor = UseOfForceRiskMonitor()
    
    def test_elevated_heart_rate_increases_risk(self):
        """Test elevated heart rate increases risk"""
        vitals = OfficerVitals(
            heart_rate=160,
            stress_index=0.5,
        )
        
        assessment = self.monitor.assess_risk(
            incident_id="INC-001",
            officer_id="RBPD-201",
            suspect_behavior=SuspectBehaviorClass.ACTIVE_RESISTANT,
            officer_vitals=vitals,
        )
        
        assert "heart rate" in " ".join(assessment.risk_factors).lower()
    
    def test_high_stress_index_increases_risk(self):
        """Test high stress index increases risk"""
        vitals = OfficerVitals(
            heart_rate=100,
            stress_index=0.85,
        )
        
        assessment = self.monitor.assess_risk(
            incident_id="INC-002",
            officer_id="RBPD-201",
            suspect_behavior=SuspectBehaviorClass.ACTIVE_RESISTANT,
            officer_vitals=vitals,
        )
        
        assert "stress" in " ".join(assessment.risk_factors).lower()


class TestSceneContextRiskWeighting:
    """Tests for scene context risk weighting"""
    
    def setup_method(self):
        """Reset singleton for each test"""
        UseOfForceRiskMonitor._instance = None
        self.monitor = UseOfForceRiskMonitor()
    
    def test_outnumbered_officer_increases_risk(self):
        """Test outnumbered officer increases risk"""
        scene = SceneContext(
            incident_id="INC-001",
            officer_id="RBPD-201",
            officer_count=1,
            suspect_count=3,
        )
        
        assessment = self.monitor.assess_risk(
            incident_id="INC-001",
            officer_id="RBPD-201",
            suspect_behavior=SuspectBehaviorClass.ACTIVE_RESISTANT,
            scene_context=scene,
        )
        
        assert "outnumbered" in " ".join(assessment.risk_factors).lower()
    
    def test_confined_space_increases_risk(self):
        """Test confined space increases risk"""
        scene = SceneContext(
            incident_id="INC-002",
            officer_id="RBPD-201",
            confined_space=True,
        )
        
        assessment = self.monitor.assess_risk(
            incident_id="INC-002",
            officer_id="RBPD-201",
            suspect_behavior=SuspectBehaviorClass.ACTIVE_RESISTANT,
            scene_context=scene,
        )
        
        assert "confined" in " ".join(assessment.risk_factors).lower()
    
    def test_backup_arriving_protective_factor(self):
        """Test backup arriving is protective factor"""
        scene = SceneContext(
            incident_id="INC-003",
            officer_id="RBPD-201",
            backup_eta_minutes=2.0,
        )
        
        assessment = self.monitor.assess_risk(
            incident_id="INC-003",
            officer_id="RBPD-201",
            suspect_behavior=SuspectBehaviorClass.ACTIVE_RESISTANT,
            scene_context=scene,
        )
        
        assert "backup" in " ".join(assessment.protective_factors).lower()
