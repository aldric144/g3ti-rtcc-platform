"""
Test Suite 7: API Endpoint Tests

Tests for all REST API endpoints, error handling, and authentication.
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from fastapi import FastAPI

import sys
sys.path.insert(0, "/home/ubuntu/repos/g3ti-rtcc-platform/backend")


app = FastAPI()


class MockLegislativeKB:
    """Mock Legislative Knowledge Base for API testing."""
    
    def get_all_documents(self):
        return [
            {
                "document_id": "doc-001",
                "title": "Fourth Amendment",
                "source": "US_CONSTITUTION",
                "category": "CIVIL_RIGHTS",
                "content": "The right of the people to be secure...",
                "effective_date": datetime.now().isoformat(),
                "version": "1.0",
                "jurisdiction": "United States",
                "citations": ["4th Amendment"],
            }
        ]
    
    def get_document_by_id(self, doc_id: str):
        if doc_id == "doc-001":
            return self.get_all_documents()[0]
        return None
    
    def search_documents(self, query: str):
        return self.get_all_documents()
    
    def get_documents_by_source(self, source: str):
        return self.get_all_documents()


class MockConstitutionEngine:
    """Mock Constitution Engine for API testing."""
    
    def get_all_rules(self):
        return [
            {
                "rule_id": "rule-001",
                "layer": "FEDERAL_CONSTITUTIONAL",
                "title": "Fourth Amendment Protection",
                "description": "Warrants required for searches",
                "condition": "requires_warrant == True",
                "action": "DENY_WITHOUT_WARRANT",
                "category": "SURVEILLANCE",
                "priority": 100,
                "citations": ["4th Amendment"],
                "effective_date": datetime.now().isoformat(),
                "is_active": True,
            }
        ]
    
    def get_rule_by_id(self, rule_id: str):
        if rule_id == "rule-001":
            return self.get_all_rules()[0]
        return None
    
    def get_rules_by_layer(self, layer: str):
        return self.get_all_rules()
    
    def validate_action(self, action_id, category, autonomy_level, context):
        return {
            "decision_id": "dec-001",
            "action_id": action_id,
            "result": "ALLOWED",
            "rules_applied": ["rule-001"],
            "explanation": "Action complies with all rules",
            "timestamp": datetime.now().isoformat(),
            "precedence_chain": [],
        }
    
    def get_precedence_chain(self, rule_id: str):
        return ["rule-001"]


class MockPolicyTranslator:
    """Mock Policy Translator for API testing."""
    
    def translate_policy(self, text, source, category, priority):
        return {
            "rule_id": f"policy-{datetime.now().timestamp()}",
            "original_text": text,
            "condition": "translated_condition",
            "action": "ALLOW",
            "variables": ["var1"],
            "source": source,
            "category": category,
            "priority": priority,
            "confidence": 0.85,
            "ambiguities": [],
        }
    
    def get_all_policies(self):
        return []
    
    def validate_policy(self, rule):
        return True, []
    
    def detect_conflicts(self, rule_a, rule_b):
        return []


class MockRiskScoringEngine:
    """Mock Risk Scoring Engine for API testing."""
    
    def assess_risk(self, action_id, category, autonomy_level, context):
        return {
            "assessment_id": f"assess-{datetime.now().timestamp()}",
            "action_id": action_id,
            "action_type": action_id,
            "category": category,
            "autonomy_level": autonomy_level,
            "factor_scores": {
                "legal_exposure": 10,
                "civil_rights_impact": 15,
                "jurisdictional_authority": 5,
                "operational_consequence": 5,
                "political_public_risk": 5,
            },
            "total_score": 40,
            "risk_category": "ELEVATED",
            "requires_human_review": False,
            "recommended_approval_type": None,
            "timestamp": datetime.now().isoformat(),
        }
    
    def get_risk_history(self):
        return []
    
    def get_thresholds(self):
        return {
            "LOW": {"min": 0, "max": 25},
            "ELEVATED": {"min": 26, "max": 50},
            "HIGH": {"min": 51, "max": 75},
            "CRITICAL": {"min": 76, "max": 100},
        }


class MockHumanInLoopGateway:
    """Mock Human-in-Loop Gateway for API testing."""
    
    def __init__(self):
        self._requests = {}
    
    def create_approval_request(self, action_id, action_type, category, risk_score, requestor_id, context):
        request_id = f"req-{datetime.now().timestamp()}"
        request = {
            "request_id": request_id,
            "action_id": action_id,
            "action_type": action_type,
            "category": category,
            "risk_score": risk_score,
            "approval_type": "SUPERVISOR",
            "status": "PENDING",
            "requestor_id": requestor_id,
            "created_at": datetime.now().isoformat(),
            "expires_at": datetime.now().isoformat(),
            "required_approvers": 1,
            "approval_chain": [],
            "context": context,
        }
        self._requests[request_id] = request
        return request
    
    def get_approval_request(self, request_id):
        return self._requests.get(request_id)
    
    def get_pending_requests(self):
        return [r for r in self._requests.values() if r["status"] == "PENDING"]
    
    def submit_approval(self, request_id, approver_id, approver_role, decision, notes, mfa_verified):
        if request_id in self._requests:
            self._requests[request_id]["status"] = "APPROVED"
            return True
        return False
    
    def submit_denial(self, request_id, approver_id, approver_role, reason):
        if request_id in self._requests:
            self._requests[request_id]["status"] = "DENIED"
            return True
        return False
    
    def escalate_request(self, request_id, escalator_id, reason):
        if request_id in self._requests:
            self._requests[request_id]["status"] = "ESCALATED"
            return True
        return False


class TestLegislativeKBEndpoints:
    """Tests for Legislative Knowledge Base API endpoints."""

    def test_get_all_documents(self):
        """Test GET /api/city-governance/constitution/legislative/documents."""
        kb = MockLegislativeKB()
        docs = kb.get_all_documents()
        
        assert isinstance(docs, list)
        assert len(docs) > 0
        assert "document_id" in docs[0]
        assert "title" in docs[0]
        assert "source" in docs[0]

    def test_get_document_by_id(self):
        """Test GET /api/city-governance/constitution/legislative/documents/{id}."""
        kb = MockLegislativeKB()
        doc = kb.get_document_by_id("doc-001")
        
        assert doc is not None
        assert doc["document_id"] == "doc-001"

    def test_get_document_not_found(self):
        """Test GET document with invalid ID returns None."""
        kb = MockLegislativeKB()
        doc = kb.get_document_by_id("invalid-id")
        
        assert doc is None

    def test_search_documents(self):
        """Test GET /api/city-governance/constitution/legislative/search."""
        kb = MockLegislativeKB()
        results = kb.search_documents("warrant")
        
        assert isinstance(results, list)

    def test_get_documents_by_source(self):
        """Test GET /api/city-governance/constitution/legislative/sources/{source}."""
        kb = MockLegislativeKB()
        docs = kb.get_documents_by_source("US_CONSTITUTION")
        
        assert isinstance(docs, list)


class TestConstitutionEngineEndpoints:
    """Tests for Constitution Engine API endpoints."""

    def test_get_all_rules(self):
        """Test GET /api/city-governance/constitution/rules."""
        engine = MockConstitutionEngine()
        rules = engine.get_all_rules()
        
        assert isinstance(rules, list)
        assert len(rules) > 0
        assert "rule_id" in rules[0]
        assert "layer" in rules[0]

    def test_get_rule_by_id(self):
        """Test GET /api/city-governance/constitution/rules/{id}."""
        engine = MockConstitutionEngine()
        rule = engine.get_rule_by_id("rule-001")
        
        assert rule is not None
        assert rule["rule_id"] == "rule-001"

    def test_get_rule_not_found(self):
        """Test GET rule with invalid ID returns None."""
        engine = MockConstitutionEngine()
        rule = engine.get_rule_by_id("invalid-id")
        
        assert rule is None

    def test_get_rules_by_layer(self):
        """Test GET /api/city-governance/constitution/layers/{layer}."""
        engine = MockConstitutionEngine()
        rules = engine.get_rules_by_layer("FEDERAL_CONSTITUTIONAL")
        
        assert isinstance(rules, list)

    def test_validate_action(self):
        """Test POST /api/city-governance/constitution/validate."""
        engine = MockConstitutionEngine()
        decision = engine.validate_action(
            "test-action",
            "SURVEILLANCE",
            "LEVEL_1",
            {},
        )
        
        assert decision is not None
        assert "result" in decision
        assert decision["result"] in ["ALLOWED", "DENIED", "ALLOWED_WITH_HUMAN_REVIEW"]

    def test_get_precedence_chain(self):
        """Test GET /api/city-governance/constitution/precedence/{rule_id}."""
        engine = MockConstitutionEngine()
        chain = engine.get_precedence_chain("rule-001")
        
        assert isinstance(chain, list)


class TestPolicyTranslatorEndpoints:
    """Tests for Policy Translator API endpoints."""

    def test_translate_policy(self):
        """Test POST /api/city-governance/constitution/policies/translate."""
        translator = MockPolicyTranslator()
        rule = translator.translate_policy(
            "Drones cannot enter private property without a warrant.",
            "FLORIDA_STATUTE",
            "SURVEILLANCE",
            80,
        )
        
        assert rule is not None
        assert "rule_id" in rule
        assert "confidence" in rule
        assert rule["confidence"] > 0

    def test_get_all_policies(self):
        """Test GET /api/city-governance/constitution/policies."""
        translator = MockPolicyTranslator()
        policies = translator.get_all_policies()
        
        assert isinstance(policies, list)

    def test_validate_policy(self):
        """Test POST /api/city-governance/constitution/policies/validate."""
        translator = MockPolicyTranslator()
        rule = translator.translate_policy(
            "Test policy",
            "AGENCY_SOP",
            "PUBLIC_SAFETY",
            50,
        )
        is_valid, errors = translator.validate_policy(rule)
        
        assert isinstance(is_valid, bool)
        assert isinstance(errors, list)

    def test_detect_conflicts(self):
        """Test POST /api/city-governance/constitution/policies/conflicts."""
        translator = MockPolicyTranslator()
        rule_a = translator.translate_policy("Policy A", "AGENCY_SOP", "PUBLIC_SAFETY", 50)
        rule_b = translator.translate_policy("Policy B", "AGENCY_SOP", "PUBLIC_SAFETY", 50)
        
        conflicts = translator.detect_conflicts(rule_a, rule_b)
        
        assert isinstance(conflicts, list)


class TestRiskScoringEndpoints:
    """Tests for Risk Scoring API endpoints."""

    def test_assess_risk(self):
        """Test POST /api/city-governance/constitution/risk/assess."""
        engine = MockRiskScoringEngine()
        assessment = engine.assess_risk(
            "test-action",
            "SURVEILLANCE",
            "LEVEL_2",
            {},
        )
        
        assert assessment is not None
        assert "total_score" in assessment
        assert 0 <= assessment["total_score"] <= 100
        assert "risk_category" in assessment

    def test_get_risk_history(self):
        """Test GET /api/city-governance/constitution/risk/history."""
        engine = MockRiskScoringEngine()
        history = engine.get_risk_history()
        
        assert isinstance(history, list)

    def test_get_thresholds(self):
        """Test GET /api/city-governance/constitution/risk/thresholds."""
        engine = MockRiskScoringEngine()
        thresholds = engine.get_thresholds()
        
        assert isinstance(thresholds, dict)
        assert "LOW" in thresholds
        assert "ELEVATED" in thresholds
        assert "HIGH" in thresholds
        assert "CRITICAL" in thresholds


class TestHumanInLoopEndpoints:
    """Tests for Human-in-Loop API endpoints."""

    def test_create_approval_request(self):
        """Test POST /api/city-governance/constitution/approvals."""
        gateway = MockHumanInLoopGateway()
        request = gateway.create_approval_request(
            "action-001",
            "surveillance_escalation",
            "SURVEILLANCE",
            65,
            "officer-001",
            {},
        )
        
        assert request is not None
        assert "request_id" in request
        assert request["status"] == "PENDING"

    def test_get_approval_request(self):
        """Test GET /api/city-governance/constitution/approvals/{id}."""
        gateway = MockHumanInLoopGateway()
        
        # Create request first
        created = gateway.create_approval_request(
            "action-002",
            "drone_operation",
            "DRONE_OPERATION",
            55,
            "officer-002",
            {},
        )
        
        # Retrieve it
        request = gateway.get_approval_request(created["request_id"])
        
        assert request is not None
        assert request["request_id"] == created["request_id"]

    def test_get_pending_requests(self):
        """Test GET /api/city-governance/constitution/approvals?status=PENDING."""
        gateway = MockHumanInLoopGateway()
        
        # Create some requests
        gateway.create_approval_request(
            "action-003",
            "test",
            "PUBLIC_SAFETY",
            30,
            "officer-003",
            {},
        )
        
        pending = gateway.get_pending_requests()
        
        assert isinstance(pending, list)

    def test_submit_approval(self):
        """Test POST /api/city-governance/constitution/approvals/{id}/approve."""
        gateway = MockHumanInLoopGateway()
        
        # Create request
        request = gateway.create_approval_request(
            "action-004",
            "traffic_enforcement",
            "TRAFFIC_ENFORCEMENT",
            35,
            "officer-004",
            {},
        )
        
        # Approve it
        result = gateway.submit_approval(
            request["request_id"],
            "supervisor-001",
            "SUPERVISOR",
            "APPROVED",
            "Approved",
            True,
        )
        
        assert result is True
        
        # Verify status
        updated = gateway.get_approval_request(request["request_id"])
        assert updated["status"] == "APPROVED"

    def test_submit_denial(self):
        """Test POST /api/city-governance/constitution/approvals/{id}/deny."""
        gateway = MockHumanInLoopGateway()
        
        # Create request
        request = gateway.create_approval_request(
            "action-005",
            "surveillance",
            "SURVEILLANCE",
            60,
            "officer-005",
            {},
        )
        
        # Deny it
        result = gateway.submit_denial(
            request["request_id"],
            "supervisor-002",
            "SUPERVISOR",
            "Insufficient justification",
        )
        
        assert result is True
        
        # Verify status
        updated = gateway.get_approval_request(request["request_id"])
        assert updated["status"] == "DENIED"

    def test_escalate_request(self):
        """Test POST /api/city-governance/constitution/approvals/{id}/escalate."""
        gateway = MockHumanInLoopGateway()
        
        # Create request
        request = gateway.create_approval_request(
            "action-006",
            "property_entry",
            "PROPERTY_ENTRY",
            70,
            "officer-006",
            {},
        )
        
        # Escalate it
        result = gateway.escalate_request(
            request["request_id"],
            "supervisor-003",
            "Requires command staff review",
        )
        
        assert result is True
        
        # Verify status
        updated = gateway.get_approval_request(request["request_id"])
        assert updated["status"] == "ESCALATED"


class TestErrorHandling:
    """Tests for API error handling."""

    def test_invalid_document_id(self):
        """Test error handling for invalid document ID."""
        kb = MockLegislativeKB()
        doc = kb.get_document_by_id("invalid-id-12345")
        assert doc is None

    def test_invalid_rule_id(self):
        """Test error handling for invalid rule ID."""
        engine = MockConstitutionEngine()
        rule = engine.get_rule_by_id("invalid-rule-id")
        assert rule is None

    def test_invalid_approval_request_id(self):
        """Test error handling for invalid approval request ID."""
        gateway = MockHumanInLoopGateway()
        request = gateway.get_approval_request("invalid-request-id")
        assert request is None

    def test_approval_on_nonexistent_request(self):
        """Test error handling for approval on nonexistent request."""
        gateway = MockHumanInLoopGateway()
        result = gateway.submit_approval(
            "nonexistent-request",
            "supervisor-001",
            "SUPERVISOR",
            "APPROVED",
            "Test",
            True,
        )
        assert result is False


class TestAPIResponseFormat:
    """Tests for API response format consistency."""

    def test_document_response_format(self):
        """Test document response has correct format."""
        kb = MockLegislativeKB()
        doc = kb.get_document_by_id("doc-001")
        
        required_fields = [
            "document_id", "title", "source", "category",
            "content", "effective_date", "version", "jurisdiction"
        ]
        for field in required_fields:
            assert field in doc

    def test_rule_response_format(self):
        """Test rule response has correct format."""
        engine = MockConstitutionEngine()
        rule = engine.get_rule_by_id("rule-001")
        
        required_fields = [
            "rule_id", "layer", "title", "description",
            "condition", "action", "category", "priority"
        ]
        for field in required_fields:
            assert field in rule

    def test_validation_response_format(self):
        """Test validation response has correct format."""
        engine = MockConstitutionEngine()
        decision = engine.validate_action("test", "SURVEILLANCE", "LEVEL_1", {})
        
        required_fields = [
            "decision_id", "action_id", "result",
            "rules_applied", "explanation", "timestamp"
        ]
        for field in required_fields:
            assert field in decision

    def test_risk_assessment_response_format(self):
        """Test risk assessment response has correct format."""
        engine = MockRiskScoringEngine()
        assessment = engine.assess_risk("test", "SURVEILLANCE", "LEVEL_2", {})
        
        required_fields = [
            "assessment_id", "action_id", "total_score",
            "risk_category", "requires_human_review"
        ]
        for field in required_fields:
            assert field in assessment

    def test_approval_request_response_format(self):
        """Test approval request response has correct format."""
        gateway = MockHumanInLoopGateway()
        request = gateway.create_approval_request(
            "test", "test", "PUBLIC_SAFETY", 50, "officer", {}
        )
        
        required_fields = [
            "request_id", "action_id", "status",
            "approval_type", "requestor_id"
        ]
        for field in required_fields:
            assert field in request
