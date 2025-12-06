"""
AI Engine Data Models.

This module contains all data classes and models used by the AI Intelligence Engine
for representing results, entities, patterns, anomalies, and predictions.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class EntityType(str, Enum):
    """Types of entities in the system."""

    PERSON = "person"
    VEHICLE = "vehicle"
    INCIDENT = "incident"
    ADDRESS = "address"
    WEAPON = "weapon"
    PHONE = "phone"
    ORGANIZATION = "organization"


class AnomalyType(str, Enum):
    """Types of anomalies detected by the system."""

    VEHICLE_BEHAVIOR = "vehicle_behavior"
    GUNFIRE_DENSITY = "gunfire_density"
    OFFENDER_CLUSTERING = "offender_clustering"
    TIMELINE_DEVIATION = "timeline_deviation"
    CRIME_SIGNATURE_SHIFT = "crime_signature_shift"
    REPEAT_CALLER = "repeat_caller"
    LOCATION_HOTSPOT = "location_hotspot"


class PatternType(str, Enum):
    """Types of patterns recognized by the system."""

    REPEAT_OFFENDER = "repeat_offender"
    VEHICLE_TRAJECTORY = "vehicle_trajectory"
    CRIME_HEAT = "crime_heat"
    GUNFIRE_RECURRENCE = "gunfire_recurrence"
    TEMPORAL_PATTERN = "temporal_pattern"
    GEOGRAPHIC_CLUSTER = "geographic_cluster"


class RiskLevel(str, Enum):
    """Risk level classifications."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    MINIMAL = "minimal"


class ConfidenceLevel(str, Enum):
    """Confidence level for AI predictions."""

    VERY_HIGH = "very_high"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNCERTAIN = "uncertain"


@dataclass
class GeoLocation:
    """Geographic location with coordinates."""

    latitude: float
    longitude: float
    address: str | None = None
    city: str | None = None
    state: str | None = None
    zip_code: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "address": self.address,
            "city": self.city,
            "state": self.state,
            "zip_code": self.zip_code,
        }


@dataclass
class TimeRange:
    """Time range for queries and analysis."""

    start: datetime
    end: datetime

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "start": self.start.isoformat(),
            "end": self.end.isoformat(),
        }


@dataclass
class EntityMatch:
    """Represents a matched or resolved entity."""

    entity_id: str
    entity_type: EntityType
    confidence: float
    source_ids: list[str] = field(default_factory=list)
    properties: dict[str, Any] = field(default_factory=dict)
    aliases: list[str] = field(default_factory=list)
    merge_candidates: list[str] = field(default_factory=list)
    matched_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "entity_id": self.entity_id,
            "entity_type": self.entity_type.value,
            "confidence": self.confidence,
            "source_ids": self.source_ids,
            "properties": self.properties,
            "aliases": self.aliases,
            "merge_candidates": self.merge_candidates,
            "matched_at": self.matched_at.isoformat(),
        }


@dataclass
class Relationship:
    """Represents a relationship between entities."""

    source_id: str
    target_id: str
    relationship_type: str
    confidence: float
    properties: dict[str, Any] = field(default_factory=dict)
    discovered_at: datetime = field(default_factory=datetime.utcnow)
    evidence: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "source_id": self.source_id,
            "target_id": self.target_id,
            "relationship_type": self.relationship_type,
            "confidence": self.confidence,
            "properties": self.properties,
            "discovered_at": self.discovered_at.isoformat(),
            "evidence": self.evidence,
        }


@dataclass
class RiskScore:
    """Risk score for an entity."""

    entity_id: str
    entity_type: EntityType
    score: float
    level: RiskLevel
    factors: dict[str, float] = field(default_factory=dict)
    last_scored_at: datetime = field(default_factory=datetime.utcnow)
    trend: str = "stable"
    historical_scores: list[float] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "entity_id": self.entity_id,
            "entity_type": self.entity_type.value,
            "score": self.score,
            "level": self.level.value,
            "factors": self.factors,
            "last_scored_at": self.last_scored_at.isoformat(),
            "trend": self.trend,
            "historical_scores": self.historical_scores,
        }


@dataclass
class AnomalyResult:
    """Result from anomaly detection."""

    anomaly_id: str
    anomaly_type: AnomalyType
    severity: float
    description: str
    detected_at: datetime = field(default_factory=datetime.utcnow)
    location: GeoLocation | None = None
    related_entities: list[str] = field(default_factory=list)
    metrics: dict[str, float] = field(default_factory=dict)
    baseline: dict[str, float] = field(default_factory=dict)
    deviation: float = 0.0
    confidence: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "anomaly_id": self.anomaly_id,
            "anomaly_type": self.anomaly_type.value,
            "severity": self.severity,
            "description": self.description,
            "detected_at": self.detected_at.isoformat(),
            "location": self.location.to_dict() if self.location else None,
            "related_entities": self.related_entities,
            "metrics": self.metrics,
            "baseline": self.baseline,
            "deviation": self.deviation,
            "confidence": self.confidence,
        }


@dataclass
class PatternResult:
    """Result from pattern recognition."""

    pattern_id: str
    pattern_type: PatternType
    description: str
    confidence: float
    discovered_at: datetime = field(default_factory=datetime.utcnow)
    entities: list[str] = field(default_factory=list)
    locations: list[GeoLocation] = field(default_factory=list)
    time_range: TimeRange | None = None
    frequency: float = 0.0
    strength: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "pattern_id": self.pattern_id,
            "pattern_type": self.pattern_type.value,
            "description": self.description,
            "confidence": self.confidence,
            "discovered_at": self.discovered_at.isoformat(),
            "entities": self.entities,
            "locations": [loc.to_dict() for loc in self.locations],
            "time_range": self.time_range.to_dict() if self.time_range else None,
            "frequency": self.frequency,
            "strength": self.strength,
            "metadata": self.metadata,
        }


@dataclass
class PredictionResult:
    """Result from predictive models."""

    prediction_id: str
    prediction_type: str
    description: str
    confidence: ConfidenceLevel
    probability: float
    predicted_at: datetime = field(default_factory=datetime.utcnow)
    target_entity: str | None = None
    predicted_location: GeoLocation | None = None
    predicted_time: datetime | None = None
    factors: dict[str, float] = field(default_factory=dict)
    recommendations: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "prediction_id": self.prediction_id,
            "prediction_type": self.prediction_type,
            "description": self.description,
            "confidence": self.confidence.value,
            "probability": self.probability,
            "predicted_at": self.predicted_at.isoformat(),
            "target_entity": self.target_entity,
            "predicted_location": (
                self.predicted_location.to_dict() if self.predicted_location else None
            ),
            "predicted_time": (self.predicted_time.isoformat() if self.predicted_time else None),
            "factors": self.factors,
            "recommendations": self.recommendations,
        }


@dataclass
class AIQueryResult:
    """Complete result from an AI query."""

    query_id: str
    original_query: str
    summary: str
    entities: list[EntityMatch] = field(default_factory=list)
    incidents: list[dict[str, Any]] = field(default_factory=list)
    relationships: list[Relationship] = field(default_factory=list)
    risk_scores: dict[str, RiskScore] = field(default_factory=dict)
    anomalies: list[AnomalyResult] = field(default_factory=list)
    patterns: list[PatternResult] = field(default_factory=list)
    predictions: list[PredictionResult] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    processed_at: datetime = field(default_factory=datetime.utcnow)
    processing_time_ms: float = 0.0
    confidence: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "query_id": self.query_id,
            "original_query": self.original_query,
            "summary": self.summary,
            "entities": [e.to_dict() for e in self.entities],
            "incidents": self.incidents,
            "relationships": [r.to_dict() for r in self.relationships],
            "risk_scores": {k: v.to_dict() for k, v in self.risk_scores.items()},
            "anomalies": [a.to_dict() for a in self.anomalies],
            "patterns": [p.to_dict() for p in self.patterns],
            "predictions": [p.to_dict() for p in self.predictions],
            "recommendations": self.recommendations,
            "processed_at": self.processed_at.isoformat(),
            "processing_time_ms": self.processing_time_ms,
            "confidence": self.confidence,
        }


@dataclass
class DSLQuery:
    """Structured DSL query parsed from natural language."""

    query_type: str
    entities: list[dict[str, Any]] = field(default_factory=list)
    filters: dict[str, Any] = field(default_factory=dict)
    time_range: TimeRange | None = None
    location: GeoLocation | None = None
    radius_meters: float | None = None
    limit: int = 100
    include_relationships: bool = True
    include_risk_scores: bool = True

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "query_type": self.query_type,
            "entities": self.entities,
            "filters": self.filters,
            "time_range": self.time_range.to_dict() if self.time_range else None,
            "location": self.location.to_dict() if self.location else None,
            "radius_meters": self.radius_meters,
            "limit": self.limit,
            "include_relationships": self.include_relationships,
            "include_risk_scores": self.include_risk_scores,
        }


@dataclass
class AIInsightEvent:
    """Real-time AI insight event for WebSocket streaming."""

    event_id: str
    event_type: str
    title: str
    description: str
    severity: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    entity_ids: list[str] = field(default_factory=list)
    location: GeoLocation | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "title": self.title,
            "description": self.description,
            "severity": self.severity,
            "timestamp": self.timestamp.isoformat(),
            "entity_ids": self.entity_ids,
            "location": self.location.to_dict() if self.location else None,
            "metadata": self.metadata,
        }


__all__ = [
    "EntityType",
    "AnomalyType",
    "PatternType",
    "RiskLevel",
    "ConfidenceLevel",
    "GeoLocation",
    "TimeRange",
    "EntityMatch",
    "Relationship",
    "RiskScore",
    "AnomalyResult",
    "PatternResult",
    "PredictionResult",
    "AIQueryResult",
    "DSLQuery",
    "AIInsightEvent",
]
