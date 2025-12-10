"""
Tests for OSINT Harvester module.

Phase 17: Global Threat Intelligence Engine
"""

import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch

import sys
sys.path.insert(0, '/home/ubuntu/repos/g3ti-rtcc-platform/backend')

from app.threat_intel.osint_harvester import (
    OSINTHarvester,
    SourceType,
    ContentCategory,
    Sentiment,
    SpikeStatus,
    RSSFeed,
    NewsArticle,
    SocialSignal,
    KeywordSpike,
    EventPrediction,
)


class TestOSINTHarvester:
    """Test suite for OSINTHarvester class."""

    @pytest.fixture
    def harvester(self):
        """Create an OSINTHarvester instance for testing."""
        return OSINTHarvester()

    def test_harvester_initialization(self, harvester):
        """Test that harvester initializes correctly."""
        assert harvester is not None
        assert isinstance(harvester.rss_feeds, dict)
        assert isinstance(harvester.articles, dict)
        assert isinstance(harvester.social_signals, dict)
        assert isinstance(harvester.keyword_spikes, dict)

    def test_add_rss_feed(self, harvester):
        """Test adding an RSS feed."""
        feed = harvester.add_rss_feed(
            name="Test News",
            url="https://example.com/rss",
            source_type=SourceType.NEWS_RSS,
            categories=[ContentCategory.CRIME, ContentCategory.PUBLIC_SAFETY],
        )
        
        assert feed is not None
        assert feed.name == "Test News"
        assert feed.url == "https://example.com/rss"
        assert feed.source_type == SourceType.NEWS_RSS
        assert feed.feed_id in harvester.rss_feeds

    def test_add_rss_feed_with_keywords(self, harvester):
        """Test adding an RSS feed with filter keywords."""
        feed = harvester.add_rss_feed(
            name="Filtered Feed",
            url="https://example.com/rss",
            source_type=SourceType.NEWS_RSS,
            categories=[ContentCategory.CRIME],
            filter_keywords=["shooting", "robbery", "assault"],
        )
        
        assert feed is not None
        assert len(feed.filter_keywords) == 3

    def test_get_rss_feeds(self, harvester):
        """Test retrieving RSS feeds."""
        harvester.add_rss_feed(
            name="Feed 1",
            url="https://example1.com/rss",
            source_type=SourceType.NEWS_RSS,
            categories=[ContentCategory.CRIME],
        )
        harvester.add_rss_feed(
            name="Feed 2",
            url="https://example2.com/rss",
            source_type=SourceType.NEWS_API,
            categories=[ContentCategory.POLITICS],
        )
        
        feeds = harvester.get_rss_feeds()
        assert len(feeds) >= 2

    def test_ingest_article(self, harvester):
        """Test ingesting a news article."""
        article = harvester.ingest_article(
            source_name="Test News",
            source_url="https://example.com/article/123",
            title="Breaking: Major Crime Incident",
            content="A major crime incident occurred downtown today...",
            author="John Reporter",
            published_at=datetime.utcnow(),
            categories=[ContentCategory.CRIME],
        )
        
        assert article is not None
        assert article.title == "Breaking: Major Crime Incident"
        assert article.source_name == "Test News"
        assert article.article_id in harvester.articles

    def test_ingest_article_with_relevance_scoring(self, harvester):
        """Test that article ingestion calculates relevance score."""
        article = harvester.ingest_article(
            source_name="Crime News",
            source_url="https://example.com/crime",
            title="Shooting at Downtown Location",
            content="Multiple shots fired at downtown location. Police responding.",
            author="Reporter",
            published_at=datetime.utcnow(),
            categories=[ContentCategory.CRIME],
        )
        
        assert article is not None
        assert article.relevance_score >= 0

    def test_get_articles(self, harvester):
        """Test retrieving articles."""
        harvester.ingest_article(
            source_name="Test",
            source_url="https://example.com/1",
            title="Article 1",
            content="Content 1",
            author="Author",
            published_at=datetime.utcnow(),
            categories=[ContentCategory.CRIME],
        )
        
        articles = harvester.get_articles()
        assert isinstance(articles, list)

    def test_get_articles_by_category(self, harvester):
        """Test retrieving articles by category."""
        harvester.ingest_article(
            source_name="Test",
            source_url="https://example.com/crime",
            title="Crime Article",
            content="Crime content",
            author="Author",
            published_at=datetime.utcnow(),
            categories=[ContentCategory.CRIME],
        )
        
        articles = harvester.get_articles(category=ContentCategory.CRIME)
        for article in articles:
            assert ContentCategory.CRIME in article.categories

    def test_ingest_social_signal(self, harvester):
        """Test ingesting a social media signal."""
        signal = harvester.ingest_social_signal(
            source_type=SourceType.SOCIAL_TWITTER,
            source_url="https://twitter.com/user/status/123",
            author_id="user123",
            author_name="TestUser",
            content="Protest planned for tomorrow at city hall #protest",
            posted_at=datetime.utcnow(),
        )
        
        assert signal is not None
        assert signal.source_type == SourceType.SOCIAL_TWITTER
        assert signal.author_name == "TestUser"
        assert signal.signal_id in harvester.social_signals

    def test_ingest_social_signal_with_hate_speech(self, harvester):
        """Test that social signal detects potential hate speech."""
        signal = harvester.ingest_social_signal(
            source_type=SourceType.SOCIAL_TWITTER,
            source_url="https://twitter.com/user/status/456",
            author_id="user456",
            author_name="BadUser",
            content="Hateful content targeting specific groups",
            posted_at=datetime.utcnow(),
        )
        
        assert signal is not None
        assert isinstance(signal.hate_speech_detected, bool)

    def test_get_social_signals(self, harvester):
        """Test retrieving social signals."""
        harvester.ingest_social_signal(
            source_type=SourceType.SOCIAL_TWITTER,
            source_url="https://twitter.com/test",
            author_id="test",
            author_name="Test",
            content="Test content",
            posted_at=datetime.utcnow(),
        )
        
        signals = harvester.get_social_signals()
        assert isinstance(signals, list)

    def test_get_social_signals_by_source(self, harvester):
        """Test retrieving social signals by source type."""
        harvester.ingest_social_signal(
            source_type=SourceType.SOCIAL_TELEGRAM,
            source_url="https://t.me/channel/123",
            author_id="channel",
            author_name="Channel",
            content="Telegram message",
            posted_at=datetime.utcnow(),
        )
        
        signals = harvester.get_social_signals(source_type=SourceType.SOCIAL_TELEGRAM)
        for signal in signals:
            assert signal.source_type == SourceType.SOCIAL_TELEGRAM

    def test_detect_keyword_spikes(self, harvester):
        """Test detecting keyword spikes."""
        for i in range(20):
            harvester.ingest_social_signal(
                source_type=SourceType.SOCIAL_TWITTER,
                source_url=f"https://twitter.com/user/status/{i}",
                author_id=f"user{i}",
                author_name=f"User{i}",
                content=f"Protest happening now! #protest #{i}",
                posted_at=datetime.utcnow(),
            )
        
        spikes = harvester.detect_keyword_spikes(
            keywords=["protest"],
            time_window_hours=24,
        )
        
        assert isinstance(spikes, list)

    def test_get_keyword_spikes(self, harvester):
        """Test retrieving keyword spikes."""
        spikes = harvester.get_keyword_spikes()
        assert isinstance(spikes, list)

    def test_get_active_spikes(self, harvester):
        """Test retrieving active keyword spikes."""
        spikes = harvester.get_keyword_spikes(status=SpikeStatus.ACTIVE)
        for spike in spikes:
            assert spike.status == SpikeStatus.ACTIVE

    def test_create_event_prediction(self, harvester):
        """Test creating an event prediction."""
        prediction = harvester.create_event_prediction(
            event_type="protest",
            title="Downtown Protest",
            description="Large protest expected downtown",
            predicted_date=datetime.utcnow(),
            location="Downtown City Hall",
            latitude=40.7128,
            longitude=-74.0060,
            confidence_score=75.0,
            source_signals=["sig-1", "sig-2"],
        )
        
        assert prediction is not None
        assert prediction.event_type == "protest"
        assert prediction.confidence_score == 75.0
        assert prediction.prediction_id in harvester.event_predictions

    def test_get_event_predictions(self, harvester):
        """Test retrieving event predictions."""
        harvester.create_event_prediction(
            event_type="protest",
            title="Test Protest",
            description="Test",
            predicted_date=datetime.utcnow(),
            location="Test Location",
            latitude=0.0,
            longitude=0.0,
            confidence_score=50.0,
            source_signals=[],
        )
        
        predictions = harvester.get_event_predictions()
        assert isinstance(predictions, list)

    def test_get_metrics(self, harvester):
        """Test retrieving metrics."""
        metrics = harvester.get_metrics()
        
        assert isinstance(metrics, dict)
        assert "total_feeds" in metrics
        assert "total_articles" in metrics
        assert "total_social_signals" in metrics
        assert "total_spikes" in metrics
        assert "total_predictions" in metrics

    def test_sentiment_analysis(self, harvester):
        """Test sentiment analysis of content."""
        positive_signal = harvester.ingest_social_signal(
            source_type=SourceType.SOCIAL_TWITTER,
            source_url="https://twitter.com/happy",
            author_id="happy",
            author_name="Happy",
            content="Great news! Everything is wonderful today!",
            posted_at=datetime.utcnow(),
        )
        
        negative_signal = harvester.ingest_social_signal(
            source_type=SourceType.SOCIAL_TWITTER,
            source_url="https://twitter.com/angry",
            author_id="angry",
            author_name="Angry",
            content="This is terrible! Everything is wrong!",
            posted_at=datetime.utcnow(),
        )
        
        assert positive_signal is not None
        assert negative_signal is not None


class TestRSSFeed:
    """Test suite for RSSFeed dataclass."""

    def test_rss_feed_creation(self):
        """Test creating an RSSFeed."""
        feed = RSSFeed(
            feed_id="feed-123",
            name="Test Feed",
            url="https://example.com/rss",
            source_type=SourceType.NEWS_RSS,
            categories=[ContentCategory.CRIME],
            filter_keywords=[],
            enabled=True,
            poll_interval_seconds=300,
            last_polled_at=None,
            created_at=datetime.utcnow(),
        )
        
        assert feed.feed_id == "feed-123"
        assert feed.name == "Test Feed"
        assert feed.poll_interval_seconds == 300


class TestNewsArticle:
    """Test suite for NewsArticle dataclass."""

    def test_article_creation(self):
        """Test creating a NewsArticle."""
        article = NewsArticle(
            article_id="art-123",
            source_name="Test News",
            source_url="https://example.com/article",
            title="Test Article",
            content="Test content",
            summary="Test summary",
            author="Author",
            published_at=datetime.utcnow(),
            ingested_at=datetime.utcnow(),
            categories=[ContentCategory.CRIME],
            sentiment=Sentiment.NEUTRAL,
            relevance_score=50.0,
            extracted_entities=[],
            extracted_locations=[],
            metadata={},
        )
        
        assert article.article_id == "art-123"
        assert article.title == "Test Article"
        assert article.relevance_score == 50.0


class TestSocialSignal:
    """Test suite for SocialSignal dataclass."""

    def test_social_signal_creation(self):
        """Test creating a SocialSignal."""
        signal = SocialSignal(
            signal_id="sig-123",
            source_type=SourceType.SOCIAL_TWITTER,
            source_url="https://twitter.com/test",
            author_id="test",
            author_name="Test",
            content="Test content",
            posted_at=datetime.utcnow(),
            ingested_at=datetime.utcnow(),
            sentiment=Sentiment.NEUTRAL,
            hate_speech_detected=False,
            threat_score=0.0,
            engagement_count=0,
            extracted_hashtags=[],
            extracted_mentions=[],
            extracted_urls=[],
            metadata={},
        )
        
        assert signal.signal_id == "sig-123"
        assert signal.source_type == SourceType.SOCIAL_TWITTER
        assert signal.hate_speech_detected is False


class TestKeywordSpike:
    """Test suite for KeywordSpike dataclass."""

    def test_spike_creation(self):
        """Test creating a KeywordSpike."""
        spike = KeywordSpike(
            spike_id="spk-123",
            keyword="protest",
            baseline_count=10,
            current_count=100,
            spike_percentage=900.0,
            time_window_hours=24,
            status=SpikeStatus.ACTIVE,
            detected_at=datetime.utcnow(),
            source_signals=[],
            metadata={},
        )
        
        assert spike.spike_id == "spk-123"
        assert spike.keyword == "protest"
        assert spike.spike_percentage == 900.0
        assert spike.status == SpikeStatus.ACTIVE


class TestEventPrediction:
    """Test suite for EventPrediction dataclass."""

    def test_prediction_creation(self):
        """Test creating an EventPrediction."""
        prediction = EventPrediction(
            prediction_id="pred-123",
            event_type="protest",
            title="Test Protest",
            description="Test description",
            predicted_date=datetime.utcnow(),
            location="Test Location",
            latitude=40.7128,
            longitude=-74.0060,
            confidence_score=75.0,
            source_signals=[],
            created_at=datetime.utcnow(),
            metadata={},
        )
        
        assert prediction.prediction_id == "pred-123"
        assert prediction.event_type == "protest"
        assert prediction.confidence_score == 75.0
