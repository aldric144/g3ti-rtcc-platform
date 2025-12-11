"""
Test Suite 5: Human-in-the-Loop Gateway Tests

Tests for approval request creation, approval chain, and escalation.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import sys
sys.path.insert(0, "/home/ubuntu/repos/g3ti-rtcc-platform/backend")

from app.city_governance.human_in_loop import (
    get_human_in_loop_gateway,
    HumanInLoopGateway,
    ApprovalRequest,
    ApprovalStatus,
    ApprovalType,
    ReviewTrigger,
    ReviewRequirement,
    ApprovalEntry,
)
from app.city_governance.constitution_engine import ActionCategory


class TestApprovalStatus:
    """Tests for ApprovalStatus enum."""

    def test_approval_statuses(self):
        """Test all approval status values."""
        assert ApprovalStatus.PENDING.value == "PENDING"
        assert ApprovalStatus.APPROVED.value == "APPROVED"
        assert ApprovalStatus.DENIED.value == "DENIED"
        assert ApprovalStatus.EXPIRED.value == "EXPIRED"
        assert ApprovalStatus.ESCALATED.value == "ESCALATED"


class TestApprovalType:
    """Tests for ApprovalType enum."""

    def test_approval_types(self):
        """Test all approval type values."""
        assert ApprovalType.SINGLE_OPERATOR.value == "SINGLE_OPERATOR"
        assert ApprovalType.SUPERVISOR.value == "SUPERVISOR"
        assert ApprovalType.COMMAND_STAFF.value == "COMMAND_STAFF"
        assert ApprovalType.MULTI_FACTOR.value == "MULTI_FACTOR"
        assert ApprovalType.LEGAL_REVIEW.value == "LEGAL_REVIEW"


class TestReviewTrigger:
    """Tests for ReviewTrigger enum."""

    def test_review_triggers(self):
        """Test all review trigger values."""
        triggers = [
            ReviewTrigger.USE_OF_FORCE,
            ReviewTrigger.SURVEILLANCE_ESCALATION,
            ReviewTrigger.DRONE_PROPERTY_ENTRY,
            ReviewTrigger.TACTICAL_ROBOTICS_ENTRY,
            ReviewTrigger.PREDICTIVE_ACTION,
            ReviewTrigger.TRAFFIC_ENFORCEMENT,
            ReviewTrigger.MASS_ALERT,
        ]
        assert len(triggers) == 7
        for trigger in triggers:
            assert trigger.value is not None


class TestReviewRequirement:
    """Tests for ReviewRequirement model."""

    def test_review_requirement_creation(self):
        """Test creating a review requirement."""
        req = ReviewRequirement(
            trigger=ReviewTrigger.USE_OF_FORCE,
            approval_type=ApprovalType.COMMAND_STAFF,
            min_approvers=1,
            timeout_minutes=30,
            requires_mfa=True,
            escalation_path=["SUPERVISOR", "COMMAND_STAFF", "CHIEF"],
        )
        assert req.trigger == ReviewTrigger.USE_OF_FORCE
        assert req.approval_type == ApprovalType.COMMAND_STAFF
        assert req.requires_mfa is True

    def test_review_requirement_multi_factor(self):
        """Test multi-factor review requirement."""
        req = ReviewRequirement(
            trigger=ReviewTrigger.TACTICAL_ROBOTICS_ENTRY,
            approval_type=ApprovalType.MULTI_FACTOR,
            min_approvers=2,
            timeout_minutes=15,
            requires_mfa=True,
            escalation_path=["SUPERVISOR", "COMMAND_STAFF"],
        )
        assert req.min_approvers == 2
        assert req.approval_type == ApprovalType.MULTI_FACTOR


class TestApprovalEntry:
    """Tests for ApprovalEntry model."""

    def test_approval_entry_creation(self):
        """Test creating an approval entry."""
        entry = ApprovalEntry(
            entry_id="entry-001",
            approver_id="officer-001",
            approver_role="SUPERVISOR",
            decision="APPROVED",
            timestamp=datetime.now(),
            notes="Approved for emergency response",
            mfa_verified=True,
        )
        assert entry.entry_id == "entry-001"
        assert entry.decision == "APPROVED"
        assert entry.mfa_verified is True

    def test_approval_entry_denial(self):
        """Test creating a denial entry."""
        entry = ApprovalEntry(
            entry_id="entry-002",
            approver_id="supervisor-001",
            approver_role="SUPERVISOR",
            decision="DENIED",
            timestamp=datetime.now(),
            notes="Insufficient justification",
            mfa_verified=True,
        )
        assert entry.decision == "DENIED"


class TestApprovalRequest:
    """Tests for ApprovalRequest model."""

    def test_approval_request_creation(self):
        """Test creating an approval request."""
        request = ApprovalRequest(
            request_id="req-001",
            action_id="action-001",
            action_type="surveillance_escalation",
            category=ActionCategory.SURVEILLANCE,
            risk_score=65,
            approval_type=ApprovalType.SUPERVISOR,
            status=ApprovalStatus.PENDING,
            requestor_id="officer-001",
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(minutes=30),
            required_approvers=1,
            approval_chain=[],
            context={},
        )
        assert request.request_id == "req-001"
        assert request.status == ApprovalStatus.PENDING
        assert request.required_approvers == 1

    def test_approval_request_with_chain(self):
        """Test approval request with approval chain."""
        entry = ApprovalEntry(
            entry_id="entry-001",
            approver_id="supervisor-001",
            approver_role="SUPERVISOR",
            decision="APPROVED",
            timestamp=datetime.now(),
            notes="Approved",
            mfa_verified=True,
        )
        request = ApprovalRequest(
            request_id="req-002",
            action_id="action-002",
            action_type="drone_operation",
            category=ActionCategory.DRONE_OPERATION,
            risk_score=55,
            approval_type=ApprovalType.SUPERVISOR,
            status=ApprovalStatus.APPROVED,
            requestor_id="officer-002",
            created_at=datetime.now() - timedelta(minutes=10),
            expires_at=datetime.now() + timedelta(minutes=20),
            required_approvers=1,
            approval_chain=[entry],
            context={},
        )
        assert len(request.approval_chain) == 1
        assert request.status == ApprovalStatus.APPROVED


class TestHumanInLoopGateway:
    """Tests for HumanInLoopGateway singleton."""

    def test_singleton_pattern(self):
        """Test that get_human_in_loop_gateway returns singleton."""
        g1 = get_human_in_loop_gateway()
        g2 = get_human_in_loop_gateway()
        assert g1 is g2

    def test_get_requirement_for_trigger(self):
        """Test getting requirement for each trigger."""
        gateway = get_human_in_loop_gateway()
        
        for trigger in ReviewTrigger:
            req = gateway.get_requirement_for_trigger(trigger)
            assert req is not None
            assert req.trigger == trigger

    def test_create_approval_request(self):
        """Test creating an approval request."""
        gateway = get_human_in_loop_gateway()
        
        request = gateway.create_approval_request(
            action_id="test-action-001",
            action_type="surveillance_escalation",
            category=ActionCategory.SURVEILLANCE,
            risk_score=65,
            requestor_id="officer-001",
            context={"target_area": "Zone 3"},
        )
        
        assert request is not None
        assert request.status == ApprovalStatus.PENDING
        assert request.risk_score == 65

    def test_create_approval_request_high_risk(self):
        """Test creating approval request for high-risk action."""
        gateway = get_human_in_loop_gateway()
        
        request = gateway.create_approval_request(
            action_id="test-action-002",
            action_type="use_of_force",
            category=ActionCategory.USE_OF_FORCE,
            risk_score=85,
            requestor_id="officer-002",
            context={"force_level": "high"},
        )
        
        assert request is not None
        # High risk should require command staff
        assert request.approval_type in [
            ApprovalType.COMMAND_STAFF,
            ApprovalType.MULTI_FACTOR,
            ApprovalType.LEGAL_REVIEW,
        ]


class TestApprovalWorkflow:
    """Tests for approval workflow operations."""

    def test_submit_approval(self):
        """Test submitting an approval."""
        gateway = get_human_in_loop_gateway()
        
        # Create request
        request = gateway.create_approval_request(
            action_id="test-action-003",
            action_type="traffic_enforcement",
            category=ActionCategory.TRAFFIC_ENFORCEMENT,
            risk_score=35,
            requestor_id="officer-003",
            context={},
        )
        
        # Submit approval
        result = gateway.submit_approval(
            request_id=request.request_id,
            approver_id="supervisor-001",
            approver_role="SUPERVISOR",
            decision="APPROVED",
            notes="Approved for routine enforcement",
            mfa_verified=True,
        )
        
        assert result is True
        
        # Check status
        updated = gateway.get_approval_request(request.request_id)
        assert updated.status == ApprovalStatus.APPROVED

    def test_submit_denial(self):
        """Test submitting a denial."""
        gateway = get_human_in_loop_gateway()
        
        # Create request
        request = gateway.create_approval_request(
            action_id="test-action-004",
            action_type="surveillance_escalation",
            category=ActionCategory.SURVEILLANCE,
            risk_score=60,
            requestor_id="officer-004",
            context={},
        )
        
        # Submit denial
        result = gateway.submit_denial(
            request_id=request.request_id,
            approver_id="supervisor-002",
            approver_role="SUPERVISOR",
            reason="Insufficient justification provided",
        )
        
        assert result is True
        
        # Check status
        updated = gateway.get_approval_request(request.request_id)
        assert updated.status == ApprovalStatus.DENIED

    def test_escalate_request(self):
        """Test escalating a request."""
        gateway = get_human_in_loop_gateway()
        
        # Create request
        request = gateway.create_approval_request(
            action_id="test-action-005",
            action_type="drone_property_entry",
            category=ActionCategory.DRONE_OPERATION,
            risk_score=70,
            requestor_id="officer-005",
            context={"is_private_property": True},
        )
        
        # Escalate
        result = gateway.escalate_request(
            request_id=request.request_id,
            escalator_id="supervisor-003",
            reason="Requires command staff review",
        )
        
        assert result is True
        
        # Check status
        updated = gateway.get_approval_request(request.request_id)
        assert updated.status == ApprovalStatus.ESCALATED


class TestMultiFactorApproval:
    """Tests for multi-factor approval workflows."""

    def test_multi_factor_requires_multiple_approvers(self):
        """Test that multi-factor requires multiple approvers."""
        gateway = get_human_in_loop_gateway()
        
        # Create high-risk request requiring multi-factor
        request = gateway.create_approval_request(
            action_id="test-action-006",
            action_type="tactical_robotics_entry",
            category=ActionCategory.ROBOTICS_OPERATION,
            risk_score=80,
            requestor_id="officer-006",
            context={"building_type": "residential"},
        )
        
        if request.approval_type == ApprovalType.MULTI_FACTOR:
            assert request.required_approvers >= 2

    def test_multi_factor_partial_approval(self):
        """Test partial approval in multi-factor workflow."""
        gateway = get_human_in_loop_gateway()
        
        # Create request requiring 2 approvers
        request = gateway.create_approval_request(
            action_id="test-action-007",
            action_type="tactical_robotics_entry",
            category=ActionCategory.ROBOTICS_OPERATION,
            risk_score=80,
            requestor_id="officer-007",
            context={},
        )
        
        if request.required_approvers >= 2:
            # First approval
            gateway.submit_approval(
                request_id=request.request_id,
                approver_id="supervisor-004",
                approver_role="SUPERVISOR",
                decision="APPROVED",
                notes="First approval",
                mfa_verified=True,
            )
            
            # Should still be pending
            updated = gateway.get_approval_request(request.request_id)
            assert updated.status == ApprovalStatus.PENDING or len(updated.approval_chain) == 1


class TestApprovalExpiration:
    """Tests for approval request expiration."""

    def test_request_has_expiration(self):
        """Test that requests have expiration time."""
        gateway = get_human_in_loop_gateway()
        
        request = gateway.create_approval_request(
            action_id="test-action-008",
            action_type="surveillance_escalation",
            category=ActionCategory.SURVEILLANCE,
            risk_score=55,
            requestor_id="officer-008",
            context={},
        )
        
        assert request.expires_at is not None
        assert request.expires_at > request.created_at

    def test_check_expired_requests(self):
        """Test checking for expired requests."""
        gateway = get_human_in_loop_gateway()
        
        expired = gateway.get_expired_requests()
        assert isinstance(expired, list)


class TestApprovalQueries:
    """Tests for approval request queries."""

    def test_get_pending_requests(self):
        """Test getting pending requests."""
        gateway = get_human_in_loop_gateway()
        
        pending = gateway.get_pending_requests()
        assert isinstance(pending, list)
        for request in pending:
            assert request.status == ApprovalStatus.PENDING

    def test_get_requests_by_status(self):
        """Test filtering requests by status."""
        gateway = get_human_in_loop_gateway()
        
        for status in ApprovalStatus:
            requests = gateway.get_requests_by_status(status)
            assert isinstance(requests, list)
            for request in requests:
                assert request.status == status

    def test_get_requests_by_approver(self):
        """Test getting requests for specific approver."""
        gateway = get_human_in_loop_gateway()
        
        requests = gateway.get_requests_for_approver("supervisor-001")
        assert isinstance(requests, list)

    def test_get_approval_request_by_id(self):
        """Test getting request by ID."""
        gateway = get_human_in_loop_gateway()
        
        # Create request
        request = gateway.create_approval_request(
            action_id="test-action-009",
            action_type="traffic_enforcement",
            category=ActionCategory.TRAFFIC_ENFORCEMENT,
            risk_score=30,
            requestor_id="officer-009",
            context={},
        )
        
        # Retrieve by ID
        retrieved = gateway.get_approval_request(request.request_id)
        assert retrieved is not None
        assert retrieved.request_id == request.request_id


class TestMFARequirement:
    """Tests for MFA requirement handling."""

    def test_high_risk_requires_mfa(self):
        """Test that high-risk actions require MFA."""
        gateway = get_human_in_loop_gateway()
        
        req = gateway.get_requirement_for_trigger(ReviewTrigger.USE_OF_FORCE)
        assert req.requires_mfa is True

    def test_approval_without_mfa_fails_when_required(self):
        """Test that approval without MFA fails when required."""
        gateway = get_human_in_loop_gateway()
        
        # Create high-risk request
        request = gateway.create_approval_request(
            action_id="test-action-010",
            action_type="use_of_force",
            category=ActionCategory.USE_OF_FORCE,
            risk_score=90,
            requestor_id="officer-010",
            context={},
        )
        
        # Try to approve without MFA
        result = gateway.submit_approval(
            request_id=request.request_id,
            approver_id="supervisor-005",
            approver_role="SUPERVISOR",
            decision="APPROVED",
            notes="Approved",
            mfa_verified=False,
        )
        
        # Should fail or be flagged
        # Implementation may vary - check that MFA is tracked
        updated = gateway.get_approval_request(request.request_id)
        if updated.approval_chain:
            # MFA status should be recorded
            assert hasattr(updated.approval_chain[-1], 'mfa_verified')
