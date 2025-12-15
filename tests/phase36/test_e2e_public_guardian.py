"""
Test Suite: End-to-End Public Guardian Integration
Phase 36: Public Safety Guardian
"""

import pytest
import asyncio
from datetime import datetime, timedelta

from backend.app.public_guardian.transparency_engine import (
    TransparencyReportEngine,
    ReportType,
    ReportPeriod,
)
from backend.app.public_guardian.community_engagement import (
    CommunityEngagementEngine,
    EventType,
    AlertType,
    AlertSeverity,
    NotificationChannel,
)
from backend.app.public_guardian.trust_score_engine import (
    TrustScoreEngine,
    TrustMetric,
)
from backend.app.public_guardian.public_feedback_engine import (
    PublicFeedbackEngine,
    FeedbackType,
    FeedbackCategory,
    FeedbackStatus,
)
from backend.app.public_guardian.data_access_validator import (
    PublicDataAccessValidator,
    ComplianceFramework,
)
from backend.app.websockets.public_guardian_ws import (
    PublicGuardianWSManager,
    PublicWSChannel,
)


class TestE2ETransparencyFlow:
    def setup_method(self):
        self.transparency = TransparencyReportEngine()
        self.validator = PublicDataAccessValidator()

    def test_generate_and_validate_report(self):
        report = self.transparency.generate_report(
            report_type=ReportType.COMPREHENSIVE,
            period=ReportPeriod.WEEKLY
        )
        assert report is not None

        report_json = self.transparency.export_to_json(report.report_id)
        assert report_json is not None

        redacted, result = self.validator.validate_and_redact(str(report_json))
        assert result is not None

    def test_weekly_report_compliance(self):
        report = self.transparency.get_weekly_report()
        assert len(report.compliance_frameworks) > 0

    def test_heatmap_privacy(self):
        report = self.transparency.generate_report(
            report_type=ReportType.HEATMAP,
            period=ReportPeriod.WEEKLY
        )
        for cell in report.heatmap.cells:
            assert cell.blur_radius >= 100


class TestE2ECommunityEngagementFlow:
    def setup_method(self):
        self.engagement = CommunityEngagementEngine()
        self.ws_manager = PublicGuardianWSManager()

    def test_create_event_and_notify(self):
        event = self.engagement.create_event(
            name="E2E Test Town Hall",
            event_type=EventType.TOWN_HALL,
            description="End-to-end test event",
            location="City Hall",
            address="600 W Blue Heron Blvd",
            start_time=datetime.utcnow() + timedelta(days=7),
            target_neighborhoods=["Downtown Riviera Beach"],
        )
        assert event is not None
        assert event.event_id is not None

    def test_create_alert_flow(self):
        alert = self.engagement.create_alert(
            alert_type=AlertType.SAFETY_ALERT,
            title="E2E Test Alert",
            message="This is an end-to-end test alert",
            severity=AlertSeverity.LOW,
            affected_areas=["Downtown Riviera Beach"],
            channels=[NotificationChannel.SMS, NotificationChannel.EMAIL],
        )
        assert alert is not None
        assert alert.active is True

        success = self.engagement.deactivate_alert(alert.alert_id)
        assert success is True

    def test_event_lifecycle(self):
        event = self.engagement.create_event(
            name="Lifecycle Test Event",
            event_type=EventType.COMMUNITY_MEETING,
            location="Community Center",
            start_time=datetime.utcnow() + timedelta(days=1),
        )

        updated = self.engagement.update_event(
            event.event_id,
            description="Updated description"
        )
        assert updated is not None

        success = self.engagement.cancel_event(event.event_id, "Test cancellation")
        assert success is True


class TestE2ETrustScoreFlow:
    def setup_method(self):
        self.trust = TrustScoreEngine()

    def test_calculate_and_audit_trust_score(self):
        score = self.trust.calculate_trust_score()
        assert score is not None
        assert 0 <= score.overall_score <= 100

        fairness = self.trust.run_fairness_audit()
        assert "passed" in fairness

        bias = self.trust.run_bias_audit()
        assert "passed" in bias

    def test_trust_score_with_neighborhoods(self):
        score = self.trust.calculate_trust_score()
        neighborhoods = self.trust.get_all_neighborhood_scores()
        assert len(neighborhoods) > 0

        for nb in neighborhoods:
            assert 0 <= nb.trust_score <= 100

    def test_trust_score_history(self):
        self.trust.calculate_trust_score()
        self.trust.calculate_trust_score()
        history = self.trust.get_score_history(limit=10)
        assert len(history.scores) > 0


class TestE2EFeedbackFlow:
    def setup_method(self):
        self.feedback = PublicFeedbackEngine()
        self.validator = PublicDataAccessValidator()

    def test_submit_and_process_feedback(self):
        feedback = self.feedback.submit_feedback(
            feedback_type=FeedbackType.SUGGESTION,
            category=FeedbackCategory.COMMUNITY_PROGRAMS,
            title="E2E Test Suggestion",
            content="This is an end-to-end test suggestion for community programs.",
            neighborhood="West Riviera Beach",
            anonymous=True,
        )
        assert feedback is not None
        assert feedback.sentiment is not None

        updated = self.feedback.update_feedback_status(
            feedback.feedback_id,
            FeedbackStatus.ACKNOWLEDGED,
            "Thank you for your suggestion."
        )
        assert updated.status == FeedbackStatus.ACKNOWLEDGED

    def test_feedback_sentiment_analysis(self):
        positive = self.feedback.submit_feedback(
            feedback_type=FeedbackType.PRAISE,
            category=FeedbackCategory.OFFICER_CONDUCT,
            title="Great Officer",
            content="Excellent service! Very professional and helpful.",
        )
        assert positive.sentiment_score > 0

        negative = self.feedback.submit_feedback(
            feedback_type=FeedbackType.COMPLAINT,
            category=FeedbackCategory.RESPONSE_TIME,
            title="Slow Response",
            content="Terrible response time. Very disappointed.",
        )
        assert negative.sentiment_score < 0

    def test_feedback_trends_detection(self):
        for i in range(3):
            self.feedback.submit_feedback(
                feedback_type=FeedbackType.CONCERN,
                category=FeedbackCategory.TRAFFIC,
                title=f"Traffic Concern {i}",
                content="Speeding on Blue Heron Blvd",
            )
        trends = self.feedback.detect_trends(period_days=30)
        assert isinstance(trends, list)


class TestE2EComplianceFlow:
    def setup_method(self):
        self.validator = PublicDataAccessValidator()
        self.transparency = TransparencyReportEngine()

    def test_validate_report_data(self):
        report = self.transparency.generate_report(
            report_type=ReportType.COMPREHENSIVE,
            period=ReportPeriod.WEEKLY
        )
        report_dict = report.to_dict()

        result = self.validator.validate_data(str(report_dict))
        assert result is not None

    def test_redact_sensitive_data(self):
        sensitive_data = """
        Report contains:
        - SSN: 123-45-6789
        - Phone: 555-123-4567
        - Email: test@example.com
        - DOB: 01/15/1990
        """
        redacted, result = self.validator.validate_and_redact(sensitive_data)
        assert "123-45-6789" not in redacted
        assert "555-123-4567" not in redacted
        assert "test@example.com" not in redacted

    def test_compliance_framework_coverage(self):
        frameworks = [
            ComplianceFramework.CJIS,
            ComplianceFramework.VAWA,
            ComplianceFramework.HIPAA,
            ComplianceFramework.FERPA,
            ComplianceFramework.FLORIDA_PUBLIC_RECORDS,
        ]
        for framework in frameworks:
            rules = self.validator.get_rules_by_framework(framework)
            assert isinstance(rules, list)


class TestE2EWebSocketFlow:
    def setup_method(self):
        self.ws_manager = PublicGuardianWSManager()

    @pytest.mark.asyncio
    async def test_websocket_connection_flow(self):
        conn = await self.ws_manager.connect(
            channels=[PublicWSChannel.ENGAGEMENT, PublicWSChannel.TRUST]
        )
        assert conn is not None

        await self.ws_manager.subscribe(conn.connection_id, PublicWSChannel.SENTIMENT)
        assert PublicWSChannel.SENTIMENT in conn.channels

        await self.ws_manager.unsubscribe(conn.connection_id, PublicWSChannel.TRUST)
        assert PublicWSChannel.TRUST not in conn.channels

        await self.ws_manager.disconnect(conn.connection_id)

    @pytest.mark.asyncio
    async def test_websocket_broadcast_flow(self):
        conn = await self.ws_manager.connect(channels=[PublicWSChannel.ENGAGEMENT])

        sent = await self.ws_manager.broadcast_new_event(
            event_id="e2e-event-001",
            title="E2E Test Event",
            description="Test event broadcast",
            location="City Hall",
            start_time=datetime.utcnow(),
        )
        assert sent >= 1

        await self.ws_manager.disconnect(conn.connection_id)


class TestE2EIntegration:
    def setup_method(self):
        self.transparency = TransparencyReportEngine()
        self.engagement = CommunityEngagementEngine()
        self.trust = TrustScoreEngine()
        self.feedback = PublicFeedbackEngine()
        self.validator = PublicDataAccessValidator()

    def test_full_public_guardian_flow(self):
        report = self.transparency.generate_report(
            report_type=ReportType.COMPREHENSIVE,
            period=ReportPeriod.WEEKLY
        )
        assert report is not None

        event = self.engagement.create_event(
            name="Integration Test Event",
            event_type=EventType.TOWN_HALL,
            location="City Hall",
            start_time=datetime.utcnow() + timedelta(days=7),
        )
        assert event is not None

        score = self.trust.calculate_trust_score()
        assert score is not None

        feedback = self.feedback.submit_feedback(
            feedback_type=FeedbackType.GENERAL,
            category=FeedbackCategory.OTHER,
            title="Integration Test",
            content="Testing the full integration flow.",
        )
        assert feedback is not None

        redacted, result = self.validator.validate_and_redact(
            f"Report {report.report_id}, Event {event.event_id}"
        )
        assert result is not None

    def test_statistics_aggregation(self):
        transparency_stats = self.transparency.get_statistics()
        engagement_stats = self.engagement.get_statistics()
        trust_stats = self.trust.get_statistics()
        feedback_stats = self.feedback.get_statistics()
        validator_stats = self.validator.get_statistics()

        assert "reports_generated" in transparency_stats
        assert "events_created" in engagement_stats
        assert "current_score" in trust_stats
        assert "total_feedback" in feedback_stats
        assert "total_validations" in validator_stats


class TestE2EDataFlow:
    def setup_method(self):
        self.transparency = TransparencyReportEngine()
        self.feedback = PublicFeedbackEngine()
        self.trust = TrustScoreEngine()

    def test_feedback_affects_trust(self):
        initial_score = self.trust.get_current_score()

        for i in range(5):
            self.feedback.submit_feedback(
                feedback_type=FeedbackType.PRAISE,
                category=FeedbackCategory.OFFICER_CONDUCT,
                title=f"Praise {i}",
                content="Excellent service!",
            )

        self.trust.calculate_trust_score()
        updated_score = self.trust.get_current_score()

        assert updated_score is not None

    def test_report_includes_feedback_trends(self):
        self.feedback.submit_feedback(
            feedback_type=FeedbackType.CONCERN,
            category=FeedbackCategory.SAFETY_CONCERNS,
            title="Safety Concern",
            content="Safety issue in the area",
        )

        trends = self.feedback.detect_trends(period_days=30)
        report = self.transparency.generate_report(
            report_type=ReportType.SAFETY_TRENDS,
            period=ReportPeriod.WEEKLY
        )

        assert report is not None
        assert isinstance(trends, list)
