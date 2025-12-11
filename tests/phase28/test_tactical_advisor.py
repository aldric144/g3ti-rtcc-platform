"""
Test Suite 4: Tactical Advisor Engine Tests

Tests for tactical guidance, cover positions, escape routes, and backup coordination.
"""

import pytest
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend', 'app'))

from officer_assist.tactical_advisor import (
    TacticalAdvisorEngine,
    TacticalScenario,
    CoverType,
    ThreatLevel,
    CoverPosition,
    EscapeRoute,
    BackupUnit,
    TacticalAdvice,
    SceneLocation,
)


class TestTacticalAdvisorEngine:
    """Tests for Tactical Advisor Engine"""
    
    def setup_method(self):
        """Reset singleton for each test"""
        TacticalAdvisorEngine._instance = None
        self.engine = TacticalAdvisorEngine()
    
    def test_singleton_pattern(self):
        """Test that engine uses singleton pattern"""
        engine1 = TacticalAdvisorEngine()
        engine2 = TacticalAdvisorEngine()
        assert engine1 is engine2
    
    def test_agency_configuration(self):
        """Test agency configuration is correct"""
        assert self.engine.agency_config["ori"] == "FL0500400"
        assert self.engine.agency_config["name"] == "Riviera Beach Police Department"
    
    def test_traffic_stop_advice(self):
        """Test tactical advice for traffic stop"""
        advice = self.engine.get_tactical_advice(
            incident_id="INC-001",
            officer_id="RBPD-201",
            scenario=TacticalScenario.TRAFFIC_STOP,
        )
        
        assert advice is not None
        assert advice.scenario == TacticalScenario.TRAFFIC_STOP
        assert advice.primary_recommendation is not None
        assert len(advice.tactical_notes) > 0
    
    def test_felony_stop_advice(self):
        """Test tactical advice for felony stop"""
        advice = self.engine.get_tactical_advice(
            incident_id="INC-002",
            officer_id="RBPD-201",
            scenario=TacticalScenario.FELONY_STOP,
            threat_level=ThreatLevel.HIGH,
        )
        
        assert advice is not None
        assert advice.scenario == TacticalScenario.FELONY_STOP
        assert advice.lethal_cover_required
    
    def test_foot_pursuit_advice(self):
        """Test tactical advice for foot pursuit"""
        advice = self.engine.get_tactical_advice(
            incident_id="INC-003",
            officer_id="RBPD-201",
            scenario=TacticalScenario.FOOT_PURSUIT,
        )
        
        assert advice is not None
        assert advice.scenario == TacticalScenario.FOOT_PURSUIT
        assert len(advice.escape_routes) > 0
    
    def test_domestic_call_advice(self):
        """Test tactical advice for domestic call"""
        advice = self.engine.get_tactical_advice(
            incident_id="INC-004",
            officer_id="RBPD-201",
            scenario=TacticalScenario.DOMESTIC_CALL,
        )
        
        assert advice is not None
        assert advice.scenario == TacticalScenario.DOMESTIC_CALL
        assert len(advice.de_escalation_options) > 0
    
    def test_shots_fired_advice(self):
        """Test tactical advice for shots fired"""
        advice = self.engine.get_tactical_advice(
            incident_id="INC-005",
            officer_id="RBPD-201",
            scenario=TacticalScenario.SHOTS_FIRED,
            threat_level=ThreatLevel.CRITICAL,
        )
        
        assert advice is not None
        assert advice.scenario == TacticalScenario.SHOTS_FIRED
        assert advice.lethal_cover_required
        assert len(advice.cover_positions) > 0
    
    def test_burglary_in_progress_advice(self):
        """Test tactical advice for burglary in progress"""
        advice = self.engine.get_tactical_advice(
            incident_id="INC-006",
            officer_id="RBPD-201",
            scenario=TacticalScenario.BURGLARY_IN_PROGRESS,
        )
        
        assert advice is not None
        assert advice.scenario == TacticalScenario.BURGLARY_IN_PROGRESS
        assert len(advice.building_entries) > 0
    
    def test_active_shooter_advice(self):
        """Test tactical advice for active shooter"""
        advice = self.engine.get_tactical_advice(
            incident_id="INC-007",
            officer_id="RBPD-201",
            scenario=TacticalScenario.ACTIVE_SHOOTER,
            threat_level=ThreatLevel.CRITICAL,
        )
        
        assert advice is not None
        assert advice.scenario == TacticalScenario.ACTIVE_SHOOTER
        assert advice.lethal_cover_required
        assert advice.air_support_recommended or len(advice.backup_units) > 0
    
    def test_hostage_situation_advice(self):
        """Test tactical advice for hostage situation"""
        advice = self.engine.get_tactical_advice(
            incident_id="INC-008",
            officer_id="RBPD-201",
            scenario=TacticalScenario.HOSTAGE_SITUATION,
            threat_level=ThreatLevel.CRITICAL,
        )
        
        assert advice is not None
        assert advice.scenario == TacticalScenario.HOSTAGE_SITUATION
        assert len(advice.de_escalation_options) > 0
    
    def test_barricaded_subject_advice(self):
        """Test tactical advice for barricaded subject"""
        advice = self.engine.get_tactical_advice(
            incident_id="INC-009",
            officer_id="RBPD-201",
            scenario=TacticalScenario.BARRICADED_SUBJECT,
        )
        
        assert advice is not None
        assert advice.scenario == TacticalScenario.BARRICADED_SUBJECT
        assert advice.containment_strategy is not None
    
    def test_cover_positions_identified(self):
        """Test cover positions are identified"""
        advice = self.engine.get_tactical_advice(
            incident_id="INC-010",
            officer_id="RBPD-201",
            scenario=TacticalScenario.SHOTS_FIRED,
        )
        
        assert len(advice.cover_positions) > 0
        for position in advice.cover_positions:
            assert position.cover_type in [CoverType.HARD_COVER, CoverType.SOFT_COVER, CoverType.CONCEALMENT]
            assert position.effectiveness >= 0 and position.effectiveness <= 1
    
    def test_escape_routes_identified(self):
        """Test escape routes are identified"""
        advice = self.engine.get_tactical_advice(
            incident_id="INC-011",
            officer_id="RBPD-201",
            scenario=TacticalScenario.FOOT_PURSUIT,
        )
        
        assert len(advice.escape_routes) > 0
        for route in advice.escape_routes:
            assert route.probability >= 0 and route.probability <= 1
            assert route.direction is not None
    
    def test_backup_units_identified(self):
        """Test backup units are identified"""
        advice = self.engine.get_tactical_advice(
            incident_id="INC-012",
            officer_id="RBPD-201",
            scenario=TacticalScenario.FELONY_STOP,
        )
        
        assert len(advice.backup_units) > 0
        for unit in advice.backup_units:
            assert unit.unit_id is not None
            assert unit.eta_minutes >= 0
    
    def test_building_entries_identified(self):
        """Test building entries are identified for building scenarios"""
        advice = self.engine.get_tactical_advice(
            incident_id="INC-013",
            officer_id="RBPD-201",
            scenario=TacticalScenario.BURGLARY_IN_PROGRESS,
        )
        
        assert len(advice.building_entries) > 0
    
    def test_communication_plan_generated(self):
        """Test communication plan is generated"""
        advice = self.engine.get_tactical_advice(
            incident_id="INC-014",
            officer_id="RBPD-201",
            scenario=TacticalScenario.ACTIVE_SHOOTER,
        )
        
        assert advice.communication_plan is not None
        assert len(advice.communication_plan) > 0
    
    def test_containment_strategy_generated(self):
        """Test containment strategy is generated"""
        advice = self.engine.get_tactical_advice(
            incident_id="INC-015",
            officer_id="RBPD-201",
            scenario=TacticalScenario.BARRICADED_SUBJECT,
        )
        
        assert advice.containment_strategy is not None
        assert len(advice.containment_strategy) > 0
    
    def test_de_escalation_options_generated(self):
        """Test de-escalation options are generated"""
        advice = self.engine.get_tactical_advice(
            incident_id="INC-016",
            officer_id="RBPD-201",
            scenario=TacticalScenario.DOMESTIC_CALL,
        )
        
        assert len(advice.de_escalation_options) > 0
    
    def test_warnings_generated_for_high_threat(self):
        """Test warnings are generated for high threat scenarios"""
        advice = self.engine.get_tactical_advice(
            incident_id="INC-017",
            officer_id="RBPD-201",
            scenario=TacticalScenario.SHOTS_FIRED,
            threat_level=ThreatLevel.CRITICAL,
        )
        
        assert len(advice.warnings) > 0
    
    def test_k9_recommended_for_foot_pursuit(self):
        """Test K9 is recommended for foot pursuit"""
        advice = self.engine.get_tactical_advice(
            incident_id="INC-018",
            officer_id="RBPD-201",
            scenario=TacticalScenario.FOOT_PURSUIT,
        )
        
        assert advice.k9_recommended
    
    def test_air_support_recommended_for_vehicle_pursuit(self):
        """Test air support is recommended for vehicle pursuit"""
        advice = self.engine.get_tactical_advice(
            incident_id="INC-019",
            officer_id="RBPD-201",
            scenario=TacticalScenario.VEHICLE_PURSUIT,
        )
        
        assert advice.air_support_recommended
    
    def test_advice_update(self):
        """Test tactical advice can be updated"""
        self.engine.get_tactical_advice(
            incident_id="INC-020",
            officer_id="RBPD-201",
            scenario=TacticalScenario.TRAFFIC_STOP,
        )
        
        updated = self.engine.update_advice(
            incident_id="INC-020",
            threat_level=ThreatLevel.HIGH,
        )
        
        assert updated is not None
    
    def test_active_advisory_retrieval(self):
        """Test active advisory can be retrieved"""
        self.engine.get_tactical_advice(
            incident_id="INC-021",
            officer_id="RBPD-201",
            scenario=TacticalScenario.TRAFFIC_STOP,
        )
        
        advisory = self.engine.get_active_advisory("INC-021")
        assert advisory is not None
        assert advisory.incident_id == "INC-021"
    
    def test_advisory_history(self):
        """Test advisory history tracking"""
        self.engine.get_tactical_advice(
            incident_id="INC-022",
            officer_id="RBPD-201",
            scenario=TacticalScenario.TRAFFIC_STOP,
        )
        
        history = self.engine.get_advisory_history()
        assert len(history) > 0
    
    def test_incident_closure(self):
        """Test incident can be closed"""
        self.engine.get_tactical_advice(
            incident_id="INC-023",
            officer_id="RBPD-201",
            scenario=TacticalScenario.TRAFFIC_STOP,
        )
        
        result = self.engine.close_incident("INC-023")
        assert result
        
        advisory = self.engine.get_active_advisory("INC-023")
        assert advisory is None
    
    def test_scenario_protocol_retrieval(self):
        """Test scenario protocol retrieval"""
        protocol = self.engine.get_scenario_protocol(TacticalScenario.TRAFFIC_STOP)
        assert protocol is not None


class TestTacticalScenarioEnums:
    """Tests for tactical scenario enums"""
    
    def test_all_scenarios_exist(self):
        """Test all tactical scenarios exist"""
        assert TacticalScenario.TRAFFIC_STOP
        assert TacticalScenario.FELONY_STOP
        assert TacticalScenario.FOOT_PURSUIT
        assert TacticalScenario.VEHICLE_PURSUIT
        assert TacticalScenario.DOMESTIC_CALL
        assert TacticalScenario.SHOTS_FIRED
        assert TacticalScenario.BURGLARY_IN_PROGRESS
        assert TacticalScenario.ROBBERY_IN_PROGRESS
        assert TacticalScenario.ACTIVE_SHOOTER
        assert TacticalScenario.HOSTAGE_SITUATION
        assert TacticalScenario.BARRICADED_SUBJECT


class TestCoverTypeEnums:
    """Tests for cover type enums"""
    
    def test_all_cover_types_exist(self):
        """Test all cover types exist"""
        assert CoverType.HARD_COVER
        assert CoverType.SOFT_COVER
        assert CoverType.CONCEALMENT


class TestThreatLevelEnums:
    """Tests for threat level enums"""
    
    def test_all_threat_levels_exist(self):
        """Test all threat levels exist"""
        assert ThreatLevel.LOW
        assert ThreatLevel.MODERATE
        assert ThreatLevel.HIGH
        assert ThreatLevel.CRITICAL
