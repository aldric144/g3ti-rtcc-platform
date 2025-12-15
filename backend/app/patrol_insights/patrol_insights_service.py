"""
Patrol Insights Service - Business Logic for Patrol Analysis

Provides patrol heatmap generation and zone management.
"""

from typing import List, Optional
import structlog

from .heatmap_engine import (
    HeatmapEngine,
    PatrolZone,
    PatrolZoneCreate,
    HeatmapData,
    GeoPoint,
)

logger = structlog.get_logger(__name__)


class PatrolInsightsService:
    """Service for managing patrol insights and heatmaps."""
    
    def __init__(self):
        self._engine = HeatmapEngine()
    
    async def get_insights(self, time_range_hours: int = 24) -> HeatmapData:
        """Get patrol insights and heatmap data."""
        return self._engine.generate_heatmap(time_range_hours)
    
    async def create_manual_zone(self, data: PatrolZoneCreate, created_by: str) -> PatrolZone:
        """Create a manual patrol zone marker."""
        zone = PatrolZone(
            zone_type=data.zone_type,
            name=data.name,
            description=data.description,
            center=data.center,
            radius_meters=data.radius_meters,
            intensity=data.intensity,
            created_by=created_by,
            metadata=data.metadata,
        )
        
        self._engine.add_zone(zone)
        logger.info("patrol_zone_created", zone_id=zone.id, zone_type=data.zone_type.value, created_by=created_by)
        
        return zone
    
    async def delete_manual_zone(self, zone_id: str, deleted_by: str) -> bool:
        """Delete a manual patrol zone."""
        success = self._engine.remove_zone(zone_id)
        if success:
            logger.info("patrol_zone_deleted", zone_id=zone_id, deleted_by=deleted_by)
        return success
    
    async def get_zone(self, zone_id: str) -> Optional[PatrolZone]:
        """Get a specific patrol zone."""
        return self._engine.get_zone(zone_id)
    
    async def get_all_zones(self, active_only: bool = True) -> List[PatrolZone]:
        """Get all patrol zones."""
        return self._engine.get_all_zones(active_only)
    
    async def record_patrol_ping(self, officer_id: str, lat: float, lng: float):
        """Record an officer location ping."""
        self._engine.record_patrol_ping(officer_id, GeoPoint(lat=lat, lng=lng))
        logger.debug("patrol_ping_recorded", officer_id=officer_id, lat=lat, lng=lng)


# Singleton instance for SAFE_MODE operation
_patrol_insights_service: Optional[PatrolInsightsService] = None


def get_patrol_insights_service() -> PatrolInsightsService:
    """Get the patrol insights service instance."""
    global _patrol_insights_service
    if _patrol_insights_service is None:
        _patrol_insights_service = PatrolInsightsService()
    return _patrol_insights_service
