"""
Tests for City Prediction Engine module.
"""

import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch


class TestCityPredictionEngine:
    """Tests for CityPredictionEngine class."""

    def test_prediction_engine_initialization(self):
        """Test CityPredictionEngine initializes correctly."""
        from backend.app.city_brain.prediction import CityPredictionEngine
        
        engine = CityPredictionEngine()
        assert engine is not None

    def test_get_comprehensive_forecast(self):
        """Test getting comprehensive forecast."""
        from backend.app.city_brain.prediction import CityPredictionEngine
        
        engine = CityPredictionEngine()
        forecast = engine.get_comprehensive_forecast(hours_ahead=24)
        
        assert forecast is not None
        assert "timestamp" in forecast
        assert "traffic" in forecast
        assert "crime" in forecast
        assert "infrastructure" in forecast
        assert "population" in forecast


class TestTrafficFlowPredictor:
    """Tests for TrafficFlowPredictor class."""

    def test_traffic_predictor_initialization(self):
        """Test TrafficFlowPredictor initializes correctly."""
        from backend.app.city_brain.prediction import TrafficFlowPredictor
        
        predictor = TrafficFlowPredictor()
        assert predictor is not None

    def test_predict_congestion(self):
        """Test predicting traffic congestion."""
        from backend.app.city_brain.prediction import TrafficFlowPredictor
        
        predictor = TrafficFlowPredictor()
        predictions = predictor.predict_congestion(hours_ahead=24)
        
        assert predictions is not None
        assert len(predictions) > 0

    def test_predict_evacuation_flow(self):
        """Test predicting evacuation flow."""
        from backend.app.city_brain.prediction import TrafficFlowPredictor
        
        predictor = TrafficFlowPredictor()
        prediction = predictor.predict_evacuation_flow(
            evacuation_zones=["A", "B"],
            population_to_evacuate=10000,
        )
        
        assert prediction is not None
        assert prediction.total_vehicles > 0

    def test_traffic_prediction_dataclass(self):
        """Test TrafficPrediction dataclass."""
        from backend.app.city_brain.prediction import TrafficPrediction, PredictionConfidence
        
        prediction = TrafficPrediction(
            segment_id="seg-001",
            road_name="Blue Heron Blvd",
            predicted_congestion="moderate",
            predicted_speed_mph=35.0,
            crash_risk=0.15,
            confidence=PredictionConfidence.HIGH,
            timestamp=datetime.utcnow(),
            hours_ahead=24,
        )
        
        assert prediction.segment_id == "seg-001"
        assert prediction.predicted_speed_mph == 35.0


class TestCrimeDisplacementPredictor:
    """Tests for CrimeDisplacementPredictor class."""

    def test_crime_predictor_initialization(self):
        """Test CrimeDisplacementPredictor initializes correctly."""
        from backend.app.city_brain.prediction import CrimeDisplacementPredictor
        
        predictor = CrimeDisplacementPredictor()
        assert predictor is not None

    def test_predict_displacement(self):
        """Test predicting crime displacement."""
        from backend.app.city_brain.prediction import CrimeDisplacementPredictor
        
        predictor = CrimeDisplacementPredictor()
        prediction = predictor.predict_displacement(
            weather_conditions={"temperature": 85, "rain": False},
            active_events=[],
            police_presence={"downtown": 3, "singer_island": 2},
            hours_ahead=24,
        )
        
        assert prediction is not None
        assert len(prediction.displacement_zones) > 0

    def test_crime_displacement_prediction_dataclass(self):
        """Test CrimeDisplacementPrediction dataclass."""
        from backend.app.city_brain.prediction import CrimeDisplacementPrediction, PredictionConfidence
        
        prediction = CrimeDisplacementPrediction(
            timestamp=datetime.utcnow(),
            time_window_hours=24,
            displacement_zones=[],
            risk_increase_areas=[],
            factors=["weather", "event"],
            patrol_recommendations=[],
            confidence=PredictionConfidence.MEDIUM,
        )
        
        assert prediction.time_window_hours == 24


class TestInfrastructureRiskPredictor:
    """Tests for InfrastructureRiskPredictor class."""

    def test_infrastructure_predictor_initialization(self):
        """Test InfrastructureRiskPredictor initializes correctly."""
        from backend.app.city_brain.prediction import InfrastructureRiskPredictor
        
        predictor = InfrastructureRiskPredictor()
        assert predictor is not None

    def test_predict_risk(self):
        """Test predicting infrastructure risk."""
        from backend.app.city_brain.prediction import InfrastructureRiskPredictor
        
        predictor = InfrastructureRiskPredictor()
        prediction = predictor.predict_risk(
            element_id="water-main-001",
            element_type="water_main",
            age_years=25,
            last_maintenance=datetime(2024, 1, 1),
            weather_forecast={"rain_inches": 4},
        )
        
        assert prediction is not None
        assert prediction.element_id == "water-main-001"

    def test_predict_all_risks(self):
        """Test predicting all infrastructure risks."""
        from backend.app.city_brain.prediction import InfrastructureRiskPredictor
        
        predictor = InfrastructureRiskPredictor()
        predictions = predictor.predict_all_risks()
        
        assert predictions is not None
        assert len(predictions) > 0


class TestDisasterImpactModel:
    """Tests for DisasterImpactModel class."""

    def test_disaster_model_initialization(self):
        """Test DisasterImpactModel initializes correctly."""
        from backend.app.city_brain.prediction import DisasterImpactModel
        
        model = DisasterImpactModel()
        assert model is not None

    def test_predict_hurricane_impact(self):
        """Test predicting hurricane impact."""
        from backend.app.city_brain.prediction import DisasterImpactModel
        
        model = DisasterImpactModel()
        prediction = model.predict_hurricane_impact(category=3)
        
        assert prediction is not None
        assert prediction.disaster_type == "hurricane"
        assert prediction.affected_population > 0

    def test_predict_flood_impact(self):
        """Test predicting flood impact."""
        from backend.app.city_brain.prediction import DisasterImpactModel
        
        model = DisasterImpactModel()
        prediction = model.predict_flood_impact(rainfall_inches=6)
        
        assert prediction is not None
        assert prediction.disaster_type == "flood"

    def test_predict_extreme_heat_impact(self):
        """Test predicting extreme heat impact."""
        from backend.app.city_brain.prediction import DisasterImpactModel
        
        model = DisasterImpactModel()
        prediction = model.predict_extreme_heat_impact(
            temperature_f=105,
            duration_hours=8,
        )
        
        assert prediction is not None
        assert prediction.disaster_type == "extreme_heat"


class TestPopulationMovementModel:
    """Tests for PopulationMovementModel class."""

    def test_population_model_initialization(self):
        """Test PopulationMovementModel initializes correctly."""
        from backend.app.city_brain.prediction import PopulationMovementModel
        
        model = PopulationMovementModel()
        assert model is not None

    def test_predict_movement(self):
        """Test predicting population movement."""
        from backend.app.city_brain.prediction import PopulationMovementModel
        
        model = PopulationMovementModel()
        prediction = model.predict_movement(
            day_of_week="saturday",
            hour_of_day=14,
            special_events=[],
            weather_conditions={"temperature": 85, "rain": False},
        )
        
        assert prediction is not None
        assert len(prediction.area_predictions) > 0

    def test_predict_marina_density(self):
        """Test predicting marina density."""
        from backend.app.city_brain.prediction import PopulationMovementModel
        
        model = PopulationMovementModel()
        density = model.predict_marina_density(
            day_of_week="saturday",
            hour_of_day=10,
            weather_conditions={"temperature": 85, "wind_mph": 8},
        )
        
        assert density is not None
        assert density >= 0


class TestPredictionEnums:
    """Tests for Prediction Engine enums."""

    def test_prediction_confidence_enum(self):
        """Test PredictionConfidence enum values."""
        from backend.app.city_brain.prediction import PredictionConfidence
        
        assert PredictionConfidence.LOW.value == "low"
        assert PredictionConfidence.MEDIUM.value == "medium"
        assert PredictionConfidence.HIGH.value == "high"
        assert PredictionConfidence.VERY_HIGH.value == "very_high"

    def test_risk_level_enum(self):
        """Test RiskLevel enum values."""
        from backend.app.city_brain.prediction import RiskLevel
        
        assert RiskLevel.MINIMAL.value == "minimal"
        assert RiskLevel.LOW.value == "low"
        assert RiskLevel.MODERATE.value == "moderate"
        assert RiskLevel.HIGH.value == "high"
        assert RiskLevel.SEVERE.value == "severe"
        assert RiskLevel.EXTREME.value == "extreme"

    def test_disaster_type_enum(self):
        """Test DisasterType enum values."""
        from backend.app.city_brain.prediction import DisasterType
        
        assert DisasterType.HURRICANE.value == "hurricane"
        assert DisasterType.FLOOD.value == "flood"
        assert DisasterType.TORNADO.value == "tornado"
        assert DisasterType.EXTREME_HEAT.value == "extreme_heat"
