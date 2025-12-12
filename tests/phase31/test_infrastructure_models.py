"""
Phase 31: Infrastructure Model Validation Tests
"""

import pytest
from backend.app.emergency_ai.disaster_prediction_engine import (
    DisasterPredictionEngine,
    HazardType,
    ThreatLevel,
)


class TestInfrastructureModels:
    """Test suite for infrastructure model validation"""

    def setup_method(self):
        """Setup test fixtures"""
        self.engine = DisasterPredictionEngine()

    def test_bridge_collapse_prediction(self):
        """Test bridge collapse prediction"""
        infra = self.engine.predict_infrastructure_failure(
            infrastructure_type="bridge",
            infrastructure_name="Blue Heron Bridge",
            zone="Zone_A",
        )
        
        assert infra is not None
        assert infra.infrastructure_type == "bridge"
        assert infra.infrastructure_name == "Blue Heron Bridge"

    def test_seawall_failure_prediction(self):
        """Test seawall failure prediction"""
        infra = self.engine.predict_infrastructure_failure(
            infrastructure_type="seawall",
            infrastructure_name="Marina Seawall",
            zone="Zone_E",
        )
        
        assert infra.infrastructure_type == "seawall"

    def test_power_grid_failure_prediction(self):
        """Test power grid failure prediction"""
        infra = self.engine.predict_infrastructure_failure(
            infrastructure_type="power_grid",
            infrastructure_name="Main Substation",
            zone="Zone_C",
        )
        
        assert infra.infrastructure_type == "power_grid"

    def test_roadway_subsidence_prediction(self):
        """Test roadway subsidence prediction"""
        infra = self.engine.predict_infrastructure_failure(
            infrastructure_type="roadway",
            infrastructure_name="Broadway Ave",
            zone="Zone_B",
        )
        
        assert infra.infrastructure_type == "roadway"

    def test_canal_failure_prediction(self):
        """Test canal failure prediction"""
        infra = self.engine.predict_infrastructure_failure(
            infrastructure_type="canal",
            infrastructure_name="Drainage Canal",
            zone="Zone_F",
        )
        
        assert infra.infrastructure_type == "canal"

    def test_infrastructure_stress_level(self):
        """Test infrastructure stress level calculation"""
        infra = self.engine.predict_infrastructure_failure(
            infrastructure_type="bridge",
            infrastructure_name="Test Bridge",
            zone="Zone_G",
            stress_factors={"age_years": 50, "load_factor": 1.2},
        )
        
        assert infra.stress_level >= 0

    def test_infrastructure_failure_probability(self):
        """Test infrastructure failure probability"""
        infra = self.engine.predict_infrastructure_failure(
            infrastructure_type="seawall",
            infrastructure_name="Test Seawall",
            zone="Zone_H",
        )
        
        assert 0 <= infra.failure_probability <= 1

    def test_infrastructure_affected_population(self):
        """Test infrastructure failure affected population"""
        infra = self.engine.predict_infrastructure_failure(
            infrastructure_type="power_grid",
            infrastructure_name="Test Substation",
            zone="Zone_I",
        )
        
        assert infra.affected_population >= 0

    def test_bridge_collapse_unified_prediction(self):
        """Test bridge collapse unified prediction"""
        prediction = self.engine.get_unified_prediction(
            hazard_type=HazardType.BRIDGE_COLLAPSE,
            infrastructure_name="Main Bridge",
            zone="Zone_A",
        )
        
        assert prediction.hazard_type == HazardType.BRIDGE_COLLAPSE

    def test_seawall_failure_unified_prediction(self):
        """Test seawall failure unified prediction"""
        prediction = self.engine.get_unified_prediction(
            hazard_type=HazardType.SEAWALL_FAILURE,
            infrastructure_name="Coastal Seawall",
            zone="Zone_E",
        )
        
        assert prediction.hazard_type == HazardType.SEAWALL_FAILURE

    def test_power_grid_failure_unified_prediction(self):
        """Test power grid failure unified prediction"""
        prediction = self.engine.get_unified_prediction(
            hazard_type=HazardType.POWER_GRID_FAILURE,
            infrastructure_name="Grid Section A",
            zone="Zone_C",
        )
        
        assert prediction.hazard_type == HazardType.POWER_GRID_FAILURE

    def test_infrastructure_chain_of_custody(self):
        """Test infrastructure prediction has chain of custody"""
        infra = self.engine.predict_infrastructure_failure(
            infrastructure_type="bridge",
            infrastructure_name="Test Bridge",
            zone="Zone_J",
        )
        
        assert infra.chain_of_custody_hash is not None
        assert len(infra.chain_of_custody_hash) == 64

    def test_infrastructure_agencies_required(self):
        """Test infrastructure failure includes required agencies"""
        prediction = self.engine.get_unified_prediction(
            hazard_type=HazardType.BRIDGE_COLLAPSE,
            infrastructure_name="Highway Bridge",
            zone="Zone_D",
        )
        
        assert len(prediction.agencies_required) > 0

    def test_infrastructure_recommended_actions(self):
        """Test infrastructure failure includes recommended actions"""
        prediction = self.engine.get_unified_prediction(
            hazard_type=HazardType.POWER_GRID_FAILURE,
            infrastructure_name="Substation B",
            zone="Zone_F",
        )
        
        assert len(prediction.recommended_actions) > 0

    def test_infrastructure_economic_impact(self):
        """Test infrastructure failure estimates economic impact"""
        prediction = self.engine.get_unified_prediction(
            hazard_type=HazardType.BRIDGE_COLLAPSE,
            infrastructure_name="Major Bridge",
            zone="Zone_A",
        )
        
        assert prediction.economic_impact_estimate >= 0

    def test_infrastructure_time_to_impact(self):
        """Test infrastructure failure time to impact"""
        prediction = self.engine.get_unified_prediction(
            hazard_type=HazardType.SEAWALL_FAILURE,
            infrastructure_name="Seawall Section",
            zone="Zone_E",
        )
        
        assert prediction.time_to_impact_hours >= 0
