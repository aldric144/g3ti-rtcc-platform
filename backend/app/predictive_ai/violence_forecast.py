"""
Violence Cluster Forecasting Engine.

Predicts violence clusters and trends based on historical data and patterns.
"""

import uuid
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Callable, Optional
from collections import deque
from pydantic import BaseModel, Field


class ClusterType(str, Enum):
    """Types of violence clusters."""
    GANG_RELATED = "gang_related"
    DOMESTIC = "domestic"
    ROBBERY = "robbery"
    ASSAULT = "assault"
    SHOOTING = "shooting"
    STABBING = "stabbing"
    DRUG_RELATED = "drug_related"
    SCHOOL_RELATED = "school_related"
    RANDOM = "random"
    UNKNOWN = "unknown"


class TrendDirection(str, Enum):
    """Direction of violence trends."""
    DECREASING_FAST = "decreasing_fast"
    DECREASING = "decreasing"
    STABLE = "stable"
    INCREASING = "increasing"
    INCREASING_FAST = "increasing_fast"


class RiskLevel(str, Enum):
    """Risk levels for clusters."""
    MINIMAL = "minimal"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


class ViolenceIncident(BaseModel):
    """Violence incident for analysis."""
    incident_id: str
    incident_type: str
    cluster_type: ClusterType = ClusterType.UNKNOWN
    latitude: float
    longitude: float
    timestamp: datetime
    severity: int = 1
    victims: int = 0
    suspects: int = 0
    weapon_used: Optional[str] = None
    gang_related: bool = False
    domestic: bool = False
    resolved: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)


class ViolenceCluster(BaseModel):
    """Identified violence cluster."""
    cluster_id: str
    cluster_type: ClusterType
    center_lat: float
    center_lon: float
    radius_m: float = 500.0
    incident_count: int = 0
    incidents: list[str] = Field(default_factory=list)
    first_incident: Optional[datetime] = None
    last_incident: Optional[datetime] = None
    avg_severity: float = 0.0
    total_victims: int = 0
    risk_level: RiskLevel = RiskLevel.LOW
    trend: TrendDirection = TrendDirection.STABLE
    active: bool = True
    predicted_next_incident: Optional[datetime] = None
    confidence: float = 0.0
    contributing_factors: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = Field(default_factory=dict)


class ClusterPrediction(BaseModel):
    """Prediction for a violence cluster."""
    prediction_id: str
    cluster_id: Optional[str] = None
    latitude: float
    longitude: float
    radius_m: float = 500.0
    predicted_type: ClusterType
    predicted_time_start: datetime
    predicted_time_end: datetime
    probability: float
    confidence: float
    risk_level: RiskLevel
    factors: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    verified: bool = False
    verified_at: Optional[datetime] = None
    actual_incidents: int = 0
    metadata: dict[str, Any] = Field(default_factory=dict)


class TrendAnalysis(BaseModel):
    """Trend analysis for violence patterns."""
    analysis_id: str
    period_start: datetime
    period_end: datetime
    total_incidents: int = 0
    incidents_by_type: dict[str, int] = Field(default_factory=dict)
    incidents_by_day: dict[str, int] = Field(default_factory=dict)
    incidents_by_hour: dict[int, int] = Field(default_factory=dict)
    hotspots: list[dict[str, Any]] = Field(default_factory=list)
    trend_direction: TrendDirection = TrendDirection.STABLE
    change_percent: float = 0.0
    peak_hours: list[int] = Field(default_factory=list)
    peak_days: list[str] = Field(default_factory=list)
    avg_daily_incidents: float = 0.0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = Field(default_factory=dict)


class ForecastConfig(BaseModel):
    """Configuration for violence forecast engine."""
    cluster_radius_m: float = 500.0
    min_incidents_for_cluster: int = 3
    cluster_time_window_days: int = 30
    prediction_horizon_hours: int = 72
    max_clusters: int = 1000
    max_incidents: int = 100000
    max_predictions: int = 10000


class ForecastMetrics(BaseModel):
    """Metrics for violence forecast engine."""
    total_incidents: int = 0
    incidents_by_type: dict[str, int] = Field(default_factory=dict)
    total_clusters: int = 0
    active_clusters: int = 0
    clusters_by_type: dict[str, int] = Field(default_factory=dict)
    total_predictions: int = 0
    prediction_accuracy: float = 0.0


class ViolenceForecastEngine:
    """
    Violence Cluster Forecasting Engine.
    
    Predicts violence clusters and trends based on historical data and patterns.
    """
    
    def __init__(self, config: Optional[ForecastConfig] = None):
        self.config = config or ForecastConfig()
        self._incidents: deque[ViolenceIncident] = deque(maxlen=self.config.max_incidents)
        self._clusters: dict[str, ViolenceCluster] = {}
        self._predictions: deque[ClusterPrediction] = deque(maxlen=self.config.max_predictions)
        self._callbacks: list[Callable] = []
        self._running = False
        self._metrics = ForecastMetrics()
    
    async def start(self) -> None:
        """Start the violence forecast engine."""
        self._running = True
    
    async def stop(self) -> None:
        """Stop the violence forecast engine."""
        self._running = False
    
    async def ingest_incident(
        self,
        incident_id: str,
        incident_type: str,
        latitude: float,
        longitude: float,
        timestamp: Optional[datetime] = None,
        severity: int = 1,
        victims: int = 0,
        suspects: int = 0,
        weapon_used: Optional[str] = None,
        gang_related: bool = False,
        domestic: bool = False,
        metadata: Optional[dict[str, Any]] = None,
    ) -> ViolenceIncident:
        """Ingest a violence incident for analysis."""
        cluster_type = self._classify_incident(
            incident_type, gang_related, domestic, weapon_used,
        )
        
        incident = ViolenceIncident(
            incident_id=incident_id,
            incident_type=incident_type,
            cluster_type=cluster_type,
            latitude=latitude,
            longitude=longitude,
            timestamp=timestamp or datetime.now(timezone.utc),
            severity=severity,
            victims=victims,
            suspects=suspects,
            weapon_used=weapon_used,
            gang_related=gang_related,
            domestic=domestic,
            metadata=metadata or {},
        )
        
        self._incidents.append(incident)
        
        await self._update_clusters(incident)
        self._update_metrics()
        
        await self._notify_callbacks(incident, "incident_ingested")
        
        return incident
    
    def _classify_incident(
        self,
        incident_type: str,
        gang_related: bool,
        domestic: bool,
        weapon_used: Optional[str],
    ) -> ClusterType:
        """Classify an incident into a cluster type."""
        if gang_related:
            return ClusterType.GANG_RELATED
        if domestic:
            return ClusterType.DOMESTIC
        
        incident_lower = incident_type.lower()
        
        if "shooting" in incident_lower or weapon_used and "gun" in weapon_used.lower():
            return ClusterType.SHOOTING
        if "stab" in incident_lower or weapon_used and "knife" in weapon_used.lower():
            return ClusterType.STABBING
        if "robbery" in incident_lower:
            return ClusterType.ROBBERY
        if "assault" in incident_lower:
            return ClusterType.ASSAULT
        if "drug" in incident_lower:
            return ClusterType.DRUG_RELATED
        if "school" in incident_lower:
            return ClusterType.SCHOOL_RELATED
        
        return ClusterType.UNKNOWN
    
    async def _update_clusters(self, incident: ViolenceIncident) -> None:
        """Update clusters based on new incident."""
        assigned = False
        
        for cluster in self._clusters.values():
            if not cluster.active:
                continue
            
            distance = self._calculate_distance(
                incident.latitude, incident.longitude,
                cluster.center_lat, cluster.center_lon,
            ) * 1000
            
            if distance <= cluster.radius_m:
                cluster.incidents.append(incident.incident_id)
                cluster.incident_count += 1
                cluster.last_incident = incident.timestamp
                cluster.total_victims += incident.victims
                
                cluster.avg_severity = (
                    (cluster.avg_severity * (cluster.incident_count - 1) + incident.severity)
                    / cluster.incident_count
                )
                
                cluster.updated_at = datetime.now(timezone.utc)
                self._update_cluster_risk(cluster)
                
                assigned = True
                break
        
        if not assigned:
            nearby_incidents = self._get_nearby_incidents(
                incident.latitude, incident.longitude,
                self.config.cluster_radius_m,
                self.config.cluster_time_window_days,
            )
            
            if len(nearby_incidents) >= self.config.min_incidents_for_cluster - 1:
                await self._create_cluster(incident, nearby_incidents)
    
    async def _create_cluster(
        self,
        incident: ViolenceIncident,
        nearby_incidents: list[ViolenceIncident],
    ) -> ViolenceCluster:
        """Create a new violence cluster."""
        all_incidents = nearby_incidents + [incident]
        
        center_lat = sum(i.latitude for i in all_incidents) / len(all_incidents)
        center_lon = sum(i.longitude for i in all_incidents) / len(all_incidents)
        
        type_counts: dict[ClusterType, int] = {}
        for i in all_incidents:
            type_counts[i.cluster_type] = type_counts.get(i.cluster_type, 0) + 1
        
        dominant_type = max(type_counts, key=lambda t: type_counts[t])
        
        cluster = ViolenceCluster(
            cluster_id=f"cluster-{uuid.uuid4().hex[:12]}",
            cluster_type=dominant_type,
            center_lat=center_lat,
            center_lon=center_lon,
            radius_m=self.config.cluster_radius_m,
            incident_count=len(all_incidents),
            incidents=[i.incident_id for i in all_incidents],
            first_incident=min(i.timestamp for i in all_incidents),
            last_incident=max(i.timestamp for i in all_incidents),
            avg_severity=sum(i.severity for i in all_incidents) / len(all_incidents),
            total_victims=sum(i.victims for i in all_incidents),
        )
        
        self._update_cluster_risk(cluster)
        self._clusters[cluster.cluster_id] = cluster
        
        await self._notify_callbacks(cluster, "cluster_created")
        
        return cluster
    
    def _update_cluster_risk(self, cluster: ViolenceCluster) -> None:
        """Update risk level for a cluster."""
        score = 0.0
        
        score += min(cluster.incident_count / 10, 1.0) * 0.3
        score += min(cluster.avg_severity / 5, 1.0) * 0.3
        score += min(cluster.total_victims / 10, 1.0) * 0.2
        
        if cluster.last_incident:
            days_since = (datetime.now(timezone.utc) - cluster.last_incident).days
            recency_score = max(0, 1 - days_since / 30)
            score += recency_score * 0.2
        
        if score >= 0.8:
            cluster.risk_level = RiskLevel.CRITICAL
        elif score >= 0.6:
            cluster.risk_level = RiskLevel.HIGH
        elif score >= 0.4:
            cluster.risk_level = RiskLevel.MODERATE
        elif score >= 0.2:
            cluster.risk_level = RiskLevel.LOW
        else:
            cluster.risk_level = RiskLevel.MINIMAL
        
        cluster.confidence = min(cluster.incident_count / 10, 1.0)
    
    def _get_nearby_incidents(
        self,
        latitude: float,
        longitude: float,
        radius_m: float,
        days: int,
    ) -> list[ViolenceIncident]:
        """Get incidents near a location within a time window."""
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        
        nearby = []
        for incident in self._incidents:
            if incident.timestamp < cutoff:
                continue
            
            distance = self._calculate_distance(
                latitude, longitude,
                incident.latitude, incident.longitude,
            ) * 1000
            
            if distance <= radius_m:
                nearby.append(incident)
        
        return nearby
    
    def get_cluster(self, cluster_id: str) -> Optional[ViolenceCluster]:
        """Get a cluster by ID."""
        return self._clusters.get(cluster_id)
    
    def get_all_clusters(self) -> list[ViolenceCluster]:
        """Get all clusters."""
        return list(self._clusters.values())
    
    def get_active_clusters(self) -> list[ViolenceCluster]:
        """Get all active clusters."""
        return [c for c in self._clusters.values() if c.active]
    
    def get_clusters_by_type(self, cluster_type: ClusterType) -> list[ViolenceCluster]:
        """Get clusters by type."""
        return [c for c in self._clusters.values() if c.cluster_type == cluster_type]
    
    def get_clusters_by_risk(self, risk_level: RiskLevel) -> list[ViolenceCluster]:
        """Get clusters by risk level."""
        return [c for c in self._clusters.values() if c.risk_level == risk_level]
    
    def get_high_risk_clusters(self) -> list[ViolenceCluster]:
        """Get all high-risk clusters."""
        return [
            c for c in self._clusters.values()
            if c.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL] and c.active
        ]
    
    def get_clusters_in_area(
        self,
        center_lat: float,
        center_lon: float,
        radius_km: float,
    ) -> list[ViolenceCluster]:
        """Get clusters within a geographic area."""
        result = []
        for cluster in self._clusters.values():
            distance = self._calculate_distance(
                center_lat, center_lon,
                cluster.center_lat, cluster.center_lon,
            )
            if distance <= radius_km:
                result.append(cluster)
        return result
    
    async def generate_predictions(
        self,
        hours_ahead: Optional[int] = None,
    ) -> list[ClusterPrediction]:
        """Generate predictions for violence clusters."""
        horizon = hours_ahead or self.config.prediction_horizon_hours
        now = datetime.now(timezone.utc)
        
        predictions = []
        
        for cluster in self._clusters.values():
            if not cluster.active or cluster.incident_count < self.config.min_incidents_for_cluster:
                continue
            
            probability = self._calculate_prediction_probability(cluster)
            
            if probability < 0.3:
                continue
            
            prediction = ClusterPrediction(
                prediction_id=f"pred-{uuid.uuid4().hex[:12]}",
                cluster_id=cluster.cluster_id,
                latitude=cluster.center_lat,
                longitude=cluster.center_lon,
                radius_m=cluster.radius_m,
                predicted_type=cluster.cluster_type,
                predicted_time_start=now,
                predicted_time_end=now + timedelta(hours=horizon),
                probability=probability,
                confidence=cluster.confidence,
                risk_level=cluster.risk_level,
                factors=cluster.contributing_factors,
                recommendations=self._generate_recommendations(cluster),
            )
            
            predictions.append(prediction)
            self._predictions.append(prediction)
        
        self._update_metrics()
        
        return predictions
    
    def _calculate_prediction_probability(self, cluster: ViolenceCluster) -> float:
        """Calculate probability of future incident in cluster."""
        if not cluster.last_incident:
            return 0.0
        
        days_since = (datetime.now(timezone.utc) - cluster.last_incident).days
        
        base_prob = min(cluster.incident_count / 20, 0.5)
        
        recency_factor = max(0, 1 - days_since / 14)
        
        severity_factor = min(cluster.avg_severity / 5, 1.0) * 0.2
        
        probability = base_prob + recency_factor * 0.3 + severity_factor
        
        return min(probability, 1.0)
    
    def _generate_recommendations(self, cluster: ViolenceCluster) -> list[str]:
        """Generate recommendations for a cluster."""
        recommendations = []
        
        if cluster.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            recommendations.append("Increase patrol presence in the area")
            recommendations.append("Deploy surveillance resources")
        
        if cluster.cluster_type == ClusterType.GANG_RELATED:
            recommendations.append("Coordinate with gang intelligence unit")
            recommendations.append("Monitor known gang members in area")
        
        if cluster.cluster_type == ClusterType.DOMESTIC:
            recommendations.append("Coordinate with domestic violence unit")
            recommendations.append("Review recent domestic calls in area")
        
        if cluster.cluster_type == ClusterType.SHOOTING:
            recommendations.append("Deploy ShotSpotter resources if available")
            recommendations.append("Coordinate with tactical unit")
        
        if cluster.incident_count >= 5:
            recommendations.append("Consider establishing a command post")
        
        return recommendations
    
    def analyze_trends(
        self,
        days: int = 30,
    ) -> TrendAnalysis:
        """Analyze violence trends over a period."""
        now = datetime.now(timezone.utc)
        start = now - timedelta(days=days)
        
        incidents_in_period = [
            i for i in self._incidents
            if start <= i.timestamp <= now
        ]
        
        by_type: dict[str, int] = {}
        by_day: dict[str, int] = {}
        by_hour: dict[int, int] = {}
        
        for incident in incidents_in_period:
            by_type[incident.cluster_type.value] = by_type.get(incident.cluster_type.value, 0) + 1
            
            day_key = incident.timestamp.strftime("%A")
            by_day[day_key] = by_day.get(day_key, 0) + 1
            
            hour = incident.timestamp.hour
            by_hour[hour] = by_hour.get(hour, 0) + 1
        
        mid_point = start + timedelta(days=days // 2)
        first_half = len([i for i in incidents_in_period if i.timestamp < mid_point])
        second_half = len([i for i in incidents_in_period if i.timestamp >= mid_point])
        
        if first_half > 0:
            change = ((second_half - first_half) / first_half) * 100
        else:
            change = 0.0
        
        if change <= -20:
            trend = TrendDirection.DECREASING_FAST
        elif change <= -5:
            trend = TrendDirection.DECREASING
        elif change >= 20:
            trend = TrendDirection.INCREASING_FAST
        elif change >= 5:
            trend = TrendDirection.INCREASING
        else:
            trend = TrendDirection.STABLE
        
        peak_hours = sorted(by_hour.keys(), key=lambda h: by_hour[h], reverse=True)[:3]
        peak_days = sorted(by_day.keys(), key=lambda d: by_day[d], reverse=True)[:3]
        
        analysis = TrendAnalysis(
            analysis_id=f"trend-{uuid.uuid4().hex[:8]}",
            period_start=start,
            period_end=now,
            total_incidents=len(incidents_in_period),
            incidents_by_type=by_type,
            incidents_by_day=by_day,
            incidents_by_hour=by_hour,
            trend_direction=trend,
            change_percent=change,
            peak_hours=peak_hours,
            peak_days=peak_days,
            avg_daily_incidents=len(incidents_in_period) / days if days > 0 else 0,
        )
        
        return analysis
    
    def get_recent_predictions(self, limit: int = 100) -> list[ClusterPrediction]:
        """Get recent predictions."""
        predictions = list(self._predictions)
        predictions.reverse()
        return predictions[:limit]
    
    def verify_prediction(
        self,
        prediction_id: str,
        actual_incidents: int,
    ) -> bool:
        """Verify a prediction with actual results."""
        for prediction in self._predictions:
            if prediction.prediction_id == prediction_id:
                prediction.verified = True
                prediction.verified_at = datetime.now(timezone.utc)
                prediction.actual_incidents = actual_incidents
                return True
        return False
    
    def deactivate_cluster(self, cluster_id: str) -> bool:
        """Deactivate a cluster."""
        cluster = self._clusters.get(cluster_id)
        if not cluster:
            return False
        
        cluster.active = False
        cluster.updated_at = datetime.now(timezone.utc)
        self._update_metrics()
        return True
    
    def get_metrics(self) -> ForecastMetrics:
        """Get forecast metrics."""
        return self._metrics
    
    def get_status(self) -> dict[str, Any]:
        """Get engine status."""
        return {
            "running": self._running,
            "total_incidents": len(self._incidents),
            "total_clusters": len(self._clusters),
            "active_clusters": len([c for c in self._clusters.values() if c.active]),
            "metrics": self._metrics.model_dump(),
        }
    
    def register_callback(self, callback: Callable) -> None:
        """Register a callback for forecast events."""
        if callback not in self._callbacks:
            self._callbacks.append(callback)
    
    def unregister_callback(self, callback: Callable) -> None:
        """Unregister a callback."""
        if callback in self._callbacks:
            self._callbacks.remove(callback)
    
    def _update_metrics(self) -> None:
        """Update forecast metrics."""
        incident_counts: dict[str, int] = {}
        for incident in self._incidents:
            incident_counts[incident.cluster_type.value] = incident_counts.get(incident.cluster_type.value, 0) + 1
        
        cluster_counts: dict[str, int] = {}
        active = 0
        for cluster in self._clusters.values():
            cluster_counts[cluster.cluster_type.value] = cluster_counts.get(cluster.cluster_type.value, 0) + 1
            if cluster.active:
                active += 1
        
        verified = [p for p in self._predictions if p.verified]
        if verified:
            accurate = len([p for p in verified if p.actual_incidents > 0])
            accuracy = accurate / len(verified)
        else:
            accuracy = 0.0
        
        self._metrics.total_incidents = len(self._incidents)
        self._metrics.incidents_by_type = incident_counts
        self._metrics.total_clusters = len(self._clusters)
        self._metrics.active_clusters = active
        self._metrics.clusters_by_type = cluster_counts
        self._metrics.total_predictions = len(self._predictions)
        self._metrics.prediction_accuracy = accuracy
    
    async def _notify_callbacks(self, data: Any, event_type: str) -> None:
        """Notify registered callbacks."""
        for callback in self._callbacks:
            try:
                if callable(callback):
                    result = callback(data, event_type)
                    if hasattr(result, "__await__"):
                        await result
            except Exception:
                pass
    
    @staticmethod
    def _calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points in kilometers."""
        import math
        
        R = 6371.0
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = (
            math.sin(delta_lat / 2) ** 2
            + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
