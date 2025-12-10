"""
Dark Web Monitor Module

Provides capabilities for:
- Tor crawler interface (stubbed for security)
- Dark keyword detection
- Market listing analysis (guns, drugs, IDs)
- Threat sentiment scoring
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Optional
import uuid
import hashlib
import re


class SignalType(Enum):
    """Types of dark web signals"""
    KEYWORD_MATCH = "keyword_match"
    MARKET_LISTING = "market_listing"
    FORUM_POST = "forum_post"
    CHAT_MESSAGE = "chat_message"
    PASTE_CONTENT = "paste_content"
    CREDENTIAL_LEAK = "credential_leak"
    DATA_BREACH = "data_breach"
    THREAT_ACTOR = "threat_actor"
    MALWARE_SAMPLE = "malware_sample"
    EXPLOIT_LISTING = "exploit_listing"


class MarketCategory(Enum):
    """Categories of dark web market listings"""
    FIREARMS = "firearms"
    AMMUNITION = "ammunition"
    EXPLOSIVES = "explosives"
    DRUGS_NARCOTICS = "drugs_narcotics"
    DRUGS_PRESCRIPTION = "drugs_prescription"
    COUNTERFEIT_IDS = "counterfeit_ids"
    COUNTERFEIT_CURRENCY = "counterfeit_currency"
    STOLEN_DATA = "stolen_data"
    CREDIT_CARDS = "credit_cards"
    HACKING_SERVICES = "hacking_services"
    MALWARE = "malware"
    HUMAN_TRAFFICKING = "human_trafficking"
    FRAUD_SERVICES = "fraud_services"
    OTHER = "other"


class SentimentLevel(Enum):
    """Threat sentiment levels"""
    BENIGN = "benign"
    LOW_CONCERN = "low_concern"
    MODERATE_CONCERN = "moderate_concern"
    HIGH_CONCERN = "high_concern"
    CRITICAL_THREAT = "critical_threat"


class SignalStatus(Enum):
    """Status of a dark web signal"""
    NEW = "new"
    ANALYZING = "analyzing"
    VERIFIED = "verified"
    FALSE_POSITIVE = "false_positive"
    ESCALATED = "escalated"
    ARCHIVED = "archived"


@dataclass
class ThreatSentiment:
    """Sentiment analysis result for dark web content"""
    sentiment_id: str = ""
    content_hash: str = ""
    sentiment_level: SentimentLevel = SentimentLevel.BENIGN
    confidence_score: float = 0.0
    threat_indicators: list[str] = field(default_factory=list)
    entity_mentions: list[str] = field(default_factory=list)
    location_mentions: list[str] = field(default_factory=list)
    temporal_indicators: list[str] = field(default_factory=list)
    violence_score: float = 0.0
    urgency_score: float = 0.0
    credibility_score: float = 0.0
    analyzed_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        if not self.sentiment_id:
            self.sentiment_id = f"sentiment-{uuid.uuid4().hex[:12]}"


@dataclass
class MarketListing:
    """Dark web market listing"""
    listing_id: str = ""
    market_name: str = ""
    category: MarketCategory = MarketCategory.OTHER
    title: str = ""
    description: str = ""
    price: float = 0.0
    currency: str = "BTC"
    seller_name: str = ""
    seller_rating: float = 0.0
    seller_sales_count: int = 0
    location_origin: str = ""
    ships_to: list[str] = field(default_factory=list)
    quantity_available: int = 0
    keywords_matched: list[str] = field(default_factory=list)
    threat_score: float = 0.0
    first_seen: datetime = field(default_factory=datetime.utcnow)
    last_seen: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True
    raw_content_hash: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.listing_id:
            self.listing_id = f"listing-{uuid.uuid4().hex[:12]}"


@dataclass
class DarkWebSignal:
    """A signal detected from dark web monitoring"""
    signal_id: str = ""
    signal_type: SignalType = SignalType.KEYWORD_MATCH
    source_platform: str = ""
    source_url_hash: str = ""
    title: str = ""
    content_snippet: str = ""
    content_hash: str = ""
    keywords_matched: list[str] = field(default_factory=list)
    entities_detected: list[str] = field(default_factory=list)
    threat_sentiment: Optional[ThreatSentiment] = None
    market_listing: Optional[MarketListing] = None
    status: SignalStatus = SignalStatus.NEW
    priority_score: float = 0.0
    jurisdiction_relevance: list[str] = field(default_factory=list)
    detected_at: datetime = field(default_factory=datetime.utcnow)
    analyzed_at: Optional[datetime] = None
    escalated_at: Optional[datetime] = None
    analyst_notes: str = ""
    related_signals: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.signal_id:
            self.signal_id = f"dwsig-{uuid.uuid4().hex[:12]}"


@dataclass
class KeywordProfile:
    """Profile for keyword monitoring"""
    profile_id: str = ""
    name: str = ""
    keywords: list[str] = field(default_factory=list)
    regex_patterns: list[str] = field(default_factory=list)
    category: str = ""
    priority: int = 1
    jurisdiction_codes: list[str] = field(default_factory=list)
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        if not self.profile_id:
            self.profile_id = f"kwprofile-{uuid.uuid4().hex[:12]}"


class DarkWebMonitor:
    """
    Dark Web Monitor for threat intelligence gathering.
    
    Note: Actual Tor crawling is stubbed for security and legal compliance.
    This module provides the interface and analysis capabilities.
    """

    def __init__(self):
        self._signals: dict[str, DarkWebSignal] = {}
        self._listings: dict[str, MarketListing] = {}
        self._keyword_profiles: dict[str, KeywordProfile] = {}
        self._sentiments: dict[str, ThreatSentiment] = {}
        self._callbacks: list[Callable[[DarkWebSignal], None]] = []
        self._events: list[dict[str, Any]] = []
        
        self._default_threat_keywords = [
            "bomb", "explosive", "attack", "target", "weapon",
            "assassination", "terrorism", "jihad", "militia",
            "mass shooting", "school shooting", "manifesto",
            "ricin", "anthrax", "chemical weapon", "biological weapon",
            "dirty bomb", "nuclear", "radiological",
        ]
        
        self._default_market_keywords = [
            "glock", "ar-15", "ak-47", "firearm", "handgun",
            "fentanyl", "heroin", "cocaine", "methamphetamine",
            "fake id", "driver license", "passport", "ssn",
            "credit card", "fullz", "cvv", "bank account",
        ]

    def register_callback(self, callback: Callable[[DarkWebSignal], None]) -> None:
        """Register a callback for new signals"""
        self._callbacks.append(callback)

    def _notify_callbacks(self, signal: DarkWebSignal) -> None:
        """Notify all registered callbacks"""
        for callback in self._callbacks:
            try:
                callback(signal)
            except Exception:
                pass

    def _record_event(self, event_type: str, data: dict[str, Any]) -> None:
        """Record an event for audit purposes"""
        self._events.append({
            "event_type": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data,
        })

    def create_keyword_profile(
        self,
        name: str,
        keywords: list[str],
        category: str = "general",
        regex_patterns: Optional[list[str]] = None,
        priority: int = 1,
        jurisdiction_codes: Optional[list[str]] = None,
    ) -> KeywordProfile:
        """Create a keyword monitoring profile"""
        profile = KeywordProfile(
            name=name,
            keywords=keywords,
            regex_patterns=regex_patterns or [],
            category=category,
            priority=priority,
            jurisdiction_codes=jurisdiction_codes or [],
        )
        self._keyword_profiles[profile.profile_id] = profile
        self._record_event("keyword_profile_created", {"profile_id": profile.profile_id})
        return profile

    def get_keyword_profile(self, profile_id: str) -> Optional[KeywordProfile]:
        """Get a keyword profile by ID"""
        return self._keyword_profiles.get(profile_id)

    def get_all_keyword_profiles(self) -> list[KeywordProfile]:
        """Get all keyword profiles"""
        return list(self._keyword_profiles.values())

    def update_keyword_profile(
        self,
        profile_id: str,
        keywords: Optional[list[str]] = None,
        enabled: Optional[bool] = None,
    ) -> bool:
        """Update a keyword profile"""
        profile = self._keyword_profiles.get(profile_id)
        if not profile:
            return False
        
        if keywords is not None:
            profile.keywords = keywords
        if enabled is not None:
            profile.enabled = enabled
        
        self._record_event("keyword_profile_updated", {"profile_id": profile_id})
        return True

    def delete_keyword_profile(self, profile_id: str) -> bool:
        """Delete a keyword profile"""
        if profile_id in self._keyword_profiles:
            del self._keyword_profiles[profile_id]
            self._record_event("keyword_profile_deleted", {"profile_id": profile_id})
            return True
        return False

    def analyze_content(
        self,
        content: str,
        source_platform: str = "unknown",
        source_url: str = "",
    ) -> DarkWebSignal:
        """
        Analyze content for threat indicators.
        
        This is the main entry point for content analysis.
        In production, this would be fed by Tor crawlers.
        """
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
        url_hash = hashlib.sha256(source_url.encode()).hexdigest()[:16] if source_url else ""
        
        keywords_matched = self._detect_keywords(content)
        entities = self._extract_entities(content)
        sentiment = self._analyze_sentiment(content, content_hash)
        
        signal_type = SignalType.KEYWORD_MATCH
        if any(kw in content.lower() for kw in ["listing", "price", "shipping", "vendor"]):
            signal_type = SignalType.MARKET_LISTING
        elif any(kw in content.lower() for kw in ["forum", "thread", "reply", "post"]):
            signal_type = SignalType.FORUM_POST
        
        priority_score = self._calculate_priority(keywords_matched, sentiment)
        
        signal = DarkWebSignal(
            signal_type=signal_type,
            source_platform=source_platform,
            source_url_hash=url_hash,
            title=content[:100] if len(content) > 100 else content,
            content_snippet=content[:500] if len(content) > 500 else content,
            content_hash=content_hash,
            keywords_matched=keywords_matched,
            entities_detected=entities,
            threat_sentiment=sentiment,
            priority_score=priority_score,
        )
        
        self._signals[signal.signal_id] = signal
        self._sentiments[sentiment.sentiment_id] = sentiment
        self._record_event("content_analyzed", {"signal_id": signal.signal_id})
        self._notify_callbacks(signal)
        
        return signal

    def _detect_keywords(self, content: str) -> list[str]:
        """Detect keywords in content"""
        content_lower = content.lower()
        matched = []
        
        all_keywords = self._default_threat_keywords + self._default_market_keywords
        for profile in self._keyword_profiles.values():
            if profile.enabled:
                all_keywords.extend(profile.keywords)
        
        for keyword in set(all_keywords):
            if keyword.lower() in content_lower:
                matched.append(keyword)
        
        for profile in self._keyword_profiles.values():
            if profile.enabled:
                for pattern in profile.regex_patterns:
                    try:
                        if re.search(pattern, content, re.IGNORECASE):
                            matched.append(f"regex:{pattern[:20]}")
                    except re.error:
                        pass
        
        return list(set(matched))

    def _extract_entities(self, content: str) -> list[str]:
        """Extract entities from content (simplified)"""
        entities = []
        
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, content)
        entities.extend([f"email:{e}" for e in emails[:5]])
        
        btc_pattern = r'\b[13][a-km-zA-HJ-NP-Z1-9]{25,34}\b'
        btc_addresses = re.findall(btc_pattern, content)
        entities.extend([f"btc:{addr[:10]}..." for addr in btc_addresses[:3]])
        
        phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
        phones = re.findall(phone_pattern, content)
        entities.extend([f"phone:{p}" for p in phones[:3]])
        
        return entities

    def _analyze_sentiment(self, content: str, content_hash: str) -> ThreatSentiment:
        """Analyze threat sentiment of content"""
        content_lower = content.lower()
        
        violence_indicators = [
            "kill", "murder", "attack", "bomb", "shoot", "stab",
            "destroy", "eliminate", "execute", "assassinate",
        ]
        urgency_indicators = [
            "now", "today", "tonight", "tomorrow", "soon",
            "immediately", "urgent", "asap", "ready",
        ]
        
        violence_count = sum(1 for ind in violence_indicators if ind in content_lower)
        urgency_count = sum(1 for ind in urgency_indicators if ind in content_lower)
        
        violence_score = min(violence_count / 5.0, 1.0)
        urgency_score = min(urgency_count / 4.0, 1.0)
        
        combined_score = (violence_score * 0.6) + (urgency_score * 0.4)
        
        if combined_score >= 0.8:
            sentiment_level = SentimentLevel.CRITICAL_THREAT
        elif combined_score >= 0.6:
            sentiment_level = SentimentLevel.HIGH_CONCERN
        elif combined_score >= 0.4:
            sentiment_level = SentimentLevel.MODERATE_CONCERN
        elif combined_score >= 0.2:
            sentiment_level = SentimentLevel.LOW_CONCERN
        else:
            sentiment_level = SentimentLevel.BENIGN
        
        threat_indicators = []
        for ind in violence_indicators + urgency_indicators:
            if ind in content_lower:
                threat_indicators.append(ind)
        
        location_pattern = r'\b(?:city|town|state|county|street|avenue|building)\s+(?:of\s+)?([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b'
        locations = re.findall(location_pattern, content)
        
        return ThreatSentiment(
            content_hash=content_hash,
            sentiment_level=sentiment_level,
            confidence_score=0.7 + (combined_score * 0.2),
            threat_indicators=threat_indicators[:10],
            location_mentions=locations[:5],
            violence_score=violence_score,
            urgency_score=urgency_score,
            credibility_score=0.5,
        )

    def _calculate_priority(
        self,
        keywords_matched: list[str],
        sentiment: ThreatSentiment,
    ) -> float:
        """Calculate priority score for a signal"""
        base_score = len(keywords_matched) * 10
        
        sentiment_multipliers = {
            SentimentLevel.BENIGN: 0.5,
            SentimentLevel.LOW_CONCERN: 1.0,
            SentimentLevel.MODERATE_CONCERN: 1.5,
            SentimentLevel.HIGH_CONCERN: 2.0,
            SentimentLevel.CRITICAL_THREAT: 3.0,
        }
        
        multiplier = sentiment_multipliers.get(sentiment.sentiment_level, 1.0)
        score = base_score * multiplier
        
        score += sentiment.violence_score * 20
        score += sentiment.urgency_score * 15
        
        return min(score, 100.0)

    def analyze_market_listing(
        self,
        title: str,
        description: str,
        price: float,
        currency: str = "BTC",
        seller_name: str = "",
        market_name: str = "",
    ) -> MarketListing:
        """Analyze a dark web market listing"""
        combined_text = f"{title} {description}".lower()
        
        category = MarketCategory.OTHER
        if any(kw in combined_text for kw in ["gun", "firearm", "pistol", "rifle", "glock", "ar-15"]):
            category = MarketCategory.FIREARMS
        elif any(kw in combined_text for kw in ["ammo", "ammunition", "rounds", "bullets"]):
            category = MarketCategory.AMMUNITION
        elif any(kw in combined_text for kw in ["explosive", "c4", "dynamite", "grenade"]):
            category = MarketCategory.EXPLOSIVES
        elif any(kw in combined_text for kw in ["fentanyl", "heroin", "cocaine", "meth", "mdma"]):
            category = MarketCategory.DRUGS_NARCOTICS
        elif any(kw in combined_text for kw in ["xanax", "oxycodone", "adderall", "prescription"]):
            category = MarketCategory.DRUGS_PRESCRIPTION
        elif any(kw in combined_text for kw in ["fake id", "driver license", "passport", "identity"]):
            category = MarketCategory.COUNTERFEIT_IDS
        elif any(kw in combined_text for kw in ["counterfeit", "fake money", "bills"]):
            category = MarketCategory.COUNTERFEIT_CURRENCY
        elif any(kw in combined_text for kw in ["credit card", "cvv", "fullz", "cc"]):
            category = MarketCategory.CREDIT_CARDS
        elif any(kw in combined_text for kw in ["database", "dump", "leak", "breach"]):
            category = MarketCategory.STOLEN_DATA
        elif any(kw in combined_text for kw in ["hack", "ddos", "botnet", "rat"]):
            category = MarketCategory.HACKING_SERVICES
        elif any(kw in combined_text for kw in ["malware", "ransomware", "trojan", "exploit"]):
            category = MarketCategory.MALWARE
        
        threat_score = self._calculate_listing_threat_score(category, price, description)
        keywords_matched = self._detect_keywords(combined_text)
        
        listing = MarketListing(
            market_name=market_name,
            category=category,
            title=title,
            description=description[:1000],
            price=price,
            currency=currency,
            seller_name=seller_name,
            keywords_matched=keywords_matched,
            threat_score=threat_score,
            raw_content_hash=hashlib.sha256(combined_text.encode()).hexdigest()[:16],
        )
        
        self._listings[listing.listing_id] = listing
        self._record_event("market_listing_analyzed", {"listing_id": listing.listing_id})
        
        return listing

    def _calculate_listing_threat_score(
        self,
        category: MarketCategory,
        price: float,
        description: str,
    ) -> float:
        """Calculate threat score for a market listing"""
        category_scores = {
            MarketCategory.FIREARMS: 90,
            MarketCategory.EXPLOSIVES: 95,
            MarketCategory.AMMUNITION: 70,
            MarketCategory.HUMAN_TRAFFICKING: 100,
            MarketCategory.DRUGS_NARCOTICS: 60,
            MarketCategory.DRUGS_PRESCRIPTION: 40,
            MarketCategory.COUNTERFEIT_IDS: 50,
            MarketCategory.STOLEN_DATA: 55,
            MarketCategory.CREDIT_CARDS: 45,
            MarketCategory.HACKING_SERVICES: 65,
            MarketCategory.MALWARE: 70,
            MarketCategory.COUNTERFEIT_CURRENCY: 35,
            MarketCategory.FRAUD_SERVICES: 40,
            MarketCategory.OTHER: 20,
        }
        
        base_score = category_scores.get(category, 20)
        
        if "bulk" in description.lower() or "wholesale" in description.lower():
            base_score += 10
        if "usa" in description.lower() or "domestic" in description.lower():
            base_score += 5
        
        return min(base_score, 100.0)

    def get_signal(self, signal_id: str) -> Optional[DarkWebSignal]:
        """Get a signal by ID"""
        return self._signals.get(signal_id)

    def get_all_signals(
        self,
        status: Optional[SignalStatus] = None,
        signal_type: Optional[SignalType] = None,
        min_priority: float = 0.0,
        limit: int = 100,
    ) -> list[DarkWebSignal]:
        """Get all signals with optional filtering"""
        signals = list(self._signals.values())
        
        if status:
            signals = [s for s in signals if s.status == status]
        if signal_type:
            signals = [s for s in signals if s.signal_type == signal_type]
        if min_priority > 0:
            signals = [s for s in signals if s.priority_score >= min_priority]
        
        signals.sort(key=lambda s: s.priority_score, reverse=True)
        return signals[:limit]

    def get_listing(self, listing_id: str) -> Optional[MarketListing]:
        """Get a market listing by ID"""
        return self._listings.get(listing_id)

    def get_all_listings(
        self,
        category: Optional[MarketCategory] = None,
        min_threat_score: float = 0.0,
        limit: int = 100,
    ) -> list[MarketListing]:
        """Get all market listings with optional filtering"""
        listings = list(self._listings.values())
        
        if category:
            listings = [l for l in listings if l.category == category]
        if min_threat_score > 0:
            listings = [l for l in listings if l.threat_score >= min_threat_score]
        
        listings.sort(key=lambda l: l.threat_score, reverse=True)
        return listings[:limit]

    def update_signal_status(
        self,
        signal_id: str,
        status: SignalStatus,
        analyst_notes: str = "",
    ) -> bool:
        """Update the status of a signal"""
        signal = self._signals.get(signal_id)
        if not signal:
            return False
        
        signal.status = status
        if analyst_notes:
            signal.analyst_notes = analyst_notes
        
        if status == SignalStatus.ANALYZING:
            signal.analyzed_at = datetime.utcnow()
        elif status == SignalStatus.ESCALATED:
            signal.escalated_at = datetime.utcnow()
        
        self._record_event("signal_status_updated", {
            "signal_id": signal_id,
            "status": status.value,
        })
        return True

    def escalate_signal(self, signal_id: str, reason: str = "") -> bool:
        """Escalate a signal for immediate attention"""
        return self.update_signal_status(
            signal_id,
            SignalStatus.ESCALATED,
            analyst_notes=f"Escalated: {reason}",
        )

    def get_high_priority_signals(self, threshold: float = 70.0) -> list[DarkWebSignal]:
        """Get high priority signals above threshold"""
        return self.get_all_signals(min_priority=threshold)

    def get_metrics(self) -> dict[str, Any]:
        """Get dark web monitor metrics"""
        signals = list(self._signals.values())
        listings = list(self._listings.values())
        
        status_counts = {}
        for status in SignalStatus:
            status_counts[status.value] = len([s for s in signals if s.status == status])
        
        category_counts = {}
        for category in MarketCategory:
            category_counts[category.value] = len([l for l in listings if l.category == category])
        
        sentiment_counts = {}
        for sentiment in SentimentLevel:
            sentiment_counts[sentiment.value] = len([
                s for s in signals
                if s.threat_sentiment and s.threat_sentiment.sentiment_level == sentiment
            ])
        
        return {
            "total_signals": len(signals),
            "total_listings": len(listings),
            "total_keyword_profiles": len(self._keyword_profiles),
            "signals_by_status": status_counts,
            "listings_by_category": category_counts,
            "signals_by_sentiment": sentiment_counts,
            "high_priority_signals": len([s for s in signals if s.priority_score >= 70]),
            "critical_threats": sentiment_counts.get(SentimentLevel.CRITICAL_THREAT.value, 0),
            "total_events": len(self._events),
        }
