"""
Unit tests for the Risk Scoring module.

Tests risk score calculation, factor weighting, and entity scoring.
"""

import pytest
from datetime import datetime, timedelta

from app.ai_engine.predictive_models import (
    RiskScoringEngine,
    RiskFactor,
    CrimePredictor,
)


class TestRiskFactor:
    """Tests for RiskFactor class."""

    def test_create_risk_factor(self):
        """Test creating a risk factor."""
        factor = RiskFactor(
            name="criminal_history",
            weight=0.3,
            value=5,
            max_value=10,
        )

        assert factor.name == "criminal_history"
        assert factor.weight == 0.3
        assert factor.value == 5

    def test_risk_factor_contribution(self):
        """Test calculating factor contribution."""
        factor = RiskFactor(
            name="criminal_history",
            weight=0.3,
            value=5,
            max_value=10,
        )

        contribution = factor.calculate_contribution()
        assert 0.0 <= contribution <= 30.0  # weight * (value/max_value) * 100

    def test_risk_factor_normalized_value(self):
        """Test normalized value calculation."""
        factor = RiskFactor(
            name="criminal_history",
            weight=0.3,
            value=5,
            max_value=10,
        )

        normalized = factor.normalized_value
        assert normalized == 0.5


class TestRiskScoringEngine:
    """Tests for RiskScoringEngine class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.engine = RiskScoringEngine()

    def test_calculate_person_risk_score(self):
        """Test calculating risk score for a person."""
        person = {
            "id": "person_1",
            "name": "John Smith",
            "criminal_history": 3,
            "active_warrants": 1,
            "recent_incidents": 2,
            "gang_affiliation": False,
        }

        score = self.engine.calculate_person_risk(person)
        assert score is not None
        assert 0.0 <= score.score <= 100.0
        assert score.level in ["critical", "high", "medium", "low", "minimal"]

    def test_calculate_vehicle_risk_score(self):
        """Test calculating risk score for a vehicle."""
        vehicle = {
            "id": "vehicle_1",
            "plate": "ABC123",
            "stolen": False,
            "hotlist_matches": 0,
            "incident_count": 1,
            "owner_risk": "low",
        }

        score = self.engine.calculate_vehicle_risk(vehicle)
        assert score is not None
        assert 0.0 <= score.score <= 100.0

    def test_calculate_address_risk_score(self):
        """Test calculating risk score for an address."""
        address = {
            "id": "address_1",
            "address": "123 Main St",
            "incident_count": 5,
            "crime_types": ["burglary", "assault"],
            "known_offenders": 2,
        }

        score = self.engine.calculate_address_risk(address)
        assert score is not None
        assert 0.0 <= score.score <= 100.0

    def test_calculate_weapon_risk_score(self):
        """Test calculating risk score for a weapon."""
        weapon = {
            "id": "weapon_1",
            "type": "handgun",
            "ballistic_matches": 2,
            "crime_count": 3,
            "recovered": False,
        }

        score = self.engine.calculate_weapon_risk(weapon)
        assert score is not None
        assert 0.0 <= score.score <= 100.0

    def test_high_risk_person(self):
        """Test high-risk person scoring."""
        person = {
            "id": "person_1",
            "name": "High Risk Person",
            "criminal_history": 10,
            "active_warrants": 3,
            "recent_incidents": 5,
            "gang_affiliation": True,
            "violent_history": True,
        }

        score = self.engine.calculate_person_risk(person)
        assert score.level in ["critical", "high"]
        assert score.score >= 60.0

    def test_low_risk_person(self):
        """Test low-risk person scoring."""
        person = {
            "id": "person_1",
            "name": "Low Risk Person",
            "criminal_history": 0,
            "active_warrants": 0,
            "recent_incidents": 0,
            "gang_affiliation": False,
        }

        score = self.engine.calculate_person_risk(person)
        assert score.level in ["low", "minimal"]
        assert score.score <= 40.0

    def test_batch_risk_calculation(self):
        """Test batch risk score calculation."""
        entities = [
            {"id": "1", "type": "person", "name": "Person 1", "criminal_history": 2},
            {"id": "2", "type": "vehicle", "plate": "ABC123", "stolen": False},
            {"id": "3", "type": "address", "address": "123 Main St", "incident_count": 3},
        ]

        scores = self.engine.calculate_batch_risk(entities)
        assert len(scores) == 3
        assert all(s.score >= 0 for s in scores.values())

    def test_risk_level_classification(self):
        """Test risk level classification."""
        test_cases = [
            (95, "critical"),
            (75, "high"),
            (55, "medium"),
            (35, "low"),
            (15, "minimal"),
        ]

        for score, expected_level in test_cases:
            level = self.engine.classify_risk_level(score)
            assert level == expected_level

    def test_get_risk_factors(self):
        """Test getting risk factors for an entity."""
        person = {
            "id": "person_1",
            "criminal_history": 5,
            "active_warrants": 2,
        }

        factors = self.engine.get_risk_factors(person, "person")
        assert isinstance(factors, list)
        assert len(factors) > 0

    def test_empty_entity_handling(self):
        """Test handling of empty entity data."""
        score = self.engine.calculate_person_risk({})
        assert score is not None
        assert score.score >= 0


class TestCrimePredictor:
    """Tests for CrimePredictor class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.predictor = CrimePredictor()

    def test_predict_crime_hotspots(self):
        """Test crime hotspot prediction."""
        historical_data = [
            {
                "id": f"crime_{i}",
                "type": "burglary",
                "location": {"lat": 40.7128 + (i % 5) * 0.01, "lng": -74.0060},
                "timestamp": (datetime.utcnow() - timedelta(days=i)).isoformat(),
            }
            for i in range(30)
        ]

        hotspots = self.predictor.predict_hotspots(historical_data)
        assert isinstance(hotspots, list)

    def test_predict_crime_type(self):
        """Test crime type prediction for a location."""
        location = {"lat": 40.7128, "lng": -74.0060}
        historical_data = [
            {"type": "burglary", "location": location},
            {"type": "burglary", "location": location},
            {"type": "assault", "location": location},
        ]

        prediction = self.predictor.predict_crime_type(location, historical_data)
        assert prediction is not None
        assert "type" in prediction or "probability" in prediction

    def test_predict_crime_time(self):
        """Test crime time prediction."""
        historical_data = [
            {"hour": 2, "day_of_week": 5},
            {"hour": 3, "day_of_week": 5},
            {"hour": 2, "day_of_week": 6},
        ]

        prediction = self.predictor.predict_crime_time(historical_data)
        assert prediction is not None

    def test_calculate_trend(self):
        """Test crime trend calculation."""
        data = [
            {"count": 10, "period": "week_1"},
            {"count": 15, "period": "week_2"},
            {"count": 20, "period": "week_3"},
        ]

        trend = self.predictor.calculate_trend(data)
        assert trend in ["increasing", "decreasing", "stable"]

    def test_empty_data_handling(self):
        """Test handling of empty data."""
        hotspots = self.predictor.predict_hotspots([])
        assert hotspots == []
