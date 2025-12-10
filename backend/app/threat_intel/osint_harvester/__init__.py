"""
OSINT Harvester Module

Provides capabilities for:
- News ingestion pipeline (RSS + API stubs)
- Social keyword spike detection
- Hate speech classification (stubbed)
- Protest/event prediction signals
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Optional
import uuid
import hashlib
import re
from collections import defaultdict


class SourceType(Enum):
    """Types of OSINT sources"""
    NEWS_RSS = "news_rss"
    NEWS_API = "news_api"
    SOCIAL_TWITTER = "social_twitter"
    SOCIAL_FACEBOOK = "social_facebook"
    SOCIAL_REDDIT = "social_reddit"
    SOCIAL_TELEGRAM = "social_telegram"
    FORUM = "forum"
    BLOG = "blog"
    GOVERNMENT = "government"
    PRESS_RELEASE = "press_release"
    POLICE_SCANNER = "police_scanner"
    PUBLIC_RECORDS = "public_records"


class ContentCategory(Enum):
    """Categories of OSINT content"""
    CRIME = "crime"
    TERRORISM = "terrorism"
    PROTEST = "protest"
    CIVIL_UNREST = "civil_unrest"
    NATURAL_DISASTER = "natural_disaster"
    PUBLIC_SAFETY = "public_safety"
    GANG_ACTIVITY = "gang_activity"
    DRUG_ACTIVITY = "drug_activity"
    CYBERSECURITY = "cybersecurity"
    POLITICAL = "political"
    ECONOMIC = "economic"
    HEALTH = "health"
    INFRASTRUCTURE = "infrastructure"
    OTHER = "other"


class SentimentType(Enum):
    """Sentiment types for content"""
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    THREATENING = "threatening"
    HATEFUL = "hateful"


class SpikeStatus(Enum):
    """Status of keyword spikes"""
    EMERGING = "emerging"
    ACTIVE = "active"
    DECLINING = "declining"
    RESOLVED = "resolved"


class EventLikelihood(Enum):
    """Likelihood levels for predicted events"""
    UNLIKELY = "unlikely"
    POSSIBLE = "possible"
    LIKELY = "likely"
    HIGHLY_LIKELY = "highly_likely"
    IMMINENT = "imminent"


class HateSpeechCategory(Enum):
    """Categories of hate speech"""
    RACIAL = "racial"
    RELIGIOUS = "religious"
    GENDER = "gender"
    SEXUAL_ORIENTATION = "sexual_orientation"
    DISABILITY = "disability"
    NATIONAL_ORIGIN = "national_origin"
    POLITICAL = "political"
    OTHER = "other"


@dataclass
class NewsArticle:
    """A news article from OSINT sources"""
    article_id: str = ""
    source_type: SourceType = SourceType.NEWS_RSS
    source_name: str = ""
    source_url: str = ""
    title: str = ""
    content: str = ""
    summary: str = ""
    author: str = ""
    published_at: datetime = field(default_factory=datetime.utcnow)
    collected_at: datetime = field(default_factory=datetime.utcnow)
    category: ContentCategory = ContentCategory.OTHER
    sentiment: SentimentType = SentimentType.NEUTRAL
    keywords: list[str] = field(default_factory=list)
    entities: list[str] = field(default_factory=list)
    locations: list[str] = field(default_factory=list)
    relevance_score: float = 0.0
    jurisdiction_codes: list[str] = field(default_factory=list)
    content_hash: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.article_id:
            self.article_id = f"article-{uuid.uuid4().hex[:12]}"
        if not self.content_hash and self.content:
            self.content_hash = hashlib.sha256(self.content.encode()).hexdigest()[:16]


@dataclass
class SocialSignal:
    """A signal from social media monitoring"""
    signal_id: str = ""
    source_type: SourceType = SourceType.SOCIAL_TWITTER
    platform_id: str = ""
    author_id: str = ""
    author_name: str = ""
    author_followers: int = 0
    content: str = ""
    engagement_count: int = 0
    share_count: int = 0
    reply_count: int = 0
    sentiment: SentimentType = SentimentType.NEUTRAL
    hate_speech_detected: bool = False
    hate_speech_category: Optional[HateSpeechCategory] = None
    hate_speech_confidence: float = 0.0
    keywords: list[str] = field(default_factory=list)
    hashtags: list[str] = field(default_factory=list)
    mentions: list[str] = field(default_factory=list)
    urls: list[str] = field(default_factory=list)
    locations: list[str] = field(default_factory=list)
    threat_score: float = 0.0
    posted_at: datetime = field(default_factory=datetime.utcnow)
    collected_at: datetime = field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.signal_id:
            self.signal_id = f"social-{uuid.uuid4().hex[:12]}"


@dataclass
class KeywordSpike:
    """A detected spike in keyword activity"""
    spike_id: str = ""
    keyword: str = ""
    baseline_count: int = 0
    current_count: int = 0
    spike_percentage: float = 0.0
    status: SpikeStatus = SpikeStatus.EMERGING
    sources: list[str] = field(default_factory=list)
    sample_content: list[str] = field(default_factory=list)
    related_keywords: list[str] = field(default_factory=list)
    locations: list[str] = field(default_factory=list)
    first_detected: datetime = field(default_factory=datetime.utcnow)
    last_updated: datetime = field(default_factory=datetime.utcnow)
    peak_time: Optional[datetime] = None
    peak_count: int = 0
    threat_assessment: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.spike_id:
            self.spike_id = f"spike-{uuid.uuid4().hex[:12]}"


@dataclass
class EventPrediction:
    """A predicted event based on OSINT analysis"""
    prediction_id: str = ""
    event_type: str = ""
    title: str = ""
    description: str = ""
    likelihood: EventLikelihood = EventLikelihood.POSSIBLE
    confidence_score: float = 0.0
    predicted_date_start: Optional[datetime] = None
    predicted_date_end: Optional[datetime] = None
    predicted_location: str = ""
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    radius_meters: int = 0
    supporting_signals: list[str] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)
    estimated_participants: int = 0
    risk_level: str = "low"
    recommended_actions: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.prediction_id:
            self.prediction_id = f"pred-{uuid.uuid4().hex[:12]}"


@dataclass
class RSSFeed:
    """Configuration for an RSS feed"""
    feed_id: str = ""
    name: str = ""
    url: str = ""
    category: ContentCategory = ContentCategory.OTHER
    enabled: bool = True
    poll_interval_minutes: int = 15
    last_polled: Optional[datetime] = None
    last_item_id: str = ""
    jurisdiction_codes: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        if not self.feed_id:
            self.feed_id = f"feed-{uuid.uuid4().hex[:12]}"


class OSINTHarvester:
    """
    OSINT Harvester for open source intelligence gathering.
    
    Monitors news, social media, forums, and other public sources
    for threat indicators and event predictions.
    """

    def __init__(self):
        self._articles: dict[str, NewsArticle] = {}
        self._social_signals: dict[str, SocialSignal] = {}
        self._keyword_spikes: dict[str, KeywordSpike] = {}
        self._event_predictions: dict[str, EventPrediction] = {}
        self._rss_feeds: dict[str, RSSFeed] = {}
        self._keyword_counts: dict[str, list[tuple[datetime, int]]] = defaultdict(list)
        self._callbacks: list[Callable[[Any], None]] = []
        self._events: list[dict[str, Any]] = []
        
        self._monitored_keywords = [
            "protest", "rally", "march", "demonstration", "riot",
            "shooting", "gunfire", "shots fired", "active shooter",
            "bomb threat", "suspicious package", "evacuation",
            "gang", "cartel", "trafficking", "smuggling",
            "threat", "attack", "violence", "assault",
        ]
        
        self._hate_speech_indicators = [
            "kill all", "death to", "exterminate", "genocide",
            "inferior race", "subhuman", "vermin", "parasites",
        ]

    def register_callback(self, callback: Callable[[Any], None]) -> None:
        """Register a callback for new signals"""
        self._callbacks.append(callback)

    def _notify_callbacks(self, data: Any) -> None:
        """Notify all registered callbacks"""
        for callback in self._callbacks:
            try:
                callback(data)
            except Exception:
                pass

    def _record_event(self, event_type: str, data: dict[str, Any]) -> None:
        """Record an event for audit purposes"""
        self._events.append({
            "event_type": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data,
        })

    def add_rss_feed(
        self,
        name: str,
        url: str,
        category: ContentCategory = ContentCategory.OTHER,
        poll_interval_minutes: int = 15,
        jurisdiction_codes: Optional[list[str]] = None,
    ) -> RSSFeed:
        """Add an RSS feed for monitoring"""
        feed = RSSFeed(
            name=name,
            url=url,
            category=category,
            poll_interval_minutes=poll_interval_minutes,
            jurisdiction_codes=jurisdiction_codes or [],
        )
        self._rss_feeds[feed.feed_id] = feed
        self._record_event("rss_feed_added", {"feed_id": feed.feed_id})
        return feed

    def get_rss_feed(self, feed_id: str) -> Optional[RSSFeed]:
        """Get an RSS feed by ID"""
        return self._rss_feeds.get(feed_id)

    def get_all_rss_feeds(self) -> list[RSSFeed]:
        """Get all RSS feeds"""
        return list(self._rss_feeds.values())

    def remove_rss_feed(self, feed_id: str) -> bool:
        """Remove an RSS feed"""
        if feed_id in self._rss_feeds:
            del self._rss_feeds[feed_id]
            self._record_event("rss_feed_removed", {"feed_id": feed_id})
            return True
        return False

    def ingest_news_article(
        self,
        title: str,
        content: str,
        source_name: str,
        source_url: str = "",
        source_type: SourceType = SourceType.NEWS_RSS,
        author: str = "",
        published_at: Optional[datetime] = None,
    ) -> NewsArticle:
        """Ingest and analyze a news article"""
        keywords = self._extract_keywords(f"{title} {content}")
        entities = self._extract_entities(content)
        locations = self._extract_locations(content)
        category = self._categorize_content(f"{title} {content}")
        sentiment = self._analyze_sentiment(content)
        relevance_score = self._calculate_relevance(keywords, category)
        
        article = NewsArticle(
            source_type=source_type,
            source_name=source_name,
            source_url=source_url,
            title=title,
            content=content,
            summary=content[:300] if len(content) > 300 else content,
            author=author,
            published_at=published_at or datetime.utcnow(),
            category=category,
            sentiment=sentiment,
            keywords=keywords,
            entities=entities,
            locations=locations,
            relevance_score=relevance_score,
        )
        
        self._articles[article.article_id] = article
        self._update_keyword_counts(keywords)
        self._record_event("article_ingested", {"article_id": article.article_id})
        self._notify_callbacks(article)
        
        return article

    def ingest_social_signal(
        self,
        content: str,
        source_type: SourceType = SourceType.SOCIAL_TWITTER,
        platform_id: str = "",
        author_id: str = "",
        author_name: str = "",
        author_followers: int = 0,
        engagement_count: int = 0,
        posted_at: Optional[datetime] = None,
    ) -> SocialSignal:
        """Ingest and analyze a social media signal"""
        keywords = self._extract_keywords(content)
        hashtags = self._extract_hashtags(content)
        mentions = self._extract_mentions(content)
        urls = self._extract_urls(content)
        locations = self._extract_locations(content)
        sentiment = self._analyze_sentiment(content)
        
        hate_detected, hate_category, hate_confidence = self._detect_hate_speech(content)
        threat_score = self._calculate_social_threat_score(
            content, sentiment, hate_detected, author_followers, engagement_count
        )
        
        signal = SocialSignal(
            source_type=source_type,
            platform_id=platform_id,
            author_id=author_id,
            author_name=author_name,
            author_followers=author_followers,
            content=content,
            engagement_count=engagement_count,
            sentiment=sentiment,
            hate_speech_detected=hate_detected,
            hate_speech_category=hate_category,
            hate_speech_confidence=hate_confidence,
            keywords=keywords,
            hashtags=hashtags,
            mentions=mentions,
            urls=urls,
            locations=locations,
            threat_score=threat_score,
            posted_at=posted_at or datetime.utcnow(),
        )
        
        self._social_signals[signal.signal_id] = signal
        self._update_keyword_counts(keywords + hashtags)
        self._record_event("social_signal_ingested", {"signal_id": signal.signal_id})
        self._notify_callbacks(signal)
        
        return signal

    def _extract_keywords(self, text: str) -> list[str]:
        """Extract keywords from text"""
        text_lower = text.lower()
        found = []
        
        for keyword in self._monitored_keywords:
            if keyword in text_lower:
                found.append(keyword)
        
        return list(set(found))

    def _extract_hashtags(self, text: str) -> list[str]:
        """Extract hashtags from text"""
        return re.findall(r'#(\w+)', text)

    def _extract_mentions(self, text: str) -> list[str]:
        """Extract mentions from text"""
        return re.findall(r'@(\w+)', text)

    def _extract_urls(self, text: str) -> list[str]:
        """Extract URLs from text"""
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        return re.findall(url_pattern, text)[:5]

    def _extract_entities(self, text: str) -> list[str]:
        """Extract named entities from text (simplified)"""
        entities = []
        
        org_patterns = [
            r'\b(?:FBI|CIA|DEA|ATF|DHS|ICE|NYPD|LAPD)\b',
            r'\b(?:Police|Sheriff|Department|Agency|Bureau)\b',
        ]
        for pattern in org_patterns:
            matches = re.findall(pattern, text)
            entities.extend([f"org:{m}" for m in matches])
        
        return list(set(entities))[:10]

    def _extract_locations(self, text: str) -> list[str]:
        """Extract location mentions from text (simplified)"""
        locations = []
        
        state_pattern = r'\b(?:California|Texas|Florida|New York|Illinois|Pennsylvania|Ohio|Georgia|Michigan|Arizona)\b'
        states = re.findall(state_pattern, text, re.IGNORECASE)
        locations.extend(states)
        
        city_pattern = r'\b(?:Los Angeles|New York|Chicago|Houston|Phoenix|Philadelphia|San Antonio|San Diego|Dallas|San Jose)\b'
        cities = re.findall(city_pattern, text, re.IGNORECASE)
        locations.extend(cities)
        
        return list(set(locations))[:5]

    def _categorize_content(self, text: str) -> ContentCategory:
        """Categorize content based on keywords"""
        text_lower = text.lower()
        
        if any(kw in text_lower for kw in ["terrorism", "terrorist", "extremist", "jihad"]):
            return ContentCategory.TERRORISM
        elif any(kw in text_lower for kw in ["protest", "rally", "demonstration", "march"]):
            return ContentCategory.PROTEST
        elif any(kw in text_lower for kw in ["riot", "unrest", "looting", "violence"]):
            return ContentCategory.CIVIL_UNREST
        elif any(kw in text_lower for kw in ["shooting", "murder", "robbery", "assault"]):
            return ContentCategory.CRIME
        elif any(kw in text_lower for kw in ["gang", "cartel", "crew"]):
            return ContentCategory.GANG_ACTIVITY
        elif any(kw in text_lower for kw in ["drug", "narcotics", "fentanyl", "overdose"]):
            return ContentCategory.DRUG_ACTIVITY
        elif any(kw in text_lower for kw in ["earthquake", "hurricane", "flood", "wildfire"]):
            return ContentCategory.NATURAL_DISASTER
        elif any(kw in text_lower for kw in ["hack", "breach", "cyber", "ransomware"]):
            return ContentCategory.CYBERSECURITY
        elif any(kw in text_lower for kw in ["safety", "warning", "alert", "emergency"]):
            return ContentCategory.PUBLIC_SAFETY
        
        return ContentCategory.OTHER

    def _analyze_sentiment(self, text: str) -> SentimentType:
        """Analyze sentiment of text (simplified)"""
        text_lower = text.lower()
        
        if any(ind in text_lower for ind in self._hate_speech_indicators):
            return SentimentType.HATEFUL
        
        threatening_words = ["kill", "attack", "destroy", "bomb", "shoot", "murder"]
        if any(word in text_lower for word in threatening_words):
            return SentimentType.THREATENING
        
        negative_words = ["bad", "terrible", "awful", "horrible", "worst", "hate", "angry"]
        positive_words = ["good", "great", "excellent", "wonderful", "best", "love", "happy"]
        
        neg_count = sum(1 for word in negative_words if word in text_lower)
        pos_count = sum(1 for word in positive_words if word in text_lower)
        
        if neg_count > pos_count + 2:
            return SentimentType.NEGATIVE
        elif pos_count > neg_count + 2:
            return SentimentType.POSITIVE
        
        return SentimentType.NEUTRAL

    def _detect_hate_speech(
        self, text: str
    ) -> tuple[bool, Optional[HateSpeechCategory], float]:
        """Detect hate speech in text (stubbed classifier)"""
        text_lower = text.lower()
        
        if any(ind in text_lower for ind in self._hate_speech_indicators):
            if any(word in text_lower for word in ["race", "racial", "white", "black", "asian"]):
                return True, HateSpeechCategory.RACIAL, 0.85
            elif any(word in text_lower for word in ["muslim", "christian", "jewish", "religion"]):
                return True, HateSpeechCategory.RELIGIOUS, 0.80
            elif any(word in text_lower for word in ["gay", "lesbian", "lgbt", "trans"]):
                return True, HateSpeechCategory.SEXUAL_ORIENTATION, 0.82
            elif any(word in text_lower for word in ["immigrant", "foreigner", "alien"]):
                return True, HateSpeechCategory.NATIONAL_ORIGIN, 0.78
            else:
                return True, HateSpeechCategory.OTHER, 0.70
        
        return False, None, 0.0

    def _calculate_relevance(
        self, keywords: list[str], category: ContentCategory
    ) -> float:
        """Calculate relevance score for content"""
        base_score = len(keywords) * 15
        
        high_priority_categories = [
            ContentCategory.TERRORISM,
            ContentCategory.CIVIL_UNREST,
            ContentCategory.CRIME,
        ]
        if category in high_priority_categories:
            base_score += 30
        
        return min(base_score, 100.0)

    def _calculate_social_threat_score(
        self,
        content: str,
        sentiment: SentimentType,
        hate_detected: bool,
        followers: int,
        engagement: int,
    ) -> float:
        """Calculate threat score for social signal"""
        score = 0.0
        
        if sentiment == SentimentType.HATEFUL:
            score += 40
        elif sentiment == SentimentType.THREATENING:
            score += 30
        elif sentiment == SentimentType.NEGATIVE:
            score += 10
        
        if hate_detected:
            score += 25
        
        if followers > 100000:
            score += 15
        elif followers > 10000:
            score += 10
        elif followers > 1000:
            score += 5
        
        if engagement > 10000:
            score += 10
        elif engagement > 1000:
            score += 5
        
        return min(score, 100.0)

    def _update_keyword_counts(self, keywords: list[str]) -> None:
        """Update keyword counts for spike detection"""
        now = datetime.utcnow()
        for keyword in keywords:
            self._keyword_counts[keyword.lower()].append((now, 1))
            cutoff = now - timedelta(hours=24)
            self._keyword_counts[keyword.lower()] = [
                (t, c) for t, c in self._keyword_counts[keyword.lower()]
                if t > cutoff
            ]

    def detect_keyword_spikes(
        self,
        threshold_percentage: float = 200.0,
        min_count: int = 10,
    ) -> list[KeywordSpike]:
        """Detect spikes in keyword activity"""
        now = datetime.utcnow()
        hour_ago = now - timedelta(hours=1)
        day_ago = now - timedelta(hours=24)
        
        new_spikes = []
        
        for keyword, counts in self._keyword_counts.items():
            recent_count = sum(c for t, c in counts if t > hour_ago)
            baseline_count = sum(c for t, c in counts if t <= hour_ago and t > day_ago) / 23
            
            if baseline_count > 0 and recent_count >= min_count:
                spike_percentage = ((recent_count - baseline_count) / baseline_count) * 100
                
                if spike_percentage >= threshold_percentage:
                    existing = None
                    for spike in self._keyword_spikes.values():
                        if spike.keyword == keyword and spike.status in [
                            SpikeStatus.EMERGING, SpikeStatus.ACTIVE
                        ]:
                            existing = spike
                            break
                    
                    if existing:
                        existing.current_count = recent_count
                        existing.spike_percentage = spike_percentage
                        existing.last_updated = now
                        if recent_count > existing.peak_count:
                            existing.peak_count = recent_count
                            existing.peak_time = now
                    else:
                        spike = KeywordSpike(
                            keyword=keyword,
                            baseline_count=int(baseline_count),
                            current_count=recent_count,
                            spike_percentage=spike_percentage,
                            status=SpikeStatus.EMERGING,
                            peak_count=recent_count,
                            peak_time=now,
                        )
                        self._keyword_spikes[spike.spike_id] = spike
                        new_spikes.append(spike)
                        self._record_event("keyword_spike_detected", {
                            "spike_id": spike.spike_id,
                            "keyword": keyword,
                        })
        
        return new_spikes

    def create_event_prediction(
        self,
        event_type: str,
        title: str,
        description: str,
        predicted_location: str,
        likelihood: EventLikelihood = EventLikelihood.POSSIBLE,
        confidence_score: float = 0.5,
        predicted_date_start: Optional[datetime] = None,
        predicted_date_end: Optional[datetime] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        estimated_participants: int = 0,
        supporting_signals: Optional[list[str]] = None,
    ) -> EventPrediction:
        """Create an event prediction"""
        risk_level = "low"
        if likelihood in [EventLikelihood.HIGHLY_LIKELY, EventLikelihood.IMMINENT]:
            risk_level = "high"
        elif likelihood == EventLikelihood.LIKELY:
            risk_level = "medium"
        
        prediction = EventPrediction(
            event_type=event_type,
            title=title,
            description=description,
            likelihood=likelihood,
            confidence_score=confidence_score,
            predicted_date_start=predicted_date_start,
            predicted_date_end=predicted_date_end,
            predicted_location=predicted_location,
            latitude=latitude,
            longitude=longitude,
            estimated_participants=estimated_participants,
            supporting_signals=supporting_signals or [],
            risk_level=risk_level,
        )
        
        self._event_predictions[prediction.prediction_id] = prediction
        self._record_event("event_prediction_created", {
            "prediction_id": prediction.prediction_id,
        })
        self._notify_callbacks(prediction)
        
        return prediction

    def get_article(self, article_id: str) -> Optional[NewsArticle]:
        """Get an article by ID"""
        return self._articles.get(article_id)

    def get_all_articles(
        self,
        category: Optional[ContentCategory] = None,
        source_type: Optional[SourceType] = None,
        min_relevance: float = 0.0,
        limit: int = 100,
    ) -> list[NewsArticle]:
        """Get all articles with optional filtering"""
        articles = list(self._articles.values())
        
        if category:
            articles = [a for a in articles if a.category == category]
        if source_type:
            articles = [a for a in articles if a.source_type == source_type]
        if min_relevance > 0:
            articles = [a for a in articles if a.relevance_score >= min_relevance]
        
        articles.sort(key=lambda a: a.collected_at, reverse=True)
        return articles[:limit]

    def get_social_signal(self, signal_id: str) -> Optional[SocialSignal]:
        """Get a social signal by ID"""
        return self._social_signals.get(signal_id)

    def get_all_social_signals(
        self,
        source_type: Optional[SourceType] = None,
        hate_speech_only: bool = False,
        min_threat_score: float = 0.0,
        limit: int = 100,
    ) -> list[SocialSignal]:
        """Get all social signals with optional filtering"""
        signals = list(self._social_signals.values())
        
        if source_type:
            signals = [s for s in signals if s.source_type == source_type]
        if hate_speech_only:
            signals = [s for s in signals if s.hate_speech_detected]
        if min_threat_score > 0:
            signals = [s for s in signals if s.threat_score >= min_threat_score]
        
        signals.sort(key=lambda s: s.threat_score, reverse=True)
        return signals[:limit]

    def get_keyword_spike(self, spike_id: str) -> Optional[KeywordSpike]:
        """Get a keyword spike by ID"""
        return self._keyword_spikes.get(spike_id)

    def get_all_keyword_spikes(
        self,
        status: Optional[SpikeStatus] = None,
        limit: int = 50,
    ) -> list[KeywordSpike]:
        """Get all keyword spikes"""
        spikes = list(self._keyword_spikes.values())
        
        if status:
            spikes = [s for s in spikes if s.status == status]
        
        spikes.sort(key=lambda s: s.spike_percentage, reverse=True)
        return spikes[:limit]

    def get_event_prediction(self, prediction_id: str) -> Optional[EventPrediction]:
        """Get an event prediction by ID"""
        return self._event_predictions.get(prediction_id)

    def get_all_event_predictions(
        self,
        likelihood: Optional[EventLikelihood] = None,
        active_only: bool = True,
        limit: int = 50,
    ) -> list[EventPrediction]:
        """Get all event predictions"""
        predictions = list(self._event_predictions.values())
        
        if likelihood:
            predictions = [p for p in predictions if p.likelihood == likelihood]
        if active_only:
            now = datetime.utcnow()
            predictions = [
                p for p in predictions
                if not p.expires_at or p.expires_at > now
            ]
        
        predictions.sort(key=lambda p: p.confidence_score, reverse=True)
        return predictions[:limit]

    def update_event_prediction(
        self,
        prediction_id: str,
        likelihood: Optional[EventLikelihood] = None,
        confidence_score: Optional[float] = None,
    ) -> bool:
        """Update an event prediction"""
        prediction = self._event_predictions.get(prediction_id)
        if not prediction:
            return False
        
        if likelihood:
            prediction.likelihood = likelihood
        if confidence_score is not None:
            prediction.confidence_score = confidence_score
        
        prediction.updated_at = datetime.utcnow()
        self._record_event("event_prediction_updated", {
            "prediction_id": prediction_id,
        })
        return True

    def get_metrics(self) -> dict[str, Any]:
        """Get OSINT harvester metrics"""
        articles = list(self._articles.values())
        signals = list(self._social_signals.values())
        spikes = list(self._keyword_spikes.values())
        predictions = list(self._event_predictions.values())
        
        category_counts = {}
        for category in ContentCategory:
            category_counts[category.value] = len([
                a for a in articles if a.category == category
            ])
        
        sentiment_counts = {}
        for sentiment in SentimentType:
            sentiment_counts[sentiment.value] = len([
                s for s in signals if s.sentiment == sentiment
            ])
        
        return {
            "total_articles": len(articles),
            "total_social_signals": len(signals),
            "total_keyword_spikes": len(spikes),
            "total_event_predictions": len(predictions),
            "total_rss_feeds": len(self._rss_feeds),
            "articles_by_category": category_counts,
            "signals_by_sentiment": sentiment_counts,
            "hate_speech_signals": len([s for s in signals if s.hate_speech_detected]),
            "active_spikes": len([s for s in spikes if s.status == SpikeStatus.ACTIVE]),
            "high_likelihood_predictions": len([
                p for p in predictions
                if p.likelihood in [EventLikelihood.HIGHLY_LIKELY, EventLikelihood.IMMINENT]
            ]),
            "total_events": len(self._events),
        }
