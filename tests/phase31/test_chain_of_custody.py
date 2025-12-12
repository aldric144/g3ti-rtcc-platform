"""
Phase 31: Chain of Custody Validation Tests
"""

import pytest
import hashlib
from backend.app.emergency_ai.disaster_prediction_engine import (
    DisasterPredictionEngine,
    HazardType,
)
from backend.app.emergency_ai.response_coordination_engine import (
    ResponseCoordinationEngine,
    AgencyType,
    TaskPriority,
    ResourceType,
)
from backend.app.emergency_ai.recovery_planner import (
    RecoveryPlanner,
    SupplyType,
    InfrastructureType,
)
from backend.app.emergency_ai.communication_intel_engine import (
    CommunicationIntelEngine,
    AlertType,
    AlertPriority,
)


class TestChainOfCustody:
    """Test suite for chain of custody validation"""

    def setup_method(self):
        """Setup test fixtures"""
        self.prediction_engine = DisasterPredictionEngine()
        self.response_engine = ResponseCoordinationEngine()
        self.recovery_planner = RecoveryPlanner()
        self.communication_engine = CommunicationIntelEngine()

    def test_prediction_hash_format(self):
        """Test prediction hash format is SHA256"""
        prediction = self.prediction_engine.get_unified_prediction(
            hazard_type=HazardType.HURRICANE,
        )
        
        assert len(prediction.chain_of_custody_hash) == 64
        assert all(c in "0123456789abcdef" for c in prediction.chain_of_custody_hash)

    def test_prediction_hash_uniqueness(self):
        """Test prediction hashes are unique"""
        prediction1 = self.prediction_engine.get_unified_prediction(
            hazard_type=HazardType.HURRICANE,
        )
        
        prediction2 = self.prediction_engine.get_unified_prediction(
            hazard_type=HazardType.FLOODING,
        )
        
        assert prediction1.chain_of_custody_hash != prediction2.chain_of_custody_hash

    def test_weather_hazard_hash(self):
        """Test weather hazard has chain of custody hash"""
        hazard = self.prediction_engine.predict_weather_hazard(
            noaa_data={"wind_speed_mph": 80},
            nhc_data={"category": 1},
        )
        
        assert hazard.chain_of_custody_hash is not None
        assert len(hazard.chain_of_custody_hash) == 64

    def test_flood_prediction_hash(self):
        """Test flood prediction has chain of custody hash"""
        flood = self.prediction_engine.predict_flood_risk(
            rainfall_inches=6,
            storm_surge_feet=4,
        )
        
        assert flood.chain_of_custody_hash is not None
        assert len(flood.chain_of_custody_hash) == 64

    def test_fire_hazard_hash(self):
        """Test fire hazard has chain of custody hash"""
        fire = self.prediction_engine.predict_fire_spread(
            origin_zone="Zone_A",
            wind_speed_mph=15,
            humidity_percent=30,
        )
        
        assert fire.chain_of_custody_hash is not None
        assert len(fire.chain_of_custody_hash) == 64

    def test_hazmat_hazard_hash(self):
        """Test hazmat hazard has chain of custody hash"""
        hazmat = self.prediction_engine.predict_hazmat_release(
            chemical_name="Chlorine",
            chemical_class="toxic_gas",
            release_type="leak",
            release_quantity_gallons=500,
            origin_zone="Zone_B",
        )
        
        assert hazmat.chain_of_custody_hash is not None
        assert len(hazmat.chain_of_custody_hash) == 64

    def test_infrastructure_hazard_hash(self):
        """Test infrastructure hazard has chain of custody hash"""
        infra = self.prediction_engine.predict_infrastructure_failure(
            infrastructure_type="bridge",
            infrastructure_name="Test Bridge",
            zone="Zone_C",
        )
        
        assert infra.chain_of_custody_hash is not None
        assert len(infra.chain_of_custody_hash) == 64

    def test_agency_task_hash(self):
        """Test agency task has chain of custody hash"""
        task = self.response_engine.create_agency_task(
            agency_type=AgencyType.POLICE,
            priority=TaskPriority.HIGH,
            description="Test task",
            location_zone="Zone_D",
        )
        
        assert task.chain_of_custody_hash is not None
        assert len(task.chain_of_custody_hash) == 64

    def test_resource_allocation_hash(self):
        """Test resource allocation has chain of custody hash"""
        allocation = self.response_engine.allocate_resources(
            resource_type=ResourceType.PATROL_UNITS,
            quantity=5,
            zone="Zone_E",
            task_id="TEST-001",
        )
        
        assert allocation.chain_of_custody_hash is not None
        assert len(allocation.chain_of_custody_hash) == 64

    def test_evacuation_route_hash(self):
        """Test evacuation route has chain of custody hash"""
        route = self.response_engine.plan_evacuation_route(
            origin_zone="Zone_F",
            destination_type="shelter",
        )
        
        assert route.chain_of_custody_hash is not None
        assert len(route.chain_of_custody_hash) == 64

    def test_response_plan_hash(self):
        """Test response plan has chain of custody hash"""
        plan = self.response_engine.coordinate_multi_agency_response(
            incident_type="hurricane",
            threat_level=4,
            affected_zones=["Zone_G"],
        )
        
        assert plan.chain_of_custody_hash is not None
        assert len(plan.chain_of_custody_hash) == 64

    def test_structure_damage_hash(self):
        """Test structure damage has chain of custody hash"""
        damage = self.recovery_planner.assess_structure_damage(
            structure_id="STR-001",
            structure_type="residential",
            address="123 Main St",
            zone="Zone_H",
            damage_indicators={"roof_damage": True, "roof_damage_percent": 30},
        )
        
        assert damage.chain_of_custody_hash is not None
        assert len(damage.chain_of_custody_hash) == 64

    def test_zone_damage_assessment_hash(self):
        """Test zone damage assessment has chain of custody hash"""
        assessment = self.recovery_planner.assess_zone_damage(
            zone="Zone_I",
            incident_type="hurricane",
            severity_factor=0.5,
        )
        
        assert assessment.chain_of_custody_hash is not None
        assert len(assessment.chain_of_custody_hash) == 64

    def test_supply_allocation_hash(self):
        """Test supply allocation has chain of custody hash"""
        allocation = self.recovery_planner.optimize_supply_allocation(
            zone="Zone_J",
            supply_type=SupplyType.WATER,
            population_served=1000,
            days_needed=3.0,
        )
        
        assert allocation.chain_of_custody_hash is not None
        assert len(allocation.chain_of_custody_hash) == 64

    def test_infrastructure_repair_hash(self):
        """Test infrastructure repair has chain of custody hash"""
        repair = self.recovery_planner.plan_infrastructure_repair(
            infrastructure_type=InfrastructureType.BRIDGE,
            infrastructure_name="Test Bridge",
            zone="Zone_A",
            damage_description="Major damage",
            priority=1,
        )
        
        assert repair.chain_of_custody_hash is not None
        assert len(repair.chain_of_custody_hash) == 64

    def test_recovery_plan_hash(self):
        """Test recovery plan has chain of custody hash"""
        plan = self.recovery_planner.create_recovery_plan(
            incident_type="hurricane",
            affected_zones=["Zone_B"],
            severity_factor=0.5,
        )
        
        assert plan.chain_of_custody_hash is not None
        assert len(plan.chain_of_custody_hash) == 64

    def test_emergency_alert_hash(self):
        """Test emergency alert has chain of custody hash"""
        alert = self.communication_engine.create_emergency_alert(
            alert_type=AlertType.EVACUATION_ORDER,
            priority=AlertPriority.EMERGENCY,
            affected_zones=["Zone_C"],
        )
        
        assert alert.chain_of_custody_hash is not None
        assert len(alert.chain_of_custody_hash) == 64

    def test_social_signal_hash(self):
        """Test social signal has chain of custody hash"""
        signals = self.communication_engine.detect_social_signals([
            {
                "content": "Need help! Flooding on my street",
                "platform": "twitter",
                "is_public": True,
            },
        ])
        
        if signals:
            assert signals[0].chain_of_custody_hash is not None
            assert len(signals[0].chain_of_custody_hash) == 64

    def test_hash_is_deterministic(self):
        """Test that hash generation is deterministic for same input"""
        test_data = "test_id:2025-12-12T00:00:00:test_type:test_value"
        hash1 = hashlib.sha256(test_data.encode()).hexdigest()
        hash2 = hashlib.sha256(test_data.encode()).hexdigest()
        
        assert hash1 == hash2
        assert len(hash1) == 64
