"""
Repeat Location Detector Module.

Identifies:
- Repeat addresses with multiple incidents
- High-frequency call locations
- Business hotspots
- Produces ranked lists
"""

from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel
from collections import defaultdict

from app.crime_analysis.crime_ingest import (
    NormalizedCrimeRecord,
    CrimeType,
    get_crime_ingestor,
)


class RepeatLocation(BaseModel):
    """A location with repeat incidents."""
    location_id: str
    latitude: float
    longitude: float
    address: Optional[str]
    incident_count: int
    first_incident: str
    last_incident: str
    crime_types: list[str]
    severity_score: float
    is_business: bool
    sector: str
    incidents: list[dict]  # Summary of each incident


class LocationCluster(BaseModel):
    """Cluster of nearby repeat locations."""
    cluster_id: str
    center_lat: float
    center_lng: float
    radius_meters: float
    total_incidents: int
    location_count: int
    top_location: RepeatLocation
    sector: str


class RepeatLocationResult(BaseModel):
    """Complete repeat location analysis."""
    repeat_locations: list[RepeatLocation]
    clusters: list[LocationCluster]
    total_repeat_locations: int
    total_incidents_at_repeats: int
    top_10_hotspots: list[RepeatLocation]
    analysis_period: str
    generated_at: str


class RepeatLocationDetector:
    """Detects and analyzes repeat crime locations."""
    
    # Coordinate precision for grouping (4 decimal places ≈ 11m)
    COORD_PRECISION = 4
    
    # Minimum incidents to be considered a repeat location
    MIN_REPEAT_COUNT = 2
    
    # Business indicators in addresses
    BUSINESS_INDICATORS = [
        "plaza", "mall", "store", "shop", "market", "gas station",
        "convenience", "restaurant", "bar", "club", "hotel", "motel",
        "bank", "atm", "parking", "lot", "garage", "station",
        "walmart", "target", "publix", "wawa", "7-eleven", "cvs", "walgreens"
    ]
    
    # Crime type weights for severity
    SEVERITY_WEIGHTS = {
        CrimeType.VIOLENT: 3.0,
        CrimeType.PROPERTY: 1.5,
        CrimeType.DRUG: 1.2,
        CrimeType.PUBLIC_ORDER: 0.8,
        CrimeType.TRAFFIC: 0.5,
        CrimeType.OTHER: 1.0,
    }
    
    def __init__(self):
        self.ingestor = get_crime_ingestor()
    
    def _round_coords(self, lat: float, lng: float) -> tuple[float, float]:
        """Round coordinates to group nearby locations."""
        return (
            round(lat, self.COORD_PRECISION),
            round(lng, self.COORD_PRECISION)
        )
    
    def _is_business(self, address: Optional[str]) -> bool:
        """Check if address appears to be a business."""
        if not address:
            return False
        address_lower = address.lower()
        return any(indicator in address_lower for indicator in self.BUSINESS_INDICATORS)
    
    def _calculate_severity(self, records: list[NormalizedCrimeRecord]) -> float:
        """Calculate severity score for a location."""
        if not records:
            return 0.0
        
        total_weight = sum(
            self.SEVERITY_WEIGHTS.get(r.type, 1.0)
            for r in records
        )
        
        # Factor in recency (more recent = higher severity)
        now = datetime.utcnow()
        recency_factor = 0
        for r in records:
            days_ago = (now - r.datetime_utc).days
            if days_ago < 7:
                recency_factor += 1.0
            elif days_ago < 30:
                recency_factor += 0.5
            else:
                recency_factor += 0.2
        
        # Combine factors
        base_score = total_weight / len(records)
        recency_bonus = recency_factor / len(records)
        
        return min(5.0, base_score + recency_bonus)
    
    def _group_by_location(
        self,
        records: list[NormalizedCrimeRecord],
    ) -> dict[tuple, list[NormalizedCrimeRecord]]:
        """Group records by rounded coordinates."""
        location_groups = defaultdict(list)
        
        for record in records:
            loc_key = self._round_coords(record.latitude, record.longitude)
            location_groups[loc_key].append(record)
        
        return location_groups
    
    def _create_repeat_location(
        self,
        loc_key: tuple[float, float],
        records: list[NormalizedCrimeRecord],
    ) -> RepeatLocation:
        """Create a RepeatLocation from grouped records."""
        # Sort by datetime
        sorted_records = sorted(records, key=lambda r: r.datetime_utc)
        
        # Get unique crime types
        crime_types = list(set(r.type.value for r in records))
        
        # Get address (use most common or first available)
        addresses = [r.address for r in records if r.address]
        address = addresses[0] if addresses else None
        
        # Get sector (use most common)
        sectors = [r.sector for r in records]
        sector = max(set(sectors), key=sectors.count) if sectors else "Unknown"
        
        # Create incident summaries
        incidents = [
            {
                "id": r.id,
                "type": r.type.value,
                "subcategory": r.subcategory,
                "datetime": r.datetime_utc.isoformat(),
                "priority": r.priority.value,
            }
            for r in sorted_records[-10:]  # Last 10 incidents
        ]
        
        return RepeatLocation(
            location_id=f"loc-{loc_key[0]:.4f}-{loc_key[1]:.4f}",
            latitude=loc_key[0],
            longitude=loc_key[1],
            address=address,
            incident_count=len(records),
            first_incident=sorted_records[0].datetime_utc.isoformat(),
            last_incident=sorted_records[-1].datetime_utc.isoformat(),
            crime_types=crime_types,
            severity_score=round(self._calculate_severity(records), 2),
            is_business=self._is_business(address),
            sector=sector,
            incidents=incidents,
        )
    
    def _cluster_locations(
        self,
        locations: list[RepeatLocation],
        epsilon: float = 0.003,  # ~330m
    ) -> list[LocationCluster]:
        """Cluster nearby repeat locations."""
        if not locations:
            return []
        
        clusters = []
        assigned = [False] * len(locations)
        cluster_id = 0
        
        for i, loc in enumerate(locations):
            if assigned[i]:
                continue
            
            # Find nearby locations
            cluster_locs = [loc]
            assigned[i] = True
            
            for j, other in enumerate(locations):
                if i != j and not assigned[j]:
                    dist = ((loc.latitude - other.latitude) ** 2 + 
                           (loc.longitude - other.longitude) ** 2) ** 0.5
                    if dist <= epsilon:
                        cluster_locs.append(other)
                        assigned[j] = True
            
            if len(cluster_locs) >= 2:
                # Calculate cluster center
                center_lat = sum(l.latitude for l in cluster_locs) / len(cluster_locs)
                center_lng = sum(l.longitude for l in cluster_locs) / len(cluster_locs)
                
                # Calculate radius
                max_dist = max(
                    ((l.latitude - center_lat) ** 2 + (l.longitude - center_lng) ** 2) ** 0.5
                    for l in cluster_locs
                )
                radius_meters = max_dist * 111000  # Approximate conversion
                
                # Get top location
                top_loc = max(cluster_locs, key=lambda l: l.incident_count)
                
                # Get sector
                sectors = [l.sector for l in cluster_locs]
                sector = max(set(sectors), key=sectors.count)
                
                clusters.append(LocationCluster(
                    cluster_id=f"cluster-{cluster_id}",
                    center_lat=center_lat,
                    center_lng=center_lng,
                    radius_meters=max(radius_meters, 100),
                    total_incidents=sum(l.incident_count for l in cluster_locs),
                    location_count=len(cluster_locs),
                    top_location=top_loc,
                    sector=sector,
                ))
                cluster_id += 1
        
        return clusters
    
    def detect(
        self,
        days: int = 30,
        min_incidents: int = None,
    ) -> RepeatLocationResult:
        """Detect repeat locations in crime data."""
        min_incidents = min_incidents or self.MIN_REPEAT_COUNT
        
        # Get all records
        all_records = self.ingestor.get_all_records()
        
        # Filter by time
        cutoff = datetime.utcnow() - timedelta(days=days)
        records = [r for r in all_records if r.datetime_utc >= cutoff]
        
        # Group by location
        location_groups = self._group_by_location(records)
        
        # Create repeat locations
        repeat_locations = []
        for loc_key, loc_records in location_groups.items():
            if len(loc_records) >= min_incidents:
                repeat_loc = self._create_repeat_location(loc_key, loc_records)
                repeat_locations.append(repeat_loc)
        
        # Sort by incident count
        repeat_locations.sort(key=lambda l: l.incident_count, reverse=True)
        
        # Cluster locations
        clusters = self._cluster_locations(repeat_locations)
        clusters.sort(key=lambda c: c.total_incidents, reverse=True)
        
        # Calculate totals
        total_incidents = sum(l.incident_count for l in repeat_locations)
        
        return RepeatLocationResult(
            repeat_locations=repeat_locations,
            clusters=clusters,
            total_repeat_locations=len(repeat_locations),
            total_incidents_at_repeats=total_incidents,
            top_10_hotspots=repeat_locations[:10],
            analysis_period=f"Last {days} days",
            generated_at=datetime.utcnow().isoformat(),
        )
    
    def get_business_hotspots(self, days: int = 30) -> list[RepeatLocation]:
        """Get repeat locations that are businesses."""
        result = self.detect(days)
        return [loc for loc in result.repeat_locations if loc.is_business]
    
    def get_residential_hotspots(self, days: int = 30) -> list[RepeatLocation]:
        """Get repeat locations that are residential."""
        result = self.detect(days)
        return [loc for loc in result.repeat_locations if not loc.is_business]


# Global detector instance
_detector: Optional[RepeatLocationDetector] = None


def get_repeat_detector() -> RepeatLocationDetector:
    """Get or create the global repeat location detector."""
    global _detector
    if _detector is None:
        _detector = RepeatLocationDetector()
    return _detector
