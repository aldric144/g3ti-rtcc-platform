"""
Investigations Engine Models.

This module defines the data models used throughout the Investigations Engine,
including case files, evidence objects, timeline events, and entity summaries.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class CaseStatus(str, Enum):
    """Status of an investigation case."""

    OPEN = "open"
    ACTIVE = "active"
    PENDING = "pending"
    CLOSED = "closed"
    ARCHIVED = "archived"


class CasePriority(str, Enum):
    """Priority level of an investigation case."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class EvidenceType(str, Enum):
    """Type of evidence collected."""

    RMS_REPORT = "rms_report"
    CAD_RECORD = "cad_record"
    SHOTSPOTTER_AUDIO = "shotspotter_audio"
    LPR_HIT = "lpr_hit"
    BWC_FOOTAGE = "bwc_footage"
    NESS_BALLISTICS = "ness_ballistics"
    CAMERA_SNAPSHOT = "camera_snapshot"
    WITNESS_STATEMENT = "witness_statement"
    DOCUMENT = "document"
    OTHER = "other"


class TimelineEventType(str, Enum):
    """Type of timeline event."""

    CAD_DISPATCH = "cad_dispatch"
    CAD_UPDATE = "cad_update"
    RMS_REPORT = "rms_report"
    LPR_DETECTION = "lpr_detection"
    GUNFIRE_ALERT = "gunfire_alert"
    BWC_ACTIVATION = "bwc_activation"
    ENTITY_INTERACTION = "entity_interaction"
    VEHICLE_MOVEMENT = "vehicle_movement"
    ARREST = "arrest"
    BOOKING = "booking"
    COURT_EVENT = "court_event"
    OTHER = "other"


class LinkageType(str, Enum):
    """Type of incident linkage."""

    TEMPORAL = "temporal"
    GEOGRAPHIC = "geographic"
    ENTITY_OVERLAP = "entity_overlap"
    NARRATIVE_SIMILARITY = "narrative_similarity"
    BALLISTIC_MATCH = "ballistic_match"
    VEHICLE_RECURRENCE = "vehicle_recurrence"
    MO_SIMILARITY = "mo_similarity"
    SUSPECT_DESCRIPTION = "suspect_description"
    WEAPON_TYPE = "weapon_type"
    REPEAT_CALLER = "repeat_caller"


class ConfidenceLevel(str, Enum):
    """Confidence level for connections and matches."""

    VERY_HIGH = "very_high"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    VERY_LOW = "very_low"


@dataclass
class EvidenceItem:
    """Represents a single piece of evidence."""

    evidence_id: str
    evidence_type: EvidenceType
    source: str
    title: str
    description: str
    collected_at: datetime
    metadata: dict[str, Any] = field(default_factory=dict)
    attachments: list[str] = field(default_factory=list)
    confidence: float = 1.0
    is_verified: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "evidence_id": self.evidence_id,
            "evidence_type": self.evidence_type.value,
            "source": self.source,
            "title": self.title,
            "description": self.description,
            "collected_at": self.collected_at.isoformat(),
            "metadata": self.metadata,
            "attachments": self.attachments,
            "confidence": self.confidence,
            "is_verified": self.is_verified,
        }


@dataclass
class EvidencePackage:
    """Collection of all evidence for a case."""

    reports: list[EvidenceItem] = field(default_factory=list)
    audio_metadata: list[EvidenceItem] = field(default_factory=list)
    ballistics: list[EvidenceItem] = field(default_factory=list)
    lpr_trail: list[EvidenceItem] = field(default_factory=list)
    bwc_interactions: list[EvidenceItem] = field(default_factory=list)
    camera_positions: list[EvidenceItem] = field(default_factory=list)
    attachments: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "reports": [e.to_dict() for e in self.reports],
            "audio_metadata": [e.to_dict() for e in self.audio_metadata],
            "ballistics": [e.to_dict() for e in self.ballistics],
            "lpr_trail": [e.to_dict() for e in self.lpr_trail],
            "bwc_interactions": [e.to_dict() for e in self.bwc_interactions],
            "camera_positions": [e.to_dict() for e in self.camera_positions],
            "attachments": self.attachments,
        }

    @property
    def total_items(self) -> int:
        """Get total number of evidence items."""
        return (
            len(self.reports)
            + len(self.audio_metadata)
            + len(self.ballistics)
            + len(self.lpr_trail)
            + len(self.bwc_interactions)
            + len(self.camera_positions)
        )


@dataclass
class TimelineEvent:
    """Represents a single event in a case timeline."""

    event_id: str
    timestamp: datetime
    event_type: TimelineEventType
    description: str
    source: str
    location: dict[str, Any] | None = None
    entities_involved: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    reliability_score: float = 1.0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "event_id": self.event_id,
            "timestamp": self.timestamp.isoformat(),
            "event_type": self.event_type.value,
            "description": self.description,
            "source": self.source,
            "location": self.location,
            "entities_involved": self.entities_involved,
            "metadata": self.metadata,
            "reliability_score": self.reliability_score,
        }


@dataclass
class IncidentLinkage:
    """Represents a link between two incidents."""

    source_incident_id: str
    target_incident_id: str
    linkage_type: LinkageType
    confidence: float
    explanation: str
    supporting_evidence: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "source_incident_id": self.source_incident_id,
            "target_incident_id": self.target_incident_id,
            "linkage_type": self.linkage_type.value,
            "confidence": self.confidence,
            "explanation": self.explanation,
            "supporting_evidence": self.supporting_evidence,
            "metadata": self.metadata,
        }


@dataclass
class EntitySummary:
    """Summary of an entity's investigative profile."""

    entity_id: str
    entity_type: str
    name: str
    prior_incidents: list[dict[str, Any]] = field(default_factory=list)
    address_history: list[dict[str, Any]] = field(default_factory=list)
    vehicle_connections: list[dict[str, Any]] = field(default_factory=list)
    weapon_matches: list[dict[str, Any]] = field(default_factory=list)
    lpr_activity: list[dict[str, Any]] = field(default_factory=list)
    bwc_interactions: list[dict[str, Any]] = field(default_factory=list)
    known_associates: list[dict[str, Any]] = field(default_factory=list)
    risk_score: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "entity_id": self.entity_id,
            "entity_type": self.entity_type,
            "name": self.name,
            "prior_incidents": self.prior_incidents,
            "address_history": self.address_history,
            "vehicle_connections": self.vehicle_connections,
            "weapon_matches": self.weapon_matches,
            "lpr_activity": self.lpr_activity,
            "bwc_interactions": self.bwc_interactions,
            "known_associates": self.known_associates,
            "risk_score": self.risk_score,
            "metadata": self.metadata,
        }


@dataclass
class RiskAssessment:
    """Risk assessment for a case or entity."""

    overall_score: float
    threat_level: str
    factors: list[dict[str, Any]] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    last_updated: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "overall_score": self.overall_score,
            "threat_level": self.threat_level,
            "factors": self.factors,
            "recommendations": self.recommendations,
            "last_updated": self.last_updated.isoformat(),
        }


@dataclass
class InvestigativeLead:
    """An investigative lead or recommendation."""

    lead_id: str
    title: str
    description: str
    priority: CasePriority
    source: str
    confidence: float
    action_items: list[str] = field(default_factory=list)
    related_entities: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "lead_id": self.lead_id,
            "title": self.title,
            "description": self.description,
            "priority": self.priority.value,
            "source": self.source,
            "confidence": self.confidence,
            "action_items": self.action_items,
            "related_entities": self.related_entities,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class CaseFile:
    """Complete investigation case file."""

    case_id: str
    case_number: str
    title: str
    summary: str
    status: CaseStatus
    priority: CasePriority
    created_at: datetime
    updated_at: datetime
    assigned_to: list[str] = field(default_factory=list)
    linked_incidents: list[dict[str, Any]] = field(default_factory=list)
    suspects: list[EntitySummary] = field(default_factory=list)
    vehicles: list[EntitySummary] = field(default_factory=list)
    addresses: list[dict[str, Any]] = field(default_factory=list)
    weapons: list[dict[str, Any]] = field(default_factory=list)
    timeline: list[TimelineEvent] = field(default_factory=list)
    evidence: EvidencePackage = field(default_factory=EvidencePackage)
    risk_assessment: RiskAssessment | None = None
    leads: list[InvestigativeLead] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    notes: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "case_id": self.case_id,
            "case_number": self.case_number,
            "title": self.title,
            "summary": self.summary,
            "status": self.status.value,
            "priority": self.priority.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "assigned_to": self.assigned_to,
            "linked_incidents": self.linked_incidents,
            "suspects": [s.to_dict() for s in self.suspects],
            "vehicles": [v.to_dict() for v in self.vehicles],
            "addresses": self.addresses,
            "weapons": self.weapons,
            "timeline": [t.to_dict() for t in self.timeline],
            "evidence": self.evidence.to_dict(),
            "risk_assessment": self.risk_assessment.to_dict() if self.risk_assessment else None,
            "leads": [lead.to_dict() for lead in self.leads],
            "recommendations": self.recommendations,
            "notes": self.notes,
            "metadata": self.metadata,
        }


@dataclass
class LinkageResult:
    """Result of incident linking operation."""

    linked_incidents: list[dict[str, Any]]
    linkages: list[IncidentLinkage]
    confidence_scores: dict[str, float]
    explanations: list[str]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "linked_incidents": self.linked_incidents,
            "linkages": [link.to_dict() for link in self.linkages],
            "confidence_scores": self.confidence_scores,
            "explanations": self.explanations,
        }


__all__ = [
    "CaseStatus",
    "CasePriority",
    "EvidenceType",
    "TimelineEventType",
    "LinkageType",
    "ConfidenceLevel",
    "EvidenceItem",
    "EvidencePackage",
    "TimelineEvent",
    "IncidentLinkage",
    "EntitySummary",
    "RiskAssessment",
    "InvestigativeLead",
    "CaseFile",
    "LinkageResult",
]
