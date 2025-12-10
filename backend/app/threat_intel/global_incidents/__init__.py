"""
Global Incidents Module

Provides capabilities for:
- NASA, USGS, DHS, Interpol feed stubs
- Global crisis map aggregation
- Geo-threat correlation engine
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Optional
import uuid
import math


class IncidentType(Enum):
    """Types of global incidents"""
    EARTHQUAKE = "earthquake"
    TSUNAMI = "tsunami"
    HURRICANE = "hurricane"
    TORNADO = "tornado"
    FLOOD = "flood"
    WILDFIRE = "wildfire"
    VOLCANIC_ERUPTION = "volcanic_eruption"
    LANDSLIDE = "landslide"
    TERRORIST_ATTACK = "terrorist_attack"
    MASS_SHOOTING = "mass_shooting"
    BOMBING = "bombing"
    HOSTAGE_SITUATION = "hostage_situation"
    CYBERATTACK = "cyberattack"
    INFRASTRUCTURE_FAILURE = "infrastructure_failure"
    CHEMICAL_SPILL = "chemical_spill"
    NUCLEAR_INCIDENT = "nuclear_incident"
    PANDEMIC = "pandemic"
    CIVIL_UNREST = "civil_unrest"
    COUP = "coup"
    WAR = "war"
    REFUGEE_CRISIS = "refugee_crisis"
    FAMINE = "famine"
    OTHER = "other"


class IncidentSeverity(Enum):
    """Severity levels for incidents"""
    MINOR = "minor"
    MODERATE = "moderate"
    SIGNIFICANT = "significant"
    SEVERE = "severe"
    CATASTROPHIC = "catastrophic"


class IncidentStatus(Enum):
    """Status of an incident"""
    REPORTED = "reported"
    CONFIRMED = "confirmed"
    ONGOING = "ongoing"
    CONTAINED = "contained"
    RESOLVED = "resolved"
    FALSE_ALARM = "false_alarm"


class FeedSource(Enum):
    """Sources of incident feeds"""
    NASA = "nasa"
    USGS = "usgs"
    NOAA = "noaa"
    DHS = "dhs"
    FBI = "fbi"
    INTERPOL = "interpol"
    EUROPOL = "europol"
    UN = "un"
    WHO = "who"
    CDC = "cdc"
    FEMA = "fema"
    NWS = "nws"
    GDACS = "gdacs"
    RSOE_EDIS = "rsoe_edis"
    CUSTOM = "custom"


class AlertLevel(Enum):
    """Alert levels for crisis alerts"""
    ADVISORY = "advisory"
    WATCH = "watch"
    WARNING = "warning"
    EMERGENCY = "emergency"
    CRITICAL = "critical"


class CorrelationType(Enum):
    """Types of geo-threat correlations"""
    PROXIMITY = "proximity"
    TEMPORAL = "temporal"
    CAUSAL = "causal"
    PATTERN = "pattern"
    CASCADING = "cascading"


@dataclass
class GlobalIncident:
    """A global incident from monitoring feeds"""
    incident_id: str = ""
    incident_type: IncidentType = IncidentType.OTHER
    title: str = ""
    description: str = ""
    severity: IncidentSeverity = IncidentSeverity.MODERATE
    status: IncidentStatus = IncidentStatus.REPORTED
    source: FeedSource = FeedSource.CUSTOM
    source_id: str = ""
    source_url: str = ""
    country: str = ""
    region: str = ""
    city: str = ""
    latitude: float = 0.0
    longitude: float = 0.0
    radius_km: float = 0.0
    affected_population: int = 0
    casualties: int = 0
    injuries: int = 0
    displaced: int = 0
    economic_impact_usd: float = 0.0
    started_at: datetime = field(default_factory=datetime.utcnow)
    reported_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None
    tags: list[str] = field(default_factory=list)
    related_incidents: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.incident_id:
            self.incident_id = f"incident-{uuid.uuid4().hex[:12]}"


@dataclass
class CrisisAlert:
    """A crisis alert for a region or jurisdiction"""
    alert_id: str = ""
    title: str = ""
    description: str = ""
    alert_level: AlertLevel = AlertLevel.ADVISORY
    incident_types: list[IncidentType] = field(default_factory=list)
    source_incidents: list[str] = field(default_factory=list)
    affected_countries: list[str] = field(default_factory=list)
    affected_regions: list[str] = field(default_factory=list)
    affected_jurisdictions: list[str] = field(default_factory=list)
    center_latitude: float = 0.0
    center_longitude: float = 0.0
    radius_km: float = 0.0
    recommended_actions: list[str] = field(default_factory=list)
    issued_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    is_active: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.alert_id:
            self.alert_id = f"alert-{uuid.uuid4().hex[:12]}"


@dataclass
class GeoThreatCorrelation:
    """A correlation between incidents and local threats"""
    correlation_id: str = ""
    correlation_type: CorrelationType = CorrelationType.PROXIMITY
    incident_ids: list[str] = field(default_factory=list)
    local_threat_ids: list[str] = field(default_factory=list)
    confidence_score: float = 0.0
    description: str = ""
    distance_km: float = 0.0
    time_delta_hours: float = 0.0
    risk_amplification: float = 1.0
    affected_jurisdictions: list[str] = field(default_factory=list)
    recommended_actions: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.correlation_id:
            self.correlation_id = f"corr-{uuid.uuid4().hex[:12]}"


@dataclass
class FeedConfiguration:
    """Configuration for an incident feed"""
    feed_id: str = ""
    source: FeedSource = FeedSource.CUSTOM
    name: str = ""
    endpoint_url: str = ""
    api_key: str = ""
    poll_interval_minutes: int = 5
    enabled: bool = True
    incident_types: list[IncidentType] = field(default_factory=list)
    geographic_filter: Optional[dict[str, Any]] = None
    last_polled: Optional[datetime] = None
    last_incident_id: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        if not self.feed_id:
            self.feed_id = f"feed-{uuid.uuid4().hex[:12]}"


class GlobalIncidentMonitor:
    """
    Global Incident Monitor for tracking worldwide incidents
    and correlating them with local threats.
    
    Note: External API integrations are stubbed for security.
    """

    def __init__(self):
        self._incidents: dict[str, GlobalIncident] = {}
        self._alerts: dict[str, CrisisAlert] = {}
        self._correlations: dict[str, GeoThreatCorrelation] = {}
        self._feeds: dict[str, FeedConfiguration] = {}
        self._callbacks: list[Callable[[Any], None]] = []
        self._events: list[dict[str, Any]] = []
        
        self._jurisdiction_coordinates: dict[str, tuple[float, float]] = {}

    def register_callback(self, callback: Callable[[Any], None]) -> None:
        """Register a callback for new incidents/alerts"""
        self._callbacks.append(callback)

    def _notify_callbacks(self, data: Any) -> None:
        """Notify all registered callbacks"""
        for callback in self._callbacks:
            try:
                callback(data)
            except Exception:
                pass

    def _record_event(self, event_type: str, data: dict[str, Any]) -> None:
        """Record an event for audit purposes"""
        self._events.append({
            "event_type": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data,
        })

    def configure_feed(
        self,
        source: FeedSource,
        name: str,
        endpoint_url: str = "",
        api_key: str = "",
        poll_interval_minutes: int = 5,
        incident_types: Optional[list[IncidentType]] = None,
    ) -> FeedConfiguration:
        """Configure an incident feed"""
        feed = FeedConfiguration(
            source=source,
            name=name,
            endpoint_url=endpoint_url,
            api_key=api_key,
            poll_interval_minutes=poll_interval_minutes,
            incident_types=incident_types or [],
        )
        self._feeds[feed.feed_id] = feed
        self._record_event("feed_configured", {"feed_id": feed.feed_id})
        return feed

    def get_feed(self, feed_id: str) -> Optional[FeedConfiguration]:
        """Get a feed configuration by ID"""
        return self._feeds.get(feed_id)

    def get_all_feeds(self) -> list[FeedConfiguration]:
        """Get all feed configurations"""
        return list(self._feeds.values())

    def enable_feed(self, feed_id: str) -> bool:
        """Enable a feed"""
        feed = self._feeds.get(feed_id)
        if feed:
            feed.enabled = True
            return True
        return False

    def disable_feed(self, feed_id: str) -> bool:
        """Disable a feed"""
        feed = self._feeds.get(feed_id)
        if feed:
            feed.enabled = False
            return True
        return False

    def register_jurisdiction(
        self,
        jurisdiction_code: str,
        latitude: float,
        longitude: float,
    ) -> None:
        """Register a jurisdiction's coordinates for correlation"""
        self._jurisdiction_coordinates[jurisdiction_code] = (latitude, longitude)

    def ingest_incident(
        self,
        incident_type: IncidentType,
        title: str,
        description: str,
        latitude: float,
        longitude: float,
        severity: IncidentSeverity = IncidentSeverity.MODERATE,
        source: FeedSource = FeedSource.CUSTOM,
        source_id: str = "",
        country: str = "",
        region: str = "",
        city: str = "",
        radius_km: float = 0.0,
        affected_population: int = 0,
        casualties: int = 0,
        injuries: int = 0,
        started_at: Optional[datetime] = None,
    ) -> GlobalIncident:
        """Ingest a new global incident"""
        incident = GlobalIncident(
            incident_type=incident_type,
            title=title,
            description=description,
            severity=severity,
            source=source,
            source_id=source_id,
            country=country,
            region=region,
            city=city,
            latitude=latitude,
            longitude=longitude,
            radius_km=radius_km,
            affected_population=affected_population,
            casualties=casualties,
            injuries=injuries,
            started_at=started_at or datetime.utcnow(),
        )
        
        self._incidents[incident.incident_id] = incident
        self._record_event("incident_ingested", {
            "incident_id": incident.incident_id,
            "type": incident_type.value,
        })
        self._notify_callbacks({"type": "incident", "data": incident})
        
        self._check_for_correlations(incident)
        
        return incident

    def get_incident(self, incident_id: str) -> Optional[GlobalIncident]:
        """Get an incident by ID"""
        return self._incidents.get(incident_id)

    def get_all_incidents(
        self,
        incident_type: Optional[IncidentType] = None,
        severity: Optional[IncidentSeverity] = None,
        status: Optional[IncidentStatus] = None,
        source: Optional[FeedSource] = None,
        country: Optional[str] = None,
        since: Optional[datetime] = None,
        limit: int = 100,
    ) -> list[GlobalIncident]:
        """Get all incidents with optional filtering"""
        incidents = list(self._incidents.values())
        
        if incident_type:
            incidents = [i for i in incidents if i.incident_type == incident_type]
        if severity:
            incidents = [i for i in incidents if i.severity == severity]
        if status:
            incidents = [i for i in incidents if i.status == status]
        if source:
            incidents = [i for i in incidents if i.source == source]
        if country:
            incidents = [i for i in incidents if i.country.lower() == country.lower()]
        if since:
            incidents = [i for i in incidents if i.reported_at >= since]
        
        incidents.sort(key=lambda i: i.reported_at, reverse=True)
        return incidents[:limit]

    def get_incidents_near_location(
        self,
        latitude: float,
        longitude: float,
        radius_km: float = 100,
        limit: int = 50,
    ) -> list[GlobalIncident]:
        """Get incidents near a specific location"""
        nearby = []
        for incident in self._incidents.values():
            distance = self._calculate_distance(
                latitude, longitude,
                incident.latitude, incident.longitude
            )
            if distance <= radius_km:
                nearby.append((incident, distance))
        
        nearby.sort(key=lambda x: x[1])
        return [i for i, _ in nearby[:limit]]

    def _calculate_distance(
        self,
        lat1: float, lon1: float,
        lat2: float, lon2: float,
    ) -> float:
        """Calculate distance between two points in km (Haversine formula)"""
        R = 6371
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = (math.sin(delta_lat / 2) ** 2 +
             math.cos(lat1_rad) * math.cos(lat2_rad) *
             math.sin(delta_lon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c

    def update_incident_status(
        self,
        incident_id: str,
        status: IncidentStatus,
        casualties: Optional[int] = None,
        injuries: Optional[int] = None,
    ) -> bool:
        """Update an incident's status"""
        incident = self._incidents.get(incident_id)
        if not incident:
            return False
        
        incident.status = status
        incident.updated_at = datetime.utcnow()
        
        if casualties is not None:
            incident.casualties = casualties
        if injuries is not None:
            incident.injuries = injuries
        
        if status == IncidentStatus.RESOLVED:
            incident.resolved_at = datetime.utcnow()
        
        self._record_event("incident_updated", {
            "incident_id": incident_id,
            "status": status.value,
        })
        return True

    def create_crisis_alert(
        self,
        title: str,
        description: str,
        alert_level: AlertLevel,
        incident_ids: list[str],
        affected_jurisdictions: Optional[list[str]] = None,
        center_latitude: float = 0.0,
        center_longitude: float = 0.0,
        radius_km: float = 0.0,
        recommended_actions: Optional[list[str]] = None,
        expires_in_hours: int = 24,
    ) -> CrisisAlert:
        """Create a crisis alert"""
        incident_types = []
        affected_countries = set()
        affected_regions = set()
        
        for inc_id in incident_ids:
            incident = self._incidents.get(inc_id)
            if incident:
                if incident.incident_type not in incident_types:
                    incident_types.append(incident.incident_type)
                if incident.country:
                    affected_countries.add(incident.country)
                if incident.region:
                    affected_regions.add(incident.region)
        
        alert = CrisisAlert(
            title=title,
            description=description,
            alert_level=alert_level,
            incident_types=incident_types,
            source_incidents=incident_ids,
            affected_countries=list(affected_countries),
            affected_regions=list(affected_regions),
            affected_jurisdictions=affected_jurisdictions or [],
            center_latitude=center_latitude,
            center_longitude=center_longitude,
            radius_km=radius_km,
            recommended_actions=recommended_actions or [],
            expires_at=datetime.utcnow() + timedelta(hours=expires_in_hours),
        )
        
        self._alerts[alert.alert_id] = alert
        self._record_event("crisis_alert_created", {
            "alert_id": alert.alert_id,
            "level": alert_level.value,
        })
        self._notify_callbacks({"type": "alert", "data": alert})
        
        return alert

    def get_alert(self, alert_id: str) -> Optional[CrisisAlert]:
        """Get an alert by ID"""
        return self._alerts.get(alert_id)

    def get_all_alerts(
        self,
        alert_level: Optional[AlertLevel] = None,
        active_only: bool = True,
        limit: int = 50,
    ) -> list[CrisisAlert]:
        """Get all alerts with optional filtering"""
        alerts = list(self._alerts.values())
        
        if alert_level:
            alerts = [a for a in alerts if a.alert_level == alert_level]
        if active_only:
            now = datetime.utcnow()
            alerts = [
                a for a in alerts
                if a.is_active and (not a.expires_at or a.expires_at > now)
            ]
        
        alerts.sort(key=lambda a: a.issued_at, reverse=True)
        return alerts[:limit]

    def get_alerts_for_jurisdiction(
        self,
        jurisdiction_code: str,
    ) -> list[CrisisAlert]:
        """Get alerts affecting a specific jurisdiction"""
        alerts = []
        for alert in self._alerts.values():
            if not alert.is_active:
                continue
            if alert.expires_at and alert.expires_at < datetime.utcnow():
                continue
            if jurisdiction_code in alert.affected_jurisdictions:
                alerts.append(alert)
                continue
            
            if jurisdiction_code in self._jurisdiction_coordinates:
                lat, lon = self._jurisdiction_coordinates[jurisdiction_code]
                if alert.center_latitude and alert.center_longitude and alert.radius_km:
                    distance = self._calculate_distance(
                        lat, lon,
                        alert.center_latitude, alert.center_longitude
                    )
                    if distance <= alert.radius_km:
                        alerts.append(alert)
        
        return alerts

    def deactivate_alert(self, alert_id: str) -> bool:
        """Deactivate an alert"""
        alert = self._alerts.get(alert_id)
        if alert:
            alert.is_active = False
            self._record_event("alert_deactivated", {"alert_id": alert_id})
            return True
        return False

    def _check_for_correlations(self, incident: GlobalIncident) -> None:
        """Check for correlations between new incident and local threats"""
        for jur_code, (lat, lon) in self._jurisdiction_coordinates.items():
            distance = self._calculate_distance(
                lat, lon,
                incident.latitude, incident.longitude
            )
            
            if distance <= 500:
                risk_amp = 1.0
                if distance <= 50:
                    risk_amp = 2.0
                elif distance <= 100:
                    risk_amp = 1.5
                elif distance <= 250:
                    risk_amp = 1.25
                
                if incident.severity in [IncidentSeverity.SEVERE, IncidentSeverity.CATASTROPHIC]:
                    risk_amp *= 1.5
                
                correlation = GeoThreatCorrelation(
                    correlation_type=CorrelationType.PROXIMITY,
                    incident_ids=[incident.incident_id],
                    confidence_score=max(0.5, 1.0 - (distance / 500)),
                    description=f"Incident within {distance:.0f}km of {jur_code}",
                    distance_km=distance,
                    risk_amplification=risk_amp,
                    affected_jurisdictions=[jur_code],
                )
                
                self._correlations[correlation.correlation_id] = correlation
                self._record_event("correlation_detected", {
                    "correlation_id": correlation.correlation_id,
                    "incident_id": incident.incident_id,
                    "jurisdiction": jur_code,
                })

    def create_correlation(
        self,
        correlation_type: CorrelationType,
        incident_ids: list[str],
        local_threat_ids: Optional[list[str]] = None,
        confidence_score: float = 0.5,
        description: str = "",
        affected_jurisdictions: Optional[list[str]] = None,
        risk_amplification: float = 1.0,
    ) -> GeoThreatCorrelation:
        """Manually create a correlation"""
        correlation = GeoThreatCorrelation(
            correlation_type=correlation_type,
            incident_ids=incident_ids,
            local_threat_ids=local_threat_ids or [],
            confidence_score=confidence_score,
            description=description,
            affected_jurisdictions=affected_jurisdictions or [],
            risk_amplification=risk_amplification,
        )
        
        self._correlations[correlation.correlation_id] = correlation
        self._record_event("correlation_created", {
            "correlation_id": correlation.correlation_id,
        })
        
        return correlation

    def get_correlation(self, correlation_id: str) -> Optional[GeoThreatCorrelation]:
        """Get a correlation by ID"""
        return self._correlations.get(correlation_id)

    def get_all_correlations(
        self,
        correlation_type: Optional[CorrelationType] = None,
        jurisdiction: Optional[str] = None,
        min_confidence: float = 0.0,
        limit: int = 100,
    ) -> list[GeoThreatCorrelation]:
        """Get all correlations with optional filtering"""
        correlations = list(self._correlations.values())
        
        if correlation_type:
            correlations = [c for c in correlations if c.correlation_type == correlation_type]
        if jurisdiction:
            correlations = [
                c for c in correlations
                if jurisdiction in c.affected_jurisdictions
            ]
        if min_confidence > 0:
            correlations = [c for c in correlations if c.confidence_score >= min_confidence]
        
        correlations.sort(key=lambda c: c.confidence_score, reverse=True)
        return correlations[:limit]

    def get_crisis_map_data(
        self,
        bounds: Optional[dict[str, float]] = None,
    ) -> dict[str, Any]:
        """Get data for crisis map visualization"""
        incidents = list(self._incidents.values())
        
        if bounds:
            incidents = [
                i for i in incidents
                if (bounds.get("south", -90) <= i.latitude <= bounds.get("north", 90) and
                    bounds.get("west", -180) <= i.longitude <= bounds.get("east", 180))
            ]
        
        incident_data = []
        for incident in incidents:
            incident_data.append({
                "id": incident.incident_id,
                "type": incident.incident_type.value,
                "title": incident.title,
                "severity": incident.severity.value,
                "status": incident.status.value,
                "latitude": incident.latitude,
                "longitude": incident.longitude,
                "radius_km": incident.radius_km,
                "reported_at": incident.reported_at.isoformat(),
            })
        
        alert_data = []
        for alert in self._alerts.values():
            if alert.is_active:
                alert_data.append({
                    "id": alert.alert_id,
                    "title": alert.title,
                    "level": alert.alert_level.value,
                    "latitude": alert.center_latitude,
                    "longitude": alert.center_longitude,
                    "radius_km": alert.radius_km,
                    "issued_at": alert.issued_at.isoformat(),
                })
        
        return {
            "incidents": incident_data,
            "alerts": alert_data,
            "total_incidents": len(incidents),
            "total_active_alerts": len(alert_data),
        }

    def simulate_feed_poll(self, feed_id: str) -> list[GlobalIncident]:
        """Simulate polling a feed (stub for testing)"""
        feed = self._feeds.get(feed_id)
        if not feed or not feed.enabled:
            return []
        
        feed.last_polled = datetime.utcnow()
        self._record_event("feed_polled", {"feed_id": feed_id})
        
        return []

    def get_metrics(self) -> dict[str, Any]:
        """Get global incident monitor metrics"""
        incidents = list(self._incidents.values())
        alerts = list(self._alerts.values())
        
        type_counts = {}
        for inc_type in IncidentType:
            type_counts[inc_type.value] = len([
                i for i in incidents if i.incident_type == inc_type
            ])
        
        severity_counts = {}
        for severity in IncidentSeverity:
            severity_counts[severity.value] = len([
                i for i in incidents if i.severity == severity
            ])
        
        status_counts = {}
        for status in IncidentStatus:
            status_counts[status.value] = len([
                i for i in incidents if i.status == status
            ])
        
        source_counts = {}
        for source in FeedSource:
            source_counts[source.value] = len([
                i for i in incidents if i.source == source
            ])
        
        return {
            "total_incidents": len(incidents),
            "total_alerts": len(alerts),
            "total_correlations": len(self._correlations),
            "total_feeds": len(self._feeds),
            "active_feeds": len([f for f in self._feeds.values() if f.enabled]),
            "incidents_by_type": type_counts,
            "incidents_by_severity": severity_counts,
            "incidents_by_status": status_counts,
            "incidents_by_source": source_counts,
            "active_alerts": len([a for a in alerts if a.is_active]),
            "total_casualties": sum(i.casualties for i in incidents),
            "total_injuries": sum(i.injuries for i in incidents),
            "registered_jurisdictions": len(self._jurisdiction_coordinates),
            "total_events": len(self._events),
        }
