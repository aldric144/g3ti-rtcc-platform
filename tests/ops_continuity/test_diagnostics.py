"""
Tests for Diagnostics Engine.

Tests error classification, predictive failure detection,
slow query detection, and diagnostic reporting.
"""

import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

from app.ops_continuity.diagnostics import (
    DiagnosticsEngine,
    DiagnosticsConfig,
    DiagnosticCategory,
    DiagnosticSeverity,
    DiagnosticEvent,
    SlowQueryEvent,
    PredictiveAlert,
)


class TestDiagnosticsEngine:
    """Tests for DiagnosticsEngine class."""

    def test_init_default_config(self):
        """Test initialization with default configuration."""
        engine = DiagnosticsEngine()
        assert engine.config is not None
        assert engine.config.slow_query_threshold_ms == 1000

    def test_init_custom_config(self):
        """Test initialization with custom configuration."""
        config = DiagnosticsConfig(
            slow_query_threshold_ms=500,
            prediction_window_minutes=30,
            max_events_stored=5000,
        )
        engine = DiagnosticsEngine(config=config)
        assert engine.config.slow_query_threshold_ms == 500
        assert engine.config.prediction_window_minutes == 30

    def test_log_event(self):
        """Test logging a diagnostic event."""
        engine = DiagnosticsEngine()
        event = engine.log_event(
            category=DiagnosticCategory.NETWORK,
            severity=DiagnosticSeverity.WARNING,
            message="Connection timeout",
            source="redis-client",
        )
        
        assert event is not None
        assert event.category == DiagnosticCategory.NETWORK
        assert event.severity == DiagnosticSeverity.WARNING

    def test_log_network_error(self):
        """Test logging a network error."""
        engine = DiagnosticsEngine()
        event = engine.log_network_error(
            message="Connection refused",
            source="neo4j-driver",
            endpoint="bolt://localhost:7687",
        )
        
        assert event is not None
        assert event.category == DiagnosticCategory.NETWORK

    def test_log_database_error(self):
        """Test logging a database error."""
        engine = DiagnosticsEngine()
        event = engine.log_database_error(
            message="Query timeout",
            source="neo4j",
            query="MATCH (n) RETURN n",
        )
        
        assert event is not None
        assert event.category == DiagnosticCategory.DATABASE

    def test_log_federal_error(self):
        """Test logging a federal endpoint error."""
        engine = DiagnosticsEngine()
        event = engine.log_federal_error(
            message="N-DEx unavailable",
            source="federal-integration",
            endpoint="ndex.fbi.gov",
        )
        
        assert event is not None
        assert event.category == DiagnosticCategory.FEDERAL

    def test_log_vendor_error(self):
        """Test logging a vendor integration error."""
        engine = DiagnosticsEngine()
        event = engine.log_vendor_error(
            message="LPR feed interrupted",
            source="lpr-integration",
            vendor="Vigilant",
        )
        
        assert event is not None
        assert event.category == DiagnosticCategory.VENDOR

    def test_log_slow_query(self):
        """Test logging a slow query."""
        engine = DiagnosticsEngine()
        event = engine.log_slow_query(
            query="MATCH (p:Person)-[:ASSOCIATED_WITH]->(v:Vehicle) RETURN p, v",
            duration_ms=2500.0,
            database="neo4j",
        )
        
        assert event is not None
        assert event.duration_ms == 2500.0

    def test_get_recent_events(self):
        """Test getting recent diagnostic events."""
        engine = DiagnosticsEngine()
        engine.log_event(
            category=DiagnosticCategory.NETWORK,
            severity=DiagnosticSeverity.INFO,
            message="Test event",
            source="test",
        )
        
        events = engine.get_recent_events(limit=10)
        assert isinstance(events, list)

    def test_get_events_by_category(self):
        """Test getting events by category."""
        engine = DiagnosticsEngine()
        engine.log_network_error("Test", "test", "localhost")
        
        events = engine.get_events_by_category(DiagnosticCategory.NETWORK)
        assert isinstance(events, list)

    def test_get_events_by_severity(self):
        """Test getting events by severity."""
        engine = DiagnosticsEngine()
        engine.log_event(
            category=DiagnosticCategory.DATABASE,
            severity=DiagnosticSeverity.ERROR,
            message="Test error",
            source="test",
        )
        
        events = engine.get_events_by_severity(DiagnosticSeverity.ERROR)
        assert isinstance(events, list)

    def test_get_slow_queries(self):
        """Test getting slow queries."""
        engine = DiagnosticsEngine()
        engine.log_slow_query("SELECT * FROM users", 1500.0, "postgres")
        
        queries = engine.get_slow_queries(limit=10)
        assert isinstance(queries, list)

    def test_get_predictive_alerts(self):
        """Test getting predictive alerts."""
        engine = DiagnosticsEngine()
        alerts = engine.get_predictive_alerts()
        
        assert isinstance(alerts, list)

    def test_generate_report(self):
        """Test generating diagnostic report."""
        engine = DiagnosticsEngine()
        report = engine.generate_report(hours=24)
        
        assert isinstance(report, dict)
        assert "period_hours" in report
        assert "total_events" in report
        assert "events_by_category" in report
        assert "events_by_severity" in report

    def test_get_metrics(self):
        """Test getting diagnostics metrics."""
        engine = DiagnosticsEngine()
        metrics = engine.get_metrics()
        
        assert metrics is not None
        assert hasattr(metrics, "total_events")
        assert hasattr(metrics, "slow_queries_count")

    def test_get_status(self):
        """Test getting diagnostics status."""
        engine = DiagnosticsEngine()
        status = engine.get_status()
        
        assert isinstance(status, dict)
        assert "running" in status
        assert "events_stored" in status

    def test_register_callback(self):
        """Test callback registration."""
        engine = DiagnosticsEngine()
        callback = MagicMock()
        
        engine.register_callback(callback)
        assert callback in engine._callbacks


class TestDiagnosticEvent:
    """Tests for DiagnosticEvent model."""

    def test_event_creation(self):
        """Test DiagnosticEvent creation."""
        event = DiagnosticEvent(
            event_id="diag-001",
            timestamp=datetime.now(timezone.utc),
            category=DiagnosticCategory.NETWORK,
            severity=DiagnosticSeverity.WARNING,
            message="Connection timeout",
            source="redis-client",
        )
        
        assert event.event_id == "diag-001"
        assert event.category == DiagnosticCategory.NETWORK
        assert event.severity == DiagnosticSeverity.WARNING

    def test_event_with_metadata(self):
        """Test event with additional metadata."""
        event = DiagnosticEvent(
            event_id="diag-002",
            timestamp=datetime.now(timezone.utc),
            category=DiagnosticCategory.DATABASE,
            severity=DiagnosticSeverity.ERROR,
            message="Query failed",
            source="neo4j",
            metadata={"query": "MATCH (n) RETURN n", "error_code": "Neo.ClientError"},
        )
        
        assert event.metadata is not None
        assert "query" in event.metadata


class TestSlowQueryEvent:
    """Tests for SlowQueryEvent model."""

    def test_slow_query_creation(self):
        """Test SlowQueryEvent creation."""
        event = SlowQueryEvent(
            event_id="sq-001",
            timestamp=datetime.now(timezone.utc),
            query="SELECT * FROM large_table",
            duration_ms=5000.0,
            database="postgres",
            threshold_ms=1000.0,
        )
        
        assert event.event_id == "sq-001"
        assert event.duration_ms == 5000.0
        assert event.database == "postgres"

    def test_slow_query_with_plan(self):
        """Test slow query with execution plan."""
        event = SlowQueryEvent(
            event_id="sq-002",
            timestamp=datetime.now(timezone.utc),
            query="MATCH (p:Person) RETURN p",
            duration_ms=3000.0,
            database="neo4j",
            threshold_ms=1000.0,
            execution_plan="NodeByLabelScan",
            recommendation="Add index on Person label",
        )
        
        assert event.execution_plan == "NodeByLabelScan"
        assert event.recommendation is not None


class TestPredictiveAlert:
    """Tests for PredictiveAlert model."""

    def test_alert_creation(self):
        """Test PredictiveAlert creation."""
        alert = PredictiveAlert(
            alert_id="pred-001",
            timestamp=datetime.now(timezone.utc),
            prediction_type="service_failure",
            affected_service="redis",
            confidence_score=0.85,
            predicted_time_minutes=15,
            recommended_action="Scale Redis cluster",
        )
        
        assert alert.alert_id == "pred-001"
        assert alert.confidence_score == 0.85
        assert alert.predicted_time_minutes == 15

    def test_high_confidence_alert(self):
        """Test high confidence predictive alert."""
        alert = PredictiveAlert(
            alert_id="pred-002",
            timestamp=datetime.now(timezone.utc),
            prediction_type="capacity_exhaustion",
            affected_service="neo4j",
            confidence_score=0.95,
            predicted_time_minutes=5,
            recommended_action="Immediate failover recommended",
            severity=DiagnosticSeverity.CRITICAL,
        )
        
        assert alert.confidence_score == 0.95
        assert alert.severity == DiagnosticSeverity.CRITICAL


class TestDiagnosticCategory:
    """Tests for DiagnosticCategory enum."""

    def test_categories(self):
        """Test all diagnostic categories exist."""
        assert DiagnosticCategory.NETWORK is not None
        assert DiagnosticCategory.DATABASE is not None
        assert DiagnosticCategory.FEDERAL is not None
        assert DiagnosticCategory.VENDOR is not None
        assert DiagnosticCategory.INTERNAL is not None
        assert DiagnosticCategory.PERFORMANCE is not None


class TestDiagnosticSeverity:
    """Tests for DiagnosticSeverity enum."""

    def test_severities(self):
        """Test all diagnostic severities exist."""
        assert DiagnosticSeverity.DEBUG is not None
        assert DiagnosticSeverity.INFO is not None
        assert DiagnosticSeverity.WARNING is not None
        assert DiagnosticSeverity.ERROR is not None
        assert DiagnosticSeverity.CRITICAL is not None


class TestDiagnosticsConfig:
    """Tests for DiagnosticsConfig model."""

    def test_default_config(self):
        """Test default configuration values."""
        config = DiagnosticsConfig()
        
        assert config.slow_query_threshold_ms == 1000
        assert config.prediction_window_minutes == 15
        assert config.max_events_stored == 10000

    def test_custom_config(self):
        """Test custom configuration values."""
        config = DiagnosticsConfig(
            slow_query_threshold_ms=500,
            prediction_window_minutes=30,
            max_events_stored=5000,
            enable_predictions=False,
        )
        
        assert config.slow_query_threshold_ms == 500
        assert config.enable_predictions is False
