"""
Test Suite 5: Officer Intent Interpreter Tests

Tests for intent detection from radio, MDT, and voice inputs.
"""

import pytest
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend', 'app'))

from officer_assist.intent_interpreter import (
    OfficerIntentInterpreter,
    IntentType,
    IntentConfidence,
    InputSource,
    OfficerIntent,
)


class TestOfficerIntentInterpreter:
    """Tests for Officer Intent Interpreter"""
    
    def setup_method(self):
        """Reset singleton for each test"""
        OfficerIntentInterpreter._instance = None
        self.interpreter = OfficerIntentInterpreter()
    
    def test_singleton_pattern(self):
        """Test that interpreter uses singleton pattern"""
        interpreter1 = OfficerIntentInterpreter()
        interpreter2 = OfficerIntentInterpreter()
        assert interpreter1 is interpreter2
    
    def test_agency_configuration(self):
        """Test agency configuration is correct"""
        assert self.interpreter.agency_config["ori"] == "FL0500400"
        assert self.interpreter.agency_config["name"] == "Riviera Beach Police Department"
    
    def test_traffic_stop_detection_ten_code(self):
        """Test traffic stop detection from 10-11 code"""
        intent = self.interpreter.interpret_input(
            officer_id="RBPD-201",
            raw_input="10-11 on Blue Honda Civic, Florida tag ABC123",
            input_source=InputSource.RADIO,
        )
        
        assert intent.intent_type == IntentType.TRAFFIC_STOP
        assert intent.confidence in [IntentConfidence.HIGH, IntentConfidence.VERY_HIGH]
    
    def test_traffic_stop_detection_natural_language(self):
        """Test traffic stop detection from natural language"""
        intent = self.interpreter.interpret_input(
            officer_id="RBPD-201",
            raw_input="Initiating traffic stop on white pickup truck",
            input_source=InputSource.RADIO,
        )
        
        assert intent.intent_type == IntentType.TRAFFIC_STOP
    
    def test_consent_search_detection(self):
        """Test consent search detection"""
        intent = self.interpreter.interpret_input(
            officer_id="RBPD-201",
            raw_input="Requesting consent to search vehicle",
            input_source=InputSource.RADIO,
        )
        
        assert intent.intent_type == IntentType.CONSENT_SEARCH
    
    def test_terry_stop_detection(self):
        """Test Terry stop detection"""
        intent = self.interpreter.interpret_input(
            officer_id="RBPD-201",
            raw_input="Conducting investigative stop on suspicious person",
            input_source=InputSource.RADIO,
        )
        
        assert intent.intent_type == IntentType.TERRY_STOP
    
    def test_arrest_detection(self):
        """Test arrest detection from 10-15"""
        intent = self.interpreter.interpret_input(
            officer_id="RBPD-201",
            raw_input="10-15 one in custody",
            input_source=InputSource.RADIO,
        )
        
        assert intent.intent_type == IntentType.ARREST
    
    def test_vehicle_pursuit_detection(self):
        """Test vehicle pursuit detection from 10-80"""
        intent = self.interpreter.interpret_input(
            officer_id="RBPD-201",
            raw_input="10-80 northbound on Blue Heron",
            input_source=InputSource.RADIO,
        )
        
        assert intent.intent_type == IntentType.VEHICLE_PURSUIT
    
    def test_foot_pursuit_detection(self):
        """Test foot pursuit detection"""
        intent = self.interpreter.interpret_input(
            officer_id="RBPD-201",
            raw_input="In foot pursuit of suspect heading east",
            input_source=InputSource.RADIO,
        )
        
        assert intent.intent_type == IntentType.FOOT_PURSUIT
    
    def test_domestic_dispute_detection(self):
        """Test domestic dispute detection from 10-16"""
        intent = self.interpreter.interpret_input(
            officer_id="RBPD-201",
            raw_input="10-16 at 123 Main Street",
            input_source=InputSource.RADIO,
        )
        
        assert intent.intent_type == IntentType.DOMESTIC_DISPUTE
    
    def test_felony_stop_detection(self):
        """Test felony stop detection"""
        intent = self.interpreter.interpret_input(
            officer_id="RBPD-201",
            raw_input="Conducting felony stop on vehicle matching BOLO",
            input_source=InputSource.RADIO,
        )
        
        assert intent.intent_type == IntentType.FELONY_STOP
    
    def test_use_of_force_detection(self):
        """Test use of force detection"""
        intent = self.interpreter.interpret_input(
            officer_id="RBPD-201",
            raw_input="Taser deployed, subject in custody",
            input_source=InputSource.RADIO,
        )
        
        assert intent.intent_type == IntentType.USE_OF_FORCE
    
    def test_miranda_advisement_detection(self):
        """Test Miranda advisement detection"""
        intent = self.interpreter.interpret_input(
            officer_id="RBPD-201",
            raw_input="Advising Miranda rights to subject",
            input_source=InputSource.RADIO,
        )
        
        assert intent.intent_type == IntentType.MIRANDA_ADVISEMENT
    
    def test_custodial_interrogation_detection(self):
        """Test custodial interrogation detection"""
        intent = self.interpreter.interpret_input(
            officer_id="RBPD-201",
            raw_input="Beginning custodial interview with suspect",
            input_source=InputSource.RADIO,
        )
        
        assert intent.intent_type == IntentType.CUSTODIAL_INTERROGATION
    
    def test_emergency_detection(self):
        """Test emergency detection from 10-33"""
        intent = self.interpreter.interpret_input(
            officer_id="RBPD-201",
            raw_input="10-33 emergency, shots fired",
            input_source=InputSource.RADIO,
        )
        
        assert intent.intent_type == IntentType.EMERGENCY
        assert intent.priority == "HIGH"
    
    def test_assistance_needed_detection(self):
        """Test assistance needed detection from 10-78"""
        intent = self.interpreter.interpret_input(
            officer_id="RBPD-201",
            raw_input="10-78 need assistance",
            input_source=InputSource.RADIO,
        )
        
        assert intent.intent_type == IntentType.ASSISTANCE_NEEDED
        assert intent.priority == "HIGH"
    
    def test_entity_extraction_vehicle(self):
        """Test vehicle entity extraction"""
        intent = self.interpreter.interpret_input(
            officer_id="RBPD-201",
            raw_input="10-11 on Blue Honda Civic, Florida tag ABC123",
            input_source=InputSource.RADIO,
        )
        
        assert "vehicle" in intent.entities or "tag" in intent.entities
    
    def test_entity_extraction_location(self):
        """Test location entity extraction"""
        intent = self.interpreter.interpret_input(
            officer_id="RBPD-201",
            raw_input="10-16 at 123 Main Street",
            input_source=InputSource.RADIO,
        )
        
        assert "location" in intent.entities or "address" in intent.entities
    
    def test_guardrail_trigger_for_high_risk_intent(self):
        """Test guardrail trigger for high-risk intents"""
        intent = self.interpreter.interpret_input(
            officer_id="RBPD-201",
            raw_input="Conducting consent search of vehicle",
            input_source=InputSource.RADIO,
        )
        
        assert intent.guardrail_triggered
    
    def test_guardrail_trigger_for_custodial_interrogation(self):
        """Test guardrail trigger for custodial interrogation"""
        intent = self.interpreter.interpret_input(
            officer_id="RBPD-201",
            raw_input="Beginning custodial interview",
            input_source=InputSource.RADIO,
        )
        
        assert intent.guardrail_triggered
    
    def test_mdt_input_source(self):
        """Test MDT input source processing"""
        intent = self.interpreter.interpret_input(
            officer_id="RBPD-201",
            raw_input="Traffic stop initiated",
            input_source=InputSource.MDT,
        )
        
        assert intent.input_source == InputSource.MDT
    
    def test_voice_input_source(self):
        """Test voice input source processing"""
        intent = self.interpreter.interpret_input(
            officer_id="RBPD-201",
            raw_input="I'm making a traffic stop",
            input_source=InputSource.VOICE,
        )
        
        assert intent.input_source == InputSource.VOICE
    
    def test_cad_input_source(self):
        """Test CAD input source processing"""
        intent = self.interpreter.interpret_input(
            officer_id="RBPD-201",
            raw_input="Unit assigned to domestic call",
            input_source=InputSource.CAD,
        )
        
        assert intent.input_source == InputSource.CAD
    
    def test_intent_history_tracking(self):
        """Test intent history is tracked"""
        self.interpreter.interpret_input(
            officer_id="RBPD-201",
            raw_input="10-11 traffic stop",
            input_source=InputSource.RADIO,
        )
        
        history = self.interpreter.get_intent_history()
        assert len(history) > 0
    
    def test_incident_intents_retrieval(self):
        """Test incident intents can be retrieved"""
        self.interpreter.interpret_input(
            officer_id="RBPD-201",
            raw_input="10-11 traffic stop",
            input_source=InputSource.RADIO,
            incident_id="INC-001",
        )
        
        intents = self.interpreter.get_incident_intents("INC-001")
        assert len(intents) > 0
    
    def test_high_priority_intents_retrieval(self):
        """Test high priority intents can be retrieved"""
        self.interpreter.interpret_input(
            officer_id="RBPD-201",
            raw_input="10-33 emergency",
            input_source=InputSource.RADIO,
        )
        
        intents = self.interpreter.get_high_priority_intents()
        assert len(intents) > 0
    
    def test_guardrail_triggered_intents_retrieval(self):
        """Test guardrail triggered intents can be retrieved"""
        self.interpreter.interpret_input(
            officer_id="RBPD-201",
            raw_input="Conducting consent search",
            input_source=InputSource.RADIO,
        )
        
        intents = self.interpreter.get_guardrail_triggered_intents()
        assert len(intents) > 0
    
    def test_ten_code_meaning_retrieval(self):
        """Test ten code meaning retrieval"""
        meaning = self.interpreter.get_ten_code_meaning("10-11")
        assert meaning is not None
        assert "traffic" in meaning.lower()
    
    def test_statistics(self):
        """Test statistics calculation"""
        self.interpreter.interpret_input(
            officer_id="RBPD-201",
            raw_input="10-11 traffic stop",
            input_source=InputSource.RADIO,
        )
        
        stats = self.interpreter.get_statistics()
        assert "total_interpretations" in stats
        assert "by_intent_type" in stats


class TestIntentTypeEnums:
    """Tests for intent type enums"""
    
    def test_all_intent_types_exist(self):
        """Test all intent types exist"""
        assert IntentType.TRAFFIC_STOP
        assert IntentType.CONSENT_SEARCH
        assert IntentType.TERRY_STOP
        assert IntentType.ARREST
        assert IntentType.VEHICLE_PURSUIT
        assert IntentType.FOOT_PURSUIT
        assert IntentType.DOMESTIC_DISPUTE
        assert IntentType.FELONY_STOP
        assert IntentType.USE_OF_FORCE
        assert IntentType.MIRANDA_ADVISEMENT
        assert IntentType.CUSTODIAL_INTERROGATION
        assert IntentType.EMERGENCY
        assert IntentType.ASSISTANCE_NEEDED


class TestIntentConfidenceEnums:
    """Tests for intent confidence enums"""
    
    def test_all_confidence_levels_exist(self):
        """Test all confidence levels exist"""
        assert IntentConfidence.LOW
        assert IntentConfidence.MEDIUM
        assert IntentConfidence.HIGH
        assert IntentConfidence.VERY_HIGH


class TestInputSourceEnums:
    """Tests for input source enums"""
    
    def test_all_input_sources_exist(self):
        """Test all input sources exist"""
        assert InputSource.RADIO
        assert InputSource.MDT
        assert InputSource.VOICE
        assert InputSource.CAD
        assert InputSource.BODY_CAMERA
