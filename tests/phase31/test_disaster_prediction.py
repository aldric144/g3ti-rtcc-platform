"""
Phase 31: Disaster Prediction Engine Tests
"""

import pytest
from datetime import datetime
from backend.app.emergency_ai.disaster_prediction_engine import (
    DisasterPredictionEngine,
    HazardType,
    ThreatLevel,
    WeatherHazard,
    FloodPrediction,
    FireHazard,
    HazmatHazard,
    InfrastructureHazard,
    HazardPrediction,
)


class TestDisasterPredictionEngine:
    """Test suite for DisasterPredictionEngine"""

    def setup_method(self):
        """Setup test fixtures"""
        self.engine = DisasterPredictionEngine()

    def test_singleton_pattern(self):
        """Test that engine follows singleton pattern"""
        engine1 = DisasterPredictionEngine()
        engine2 = DisasterPredictionEngine()
        assert engine1 is engine2

    def test_agency_config(self):
        """Test agency configuration"""
        assert self.engine.agency_config["ori"] == "FL0500400"
        assert self.engine.agency_config["city"] == "Riviera Beach"
        assert self.engine.agency_config["state"] == "FL"
        assert self.engine.agency_config["zip"] == "33404"

    def test_city_zones(self):
        """Test city zones configuration"""
        assert len(self.engine.city_zones) == 10
        assert "Zone_A" in self.engine.city_zones
        assert "Zone_J" in self.engine.city_zones

    def test_zone_populations(self):
        """Test zone population data"""
        assert self.engine.zone_populations["Zone_A"] == 3500
        assert self.engine.zone_populations["Zone_E"] == 4500
        total_pop = sum(self.engine.zone_populations.values())
        assert total_pop == 36000

    def test_zone_elevations(self):
        """Test zone elevation data"""
        assert self.engine.zone_elevations["Zone_D"] == 15.3
        assert self.engine.zone_elevations["Zone_E"] == 4.8

    def test_predict_weather_hazard_hurricane(self):
        """Test hurricane prediction"""
        noaa_data = {
            "wind_speed_mph": 85,
            "rainfall_inches": 8,
            "pressure_mb": 975,
        }
        nhc_data = {
            "storm_name": "Test Hurricane",
            "category": 1,
            "storm_surge_feet": 5,
            "movement_speed_mph": 12,
        }
        
        hazard = self.engine.predict_weather_hazard(
            noaa_data=noaa_data,
            nhc_data=nhc_data,
        )
        
        assert hazard is not None
        assert hazard.hazard_id.startswith("WH-")
        assert hazard.threat_level.value >= 3
        assert len(hazard.affected_zones) > 0
        assert hazard.chain_of_custody_hash is not None

    def test_predict_flood_risk(self):
        """Test flood risk prediction"""
        flood = self.engine.predict_flood_risk(
            rainfall_inches=6,
            storm_surge_feet=4,
            tide_level="high",
        )
        
        assert flood is not None
        assert flood.prediction_id.startswith("FP-")
        assert len(flood.zone_flood_risks) > 0
        assert flood.chain_of_custody_hash is not None

    def test_predict_fire_spread(self):
        """Test fire spread prediction"""
        fire = self.engine.predict_fire_spread(
            origin_zone="Zone_A",
            wind_speed_mph=20,
            humidity_percent=30,
            temperature_f=95,
        )
        
        assert fire is not None
        assert fire.hazard_id.startswith("FH-")
        assert fire.origin_zone == "Zone_A"
        assert fire.spread_rate_acres_per_hour > 0
        assert fire.chain_of_custody_hash is not None

    def test_predict_hazmat_release(self):
        """Test hazmat release prediction"""
        hazmat = self.engine.predict_hazmat_release(
            chemical_name="Chlorine",
            chemical_class="toxic_gas",
            release_type="leak",
            release_quantity_gallons=500,
            origin_zone="Zone_B",
        )
        
        assert hazmat is not None
        assert hazmat.hazard_id.startswith("HZ-")
        assert hazmat.chemical_name == "Chlorine"
        assert hazmat.affected_radius_miles > 0
        assert hazmat.chain_of_custody_hash is not None

    def test_predict_infrastructure_failure(self):
        """Test infrastructure failure prediction"""
        infra = self.engine.predict_infrastructure_failure(
            infrastructure_type="bridge",
            infrastructure_name="Test Bridge",
            zone="Zone_C",
        )
        
        assert infra is not None
        assert infra.hazard_id.startswith("IH-")
        assert infra.infrastructure_type == "bridge"
        assert infra.chain_of_custody_hash is not None

    def test_get_unified_prediction(self):
        """Test unified prediction output"""
        prediction = self.engine.get_unified_prediction(
            hazard_type=HazardType.HURRICANE,
        )
        
        assert prediction is not None
        assert prediction.prediction_id.startswith("HP-")
        assert prediction.hazard_type == HazardType.HURRICANE
        assert prediction.threat_level in ThreatLevel
        assert prediction.confidence_score >= 0 and prediction.confidence_score <= 1
        assert len(prediction.recommended_actions) > 0
        assert len(prediction.agencies_required) > 0
        assert prediction.chain_of_custody_hash is not None

    def test_get_active_hazards(self):
        """Test getting active hazards"""
        hazards = self.engine.get_active_hazards()
        assert isinstance(hazards, list)

    def test_threat_level_enum(self):
        """Test threat level enumeration"""
        assert ThreatLevel.MINIMAL.value == 1
        assert ThreatLevel.LOW.value == 2
        assert ThreatLevel.MODERATE.value == 3
        assert ThreatLevel.HIGH.value == 4
        assert ThreatLevel.EXTREME.value == 5

    def test_hazard_type_enum(self):
        """Test hazard type enumeration"""
        assert HazardType.HURRICANE.value == "hurricane"
        assert HazardType.TORNADO.value == "tornado"
        assert HazardType.FLOODING.value == "flooding"
        assert HazardType.URBAN_FIRE.value == "urban_fire"
        assert HazardType.HAZMAT_RELEASE.value == "hazmat_release"

    def test_chain_of_custody_hash_format(self):
        """Test chain of custody hash format"""
        prediction = self.engine.get_unified_prediction(HazardType.FLOODING)
        assert len(prediction.chain_of_custody_hash) == 64
        assert all(c in "0123456789abcdef" for c in prediction.chain_of_custody_hash)

    def test_statistics_tracking(self):
        """Test statistics tracking"""
        initial_stats = self.engine.get_statistics()
        
        self.engine.get_unified_prediction(HazardType.HURRICANE)
        
        updated_stats = self.engine.get_statistics()
        assert updated_stats["total_predictions"] >= initial_stats["total_predictions"]
