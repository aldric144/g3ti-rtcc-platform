"""
Test Suite: Public Feedback Engine
Phase 36: Public Safety Guardian
"""

import pytest
from datetime import datetime, timedelta

from backend.app.public_guardian.public_feedback_engine import (
    PublicFeedbackEngine,
    FeedbackType,
    SentimentLevel,
    FeedbackCategory,
    FeedbackStatus,
    PublicFeedback,
    FeedbackTrend,
    NeighborhoodInsight,
)


class TestPublicFeedbackEngine:
    def setup_method(self):
        self.engine = PublicFeedbackEngine()

    def test_engine_singleton(self):
        engine2 = PublicFeedbackEngine()
        assert self.engine is engine2

    def test_submit_feedback(self):
        feedback = self.engine.submit_feedback(
            feedback_type=FeedbackType.GENERAL,
            category=FeedbackCategory.OTHER,
            title="Test Feedback",
            content="This is a test feedback submission.",
        )
        assert feedback is not None
        assert feedback.feedback_id is not None
        assert feedback.title == "Test Feedback"

    def test_submit_feedback_with_all_fields(self):
        feedback = self.engine.submit_feedback(
            feedback_type=FeedbackType.SUGGESTION,
            category=FeedbackCategory.COMMUNITY_PROGRAMS,
            title="Youth Program Suggestion",
            content="We should have more youth basketball programs in the area.",
            neighborhood="West Riviera Beach",
            anonymous=True,
            contact_email="",
            tags=["youth", "sports", "community"],
        )
        assert feedback is not None
        assert feedback.neighborhood == "West Riviera Beach"

    def test_submit_complaint(self):
        feedback = self.engine.submit_feedback(
            feedback_type=FeedbackType.COMPLAINT,
            category=FeedbackCategory.RESPONSE_TIME,
            title="Slow Response",
            content="Response time was too slow for my call.",
            anonymous=False,
            contact_email="test@example.com",
        )
        assert feedback is not None
        assert feedback.feedback_type == FeedbackType.COMPLAINT

    def test_submit_praise(self):
        feedback = self.engine.submit_feedback(
            feedback_type=FeedbackType.PRAISE,
            category=FeedbackCategory.OFFICER_CONDUCT,
            title="Great Officer",
            content="The officer was very professional and helpful. Thank you!",
        )
        assert feedback is not None
        assert feedback.feedback_type == FeedbackType.PRAISE

    def test_sentiment_analysis_positive(self):
        feedback = self.engine.submit_feedback(
            feedback_type=FeedbackType.PRAISE,
            category=FeedbackCategory.OTHER,
            title="Great Service",
            content="Excellent service! Very helpful and professional. Thank you so much!",
        )
        assert feedback.sentiment in [SentimentLevel.POSITIVE, SentimentLevel.VERY_POSITIVE]
        assert feedback.sentiment_score > 0

    def test_sentiment_analysis_negative(self):
        feedback = self.engine.submit_feedback(
            feedback_type=FeedbackType.COMPLAINT,
            category=FeedbackCategory.OTHER,
            title="Poor Service",
            content="Terrible experience. Very disappointed and frustrated with the service.",
        )
        assert feedback.sentiment in [SentimentLevel.NEGATIVE, SentimentLevel.VERY_NEGATIVE]
        assert feedback.sentiment_score < 0

    def test_sentiment_analysis_neutral(self):
        feedback = self.engine.submit_feedback(
            feedback_type=FeedbackType.GENERAL,
            category=FeedbackCategory.OTHER,
            title="Information Request",
            content="I would like to know the hours of operation.",
        )
        assert feedback.sentiment is not None

    def test_update_feedback_status(self):
        feedback = self.engine.submit_feedback(
            feedback_type=FeedbackType.QUESTION,
            category=FeedbackCategory.COMMUNICATION,
            title="Question",
            content="When is the next town hall?",
        )
        updated = self.engine.update_feedback_status(
            feedback.feedback_id,
            FeedbackStatus.ACKNOWLEDGED,
            "Thank you for your question. The next town hall is on January 15th."
        )
        assert updated is not None
        assert updated.status == FeedbackStatus.ACKNOWLEDGED

    def test_get_feedback(self):
        feedback = self.engine.submit_feedback(
            feedback_type=FeedbackType.GENERAL,
            category=FeedbackCategory.OTHER,
            title="Retrievable Feedback",
            content="Test content",
        )
        retrieved = self.engine.get_feedback(feedback.feedback_id)
        assert retrieved is not None
        assert retrieved.feedback_id == feedback.feedback_id

    def test_get_feedback_by_neighborhood(self):
        self.engine.submit_feedback(
            feedback_type=FeedbackType.GENERAL,
            category=FeedbackCategory.SAFETY_CONCERNS,
            title="Neighborhood Feedback",
            content="Safety concern in the area",
            neighborhood="Singer Island",
        )
        feedback_list = self.engine.get_feedback_by_neighborhood("Singer Island")
        assert isinstance(feedback_list, list)

    def test_get_feedback_by_category(self):
        self.engine.submit_feedback(
            feedback_type=FeedbackType.CONCERN,
            category=FeedbackCategory.TRAFFIC,
            title="Traffic Concern",
            content="Speeding on Blue Heron Blvd",
        )
        feedback_list = self.engine.get_feedback_by_category(FeedbackCategory.TRAFFIC)
        assert isinstance(feedback_list, list)

    def test_get_feedback_by_sentiment(self):
        feedback_list = self.engine.get_feedback_by_sentiment(SentimentLevel.POSITIVE)
        assert isinstance(feedback_list, list)

    def test_get_recent_feedback(self):
        feedback_list = self.engine.get_recent_feedback(limit=10)
        assert isinstance(feedback_list, list)

    def test_detect_trends(self):
        trends = self.engine.detect_trends(period_days=30)
        assert isinstance(trends, list)

    def test_get_neighborhood_insight(self):
        insight = self.engine.get_neighborhood_insight("Downtown Riviera Beach")
        assert insight is not None
        assert hasattr(insight, "neighborhood")

    def test_get_all_insights(self):
        insights = self.engine.get_all_insights()
        assert isinstance(insights, list)

    def test_get_common_concerns(self):
        concerns = self.engine.get_common_concerns()
        assert isinstance(concerns, list)

    def test_get_sentiment_summary(self):
        summary = self.engine.get_sentiment_summary()
        assert "total" in summary
        assert "distribution" in summary

    def test_get_statistics(self):
        stats = self.engine.get_statistics()
        assert "total_feedback" in stats
        assert "sentiment_analyses" in stats

    def test_feedback_to_dict(self):
        feedback = self.engine.submit_feedback(
            feedback_type=FeedbackType.GENERAL,
            category=FeedbackCategory.OTHER,
            title="Dict Test",
            content="Test content",
        )
        feedback_dict = feedback.to_dict()
        assert "feedback_id" in feedback_dict
        assert "title" in feedback_dict
        assert "sentiment" in feedback_dict


class TestFeedbackType:
    def test_all_types_exist(self):
        expected = [
            "survey", "complaint", "praise", "suggestion",
            "question", "concern", "request", "general"
        ]
        for ft in expected:
            assert hasattr(FeedbackType, ft.upper())


class TestFeedbackCategory:
    def test_all_categories_exist(self):
        expected = [
            "response_time", "officer_conduct", "community_programs",
            "safety_concerns", "traffic", "noise", "property_crime",
            "youth_services", "communication", "accessibility", "other"
        ]
        for fc in expected:
            assert hasattr(FeedbackCategory, fc.upper())


class TestSentimentLevel:
    def test_all_levels_exist(self):
        expected = [
            "very_negative", "negative", "neutral", "positive", "very_positive"
        ]
        for sl in expected:
            assert hasattr(SentimentLevel, sl.upper())


class TestFeedbackStatus:
    def test_all_statuses_exist(self):
        expected = [
            "received", "under_review", "acknowledged",
            "in_progress", "resolved", "closed"
        ]
        for fs in expected:
            assert hasattr(FeedbackStatus, fs.upper())
