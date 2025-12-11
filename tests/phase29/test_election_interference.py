"""
Test Suite 10: Election Interference Detection Tests

Tests for election interference and bot network detection.
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))


class TestElectionInterference:
    """Tests for election interference detection"""
    
    def test_campaign_type_enum(self):
        """Test CampaignType enum values"""
        from backend.app.cyber_intel.info_warfare_engine import CampaignType
        
        assert CampaignType.VOTER_SUPPRESSION is not None
        assert CampaignType.CANDIDATE_SMEAR is not None
        assert CampaignType.FOREIGN_INFLUENCE is not None
        assert CampaignType.DOMESTIC_ASTROTURF is not None
    
    def test_target_audience_enum(self):
        """Test TargetAudience enum values"""
        from backend.app.cyber_intel.info_warfare_engine import TargetAudience
        
        assert TargetAudience.GENERAL_PUBLIC is not None
        assert TargetAudience.MINORITY_COMMUNITIES is not None
        assert TargetAudience.ELDERLY is not None
        assert TargetAudience.FIRST_TIME_VOTERS is not None
    
    def test_detect_bot_network(self):
        """Test bot network detection"""
        from backend.app.cyber_intel.info_warfare_engine import InfoWarfareEngine
        
        engine = InfoWarfareEngine()
        
        threat = engine.detect_election_interference(
            source_platform="TWITTER_X",
            content="Vote manipulation campaign",
            bot_indicators={
                "coordinated_posting": True,
                "similar_account_creation_dates": True,
                "identical_messaging": True,
            },
            bot_account_count=500,
        )
        
        assert threat is not None
        assert threat.bot_network_detected is True
        assert threat.bot_account_count >= 500
    
    def test_detect_voter_suppression(self):
        """Test voter suppression detection"""
        from backend.app.cyber_intel.info_warfare_engine import (
            InfoWarfareEngine, CampaignType
        )
        
        engine = InfoWarfareEngine()
        
        threat = engine.detect_election_interference(
            source_platform="FACEBOOK",
            content="Wrong voting date information",
            voter_suppression_indicators=["wrong_date", "wrong_location"],
            target_audience="MINORITY_COMMUNITIES",
        )
        
        assert threat is not None
        assert threat.campaign_type == CampaignType.VOTER_SUPPRESSION
    
    def test_detect_identity_spoofing(self):
        """Test identity spoofing detection"""
        from backend.app.cyber_intel.info_warfare_engine import InfoWarfareEngine
        
        engine = InfoWarfareEngine()
        
        threat = engine.detect_election_interference(
            source_platform="INSTAGRAM",
            content="Fake official election announcement",
            identity_spoofing=True,
            spoofed_entity="Palm Beach County Elections",
        )
        
        assert threat is not None
        assert threat.identity_spoofing is True
    
    def test_election_threat_dataclass(self):
        """Test ElectionThreat dataclass structure"""
        from backend.app.cyber_intel.info_warfare_engine import (
            ElectionThreat, DisinfoType, DisinfoSeverity, 
            DisinfoSource, CampaignType, TargetAudience
        )
        
        threat = ElectionThreat(
            threat_id="election-123",
            timestamp=datetime.utcnow(),
            disinfo_type=DisinfoType.BOT_NETWORK,
            severity=DisinfoSeverity.HIGH,
            source_platform=DisinfoSource.TWITTER_X,
            campaign_type=CampaignType.VOTER_SUPPRESSION,
            target_audience=TargetAudience.MINORITY_COMMUNITIES,
        )
        
        assert threat.threat_id == "election-123"
        assert threat.campaign_type == CampaignType.VOTER_SUPPRESSION
        assert threat.target_audience == TargetAudience.MINORITY_COMMUNITIES
    
    def test_election_chain_of_custody(self):
        """Test election threat has chain of custody hash"""
        from backend.app.cyber_intel.info_warfare_engine import InfoWarfareEngine
        
        engine = InfoWarfareEngine()
        
        threat = engine.detect_election_interference(
            source_platform="TELEGRAM",
            content="Election misinformation",
            bot_indicators={"coordinated_posting": True},
            bot_account_count=100,
        )
        
        assert threat is not None
        assert threat.chain_of_custody_hash is not None
        assert len(threat.chain_of_custody_hash) == 64
    
    def test_election_recommended_action(self):
        """Test election threat has recommended action"""
        from backend.app.cyber_intel.info_warfare_engine import InfoWarfareEngine
        
        engine = InfoWarfareEngine()
        
        threat = engine.detect_election_interference(
            source_platform="FACEBOOK",
            content="Voter suppression campaign",
            voter_suppression_indicators=["wrong_date"],
            target_audience="ELDERLY",
        )
        
        assert threat is not None
        assert threat.recommended_action is not None
        assert len(threat.recommended_action) > 0
    
    def test_foreign_influence_detection(self):
        """Test foreign influence detection"""
        from backend.app.cyber_intel.info_warfare_engine import (
            InfoWarfareEngine, CampaignType
        )
        
        engine = InfoWarfareEngine()
        
        threat = engine.detect_election_interference(
            source_platform="TWITTER_X",
            content="Foreign influence operation",
            foreign_indicators={
                "foreign_ip_addresses": True,
                "foreign_language_artifacts": True,
            },
        )
        
        assert threat is not None
        assert threat.campaign_type == CampaignType.FOREIGN_INFLUENCE
    
    def test_reach_estimate_calculation(self):
        """Test reach estimate for election threats"""
        from backend.app.cyber_intel.info_warfare_engine import InfoWarfareEngine
        
        engine = InfoWarfareEngine()
        
        threat = engine.detect_election_interference(
            source_platform="TIKTOK",
            content="Viral election misinformation",
            bot_account_count=1000,
            share_count=50000,
        )
        
        assert threat is not None
        assert threat.reach_estimate > 0
    
    def test_no_threat_for_legitimate_content(self):
        """Test no threat for legitimate election content"""
        from backend.app.cyber_intel.info_warfare_engine import InfoWarfareEngine
        
        engine = InfoWarfareEngine()
        
        threat = engine.detect_election_interference(
            source_platform="FACEBOOK",
            content="Official voting information from elections office",
            bot_indicators={},
            voter_suppression_indicators=[],
        )
        
        assert threat is None
