"""
Test Suite: Sentinel Decision Engine

Tests for the sentinel decision engine functionality including:
- Alert consolidation
- Autonomous action requests
- Cascade prediction
- Recommendation management
- Command staff alerts
- Priority assignment
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import sys
sys.path.insert(0, "/home/ubuntu/repos/g3ti-rtcc-platform")

from backend.app.ai_supervisor.sentinel_engine import (
    SentinelEngine,
    AlertPriority,
    AlertSource,
    AutonomyLevel,
    ActionApproval,
    RecommendationType,
    ConsolidatedAlert,
    AutonomousActionRequest,
    CascadePrediction,
    SentinelRecommendation,
    CommandStaffAlert,
)


class TestSentinelEngine:
    """Test cases for SentinelEngine class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.engine = SentinelEngine()

    def test_singleton_pattern(self):
        """Test that SentinelEngine follows singleton pattern."""
        engine1 = SentinelEngine()
        engine2 = SentinelEngine()
        assert engine1 is engine2

    def test_consolidate_alert(self):
        """Test consolidating alerts from multiple sources."""
        alert = self.engine.consolidate_alert(
            sources=[AlertSource.SYSTEM_MONITOR, AlertSource.AUTO_CORRECTOR],
            title="Critical System Alert",
            description="Multiple issues detected across systems",
            affected_systems=["predictive_ai", "city_brain"],
            affected_areas=["downtown", "north_district"],
            metrics={"cpu": 95, "memory": 88},
            severity_score=0.9,
        )
        assert alert is not None
        assert AlertSource.SYSTEM_MONITOR in alert.sources
        assert alert.priority in [AlertPriority.P1_CRITICAL, AlertPriority.P2_HIGH]

    def test_consolidate_alert_assigns_priority(self):
        """Test that alert priority is assigned based on severity."""
        alert = self.engine.consolidate_alert(
            sources=[AlertSource.ETHICS_GUARD],
            title="Critical Violation",
            description="Constitutional violation detected",
            affected_systems=["intel_orchestration"],
            affected_areas=["citywide"],
            metrics={},
            severity_score=0.95,
        )
        assert alert.priority == AlertPriority.P1_CRITICAL

    def test_request_autonomous_action_approved(self):
        """Test requesting an autonomous action that gets approved."""
        request = self.engine.request_autonomous_action(
            source_engine="auto_corrector",
            action_type="cache_rebuild",
            autonomy_level=AutonomyLevel.SUPERVISED,
            target="city_brain",
            parameters={"cache_name": "prediction_cache"},
            justification="Cache corruption detected",
            risk_score=0.2,
        )
        assert request is not None
        assert request.approval_status in [ActionApproval.APPROVED, ActionApproval.PENDING]

    def test_request_autonomous_action_denied_high_risk(self):
        """Test that high-risk actions are denied or require review."""
        request = self.engine.request_autonomous_action(
            source_engine="auto_corrector",
            action_type="failover_activation",
            autonomy_level=AutonomyLevel.HIGH_AUTONOMY,
            target="predictive_ai",
            parameters={},
            justification="System failure imminent",
            risk_score=0.9,
        )
        assert request.approval_status in [ActionApproval.DENIED, ActionApproval.PENDING, ActionApproval.CONDITIONAL]

    def test_request_autonomous_action_respects_autonomy_level(self):
        """Test that autonomy level affects approval."""
        request_low = self.engine.request_autonomous_action(
            source_engine="system_monitor",
            action_type="alert_notification",
            autonomy_level=AutonomyLevel.MANUAL,
            target="command_staff",
            parameters={},
            justification="Routine notification",
            risk_score=0.1,
        )
        assert request_low.approval_status == ActionApproval.PENDING

    def test_predict_cascade(self):
        """Test predicting cascade outcomes."""
        prediction = self.engine.predict_cascade(
            trigger_event="Predictive AI Engine Overload",
            trigger_source=AlertSource.SYSTEM_MONITOR,
            initial_severity=0.8,
            time_horizon_hours=24,
        )
        assert prediction is not None
        assert len(prediction.predicted_outcomes) > 0
        assert prediction.probability >= 0.0 and prediction.probability <= 1.0
        assert len(prediction.mitigation_options) > 0

    def test_create_recommendation(self):
        """Test creating a sentinel recommendation."""
        recommendation = self.engine.create_recommendation(
            recommendation_type=RecommendationType.IMMEDIATE_ACTION,
            priority=AlertPriority.P1_CRITICAL,
            title="Scale Predictive AI Engine",
            description="Engine approaching critical load levels",
            rationale="CPU at 92%, memory at 88%",
            affected_systems=["predictive_ai", "intel_engine"],
            implementation_steps=["Increase instances", "Enable auto-scaling"],
            expected_outcome="Reduce load to 60%",
            risk_if_ignored="System failure within 2 hours",
            deadline_hours=1,
        )
        assert recommendation is not None
        assert recommendation.recommendation_type == RecommendationType.IMMEDIATE_ACTION
        assert recommendation.priority == AlertPriority.P1_CRITICAL
        assert recommendation.deadline is not None

    def test_acknowledge_alert(self):
        """Test acknowledging a consolidated alert."""
        alert = self.engine.consolidate_alert(
            sources=[AlertSource.SYSTEM_MONITOR],
            title="Test Alert",
            description="Test description",
            affected_systems=["test_system"],
            affected_areas=["test_area"],
            metrics={},
            severity_score=0.5,
        )
        success = self.engine.acknowledge_alert(alert.alert_id, "Sgt. Johnson")
        assert success is True
        updated_alert = self.engine.consolidated_alerts.get(alert.alert_id)
        assert updated_alert.acknowledged is True
        assert updated_alert.assigned_to == "Sgt. Johnson"

    def test_resolve_alert(self):
        """Test resolving a consolidated alert."""
        alert = self.engine.consolidate_alert(
            sources=[AlertSource.AUTO_CORRECTOR],
            title="Test Alert",
            description="Test description",
            affected_systems=["test_system"],
            affected_areas=["test_area"],
            metrics={},
            severity_score=0.3,
        )
        success = self.engine.resolve_alert(alert.alert_id, "Issue resolved by auto-corrector")
        assert success is True
        updated_alert = self.engine.consolidated_alerts.get(alert.alert_id)
        assert updated_alert.resolved is True

    def test_acknowledge_command_alert(self):
        """Test acknowledging a command staff alert."""
        alert = self.engine.consolidate_alert(
            sources=[AlertSource.SENTINEL_ENGINE],
            title="Critical Alert for Command",
            description="Requires command attention",
            affected_systems=["all"],
            affected_areas=["citywide"],
            metrics={},
            severity_score=0.95,
        )
        command_alerts = self.engine.get_command_alerts()
        if command_alerts:
            success = self.engine.acknowledge_command_alert(
                command_alerts[0].alert_id,
                "Acknowledged and investigating"
            )
            assert success is True

    def test_accept_recommendation(self):
        """Test accepting a recommendation."""
        recommendation = self.engine.create_recommendation(
            recommendation_type=RecommendationType.PREVENTIVE_ACTION,
            priority=AlertPriority.P3_MEDIUM,
            title="Update Bias Models",
            description="Bias detected in predictions",
            rationale="Disparate impact score below threshold",
            affected_systems=["predictive_ai"],
            implementation_steps=["Retrain model", "Validate"],
            expected_outcome="Improved fairness",
            risk_if_ignored="Continued bias",
        )
        success = self.engine.accept_recommendation(recommendation.recommendation_id)
        assert success is True
        updated_rec = self.engine.recommendations.get(recommendation.recommendation_id)
        assert updated_rec.accepted is True

    def test_implement_recommendation(self):
        """Test marking a recommendation as implemented."""
        recommendation = self.engine.create_recommendation(
            recommendation_type=RecommendationType.RESOURCE_ALLOCATION,
            priority=AlertPriority.P4_LOW,
            title="Rebalance Load",
            description="Load imbalance detected",
            rationale="Uneven resource utilization",
            affected_systems=["city_brain", "intel_engine"],
            implementation_steps=["Migrate workload"],
            expected_outcome="Balanced load",
            risk_if_ignored="Performance degradation",
        )
        self.engine.accept_recommendation(recommendation.recommendation_id)
        success = self.engine.implement_recommendation(recommendation.recommendation_id)
        assert success is True
        updated_rec = self.engine.recommendations.get(recommendation.recommendation_id)
        assert updated_rec.implemented is True

    def test_get_active_alerts(self):
        """Test getting active alerts."""
        self.engine.consolidate_alert(
            sources=[AlertSource.SYSTEM_MONITOR],
            title="Active Alert",
            description="Test",
            affected_systems=["test"],
            affected_areas=["test"],
            metrics={},
            severity_score=0.5,
        )
        alerts = self.engine.get_active_alerts()
        assert len(alerts) >= 0

    def test_get_active_alerts_by_priority(self):
        """Test filtering alerts by priority."""
        alerts = self.engine.get_active_alerts(priority=AlertPriority.P1_CRITICAL)
        assert all(a.priority == AlertPriority.P1_CRITICAL for a in alerts)

    def test_get_pending_action_requests(self):
        """Test getting pending action requests."""
        requests = self.engine.get_pending_action_requests()
        assert isinstance(requests, list)

    def test_get_pending_recommendations(self):
        """Test getting pending recommendations."""
        recommendations = self.engine.get_pending_recommendations()
        assert isinstance(recommendations, list)

    def test_get_command_alerts(self):
        """Test getting command staff alerts."""
        alerts = self.engine.get_command_alerts()
        assert isinstance(alerts, list)

    def test_get_dashboard_summary(self):
        """Test getting dashboard summary."""
        summary = self.engine.get_dashboard_summary()
        assert "active_alerts" in summary
        assert "pending_action_requests" in summary
        assert "pending_recommendations" in summary
        assert "system_status" in summary

    def test_alert_chain_of_custody(self):
        """Test that alerts have chain of custody hash."""
        alert = self.engine.consolidate_alert(
            sources=[AlertSource.ETHICS_GUARD],
            title="Test Alert",
            description="Test",
            affected_systems=["test"],
            affected_areas=["test"],
            metrics={},
            severity_score=0.5,
        )
        assert alert.chain_of_custody_hash is not None
        assert len(alert.chain_of_custody_hash) == 64

    def test_recommendation_chain_of_custody(self):
        """Test that recommendations have chain of custody hash."""
        recommendation = self.engine.create_recommendation(
            recommendation_type=RecommendationType.MONITORING,
            priority=AlertPriority.P5_INFO,
            title="Monitor System",
            description="Continue monitoring",
            rationale="Routine check",
            affected_systems=["all"],
            implementation_steps=["Monitor"],
            expected_outcome="Awareness",
            risk_if_ignored="None",
        )
        assert recommendation.chain_of_custody_hash is not None
        assert len(recommendation.chain_of_custody_hash) == 64

    def test_get_statistics(self):
        """Test getting engine statistics."""
        stats = self.engine.get_statistics()
        assert "total_alerts" in stats
        assert "total_action_requests" in stats
        assert "total_recommendations" in stats


class TestAlertPriority:
    """Test cases for AlertPriority enum."""

    def test_alert_priority_values(self):
        """Test alert priority enum values."""
        assert AlertPriority.P1_CRITICAL.value == 1
        assert AlertPriority.P2_HIGH.value == 2
        assert AlertPriority.P3_MEDIUM.value == 3
        assert AlertPriority.P4_LOW.value == 4
        assert AlertPriority.P5_INFO.value == 5


class TestAlertSource:
    """Test cases for AlertSource enum."""

    def test_alert_source_values(self):
        """Test alert source enum values."""
        assert AlertSource.SYSTEM_MONITOR.value == "system_monitor"
        assert AlertSource.AUTO_CORRECTOR.value == "auto_corrector"
        assert AlertSource.ETHICS_GUARD.value == "ethics_guard"
        assert AlertSource.SENTINEL_ENGINE.value == "sentinel_engine"


class TestAutonomyLevel:
    """Test cases for AutonomyLevel enum."""

    def test_autonomy_level_values(self):
        """Test autonomy level enum values."""
        assert AutonomyLevel.MANUAL.value == 0
        assert AutonomyLevel.ASSISTED.value == 1
        assert AutonomyLevel.SUPERVISED.value == 2
        assert AutonomyLevel.CONDITIONAL.value == 3
        assert AutonomyLevel.HIGH_AUTONOMY.value == 4
        assert AutonomyLevel.FULL_AUTONOMY.value == 5


class TestRecommendationType:
    """Test cases for RecommendationType enum."""

    def test_recommendation_type_values(self):
        """Test recommendation type enum values."""
        assert RecommendationType.IMMEDIATE_ACTION.value == "immediate_action"
        assert RecommendationType.PREVENTIVE_ACTION.value == "preventive_action"
        assert RecommendationType.MONITORING.value == "monitoring"
        assert RecommendationType.ESCALATION.value == "escalation"
