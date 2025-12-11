"""
Test Suite 2: Use-of-Force Risk Monitor Tests

Tests for risk classification, escalation patterns, and supervisor notifications.
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
    ForceRiskAssessment,
)


class TestUseOfForceRiskMonitor:
    """Tests for Use-of-Force Risk Monitor"""
    
    def setup_method(self):
        """Reset singleton for each test"""
        UseOfForceRiskMonitor._instance = None
        self.monitor = UseOfForceRiskMonitor()
    
    def test_singleton_pattern(self):
        """Test that monitor uses singleton pattern"""
        monitor1 = UseOfForceRiskMonitor()
        monitor2 = UseOfForceRiskMonitor()
        assert monitor1 is monitor2
    
    def test_agency_configuration(self):
        """Test agency configuration is correct"""
        assert self.monitor.agency_config["ori"] == "FL0500400"
        assert self.monitor.agency_config["name"] == "Riviera Beach Police Department"
    
    def test_compliant_suspect_green_risk(self):
        """Test compliant suspect results in green risk level"""
        assessment = self.monitor.assess_risk(
            incident_id="INC-001",
            officer_id="RBPD-201",
            suspect_behavior=SuspectBehaviorClass.COMPLIANT,
        )
        
        assert assessment.risk_level == RiskLevel.GREEN
        assert assessment.risk_score < 0.3
    
    def test_active_resistant_yellow_risk(self):
        """Test active resistant suspect results in yellow risk"""
        assessment = self.monitor.assess_risk(
            incident_id="INC-002",
            officer_id="RBPD-201",
            suspect_behavior=SuspectBehaviorClass.ACTIVE_RESISTANT,
        )
        
        assert assessment.risk_level == RiskLevel.YELLOW
        assert 0.3 <= assessment.risk_score <= 0.7
    
    def test_assaultive_suspect_red_risk(self):
        """Test assaultive suspect results in red risk"""
        assessment = self.monitor.assess_risk(
            incident_id="INC-003",
            officer_id="RBPD-201",
            suspect_behavior=SuspectBehaviorClass.ASSAULTIVE,
            escalation_pattern=SceneEscalationPattern.RAPIDLY_ESCALATING,
        )
        
        assert assessment.risk_level == RiskLevel.RED
        assert assessment.risk_score > 0.7
    
    def test_life_threatening_suspect_red_risk(self):
        """Test life-threatening suspect results in red risk"""
        assessment = self.monitor.assess_risk(
            incident_id="INC-004",
            officer_id="RBPD-201",
            suspect_behavior=SuspectBehaviorClass.LIFE_THREATENING,
        )
        
        assert assessment.risk_level == RiskLevel.RED
        assert assessment.supervisor_notified
    
    def test_weapon_detection_increases_risk(self):
        """Test weapon detection increases risk score"""
        assessment_no_weapon = self.monitor.assess_risk(
            incident_id="INC-005",
            officer_id="RBPD-201",
            suspect_behavior=SuspectBehaviorClass.AGGRESSIVE,
            weapon_type=WeaponType.NONE,
        )
        
        UseOfForceRiskMonitor._instance = None
        monitor2 = UseOfForceRiskMonitor()
        
        assessment_with_weapon = monitor2.assess_risk(
            incident_id="INC-006",
            officer_id="RBPD-201",
            suspect_behavior=SuspectBehaviorClass.AGGRESSIVE,
            weapon_type=WeaponType.FIREARM,
            weapon_probability=0.8,
        )
        
        assert assessment_with_weapon.risk_score > assessment_no_weapon.risk_score
    
    def test_firearm_detection_high_risk(self):
        """Test firearm detection results in high risk"""
        assessment = self.monitor.assess_risk(
            incident_id="INC-007",
            officer_id="RBPD-201",
            suspect_behavior=SuspectBehaviorClass.AGGRESSIVE,
            weapon_type=WeaponType.FIREARM,
            weapon_probability=0.9,
        )
        
        assert assessment.risk_level == RiskLevel.RED
        assert assessment.weapon_detected
    
    def test_danger_zone_proximity_increases_risk(self):
        """Test officer in danger zone (<21 ft) increases risk"""
        assessment = self.monitor.assess_risk(
            incident_id="INC-008",
            officer_id="RBPD-201",
            suspect_behavior=SuspectBehaviorClass.ACTIVE_RESISTANT,
            officer_proximity_feet=15,
        )
        
        assert "danger zone" in " ".join(assessment.risk_factors).lower()
    
    def test_safe_distance_protective_factor(self):
        """Test safe distance is a protective factor"""
        assessment = self.monitor.assess_risk(
            incident_id="INC-009",
            officer_id="RBPD-201",
            suspect_behavior=SuspectBehaviorClass.PASSIVE_RESISTANT,
            officer_proximity_feet=150,
        )
        
        assert len(assessment.protective_factors) > 0
    
    def test_elevated_heart_rate_increases_risk(self):
        """Test elevated officer heart rate increases risk"""
        vitals = OfficerVitals(
            heart_rate=160,
            stress_index=0.85,
        )
        
        assessment = self.monitor.assess_risk(
            incident_id="INC-010",
            officer_id="RBPD-201",
            suspect_behavior=SuspectBehaviorClass.ACTIVE_RESISTANT,
            officer_vitals=vitals,
        )
        
        assert "heart rate" in " ".join(assessment.risk_factors).lower()
    
    def test_outnumbered_officer_increases_risk(self):
        """Test outnumbered officer increases risk"""
        scene = SceneContext(
            incident_id="INC-011",
            officer_id="RBPD-201",
            officer_count=1,
            suspect_count=3,
        )
        
        assessment = self.monitor.assess_risk(
            incident_id="INC-011",
            officer_id="RBPD-201",
            suspect_behavior=SuspectBehaviorClass.ACTIVE_RESISTANT,
            scene_context=scene,
        )
        
        assert "outnumbered" in " ".join(assessment.risk_factors).lower()
    
    def test_de_escalating_scene_reduces_risk(self):
        """Test de-escalating scene reduces risk"""
        assessment = self.monitor.assess_risk(
            incident_id="INC-012",
            officer_id="RBPD-201",
            suspect_behavior=SuspectBehaviorClass.PASSIVE_RESISTANT,
            escalation_pattern=SceneEscalationPattern.DE_ESCALATING,
        )
        
        assert "de-escalating" in " ".join(assessment.protective_factors).lower()
    
    def test_red_level_triggers_supervisor_notification(self):
        """Test red level triggers supervisor notification"""
        assessment = self.monitor.assess_risk(
            incident_id="INC-013",
            officer_id="RBPD-201",
            suspect_behavior=SuspectBehaviorClass.LIFE_THREATENING,
        )
        
        assert assessment.supervisor_notified
        assert assessment.rtcc_notified
        assert assessment.backup_requested
    
    def test_red_level_triggers_backup_request(self):
        """Test red level triggers backup request"""
        assessment = self.monitor.assess_risk(
            incident_id="INC-014",
            officer_id="RBPD-201",
            suspect_behavior=SuspectBehaviorClass.ASSAULTIVE,
            escalation_pattern=SceneEscalationPattern.CRITICAL,
        )
        
        assert assessment.backup_requested
    
    def test_yellow_level_recommends_de_escalation(self):
        """Test yellow level recommends de-escalation"""
        assessment = self.monitor.assess_risk(
            incident_id="INC-015",
            officer_id="RBPD-201",
            suspect_behavior=SuspectBehaviorClass.ACTIVE_RESISTANT,
        )
        
        assert assessment.de_escalation_recommended
    
    def test_assessment_history_tracking(self):
        """Test assessment history is tracked"""
        self.monitor.assess_risk(
            incident_id="INC-016",
            officer_id="RBPD-201",
            suspect_behavior=SuspectBehaviorClass.COMPLIANT,
        )
        
        history = self.monitor.get_assessment_history()
        assert len(history) > 0
    
    def test_active_assessment_retrieval(self):
        """Test active assessment can be retrieved"""
        self.monitor.assess_risk(
            incident_id="INC-017",
            officer_id="RBPD-201",
            suspect_behavior=SuspectBehaviorClass.COMPLIANT,
        )
        
        assessment = self.monitor.get_active_assessment("INC-017")
        assert assessment is not None
        assert assessment.incident_id == "INC-017"
    
    def test_assessment_update(self):
        """Test assessment can be updated"""
        self.monitor.assess_risk(
            incident_id="INC-018",
            officer_id="RBPD-201",
            suspect_behavior=SuspectBehaviorClass.COMPLIANT,
        )
        
        updated = self.monitor.update_assessment(
            incident_id="INC-018",
            suspect_behavior=SuspectBehaviorClass.AGGRESSIVE,
        )
        
        assert updated is not None
        assert updated.suspect_behavior == SuspectBehaviorClass.AGGRESSIVE
    
    def test_incident_closure(self):
        """Test incident can be closed"""
        self.monitor.assess_risk(
            incident_id="INC-019",
            officer_id="RBPD-201",
            suspect_behavior=SuspectBehaviorClass.COMPLIANT,
        )
        
        result = self.monitor.close_incident("INC-019")
        assert result
        
        assessment = self.monitor.get_active_assessment("INC-019")
        assert assessment is None
    
    def test_supervisor_alert_acknowledgment(self):
        """Test supervisor alert can be acknowledged"""
        assessment = self.monitor.assess_risk(
            incident_id="INC-020",
            officer_id="RBPD-201",
            suspect_behavior=SuspectBehaviorClass.LIFE_THREATENING,
        )
        
        alerts = self.monitor.get_supervisor_alerts()
        if alerts:
            result = self.monitor.acknowledge_alert(alerts[0].alert_id, "SGT-001")
            assert result
    
    def test_risk_statistics(self):
        """Test risk statistics calculation"""
        self.monitor.assess_risk(
            incident_id="INC-021",
            officer_id="RBPD-201",
            suspect_behavior=SuspectBehaviorClass.COMPLIANT,
        )
        
        stats = self.monitor.get_risk_statistics()
        assert "total_assessments" in stats
        assert "green_count" in stats
        assert "average_risk_score" in stats


class TestRiskLevelEnums:
    """Tests for risk level enums"""
    
    def test_risk_levels_exist(self):
        """Test all risk levels exist"""
        assert RiskLevel.GREEN
        assert RiskLevel.YELLOW
        assert RiskLevel.RED


class TestSuspectBehaviorClasses:
    """Tests for suspect behavior classification enums"""
    
    def test_all_behavior_classes_exist(self):
        """Test all behavior classes exist"""
        assert SuspectBehaviorClass.COMPLIANT
        assert SuspectBehaviorClass.PASSIVE_RESISTANT
        assert SuspectBehaviorClass.ACTIVE_RESISTANT
        assert SuspectBehaviorClass.AGGRESSIVE
        assert SuspectBehaviorClass.ASSAULTIVE
        assert SuspectBehaviorClass.LIFE_THREATENING


class TestWeaponTypes:
    """Tests for weapon type enums"""
    
    def test_all_weapon_types_exist(self):
        """Test all weapon types exist"""
        assert WeaponType.NONE
        assert WeaponType.UNKNOWN
        assert WeaponType.BLUNT_OBJECT
        assert WeaponType.EDGED_WEAPON
        assert WeaponType.FIREARM
        assert WeaponType.VEHICLE
        assert WeaponType.EXPLOSIVE
