"""
Phase 17: Global Threat Intelligence API Router

Provides REST endpoints for:
- Dark Web monitoring
- OSINT harvesting
- Extremist network analysis
- Global incident monitoring
- Threat scoring
- Threat alerts
"""

from datetime import datetime
from typing import Any, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.threat_intel.dark_web_monitor import (
    DarkWebMonitor,
    SignalType,
    MarketCategory,
    SignalStatus,
)
from app.threat_intel.osint_harvester import (
    OSINTHarvester,
    SourceType,
    ContentCategory,
    EventLikelihood,
)
from app.threat_intel.extremist_networks import (
    ExtremistNetworkAnalyzer,
    NodeType,
    EdgeType,
    IdeologyType,
    ThreatLevel as NetworkThreatLevel,
)
from app.threat_intel.global_incidents import (
    GlobalIncidentMonitor,
    IncidentType,
    IncidentSeverity,
    IncidentStatus,
    FeedSource,
    AlertLevel,
)
from app.threat_intel.threat_scoring_engine import (
    ThreatScoringEngine,
    ThreatLevel,
    ThreatDomain,
    RuleType,
    FusionMethod,
    TriggerAction,
)
from app.threat_intel.threat_alerts import (
    ThreatAlertManager,
    AlertPriority,
    AlertStatus as ThreatAlertStatus,
    AlertCategory,
    AlertDestination,
    EscalationLevel,
)

router = APIRouter()

dark_web_monitor = DarkWebMonitor()
osint_harvester = OSINTHarvester()
extremist_analyzer = ExtremistNetworkAnalyzer()
incident_monitor = GlobalIncidentMonitor()
scoring_engine = ThreatScoringEngine()
alert_manager = ThreatAlertManager()


class KeywordProfileCreate(BaseModel):
    name: str
    keywords: list[str]
    regex_patterns: list[str] = Field(default_factory=list)
    category: str = "general"
    priority: int = 1
    jurisdiction_codes: list[str] = Field(default_factory=list)


class ContentAnalyzeRequest(BaseModel):
    content: str
    source_platform: str = "unknown"
    source_url: str = ""


class MarketListingRequest(BaseModel):
    title: str
    description: str
    price: float
    currency: str = "USD"
    market_name: str = ""
    seller_name: str = ""
    category: str = ""


class RSSFeedCreate(BaseModel):
    name: str
    url: str
    category: str = "other"
    poll_interval_minutes: int = 15
    jurisdiction_codes: list[str] = Field(default_factory=list)


class NewsArticleIngest(BaseModel):
    title: str
    content: str
    source_name: str
    source_url: str = ""
    source_type: str = "news_rss"
    author: str = ""


class SocialSignalIngest(BaseModel):
    content: str
    source_type: str = "social_twitter"
    platform_id: str = ""
    author_id: str = ""
    author_name: str = ""
    author_followers: int = 0
    engagement_count: int = 0


class EventPredictionCreate(BaseModel):
    event_type: str
    title: str
    description: str
    predicted_location: str
    likelihood: str = "possible"
    confidence_score: float = 0.5
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    estimated_participants: int = 0


class NetworkNodeCreate(BaseModel):
    name: str
    node_type: str = "individual"
    ideology: Optional[str] = None
    platform: str = ""
    platform_id: str = ""
    description: str = ""
    location: str = ""
    aliases: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)


class NetworkEdgeCreate(BaseModel):
    source_node_id: str
    target_node_id: str
    edge_type: str = "associated_with"
    weight: float = 1.0
    confidence: float = 0.5
    evidence: list[str] = Field(default_factory=list)


class ClusterCreate(BaseModel):
    name: str
    node_ids: list[str]
    ideology: Optional[str] = None
    description: str = ""


class IncidentIngest(BaseModel):
    incident_type: str
    title: str
    description: str
    latitude: float
    longitude: float
    severity: str = "moderate"
    source: str = "custom"
    country: str = ""
    region: str = ""
    city: str = ""
    radius_km: float = 0.0
    affected_population: int = 0
    casualties: int = 0
    injuries: int = 0


class CrisisAlertCreate(BaseModel):
    title: str
    description: str
    alert_level: str
    incident_ids: list[str]
    affected_jurisdictions: list[str] = Field(default_factory=list)
    center_latitude: float = 0.0
    center_longitude: float = 0.0
    radius_km: float = 0.0
    recommended_actions: list[str] = Field(default_factory=list)
    expires_in_hours: int = 24


class FeedConfigCreate(BaseModel):
    source: str
    name: str
    endpoint_url: str = ""
    poll_interval_minutes: int = 5
    incident_types: list[str] = Field(default_factory=list)


class ScoringRuleCreate(BaseModel):
    name: str
    rule_type: str
    domain: str
    conditions: dict[str, Any]
    score_contribution: float
    weight: float = 1.0
    priority: int = 1
    description: str = ""
    trigger_actions: list[str] = Field(default_factory=list)


class TriggerConditionCreate(BaseModel):
    name: str
    threshold_score: float
    actions: list[str]
    threshold_level: Optional[str] = None
    domains: list[str] = Field(default_factory=list)
    entity_types: list[str] = Field(default_factory=list)
    jurisdiction_codes: list[str] = Field(default_factory=list)
    cooldown_minutes: int = 60
    description: str = ""


class ScoreCalculateRequest(BaseModel):
    entity_id: str
    entity_type: str
    entity_name: str
    domain_inputs: dict[str, dict[str, Any]]
    jurisdiction_codes: list[str] = Field(default_factory=list)


class FusionRequest(BaseModel):
    entity_id: str
    entity_type: str
    score_ids: list[str]
    method: str = "weighted_average"
    custom_weights: Optional[dict[str, float]] = None


class ThreatAlertCreate(BaseModel):
    title: str
    description: str
    priority: str
    category: str
    source_module: str = ""
    source_signal_ids: list[str] = Field(default_factory=list)
    threat_score: float = 0.0
    threat_level: str = ""
    entity_id: str = ""
    entity_type: str = ""
    entity_name: str = ""
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    jurisdiction_codes: list[str] = Field(default_factory=list)
    recommended_actions: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)


class RoutingRuleCreate(BaseModel):
    name: str
    destinations: list[str]
    categories: list[str] = Field(default_factory=list)
    min_priority: str = "p3_moderate"
    jurisdiction_codes: list[str] = Field(default_factory=list)
    description: str = ""
    auto_escalate: bool = False
    escalation_threshold_minutes: int = 30


class SubscriptionCreate(BaseModel):
    subscriber_id: str
    subscriber_type: str
    subscriber_name: str
    categories: list[str] = Field(default_factory=list)
    min_priority: str = "p3_moderate"
    jurisdiction_codes: list[str] = Field(default_factory=list)
    websocket_channel: str = ""
    webhook_url: str = ""
    email: str = ""


@router.get("/dark-web/profiles")
async def get_keyword_profiles():
    """Get all keyword profiles"""
    profiles = dark_web_monitor.get_all_keyword_profiles()
    return {"profiles": [vars(p) for p in profiles]}


@router.post("/dark-web/profiles")
async def create_keyword_profile(data: KeywordProfileCreate):
    """Create a keyword profile"""
    profile = dark_web_monitor.create_keyword_profile(
        name=data.name,
        keywords=data.keywords,
        regex_patterns=data.regex_patterns,
        category=data.category,
        priority=data.priority,
        jurisdiction_codes=data.jurisdiction_codes,
    )
    return {"profile": vars(profile)}


@router.get("/dark-web/profiles/{profile_id}")
async def get_keyword_profile(profile_id: str):
    """Get a keyword profile by ID"""
    profile = dark_web_monitor.get_keyword_profile(profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return {"profile": vars(profile)}


@router.delete("/dark-web/profiles/{profile_id}")
async def delete_keyword_profile(profile_id: str):
    """Delete a keyword profile"""
    success = dark_web_monitor.delete_keyword_profile(profile_id)
    if not success:
        raise HTTPException(status_code=404, detail="Profile not found")
    return {"success": True}


@router.post("/dark-web/analyze")
async def analyze_dark_web_content(data: ContentAnalyzeRequest):
    """Analyze dark web content"""
    signal = dark_web_monitor.analyze_content(
        content=data.content,
        source_platform=data.source_platform,
        source_url=data.source_url,
    )
    return {"signal": vars(signal)}


@router.post("/dark-web/market-listing")
async def analyze_market_listing(data: MarketListingRequest):
    """Analyze a market listing"""
    category = MarketCategory(data.category) if data.category else None
    listing = dark_web_monitor.analyze_market_listing(
        title=data.title,
        description=data.description,
        price=data.price,
        currency=data.currency,
        market_name=data.market_name,
        seller_name=data.seller_name,
        category=category,
    )
    return {"listing": vars(listing)}


@router.get("/dark-web/signals")
async def get_dark_web_signals(
    signal_type: Optional[str] = None,
    status: Optional[str] = None,
    min_priority: float = 0.0,
    limit: int = Query(default=100, le=500),
):
    """Get dark web signals"""
    sig_type = SignalType(signal_type) if signal_type else None
    sig_status = SignalStatus(status) if status else None
    signals = dark_web_monitor.get_all_signals(
        signal_type=sig_type,
        status=sig_status,
        min_priority=min_priority,
        limit=limit,
    )
    return {"signals": [vars(s) for s in signals]}


@router.get("/dark-web/signals/{signal_id}")
async def get_dark_web_signal(signal_id: str):
    """Get a dark web signal by ID"""
    signal = dark_web_monitor.get_signal(signal_id)
    if not signal:
        raise HTTPException(status_code=404, detail="Signal not found")
    return {"signal": vars(signal)}


@router.get("/dark-web/signals/high-priority")
async def get_high_priority_signals(threshold: float = 70.0, limit: int = 50):
    """Get high priority dark web signals"""
    signals = dark_web_monitor.get_high_priority_signals(threshold=threshold, limit=limit)
    return {"signals": [vars(s) for s in signals]}


@router.get("/dark-web/listings")
async def get_market_listings(
    category: Optional[str] = None,
    min_threat_score: float = 0.0,
    limit: int = Query(default=100, le=500),
):
    """Get market listings"""
    cat = MarketCategory(category) if category else None
    listings = dark_web_monitor.get_all_listings(
        category=cat,
        min_threat_score=min_threat_score,
        limit=limit,
    )
    return {"listings": [vars(l) for l in listings]}


@router.get("/dark-web/metrics")
async def get_dark_web_metrics():
    """Get dark web monitor metrics"""
    return dark_web_monitor.get_metrics()


@router.get("/osint/feeds")
async def get_rss_feeds():
    """Get all RSS feeds"""
    feeds = osint_harvester.get_all_rss_feeds()
    return {"feeds": [vars(f) for f in feeds]}


@router.post("/osint/feeds")
async def add_rss_feed(data: RSSFeedCreate):
    """Add an RSS feed"""
    category = ContentCategory(data.category) if data.category else ContentCategory.OTHER
    feed = osint_harvester.add_rss_feed(
        name=data.name,
        url=data.url,
        category=category,
        poll_interval_minutes=data.poll_interval_minutes,
        jurisdiction_codes=data.jurisdiction_codes,
    )
    return {"feed": vars(feed)}


@router.delete("/osint/feeds/{feed_id}")
async def remove_rss_feed(feed_id: str):
    """Remove an RSS feed"""
    success = osint_harvester.remove_rss_feed(feed_id)
    if not success:
        raise HTTPException(status_code=404, detail="Feed not found")
    return {"success": True}


@router.post("/osint/articles")
async def ingest_news_article(data: NewsArticleIngest):
    """Ingest a news article"""
    source_type = SourceType(data.source_type) if data.source_type else SourceType.NEWS_RSS
    article = osint_harvester.ingest_news_article(
        title=data.title,
        content=data.content,
        source_name=data.source_name,
        source_url=data.source_url,
        source_type=source_type,
        author=data.author,
    )
    return {"article": vars(article)}


@router.get("/osint/articles")
async def get_articles(
    category: Optional[str] = None,
    source_type: Optional[str] = None,
    min_relevance: float = 0.0,
    limit: int = Query(default=100, le=500),
):
    """Get news articles"""
    cat = ContentCategory(category) if category else None
    src = SourceType(source_type) if source_type else None
    articles = osint_harvester.get_all_articles(
        category=cat,
        source_type=src,
        min_relevance=min_relevance,
        limit=limit,
    )
    return {"articles": [vars(a) for a in articles]}


@router.post("/osint/social")
async def ingest_social_signal(data: SocialSignalIngest):
    """Ingest a social media signal"""
    source_type = SourceType(data.source_type) if data.source_type else SourceType.SOCIAL_TWITTER
    signal = osint_harvester.ingest_social_signal(
        content=data.content,
        source_type=source_type,
        platform_id=data.platform_id,
        author_id=data.author_id,
        author_name=data.author_name,
        author_followers=data.author_followers,
        engagement_count=data.engagement_count,
    )
    return {"signal": vars(signal)}


@router.get("/osint/social")
async def get_social_signals(
    source_type: Optional[str] = None,
    hate_speech_only: bool = False,
    min_threat_score: float = 0.0,
    limit: int = Query(default=100, le=500),
):
    """Get social signals"""
    src = SourceType(source_type) if source_type else None
    signals = osint_harvester.get_all_social_signals(
        source_type=src,
        hate_speech_only=hate_speech_only,
        min_threat_score=min_threat_score,
        limit=limit,
    )
    return {"signals": [vars(s) for s in signals]}


@router.get("/osint/spikes")
async def get_keyword_spikes(status: Optional[str] = None, limit: int = 50):
    """Get keyword spikes"""
    from app.threat_intel.osint_harvester import SpikeStatus
    spike_status = SpikeStatus(status) if status else None
    spikes = osint_harvester.get_all_keyword_spikes(status=spike_status, limit=limit)
    return {"spikes": [vars(s) for s in spikes]}


@router.post("/osint/spikes/detect")
async def detect_keyword_spikes(threshold_percentage: float = 200.0, min_count: int = 10):
    """Detect keyword spikes"""
    spikes = osint_harvester.detect_keyword_spikes(
        threshold_percentage=threshold_percentage,
        min_count=min_count,
    )
    return {"new_spikes": [vars(s) for s in spikes]}


@router.post("/osint/predictions")
async def create_event_prediction(data: EventPredictionCreate):
    """Create an event prediction"""
    likelihood = EventLikelihood(data.likelihood) if data.likelihood else EventLikelihood.POSSIBLE
    prediction = osint_harvester.create_event_prediction(
        event_type=data.event_type,
        title=data.title,
        description=data.description,
        predicted_location=data.predicted_location,
        likelihood=likelihood,
        confidence_score=data.confidence_score,
        latitude=data.latitude,
        longitude=data.longitude,
        estimated_participants=data.estimated_participants,
    )
    return {"prediction": vars(prediction)}


@router.get("/osint/predictions")
async def get_event_predictions(
    likelihood: Optional[str] = None,
    active_only: bool = True,
    limit: int = 50,
):
    """Get event predictions"""
    lik = EventLikelihood(likelihood) if likelihood else None
    predictions = osint_harvester.get_all_event_predictions(
        likelihood=lik,
        active_only=active_only,
        limit=limit,
    )
    return {"predictions": [vars(p) for p in predictions]}


@router.get("/osint/metrics")
async def get_osint_metrics():
    """Get OSINT harvester metrics"""
    return osint_harvester.get_metrics()


@router.post("/extremist/nodes")
async def add_network_node(data: NetworkNodeCreate):
    """Add a network node"""
    node_type = NodeType(data.node_type) if data.node_type else NodeType.INDIVIDUAL
    ideology = IdeologyType(data.ideology) if data.ideology else None
    node = extremist_analyzer.add_node(
        name=data.name,
        node_type=node_type,
        ideology=ideology,
        platform=data.platform,
        platform_id=data.platform_id,
        description=data.description,
        location=data.location,
        aliases=data.aliases,
        tags=data.tags,
    )
    return {"node": vars(node)}


@router.get("/extremist/nodes")
async def get_network_nodes(
    node_type: Optional[str] = None,
    ideology: Optional[str] = None,
    threat_level: Optional[str] = None,
    limit: int = Query(default=100, le=500),
):
    """Get network nodes"""
    nt = NodeType(node_type) if node_type else None
    ideo = IdeologyType(ideology) if ideology else None
    tl = NetworkThreatLevel(threat_level) if threat_level else None
    nodes = extremist_analyzer.get_all_nodes(
        node_type=nt,
        ideology=ideo,
        threat_level=tl,
        limit=limit,
    )
    return {"nodes": [vars(n) for n in nodes]}


@router.get("/extremist/nodes/{node_id}")
async def get_network_node(node_id: str):
    """Get a network node by ID"""
    node = extremist_analyzer.get_node(node_id)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    return {"node": vars(node)}


@router.delete("/extremist/nodes/{node_id}")
async def remove_network_node(node_id: str):
    """Remove a network node"""
    success = extremist_analyzer.remove_node(node_id)
    if not success:
        raise HTTPException(status_code=404, detail="Node not found")
    return {"success": True}


@router.post("/extremist/edges")
async def add_network_edge(data: NetworkEdgeCreate):
    """Add a network edge"""
    edge_type = EdgeType(data.edge_type) if data.edge_type else EdgeType.ASSOCIATED_WITH
    edge = extremist_analyzer.add_edge(
        source_node_id=data.source_node_id,
        target_node_id=data.target_node_id,
        edge_type=edge_type,
        weight=data.weight,
        confidence=data.confidence,
        evidence=data.evidence,
    )
    if not edge:
        raise HTTPException(status_code=400, detail="Invalid node IDs")
    return {"edge": vars(edge)}


@router.get("/extremist/nodes/{node_id}/connections")
async def get_node_connections(node_id: str, max_depth: int = 1):
    """Get connected nodes"""
    connected = extremist_analyzer.get_connected_nodes(node_id, max_depth=max_depth)
    return {"connected_nodes": [vars(n) for n in connected]}


@router.post("/extremist/nodes/{node_id}/influence")
async def calculate_influence(node_id: str):
    """Calculate influence score for a node"""
    score = extremist_analyzer.calculate_influence_score(node_id)
    if not score:
        raise HTTPException(status_code=404, detail="Node not found")
    return {"influence_score": vars(score)}


@router.post("/extremist/nodes/{node_id}/trajectory")
async def analyze_trajectory(
    node_id: str,
    risk_indicators: list[str] = Query(default=[]),
    protective_factors: list[str] = Query(default=[]),
):
    """Analyze radicalization trajectory"""
    trajectory = extremist_analyzer.analyze_radicalization_trajectory(
        node_id,
        risk_indicators=risk_indicators,
        protective_factors=protective_factors,
    )
    if not trajectory:
        raise HTTPException(status_code=404, detail="Node not found or not an individual")
    return {"trajectory": vars(trajectory)}


@router.post("/extremist/clusters")
async def create_cluster(data: ClusterCreate):
    """Create a network cluster"""
    ideology = IdeologyType(data.ideology) if data.ideology else None
    cluster = extremist_analyzer.create_cluster(
        name=data.name,
        node_ids=data.node_ids,
        ideology=ideology,
        description=data.description,
    )
    return {"cluster": vars(cluster)}


@router.get("/extremist/clusters")
async def get_clusters(
    ideology: Optional[str] = None,
    threat_level: Optional[str] = None,
):
    """Get network clusters"""
    ideo = IdeologyType(ideology) if ideology else None
    tl = NetworkThreatLevel(threat_level) if threat_level else None
    clusters = extremist_analyzer.get_all_clusters(ideology=ideo, threat_level=tl)
    return {"clusters": [vars(c) for c in clusters]}


@router.post("/extremist/clusters/detect")
async def detect_clusters(min_size: int = 3):
    """Automatically detect clusters"""
    clusters = extremist_analyzer.detect_clusters(min_size=min_size)
    return {"detected_clusters": [vars(c) for c in clusters]}


@router.get("/extremist/high-risk")
async def get_high_risk_nodes(threshold: float = 60.0):
    """Get high risk nodes"""
    nodes = extremist_analyzer.get_high_risk_nodes(threshold=threshold)
    return {"high_risk_nodes": [vars(n) for n in nodes]}


@router.get("/extremist/influencers")
async def get_top_influencers(limit: int = 10):
    """Get top influencer nodes"""
    nodes = extremist_analyzer.get_top_influencers(limit=limit)
    return {"influencers": [vars(n) for n in nodes]}


@router.get("/extremist/graph")
async def export_network_graph():
    """Export network graph for visualization"""
    return extremist_analyzer.export_graph()


@router.get("/extremist/metrics")
async def get_extremist_metrics():
    """Get extremist network analyzer metrics"""
    return extremist_analyzer.get_metrics()


@router.post("/incidents/feeds")
async def configure_incident_feed(data: FeedConfigCreate):
    """Configure an incident feed"""
    source = FeedSource(data.source) if data.source else FeedSource.CUSTOM
    incident_types = [IncidentType(t) for t in data.incident_types] if data.incident_types else None
    feed = incident_monitor.configure_feed(
        source=source,
        name=data.name,
        endpoint_url=data.endpoint_url,
        poll_interval_minutes=data.poll_interval_minutes,
        incident_types=incident_types,
    )
    return {"feed": vars(feed)}


@router.get("/incidents/feeds")
async def get_incident_feeds():
    """Get all incident feeds"""
    feeds = incident_monitor.get_all_feeds()
    return {"feeds": [vars(f) for f in feeds]}


@router.post("/incidents")
async def ingest_incident(data: IncidentIngest):
    """Ingest a global incident"""
    incident_type = IncidentType(data.incident_type) if data.incident_type else IncidentType.OTHER
    severity = IncidentSeverity(data.severity) if data.severity else IncidentSeverity.MODERATE
    source = FeedSource(data.source) if data.source else FeedSource.CUSTOM
    incident = incident_monitor.ingest_incident(
        incident_type=incident_type,
        title=data.title,
        description=data.description,
        latitude=data.latitude,
        longitude=data.longitude,
        severity=severity,
        source=source,
        country=data.country,
        region=data.region,
        city=data.city,
        radius_km=data.radius_km,
        affected_population=data.affected_population,
        casualties=data.casualties,
        injuries=data.injuries,
    )
    return {"incident": vars(incident)}


@router.get("/incidents")
async def get_incidents(
    incident_type: Optional[str] = None,
    severity: Optional[str] = None,
    status: Optional[str] = None,
    source: Optional[str] = None,
    country: Optional[str] = None,
    limit: int = Query(default=100, le=500),
):
    """Get global incidents"""
    it = IncidentType(incident_type) if incident_type else None
    sev = IncidentSeverity(severity) if severity else None
    stat = IncidentStatus(status) if status else None
    src = FeedSource(source) if source else None
    incidents = incident_monitor.get_all_incidents(
        incident_type=it,
        severity=sev,
        status=stat,
        source=src,
        country=country,
        limit=limit,
    )
    return {"incidents": [vars(i) for i in incidents]}


@router.get("/incidents/{incident_id}")
async def get_incident(incident_id: str):
    """Get an incident by ID"""
    incident = incident_monitor.get_incident(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return {"incident": vars(incident)}


@router.get("/incidents/near")
async def get_incidents_near_location(
    latitude: float,
    longitude: float,
    radius_km: float = 100,
    limit: int = 50,
):
    """Get incidents near a location"""
    incidents = incident_monitor.get_incidents_near_location(
        latitude=latitude,
        longitude=longitude,
        radius_km=radius_km,
        limit=limit,
    )
    return {"incidents": [vars(i) for i in incidents]}


@router.post("/incidents/alerts")
async def create_crisis_alert(data: CrisisAlertCreate):
    """Create a crisis alert"""
    alert_level = AlertLevel(data.alert_level) if data.alert_level else AlertLevel.ADVISORY
    alert = incident_monitor.create_crisis_alert(
        title=data.title,
        description=data.description,
        alert_level=alert_level,
        incident_ids=data.incident_ids,
        affected_jurisdictions=data.affected_jurisdictions,
        center_latitude=data.center_latitude,
        center_longitude=data.center_longitude,
        radius_km=data.radius_km,
        recommended_actions=data.recommended_actions,
        expires_in_hours=data.expires_in_hours,
    )
    return {"alert": vars(alert)}


@router.get("/incidents/alerts")
async def get_crisis_alerts(
    alert_level: Optional[str] = None,
    active_only: bool = True,
    limit: int = 50,
):
    """Get crisis alerts"""
    level = AlertLevel(alert_level) if alert_level else None
    alerts = incident_monitor.get_all_alerts(
        alert_level=level,
        active_only=active_only,
        limit=limit,
    )
    return {"alerts": [vars(a) for a in alerts]}


@router.get("/incidents/map")
async def get_crisis_map_data(
    south: Optional[float] = None,
    north: Optional[float] = None,
    west: Optional[float] = None,
    east: Optional[float] = None,
):
    """Get crisis map data"""
    bounds = None
    if all(v is not None for v in [south, north, west, east]):
        bounds = {"south": south, "north": north, "west": west, "east": east}
    return incident_monitor.get_crisis_map_data(bounds=bounds)


@router.get("/incidents/correlations")
async def get_correlations(
    jurisdiction: Optional[str] = None,
    min_confidence: float = 0.0,
    limit: int = 100,
):
    """Get geo-threat correlations"""
    correlations = incident_monitor.get_all_correlations(
        jurisdiction=jurisdiction,
        min_confidence=min_confidence,
        limit=limit,
    )
    return {"correlations": [vars(c) for c in correlations]}


@router.get("/incidents/metrics")
async def get_incident_metrics():
    """Get global incident monitor metrics"""
    return incident_monitor.get_metrics()


@router.post("/scoring/rules")
async def create_scoring_rule(data: ScoringRuleCreate):
    """Create a scoring rule"""
    rule_type = RuleType(data.rule_type) if data.rule_type else RuleType.THRESHOLD
    domain = ThreatDomain(data.domain) if data.domain else ThreatDomain.LOCAL_CRIME
    trigger_actions = [TriggerAction(a) for a in data.trigger_actions] if data.trigger_actions else None
    rule = scoring_engine.create_rule(
        name=data.name,
        rule_type=rule_type,
        domain=domain,
        conditions=data.conditions,
        score_contribution=data.score_contribution,
        weight=data.weight,
        priority=data.priority,
        description=data.description,
        trigger_actions=trigger_actions,
    )
    return {"rule": vars(rule)}


@router.get("/scoring/rules")
async def get_scoring_rules(
    domain: Optional[str] = None,
    rule_type: Optional[str] = None,
    enabled_only: bool = True,
):
    """Get scoring rules"""
    dom = ThreatDomain(domain) if domain else None
    rt = RuleType(rule_type) if rule_type else None
    rules = scoring_engine.get_all_rules(domain=dom, rule_type=rt, enabled_only=enabled_only)
    return {"rules": [vars(r) for r in rules]}


@router.delete("/scoring/rules/{rule_id}")
async def delete_scoring_rule(rule_id: str):
    """Delete a scoring rule"""
    success = scoring_engine.delete_rule(rule_id)
    if not success:
        raise HTTPException(status_code=404, detail="Rule not found")
    return {"success": True}


@router.post("/scoring/triggers")
async def create_trigger_condition(data: TriggerConditionCreate):
    """Create a trigger condition"""
    threshold_level = ThreatLevel(data.threshold_level) if data.threshold_level else None
    domains = [ThreatDomain(d) for d in data.domains] if data.domains else None
    actions = [TriggerAction(a) for a in data.actions]
    trigger = scoring_engine.create_trigger(
        name=data.name,
        threshold_score=data.threshold_score,
        actions=actions,
        threshold_level=threshold_level,
        domains=domains,
        entity_types=data.entity_types,
        jurisdiction_codes=data.jurisdiction_codes,
        cooldown_minutes=data.cooldown_minutes,
        description=data.description,
    )
    return {"trigger": vars(trigger)}


@router.get("/scoring/triggers")
async def get_trigger_conditions(enabled_only: bool = True):
    """Get trigger conditions"""
    triggers = scoring_engine.get_all_triggers(enabled_only=enabled_only)
    return {"triggers": [vars(t) for t in triggers]}


@router.post("/scoring/calculate")
async def calculate_threat_score(data: ScoreCalculateRequest):
    """Calculate threat score for an entity"""
    score = scoring_engine.calculate_score(
        entity_id=data.entity_id,
        entity_type=data.entity_type,
        entity_name=data.entity_name,
        domain_inputs=data.domain_inputs,
        jurisdiction_codes=data.jurisdiction_codes,
    )
    return {"score": vars(score)}


@router.post("/scoring/fuse")
async def fuse_threat_scores(data: FusionRequest):
    """Fuse multiple threat scores"""
    scores = [scoring_engine.get_score(sid) for sid in data.score_ids]
    scores = [s for s in scores if s is not None]
    if not scores:
        raise HTTPException(status_code=400, detail="No valid scores found")
    
    method = FusionMethod(data.method) if data.method else FusionMethod.WEIGHTED_AVERAGE
    fusion = scoring_engine.fuse_scores(
        entity_id=data.entity_id,
        entity_type=data.entity_type,
        scores=scores,
        method=method,
        custom_weights=data.custom_weights,
    )
    return {"fusion": vars(fusion)}


@router.get("/scoring/scores/{entity_id}")
async def get_entity_scores(entity_id: str, limit: int = 10):
    """Get scores for an entity"""
    scores = scoring_engine.get_scores_for_entity(entity_id, limit=limit)
    return {"scores": [vars(s) for s in scores]}


@router.get("/scoring/high-threat")
async def get_high_threat_scores(min_level: str = "level_4_high", limit: int = 50):
    """Get high threat scores"""
    level = ThreatLevel(min_level) if min_level else ThreatLevel.LEVEL_4_HIGH
    scores = scoring_engine.get_high_threat_scores(min_level=level, limit=limit)
    return {"scores": [vars(s) for s in scores]}


@router.get("/scoring/metrics")
async def get_scoring_metrics():
    """Get threat scoring engine metrics"""
    return scoring_engine.get_metrics()


@router.post("/alerts")
async def create_threat_alert(data: ThreatAlertCreate):
    """Create a threat alert"""
    priority = AlertPriority(data.priority) if data.priority else AlertPriority.P3_MODERATE
    category = AlertCategory(data.category) if data.category else AlertCategory.COMPOSITE
    alert = alert_manager.create_alert(
        title=data.title,
        description=data.description,
        priority=priority,
        category=category,
        source_module=data.source_module,
        source_signal_ids=data.source_signal_ids,
        threat_score=data.threat_score,
        threat_level=data.threat_level,
        entity_id=data.entity_id,
        entity_type=data.entity_type,
        entity_name=data.entity_name,
        latitude=data.latitude,
        longitude=data.longitude,
        jurisdiction_codes=data.jurisdiction_codes,
        recommended_actions=data.recommended_actions,
        tags=data.tags,
    )
    return {"alert": vars(alert)}


@router.get("/alerts")
async def get_threat_alerts(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    category: Optional[str] = None,
    jurisdiction: Optional[str] = None,
    active_only: bool = True,
    limit: int = Query(default=100, le=500),
):
    """Get threat alerts"""
    stat = ThreatAlertStatus(status) if status else None
    pri = AlertPriority(priority) if priority else None
    cat = AlertCategory(category) if category else None
    alerts = alert_manager.get_all_alerts(
        status=stat,
        priority=pri,
        category=cat,
        jurisdiction=jurisdiction,
        active_only=active_only,
        limit=limit,
    )
    return {"alerts": [vars(a) for a in alerts]}


@router.get("/alerts/{alert_id}")
async def get_threat_alert(alert_id: str):
    """Get a threat alert by ID"""
    alert = alert_manager.get_alert(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return {"alert": vars(alert)}


@router.post("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(alert_id: str, user_id: str, user_name: str):
    """Acknowledge an alert"""
    success = alert_manager.acknowledge_alert(alert_id, user_id, user_name)
    if not success:
        raise HTTPException(status_code=404, detail="Alert not found")
    return {"success": True}


@router.post("/alerts/{alert_id}/escalate")
async def escalate_alert(
    alert_id: str,
    escalation_level: str,
    user_id: str,
    user_name: str,
    reason: str = "",
):
    """Escalate an alert"""
    level = EscalationLevel(escalation_level)
    success = alert_manager.escalate_alert(alert_id, level, user_id, user_name, reason)
    if not success:
        raise HTTPException(status_code=404, detail="Alert not found")
    return {"success": True}


@router.post("/alerts/{alert_id}/resolve")
async def resolve_alert(
    alert_id: str,
    user_id: str,
    user_name: str,
    resolution_notes: str = "",
    is_false_positive: bool = False,
):
    """Resolve an alert"""
    success = alert_manager.resolve_alert(
        alert_id, user_id, user_name, resolution_notes, is_false_positive
    )
    if not success:
        raise HTTPException(status_code=404, detail="Alert not found")
    return {"success": True}


@router.get("/alerts/destination/{destination}")
async def get_alerts_for_destination(
    destination: str,
    active_only: bool = True,
    limit: int = 50,
):
    """Get alerts for a specific destination"""
    dest = AlertDestination(destination)
    alerts = alert_manager.get_alerts_for_destination(dest, active_only=active_only, limit=limit)
    return {"alerts": [vars(a) for a in alerts]}


@router.post("/alerts/routing-rules")
async def create_routing_rule(data: RoutingRuleCreate):
    """Create a routing rule"""
    destinations = [AlertDestination(d) for d in data.destinations]
    categories = [AlertCategory(c) for c in data.categories] if data.categories else None
    min_priority = AlertPriority(data.min_priority) if data.min_priority else AlertPriority.P3_MODERATE
    rule = alert_manager.create_routing_rule(
        name=data.name,
        destinations=destinations,
        categories=categories,
        min_priority=min_priority,
        jurisdiction_codes=data.jurisdiction_codes,
        description=data.description,
        auto_escalate=data.auto_escalate,
        escalation_threshold_minutes=data.escalation_threshold_minutes,
    )
    return {"rule": vars(rule)}


@router.get("/alerts/routing-rules")
async def get_routing_rules():
    """Get all routing rules"""
    rules = alert_manager.get_all_routing_rules()
    return {"rules": [vars(r) for r in rules]}


@router.delete("/alerts/routing-rules/{rule_id}")
async def delete_routing_rule(rule_id: str):
    """Delete a routing rule"""
    success = alert_manager.delete_routing_rule(rule_id)
    if not success:
        raise HTTPException(status_code=404, detail="Rule not found")
    return {"success": True}


@router.post("/alerts/subscriptions")
async def create_subscription(data: SubscriptionCreate):
    """Create an alert subscription"""
    categories = [AlertCategory(c) for c in data.categories] if data.categories else None
    min_priority = AlertPriority(data.min_priority) if data.min_priority else AlertPriority.P3_MODERATE
    subscription = alert_manager.create_subscription(
        subscriber_id=data.subscriber_id,
        subscriber_type=data.subscriber_type,
        subscriber_name=data.subscriber_name,
        categories=categories,
        min_priority=min_priority,
        jurisdiction_codes=data.jurisdiction_codes,
        websocket_channel=data.websocket_channel,
        webhook_url=data.webhook_url,
        email=data.email,
    )
    return {"subscription": vars(subscription)}


@router.get("/alerts/subscriptions/{subscriber_id}")
async def get_subscriptions(subscriber_id: str):
    """Get subscriptions for a subscriber"""
    subscriptions = alert_manager.get_subscriptions_for_subscriber(subscriber_id)
    return {"subscriptions": [vars(s) for s in subscriptions]}


@router.delete("/alerts/subscriptions/{subscription_id}")
async def delete_subscription(subscription_id: str):
    """Delete a subscription"""
    success = alert_manager.delete_subscription(subscription_id)
    if not success:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return {"success": True}


@router.get("/alerts/audit/{alert_id}")
async def get_alert_audit_log(alert_id: str, limit: int = 100):
    """Get audit log for an alert"""
    entries = alert_manager.get_audit_log(alert_id=alert_id, limit=limit)
    return {"audit_entries": [vars(e) for e in entries]}


@router.get("/alerts/statistics")
async def get_alert_statistics():
    """Get alert statistics"""
    return alert_manager.get_alert_statistics()


@router.get("/alerts/metrics")
async def get_alert_metrics():
    """Get threat alert manager metrics"""
    return alert_manager.get_metrics()


@router.get("/metrics")
async def get_all_metrics():
    """Get metrics from all threat intel modules"""
    return {
        "dark_web": dark_web_monitor.get_metrics(),
        "osint": osint_harvester.get_metrics(),
        "extremist_networks": extremist_analyzer.get_metrics(),
        "global_incidents": incident_monitor.get_metrics(),
        "threat_scoring": scoring_engine.get_metrics(),
        "threat_alerts": alert_manager.get_metrics(),
    }
