"""
Test Suite 12: End-to-End Integration Tests

Tests for complete system integration across all Phase 28 components.
"""

import pytest
from datetime import datetime, timedelta
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend', 'app'))

from officer_assist.constitutional_guardrails import (
    ConstitutionalGuardrailEngine,
    GuardrailStatus,
    ActionType,
    ActionContext,
)
from officer_assist.use_of_force_monitor import (
    UseOfForceRiskMonitor,
    RiskLevel,
    SuspectBehaviorClass,
    SceneEscalationPattern,
    WeaponType,
)
from officer_assist.officer_behavioral_safety import (
    OfficerBehavioralSafetyEngine,
    FatigueLevel,
    OfficerWorkload,
)
from officer_assist.tactical_advisor import (
    TacticalAdvisorEngine,
    TacticalScenario,
    ThreatLevel,
)
from officer_assist.intent_interpreter import (
    OfficerIntentInterpreter,
    IntentType,
    InputSource,
)


class TestTrafficStopScenario:
    """End-to-end tests for traffic stop scenario"""
    
    def setup_method(self):
        """Reset all singletons for each test"""
        ConstitutionalGuardrailEngine._instance = None
        UseOfForceRiskMonitor._instance = None
        OfficerBehavioralSafetyEngine._instance = None
        TacticalAdvisorEngine._instance = None
        OfficerIntentInterpreter._instance = None
        
        self.guardrail_engine = ConstitutionalGuardrailEngine()
        self.force_monitor = UseOfForceRiskMonitor()
        self.safety_engine = OfficerBehavioralSafetyEngine()
        self.tactical_advisor = TacticalAdvisorEngine()
        self.intent_interpreter = OfficerIntentInterpreter()
    
    def test_traffic_stop_full_workflow(self):
        """Test complete traffic stop workflow"""
        officer_id = "RBPD-201"
        incident_id = "INC-2024-001"
        
        intent = self.intent_interpreter.interpret_input(
            officer_id=officer_id,
            raw_input="10-11 on Blue Honda Civic, Florida tag ABC123",
            input_source=InputSource.RADIO,
            incident_id=incident_id,
        )
        
        assert intent.intent_type == IntentType.TRAFFIC_STOP
        
        context = ActionContext(
            action_type=ActionType.TRAFFIC_STOP,
            officer_id=officer_id,
            incident_id=incident_id,
            reasonable_suspicion="Vehicle matching BOLO description",
        )
        
        guardrail_result = self.guardrail_engine.evaluate_action(context)
        
        assert guardrail_result.overall_status == GuardrailStatus.PASS
        
        force_assessment = self.force_monitor.assess_risk(
            incident_id=incident_id,
            officer_id=officer_id,
            suspect_behavior=SuspectBehaviorClass.COMPLIANT,
        )
        
        assert force_assessment.risk_level == RiskLevel.GREEN
        
        tactical_advice = self.tactical_advisor.get_tactical_advice(
            incident_id=incident_id,
            officer_id=officer_id,
            scenario=TacticalScenario.TRAFFIC_STOP,
        )
        
        assert tactical_advice is not None
        assert tactical_advice.primary_recommendation is not None
    
    def test_traffic_stop_escalation(self):
        """Test traffic stop with escalation"""
        officer_id = "RBPD-201"
        incident_id = "INC-2024-002"
        
        initial_assessment = self.force_monitor.assess_risk(
            incident_id=incident_id,
            officer_id=officer_id,
            suspect_behavior=SuspectBehaviorClass.COMPLIANT,
        )
        
        assert initial_assessment.risk_level == RiskLevel.GREEN
        
        escalated_assessment = self.force_monitor.update_assessment(
            incident_id=incident_id,
            suspect_behavior=SuspectBehaviorClass.ACTIVE_RESISTANT,
            escalation_pattern=SceneEscalationPattern.SLOWLY_ESCALATING,
        )
        
        assert escalated_assessment.risk_level in [RiskLevel.YELLOW, RiskLevel.RED]
        
        tactical_advice = self.tactical_advisor.get_tactical_advice(
            incident_id=incident_id,
            officer_id=officer_id,
            scenario=TacticalScenario.TRAFFIC_STOP,
            threat_level=ThreatLevel.MODERATE,
        )
        
        assert len(tactical_advice.de_escalation_options) > 0


class TestDomesticCallScenario:
    """End-to-end tests for domestic call scenario"""
    
    def setup_method(self):
        """Reset all singletons for each test"""
        ConstitutionalGuardrailEngine._instance = None
        UseOfForceRiskMonitor._instance = None
        TacticalAdvisorEngine._instance = None
        OfficerIntentInterpreter._instance = None
        
        self.guardrail_engine = ConstitutionalGuardrailEngine()
        self.force_monitor = UseOfForceRiskMonitor()
        self.tactical_advisor = TacticalAdvisorEngine()
        self.intent_interpreter = OfficerIntentInterpreter()
    
    def test_domestic_call_full_workflow(self):
        """Test complete domestic call workflow"""
        officer_id = "RBPD-205"
        incident_id = "INC-2024-003"
        
        intent = self.intent_interpreter.interpret_input(
            officer_id=officer_id,
            raw_input="10-16 at 123 Main Street",
            input_source=InputSource.RADIO,
            incident_id=incident_id,
        )
        
        assert intent.intent_type == IntentType.DOMESTIC_DISPUTE
        
        tactical_advice = self.tactical_advisor.get_tactical_advice(
            incident_id=incident_id,
            officer_id=officer_id,
            scenario=TacticalScenario.DOMESTIC_CALL,
        )
        
        assert tactical_advice is not None
        assert len(tactical_advice.de_escalation_options) > 0
        
        force_assessment = self.force_monitor.assess_risk(
            incident_id=incident_id,
            officer_id=officer_id,
            suspect_behavior=SuspectBehaviorClass.AGGRESSIVE,
        )
        
        assert force_assessment.risk_level in [RiskLevel.YELLOW, RiskLevel.RED]


class TestCustodialInterrogationScenario:
    """End-to-end tests for custodial interrogation scenario"""
    
    def setup_method(self):
        """Reset all singletons for each test"""
        ConstitutionalGuardrailEngine._instance = None
        OfficerIntentInterpreter._instance = None
        
        self.guardrail_engine = ConstitutionalGuardrailEngine()
        self.intent_interpreter = OfficerIntentInterpreter()
    
    def test_custodial_interrogation_without_miranda_blocked(self):
        """Test custodial interrogation without Miranda is blocked"""
        officer_id = "RBPD-210"
        incident_id = "INC-2024-004"
        
        intent = self.intent_interpreter.interpret_input(
            officer_id=officer_id,
            raw_input="Beginning custodial interview with suspect",
            input_source=InputSource.RADIO,
            incident_id=incident_id,
        )
        
        assert intent.intent_type == IntentType.CUSTODIAL_INTERROGATION
        assert intent.guardrail_triggered
        
        context = ActionContext(
            action_type=ActionType.CUSTODIAL_INTERROGATION,
            officer_id=officer_id,
            incident_id=incident_id,
            custodial=True,
            miranda_given=False,
        )
        
        guardrail_result = self.guardrail_engine.evaluate_action(context)
        
        assert guardrail_result.overall_status == GuardrailStatus.BLOCKED
        assert any("Miranda" in issue for issue in guardrail_result.constitutional_issues)
    
    def test_custodial_interrogation_with_miranda_passes(self):
        """Test custodial interrogation with Miranda passes"""
        officer_id = "RBPD-210"
        incident_id = "INC-2024-005"
        
        context = ActionContext(
            action_type=ActionType.CUSTODIAL_INTERROGATION,
            officer_id=officer_id,
            incident_id=incident_id,
            custodial=True,
            miranda_given=True,
        )
        
        guardrail_result = self.guardrail_engine.evaluate_action(context)
        
        assert guardrail_result.overall_status == GuardrailStatus.PASS


class TestOfficerFatigueScenario:
    """End-to-end tests for officer fatigue scenario"""
    
    def setup_method(self):
        """Reset all singletons for each test"""
        OfficerBehavioralSafetyEngine._instance = None
        UseOfForceRiskMonitor._instance = None
        
        self.safety_engine = OfficerBehavioralSafetyEngine()
        self.force_monitor = UseOfForceRiskMonitor()
    
    def test_fatigued_officer_high_risk_incident(self):
        """Test fatigued officer handling high-risk incident"""
        officer_id = "RBPD-215"
        incident_id = "INC-2024-006"
        
        workload = OfficerWorkload(
            officer_id=officer_id,
            shift_start=datetime.utcnow() - timedelta(hours=13),
            hours_on_duty=13,
            calls_handled=20,
            high_stress_calls=5,
            breaks_taken=0,
        )
        
        safety_status = self.safety_engine.assess_officer_safety(
            officer_id=officer_id,
            workload=workload,
        )
        
        assert safety_status.fatigue_level in [FatigueLevel.SEVERE, FatigueLevel.CRITICAL]
        assert safety_status.supervisor_review_required
        
        force_assessment = self.force_monitor.assess_risk(
            incident_id=incident_id,
            officer_id=officer_id,
            suspect_behavior=SuspectBehaviorClass.AGGRESSIVE,
        )
        
        assert force_assessment.risk_level in [RiskLevel.YELLOW, RiskLevel.RED]


class TestHighRiskIncidentScenario:
    """End-to-end tests for high-risk incident scenario"""
    
    def setup_method(self):
        """Reset all singletons for each test"""
        ConstitutionalGuardrailEngine._instance = None
        UseOfForceRiskMonitor._instance = None
        TacticalAdvisorEngine._instance = None
        OfficerIntentInterpreter._instance = None
        
        self.guardrail_engine = ConstitutionalGuardrailEngine()
        self.force_monitor = UseOfForceRiskMonitor()
        self.tactical_advisor = TacticalAdvisorEngine()
        self.intent_interpreter = OfficerIntentInterpreter()
    
    def test_armed_suspect_full_workflow(self):
        """Test armed suspect incident workflow"""
        officer_id = "RBPD-220"
        incident_id = "INC-2024-007"
        
        force_assessment = self.force_monitor.assess_risk(
            incident_id=incident_id,
            officer_id=officer_id,
            suspect_behavior=SuspectBehaviorClass.ASSAULTIVE,
            escalation_pattern=SceneEscalationPattern.RAPIDLY_ESCALATING,
            weapon_type=WeaponType.FIREARM,
            weapon_probability=0.85,
            officer_proximity_feet=25,
        )
        
        assert force_assessment.risk_level == RiskLevel.RED
        assert force_assessment.supervisor_notified
        assert force_assessment.backup_requested
        
        tactical_advice = self.tactical_advisor.get_tactical_advice(
            incident_id=incident_id,
            officer_id=officer_id,
            scenario=TacticalScenario.SHOTS_FIRED,
            threat_level=ThreatLevel.CRITICAL,
        )
        
        assert tactical_advice.lethal_cover_required
        assert len(tactical_advice.cover_positions) > 0
        assert len(tactical_advice.warnings) > 0


class TestConsentSearchScenario:
    """End-to-end tests for consent search scenario"""
    
    def setup_method(self):
        """Reset all singletons for each test"""
        ConstitutionalGuardrailEngine._instance = None
        OfficerIntentInterpreter._instance = None
        
        self.guardrail_engine = ConstitutionalGuardrailEngine()
        self.intent_interpreter = OfficerIntentInterpreter()
    
    def test_consent_search_workflow(self):
        """Test consent search workflow"""
        officer_id = "RBPD-225"
        incident_id = "INC-2024-008"
        
        intent = self.intent_interpreter.interpret_input(
            officer_id=officer_id,
            raw_input="Requesting consent to search vehicle",
            input_source=InputSource.RADIO,
            incident_id=incident_id,
        )
        
        assert intent.intent_type == IntentType.CONSENT_SEARCH
        assert intent.guardrail_triggered
        
        context_with_consent = ActionContext(
            action_type=ActionType.CONSENT_SEARCH,
            officer_id=officer_id,
            incident_id=incident_id,
            consent_obtained=True,
            consent_voluntary=True,
        )
        
        result_with_consent = self.guardrail_engine.evaluate_action(context_with_consent)
        
        assert result_with_consent.overall_status == GuardrailStatus.PASS
        
        ConstitutionalGuardrailEngine._instance = None
        engine2 = ConstitutionalGuardrailEngine()
        
        context_without_consent = ActionContext(
            action_type=ActionType.CONSENT_SEARCH,
            officer_id=officer_id,
            incident_id=incident_id,
            consent_obtained=False,
        )
        
        result_without_consent = engine2.evaluate_action(context_without_consent)
        
        assert result_without_consent.overall_status == GuardrailStatus.BLOCKED


class TestMultiOfficerIncident:
    """End-to-end tests for multi-officer incident"""
    
    def setup_method(self):
        """Reset all singletons for each test"""
        UseOfForceRiskMonitor._instance = None
        OfficerBehavioralSafetyEngine._instance = None
        TacticalAdvisorEngine._instance = None
        
        self.force_monitor = UseOfForceRiskMonitor()
        self.safety_engine = OfficerBehavioralSafetyEngine()
        self.tactical_advisor = TacticalAdvisorEngine()
    
    def test_multi_officer_response(self):
        """Test multi-officer response coordination"""
        incident_id = "INC-2024-009"
        officers = ["RBPD-201", "RBPD-205", "RBPD-210"]
        
        for officer_id in officers:
            self.safety_engine.assess_officer_safety(officer_id=officer_id)
        
        tactical_advice = self.tactical_advisor.get_tactical_advice(
            incident_id=incident_id,
            officer_id=officers[0],
            scenario=TacticalScenario.FELONY_STOP,
            threat_level=ThreatLevel.HIGH,
        )
        
        assert len(tactical_advice.backup_units) > 0
        assert tactical_advice.communication_plan is not None


class TestSystemIntegration:
    """Tests for overall system integration"""
    
    def setup_method(self):
        """Reset all singletons for each test"""
        ConstitutionalGuardrailEngine._instance = None
        UseOfForceRiskMonitor._instance = None
        OfficerBehavioralSafetyEngine._instance = None
        TacticalAdvisorEngine._instance = None
        OfficerIntentInterpreter._instance = None
    
    def test_all_engines_initialize(self):
        """Test all engines initialize correctly"""
        guardrail_engine = ConstitutionalGuardrailEngine()
        force_monitor = UseOfForceRiskMonitor()
        safety_engine = OfficerBehavioralSafetyEngine()
        tactical_advisor = TacticalAdvisorEngine()
        intent_interpreter = OfficerIntentInterpreter()
        
        assert guardrail_engine is not None
        assert force_monitor is not None
        assert safety_engine is not None
        assert tactical_advisor is not None
        assert intent_interpreter is not None
    
    def test_all_engines_share_agency_config(self):
        """Test all engines share same agency configuration"""
        guardrail_engine = ConstitutionalGuardrailEngine()
        force_monitor = UseOfForceRiskMonitor()
        safety_engine = OfficerBehavioralSafetyEngine()
        tactical_advisor = TacticalAdvisorEngine()
        intent_interpreter = OfficerIntentInterpreter()
        
        ori = "FL0500400"
        
        assert guardrail_engine.agency_config["ori"] == ori
        assert force_monitor.agency_config["ori"] == ori
        assert safety_engine.agency_config["ori"] == ori
        assert tactical_advisor.agency_config["ori"] == ori
        assert intent_interpreter.agency_config["ori"] == ori
    
    def test_statistics_collection(self):
        """Test statistics collection across all engines"""
        guardrail_engine = ConstitutionalGuardrailEngine()
        force_monitor = UseOfForceRiskMonitor()
        safety_engine = OfficerBehavioralSafetyEngine()
        intent_interpreter = OfficerIntentInterpreter()
        
        context = ActionContext(
            action_type=ActionType.TRAFFIC_STOP,
            officer_id="RBPD-201",
            reasonable_suspicion="Test",
        )
        guardrail_engine.evaluate_action(context)
        
        force_monitor.assess_risk(
            incident_id="INC-001",
            officer_id="RBPD-201",
            suspect_behavior=SuspectBehaviorClass.COMPLIANT,
        )
        
        safety_engine.assess_officer_safety(officer_id="RBPD-201")
        
        intent_interpreter.interpret_input(
            officer_id="RBPD-201",
            raw_input="10-11 traffic stop",
            input_source=InputSource.RADIO,
        )
        
        guardrail_log = guardrail_engine.get_guardrail_log()
        force_stats = force_monitor.get_risk_statistics()
        safety_stats = safety_engine.get_safety_statistics()
        intent_stats = intent_interpreter.get_statistics()
        
        assert len(guardrail_log) > 0
        assert force_stats["total_assessments"] > 0
        assert safety_stats["officers_monitored"] > 0
        assert intent_stats["total_interpretations"] > 0
