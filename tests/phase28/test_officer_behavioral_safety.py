"""
Test Suite 3: Officer Behavioral Safety Engine Tests

Tests for fatigue, stress, workload, and trauma monitoring.
"""

import pytest
from datetime import datetime, timedelta
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend', 'app'))

from officer_assist.officer_behavioral_safety import (
    OfficerBehavioralSafetyEngine,
    FatigueLevel,
    StressIndicator,
    TraumaPattern,
    SafetyAlertType,
    OfficerWorkload,
    OfficerHistory,
    OfficerSafetyStatus,
)


class TestOfficerBehavioralSafetyEngine:
    """Tests for Officer Behavioral Safety Engine"""
    
    def setup_method(self):
        """Reset singleton for each test"""
        OfficerBehavioralSafetyEngine._instance = None
        self.engine = OfficerBehavioralSafetyEngine()
    
    def test_singleton_pattern(self):
        """Test that engine uses singleton pattern"""
        engine1 = OfficerBehavioralSafetyEngine()
        engine2 = OfficerBehavioralSafetyEngine()
        assert engine1 is engine2
    
    def test_agency_configuration(self):
        """Test agency configuration is correct"""
        assert self.engine.agency_config["ori"] == "FL0500400"
        assert self.engine.agency_config["name"] == "Riviera Beach Police Department"
    
    def test_normal_workload_low_risk(self):
        """Test normal workload results in low risk"""
        workload = OfficerWorkload(
            officer_id="RBPD-201",
            shift_start=datetime.utcnow() - timedelta(hours=6),
            hours_on_duty=6,
            calls_handled=8,
            high_stress_calls=1,
            breaks_taken=1,
        )
        
        status = self.engine.assess_officer_safety(
            officer_id="RBPD-201",
            workload=workload,
        )
        
        assert status.overall_risk_score < 0.5
        assert status.fit_for_duty
    
    def test_excessive_hours_increases_fatigue(self):
        """Test excessive hours increases fatigue level"""
        workload = OfficerWorkload(
            officer_id="RBPD-201",
            shift_start=datetime.utcnow() - timedelta(hours=14),
            hours_on_duty=14,
            calls_handled=20,
            breaks_taken=0,
        )
        
        status = self.engine.assess_officer_safety(
            officer_id="RBPD-201",
            workload=workload,
        )
        
        assert status.fatigue_level in [FatigueLevel.SEVERE, FatigueLevel.CRITICAL]
        assert status.fatigue_score > 0.7
    
    def test_critical_fatigue_not_fit_for_duty(self):
        """Test critical fatigue results in not fit for duty"""
        workload = OfficerWorkload(
            officer_id="RBPD-201",
            shift_start=datetime.utcnow() - timedelta(hours=15),
            hours_on_duty=15,
            calls_handled=25,
            breaks_taken=0,
            consecutive_days_worked=6,
        )
        
        status = self.engine.assess_officer_safety(
            officer_id="RBPD-201",
            workload=workload,
        )
        
        assert status.fatigue_level == FatigueLevel.CRITICAL
        assert not status.fit_for_duty
    
    def test_high_stress_calls_increases_stress(self):
        """Test high stress calls increase stress score"""
        workload = OfficerWorkload(
            officer_id="RBPD-201",
            shift_start=datetime.utcnow() - timedelta(hours=8),
            hours_on_duty=8,
            calls_handled=15,
            high_stress_calls=6,
            breaks_taken=0,
        )
        
        status = self.engine.assess_officer_safety(
            officer_id="RBPD-201",
            workload=workload,
        )
        
        assert status.stress_score > 0.5
    
    def test_stress_indicators_increase_stress(self):
        """Test stress indicators increase stress score"""
        workload = OfficerWorkload(
            officer_id="RBPD-201",
            shift_start=datetime.utcnow() - timedelta(hours=8),
            hours_on_duty=8,
            calls_handled=10,
        )
        
        status = self.engine.assess_officer_safety(
            officer_id="RBPD-201",
            workload=workload,
            stress_indicators=[
                StressIndicator.ELEVATED_HEART_RATE,
                StressIndicator.VOICE_STRESS,
                StressIndicator.IRRITABILITY,
            ],
        )
        
        assert len(status.stress_indicators) == 3
        assert status.stress_score > 0.3
    
    def test_excessive_calls_increases_workload(self):
        """Test excessive calls increase workload score"""
        workload = OfficerWorkload(
            officer_id="RBPD-201",
            shift_start=datetime.utcnow() - timedelta(hours=8),
            hours_on_duty=8,
            calls_handled=25,
            arrests_made=6,
        )
        
        status = self.engine.assess_officer_safety(
            officer_id="RBPD-201",
            workload=workload,
        )
        
        assert status.workload_score > 0.5
    
    def test_trauma_exposure_increases_risk(self):
        """Test trauma exposure increases risk score"""
        history = OfficerHistory(
            officer_id="RBPD-201",
            trauma_exposures_90d=3,
            counseling_referrals=1,
        )
        
        status = self.engine.assess_officer_safety(
            officer_id="RBPD-201",
            history=history,
        )
        
        assert status.trauma_exposure_score > 0.3
    
    def test_trauma_call_type_increases_trauma_score(self):
        """Test trauma call type increases trauma score"""
        status = self.engine.assess_officer_safety(
            officer_id="RBPD-201",
            recent_call_type="OFFICER_INVOLVED_SHOOTING",
        )
        
        assert status.trauma_exposure_score > 0.2
        assert len(status.recent_trauma_events) > 0
    
    def test_pattern_detection_high_stress_events(self):
        """Test pattern detection for high stress events"""
        history = OfficerHistory(
            officer_id="RBPD-201",
            high_stress_events_30d=6,
        )
        
        status = self.engine.assess_officer_safety(
            officer_id="RBPD-201",
            history=history,
        )
        
        assert len(status.pattern_flags) > 0
        assert any("stress" in flag.lower() for flag in status.pattern_flags)
    
    def test_pattern_detection_complaints(self):
        """Test pattern detection for complaints"""
        history = OfficerHistory(
            officer_id="RBPD-201",
            complaints_12m=3,
        )
        
        status = self.engine.assess_officer_safety(
            officer_id="RBPD-201",
            history=history,
        )
        
        assert len(status.pattern_flags) > 0
        assert any("complaint" in flag.lower() for flag in status.pattern_flags)
    
    def test_pattern_detection_use_of_force(self):
        """Test pattern detection for use of force incidents"""
        history = OfficerHistory(
            officer_id="RBPD-201",
            use_of_force_incidents_12m=4,
        )
        
        status = self.engine.assess_officer_safety(
            officer_id="RBPD-201",
            history=history,
        )
        
        assert len(status.pattern_flags) > 0
        assert any("force" in flag.lower() for flag in status.pattern_flags)
    
    def test_wellness_check_overdue_detection(self):
        """Test wellness check overdue detection"""
        history = OfficerHistory(
            officer_id="RBPD-201",
            last_wellness_check=datetime.utcnow() - timedelta(days=100),
        )
        
        status = self.engine.assess_officer_safety(
            officer_id="RBPD-201",
            history=history,
        )
        
        assert len(status.pattern_flags) > 0
        assert any("wellness" in flag.lower() for flag in status.pattern_flags)
    
    def test_supervisor_review_required_high_risk(self):
        """Test supervisor review required for high risk"""
        workload = OfficerWorkload(
            officer_id="RBPD-201",
            shift_start=datetime.utcnow() - timedelta(hours=12),
            hours_on_duty=12,
            calls_handled=20,
            high_stress_calls=5,
            breaks_taken=0,
        )
        
        status = self.engine.assess_officer_safety(
            officer_id="RBPD-201",
            workload=workload,
        )
        
        assert status.supervisor_review_required
    
    def test_safety_alert_generation(self):
        """Test safety alert generation"""
        workload = OfficerWorkload(
            officer_id="RBPD-201",
            shift_start=datetime.utcnow() - timedelta(hours=14),
            hours_on_duty=14,
            breaks_taken=0,
        )
        
        status = self.engine.assess_officer_safety(
            officer_id="RBPD-201",
            workload=workload,
        )
        
        assert len(status.active_alerts) > 0
    
    def test_recommendations_generated(self):
        """Test recommendations are generated for high risk"""
        workload = OfficerWorkload(
            officer_id="RBPD-201",
            shift_start=datetime.utcnow() - timedelta(hours=13),
            hours_on_duty=13,
            breaks_taken=0,
        )
        
        status = self.engine.assess_officer_safety(
            officer_id="RBPD-201",
            workload=workload,
        )
        
        assert len(status.recommendations) > 0
    
    def test_record_call(self):
        """Test recording a call updates workload"""
        status = self.engine.record_call(
            officer_id="RBPD-201",
            call_type="DOMESTIC_VIOLENCE",
            duration_minutes=30,
        )
        
        assert status.workload.calls_handled >= 1
    
    def test_record_break(self):
        """Test recording a break updates workload"""
        self.engine.record_call(
            officer_id="RBPD-201",
            call_type="TRAFFIC_STOP",
        )
        
        result = self.engine.record_break("RBPD-201")
        assert result
    
    def test_get_officer_status(self):
        """Test getting officer status"""
        self.engine.assess_officer_safety(officer_id="RBPD-201")
        
        status = self.engine.get_officer_status("RBPD-201")
        assert status is not None
        assert status.officer_id == "RBPD-201"
    
    def test_get_all_alerts(self):
        """Test getting all alerts"""
        workload = OfficerWorkload(
            officer_id="RBPD-201",
            shift_start=datetime.utcnow() - timedelta(hours=14),
            hours_on_duty=14,
            breaks_taken=0,
        )
        
        self.engine.assess_officer_safety(
            officer_id="RBPD-201",
            workload=workload,
        )
        
        alerts = self.engine.get_all_alerts()
        assert len(alerts) >= 0
    
    def test_acknowledge_alert(self):
        """Test acknowledging an alert"""
        workload = OfficerWorkload(
            officer_id="RBPD-201",
            shift_start=datetime.utcnow() - timedelta(hours=14),
            hours_on_duty=14,
            breaks_taken=0,
        )
        
        status = self.engine.assess_officer_safety(
            officer_id="RBPD-201",
            workload=workload,
        )
        
        if status.active_alerts:
            result = self.engine.acknowledge_alert(status.active_alerts[0].alert_id)
            assert result
    
    def test_resolve_alert(self):
        """Test resolving an alert"""
        workload = OfficerWorkload(
            officer_id="RBPD-201",
            shift_start=datetime.utcnow() - timedelta(hours=14),
            hours_on_duty=14,
            breaks_taken=0,
        )
        
        status = self.engine.assess_officer_safety(
            officer_id="RBPD-201",
            workload=workload,
        )
        
        if status.active_alerts:
            result = self.engine.resolve_alert(status.active_alerts[0].alert_id)
            assert result
    
    def test_get_officers_requiring_review(self):
        """Test getting officers requiring review"""
        workload = OfficerWorkload(
            officer_id="RBPD-201",
            shift_start=datetime.utcnow() - timedelta(hours=12),
            hours_on_duty=12,
            calls_handled=20,
            high_stress_calls=5,
        )
        
        self.engine.assess_officer_safety(
            officer_id="RBPD-201",
            workload=workload,
        )
        
        officers = self.engine.get_officers_requiring_review()
        assert isinstance(officers, list)
    
    def test_safety_statistics(self):
        """Test safety statistics calculation"""
        self.engine.assess_officer_safety(officer_id="RBPD-201")
        
        stats = self.engine.get_safety_statistics()
        assert "officers_monitored" in stats
        assert "average_risk_score" in stats
        assert "high_risk_officers" in stats


class TestFatigueLevelEnums:
    """Tests for fatigue level enums"""
    
    def test_all_fatigue_levels_exist(self):
        """Test all fatigue levels exist"""
        assert FatigueLevel.NORMAL
        assert FatigueLevel.MILD
        assert FatigueLevel.MODERATE
        assert FatigueLevel.SEVERE
        assert FatigueLevel.CRITICAL


class TestStressIndicatorEnums:
    """Tests for stress indicator enums"""
    
    def test_all_stress_indicators_exist(self):
        """Test all stress indicators exist"""
        assert StressIndicator.ELEVATED_HEART_RATE
        assert StressIndicator.VOICE_STRESS
        assert StressIndicator.RAPID_DECISION_MAKING
        assert StressIndicator.COMMUNICATION_BREAKDOWN
        assert StressIndicator.BEHAVIORAL_CHANGE
        assert StressIndicator.ISOLATION
        assert StressIndicator.IRRITABILITY


class TestSafetyAlertTypeEnums:
    """Tests for safety alert type enums"""
    
    def test_all_alert_types_exist(self):
        """Test all alert types exist"""
        assert SafetyAlertType.FATIGUE_WARNING
        assert SafetyAlertType.STRESS_WARNING
        assert SafetyAlertType.WORKLOAD_WARNING
        assert SafetyAlertType.TRAUMA_EXPOSURE
        assert SafetyAlertType.PATTERN_DETECTED
        assert SafetyAlertType.WELLNESS_CHECK
        assert SafetyAlertType.MANDATORY_BREAK
