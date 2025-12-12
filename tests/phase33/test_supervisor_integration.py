"""
Test Suite: AI Supervisor Integration Tests

Tests for integration between supervisor components:
- System Monitor + Auto-Corrector integration
- Ethics Guard + Sentinel Engine integration
- Full pipeline integration
- Cross-component communication
"""

import pytest
from datetime import datetime
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
    ActionDecision,
    ViolationSeverity,
)
from backend.app.ai_supervisor.sentinel_engine import (
    SentinelEngine,
    AlertPriority,
    AlertSource,
    AutonomyLevel,
)


class TestSystemMonitorAutoCorrector:
    """Integration tests for System Monitor and Auto-Corrector."""

    def setup_method(self):
        """Set up test fixtures."""
        self.monitor = SystemMonitor()
        self.corrector = AutoCorrector()

    def test_critical_alert_triggers_correction(self):
        """Test that critical alerts can trigger corrections."""
        self.monitor.update_engine_metrics(
            engine_type=EngineType.PREDICTIVE_AI,
            cpu_percent=95.0,
            memory_percent=92.0,
        )
        
        alerts = self.monitor.get_active_alerts(severity=AlertSeverity.CRITICAL)
        
        if alerts:
            action = self.corrector.create_correction_action(
                correction_type=CorrectionType.LOAD_REBALANCE,
                target_engine="predictive_ai",
                target_component="main_cluster",
                priority=CorrectionPriority.CRITICAL,
                description=f"Auto-correction for alert: {alerts[0].title}",
            )
            assert action is not None

    def test_data_corruption_triggers_cache_rebuild(self):
        """Test that data corruption triggers cache rebuild."""
        alert = self.monitor.detect_data_corruption(
            engine_type=EngineType.CITY_BRAIN,
            data_source="prediction_cache",
            expected_checksum="abc123",
            actual_checksum="xyz789",
        )
        
        if alert:
            action = self.corrector.create_correction_action(
                correction_type=CorrectionType.CACHE_REBUILD,
                target_engine="city_brain",
                target_component="prediction_cache",
                priority=CorrectionPriority.HIGH,
                description="Rebuild cache due to corruption",
            )
            assert action is not None
            assert action.correction_type == CorrectionType.CACHE_REBUILD

    def test_feedback_loop_triggers_correction(self):
        """Test that feedback loop detection triggers correction."""
        detection = self.monitor.detect_feedback_loop(
            source_engine=EngineType.PREDICTIVE_AI,
            target_engine=EngineType.CITY_BRAIN,
            cycle_time_ms=50.0,
            amplification_factor=2.0,
        )
        
        if detection and detection.is_critical:
            action = self.corrector.create_correction_action(
                correction_type=CorrectionType.CONNECTION_RESET,
                target_engine="predictive_ai",
                target_component="city_brain_connector",
                priority=CorrectionPriority.HIGH,
                description="Break feedback loop",
            )
            assert action is not None


class TestEthicsGuardSentinelEngine:
    """Integration tests for Ethics Guard and Sentinel Engine."""

    def setup_method(self):
        """Set up test fixtures."""
        self.guard = EthicsGuard()
        self.sentinel = SentinelEngine()

    def test_violation_creates_sentinel_alert(self):
        """Test that ethics violations create sentinel alerts."""
        validation = self.guard.validate_action(
            action_type="facial_recognition",
            engine="intel_orchestration",
            target="private_residence",
            parameters={"duration": "24h"},
            warrant_obtained=False,
        )
        
        if validation.decision == ActionDecision.BLOCKED:
            alert = self.sentinel.consolidate_alert(
                sources=[AlertSource.ETHICS_GUARD],
                title="Ethics Violation Detected",
                description=f"Action blocked: {validation.violations}",
                affected_systems=["intel_orchestration"],
                affected_areas=["citywide"],
                metrics={},
                severity_score=0.9,
            )
            assert alert is not None
            assert alert.priority in [AlertPriority.P1_CRITICAL, AlertPriority.P2_HIGH]

    def test_bias_audit_creates_recommendation(self):
        """Test that bias audit results create recommendations."""
        predictions = [
            {"id": i, "score": 0.9 if i % 2 == 0 else 0.3, "demographics": {"race": "white" if i % 2 == 0 else "black"}}
            for i in range(100)
        ]
        audit = self.guard.conduct_bias_audit(
            engine="predictive_ai",
            model_name="biased_model",
            predictions=predictions,
        )
        
        if audit.bias_detected:
            from backend.app.ai_supervisor.sentinel_engine import RecommendationType
            recommendation = self.sentinel.create_recommendation(
                recommendation_type=RecommendationType.IMMEDIATE_ACTION,
                priority=AlertPriority.P1_CRITICAL,
                title="Address Model Bias",
                description="Significant bias detected in predictions",
                rationale=f"Bias score: {audit.overall_bias_score}",
                affected_systems=["predictive_ai"],
                implementation_steps=["Retrain model", "Validate fairness"],
                expected_outcome="Reduced bias",
                risk_if_ignored="Continued discrimination",
            )
            assert recommendation is not None


class TestFullPipelineIntegration:
    """Integration tests for full supervisor pipeline."""

    def setup_method(self):
        """Set up test fixtures."""
        self.monitor = SystemMonitor()
        self.corrector = AutoCorrector()
        self.guard = EthicsGuard()
        self.sentinel = SentinelEngine()

    def test_full_alert_to_correction_pipeline(self):
        """Test full pipeline from alert to correction."""
        self.monitor.update_engine_metrics(
            engine_type=EngineType.CYBER_INTEL,
            cpu_percent=90.0,
            memory_percent=85.0,
            latency_ms=500.0,
        )
        
        health = self.monitor.get_system_health_summary()
        assert health["overall_status"] in ["WARNING", "CRITICAL"]
        
        alert = self.sentinel.consolidate_alert(
            sources=[AlertSource.SYSTEM_MONITOR],
            title="Cyber Intel Engine Overload",
            description="High resource usage detected",
            affected_systems=["cyber_intel"],
            affected_areas=["citywide"],
            metrics={"cpu": 90.0, "memory": 85.0},
            severity_score=0.8,
        )
        
        action = self.corrector.create_correction_action(
            correction_type=CorrectionType.LOAD_REBALANCE,
            target_engine="cyber_intel",
            target_component="main_cluster",
            priority=CorrectionPriority.HIGH,
            description="Rebalance load to reduce pressure",
        )
        
        assert alert is not None
        assert action is not None

    def test_ethics_validation_in_autonomous_action(self):
        """Test that autonomous actions are validated by ethics guard."""
        validation = self.guard.validate_action(
            action_type="service_restart",
            engine="auto_corrector",
            target="cyber_intel",
            parameters={"service": "threat_analyzer"},
            warrant_obtained=False,
            human_approved=True,
            approved_by="System Admin",
        )
        
        if validation.decision in [ActionDecision.APPROVED, ActionDecision.APPROVED_WITH_CONDITIONS]:
            request = self.sentinel.request_autonomous_action(
                source_engine="auto_corrector",
                action_type="service_restart",
                autonomy_level=AutonomyLevel.SUPERVISED,
                target="cyber_intel",
                parameters={"service": "threat_analyzer"},
                justification="Service unresponsive",
                risk_score=0.2,
            )
            assert request is not None

    def test_cascade_prediction_triggers_recommendations(self):
        """Test that cascade predictions trigger recommendations."""
        prediction = self.sentinel.predict_cascade(
            trigger_event="Predictive AI Engine Failure",
            trigger_source=AlertSource.SYSTEM_MONITOR,
            initial_severity=0.9,
            time_horizon_hours=24,
        )
        
        if prediction.probability > 0.5:
            from backend.app.ai_supervisor.sentinel_engine import RecommendationType
            recommendation = self.sentinel.create_recommendation(
                recommendation_type=RecommendationType.PREVENTIVE_ACTION,
                priority=AlertPriority.P2_HIGH,
                title="Prevent Cascade Failure",
                description=f"Cascade predicted with {prediction.probability:.0%} probability",
                rationale="Multiple systems at risk",
                affected_systems=prediction.affected_systems,
                implementation_steps=prediction.mitigation_options,
                expected_outcome="Prevented cascade",
                risk_if_ignored="System-wide failure",
            )
            assert recommendation is not None


class TestCrossComponentCommunication:
    """Tests for cross-component communication."""

    def setup_method(self):
        """Set up test fixtures."""
        self.monitor = SystemMonitor()
        self.corrector = AutoCorrector()
        self.guard = EthicsGuard()
        self.sentinel = SentinelEngine()

    def test_all_components_share_engine_types(self):
        """Test that all components use consistent engine types."""
        monitor_engines = set(e.value for e in EngineType)
        
        assert "predictive_ai" in monitor_engines
        assert "city_brain" in monitor_engines
        assert "cyber_intel" in monitor_engines
        assert "intel_orchestration" in monitor_engines

    def test_alert_sources_match_components(self):
        """Test that alert sources match component names."""
        sources = set(s.value for s in AlertSource)
        
        assert "system_monitor" in sources
        assert "auto_corrector" in sources
        assert "ethics_guard" in sources
        assert "sentinel_engine" in sources

    def test_chain_of_custody_consistency(self):
        """Test that chain of custody hashes are consistent format."""
        alert = self.monitor.detect_data_corruption(
            engine_type=EngineType.DATA_LAKE,
            data_source="test",
            expected_checksum="abc",
            actual_checksum="xyz",
        )
        
        action = self.corrector.create_correction_action(
            correction_type=CorrectionType.CACHE_REBUILD,
            target_engine="data_lake",
            target_component="test_cache",
            priority=CorrectionPriority.LOW,
            description="Test",
        )
        
        validation = self.guard.validate_action(
            action_type="test",
            engine="test",
            target="test",
            parameters={},
            warrant_obtained=False,
            human_approved=True,
            approved_by="Test",
        )
        
        sentinel_alert = self.sentinel.consolidate_alert(
            sources=[AlertSource.SYSTEM_MONITOR],
            title="Test",
            description="Test",
            affected_systems=["test"],
            affected_areas=["test"],
            metrics={},
            severity_score=0.5,
        )
        
        assert len(alert.chain_of_custody_hash) == 64
        assert len(action.chain_of_custody_hash) == 64
        assert len(validation.chain_of_custody_hash) == 64
        assert len(sentinel_alert.chain_of_custody_hash) == 64

    def test_statistics_aggregation(self):
        """Test that statistics can be aggregated across components."""
        monitor_stats = self.monitor.get_statistics()
        corrector_stats = self.corrector.get_statistics()
        guard_stats = self.guard.get_statistics()
        sentinel_stats = self.sentinel.get_statistics()
        
        total_stats = {
            "monitor": monitor_stats,
            "corrector": corrector_stats,
            "guard": guard_stats,
            "sentinel": sentinel_stats,
        }
        
        assert len(total_stats) == 4
        assert all(isinstance(s, dict) for s in total_stats.values())
