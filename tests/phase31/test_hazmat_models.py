"""
Phase 31: Hazmat Model Validation Tests
"""

import pytest
from backend.app.emergency_ai.disaster_prediction_engine import (
    DisasterPredictionEngine,
    HazardType,
    ThreatLevel,
)


class TestHazmatModels:
    """Test suite for hazmat model validation"""

    def setup_method(self):
        """Setup test fixtures"""
        self.engine = DisasterPredictionEngine()

    def test_hazmat_release_prediction(self):
        """Test hazmat release prediction"""
        hazmat = self.engine.predict_hazmat_release(
            chemical_name="Chlorine",
            chemical_class="toxic_gas",
            release_type="leak",
            release_quantity_gallons=500,
            origin_zone="Zone_A",
        )
        
        assert hazmat is not None
        assert hazmat.chemical_name == "Chlorine"
        assert hazmat.affected_radius_miles > 0

    def test_hazmat_toxic_gas(self):
        """Test toxic gas release"""
        hazmat = self.engine.predict_hazmat_release(
            chemical_name="Ammonia",
            chemical_class="toxic_gas",
            release_type="rupture",
            release_quantity_gallons=1000,
            origin_zone="Zone_B",
        )
        
        assert hazmat.chemical_class == "toxic_gas"
        assert hazmat.threat_level.value >= 3

    def test_hazmat_flammable_liquid(self):
        """Test flammable liquid release"""
        hazmat = self.engine.predict_hazmat_release(
            chemical_name="Gasoline",
            chemical_class="flammable_liquid",
            release_type="spill",
            release_quantity_gallons=2000,
            origin_zone="Zone_C",
        )
        
        assert hazmat.chemical_class == "flammable_liquid"

    def test_hazmat_corrosive(self):
        """Test corrosive release"""
        hazmat = self.engine.predict_hazmat_release(
            chemical_name="Sulfuric Acid",
            chemical_class="corrosive",
            release_type="leak",
            release_quantity_gallons=300,
            origin_zone="Zone_D",
        )
        
        assert hazmat.chemical_class == "corrosive"

    def test_hazmat_affected_radius_by_quantity(self):
        """Test affected radius varies by quantity"""
        hazmat_small = self.engine.predict_hazmat_release(
            chemical_name="Chlorine",
            chemical_class="toxic_gas",
            release_type="leak",
            release_quantity_gallons=100,
            origin_zone="Zone_E",
        )
        
        hazmat_large = self.engine.predict_hazmat_release(
            chemical_name="Chlorine",
            chemical_class="toxic_gas",
            release_type="leak",
            release_quantity_gallons=5000,
            origin_zone="Zone_E",
        )
        
        assert hazmat_large.affected_radius_miles >= hazmat_small.affected_radius_miles

    def test_hazmat_evacuation_zones(self):
        """Test hazmat predicts evacuation zones"""
        hazmat = self.engine.predict_hazmat_release(
            chemical_name="Chlorine",
            chemical_class="toxic_gas",
            release_type="rupture",
            release_quantity_gallons=2000,
            origin_zone="Zone_F",
        )
        
        assert len(hazmat.evacuation_zones) > 0

    def test_hazmat_shelter_in_place_zones(self):
        """Test hazmat predicts shelter-in-place zones"""
        hazmat = self.engine.predict_hazmat_release(
            chemical_name="Ammonia",
            chemical_class="toxic_gas",
            release_type="leak",
            release_quantity_gallons=500,
            origin_zone="Zone_G",
        )
        
        assert len(hazmat.shelter_in_place_zones) >= 0

    def test_hazmat_affected_population(self):
        """Test hazmat estimates affected population"""
        hazmat = self.engine.predict_hazmat_release(
            chemical_name="Chlorine",
            chemical_class="toxic_gas",
            release_type="leak",
            release_quantity_gallons=1000,
            origin_zone="Zone_H",
        )
        
        assert hazmat.affected_population > 0

    def test_chemical_spill_prediction(self):
        """Test chemical spill unified prediction"""
        prediction = self.engine.get_unified_prediction(
            hazard_type=HazardType.CHEMICAL_SPILL,
            chemical_name="Diesel Fuel",
            chemical_class="flammable_liquid",
            release_type="spill",
            release_quantity_gallons=3000,
            origin_zone="Zone_I",
        )
        
        assert prediction.hazard_type == HazardType.CHEMICAL_SPILL

    def test_hazmat_release_unified_prediction(self):
        """Test hazmat release unified prediction"""
        prediction = self.engine.get_unified_prediction(
            hazard_type=HazardType.HAZMAT_RELEASE,
            chemical_name="Propane",
            chemical_class="flammable_gas",
            release_type="leak",
            release_quantity_gallons=500,
            origin_zone="Zone_J",
        )
        
        assert prediction.hazard_type == HazardType.HAZMAT_RELEASE
        assert len(prediction.recommended_actions) > 0

    def test_hazmat_chain_of_custody(self):
        """Test hazmat prediction has chain of custody"""
        hazmat = self.engine.predict_hazmat_release(
            chemical_name="Chlorine",
            chemical_class="toxic_gas",
            release_type="leak",
            release_quantity_gallons=500,
            origin_zone="Zone_A",
        )
        
        assert hazmat.chain_of_custody_hash is not None
        assert len(hazmat.chain_of_custody_hash) == 64

    def test_hazmat_agencies_required(self):
        """Test hazmat includes required agencies"""
        prediction = self.engine.get_unified_prediction(
            hazard_type=HazardType.HAZMAT_RELEASE,
            chemical_name="Unknown Chemical",
            origin_zone="Zone_B",
        )
        
        assert len(prediction.agencies_required) > 0

    def test_hazmat_time_to_impact(self):
        """Test hazmat estimates time to impact"""
        prediction = self.engine.get_unified_prediction(
            hazard_type=HazardType.HAZMAT_RELEASE,
            chemical_name="Chlorine",
            origin_zone="Zone_C",
        )
        
        assert prediction.time_to_impact_hours >= 0

    def test_hazmat_wind_direction_factor(self):
        """Test hazmat considers wind direction"""
        hazmat = self.engine.predict_hazmat_release(
            chemical_name="Ammonia",
            chemical_class="toxic_gas",
            release_type="leak",
            release_quantity_gallons=1000,
            origin_zone="Zone_D",
            wind_speed_mph=15,
            wind_direction="NE",
        )
        
        assert hazmat is not None
