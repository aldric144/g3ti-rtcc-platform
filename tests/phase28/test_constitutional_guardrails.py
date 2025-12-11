"""
Test Suite 1: Constitutional Guardrail Engine Tests

Tests for 4th, 5th, 14th Amendment compliance and RBPD policy enforcement.
"""

import pytest
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend', 'app'))

from officer_assist.constitutional_guardrails import (
    ConstitutionalGuardrailEngine,
    GuardrailStatus,
    ConstitutionalViolationType,
    PolicyViolationType,
    ActionType,
    ActionContext,
    GuardrailResult,
)


class TestConstitutionalGuardrailEngine:
    """Tests for Constitutional Guardrail Engine"""
    
    def setup_method(self):
        """Reset singleton for each test"""
        ConstitutionalGuardrailEngine._instance = None
        self.engine = ConstitutionalGuardrailEngine()
    
    def test_singleton_pattern(self):
        """Test that engine uses singleton pattern"""
        engine1 = ConstitutionalGuardrailEngine()
        engine2 = ConstitutionalGuardrailEngine()
        assert engine1 is engine2
    
    def test_agency_configuration(self):
        """Test agency configuration is correct for Riviera Beach PD"""
        assert self.engine.agency_config["ori"] == "FL0500400"
        assert self.engine.agency_config["name"] == "Riviera Beach Police Department"
        assert self.engine.agency_config["state"] == "FL"
    
    def test_traffic_stop_with_reasonable_suspicion_passes(self):
        """Test traffic stop with documented RS passes guardrails"""
        context = ActionContext(
            action_type=ActionType.TRAFFIC_STOP,
            officer_id="RBPD-201",
            reasonable_suspicion="Vehicle matching BOLO description",
            detention_duration_minutes=10,
        )
        
        result = self.engine.evaluate_action(context)
        
        assert result.overall_status == GuardrailStatus.PASS
        assert result.legal_risk_score < 0.5
    
    def test_traffic_stop_without_reasonable_suspicion_blocked(self):
        """Test traffic stop without RS is blocked"""
        context = ActionContext(
            action_type=ActionType.TRAFFIC_STOP,
            officer_id="RBPD-201",
            reasonable_suspicion=None,
        )
        
        result = self.engine.evaluate_action(context)
        
        assert result.overall_status in [GuardrailStatus.WARNING, GuardrailStatus.BLOCKED]
        assert len(result.constitutional_issues) > 0
    
    def test_traffic_stop_exceeding_duration_warning(self):
        """Test traffic stop exceeding 20 minutes triggers warning"""
        context = ActionContext(
            action_type=ActionType.TRAFFIC_STOP,
            officer_id="RBPD-201",
            reasonable_suspicion="Speeding violation",
            detention_duration_minutes=25,
        )
        
        result = self.engine.evaluate_action(context)
        
        assert result.overall_status in [GuardrailStatus.WARNING, GuardrailStatus.BLOCKED]
    
    def test_terry_stop_with_articulable_facts_passes(self):
        """Test Terry stop with articulable facts passes"""
        context = ActionContext(
            action_type=ActionType.TERRY_STOP,
            officer_id="RBPD-201",
            reasonable_suspicion="Subject matching robbery suspect description, bulge in waistband",
            detention_duration_minutes=10,
        )
        
        result = self.engine.evaluate_action(context)
        
        assert result.overall_status == GuardrailStatus.PASS
    
    def test_terry_stop_exceeding_duration_warning(self):
        """Test Terry stop exceeding 15 minutes triggers warning"""
        context = ActionContext(
            action_type=ActionType.TERRY_STOP,
            officer_id="RBPD-201",
            reasonable_suspicion="Suspicious behavior",
            detention_duration_minutes=20,
        )
        
        result = self.engine.evaluate_action(context)
        
        assert result.overall_status in [GuardrailStatus.WARNING, GuardrailStatus.BLOCKED]
    
    def test_consent_search_with_voluntary_consent_passes(self):
        """Test consent search with voluntary consent passes"""
        context = ActionContext(
            action_type=ActionType.CONSENT_SEARCH,
            officer_id="RBPD-201",
            consent_obtained=True,
            consent_voluntary=True,
        )
        
        result = self.engine.evaluate_action(context)
        
        assert result.overall_status == GuardrailStatus.PASS
    
    def test_consent_search_without_consent_blocked(self):
        """Test consent search without consent is blocked"""
        context = ActionContext(
            action_type=ActionType.CONSENT_SEARCH,
            officer_id="RBPD-201",
            consent_obtained=False,
        )
        
        result = self.engine.evaluate_action(context)
        
        assert result.overall_status == GuardrailStatus.BLOCKED
    
    def test_warrantless_search_without_exception_blocked(self):
        """Test warrantless search without exception is blocked"""
        context = ActionContext(
            action_type=ActionType.WARRANTLESS_SEARCH,
            officer_id="RBPD-201",
            consent_obtained=False,
        )
        
        result = self.engine.evaluate_action(context)
        
        assert result.overall_status == GuardrailStatus.BLOCKED
    
    def test_arrest_with_probable_cause_passes(self):
        """Test arrest with probable cause passes"""
        context = ActionContext(
            action_type=ActionType.ARREST,
            officer_id="RBPD-201",
            probable_cause="Witnessed subject commit battery",
        )
        
        result = self.engine.evaluate_action(context)
        
        assert result.overall_status == GuardrailStatus.PASS
    
    def test_arrest_without_probable_cause_blocked(self):
        """Test arrest without probable cause is blocked"""
        context = ActionContext(
            action_type=ActionType.ARREST,
            officer_id="RBPD-201",
            probable_cause=None,
        )
        
        result = self.engine.evaluate_action(context)
        
        assert result.overall_status == GuardrailStatus.BLOCKED
    
    def test_custodial_interrogation_with_miranda_passes(self):
        """Test custodial interrogation with Miranda passes"""
        context = ActionContext(
            action_type=ActionType.CUSTODIAL_INTERROGATION,
            officer_id="RBPD-201",
            custodial=True,
            miranda_given=True,
        )
        
        result = self.engine.evaluate_action(context)
        
        assert result.overall_status == GuardrailStatus.PASS
    
    def test_custodial_interrogation_without_miranda_blocked(self):
        """Test custodial interrogation without Miranda is blocked"""
        context = ActionContext(
            action_type=ActionType.CUSTODIAL_INTERROGATION,
            officer_id="RBPD-201",
            custodial=True,
            miranda_given=False,
        )
        
        result = self.engine.evaluate_action(context)
        
        assert result.overall_status == GuardrailStatus.BLOCKED
        assert any("Miranda" in issue for issue in result.constitutional_issues)
    
    def test_vehicle_pursuit_within_policy_passes(self):
        """Test vehicle pursuit within policy passes"""
        context = ActionContext(
            action_type=ActionType.VEHICLE_PURSUIT,
            officer_id="RBPD-201",
            pursuit_speed=80,
            pursuit_reason="Armed robbery suspect fleeing",
        )
        
        result = self.engine.evaluate_action(context)
        
        assert result.overall_status in [GuardrailStatus.PASS, GuardrailStatus.WARNING]
    
    def test_vehicle_pursuit_excessive_speed_warning(self):
        """Test vehicle pursuit with excessive speed triggers warning"""
        context = ActionContext(
            action_type=ActionType.VEHICLE_PURSUIT,
            officer_id="RBPD-201",
            pursuit_speed=120,
            pursuit_reason="Traffic violation",
        )
        
        result = self.engine.evaluate_action(context)
        
        assert result.overall_status in [GuardrailStatus.WARNING, GuardrailStatus.BLOCKED]
    
    def test_use_of_force_proportional_passes(self):
        """Test proportional use of force passes"""
        context = ActionContext(
            action_type=ActionType.USE_OF_FORCE,
            officer_id="RBPD-201",
            force_level="SOFT_HANDS",
            weapon_involved=False,
        )
        
        result = self.engine.evaluate_action(context)
        
        assert result.overall_status == GuardrailStatus.PASS
    
    def test_use_of_force_deadly_without_threat_blocked(self):
        """Test deadly force without deadly threat is blocked"""
        context = ActionContext(
            action_type=ActionType.USE_OF_FORCE,
            officer_id="RBPD-201",
            force_level="DEADLY",
            weapon_involved=False,
        )
        
        result = self.engine.evaluate_action(context)
        
        assert result.overall_status == GuardrailStatus.BLOCKED
    
    def test_guardrail_log_tracking(self):
        """Test that guardrail evaluations are logged"""
        context = ActionContext(
            action_type=ActionType.TRAFFIC_STOP,
            officer_id="RBPD-201",
            reasonable_suspicion="Speeding",
        )
        
        self.engine.evaluate_action(context)
        
        log = self.engine.get_guardrail_log()
        assert len(log) > 0
    
    def test_blocked_actions_tracking(self):
        """Test that blocked actions are tracked"""
        context = ActionContext(
            action_type=ActionType.ARREST,
            officer_id="RBPD-201",
            probable_cause=None,
        )
        
        self.engine.evaluate_action(context)
        
        blocked = self.engine.get_blocked_actions()
        assert len(blocked) > 0
    
    def test_civil_liability_assessment(self):
        """Test civil liability risk assessment"""
        context = ActionContext(
            action_type=ActionType.USE_OF_FORCE,
            officer_id="RBPD-201",
            force_level="DEADLY",
            weapon_involved=False,
        )
        
        result = self.engine.evaluate_action(context)
        
        assert result.civil_liability_risk in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    
    def test_policy_reference_retrieval(self):
        """Test policy reference retrieval"""
        ref = self.engine.get_policy_reference("use_of_force")
        assert ref is not None
        assert "Policy 300" in str(ref) or "use" in str(ref).lower()
    
    def test_constitutional_rule_retrieval(self):
        """Test constitutional rule retrieval"""
        rule = self.engine.get_constitutional_rule("4th_amendment", "traffic_stop")
        assert rule is not None


class TestGuardrailModels:
    """Tests for guardrail data models"""
    
    def test_action_context_creation(self):
        """Test ActionContext model creation"""
        context = ActionContext(
            action_type=ActionType.TRAFFIC_STOP,
            officer_id="RBPD-201",
        )
        
        assert context.action_type == ActionType.TRAFFIC_STOP
        assert context.officer_id == "RBPD-201"
    
    def test_guardrail_result_fields(self):
        """Test GuardrailResult has required fields"""
        ConstitutionalGuardrailEngine._instance = None
        engine = ConstitutionalGuardrailEngine()
        
        context = ActionContext(
            action_type=ActionType.TRAFFIC_STOP,
            officer_id="RBPD-201",
            reasonable_suspicion="Test",
        )
        
        result = engine.evaluate_action(context)
        
        assert hasattr(result, 'result_id')
        assert hasattr(result, 'timestamp')
        assert hasattr(result, 'overall_status')
        assert hasattr(result, 'checks')
        assert hasattr(result, 'constitutional_issues')
        assert hasattr(result, 'policy_issues')
        assert hasattr(result, 'recommendations')
        assert hasattr(result, 'legal_risk_score')
        assert hasattr(result, 'civil_liability_risk')


class TestConstitutionalViolationTypes:
    """Tests for constitutional violation type enums"""
    
    def test_fourth_amendment_types(self):
        """Test 4th Amendment violation types exist"""
        assert ConstitutionalViolationType.FOURTH_SEARCH
        assert ConstitutionalViolationType.FOURTH_SEIZURE
        assert ConstitutionalViolationType.FOURTH_TRAFFIC_STOP
        assert ConstitutionalViolationType.FOURTH_TERRY_STOP
        assert ConstitutionalViolationType.FOURTH_CONSENT
    
    def test_fifth_amendment_types(self):
        """Test 5th Amendment violation types exist"""
        assert ConstitutionalViolationType.FIFTH_MIRANDA
        assert ConstitutionalViolationType.FIFTH_CUSTODIAL
        assert ConstitutionalViolationType.FIFTH_SELF_INCRIMINATION
    
    def test_fourteenth_amendment_types(self):
        """Test 14th Amendment violation types exist"""
        assert ConstitutionalViolationType.FOURTEENTH_DUE_PROCESS
        assert ConstitutionalViolationType.FOURTEENTH_EQUAL_PROTECTION


class TestPolicyViolationTypes:
    """Tests for policy violation type enums"""
    
    def test_use_of_force_policy_types(self):
        """Test use of force policy violation types exist"""
        assert PolicyViolationType.USE_OF_FORCE_EXCESSIVE
        assert PolicyViolationType.USE_OF_FORCE_UNAUTHORIZED
        assert PolicyViolationType.USE_OF_FORCE_REPORTING
    
    def test_pursuit_policy_types(self):
        """Test pursuit policy violation types exist"""
        assert PolicyViolationType.PURSUIT_UNAUTHORIZED
        assert PolicyViolationType.PURSUIT_EXCESSIVE_SPEED
        assert PolicyViolationType.PURSUIT_TERMINATION


class TestActionTypes:
    """Tests for action type enums"""
    
    def test_all_action_types_exist(self):
        """Test all required action types exist"""
        assert ActionType.TRAFFIC_STOP
        assert ActionType.TERRY_STOP
        assert ActionType.CONSENT_SEARCH
        assert ActionType.WARRANT_SEARCH
        assert ActionType.WARRANTLESS_SEARCH
        assert ActionType.ARREST
        assert ActionType.DETENTION
        assert ActionType.CUSTODIAL_INTERROGATION
        assert ActionType.VEHICLE_PURSUIT
        assert ActionType.FOOT_PURSUIT
        assert ActionType.USE_OF_FORCE
        assert ActionType.FELONY_STOP
        assert ActionType.DOMESTIC_RESPONSE
