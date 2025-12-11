"""
Phase 25: Human-in-the-Loop Gateway

Defines mandatory human review workflows for high-risk AI actions:
- Use of force
- Surveillance escalation
- Drone property entry
- Tactical robotics entry
- Predictive actions involving individuals
- Traffic enforcement automation
- Mass alerts

Creates workflows with required approvals, multi-factor authorization,
and audit-trail signatures.
"""

from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from uuid import uuid4
import hashlib
import json

from .constitution_engine import ActionCategory, ValidationResult
from .risk_scoring import RiskCategory


class ApprovalType(Enum):
    """Types of approvals required."""
    SINGLE_OPERATOR = "single_operator"
    SUPERVISOR = "supervisor"
    COMMAND_STAFF = "command_staff"
    MULTI_FACTOR = "multi_factor"
    LEGAL_REVIEW = "legal_review"
    CITY_MANAGER = "city_manager"
    EMERGENCY_DIRECTOR = "emergency_director"


class ApprovalStatus(Enum):
    """Status of an approval request."""
    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"
    EXPIRED = "expired"
    ESCALATED = "escalated"
    WITHDRAWN = "withdrawn"


class ReviewTrigger(Enum):
    """Triggers that require human review."""
    USE_OF_FORCE = "use_of_force"
    SURVEILLANCE_ESCALATION = "surveillance_escalation"
    DRONE_PROPERTY_ENTRY = "drone_property_entry"
    ROBOTICS_PROPERTY_ENTRY = "robotics_property_entry"
    PREDICTIVE_INDIVIDUAL_ACTION = "predictive_individual_action"
    TRAFFIC_ENFORCEMENT_AUTOMATION = "traffic_enforcement_automation"
    MASS_ALERT = "mass_alert"
    EVACUATION_ORDER = "evacuation_order"
    HIGH_RISK_SCORE = "high_risk_score"
    CONSTITUTIONAL_CONCERN = "constitutional_concern"


@dataclass
class ApprovalSignature:
    """Digital signature for an approval."""
    signature_id: str
    approver_id: str
    approver_name: str
    approver_role: str
    approval_type: ApprovalType
    decision: str  # approved, denied
    timestamp: datetime
    signature_hash: str
    mfa_verified: bool
    ip_address: Optional[str] = None
    device_id: Optional[str] = None
    notes: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "signature_id": self.signature_id,
            "approver_id": self.approver_id,
            "approver_name": self.approver_name,
            "approver_role": self.approver_role,
            "approval_type": self.approval_type.value,
            "decision": self.decision,
            "timestamp": self.timestamp.isoformat(),
            "signature_hash": self.signature_hash,
            "mfa_verified": self.mfa_verified,
            "ip_address": self.ip_address,
            "device_id": self.device_id,
            "notes": self.notes,
        }


@dataclass
class ApprovalRequirement:
    """Defines what approvals are required for an action."""
    requirement_id: str
    trigger: ReviewTrigger
    approval_types: List[ApprovalType]
    minimum_approvals: int
    requires_mfa: bool
    timeout_minutes: int
    escalation_chain: List[ApprovalType]
    auto_deny_on_timeout: bool
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "requirement_id": self.requirement_id,
            "trigger": self.trigger.value,
            "approval_types": [a.value for a in self.approval_types],
            "minimum_approvals": self.minimum_approvals,
            "requires_mfa": self.requires_mfa,
            "timeout_minutes": self.timeout_minutes,
            "escalation_chain": [a.value for a in self.escalation_chain],
            "auto_deny_on_timeout": self.auto_deny_on_timeout,
        }


@dataclass
class ApprovalRequest:
    """A request for human approval."""
    request_id: str
    action_type: str
    action_category: ActionCategory
    action_details: Dict[str, Any]
    trigger: ReviewTrigger
    requirement: ApprovalRequirement
    risk_score: int
    risk_category: RiskCategory
    validation_result: ValidationResult
    explanation: str
    signatures: List[ApprovalSignature]
    status: ApprovalStatus
    created_at: datetime
    expires_at: datetime
    completed_at: Optional[datetime] = None
    escalated_at: Optional[datetime] = None
    escalation_level: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "request_id": self.request_id,
            "action_type": self.action_type,
            "action_category": self.action_category.value,
            "action_details": self.action_details,
            "trigger": self.trigger.value,
            "requirement": self.requirement.to_dict(),
            "risk_score": self.risk_score,
            "risk_category": self.risk_category.value,
            "validation_result": self.validation_result.value,
            "explanation": self.explanation,
            "signatures": [s.to_dict() for s in self.signatures],
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "escalated_at": self.escalated_at.isoformat() if self.escalated_at else None,
            "escalation_level": self.escalation_level,
            "approvals_received": len([s for s in self.signatures if s.decision == "approved"]),
            "approvals_required": self.requirement.minimum_approvals,
        }
    
    def is_approved(self) -> bool:
        """Check if request has sufficient approvals."""
        approved_count = len([s for s in self.signatures if s.decision == "approved"])
        return approved_count >= self.requirement.minimum_approvals
    
    def is_denied(self) -> bool:
        """Check if request has been denied."""
        return any(s.decision == "denied" for s in self.signatures)
    
    def is_expired(self) -> bool:
        """Check if request has expired."""
        return datetime.utcnow() > self.expires_at


@dataclass
class WorkflowAuditEntry:
    """Audit entry for workflow actions."""
    entry_id: str
    request_id: str
    event_type: str
    actor_id: Optional[str]
    actor_name: Optional[str]
    details: Dict[str, Any]
    timestamp: datetime
    signature_hash: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "entry_id": self.entry_id,
            "request_id": self.request_id,
            "event_type": self.event_type,
            "actor_id": self.actor_id,
            "actor_name": self.actor_name,
            "details": self.details,
            "timestamp": self.timestamp.isoformat(),
            "signature_hash": self.signature_hash,
        }


class HumanInTheLoopGateway:
    """
    Human-in-the-Loop Gateway
    
    Manages mandatory human review workflows for high-risk AI actions.
    Ensures proper authorization, multi-factor authentication, and
    complete audit trails.
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._requirements: Dict[ReviewTrigger, ApprovalRequirement] = {}
        self._requests: Dict[str, ApprovalRequest] = {}
        self._pending_requests: Dict[str, ApprovalRequest] = {}
        self._audit_log: List[WorkflowAuditEntry] = []
        self._notification_callbacks: List[Callable] = []
        
        self._initialize_requirements()
        self._initialized = True
    
    def _initialize_requirements(self):
        """Initialize approval requirements for each trigger."""
        
        # Use of Force - Highest scrutiny
        self._requirements[ReviewTrigger.USE_OF_FORCE] = ApprovalRequirement(
            requirement_id="req-uof",
            trigger=ReviewTrigger.USE_OF_FORCE,
            approval_types=[ApprovalType.SUPERVISOR, ApprovalType.COMMAND_STAFF],
            minimum_approvals=2,
            requires_mfa=True,
            timeout_minutes=5,
            escalation_chain=[ApprovalType.COMMAND_STAFF, ApprovalType.LEGAL_REVIEW],
            auto_deny_on_timeout=True,
        )
        
        # Surveillance Escalation
        self._requirements[ReviewTrigger.SURVEILLANCE_ESCALATION] = ApprovalRequirement(
            requirement_id="req-surv",
            trigger=ReviewTrigger.SURVEILLANCE_ESCALATION,
            approval_types=[ApprovalType.SUPERVISOR],
            minimum_approvals=1,
            requires_mfa=True,
            timeout_minutes=15,
            escalation_chain=[ApprovalType.COMMAND_STAFF],
            auto_deny_on_timeout=False,
        )
        
        # Drone Property Entry
        self._requirements[ReviewTrigger.DRONE_PROPERTY_ENTRY] = ApprovalRequirement(
            requirement_id="req-drone",
            trigger=ReviewTrigger.DRONE_PROPERTY_ENTRY,
            approval_types=[ApprovalType.SUPERVISOR, ApprovalType.LEGAL_REVIEW],
            minimum_approvals=2,
            requires_mfa=True,
            timeout_minutes=10,
            escalation_chain=[ApprovalType.COMMAND_STAFF, ApprovalType.LEGAL_REVIEW],
            auto_deny_on_timeout=True,
        )
        
        # Robotics Property Entry
        self._requirements[ReviewTrigger.ROBOTICS_PROPERTY_ENTRY] = ApprovalRequirement(
            requirement_id="req-robot",
            trigger=ReviewTrigger.ROBOTICS_PROPERTY_ENTRY,
            approval_types=[ApprovalType.COMMAND_STAFF, ApprovalType.LEGAL_REVIEW],
            minimum_approvals=2,
            requires_mfa=True,
            timeout_minutes=10,
            escalation_chain=[ApprovalType.CITY_MANAGER],
            auto_deny_on_timeout=True,
        )
        
        # Predictive Individual Action
        self._requirements[ReviewTrigger.PREDICTIVE_INDIVIDUAL_ACTION] = ApprovalRequirement(
            requirement_id="req-pred",
            trigger=ReviewTrigger.PREDICTIVE_INDIVIDUAL_ACTION,
            approval_types=[ApprovalType.SUPERVISOR],
            minimum_approvals=1,
            requires_mfa=False,
            timeout_minutes=30,
            escalation_chain=[ApprovalType.COMMAND_STAFF],
            auto_deny_on_timeout=False,
        )
        
        # Traffic Enforcement Automation
        self._requirements[ReviewTrigger.TRAFFIC_ENFORCEMENT_AUTOMATION] = ApprovalRequirement(
            requirement_id="req-traffic",
            trigger=ReviewTrigger.TRAFFIC_ENFORCEMENT_AUTOMATION,
            approval_types=[ApprovalType.SINGLE_OPERATOR],
            minimum_approvals=1,
            requires_mfa=False,
            timeout_minutes=60,
            escalation_chain=[ApprovalType.SUPERVISOR],
            auto_deny_on_timeout=False,
        )
        
        # Mass Alert
        self._requirements[ReviewTrigger.MASS_ALERT] = ApprovalRequirement(
            requirement_id="req-alert",
            trigger=ReviewTrigger.MASS_ALERT,
            approval_types=[ApprovalType.SUPERVISOR, ApprovalType.COMMAND_STAFF],
            minimum_approvals=2,
            requires_mfa=True,
            timeout_minutes=5,
            escalation_chain=[ApprovalType.EMERGENCY_DIRECTOR],
            auto_deny_on_timeout=False,
        )
        
        # Evacuation Order
        self._requirements[ReviewTrigger.EVACUATION_ORDER] = ApprovalRequirement(
            requirement_id="req-evac",
            trigger=ReviewTrigger.EVACUATION_ORDER,
            approval_types=[ApprovalType.COMMAND_STAFF, ApprovalType.EMERGENCY_DIRECTOR],
            minimum_approvals=2,
            requires_mfa=True,
            timeout_minutes=15,
            escalation_chain=[ApprovalType.CITY_MANAGER],
            auto_deny_on_timeout=False,
        )
        
        # High Risk Score
        self._requirements[ReviewTrigger.HIGH_RISK_SCORE] = ApprovalRequirement(
            requirement_id="req-risk",
            trigger=ReviewTrigger.HIGH_RISK_SCORE,
            approval_types=[ApprovalType.SUPERVISOR],
            minimum_approvals=1,
            requires_mfa=False,
            timeout_minutes=30,
            escalation_chain=[ApprovalType.COMMAND_STAFF],
            auto_deny_on_timeout=False,
        )
        
        # Constitutional Concern
        self._requirements[ReviewTrigger.CONSTITUTIONAL_CONCERN] = ApprovalRequirement(
            requirement_id="req-const",
            trigger=ReviewTrigger.CONSTITUTIONAL_CONCERN,
            approval_types=[ApprovalType.LEGAL_REVIEW, ApprovalType.COMMAND_STAFF],
            minimum_approvals=2,
            requires_mfa=True,
            timeout_minutes=60,
            escalation_chain=[ApprovalType.CITY_MANAGER],
            auto_deny_on_timeout=True,
        )
    
    def determine_trigger(
        self,
        action_category: ActionCategory,
        action_details: Dict[str, Any],
        risk_score: int,
        risk_category: RiskCategory,
    ) -> Optional[ReviewTrigger]:
        """Determine which review trigger applies to an action."""
        
        # Use of force
        if action_details.get("involves_force", False):
            return ReviewTrigger.USE_OF_FORCE
        
        # Surveillance escalation
        if action_category == ActionCategory.SURVEILLANCE:
            if action_details.get("escalation", False) or action_details.get("duration_hours", 0) > 4:
                return ReviewTrigger.SURVEILLANCE_ESCALATION
        
        # Drone property entry
        if action_category == ActionCategory.DRONE_OPERATION:
            if action_details.get("enters_private_property", False):
                return ReviewTrigger.DRONE_PROPERTY_ENTRY
        
        # Robotics property entry
        if action_category == ActionCategory.ROBOTICS_DEPLOYMENT:
            if action_details.get("enters_private_property", False):
                return ReviewTrigger.ROBOTICS_PROPERTY_ENTRY
        
        # Predictive individual action
        if action_category == ActionCategory.PREDICTIVE_POLICING:
            if action_details.get("targets_individual", False):
                return ReviewTrigger.PREDICTIVE_INDIVIDUAL_ACTION
        
        # Traffic enforcement automation
        if action_category == ActionCategory.TRAFFIC_CONTROL:
            if action_details.get("automated_enforcement", False):
                return ReviewTrigger.TRAFFIC_ENFORCEMENT_AUTOMATION
        
        # Mass alert
        if action_category == ActionCategory.MASS_ALERT:
            return ReviewTrigger.MASS_ALERT
        
        # Evacuation order
        if action_category == ActionCategory.EVACUATION:
            return ReviewTrigger.EVACUATION_ORDER
        
        # High risk score
        if risk_category in [RiskCategory.HIGH, RiskCategory.CRITICAL]:
            return ReviewTrigger.HIGH_RISK_SCORE
        
        # Constitutional concern (from validation)
        if action_details.get("constitutional_concern", False):
            return ReviewTrigger.CONSTITUTIONAL_CONCERN
        
        return None
    
    def create_approval_request(
        self,
        action_type: str,
        action_category: ActionCategory,
        action_details: Dict[str, Any],
        trigger: ReviewTrigger,
        risk_score: int,
        risk_category: RiskCategory,
        validation_result: ValidationResult,
        explanation: str,
    ) -> ApprovalRequest:
        """Create a new approval request."""
        request_id = f"approval-{uuid4().hex[:12]}"
        requirement = self._requirements[trigger]
        
        now = datetime.utcnow()
        expires_at = now + timedelta(minutes=requirement.timeout_minutes)
        
        request = ApprovalRequest(
            request_id=request_id,
            action_type=action_type,
            action_category=action_category,
            action_details=action_details,
            trigger=trigger,
            requirement=requirement,
            risk_score=risk_score,
            risk_category=risk_category,
            validation_result=validation_result,
            explanation=explanation,
            signatures=[],
            status=ApprovalStatus.PENDING,
            created_at=now,
            expires_at=expires_at,
        )
        
        self._requests[request_id] = request
        self._pending_requests[request_id] = request
        
        # Log creation
        self._log_audit(request_id, "request_created", None, None, {
            "trigger": trigger.value,
            "risk_score": risk_score,
            "expires_at": expires_at.isoformat(),
        })
        
        # Notify
        self._notify_new_request(request)
        
        return request
    
    def submit_approval(
        self,
        request_id: str,
        approver_id: str,
        approver_name: str,
        approver_role: str,
        approval_type: ApprovalType,
        decision: str,  # "approved" or "denied"
        mfa_verified: bool = False,
        ip_address: Optional[str] = None,
        device_id: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Submit an approval or denial for a request."""
        request = self._requests.get(request_id)
        if not request:
            return {"success": False, "error": "Request not found"}
        
        if request.status != ApprovalStatus.PENDING:
            return {"success": False, "error": f"Request is {request.status.value}"}
        
        if request.is_expired():
            self._handle_expiration(request)
            return {"success": False, "error": "Request has expired"}
        
        # Check MFA requirement
        if request.requirement.requires_mfa and not mfa_verified:
            return {"success": False, "error": "MFA verification required"}
        
        # Check if approver type is valid
        if approval_type not in request.requirement.approval_types:
            # Check escalation chain
            if approval_type not in request.requirement.escalation_chain:
                return {"success": False, "error": f"Approval type {approval_type.value} not authorized"}
        
        # Create signature
        signature_data = f"{request_id}:{approver_id}:{decision}:{datetime.utcnow().isoformat()}"
        signature_hash = hashlib.sha256(signature_data.encode()).hexdigest()
        
        signature = ApprovalSignature(
            signature_id=f"sig-{uuid4().hex[:8]}",
            approver_id=approver_id,
            approver_name=approver_name,
            approver_role=approver_role,
            approval_type=approval_type,
            decision=decision,
            timestamp=datetime.utcnow(),
            signature_hash=signature_hash,
            mfa_verified=mfa_verified,
            ip_address=ip_address,
            device_id=device_id,
            notes=notes,
        )
        
        request.signatures.append(signature)
        
        # Log the approval
        self._log_audit(request_id, f"approval_{decision}", approver_id, approver_name, {
            "approval_type": approval_type.value,
            "mfa_verified": mfa_verified,
            "signature_hash": signature_hash,
        })
        
        # Check if request is now complete
        if decision == "denied":
            request.status = ApprovalStatus.DENIED
            request.completed_at = datetime.utcnow()
            del self._pending_requests[request_id]
            self._log_audit(request_id, "request_denied", approver_id, approver_name, {})
            return {"success": True, "status": "denied", "request": request.to_dict()}
        
        if request.is_approved():
            request.status = ApprovalStatus.APPROVED
            request.completed_at = datetime.utcnow()
            del self._pending_requests[request_id]
            self._log_audit(request_id, "request_approved", None, None, {
                "total_approvals": len(request.signatures),
            })
            return {"success": True, "status": "approved", "request": request.to_dict()}
        
        return {
            "success": True,
            "status": "pending",
            "approvals_received": len([s for s in request.signatures if s.decision == "approved"]),
            "approvals_required": request.requirement.minimum_approvals,
            "request": request.to_dict(),
        }
    
    def escalate_request(self, request_id: str, reason: str) -> Dict[str, Any]:
        """Escalate a request to the next level in the chain."""
        request = self._requests.get(request_id)
        if not request:
            return {"success": False, "error": "Request not found"}
        
        if request.status != ApprovalStatus.PENDING:
            return {"success": False, "error": f"Request is {request.status.value}"}
        
        escalation_chain = request.requirement.escalation_chain
        if request.escalation_level >= len(escalation_chain):
            return {"success": False, "error": "No further escalation available"}
        
        # Get next escalation level
        next_level = escalation_chain[request.escalation_level]
        request.escalation_level += 1
        request.escalated_at = datetime.utcnow()
        request.status = ApprovalStatus.ESCALATED
        
        # Extend timeout
        request.expires_at = datetime.utcnow() + timedelta(
            minutes=request.requirement.timeout_minutes
        )
        
        self._log_audit(request_id, "request_escalated", None, None, {
            "escalation_level": request.escalation_level,
            "next_approval_type": next_level.value,
            "reason": reason,
        })
        
        # Reset status to pending for new approvers
        request.status = ApprovalStatus.PENDING
        
        return {
            "success": True,
            "escalation_level": request.escalation_level,
            "next_approval_type": next_level.value,
            "new_expires_at": request.expires_at.isoformat(),
        }
    
    def withdraw_request(self, request_id: str, reason: str) -> Dict[str, Any]:
        """Withdraw an approval request."""
        request = self._requests.get(request_id)
        if not request:
            return {"success": False, "error": "Request not found"}
        
        if request.status not in [ApprovalStatus.PENDING, ApprovalStatus.ESCALATED]:
            return {"success": False, "error": f"Cannot withdraw {request.status.value} request"}
        
        request.status = ApprovalStatus.WITHDRAWN
        request.completed_at = datetime.utcnow()
        
        if request_id in self._pending_requests:
            del self._pending_requests[request_id]
        
        self._log_audit(request_id, "request_withdrawn", None, None, {"reason": reason})
        
        return {"success": True, "status": "withdrawn"}
    
    def _handle_expiration(self, request: ApprovalRequest):
        """Handle an expired request."""
        if request.requirement.auto_deny_on_timeout:
            request.status = ApprovalStatus.DENIED
        else:
            request.status = ApprovalStatus.EXPIRED
        
        request.completed_at = datetime.utcnow()
        
        if request.request_id in self._pending_requests:
            del self._pending_requests[request.request_id]
        
        self._log_audit(request.request_id, "request_expired", None, None, {
            "auto_denied": request.requirement.auto_deny_on_timeout,
        })
    
    def check_expired_requests(self) -> List[ApprovalRequest]:
        """Check and handle expired requests."""
        expired = []
        for request_id, request in list(self._pending_requests.items()):
            if request.is_expired():
                self._handle_expiration(request)
                expired.append(request)
        return expired
    
    def get_request(self, request_id: str) -> Optional[ApprovalRequest]:
        """Get a request by ID."""
        return self._requests.get(request_id)
    
    def get_pending_requests(
        self,
        approval_type: Optional[ApprovalType] = None,
    ) -> List[ApprovalRequest]:
        """Get all pending requests, optionally filtered by approval type."""
        requests = list(self._pending_requests.values())
        
        if approval_type:
            requests = [
                r for r in requests
                if approval_type in r.requirement.approval_types or
                   approval_type in r.requirement.escalation_chain
            ]
        
        # Sort by risk score (highest first) then by creation time
        requests.sort(key=lambda r: (-r.risk_score, r.created_at))
        
        return requests
    
    def get_requests_by_status(
        self,
        status: ApprovalStatus,
        limit: int = 100,
    ) -> List[ApprovalRequest]:
        """Get requests by status."""
        requests = [r for r in self._requests.values() if r.status == status]
        requests.sort(key=lambda r: r.created_at, reverse=True)
        return requests[:limit]
    
    def get_requirement(self, trigger: ReviewTrigger) -> Optional[ApprovalRequirement]:
        """Get the approval requirement for a trigger."""
        return self._requirements.get(trigger)
    
    def get_all_requirements(self) -> List[ApprovalRequirement]:
        """Get all approval requirements."""
        return list(self._requirements.values())
    
    def _log_audit(
        self,
        request_id: str,
        event_type: str,
        actor_id: Optional[str],
        actor_name: Optional[str],
        details: Dict[str, Any],
    ):
        """Log an audit entry."""
        entry_data = f"{request_id}:{event_type}:{datetime.utcnow().isoformat()}"
        signature_hash = hashlib.sha256(entry_data.encode()).hexdigest()
        
        entry = WorkflowAuditEntry(
            entry_id=f"audit-{uuid4().hex[:8]}",
            request_id=request_id,
            event_type=event_type,
            actor_id=actor_id,
            actor_name=actor_name,
            details=details,
            timestamp=datetime.utcnow(),
            signature_hash=signature_hash,
        )
        
        self._audit_log.append(entry)
    
    def get_audit_log(
        self,
        request_id: Optional[str] = None,
        limit: int = 100,
    ) -> List[WorkflowAuditEntry]:
        """Get audit log entries."""
        entries = self._audit_log
        
        if request_id:
            entries = [e for e in entries if e.request_id == request_id]
        
        return entries[-limit:]
    
    def register_notification_callback(self, callback: Callable):
        """Register a callback for new request notifications."""
        self._notification_callbacks.append(callback)
    
    def _notify_new_request(self, request: ApprovalRequest):
        """Notify registered callbacks of a new request."""
        for callback in self._notification_callbacks:
            try:
                callback(request)
            except Exception:
                pass
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get gateway statistics."""
        total = len(self._requests)
        if total == 0:
            return {
                "total_requests": 0,
                "pending": 0,
                "approved": 0,
                "denied": 0,
                "expired": 0,
                "average_approval_time_minutes": 0,
            }
        
        by_status = {}
        for status in ApprovalStatus:
            by_status[status.value] = len([r for r in self._requests.values() if r.status == status])
        
        # Calculate average approval time
        completed = [r for r in self._requests.values() if r.completed_at and r.status == ApprovalStatus.APPROVED]
        if completed:
            avg_time = sum(
                (r.completed_at - r.created_at).total_seconds() / 60
                for r in completed
            ) / len(completed)
        else:
            avg_time = 0
        
        return {
            "total_requests": total,
            "by_status": by_status,
            "pending": by_status.get("pending", 0),
            "approved": by_status.get("approved", 0),
            "denied": by_status.get("denied", 0),
            "expired": by_status.get("expired", 0),
            "average_approval_time_minutes": round(avg_time, 2),
            "by_trigger": {
                trigger.value: len([r for r in self._requests.values() if r.trigger == trigger])
                for trigger in ReviewTrigger
            },
        }


# Singleton accessor
_hitl_gateway_instance: Optional[HumanInTheLoopGateway] = None


def get_human_in_loop_gateway() -> HumanInTheLoopGateway:
    """Get the singleton HumanInTheLoopGateway instance."""
    global _hitl_gateway_instance
    if _hitl_gateway_instance is None:
        _hitl_gateway_instance = HumanInTheLoopGateway()
    return _hitl_gateway_instance
