"""
Mission Reasoning Engine

Converts tasks into actionable mission steps with:
- Risk and obstacle prediction
- Task assignment to drones, robots, or units
- Legal/policy violation checking
- Human approval requests when required
- Outcome evaluation (branch prediction)

Ties all personas into one shared decision model.
"""

import hashlib
import uuid
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple

from backend.app.personas.persona_engine import (
    PersonaEngine,
    PersonaType,
    PersonaStatus,
    Persona,
    MissionContext,
)


class MissionStatus(Enum):
    """Status of a mission."""
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    BLOCKED = "blocked"


class MissionPriority(Enum):
    """Priority levels for missions."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    ROUTINE = "routine"


class TaskType(Enum):
    """Types of mission tasks."""
    RECONNAISSANCE = "reconnaissance"
    SURVEILLANCE = "surveillance"
    PATROL = "patrol"
    RESPONSE = "response"
    INVESTIGATION = "investigation"
    COORDINATION = "coordination"
    ANALYSIS = "analysis"
    COMMUNICATION = "communication"
    DEPLOYMENT = "deployment"
    EXTRACTION = "extraction"
    DEESCALATION = "deescalation"
    DOCUMENTATION = "documentation"
    SUPPORT = "support"


class ResourceType(Enum):
    """Types of resources that can be assigned."""
    PATROL_UNIT = "patrol_unit"
    DETECTIVE = "detective"
    SUPERVISOR = "supervisor"
    DRONE = "drone"
    GROUND_ROBOT = "ground_robot"
    K9_UNIT = "k9_unit"
    SWAT = "swat"
    NEGOTIATOR = "negotiator"
    MEDICAL = "medical"
    FIRE = "fire"
    ANALYST = "analyst"
    DISPATCHER = "dispatcher"


class RiskLevel(Enum):
    """Risk levels for missions and tasks."""
    MINIMAL = "minimal"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    EXTREME = "extreme"


class ApprovalStatus(Enum):
    """Status of approval requests."""
    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"
    CONDITIONAL = "conditional"
    EXPIRED = "expired"


@dataclass
class RiskAssessment:
    """Assessment of risks for a mission or task."""
    assessment_id: str
    risk_level: RiskLevel
    risk_factors: List[Dict[str, Any]]
    mitigation_strategies: List[str]
    probability_of_success: float
    potential_casualties: int
    property_damage_risk: float
    legal_exposure: float
    public_relations_risk: float
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "assessment_id": self.assessment_id,
            "risk_level": self.risk_level.value,
            "risk_factors": self.risk_factors,
            "mitigation_strategies": self.mitigation_strategies,
            "probability_of_success": self.probability_of_success,
            "potential_casualties": self.potential_casualties,
            "property_damage_risk": self.property_damage_risk,
            "legal_exposure": self.legal_exposure,
            "public_relations_risk": self.public_relations_risk,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class PolicyViolation:
    """Detected policy or legal violation."""
    violation_id: str
    violation_type: str
    description: str
    severity: str
    policy_reference: str
    blocking: bool
    remediation: Optional[str]
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "violation_id": self.violation_id,
            "violation_type": self.violation_type,
            "description": self.description,
            "severity": self.severity,
            "policy_reference": self.policy_reference,
            "blocking": self.blocking,
            "remediation": self.remediation,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class ApprovalRequest:
    """Request for human approval."""
    request_id: str
    mission_id: str
    task_id: Optional[str]
    request_type: str
    description: str
    urgency: MissionPriority
    requested_by: str
    required_authority: str
    status: ApprovalStatus = ApprovalStatus.PENDING
    approved_by: Optional[str] = None
    approval_notes: Optional[str] = None
    conditions: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    chain_of_custody_hash: str = ""
    
    def __post_init__(self):
        if not self.chain_of_custody_hash:
            self.chain_of_custody_hash = self._generate_hash()
        if not self.expires_at:
            expiry_hours = {
                MissionPriority.CRITICAL: 0.5,
                MissionPriority.HIGH: 2,
                MissionPriority.MEDIUM: 8,
                MissionPriority.LOW: 24,
                MissionPriority.ROUTINE: 48,
            }
            self.expires_at = self.created_at + timedelta(hours=expiry_hours.get(self.urgency, 24))
    
    def _generate_hash(self) -> str:
        data = f"{self.request_id}:{self.mission_id}:{self.request_type}:{self.created_at.isoformat()}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    def approve(self, approved_by: str, notes: Optional[str] = None, conditions: Optional[List[str]] = None) -> None:
        """Approve the request."""
        self.status = ApprovalStatus.CONDITIONAL if conditions else ApprovalStatus.APPROVED
        self.approved_by = approved_by
        self.approval_notes = notes
        self.conditions = conditions or []
        self.resolved_at = datetime.utcnow()
    
    def deny(self, denied_by: str, reason: str) -> None:
        """Deny the request."""
        self.status = ApprovalStatus.DENIED
        self.approved_by = denied_by
        self.approval_notes = reason
        self.resolved_at = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "request_id": self.request_id,
            "mission_id": self.mission_id,
            "task_id": self.task_id,
            "request_type": self.request_type,
            "description": self.description,
            "urgency": self.urgency.value,
            "requested_by": self.requested_by,
            "required_authority": self.required_authority,
            "status": self.status.value,
            "approved_by": self.approved_by,
            "approval_notes": self.approval_notes,
            "conditions": self.conditions,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "chain_of_custody_hash": self.chain_of_custody_hash,
        }


@dataclass
class MissionTask:
    """Individual task within a mission."""
    task_id: str
    mission_id: str
    task_type: TaskType
    description: str
    sequence_number: int
    assigned_resources: List[Dict[str, Any]] = field(default_factory=list)
    assigned_personas: List[str] = field(default_factory=list)
    prerequisites: List[str] = field(default_factory=list)
    estimated_duration_minutes: int = 30
    actual_duration_minutes: Optional[int] = None
    status: str = "pending"
    risk_assessment: Optional[RiskAssessment] = None
    policy_violations: List[PolicyViolation] = field(default_factory=list)
    approval_required: bool = False
    approval_request: Optional[ApprovalRequest] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    result: Optional[str] = None
    notes: List[str] = field(default_factory=list)
    chain_of_custody_hash: str = ""
    
    def __post_init__(self):
        if not self.chain_of_custody_hash:
            self.chain_of_custody_hash = self._generate_hash()
    
    def _generate_hash(self) -> str:
        data = f"{self.task_id}:{self.mission_id}:{self.task_type.value}:{self.sequence_number}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    def start(self) -> None:
        """Start the task."""
        self.status = "in_progress"
        self.start_time = datetime.utcnow()
    
    def complete(self, result: str) -> None:
        """Complete the task."""
        self.status = "completed"
        self.end_time = datetime.utcnow()
        self.result = result
        if self.start_time:
            self.actual_duration_minutes = int((self.end_time - self.start_time).total_seconds() / 60)
    
    def fail(self, reason: str) -> None:
        """Mark task as failed."""
        self.status = "failed"
        self.end_time = datetime.utcnow()
        self.result = f"Failed: {reason}"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "mission_id": self.mission_id,
            "task_type": self.task_type.value,
            "description": self.description,
            "sequence_number": self.sequence_number,
            "assigned_resources": self.assigned_resources,
            "assigned_personas": self.assigned_personas,
            "prerequisites": self.prerequisites,
            "estimated_duration_minutes": self.estimated_duration_minutes,
            "actual_duration_minutes": self.actual_duration_minutes,
            "status": self.status,
            "risk_assessment": self.risk_assessment.to_dict() if self.risk_assessment else None,
            "policy_violations": [v.to_dict() for v in self.policy_violations],
            "approval_required": self.approval_required,
            "approval_request": self.approval_request.to_dict() if self.approval_request else None,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "result": self.result,
            "notes": self.notes,
            "chain_of_custody_hash": self.chain_of_custody_hash,
        }


@dataclass
class MissionOutcome:
    """Predicted or actual outcome of a mission."""
    outcome_id: str
    mission_id: str
    outcome_type: str
    probability: float
    description: str
    impact_assessment: Dict[str, Any]
    contributing_factors: List[str]
    is_prediction: bool = True
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "outcome_id": self.outcome_id,
            "mission_id": self.mission_id,
            "outcome_type": self.outcome_type,
            "probability": self.probability,
            "description": self.description,
            "impact_assessment": self.impact_assessment,
            "contributing_factors": self.contributing_factors,
            "is_prediction": self.is_prediction,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class Mission:
    """Complete mission with tasks and reasoning."""
    mission_id: str
    title: str
    description: str
    mission_type: str
    priority: MissionPriority
    status: MissionStatus
    created_by: str
    assigned_personas: List[str] = field(default_factory=list)
    tasks: List[MissionTask] = field(default_factory=list)
    objectives: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    resources_required: List[Dict[str, Any]] = field(default_factory=list)
    resources_assigned: List[Dict[str, Any]] = field(default_factory=list)
    location: Optional[str] = None
    risk_assessment: Optional[RiskAssessment] = None
    policy_violations: List[PolicyViolation] = field(default_factory=list)
    approval_requests: List[ApprovalRequest] = field(default_factory=list)
    predicted_outcomes: List[MissionOutcome] = field(default_factory=list)
    actual_outcome: Optional[MissionOutcome] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    deadline: Optional[datetime] = None
    chain_of_custody_hash: str = ""
    
    def __post_init__(self):
        if not self.chain_of_custody_hash:
            self.chain_of_custody_hash = self._generate_hash()
    
    def _generate_hash(self) -> str:
        data = f"{self.mission_id}:{self.title}:{self.mission_type}:{self.created_at.isoformat()}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    def add_task(self, task: MissionTask) -> None:
        """Add a task to the mission."""
        self.tasks.append(task)
    
    def get_next_task(self) -> Optional[MissionTask]:
        """Get the next pending task."""
        pending = [t for t in self.tasks if t.status == "pending"]
        if not pending:
            return None
        
        for task in sorted(pending, key=lambda t: t.sequence_number):
            if all(
                any(t.task_id == prereq and t.status == "completed" for t in self.tasks)
                for prereq in task.prerequisites
            ) or not task.prerequisites:
                return task
        return None
    
    def get_progress(self) -> Dict[str, Any]:
        """Get mission progress."""
        total = len(self.tasks)
        completed = len([t for t in self.tasks if t.status == "completed"])
        in_progress = len([t for t in self.tasks if t.status == "in_progress"])
        failed = len([t for t in self.tasks if t.status == "failed"])
        
        return {
            "total_tasks": total,
            "completed": completed,
            "in_progress": in_progress,
            "failed": failed,
            "pending": total - completed - in_progress - failed,
            "completion_percentage": (completed / total * 100) if total > 0 else 0,
        }
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "mission_id": self.mission_id,
            "title": self.title,
            "description": self.description,
            "mission_type": self.mission_type,
            "priority": self.priority.value,
            "status": self.status.value,
            "created_by": self.created_by,
            "assigned_personas": self.assigned_personas,
            "tasks": [t.to_dict() for t in self.tasks],
            "objectives": self.objectives,
            "constraints": self.constraints,
            "resources_required": self.resources_required,
            "resources_assigned": self.resources_assigned,
            "location": self.location,
            "risk_assessment": self.risk_assessment.to_dict() if self.risk_assessment else None,
            "policy_violations": [v.to_dict() for v in self.policy_violations],
            "approval_requests": [a.to_dict() for a in self.approval_requests],
            "predicted_outcomes": [o.to_dict() for o in self.predicted_outcomes],
            "actual_outcome": self.actual_outcome.to_dict() if self.actual_outcome else None,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "progress": self.get_progress(),
            "chain_of_custody_hash": self.chain_of_custody_hash,
        }


class MissionReasoner:
    """
    Mission Reasoning Engine for AI Personas.
    
    Converts tasks into actionable mission steps with:
    - Risk and obstacle prediction
    - Task assignment to drones, robots, or units
    - Legal/policy violation checking
    - Human approval requests when required
    - Outcome evaluation (branch prediction)
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
        
        self.persona_engine = PersonaEngine()
        self.missions: Dict[str, Mission] = {}
        self.approval_requests: Dict[str, ApprovalRequest] = {}
        self.policy_rules: List[Dict[str, Any]] = []
        self.resource_pool: Dict[str, Dict[str, Any]] = {}
        
        self._initialize_policy_rules()
        self._initialize_resource_pool()
        self._initialized = True
    
    def _initialize_policy_rules(self) -> None:
        """Initialize policy rules for violation checking."""
        self.policy_rules = [
            {
                "rule_id": "PR-001",
                "name": "Warrant Requirement",
                "description": "Surveillance and search operations require valid warrant",
                "applicable_task_types": [TaskType.SURVEILLANCE, TaskType.RECONNAISSANCE],
                "conditions": {"requires_warrant": True},
                "severity": "critical",
                "blocking": True,
            },
            {
                "rule_id": "PR-002",
                "name": "Use of Force Authorization",
                "description": "Tactical operations require command authorization",
                "applicable_task_types": [TaskType.RESPONSE, TaskType.EXTRACTION],
                "conditions": {"requires_authorization": True},
                "severity": "critical",
                "blocking": True,
            },
            {
                "rule_id": "PR-003",
                "name": "Drone Flight Restrictions",
                "description": "Drone operations must comply with FAA regulations",
                "applicable_task_types": [TaskType.RECONNAISSANCE, TaskType.SURVEILLANCE],
                "conditions": {"resource_type": ResourceType.DRONE},
                "severity": "high",
                "blocking": True,
            },
            {
                "rule_id": "PR-004",
                "name": "Privacy Protection",
                "description": "Operations must not violate citizen privacy rights",
                "applicable_task_types": [TaskType.SURVEILLANCE, TaskType.INVESTIGATION],
                "conditions": {"privacy_sensitive": True},
                "severity": "high",
                "blocking": True,
            },
            {
                "rule_id": "PR-005",
                "name": "Officer Safety Protocol",
                "description": "High-risk operations require backup units",
                "applicable_task_types": [TaskType.RESPONSE, TaskType.EXTRACTION],
                "conditions": {"risk_level": RiskLevel.HIGH},
                "severity": "high",
                "blocking": False,
            },
        ]
    
    def _initialize_resource_pool(self) -> None:
        """Initialize available resources."""
        self.resource_pool = {
            "UNIT-101": {"type": ResourceType.PATROL_UNIT, "status": "available", "location": "sector_1"},
            "UNIT-102": {"type": ResourceType.PATROL_UNIT, "status": "available", "location": "sector_2"},
            "UNIT-103": {"type": ResourceType.PATROL_UNIT, "status": "busy", "location": "sector_3"},
            "DET-201": {"type": ResourceType.DETECTIVE, "status": "available", "location": "headquarters"},
            "DET-202": {"type": ResourceType.DETECTIVE, "status": "available", "location": "headquarters"},
            "DRONE-301": {"type": ResourceType.DRONE, "status": "available", "location": "hangar"},
            "DRONE-302": {"type": ResourceType.DRONE, "status": "available", "location": "hangar"},
            "ROBOT-401": {"type": ResourceType.GROUND_ROBOT, "status": "available", "location": "garage"},
            "K9-501": {"type": ResourceType.K9_UNIT, "status": "available", "location": "kennel"},
            "SWAT-601": {"type": ResourceType.SWAT, "status": "standby", "location": "headquarters"},
            "NEG-701": {"type": ResourceType.NEGOTIATOR, "status": "available", "location": "headquarters"},
        }
    
    def create_mission(
        self,
        title: str,
        description: str,
        mission_type: str,
        priority: MissionPriority,
        created_by: str,
        objectives: List[str],
        constraints: Optional[List[str]] = None,
        location: Optional[str] = None,
        deadline: Optional[datetime] = None,
    ) -> Mission:
        """Create a new mission."""
        mission = Mission(
            mission_id=str(uuid.uuid4()),
            title=title,
            description=description,
            mission_type=mission_type,
            priority=priority,
            status=MissionStatus.DRAFT,
            created_by=created_by,
            objectives=objectives,
            constraints=constraints or [],
            location=location,
            deadline=deadline,
        )
        
        self.missions[mission.mission_id] = mission
        return mission
    
    def plan_mission(self, mission_id: str) -> Mission:
        """Plan mission by generating tasks from objectives."""
        mission = self.missions.get(mission_id)
        if not mission:
            raise ValueError(f"Mission not found: {mission_id}")
        
        tasks = self._generate_tasks_from_objectives(mission)
        for task in tasks:
            mission.add_task(task)
        
        mission.risk_assessment = self._assess_mission_risk(mission)
        
        violations = self._check_policy_violations(mission)
        mission.policy_violations = violations
        
        if any(v.blocking for v in violations):
            mission.status = MissionStatus.BLOCKED
        else:
            mission.status = MissionStatus.PENDING_APPROVAL if self._requires_approval(mission) else MissionStatus.APPROVED
        
        mission.predicted_outcomes = self._predict_outcomes(mission)
        
        return mission
    
    def _generate_tasks_from_objectives(self, mission: Mission) -> List[MissionTask]:
        """Generate tasks from mission objectives."""
        tasks = []
        sequence = 1
        
        for objective in mission.objectives:
            objective_lower = objective.lower()
            
            if any(word in objective_lower for word in ["survey", "recon", "scout"]):
                task_type = TaskType.RECONNAISSANCE
            elif any(word in objective_lower for word in ["watch", "monitor", "observe"]):
                task_type = TaskType.SURVEILLANCE
            elif any(word in objective_lower for word in ["patrol", "secure", "protect"]):
                task_type = TaskType.PATROL
            elif any(word in objective_lower for word in ["respond", "intervene", "engage"]):
                task_type = TaskType.RESPONSE
            elif any(word in objective_lower for word in ["investigate", "examine", "analyze"]):
                task_type = TaskType.INVESTIGATION
            elif any(word in objective_lower for word in ["coordinate", "sync", "collaborate"]):
                task_type = TaskType.COORDINATION
            elif any(word in objective_lower for word in ["calm", "deescalate", "negotiate"]):
                task_type = TaskType.DEESCALATION
            elif any(word in objective_lower for word in ["deploy", "position", "station"]):
                task_type = TaskType.DEPLOYMENT
            elif any(word in objective_lower for word in ["extract", "rescue", "retrieve"]):
                task_type = TaskType.EXTRACTION
            elif any(word in objective_lower for word in ["document", "record", "report"]):
                task_type = TaskType.DOCUMENTATION
            else:
                task_type = TaskType.SUPPORT
            
            task = MissionTask(
                task_id=str(uuid.uuid4()),
                mission_id=mission.mission_id,
                task_type=task_type,
                description=objective,
                sequence_number=sequence,
                estimated_duration_minutes=self._estimate_task_duration(task_type),
            )
            
            task.risk_assessment = self._assess_task_risk(task, mission)
            
            task_violations = self._check_task_policy_violations(task)
            task.policy_violations = task_violations
            task.approval_required = any(v.blocking for v in task_violations) or task_type in [TaskType.RESPONSE, TaskType.EXTRACTION, TaskType.SURVEILLANCE]
            
            tasks.append(task)
            sequence += 1
        
        return tasks
    
    def _estimate_task_duration(self, task_type: TaskType) -> int:
        """Estimate task duration in minutes."""
        durations = {
            TaskType.RECONNAISSANCE: 45,
            TaskType.SURVEILLANCE: 120,
            TaskType.PATROL: 60,
            TaskType.RESPONSE: 30,
            TaskType.INVESTIGATION: 180,
            TaskType.COORDINATION: 30,
            TaskType.ANALYSIS: 90,
            TaskType.COMMUNICATION: 15,
            TaskType.DEPLOYMENT: 20,
            TaskType.EXTRACTION: 45,
            TaskType.DEESCALATION: 60,
            TaskType.DOCUMENTATION: 30,
            TaskType.SUPPORT: 30,
        }
        return durations.get(task_type, 30)
    
    def _assess_mission_risk(self, mission: Mission) -> RiskAssessment:
        """Assess overall mission risk."""
        risk_factors = []
        
        if mission.priority == MissionPriority.CRITICAL:
            risk_factors.append({"factor": "critical_priority", "weight": 0.3})
        
        high_risk_tasks = [t for t in mission.tasks if t.task_type in [TaskType.RESPONSE, TaskType.EXTRACTION]]
        if high_risk_tasks:
            risk_factors.append({"factor": "high_risk_tasks", "weight": 0.4, "count": len(high_risk_tasks)})
        
        if len(mission.tasks) > 5:
            risk_factors.append({"factor": "complex_mission", "weight": 0.2})
        
        total_weight = sum(f["weight"] for f in risk_factors)
        
        if total_weight >= 0.7:
            risk_level = RiskLevel.HIGH
        elif total_weight >= 0.5:
            risk_level = RiskLevel.MODERATE
        elif total_weight >= 0.3:
            risk_level = RiskLevel.LOW
        else:
            risk_level = RiskLevel.MINIMAL
        
        return RiskAssessment(
            assessment_id=str(uuid.uuid4()),
            risk_level=risk_level,
            risk_factors=risk_factors,
            mitigation_strategies=self._generate_mitigation_strategies(risk_factors),
            probability_of_success=max(0.5, 1.0 - total_weight),
            potential_casualties=1 if risk_level in [RiskLevel.HIGH, RiskLevel.EXTREME] else 0,
            property_damage_risk=total_weight * 0.5,
            legal_exposure=total_weight * 0.3,
            public_relations_risk=total_weight * 0.2,
        )
    
    def _assess_task_risk(self, task: MissionTask, mission: Mission) -> RiskAssessment:
        """Assess risk for a specific task."""
        risk_factors = []
        
        high_risk_types = [TaskType.RESPONSE, TaskType.EXTRACTION, TaskType.SURVEILLANCE]
        if task.task_type in high_risk_types:
            risk_factors.append({"factor": "high_risk_task_type", "weight": 0.4})
        
        if mission.priority == MissionPriority.CRITICAL:
            risk_factors.append({"factor": "critical_mission", "weight": 0.2})
        
        total_weight = sum(f["weight"] for f in risk_factors)
        
        if total_weight >= 0.6:
            risk_level = RiskLevel.HIGH
        elif total_weight >= 0.4:
            risk_level = RiskLevel.MODERATE
        elif total_weight >= 0.2:
            risk_level = RiskLevel.LOW
        else:
            risk_level = RiskLevel.MINIMAL
        
        return RiskAssessment(
            assessment_id=str(uuid.uuid4()),
            risk_level=risk_level,
            risk_factors=risk_factors,
            mitigation_strategies=[],
            probability_of_success=max(0.6, 1.0 - total_weight),
            potential_casualties=0,
            property_damage_risk=total_weight * 0.3,
            legal_exposure=total_weight * 0.2,
            public_relations_risk=total_weight * 0.1,
        )
    
    def _generate_mitigation_strategies(self, risk_factors: List[Dict[str, Any]]) -> List[str]:
        """Generate mitigation strategies for risk factors."""
        strategies = []
        
        for factor in risk_factors:
            if factor["factor"] == "critical_priority":
                strategies.append("Ensure command oversight throughout mission")
            elif factor["factor"] == "high_risk_tasks":
                strategies.append("Deploy backup units for high-risk tasks")
                strategies.append("Establish clear communication protocols")
            elif factor["factor"] == "complex_mission":
                strategies.append("Break mission into phases with checkpoints")
        
        return strategies
    
    def _check_policy_violations(self, mission: Mission) -> List[PolicyViolation]:
        """Check mission for policy violations."""
        violations = []
        
        for task in mission.tasks:
            task_violations = self._check_task_policy_violations(task)
            violations.extend(task_violations)
        
        return violations
    
    def _check_task_policy_violations(self, task: MissionTask) -> List[PolicyViolation]:
        """Check task for policy violations."""
        violations = []
        
        for rule in self.policy_rules:
            applicable_types = rule.get("applicable_task_types", [])
            if task.task_type in applicable_types:
                conditions = rule.get("conditions", {})
                
                if conditions.get("requires_warrant") and task.task_type in [TaskType.SURVEILLANCE, TaskType.RECONNAISSANCE]:
                    violations.append(PolicyViolation(
                        violation_id=str(uuid.uuid4()),
                        violation_type="warrant_required",
                        description=f"Task '{task.description}' requires valid warrant",
                        severity=rule["severity"],
                        policy_reference=rule["rule_id"],
                        blocking=rule["blocking"],
                        remediation="Obtain warrant before proceeding",
                    ))
                
                if conditions.get("requires_authorization") and task.task_type in [TaskType.RESPONSE, TaskType.EXTRACTION]:
                    violations.append(PolicyViolation(
                        violation_id=str(uuid.uuid4()),
                        violation_type="authorization_required",
                        description=f"Task '{task.description}' requires command authorization",
                        severity=rule["severity"],
                        policy_reference=rule["rule_id"],
                        blocking=rule["blocking"],
                        remediation="Obtain command authorization before proceeding",
                    ))
        
        return violations
    
    def _requires_approval(self, mission: Mission) -> bool:
        """Check if mission requires human approval."""
        if mission.priority in [MissionPriority.CRITICAL, MissionPriority.HIGH]:
            return True
        
        if any(t.approval_required for t in mission.tasks):
            return True
        
        if mission.risk_assessment and mission.risk_assessment.risk_level in [RiskLevel.HIGH, RiskLevel.EXTREME]:
            return True
        
        return False
    
    def _predict_outcomes(self, mission: Mission) -> List[MissionOutcome]:
        """Predict possible outcomes for mission."""
        outcomes = []
        
        success_prob = mission.risk_assessment.probability_of_success if mission.risk_assessment else 0.7
        
        outcomes.append(MissionOutcome(
            outcome_id=str(uuid.uuid4()),
            mission_id=mission.mission_id,
            outcome_type="success",
            probability=success_prob,
            description="Mission objectives achieved successfully",
            impact_assessment={
                "public_safety": "improved",
                "resource_utilization": "optimal",
                "legal_compliance": "maintained",
            },
            contributing_factors=["adequate_resources", "proper_planning", "team_coordination"],
        ))
        
        outcomes.append(MissionOutcome(
            outcome_id=str(uuid.uuid4()),
            mission_id=mission.mission_id,
            outcome_type="partial_success",
            probability=(1 - success_prob) * 0.6,
            description="Some objectives achieved, others require follow-up",
            impact_assessment={
                "public_safety": "maintained",
                "resource_utilization": "moderate",
                "legal_compliance": "maintained",
            },
            contributing_factors=["resource_constraints", "unexpected_obstacles"],
        ))
        
        outcomes.append(MissionOutcome(
            outcome_id=str(uuid.uuid4()),
            mission_id=mission.mission_id,
            outcome_type="failure",
            probability=(1 - success_prob) * 0.4,
            description="Mission objectives not achieved",
            impact_assessment={
                "public_safety": "at_risk",
                "resource_utilization": "wasted",
                "legal_compliance": "review_required",
            },
            contributing_factors=["insufficient_resources", "poor_intelligence", "external_factors"],
        ))
        
        return outcomes
    
    def request_approval(
        self,
        mission_id: str,
        task_id: Optional[str],
        request_type: str,
        description: str,
        requested_by: str,
        required_authority: str,
    ) -> ApprovalRequest:
        """Create an approval request."""
        mission = self.missions.get(mission_id)
        if not mission:
            raise ValueError(f"Mission not found: {mission_id}")
        
        request = ApprovalRequest(
            request_id=str(uuid.uuid4()),
            mission_id=mission_id,
            task_id=task_id,
            request_type=request_type,
            description=description,
            urgency=mission.priority,
            requested_by=requested_by,
            required_authority=required_authority,
        )
        
        self.approval_requests[request.request_id] = request
        mission.approval_requests.append(request)
        
        return request
    
    def approve_request(
        self,
        request_id: str,
        approved_by: str,
        notes: Optional[str] = None,
        conditions: Optional[List[str]] = None,
    ) -> bool:
        """Approve an approval request."""
        request = self.approval_requests.get(request_id)
        if not request:
            return False
        
        request.approve(approved_by, notes, conditions)
        
        mission = self.missions.get(request.mission_id)
        if mission:
            pending_requests = [r for r in mission.approval_requests if r.status == ApprovalStatus.PENDING]
            if not pending_requests and mission.status == MissionStatus.PENDING_APPROVAL:
                mission.status = MissionStatus.APPROVED
        
        return True
    
    def deny_request(self, request_id: str, denied_by: str, reason: str) -> bool:
        """Deny an approval request."""
        request = self.approval_requests.get(request_id)
        if not request:
            return False
        
        request.deny(denied_by, reason)
        
        mission = self.missions.get(request.mission_id)
        if mission:
            mission.status = MissionStatus.BLOCKED
        
        return True
    
    def assign_resources(self, mission_id: str) -> Dict[str, Any]:
        """Assign resources to mission tasks."""
        mission = self.missions.get(mission_id)
        if not mission:
            raise ValueError(f"Mission not found: {mission_id}")
        
        assignments = []
        
        for task in mission.tasks:
            required_resources = self._determine_required_resources(task)
            assigned = []
            
            for req in required_resources:
                resource = self._find_available_resource(req["type"])
                if resource:
                    assigned.append({
                        "resource_id": resource[0],
                        "resource_type": resource[1]["type"].value,
                        "task_id": task.task_id,
                    })
                    self.resource_pool[resource[0]]["status"] = "assigned"
            
            task.assigned_resources = assigned
            assignments.extend(assigned)
        
        mission.resources_assigned = assignments
        return {"mission_id": mission_id, "assignments": assignments}
    
    def _determine_required_resources(self, task: MissionTask) -> List[Dict[str, Any]]:
        """Determine required resources for a task."""
        requirements = []
        
        resource_mapping = {
            TaskType.RECONNAISSANCE: [ResourceType.DRONE],
            TaskType.SURVEILLANCE: [ResourceType.DRONE, ResourceType.PATROL_UNIT],
            TaskType.PATROL: [ResourceType.PATROL_UNIT],
            TaskType.RESPONSE: [ResourceType.PATROL_UNIT, ResourceType.PATROL_UNIT],
            TaskType.INVESTIGATION: [ResourceType.DETECTIVE],
            TaskType.DEESCALATION: [ResourceType.NEGOTIATOR],
            TaskType.EXTRACTION: [ResourceType.SWAT],
            TaskType.DEPLOYMENT: [ResourceType.GROUND_ROBOT],
        }
        
        resource_types = resource_mapping.get(task.task_type, [ResourceType.PATROL_UNIT])
        for rt in resource_types:
            requirements.append({"type": rt, "quantity": 1})
        
        return requirements
    
    def _find_available_resource(self, resource_type: ResourceType) -> Optional[Tuple[str, Dict[str, Any]]]:
        """Find an available resource of the specified type."""
        for resource_id, resource in self.resource_pool.items():
            if resource["type"] == resource_type and resource["status"] == "available":
                return (resource_id, resource)
        return None
    
    def assign_personas(self, mission_id: str) -> Dict[str, Any]:
        """Assign personas to mission based on task types."""
        mission = self.missions.get(mission_id)
        if not mission:
            raise ValueError(f"Mission not found: {mission_id}")
        
        assignments = []
        
        task_to_persona = {
            TaskType.RECONNAISSANCE: PersonaType.APEX_ROBOTICS,
            TaskType.SURVEILLANCE: PersonaType.APEX_INTEL,
            TaskType.PATROL: PersonaType.APEX_PATROL,
            TaskType.RESPONSE: PersonaType.APEX_PATROL,
            TaskType.INVESTIGATION: PersonaType.APEX_INVESTIGATIONS,
            TaskType.COORDINATION: PersonaType.APEX_COMMAND,
            TaskType.ANALYSIS: PersonaType.APEX_INTEL,
            TaskType.DEESCALATION: PersonaType.APEX_CRISIS,
            TaskType.EXTRACTION: PersonaType.APEX_ROBOTICS,
        }
        
        for task in mission.tasks:
            persona_type = task_to_persona.get(task.task_type, PersonaType.APEX_PATROL)
            personas = self.persona_engine.get_personas_by_type(persona_type)
            available = [p for p in personas if p.status in [PersonaStatus.ACTIVE, PersonaStatus.STANDBY]]
            
            if available:
                persona = available[0]
                task.assigned_personas.append(persona.persona_id)
                if persona.persona_id not in mission.assigned_personas:
                    mission.assigned_personas.append(persona.persona_id)
                
                assignments.append({
                    "task_id": task.task_id,
                    "persona_id": persona.persona_id,
                    "persona_name": persona.name,
                    "persona_type": persona.persona_type.value,
                })
        
        return {"mission_id": mission_id, "assignments": assignments}
    
    def start_mission(self, mission_id: str) -> bool:
        """Start executing a mission."""
        mission = self.missions.get(mission_id)
        if not mission:
            return False
        
        if mission.status != MissionStatus.APPROVED:
            return False
        
        mission.status = MissionStatus.IN_PROGRESS
        mission.started_at = datetime.utcnow()
        
        for persona_id in mission.assigned_personas:
            persona = self.persona_engine.get_persona(persona_id)
            if persona:
                self.persona_engine.assign_mission(
                    persona_id,
                    MissionContext(
                        mission_id=mission.mission_id,
                        mission_type=mission.mission_type,
                        objectives=mission.objectives,
                        constraints=mission.constraints,
                        location=mission.location,
                        start_time=mission.started_at,
                        deadline=mission.deadline,
                        priority=mission.priority.value,
                        status="in_progress",
                    )
                )
        
        return True
    
    def complete_mission(self, mission_id: str, success: bool, summary: str) -> bool:
        """Complete a mission."""
        mission = self.missions.get(mission_id)
        if not mission:
            return False
        
        mission.status = MissionStatus.COMPLETED if success else MissionStatus.FAILED
        mission.completed_at = datetime.utcnow()
        
        mission.actual_outcome = MissionOutcome(
            outcome_id=str(uuid.uuid4()),
            mission_id=mission_id,
            outcome_type="success" if success else "failure",
            probability=1.0,
            description=summary,
            impact_assessment={"result": "success" if success else "failure"},
            contributing_factors=[],
            is_prediction=False,
        )
        
        for persona_id in mission.assigned_personas:
            self.persona_engine.complete_mission(persona_id, success, summary)
        
        for assignment in mission.resources_assigned:
            resource_id = assignment.get("resource_id")
            if resource_id in self.resource_pool:
                self.resource_pool[resource_id]["status"] = "available"
        
        return True
    
    def get_mission(self, mission_id: str) -> Optional[Mission]:
        """Get a mission by ID."""
        return self.missions.get(mission_id)
    
    def get_all_missions(self) -> List[Mission]:
        """Get all missions."""
        return list(self.missions.values())
    
    def get_active_missions(self) -> List[Mission]:
        """Get all active missions."""
        return [m for m in self.missions.values() if m.status == MissionStatus.IN_PROGRESS]
    
    def get_pending_approvals(self) -> List[ApprovalRequest]:
        """Get all pending approval requests."""
        return [r for r in self.approval_requests.values() if r.status == ApprovalStatus.PENDING]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get mission reasoner statistics."""
        total_missions = len(self.missions)
        completed = len([m for m in self.missions.values() if m.status == MissionStatus.COMPLETED])
        failed = len([m for m in self.missions.values() if m.status == MissionStatus.FAILED])
        in_progress = len([m for m in self.missions.values() if m.status == MissionStatus.IN_PROGRESS])
        
        return {
            "total_missions": total_missions,
            "completed_missions": completed,
            "failed_missions": failed,
            "in_progress_missions": in_progress,
            "pending_missions": total_missions - completed - failed - in_progress,
            "success_rate": completed / (completed + failed) * 100 if (completed + failed) > 0 else 0,
            "pending_approvals": len(self.get_pending_approvals()),
            "available_resources": len([r for r in self.resource_pool.values() if r["status"] == "available"]),
        }
