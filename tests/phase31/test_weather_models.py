"""
Phase 31: Weather Hazard Model Validation Tests
"""

import pytest
from backend.app.emergency_ai.disaster_prediction_engine import (
    DisasterPredictionEngine,
    HazardType,
    ThreatLevel,
)


class TestWeatherModels:
    """Test suite for weather hazard model validation"""

    def setup_method(self):
        """Setup test fixtures"""
        self.engine = DisasterPredictionEngine()

    def test_hurricane_category_1(self):
        """Test hurricane category 1 prediction"""
        prediction = self.engine.get_unified_prediction(
            hazard_type=HazardType.HURRICANE,
            noaa_data={"wind_speed_mph": 80, "pressure_mb": 985},
            nhc_data={"category": 1, "storm_surge_feet": 4},
        )
        
        assert prediction.threat_level.value >= 3

    def test_hurricane_category_3(self):
        """Test hurricane category 3 prediction"""
        prediction = self.engine.get_unified_prediction(
            hazard_type=HazardType.HURRICANE,
            noaa_data={"wind_speed_mph": 120, "pressure_mb": 960},
            nhc_data={"category": 3, "storm_surge_feet": 9},
        )
        
        assert prediction.threat_level.value >= 4

    def test_hurricane_category_5(self):
        """Test hurricane category 5 prediction"""
        prediction = self.engine.get_unified_prediction(
            hazard_type=HazardType.HURRICANE,
            noaa_data={"wind_speed_mph": 160, "pressure_mb": 920},
            nhc_data={"category": 5, "storm_surge_feet": 15},
        )
        
        assert prediction.threat_level == ThreatLevel.EXTREME

    def test_tornado_prediction(self):
        """Test tornado prediction"""
        prediction = self.engine.get_unified_prediction(
            hazard_type=HazardType.TORNADO,
            noaa_data={"wind_speed_mph": 100},
        )
        
        assert prediction.hazard_type == HazardType.TORNADO
        assert prediction.threat_level.value >= 3

    def test_flooding_low_rainfall(self):
        """Test flooding prediction with low rainfall"""
        prediction = self.engine.get_unified_prediction(
            hazard_type=HazardType.FLOODING,
            local_sensor_data={"rainfall_inches": 2},
        )
        
        assert prediction.threat_level.value <= 3

    def test_flooding_high_rainfall(self):
        """Test flooding prediction with high rainfall"""
        prediction = self.engine.get_unified_prediction(
            hazard_type=HazardType.FLOODING,
            local_sensor_data={"rainfall_inches": 10},
        )
        
        assert prediction.threat_level.value >= 3

    def test_storm_surge_prediction(self):
        """Test storm surge prediction"""
        prediction = self.engine.get_unified_prediction(
            hazard_type=HazardType.STORM_SURGE,
            nhc_data={"storm_surge_feet": 8},
        )
        
        assert prediction.hazard_type == HazardType.STORM_SURGE
        assert len(prediction.affected_zones) > 0

    def test_severe_thunderstorm_prediction(self):
        """Test severe thunderstorm prediction"""
        prediction = self.engine.get_unified_prediction(
            hazard_type=HazardType.SEVERE_THUNDERSTORM,
            noaa_data={"wind_speed_mph": 60, "hail_size_inches": 1},
        )
        
        assert prediction.hazard_type == HazardType.SEVERE_THUNDERSTORM

    def test_flood_risk_by_elevation(self):
        """Test flood risk varies by zone elevation"""
        flood = self.engine.predict_flood_risk(
            rainfall_inches=6,
            storm_surge_feet=4,
        )
        
        zone_e_risk = flood.zone_flood_risks.get("Zone_E", 0)
        zone_d_risk = flood.zone_flood_risks.get("Zone_D", 0)
        
        assert zone_e_risk >= zone_d_risk

    def test_weather_hazard_agencies_required(self):
        """Test weather hazard includes required agencies"""
        prediction = self.engine.get_unified_prediction(
            hazard_type=HazardType.HURRICANE,
            nhc_data={"category": 2},
        )
        
        assert len(prediction.agencies_required) > 0

    def test_weather_hazard_recommended_actions(self):
        """Test weather hazard includes recommended actions"""
        prediction = self.engine.get_unified_prediction(
            hazard_type=HazardType.FLOODING,
        )
        
        assert len(prediction.recommended_actions) > 0

    def test_weather_hazard_affected_population(self):
        """Test weather hazard calculates affected population"""
        prediction = self.engine.get_unified_prediction(
            hazard_type=HazardType.HURRICANE,
        )
        
        assert prediction.affected_population > 0

    def test_weather_hazard_time_to_impact(self):
        """Test weather hazard estimates time to impact"""
        prediction = self.engine.get_unified_prediction(
            hazard_type=HazardType.TORNADO,
        )
        
        assert prediction.time_to_impact_hours >= 0

    def test_weather_hazard_confidence_score(self):
        """Test weather hazard confidence score range"""
        prediction = self.engine.get_unified_prediction(
            hazard_type=HazardType.HURRICANE,
        )
        
        assert 0 <= prediction.confidence_score <= 1

    def test_weather_hazard_economic_impact(self):
        """Test weather hazard estimates economic impact"""
        prediction = self.engine.get_unified_prediction(
            hazard_type=HazardType.HURRICANE,
            nhc_data={"category": 3},
        )
        
        assert prediction.economic_impact_estimate > 0
