"""
Test Suite: Moral Compass API

Phase 35: AI Moral Compass & Societal Ethics Reasoning Engine
Tests for REST API endpoints.
"""

import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch


class TestMoralAssessEndpoint:
    """Tests for POST /api/moral/assess endpoint."""

    def test_assess_request_model(self):
        from backend.app.api.moral_compass.moral_compass_router import MoralAssessRequest
        
        request = MoralAssessRequest(
            action_type="arrest",
            action_description="Arrest suspect",
            requester_id="officer_001",
        )
        assert request.action_type == "arrest"
        assert request.requester_id == "officer_001"

    def test_assess_response_model(self):
        from backend.app.api.moral_compass.moral_compass_router import MoralAssessResponse
        
        response = MoralAssessResponse(
            assessment_id="test-123",
            action_type="arrest",
            decision="allow",
            reasoning_summary="Action permitted",
            community_impact_score=25.0,
            risk_to_community=15.0,
            required_approvals=[],
            conditions=[],
            confidence=0.9,
            assessment_hash="abc123",
        )
        assert response.assessment_id == "test-123"
        assert response.decision == "allow"


class TestFairnessEndpoint:
    """Tests for POST /api/moral/fairness endpoint."""

    def test_fairness_request_model(self):
        from backend.app.api.moral_compass.moral_compass_router import FairnessRequest
        
        request = FairnessRequest(
            action_type="targeting",
            requester_id="system_001",
        )
        assert request.action_type == "targeting"

    def test_fairness_response_model(self):
        from backend.app.api.moral_compass.moral_compass_router import FairnessResponse
        
        response = FairnessResponse(
            assessment_id="fair-123",
            overall_fairness_score=0.85,
            passed=True,
            requires_review=False,
            bias_detected=False,
            disparity_count=0,
            recommendations=[],
        )
        assert response.passed is True
        assert response.overall_fairness_score == 0.85


class TestReasoningEndpoint:
    """Tests for POST /api/moral/reason endpoint."""

    def test_reasoning_request_model(self):
        from backend.app.api.moral_compass.moral_compass_router import ReasoningRequest
        
        request = ReasoningRequest(
            action_type="search",
            context={"warrant": True},
        )
        assert request.action_type == "search"

    def test_reasoning_response_model(self):
        from backend.app.api.moral_compass.moral_compass_router import ReasoningResponse
        
        response = ReasoningResponse(
            capsule_id="cap-123",
            action_type="search",
            decision="allow",
            key_factors=["warrant_present"],
            constraints_applied=["4th_amendment"],
            ethical_principles=["justice"],
            human_readable_explanation="Search permitted with warrant",
            confidence=0.95,
        )
        assert response.capsule_id == "cap-123"
        assert response.confidence == 0.95


class TestContextEndpoint:
    """Tests for GET /api/moral/context endpoint."""

    def test_context_request_model(self):
        from backend.app.api.moral_compass.moral_compass_router import ContextRequest
        
        request = ContextRequest(
            location="Downtown Riviera Beach",
            action_type="patrol",
        )
        assert request.location == "Downtown Riviera Beach"


class TestGuardrailEndpoints:
    """Tests for guardrail-related endpoints."""

    def test_guardrail_check_request_model(self):
        from backend.app.api.moral_compass.moral_compass_router import GuardrailCheckRequest
        
        request = GuardrailCheckRequest(
            action_type="search",
            action_description="Search vehicle",
            requester_id="officer_001",
        )
        assert request.action_type == "search"

    def test_guardrail_check_response_model(self):
        from backend.app.api.moral_compass.moral_compass_router import GuardrailCheckResponse
        
        response = GuardrailCheckResponse(
            assessment_id="guard-123",
            passed=True,
            blocked=False,
            requires_review=False,
            violation_count=0,
            recommendations=[],
        )
        assert response.passed is True
        assert response.blocked is False


class TestEventEndpoints:
    """Tests for event-related endpoints."""

    def test_event_create_request_model(self):
        from backend.app.api.moral_compass.moral_compass_router import EventCreateRequest
        
        request = EventCreateRequest(
            name="Community Festival",
            event_type="festival",
            location="Downtown",
            start_time=datetime.utcnow(),
            expected_attendance=500,
        )
        assert request.name == "Community Festival"
        assert request.expected_attendance == 500


class TestViolationEndpoints:
    """Tests for violation-related endpoints."""

    def test_violation_resolve_request_model(self):
        from backend.app.api.moral_compass.moral_compass_router import ViolationResolveRequest
        
        request = ViolationResolveRequest(
            resolved_by="supervisor_001",
            notes="Reviewed and resolved",
        )
        assert request.resolved_by == "supervisor_001"


class TestRouterConfiguration:
    """Tests for router configuration."""

    def test_router_prefix(self):
        from backend.app.api.moral_compass.moral_compass_router import router
        
        assert router.prefix == "/api/moral"

    def test_router_tags(self):
        from backend.app.api.moral_compass.moral_compass_router import router
        
        assert "moral_compass" in router.tags
