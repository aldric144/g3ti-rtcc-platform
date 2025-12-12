"""
Test Suite: Global System Monitor

Tests for the system monitoring functionality including:
- Engine metrics tracking
- Alert generation
- Data corruption detection
- Feedback loop detection
- Overload prediction
- Health status management
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
    IssueType,
    EngineMetrics,
    SystemAlert,
    FeedbackLoopDetection,
    OverloadPrediction,
)


class TestSystemMonitor:
    """Test cases for SystemMonitor class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.monitor = SystemMonitor()

    def test_singleton_pattern(self):
        """Test that SystemMonitor follows singleton pattern."""
        monitor1 = SystemMonitor()
        monitor2 = SystemMonitor()
        assert monitor1 is monitor2

    def test_initial_engine_metrics(self):
        """Test that all 16 engines are initialized."""
        assert len(self.monitor.engine_metrics) == 16
        for engine_type in EngineType:
            assert engine_type in self.monitor.engine_metrics

    def test_get_engine_metrics(self):
        """Test getting metrics for a specific engine."""
        metrics = self.monitor.get_engine_metrics(EngineType.PREDICTIVE_AI)
        assert metrics is not None
        assert metrics.engine_type == EngineType.PREDICTIVE_AI
        assert isinstance(metrics.cpu_percent, float)
        assert isinstance(metrics.memory_percent, float)

    def test_get_all_engine_metrics(self):
        """Test getting metrics for all engines."""
        all_metrics = self.monitor.get_all_engine_metrics()
        assert len(all_metrics) == 16

    def test_update_engine_metrics(self):
        """Test updating engine metrics."""
        metrics = self.monitor.update_engine_metrics(
            engine_type=EngineType.CITY_BRAIN,
            cpu_percent=75.5,
            memory_percent=68.2,
            latency_ms=150.0,
        )
        assert metrics.cpu_percent == 75.5
        assert metrics.memory_percent == 68.2
        assert metrics.latency_ms == 150.0

    def test_update_engine_metrics_triggers_warning(self):
        """Test that high metrics trigger warning status."""
        metrics = self.monitor.update_engine_metrics(
            engine_type=EngineType.INTEL_ORCHESTRATION,
            cpu_percent=85.0,
        )
        assert metrics.status in [HealthStatus.WARNING, HealthStatus.CRITICAL]

    def test_update_engine_metrics_triggers_critical(self):
        """Test that very high metrics trigger critical status."""
        metrics = self.monitor.update_engine_metrics(
            engine_type=EngineType.CYBER_INTEL,
            cpu_percent=95.0,
            memory_percent=92.0,
        )
        assert metrics.status == HealthStatus.CRITICAL

    def test_detect_data_corruption(self):
        """Test data corruption detection."""
        alert = self.monitor.detect_data_corruption(
            engine_type=EngineType.DATA_LAKE,
            data_source="crime_records",
            expected_checksum="abc123def456",
            actual_checksum="xyz789ghi012",
        )
        assert alert is not None
        assert alert.issue_type == IssueType.DATA_CORRUPTION
        assert alert.severity == AlertSeverity.CRITICAL

    def test_detect_data_corruption_no_mismatch(self):
        """Test that matching checksums don't trigger alert."""
        alert = self.monitor.detect_data_corruption(
            engine_type=EngineType.DATA_LAKE,
            data_source="crime_records",
            expected_checksum="abc123",
            actual_checksum="abc123",
        )
        assert alert is None

    def test_detect_feedback_loop(self):
        """Test feedback loop detection."""
        detection = self.monitor.detect_feedback_loop(
            source_engine=EngineType.PREDICTIVE_AI,
            target_engine=EngineType.CITY_BRAIN,
            cycle_time_ms=150.0,
            amplification_factor=1.5,
        )
        assert detection is not None
        assert detection.source_engine == EngineType.PREDICTIVE_AI
        assert detection.target_engine == EngineType.CITY_BRAIN
        assert detection.cycle_time_ms == 150.0
        assert detection.amplification_factor == 1.5
        assert detection.loop_type in ["positive", "negative", "oscillating"]

    def test_predict_system_overload(self):
        """Test system overload prediction."""
        self.monitor.update_engine_metrics(
            engine_type=EngineType.PREDICTIVE_AI,
            cpu_percent=85.0,
            memory_percent=80.0,
        )
        prediction = self.monitor.predict_system_overload(
            engine_type=EngineType.PREDICTIVE_AI,
            time_horizon_hours=24,
        )
        assert prediction is not None
        assert prediction.engine_type == EngineType.PREDICTIVE_AI
        assert prediction.confidence >= 0.0 and prediction.confidence <= 1.0
        assert len(prediction.recommended_actions) > 0

    def test_get_system_health_summary(self):
        """Test getting system health summary."""
        summary = self.monitor.get_system_health_summary()
        assert "overall_status" in summary
        assert "total_engines" in summary
        assert summary["total_engines"] == 16
        assert "healthy_count" in summary
        assert "active_alerts" in summary

    def test_get_active_alerts(self):
        """Test getting active alerts."""
        self.monitor.detect_data_corruption(
            engine_type=EngineType.INTEL_ORCHESTRATION,
            data_source="test_data",
            expected_checksum="abc",
            actual_checksum="xyz",
        )
        alerts = self.monitor.get_active_alerts()
        assert len(alerts) > 0

    def test_get_active_alerts_by_severity(self):
        """Test filtering alerts by severity."""
        self.monitor.detect_data_corruption(
            engine_type=EngineType.CITY_BRAIN,
            data_source="test_data",
            expected_checksum="abc",
            actual_checksum="xyz",
        )
        critical_alerts = self.monitor.get_active_alerts(severity=AlertSeverity.CRITICAL)
        assert all(a.severity == AlertSeverity.CRITICAL for a in critical_alerts)

    def test_acknowledge_alert(self):
        """Test acknowledging an alert."""
        alert = self.monitor.detect_data_corruption(
            engine_type=EngineType.EMERGENCY_MANAGEMENT,
            data_source="test_data",
            expected_checksum="abc",
            actual_checksum="xyz",
        )
        success = self.monitor.acknowledge_alert(alert.alert_id)
        assert success is True
        updated_alert = self.monitor.alerts.get(alert.alert_id)
        assert updated_alert.acknowledged is True

    def test_resolve_alert(self):
        """Test resolving an alert."""
        alert = self.monitor.detect_data_corruption(
            engine_type=EngineType.OFFICER_ASSIST,
            data_source="test_data",
            expected_checksum="abc",
            actual_checksum="xyz",
        )
        success = self.monitor.resolve_alert(alert.alert_id)
        assert success is True
        updated_alert = self.monitor.alerts.get(alert.alert_id)
        assert updated_alert.resolved is True

    def test_alert_chain_of_custody(self):
        """Test that alerts have chain of custody hash."""
        alert = self.monitor.detect_data_corruption(
            engine_type=EngineType.GLOBAL_AWARENESS,
            data_source="test_data",
            expected_checksum="abc",
            actual_checksum="xyz",
        )
        assert alert.chain_of_custody_hash is not None
        assert len(alert.chain_of_custody_hash) == 64

    def test_engine_metrics_chain_of_custody(self):
        """Test that engine metrics have chain of custody hash."""
        metrics = self.monitor.get_engine_metrics(EngineType.DRONE_TASK_FORCE)
        assert metrics.chain_of_custody_hash is not None
        assert len(metrics.chain_of_custody_hash) == 64

    def test_get_statistics(self):
        """Test getting monitor statistics."""
        stats = self.monitor.get_statistics()
        assert "total_engines_monitored" in stats
        assert "total_alerts_generated" in stats
        assert "active_alerts" in stats


class TestEngineMetrics:
    """Test cases for EngineMetrics dataclass."""

    def test_engine_metrics_creation(self):
        """Test creating engine metrics."""
        metrics = EngineMetrics(
            engine_type=EngineType.PREDICTIVE_AI,
            cpu_percent=50.0,
            memory_percent=60.0,
            gpu_percent=40.0,
            queue_depth=100,
            active_tasks=10,
            latency_ms=50.0,
            error_rate=0.01,
            throughput_per_sec=500.0,
            uptime_seconds=3600,
            status=HealthStatus.HEALTHY,
            version="1.0.0",
            instance_count=3,
            last_heartbeat=datetime.utcnow(),
        )
        assert metrics.engine_type == EngineType.PREDICTIVE_AI
        assert metrics.cpu_percent == 50.0


class TestSystemAlert:
    """Test cases for SystemAlert dataclass."""

    def test_system_alert_creation(self):
        """Test creating system alert."""
        alert = SystemAlert(
            alert_id="TEST-001",
            engine_type=EngineType.CITY_BRAIN,
            issue_type=IssueType.CPU_OVERLOAD,
            severity=AlertSeverity.HIGH,
            title="Test Alert",
            description="Test description",
            metrics={"cpu": 90.0},
            recommended_action="Scale up",
            auto_correctable=True,
            timestamp=datetime.utcnow(),
        )
        assert alert.alert_id == "TEST-001"
        assert alert.severity == AlertSeverity.HIGH


class TestHealthStatus:
    """Test cases for HealthStatus enum."""

    def test_health_status_values(self):
        """Test health status enum values."""
        assert HealthStatus.HEALTHY.value == "healthy"
        assert HealthStatus.DEGRADED.value == "degraded"
        assert HealthStatus.WARNING.value == "warning"
        assert HealthStatus.CRITICAL.value == "critical"
        assert HealthStatus.OFFLINE.value == "offline"


class TestAlertSeverity:
    """Test cases for AlertSeverity enum."""

    def test_alert_severity_values(self):
        """Test alert severity enum values."""
        assert AlertSeverity.INFO.value == "info"
        assert AlertSeverity.LOW.value == "low"
        assert AlertSeverity.MODERATE.value == "moderate"
        assert AlertSeverity.HIGH.value == "high"
        assert AlertSeverity.CRITICAL.value == "critical"
