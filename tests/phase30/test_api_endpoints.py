"""
Phase 30: API Endpoint Tests

Tests for:
- Mental health check endpoint
- Suicide risk endpoint
- DV escalation endpoint
- Crisis routing endpoint
- Youth risk endpoint
- Stability map endpoint
- Community pulse endpoint
"""

import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock, AsyncMock
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))


class TestMentalHealthCheckEndpoint:
    """Tests for mental health check endpoint"""
    
    def test_mental_health_check_request_model(self):
        """Test MentalHealthCheckRequest model"""
        from backend.app.api.human_intel.human_intel_router import MentalHealthCheckRequest
        
        request = MentalHealthCheckRequest(
            call_narrative="Test narrative",
            call_type="welfare_check",
            zone="Zone_A",
        )
        
        assert request.call_narrative == "Test narrative"
        assert request.call_type == "welfare_check"
    
    def test_mental_health_check_response_model(self):
        """Test MentalHealthCheckResponse model"""
        from backend.app.api.human_intel.human_intel_router import MentalHealthCheckResponse
        
        response = MentalHealthCheckResponse(
            check_id="MHC-001",
            timestamp=datetime.utcnow().isoformat(),
            risk_level="LOW",
            confidence_score=0.75,
            recommended_actions=["Standard response"],
            anonymization_level="FULL",
            privacy_protections=["No PII stored"],
            chain_of_custody_hash="abc123",
        )
        
        assert response.check_id == "MHC-001"
        assert response.risk_level == "LOW"


class TestSuicideRiskEndpoint:
    """Tests for suicide risk endpoint"""
    
    def test_suicide_risk_request_model(self):
        """Test SuicideRiskRequest model"""
        from backend.app.api.human_intel.human_intel_router import SuicideRiskRequest
        
        request = SuicideRiskRequest(
            call_narrative="Subject threatening suicide",
            caller_type="family",
            prior_welfare_checks=2,
            prior_crisis_calls=1,
        )
        
        assert request.call_narrative == "Subject threatening suicide"
        assert request.prior_welfare_checks == 2
    
    def test_suicide_risk_response_model(self):
        """Test SuicideRiskResponse model"""
        from backend.app.api.human_intel.human_intel_router import SuicideRiskResponse
        
        response = SuicideRiskResponse(
            assessment_id="SR-001",
            timestamp=datetime.utcnow().isoformat(),
            risk_level="HIGH",
            confidence_score=0.85,
            crisis_phrases_detected=["want to die"],
            recommended_actions=["Dispatch crisis team"],
            auto_alert_triggered=True,
            anonymization_level="FULL",
            privacy_protections=["No PII stored"],
            chain_of_custody_hash="abc123",
        )
        
        assert response.assessment_id == "SR-001"
        assert response.risk_level == "HIGH"
        assert response.auto_alert_triggered == True


class TestDVEscalationEndpoint:
    """Tests for DV escalation endpoint"""
    
    def test_dv_escalation_request_model(self):
        """Test DVEscalationRequest model"""
        from backend.app.api.human_intel.human_intel_router import DVEscalationRequest
        
        request = DVEscalationRequest(
            incident_narrative="DV incident",
            repeat_call_count=3,
            alcohol_involved=True,
            weapons_present=True,
        )
        
        assert request.incident_narrative == "DV incident"
        assert request.repeat_call_count == 3
    
    def test_dv_escalation_response_model(self):
        """Test DVEscalationResponse model"""
        from backend.app.api.human_intel.human_intel_router import DVEscalationResponse
        
        response = DVEscalationResponse(
            assessment_id="DV-001",
            timestamp=datetime.utcnow().isoformat(),
            escalation_level="HIGH",
            lethality_risk_score=0.65,
            campbell_danger_indicators=["weapon_in_home"],
            intervention_pathway="ENHANCED_RESPONSE",
            recommended_actions=["Priority dispatch"],
            anonymization_level="FULL",
            privacy_protections=["Victim identity protected"],
            chain_of_custody_hash="abc123",
        )
        
        assert response.assessment_id == "DV-001"
        assert response.lethality_risk_score == 0.65


class TestCrisisRouteEndpoint:
    """Tests for crisis routing endpoint"""
    
    def test_crisis_route_request_model(self):
        """Test CrisisRouteRequest model"""
        from backend.app.api.human_intel.human_intel_router import CrisisRouteRequest
        
        request = CrisisRouteRequest(
            call_narrative="Crisis call",
            call_type="mental_health",
            weapons_mentioned=False,
            violence_mentioned=False,
        )
        
        assert request.call_narrative == "Crisis call"
        assert request.call_type == "mental_health"
    
    def test_crisis_route_response_model(self):
        """Test CrisisRouteResponse model"""
        from backend.app.api.human_intel.human_intel_router import CrisisRouteResponse
        
        response = CrisisRouteResponse(
            decision_id="CRD-001",
            timestamp=datetime.utcnow().isoformat(),
            call_type="mental_health",
            priority="URGENT",
            primary_responder="crisis_intervention_team",
            co_responders=["mental_health_clinician"],
            de_escalation_prompts=["Use calm tone"],
            recommended_actions=["Dispatch CIT"],
            risk_level="MODERATE",
            anonymization_level="FULL",
            privacy_protections=["No PII stored"],
        )
        
        assert response.decision_id == "CRD-001"
        assert response.priority == "URGENT"


class TestYouthRiskEndpoint:
    """Tests for youth risk endpoint"""
    
    def test_youth_risk_request_model(self):
        """Test YouthRiskRequest model"""
        from backend.app.api.human_intel.human_intel_router import YouthRiskRequest
        
        request = YouthRiskRequest(
            school_zone="Zone_A",
            age_group="middle_school",
            incident_history=["prior_incident"],
        )
        
        assert request.school_zone == "Zone_A"
        assert request.age_group == "middle_school"
    
    def test_youth_risk_response_model(self):
        """Test YouthRiskResponse model"""
        from backend.app.api.human_intel.human_intel_router import YouthRiskResponse
        
        response = YouthRiskResponse(
            assessment_id="YRA-001",
            timestamp=datetime.utcnow().isoformat(),
            risk_level="ELEVATED",
            risk_types=["truancy"],
            recommended_interventions=["school_counselor"],
            urgency="URGENT",
            anonymization_level="FULL",
            privacy_protections=["FERPA protections applied"],
            chain_of_custody_hash="abc123",
        )
        
        assert response.assessment_id == "YRA-001"
        assert response.risk_level == "ELEVATED"


class TestStabilityMapEndpoint:
    """Tests for stability map endpoint"""
    
    def test_stability_map_response_model(self):
        """Test StabilityMapResponse model"""
        from backend.app.api.human_intel.human_intel_router import StabilityMapResponse
        
        response = StabilityMapResponse(
            map_id="SM-001",
            timestamp=datetime.utcnow().isoformat(),
            overall_stability_score=74.5,
            mental_health_score=72.0,
            violence_score=78.0,
            community_cohesion_score=70.0,
            youth_stability_score=68.0,
            high_risk_areas=[],
            trend_7_day=0.5,
            trend_30_day=1.2,
            anonymization_level="AGGREGATED",
            privacy_protections=["All data aggregated"],
        )
        
        assert response.map_id == "SM-001"
        assert response.overall_stability_score == 74.5


class TestCommunityPulseEndpoint:
    """Tests for community pulse endpoint"""
    
    def test_community_pulse_response_model(self):
        """Test CommunityPulseResponse model"""
        from backend.app.api.human_intel.human_intel_router import CommunityPulseResponse
        
        response = CommunityPulseResponse(
            pulse_id="CP-001",
            timestamp=datetime.utcnow().isoformat(),
            stability_index=75.0,
            community_shock_level=0.25,
            trauma_clusters=[],
            trend_direction="stable",
            recommended_interventions=["Community outreach"],
            anonymization_level="AGGREGATED",
            privacy_protections=["All data aggregated"],
        )
        
        assert response.pulse_id == "CP-001"
        assert response.stability_index == 75.0


class TestPrivacyChecksOnEndpoints:
    """Tests for privacy checks on endpoints"""
    
    def test_privacy_check_blocks_prohibited_source(self):
        """Test privacy check blocks prohibited data source"""
        from backend.app.human_intel.privacy_guard import PrivacyGuard
        
        guard = PrivacyGuard()
        
        result = guard.check_query(
            query_type="suicide_risk",
            data_sources=["private_social_media"],
            filters={},
        )
        
        assert result.query_allowed == False
    
    def test_privacy_check_blocks_demographic_filter(self):
        """Test privacy check blocks demographic filter"""
        from backend.app.human_intel.privacy_guard import PrivacyGuard
        
        guard = PrivacyGuard()
        
        result = guard.check_query(
            query_type="youth_risk",
            data_sources=["school_data"],
            filters={"race": "any"},
        )
        
        assert result.query_allowed == False
    
    def test_privacy_check_allows_valid_query(self):
        """Test privacy check allows valid query"""
        from backend.app.human_intel.privacy_guard import PrivacyGuard
        
        guard = PrivacyGuard()
        
        result = guard.check_query(
            query_type="stability_map",
            data_sources=["aggregated_data"],
            filters={},
        )
        
        assert result.query_allowed == True
