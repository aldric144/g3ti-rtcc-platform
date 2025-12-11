"""
Phase 30: Community Trauma Pulse Tests

Tests for:
- Stability index calculation
- Trauma cluster detection
- Community shock level
- Zone-level analysis
"""

import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))


class TestCommunityTraumaPulse:
    """Tests for community trauma pulse monitoring"""
    
    def test_get_stability_index(self):
        """Test stability index retrieval"""
        from backend.app.human_intel.behavioral_crisis_engine import BehavioralCrisisEngine
        
        engine = BehavioralCrisisEngine()
        
        index = engine.get_stability_index()
        
        assert index is not None
        assert 0 <= index.overall_score <= 100
    
    def test_stability_index_components(self):
        """Test stability index has all components"""
        from backend.app.human_intel.behavioral_crisis_engine import BehavioralCrisisEngine
        
        engine = BehavioralCrisisEngine()
        
        index = engine.get_stability_index()
        
        assert index is not None
        assert hasattr(index, "mental_health_score")
        assert hasattr(index, "violence_score")
        assert hasattr(index, "community_cohesion_score")
        assert hasattr(index, "youth_stability_score")
    
    def test_stability_index_scores_in_range(self):
        """Test all stability scores are in valid range"""
        from backend.app.human_intel.behavioral_crisis_engine import BehavioralCrisisEngine
        
        engine = BehavioralCrisisEngine()
        
        index = engine.get_stability_index()
        
        assert 0 <= index.mental_health_score <= 100
        assert 0 <= index.violence_score <= 100
        assert 0 <= index.community_cohesion_score <= 100
        assert 0 <= index.youth_stability_score <= 100
    
    def test_stability_index_trends(self):
        """Test stability index includes trends"""
        from backend.app.human_intel.behavioral_crisis_engine import BehavioralCrisisEngine
        
        engine = BehavioralCrisisEngine()
        
        index = engine.get_stability_index()
        
        assert index is not None
        assert hasattr(index, "trend_7_day")
        assert hasattr(index, "trend_30_day")
    
    def test_get_community_trauma_pulse(self):
        """Test community trauma pulse retrieval"""
        from backend.app.human_intel.behavioral_crisis_engine import BehavioralCrisisEngine
        
        engine = BehavioralCrisisEngine()
        
        pulse = engine.get_community_trauma_pulse(time_window_hours=72)
        
        assert pulse is not None
        assert 0 <= pulse.stability_index <= 100
    
    def test_community_trauma_pulse_shock_level(self):
        """Test community shock level is in valid range"""
        from backend.app.human_intel.behavioral_crisis_engine import BehavioralCrisisEngine
        
        engine = BehavioralCrisisEngine()
        
        pulse = engine.get_community_trauma_pulse(time_window_hours=72)
        
        assert pulse is not None
        assert 0 <= pulse.community_shock_level <= 1.0
    
    def test_community_trauma_pulse_clusters(self):
        """Test trauma clusters are returned"""
        from backend.app.human_intel.behavioral_crisis_engine import BehavioralCrisisEngine
        
        engine = BehavioralCrisisEngine()
        
        pulse = engine.get_community_trauma_pulse(time_window_hours=72)
        
        assert pulse is not None
        assert hasattr(pulse, "trauma_clusters")
        assert isinstance(pulse.trauma_clusters, list)
    
    def test_community_trauma_pulse_trend(self):
        """Test trend direction is valid"""
        from backend.app.human_intel.behavioral_crisis_engine import BehavioralCrisisEngine
        
        engine = BehavioralCrisisEngine()
        
        pulse = engine.get_community_trauma_pulse(time_window_hours=72)
        
        assert pulse is not None
        assert pulse.trend_direction in ["improving", "stable", "declining"]
    
    def test_community_trauma_pulse_anonymization(self):
        """Test anonymization level is aggregated"""
        from backend.app.human_intel.behavioral_crisis_engine import BehavioralCrisisEngine
        
        engine = BehavioralCrisisEngine()
        
        pulse = engine.get_community_trauma_pulse(time_window_hours=72)
        
        assert pulse is not None
        assert pulse.anonymization_level == "AGGREGATED"
    
    def test_community_trauma_pulse_privacy_protections(self):
        """Test privacy protections are applied"""
        from backend.app.human_intel.behavioral_crisis_engine import BehavioralCrisisEngine
        
        engine = BehavioralCrisisEngine()
        
        pulse = engine.get_community_trauma_pulse(time_window_hours=72)
        
        assert pulse is not None
        assert len(pulse.privacy_protections) > 0
    
    def test_high_risk_areas_identification(self):
        """Test high risk areas are identified"""
        from backend.app.human_intel.behavioral_crisis_engine import BehavioralCrisisEngine
        
        engine = BehavioralCrisisEngine()
        
        index = engine.get_stability_index()
        
        assert index is not None
        assert hasattr(index, "high_risk_areas")
        assert isinstance(index.high_risk_areas, list)
    
    def test_school_disturbances_tracking(self):
        """Test school disturbances are tracked"""
        from backend.app.human_intel.behavioral_crisis_engine import BehavioralCrisisEngine
        
        engine = BehavioralCrisisEngine()
        
        pulse = engine.get_community_trauma_pulse(time_window_hours=72)
        
        assert pulse is not None
        assert hasattr(pulse, "school_disturbances")
        assert isinstance(pulse.school_disturbances, list)
    
    def test_youth_violence_warnings(self):
        """Test youth violence warnings are tracked"""
        from backend.app.human_intel.behavioral_crisis_engine import BehavioralCrisisEngine
        
        engine = BehavioralCrisisEngine()
        
        pulse = engine.get_community_trauma_pulse(time_window_hours=72)
        
        assert pulse is not None
        assert hasattr(pulse, "youth_violence_warnings")
        assert isinstance(pulse.youth_violence_warnings, list)
    
    def test_recommended_interventions(self):
        """Test recommended interventions are provided"""
        from backend.app.human_intel.behavioral_crisis_engine import BehavioralCrisisEngine
        
        engine = BehavioralCrisisEngine()
        
        pulse = engine.get_community_trauma_pulse(time_window_hours=72)
        
        assert pulse is not None
        assert hasattr(pulse, "recommended_interventions")
        assert isinstance(pulse.recommended_interventions, list)
    
    def test_time_window_parameter(self):
        """Test different time windows work"""
        from backend.app.human_intel.behavioral_crisis_engine import BehavioralCrisisEngine
        
        engine = BehavioralCrisisEngine()
        
        pulse_24h = engine.get_community_trauma_pulse(time_window_hours=24)
        pulse_72h = engine.get_community_trauma_pulse(time_window_hours=72)
        pulse_168h = engine.get_community_trauma_pulse(time_window_hours=168)
        
        assert pulse_24h is not None
        assert pulse_72h is not None
        assert pulse_168h is not None
