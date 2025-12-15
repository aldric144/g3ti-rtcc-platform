"""
Test Suite: Public Guardian REST API
Phase 36: Public Safety Guardian
"""

import pytest
from datetime import datetime, timedelta

from backend.app.api.public_guardian.public_guardian_router import (
    router,
    transparency_engine,
    engagement_engine,
    trust_engine,
    feedback_engine,
    validator,
    TransparencyReportRequest,
    TransparencyReportResponse,
    EventCreateRequest,
    EventResponse,
    AlertCreateRequest,
    AlertResponse,
    TrustScoreResponse,
    TrustScoreHistoryResponse,
    FeedbackSubmitRequest,
    FeedbackResponse,
    FeedbackTrendsResponse,
)


class TestTransparencyAPI:
    def test_router_exists(self):
        assert router is not None
        assert router.prefix == "/api/public"

    def test_transparency_engine_initialized(self):
        assert transparency_engine is not None

    @pytest.mark.asyncio
    async def test_get_transparency_report(self):
        from backend.app.api.public_guardian.public_guardian_router import get_transparency_report
        response = await get_transparency_report()
        assert response is not None
        assert hasattr(response, "report_id")

    @pytest.mark.asyncio
    async def test_get_weekly_report(self):
        from backend.app.api.public_guardian.public_guardian_router import get_weekly_report
        response = await get_weekly_report()
        assert response is not None

    @pytest.mark.asyncio
    async def test_get_monthly_report(self):
        from backend.app.api.public_guardian.public_guardian_router import get_monthly_report
        response = await get_monthly_report()
        assert response is not None

    @pytest.mark.asyncio
    async def test_get_quarterly_report(self):
        from backend.app.api.public_guardian.public_guardian_router import get_quarterly_report
        response = await get_quarterly_report()
        assert response is not None


class TestCommunityEngagementAPI:
    def test_engagement_engine_initialized(self):
        assert engagement_engine is not None

    @pytest.mark.asyncio
    async def test_get_community_events(self):
        from backend.app.api.public_guardian.public_guardian_router import get_community_events
        response = await get_community_events()
        assert response is not None
        assert "events" in response

    @pytest.mark.asyncio
    async def test_create_community_event(self):
        from backend.app.api.public_guardian.public_guardian_router import create_community_event
        request = EventCreateRequest(
            name="Test API Event",
            event_type="town_hall",
            description="Test event from API",
            location="City Hall",
            address="600 W Blue Heron Blvd",
            start_time=datetime.utcnow() + timedelta(days=7),
        )
        response = await create_community_event(request)
        assert response is not None
        assert response.name == "Test API Event"

    @pytest.mark.asyncio
    async def test_get_community_alerts(self):
        from backend.app.api.public_guardian.public_guardian_router import get_community_alerts
        response = await get_community_alerts()
        assert response is not None
        assert "alerts" in response

    @pytest.mark.asyncio
    async def test_create_community_alert(self):
        from backend.app.api.public_guardian.public_guardian_router import create_community_alert
        request = AlertCreateRequest(
            alert_type="safety_alert",
            title="Test API Alert",
            message="This is a test alert from the API",
            severity="medium",
            affected_areas=["Downtown Riviera Beach"],
        )
        response = await create_community_alert(request)
        assert response is not None
        assert response.title == "Test API Alert"


class TestTrustScoreAPI:
    def test_trust_engine_initialized(self):
        assert trust_engine is not None

    @pytest.mark.asyncio
    async def test_get_current_trust_score(self):
        from backend.app.api.public_guardian.public_guardian_router import get_current_trust_score
        response = await get_current_trust_score()
        assert response is not None

    @pytest.mark.asyncio
    async def test_get_trust_score_history(self):
        from backend.app.api.public_guardian.public_guardian_router import get_trust_score_history
        response = await get_trust_score_history()
        assert response is not None

    @pytest.mark.asyncio
    async def test_get_trust_score_breakdown(self):
        from backend.app.api.public_guardian.public_guardian_router import get_trust_score_breakdown
        response = await get_trust_score_breakdown()
        assert response is not None
        assert "metrics" in response

    @pytest.mark.asyncio
    async def test_get_neighborhood_trust_scores(self):
        from backend.app.api.public_guardian.public_guardian_router import get_neighborhood_trust_scores
        response = await get_neighborhood_trust_scores()
        assert response is not None
        assert "neighborhoods" in response

    @pytest.mark.asyncio
    async def test_run_fairness_audit(self):
        from backend.app.api.public_guardian.public_guardian_router import run_fairness_audit
        response = await run_fairness_audit()
        assert response is not None
        assert "passed" in response

    @pytest.mark.asyncio
    async def test_run_bias_audit(self):
        from backend.app.api.public_guardian.public_guardian_router import run_bias_audit
        response = await run_bias_audit()
        assert response is not None
        assert "passed" in response


class TestFeedbackAPI:
    def test_feedback_engine_initialized(self):
        assert feedback_engine is not None

    @pytest.mark.asyncio
    async def test_submit_feedback(self):
        from backend.app.api.public_guardian.public_guardian_router import submit_feedback
        request = FeedbackSubmitRequest(
            feedback_type="general",
            category="other",
            title="Test API Feedback",
            content="This is test feedback from the API",
            anonymous=True,
        )
        response = await submit_feedback(request)
        assert response is not None
        assert response.title == "Test API Feedback"

    @pytest.mark.asyncio
    async def test_get_feedback_trends(self):
        from backend.app.api.public_guardian.public_guardian_router import get_feedback_trends
        response = await get_feedback_trends()
        assert response is not None
        assert hasattr(response, "trends")

    @pytest.mark.asyncio
    async def test_get_recent_feedback(self):
        from backend.app.api.public_guardian.public_guardian_router import get_recent_feedback
        response = await get_recent_feedback()
        assert response is not None
        assert "feedback" in response

    @pytest.mark.asyncio
    async def test_get_sentiment_summary(self):
        from backend.app.api.public_guardian.public_guardian_router import get_sentiment_summary
        response = await get_sentiment_summary()
        assert response is not None


class TestComplianceAPI:
    def test_validator_initialized(self):
        assert validator is not None

    @pytest.mark.asyncio
    async def test_check_compliance(self):
        from backend.app.api.public_guardian.public_guardian_router import check_compliance
        response = await check_compliance("Clean data")
        assert response is not None

    @pytest.mark.asyncio
    async def test_redact_data(self):
        from backend.app.api.public_guardian.public_guardian_router import redact_data
        response = await redact_data("SSN: 123-45-6789")
        assert response is not None
        assert "redacted_data" in response

    @pytest.mark.asyncio
    async def test_get_compliance_rules(self):
        from backend.app.api.public_guardian.public_guardian_router import get_compliance_rules
        response = await get_compliance_rules()
        assert response is not None
        assert "rules" in response

    @pytest.mark.asyncio
    async def test_get_compliance_summary(self):
        from backend.app.api.public_guardian.public_guardian_router import get_compliance_summary
        response = await get_compliance_summary()
        assert response is not None


class TestStatisticsAPI:
    @pytest.mark.asyncio
    async def test_get_public_guardian_statistics(self):
        from backend.app.api.public_guardian.public_guardian_router import get_public_guardian_statistics
        response = await get_public_guardian_statistics()
        assert response is not None
        assert "transparency" in response
        assert "engagement" in response
        assert "trust_score" in response
        assert "feedback" in response
        assert "compliance" in response

    @pytest.mark.asyncio
    async def test_health_check(self):
        from backend.app.api.public_guardian.public_guardian_router import health_check
        response = await health_check()
        assert response is not None
        assert response["status"] == "healthy"
        assert response["service"] == "public_guardian"
