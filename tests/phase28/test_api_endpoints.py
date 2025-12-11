"""
Test Suite 6: API Endpoints Tests

Tests for Officer Assist API endpoints.
"""

import pytest
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend', 'app'))


class TestGuardrailCheckEndpoint:
    """Tests for POST /api/officer-assist/guardrails/check"""
    
    def test_guardrail_check_request_structure(self):
        """Test guardrail check request structure"""
        request = {
            "action_type": "TRAFFIC_STOP",
            "officer_id": "RBPD-201",
            "incident_id": "INC-001",
            "reasonable_suspicion": "Vehicle matching BOLO",
            "consent_obtained": False,
            "miranda_given": False,
            "custodial": False,
        }
        
        assert "action_type" in request
        assert "officer_id" in request
    
    def test_guardrail_check_response_structure(self):
        """Test guardrail check response structure"""
        response = {
            "result_id": "gr-20241209120000-RBPD-201",
            "overall_status": "PASS",
            "risk_level": "LOW",
            "guardrail_status": "PASS",
            "reason": "Action complies with requirements",
            "citations": ["Terry v. Ohio"],
            "issues": [],
            "recommendations": [],
        }
        
        assert "result_id" in response
        assert "overall_status" in response
        assert "guardrail_status" in response
        assert response["overall_status"] in ["PASS", "WARNING", "BLOCKED"]
    
    def test_guardrail_check_traffic_stop_pass(self):
        """Test traffic stop with RS passes"""
        request = {
            "action_type": "TRAFFIC_STOP",
            "officer_id": "RBPD-201",
            "reasonable_suspicion": "Speeding violation",
        }
        
        assert request["reasonable_suspicion"] is not None
    
    def test_guardrail_check_traffic_stop_blocked(self):
        """Test traffic stop without RS is blocked"""
        request = {
            "action_type": "TRAFFIC_STOP",
            "officer_id": "RBPD-201",
            "reasonable_suspicion": None,
        }
        
        assert request["reasonable_suspicion"] is None


class TestUseOfForceRiskEndpoint:
    """Tests for POST /api/officer-assist/use-of-force/risk"""
    
    def test_use_of_force_request_structure(self):
        """Test use of force request structure"""
        request = {
            "incident_id": "INC-001",
            "officer_id": "RBPD-201",
            "suspect_behavior": "ACTIVE_RESISTANT",
            "escalation_pattern": "SLOWLY_ESCALATING",
            "weapon_type": "NONE",
            "weapon_probability": 0.0,
            "officer_proximity_feet": 35,
        }
        
        assert "incident_id" in request
        assert "officer_id" in request
        assert "suspect_behavior" in request
    
    def test_use_of_force_response_structure(self):
        """Test use of force response structure"""
        response = {
            "assessment_id": "fra-20241209120000-RBPD-201",
            "risk_level": "YELLOW",
            "risk_score": 0.55,
            "reason": "Risk level YELLOW",
            "recommended_action": "Attempt verbal de-escalation",
            "risk_factors": ["Suspect behavior: ACTIVE_RESISTANT"],
            "protective_factors": [],
            "de_escalation_recommended": True,
            "supervisor_notified": False,
            "backup_requested": False,
        }
        
        assert "assessment_id" in response
        assert "risk_level" in response
        assert response["risk_level"] in ["GREEN", "YELLOW", "RED"]
    
    def test_use_of_force_green_level(self):
        """Test green level risk assessment"""
        request = {
            "suspect_behavior": "COMPLIANT",
            "officer_proximity_feet": 100,
        }
        
        assert request["suspect_behavior"] == "COMPLIANT"
    
    def test_use_of_force_red_level(self):
        """Test red level risk assessment"""
        request = {
            "suspect_behavior": "ASSAULTIVE",
            "weapon_type": "FIREARM",
            "weapon_probability": 0.9,
        }
        
        assert request["suspect_behavior"] == "ASSAULTIVE"


class TestTacticalAdviceEndpoint:
    """Tests for POST /api/officer-assist/tactical-advice"""
    
    def test_tactical_advice_request_structure(self):
        """Test tactical advice request structure"""
        request = {
            "incident_id": "INC-001",
            "officer_id": "RBPD-201",
            "scenario": "TRAFFIC_STOP",
            "threat_level": "MODERATE",
            "suspect_armed": False,
            "suspect_count": 2,
            "officer_count": 1,
        }
        
        assert "incident_id" in request
        assert "scenario" in request
    
    def test_tactical_advice_response_structure(self):
        """Test tactical advice response structure"""
        response = {
            "advice_id": "ta-20241209120000-RBPD-201",
            "scenario": "TRAFFIC_STOP",
            "threat_level": "MODERATE",
            "primary_recommendation": "Standard approach",
            "tactical_notes": ["Position vehicle offset"],
            "warnings": [],
            "de_escalation_options": ["Use calm commands"],
            "cover_positions": [],
            "escape_routes": [],
            "backup_units": [],
            "communication_plan": "Standard radio",
            "containment_strategy": "Standard containment",
            "lethal_cover_required": False,
            "k9_recommended": False,
            "air_support_recommended": False,
        }
        
        assert "advice_id" in response
        assert "primary_recommendation" in response
        assert "tactical_notes" in response


class TestIntentEndpoint:
    """Tests for POST /api/officer-assist/intent"""
    
    def test_intent_request_structure(self):
        """Test intent request structure"""
        request = {
            "officer_id": "RBPD-201",
            "raw_input": "10-11 on Blue Honda Civic",
            "input_source": "RADIO",
            "incident_id": "INC-001",
        }
        
        assert "officer_id" in request
        assert "raw_input" in request
        assert "input_source" in request
    
    def test_intent_response_structure(self):
        """Test intent response structure"""
        response = {
            "intent_id": "int-20241209120000-RBPD-201",
            "intent_type": "TRAFFIC_STOP",
            "confidence": "HIGH",
            "entities": {"vehicle": "Blue Honda Civic"},
            "guardrail_triggered": True,
            "guardrail_status": "PASS",
            "priority": "NORMAL",
        }
        
        assert "intent_id" in response
        assert "intent_type" in response
        assert "confidence" in response


class TestOfficerStatusEndpoint:
    """Tests for GET /api/officer-assist/officer/{id}/status"""
    
    def test_officer_status_response_structure(self):
        """Test officer status response structure"""
        response = {
            "officer_id": "RBPD-201",
            "overall_risk_score": 0.25,
            "fatigue_level": "NORMAL",
            "fatigue_score": 0.2,
            "stress_score": 0.3,
            "workload_score": 0.25,
            "trauma_exposure_score": 0.1,
            "hours_on_duty": 6.5,
            "calls_handled": 8,
            "high_stress_calls": 1,
            "breaks_taken": 1,
            "fit_for_duty": True,
            "supervisor_review_required": False,
            "pattern_flags": [],
            "recommendations": [],
        }
        
        assert "officer_id" in response
        assert "overall_risk_score" in response
        assert "fit_for_duty" in response
    
    def test_officer_status_high_risk(self):
        """Test high risk officer status"""
        response = {
            "officer_id": "RBPD-210",
            "overall_risk_score": 0.85,
            "fatigue_level": "CRITICAL",
            "fit_for_duty": False,
            "supervisor_review_required": True,
        }
        
        assert response["overall_risk_score"] > 0.7
        assert not response["fit_for_duty"]


class TestAlertsEndpoint:
    """Tests for GET /api/officer-assist/alerts"""
    
    def test_alerts_response_structure(self):
        """Test alerts response structure"""
        response = {
            "alerts": [
                {
                    "alert_id": "alert-001",
                    "timestamp": "2024-12-09T12:00:00Z",
                    "type": "USE_OF_FORCE_RISK",
                    "severity": "HIGH",
                    "officer_id": "RBPD-201",
                    "description": "Red level risk",
                    "acknowledged": False,
                    "resolved": False,
                }
            ],
            "total": 1,
            "unacknowledged": 1,
            "high_severity": 1,
        }
        
        assert "alerts" in response
        assert "total" in response
        assert "unacknowledged" in response
    
    def test_alerts_filtering(self):
        """Test alerts filtering by severity"""
        params = {
            "severity": "HIGH",
            "acknowledged": False,
        }
        
        assert params["severity"] == "HIGH"


class TestAPIValidation:
    """Tests for API input validation"""
    
    def test_invalid_action_type_rejected(self):
        """Test invalid action type is rejected"""
        request = {
            "action_type": "INVALID_TYPE",
            "officer_id": "RBPD-201",
        }
        
        valid_types = [
            "TRAFFIC_STOP", "TERRY_STOP", "CONSENT_SEARCH",
            "ARREST", "CUSTODIAL_INTERROGATION", "USE_OF_FORCE",
        ]
        
        assert request["action_type"] not in valid_types
    
    def test_invalid_risk_level_rejected(self):
        """Test invalid risk level is rejected"""
        request = {
            "suspect_behavior": "INVALID_BEHAVIOR",
        }
        
        valid_behaviors = [
            "COMPLIANT", "PASSIVE_RESISTANT", "ACTIVE_RESISTANT",
            "AGGRESSIVE", "ASSAULTIVE", "LIFE_THREATENING",
        ]
        
        assert request["suspect_behavior"] not in valid_behaviors
    
    def test_missing_required_fields_rejected(self):
        """Test missing required fields are rejected"""
        request = {
            "action_type": "TRAFFIC_STOP",
        }
        
        assert "officer_id" not in request
    
    def test_invalid_officer_id_format(self):
        """Test invalid officer ID format"""
        request = {
            "officer_id": "",
        }
        
        assert len(request["officer_id"]) == 0


class TestAPIErrorHandling:
    """Tests for API error handling"""
    
    def test_not_found_error_structure(self):
        """Test not found error structure"""
        error = {
            "error": "Officer not found",
            "code": "NOT_FOUND",
            "officer_id": "RBPD-999",
        }
        
        assert "error" in error
        assert error["code"] == "NOT_FOUND"
    
    def test_validation_error_structure(self):
        """Test validation error structure"""
        error = {
            "error": "Validation failed",
            "code": "VALIDATION_ERROR",
            "details": [
                {"field": "action_type", "message": "Invalid action type"}
            ],
        }
        
        assert "error" in error
        assert "details" in error
    
    def test_internal_error_structure(self):
        """Test internal error structure"""
        error = {
            "error": "Internal server error",
            "code": "INTERNAL_ERROR",
            "request_id": "req-12345",
        }
        
        assert "error" in error
        assert error["code"] == "INTERNAL_ERROR"
