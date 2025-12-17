"""
Crime Heatmap Engine.

Generates:
- Kernel Density Heatmaps for map visualization
- Hotspot clustering with HDBSCAN algorithm
- Supports multiple time ranges (24h, 7d, 30d, custom)
"""

import math
from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel
from enum import Enum

from app.crime_analysis.crime_ingest import (
    NormalizedCrimeRecord,
    CrimeType,
    get_crime_ingestor,
)


class TimeRange(str, Enum):
    HOURS_24 = "24h"
    DAYS_7 = "7d"
    DAYS_30 = "30d"
    CUSTOM = "custom"


class HeatmapPoint(BaseModel):
    """Single point in heatmap with intensity."""
    latitude: float
    longitude: float
    intensity: float
    weight: float = 1.0


class HotspotCluster(BaseModel):
    """Identified crime hotspot cluster."""
    cluster_id: int
    center_lat: float
    center_lng: float
    radius_meters: float
    incident_count: int
    crime_types: list[str]
    severity_score: float
    top_crimes: list[str]


class HeatmapResult(BaseModel):
    """Complete heatmap analysis result."""
    points: list[HeatmapPoint]
    hotspots: list[HotspotCluster]
    time_range: str
    start_date: str
    end_date: str
    total_incidents: int
    bounds: dict  # {north, south, east, west}


class CrimeHeatmapEngine:
    """Generates crime heatmaps and identifies hotspots."""
    
    # Kernel bandwidth in degrees (approximately 500m)
    DEFAULT_BANDWIDTH = 0.005
    
    # Grid resolution for density estimation
    GRID_SIZE = 50
    
    # Minimum cluster size for HDBSCAN
    MIN_CLUSTER_SIZE = 3
    
    # Distance threshold for clustering (in degrees, ~200m)
    CLUSTER_EPSILON = 0.002
    
    # Crime type weights for intensity calculation
    CRIME_WEIGHTS = {
        CrimeType.VIOLENT: 3.0,
        CrimeType.PROPERTY: 1.5,
        CrimeType.DRUG: 1.2,
        CrimeType.PUBLIC_ORDER: 0.8,
        CrimeType.TRAFFIC: 0.5,
        CrimeType.OTHER: 1.0,
    }
    
    def __init__(self):
        self.ingestor = get_crime_ingestor()
    
    def _filter_by_time_range(
        self,
        records: list[NormalizedCrimeRecord],
        time_range: TimeRange,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> tuple[list[NormalizedCrimeRecord], datetime, datetime]:
        """Filter records by time range."""
        now = datetime.utcnow()
        
        if time_range == TimeRange.HOURS_24:
            start = now - timedelta(hours=24)
            end = now
        elif time_range == TimeRange.DAYS_7:
            start = now - timedelta(days=7)
            end = now
        elif time_range == TimeRange.DAYS_30:
            start = now - timedelta(days=30)
            end = now
        elif time_range == TimeRange.CUSTOM:
            start = start_date or (now - timedelta(days=30))
            end = end_date or now
        else:
            start = now - timedelta(days=7)
            end = now
        
        filtered = [
            r for r in records
            if start <= r.datetime_utc <= end
        ]
        
        return filtered, start, end
    
    def _filter_by_crime_type(
        self,
        records: list[NormalizedCrimeRecord],
        crime_types: Optional[list[CrimeType]] = None,
    ) -> list[NormalizedCrimeRecord]:
        """Filter records by crime type."""
        if not crime_types:
            return records
        return [r for r in records if r.type in crime_types]
    
    def _gaussian_kernel(self, distance: float, bandwidth: float) -> float:
        """Calculate Gaussian kernel value."""
        return math.exp(-(distance ** 2) / (2 * bandwidth ** 2))
    
    def _calculate_distance(
        self,
        lat1: float, lng1: float,
        lat2: float, lng2: float
    ) -> float:
        """Calculate Euclidean distance in degrees."""
        return math.sqrt((lat2 - lat1) ** 2 + (lng2 - lng1) ** 2)
    
    def _kernel_density_estimation(
        self,
        records: list[NormalizedCrimeRecord],
        bounds: dict,
        bandwidth: float = None,
    ) -> list[HeatmapPoint]:
        """Perform kernel density estimation."""
        if not records:
            return []
        
        bandwidth = bandwidth or self.DEFAULT_BANDWIDTH
        
        # Create grid
        lat_step = (bounds["north"] - bounds["south"]) / self.GRID_SIZE
        lng_step = (bounds["east"] - bounds["west"]) / self.GRID_SIZE
        
        points = []
        
        for i in range(self.GRID_SIZE):
            for j in range(self.GRID_SIZE):
                grid_lat = bounds["south"] + (i + 0.5) * lat_step
                grid_lng = bounds["west"] + (j + 0.5) * lng_step
                
                # Calculate density at this grid point
                density = 0.0
                for record in records:
                    distance = self._calculate_distance(
                        grid_lat, grid_lng,
                        record.latitude, record.longitude
                    )
                    weight = self.CRIME_WEIGHTS.get(record.type, 1.0)
                    density += weight * self._gaussian_kernel(distance, bandwidth)
                
                if density > 0.01:  # Threshold to reduce noise
                    points.append(HeatmapPoint(
                        latitude=grid_lat,
                        longitude=grid_lng,
                        intensity=min(density, 10.0),  # Cap intensity
                        weight=density,
                    ))
        
        return points
    
    def _simple_clustering(
        self,
        records: list[NormalizedCrimeRecord],
        epsilon: float = None,
        min_samples: int = None,
    ) -> list[HotspotCluster]:
        """Simple distance-based clustering (HDBSCAN-like)."""
        if not records:
            return []
        
        epsilon = epsilon or self.CLUSTER_EPSILON
        min_samples = min_samples or self.MIN_CLUSTER_SIZE
        
        # Track which records have been assigned to clusters
        assigned = [False] * len(records)
        clusters = []
        cluster_id = 0
        
        for i, record in enumerate(records):
            if assigned[i]:
                continue
            
            # Find all neighbors within epsilon
            neighbors = [i]
            for j, other in enumerate(records):
                if i != j and not assigned[j]:
                    distance = self._calculate_distance(
                        record.latitude, record.longitude,
                        other.latitude, other.longitude
                    )
                    if distance <= epsilon:
                        neighbors.append(j)
            
            # Only create cluster if we have enough points
            if len(neighbors) >= min_samples:
                # Mark all neighbors as assigned
                for idx in neighbors:
                    assigned[idx] = True
                
                # Calculate cluster properties
                cluster_records = [records[idx] for idx in neighbors]
                center_lat = sum(r.latitude for r in cluster_records) / len(cluster_records)
                center_lng = sum(r.longitude for r in cluster_records) / len(cluster_records)
                
                # Calculate radius (max distance from center)
                max_dist = 0
                for r in cluster_records:
                    dist = self._calculate_distance(center_lat, center_lng, r.latitude, r.longitude)
                    max_dist = max(max_dist, dist)
                
                # Convert degrees to meters (approximate)
                radius_meters = max_dist * 111000  # 1 degree ≈ 111km
                
                # Get crime types and top crimes
                crime_types = list(set(r.type.value for r in cluster_records))
                crime_counts = {}
                for r in cluster_records:
                    key = r.subcategory
                    crime_counts[key] = crime_counts.get(key, 0) + 1
                top_crimes = sorted(crime_counts.keys(), key=lambda x: crime_counts[x], reverse=True)[:5]
                
                # Calculate severity score
                severity = sum(self.CRIME_WEIGHTS.get(r.type, 1.0) for r in cluster_records)
                severity_score = min(severity / len(cluster_records) * 2, 5.0)
                
                clusters.append(HotspotCluster(
                    cluster_id=cluster_id,
                    center_lat=center_lat,
                    center_lng=center_lng,
                    radius_meters=max(radius_meters, 100),  # Minimum 100m radius
                    incident_count=len(cluster_records),
                    crime_types=crime_types,
                    severity_score=round(severity_score, 2),
                    top_crimes=top_crimes,
                ))
                cluster_id += 1
        
        return clusters
    
    def _calculate_bounds(self, records: list[NormalizedCrimeRecord]) -> dict:
        """Calculate geographic bounds of records."""
        if not records:
            # Default to Riviera Beach area
            return {
                "north": 26.82,
                "south": 26.75,
                "east": -80.03,
                "west": -80.12,
            }
        
        lats = [r.latitude for r in records]
        lngs = [r.longitude for r in records]
        
        # Add padding
        padding = 0.01
        return {
            "north": max(lats) + padding,
            "south": min(lats) - padding,
            "east": max(lngs) + padding,
            "west": min(lngs) - padding,
        }
    
    def generate_heatmap(
        self,
        time_range: TimeRange = TimeRange.DAYS_7,
        crime_types: Optional[list[CrimeType]] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> HeatmapResult:
        """Generate complete heatmap analysis."""
        # Get all records
        all_records = self.ingestor.get_all_records()
        
        # Filter by time range
        filtered_records, start, end = self._filter_by_time_range(
            all_records, time_range, start_date, end_date
        )
        
        # Filter by crime type
        filtered_records = self._filter_by_crime_type(filtered_records, crime_types)
        
        # Calculate bounds
        bounds = self._calculate_bounds(filtered_records)
        
        # Generate heatmap points
        points = self._kernel_density_estimation(filtered_records, bounds)
        
        # Identify hotspots
        hotspots = self._simple_clustering(filtered_records)
        
        return HeatmapResult(
            points=points,
            hotspots=hotspots,
            time_range=time_range.value,
            start_date=start.strftime("%Y-%m-%d"),
            end_date=end.strftime("%Y-%m-%d"),
            total_incidents=len(filtered_records),
            bounds=bounds,
        )


# Global engine instance
_engine: Optional[CrimeHeatmapEngine] = None


def get_heatmap_engine() -> CrimeHeatmapEngine:
    """Get or create the global heatmap engine."""
    global _engine
    if _engine is None:
        _engine = CrimeHeatmapEngine()
    return _engine
