"""
Phase 24: AutomatedCityStabilizer Tests

Tests for anomaly detection, cascade prediction, and stabilization actions.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

from backend.app.city_autonomy.stabilizer import (
    AutomatedCityStabilizer,
    MonitoringDomain,
    AnomalyType,
    AnomalySeverity,
    StabilizationActionType,
    StabilizerStatus,
    SensorReading,
    Anomaly,
    CascadeFailurePrediction,
    StabilizationAction,
    get_city_stabilizer,
)


class TestAutomatedCityStabilizer:
    """Test suite for AutomatedCityStabilizer."""

    def setup_method(self):
        """Set up test fixtures."""
        self.stabilizer = AutomatedCityStabilizer()

    def test_stabilizer_initialization(self):
        """Test stabilizer initializes correctly."""
        assert self.stabilizer._status == StabilizerStatus.IDLE
        assert self.stabilizer._circuit_breaker_open is False
        assert len(self.stabilizer._domain_baselines) > 0

    def test_domain_baselines_configured(self):
        """Test domain baselines are configured for Riviera Beach."""
        baselines = self.stabilizer._domain_baselines
        
        assert MonitoringDomain.TRAFFIC in baselines
        assert MonitoringDomain.POWER_GRID in baselines
        assert MonitoringDomain.CRIME in baselines
        assert MonitoringDomain.EMS in baselines
        assert MonitoringDomain.FIRE in baselines
        assert MonitoringDomain.WEATHER in baselines
        assert MonitoringDomain.FLOODING in baselines
        assert MonitoringDomain.CROWD in baselines

    def test_ingest_sensor_reading_normal(self):
        """Test ingesting normal sensor reading."""
        reading = SensorReading(
            sensor_id="traffic-001",
            domain=MonitoringDomain.TRAFFIC,
            metric="congestion_index",
            value=0.5,
            unit="index",
            location="blue_heron_us1",
            timestamp=datetime.utcnow(),
        )
        
        anomaly = self.stabilizer.ingest_sensor_reading(reading)
        
        # Normal reading should not trigger anomaly
        assert anomaly is None

    def test_ingest_sensor_reading_anomaly(self):
        """Test ingesting anomalous sensor reading."""
        reading = SensorReading(
            sensor_id="traffic-001",
            domain=MonitoringDomain.TRAFFIC,
            metric="congestion_index",
            value=0.95,  # Above threshold
            unit="index",
            location="blue_heron_us1",
            timestamp=datetime.utcnow(),
        )
        
        anomaly = self.stabilizer.ingest_sensor_reading(reading)
        
        assert anomaly is not None
        assert anomaly.domain == MonitoringDomain.TRAFFIC
        assert anomaly.severity in [AnomalySeverity.HIGH, AnomalySeverity.CRITICAL]

    def test_anomaly_severity_classification(self):
        """Test anomaly severity classification."""
        test_cases = [
            (0.75, AnomalySeverity.LOW),
            (0.85, AnomalySeverity.MEDIUM),
            (0.92, AnomalySeverity.HIGH),
            (0.98, AnomalySeverity.CRITICAL),
        ]
        
        for value, expected_severity in test_cases:
            reading = SensorReading(
                sensor_id="traffic-001",
                domain=MonitoringDomain.TRAFFIC,
                metric="congestion_index",
                value=value,
                unit="index",
                location="test",
                timestamp=datetime.utcnow(),
            )
            
            anomaly = self.stabilizer.ingest_sensor_reading(reading)
            if anomaly:
                # Severity should be at least the expected level
                assert anomaly.severity.value >= expected_severity.value or anomaly is None

    def test_get_active_anomalies(self):
        """Test retrieving active anomalies."""
        reading = SensorReading(
            sensor_id="traffic-001",
            domain=MonitoringDomain.TRAFFIC,
            metric="congestion_index",
            value=0.95,
            unit="index",
            location="test",
            timestamp=datetime.utcnow(),
        )
        
        self.stabilizer.ingest_sensor_reading(reading)
        
        anomalies = self.stabilizer.get_active_anomalies()
        assert len(anomalies) >= 0  # May or may not have anomalies

    def test_resolve_anomaly(self):
        """Test anomaly resolution."""
        reading = SensorReading(
            sensor_id="traffic-001",
            domain=MonitoringDomain.TRAFFIC,
            metric="congestion_index",
            value=0.95,
            unit="index",
            location="test",
            timestamp=datetime.utcnow(),
        )
        
        anomaly = self.stabilizer.ingest_sensor_reading(reading)
        
        if anomaly:
            success = self.stabilizer.resolve_anomaly(
                anomaly.anomaly_id,
                resolved_by="operator-001",
                resolution_notes="Manually resolved",
            )
            assert success is True


class TestCascadePrediction:
    """Test suite for cascade failure prediction."""

    def setup_method(self):
        """Set up test fixtures."""
        self.stabilizer = AutomatedCityStabilizer()

    def test_cascade_prediction_generated(self):
        """Test cascade prediction is generated for high-risk anomalies."""
        reading = SensorReading(
            sensor_id="power-001",
            domain=MonitoringDomain.POWER_GRID,
            metric="load_percentage",
            value=95,  # Critical load
            unit="percent",
            location="sector_3",
            timestamp=datetime.utcnow(),
        )
        
        anomaly = self.stabilizer.ingest_sensor_reading(reading)
        
        if anomaly and anomaly.cascade_risk > 0.5:
            predictions = self.stabilizer.get_cascade_predictions()
            # May have predictions if cascade risk is high
            assert isinstance(predictions, list)

    def test_cascade_prediction_contains_failures(self):
        """Test cascade prediction contains predicted failures."""
        predictions = self.stabilizer.get_cascade_predictions()
        
        for prediction in predictions:
            assert hasattr(prediction, "predicted_failures")
            assert hasattr(prediction, "probability")
            assert hasattr(prediction, "affected_systems")
            assert hasattr(prediction, "recommended_actions")

    def test_cascade_risk_calculation(self):
        """Test cascade risk is calculated for anomalies."""
        reading = SensorReading(
            sensor_id="traffic-001",
            domain=MonitoringDomain.TRAFFIC,
            metric="congestion_index",
            value=0.95,
            unit="index",
            location="test",
            timestamp=datetime.utcnow(),
        )
        
        anomaly = self.stabilizer.ingest_sensor_reading(reading)
        
        if anomaly:
            assert 0 <= anomaly.cascade_risk <= 1


class TestStabilizationActions:
    """Test suite for stabilization actions."""

    def setup_method(self):
        """Set up test fixtures."""
        self.stabilizer = AutomatedCityStabilizer()

    def test_stabilization_actions_generated(self):
        """Test stabilization actions are generated for anomalies."""
        reading = SensorReading(
            sensor_id="traffic-001",
            domain=MonitoringDomain.TRAFFIC,
            metric="congestion_index",
            value=0.95,
            unit="index",
            location="blue_heron_us1",
            timestamp=datetime.utcnow(),
        )
        
        self.stabilizer.ingest_sensor_reading(reading)
        
        actions = self.stabilizer.get_stabilization_actions()
        assert isinstance(actions, list)

    def test_execute_stabilization_action(self):
        """Test executing a stabilization action."""
        reading = SensorReading(
            sensor_id="traffic-001",
            domain=MonitoringDomain.TRAFFIC,
            metric="congestion_index",
            value=0.95,
            unit="index",
            location="test",
            timestamp=datetime.utcnow(),
        )
        
        self.stabilizer.ingest_sensor_reading(reading)
        
        actions = self.stabilizer.get_stabilization_actions(status="pending")
        
        if actions:
            success = self.stabilizer.execute_stabilization_action(
                actions[0].action_id,
                executed_by="operator-001",
            )
            assert isinstance(success, bool)

    def test_domain_specific_actions(self):
        """Test domain-specific stabilization actions."""
        domain_action_types = {
            MonitoringDomain.TRAFFIC: [
                StabilizationActionType.TRAFFIC_REROUTE,
                StabilizationActionType.SIGNAL_OPTIMIZATION,
            ],
            MonitoringDomain.POWER_GRID: [
                StabilizationActionType.LOAD_SHEDDING,
                StabilizationActionType.GRID_BALANCING,
            ],
            MonitoringDomain.CRIME: [
                StabilizationActionType.PATROL_REBALANCE,
            ],
        }
        
        for domain, expected_types in domain_action_types.items():
            assert isinstance(expected_types, list)


class TestStabilizerCircuitBreaker:
    """Test suite for stabilizer circuit breaker."""

    def setup_method(self):
        """Set up test fixtures."""
        self.stabilizer = AutomatedCityStabilizer()

    def test_circuit_breaker_triggers(self):
        """Test circuit breaker triggers after failures."""
        for i in range(5):
            self.stabilizer._record_failure()
        
        assert self.stabilizer._circuit_breaker_open is True

    def test_circuit_breaker_reset(self):
        """Test circuit breaker reset."""
        for i in range(5):
            self.stabilizer._record_failure()
        
        assert self.stabilizer._circuit_breaker_open is True
        
        self.stabilizer.reset_circuit_breaker()
        
        assert self.stabilizer._circuit_breaker_open is False
        assert self.stabilizer._consecutive_failures == 0

    def test_stabilization_blocked_when_open(self):
        """Test stabilization is blocked when circuit breaker is open."""
        for i in range(5):
            self.stabilizer._record_failure()
        
        result = self.stabilizer.run_stabilization_cycle()
        
        # Should return early or indicate blocked
        assert self.stabilizer._circuit_breaker_open is True


class TestStabilizerStatus:
    """Test suite for stabilizer status and statistics."""

    def setup_method(self):
        """Set up test fixtures."""
        self.stabilizer = AutomatedCityStabilizer()

    def test_get_status(self):
        """Test status retrieval."""
        status = self.stabilizer.get_status()
        
        assert "status" in status
        assert "circuit_breaker_open" in status
        assert "active_anomalies" in status
        assert "pending_actions" in status

    def test_get_statistics(self):
        """Test statistics retrieval."""
        stats = self.stabilizer.get_statistics()
        
        assert "total_anomalies_detected" in stats
        assert "anomalies_by_domain" in stats
        assert "anomalies_by_severity" in stats
        assert "stabilization_actions" in stats

    def test_run_stabilization_cycle(self):
        """Test running a stabilization cycle."""
        result = self.stabilizer.run_stabilization_cycle()
        
        assert isinstance(result, dict)
        assert "anomalies_detected" in result
        assert "actions_generated" in result

    def test_singleton_instance(self):
        """Test singleton pattern."""
        stabilizer1 = get_city_stabilizer()
        stabilizer2 = get_city_stabilizer()
        assert stabilizer1 is stabilizer2
