"""
Heatmap Engine - Patrol Intensity and Zone Analysis

Generates patrol heatmaps and analyzes coverage patterns.
"""

from datetime import datetime, UTC, timedelta
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
import uuid
import math


class ZoneType(str, Enum):
    """Types of patrol zones."""
    HOTSPOT = "hotspot"
    HIGH_CALLS = "high_calls"
    VISIBILITY_GAP = "visibility_gap"
    COMMUNITY_CONCERN = "community_concern"
    MANUAL = "manual"


class PatrolStatus(str, Enum):
    """Patrol coverage status."""
    OVER_POLICED = "over_policed"
    UNDER_POLICED = "under_policed"
    BALANCED = "balanced"
    UNBALANCED = "unbalanced"


class GeoPoint(BaseModel):
    """Geographic point with latitude and longitude."""
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)


class PatrolZone(BaseModel):
    """Model for a patrol zone or marker."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    zone_type: ZoneType
    name: str
    description: Optional[str] = None
    center: GeoPoint
    radius_meters: float = Field(default=500, ge=50, le=5000)
    intensity: float = Field(default=0.5, ge=0, le=1)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    created_by: str
    is_active: bool = True
    metadata: Dict[str, Any] = Field(default_factory=dict)


class PatrolZoneCreate(BaseModel):
    """Request to create a patrol zone."""
    zone_type: ZoneType
    name: str
    description: Optional[str] = None
    center: GeoPoint
    radius_meters: float = Field(default=500, ge=50, le=5000)
    intensity: float = Field(default=0.5, ge=0, le=1)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SectorScore(BaseModel):
    """Patrol score for a sector."""
    sector_id: str
    sector_name: str
    patrol_intensity: float = Field(ge=0, le=1)
    status: PatrolStatus
    hourly_visits: int
    daily_visits: int
    flags: List[str] = Field(default_factory=list)


class HeatmapData(BaseModel):
    """Heatmap data for visualization."""
    zones: List[PatrolZone]
    sector_scores: List[SectorScore]
    overall_balance: float = Field(ge=0, le=1)
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    time_range_hours: int = 24


class HeatmapEngine:
    """Engine for generating patrol heatmaps and analysis."""
    
    # Riviera Beach sectors (simplified)
    SECTORS = [
        {"id": "sector_1", "name": "Downtown/Marina", "center": {"lat": 26.7754, "lng": -80.0583}},
        {"id": "sector_2", "name": "Singer Island", "center": {"lat": 26.7900, "lng": -80.0350}},
        {"id": "sector_3", "name": "Blue Heron Corridor", "center": {"lat": 26.7650, "lng": -80.0700}},
        {"id": "sector_4", "name": "Industrial District", "center": {"lat": 26.7550, "lng": -80.0800}},
        {"id": "sector_5", "name": "Residential North", "center": {"lat": 26.7850, "lng": -80.0650}},
        {"id": "sector_6", "name": "Residential South", "center": {"lat": 26.7450, "lng": -80.0650}},
    ]
    
    def __init__(self):
        self._zones: Dict[str, PatrolZone] = {}
        self._patrol_pings: List[Dict[str, Any]] = []
    
    def add_zone(self, zone: PatrolZone) -> PatrolZone:
        """Add a patrol zone."""
        self._zones[zone.id] = zone
        return zone
    
    def remove_zone(self, zone_id: str) -> bool:
        """Remove a patrol zone."""
        if zone_id in self._zones:
            del self._zones[zone_id]
            return True
        return False
    
    def get_zone(self, zone_id: str) -> Optional[PatrolZone]:
        """Get a patrol zone by ID."""
        return self._zones.get(zone_id)
    
    def get_all_zones(self, active_only: bool = True) -> List[PatrolZone]:
        """Get all patrol zones."""
        zones = list(self._zones.values())
        if active_only:
            zones = [z for z in zones if z.is_active]
        return zones
    
    def record_patrol_ping(self, officer_id: str, location: GeoPoint):
        """Record an officer location ping."""
        self._patrol_pings.append({
            "officer_id": officer_id,
            "location": location,
            "timestamp": datetime.now(UTC),
        })
        # Keep only last 24 hours of pings
        cutoff = datetime.now(UTC) - timedelta(hours=24)
        self._patrol_pings = [p for p in self._patrol_pings if p["timestamp"] > cutoff]
    
    def _calculate_distance(self, p1: GeoPoint, p2: Dict[str, float]) -> float:
        """Calculate distance between two points in meters (Haversine formula)."""
        R = 6371000  # Earth's radius in meters
        lat1, lon1 = math.radians(p1.lat), math.radians(p1.lng)
        lat2, lon2 = math.radians(p2["lat"]), math.radians(p2["lng"])
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        return R * c
    
    def _get_sector_pings(self, sector: Dict[str, Any], hours: int = 24) -> List[Dict[str, Any]]:
        """Get patrol pings within a sector."""
        cutoff = datetime.now(UTC) - timedelta(hours=hours)
        sector_center = sector["center"]
        sector_radius = 1500  # 1.5km radius for sector
        
        return [
            p for p in self._patrol_pings
            if p["timestamp"] > cutoff and
            self._calculate_distance(p["location"], sector_center) <= sector_radius
        ]
    
    def calculate_sector_scores(self) -> List[SectorScore]:
        """Calculate patrol scores for all sectors."""
        scores = []
        
        for sector in self.SECTORS:
            hourly_pings = self._get_sector_pings(sector, hours=1)
            daily_pings = self._get_sector_pings(sector, hours=24)
            
            # Calculate intensity (0-1 scale)
            # Baseline: 10 pings/hour is optimal
            hourly_intensity = min(len(hourly_pings) / 10, 1.0)
            daily_intensity = min(len(daily_pings) / 240, 1.0)  # 10 pings/hour * 24 hours
            
            intensity = (hourly_intensity + daily_intensity) / 2
            
            # Determine status
            if intensity > 0.8:
                status = PatrolStatus.OVER_POLICED
            elif intensity < 0.2:
                status = PatrolStatus.UNDER_POLICED
            elif 0.4 <= intensity <= 0.6:
                status = PatrolStatus.BALANCED
            else:
                status = PatrolStatus.UNBALANCED
            
            # Generate flags
            flags = []
            if status == PatrolStatus.OVER_POLICED:
                flags.append("Consider redistributing patrol resources")
            elif status == PatrolStatus.UNDER_POLICED:
                flags.append("Increase patrol presence recommended")
            
            # Check for zones in this sector
            for zone in self._zones.values():
                if zone.is_active:
                    dist = self._calculate_distance(zone.center, sector["center"])
                    if dist <= 1500:  # Zone is in this sector
                        if zone.zone_type == ZoneType.HIGH_CALLS:
                            flags.append(f"High-calls zone: {zone.name}")
                        elif zone.zone_type == ZoneType.VISIBILITY_GAP:
                            flags.append(f"Visibility gap: {zone.name}")
                        elif zone.zone_type == ZoneType.COMMUNITY_CONCERN:
                            flags.append(f"Community concern: {zone.name}")
            
            scores.append(SectorScore(
                sector_id=sector["id"],
                sector_name=sector["name"],
                patrol_intensity=round(intensity, 2),
                status=status,
                hourly_visits=len(hourly_pings),
                daily_visits=len(daily_pings),
                flags=flags,
            ))
        
        return scores
    
    def generate_heatmap(self, time_range_hours: int = 24) -> HeatmapData:
        """Generate complete heatmap data."""
        zones = self.get_all_zones(active_only=True)
        sector_scores = self.calculate_sector_scores()
        
        # Calculate overall balance
        intensities = [s.patrol_intensity for s in sector_scores]
        if intensities:
            avg_intensity = sum(intensities) / len(intensities)
            variance = sum((i - avg_intensity) ** 2 for i in intensities) / len(intensities)
            # Lower variance = better balance
            overall_balance = max(0, 1 - math.sqrt(variance) * 2)
        else:
            overall_balance = 0.5
        
        return HeatmapData(
            zones=zones,
            sector_scores=sector_scores,
            overall_balance=round(overall_balance, 2),
            time_range_hours=time_range_hours,
        )
