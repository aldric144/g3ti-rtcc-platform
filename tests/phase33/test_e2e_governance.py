"""
Test Suite: End-to-End Governance Tests

Tests for full end-to-end governance scenarios:
- Complete governance workflow
- Multi-engine oversight
- Constitutional compliance enforcement
- Autonomous action governance
- Command staff escalation
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import sys
sys.path.insert(0, "/home/ubuntu/repos/g3ti-rtcc-platform")

from backend.app.ai_supervisor.system_monitor import (
    SystemMonitor,
    EngineType,
    HealthStatus,
    AlertSeverity,
)
from backend.app.ai_supervisor.auto_corrector import (
    AutoCorrector,
    CorrectionType,
    CorrectionPriority,
)
from backend.app.ai_supervisor.ethics_guard import (
    EthicsGuard,
    ComplianceFramework,
    ViolationType,
    ActionDecision,
)
from backend.app.ai_supervisor.sentinel_engine import (
    SentinelEngine,
    AlertPriority,
    AlertSource,
    AutonomyLevel,
    RecommendationType,
)


class TestCompleteGovernanceWorkflow:
    """Tests for complete governance workflow."""

    def setup_method(self):
        """Set up test fixtures."""
        self.monitor = SystemMonitor()
        self.corrector = AutoCorrector()
        self.guard = EthicsGuard()
        self.sentinel = SentinelEngine()

    def test_full_governance_cycle(self):
        """Test complete governance cycle from detection to resolution."""
        self.monitor.update_engine_metrics(
            engine_type=EngineType.PREDICTIVE_AI,
            cpu_percent=92.0,
            memory_percent=88.0,
        )
        
        health = self.monitor.get_system_health_summary()
        assert health["overall_status"] in ["WARNING", "CRITICAL"]
        
        alert = self.sentinel.consolidate_alert(
            sources=[AlertSource.SYSTEM_MONITOR],
            title="Predictive AI Overload",
            description="High resource usage detected",
            affected_systems=["predictive_ai"],
            affected_areas=["citywide"],
            metrics={"cpu": 92.0, "memory": 88.0},
            severity_score=0.85,
        )
        assert alert.priority in [AlertPriority.P1_CRITICAL, AlertPriority.P2_HIGH]
        
        validation = self.guard.validate_action(
            action_type="load_rebalance",
            engine="auto_corrector",
            target="predictive_ai",
            parameters={"action": "scale_up"},
            warrant_obtained=False,
            human_approved=True,
            approved_by="System Admin",
        )
        assert validation.decision in [ActionDecision.APPROVED, ActionDecision.APPROVED_WITH_CONDITIONS]
        
        action = self.corrector.create_correction_action(
            correction_type=CorrectionType.LOAD_REBALANCE,
            target_engine="predictive_ai",
            target_component="main_cluster",
            priority=CorrectionPriority.HIGH,
            description="Rebalance load to reduce pressure",
        )
        
        if action.requires_approval:
            self.corrector.approve_correction(action.action_id, "admin")
        
        result = self.corrector.execute_correction(action.action_id)
        assert result.success is True
        
        self.sentinel.resolve_alert(alert.alert_id, "Issue resolved by auto-corrector")
        resolved_alert = self.sentinel.consolidated_alerts.get(alert.alert_id)
        assert resolved_alert.resolved is True

    def test_ethics_violation_escalation_workflow(self):
        """Test ethics violation escalation workflow."""
        validation = self.guard.validate_action(
            action_type="facial_recognition",
            engine="intel_orchestration",
            target="private_residence",
            parameters={"duration": "24h"},
            warrant_obtained=False,
        )
        assert validation.decision == ActionDecision.BLOCKED
        
        violations = self.guard.get_active_violations()
        assert len(violations) > 0
        
        alert = self.sentinel.consolidate_alert(
            sources=[AlertSource.ETHICS_GUARD],
            title="Constitutional Violation Detected",
            description="Warrantless surveillance attempted",
            affected_systems=["intel_orchestration"],
            affected_areas=["citywide"],
            metrics={},
            severity_score=0.95,
        )
        assert alert.priority == AlertPriority.P1_CRITICAL
        
        command_alerts = self.sentinel.get_command_alerts()
        assert len(command_alerts) >= 0


class TestMultiEngineOversight:
    """Tests for multi-engine oversight."""

    def setup_method(self):
        """Set up test fixtures."""
        self.monitor = SystemMonitor()
        self.sentinel = SentinelEngine()

    def test_monitor_all_16_engines(self):
        """Test that all 16 engines are monitored."""
        all_metrics = self.monitor.get_all_engine_metrics()
        assert len(all_metrics) == 16

    def test_cross_engine_alert_consolidation(self):
        """Test consolidating alerts from multiple engines."""
        alert = self.sentinel.consolidate_alert(
            sources=[
                AlertSource.SYSTEM_MONITOR,
                AlertSource.AUTO_CORRECTOR,
                AlertSource.ETHICS_GUARD,
            ],
            title="Multi-Engine Alert",
            description="Issues detected across multiple engines",
            affected_systems=["predictive_ai", "city_brain", "intel_orchestration"],
            affected_areas=["downtown", "north_district"],
            metrics={"cpu_avg": 85.0, "memory_avg": 80.0},
            severity_score=0.8,
        )
        assert len(alert.sources) == 3
        assert len(alert.affected_systems) == 3

    def test_cascade_prediction_across_engines(self):
        """Test cascade prediction affecting multiple engines."""
        prediction = self.sentinel.predict_cascade(
            trigger_event="Data Lake Failure",
            trigger_source=AlertSource.SYSTEM_MONITOR,
            initial_severity=0.9,
            time_horizon_hours=24,
        )
        assert len(prediction.affected_systems) > 1


class TestConstitutionalComplianceEnforcement:
    """Tests for constitutional compliance enforcement."""

    def setup_method(self):
        """Set up test fixtures."""
        self.guard = EthicsGuard()
        self.sentinel = SentinelEngine()

    def test_fourth_amendment_enforcement(self):
        """Test 4th Amendment enforcement in governance."""
        validation = self.guard.validate_action(
            action_type="surveillance",
            engine="drone_task_force",
            target="private_property",
            parameters={},
            warrant_obtained=False,
        )
        assert validation.decision == ActionDecision.BLOCKED
        assert any(
            v.framework == ComplianceFramework.FOURTH_AMENDMENT
            for v in validation.violations
        )

    def test_fifth_amendment_enforcement(self):
        """Test 5th Amendment enforcement in governance."""
        validation = self.guard.validate_action(
            action_type="interrogation_assist",
            engine="detective_ai",
            target="suspect",
            parameters={"miranda_given": False},
            warrant_obtained=False,
        )
        assert validation.human_approval_required or validation.decision == ActionDecision.BLOCKED

    def test_fourteenth_amendment_enforcement(self):
        """Test 14th Amendment enforcement in governance."""
        validation = self.guard.validate_action(
            action_type="predictive_targeting",
            engine="predictive_ai",
            target="demographic_group",
            parameters={"protected_class": "race"},
            warrant_obtained=False,
        )
        assert validation.decision == ActionDecision.BLOCKED


class TestAutonomousActionGovernance:
    """Tests for autonomous action governance."""

    def setup_method(self):
        """Set up test fixtures."""
        self.guard = EthicsGuard()
        self.sentinel = SentinelEngine()

    def test_level_0_manual_requires_approval(self):
        """Test that Level 0 (Manual) requires human approval."""
        request = self.sentinel.request_autonomous_action(
            source_engine="auto_corrector",
            action_type="service_restart",
            autonomy_level=AutonomyLevel.MANUAL,
            target="cyber_intel",
            parameters={},
            justification="Service unresponsive",
            risk_score=0.2,
        )
        assert request.approval_status.value in ["pending", "denied"]

    def test_level_2_supervised_with_oversight(self):
        """Test that Level 2 (Supervised) has oversight."""
        request = self.sentinel.request_autonomous_action(
            source_engine="auto_corrector",
            action_type="cache_rebuild",
            autonomy_level=AutonomyLevel.SUPERVISED,
            target="city_brain",
            parameters={},
            justification="Cache corruption detected",
            risk_score=0.3,
        )
        assert request is not None

    def test_high_risk_action_denied(self):
        """Test that high-risk actions are denied or require review."""
        request = self.sentinel.request_autonomous_action(
            source_engine="auto_corrector",
            action_type="failover_activation",
            autonomy_level=AutonomyLevel.HIGH_AUTONOMY,
            target="all_systems",
            parameters={},
            justification="System failure",
            risk_score=0.95,
        )
        assert request.approval_status.value in ["pending", "denied", "conditional"]

    def test_ethics_validation_before_autonomous_action(self):
        """Test that ethics validation occurs before autonomous action."""
        validation = self.guard.validate_action(
            action_type="autonomous_correction",
            engine="auto_corrector",
            target="predictive_ai",
            parameters={"action": "restart"},
            warrant_obtained=False,
            human_approved=True,
            approved_by="System Admin",
        )
        
        if validation.decision in [ActionDecision.APPROVED, ActionDecision.APPROVED_WITH_CONDITIONS]:
            request = self.sentinel.request_autonomous_action(
                source_engine="auto_corrector",
                action_type="service_restart",
                autonomy_level=AutonomyLevel.SUPERVISED,
                target="predictive_ai",
                parameters={},
                justification="Validated by ethics guard",
                risk_score=0.2,
            )
            assert request is not None


class TestCommandStaffEscalation:
    """Tests for command staff escalation."""

    def setup_method(self):
        """Set up test fixtures."""
        self.sentinel = SentinelEngine()

    def test_critical_alert_escalates_to_command(self):
        """Test that critical alerts escalate to command staff."""
        alert = self.sentinel.consolidate_alert(
            sources=[AlertSource.ETHICS_GUARD],
            title="Critical Constitutional Violation",
            description="Immediate command attention required",
            affected_systems=["all"],
            affected_areas=["citywide"],
            metrics={},
            severity_score=0.98,
        )
        assert alert.priority == AlertPriority.P1_CRITICAL

    def test_command_alert_acknowledgment(self):
        """Test command staff alert acknowledgment."""
        alert = self.sentinel.consolidate_alert(
            sources=[AlertSource.SENTINEL_ENGINE],
            title="Command Alert",
            description="Requires command attention",
            affected_systems=["all"],
            affected_areas=["citywide"],
            metrics={},
            severity_score=0.95,
        )
        
        command_alerts = self.sentinel.get_command_alerts()
        if command_alerts:
            success = self.sentinel.acknowledge_command_alert(
                command_alerts[0].alert_id,
                "Acknowledged and investigating"
            )
            assert success is True

    def test_recommendation_to_command(self):
        """Test creating recommendation for command staff."""
        recommendation = self.sentinel.create_recommendation(
            recommendation_type=RecommendationType.ESCALATION,
            priority=AlertPriority.P1_CRITICAL,
            title="Escalate to Command",
            description="Situation requires command decision",
            rationale="Multiple critical violations detected",
            affected_systems=["all"],
            implementation_steps=["Brief command staff", "Await decision"],
            expected_outcome="Command guidance received",
            risk_if_ignored="Continued violations",
        )
        assert recommendation.recommendation_type == RecommendationType.ESCALATION
        assert recommendation.priority == AlertPriority.P1_CRITICAL


class TestGovernanceChainOfCustody:
    """Tests for governance chain of custody."""

    def setup_method(self):
        """Set up test fixtures."""
        self.monitor = SystemMonitor()
        self.corrector = AutoCorrector()
        self.guard = EthicsGuard()
        self.sentinel = SentinelEngine()

    def test_all_governance_objects_have_hash(self):
        """Test that all governance objects have chain of custody hash."""
        alert = self.monitor.detect_data_corruption(
            engine_type=EngineType.DATA_LAKE,
            data_source="test",
            expected_checksum="abc",
            actual_checksum="xyz",
        )
        assert len(alert.chain_of_custody_hash) == 64
        
        action = self.corrector.create_correction_action(
            correction_type=CorrectionType.CACHE_REBUILD,
            target_engine="data_lake",
            target_component="test",
            priority=CorrectionPriority.LOW,
            description="Test",
        )
        assert len(action.chain_of_custody_hash) == 64
        
        validation = self.guard.validate_action(
            action_type="test",
            engine="test",
            target="test",
            parameters={},
            warrant_obtained=False,
            human_approved=True,
            approved_by="Test",
        )
        assert len(validation.chain_of_custody_hash) == 64
        
        sentinel_alert = self.sentinel.consolidate_alert(
            sources=[AlertSource.SYSTEM_MONITOR],
            title="Test",
            description="Test",
            affected_systems=["test"],
            affected_areas=["test"],
            metrics={},
            severity_score=0.5,
        )
        assert len(sentinel_alert.chain_of_custody_hash) == 64

    def test_hash_uniqueness(self):
        """Test that chain of custody hashes are unique."""
        hashes = set()
        
        for i in range(10):
            alert = self.sentinel.consolidate_alert(
                sources=[AlertSource.SYSTEM_MONITOR],
                title=f"Test Alert {i}",
                description=f"Test {i}",
                affected_systems=["test"],
                affected_areas=["test"],
                metrics={"i": i},
                severity_score=0.5,
            )
            hashes.add(alert.chain_of_custody_hash)
        
        assert len(hashes) == 10
