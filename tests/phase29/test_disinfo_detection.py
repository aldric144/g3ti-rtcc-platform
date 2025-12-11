"""
Test Suite 9: Disinformation Detection Tests

Tests for disinformation and rumor detection.
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))


class TestDisinfoDetection:
    """Tests for disinformation detection functionality"""
    
    def test_engine_initialization(self):
        """Test engine initializes correctly"""
        from backend.app.cyber_intel.info_warfare_engine import InfoWarfareEngine
        
        engine = InfoWarfareEngine()
        
        assert engine is not None
        assert engine.agency_config["ori"] == "FL0500400"
        assert engine.agency_config["name"] == "Riviera Beach Police Department"
    
    def test_singleton_pattern(self):
        """Test engine follows singleton pattern"""
        from backend.app.cyber_intel.info_warfare_engine import InfoWarfareEngine
        
        engine1 = InfoWarfareEngine()
        engine2 = InfoWarfareEngine()
        
        assert engine1 is engine2
    
    def test_disinfo_type_enum(self):
        """Test DisinfoType enum values"""
        from backend.app.cyber_intel.info_warfare_engine import DisinfoType
        
        assert DisinfoType.VIRAL_FALSE_POST is not None
        assert DisinfoType.COORDINATED_PANIC is not None
        assert DisinfoType.EMERGENCY_HOAX is not None
        assert DisinfoType.FAKE_POLICE_PAGE is not None
        assert DisinfoType.BOT_NETWORK is not None
    
    def test_disinfo_severity_enum(self):
        """Test DisinfoSeverity enum values"""
        from backend.app.cyber_intel.info_warfare_engine import DisinfoSeverity
        
        assert DisinfoSeverity.INFORMATIONAL.value == 1
        assert DisinfoSeverity.LOW.value == 2
        assert DisinfoSeverity.MEDIUM.value == 3
        assert DisinfoSeverity.HIGH.value == 4
        assert DisinfoSeverity.EMERGENCY.value == 5
    
    def test_disinfo_source_enum(self):
        """Test DisinfoSource enum values"""
        from backend.app.cyber_intel.info_warfare_engine import DisinfoSource
        
        assert DisinfoSource.FACEBOOK is not None
        assert DisinfoSource.TWITTER_X is not None
        assert DisinfoSource.INSTAGRAM is not None
        assert DisinfoSource.TIKTOK is not None
        assert DisinfoSource.NEXTDOOR is not None
        assert DisinfoSource.TELEGRAM is not None
    
    def test_detect_viral_false_post(self):
        """Test viral false post detection"""
        from backend.app.cyber_intel.info_warfare_engine import (
            InfoWarfareEngine, DisinfoType
        )
        
        engine = InfoWarfareEngine()
        
        alert = engine.detect_rumor_panic(
            source_platform="FACEBOOK",
            content="BREAKING: Active shooter at Riviera Beach Mall!",
            share_count=5000,
            viral_velocity=0.8,
        )
        
        assert alert is not None
        assert alert.disinfo_type == DisinfoType.VIRAL_FALSE_POST
    
    def test_detect_emergency_hoax(self):
        """Test emergency hoax detection"""
        from backend.app.cyber_intel.info_warfare_engine import (
            InfoWarfareEngine, DisinfoType
        )
        
        engine = InfoWarfareEngine()
        
        alert = engine.detect_rumor_panic(
            source_platform="TWITTER_X",
            content="URGENT: Evacuation order for all of Riviera Beach!",
            share_count=10000,
            viral_velocity=0.9,
            panic_keywords=["evacuation", "urgent", "emergency"],
        )
        
        assert alert is not None
        assert alert.disinfo_type == DisinfoType.EMERGENCY_HOAX
    
    def test_detect_coordinated_panic(self):
        """Test coordinated panic campaign detection"""
        from backend.app.cyber_intel.info_warfare_engine import (
            InfoWarfareEngine, DisinfoType
        )
        
        engine = InfoWarfareEngine()
        
        alert = engine.detect_rumor_panic(
            source_platform="TELEGRAM",
            content="Multiple attacks happening across the city!",
            share_count=8000,
            viral_velocity=0.85,
            coordinated_accounts=["account1", "account2", "account3"],
        )
        
        assert alert is not None
        assert alert.disinfo_type == DisinfoType.COORDINATED_PANIC
    
    def test_rumor_alert_dataclass(self):
        """Test RumorAlert dataclass structure"""
        from backend.app.cyber_intel.info_warfare_engine import (
            RumorAlert, DisinfoType, DisinfoSeverity, DisinfoSource
        )
        
        alert = RumorAlert(
            alert_id="rumor-123",
            timestamp=datetime.utcnow(),
            disinfo_type=DisinfoType.VIRAL_FALSE_POST,
            severity=DisinfoSeverity.HIGH,
            source_platform=DisinfoSource.FACEBOOK,
            content_summary="False active shooter claim",
        )
        
        assert alert.alert_id == "rumor-123"
        assert alert.disinfo_type == DisinfoType.VIRAL_FALSE_POST
        assert alert.source_platform == DisinfoSource.FACEBOOK
    
    def test_rumor_chain_of_custody(self):
        """Test rumor alert has chain of custody hash"""
        from backend.app.cyber_intel.info_warfare_engine import InfoWarfareEngine
        
        engine = InfoWarfareEngine()
        
        alert = engine.detect_rumor_panic(
            source_platform="FACEBOOK",
            content="False emergency alert",
            share_count=3000,
            viral_velocity=0.7,
        )
        
        assert alert is not None
        assert alert.chain_of_custody_hash is not None
        assert len(alert.chain_of_custody_hash) == 64
    
    def test_viral_velocity_tracking(self):
        """Test viral velocity tracking"""
        from backend.app.cyber_intel.info_warfare_engine import InfoWarfareEngine
        
        engine = InfoWarfareEngine()
        
        alert = engine.detect_rumor_panic(
            source_platform="TIKTOK",
            content="Viral misinformation",
            share_count=20000,
            viral_velocity=0.95,
        )
        
        assert alert is not None
        assert alert.viral_velocity == 0.95
    
    def test_reach_estimate(self):
        """Test reach estimate calculation"""
        from backend.app.cyber_intel.info_warfare_engine import InfoWarfareEngine
        
        engine = InfoWarfareEngine()
        
        alert = engine.detect_rumor_panic(
            source_platform="INSTAGRAM",
            content="Misleading post",
            share_count=15000,
            viral_velocity=0.8,
        )
        
        assert alert is not None
        assert alert.reach_estimate > 0
    
    def test_community_tension_score(self):
        """Test community tension score"""
        from backend.app.cyber_intel.info_warfare_engine import InfoWarfareEngine
        
        engine = InfoWarfareEngine()
        
        alert = engine.detect_rumor_panic(
            source_platform="NEXTDOOR",
            content="Inflammatory community post",
            share_count=5000,
            viral_velocity=0.75,
            community_tension_indicators=["racial", "police", "violence"],
        )
        
        assert alert is not None
        assert alert.community_tension_score >= 0.0
        assert alert.community_tension_score <= 1.0
    
    def test_get_disinfo_assessment(self):
        """Test disinformation assessment retrieval"""
        from backend.app.cyber_intel.info_warfare_engine import InfoWarfareEngine
        
        engine = InfoWarfareEngine()
        assessment = engine.get_disinfo_assessment()
        
        assert assessment is not None
        assert assessment.assessment_id is not None
        assert assessment.timestamp is not None
    
    def test_get_statistics(self):
        """Test statistics retrieval"""
        from backend.app.cyber_intel.info_warfare_engine import InfoWarfareEngine
        
        engine = InfoWarfareEngine()
        stats = engine.get_statistics()
        
        assert "total_rumor_alerts" in stats
        assert "total_impersonation_alerts" in stats
        assert "total_election_threats" in stats
        assert "total_crisis_manipulations" in stats
