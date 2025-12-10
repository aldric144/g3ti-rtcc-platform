"""
FederatedAnalyticsEngine - Multi-city analytics for G3TI Fusion Cloud

Manages:
- Multi-city crime heatmaps
- Cross-city offender trajectory predictions
- Regional crime clusters
- Real-time risk overlays
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
import uuid
import math


class HeatmapType(str, Enum):
    """Types of heatmaps"""
    CRIME = "crime"
    VIOLENCE = "violence"
    PROPERTY_CRIME = "property_crime"
    DRUG_ACTIVITY = "drug_activity"
    GANG_ACTIVITY = "gang_activity"
    TRAFFIC_INCIDENTS = "traffic_incidents"
    CALLS_FOR_SERVICE = "calls_for_service"
    ARRESTS = "arrests"
    SHOTS_FIRED = "shots_fired"
    DOMESTIC_VIOLENCE = "domestic_violence"
    CUSTOM = "custom"


class ClusterType(str, Enum):
    """Types of crime clusters"""
    EMERGING = "emerging"
    ACTIVE = "active"
    DECLINING = "declining"
    DORMANT = "dormant"
    SEASONAL = "seasonal"
    PERSISTENT = "persistent"


class RiskLevel(str, Enum):
    """Risk levels"""
    MINIMAL = "minimal"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


class TrajectoryConfidence(str, Enum):
    """Confidence levels for trajectory predictions"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


@dataclass
class HeatmapCell:
    """A cell in a heatmap grid"""
    cell_id: str
    h3_index: str
    latitude: float
    longitude: float
    value: float
    count: int = 0
    risk_level: RiskLevel = RiskLevel.LOW
    trend: str = "stable"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RegionalHeatmap:
    """A regional heatmap spanning multiple jurisdictions"""
    heatmap_id: str
    heatmap_type: HeatmapType
    name: str
    description: str = ""
    region_codes: List[str] = field(default_factory=list)
    tenant_ids: List[str] = field(default_factory=list)
    cells: List[HeatmapCell] = field(default_factory=list)
    resolution: int = 8
    min_lat: float = 0.0
    max_lat: float = 0.0
    min_lon: float = 0.0
    max_lon: float = 0.0
    time_range_start: Optional[datetime] = None
    time_range_end: Optional[datetime] = None
    total_incidents: int = 0
    max_value: float = 0.0
    avg_value: float = 0.0
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TrajectoryPoint:
    """A point in an offender trajectory"""
    point_id: str
    latitude: float
    longitude: float
    timestamp: datetime
    location_type: str = ""
    jurisdiction_code: str = ""
    tenant_id: str = ""
    incident_id: str = ""
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CrossCityTrajectory:
    """Cross-city offender trajectory prediction"""
    trajectory_id: str
    offender_id: str
    offender_name: str = ""
    offender_aliases: List[str] = field(default_factory=list)
    known_points: List[TrajectoryPoint] = field(default_factory=list)
    predicted_points: List[TrajectoryPoint] = field(default_factory=list)
    jurisdictions_crossed: List[str] = field(default_factory=list)
    tenants_involved: List[str] = field(default_factory=list)
    pattern_type: str = ""
    confidence: TrajectoryConfidence = TrajectoryConfidence.MEDIUM
    confidence_score: float = 0.5
    risk_level: RiskLevel = RiskLevel.MODERATE
    last_known_location: Optional[TrajectoryPoint] = None
    predicted_next_location: Optional[TrajectoryPoint] = None
    avg_time_between_incidents_hours: float = 0.0
    total_incidents: int = 0
    active_warrants: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RegionalCluster:
    """A regional crime cluster"""
    cluster_id: str
    cluster_type: ClusterType
    name: str
    description: str = ""
    center_lat: float = 0.0
    center_lon: float = 0.0
    radius_km: float = 1.0
    boundary_coords: List[Tuple[float, float]] = field(default_factory=list)
    jurisdictions: List[str] = field(default_factory=list)
    tenants: List[str] = field(default_factory=list)
    crime_types: List[str] = field(default_factory=list)
    incident_count: int = 0
    incident_count_7d: int = 0
    incident_count_30d: int = 0
    trend: str = "stable"
    trend_percent: float = 0.0
    risk_level: RiskLevel = RiskLevel.MODERATE
    peak_hours: List[int] = field(default_factory=list)
    peak_days: List[int] = field(default_factory=list)
    first_detected: datetime = field(default_factory=datetime.utcnow)
    last_incident: Optional[datetime] = None
    predicted_next_incident: Optional[datetime] = None
    contributing_factors: List[str] = field(default_factory=list)
    recommended_actions: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RiskOverlayCell:
    """A cell in a risk overlay"""
    cell_id: str
    h3_index: str
    latitude: float
    longitude: float
    risk_score: float
    risk_level: RiskLevel
    contributing_factors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FederatedRiskMap:
    """A federated risk map combining multiple data sources"""
    riskmap_id: str
    name: str
    description: str = ""
    region_codes: List[str] = field(default_factory=list)
    tenant_ids: List[str] = field(default_factory=list)
    cells: List[RiskOverlayCell] = field(default_factory=list)
    resolution: int = 8
    min_lat: float = 0.0
    max_lat: float = 0.0
    min_lon: float = 0.0
    max_lon: float = 0.0
    data_sources: List[str] = field(default_factory=list)
    weights: Dict[str, float] = field(default_factory=dict)
    high_risk_count: int = 0
    critical_risk_count: int = 0
    avg_risk_score: float = 0.0
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    valid_until: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AnalyticsQuery:
    """Query parameters for federated analytics"""
    query_id: str
    query_type: str
    tenant_ids: List[str] = field(default_factory=list)
    region_codes: List[str] = field(default_factory=list)
    time_range_start: Optional[datetime] = None
    time_range_end: Optional[datetime] = None
    crime_types: List[str] = field(default_factory=list)
    min_lat: float = 0.0
    max_lat: float = 0.0
    min_lon: float = 0.0
    max_lon: float = 0.0
    resolution: int = 8
    filters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AnalyticsMetrics:
    """Metrics for federated analytics"""
    total_heatmaps: int = 0
    total_trajectories: int = 0
    total_clusters: int = 0
    total_riskmaps: int = 0
    active_clusters: int = 0
    high_risk_areas: int = 0
    cross_jurisdiction_offenders: int = 0
    queries_24h: int = 0


class FederatedAnalyticsEngine:
    """
    Manages federated analytics across multiple cities and agencies.
    
    Provides:
    - Multi-city crime heatmaps
    - Cross-city offender trajectory predictions
    - Regional crime clusters
    - Real-time risk overlays
    """
    
    def __init__(self):
        self._heatmaps: Dict[str, RegionalHeatmap] = {}
        self._trajectories: Dict[str, CrossCityTrajectory] = {}
        self._clusters: Dict[str, RegionalCluster] = {}
        self._riskmaps: Dict[str, FederatedRiskMap] = {}
        self._callbacks: Dict[str, List[Callable]] = {}
        self._events: List[Dict[str, Any]] = []
        self._max_events = 10000
    
    def create_regional_heatmap(
        self,
        heatmap_type: HeatmapType,
        name: str,
        region_codes: List[str],
        tenant_ids: List[str],
        time_range_start: datetime = None,
        time_range_end: datetime = None,
        resolution: int = 8,
        description: str = "",
    ) -> Optional[RegionalHeatmap]:
        """Create a regional heatmap"""
        heatmap_id = f"heatmap-{uuid.uuid4().hex[:12]}"
        
        if time_range_end is None:
            time_range_end = datetime.utcnow()
        if time_range_start is None:
            time_range_start = time_range_end - timedelta(days=30)
        
        heatmap = RegionalHeatmap(
            heatmap_id=heatmap_id,
            heatmap_type=heatmap_type,
            name=name,
            description=description,
            region_codes=region_codes,
            tenant_ids=tenant_ids,
            resolution=resolution,
            time_range_start=time_range_start,
            time_range_end=time_range_end,
        )
        
        self._heatmaps[heatmap_id] = heatmap
        
        self._record_event("heatmap_created", {
            "heatmap_id": heatmap_id,
            "heatmap_type": heatmap_type.value,
            "name": name,
        })
        self._notify_callbacks("heatmap_created", heatmap)
        
        return heatmap
    
    def add_heatmap_data(
        self,
        heatmap_id: str,
        incidents: List[Dict[str, Any]],
    ) -> bool:
        """Add incident data to a heatmap"""
        if heatmap_id not in self._heatmaps:
            return False
        
        heatmap = self._heatmaps[heatmap_id]
        
        cell_data: Dict[str, Dict[str, Any]] = {}
        
        for incident in incidents:
            lat = incident.get("latitude", 0)
            lon = incident.get("longitude", 0)
            
            if lat == 0 or lon == 0:
                continue
            
            h3_index = self._lat_lon_to_h3(lat, lon, heatmap.resolution)
            
            if h3_index not in cell_data:
                cell_data[h3_index] = {
                    "count": 0,
                    "lat_sum": 0,
                    "lon_sum": 0,
                }
            
            cell_data[h3_index]["count"] += 1
            cell_data[h3_index]["lat_sum"] += lat
            cell_data[h3_index]["lon_sum"] += lon
        
        for h3_index, data in cell_data.items():
            count = data["count"]
            avg_lat = data["lat_sum"] / count
            avg_lon = data["lon_sum"] / count
            
            existing_cell = None
            for cell in heatmap.cells:
                if cell.h3_index == h3_index:
                    existing_cell = cell
                    break
            
            if existing_cell:
                existing_cell.count += count
                existing_cell.value = existing_cell.count
            else:
                cell = HeatmapCell(
                    cell_id=f"cell-{uuid.uuid4().hex[:8]}",
                    h3_index=h3_index,
                    latitude=avg_lat,
                    longitude=avg_lon,
                    value=count,
                    count=count,
                )
                heatmap.cells.append(cell)
        
        self._update_heatmap_stats(heatmap)
        self._calculate_heatmap_risk_levels(heatmap)
        
        heatmap.total_incidents += len(incidents)
        heatmap.updated_at = datetime.utcnow()
        
        self._notify_callbacks("heatmap_updated", heatmap)
        
        return True
    
    def get_heatmap(self, heatmap_id: str) -> Optional[RegionalHeatmap]:
        """Get a heatmap by ID"""
        return self._heatmaps.get(heatmap_id)
    
    def get_heatmaps_for_region(self, region_code: str) -> List[RegionalHeatmap]:
        """Get heatmaps for a region"""
        return [h for h in self._heatmaps.values() if region_code in h.region_codes]
    
    def get_heatmaps_for_tenant(self, tenant_id: str) -> List[RegionalHeatmap]:
        """Get heatmaps accessible to a tenant"""
        return [h for h in self._heatmaps.values() if tenant_id in h.tenant_ids]
    
    def create_trajectory(
        self,
        offender_id: str,
        offender_name: str = "",
        offender_aliases: List[str] = None,
    ) -> Optional[CrossCityTrajectory]:
        """Create a cross-city trajectory for an offender"""
        trajectory_id = f"traj-{uuid.uuid4().hex[:12]}"
        
        trajectory = CrossCityTrajectory(
            trajectory_id=trajectory_id,
            offender_id=offender_id,
            offender_name=offender_name,
            offender_aliases=offender_aliases or [],
        )
        
        self._trajectories[trajectory_id] = trajectory
        
        self._record_event("trajectory_created", {
            "trajectory_id": trajectory_id,
            "offender_id": offender_id,
        })
        self._notify_callbacks("trajectory_created", trajectory)
        
        return trajectory
    
    def add_trajectory_point(
        self,
        trajectory_id: str,
        latitude: float,
        longitude: float,
        timestamp: datetime,
        location_type: str = "",
        jurisdiction_code: str = "",
        tenant_id: str = "",
        incident_id: str = "",
        confidence: float = 1.0,
    ) -> bool:
        """Add a known point to a trajectory"""
        if trajectory_id not in self._trajectories:
            return False
        
        trajectory = self._trajectories[trajectory_id]
        
        point = TrajectoryPoint(
            point_id=f"pt-{uuid.uuid4().hex[:8]}",
            latitude=latitude,
            longitude=longitude,
            timestamp=timestamp,
            location_type=location_type,
            jurisdiction_code=jurisdiction_code,
            tenant_id=tenant_id,
            incident_id=incident_id,
            confidence=confidence,
        )
        
        trajectory.known_points.append(point)
        trajectory.known_points.sort(key=lambda p: p.timestamp)
        
        if jurisdiction_code and jurisdiction_code not in trajectory.jurisdictions_crossed:
            trajectory.jurisdictions_crossed.append(jurisdiction_code)
        
        if tenant_id and tenant_id not in trajectory.tenants_involved:
            trajectory.tenants_involved.append(tenant_id)
        
        trajectory.total_incidents = len(trajectory.known_points)
        trajectory.last_known_location = trajectory.known_points[-1]
        
        if len(trajectory.known_points) >= 2:
            self._calculate_trajectory_stats(trajectory)
            self._predict_next_location(trajectory)
        
        trajectory.updated_at = datetime.utcnow()
        
        self._notify_callbacks("trajectory_updated", trajectory)
        
        return True
    
    def get_trajectory(self, trajectory_id: str) -> Optional[CrossCityTrajectory]:
        """Get a trajectory by ID"""
        return self._trajectories.get(trajectory_id)
    
    def get_trajectory_by_offender(self, offender_id: str) -> Optional[CrossCityTrajectory]:
        """Get trajectory for an offender"""
        for traj in self._trajectories.values():
            if traj.offender_id == offender_id:
                return traj
        return None
    
    def get_cross_jurisdiction_trajectories(self, min_jurisdictions: int = 2) -> List[CrossCityTrajectory]:
        """Get trajectories that cross multiple jurisdictions"""
        return [
            t for t in self._trajectories.values()
            if len(t.jurisdictions_crossed) >= min_jurisdictions
        ]
    
    def create_cluster(
        self,
        cluster_type: ClusterType,
        name: str,
        center_lat: float,
        center_lon: float,
        radius_km: float = 1.0,
        jurisdictions: List[str] = None,
        tenants: List[str] = None,
        crime_types: List[str] = None,
        description: str = "",
    ) -> Optional[RegionalCluster]:
        """Create a regional crime cluster"""
        cluster_id = f"cluster-{uuid.uuid4().hex[:12]}"
        
        cluster = RegionalCluster(
            cluster_id=cluster_id,
            cluster_type=cluster_type,
            name=name,
            description=description,
            center_lat=center_lat,
            center_lon=center_lon,
            radius_km=radius_km,
            jurisdictions=jurisdictions or [],
            tenants=tenants or [],
            crime_types=crime_types or [],
        )
        
        self._clusters[cluster_id] = cluster
        
        self._record_event("cluster_created", {
            "cluster_id": cluster_id,
            "cluster_type": cluster_type.value,
            "name": name,
        })
        self._notify_callbacks("cluster_created", cluster)
        
        return cluster
    
    def update_cluster_stats(
        self,
        cluster_id: str,
        incident_count: int = None,
        incident_count_7d: int = None,
        incident_count_30d: int = None,
        last_incident: datetime = None,
        peak_hours: List[int] = None,
        peak_days: List[int] = None,
    ) -> bool:
        """Update cluster statistics"""
        if cluster_id not in self._clusters:
            return False
        
        cluster = self._clusters[cluster_id]
        
        if incident_count is not None:
            cluster.incident_count = incident_count
        if incident_count_7d is not None:
            cluster.incident_count_7d = incident_count_7d
        if incident_count_30d is not None:
            cluster.incident_count_30d = incident_count_30d
        if last_incident is not None:
            cluster.last_incident = last_incident
        if peak_hours is not None:
            cluster.peak_hours = peak_hours
        if peak_days is not None:
            cluster.peak_days = peak_days
        
        self._calculate_cluster_trend(cluster)
        self._calculate_cluster_risk(cluster)
        self._predict_next_cluster_incident(cluster)
        
        cluster.updated_at = datetime.utcnow()
        
        self._notify_callbacks("cluster_updated", cluster)
        
        return True
    
    def get_cluster(self, cluster_id: str) -> Optional[RegionalCluster]:
        """Get a cluster by ID"""
        return self._clusters.get(cluster_id)
    
    def get_clusters_for_region(self, region_code: str) -> List[RegionalCluster]:
        """Get clusters for a region"""
        return [c for c in self._clusters.values() if region_code in c.jurisdictions]
    
    def get_active_clusters(self) -> List[RegionalCluster]:
        """Get active clusters"""
        return [c for c in self._clusters.values() if c.cluster_type == ClusterType.ACTIVE]
    
    def get_high_risk_clusters(self) -> List[RegionalCluster]:
        """Get high-risk clusters"""
        return [
            c for c in self._clusters.values()
            if c.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]
        ]
    
    def create_risk_map(
        self,
        name: str,
        region_codes: List[str],
        tenant_ids: List[str],
        data_sources: List[str] = None,
        weights: Dict[str, float] = None,
        resolution: int = 8,
        description: str = "",
        valid_hours: int = 24,
    ) -> Optional[FederatedRiskMap]:
        """Create a federated risk map"""
        riskmap_id = f"riskmap-{uuid.uuid4().hex[:12]}"
        
        default_weights = {
            "crime_history": 0.3,
            "recent_incidents": 0.25,
            "environmental_factors": 0.15,
            "time_of_day": 0.1,
            "special_events": 0.1,
            "officer_presence": 0.1,
        }
        
        riskmap = FederatedRiskMap(
            riskmap_id=riskmap_id,
            name=name,
            description=description,
            region_codes=region_codes,
            tenant_ids=tenant_ids,
            resolution=resolution,
            data_sources=data_sources or list(default_weights.keys()),
            weights=weights or default_weights,
            valid_until=datetime.utcnow() + timedelta(hours=valid_hours),
        )
        
        self._riskmaps[riskmap_id] = riskmap
        
        self._record_event("riskmap_created", {
            "riskmap_id": riskmap_id,
            "name": name,
        })
        self._notify_callbacks("riskmap_created", riskmap)
        
        return riskmap
    
    def add_risk_data(
        self,
        riskmap_id: str,
        risk_scores: List[Dict[str, Any]],
    ) -> bool:
        """Add risk score data to a risk map"""
        if riskmap_id not in self._riskmaps:
            return False
        
        riskmap = self._riskmaps[riskmap_id]
        
        for score_data in risk_scores:
            lat = score_data.get("latitude", 0)
            lon = score_data.get("longitude", 0)
            risk_score = score_data.get("risk_score", 0)
            factors = score_data.get("contributing_factors", [])
            
            if lat == 0 or lon == 0:
                continue
            
            h3_index = self._lat_lon_to_h3(lat, lon, riskmap.resolution)
            
            risk_level = self._score_to_risk_level(risk_score)
            
            cell = RiskOverlayCell(
                cell_id=f"risk-{uuid.uuid4().hex[:8]}",
                h3_index=h3_index,
                latitude=lat,
                longitude=lon,
                risk_score=risk_score,
                risk_level=risk_level,
                contributing_factors=factors,
            )
            
            riskmap.cells.append(cell)
            
            if risk_level == RiskLevel.HIGH:
                riskmap.high_risk_count += 1
            elif risk_level == RiskLevel.CRITICAL:
                riskmap.critical_risk_count += 1
        
        if riskmap.cells:
            total_score = sum(c.risk_score for c in riskmap.cells)
            riskmap.avg_risk_score = total_score / len(riskmap.cells)
        
        self._update_riskmap_bounds(riskmap)
        riskmap.updated_at = datetime.utcnow()
        
        self._notify_callbacks("riskmap_updated", riskmap)
        
        return True
    
    def get_risk_map(self, riskmap_id: str) -> Optional[FederatedRiskMap]:
        """Get a risk map by ID"""
        return self._riskmaps.get(riskmap_id)
    
    def get_risk_maps_for_tenant(self, tenant_id: str) -> List[FederatedRiskMap]:
        """Get risk maps accessible to a tenant"""
        return [r for r in self._riskmaps.values() if tenant_id in r.tenant_ids]
    
    def get_risk_at_location(
        self,
        latitude: float,
        longitude: float,
        riskmap_id: str = None,
    ) -> Optional[RiskOverlayCell]:
        """Get risk level at a specific location"""
        if riskmap_id:
            riskmaps = [self._riskmaps.get(riskmap_id)] if riskmap_id in self._riskmaps else []
        else:
            riskmaps = list(self._riskmaps.values())
        
        for riskmap in riskmaps:
            if not riskmap:
                continue
            
            h3_index = self._lat_lon_to_h3(latitude, longitude, riskmap.resolution)
            
            for cell in riskmap.cells:
                if cell.h3_index == h3_index:
                    return cell
        
        return None
    
    def query_analytics(self, query: AnalyticsQuery) -> Dict[str, Any]:
        """Execute a federated analytics query"""
        results = {
            "query_id": query.query_id,
            "heatmaps": [],
            "clusters": [],
            "trajectories": [],
            "riskmaps": [],
        }
        
        for heatmap in self._heatmaps.values():
            if query.tenant_ids and not any(t in heatmap.tenant_ids for t in query.tenant_ids):
                continue
            if query.region_codes and not any(r in heatmap.region_codes for r in query.region_codes):
                continue
            results["heatmaps"].append(heatmap)
        
        for cluster in self._clusters.values():
            if query.tenant_ids and not any(t in cluster.tenants for t in query.tenant_ids):
                continue
            if query.region_codes and not any(r in cluster.jurisdictions for r in query.region_codes):
                continue
            results["clusters"].append(cluster)
        
        for trajectory in self._trajectories.values():
            if query.tenant_ids and not any(t in trajectory.tenants_involved for t in query.tenant_ids):
                continue
            if query.region_codes and not any(r in trajectory.jurisdictions_crossed for r in query.region_codes):
                continue
            results["trajectories"].append(trajectory)
        
        for riskmap in self._riskmaps.values():
            if query.tenant_ids and not any(t in riskmap.tenant_ids for t in query.tenant_ids):
                continue
            if query.region_codes and not any(r in riskmap.region_codes for r in query.region_codes):
                continue
            results["riskmaps"].append(riskmap)
        
        self._record_event("analytics_query", {
            "query_id": query.query_id,
            "query_type": query.query_type,
        })
        
        return results
    
    def get_metrics(self) -> AnalyticsMetrics:
        """Get analytics metrics"""
        metrics = AnalyticsMetrics()
        metrics.total_heatmaps = len(self._heatmaps)
        metrics.total_trajectories = len(self._trajectories)
        metrics.total_clusters = len(self._clusters)
        metrics.total_riskmaps = len(self._riskmaps)
        
        metrics.active_clusters = len([
            c for c in self._clusters.values()
            if c.cluster_type == ClusterType.ACTIVE
        ])
        
        metrics.high_risk_areas = sum(r.high_risk_count + r.critical_risk_count for r in self._riskmaps.values())
        
        metrics.cross_jurisdiction_offenders = len([
            t for t in self._trajectories.values()
            if len(t.jurisdictions_crossed) >= 2
        ])
        
        return metrics
    
    def get_recent_events(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent events"""
        return self._events[-limit:]
    
    def register_callback(self, event_type: str, callback: Callable) -> None:
        """Register a callback for an event type"""
        if event_type not in self._callbacks:
            self._callbacks[event_type] = []
        self._callbacks[event_type].append(callback)
    
    def _lat_lon_to_h3(self, lat: float, lon: float, resolution: int) -> str:
        """Convert lat/lon to H3 index (simplified)"""
        lat_grid = int((lat + 90) * (10 ** (resolution - 5)))
        lon_grid = int((lon + 180) * (10 ** (resolution - 5)))
        return f"h3_{resolution}_{lat_grid}_{lon_grid}"
    
    def _update_heatmap_stats(self, heatmap: RegionalHeatmap) -> None:
        """Update heatmap statistics"""
        if not heatmap.cells:
            return
        
        values = [c.value for c in heatmap.cells]
        heatmap.max_value = max(values)
        heatmap.avg_value = sum(values) / len(values)
        
        lats = [c.latitude for c in heatmap.cells]
        lons = [c.longitude for c in heatmap.cells]
        heatmap.min_lat = min(lats)
        heatmap.max_lat = max(lats)
        heatmap.min_lon = min(lons)
        heatmap.max_lon = max(lons)
    
    def _calculate_heatmap_risk_levels(self, heatmap: RegionalHeatmap) -> None:
        """Calculate risk levels for heatmap cells"""
        if not heatmap.cells or heatmap.max_value == 0:
            return
        
        for cell in heatmap.cells:
            normalized = cell.value / heatmap.max_value
            cell.risk_level = self._score_to_risk_level(normalized * 100)
    
    def _calculate_trajectory_stats(self, trajectory: CrossCityTrajectory) -> None:
        """Calculate trajectory statistics"""
        if len(trajectory.known_points) < 2:
            return
        
        total_hours = 0
        for i in range(1, len(trajectory.known_points)):
            delta = trajectory.known_points[i].timestamp - trajectory.known_points[i-1].timestamp
            total_hours += delta.total_seconds() / 3600
        
        trajectory.avg_time_between_incidents_hours = total_hours / (len(trajectory.known_points) - 1)
        
        if len(trajectory.jurisdictions_crossed) >= 3:
            trajectory.confidence = TrajectoryConfidence.HIGH
            trajectory.confidence_score = 0.8
        elif len(trajectory.jurisdictions_crossed) >= 2:
            trajectory.confidence = TrajectoryConfidence.MEDIUM
            trajectory.confidence_score = 0.6
        else:
            trajectory.confidence = TrajectoryConfidence.LOW
            trajectory.confidence_score = 0.4
        
        if trajectory.total_incidents >= 5:
            trajectory.risk_level = RiskLevel.HIGH
        elif trajectory.total_incidents >= 3:
            trajectory.risk_level = RiskLevel.MODERATE
        else:
            trajectory.risk_level = RiskLevel.LOW
    
    def _predict_next_location(self, trajectory: CrossCityTrajectory) -> None:
        """Predict next location for a trajectory"""
        if len(trajectory.known_points) < 2:
            return
        
        recent_points = trajectory.known_points[-3:]
        
        avg_lat = sum(p.latitude for p in recent_points) / len(recent_points)
        avg_lon = sum(p.longitude for p in recent_points) / len(recent_points)
        
        if len(recent_points) >= 2:
            lat_trend = recent_points[-1].latitude - recent_points[-2].latitude
            lon_trend = recent_points[-1].longitude - recent_points[-2].longitude
            avg_lat += lat_trend * 0.5
            avg_lon += lon_trend * 0.5
        
        predicted_time = datetime.utcnow() + timedelta(hours=trajectory.avg_time_between_incidents_hours)
        
        predicted_point = TrajectoryPoint(
            point_id=f"pred-{uuid.uuid4().hex[:8]}",
            latitude=avg_lat,
            longitude=avg_lon,
            timestamp=predicted_time,
            location_type="predicted",
            confidence=trajectory.confidence_score * 0.7,
        )
        
        trajectory.predicted_next_location = predicted_point
        trajectory.predicted_points = [predicted_point]
    
    def _calculate_cluster_trend(self, cluster: RegionalCluster) -> None:
        """Calculate cluster trend"""
        if cluster.incident_count_30d == 0:
            cluster.trend = "stable"
            cluster.trend_percent = 0
            return
        
        if cluster.incident_count_7d > 0:
            weekly_rate = cluster.incident_count_7d / 7
            monthly_rate = cluster.incident_count_30d / 30
            
            if monthly_rate > 0:
                change = ((weekly_rate - monthly_rate) / monthly_rate) * 100
                cluster.trend_percent = change
                
                if change > 20:
                    cluster.trend = "increasing_fast"
                    cluster.cluster_type = ClusterType.EMERGING
                elif change > 5:
                    cluster.trend = "increasing"
                elif change < -20:
                    cluster.trend = "decreasing_fast"
                    cluster.cluster_type = ClusterType.DECLINING
                elif change < -5:
                    cluster.trend = "decreasing"
                else:
                    cluster.trend = "stable"
    
    def _calculate_cluster_risk(self, cluster: RegionalCluster) -> None:
        """Calculate cluster risk level"""
        if cluster.incident_count_7d >= 10:
            cluster.risk_level = RiskLevel.CRITICAL
        elif cluster.incident_count_7d >= 5:
            cluster.risk_level = RiskLevel.HIGH
        elif cluster.incident_count_7d >= 2:
            cluster.risk_level = RiskLevel.MODERATE
        elif cluster.incident_count_7d >= 1:
            cluster.risk_level = RiskLevel.LOW
        else:
            cluster.risk_level = RiskLevel.MINIMAL
    
    def _predict_next_cluster_incident(self, cluster: RegionalCluster) -> None:
        """Predict next incident time for a cluster"""
        if cluster.incident_count_7d == 0:
            return
        
        avg_hours_between = (7 * 24) / cluster.incident_count_7d
        
        if cluster.last_incident:
            cluster.predicted_next_incident = cluster.last_incident + timedelta(hours=avg_hours_between)
        else:
            cluster.predicted_next_incident = datetime.utcnow() + timedelta(hours=avg_hours_between)
    
    def _score_to_risk_level(self, score: float) -> RiskLevel:
        """Convert a score to a risk level"""
        if score >= 80:
            return RiskLevel.CRITICAL
        elif score >= 60:
            return RiskLevel.HIGH
        elif score >= 40:
            return RiskLevel.MODERATE
        elif score >= 20:
            return RiskLevel.LOW
        else:
            return RiskLevel.MINIMAL
    
    def _update_riskmap_bounds(self, riskmap: FederatedRiskMap) -> None:
        """Update risk map bounds"""
        if not riskmap.cells:
            return
        
        lats = [c.latitude for c in riskmap.cells]
        lons = [c.longitude for c in riskmap.cells]
        riskmap.min_lat = min(lats)
        riskmap.max_lat = max(lats)
        riskmap.min_lon = min(lons)
        riskmap.max_lon = max(lons)
    
    def _record_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Record an event"""
        event = {
            "event_id": f"evt-{uuid.uuid4().hex[:8]}",
            "event_type": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data,
        }
        self._events.append(event)
        
        if len(self._events) > self._max_events:
            self._events = self._events[-self._max_events:]
    
    def _notify_callbacks(self, event_type: str, data: Any) -> None:
        """Notify registered callbacks"""
        if event_type in self._callbacks:
            for callback in self._callbacks[event_type]:
                try:
                    callback(data)
                except Exception:
                    pass
