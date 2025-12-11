"""
Phase 25: AI City Constitution & Governance Framework API Router

REST API endpoints for the AI City Constitution system including:
- Legislative Knowledge Base
- AI Constitution Engine
- Policy Translator Engine
- Governance Risk Scoring Engine
- Human-in-the-Loop Gateway
"""

from datetime import datetime
from typing import Any, Optional
from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel, Field
import uuid

from ...city_governance.legislative_kb import (
    get_legislative_kb,
    LegislativeKnowledgeBase,
    LegalSource,
    LegalCategory,
    LegalDocument,
    LegalSection,
)
from ...city_governance.constitution_engine import (
    get_constitution_engine,
    AIConstitutionEngine,
    ConstitutionalLayer,
    ValidationResult,
    ActionCategory,
    AutonomyLevel,
)
from ...city_governance.policy_translator import (
    get_policy_translator,
    PolicyTranslatorEngine,
    RuleAction,
)
from ...city_governance.risk_scoring import (
    get_risk_scoring_engine,
    GovernanceRiskScoringEngine,
    RiskCategory,
    RiskDimension,
)
from ...city_governance.human_in_loop import (
    get_human_in_loop_gateway,
    HumanInTheLoopGateway,
    ApprovalType,
    ApprovalStatus,
    ReviewTrigger,
)


router = APIRouter(prefix="/constitution", tags=["AI City Constitution"])


class ConstitutionAuditLogger:
    """CJIS-aligned audit logger for constitutional governance operations."""

    _logs: list[dict[str, Any]] = []

    @classmethod
    def log(
        cls,
        action: str,
        resource_type: str,
        resource_id: str,
        user_id: str = "system",
        details: Optional[dict[str, Any]] = None,
    ):
        """Log an audit entry."""
        entry = {
            "audit_id": f"const-audit-{uuid.uuid4().hex[:12]}",
            "timestamp": datetime.utcnow().isoformat(),
            "action": action,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "user_id": user_id,
            "details": details or {},
            "ip_address": "internal",
            "session_id": "api-session",
            "compliance_tags": ["CJIS", "CONSTITUTIONAL"],
        }
        cls._logs.append(entry)
        if len(cls._logs) > 10000:
            cls._logs = cls._logs[-5000:]

    @classmethod
    def get_logs(
        cls,
        limit: int = 100,
        action_filter: Optional[str] = None,
        resource_type_filter: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """Get recent audit logs with optional filtering."""
        logs = cls._logs
        if action_filter:
            logs = [log for log in logs if log["action"] == action_filter]
        if resource_type_filter:
            logs = [log for log in logs if log["resource_type"] == resource_type_filter]
        return logs[-limit:]


class ActionValidationRequest(BaseModel):
    """Request model for validating an AI action against the constitution."""
    action_type: str = Field(..., description="Type of action to validate")
    action_category: str = Field(..., description="Category of the action")
    autonomy_level: str = Field("level_1", description="Autonomy level (level_0, level_1, level_2)")
    context: dict[str, Any] = Field(default_factory=dict, description="Action context data")
    operator_id: Optional[str] = Field(None, description="Operator requesting validation")


class PolicyCreateRequest(BaseModel):
    """Request model for creating a new policy."""
    natural_language_policy: str = Field(..., description="Policy in natural language")
    source: str = Field("agency_sop", description="Legal source for the policy")
    category: str = Field("public_safety", description="Policy category")
    created_by: str = Field("system", description="Creator of the policy")
    priority: int = Field(50, ge=1, le=100, description="Policy priority (1-100)")


class PolicyUpdateRequest(BaseModel):
    """Request model for updating an existing policy."""
    natural_language_policy: Optional[str] = Field(None, description="Updated policy text")
    priority: Optional[int] = Field(None, ge=1, le=100, description="Updated priority")
    is_active: Optional[bool] = Field(None, description="Whether policy is active")


class RiskScoreRequest(BaseModel):
    """Request model for calculating risk score."""
    action_type: str = Field(..., description="Type of action")
    action_category: str = Field(..., description="Category of the action")
    context: dict[str, Any] = Field(default_factory=dict, description="Action context")
    autonomy_level: str = Field("level_1", description="Autonomy level")


class ApprovalSubmitRequest(BaseModel):
    """Request model for submitting an approval decision."""
    approver_id: str = Field(..., description="ID of the approver")
    approval_type: str = Field(..., description="Type of approval")
    decision: str = Field(..., description="Decision: approved or denied")
    mfa_verified: bool = Field(False, description="Whether MFA was verified")
    notes: Optional[str] = Field(None, description="Approval notes")


class LegalDocumentCreateRequest(BaseModel):
    """Request model for creating a legal document."""
    source: str = Field(..., description="Legal source type")
    title: str = Field(..., description="Document title")
    content: str = Field(..., description="Document content")
    categories: list[str] = Field(..., description="Document categories")
    applicability_tags: list[str] = Field(default_factory=list, description="Applicability tags")


class LegalSectionCreateRequest(BaseModel):
    """Request model for adding a section to a document."""
    section_number: str = Field(..., description="Section number")
    title: str = Field(..., description="Section title")
    content: str = Field(..., description="Section content")
    applicability_tags: list[str] = Field(default_factory=list, description="Applicability tags")
    keywords: list[str] = Field(default_factory=list, description="Keywords")


@router.post("/validate-action")
async def validate_action(request: ActionValidationRequest):
    """
    Validate an AI action against the constitutional framework.
    
    Checks the action against all 7 constitutional layers:
    - Federal Constitutional
    - State Constitutional
    - Statutory
    - Local Ordinance
    - Agency SOP
    - Ethics
    - Autonomy
    
    Returns validation decision with full explainability.
    """
    engine = get_constitution_engine()
    
    try:
        action_category = ActionCategory(request.action_category)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid action category: {request.action_category}. Valid categories: {[c.value for c in ActionCategory]}",
        )
    
    try:
        autonomy_level = AutonomyLevel(request.autonomy_level)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid autonomy level: {request.autonomy_level}. Valid levels: {[l.value for l in AutonomyLevel]}",
        )
    
    decision = engine.validate_action(
        action_type=request.action_type,
        action_category=action_category,
        autonomy_level=autonomy_level,
        context=request.context,
    )
    
    ConstitutionAuditLogger.log(
        action="validate_action",
        resource_type="constitutional_validation",
        resource_id=decision.decision_id,
        user_id=request.operator_id or "system",
        details={
            "action_type": request.action_type,
            "action_category": request.action_category,
            "autonomy_level": request.autonomy_level,
            "result": decision.result.value,
            "triggered_rules": len(decision.triggered_rules),
            "blocking_rules": len(decision.blocking_rules),
        },
    )
    
    return {
        "success": True,
        "validation": decision.to_dict(),
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.post("/policy")
async def create_policy(request: PolicyCreateRequest):
    """
    Create a new policy from natural language.
    
    Translates natural language policy into machine-readable rules
    using the Policy Translator Engine.
    """
    translator = get_policy_translator()
    
    try:
        source = LegalSource(request.source)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid source: {request.source}. Valid sources: {[s.value for s in LegalSource]}",
        )
    
    try:
        category = LegalCategory(request.category)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid category: {request.category}. Valid categories: {[c.value for c in LegalCategory]}",
        )
    
    rule = translator.translate_policy(
        natural_language=request.natural_language_policy,
        source=source,
        category=category,
        priority=request.priority,
    )
    
    ConstitutionAuditLogger.log(
        action="create_policy",
        resource_type="policy",
        resource_id=rule.rule_id,
        user_id=request.created_by,
        details={
            "original_text": request.natural_language_policy[:100],
            "confidence": rule.confidence,
            "ambiguities": len(rule.ambiguities),
        },
    )
    
    return {
        "success": True,
        "policy": rule.to_dict(),
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/policies")
async def get_policies(
    source: Optional[str] = Query(None, description="Filter by legal source"),
    category: Optional[str] = Query(None, description="Filter by category"),
    active_only: bool = Query(True, description="Only return active policies"),
    limit: int = Query(50, ge=1, le=200, description="Maximum results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
):
    """
    Get all policies with optional filtering.
    
    Returns machine-readable rules translated from natural language policies.
    """
    translator = get_policy_translator()
    
    rules = translator.get_all_rules()
    
    if source:
        try:
            source_enum = LegalSource(source)
            rules = [r for r in rules if r.source == source_enum]
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid source: {source}")
    
    if category:
        try:
            category_enum = LegalCategory(category)
            rules = [r for r in rules if r.category == category_enum]
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid category: {category}")
    
    if active_only:
        rules = [r for r in rules if r.is_active]
    
    total = len(rules)
    rules = rules[offset : offset + limit]
    
    ConstitutionAuditLogger.log(
        action="get_policies",
        resource_type="policy",
        resource_id="query",
        details={"source": source, "category": category, "count": len(rules)},
    )
    
    return {
        "success": True,
        "policies": [r.to_dict() for r in rules],
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.get("/policies/{policy_id}")
async def get_policy(policy_id: str):
    """Get a specific policy by ID."""
    translator = get_policy_translator()
    rule = translator.get_rule(policy_id)
    
    if not rule:
        raise HTTPException(status_code=404, detail="Policy not found")
    
    ConstitutionAuditLogger.log(
        action="get_policy",
        resource_type="policy",
        resource_id=policy_id,
    )
    
    return {
        "success": True,
        "policy": rule.to_dict(),
    }


@router.delete("/policies/{policy_id}")
async def deactivate_policy(policy_id: str, deactivated_by: str = Query("system")):
    """Deactivate a policy (soft delete)."""
    translator = get_policy_translator()
    
    success = translator.deactivate_rule(policy_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Policy not found")
    
    ConstitutionAuditLogger.log(
        action="deactivate_policy",
        resource_type="policy",
        resource_id=policy_id,
        user_id=deactivated_by,
    )
    
    return {
        "success": True,
        "message": "Policy deactivated",
        "policy_id": policy_id,
    }


@router.post("/policies/detect-conflicts")
async def detect_policy_conflicts(policy_ids: list[str] = Query(..., description="Policy IDs to check")):
    """
    Detect conflicts between specified policies.
    
    Analyzes policies for direct contradictions, partial overlaps,
    precedence ambiguities, and scope conflicts.
    """
    translator = get_policy_translator()
    
    conflicts = translator.detect_conflicts(policy_ids)
    
    ConstitutionAuditLogger.log(
        action="detect_conflicts",
        resource_type="policy",
        resource_id="conflict_check",
        details={"policy_count": len(policy_ids), "conflicts_found": len(conflicts)},
    )
    
    return {
        "success": True,
        "conflicts": [c.to_dict() for c in conflicts],
        "conflict_count": len(conflicts),
    }


@router.post("/risk-score")
async def calculate_risk_score(request: RiskScoreRequest):
    """
    Calculate governance risk score for an AI action.
    
    Evaluates risk across 5 dimensions:
    - Legal Exposure
    - Civil Rights Impact
    - Jurisdictional Authority
    - Operational Consequence
    - Political/Public Risk
    
    Returns score 0-100 and risk category (Low/Elevated/High/Critical).
    """
    engine = get_risk_scoring_engine()
    
    try:
        action_category = ActionCategory(request.action_category)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid action category: {request.action_category}",
        )
    
    try:
        autonomy_level = AutonomyLevel(request.autonomy_level)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid autonomy level: {request.autonomy_level}",
        )
    
    assessment = engine.assess_risk(
        action_type=request.action_type,
        action_category=action_category,
        autonomy_level=autonomy_level,
        context=request.context,
    )
    
    ConstitutionAuditLogger.log(
        action="calculate_risk_score",
        resource_type="risk_assessment",
        resource_id=assessment.assessment_id,
        details={
            "action_type": request.action_type,
            "total_score": assessment.total_score,
            "category": assessment.category.value,
            "requires_human_review": assessment.requires_human_review,
        },
    )
    
    return {
        "success": True,
        "assessment": assessment.to_dict(),
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/constitution")
async def get_constitution():
    """
    Get the full AI Constitution structure.
    
    Returns all constitutional rules organized by layer with
    precedence information and source document references.
    """
    engine = get_constitution_engine()
    
    constitution = engine.get_constitution_structure()
    
    ConstitutionAuditLogger.log(
        action="get_constitution",
        resource_type="constitution",
        resource_id="full_structure",
    )
    
    return {
        "success": True,
        "constitution": constitution,
        "layers": [layer.value for layer in ConstitutionalLayer],
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/constitution/rules")
async def get_constitutional_rules(
    layer: Optional[str] = Query(None, description="Filter by constitutional layer"),
    action_category: Optional[str] = Query(None, description="Filter by action category"),
    limit: int = Query(50, ge=1, le=200, description="Maximum results"),
):
    """Get constitutional rules with optional filtering."""
    engine = get_constitution_engine()
    
    rules = engine.get_all_rules()
    
    if layer:
        try:
            layer_enum = ConstitutionalLayer(layer)
            rules = [r for r in rules if r.layer == layer_enum]
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid layer: {layer}")
    
    if action_category:
        try:
            category_enum = ActionCategory(action_category)
            rules = [r for r in rules if category_enum in r.action_categories]
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid action category: {action_category}")
    
    rules = rules[:limit]
    
    ConstitutionAuditLogger.log(
        action="get_constitutional_rules",
        resource_type="constitutional_rule",
        resource_id="query",
        details={"layer": layer, "action_category": action_category, "count": len(rules)},
    )
    
    return {
        "success": True,
        "rules": [r.to_dict() for r in rules],
        "count": len(rules),
    }


@router.get("/audit")
async def get_audit_logs(
    action: Optional[str] = Query(None, description="Filter by action type"),
    resource_type: Optional[str] = Query(None, description="Filter by resource type"),
    limit: int = Query(100, ge=1, le=500, description="Maximum results"),
):
    """
    Get constitutional governance audit logs.
    
    Returns CJIS-compliant audit trail for all constitutional
    validation, policy, and approval operations.
    """
    logs = ConstitutionAuditLogger.get_logs(
        limit=limit,
        action_filter=action,
        resource_type_filter=resource_type,
    )
    
    return {
        "success": True,
        "audit_logs": logs,
        "count": len(logs),
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.post("/approvals/request")
async def create_approval_request(
    action_id: str = Query(..., description="Action ID requiring approval"),
    action_type: str = Query(..., description="Type of action"),
    action_category: str = Query(..., description="Category of action"),
    risk_score: float = Query(..., ge=0, le=100, description="Risk score"),
    requested_by: str = Query(..., description="Operator requesting approval"),
    context: Optional[dict[str, Any]] = None,
):
    """
    Create a human-in-the-loop approval request.
    
    Triggers approval workflow based on action type and risk level.
    """
    gateway = get_human_in_loop_gateway()
    
    try:
        category = ActionCategory(action_category)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid action category: {action_category}",
        )
    
    request = gateway.create_approval_request(
        action_id=action_id,
        action_type=action_type,
        action_category=category,
        risk_score=risk_score,
        requested_by=requested_by,
        context=context or {},
    )
    
    ConstitutionAuditLogger.log(
        action="create_approval_request",
        resource_type="approval_request",
        resource_id=request.request_id,
        user_id=requested_by,
        details={
            "action_id": action_id,
            "action_type": action_type,
            "risk_score": risk_score,
            "required_approvals": len(request.requirements),
        },
    )
    
    return {
        "success": True,
        "approval_request": request.to_dict(),
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.post("/approvals/{request_id}/submit")
async def submit_approval(request_id: str, approval: ApprovalSubmitRequest):
    """
    Submit an approval decision for a pending request.
    
    Supports single operator, supervisor, command staff,
    multi-factor, and legal review approval types.
    """
    gateway = get_human_in_loop_gateway()
    
    try:
        approval_type = ApprovalType(approval.approval_type)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid approval type: {approval.approval_type}. Valid types: {[t.value for t in ApprovalType]}",
        )
    
    if approval.decision not in ["approved", "denied"]:
        raise HTTPException(
            status_code=400,
            detail="Decision must be 'approved' or 'denied'",
        )
    
    success = gateway.submit_approval(
        request_id=request_id,
        approver_id=approval.approver_id,
        approval_type=approval_type,
        decision=approval.decision,
        mfa_verified=approval.mfa_verified,
        notes=approval.notes,
    )
    
    if not success:
        raise HTTPException(
            status_code=400,
            detail="Approval request not found or already completed",
        )
    
    ConstitutionAuditLogger.log(
        action="submit_approval",
        resource_type="approval_request",
        resource_id=request_id,
        user_id=approval.approver_id,
        details={
            "approval_type": approval.approval_type,
            "decision": approval.decision,
            "mfa_verified": approval.mfa_verified,
        },
    )
    
    return {
        "success": True,
        "message": f"Approval {approval.decision}",
        "request_id": request_id,
    }


@router.get("/approvals/pending")
async def get_pending_approvals(
    approver_id: Optional[str] = Query(None, description="Filter by approver"),
    approval_type: Optional[str] = Query(None, description="Filter by approval type"),
    limit: int = Query(50, ge=1, le=200, description="Maximum results"),
):
    """Get all pending approval requests."""
    gateway = get_human_in_loop_gateway()
    
    requests = gateway.get_pending_requests()
    
    if approval_type:
        try:
            type_enum = ApprovalType(approval_type)
            requests = [
                r for r in requests
                if any(req.approval_type == type_enum for req in r.requirements)
            ]
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid approval type: {approval_type}")
    
    requests = requests[:limit]
    
    ConstitutionAuditLogger.log(
        action="get_pending_approvals",
        resource_type="approval_request",
        resource_id="query",
        details={"count": len(requests)},
    )
    
    return {
        "success": True,
        "pending_requests": [r.to_dict() for r in requests],
        "count": len(requests),
    }


@router.get("/approvals/{request_id}")
async def get_approval_request(request_id: str):
    """Get a specific approval request by ID."""
    gateway = get_human_in_loop_gateway()
    
    request = gateway.get_request(request_id)
    
    if not request:
        raise HTTPException(status_code=404, detail="Approval request not found")
    
    ConstitutionAuditLogger.log(
        action="get_approval_request",
        resource_type="approval_request",
        resource_id=request_id,
    )
    
    return {
        "success": True,
        "approval_request": request.to_dict(),
    }


@router.post("/approvals/{request_id}/escalate")
async def escalate_approval(
    request_id: str,
    escalated_by: str = Query(..., description="User escalating the request"),
    reason: str = Query(..., description="Escalation reason"),
):
    """Escalate an approval request to the next level."""
    gateway = get_human_in_loop_gateway()
    
    success = gateway.escalate_request(request_id, escalated_by, reason)
    
    if not success:
        raise HTTPException(
            status_code=400,
            detail="Approval request not found or cannot be escalated",
        )
    
    ConstitutionAuditLogger.log(
        action="escalate_approval",
        resource_type="approval_request",
        resource_id=request_id,
        user_id=escalated_by,
        details={"reason": reason},
    )
    
    return {
        "success": True,
        "message": "Approval request escalated",
        "request_id": request_id,
    }


@router.get("/legislative/documents")
async def get_legal_documents(
    source: Optional[str] = Query(None, description="Filter by legal source"),
    category: Optional[str] = Query(None, description="Filter by category"),
    keyword: Optional[str] = Query(None, description="Search by keyword"),
    limit: int = Query(50, ge=1, le=200, description="Maximum results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
):
    """
    Get legal documents from the Legislative Knowledge Base.
    
    Includes US Constitution, Florida Constitution, Florida Statutes,
    Federal frameworks, Riviera Beach codes, and agency SOPs.
    """
    kb = get_legislative_kb()
    
    if keyword:
        documents = kb.search_documents(keyword)
    elif source:
        try:
            source_enum = LegalSource(source)
            documents = kb.get_documents_by_source(source_enum)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid source: {source}")
    elif category:
        try:
            category_enum = LegalCategory(category)
            documents = kb.get_documents_by_category(category_enum)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid category: {category}")
    else:
        documents = kb.get_all_documents()
    
    total = len(documents)
    documents = documents[offset : offset + limit]
    
    ConstitutionAuditLogger.log(
        action="get_legal_documents",
        resource_type="legal_document",
        resource_id="query",
        details={"source": source, "category": category, "keyword": keyword, "count": len(documents)},
    )
    
    return {
        "success": True,
        "documents": [d.to_dict() for d in documents],
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.get("/legislative/documents/{document_id}")
async def get_legal_document(document_id: str):
    """Get a specific legal document by ID."""
    kb = get_legislative_kb()
    
    document = kb.get_document(document_id)
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    ConstitutionAuditLogger.log(
        action="get_legal_document",
        resource_type="legal_document",
        resource_id=document_id,
    )
    
    return {
        "success": True,
        "document": document.to_dict(),
    }


@router.post("/legislative/documents")
async def create_legal_document(request: LegalDocumentCreateRequest):
    """
    Add a new legal document to the knowledge base.
    
    Supports all legal source types including emergency ordinances.
    """
    kb = get_legislative_kb()
    
    try:
        source = LegalSource(request.source)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid source: {request.source}. Valid sources: {[s.value for s in LegalSource]}",
        )
    
    categories = []
    for cat in request.categories:
        try:
            categories.append(LegalCategory(cat))
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid category: {cat}")
    
    document = kb.ingest_document(
        source=source,
        title=request.title,
        content=request.content,
        categories=categories,
        applicability_tags=request.applicability_tags,
    )
    
    ConstitutionAuditLogger.log(
        action="create_legal_document",
        resource_type="legal_document",
        resource_id=document.document_id,
        details={"source": request.source, "title": request.title},
    )
    
    return {
        "success": True,
        "document": document.to_dict(),
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.post("/legislative/documents/{document_id}/sections")
async def add_document_section(document_id: str, request: LegalSectionCreateRequest):
    """Add a section to an existing legal document."""
    kb = get_legislative_kb()
    
    document = kb.get_document(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    section = kb.add_section(
        document_id=document_id,
        section_number=request.section_number,
        title=request.title,
        content=request.content,
        applicability_tags=request.applicability_tags,
        keywords=request.keywords,
    )
    
    if not section:
        raise HTTPException(status_code=400, detail="Failed to add section")
    
    ConstitutionAuditLogger.log(
        action="add_document_section",
        resource_type="legal_section",
        resource_id=section.section_id,
        details={"document_id": document_id, "section_number": request.section_number},
    )
    
    return {
        "success": True,
        "section": section.to_dict(),
    }


@router.get("/legislative/sources")
async def get_legal_sources():
    """Get all available legal source types."""
    return {
        "success": True,
        "sources": [
            {
                "value": source.value,
                "name": source.name,
                "description": _get_source_description(source),
            }
            for source in LegalSource
        ],
    }


@router.get("/legislative/categories")
async def get_legal_categories():
    """Get all available legal categories."""
    return {
        "success": True,
        "categories": [
            {
                "value": category.value,
                "name": category.name,
            }
            for category in LegalCategory
        ],
    }


@router.get("/statistics")
async def get_constitution_statistics():
    """Get statistics for the AI City Constitution system."""
    engine = get_constitution_engine()
    translator = get_policy_translator()
    gateway = get_human_in_loop_gateway()
    kb = get_legislative_kb()
    risk_engine = get_risk_scoring_engine()
    
    stats = {
        "constitutional_rules": len(engine.get_all_rules()),
        "policies": len(translator.get_all_rules()),
        "active_policies": len([r for r in translator.get_all_rules() if r.is_active]),
        "pending_approvals": len(gateway.get_pending_requests()),
        "legal_documents": len(kb.get_all_documents()),
        "validation_count": engine.get_validation_count(),
        "risk_assessments": risk_engine.get_assessment_count(),
        "audit_log_entries": len(ConstitutionAuditLogger._logs),
        "layers": {
            layer.value: len([r for r in engine.get_all_rules() if r.layer == layer])
            for layer in ConstitutionalLayer
        },
    }
    
    ConstitutionAuditLogger.log(
        action="get_statistics",
        resource_type="constitution",
        resource_id="statistics",
    )
    
    return {
        "success": True,
        "statistics": stats,
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/health")
async def health_check():
    """Health check endpoint for the AI City Constitution system."""
    return {
        "success": True,
        "status": "healthy",
        "service": "ai-city-constitution",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
    }


def _get_source_description(source: LegalSource) -> str:
    """Get description for a legal source type."""
    descriptions = {
        LegalSource.US_CONSTITUTION: "United States Constitution and Amendments",
        LegalSource.FLORIDA_CONSTITUTION: "Florida State Constitution",
        LegalSource.FLORIDA_STATUTE: "Florida State Statutes",
        LegalSource.RIVIERA_BEACH_CODE: "Riviera Beach Municipal Code",
        LegalSource.FEDERAL_FRAMEWORK: "Federal frameworks (NIST AI RMF, CJIS, DHS S&T)",
        LegalSource.AGENCY_SOP: "Agency Standard Operating Procedures",
        LegalSource.EMERGENCY_ORDINANCE: "Emergency Ordinances and Declarations",
    }
    return descriptions.get(source, "Legal document")
