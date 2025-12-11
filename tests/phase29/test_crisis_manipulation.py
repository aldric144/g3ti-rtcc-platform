"""
Test Suite 11: Crisis Manipulation Detection Tests

Tests for crisis narrative manipulation detection.
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))


class TestCrisisManipulation:
    """Tests for crisis manipulation detection"""
    
    def test_detect_fake_crime_spike(self):
        """Test detection of fake crime spike claims"""
        from backend.app.cyber_intel.info_warfare_engine import InfoWarfareEngine
        
        engine = InfoWarfareEngine()
        
        manipulation = engine.detect_crisis_manipulation(
            source_platform="NEXTDOOR",
            content="Crime is out of control! 10 murders this week!",
            crisis_type="FAKE_CRIME_SPIKE",
            false_statistics=True,
        )
        
        assert manipulation is not None
        assert manipulation.crisis_type == "FAKE_CRIME_SPIKE"
    
    def test_detect_false_ois_claim(self):
        """Test detection of false officer-involved shooting claims"""
        from backend.app.cyber_intel.info_warfare_engine import InfoWarfareEngine
        
        engine = InfoWarfareEngine()
        
        manipulation = engine.detect_crisis_manipulation(
            source_platform="TWITTER_X",
            content="RBPD just shot an unarmed person at the park!",
            crisis_type="FALSE_OIS_CLAIM",
            officer_involved=True,
        )
        
        assert manipulation is not None
        assert manipulation.crisis_type == "FALSE_OIS_CLAIM"
    
    def test_detect_anti_police_wave(self):
        """Test detection of anti-police disinformation wave"""
        from backend.app.cyber_intel.info_warfare_engine import InfoWarfareEngine
        
        engine = InfoWarfareEngine()
        
        manipulation = engine.detect_crisis_manipulation(
            source_platform="FACEBOOK",
            content="Coordinated anti-police campaign",
            crisis_type="ANTI_POLICE_WAVE",
            coordinated_accounts=["account1", "account2", "account3"],
            share_count=10000,
        )
        
        assert manipulation is not None
        assert manipulation.crisis_type == "ANTI_POLICE_WAVE"
    
    def test_community_tension_score(self):
        """Test community tension score calculation"""
        from backend.app.cyber_intel.info_warfare_engine import InfoWarfareEngine
        
        engine = InfoWarfareEngine()
        
        manipulation = engine.detect_crisis_manipulation(
            source_platform="INSTAGRAM",
            content="Inflammatory community content",
            crisis_type="COMMUNITY_TENSION",
            tension_indicators=["racial", "violence", "protest"],
        )
        
        assert manipulation is not None
        assert manipulation.community_tension_score >= 0.0
        assert manipulation.community_tension_score <= 1.0
    
    def test_public_safety_impact(self):
        """Test public safety impact assessment"""
        from backend.app.cyber_intel.info_warfare_engine import InfoWarfareEngine
        
        engine = InfoWarfareEngine()
        
        manipulation = engine.detect_crisis_manipulation(
            source_platform="TELEGRAM",
            content="False emergency causing panic",
            crisis_type="EMERGENCY_HOAX",
            public_safety_indicators=["evacuation", "panic", "emergency"],
        )
        
        assert manipulation is not None
        assert manipulation.public_safety_impact is not None
    
    def test_crisis_manipulation_dataclass(self):
        """Test CrisisManipulation dataclass structure"""
        from backend.app.cyber_intel.info_warfare_engine import (
            CrisisManipulation, DisinfoType, DisinfoSeverity, DisinfoSource
        )
        
        manipulation = CrisisManipulation(
            manipulation_id="crisis-123",
            timestamp=datetime.utcnow(),
            disinfo_type=DisinfoType.VIRAL_FALSE_POST,
            severity=DisinfoSeverity.HIGH,
            source_platform=DisinfoSource.FACEBOOK,
            crisis_type="FAKE_CRIME_SPIKE",
        )
        
        assert manipulation.manipulation_id == "crisis-123"
        assert manipulation.crisis_type == "FAKE_CRIME_SPIKE"
    
    def test_crisis_chain_of_custody(self):
        """Test crisis manipulation has chain of custody hash"""
        from backend.app.cyber_intel.info_warfare_engine import InfoWarfareEngine
        
        engine = InfoWarfareEngine()
        
        manipulation = engine.detect_crisis_manipulation(
            source_platform="TWITTER_X",
            content="False crisis claim",
            crisis_type="FAKE_EMERGENCY",
        )
        
        assert manipulation is not None
        assert manipulation.chain_of_custody_hash is not None
        assert len(manipulation.chain_of_custody_hash) == 64
    
    def test_crisis_recommended_action(self):
        """Test crisis manipulation has recommended action"""
        from backend.app.cyber_intel.info_warfare_engine import InfoWarfareEngine
        
        engine = InfoWarfareEngine()
        
        manipulation = engine.detect_crisis_manipulation(
            source_platform="FACEBOOK",
            content="Dangerous misinformation",
            crisis_type="PUBLIC_SAFETY_THREAT",
            public_safety_indicators=["danger", "threat", "warning"],
        )
        
        assert manipulation is not None
        assert manipulation.recommended_action is not None
        assert len(manipulation.recommended_action) > 0
    
    def test_track_narrative(self):
        """Test narrative tracking functionality"""
        from backend.app.cyber_intel.info_warfare_engine import InfoWarfareEngine
        
        engine = InfoWarfareEngine()
        
        result = engine.track_narrative(
            narrative="crime_spike_claims",
            keywords=["crime", "spike", "dangerous"],
            platforms=["FACEBOOK", "NEXTDOOR"],
        )
        
        assert result is True
    
    def test_register_official_account(self):
        """Test official account registration"""
        from backend.app.cyber_intel.info_warfare_engine import InfoWarfareEngine
        
        engine = InfoWarfareEngine()
        
        result = engine.register_official_account(
            platform="FACEBOOK",
            account_id="RivieraBeachPD",
            account_name="Riviera Beach Police Department",
        )
        
        assert result is True
    
    def test_no_manipulation_for_legitimate_content(self):
        """Test no manipulation for legitimate crisis reporting"""
        from backend.app.cyber_intel.info_warfare_engine import InfoWarfareEngine
        
        engine = InfoWarfareEngine()
        
        manipulation = engine.detect_crisis_manipulation(
            source_platform="FACEBOOK",
            content="Official RBPD statement on recent incident",
            crisis_type=None,
            official_source=True,
        )
        
        assert manipulation is None
