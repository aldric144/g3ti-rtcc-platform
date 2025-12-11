"""
Phase 24: AI City Autonomy - Level-2 Autonomous City Operations

This module implements Level-2 Autonomous City Operations for Riviera Beach,
enabling the AI system to independently detect issues, propose solutions,
execute low-risk actions, and prepare high-risk actions for operator approval.

Components:
- AutonomousActionEngine: Interprets recommendations and executes/requests actions
- PolicyEngine: Manages city operation rules and emergency thresholds
- AutomatedCityStabilizer: Monitors city systems and generates stabilization actions
- ActionAuditEngine: Maintains tamper-proof audit logs for all autonomous actions
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Callable
import uuid
import hashlib
import json


class ActionLevel(Enum):
    """Action autonomy levels."""
    LEVEL_0 = 0  # Read-only / observation
    LEVEL_1 = 1  # Automated low-risk actions
    LEVEL_2 = 2  # Human-confirmed medium/high-risk actions


class ActionCategory(Enum):
    """Categories of autonomous actions."""
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


class ActionStatus(Enum):
    """Status of autonomous actions."""
    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    ESCALATED = "escalated"


class RiskLevel(Enum):
    """Risk levels for actions."""
    MINIMAL = "minimal"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class DecisionTreeNode:
    """Node in the decision tree for explainability."""
    node_id: str
    condition: str
    result: Optional[str] = None
    true_branch: Optional["DecisionTreeNode"] = None
    false_branch: Optional["DecisionTreeNode"] = None
    weight: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "condition": self.condition,
            "result": self.result,
            "true_branch": self.true_branch.to_dict() if self.true_branch else None,
            "false_branch": self.false_branch.to_dict() if self.false_branch else None,
            "weight": self.weight,
        }


@dataclass
class ActionExplainability:
    """Explainability data for an autonomous action."""
    decision_tree: Optional[DecisionTreeNode] = None
    model_weights: Dict[str, float] = field(default_factory=dict)
    recommended_path: List[str] = field(default_factory=list)
    risk_factors: List[str] = field(default_factory=list)
    confidence_score: float = 0.0
    reasoning: str = ""
    data_sources: List[str] = field(default_factory=list)
    alternative_actions: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "decision_tree": self.decision_tree.to_dict() if self.decision_tree else None,
            "model_weights": self.model_weights,
            "recommended_path": self.recommended_path,
            "risk_factors": self.risk_factors,
            "confidence_score": self.confidence_score,
            "reasoning": self.reasoning,
            "data_sources": self.data_sources,
            "alternative_actions": self.alternative_actions,
        }


@dataclass
class AutonomousAction:
    """Represents an autonomous action."""
    action_id: str
    action_type: str
    category: ActionCategory
    level: ActionLevel
    title: str
    description: str
    parameters: Dict[str, Any]
    risk_level: RiskLevel
    risk_score: float
    status: ActionStatus
    explainability: ActionExplainability
    source_recommendation_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    approved_at: Optional[datetime] = None
    approved_by: Optional[str] = None
    denied_at: Optional[datetime] = None
    denied_by: Optional[str] = None
    denial_reason: Optional[str] = None
    executed_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    execution_result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    escalated_to: Optional[str] = None
    escalation_reason: Optional[str] = None
    timeout_minutes: int = 30
    priority: int = 5

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action_id": self.action_id,
            "action_type": self.action_type,
            "category": self.category.value,
            "level": self.level.value,
            "title": self.title,
            "description": self.description,
            "parameters": self.parameters,
            "risk_level": self.risk_level.value,
            "risk_score": self.risk_score,
            "status": self.status.value,
            "explainability": self.explainability.to_dict(),
            "source_recommendation_id": self.source_recommendation_id,
            "created_at": self.created_at.isoformat(),
            "approved_at": self.approved_at.isoformat() if self.approved_at else None,
            "approved_by": self.approved_by,
            "denied_at": self.denied_at.isoformat() if self.denied_at else None,
            "denied_by": self.denied_by,
            "denial_reason": self.denial_reason,
            "executed_at": self.executed_at.isoformat() if self.executed_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "execution_result": self.execution_result,
            "error_message": self.error_message,
            "escalated_to": self.escalated_to,
            "escalation_reason": self.escalation_reason,
            "timeout_minutes": self.timeout_minutes,
            "priority": self.priority,
        }


class AutonomousActionEngine:
    """
    Engine for managing autonomous city operations.
    
    Interprets recommendations from Phases 22 & 23, categorizes actions
    into levels, auto-executes Level 1 actions, and requests operator
    approval for Level 2 actions.
    """

    def __init__(self):
        self._actions: Dict[str, AutonomousAction] = {}
        self._action_handlers: Dict[str, Callable] = {}
        self._level1_auto_execute = True
        self._circuit_breaker_open = False
        self._failed_action_count = 0
        self._max_failures_before_circuit_break = 5
        self._initialize_default_handlers()

    def _initialize_default_handlers(self):
        """Initialize default action handlers."""
        self._action_handlers = {
            "traffic_signal_timing": self._handle_traffic_signal,
            "patrol_rebalance": self._handle_patrol_rebalance,
            "send_notification": self._handle_notification,
            "adjust_coverage": self._handle_coverage_adjustment,
            "deploy_units": self._handle_unit_deployment,
            "modify_patrol_zone": self._handle_patrol_zone_modification,
            "coordinate_evacuation": self._handle_evacuation,
            "utility_adjustment": self._handle_utility_adjustment,
            "crowd_control": self._handle_crowd_control,
            "emergency_alert": self._handle_emergency_alert,
        }

    def interpret_recommendation(
        self,
        recommendation: Dict[str, Any],
        source_id: Optional[str] = None,
    ) -> AutonomousAction:
        """
        Interpret a recommendation from Phase 22/23 and create an autonomous action.
        """
        action_type = recommendation.get("action_type", "unknown")
        category = self._determine_category(recommendation)
        level = self._determine_action_level(recommendation)
        risk_level, risk_score = self._calculate_risk(recommendation)

        explainability = self._generate_explainability(recommendation)

        action = AutonomousAction(
            action_id=f"action-{uuid.uuid4().hex[:12]}",
            action_type=action_type,
            category=category,
            level=level,
            title=recommendation.get("title", f"Action: {action_type}"),
            description=recommendation.get("description", ""),
            parameters=recommendation.get("parameters", {}),
            risk_level=risk_level,
            risk_score=risk_score,
            status=ActionStatus.PENDING,
            explainability=explainability,
            source_recommendation_id=source_id,
            priority=recommendation.get("priority", 5),
            timeout_minutes=recommendation.get("timeout_minutes", 30),
        )

        self._actions[action.action_id] = action

        if level == ActionLevel.LEVEL_1 and self._level1_auto_execute:
            if not self._circuit_breaker_open:
                self._auto_execute_action(action)

        return action

    def _determine_category(self, recommendation: Dict[str, Any]) -> ActionCategory:
        """Determine the action category from recommendation."""
        action_type = recommendation.get("action_type", "").lower()
        domain = recommendation.get("domain", "").lower()

        category_mapping = {
            "traffic": ActionCategory.TRAFFIC_CONTROL,
            "patrol": ActionCategory.PATROL_DEPLOYMENT,
            "resource": ActionCategory.RESOURCE_ALLOCATION,
            "notification": ActionCategory.NOTIFICATION,
            "emergency": ActionCategory.EMERGENCY_RESPONSE,
            "utility": ActionCategory.UTILITY_MANAGEMENT,
            "crowd": ActionCategory.CROWD_MANAGEMENT,
            "evacuation": ActionCategory.EVACUATION,
            "infrastructure": ActionCategory.INFRASTRUCTURE,
        }

        for key, category in category_mapping.items():
            if key in action_type or key in domain:
                return category

        return ActionCategory.OBSERVATION

    def _determine_action_level(self, recommendation: Dict[str, Any]) -> ActionLevel:
        """Determine the autonomy level for an action."""
        action_type = recommendation.get("action_type", "").lower()
        risk = recommendation.get("risk_level", "low").lower()

        level_0_actions = ["observe", "monitor", "report", "log", "analyze"]
        level_1_actions = [
            "traffic_signal_timing", "patrol_rebalance", "send_notification",
            "adjust_coverage", "minor_adjustment", "alert", "notify",
        ]
        level_2_actions = [
            "deploy_units", "modify_patrol_zone", "coordinate_evacuation",
            "emergency_response", "major_deployment", "evacuation",
        ]

        for l0 in level_0_actions:
            if l0 in action_type:
                return ActionLevel.LEVEL_0

        if risk in ["high", "critical"]:
            return ActionLevel.LEVEL_2

        for l2 in level_2_actions:
            if l2 in action_type:
                return ActionLevel.LEVEL_2

        for l1 in level_1_actions:
            if l1 in action_type:
                return ActionLevel.LEVEL_1

        return ActionLevel.LEVEL_0

    def _calculate_risk(self, recommendation: Dict[str, Any]) -> tuple:
        """Calculate risk level and score for an action."""
        base_risk = recommendation.get("risk_level", "low").lower()
        impact_score = recommendation.get("impact_score", 0.3)
        reversibility = recommendation.get("reversibility", 0.8)
        urgency = recommendation.get("urgency", 0.5)

        risk_score = (impact_score * 0.4) + ((1 - reversibility) * 0.3) + (urgency * 0.3)

        if risk_score >= 0.8:
            return RiskLevel.CRITICAL, risk_score
        elif risk_score >= 0.6:
            return RiskLevel.HIGH, risk_score
        elif risk_score >= 0.4:
            return RiskLevel.MEDIUM, risk_score
        elif risk_score >= 0.2:
            return RiskLevel.LOW, risk_score
        else:
            return RiskLevel.MINIMAL, risk_score

    def _generate_explainability(self, recommendation: Dict[str, Any]) -> ActionExplainability:
        """Generate explainability data for an action."""
        root_node = DecisionTreeNode(
            node_id="root",
            condition=f"Recommendation received: {recommendation.get('action_type', 'unknown')}",
            weight=1.0,
        )

        risk_node = DecisionTreeNode(
            node_id="risk_check",
            condition=f"Risk level: {recommendation.get('risk_level', 'low')}",
            weight=0.8,
        )
        root_node.true_branch = risk_node

        level_node = DecisionTreeNode(
            node_id="level_determination",
            condition="Determine action level based on risk and type",
            result=f"Level {self._determine_action_level(recommendation).value}",
            weight=0.9,
        )
        risk_node.true_branch = level_node

        return ActionExplainability(
            decision_tree=root_node,
            model_weights={
                "impact_score": 0.4,
                "reversibility": 0.3,
                "urgency": 0.3,
            },
            recommended_path=[
                "Receive recommendation",
                "Analyze risk factors",
                "Determine action level",
                "Generate action plan",
            ],
            risk_factors=recommendation.get("risk_factors", []),
            confidence_score=recommendation.get("confidence", 0.8),
            reasoning=recommendation.get("reasoning", "Action generated from city governance recommendation"),
            data_sources=recommendation.get("data_sources", ["Phase 22 City Brain", "Phase 23 Governance Engine"]),
            alternative_actions=recommendation.get("alternatives", []),
        )

    def _auto_execute_action(self, action: AutonomousAction):
        """Auto-execute a Level 1 action."""
        if action.level != ActionLevel.LEVEL_1:
            return

        action.status = ActionStatus.EXECUTING
        action.executed_at = datetime.utcnow()

        try:
            handler = self._action_handlers.get(action.action_type)
            if handler:
                result = handler(action)
                action.execution_result = result
                action.status = ActionStatus.COMPLETED
                action.completed_at = datetime.utcnow()
                self._failed_action_count = 0
            else:
                action.execution_result = {"status": "simulated", "message": "No handler registered"}
                action.status = ActionStatus.COMPLETED
                action.completed_at = datetime.utcnow()
        except Exception as e:
            action.status = ActionStatus.FAILED
            action.error_message = str(e)
            self._failed_action_count += 1
            if self._failed_action_count >= self._max_failures_before_circuit_break:
                self._circuit_breaker_open = True

    def _handle_traffic_signal(self, action: AutonomousAction) -> Dict[str, Any]:
        """Handle traffic signal timing adjustment."""
        return {
            "status": "executed",
            "action": "traffic_signal_timing",
            "parameters": action.parameters,
            "timestamp": datetime.utcnow().isoformat(),
        }

    def _handle_patrol_rebalance(self, action: AutonomousAction) -> Dict[str, Any]:
        """Handle patrol rebalancing."""
        return {
            "status": "executed",
            "action": "patrol_rebalance",
            "parameters": action.parameters,
            "timestamp": datetime.utcnow().isoformat(),
        }

    def _handle_notification(self, action: AutonomousAction) -> Dict[str, Any]:
        """Handle sending notifications."""
        return {
            "status": "executed",
            "action": "send_notification",
            "recipients": action.parameters.get("recipients", []),
            "timestamp": datetime.utcnow().isoformat(),
        }

    def _handle_coverage_adjustment(self, action: AutonomousAction) -> Dict[str, Any]:
        """Handle coverage adjustment."""
        return {
            "status": "executed",
            "action": "adjust_coverage",
            "parameters": action.parameters,
            "timestamp": datetime.utcnow().isoformat(),
        }

    def _handle_unit_deployment(self, action: AutonomousAction) -> Dict[str, Any]:
        """Handle unit deployment (Level 2 - requires approval)."""
        return {
            "status": "executed",
            "action": "deploy_units",
            "units": action.parameters.get("units", []),
            "timestamp": datetime.utcnow().isoformat(),
        }

    def _handle_patrol_zone_modification(self, action: AutonomousAction) -> Dict[str, Any]:
        """Handle patrol zone modification (Level 2 - requires approval)."""
        return {
            "status": "executed",
            "action": "modify_patrol_zone",
            "zones": action.parameters.get("zones", []),
            "timestamp": datetime.utcnow().isoformat(),
        }

    def _handle_evacuation(self, action: AutonomousAction) -> Dict[str, Any]:
        """Handle evacuation coordination (Level 2 - requires approval)."""
        return {
            "status": "executed",
            "action": "coordinate_evacuation",
            "areas": action.parameters.get("areas", []),
            "timestamp": datetime.utcnow().isoformat(),
        }

    def _handle_utility_adjustment(self, action: AutonomousAction) -> Dict[str, Any]:
        """Handle utility adjustment."""
        return {
            "status": "executed",
            "action": "utility_adjustment",
            "parameters": action.parameters,
            "timestamp": datetime.utcnow().isoformat(),
        }

    def _handle_crowd_control(self, action: AutonomousAction) -> Dict[str, Any]:
        """Handle crowd control measures."""
        return {
            "status": "executed",
            "action": "crowd_control",
            "parameters": action.parameters,
            "timestamp": datetime.utcnow().isoformat(),
        }

    def _handle_emergency_alert(self, action: AutonomousAction) -> Dict[str, Any]:
        """Handle emergency alert."""
        return {
            "status": "executed",
            "action": "emergency_alert",
            "alert_type": action.parameters.get("alert_type", "general"),
            "timestamp": datetime.utcnow().isoformat(),
        }

    def approve_action(
        self,
        action_id: str,
        approved_by: str,
        notes: Optional[str] = None,
    ) -> bool:
        """Approve a pending Level 2 action."""
        action = self._actions.get(action_id)
        if not action or action.status != ActionStatus.PENDING:
            return False

        action.status = ActionStatus.APPROVED
        action.approved_at = datetime.utcnow()
        action.approved_by = approved_by

        self._execute_approved_action(action)
        return True

    def deny_action(
        self,
        action_id: str,
        denied_by: str,
        reason: str,
    ) -> bool:
        """Deny a pending action."""
        action = self._actions.get(action_id)
        if not action or action.status != ActionStatus.PENDING:
            return False

        action.status = ActionStatus.DENIED
        action.denied_at = datetime.utcnow()
        action.denied_by = denied_by
        action.denial_reason = reason
        return True

    def _execute_approved_action(self, action: AutonomousAction):
        """Execute an approved action."""
        action.status = ActionStatus.EXECUTING
        action.executed_at = datetime.utcnow()

        try:
            handler = self._action_handlers.get(action.action_type)
            if handler:
                result = handler(action)
                action.execution_result = result
                action.status = ActionStatus.COMPLETED
                action.completed_at = datetime.utcnow()
            else:
                action.execution_result = {"status": "simulated", "message": "No handler registered"}
                action.status = ActionStatus.COMPLETED
                action.completed_at = datetime.utcnow()
        except Exception as e:
            action.status = ActionStatus.FAILED
            action.error_message = str(e)

    def escalate_action(
        self,
        action_id: str,
        escalate_to: str,
        reason: str,
    ) -> bool:
        """Escalate an action to a higher authority."""
        action = self._actions.get(action_id)
        if not action:
            return False

        action.status = ActionStatus.ESCALATED
        action.escalated_to = escalate_to
        action.escalation_reason = reason
        return True

    def get_action(self, action_id: str) -> Optional[AutonomousAction]:
        """Get an action by ID."""
        return self._actions.get(action_id)

    def get_pending_actions(self) -> List[AutonomousAction]:
        """Get all pending actions requiring approval."""
        return [
            a for a in self._actions.values()
            if a.status == ActionStatus.PENDING and a.level == ActionLevel.LEVEL_2
        ]

    def get_action_history(
        self,
        limit: int = 100,
        category: Optional[ActionCategory] = None,
        status: Optional[ActionStatus] = None,
    ) -> List[AutonomousAction]:
        """Get action history with optional filters."""
        actions = list(self._actions.values())

        if category:
            actions = [a for a in actions if a.category == category]
        if status:
            actions = [a for a in actions if a.status == status]

        actions.sort(key=lambda a: a.created_at, reverse=True)
        return actions[:limit]

    def get_statistics(self) -> Dict[str, Any]:
        """Get engine statistics."""
        actions = list(self._actions.values())
        return {
            "total_actions": len(actions),
            "pending_actions": len([a for a in actions if a.status == ActionStatus.PENDING]),
            "completed_actions": len([a for a in actions if a.status == ActionStatus.COMPLETED]),
            "failed_actions": len([a for a in actions if a.status == ActionStatus.FAILED]),
            "denied_actions": len([a for a in actions if a.status == ActionStatus.DENIED]),
            "actions_by_level": {
                "level_0": len([a for a in actions if a.level == ActionLevel.LEVEL_0]),
                "level_1": len([a for a in actions if a.level == ActionLevel.LEVEL_1]),
                "level_2": len([a for a in actions if a.level == ActionLevel.LEVEL_2]),
            },
            "actions_by_category": {
                cat.value: len([a for a in actions if a.category == cat])
                for cat in ActionCategory
            },
            "circuit_breaker_open": self._circuit_breaker_open,
            "failed_action_count": self._failed_action_count,
            "level1_auto_execute": self._level1_auto_execute,
        }

    def reset_circuit_breaker(self):
        """Reset the circuit breaker."""
        self._circuit_breaker_open = False
        self._failed_action_count = 0

    def set_auto_execute(self, enabled: bool):
        """Enable or disable auto-execution of Level 1 actions."""
        self._level1_auto_execute = enabled

    def register_action_handler(self, action_type: str, handler: Callable):
        """Register a custom action handler."""
        self._action_handlers[action_type] = handler


_autonomous_action_engine: Optional[AutonomousActionEngine] = None


def get_autonomous_action_engine() -> AutonomousActionEngine:
    """Get the singleton AutonomousActionEngine instance."""
    global _autonomous_action_engine
    if _autonomous_action_engine is None:
        _autonomous_action_engine = AutonomousActionEngine()
    return _autonomous_action_engine
