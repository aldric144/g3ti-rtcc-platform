"""
Phase 24: City Autonomy API Router

REST API endpoints for AI City Autonomy - Level-2 Autonomous City Operations.

Endpoints:
- Autonomous Actions: execute, pending, approve, deny, history
- Policy Engine: get, update, simulate
- Stabilizer: status, run
- Audit: query, get by ID
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from enum import Enum
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException, Query, Path, Body, Depends
import uuid

router = APIRouter(prefix="/api/autonomy", tags=["City Autonomy"])


# ============================================================================
# Request/Response Models
# ============================================================================

class ActionLevelEnum(str, Enum):
    LEVEL_0 = "level_0"
    LEVEL_1 = "level_1"
    LEVEL_2 = "level_2"


class ActionCategoryEnum(str, Enum):
    TRAFFIC_CONTROL = "traffic_control"
    PATROL_DEPLOYMENT = "patrol_deployment"
    RESOURCE_ALLOCATION = "resource_allocation"
    NOTIFICATION = "notification"
    EMERGENCY_RESPONSE = "emergency_response"
    UTILITY_MANAGEMENT = "utility_management"
    CROWD_MANAGEMENT = "crowd_management"
    EVACUATION = "evacuation"
    INFRASTRUCTURE = "infrastructure"
    OBSERVATION = "observation"


class ActionStatusEnum(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    ESCALATED = "escalated"


class RiskLevelEnum(str, Enum):
    MINIMAL = "minimal"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class PolicyScopeEnum(str, Enum):
    GLOBAL = "global"
    CITY = "city"
    DEPARTMENT = "department"
    SCENARIO = "scenario"


class PolicyTypeEnum(str, Enum):
    TRAFFIC = "traffic"
    PATROL = "patrol"
    EMS = "ems"
    FIRE = "fire"
    UTILITY = "utility"
    EMERGENCY = "emergency"
    RESOURCE = "resource"
    NOTIFICATION = "notification"
    CROWD = "crowd"
    EVACUATION = "evacuation"


class PolicyStatusEnum(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    TESTING = "testing"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"


class AuditEventTypeEnum(str, Enum):
    ACTION_CREATED = "action_created"
    ACTION_EXECUTED = "action_executed"
    ACTION_COMPLETED = "action_completed"
    ACTION_FAILED = "action_failed"
    ACTION_APPROVED = "action_approved"
    ACTION_DENIED = "action_denied"
    ACTION_ESCALATED = "action_escalated"
    HUMAN_OVERRIDE = "human_override"
    POLICY_ACTIVATED = "policy_activated"
    EMERGENCY_OVERRIDE_ACTIVATED = "emergency_override_activated"
    ANOMALY_DETECTED = "anomaly_detected"
    STABILIZATION_ACTION = "stabilization_action"


class AuditSeverityEnum(str, Enum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ReportPeriodEnum(str, Enum):
    HOURLY = "hourly"
    DAILY_24H = "24h"
    WEEKLY_7D = "7d"
    MONTHLY_30D = "30d"


class ComplianceStandardEnum(str, Enum):
    CJIS = "cjis"
    NIST = "nist"
    FL_STATE = "fl_state"
    HIPAA = "hipaa"


# Request Models
class ExecuteActionRequest(BaseModel):
    action_type: str = Field(..., description="Type of action to execute")
    title: str = Field(..., description="Action title")
    description: str = Field("", description="Action description")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Action parameters")
    priority: int = Field(5, ge=1, le=10, description="Action priority (1-10)")
    timeout_minutes: int = Field(30, ge=1, le=1440, description="Action timeout in minutes")
    risk_level: Optional[RiskLevelEnum] = Field(None, description="Risk level override")
    domain: Optional[str] = Field(None, description="Domain for action categorization")


class ApproveActionRequest(BaseModel):
    approved_by: str = Field(..., description="ID of approving user")
    notes: Optional[str] = Field(None, description="Approval notes")


class DenyActionRequest(BaseModel):
    denied_by: str = Field(..., description="ID of denying user")
    reason: str = Field(..., description="Reason for denial")


class EscalateActionRequest(BaseModel):
    escalate_to: str = Field(..., description="ID of user/role to escalate to")
    reason: str = Field(..., description="Reason for escalation")


class PolicyRuleRequest(BaseModel):
    name: str = Field(..., description="Rule name")
    description: str = Field("", description="Rule description")
    condition: str = Field(..., description="Rule condition expression")
    action: str = Field(..., description="Action to take when condition is met")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Action parameters")
    priority: int = Field(5, ge=1, le=10, description="Rule priority")
    enabled: bool = Field(True, description="Whether rule is enabled")


class PolicyThresholdRequest(BaseModel):
    name: str = Field(..., description="Threshold name")
    metric: str = Field(..., description="Metric to monitor")
    operator: str = Field(..., description="Comparison operator (gt, lt, gte, lte, eq, neq)")
    value: float = Field(..., description="Threshold value")
    unit: str = Field(..., description="Unit of measurement")
    action_on_breach: str = Field(..., description="Action when threshold is breached")
    cooldown_minutes: int = Field(15, ge=1, description="Cooldown period in minutes")


class CreatePolicyRequest(BaseModel):
    name: str = Field(..., description="Policy name")
    description: str = Field("", description="Policy description")
    policy_type: PolicyTypeEnum = Field(..., description="Type of policy")
    scope: PolicyScopeEnum = Field(..., description="Policy scope")
    scope_id: Optional[str] = Field(None, description="Scope ID (department/scenario)")
    rules: List[PolicyRuleRequest] = Field(default_factory=list, description="Policy rules")
    thresholds: List[PolicyThresholdRequest] = Field(default_factory=list, description="Policy thresholds")
    parent_policy_id: Optional[str] = Field(None, description="Parent policy ID")
    tags: List[str] = Field(default_factory=list, description="Policy tags")
    created_by: str = Field(..., description="Creator ID")


class UpdatePolicyRequest(BaseModel):
    name: Optional[str] = Field(None, description="Policy name")
    description: Optional[str] = Field(None, description="Policy description")
    rules: Optional[List[PolicyRuleRequest]] = Field(None, description="Policy rules")
    thresholds: Optional[List[PolicyThresholdRequest]] = Field(None, description="Policy thresholds")
    status: Optional[PolicyStatusEnum] = Field(None, description="Policy status")
    tags: Optional[List[str]] = Field(None, description="Policy tags")
    updated_by: str = Field(..., description="Updater ID")
    change_summary: str = Field(..., description="Summary of changes")


class SimulatePolicyRequest(BaseModel):
    policy_id: str = Field(..., description="Policy ID to simulate")
    scenario: Dict[str, Any] = Field(..., description="Scenario data for simulation")


class ActivateEmergencyOverrideRequest(BaseModel):
    override_id: str = Field(..., description="Emergency override ID")
    activated_by: str = Field(..., description="ID of activating user")


class SensorReadingRequest(BaseModel):
    sensor_id: str = Field(..., description="Sensor ID")
    domain: str = Field(..., description="Monitoring domain")
    metric: str = Field(..., description="Metric name")
    value: float = Field(..., description="Metric value")
    unit: str = Field(..., description="Unit of measurement")
    location: Optional[Dict[str, float]] = Field(None, description="Location coordinates")
    quality: float = Field(1.0, ge=0, le=1, description="Data quality score")


class GenerateReportRequest(BaseModel):
    compliance_standard: ComplianceStandardEnum = Field(..., description="Compliance standard")
    period: ReportPeriodEnum = Field(..., description="Report period")
    generated_by: str = Field(..., description="Generator ID")
    start_date: Optional[datetime] = Field(None, description="Custom start date")
    end_date: Optional[datetime] = Field(None, description="Custom end date")


# Response Models
class ActionResponse(BaseModel):
    action_id: str
    action_type: str
    category: str
    level: int
    title: str
    description: str
    parameters: Dict[str, Any]
    risk_level: str
    risk_score: float
    status: str
    explainability: Dict[str, Any]
    created_at: str
    approved_at: Optional[str]
    approved_by: Optional[str]
    executed_at: Optional[str]
    completed_at: Optional[str]
    priority: int


class PendingActionsResponse(BaseModel):
    actions: List[ActionResponse]
    total_count: int
    page: int
    page_size: int


class ActionHistoryResponse(BaseModel):
    actions: List[ActionResponse]
    total_count: int
    page: int
    page_size: int


class PolicyResponse(BaseModel):
    policy_id: str
    name: str
    description: str
    policy_type: str
    scope: str
    scope_id: Optional[str]
    rules: List[Dict[str, Any]]
    thresholds: List[Dict[str, Any]]
    status: str
    version: int
    created_at: str
    updated_at: str
    created_by: str
    tags: List[str]


class PolicyListResponse(BaseModel):
    policies: List[PolicyResponse]
    total_count: int


class SimulationResultResponse(BaseModel):
    simulation_id: str
    policy_id: str
    scenario: Dict[str, Any]
    triggered_rules: List[str]
    actions_generated: List[Dict[str, Any]]
    conflicts_detected: List[Dict[str, Any]]
    metrics: Dict[str, float]
    success: bool
    error_message: Optional[str]
    duration_ms: float


class StabilizerStatusResponse(BaseModel):
    status: str
    circuit_breaker_open: bool
    consecutive_failures: int
    active_anomalies: int
    cascade_predictions: int
    pending_actions: int
    city_config: Dict[str, Any]


class AnomalyResponse(BaseModel):
    anomaly_id: str
    domain: str
    anomaly_type: str
    severity: str
    title: str
    description: str
    affected_area: Optional[str]
    metrics: Dict[str, float]
    confidence: float
    detected_at: str
    cascade_risk: float


class StabilizationActionResponse(BaseModel):
    action_id: str
    action_type: str
    title: str
    description: str
    target_domain: str
    priority: int
    requires_approval: bool
    created_at: str
    executed_at: Optional[str]


class AuditEntryResponse(BaseModel):
    entry_id: str
    event_type: str
    severity: str
    timestamp: str
    actor_id: str
    actor_type: str
    actor_name: str
    resource_type: str
    resource_id: str
    description: str
    compliance_tags: List[str]
    signature: Optional[str]


class AuditQueryResponse(BaseModel):
    entries: List[AuditEntryResponse]
    total_count: int
    page: int
    page_size: int


class ComplianceReportResponse(BaseModel):
    report_id: str
    report_type: str
    period: str
    compliance_standard: str
    generated_at: str
    summary: Dict[str, Any]
    findings: List[Dict[str, Any]]
    recommendations: List[str]


class AutonomySummaryResponse(BaseModel):
    summary_id: str
    period: str
    start_date: str
    end_date: str
    total_actions: int
    actions_by_level: Dict[str, int]
    actions_by_status: Dict[str, int]
    human_overrides: int
    denied_actions: int
    ai_vs_human_ratio: float


class EngineStatisticsResponse(BaseModel):
    action_engine: Dict[str, Any]
    policy_engine: Dict[str, Any]
    stabilizer: Dict[str, Any]
    audit_engine: Dict[str, Any]


# ============================================================================
# Audit Logging Helper
# ============================================================================

def log_api_access(
    endpoint: str,
    method: str,
    user_id: str = "api_user",
    details: Optional[Dict[str, Any]] = None,
):
    """Log API access for CJIS compliance."""
    from backend.app.city_autonomy.audit_engine import get_audit_engine, AuditEventType
    
    audit_engine = get_audit_engine()
    audit_engine.log_event(
        event_type=AuditEventType.ACCESS_GRANTED,
        actor_id=user_id,
        actor_type="human",
        actor_name=user_id,
        resource_type="api_endpoint",
        resource_id=endpoint,
        description=f"{method} {endpoint}",
        details=details or {},
    )


# ============================================================================
# Autonomous Actions Endpoints
# ============================================================================

@router.post("/action/execute", response_model=ActionResponse)
async def execute_action(request: ExecuteActionRequest):
    """
    Execute an autonomous action.
    
    Creates and processes an action based on the provided recommendation.
    Level 1 actions are auto-executed, Level 2 actions require approval.
    """
    from backend.app.city_autonomy import get_autonomous_action_engine
    from backend.app.city_autonomy.audit_engine import get_audit_engine, AuditEventType
    
    engine = get_autonomous_action_engine()
    audit_engine = get_audit_engine()
    
    recommendation = {
        "action_type": request.action_type,
        "title": request.title,
        "description": request.description,
        "parameters": request.parameters,
        "priority": request.priority,
        "timeout_minutes": request.timeout_minutes,
        "risk_level": request.risk_level.value if request.risk_level else "low",
        "domain": request.domain or "",
    }
    
    action = engine.interpret_recommendation(recommendation)
    
    # Log the action creation
    audit_engine.log_event(
        event_type=AuditEventType.ACTION_CREATED,
        actor_id="api_user",
        actor_type="system",
        actor_name="Autonomy API",
        action_id=action.action_id,
        resource_type="autonomous_action",
        resource_id=action.action_id,
        description=f"Action created: {action.title}",
        details={
            "action_type": action.action_type,
            "level": action.level.value,
            "category": action.category.value,
            "risk_score": action.risk_score,
        },
    )
    
    return ActionResponse(
        action_id=action.action_id,
        action_type=action.action_type,
        category=action.category.value,
        level=action.level.value,
        title=action.title,
        description=action.description,
        parameters=action.parameters,
        risk_level=action.risk_level.value,
        risk_score=action.risk_score,
        status=action.status.value,
        explainability=action.explainability.to_dict(),
        created_at=action.created_at.isoformat(),
        approved_at=action.approved_at.isoformat() if action.approved_at else None,
        approved_by=action.approved_by,
        executed_at=action.executed_at.isoformat() if action.executed_at else None,
        completed_at=action.completed_at.isoformat() if action.completed_at else None,
        priority=action.priority,
    )


@router.get("/action/pending", response_model=PendingActionsResponse)
async def get_pending_actions(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Page size"),
):
    """
    Get all pending actions requiring approval.
    
    Returns Level 2 actions that are awaiting operator approval.
    """
    from backend.app.city_autonomy import get_autonomous_action_engine
    
    engine = get_autonomous_action_engine()
    pending = engine.get_pending_actions()
    
    # Paginate
    start = (page - 1) * page_size
    end = start + page_size
    paginated = pending[start:end]
    
    actions = [
        ActionResponse(
            action_id=a.action_id,
            action_type=a.action_type,
            category=a.category.value,
            level=a.level.value,
            title=a.title,
            description=a.description,
            parameters=a.parameters,
            risk_level=a.risk_level.value,
            risk_score=a.risk_score,
            status=a.status.value,
            explainability=a.explainability.to_dict(),
            created_at=a.created_at.isoformat(),
            approved_at=a.approved_at.isoformat() if a.approved_at else None,
            approved_by=a.approved_by,
            executed_at=a.executed_at.isoformat() if a.executed_at else None,
            completed_at=a.completed_at.isoformat() if a.completed_at else None,
            priority=a.priority,
        )
        for a in paginated
    ]
    
    return PendingActionsResponse(
        actions=actions,
        total_count=len(pending),
        page=page,
        page_size=page_size,
    )


@router.post("/action/approve/{action_id}")
async def approve_action(
    action_id: str = Path(..., description="Action ID to approve"),
    request: ApproveActionRequest = Body(...),
):
    """
    Approve a pending action.
    
    Approves and executes a Level 2 action that was awaiting approval.
    """
    from backend.app.city_autonomy import get_autonomous_action_engine
    from backend.app.city_autonomy.audit_engine import get_audit_engine, AuditEventType
    
    engine = get_autonomous_action_engine()
    audit_engine = get_audit_engine()
    
    action = engine.get_action(action_id)
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")
    
    success = engine.approve_action(action_id, request.approved_by, request.notes)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to approve action")
    
    # Log the approval
    audit_engine.log_event(
        event_type=AuditEventType.ACTION_APPROVED,
        actor_id=request.approved_by,
        actor_type="human",
        actor_name=request.approved_by,
        action_id=action_id,
        resource_type="autonomous_action",
        resource_id=action_id,
        description=f"Action approved: {action.title}",
        details={"notes": request.notes},
    )
    
    return {"status": "approved", "action_id": action_id}


@router.post("/action/deny/{action_id}")
async def deny_action(
    action_id: str = Path(..., description="Action ID to deny"),
    request: DenyActionRequest = Body(...),
):
    """
    Deny a pending action.
    
    Denies a Level 2 action with a reason.
    """
    from backend.app.city_autonomy import get_autonomous_action_engine
    from backend.app.city_autonomy.audit_engine import get_audit_engine, AuditEventType
    
    engine = get_autonomous_action_engine()
    audit_engine = get_audit_engine()
    
    action = engine.get_action(action_id)
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")
    
    success = engine.deny_action(action_id, request.denied_by, request.reason)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to deny action")
    
    # Log the denial
    audit_engine.log_event(
        event_type=AuditEventType.ACTION_DENIED,
        actor_id=request.denied_by,
        actor_type="human",
        actor_name=request.denied_by,
        action_id=action_id,
        resource_type="autonomous_action",
        resource_id=action_id,
        description=f"Action denied: {action.title}",
        details={"reason": request.reason},
    )
    
    return {"status": "denied", "action_id": action_id, "reason": request.reason}


@router.post("/action/escalate/{action_id}")
async def escalate_action(
    action_id: str = Path(..., description="Action ID to escalate"),
    request: EscalateActionRequest = Body(...),
):
    """
    Escalate an action to a higher authority.
    """
    from backend.app.city_autonomy import get_autonomous_action_engine
    from backend.app.city_autonomy.audit_engine import get_audit_engine, AuditEventType
    
    engine = get_autonomous_action_engine()
    audit_engine = get_audit_engine()
    
    action = engine.get_action(action_id)
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")
    
    success = engine.escalate_action(action_id, request.escalate_to, request.reason)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to escalate action")
    
    # Log the escalation
    audit_engine.log_event(
        event_type=AuditEventType.ACTION_ESCALATED,
        actor_id="api_user",
        actor_type="human",
        actor_name="API User",
        action_id=action_id,
        resource_type="autonomous_action",
        resource_id=action_id,
        description=f"Action escalated: {action.title}",
        details={"escalate_to": request.escalate_to, "reason": request.reason},
    )
    
    return {"status": "escalated", "action_id": action_id, "escalated_to": request.escalate_to}


@router.get("/action/history", response_model=ActionHistoryResponse)
async def get_action_history(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Page size"),
    category: Optional[ActionCategoryEnum] = Query(None, description="Filter by category"),
    status: Optional[ActionStatusEnum] = Query(None, description="Filter by status"),
):
    """
    Get action history with optional filters.
    """
    from backend.app.city_autonomy import get_autonomous_action_engine, ActionCategory, ActionStatus
    
    engine = get_autonomous_action_engine()
    
    cat = ActionCategory(category.value) if category else None
    stat = ActionStatus(status.value) if status else None
    
    history = engine.get_action_history(
        limit=page_size * page,
        category=cat,
        status=stat,
    )
    
    # Paginate
    start = (page - 1) * page_size
    end = start + page_size
    paginated = history[start:end]
    
    actions = [
        ActionResponse(
            action_id=a.action_id,
            action_type=a.action_type,
            category=a.category.value,
            level=a.level.value,
            title=a.title,
            description=a.description,
            parameters=a.parameters,
            risk_level=a.risk_level.value,
            risk_score=a.risk_score,
            status=a.status.value,
            explainability=a.explainability.to_dict(),
            created_at=a.created_at.isoformat(),
            approved_at=a.approved_at.isoformat() if a.approved_at else None,
            approved_by=a.approved_by,
            executed_at=a.executed_at.isoformat() if a.executed_at else None,
            completed_at=a.completed_at.isoformat() if a.completed_at else None,
            priority=a.priority,
        )
        for a in paginated
    ]
    
    return ActionHistoryResponse(
        actions=actions,
        total_count=len(history),
        page=page,
        page_size=page_size,
    )


@router.get("/action/{action_id}", response_model=ActionResponse)
async def get_action(action_id: str = Path(..., description="Action ID")):
    """
    Get a specific action by ID.
    """
    from backend.app.city_autonomy import get_autonomous_action_engine
    
    engine = get_autonomous_action_engine()
    action = engine.get_action(action_id)
    
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")
    
    return ActionResponse(
        action_id=action.action_id,
        action_type=action.action_type,
        category=action.category.value,
        level=action.level.value,
        title=action.title,
        description=action.description,
        parameters=action.parameters,
        risk_level=action.risk_level.value,
        risk_score=action.risk_score,
        status=action.status.value,
        explainability=action.explainability.to_dict(),
        created_at=action.created_at.isoformat(),
        approved_at=action.approved_at.isoformat() if action.approved_at else None,
        approved_by=action.approved_by,
        executed_at=action.executed_at.isoformat() if action.executed_at else None,
        completed_at=action.completed_at.isoformat() if action.completed_at else None,
        priority=action.priority,
    )


# ============================================================================
# Policy Engine Endpoints
# ============================================================================

@router.get("/policy", response_model=PolicyListResponse)
async def get_policies(
    policy_type: Optional[PolicyTypeEnum] = Query(None, description="Filter by type"),
    scope: Optional[PolicyScopeEnum] = Query(None, description="Filter by scope"),
    status: Optional[PolicyStatusEnum] = Query(None, description="Filter by status"),
):
    """
    Get all policies with optional filters.
    """
    from backend.app.city_autonomy.policy_engine import get_policy_engine, PolicyType, PolicyScope, PolicyStatus
    
    engine = get_policy_engine()
    
    pt = PolicyType(policy_type.value) if policy_type else None
    ps = PolicyScope(scope.value) if scope else None
    pst = PolicyStatus(status.value) if status else None
    
    policies = engine.get_policies(policy_type=pt, scope=ps, status=pst)
    
    policy_responses = [
        PolicyResponse(
            policy_id=p.policy_id,
            name=p.name,
            description=p.description,
            policy_type=p.policy_type.value,
            scope=p.scope.value,
            scope_id=p.scope_id,
            rules=[r.to_dict() for r in p.rules],
            thresholds=[t.to_dict() for t in p.thresholds],
            status=p.status.value,
            version=p.version,
            created_at=p.created_at.isoformat(),
            updated_at=p.updated_at.isoformat(),
            created_by=p.created_by,
            tags=p.tags,
        )
        for p in policies
    ]
    
    return PolicyListResponse(
        policies=policy_responses,
        total_count=len(policies),
    )


@router.get("/policy/{policy_id}", response_model=PolicyResponse)
async def get_policy(policy_id: str = Path(..., description="Policy ID")):
    """
    Get a specific policy by ID.
    """
    from backend.app.city_autonomy.policy_engine import get_policy_engine
    
    engine = get_policy_engine()
    policy = engine.get_policy(policy_id)
    
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    
    return PolicyResponse(
        policy_id=policy.policy_id,
        name=policy.name,
        description=policy.description,
        policy_type=policy.policy_type.value,
        scope=policy.scope.value,
        scope_id=policy.scope_id,
        rules=[r.to_dict() for r in policy.rules],
        thresholds=[t.to_dict() for t in policy.thresholds],
        status=policy.status.value,
        version=policy.version,
        created_at=policy.created_at.isoformat(),
        updated_at=policy.updated_at.isoformat(),
        created_by=policy.created_by,
        tags=policy.tags,
    )


@router.post("/policy", response_model=PolicyResponse)
async def create_policy(request: CreatePolicyRequest):
    """
    Create a new policy.
    """
    from backend.app.city_autonomy.policy_engine import (
        get_policy_engine, PolicyType, PolicyScope, PolicyRule, PolicyThreshold
    )
    from backend.app.city_autonomy.audit_engine import get_audit_engine, AuditEventType
    
    engine = get_policy_engine()
    audit_engine = get_audit_engine()
    
    rules = [
        PolicyRule(
            rule_id=f"rule-{uuid.uuid4().hex[:8]}",
            name=r.name,
            description=r.description,
            condition=r.condition,
            action=r.action,
            parameters=r.parameters,
            priority=r.priority,
            enabled=r.enabled,
        )
        for r in request.rules
    ]
    
    thresholds = [
        PolicyThreshold(
            threshold_id=f"thresh-{uuid.uuid4().hex[:8]}",
            name=t.name,
            metric=t.metric,
            operator=t.operator,
            value=t.value,
            unit=t.unit,
            action_on_breach=t.action_on_breach,
            cooldown_minutes=t.cooldown_minutes,
        )
        for t in request.thresholds
    ]
    
    policy = engine.create_policy(
        name=request.name,
        description=request.description,
        policy_type=PolicyType(request.policy_type.value),
        scope=PolicyScope(request.scope.value),
        rules=rules,
        thresholds=thresholds,
        created_by=request.created_by,
        scope_id=request.scope_id,
        parent_policy_id=request.parent_policy_id,
        tags=request.tags,
    )
    
    # Log policy creation
    audit_engine.log_event(
        event_type=AuditEventType.POLICY_ACTIVATED,
        actor_id=request.created_by,
        actor_type="human",
        actor_name=request.created_by,
        resource_type="policy",
        resource_id=policy.policy_id,
        description=f"Policy created: {policy.name}",
        details={"policy_type": policy.policy_type.value, "scope": policy.scope.value},
    )
    
    return PolicyResponse(
        policy_id=policy.policy_id,
        name=policy.name,
        description=policy.description,
        policy_type=policy.policy_type.value,
        scope=policy.scope.value,
        scope_id=policy.scope_id,
        rules=[r.to_dict() for r in policy.rules],
        thresholds=[t.to_dict() for t in policy.thresholds],
        status=policy.status.value,
        version=policy.version,
        created_at=policy.created_at.isoformat(),
        updated_at=policy.updated_at.isoformat(),
        created_by=policy.created_by,
        tags=policy.tags,
    )


@router.put("/policy/{policy_id}", response_model=PolicyResponse)
async def update_policy(
    policy_id: str = Path(..., description="Policy ID"),
    request: UpdatePolicyRequest = Body(...),
):
    """
    Update an existing policy.
    """
    from backend.app.city_autonomy.policy_engine import (
        get_policy_engine, PolicyStatus, PolicyRule, PolicyThreshold
    )
    
    engine = get_policy_engine()
    
    rules = None
    if request.rules is not None:
        rules = [
            PolicyRule(
                rule_id=f"rule-{uuid.uuid4().hex[:8]}",
                name=r.name,
                description=r.description,
                condition=r.condition,
                action=r.action,
                parameters=r.parameters,
                priority=r.priority,
                enabled=r.enabled,
            )
            for r in request.rules
        ]
    
    thresholds = None
    if request.thresholds is not None:
        thresholds = [
            PolicyThreshold(
                threshold_id=f"thresh-{uuid.uuid4().hex[:8]}",
                name=t.name,
                metric=t.metric,
                operator=t.operator,
                value=t.value,
                unit=t.unit,
                action_on_breach=t.action_on_breach,
                cooldown_minutes=t.cooldown_minutes,
            )
            for t in request.thresholds
        ]
    
    status = PolicyStatus(request.status.value) if request.status else None
    
    policy = engine.update_policy(
        policy_id=policy_id,
        updated_by=request.updated_by,
        change_summary=request.change_summary,
        name=request.name,
        description=request.description,
        rules=rules,
        thresholds=thresholds,
        status=status,
        tags=request.tags,
    )
    
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    
    return PolicyResponse(
        policy_id=policy.policy_id,
        name=policy.name,
        description=policy.description,
        policy_type=policy.policy_type.value,
        scope=policy.scope.value,
        scope_id=policy.scope_id,
        rules=[r.to_dict() for r in policy.rules],
        thresholds=[t.to_dict() for t in policy.thresholds],
        status=policy.status.value,
        version=policy.version,
        created_at=policy.created_at.isoformat(),
        updated_at=policy.updated_at.isoformat(),
        created_by=policy.created_by,
        tags=policy.tags,
    )


@router.post("/policy/simulate", response_model=SimulationResultResponse)
async def simulate_policy(request: SimulatePolicyRequest):
    """
    Simulate a policy against a scenario.
    
    Tests policy rules and thresholds without executing actions.
    """
    from backend.app.city_autonomy.policy_engine import get_policy_engine
    
    engine = get_policy_engine()
    result = engine.simulate_policy(request.policy_id, request.scenario)
    
    return SimulationResultResponse(
        simulation_id=result.simulation_id,
        policy_id=result.policy_id,
        scenario=result.scenario,
        triggered_rules=result.triggered_rules,
        actions_generated=result.actions_generated,
        conflicts_detected=[c.to_dict() for c in result.conflicts_detected],
        metrics=result.metrics,
        success=result.success,
        error_message=result.error_message,
        duration_ms=result.duration_ms,
    )


@router.post("/policy/{policy_id}/activate")
async def activate_policy(policy_id: str = Path(..., description="Policy ID")):
    """
    Activate a policy.
    """
    from backend.app.city_autonomy.policy_engine import get_policy_engine
    
    engine = get_policy_engine()
    success = engine.activate_policy(policy_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Policy not found")
    
    return {"status": "activated", "policy_id": policy_id}


@router.post("/policy/{policy_id}/deactivate")
async def deactivate_policy(policy_id: str = Path(..., description="Policy ID")):
    """
    Deactivate a policy.
    """
    from backend.app.city_autonomy.policy_engine import get_policy_engine
    
    engine = get_policy_engine()
    success = engine.deactivate_policy(policy_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Policy not found")
    
    return {"status": "deactivated", "policy_id": policy_id}


@router.get("/policy/emergency-overrides")
async def get_emergency_overrides():
    """
    Get all emergency override configurations.
    """
    from backend.app.city_autonomy.policy_engine import get_policy_engine
    
    engine = get_policy_engine()
    overrides = engine.get_all_emergency_overrides()
    
    return {
        "overrides": [o.to_dict() for o in overrides],
        "active_overrides": [o.to_dict() for o in engine.get_active_overrides()],
    }


@router.post("/policy/emergency-override/activate")
async def activate_emergency_override(request: ActivateEmergencyOverrideRequest):
    """
    Activate an emergency override.
    """
    from backend.app.city_autonomy.policy_engine import get_policy_engine
    from backend.app.city_autonomy.audit_engine import get_audit_engine, AuditEventType
    
    engine = get_policy_engine()
    audit_engine = get_audit_engine()
    
    success = engine.activate_emergency_override(request.override_id, request.activated_by)
    
    if not success:
        raise HTTPException(status_code=400, detail="Failed to activate emergency override")
    
    # Log emergency override activation
    audit_engine.log_event(
        event_type=AuditEventType.EMERGENCY_OVERRIDE_ACTIVATED,
        actor_id=request.activated_by,
        actor_type="human",
        actor_name=request.activated_by,
        resource_type="emergency_override",
        resource_id=request.override_id,
        description=f"Emergency override activated: {request.override_id}",
        details={},
    )
    
    return {"status": "activated", "override_id": request.override_id}


@router.post("/policy/emergency-override/{override_id}/deactivate")
async def deactivate_emergency_override(
    override_id: str = Path(..., description="Override ID"),
):
    """
    Deactivate an emergency override.
    """
    from backend.app.city_autonomy.policy_engine import get_policy_engine
    
    engine = get_policy_engine()
    success = engine.deactivate_emergency_override(override_id)
    
    if not success:
        raise HTTPException(status_code=400, detail="Failed to deactivate emergency override")
    
    return {"status": "deactivated", "override_id": override_id}


# ============================================================================
# Stabilizer Endpoints
# ============================================================================

@router.get("/stabilizer/status", response_model=StabilizerStatusResponse)
async def get_stabilizer_status():
    """
    Get the current status of the city stabilizer.
    """
    from backend.app.city_autonomy.stabilizer import get_city_stabilizer
    
    stabilizer = get_city_stabilizer()
    status = stabilizer.get_status()
    
    return StabilizerStatusResponse(**status)


@router.post("/stabilizer/run")
async def run_stabilization_cycle():
    """
    Run a stabilization cycle.
    
    Processes pending actions and executes auto-approved stabilization measures.
    """
    from backend.app.city_autonomy.stabilizer import get_city_stabilizer
    
    stabilizer = get_city_stabilizer()
    result = stabilizer.run_stabilization_cycle()
    
    return result


@router.get("/stabilizer/anomalies")
async def get_active_anomalies():
    """
    Get all active anomalies.
    """
    from backend.app.city_autonomy.stabilizer import get_city_stabilizer
    
    stabilizer = get_city_stabilizer()
    anomalies = stabilizer.get_active_anomalies()
    
    return {
        "anomalies": [a.to_dict() for a in anomalies],
        "total_count": len(anomalies),
    }


@router.get("/stabilizer/cascade-predictions")
async def get_cascade_predictions():
    """
    Get cascade failure predictions.
    """
    from backend.app.city_autonomy.stabilizer import get_city_stabilizer
    
    stabilizer = get_city_stabilizer()
    predictions = stabilizer.get_cascade_predictions()
    
    return {
        "predictions": [p.to_dict() for p in predictions],
        "total_count": len(predictions),
    }


@router.get("/stabilizer/actions")
async def get_stabilization_actions(
    pending_only: bool = Query(False, description="Only show pending actions"),
):
    """
    Get stabilization actions.
    """
    from backend.app.city_autonomy.stabilizer import get_city_stabilizer
    
    stabilizer = get_city_stabilizer()
    actions = stabilizer.get_stabilization_actions(pending_only=pending_only)
    
    return {
        "actions": [a.to_dict() for a in actions],
        "total_count": len(actions),
    }


@router.post("/stabilizer/sensor-reading")
async def ingest_sensor_reading(request: SensorReadingRequest):
    """
    Ingest a sensor reading for anomaly detection.
    """
    from backend.app.city_autonomy.stabilizer import get_city_stabilizer, SensorReading, MonitoringDomain
    
    stabilizer = get_city_stabilizer()
    
    reading = SensorReading(
        sensor_id=request.sensor_id,
        domain=MonitoringDomain(request.domain),
        metric=request.metric,
        value=request.value,
        unit=request.unit,
        location=request.location,
        quality=request.quality,
    )
    
    stabilizer.ingest_sensor_reading(reading)
    
    return {"status": "ingested", "sensor_id": request.sensor_id}


@router.post("/stabilizer/anomaly/{anomaly_id}/resolve")
async def resolve_anomaly(anomaly_id: str = Path(..., description="Anomaly ID")):
    """
    Mark an anomaly as resolved.
    """
    from backend.app.city_autonomy.stabilizer import get_city_stabilizer
    
    stabilizer = get_city_stabilizer()
    success = stabilizer.resolve_anomaly(anomaly_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Anomaly not found")
    
    return {"status": "resolved", "anomaly_id": anomaly_id}


@router.post("/stabilizer/action/{action_id}/execute")
async def execute_stabilization_action(action_id: str = Path(..., description="Action ID")):
    """
    Execute a stabilization action.
    """
    from backend.app.city_autonomy.stabilizer import get_city_stabilizer
    
    stabilizer = get_city_stabilizer()
    success = stabilizer.execute_stabilization_action(action_id)
    
    if not success:
        raise HTTPException(status_code=400, detail="Failed to execute action")
    
    return {"status": "executed", "action_id": action_id}


@router.post("/stabilizer/circuit-breaker/reset")
async def reset_circuit_breaker():
    """
    Reset the stabilizer circuit breaker.
    """
    from backend.app.city_autonomy.stabilizer import get_city_stabilizer
    
    stabilizer = get_city_stabilizer()
    stabilizer.reset_circuit_breaker()
    
    return {"status": "reset"}


# ============================================================================
# Audit Endpoints
# ============================================================================

@router.get("/audit", response_model=AuditQueryResponse)
async def query_audit_entries(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Page size"),
    event_type: Optional[AuditEventTypeEnum] = Query(None, description="Filter by event type"),
    severity: Optional[AuditSeverityEnum] = Query(None, description="Filter by severity"),
    actor_id: Optional[str] = Query(None, description="Filter by actor ID"),
    resource_type: Optional[str] = Query(None, description="Filter by resource type"),
    start_date: Optional[datetime] = Query(None, description="Start date filter"),
    end_date: Optional[datetime] = Query(None, description="End date filter"),
):
    """
    Query audit entries with filters.
    """
    from backend.app.city_autonomy.audit_engine import get_audit_engine, AuditEventType, AuditSeverity
    
    audit_engine = get_audit_engine()
    
    event_types = [AuditEventType(event_type.value)] if event_type else None
    sev = AuditSeverity(severity.value) if severity else None
    
    entries = audit_engine.query_entries(
        start_date=start_date,
        end_date=end_date,
        event_types=event_types,
        actor_id=actor_id,
        resource_type=resource_type,
        severity=sev,
        limit=page_size,
        offset=(page - 1) * page_size,
    )
    
    entry_responses = [
        AuditEntryResponse(
            entry_id=e.entry_id,
            event_type=e.event_type.value,
            severity=e.severity.value,
            timestamp=e.timestamp.isoformat(),
            actor_id=e.actor_id,
            actor_type=e.actor_type,
            actor_name=e.actor_name,
            resource_type=e.resource_type,
            resource_id=e.resource_id,
            description=e.description,
            compliance_tags=[c.value for c in e.compliance_tags],
            signature=e.signature,
        )
        for e in entries
    ]
    
    return AuditQueryResponse(
        entries=entry_responses,
        total_count=len(entries),
        page=page,
        page_size=page_size,
    )


@router.get("/audit/{entry_id}", response_model=AuditEntryResponse)
async def get_audit_entry(entry_id: str = Path(..., description="Audit entry ID")):
    """
    Get a specific audit entry by ID.
    """
    from backend.app.city_autonomy.audit_engine import get_audit_engine
    
    audit_engine = get_audit_engine()
    entry = audit_engine.get_entry(entry_id)
    
    if not entry:
        raise HTTPException(status_code=404, detail="Audit entry not found")
    
    return AuditEntryResponse(
        entry_id=entry.entry_id,
        event_type=entry.event_type.value,
        severity=entry.severity.value,
        timestamp=entry.timestamp.isoformat(),
        actor_id=entry.actor_id,
        actor_type=entry.actor_type,
        actor_name=entry.actor_name,
        resource_type=entry.resource_type,
        resource_id=entry.resource_id,
        description=entry.description,
        compliance_tags=[c.value for c in entry.compliance_tags],
        signature=entry.signature,
    )


@router.get("/audit/action/{action_id}")
async def get_audit_entries_by_action(action_id: str = Path(..., description="Action ID")):
    """
    Get all audit entries for a specific action.
    """
    from backend.app.city_autonomy.audit_engine import get_audit_engine
    
    audit_engine = get_audit_engine()
    entries = audit_engine.get_entries_by_action(action_id)
    
    return {
        "action_id": action_id,
        "entries": [e.to_dict() for e in entries],
        "total_count": len(entries),
    }


@router.get("/audit/chain-of-custody/{resource_type}/{resource_id}")
async def get_chain_of_custody(
    resource_type: str = Path(..., description="Resource type"),
    resource_id: str = Path(..., description="Resource ID"),
):
    """
    Get chain of custody for a resource.
    """
    from backend.app.city_autonomy.audit_engine import get_audit_engine
    
    audit_engine = get_audit_engine()
    chain = audit_engine.get_chain_of_custody(resource_type, resource_id)
    
    if not chain:
        raise HTTPException(status_code=404, detail="Chain of custody not found")
    
    return chain.to_dict()


@router.post("/audit/chain-of-custody/{resource_type}/{resource_id}/seal")
async def seal_chain_of_custody(
    resource_type: str = Path(..., description="Resource type"),
    resource_id: str = Path(..., description="Resource ID"),
):
    """
    Seal a chain of custody to prevent further modifications.
    """
    from backend.app.city_autonomy.audit_engine import get_audit_engine
    
    audit_engine = get_audit_engine()
    success = audit_engine.seal_chain_of_custody(resource_type, resource_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Chain of custody not found")
    
    return {"status": "sealed", "resource_type": resource_type, "resource_id": resource_id}


@router.get("/audit/verify-chain")
async def verify_chain_integrity():
    """
    Verify the integrity of the entire audit chain.
    """
    from backend.app.city_autonomy.audit_engine import get_audit_engine
    
    audit_engine = get_audit_engine()
    is_valid, errors = audit_engine.verify_chain_integrity()
    
    return {
        "is_valid": is_valid,
        "errors": errors,
        "error_count": len(errors),
    }


@router.post("/audit/report/compliance", response_model=ComplianceReportResponse)
async def generate_compliance_report(request: GenerateReportRequest):
    """
    Generate a compliance report.
    """
    from backend.app.city_autonomy.audit_engine import get_audit_engine, ComplianceStandard, ReportPeriod
    
    audit_engine = get_audit_engine()
    
    report = audit_engine.generate_compliance_report(
        compliance_standard=ComplianceStandard(request.compliance_standard.value),
        period=ReportPeriod(request.period.value),
        generated_by=request.generated_by,
        start_date=request.start_date,
        end_date=request.end_date,
    )
    
    return ComplianceReportResponse(
        report_id=report.report_id,
        report_type=report.report_type,
        period=report.period.value,
        compliance_standard=report.compliance_standard.value,
        generated_at=report.generated_at.isoformat(),
        summary=report.summary,
        findings=report.findings,
        recommendations=report.recommendations,
    )


@router.get("/audit/summary/{period}", response_model=AutonomySummaryResponse)
async def get_autonomy_summary(
    period: ReportPeriodEnum = Path(..., description="Report period"),
):
    """
    Get autonomy summary for a time period.
    """
    from backend.app.city_autonomy.audit_engine import get_audit_engine, ReportPeriod
    
    audit_engine = get_audit_engine()
    summary = audit_engine.generate_autonomy_summary(ReportPeriod(period.value))
    
    return AutonomySummaryResponse(
        summary_id=summary.summary_id,
        period=summary.period.value,
        start_date=summary.start_date.isoformat(),
        end_date=summary.end_date.isoformat(),
        total_actions=summary.total_actions,
        actions_by_level=summary.actions_by_level,
        actions_by_status=summary.actions_by_status,
        human_overrides=summary.human_overrides,
        denied_actions=summary.denied_actions,
        ai_vs_human_ratio=summary.ai_vs_human_ratio,
    )


@router.get("/audit/incident-report/{action_id}")
async def get_incident_report(
    action_id: str = Path(..., description="Action ID"),
    generated_by: str = Query("system", description="Report generator ID"),
):
    """
    Generate an incident-level action report.
    """
    from backend.app.city_autonomy.audit_engine import get_audit_engine
    
    audit_engine = get_audit_engine()
    report = audit_engine.generate_incident_report(action_id, generated_by)
    
    if "error" in report:
        raise HTTPException(status_code=404, detail=report["error"])
    
    return report


# ============================================================================
# Statistics Endpoints
# ============================================================================

@router.get("/statistics", response_model=EngineStatisticsResponse)
async def get_all_statistics():
    """
    Get statistics from all autonomy engines.
    """
    from backend.app.city_autonomy import get_autonomous_action_engine
    from backend.app.city_autonomy.policy_engine import get_policy_engine
    from backend.app.city_autonomy.stabilizer import get_city_stabilizer
    from backend.app.city_autonomy.audit_engine import get_audit_engine
    
    action_engine = get_autonomous_action_engine()
    policy_engine = get_policy_engine()
    stabilizer = get_city_stabilizer()
    audit_engine = get_audit_engine()
    
    return EngineStatisticsResponse(
        action_engine=action_engine.get_statistics(),
        policy_engine=policy_engine.get_statistics(),
        stabilizer=stabilizer.get_statistics(),
        audit_engine=audit_engine.get_statistics(),
    )


@router.post("/circuit-breaker/reset")
async def reset_all_circuit_breakers():
    """
    Reset circuit breakers for all engines.
    """
    from backend.app.city_autonomy import get_autonomous_action_engine
    from backend.app.city_autonomy.stabilizer import get_city_stabilizer
    
    action_engine = get_autonomous_action_engine()
    stabilizer = get_city_stabilizer()
    
    action_engine.reset_circuit_breaker()
    stabilizer.reset_circuit_breaker()
    
    return {"status": "all_circuit_breakers_reset"}


@router.post("/mode/manual")
async def switch_to_manual_mode():
    """
    Switch autonomy system to manual mode.
    """
    from backend.app.city_autonomy import get_autonomous_action_engine
    from backend.app.city_autonomy.audit_engine import get_audit_engine, AuditEventType
    
    action_engine = get_autonomous_action_engine()
    audit_engine = get_audit_engine()
    
    action_engine.set_auto_execute(False)
    
    # Log mode change
    audit_engine.log_event(
        event_type=AuditEventType.SYSTEM_MODE_CHANGE,
        actor_id="api_user",
        actor_type="human",
        actor_name="API User",
        resource_type="autonomy_system",
        resource_id="main",
        description="System switched to manual mode",
        details={"mode": "manual"},
    )
    
    return {"status": "manual_mode_enabled"}


@router.post("/mode/autonomous")
async def switch_to_autonomous_mode():
    """
    Switch autonomy system to autonomous mode.
    """
    from backend.app.city_autonomy import get_autonomous_action_engine
    from backend.app.city_autonomy.audit_engine import get_audit_engine, AuditEventType
    
    action_engine = get_autonomous_action_engine()
    audit_engine = get_audit_engine()
    
    action_engine.set_auto_execute(True)
    
    # Log mode change
    audit_engine.log_event(
        event_type=AuditEventType.SYSTEM_MODE_CHANGE,
        actor_id="api_user",
        actor_type="human",
        actor_name="API User",
        resource_type="autonomy_system",
        resource_id="main",
        description="System switched to autonomous mode",
        details={"mode": "autonomous"},
    )
    
    return {"status": "autonomous_mode_enabled"}
