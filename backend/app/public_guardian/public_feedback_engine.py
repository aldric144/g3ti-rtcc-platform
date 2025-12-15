"""
Public Feedback Engine

Phase 36: Public Safety Guardian
Handles public survey ingestion, sentiment analysis, trend detection,
and aggregates neighborhood-level insights from community feedback.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional
import hashlib
import json
import uuid


class FeedbackType(Enum):
    SURVEY = "survey"
    COMPLAINT = "complaint"
    PRAISE = "praise"
    SUGGESTION = "suggestion"
    QUESTION = "question"
    CONCERN = "concern"
    REQUEST = "request"
    GENERAL = "general"


class SentimentLevel(Enum):
    VERY_NEGATIVE = "very_negative"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    POSITIVE = "positive"
    VERY_POSITIVE = "very_positive"


class FeedbackCategory(Enum):
    RESPONSE_TIME = "response_time"
    OFFICER_CONDUCT = "officer_conduct"
    COMMUNITY_PROGRAMS = "community_programs"
    SAFETY_CONCERNS = "safety_concerns"
    TRAFFIC = "traffic"
    NOISE = "noise"
    PROPERTY_CRIME = "property_crime"
    YOUTH_SERVICES = "youth_services"
    COMMUNICATION = "communication"
    ACCESSIBILITY = "accessibility"
    OTHER = "other"


class FeedbackStatus(Enum):
    RECEIVED = "received"
    UNDER_REVIEW = "under_review"
    ACKNOWLEDGED = "acknowledged"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


@dataclass
class PublicFeedback:
    feedback_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    feedback_type: FeedbackType = FeedbackType.GENERAL
    category: FeedbackCategory = FeedbackCategory.OTHER
    title: str = ""
    content: str = ""
    sentiment: SentimentLevel = SentimentLevel.NEUTRAL
    sentiment_score: float = 0.0
    neighborhood: str = ""
    status: FeedbackStatus = FeedbackStatus.RECEIVED
    anonymous: bool = True
    contact_email: str = ""
    response: str = ""
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None
    feedback_hash: str = ""

    def __post_init__(self):
        if not self.feedback_hash:
            self.feedback_hash = self._generate_hash()

    def _generate_hash(self) -> str:
        content = f"{self.feedback_id}{self.created_at.isoformat()}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "feedback_id": self.feedback_id,
            "feedback_type": self.feedback_type.value,
            "category": self.category.value,
            "title": self.title,
            "content": self.content,
            "sentiment": self.sentiment.value,
            "sentiment_score": self.sentiment_score,
            "neighborhood": self.neighborhood,
            "status": self.status.value,
            "anonymous": self.anonymous,
            "contact_email": self.contact_email if not self.anonymous else "",
            "response": self.response,
            "tags": self.tags,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "feedback_hash": self.feedback_hash,
        }


@dataclass
class FeedbackTrend:
    trend_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    category: FeedbackCategory = FeedbackCategory.OTHER
    trend_type: str = ""
    description: str = ""
    count: int = 0
    sentiment_average: float = 0.0
    neighborhoods_affected: List[str] = field(default_factory=list)
    period_start: datetime = field(default_factory=datetime.utcnow)
    period_end: datetime = field(default_factory=datetime.utcnow)
    trend_direction: str = "stable"
    significance: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "trend_id": self.trend_id,
            "category": self.category.value,
            "trend_type": self.trend_type,
            "description": self.description,
            "count": self.count,
            "sentiment_average": self.sentiment_average,
            "neighborhoods_affected": self.neighborhoods_affected,
            "period_start": self.period_start.isoformat(),
            "period_end": self.period_end.isoformat(),
            "trend_direction": self.trend_direction,
            "significance": self.significance,
        }


@dataclass
class NeighborhoodInsight:
    insight_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    neighborhood: str = ""
    total_feedback: int = 0
    sentiment_average: float = 0.0
    sentiment_distribution: Dict[str, int] = field(default_factory=dict)
    top_concerns: List[str] = field(default_factory=list)
    top_praise: List[str] = field(default_factory=list)
    category_breakdown: Dict[str, int] = field(default_factory=dict)
    trend_vs_previous: float = 0.0
    period_start: datetime = field(default_factory=datetime.utcnow)
    period_end: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "insight_id": self.insight_id,
            "neighborhood": self.neighborhood,
            "total_feedback": self.total_feedback,
            "sentiment_average": self.sentiment_average,
            "sentiment_distribution": self.sentiment_distribution,
            "top_concerns": self.top_concerns,
            "top_praise": self.top_praise,
            "category_breakdown": self.category_breakdown,
            "trend_vs_previous": self.trend_vs_previous,
            "period_start": self.period_start.isoformat(),
            "period_end": self.period_end.isoformat(),
        }


class PublicFeedbackEngine:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.feedback: Dict[str, PublicFeedback] = {}
        self.trends: Dict[str, FeedbackTrend] = {}
        self.insights: Dict[str, NeighborhoodInsight] = {}
        self.statistics = {
            "total_feedback": 0,
            "surveys_received": 0,
            "complaints_received": 0,
            "praise_received": 0,
            "suggestions_received": 0,
            "resolved_feedback": 0,
            "average_resolution_time_hours": 0,
            "sentiment_analyses": 0,
        }
        self.sentiment_keywords = {
            "positive": ["great", "excellent", "helpful", "professional", "quick", "friendly", "safe", "thank", "appreciate", "good"],
            "negative": ["slow", "rude", "unhelpful", "unsafe", "ignored", "frustrated", "disappointed", "poor", "bad", "worse"],
        }
        self._initialize_sample_feedback()

    def _initialize_sample_feedback(self):
        sample_feedback = [
            PublicFeedback(
                feedback_type=FeedbackType.PRAISE,
                category=FeedbackCategory.OFFICER_CONDUCT,
                title="Great response to my call",
                content="Officers responded quickly and were very professional. Thank you!",
                sentiment=SentimentLevel.VERY_POSITIVE,
                sentiment_score=0.9,
                neighborhood="Singer Island",
                status=FeedbackStatus.ACKNOWLEDGED,
            ),
            PublicFeedback(
                feedback_type=FeedbackType.CONCERN,
                category=FeedbackCategory.SAFETY_CONCERNS,
                title="Speeding on Blue Heron",
                content="There's been a lot of speeding on Blue Heron Blvd lately. Can we get more patrols?",
                sentiment=SentimentLevel.NEGATIVE,
                sentiment_score=-0.3,
                neighborhood="Downtown Riviera Beach",
                status=FeedbackStatus.UNDER_REVIEW,
            ),
            PublicFeedback(
                feedback_type=FeedbackType.SUGGESTION,
                category=FeedbackCategory.COMMUNITY_PROGRAMS,
                title="Youth basketball program",
                content="Would love to see a police-sponsored youth basketball league in the summer.",
                sentiment=SentimentLevel.POSITIVE,
                sentiment_score=0.5,
                neighborhood="West Riviera Beach",
                status=FeedbackStatus.RECEIVED,
            ),
        ]
        for fb in sample_feedback:
            self.feedback[fb.feedback_id] = fb

    def submit_feedback(
        self,
        feedback_type: FeedbackType,
        category: FeedbackCategory,
        title: str,
        content: str,
        neighborhood: str = "",
        anonymous: bool = True,
        contact_email: str = "",
        tags: Optional[List[str]] = None,
    ) -> PublicFeedback:
        sentiment, score = self._analyze_sentiment(content)

        feedback = PublicFeedback(
            feedback_type=feedback_type,
            category=category,
            title=title,
            content=content,
            sentiment=sentiment,
            sentiment_score=score,
            neighborhood=neighborhood,
            anonymous=anonymous,
            contact_email=contact_email if not anonymous else "",
            tags=tags or [],
        )

        self.feedback[feedback.feedback_id] = feedback
        self.statistics["total_feedback"] += 1
        self.statistics[f"{feedback_type.value}s_received"] = self.statistics.get(f"{feedback_type.value}s_received", 0) + 1
        self.statistics["sentiment_analyses"] += 1

        return feedback

    def _analyze_sentiment(self, content: str) -> tuple:
        content_lower = content.lower()
        positive_count = sum(1 for word in self.sentiment_keywords["positive"] if word in content_lower)
        negative_count = sum(1 for word in self.sentiment_keywords["negative"] if word in content_lower)

        if positive_count > negative_count + 2:
            return SentimentLevel.VERY_POSITIVE, 0.8 + (positive_count * 0.02)
        elif positive_count > negative_count:
            return SentimentLevel.POSITIVE, 0.3 + (positive_count * 0.05)
        elif negative_count > positive_count + 2:
            return SentimentLevel.VERY_NEGATIVE, -0.8 - (negative_count * 0.02)
        elif negative_count > positive_count:
            return SentimentLevel.NEGATIVE, -0.3 - (negative_count * 0.05)
        else:
            return SentimentLevel.NEUTRAL, 0.0

    def update_feedback_status(
        self,
        feedback_id: str,
        status: FeedbackStatus,
        response: str = "",
    ) -> Optional[PublicFeedback]:
        feedback = self.feedback.get(feedback_id)
        if not feedback:
            return None

        feedback.status = status
        feedback.updated_at = datetime.utcnow()

        if response:
            feedback.response = response

        if status == FeedbackStatus.RESOLVED:
            feedback.resolved_at = datetime.utcnow()
            self.statistics["resolved_feedback"] += 1

        return feedback

    def get_feedback(self, feedback_id: str) -> Optional[PublicFeedback]:
        return self.feedback.get(feedback_id)

    def get_feedback_by_neighborhood(self, neighborhood: str) -> List[PublicFeedback]:
        return [f for f in self.feedback.values() if f.neighborhood == neighborhood]

    def get_feedback_by_category(self, category: FeedbackCategory) -> List[PublicFeedback]:
        return [f for f in self.feedback.values() if f.category == category]

    def get_feedback_by_sentiment(self, sentiment: SentimentLevel) -> List[PublicFeedback]:
        return [f for f in self.feedback.values() if f.sentiment == sentiment]

    def get_recent_feedback(self, limit: int = 20) -> List[PublicFeedback]:
        sorted_feedback = sorted(
            self.feedback.values(),
            key=lambda f: f.created_at,
            reverse=True,
        )
        return sorted_feedback[:limit]

    def detect_trends(
        self,
        period_days: int = 30,
    ) -> List[FeedbackTrend]:
        now = datetime.utcnow()
        period_start = now - timedelta(days=period_days)

        recent_feedback = [
            f for f in self.feedback.values()
            if f.created_at >= period_start
        ]

        category_counts: Dict[FeedbackCategory, List[PublicFeedback]] = {}
        for fb in recent_feedback:
            if fb.category not in category_counts:
                category_counts[fb.category] = []
            category_counts[fb.category].append(fb)

        trends = []
        for category, feedback_list in category_counts.items():
            if len(feedback_list) >= 3:
                avg_sentiment = sum(f.sentiment_score for f in feedback_list) / len(feedback_list)
                neighborhoods = list(set(f.neighborhood for f in feedback_list if f.neighborhood))

                trend_direction = "increasing" if len(feedback_list) > 5 else "stable"
                if avg_sentiment < -0.3:
                    trend_type = "concern"
                elif avg_sentiment > 0.3:
                    trend_type = "praise"
                else:
                    trend_type = "neutral"

                trend = FeedbackTrend(
                    category=category,
                    trend_type=trend_type,
                    description=f"{category.value.replace('_', ' ').title()} feedback trend",
                    count=len(feedback_list),
                    sentiment_average=round(avg_sentiment, 2),
                    neighborhoods_affected=neighborhoods,
                    period_start=period_start,
                    period_end=now,
                    trend_direction=trend_direction,
                    significance=len(feedback_list) / max(len(recent_feedback), 1),
                )
                trends.append(trend)
                self.trends[trend.trend_id] = trend

        return sorted(trends, key=lambda t: t.count, reverse=True)

    def get_neighborhood_insight(
        self,
        neighborhood: str,
        period_days: int = 30,
    ) -> NeighborhoodInsight:
        now = datetime.utcnow()
        period_start = now - timedelta(days=period_days)

        neighborhood_feedback = [
            f for f in self.feedback.values()
            if f.neighborhood == neighborhood and f.created_at >= period_start
        ]

        sentiment_dist = {
            "very_positive": 0,
            "positive": 0,
            "neutral": 0,
            "negative": 0,
            "very_negative": 0,
        }
        category_breakdown: Dict[str, int] = {}
        concerns = []
        praise = []

        for fb in neighborhood_feedback:
            sentiment_dist[fb.sentiment.value] += 1
            category_breakdown[fb.category.value] = category_breakdown.get(fb.category.value, 0) + 1

            if fb.sentiment in [SentimentLevel.NEGATIVE, SentimentLevel.VERY_NEGATIVE]:
                concerns.append(fb.title)
            elif fb.sentiment in [SentimentLevel.POSITIVE, SentimentLevel.VERY_POSITIVE]:
                praise.append(fb.title)

        avg_sentiment = (
            sum(f.sentiment_score for f in neighborhood_feedback) / len(neighborhood_feedback)
            if neighborhood_feedback else 0
        )

        insight = NeighborhoodInsight(
            neighborhood=neighborhood,
            total_feedback=len(neighborhood_feedback),
            sentiment_average=round(avg_sentiment, 2),
            sentiment_distribution=sentiment_dist,
            top_concerns=concerns[:5],
            top_praise=praise[:5],
            category_breakdown=category_breakdown,
            trend_vs_previous=2.5,
            period_start=period_start,
            period_end=now,
        )

        self.insights[insight.insight_id] = insight
        return insight

    def get_all_insights(self, period_days: int = 30) -> List[NeighborhoodInsight]:
        neighborhoods = list(set(f.neighborhood for f in self.feedback.values() if f.neighborhood))
        return [self.get_neighborhood_insight(n, period_days) for n in neighborhoods]

    def get_common_concerns(self, limit: int = 10) -> List[Dict[str, Any]]:
        negative_feedback = [
            f for f in self.feedback.values()
            if f.sentiment in [SentimentLevel.NEGATIVE, SentimentLevel.VERY_NEGATIVE]
        ]

        category_concerns: Dict[str, int] = {}
        for fb in negative_feedback:
            category_concerns[fb.category.value] = category_concerns.get(fb.category.value, 0) + 1

        sorted_concerns = sorted(category_concerns.items(), key=lambda x: x[1], reverse=True)

        return [
            {"category": cat, "count": count, "percentage": round(count / max(len(negative_feedback), 1) * 100, 1)}
            for cat, count in sorted_concerns[:limit]
        ]

    def get_sentiment_summary(self) -> Dict[str, Any]:
        if not self.feedback:
            return {"total": 0, "average_sentiment": 0, "distribution": {}}

        total = len(self.feedback)
        avg_sentiment = sum(f.sentiment_score for f in self.feedback.values()) / total

        distribution = {
            "very_positive": sum(1 for f in self.feedback.values() if f.sentiment == SentimentLevel.VERY_POSITIVE),
            "positive": sum(1 for f in self.feedback.values() if f.sentiment == SentimentLevel.POSITIVE),
            "neutral": sum(1 for f in self.feedback.values() if f.sentiment == SentimentLevel.NEUTRAL),
            "negative": sum(1 for f in self.feedback.values() if f.sentiment == SentimentLevel.NEGATIVE),
            "very_negative": sum(1 for f in self.feedback.values() if f.sentiment == SentimentLevel.VERY_NEGATIVE),
        }

        return {
            "total": total,
            "average_sentiment": round(avg_sentiment, 2),
            "distribution": distribution,
            "positive_percentage": round((distribution["very_positive"] + distribution["positive"]) / total * 100, 1),
            "negative_percentage": round((distribution["very_negative"] + distribution["negative"]) / total * 100, 1),
        }

    def get_statistics(self) -> Dict[str, Any]:
        return {
            **self.statistics,
            "total_stored": len(self.feedback),
            "trends_detected": len(self.trends),
            "insights_generated": len(self.insights),
            "sentiment_summary": self.get_sentiment_summary(),
        }
