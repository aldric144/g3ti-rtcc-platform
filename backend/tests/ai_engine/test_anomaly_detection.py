"""
Unit tests for the Anomaly Detection module.

Tests anomaly detection algorithms including Z-score analysis,
DBSCAN clustering, and various anomaly types.
"""

from datetime import datetime, timedelta

from app.ai_engine.anomaly_detection import (
    AnomalyDetector,
    BaselineMetrics,
    SpatialCluster,
)


class TestBaselineMetrics:
    """Tests for BaselineMetrics class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.metrics = BaselineMetrics()

    def test_add_value(self):
        """Test adding values to baseline."""
        self.metrics.add_value(10.0)
        self.metrics.add_value(20.0)
        self.metrics.add_value(30.0)

        assert self.metrics.count == 3
        assert self.metrics.mean == 20.0

    def test_calculate_zscore_normal(self):
        """Test Z-score calculation for normal values."""
        for i in range(100):
            self.metrics.add_value(50.0 + (i % 10))

        zscore = self.metrics.calculate_zscore(55.0)
        assert -2.0 <= zscore <= 2.0

    def test_calculate_zscore_anomaly(self):
        """Test Z-score calculation for anomalous values."""
        for _ in range(100):
            self.metrics.add_value(50.0)

        zscore = self.metrics.calculate_zscore(100.0)
        assert abs(zscore) > 2.0

    def test_calculate_zscore_empty(self):
        """Test Z-score calculation with no baseline."""
        zscore = self.metrics.calculate_zscore(50.0)
        assert zscore == 0.0

    def test_is_anomaly_threshold(self):
        """Test anomaly detection with threshold."""
        for _ in range(100):
            self.metrics.add_value(50.0)

        assert not self.metrics.is_anomaly(52.0, threshold=2.0)
        assert self.metrics.is_anomaly(100.0, threshold=2.0)


class TestSpatialCluster:
    """Tests for SpatialCluster class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.cluster = SpatialCluster(
            center_lat=40.7128,
            center_lng=-74.0060,
            radius_km=1.0,
        )

    def test_add_point(self):
        """Test adding points to cluster."""
        self.cluster.add_point(40.7128, -74.0060, {"id": "1"})
        self.cluster.add_point(40.7130, -74.0062, {"id": "2"})

        assert len(self.cluster.points) == 2

    def test_contains_point_inside(self):
        """Test point containment for points inside cluster."""
        assert self.cluster.contains_point(40.7128, -74.0060)
        assert self.cluster.contains_point(40.7130, -74.0062)

    def test_contains_point_outside(self):
        """Test point containment for points outside cluster."""
        assert not self.cluster.contains_point(41.0000, -75.0000)

    def test_density(self):
        """Test cluster density calculation."""
        self.cluster.add_point(40.7128, -74.0060, {"id": "1"})
        self.cluster.add_point(40.7130, -74.0062, {"id": "2"})
        self.cluster.add_point(40.7129, -74.0061, {"id": "3"})

        density = self.cluster.density
        assert density > 0


class TestAnomalyDetector:
    """Tests for AnomalyDetector class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.detector = AnomalyDetector()

    def test_detect_vehicle_behavior_anomaly(self):
        """Test vehicle behavior anomaly detection."""
        vehicle_data = [
            {
                "plate": "ABC123",
                "location": {"lat": 40.7128, "lng": -74.0060},
                "timestamp": datetime.utcnow().isoformat(),
                "speed": 35,
            },
            {
                "plate": "ABC123",
                "location": {"lat": 40.7500, "lng": -74.0500},
                "timestamp": (datetime.utcnow() - timedelta(minutes=5)).isoformat(),
                "speed": 120,  # Anomalous speed
            },
        ]

        anomalies = self.detector.detect_vehicle_behavior(vehicle_data)
        assert isinstance(anomalies, list)

    def test_detect_gunfire_density_anomaly(self):
        """Test gunfire density anomaly detection."""
        gunfire_data = [
            {
                "id": f"shot_{i}",
                "location": {"lat": 40.7128 + (i * 0.001), "lng": -74.0060},
                "timestamp": datetime.utcnow().isoformat(),
                "rounds": 3,
            }
            for i in range(10)
        ]

        anomalies = self.detector.detect_gunfire_density(gunfire_data)
        assert isinstance(anomalies, list)

    def test_detect_offender_clustering(self):
        """Test offender clustering anomaly detection."""
        offender_data = [
            {
                "id": f"offender_{i}",
                "name": f"Person {i}",
                "location": {"lat": 40.7128, "lng": -74.0060},
                "last_seen": datetime.utcnow().isoformat(),
            }
            for i in range(5)
        ]

        anomalies = self.detector.detect_offender_clustering(offender_data)
        assert isinstance(anomalies, list)

    def test_detect_timeline_deviation(self):
        """Test timeline deviation anomaly detection."""
        events = [
            {
                "id": f"event_{i}",
                "type": "incident",
                "timestamp": (datetime.utcnow() - timedelta(hours=i)).isoformat(),
            }
            for i in range(24)
        ]

        anomalies = self.detector.detect_timeline_deviation(events)
        assert isinstance(anomalies, list)

    def test_detect_crime_signature_shift(self):
        """Test crime signature shift detection."""
        crime_data = [
            {
                "id": f"crime_{i}",
                "type": "burglary" if i % 2 == 0 else "assault",
                "hour": i % 24,
                "day_of_week": i % 7,
            }
            for i in range(100)
        ]

        anomalies = self.detector.detect_crime_signature_shift(crime_data)
        assert isinstance(anomalies, list)

    def test_detect_repeat_caller_anomaly(self):
        """Test repeat caller anomaly detection."""
        caller_data = [
            {
                "caller_id": "caller_1",
                "call_count": 50,  # High call count
                "last_call": datetime.utcnow().isoformat(),
            },
            {
                "caller_id": "caller_2",
                "call_count": 2,
                "last_call": datetime.utcnow().isoformat(),
            },
        ]

        anomalies = self.detector.detect_repeat_caller_anomaly(caller_data)
        assert isinstance(anomalies, list)

    def test_detect_all_anomalies(self):
        """Test detecting all anomaly types."""
        data = {
            "vehicles": [],
            "gunfire": [],
            "offenders": [],
            "events": [],
            "crimes": [],
            "callers": [],
        }

        anomalies = self.detector.detect_all(data, hours=24)
        assert isinstance(anomalies, list)

    def test_anomaly_severity_classification(self):
        """Test anomaly severity classification."""
        anomaly = {
            "type": "vehicle_behavior",
            "confidence": 0.95,
            "deviation": 5.0,
        }

        severity = self.detector.classify_severity(anomaly)
        assert severity in ["critical", "high", "medium", "low"]

    def test_empty_data_handling(self):
        """Test handling of empty data."""
        anomalies = self.detector.detect_vehicle_behavior([])
        assert anomalies == []

        anomalies = self.detector.detect_gunfire_density([])
        assert anomalies == []
