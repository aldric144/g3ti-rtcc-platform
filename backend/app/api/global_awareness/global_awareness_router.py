"""
Phase 32: Global Awareness API Router

REST API endpoints for global situation awareness operations.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from backend.app.global_awareness.global_sensor_layer import (
    GlobalSensorLayer,
    SensorDomain,
    SeverityLevel,
    DataSource,
)
from backend.app.global_awareness.knowledge_graph_engine import (
    KnowledgeGraphEngine,
    EntityType,
    RelationshipType,
    InfluenceCategory,
)
from backend.app.global_awareness.risk_fusion_engine import (
    RiskFusionEngine,
    RiskDomain,
    RiskLevel,
)
from backend.app.global_awareness.event_correlation_engine import (
    EventCorrelationEngine,
    EventCategory,
    ImpactMagnitude,
)
from backend.app.global_awareness.satellite_analysis_layer import (
    SatelliteAnalysisLayer,
    ImagerySource,
    ChangeCategory,
)

router = APIRouter(prefix="/api/global-awareness", tags=["Global Awareness"])


class CrisisFeedRequest(BaseModel):
    event_type: str = Field(..., description="Type of crisis event")
    severity: int = Field(3, ge=1, le=5, description="Severity level 1-5")
    lat: float = Field(..., description="Latitude")
    lon: float = Field(..., description="Longitude")
    country: str = Field(..., description="Country name")
    region: str = Field(..., description="Region name")
    affected_population: int = Field(0, ge=0)
    casualties: int = Field(0, ge=0)
    displaced: int = Field(0, ge=0)
    description: str = Field("", description="Event description")
    source: str = Field("gdacs", description="Data source")


class ConflictIndicatorRequest(BaseModel):
    title: str = Field(..., description="Indicator title")
    description: str = Field("", description="Description")
    severity: int = Field(3, ge=1, le=5)
    lat: float = Field(0.0)
    lon: float = Field(0.0)
    country: str = Field("Unknown")
    region: str = Field("Unknown")
    source: str = Field("acled")
    confidence: float = Field(0.7, ge=0, le=1)
    tags: list[str] = Field(default_factory=list)
    entities: list[str] = Field(default_factory=list)


class MaritimeDataRequest(BaseModel):
    mmsi: str = Field(..., description="Maritime Mobile Service Identity")
    vessel_name: str = Field("Unknown")
    vessel_type: str = Field("Unknown")
    flag: str = Field("Unknown")
    lat: float = Field(...)
    lon: float = Field(...)
    speed: float = Field(0.0)
    heading: float = Field(0.0)
    destination: str = Field("Unknown")
    ais_off: bool = Field(False)
    dark_voyage: bool = Field(False)
    spoofing_detected: bool = Field(False)


class AviationDataRequest(BaseModel):
    flight_id: str = Field(...)
    icao: str = Field("")
    callsign: str = Field("")
    origin: str = Field("Unknown")
    destination: str = Field("Unknown")
    lat: float = Field(...)
    lon: float = Field(...)
    altitude: int = Field(0)
    speed: float = Field(0.0)
    heading: float = Field(0.0)
    squawk: str = Field("")
    transponder_off: bool = Field(False)
    deviation_from_route: float = Field(0.0)


class CyberSignalRequest(BaseModel):
    threat_type: str = Field(..., description="Type of cyber threat")
    threat_actor: Optional[str] = Field(None)
    target_sector: str = Field("Unknown")
    target_country: str = Field("Unknown")
    attack_vector: str = Field("Unknown")
    iocs: list[str] = Field(default_factory=list)
    severity: int = Field(3, ge=1, le=5)
    cve_ids: list[str] = Field(default_factory=list)
    ttps: list[str] = Field(default_factory=list)
    source: str = Field("threat_intel")
    confidence: float = Field(0.7, ge=0, le=1)


class EntityRequest(BaseModel):
    entity_type: str = Field(..., description="Type of entity")
    name: str = Field(..., description="Entity name")
    aliases: list[str] = Field(default_factory=list)
    attributes: dict = Field(default_factory=dict)
    metadata: dict = Field(default_factory=dict)
    sources: list[str] = Field(default_factory=list)


class RelationshipRequest(BaseModel):
    source_entity_id: str = Field(...)
    target_entity_id: str = Field(...)
    relationship_type: str = Field(...)
    strength: float = Field(0.5, ge=0, le=1)
    confidence: float = Field(0.8, ge=0, le=1)
    evidence: list[str] = Field(default_factory=list)
    mechanism: Optional[str] = Field(None)


class RiskAssessmentRequest(BaseModel):
    region: str = Field(..., description="Region to assess")
    country: Optional[str] = Field(None)
    domains: list[str] = Field(default_factory=list, description="Risk domains to assess")
    indicators: dict = Field(default_factory=dict)


class EventRequest(BaseModel):
    category: str = Field(..., description="Event category")
    title: str = Field(...)
    description: str = Field("")
    lat: float = Field(0.0)
    lon: float = Field(0.0)
    affected_regions: list[str] = Field(default_factory=list)
    affected_countries: list[str] = Field(default_factory=list)
    actors: list[str] = Field(default_factory=list)
    impact_magnitude: int = Field(3, ge=1, le=6)
    sources: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)


class CascadePredictionRequest(BaseModel):
    trigger_event_id: str = Field(...)
    time_horizon_days: int = Field(30, ge=1, le=365)


class TimelineRequest(BaseModel):
    title: str = Field(...)
    start_date: datetime = Field(...)
    end_date: datetime = Field(...)
    filter_categories: list[str] = Field(default_factory=list)
    filter_regions: list[str] = Field(default_factory=list)


class SatelliteImageRequest(BaseModel):
    source: str = Field("sentinel_2")
    lat: float = Field(...)
    lon: float = Field(...)
    region: Optional[str] = Field(None)
    resolution_meters: float = Field(10.0)
    cloud_cover_percent: float = Field(0.0, ge=0, le=100)
    bands: list[str] = Field(default_factory=lambda: ["RGB", "NIR"])


class ChangeDetectionRequest(BaseModel):
    before_image_id: str = Field(...)
    after_image_id: str = Field(...)
    analysis_types: list[str] = Field(default_factory=list)


@router.post("/ingest/crisis")
async def ingest_crisis_feed(request: CrisisFeedRequest):
    """Ingest a crisis event from external feeds."""
    sensor_layer = GlobalSensorLayer()
    event = sensor_layer.ingest_crisis_feed(request.model_dump())
    return {
        "status": "success",
        "event_id": event.event_id,
        "event_type": event.event_type,
        "severity": event.severity.value,
        "location": event.location,
        "chain_of_custody_hash": event.chain_of_custody_hash,
    }


@router.post("/ingest/conflict")
async def ingest_conflict_indicator(request: ConflictIndicatorRequest):
    """Ingest a conflict indicator."""
    sensor_layer = GlobalSensorLayer()
    signal = sensor_layer.ingest_conflict_indicator(request.model_dump())
    return {
        "status": "success",
        "signal_id": signal.signal_id,
        "domain": signal.domain.value,
        "severity": signal.severity.value,
        "chain_of_custody_hash": signal.chain_of_custody_hash,
    }


@router.post("/ingest/maritime")
async def ingest_maritime_data(request: MaritimeDataRequest):
    """Ingest maritime AIS data."""
    sensor_layer = GlobalSensorLayer()
    signal = sensor_layer.ingest_maritime_data(request.model_dump())
    return {
        "status": "success",
        "signal_id": signal.signal_id,
        "vessel_mmsi": signal.vessel_mmsi,
        "anomaly_type": signal.anomaly_type,
        "anomaly_score": signal.anomaly_score,
        "chain_of_custody_hash": signal.chain_of_custody_hash,
    }


@router.post("/ingest/aviation")
async def ingest_aviation_data(request: AviationDataRequest):
    """Ingest aviation ADS-B data."""
    sensor_layer = GlobalSensorLayer()
    signal = sensor_layer.ingest_aviation_data(request.model_dump())
    return {
        "status": "success",
        "signal_id": signal.signal_id,
        "flight_id": signal.flight_id,
        "anomaly_type": signal.anomaly_type,
        "anomaly_score": signal.anomaly_score,
        "chain_of_custody_hash": signal.chain_of_custody_hash,
    }


@router.post("/ingest/cyber")
async def ingest_cyber_signal(request: CyberSignalRequest):
    """Ingest a cyber threat signal."""
    sensor_layer = GlobalSensorLayer()
    signal = sensor_layer.ingest_cyber_signal(request.model_dump())
    return {
        "status": "success",
        "signal_id": signal.signal_id,
        "threat_type": signal.threat_type,
        "severity": signal.severity.value,
        "chain_of_custody_hash": signal.chain_of_custody_hash,
    }


@router.get("/signals")
async def get_signals(
    domain: Optional[str] = Query(None, description="Filter by domain"),
    min_severity: int = Query(1, ge=1, le=5, description="Minimum severity"),
    region: Optional[str] = Query(None, description="Filter by region"),
    country: Optional[str] = Query(None, description="Filter by country"),
    hours: int = Query(24, ge=1, le=168, description="Hours to look back"),
):
    """Get global signals with optional filters."""
    sensor_layer = GlobalSensorLayer()

    if domain:
        try:
            domain_enum = SensorDomain(domain)
            signals = sensor_layer.get_signals_by_domain(domain_enum)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid domain: {domain}")
    else:
        signals = sensor_layer.get_recent_signals(hours)

    if min_severity > 1:
        severity_enum = SeverityLevel(min_severity)
        signals = [s for s in signals if s.severity.value >= severity_enum.value]

    if region:
        signals = [s for s in signals if region in s.affected_regions]

    if country:
        signals = [s for s in signals if country in s.affected_countries]

    return {
        "count": len(signals),
        "signals": [
            {
                "signal_id": s.signal_id,
                "domain": s.domain.value,
                "severity": s.severity.value,
                "title": s.title,
                "description": s.description,
                "location": s.location,
                "affected_regions": s.affected_regions,
                "affected_countries": s.affected_countries,
                "timestamp": s.timestamp.isoformat(),
                "confidence_score": s.confidence_score,
                "chain_of_custody_hash": s.chain_of_custody_hash,
            }
            for s in signals
        ],
    }


@router.get("/signals/actionable")
async def get_actionable_signals():
    """Get signals that require immediate action."""
    sensor_layer = GlobalSensorLayer()
    signals = sensor_layer.get_actionable_signals()
    return {
        "count": len(signals),
        "signals": [
            {
                "signal_id": s.signal_id,
                "domain": s.domain.value,
                "severity": s.severity.value,
                "title": s.title,
                "timestamp": s.timestamp.isoformat(),
            }
            for s in signals
        ],
    }


@router.post("/entities")
async def create_entity(request: EntityRequest):
    """Create a new entity in the knowledge graph."""
    kg_engine = KnowledgeGraphEngine()
    try:
        entity_type = EntityType(request.entity_type)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid entity type: {request.entity_type}")

    entity = kg_engine.create_entity(
        entity_type=entity_type,
        name=request.name,
        aliases=request.aliases,
        attributes=request.attributes,
        metadata=request.metadata,
        sources=request.sources,
    )
    return {
        "status": "success",
        "entity_id": entity.entity_id,
        "name": entity.name,
        "entity_type": entity.entity_type.value,
        "chain_of_custody_hash": entity.chain_of_custody_hash,
    }


@router.get("/entities/{entity_id}")
async def get_entity(entity_id: str):
    """Get an entity by ID."""
    kg_engine = KnowledgeGraphEngine()
    entity = kg_engine.get_entity(entity_id)
    if not entity:
        raise HTTPException(status_code=404, detail=f"Entity {entity_id} not found")
    return {
        "entity_id": entity.entity_id,
        "entity_type": entity.entity_type.value,
        "name": entity.name,
        "aliases": entity.aliases,
        "attributes": entity.attributes,
        "confidence_score": entity.confidence_score,
        "chain_of_custody_hash": entity.chain_of_custody_hash,
    }


@router.get("/entities/{entity_id}/network")
async def get_entity_network(entity_id: str, depth: int = Query(2, ge=1, le=4)):
    """Get the relationship network for an entity."""
    kg_engine = KnowledgeGraphEngine()
    entity = kg_engine.get_entity(entity_id)
    if not entity:
        raise HTTPException(status_code=404, detail=f"Entity {entity_id} not found")
    network = kg_engine.get_entity_network(entity_id, depth)
    return network


@router.post("/relationships")
async def create_relationship(request: RelationshipRequest):
    """Create a relationship between entities."""
    kg_engine = KnowledgeGraphEngine()
    try:
        rel_type = RelationshipType(request.relationship_type)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid relationship type: {request.relationship_type}")

    relationship = kg_engine.create_relationship(
        source_entity_id=request.source_entity_id,
        target_entity_id=request.target_entity_id,
        relationship_type=rel_type,
        strength=request.strength,
        confidence=request.confidence,
        evidence=request.evidence,
        mechanism=request.mechanism,
    )
    return {
        "status": "success",
        "relationship_id": relationship.relationship_id,
        "relationship_type": relationship.relationship_type.value,
        "chain_of_custody_hash": relationship.chain_of_custody_hash,
    }


@router.get("/entities/{entity_id}/influence")
async def get_entity_influence(entity_id: str, category: str = Query("political")):
    """Calculate influence score for an entity."""
    kg_engine = KnowledgeGraphEngine()
    try:
        cat_enum = InfluenceCategory(category)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid category: {category}")

    try:
        score = kg_engine.calculate_influence_score(entity_id, cat_enum)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return {
        "entity_id": score.entity_id,
        "category": score.category.value,
        "score": score.score,
        "rank": score.rank,
        "trend": score.trend,
        "factors": score.factors,
        "chain_of_custody_hash": score.chain_of_custody_hash,
    }


@router.post("/risk/assess")
async def assess_risk(request: RiskAssessmentRequest):
    """Create a fused risk assessment for a region."""
    risk_engine = RiskFusionEngine()
    assessment = risk_engine.create_fused_assessment(
        region=request.region,
        country=request.country,
    )
    return {
        "assessment_id": assessment.assessment_id,
        "region": assessment.region,
        "country": assessment.country,
        "overall_risk_score": assessment.overall_risk_score,
        "overall_risk_level": assessment.overall_risk_level.name,
        "domain_scores": assessment.domain_scores,
        "primary_risk_domain": assessment.primary_risk_domain.value,
        "secondary_risk_domains": [d.value for d in assessment.secondary_risk_domains],
        "risk_interactions": assessment.risk_interactions,
        "forecast_7_day": assessment.forecast_7_day,
        "forecast_30_day": assessment.forecast_30_day,
        "recommended_actions": assessment.recommended_actions,
        "chain_of_custody_hash": assessment.chain_of_custody_hash,
    }


@router.post("/risk/domain")
async def assess_domain_risk(
    domain: str,
    region: str,
    country: Optional[str] = None,
    indicators: dict = None,
):
    """Calculate risk score for a specific domain."""
    risk_engine = RiskFusionEngine()
    try:
        domain_enum = RiskDomain(domain)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid domain: {domain}")

    score = risk_engine.calculate_domain_risk(
        domain=domain_enum,
        region=region,
        country=country,
        indicators=indicators or {},
    )
    return {
        "score_id": score.score_id,
        "domain": score.domain.value,
        "region": score.region,
        "score": score.score,
        "level": score.level.name,
        "trend": score.trend.value,
        "contributing_factors": score.contributing_factors,
        "mitigation_recommendations": score.mitigation_recommendations,
        "chain_of_custody_hash": score.chain_of_custody_hash,
    }


@router.get("/risk/summary")
async def get_risk_summary():
    """Get regional risk summary."""
    risk_engine = RiskFusionEngine()
    return risk_engine.get_regional_risk_summary()


@router.get("/risk/alerts")
async def get_risk_alerts():
    """Get active risk alerts."""
    risk_engine = RiskFusionEngine()
    alerts = risk_engine.get_active_alerts()
    return {
        "count": len(alerts),
        "alerts": [
            {
                "alert_id": a.alert_id,
                "domain": a.domain.value,
                "region": a.region,
                "title": a.title,
                "risk_level": a.risk_level.name,
                "trigger_factors": a.trigger_factors,
                "recommended_response": a.recommended_response,
                "expires_at": a.expires_at.isoformat(),
            }
            for a in alerts
        ],
    }


@router.post("/events")
async def create_event(request: EventRequest):
    """Create a global event."""
    correlation_engine = EventCorrelationEngine()
    try:
        category = EventCategory(request.category)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid category: {request.category}")

    try:
        magnitude = ImpactMagnitude(request.impact_magnitude)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid impact magnitude: {request.impact_magnitude}")

    event = correlation_engine.create_event(
        category=category,
        title=request.title,
        description=request.description,
        location={"lat": request.lat, "lon": request.lon},
        affected_regions=request.affected_regions,
        affected_countries=request.affected_countries,
        actors=request.actors,
        impact_magnitude=magnitude,
        sources=request.sources,
        tags=request.tags,
    )
    return {
        "status": "success",
        "event_id": event.event_id,
        "category": event.category.value,
        "title": event.title,
        "impact_magnitude": event.impact_magnitude.value,
        "chain_of_custody_hash": event.chain_of_custody_hash,
    }


@router.get("/events/{event_id}")
async def get_event(event_id: str):
    """Get an event by ID."""
    correlation_engine = EventCorrelationEngine()
    event = correlation_engine.get_event(event_id)
    if not event:
        raise HTTPException(status_code=404, detail=f"Event {event_id} not found")
    return {
        "event_id": event.event_id,
        "category": event.category.value,
        "title": event.title,
        "description": event.description,
        "timestamp": event.timestamp.isoformat(),
        "location": event.location,
        "affected_regions": event.affected_regions,
        "affected_countries": event.affected_countries,
        "actors": event.actors,
        "impact_magnitude": event.impact_magnitude.value,
        "chain_of_custody_hash": event.chain_of_custody_hash,
    }


@router.get("/events/{event_id}/correlations")
async def get_event_correlations(event_id: str):
    """Get correlations for an event."""
    correlation_engine = EventCorrelationEngine()
    correlations = correlation_engine.get_correlations_for_event(event_id)
    return {
        "event_id": event_id,
        "count": len(correlations),
        "correlations": [
            {
                "correlation_id": c.correlation_id,
                "source_event_id": c.source_event_id,
                "target_event_id": c.target_event_id,
                "correlation_type": c.correlation_type.value,
                "strength": c.strength,
                "time_lag_hours": c.time_lag_hours,
            }
            for c in correlations
        ],
    }


@router.post("/events/cascade")
async def predict_cascade(request: CascadePredictionRequest):
    """Predict cascade effects from a trigger event."""
    correlation_engine = EventCorrelationEngine()
    try:
        cascade = correlation_engine.predict_cascade(
            trigger_event_id=request.trigger_event_id,
            time_horizon_days=request.time_horizon_days,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return {
        "cascade_id": cascade.cascade_id,
        "trigger_event_id": cascade.trigger_event_id,
        "cascade_type": cascade.cascade_type.value,
        "affected_events": cascade.affected_events,
        "propagation_path": cascade.propagation_path,
        "total_impact_score": cascade.total_impact_score,
        "time_horizon_days": cascade.time_horizon_days,
        "probability": cascade.probability,
        "mitigation_options": cascade.mitigation_options,
        "chain_of_custody_hash": cascade.chain_of_custody_hash,
    }


@router.post("/events/timeline")
async def reconstruct_timeline(request: TimelineRequest):
    """Reconstruct a timeline of events."""
    correlation_engine = EventCorrelationEngine()

    filter_categories = None
    if request.filter_categories:
        try:
            filter_categories = [EventCategory(c) for c in request.filter_categories]
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid category: {e}")

    timeline = correlation_engine.reconstruct_timeline(
        title=request.title,
        start_date=request.start_date,
        end_date=request.end_date,
        filter_categories=filter_categories,
        filter_regions=request.filter_regions,
    )
    return {
        "timeline_id": timeline.timeline_id,
        "title": timeline.title,
        "start_date": timeline.start_date.isoformat(),
        "end_date": timeline.end_date.isoformat(),
        "events": timeline.events,
        "correlations": timeline.correlations,
        "key_actors": timeline.key_actors,
        "key_locations": timeline.key_locations,
        "narrative_summary": timeline.narrative_summary,
        "chain_of_custody_hash": timeline.chain_of_custody_hash,
    }


@router.get("/events/patterns")
async def detect_patterns(min_frequency: int = Query(2, ge=2, le=10)):
    """Detect patterns in events."""
    correlation_engine = EventCorrelationEngine()
    patterns = correlation_engine.detect_patterns(min_frequency)
    return {
        "count": len(patterns),
        "patterns": [
            {
                "pattern_id": p.pattern_id,
                "pattern_name": p.pattern_name,
                "pattern_type": p.pattern_type,
                "frequency": p.frequency,
                "confidence": p.confidence,
                "description": p.description,
            }
            for p in patterns
        ],
    }


@router.post("/satellite/ingest")
async def ingest_satellite_image(request: SatelliteImageRequest):
    """Ingest a satellite image for analysis."""
    satellite_layer = SatelliteAnalysisLayer()
    try:
        source = ImagerySource(request.source)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid source: {request.source}")

    image = satellite_layer.ingest_image(
        source=source,
        location={"lat": request.lat, "lon": request.lon, "region": request.region},
        resolution_meters=request.resolution_meters,
        cloud_cover_percent=request.cloud_cover_percent,
        bands=request.bands,
    )
    return {
        "status": "success",
        "image_id": image.image_id,
        "source": image.source.value,
        "capture_time": image.capture_time.isoformat(),
        "chain_of_custody_hash": image.chain_of_custody_hash,
    }


@router.post("/satellite/detect-changes")
async def detect_satellite_changes(request: ChangeDetectionRequest):
    """Detect changes between two satellite images."""
    satellite_layer = SatelliteAnalysisLayer()

    analysis_types = None
    if request.analysis_types:
        try:
            analysis_types = [ChangeCategory(t) for t in request.analysis_types]
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid analysis type: {e}")

    try:
        detections = satellite_layer.detect_changes(
            before_image_id=request.before_image_id,
            after_image_id=request.after_image_id,
            analysis_types=analysis_types,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return {
        "count": len(detections),
        "detections": [
            {
                "detection_id": d.detection_id,
                "change_category": d.change_category.value,
                "area_sq_km": d.area_sq_km,
                "change_magnitude": d.change_magnitude,
                "confidence": d.confidence.value,
                "description": d.description,
                "chain_of_custody_hash": d.chain_of_custody_hash,
            }
            for d in detections
        ],
    }


@router.post("/satellite/maritime/{image_id}")
async def analyze_maritime(image_id: str, region: Optional[str] = None):
    """Analyze maritime activity in a satellite image."""
    satellite_layer = SatelliteAnalysisLayer()
    try:
        detection = satellite_layer.analyze_maritime_activity(image_id, region)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return {
        "detection_id": detection.detection_id,
        "image_id": detection.image_id,
        "vessel_count": detection.vessel_count,
        "vessels": detection.vessels[:10],
        "port_activity_level": detection.port_activity_level,
        "anomalies": detection.anomalies,
        "chain_of_custody_hash": detection.chain_of_custody_hash,
    }


@router.post("/satellite/infrastructure/{image_id}")
async def assess_infrastructure(image_id: str, infrastructure_type: str):
    """Assess infrastructure in a satellite image."""
    satellite_layer = SatelliteAnalysisLayer()
    try:
        assessment = satellite_layer.assess_infrastructure(image_id, infrastructure_type)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return {
        "assessment_id": assessment.assessment_id,
        "infrastructure_type": assessment.infrastructure_type,
        "condition": assessment.condition,
        "damage_level": assessment.damage_level,
        "activity_level": assessment.activity_level,
        "changes_detected": assessment.changes_detected,
        "confidence": assessment.confidence.value,
        "chain_of_custody_hash": assessment.chain_of_custody_hash,
    }


@router.post("/satellite/military/{image_id}")
async def detect_military(image_id: str, region: Optional[str] = None):
    """Detect military activity in a satellite image."""
    satellite_layer = SatelliteAnalysisLayer()
    try:
        detection = satellite_layer.detect_military_activity(image_id, region)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return {
        "detection_id": detection.detection_id,
        "activity_type": detection.activity_type,
        "unit_types": detection.unit_types,
        "estimated_personnel": detection.estimated_personnel,
        "vehicle_count": detection.vehicle_count,
        "aircraft_count": detection.aircraft_count,
        "confidence": detection.confidence.value,
        "assessment": detection.assessment,
        "chain_of_custody_hash": detection.chain_of_custody_hash,
    }


@router.get("/satellite/alerts")
async def get_satellite_alerts():
    """Get active satellite alerts."""
    satellite_layer = SatelliteAnalysisLayer()
    alerts = satellite_layer.get_active_alerts()
    return {
        "count": len(alerts),
        "alerts": [
            {
                "alert_id": a.alert_id,
                "alert_type": a.alert_type,
                "priority": a.priority.value,
                "title": a.title,
                "description": a.description,
                "location": a.location,
                "recommended_action": a.recommended_action,
                "expires_at": a.expires_at.isoformat(),
            }
            for a in alerts
        ],
    }


@router.get("/satellite/detections")
async def get_recent_detections(hours: int = Query(24, ge=1, le=168)):
    """Get recent satellite detections."""
    satellite_layer = SatelliteAnalysisLayer()
    detections = satellite_layer.get_recent_detections(hours)
    return {
        "change_detections": len(detections["change_detections"]),
        "maritime_detections": len(detections["maritime_detections"]),
        "infrastructure_assessments": len(detections["infrastructure_assessments"]),
        "military_detections": len(detections["military_detections"]),
    }


@router.get("/statistics")
async def get_statistics():
    """Get statistics from all GSAE modules."""
    sensor_layer = GlobalSensorLayer()
    kg_engine = KnowledgeGraphEngine()
    risk_engine = RiskFusionEngine()
    correlation_engine = EventCorrelationEngine()
    satellite_layer = SatelliteAnalysisLayer()

    return {
        "sensor_layer": sensor_layer.get_statistics(),
        "knowledge_graph": kg_engine.get_statistics(),
        "risk_fusion": risk_engine.get_statistics(),
        "event_correlation": correlation_engine.get_statistics(),
        "satellite_analysis": satellite_layer.get_statistics(),
    }
