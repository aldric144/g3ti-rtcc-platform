"""
Test Suite 6: Ethics Guardian API Tests
Tests for API endpoints
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../backend'))


class TestBiasCheckEndpoint:
    """Tests for POST /api/ethics/check-bias endpoint"""

    def test_bias_check_request_model(self):
        """Test bias check request model structure"""
        from app.api.ethics_guardian.ethics_router import BiasCheckRequest
        request = BiasCheckRequest(
            analysis_type="PREDICTIVE_AI",
            data={
                "demographic_outcomes": {
                    "Black": {"positive": 80, "negative": 20},
                    "White": {"positive": 85, "negative": 15},
                },
                "reference_group": "White",
            },
            model_version="v1.0",
            geographic_scope="Downtown",
        )
        assert request.analysis_type == "PREDICTIVE_AI"
        assert request.model_version == "v1.0"

    def test_bias_check_response_model(self):
        """Test bias check response model structure"""
        from app.api.ethics_guardian.ethics_router import BiasCheckResponse
        response = BiasCheckResponse(
            analysis_id="test-001",
            status="NO_BIAS_DETECTED",
            blocked=False,
            confidence_score=0.95,
            metrics=[],
            affected_groups=[],
            recommendations=[],
        )
        assert response.status == "NO_BIAS_DETECTED"
        assert response.blocked is False


class TestForceRiskEndpoint:
    """Tests for POST /api/ethics/force-risk endpoint"""

    def test_force_risk_request_model(self):
        """Test force risk request model structure"""
        from app.api.ethics_guardian.ethics_router import ForceRiskRequest
        request = ForceRiskRequest(
            action_id="test-001",
            context={
                "civil_rights_exposure": 30,
                "force_escalation_probability": 25,
            },
        )
        assert request.action_id == "test-001"

    def test_force_risk_response_model(self):
        """Test force risk response model structure"""
        from app.api.ethics_guardian.ethics_router import ForceRiskResponse
        response = ForceRiskResponse(
            action_id="test-001",
            risk_score=35,
            risk_level="MODERATE",
            factor_scores={},
            deescalation_recommendations=[],
            recommended_force_level="VERBAL",
        )
        assert response.risk_level == "MODERATE"


class TestCivilRightsEndpoint:
    """Tests for POST /api/ethics/civil-rights endpoint"""

    def test_civil_rights_request_model(self):
        """Test civil rights request model structure"""
        from app.api.ethics_guardian.ethics_router import CivilRightsRequest
        request = CivilRightsRequest(
            action_id="test-001",
            action_type="search",
            context={"has_warrant": True},
        )
        assert request.action_type == "search"

    def test_civil_rights_response_model(self):
        """Test civil rights response model structure"""
        from app.api.ethics_guardian.ethics_router import CivilRightsResponse
        response = CivilRightsResponse(
            action_id="test-001",
            action_type="search",
            status="COMPLIANT",
            violations=[],
            blocked=False,
            constitutional_concerns=[],
        )
        assert response.status == "COMPLIANT"


class TestEthicsScoreEndpoint:
    """Tests for POST /api/ethics/ethics-score endpoint"""

    def test_ethics_score_request_model(self):
        """Test ethics score request model structure"""
        from app.api.ethics_guardian.ethics_router import EthicsScoreRequest
        request = EthicsScoreRequest(
            action_id="test-001",
            action_type="patrol",
            context={
                "bias_detected": False,
                "civil_rights_compliant": True,
            },
        )
        assert request.action_type == "patrol"

    def test_ethics_score_response_model(self):
        """Test ethics score response model structure"""
        from app.api.ethics_guardian.ethics_router import EthicsScoreResponse
        response = EthicsScoreResponse(
            action_id="test-001",
            action_type="patrol",
            total_score=85,
            ethics_level="GOOD",
            color_code="#84CC16",
            required_action="ALLOW_WITH_LOGGING",
            component_scores={},
            human_review_required=False,
        )
        assert response.ethics_level == "GOOD"


class TestProtectedCommunityEndpoint:
    """Tests for POST /api/ethics/protected-community endpoint"""

    def test_protected_community_request_model(self):
        """Test protected community request model structure"""
        from app.api.ethics_guardian.ethics_router import ProtectedCommunityRequest
        request = ProtectedCommunityRequest(
            action_id="test-001",
            action_type="enforcement",
            context={
                "affected_communities": ["BLACK_COMMUNITY"],
            },
        )
        assert request.action_type == "enforcement"

    def test_protected_community_response_model(self):
        """Test protected community response model structure"""
        from app.api.ethics_guardian.ethics_router import ProtectedCommunityResponse
        response = ProtectedCommunityResponse(
            action_id="test-001",
            triggered_rules=[],
            affected_communities=[],
            escalation_required=False,
            liaison_notification=False,
        )
        assert response.escalation_required is False


class TestExplainEndpoint:
    """Tests for GET /api/ethics/explain/{action_id} endpoint"""

    def test_explanation_response_model(self):
        """Test explanation response model structure"""
        from app.api.ethics_guardian.ethics_router import ExplanationResponse
        response = ExplanationResponse(
            action_id="test-001",
            action_type="patrol",
            summary="Decision allowed based on ethics assessment",
            chain_of_reasoning=[],
            legal_basis=[],
            data_sources=[],
            bias_metrics={},
            risk_impacts={},
            safeguard_triggers=[],
            alternative_actions=[],
            limitations=[],
        )
        assert response.action_id == "test-001"


class TestAuditEndpoint:
    """Tests for GET /api/ethics/audit endpoint"""

    def test_audit_entry_model(self):
        """Test audit entry model structure"""
        from app.api.ethics_guardian.ethics_router import AuditEntryResponse
        response = AuditEntryResponse(
            id="audit-001",
            timestamp="2024-01-15T14:30:00Z",
            action_id="test-001",
            action_type="patrol",
            actor_id="system",
            actor_role="AI",
            severity="INFO",
            summary="Decision allowed",
            hash_chain="abc123",
            retention_days=365,
        )
        assert response.severity == "INFO"


class TestRouterConfiguration:
    """Tests for router configuration"""

    def test_router_prefix(self):
        """Test router has correct prefix"""
        from app.api.ethics_guardian.ethics_router import router
        assert router.prefix == "/api/ethics"

    def test_router_tags(self):
        """Test router has correct tags"""
        from app.api.ethics_guardian.ethics_router import router
        assert "Ethics Guardian" in router.tags


class TestHistoryEndpoints:
    """Tests for history retrieval endpoints"""

    def test_bias_history_endpoint_exists(self):
        """Test bias history endpoint is defined"""
        from app.api.ethics_guardian.ethics_router import router
        routes = [r.path for r in router.routes]
        assert "/bias-history" in routes

    def test_force_risk_history_endpoint_exists(self):
        """Test force risk history endpoint is defined"""
        from app.api.ethics_guardian.ethics_router import router
        routes = [r.path for r in router.routes]
        assert "/force-risk-history" in routes

    def test_ethics_history_endpoint_exists(self):
        """Test ethics history endpoint is defined"""
        from app.api.ethics_guardian.ethics_router import router
        routes = [r.path for r in router.routes]
        assert "/ethics-history" in routes


class TestConfigurationEndpoints:
    """Tests for configuration retrieval endpoints"""

    def test_community_profiles_endpoint_exists(self):
        """Test community profiles endpoint is defined"""
        from app.api.ethics_guardian.ethics_router import router
        routes = [r.path for r in router.routes]
        assert "/community-profiles" in routes

    def test_retention_limits_endpoint_exists(self):
        """Test retention limits endpoint is defined"""
        from app.api.ethics_guardian.ethics_router import router
        routes = [r.path for r in router.routes]
        assert "/retention-limits" in routes

    def test_ethics_thresholds_endpoint_exists(self):
        """Test ethics thresholds endpoint is defined"""
        from app.api.ethics_guardian.ethics_router import router
        routes = [r.path for r in router.routes]
        assert "/ethics-thresholds" in routes
