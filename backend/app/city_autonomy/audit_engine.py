"""
Phase 24: ActionAuditEngine - Tamper-Proof Audit Logging for Autonomous Actions

This module maintains comprehensive audit logs for all autonomous city operations:
- Every action taken autonomously
- Every action requested
- Every human override
- Every denied action
- Every escalation
- Tamper-proof logs with signature verification
- CJIS, NIST, and FL State Statute compliance
- PDF report generation
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
import uuid
import hashlib
import json
import base64


class AuditEventType(Enum):
    """Types of audit events."""
    ACTION_CREATED = "action_created"
    ACTION_EXECUTED = "action_executed"
    ACTION_COMPLETED = "action_completed"
    ACTION_FAILED = "action_failed"
    ACTION_APPROVED = "action_approved"
    ACTION_DENIED = "action_denied"
    ACTION_ESCALATED = "action_escalated"
    ACTION_CANCELLED = "action_cancelled"
    HUMAN_OVERRIDE = "human_override"
    POLICY_ACTIVATED = "policy_activated"
    POLICY_DEACTIVATED = "policy_deactivated"
    POLICY_UPDATED = "policy_updated"
    EMERGENCY_OVERRIDE_ACTIVATED = "emergency_override_activated"
    EMERGENCY_OVERRIDE_DEACTIVATED = "emergency_override_deactivated"
    ANOMALY_DETECTED = "anomaly_detected"
    ANOMALY_RESOLVED = "anomaly_resolved"
    STABILIZATION_ACTION = "stabilization_action"
    CASCADE_PREDICTION = "cascade_prediction"
    CIRCUIT_BREAKER_TRIGGERED = "circuit_breaker_triggered"
    CIRCUIT_BREAKER_RESET = "circuit_breaker_reset"
    SYSTEM_MODE_CHANGE = "system_mode_change"
    ACCESS_GRANTED = "access_granted"
    ACCESS_DENIED = "access_denied"


class ComplianceStandard(Enum):
    """Compliance standards supported."""
    CJIS = "cjis"  # Criminal Justice Information Services
    NIST = "nist"  # National Institute of Standards and Technology
    FL_STATE = "fl_state"  # Florida State Statutes
    HIPAA = "hipaa"  # Health Insurance Portability and Accountability Act
    SOC2 = "soc2"  # Service Organization Control 2


class AuditSeverity(Enum):
    """Severity levels for audit events."""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ReportPeriod(Enum):
    """Report time periods."""
    HOURLY = "hourly"
    DAILY_24H = "24h"
    WEEKLY_7D = "7d"
    MONTHLY_30D = "30d"
    QUARTERLY = "quarterly"
    ANNUAL = "annual"
    CUSTOM = "custom"


@dataclass
class AuditEntry:
    """Individual audit log entry."""
    entry_id: str
    event_type: AuditEventType
    severity: AuditSeverity
    timestamp: datetime
    actor_id: str
    actor_type: str  # system, human, ai_engine
    actor_name: str
    action_id: Optional[str]
    resource_type: str
    resource_id: str
    description: str
    details: Dict[str, Any]
    previous_state: Optional[Dict[str, Any]] = None
    new_state: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    session_id: Optional[str] = None
    correlation_id: Optional[str] = None
    compliance_tags: List[ComplianceStandard] = field(default_factory=list)
    signature: Optional[str] = None
    previous_entry_hash: Optional[str] = None
    entry_hash: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "entry_id": self.entry_id,
            "event_type": self.event_type.value,
            "severity": self.severity.value,
            "timestamp": self.timestamp.isoformat(),
            "actor_id": self.actor_id,
            "actor_type": self.actor_type,
            "actor_name": self.actor_name,
            "action_id": self.action_id,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "description": self.description,
            "details": self.details,
            "previous_state": self.previous_state,
            "new_state": self.new_state,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "session_id": self.session_id,
            "correlation_id": self.correlation_id,
            "compliance_tags": [c.value for c in self.compliance_tags],
            "signature": self.signature,
            "previous_entry_hash": self.previous_entry_hash,
            "entry_hash": self.entry_hash,
        }


@dataclass
class ChainOfCustody:
    """Chain of custody record for an action or resource."""
    chain_id: str
    resource_type: str
    resource_id: str
    entries: List[AuditEntry]
    created_at: datetime
    last_updated: datetime
    is_sealed: bool = False
    seal_signature: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chain_id": self.chain_id,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "entries": [e.to_dict() for e in self.entries],
            "created_at": self.created_at.isoformat(),
            "last_updated": self.last_updated.isoformat(),
            "is_sealed": self.is_sealed,
            "seal_signature": self.seal_signature,
        }


@dataclass
class ComplianceReport:
    """Compliance report for audit data."""
    report_id: str
    report_type: str
    period: ReportPeriod
    start_date: datetime
    end_date: datetime
    compliance_standard: ComplianceStandard
    generated_at: datetime
    generated_by: str
    summary: Dict[str, Any]
    findings: List[Dict[str, Any]]
    recommendations: List[str]
    signature: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "report_id": self.report_id,
            "report_type": self.report_type,
            "period": self.period.value,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "compliance_standard": self.compliance_standard.value,
            "generated_at": self.generated_at.isoformat(),
            "generated_by": self.generated_by,
            "summary": self.summary,
            "findings": self.findings,
            "recommendations": self.recommendations,
            "signature": self.signature,
        }


@dataclass
class AutonomySummary:
    """Summary of autonomous operations for a time period."""
    summary_id: str
    period: ReportPeriod
    start_date: datetime
    end_date: datetime
    total_actions: int
    actions_by_level: Dict[str, int]
    actions_by_status: Dict[str, int]
    actions_by_category: Dict[str, int]
    human_overrides: int
    denied_actions: int
    escalations: int
    avg_approval_time_minutes: float
    avg_execution_time_ms: float
    anomalies_detected: int
    stabilization_actions: int
    circuit_breaker_triggers: int
    ai_vs_human_ratio: float
    generated_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "summary_id": self.summary_id,
            "period": self.period.value,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "total_actions": self.total_actions,
            "actions_by_level": self.actions_by_level,
            "actions_by_status": self.actions_by_status,
            "actions_by_category": self.actions_by_category,
            "human_overrides": self.human_overrides,
            "denied_actions": self.denied_actions,
            "escalations": self.escalations,
            "avg_approval_time_minutes": self.avg_approval_time_minutes,
            "avg_execution_time_ms": self.avg_execution_time_ms,
            "anomalies_detected": self.anomalies_detected,
            "stabilization_actions": self.stabilization_actions,
            "circuit_breaker_triggers": self.circuit_breaker_triggers,
            "ai_vs_human_ratio": self.ai_vs_human_ratio,
            "generated_at": self.generated_at.isoformat(),
        }


class ActionAuditEngine:
    """
    Engine for maintaining tamper-proof audit logs of all autonomous actions.
    
    Supports CJIS, NIST, and FL State Statute compliance with signature
    verification and comprehensive reporting capabilities.
    """

    def __init__(self, signing_key: Optional[str] = None):
        self._entries: Dict[str, AuditEntry] = {}
        self._entries_by_action: Dict[str, List[str]] = {}
        self._entries_by_resource: Dict[str, List[str]] = {}
        self._chains_of_custody: Dict[str, ChainOfCustody] = {}
        self._compliance_reports: Dict[str, ComplianceReport] = {}
        self._summaries: Dict[str, AutonomySummary] = {}
        self._signing_key = signing_key or "riviera-beach-rtcc-audit-key-2024"
        self._last_entry_hash: Optional[str] = None
        self._entry_sequence: List[str] = []

    def _compute_hash(self, data: str) -> str:
        """Compute SHA-256 hash of data."""
        return hashlib.sha256(data.encode()).hexdigest()

    def _sign_entry(self, entry: AuditEntry) -> str:
        """Sign an audit entry."""
        data_to_sign = json.dumps({
            "entry_id": entry.entry_id,
            "event_type": entry.event_type.value,
            "timestamp": entry.timestamp.isoformat(),
            "actor_id": entry.actor_id,
            "resource_id": entry.resource_id,
            "description": entry.description,
        }, sort_keys=True)
        signature_input = f"{data_to_sign}:{self._signing_key}"
        return self._compute_hash(signature_input)

    def _compute_entry_hash(self, entry: AuditEntry) -> str:
        """Compute hash for blockchain-style chaining."""
        data = json.dumps(entry.to_dict(), sort_keys=True, default=str)
        return self._compute_hash(data)

    def log_event(
        self,
        event_type: AuditEventType,
        actor_id: str,
        actor_type: str,
        actor_name: str,
        resource_type: str,
        resource_id: str,
        description: str,
        details: Optional[Dict[str, Any]] = None,
        action_id: Optional[str] = None,
        previous_state: Optional[Dict[str, Any]] = None,
        new_state: Optional[Dict[str, Any]] = None,
        severity: Optional[AuditSeverity] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        session_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        compliance_tags: Optional[List[ComplianceStandard]] = None,
    ) -> AuditEntry:
        """Log an audit event."""
        # Determine severity if not provided
        if severity is None:
            severity = self._determine_severity(event_type)

        # Determine compliance tags if not provided
        if compliance_tags is None:
            compliance_tags = self._determine_compliance_tags(event_type, resource_type)

        entry = AuditEntry(
            entry_id=f"audit-{uuid.uuid4().hex[:12]}",
            event_type=event_type,
            severity=severity,
            timestamp=datetime.utcnow(),
            actor_id=actor_id,
            actor_type=actor_type,
            actor_name=actor_name,
            action_id=action_id,
            resource_type=resource_type,
            resource_id=resource_id,
            description=description,
            details=details or {},
            previous_state=previous_state,
            new_state=new_state,
            ip_address=ip_address,
            user_agent=user_agent,
            session_id=session_id,
            correlation_id=correlation_id,
            compliance_tags=compliance_tags,
            previous_entry_hash=self._last_entry_hash,
        )

        # Sign the entry
        entry.signature = self._sign_entry(entry)

        # Compute entry hash for chain
        entry.entry_hash = self._compute_entry_hash(entry)
        self._last_entry_hash = entry.entry_hash

        # Store entry
        self._entries[entry.entry_id] = entry
        self._entry_sequence.append(entry.entry_id)

        # Index by action
        if action_id:
            if action_id not in self._entries_by_action:
                self._entries_by_action[action_id] = []
            self._entries_by_action[action_id].append(entry.entry_id)

        # Index by resource
        resource_key = f"{resource_type}:{resource_id}"
        if resource_key not in self._entries_by_resource:
            self._entries_by_resource[resource_key] = []
        self._entries_by_resource[resource_key].append(entry.entry_id)

        # Update chain of custody
        self._update_chain_of_custody(entry)

        return entry

    def _determine_severity(self, event_type: AuditEventType) -> AuditSeverity:
        """Determine severity based on event type."""
        severity_map = {
            AuditEventType.ACTION_CREATED: AuditSeverity.INFO,
            AuditEventType.ACTION_EXECUTED: AuditSeverity.LOW,
            AuditEventType.ACTION_COMPLETED: AuditSeverity.INFO,
            AuditEventType.ACTION_FAILED: AuditSeverity.MEDIUM,
            AuditEventType.ACTION_APPROVED: AuditSeverity.LOW,
            AuditEventType.ACTION_DENIED: AuditSeverity.MEDIUM,
            AuditEventType.ACTION_ESCALATED: AuditSeverity.MEDIUM,
            AuditEventType.ACTION_CANCELLED: AuditSeverity.LOW,
            AuditEventType.HUMAN_OVERRIDE: AuditSeverity.HIGH,
            AuditEventType.POLICY_ACTIVATED: AuditSeverity.MEDIUM,
            AuditEventType.POLICY_DEACTIVATED: AuditSeverity.MEDIUM,
            AuditEventType.POLICY_UPDATED: AuditSeverity.MEDIUM,
            AuditEventType.EMERGENCY_OVERRIDE_ACTIVATED: AuditSeverity.CRITICAL,
            AuditEventType.EMERGENCY_OVERRIDE_DEACTIVATED: AuditSeverity.HIGH,
            AuditEventType.ANOMALY_DETECTED: AuditSeverity.MEDIUM,
            AuditEventType.ANOMALY_RESOLVED: AuditSeverity.LOW,
            AuditEventType.STABILIZATION_ACTION: AuditSeverity.MEDIUM,
            AuditEventType.CASCADE_PREDICTION: AuditSeverity.HIGH,
            AuditEventType.CIRCUIT_BREAKER_TRIGGERED: AuditSeverity.CRITICAL,
            AuditEventType.CIRCUIT_BREAKER_RESET: AuditSeverity.HIGH,
            AuditEventType.SYSTEM_MODE_CHANGE: AuditSeverity.HIGH,
            AuditEventType.ACCESS_GRANTED: AuditSeverity.INFO,
            AuditEventType.ACCESS_DENIED: AuditSeverity.MEDIUM,
        }
        return severity_map.get(event_type, AuditSeverity.INFO)

    def _determine_compliance_tags(
        self,
        event_type: AuditEventType,
        resource_type: str,
    ) -> List[ComplianceStandard]:
        """Determine applicable compliance standards."""
        tags = [ComplianceStandard.NIST]  # NIST applies to all

        # CJIS for law enforcement related events
        cjis_resource_types = ["patrol", "crime", "investigation", "arrest", "officer"]
        cjis_event_types = [
            AuditEventType.ACTION_APPROVED, AuditEventType.ACTION_DENIED,
            AuditEventType.HUMAN_OVERRIDE, AuditEventType.ACCESS_GRANTED,
            AuditEventType.ACCESS_DENIED,
        ]
        if resource_type.lower() in cjis_resource_types or event_type in cjis_event_types:
            tags.append(ComplianceStandard.CJIS)

        # FL State for emergency and public safety
        fl_resource_types = ["emergency", "evacuation", "public_safety", "city_operations"]
        fl_event_types = [
            AuditEventType.EMERGENCY_OVERRIDE_ACTIVATED,
            AuditEventType.EMERGENCY_OVERRIDE_DEACTIVATED,
            AuditEventType.STABILIZATION_ACTION,
        ]
        if resource_type.lower() in fl_resource_types or event_type in fl_event_types:
            tags.append(ComplianceStandard.FL_STATE)

        # HIPAA for medical/EMS related
        if "ems" in resource_type.lower() or "medical" in resource_type.lower():
            tags.append(ComplianceStandard.HIPAA)

        return tags

    def _update_chain_of_custody(self, entry: AuditEntry):
        """Update chain of custody for a resource."""
        chain_key = f"{entry.resource_type}:{entry.resource_id}"

        if chain_key not in self._chains_of_custody:
            self._chains_of_custody[chain_key] = ChainOfCustody(
                chain_id=f"chain-{uuid.uuid4().hex[:8]}",
                resource_type=entry.resource_type,
                resource_id=entry.resource_id,
                entries=[],
                created_at=datetime.utcnow(),
                last_updated=datetime.utcnow(),
            )

        chain = self._chains_of_custody[chain_key]
        if not chain.is_sealed:
            chain.entries.append(entry)
            chain.last_updated = datetime.utcnow()

    def verify_entry_signature(self, entry_id: str) -> bool:
        """Verify the signature of an audit entry."""
        entry = self._entries.get(entry_id)
        if not entry:
            return False

        expected_signature = self._sign_entry(entry)
        return entry.signature == expected_signature

    def verify_chain_integrity(self) -> Tuple[bool, List[str]]:
        """Verify the integrity of the entire audit chain."""
        errors = []
        previous_hash = None

        for entry_id in self._entry_sequence:
            entry = self._entries.get(entry_id)
            if not entry:
                errors.append(f"Missing entry: {entry_id}")
                continue

            # Verify previous hash link
            if entry.previous_entry_hash != previous_hash:
                errors.append(f"Chain break at entry: {entry_id}")

            # Verify signature
            if not self.verify_entry_signature(entry_id):
                errors.append(f"Invalid signature at entry: {entry_id}")

            # Verify entry hash
            computed_hash = self._compute_entry_hash(entry)
            if entry.entry_hash != computed_hash:
                errors.append(f"Hash mismatch at entry: {entry_id}")

            previous_hash = entry.entry_hash

        return len(errors) == 0, errors

    def get_entry(self, entry_id: str) -> Optional[AuditEntry]:
        """Get an audit entry by ID."""
        return self._entries.get(entry_id)

    def get_entries_by_action(self, action_id: str) -> List[AuditEntry]:
        """Get all audit entries for an action."""
        entry_ids = self._entries_by_action.get(action_id, [])
        return [self._entries[eid] for eid in entry_ids if eid in self._entries]

    def get_entries_by_resource(
        self,
        resource_type: str,
        resource_id: str,
    ) -> List[AuditEntry]:
        """Get all audit entries for a resource."""
        resource_key = f"{resource_type}:{resource_id}"
        entry_ids = self._entries_by_resource.get(resource_key, [])
        return [self._entries[eid] for eid in entry_ids if eid in self._entries]

    def get_chain_of_custody(
        self,
        resource_type: str,
        resource_id: str,
    ) -> Optional[ChainOfCustody]:
        """Get chain of custody for a resource."""
        chain_key = f"{resource_type}:{resource_id}"
        return self._chains_of_custody.get(chain_key)

    def seal_chain_of_custody(
        self,
        resource_type: str,
        resource_id: str,
    ) -> bool:
        """Seal a chain of custody to prevent further modifications."""
        chain_key = f"{resource_type}:{resource_id}"
        chain = self._chains_of_custody.get(chain_key)
        if not chain:
            return False

        # Compute seal signature
        chain_data = json.dumps(chain.to_dict(), sort_keys=True, default=str)
        chain.seal_signature = self._compute_hash(f"{chain_data}:{self._signing_key}")
        chain.is_sealed = True
        return True

    def query_entries(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        event_types: Optional[List[AuditEventType]] = None,
        actor_id: Optional[str] = None,
        actor_type: Optional[str] = None,
        resource_type: Optional[str] = None,
        severity: Optional[AuditSeverity] = None,
        compliance_standard: Optional[ComplianceStandard] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[AuditEntry]:
        """Query audit entries with filters."""
        entries = list(self._entries.values())

        if start_date:
            entries = [e for e in entries if e.timestamp >= start_date]
        if end_date:
            entries = [e for e in entries if e.timestamp <= end_date]
        if event_types:
            entries = [e for e in entries if e.event_type in event_types]
        if actor_id:
            entries = [e for e in entries if e.actor_id == actor_id]
        if actor_type:
            entries = [e for e in entries if e.actor_type == actor_type]
        if resource_type:
            entries = [e for e in entries if e.resource_type == resource_type]
        if severity:
            entries = [e for e in entries if e.severity == severity]
        if compliance_standard:
            entries = [e for e in entries if compliance_standard in e.compliance_tags]

        # Sort by timestamp descending
        entries.sort(key=lambda e: e.timestamp, reverse=True)

        return entries[offset:offset + limit]

    def generate_autonomy_summary(
        self,
        period: ReportPeriod,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> AutonomySummary:
        """Generate autonomy summary for a time period."""
        now = datetime.utcnow()

        if start_date is None or end_date is None:
            if period == ReportPeriod.DAILY_24H:
                start_date = now - timedelta(hours=24)
                end_date = now
            elif period == ReportPeriod.WEEKLY_7D:
                start_date = now - timedelta(days=7)
                end_date = now
            elif period == ReportPeriod.MONTHLY_30D:
                start_date = now - timedelta(days=30)
                end_date = now
            else:
                start_date = now - timedelta(hours=24)
                end_date = now

        entries = self.query_entries(
            start_date=start_date,
            end_date=end_date,
            limit=10000,
        )

        # Calculate statistics
        action_entries = [e for e in entries if e.event_type in [
            AuditEventType.ACTION_CREATED, AuditEventType.ACTION_EXECUTED,
            AuditEventType.ACTION_COMPLETED, AuditEventType.ACTION_FAILED,
        ]]

        actions_by_level = {"level_0": 0, "level_1": 0, "level_2": 0}
        actions_by_status = {
            "created": 0, "executed": 0, "completed": 0, "failed": 0,
            "approved": 0, "denied": 0, "escalated": 0,
        }
        actions_by_category = {}

        for entry in entries:
            level = entry.details.get("level", "unknown")
            if level in actions_by_level:
                actions_by_level[level] += 1

            category = entry.details.get("category", "unknown")
            actions_by_category[category] = actions_by_category.get(category, 0) + 1

            if entry.event_type == AuditEventType.ACTION_CREATED:
                actions_by_status["created"] += 1
            elif entry.event_type == AuditEventType.ACTION_EXECUTED:
                actions_by_status["executed"] += 1
            elif entry.event_type == AuditEventType.ACTION_COMPLETED:
                actions_by_status["completed"] += 1
            elif entry.event_type == AuditEventType.ACTION_FAILED:
                actions_by_status["failed"] += 1
            elif entry.event_type == AuditEventType.ACTION_APPROVED:
                actions_by_status["approved"] += 1
            elif entry.event_type == AuditEventType.ACTION_DENIED:
                actions_by_status["denied"] += 1
            elif entry.event_type == AuditEventType.ACTION_ESCALATED:
                actions_by_status["escalated"] += 1

        human_overrides = len([e for e in entries if e.event_type == AuditEventType.HUMAN_OVERRIDE])
        denied_actions = len([e for e in entries if e.event_type == AuditEventType.ACTION_DENIED])
        escalations = len([e for e in entries if e.event_type == AuditEventType.ACTION_ESCALATED])
        anomalies = len([e for e in entries if e.event_type == AuditEventType.ANOMALY_DETECTED])
        stabilization = len([e for e in entries if e.event_type == AuditEventType.STABILIZATION_ACTION])
        circuit_breakers = len([e for e in entries if e.event_type == AuditEventType.CIRCUIT_BREAKER_TRIGGERED])

        # Calculate AI vs Human ratio
        ai_actions = len([e for e in entries if e.actor_type in ["system", "ai_engine"]])
        human_actions = len([e for e in entries if e.actor_type == "human"])
        ai_vs_human = ai_actions / max(human_actions, 1)

        summary = AutonomySummary(
            summary_id=f"summary-{uuid.uuid4().hex[:8]}",
            period=period,
            start_date=start_date,
            end_date=end_date,
            total_actions=len(action_entries),
            actions_by_level=actions_by_level,
            actions_by_status=actions_by_status,
            actions_by_category=actions_by_category,
            human_overrides=human_overrides,
            denied_actions=denied_actions,
            escalations=escalations,
            avg_approval_time_minutes=5.2,  # Would calculate from actual data
            avg_execution_time_ms=150.0,  # Would calculate from actual data
            anomalies_detected=anomalies,
            stabilization_actions=stabilization,
            circuit_breaker_triggers=circuit_breakers,
            ai_vs_human_ratio=ai_vs_human,
        )

        self._summaries[summary.summary_id] = summary
        return summary

    def generate_compliance_report(
        self,
        compliance_standard: ComplianceStandard,
        period: ReportPeriod,
        generated_by: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> ComplianceReport:
        """Generate a compliance report."""
        now = datetime.utcnow()

        if start_date is None or end_date is None:
            if period == ReportPeriod.DAILY_24H:
                start_date = now - timedelta(hours=24)
                end_date = now
            elif period == ReportPeriod.WEEKLY_7D:
                start_date = now - timedelta(days=7)
                end_date = now
            elif period == ReportPeriod.MONTHLY_30D:
                start_date = now - timedelta(days=30)
                end_date = now
            else:
                start_date = now - timedelta(hours=24)
                end_date = now

        entries = self.query_entries(
            start_date=start_date,
            end_date=end_date,
            compliance_standard=compliance_standard,
            limit=10000,
        )

        # Generate findings based on compliance standard
        findings = []
        recommendations = []

        if compliance_standard == ComplianceStandard.CJIS:
            findings = self._generate_cjis_findings(entries)
            recommendations = [
                "Ensure all access to criminal justice information is logged",
                "Verify multi-factor authentication for all users",
                "Review and update access control policies quarterly",
                "Conduct security awareness training for all personnel",
            ]
        elif compliance_standard == ComplianceStandard.NIST:
            findings = self._generate_nist_findings(entries)
            recommendations = [
                "Implement continuous monitoring of security controls",
                "Maintain incident response procedures",
                "Conduct regular vulnerability assessments",
                "Update system security plans annually",
            ]
        elif compliance_standard == ComplianceStandard.FL_STATE:
            findings = self._generate_fl_state_findings(entries)
            recommendations = [
                "Ensure public records retention compliance",
                "Maintain emergency response documentation",
                "Review interagency data sharing agreements",
                "Update disaster recovery procedures",
            ]

        # Generate summary
        summary = {
            "total_events": len(entries),
            "events_by_severity": {
                sev.value: len([e for e in entries if e.severity == sev])
                for sev in AuditSeverity
            },
            "events_by_type": {},
            "chain_integrity": self.verify_chain_integrity()[0],
            "compliance_score": self._calculate_compliance_score(entries, compliance_standard),
        }

        for entry in entries:
            event_type = entry.event_type.value
            summary["events_by_type"][event_type] = summary["events_by_type"].get(event_type, 0) + 1

        report = ComplianceReport(
            report_id=f"report-{uuid.uuid4().hex[:8]}",
            report_type=f"{compliance_standard.value}_compliance",
            period=period,
            start_date=start_date,
            end_date=end_date,
            compliance_standard=compliance_standard,
            generated_at=now,
            generated_by=generated_by,
            summary=summary,
            findings=findings,
            recommendations=recommendations,
        )

        # Sign the report
        report_data = json.dumps(report.to_dict(), sort_keys=True, default=str)
        report.signature = self._compute_hash(f"{report_data}:{self._signing_key}")

        self._compliance_reports[report.report_id] = report
        return report

    def _generate_cjis_findings(self, entries: List[AuditEntry]) -> List[Dict[str, Any]]:
        """Generate CJIS-specific findings."""
        findings = []

        # Check for access denials
        access_denials = [e for e in entries if e.event_type == AuditEventType.ACCESS_DENIED]
        if access_denials:
            findings.append({
                "finding_id": f"finding-{uuid.uuid4().hex[:6]}",
                "category": "access_control",
                "severity": "medium",
                "description": f"{len(access_denials)} access denial events detected",
                "recommendation": "Review access denial patterns for potential security issues",
            })

        # Check for human overrides
        overrides = [e for e in entries if e.event_type == AuditEventType.HUMAN_OVERRIDE]
        if overrides:
            findings.append({
                "finding_id": f"finding-{uuid.uuid4().hex[:6]}",
                "category": "audit_trail",
                "severity": "info",
                "description": f"{len(overrides)} human override events recorded",
                "recommendation": "Ensure all overrides are properly documented and justified",
            })

        return findings

    def _generate_nist_findings(self, entries: List[AuditEntry]) -> List[Dict[str, Any]]:
        """Generate NIST-specific findings."""
        findings = []

        # Check for system failures
        failures = [e for e in entries if e.event_type == AuditEventType.ACTION_FAILED]
        if failures:
            findings.append({
                "finding_id": f"finding-{uuid.uuid4().hex[:6]}",
                "category": "system_reliability",
                "severity": "medium",
                "description": f"{len(failures)} action failures detected",
                "recommendation": "Investigate root causes of failures and implement corrective actions",
            })

        # Check for circuit breaker triggers
        circuit_breakers = [e for e in entries if e.event_type == AuditEventType.CIRCUIT_BREAKER_TRIGGERED]
        if circuit_breakers:
            findings.append({
                "finding_id": f"finding-{uuid.uuid4().hex[:6]}",
                "category": "system_availability",
                "severity": "high",
                "description": f"{len(circuit_breakers)} circuit breaker triggers detected",
                "recommendation": "Review system stability and implement preventive measures",
            })

        return findings

    def _generate_fl_state_findings(self, entries: List[AuditEntry]) -> List[Dict[str, Any]]:
        """Generate Florida State-specific findings."""
        findings = []

        # Check for emergency overrides
        emergency_overrides = [e for e in entries if e.event_type == AuditEventType.EMERGENCY_OVERRIDE_ACTIVATED]
        if emergency_overrides:
            findings.append({
                "finding_id": f"finding-{uuid.uuid4().hex[:6]}",
                "category": "emergency_management",
                "severity": "info",
                "description": f"{len(emergency_overrides)} emergency override activations",
                "recommendation": "Ensure all emergency activations are documented per FL Statute 252",
            })

        # Check for stabilization actions
        stabilization = [e for e in entries if e.event_type == AuditEventType.STABILIZATION_ACTION]
        if stabilization:
            findings.append({
                "finding_id": f"finding-{uuid.uuid4().hex[:6]}",
                "category": "public_safety",
                "severity": "info",
                "description": f"{len(stabilization)} stabilization actions taken",
                "recommendation": "Maintain records per public records retention requirements",
            })

        return findings

    def _calculate_compliance_score(
        self,
        entries: List[AuditEntry],
        standard: ComplianceStandard,
    ) -> float:
        """Calculate compliance score (0-100)."""
        if not entries:
            return 100.0

        score = 100.0

        # Deduct for critical events
        critical_events = len([e for e in entries if e.severity == AuditSeverity.CRITICAL])
        score -= critical_events * 5

        # Deduct for high severity events
        high_events = len([e for e in entries if e.severity == AuditSeverity.HIGH])
        score -= high_events * 2

        # Deduct for failed actions
        failed = len([e for e in entries if e.event_type == AuditEventType.ACTION_FAILED])
        score -= failed * 1

        # Verify chain integrity
        is_valid, errors = self.verify_chain_integrity()
        if not is_valid:
            score -= len(errors) * 10

        return max(0.0, min(100.0, score))

    def generate_incident_report(
        self,
        action_id: str,
        generated_by: str,
    ) -> Dict[str, Any]:
        """Generate an incident-level action report."""
        entries = self.get_entries_by_action(action_id)
        if not entries:
            return {"error": "No entries found for action"}

        entries.sort(key=lambda e: e.timestamp)

        report = {
            "report_id": f"incident-{uuid.uuid4().hex[:8]}",
            "action_id": action_id,
            "generated_at": datetime.utcnow().isoformat(),
            "generated_by": generated_by,
            "timeline": [
                {
                    "timestamp": e.timestamp.isoformat(),
                    "event_type": e.event_type.value,
                    "actor": e.actor_name,
                    "description": e.description,
                }
                for e in entries
            ],
            "actors_involved": list(set(e.actor_name for e in entries)),
            "total_events": len(entries),
            "duration_minutes": (entries[-1].timestamp - entries[0].timestamp).total_seconds() / 60 if len(entries) > 1 else 0,
            "final_status": entries[-1].event_type.value,
            "compliance_tags": list(set(
                tag.value for e in entries for tag in e.compliance_tags
            )),
        }

        # Sign the report
        report_data = json.dumps(report, sort_keys=True, default=str)
        report["signature"] = self._compute_hash(f"{report_data}:{self._signing_key}")

        return report

    def export_to_pdf_data(
        self,
        report_type: str,
        report_id: str,
    ) -> Dict[str, Any]:
        """Export report data for PDF generation."""
        if report_type == "compliance":
            report = self._compliance_reports.get(report_id)
            if report:
                return {
                    "type": "compliance_report",
                    "data": report.to_dict(),
                    "format": "pdf",
                    "template": "compliance_report_template",
                }
        elif report_type == "summary":
            summary = self._summaries.get(report_id)
            if summary:
                return {
                    "type": "autonomy_summary",
                    "data": summary.to_dict(),
                    "format": "pdf",
                    "template": "autonomy_summary_template",
                }

        return {"error": "Report not found"}

    def get_statistics(self) -> Dict[str, Any]:
        """Get audit engine statistics."""
        entries = list(self._entries.values())
        is_valid, errors = self.verify_chain_integrity()

        return {
            "total_entries": len(entries),
            "entries_by_type": {
                et.value: len([e for e in entries if e.event_type == et])
                for et in AuditEventType
            },
            "entries_by_severity": {
                sev.value: len([e for e in entries if e.severity == sev])
                for sev in AuditSeverity
            },
            "entries_by_actor_type": {
                "system": len([e for e in entries if e.actor_type == "system"]),
                "human": len([e for e in entries if e.actor_type == "human"]),
                "ai_engine": len([e for e in entries if e.actor_type == "ai_engine"]),
            },
            "chains_of_custody": len(self._chains_of_custody),
            "sealed_chains": len([c for c in self._chains_of_custody.values() if c.is_sealed]),
            "compliance_reports_generated": len(self._compliance_reports),
            "summaries_generated": len(self._summaries),
            "chain_integrity_valid": is_valid,
            "chain_integrity_errors": len(errors),
        }


_audit_engine: Optional[ActionAuditEngine] = None


def get_audit_engine() -> ActionAuditEngine:
    """Get the singleton ActionAuditEngine instance."""
    global _audit_engine
    if _audit_engine is None:
        _audit_engine = ActionAuditEngine()
    return _audit_engine
