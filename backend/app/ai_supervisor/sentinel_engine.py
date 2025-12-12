"""
Sentinel Decision Engine

Master decision engine that:
- Consolidates alerts from all subsystems
- Assigns priority (P1–P5)
- Recommends actions
- Approves or denies autonomous actions from Level 1–2 systems
- Predicts cascading outcomes
- Sends alerts to command staff
"""

import hashlib
import random
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional


class AlertPriority(Enum):
    """Alert priority levels (P1 = highest)."""
    P1_CRITICAL = 1
    P2_HIGH = 2
    P3_MEDIUM = 3
    P4_LOW = 4
    P5_INFO = 5


class AlertSource(Enum):
    """Sources of alerts."""
    SYSTEM_MONITOR = "system_monitor"
    ETHICS_GUARD = "ethics_guard"
    AUTO_CORRECTOR = "auto_corrector"
    DRONE_ENGINE = "drone_engine"
    ROBOTICS_ENGINE = "robotics_engine"
    INTEL_ENGINE = "intel_engine"
    HUMAN_STABILITY = "human_stability"
    PREDICTIVE_AI = "predictive_ai"
    CITY_AUTONOMY = "city_autonomy"
    GLOBAL_AWARENESS = "global_awareness"
    EMERGENCY_MANAGEMENT = "emergency_management"
    CYBER_INTEL = "cyber_intel"
    OFFICER_ASSIST = "officer_assist"


class AutonomyLevel(Enum):
    """Autonomy levels for system actions."""
    LEVEL_0_MANUAL = 0
    LEVEL_1_ASSISTED = 1
    LEVEL_2_PARTIAL = 2
    LEVEL_3_CONDITIONAL = 3
    LEVEL_4_HIGH = 4
    LEVEL_5_FULL = 5


class ActionApproval(Enum):
    """Approval status for autonomous actions."""
    APPROVED = "approved"
    DENIED = "denied"
    PENDING = "pending"
    ESCALATED = "escalated"
    CONDITIONAL = "conditional"


class RecommendationType(Enum):
    """Types of recommendations."""
    IMMEDIATE_ACTION = "immediate_action"
    PREVENTIVE_ACTION = "preventive_action"
    MONITORING = "monitoring"
    ESCALATION = "escalation"
    RESOURCE_ALLOCATION = "resource_allocation"
    POLICY_CHANGE = "policy_change"
    TRAINING = "training"
    INVESTIGATION = "investigation"


@dataclass
class ConsolidatedAlert:
    """A consolidated alert from multiple sources."""
    alert_id: str
    priority: AlertPriority
    sources: list[AlertSource]
    title: str
    description: str
    affected_systems: list[str]
    affected_areas: list[str]
    metrics: dict
    recommended_actions: list[str]
    auto_response_triggered: bool
    acknowledged: bool
    resolved: bool
    assigned_to: Optional[str]
    timestamp: datetime
    chain_of_custody_hash: str


@dataclass
class AutonomousActionRequest:
    """Request for autonomous action approval."""
    request_id: str
    source_engine: str
    action_type: str
    autonomy_level: AutonomyLevel
    target: str
    parameters: dict
    justification: str
    risk_assessment: dict
    approval_status: ActionApproval
    approved_by: Optional[str]
    denial_reason: Optional[str]
    conditions: list[str]
    timestamp: datetime
    chain_of_custody_hash: str


@dataclass
class CascadePrediction:
    """Prediction of cascading outcomes."""
    prediction_id: str
    trigger_event: str
    trigger_source: AlertSource
    predicted_outcomes: list[dict]
    probability: float
    time_horizon_hours: int
    affected_systems: list[str]
    mitigation_options: list[str]
    confidence: float
    timestamp: datetime
    chain_of_custody_hash: str


@dataclass
class SentinelRecommendation:
    """A recommendation from the Sentinel Engine."""
    recommendation_id: str
    recommendation_type: RecommendationType
    priority: AlertPriority
    title: str
    description: str
    rationale: str
    affected_systems: list[str]
    implementation_steps: list[str]
    expected_outcome: str
    risk_if_ignored: str
    deadline: Optional[datetime]
    accepted: bool
    implemented: bool
    timestamp: datetime
    chain_of_custody_hash: str


@dataclass
class CommandStaffAlert:
    """Alert sent to command staff."""
    alert_id: str
    priority: AlertPriority
    recipient_role: str
    title: str
    summary: str
    details: dict
    required_action: str
    deadline: Optional[datetime]
    acknowledged: bool
    response: Optional[str]
    sent_at: datetime
    acknowledged_at: Optional[datetime]
    chain_of_custody_hash: str


class SentinelEngine:
    """
    Sentinel Decision Engine for RTCC-UIP platform.
    
    Master oversight engine that consolidates alerts,
    approves autonomous actions, and coordinates responses.
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
        
        self.consolidated_alerts: dict[str, ConsolidatedAlert] = {}
        self.action_requests: dict[str, AutonomousActionRequest] = {}
        self.cascade_predictions: dict[str, CascadePrediction] = {}
        self.recommendations: dict[str, SentinelRecommendation] = {}
        self.command_alerts: dict[str, CommandStaffAlert] = {}
        
        self.autonomy_policies = {
            AutonomyLevel.LEVEL_0_MANUAL: {"auto_approve": False, "requires_human": True},
            AutonomyLevel.LEVEL_1_ASSISTED: {"auto_approve": False, "requires_human": True},
            AutonomyLevel.LEVEL_2_PARTIAL: {"auto_approve": True, "requires_human": False, "max_risk": 0.3},
            AutonomyLevel.LEVEL_3_CONDITIONAL: {"auto_approve": True, "requires_human": False, "max_risk": 0.5},
            AutonomyLevel.LEVEL_4_HIGH: {"auto_approve": True, "requires_human": False, "max_risk": 0.7},
            AutonomyLevel.LEVEL_5_FULL: {"auto_approve": True, "requires_human": False, "max_risk": 1.0},
        }
        
        self.priority_thresholds = {
            AlertPriority.P1_CRITICAL: {"response_time_minutes": 5, "escalation_time_minutes": 15},
            AlertPriority.P2_HIGH: {"response_time_minutes": 15, "escalation_time_minutes": 30},
            AlertPriority.P3_MEDIUM: {"response_time_minutes": 60, "escalation_time_minutes": 120},
            AlertPriority.P4_LOW: {"response_time_minutes": 240, "escalation_time_minutes": 480},
            AlertPriority.P5_INFO: {"response_time_minutes": 1440, "escalation_time_minutes": None},
        }
        
        self._initialized = True
    
    def _generate_hash(self, data: str) -> str:
        """Generate SHA256 hash for chain of custody."""
        return hashlib.sha256(f"{data}:{datetime.utcnow().isoformat()}".encode()).hexdigest()
    
    def consolidate_alert(
        self,
        sources: list[AlertSource],
        title: str,
        description: str,
        affected_systems: list[str],
        affected_areas: list[str],
        metrics: dict,
        severity_score: float,
    ) -> ConsolidatedAlert:
        """Consolidate alerts from multiple sources."""
        alert_id = f"CON-{hashlib.sha256(f'{title}:{datetime.utcnow().isoformat()}'.encode()).hexdigest()[:8].upper()}"
        
        priority = self._calculate_priority(severity_score, len(sources), affected_systems)
        
        recommended_actions = self._generate_recommended_actions(
            priority, affected_systems, metrics
        )
        
        auto_response = priority in [AlertPriority.P1_CRITICAL, AlertPriority.P2_HIGH] and \
                       severity_score > 0.8
        
        alert = ConsolidatedAlert(
            alert_id=alert_id,
            priority=priority,
            sources=sources,
            title=title,
            description=description,
            affected_systems=affected_systems,
            affected_areas=affected_areas,
            metrics=metrics,
            recommended_actions=recommended_actions,
            auto_response_triggered=auto_response,
            acknowledged=False,
            resolved=False,
            assigned_to=None,
            timestamp=datetime.utcnow(),
            chain_of_custody_hash=self._generate_hash(f"{alert_id}:{priority.value}"),
        )
        
        self.consolidated_alerts[alert_id] = alert
        
        if priority in [AlertPriority.P1_CRITICAL, AlertPriority.P2_HIGH]:
            self._send_command_staff_alert(alert)
        
        return alert
    
    def _calculate_priority(
        self,
        severity_score: float,
        source_count: int,
        affected_systems: list[str],
    ) -> AlertPriority:
        """Calculate alert priority based on factors."""
        priority_score = severity_score * 0.5 + \
                        min(source_count / 5, 1.0) * 0.2 + \
                        min(len(affected_systems) / 10, 1.0) * 0.3
        
        if priority_score >= 0.9:
            return AlertPriority.P1_CRITICAL
        elif priority_score >= 0.7:
            return AlertPriority.P2_HIGH
        elif priority_score >= 0.5:
            return AlertPriority.P3_MEDIUM
        elif priority_score >= 0.3:
            return AlertPriority.P4_LOW
        else:
            return AlertPriority.P5_INFO
    
    def _generate_recommended_actions(
        self,
        priority: AlertPriority,
        affected_systems: list[str],
        metrics: dict,
    ) -> list[str]:
        """Generate recommended actions for an alert."""
        actions = []
        
        if priority == AlertPriority.P1_CRITICAL:
            actions.append("Immediately notify on-duty supervisor")
            actions.append("Activate incident response team")
            actions.append("Begin system isolation if security-related")
        
        if priority in [AlertPriority.P1_CRITICAL, AlertPriority.P2_HIGH]:
            actions.append("Document all actions taken")
            actions.append("Preserve evidence and logs")
        
        if metrics.get("cpu_percent", 0) > 90:
            actions.append("Scale up compute resources")
        if metrics.get("error_rate", 0) > 0.05:
            actions.append("Investigate error sources")
        if metrics.get("latency_ms", 0) > 1000:
            actions.append("Check network and database connections")
        
        for system in affected_systems:
            actions.append(f"Monitor {system} for further issues")
        
        return actions
    
    def _send_command_staff_alert(self, alert: ConsolidatedAlert):
        """Send alert to command staff."""
        cmd_alert_id = f"CMD-{hashlib.sha256(f'{alert.alert_id}:{datetime.utcnow().isoformat()}'.encode()).hexdigest()[:8].upper()}"
        
        if alert.priority == AlertPriority.P1_CRITICAL:
            recipient_role = "Watch Commander"
            deadline = datetime.utcnow() + timedelta(minutes=5)
        else:
            recipient_role = "Duty Supervisor"
            deadline = datetime.utcnow() + timedelta(minutes=15)
        
        cmd_alert = CommandStaffAlert(
            alert_id=cmd_alert_id,
            priority=alert.priority,
            recipient_role=recipient_role,
            title=alert.title,
            summary=alert.description[:200],
            details={
                "sources": [s.value for s in alert.sources],
                "affected_systems": alert.affected_systems,
                "metrics": alert.metrics,
            },
            required_action="Review and acknowledge alert",
            deadline=deadline,
            acknowledged=False,
            response=None,
            sent_at=datetime.utcnow(),
            acknowledged_at=None,
            chain_of_custody_hash=self._generate_hash(f"{cmd_alert_id}:{alert.priority.value}"),
        )
        
        self.command_alerts[cmd_alert_id] = cmd_alert
    
    def request_autonomous_action(
        self,
        source_engine: str,
        action_type: str,
        autonomy_level: AutonomyLevel,
        target: str,
        parameters: dict,
        justification: str,
        risk_score: float,
    ) -> AutonomousActionRequest:
        """Request approval for an autonomous action."""
        request_id = f"AAR-{hashlib.sha256(f'{source_engine}:{action_type}:{datetime.utcnow().isoformat()}'.encode()).hexdigest()[:8].upper()}"
        
        risk_assessment = {
            "risk_score": risk_score,
            "risk_level": "high" if risk_score > 0.7 else "medium" if risk_score > 0.4 else "low",
            "potential_impacts": self._assess_potential_impacts(action_type, target),
            "reversible": self._is_action_reversible(action_type),
        }
        
        approval_status, denial_reason, conditions = self._evaluate_action_request(
            autonomy_level, risk_score, action_type, parameters
        )
        
        request = AutonomousActionRequest(
            request_id=request_id,
            source_engine=source_engine,
            action_type=action_type,
            autonomy_level=autonomy_level,
            target=target,
            parameters=parameters,
            justification=justification,
            risk_assessment=risk_assessment,
            approval_status=approval_status,
            approved_by="sentinel_engine" if approval_status == ActionApproval.APPROVED else None,
            denial_reason=denial_reason,
            conditions=conditions,
            timestamp=datetime.utcnow(),
            chain_of_custody_hash=self._generate_hash(f"{request_id}:{approval_status.value}"),
        )
        
        self.action_requests[request_id] = request
        return request
    
    def _evaluate_action_request(
        self,
        autonomy_level: AutonomyLevel,
        risk_score: float,
        action_type: str,
        parameters: dict,
    ) -> tuple[ActionApproval, Optional[str], list[str]]:
        """Evaluate an autonomous action request."""
        policy = self.autonomy_policies.get(autonomy_level, {})
        
        if not policy.get("auto_approve", False):
            return ActionApproval.PENDING, "Requires human approval", []
        
        max_risk = policy.get("max_risk", 0)
        if risk_score > max_risk:
            return ActionApproval.DENIED, f"Risk score {risk_score:.2f} exceeds maximum {max_risk} for autonomy level {autonomy_level.value}", []
        
        high_risk_actions = ["deploy_lethal", "vehicle_pursuit", "building_breach", "mass_notification"]
        if action_type in high_risk_actions:
            return ActionApproval.ESCALATED, "High-risk action requires command approval", []
        
        conditions = []
        if risk_score > 0.3:
            conditions.append("Log all actions for review")
        if risk_score > 0.5:
            conditions.append("Notify supervisor within 15 minutes")
        
        return ActionApproval.APPROVED, None, conditions
    
    def _assess_potential_impacts(self, action_type: str, target: str) -> list[str]:
        """Assess potential impacts of an action."""
        impacts = []
        
        if "deploy" in action_type.lower():
            impacts.append("Resource deployment")
        if "alert" in action_type.lower():
            impacts.append("Public notification")
        if "restrict" in action_type.lower():
            impacts.append("Access restriction")
        if "surveillance" in action_type.lower():
            impacts.append("Privacy implications")
        
        impacts.append(f"Target: {target}")
        
        return impacts
    
    def _is_action_reversible(self, action_type: str) -> bool:
        """Determine if an action is reversible."""
        irreversible_actions = [
            "deploy_lethal",
            "mass_notification",
            "data_deletion",
            "arrest",
        ]
        return action_type not in irreversible_actions
    
    def predict_cascade(
        self,
        trigger_event: str,
        trigger_source: AlertSource,
        initial_severity: float,
        time_horizon_hours: int = 24,
    ) -> CascadePrediction:
        """Predict cascading outcomes from an event."""
        prediction_id = f"CAS-{hashlib.sha256(f'{trigger_event}:{datetime.utcnow().isoformat()}'.encode()).hexdigest()[:8].upper()}"
        
        predicted_outcomes = []
        affected_systems = []
        
        if initial_severity > 0.8:
            predicted_outcomes.append({
                "outcome": "System-wide performance degradation",
                "probability": 0.7,
                "time_to_impact_hours": 1,
            })
            affected_systems.extend(["intel_engine", "predictive_ai", "city_brain"])
        
        if initial_severity > 0.6:
            predicted_outcomes.append({
                "outcome": "Secondary system alerts",
                "probability": 0.6,
                "time_to_impact_hours": 2,
            })
            affected_systems.extend(["emergency_management", "officer_assist"])
        
        if initial_severity > 0.4:
            predicted_outcomes.append({
                "outcome": "Increased operator workload",
                "probability": 0.5,
                "time_to_impact_hours": 4,
            })
        
        mitigation_options = [
            "Proactive resource scaling",
            "Enable circuit breakers",
            "Activate backup systems",
            "Notify relevant teams",
        ]
        
        overall_probability = sum(o["probability"] for o in predicted_outcomes) / max(len(predicted_outcomes), 1)
        confidence = 0.7 + (0.2 * (1 - initial_severity))
        
        prediction = CascadePrediction(
            prediction_id=prediction_id,
            trigger_event=trigger_event,
            trigger_source=trigger_source,
            predicted_outcomes=predicted_outcomes,
            probability=overall_probability,
            time_horizon_hours=time_horizon_hours,
            affected_systems=list(set(affected_systems)),
            mitigation_options=mitigation_options,
            confidence=confidence,
            timestamp=datetime.utcnow(),
            chain_of_custody_hash=self._generate_hash(f"{prediction_id}:{overall_probability}"),
        )
        
        self.cascade_predictions[prediction_id] = prediction
        return prediction
    
    def create_recommendation(
        self,
        recommendation_type: RecommendationType,
        priority: AlertPriority,
        title: str,
        description: str,
        rationale: str,
        affected_systems: list[str],
        implementation_steps: list[str],
        expected_outcome: str,
        risk_if_ignored: str,
        deadline_hours: Optional[int] = None,
    ) -> SentinelRecommendation:
        """Create a recommendation."""
        recommendation_id = f"REC-{hashlib.sha256(f'{title}:{datetime.utcnow().isoformat()}'.encode()).hexdigest()[:8].upper()}"
        
        deadline = datetime.utcnow() + timedelta(hours=deadline_hours) if deadline_hours else None
        
        recommendation = SentinelRecommendation(
            recommendation_id=recommendation_id,
            recommendation_type=recommendation_type,
            priority=priority,
            title=title,
            description=description,
            rationale=rationale,
            affected_systems=affected_systems,
            implementation_steps=implementation_steps,
            expected_outcome=expected_outcome,
            risk_if_ignored=risk_if_ignored,
            deadline=deadline,
            accepted=False,
            implemented=False,
            timestamp=datetime.utcnow(),
            chain_of_custody_hash=self._generate_hash(f"{recommendation_id}:{recommendation_type.value}"),
        )
        
        self.recommendations[recommendation_id] = recommendation
        return recommendation
    
    def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> bool:
        """Acknowledge a consolidated alert."""
        alert = self.consolidated_alerts.get(alert_id)
        if alert:
            alert.acknowledged = True
            alert.assigned_to = acknowledged_by
            return True
        return False
    
    def resolve_alert(self, alert_id: str, resolution_notes: str) -> bool:
        """Resolve a consolidated alert."""
        alert = self.consolidated_alerts.get(alert_id)
        if alert:
            alert.resolved = True
            return True
        return False
    
    def acknowledge_command_alert(
        self,
        alert_id: str,
        response: str,
    ) -> bool:
        """Acknowledge a command staff alert."""
        alert = self.command_alerts.get(alert_id)
        if alert:
            alert.acknowledged = True
            alert.acknowledged_at = datetime.utcnow()
            alert.response = response
            return True
        return False
    
    def accept_recommendation(self, recommendation_id: str) -> bool:
        """Accept a recommendation."""
        rec = self.recommendations.get(recommendation_id)
        if rec:
            rec.accepted = True
            return True
        return False
    
    def implement_recommendation(self, recommendation_id: str) -> bool:
        """Mark a recommendation as implemented."""
        rec = self.recommendations.get(recommendation_id)
        if rec and rec.accepted:
            rec.implemented = True
            return True
        return False
    
    def get_active_alerts(self, priority: Optional[AlertPriority] = None) -> list[ConsolidatedAlert]:
        """Get active (unresolved) alerts."""
        alerts = [a for a in self.consolidated_alerts.values() if not a.resolved]
        if priority:
            alerts = [a for a in alerts if a.priority == priority]
        return sorted(alerts, key=lambda a: (a.priority.value, a.timestamp))
    
    def get_pending_action_requests(self) -> list[AutonomousActionRequest]:
        """Get pending action requests."""
        return [
            r for r in self.action_requests.values()
            if r.approval_status in [ActionApproval.PENDING, ActionApproval.ESCALATED]
        ]
    
    def get_pending_recommendations(self) -> list[SentinelRecommendation]:
        """Get pending (unaccepted) recommendations."""
        return [r for r in self.recommendations.values() if not r.accepted]
    
    def get_command_alerts(self, unacknowledged_only: bool = False) -> list[CommandStaffAlert]:
        """Get command staff alerts."""
        alerts = list(self.command_alerts.values())
        if unacknowledged_only:
            alerts = [a for a in alerts if not a.acknowledged]
        return sorted(alerts, key=lambda a: (a.priority.value, a.sent_at))
    
    def get_dashboard_summary(self) -> dict:
        """Get summary for supervisor dashboard."""
        active_alerts = self.get_active_alerts()
        p1_alerts = [a for a in active_alerts if a.priority == AlertPriority.P1_CRITICAL]
        p2_alerts = [a for a in active_alerts if a.priority == AlertPriority.P2_HIGH]
        
        pending_requests = self.get_pending_action_requests()
        pending_recommendations = self.get_pending_recommendations()
        unack_command_alerts = [a for a in self.command_alerts.values() if not a.acknowledged]
        
        return {
            "active_alerts": len(active_alerts),
            "p1_critical_alerts": len(p1_alerts),
            "p2_high_alerts": len(p2_alerts),
            "pending_action_requests": len(pending_requests),
            "pending_recommendations": len(pending_recommendations),
            "unacknowledged_command_alerts": len(unack_command_alerts),
            "cascade_predictions_active": len(self.cascade_predictions),
            "system_status": "CRITICAL" if p1_alerts else "WARNING" if p2_alerts else "NORMAL",
            "timestamp": datetime.utcnow().isoformat(),
        }
    
    def get_statistics(self) -> dict:
        """Get sentinel engine statistics."""
        total_alerts = len(self.consolidated_alerts)
        resolved_alerts = sum(1 for a in self.consolidated_alerts.values() if a.resolved)
        
        total_requests = len(self.action_requests)
        approved_requests = sum(1 for r in self.action_requests.values() if r.approval_status == ActionApproval.APPROVED)
        denied_requests = sum(1 for r in self.action_requests.values() if r.approval_status == ActionApproval.DENIED)
        
        return {
            "total_alerts": total_alerts,
            "resolved_alerts": resolved_alerts,
            "resolution_rate": resolved_alerts / total_alerts if total_alerts > 0 else 1.0,
            "total_action_requests": total_requests,
            "approved_requests": approved_requests,
            "denied_requests": denied_requests,
            "approval_rate": approved_requests / total_requests if total_requests > 0 else 1.0,
            "cascade_predictions": len(self.cascade_predictions),
            "recommendations_issued": len(self.recommendations),
            "command_alerts_sent": len(self.command_alerts),
            "timestamp": datetime.utcnow().isoformat(),
        }
