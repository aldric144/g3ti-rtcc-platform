"""
Phase 31: Fire Spread Model Validation Tests
"""

import pytest
from backend.app.emergency_ai.disaster_prediction_engine import (
    DisasterPredictionEngine,
    HazardType,
    ThreatLevel,
)


class TestFireModels:
    """Test suite for fire spread model validation"""

    def setup_method(self):
        """Setup test fixtures"""
        self.engine = DisasterPredictionEngine()

    def test_urban_fire_prediction(self):
        """Test urban fire prediction"""
        fire = self.engine.predict_fire_spread(
            origin_zone="Zone_A",
            wind_speed_mph=15,
            humidity_percent=40,
            temperature_f=85,
        )
        
        assert fire is not None
        assert fire.origin_zone == "Zone_A"
        assert fire.spread_rate_acres_per_hour > 0

    def test_fire_spread_high_wind(self):
        """Test fire spread with high wind"""
        fire_low_wind = self.engine.predict_fire_spread(
            origin_zone="Zone_B",
            wind_speed_mph=5,
            humidity_percent=50,
        )
        
        fire_high_wind = self.engine.predict_fire_spread(
            origin_zone="Zone_B",
            wind_speed_mph=30,
            humidity_percent=50,
        )
        
        assert fire_high_wind.spread_rate_acres_per_hour >= fire_low_wind.spread_rate_acres_per_hour

    def test_fire_spread_low_humidity(self):
        """Test fire spread with low humidity"""
        fire_high_humidity = self.engine.predict_fire_spread(
            origin_zone="Zone_C",
            wind_speed_mph=10,
            humidity_percent=80,
        )
        
        fire_low_humidity = self.engine.predict_fire_spread(
            origin_zone="Zone_C",
            wind_speed_mph=10,
            humidity_percent=20,
        )
        
        assert fire_low_humidity.spread_rate_acres_per_hour >= fire_high_humidity.spread_rate_acres_per_hour

    def test_fire_spread_high_temperature(self):
        """Test fire spread with high temperature"""
        fire = self.engine.predict_fire_spread(
            origin_zone="Zone_D",
            wind_speed_mph=15,
            humidity_percent=30,
            temperature_f=100,
        )
        
        assert fire.spread_rate_acres_per_hour > 0

    def test_fire_affected_zones(self):
        """Test fire predicts affected zones"""
        fire = self.engine.predict_fire_spread(
            origin_zone="Zone_A",
            wind_speed_mph=20,
            humidity_percent=25,
        )
        
        assert len(fire.affected_zones) > 0
        assert fire.origin_zone in fire.affected_zones

    def test_fire_time_to_critical(self):
        """Test fire estimates time to critical spread"""
        fire = self.engine.predict_fire_spread(
            origin_zone="Zone_E",
            wind_speed_mph=25,
            humidity_percent=20,
        )
        
        assert fire.time_to_critical_hours > 0

    def test_fire_structures_at_risk(self):
        """Test fire estimates structures at risk"""
        fire = self.engine.predict_fire_spread(
            origin_zone="Zone_F",
            wind_speed_mph=15,
            humidity_percent=35,
        )
        
        assert fire.structures_at_risk >= 0

    def test_wildfire_prediction(self):
        """Test wildfire prediction"""
        prediction = self.engine.get_unified_prediction(
            hazard_type=HazardType.WILDFIRE,
            origin_zone="Zone_G",
            wind_speed_mph=20,
            humidity_percent=25,
        )
        
        assert prediction.hazard_type == HazardType.WILDFIRE

    def test_urban_fire_unified_prediction(self):
        """Test urban fire unified prediction"""
        prediction = self.engine.get_unified_prediction(
            hazard_type=HazardType.URBAN_FIRE,
            origin_zone="Zone_H",
        )
        
        assert prediction.hazard_type == HazardType.URBAN_FIRE
        assert len(prediction.recommended_actions) > 0

    def test_fire_threat_level_calculation(self):
        """Test fire threat level calculation"""
        fire_mild = self.engine.predict_fire_spread(
            origin_zone="Zone_A",
            wind_speed_mph=5,
            humidity_percent=70,
            temperature_f=70,
        )
        
        fire_severe = self.engine.predict_fire_spread(
            origin_zone="Zone_A",
            wind_speed_mph=35,
            humidity_percent=15,
            temperature_f=100,
        )
        
        assert fire_severe.threat_level.value >= fire_mild.threat_level.value

    def test_fire_chain_of_custody(self):
        """Test fire prediction has chain of custody"""
        fire = self.engine.predict_fire_spread(
            origin_zone="Zone_I",
            wind_speed_mph=10,
            humidity_percent=50,
        )
        
        assert fire.chain_of_custody_hash is not None
        assert len(fire.chain_of_custody_hash) == 64

    def test_fire_agencies_required(self):
        """Test fire prediction includes required agencies"""
        prediction = self.engine.get_unified_prediction(
            hazard_type=HazardType.URBAN_FIRE,
            origin_zone="Zone_J",
        )
        
        assert "fire_rescue" in prediction.agencies_required or len(prediction.agencies_required) > 0

    def test_fire_evacuation_recommendation(self):
        """Test severe fire recommends evacuation"""
        prediction = self.engine.get_unified_prediction(
            hazard_type=HazardType.URBAN_FIRE,
            origin_zone="Zone_A",
            wind_speed_mph=30,
            humidity_percent=15,
        )
        
        assert prediction.threat_level.value >= 3

    def test_fire_economic_impact(self):
        """Test fire estimates economic impact"""
        prediction = self.engine.get_unified_prediction(
            hazard_type=HazardType.URBAN_FIRE,
            origin_zone="Zone_B",
        )
        
        assert prediction.economic_impact_estimate >= 0
