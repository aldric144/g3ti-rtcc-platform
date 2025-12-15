"""
Riviera Beach Public Camera Network Catalog.

This module contains the catalog of publicly available cameras in the
Riviera Beach area, including FDOT traffic cameras, Port of Palm Beach
cameras, Singer Island public cameras, and Marina cameras.

Each camera entry contains:
- name: Camera display name
- gps: (latitude, longitude) coordinates
- stream_url: URL for video stream (placeholder until live integration)
- type: Camera type (traffic, marine, public, beach, cctv)
- source: Data source (FDOT, Port of Palm Beach, Singer Island, Marina)
- sector: Auto-computed closest patrol zone
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
from datetime import datetime
import math


class CameraType(str, Enum):
    """Camera type classification."""
    TRAFFIC = "traffic"
    MARINE = "marine"
    PUBLIC = "public"
    BEACH = "beach"
    CCTV = "cctv"


class CameraSource(str, Enum):
    """Camera data source."""
    FDOT = "FDOT"
    PORT_OF_PALM_BEACH = "Port of Palm Beach"
    SINGER_ISLAND = "Singer Island"
    MARINA = "Marina"


# Patrol zone centers for sector computation
PATROL_ZONES = {
    "Zone-1-Downtown": (26.7753, -80.0589),
    "Zone-2-Marina": (26.7789, -80.0512),
    "Zone-3-Commercial": (26.7748, -80.0721),
    "Zone-4-Residential": (26.7698, -80.0612),
    "Zone-5-Port": (26.7634, -80.0534),
    "Zone-6-Beach": (26.7912, -80.0345),
}

# Placeholder stream URL
PLACEHOLDER_STREAM_URL = "https://via.placeholder.com/640x360?text=No+Live+Feed+Available"


def compute_closest_sector(lat: float, lng: float) -> str:
    """
    Compute the closest patrol zone/sector for a given GPS coordinate.
    
    Uses Haversine distance formula to find the nearest patrol zone center.
    """
    min_distance = float('inf')
    closest_zone = "Zone-1-Downtown"
    
    for zone_name, (zone_lat, zone_lng) in PATROL_ZONES.items():
        # Haversine formula for distance
        lat1, lat2 = math.radians(lat), math.radians(zone_lat)
        dlat = math.radians(zone_lat - lat)
        dlng = math.radians(zone_lng - lng)
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng/2)**2
        c = 2 * math.asin(math.sqrt(a))
        distance = 6371 * c  # Earth radius in km
        
        if distance < min_distance:
            min_distance = distance
            closest_zone = zone_name
    
    return closest_zone


@dataclass
class PublicCamera:
    """Public camera entry in the catalog."""
    id: str
    name: str
    latitude: float
    longitude: float
    camera_type: CameraType
    source: CameraSource
    stream_url: str = PLACEHOLDER_STREAM_URL
    sector: str = ""
    status: str = "online"
    last_updated: datetime = field(default_factory=datetime.utcnow)
    description: Optional[str] = None
    
    def __post_init__(self):
        """Auto-compute sector if not provided."""
        if not self.sector:
            self.sector = compute_closest_sector(self.latitude, self.longitude)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "gps": {
                "latitude": self.latitude,
                "longitude": self.longitude,
            },
            "stream_url": self.stream_url,
            "type": self.camera_type.value,
            "source": self.source.value,
            "sector": self.sector,
            "status": self.status,
            "last_updated": self.last_updated.isoformat(),
            "description": self.description,
        }


class PublicCameraCatalog:
    """
    Catalog of all public cameras in the Riviera Beach area.
    
    Provides methods to query, filter, and manage the camera catalog.
    """
    
    def __init__(self):
        self.cameras: list[PublicCamera] = []
        self._load_default_cameras()
    
    def _load_default_cameras(self):
        """Load the default public camera catalog."""
        
        # FDOT TRAFFIC CAMERAS (RIVIERA BEACH)
        fdot_cameras = [
            PublicCamera(
                id="fdot-001",
                name="Blue Heron @ I-95 EB",
                latitude=26.784945,
                longitude=-80.094221,
                camera_type=CameraType.TRAFFIC,
                source=CameraSource.FDOT,
                description="FDOT traffic camera at Blue Heron Blvd and I-95 Eastbound",
            ),
            PublicCamera(
                id="fdot-002",
                name="Blue Heron @ I-95 WB",
                latitude=26.784820,
                longitude=-80.095600,
                camera_type=CameraType.TRAFFIC,
                source=CameraSource.FDOT,
                description="FDOT traffic camera at Blue Heron Blvd and I-95 Westbound",
            ),
            PublicCamera(
                id="fdot-003",
                name="Blue Heron @ Broadway (US-1)",
                latitude=26.784600,
                longitude=-80.059700,
                camera_type=CameraType.TRAFFIC,
                source=CameraSource.FDOT,
                description="FDOT traffic camera at Blue Heron Blvd and Broadway (US-1)",
            ),
            PublicCamera(
                id="fdot-004",
                name="Military Trl @ Blue Heron",
                latitude=26.785000,
                longitude=-80.116000,
                camera_type=CameraType.TRAFFIC,
                source=CameraSource.FDOT,
                description="FDOT traffic camera at Military Trail and Blue Heron Blvd",
            ),
            PublicCamera(
                id="fdot-005",
                name="US-1 @ Silver Beach Rd",
                latitude=26.792900,
                longitude=-80.056900,
                camera_type=CameraType.TRAFFIC,
                source=CameraSource.FDOT,
                description="FDOT traffic camera at US-1 and Silver Beach Road",
            ),
            PublicCamera(
                id="fdot-006",
                name="US-1 @ Park Ave",
                latitude=26.778600,
                longitude=-80.056700,
                camera_type=CameraType.TRAFFIC,
                source=CameraSource.FDOT,
                description="FDOT traffic camera at US-1 and Park Avenue",
            ),
            PublicCamera(
                id="fdot-007",
                name="Congress Ave @ Blue Heron",
                latitude=26.784500,
                longitude=-80.099900,
                camera_type=CameraType.TRAFFIC,
                source=CameraSource.FDOT,
                description="FDOT traffic camera at Congress Avenue and Blue Heron Blvd",
            ),
        ]
        
        # PORT OF PALM BEACH CAMERAS
        port_cameras = [
            PublicCamera(
                id="port-001",
                name="Port South Gate Cam",
                latitude=26.777830,
                longitude=-80.054260,
                camera_type=CameraType.MARINE,
                source=CameraSource.PORT_OF_PALM_BEACH,
                description="Port of Palm Beach south gate security camera",
            ),
            PublicCamera(
                id="port-002",
                name="Port Main Entrance Cam",
                latitude=26.779100,
                longitude=-80.058200,
                camera_type=CameraType.CCTV,
                source=CameraSource.PORT_OF_PALM_BEACH,
                description="Port of Palm Beach main entrance security camera",
            ),
        ]
        
        # SINGER ISLAND PUBLIC CAMERAS
        singer_island_cameras = [
            PublicCamera(
                id="singer-001",
                name="Singer Island Beach Cam",
                latitude=26.778000,
                longitude=-80.032500,
                camera_type=CameraType.BEACH,
                source=CameraSource.SINGER_ISLAND,
                description="Public beach camera on Singer Island",
            ),
            PublicCamera(
                id="singer-002",
                name="Palm Beach Shores Inlet Cam",
                latitude=26.774000,
                longitude=-80.038100,
                camera_type=CameraType.MARINE,
                source=CameraSource.SINGER_ISLAND,
                description="Palm Beach Shores inlet marine camera",
            ),
        ]
        
        # RIVIERA BEACH MARINA CAMERAS
        marina_cameras = [
            PublicCamera(
                id="marina-001",
                name="Marina Harbor Cam",
                latitude=26.772871,
                longitude=-80.050105,
                camera_type=CameraType.MARINE,
                source=CameraSource.MARINA,
                description="Riviera Beach Marina harbor overview camera",
            ),
            PublicCamera(
                id="marina-002",
                name="Marina Fuel Dock Cam",
                latitude=26.772300,
                longitude=-80.050800,
                camera_type=CameraType.CCTV,
                source=CameraSource.MARINA,
                description="Riviera Beach Marina fuel dock security camera",
            ),
        ]
        
        # Add all cameras to the catalog
        self.cameras.extend(fdot_cameras)
        self.cameras.extend(port_cameras)
        self.cameras.extend(singer_island_cameras)
        self.cameras.extend(marina_cameras)
    
    def get_all(self) -> list[dict]:
        """Get all cameras as a list of dictionaries."""
        return [camera.to_dict() for camera in self.cameras]
    
    def get_by_id(self, camera_id: str) -> Optional[dict]:
        """Get a camera by its ID."""
        for camera in self.cameras:
            if camera.id == camera_id:
                return camera.to_dict()
        return None
    
    def get_by_type(self, camera_type: CameraType) -> list[dict]:
        """Get all cameras of a specific type."""
        return [
            camera.to_dict()
            for camera in self.cameras
            if camera.camera_type == camera_type
        ]
    
    def get_by_source(self, source: CameraSource) -> list[dict]:
        """Get all cameras from a specific source."""
        return [
            camera.to_dict()
            for camera in self.cameras
            if camera.source == source
        ]
    
    def get_by_sector(self, sector: str) -> list[dict]:
        """Get all cameras in a specific patrol sector."""
        return [
            camera.to_dict()
            for camera in self.cameras
            if camera.sector == sector
        ]
    
    def add_camera(self, camera: PublicCamera) -> dict:
        """Add a new camera to the catalog."""
        self.cameras.append(camera)
        return camera.to_dict()
    
    def update_camera(self, camera_id: str, updates: dict) -> Optional[dict]:
        """Update an existing camera in the catalog."""
        for i, camera in enumerate(self.cameras):
            if camera.id == camera_id:
                # Update allowed fields
                if "name" in updates:
                    camera.name = updates["name"]
                if "stream_url" in updates:
                    camera.stream_url = updates["stream_url"]
                if "status" in updates:
                    camera.status = updates["status"]
                if "description" in updates:
                    camera.description = updates["description"]
                camera.last_updated = datetime.utcnow()
                return camera.to_dict()
        return None
    
    def delete_camera(self, camera_id: str) -> bool:
        """Delete a camera from the catalog."""
        for i, camera in enumerate(self.cameras):
            if camera.id == camera_id:
                self.cameras.pop(i)
                return True
        return False
    
    def get_stats(self) -> dict:
        """Get catalog statistics."""
        type_counts = {}
        source_counts = {}
        sector_counts = {}
        
        for camera in self.cameras:
            # Count by type
            type_key = camera.camera_type.value
            type_counts[type_key] = type_counts.get(type_key, 0) + 1
            
            # Count by source
            source_key = camera.source.value
            source_counts[source_key] = source_counts.get(source_key, 0) + 1
            
            # Count by sector
            sector_counts[camera.sector] = sector_counts.get(camera.sector, 0) + 1
        
        online_count = sum(1 for c in self.cameras if c.status == "online")
        
        return {
            "total_cameras": len(self.cameras),
            "online_cameras": online_count,
            "offline_cameras": len(self.cameras) - online_count,
            "by_type": type_counts,
            "by_source": source_counts,
            "by_sector": sector_counts,
        }


# Singleton instance
_catalog_instance: Optional[PublicCameraCatalog] = None


def get_public_camera_catalog() -> PublicCameraCatalog:
    """Get the singleton public camera catalog instance."""
    global _catalog_instance
    if _catalog_instance is None:
        _catalog_instance = PublicCameraCatalog()
    return _catalog_instance
