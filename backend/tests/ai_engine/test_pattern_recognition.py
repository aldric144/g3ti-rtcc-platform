"""
Unit tests for the Pattern Recognition module.

Tests pattern detection, trajectory prediction, and crime forecasting.
"""

from datetime import datetime, timedelta

from app.ai_engine.pattern_recognition import (
    MarkovState,
    PatternPredictor,
    TrajectoryPoint,
)


class TestTrajectoryPoint:
    """Tests for TrajectoryPoint class."""

    def test_create_trajectory_point(self):
        """Test creating a trajectory point."""
        point = TrajectoryPoint(
            lat=40.7128,
            lng=-74.0060,
            timestamp=datetime.utcnow(),
            entity_id="vehicle_1",
        )

        assert point.lat == 40.7128
        assert point.lng == -74.0060
        assert point.entity_id == "vehicle_1"

    def test_trajectory_point_distance(self):
        """Test distance calculation between trajectory points."""
        point1 = TrajectoryPoint(
            lat=40.7128,
            lng=-74.0060,
            timestamp=datetime.utcnow(),
            entity_id="vehicle_1",
        )
        point2 = TrajectoryPoint(
            lat=40.7500,
            lng=-74.0500,
            timestamp=datetime.utcnow(),
            entity_id="vehicle_1",
        )

        distance = point1.distance_to(point2)
        assert distance > 0


class TestMarkovState:
    """Tests for MarkovState class."""

    def test_create_markov_state(self):
        """Test creating a Markov state."""
        state = MarkovState(
            state_id="location_1",
            transitions={"location_2": 0.6, "location_3": 0.4},
        )

        assert state.state_id == "location_1"
        assert len(state.transitions) == 2

    def test_markov_state_next_state(self):
        """Test getting next state from Markov chain."""
        state = MarkovState(
            state_id="location_1",
            transitions={"location_2": 0.6, "location_3": 0.4},
        )

        next_state = state.get_most_likely_next()
        assert next_state == "location_2"

    def test_markov_state_probability(self):
        """Test getting transition probability."""
        state = MarkovState(
            state_id="location_1",
            transitions={"location_2": 0.6, "location_3": 0.4},
        )

        prob = state.get_probability("location_2")
        assert prob == 0.6

        prob = state.get_probability("unknown")
        assert prob == 0.0


class TestPatternPredictor:
    """Tests for PatternPredictor class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.predictor = PatternPredictor()

    def test_find_repeat_offender_pathways(self):
        """Test finding repeat offender pathways."""
        offender_data = [
            {
                "offender_id": "offender_1",
                "incidents": [
                    {
                        "location": {"lat": 40.7128, "lng": -74.0060},
                        "timestamp": "2024-01-01T10:00:00Z",
                    },
                    {
                        "location": {"lat": 40.7200, "lng": -74.0100},
                        "timestamp": "2024-01-02T10:00:00Z",
                    },
                    {
                        "location": {"lat": 40.7128, "lng": -74.0060},
                        "timestamp": "2024-01-03T10:00:00Z",
                    },
                ],
            },
        ]

        patterns = self.predictor.find_repeat_offender_pathways(offender_data)
        assert isinstance(patterns, list)

    def test_predict_vehicle_trajectory(self):
        """Test vehicle trajectory prediction."""
        trajectory_data = [
            {
                "plate": "ABC123",
                "lat": 40.7128,
                "lng": -74.0060,
                "timestamp": "2024-01-01T10:00:00Z",
            },
            {
                "plate": "ABC123",
                "lat": 40.7200,
                "lng": -74.0100,
                "timestamp": "2024-01-01T10:30:00Z",
            },
            {
                "plate": "ABC123",
                "lat": 40.7300,
                "lng": -74.0200,
                "timestamp": "2024-01-01T11:00:00Z",
            },
        ]

        prediction = self.predictor.predict_vehicle_trajectory(trajectory_data)
        assert prediction is not None
        assert "next_location" in prediction or "probability" in prediction

    def test_forecast_crime_heat(self):
        """Test crime heat forecasting."""
        crime_data = [
            {
                "id": f"crime_{i}",
                "type": "burglary",
                "location": {"lat": 40.7128 + (i * 0.01), "lng": -74.0060},
                "timestamp": (datetime.utcnow() - timedelta(days=i)).isoformat(),
            }
            for i in range(30)
        ]

        forecast = self.predictor.forecast_crime_heat(crime_data, grid_size=0.01)
        assert isinstance(forecast, dict)
        assert "hotspots" in forecast or "predictions" in forecast

    def test_map_gunfire_recurrence(self):
        """Test gunfire recurrence mapping."""
        gunfire_data = [
            {
                "id": f"shot_{i}",
                "location": {"lat": 40.7128, "lng": -74.0060},
                "timestamp": (datetime.utcnow() - timedelta(days=i * 7)).isoformat(),
                "rounds": 3,
            }
            for i in range(10)
        ]

        recurrence = self.predictor.map_gunfire_recurrence(gunfire_data)
        assert isinstance(recurrence, dict)

    def test_find_temporal_patterns(self):
        """Test finding temporal patterns."""
        events = [
            {
                "id": f"event_{i}",
                "type": "incident",
                "hour": i % 24,
                "day_of_week": i % 7,
                "timestamp": datetime.utcnow().isoformat(),
            }
            for i in range(100)
        ]

        patterns = self.predictor.find_temporal_patterns(events)
        assert isinstance(patterns, list)

    def test_find_geographic_patterns(self):
        """Test finding geographic patterns."""
        events = [
            {
                "id": f"event_{i}",
                "location": {"lat": 40.7128 + (i % 5) * 0.01, "lng": -74.0060 + (i % 3) * 0.01},
                "timestamp": datetime.utcnow().isoformat(),
            }
            for i in range(50)
        ]

        patterns = self.predictor.find_geographic_patterns(events)
        assert isinstance(patterns, list)

    def test_calculate_pattern_strength(self):
        """Test pattern strength calculation."""
        pattern = {
            "frequency": 10,
            "consistency": 0.8,
            "recency": 0.9,
        }

        strength = self.predictor.calculate_pattern_strength(pattern)
        assert 0.0 <= strength <= 1.0

    def test_empty_data_handling(self):
        """Test handling of empty data."""
        patterns = self.predictor.find_repeat_offender_pathways([])
        assert patterns == []

        prediction = self.predictor.predict_vehicle_trajectory([])
        assert prediction is not None

    def test_get_all_patterns(self):
        """Test getting all pattern types."""
        data = {
            "offenders": [],
            "vehicles": [],
            "crimes": [],
            "gunfire": [],
            "events": [],
        }

        patterns = self.predictor.get_all_patterns(data, hours=168)
        assert isinstance(patterns, list)
