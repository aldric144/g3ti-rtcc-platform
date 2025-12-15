"""
Test Suite: Sentiment Analysis
Phase 36: Public Safety Guardian
"""

import pytest
from datetime import datetime

from backend.app.public_guardian.public_feedback_engine import (
    PublicFeedbackEngine,
    FeedbackType,
    SentimentLevel,
    FeedbackCategory,
)


class TestSentimentAnalysis:
    def setup_method(self):
        self.engine = PublicFeedbackEngine()

    def test_very_positive_sentiment(self):
        feedback = self.engine.submit_feedback(
            feedback_type=FeedbackType.PRAISE,
            category=FeedbackCategory.OFFICER_CONDUCT,
            title="Amazing Service",
            content="Absolutely excellent! Outstanding service! The officer was wonderful, helpful, and professional. Thank you so much!",
        )
        assert feedback.sentiment in [SentimentLevel.POSITIVE, SentimentLevel.VERY_POSITIVE]
        assert feedback.sentiment_score > 0

    def test_positive_sentiment(self):
        feedback = self.engine.submit_feedback(
            feedback_type=FeedbackType.PRAISE,
            category=FeedbackCategory.OTHER,
            title="Good Experience",
            content="Good experience overall. The response was helpful and professional.",
        )
        assert feedback.sentiment in [SentimentLevel.POSITIVE, SentimentLevel.VERY_POSITIVE, SentimentLevel.NEUTRAL]
        assert feedback.sentiment_score >= 0

    def test_neutral_sentiment(self):
        feedback = self.engine.submit_feedback(
            feedback_type=FeedbackType.GENERAL,
            category=FeedbackCategory.OTHER,
            title="Information Request",
            content="I would like to know the operating hours for the station.",
        )
        assert feedback.sentiment is not None

    def test_negative_sentiment(self):
        feedback = self.engine.submit_feedback(
            feedback_type=FeedbackType.COMPLAINT,
            category=FeedbackCategory.RESPONSE_TIME,
            title="Slow Response",
            content="The response was slow and disappointing. Not satisfied with the service.",
        )
        assert feedback.sentiment in [SentimentLevel.NEGATIVE, SentimentLevel.VERY_NEGATIVE, SentimentLevel.NEUTRAL]

    def test_very_negative_sentiment(self):
        feedback = self.engine.submit_feedback(
            feedback_type=FeedbackType.COMPLAINT,
            category=FeedbackCategory.OTHER,
            title="Terrible Experience",
            content="Absolutely terrible! Horrible experience! Very disappointed and frustrated. This was awful and unacceptable.",
        )
        assert feedback.sentiment in [SentimentLevel.NEGATIVE, SentimentLevel.VERY_NEGATIVE]
        assert feedback.sentiment_score < 0


class TestSentimentKeywords:
    def setup_method(self):
        self.engine = PublicFeedbackEngine()

    def test_positive_keywords(self):
        positive_words = ["excellent", "great", "wonderful", "helpful", "professional"]
        for word in positive_words:
            feedback = self.engine.submit_feedback(
                feedback_type=FeedbackType.GENERAL,
                category=FeedbackCategory.OTHER,
                title="Test",
                content=f"The service was {word}.",
            )
            assert feedback.sentiment_score >= 0

    def test_negative_keywords(self):
        negative_words = ["terrible", "awful", "horrible", "disappointed", "frustrated"]
        for word in negative_words:
            feedback = self.engine.submit_feedback(
                feedback_type=FeedbackType.GENERAL,
                category=FeedbackCategory.OTHER,
                title="Test",
                content=f"The experience was {word}.",
            )
            assert feedback.sentiment_score <= 0


class TestSentimentScoring:
    def setup_method(self):
        self.engine = PublicFeedbackEngine()

    def test_sentiment_score_range(self):
        feedback = self.engine.submit_feedback(
            feedback_type=FeedbackType.GENERAL,
            category=FeedbackCategory.OTHER,
            title="Test",
            content="Random content for testing.",
        )
        assert -1 <= feedback.sentiment_score <= 1

    def test_sentiment_score_positive_range(self):
        feedback = self.engine.submit_feedback(
            feedback_type=FeedbackType.PRAISE,
            category=FeedbackCategory.OTHER,
            title="Great",
            content="Excellent wonderful amazing fantastic great!",
        )
        assert feedback.sentiment_score > 0

    def test_sentiment_score_negative_range(self):
        feedback = self.engine.submit_feedback(
            feedback_type=FeedbackType.COMPLAINT,
            category=FeedbackCategory.OTHER,
            title="Bad",
            content="Terrible horrible awful disappointing frustrating!",
        )
        assert feedback.sentiment_score < 0


class TestSentimentSummary:
    def setup_method(self):
        self.engine = PublicFeedbackEngine()

    def test_sentiment_summary_structure(self):
        summary = self.engine.get_sentiment_summary()
        assert "total" in summary
        assert "distribution" in summary

    def test_sentiment_distribution(self):
        summary = self.engine.get_sentiment_summary()
        distribution = summary.get("distribution", {})
        assert isinstance(distribution, dict)

    def test_positive_percentage(self):
        summary = self.engine.get_sentiment_summary()
        assert "positive_percentage" in summary or "distribution" in summary

    def test_negative_percentage(self):
        summary = self.engine.get_sentiment_summary()
        assert "negative_percentage" in summary or "distribution" in summary


class TestSentimentTrends:
    def setup_method(self):
        self.engine = PublicFeedbackEngine()

    def test_detect_trends(self):
        trends = self.engine.detect_trends(period_days=30)
        assert isinstance(trends, list)

    def test_trend_structure(self):
        self.engine.submit_feedback(
            feedback_type=FeedbackType.COMPLAINT,
            category=FeedbackCategory.RESPONSE_TIME,
            title="Slow",
            content="Response was slow",
        )
        self.engine.submit_feedback(
            feedback_type=FeedbackType.COMPLAINT,
            category=FeedbackCategory.RESPONSE_TIME,
            title="Too Slow",
            content="Response time too slow",
        )
        trends = self.engine.detect_trends(period_days=30)
        assert isinstance(trends, list)


class TestNeighborhoodSentiment:
    def setup_method(self):
        self.engine = PublicFeedbackEngine()

    def test_neighborhood_insight(self):
        self.engine.submit_feedback(
            feedback_type=FeedbackType.GENERAL,
            category=FeedbackCategory.SAFETY_CONCERNS,
            title="Safety",
            content="Safety concern in the area",
            neighborhood="Downtown Riviera Beach",
        )
        insight = self.engine.get_neighborhood_insight("Downtown Riviera Beach")
        assert insight is not None

    def test_neighborhood_insight_structure(self):
        insight = self.engine.get_neighborhood_insight("Singer Island")
        assert hasattr(insight, "neighborhood")

    def test_all_neighborhood_insights(self):
        insights = self.engine.get_all_insights()
        assert isinstance(insights, list)


class TestCommonConcerns:
    def setup_method(self):
        self.engine = PublicFeedbackEngine()

    def test_get_common_concerns(self):
        concerns = self.engine.get_common_concerns()
        assert isinstance(concerns, list)

    def test_common_concerns_structure(self):
        self.engine.submit_feedback(
            feedback_type=FeedbackType.CONCERN,
            category=FeedbackCategory.TRAFFIC,
            title="Speeding",
            content="Speeding on Blue Heron Blvd",
        )
        concerns = self.engine.get_common_concerns()
        assert isinstance(concerns, list)


class TestFeedbackBySentiment:
    def setup_method(self):
        self.engine = PublicFeedbackEngine()

    def test_get_positive_feedback(self):
        feedback_list = self.engine.get_feedback_by_sentiment(SentimentLevel.POSITIVE)
        assert isinstance(feedback_list, list)

    def test_get_negative_feedback(self):
        feedback_list = self.engine.get_feedback_by_sentiment(SentimentLevel.NEGATIVE)
        assert isinstance(feedback_list, list)

    def test_get_neutral_feedback(self):
        feedback_list = self.engine.get_feedback_by_sentiment(SentimentLevel.NEUTRAL)
        assert isinstance(feedback_list, list)


class TestSentimentEdgeCases:
    def setup_method(self):
        self.engine = PublicFeedbackEngine()

    def test_empty_content(self):
        feedback = self.engine.submit_feedback(
            feedback_type=FeedbackType.GENERAL,
            category=FeedbackCategory.OTHER,
            title="Empty",
            content="",
        )
        assert feedback.sentiment is not None

    def test_single_word(self):
        feedback = self.engine.submit_feedback(
            feedback_type=FeedbackType.GENERAL,
            category=FeedbackCategory.OTHER,
            title="Single",
            content="Good",
        )
        assert feedback.sentiment is not None

    def test_mixed_sentiment(self):
        feedback = self.engine.submit_feedback(
            feedback_type=FeedbackType.GENERAL,
            category=FeedbackCategory.OTHER,
            title="Mixed",
            content="The response was good but the wait was terrible.",
        )
        assert feedback.sentiment is not None

    def test_all_caps(self):
        feedback = self.engine.submit_feedback(
            feedback_type=FeedbackType.GENERAL,
            category=FeedbackCategory.OTHER,
            title="Caps",
            content="EXCELLENT SERVICE THANK YOU",
        )
        assert feedback.sentiment is not None

    def test_special_characters(self):
        feedback = self.engine.submit_feedback(
            feedback_type=FeedbackType.GENERAL,
            category=FeedbackCategory.OTHER,
            title="Special",
            content="Great!!! Amazing!!! Thank you!!!",
        )
        assert feedback.sentiment is not None
