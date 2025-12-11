"""
Test Suite 8: Stress/Fatigue Model Tests

Tests for stress and fatigue scoring algorithms.
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
    OfficerWorkload,
    OfficerHistory,
)


class TestFatigueScoring:
    """Tests for fatigue scoring algorithm"""
    
    def setup_method(self):
        """Reset singleton for each test"""
        OfficerBehavioralSafetyEngine._instance = None
        self.engine = OfficerBehavioralSafetyEngine()
    
    def test_fatigue_score_under_8_hours_normal(self):
        """Test fatigue score is low under 8 hours"""
        workload = OfficerWorkload(
            officer_id="RBPD-201",
            shift_start=datetime.utcnow() - timedelta(hours=6),
            hours_on_duty=6,
            breaks_taken=1,
        )
        
        status = self.engine.assess_officer_safety(
            officer_id="RBPD-201",
            workload=workload,
        )
        
        assert status.fatigue_level == FatigueLevel.NORMAL
        assert status.fatigue_score < 0.3
    
    def test_fatigue_score_8_to_10_hours_mild(self):
        """Test fatigue score is mild between 8-10 hours"""
        workload = OfficerWorkload(
            officer_id="RBPD-201",
            shift_start=datetime.utcnow() - timedelta(hours=9),
            hours_on_duty=9,
            breaks_taken=1,
        )
        
        status = self.engine.assess_officer_safety(
            officer_id="RBPD-201",
            workload=workload,
        )
        
        assert status.fatigue_level in [FatigueLevel.NORMAL, FatigueLevel.MILD]
    
    def test_fatigue_score_10_to_12_hours_moderate(self):
        """Test fatigue score is moderate between 10-12 hours"""
        workload = OfficerWorkload(
            officer_id="RBPD-201",
            shift_start=datetime.utcnow() - timedelta(hours=11),
            hours_on_duty=11,
            breaks_taken=0,
        )
        
        status = self.engine.assess_officer_safety(
            officer_id="RBPD-201",
            workload=workload,
        )
        
        assert status.fatigue_level in [FatigueLevel.MODERATE, FatigueLevel.SEVERE]
        assert status.fatigue_score >= 0.4
    
    def test_fatigue_score_12_to_14_hours_severe(self):
        """Test fatigue score is severe between 12-14 hours"""
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
        
        assert status.fatigue_level in [FatigueLevel.SEVERE, FatigueLevel.CRITICAL]
        assert status.fatigue_score >= 0.6
    
    def test_fatigue_score_over_14_hours_critical(self):
        """Test fatigue score is critical over 14 hours"""
        workload = OfficerWorkload(
            officer_id="RBPD-201",
            shift_start=datetime.utcnow() - timedelta(hours=15),
            hours_on_duty=15,
            breaks_taken=0,
        )
        
        status = self.engine.assess_officer_safety(
            officer_id="RBPD-201",
            workload=workload,
        )
        
        assert status.fatigue_level == FatigueLevel.CRITICAL
        assert status.fatigue_score >= 0.8
    
    def test_breaks_reduce_fatigue_score(self):
        """Test breaks reduce fatigue score"""
        workload_no_breaks = OfficerWorkload(
            officer_id="RBPD-201",
            shift_start=datetime.utcnow() - timedelta(hours=10),
            hours_on_duty=10,
            breaks_taken=0,
        )
        
        status_no_breaks = self.engine.assess_officer_safety(
            officer_id="RBPD-201",
            workload=workload_no_breaks,
        )
        
        OfficerBehavioralSafetyEngine._instance = None
        engine2 = OfficerBehavioralSafetyEngine()
        
        workload_with_breaks = OfficerWorkload(
            officer_id="RBPD-202",
            shift_start=datetime.utcnow() - timedelta(hours=10),
            hours_on_duty=10,
            breaks_taken=2,
        )
        
        status_with_breaks = engine2.assess_officer_safety(
            officer_id="RBPD-202",
            workload=workload_with_breaks,
        )
        
        assert status_with_breaks.fatigue_score <= status_no_breaks.fatigue_score
    
    def test_consecutive_days_increase_fatigue(self):
        """Test consecutive days worked increase fatigue"""
        workload = OfficerWorkload(
            officer_id="RBPD-201",
            shift_start=datetime.utcnow() - timedelta(hours=8),
            hours_on_duty=8,
            consecutive_days_worked=6,
        )
        
        status = self.engine.assess_officer_safety(
            officer_id="RBPD-201",
            workload=workload,
        )
        
        assert status.fatigue_score > 0.3


class TestStressScoring:
    """Tests for stress scoring algorithm"""
    
    def setup_method(self):
        """Reset singleton for each test"""
        OfficerBehavioralSafetyEngine._instance = None
        self.engine = OfficerBehavioralSafetyEngine()
    
    def test_stress_score_low_with_no_indicators(self):
        """Test stress score is low with no indicators"""
        workload = OfficerWorkload(
            officer_id="RBPD-201",
            shift_start=datetime.utcnow() - timedelta(hours=6),
            hours_on_duty=6,
            high_stress_calls=0,
        )
        
        status = self.engine.assess_officer_safety(
            officer_id="RBPD-201",
            workload=workload,
            stress_indicators=[],
        )
        
        assert status.stress_score < 0.3
    
    def test_stress_score_increases_with_high_stress_calls(self):
        """Test stress score increases with high stress calls"""
        workload = OfficerWorkload(
            officer_id="RBPD-201",
            shift_start=datetime.utcnow() - timedelta(hours=8),
            hours_on_duty=8,
            high_stress_calls=5,
        )
        
        status = self.engine.assess_officer_safety(
            officer_id="RBPD-201",
            workload=workload,
        )
        
        assert status.stress_score > 0.3
    
    def test_stress_score_increases_with_indicators(self):
        """Test stress score increases with stress indicators"""
        workload = OfficerWorkload(
            officer_id="RBPD-201",
            shift_start=datetime.utcnow() - timedelta(hours=8),
            hours_on_duty=8,
        )
        
        status = self.engine.assess_officer_safety(
            officer_id="RBPD-201",
            workload=workload,
            stress_indicators=[
                StressIndicator.ELEVATED_HEART_RATE,
                StressIndicator.VOICE_STRESS,
            ],
        )
        
        assert status.stress_score > 0.3
        assert len(status.stress_indicators) == 2
    
    def test_multiple_stress_indicators_compound(self):
        """Test multiple stress indicators compound"""
        workload = OfficerWorkload(
            officer_id="RBPD-201",
            shift_start=datetime.utcnow() - timedelta(hours=8),
            hours_on_duty=8,
        )
        
        status = self.engine.assess_officer_safety(
            officer_id="RBPD-201",
            workload=workload,
            stress_indicators=[
                StressIndicator.ELEVATED_HEART_RATE,
                StressIndicator.VOICE_STRESS,
                StressIndicator.IRRITABILITY,
                StressIndicator.BEHAVIORAL_CHANGE,
            ],
        )
        
        assert status.stress_score > 0.5
    
    def test_stress_score_from_recent_trauma(self):
        """Test stress score increases from recent trauma"""
        status = self.engine.assess_officer_safety(
            officer_id="RBPD-201",
            recent_call_type="OFFICER_INVOLVED_SHOOTING",
        )
        
        assert status.stress_score > 0.2


class TestWorkloadScoring:
    """Tests for workload scoring algorithm"""
    
    def setup_method(self):
        """Reset singleton for each test"""
        OfficerBehavioralSafetyEngine._instance = None
        self.engine = OfficerBehavioralSafetyEngine()
    
    def test_workload_score_low_with_few_calls(self):
        """Test workload score is low with few calls"""
        workload = OfficerWorkload(
            officer_id="RBPD-201",
            shift_start=datetime.utcnow() - timedelta(hours=6),
            hours_on_duty=6,
            calls_handled=5,
        )
        
        status = self.engine.assess_officer_safety(
            officer_id="RBPD-201",
            workload=workload,
        )
        
        assert status.workload_score < 0.4
    
    def test_workload_score_increases_with_calls(self):
        """Test workload score increases with more calls"""
        workload = OfficerWorkload(
            officer_id="RBPD-201",
            shift_start=datetime.utcnow() - timedelta(hours=8),
            hours_on_duty=8,
            calls_handled=20,
        )
        
        status = self.engine.assess_officer_safety(
            officer_id="RBPD-201",
            workload=workload,
        )
        
        assert status.workload_score > 0.4
    
    def test_workload_score_increases_with_arrests(self):
        """Test workload score increases with arrests"""
        workload = OfficerWorkload(
            officer_id="RBPD-201",
            shift_start=datetime.utcnow() - timedelta(hours=8),
            hours_on_duty=8,
            calls_handled=10,
            arrests_made=5,
        )
        
        status = self.engine.assess_officer_safety(
            officer_id="RBPD-201",
            workload=workload,
        )
        
        assert status.workload_score > 0.3
    
    def test_workload_score_increases_with_overtime(self):
        """Test workload score increases with overtime"""
        workload = OfficerWorkload(
            officer_id="RBPD-201",
            shift_start=datetime.utcnow() - timedelta(hours=10),
            hours_on_duty=10,
            calls_handled=15,
            overtime_hours=2,
        )
        
        status = self.engine.assess_officer_safety(
            officer_id="RBPD-201",
            workload=workload,
        )
        
        assert status.workload_score > 0.4


class TestTraumaExposureScoring:
    """Tests for trauma exposure scoring algorithm"""
    
    def setup_method(self):
        """Reset singleton for each test"""
        OfficerBehavioralSafetyEngine._instance = None
        self.engine = OfficerBehavioralSafetyEngine()
    
    def test_trauma_score_low_with_no_exposure(self):
        """Test trauma score is low with no exposure"""
        history = OfficerHistory(
            officer_id="RBPD-201",
            trauma_exposures_90d=0,
        )
        
        status = self.engine.assess_officer_safety(
            officer_id="RBPD-201",
            history=history,
        )
        
        assert status.trauma_exposure_score < 0.3
    
    def test_trauma_score_increases_with_exposures(self):
        """Test trauma score increases with exposures"""
        history = OfficerHistory(
            officer_id="RBPD-201",
            trauma_exposures_90d=3,
        )
        
        status = self.engine.assess_officer_safety(
            officer_id="RBPD-201",
            history=history,
        )
        
        assert status.trauma_exposure_score > 0.3
    
    def test_trauma_score_high_with_multiple_exposures(self):
        """Test trauma score is high with multiple exposures"""
        history = OfficerHistory(
            officer_id="RBPD-201",
            trauma_exposures_90d=5,
            counseling_referrals=2,
        )
        
        status = self.engine.assess_officer_safety(
            officer_id="RBPD-201",
            history=history,
        )
        
        assert status.trauma_exposure_score > 0.5
    
    def test_recent_trauma_call_increases_score(self):
        """Test recent trauma call increases score"""
        status = self.engine.assess_officer_safety(
            officer_id="RBPD-201",
            recent_call_type="CHILD_FATALITY",
        )
        
        assert status.trauma_exposure_score > 0.2


class TestOverallRiskScoring:
    """Tests for overall risk score calculation"""
    
    def setup_method(self):
        """Reset singleton for each test"""
        OfficerBehavioralSafetyEngine._instance = None
        self.engine = OfficerBehavioralSafetyEngine()
    
    def test_overall_risk_weighted_average(self):
        """Test overall risk is weighted average of components"""
        workload = OfficerWorkload(
            officer_id="RBPD-201",
            shift_start=datetime.utcnow() - timedelta(hours=8),
            hours_on_duty=8,
            calls_handled=10,
        )
        
        status = self.engine.assess_officer_safety(
            officer_id="RBPD-201",
            workload=workload,
        )
        
        expected_range = (
            status.fatigue_score * 0.25 +
            status.stress_score * 0.30 +
            status.workload_score * 0.20 +
            status.trauma_exposure_score * 0.25
        )
        
        assert abs(status.overall_risk_score - expected_range) < 0.1
    
    def test_fit_for_duty_threshold(self):
        """Test fit for duty threshold"""
        workload = OfficerWorkload(
            officer_id="RBPD-201",
            shift_start=datetime.utcnow() - timedelta(hours=6),
            hours_on_duty=6,
        )
        
        status = self.engine.assess_officer_safety(
            officer_id="RBPD-201",
            workload=workload,
        )
        
        if status.overall_risk_score < 0.7:
            assert status.fit_for_duty
    
    def test_not_fit_for_duty_high_risk(self):
        """Test not fit for duty with high risk"""
        workload = OfficerWorkload(
            officer_id="RBPD-201",
            shift_start=datetime.utcnow() - timedelta(hours=15),
            hours_on_duty=15,
            calls_handled=25,
            high_stress_calls=8,
            breaks_taken=0,
        )
        
        status = self.engine.assess_officer_safety(
            officer_id="RBPD-201",
            workload=workload,
        )
        
        assert not status.fit_for_duty
    
    def test_supervisor_review_threshold(self):
        """Test supervisor review threshold"""
        workload = OfficerWorkload(
            officer_id="RBPD-201",
            shift_start=datetime.utcnow() - timedelta(hours=12),
            hours_on_duty=12,
            high_stress_calls=5,
        )
        
        status = self.engine.assess_officer_safety(
            officer_id="RBPD-201",
            workload=workload,
        )
        
        if status.overall_risk_score > 0.5:
            assert status.supervisor_review_required
