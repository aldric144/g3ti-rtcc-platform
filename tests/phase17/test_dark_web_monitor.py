"""
Tests for Dark Web Monitor module.

Phase 17: Global Threat Intelligence Engine
"""

import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch

import sys
sys.path.insert(0, '/home/ubuntu/repos/g3ti-rtcc-platform/backend')

from app.threat_intel.dark_web_monitor import (
    DarkWebMonitor,
    SignalType,
    SignalPriority,
    SignalStatus,
    MarketCategory,
    KeywordProfile,
    DarkWebSignal,
    MarketListing,
)


class TestDarkWebMonitor:
    """Test suite for DarkWebMonitor class."""

    @pytest.fixture
    def monitor(self):
        """Create a DarkWebMonitor instance for testing."""
        return DarkWebMonitor()

    def test_monitor_initialization(self, monitor):
        """Test that monitor initializes correctly."""
        assert monitor is not None
        assert isinstance(monitor.keyword_profiles, dict)
        assert isinstance(monitor.signals, dict)
        assert isinstance(monitor.market_listings, dict)

    def test_add_keyword_profile(self, monitor):
        """Test adding a keyword profile."""
        profile = monitor.add_keyword_profile(
            name="Test Profile",
            keywords=["weapon", "gun", "firearm"],
            signal_type=SignalType.WEAPONS_TRAFFICKING,
            priority=SignalPriority.HIGH,
        )
        
        assert profile is not None
        assert profile.name == "Test Profile"
        assert "weapon" in profile.keywords
        assert profile.signal_type == SignalType.WEAPONS_TRAFFICKING
        assert profile.priority == SignalPriority.HIGH
        assert profile.profile_id in monitor.keyword_profiles

    def test_add_keyword_profile_with_patterns(self, monitor):
        """Test adding a keyword profile with regex patterns."""
        profile = monitor.add_keyword_profile(
            name="Pattern Profile",
            keywords=["test"],
            signal_type=SignalType.CYBER_THREATS,
            priority=SignalPriority.MEDIUM,
            patterns=[r"\d{3}-\d{2}-\d{4}"],  # SSN pattern
        )
        
        assert profile is not None
        assert len(profile.patterns) == 1

    def test_get_keyword_profiles(self, monitor):
        """Test retrieving keyword profiles."""
        monitor.add_keyword_profile(
            name="Profile 1",
            keywords=["test1"],
            signal_type=SignalType.GENERAL,
            priority=SignalPriority.LOW,
        )
        monitor.add_keyword_profile(
            name="Profile 2",
            keywords=["test2"],
            signal_type=SignalType.GENERAL,
            priority=SignalPriority.MEDIUM,
        )
        
        profiles = monitor.get_keyword_profiles()
        assert len(profiles) >= 2

    def test_analyze_content_no_matches(self, monitor):
        """Test analyzing content with no keyword matches."""
        signal = monitor.analyze_content(
            content="This is a normal message with no threats.",
            source_url="http://example.onion/page",
            source_name="Test Source",
        )
        
        assert signal is None or signal.priority == SignalPriority.LOW

    def test_analyze_content_with_matches(self, monitor):
        """Test analyzing content with keyword matches."""
        monitor.add_keyword_profile(
            name="Weapons Profile",
            keywords=["weapon", "gun", "firearm", "ammunition"],
            signal_type=SignalType.WEAPONS_TRAFFICKING,
            priority=SignalPriority.CRITICAL,
        )
        
        signal = monitor.analyze_content(
            content="Selling weapons and ammunition. Contact for gun deals.",
            source_url="http://market.onion/listing",
            source_name="Dark Market",
        )
        
        assert signal is not None
        assert signal.signal_type == SignalType.WEAPONS_TRAFFICKING
        assert len(signal.matched_keywords) > 0

    def test_analyze_market_listing(self, monitor):
        """Test analyzing a market listing."""
        listing = monitor.analyze_market_listing(
            title="High Quality Product",
            description="Premium quality items available",
            price=500.0,
            currency="USD",
            vendor_name="TestVendor",
            category=MarketCategory.OTHER,
            source_url="http://market.onion/item/123",
            source_name="Test Market",
        )
        
        assert listing is not None
        assert listing.title == "High Quality Product"
        assert listing.price == 500.0
        assert listing.vendor_name == "TestVendor"
        assert listing.listing_id in monitor.market_listings

    def test_analyze_market_listing_weapons(self, monitor):
        """Test analyzing a weapons market listing."""
        listing = monitor.analyze_market_listing(
            title="Glock 19 Gen 5",
            description="Brand new, never fired. Includes extra magazines.",
            price=800.0,
            currency="USD",
            vendor_name="GunDealer",
            category=MarketCategory.WEAPONS,
            source_url="http://market.onion/weapons/456",
            source_name="Arms Market",
        )
        
        assert listing is not None
        assert listing.category == MarketCategory.WEAPONS
        assert listing.threat_score > 0

    def test_get_signals(self, monitor):
        """Test retrieving signals."""
        monitor.add_keyword_profile(
            name="Test Profile",
            keywords=["threat"],
            signal_type=SignalType.GENERAL,
            priority=SignalPriority.MEDIUM,
        )
        
        monitor.analyze_content(
            content="This is a threat message.",
            source_url="http://test.onion",
            source_name="Test",
        )
        
        signals = monitor.get_signals()
        assert isinstance(signals, list)

    def test_get_signals_by_type(self, monitor):
        """Test retrieving signals filtered by type."""
        monitor.add_keyword_profile(
            name="Weapons",
            keywords=["weapon"],
            signal_type=SignalType.WEAPONS_TRAFFICKING,
            priority=SignalPriority.HIGH,
        )
        
        monitor.analyze_content(
            content="Weapon for sale",
            source_url="http://test.onion",
            source_name="Test",
        )
        
        signals = monitor.get_signals(signal_type=SignalType.WEAPONS_TRAFFICKING)
        for signal in signals:
            assert signal.signal_type == SignalType.WEAPONS_TRAFFICKING

    def test_get_signals_by_priority(self, monitor):
        """Test retrieving signals filtered by priority."""
        signals = monitor.get_signals(min_priority=SignalPriority.HIGH)
        for signal in signals:
            assert signal.priority.value >= SignalPriority.HIGH.value

    def test_get_high_priority_signals(self, monitor):
        """Test retrieving high priority signals."""
        signals = monitor.get_high_priority_signals()
        for signal in signals:
            assert signal.priority in [SignalPriority.HIGH, SignalPriority.CRITICAL]

    def test_get_market_listings(self, monitor):
        """Test retrieving market listings."""
        monitor.analyze_market_listing(
            title="Test Item",
            description="Test description",
            price=100.0,
            currency="USD",
            vendor_name="Vendor",
            category=MarketCategory.OTHER,
            source_url="http://test.onion",
            source_name="Test",
        )
        
        listings = monitor.get_market_listings()
        assert isinstance(listings, list)
        assert len(listings) >= 1

    def test_get_market_listings_by_category(self, monitor):
        """Test retrieving market listings by category."""
        monitor.analyze_market_listing(
            title="Drug Item",
            description="Test",
            price=50.0,
            currency="USD",
            vendor_name="Vendor",
            category=MarketCategory.DRUGS,
            source_url="http://test.onion",
            source_name="Test",
        )
        
        listings = monitor.get_market_listings(category=MarketCategory.DRUGS)
        for listing in listings:
            assert listing.category == MarketCategory.DRUGS

    def test_update_signal_status(self, monitor):
        """Test updating signal status."""
        monitor.add_keyword_profile(
            name="Test",
            keywords=["alert"],
            signal_type=SignalType.GENERAL,
            priority=SignalPriority.MEDIUM,
        )
        
        signal = monitor.analyze_content(
            content="Alert message",
            source_url="http://test.onion",
            source_name="Test",
        )
        
        if signal:
            updated = monitor.update_signal_status(
                signal.signal_id,
                SignalStatus.REVIEWED,
            )
            assert updated is True or updated is None

    def test_get_metrics(self, monitor):
        """Test retrieving metrics."""
        metrics = monitor.get_metrics()
        
        assert isinstance(metrics, dict)
        assert "total_profiles" in metrics
        assert "total_signals" in metrics
        assert "total_listings" in metrics

    def test_sentiment_scoring(self, monitor):
        """Test sentiment scoring of content."""
        monitor.add_keyword_profile(
            name="Violence",
            keywords=["kill", "attack", "bomb"],
            signal_type=SignalType.TERRORISM_RELATED,
            priority=SignalPriority.CRITICAL,
        )
        
        signal = monitor.analyze_content(
            content="Planning to attack the target. Will kill everyone.",
            source_url="http://threat.onion",
            source_name="Threat Forum",
        )
        
        if signal:
            assert signal.threat_sentiment_score > 0

    def test_entity_extraction(self, monitor):
        """Test entity extraction from content."""
        monitor.add_keyword_profile(
            name="Test",
            keywords=["meeting"],
            signal_type=SignalType.GENERAL,
            priority=SignalPriority.MEDIUM,
        )
        
        signal = monitor.analyze_content(
            content="Meeting at New York City on January 15th. Contact John Smith.",
            source_url="http://test.onion",
            source_name="Test",
        )
        
        if signal:
            assert isinstance(signal.extracted_entities, list)
            assert isinstance(signal.extracted_locations, list)


class TestKeywordProfile:
    """Test suite for KeywordProfile dataclass."""

    def test_keyword_profile_creation(self):
        """Test creating a KeywordProfile."""
        profile = KeywordProfile(
            profile_id="test-123",
            name="Test Profile",
            keywords=["test", "keyword"],
            patterns=[],
            signal_type=SignalType.GENERAL,
            priority=SignalPriority.MEDIUM,
            enabled=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        
        assert profile.profile_id == "test-123"
        assert profile.name == "Test Profile"
        assert len(profile.keywords) == 2


class TestDarkWebSignal:
    """Test suite for DarkWebSignal dataclass."""

    def test_signal_creation(self):
        """Test creating a DarkWebSignal."""
        signal = DarkWebSignal(
            signal_id="sig-123",
            signal_type=SignalType.WEAPONS_TRAFFICKING,
            priority=SignalPriority.HIGH,
            status=SignalStatus.NEW,
            source_url="http://test.onion",
            source_name="Test",
            content_hash="abc123",
            matched_keywords=["weapon"],
            matched_patterns=[],
            threat_sentiment_score=75.0,
            violence_indicator=True,
            urgency_indicator=False,
            extracted_entities=[],
            extracted_locations=[],
            raw_content="Test content",
            detected_at=datetime.utcnow(),
            metadata={},
        )
        
        assert signal.signal_id == "sig-123"
        assert signal.signal_type == SignalType.WEAPONS_TRAFFICKING
        assert signal.threat_sentiment_score == 75.0


class TestMarketListing:
    """Test suite for MarketListing dataclass."""

    def test_listing_creation(self):
        """Test creating a MarketListing."""
        listing = MarketListing(
            listing_id="list-123",
            title="Test Item",
            description="Test description",
            price=100.0,
            currency="USD",
            vendor_name="Vendor",
            vendor_rating=4.5,
            category=MarketCategory.OTHER,
            source_url="http://test.onion",
            source_name="Test Market",
            threat_score=50.0,
            detected_at=datetime.utcnow(),
            metadata={},
        )
        
        assert listing.listing_id == "list-123"
        assert listing.price == 100.0
        assert listing.category == MarketCategory.OTHER
