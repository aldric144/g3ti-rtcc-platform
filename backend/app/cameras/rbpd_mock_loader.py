"""
RBPD Internal Mock Camera Network Loader for G3TI RTCC-UIP Platform.

This module loads a set of mock but realistic RBPD cameras for RTCC testing.
All cameras are assigned to specific sectors and include realistic metadata.

Camera Types:
- CCTV: Fixed position surveillance cameras
- PTZ: Pan-Tilt-Zoom controllable cameras
- LPR: License Plate Recognition cameras

Jurisdiction: RBPD (Riviera Beach Police Department)
"""

import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import List, Dict, Any, Optional
from enum import Enum


class RBPDCameraType(str, Enum):
    """Camera type enumeration for RBPD cameras."""
    CCTV = "CCTV"
    PTZ = "PTZ"
    LPR = "LPR"


PLACEHOLDER_STREAM_URL = "https://via.placeholder.com/640x360?text=RBPD+Camera"


@dataclass
class RBPDMockCamera:
    """
    RBPD Mock Camera data class.
    
    Represents a single RBPD internal camera with all required metadata.
    """
    name: str
    latitude: float
    longitude: float
    assigned_sector: str
    camera_type: RBPDCameraType
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    jurisdiction: str = "RBPD"
    stream_url: str = PLACEHOLDER_STREAM_URL
    status: str = "online"
    source: str = "rbpd_mock"
    description: str = ""
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert camera to dictionary format."""
        return {
            "id": self.id,
            "name": self.name,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "gps": {
                "latitude": self.latitude,
                "longitude": self.longitude,
            },
            "assigned_sector": self.assigned_sector,
            "sector": self.assigned_sector,
            "camera_type": self.camera_type.value if isinstance(self.camera_type, RBPDCameraType) else self.camera_type,
            "type": self.camera_type.value if isinstance(self.camera_type, RBPDCameraType) else self.camera_type,
            "jurisdiction": self.jurisdiction,
            "stream_url": self.stream_url,
            "status": self.status,
            "source": self.source,
            "description": self.description,
            "created_at": self.created_at,
        }


# ============================================================================
# RBPD HEADQUARTERS CAMERAS - 600 W Blue Heron Blvd
# ============================================================================

RBPD_HQ_CAMERAS = [
    RBPDMockCamera(
        name="RBPD HQ - Front Entrance Cam",
        latitude=26.784110,
        longitude=-80.072180,
        assigned_sector="HQ",
        camera_type=RBPDCameraType.PTZ,
        description="Main entrance surveillance - 600 W Blue Heron Blvd",
    ),
    RBPDMockCamera(
        name="RBPD HQ - Lobby Cam",
        latitude=26.784120,
        longitude=-80.072150,
        assigned_sector="HQ",
        camera_type=RBPDCameraType.CCTV,
        description="Lobby interior surveillance",
    ),
    RBPDMockCamera(
        name="RBPD HQ - Sally Port Cam",
        latitude=26.784270,
        longitude=-80.072260,
        assigned_sector="HQ",
        camera_type=RBPDCameraType.CCTV,
        description="Sally port vehicle entry surveillance",
    ),
    RBPDMockCamera(
        name="RBPD HQ - Detention Wing Cam",
        latitude=26.784300,
        longitude=-80.072300,
        assigned_sector="HQ",
        camera_type=RBPDCameraType.CCTV,
        description="Detention wing corridor surveillance",
    ),
    RBPDMockCamera(
        name="RBPD HQ - Parking Lot North",
        latitude=26.784350,
        longitude=-80.072120,
        assigned_sector="HQ",
        camera_type=RBPDCameraType.CCTV,
        description="North parking lot surveillance",
    ),
    RBPDMockCamera(
        name="RBPD HQ - Parking Lot South",
        latitude=26.784010,
        longitude=-80.072340,
        assigned_sector="HQ",
        camera_type=RBPDCameraType.CCTV,
        description="South parking lot surveillance",
    ),
]


# ============================================================================
# SECTOR 1 CAMERAS - Broadway / Park Ave / US-1
# ============================================================================

SECTOR_1_CAMERAS = [
    RBPDMockCamera(
        name="Sector 1 - Park Ave & Broadway",
        latitude=26.7755,
        longitude=-80.0580,
        assigned_sector="Sector 1",
        camera_type=RBPDCameraType.PTZ,
        description="Park Ave & Broadway intersection - high traffic area",
    ),
    RBPDMockCamera(
        name="Sector 1 - 30th St & Broadway",
        latitude=26.7820,
        longitude=-80.0575,
        assigned_sector="Sector 1",
        camera_type=RBPDCameraType.CCTV,
        description="30th St & Broadway intersection surveillance",
    ),
    RBPDMockCamera(
        name="Sector 1 - 13th St Apartments",
        latitude=26.7680,
        longitude=-80.0590,
        assigned_sector="Sector 1",
        camera_type=RBPDCameraType.CCTV,
        description="13th St apartment complex surveillance",
    ),
    RBPDMockCamera(
        name="Sector 1 - 21st St & A Ave LPR",
        latitude=26.7740,
        longitude=-80.0600,
        assigned_sector="Sector 1",
        camera_type=RBPDCameraType.LPR,
        description="License plate recognition - 21st St & A Ave",
    ),
]


# ============================================================================
# SECTOR 2 CAMERAS - Avenue S / W10th / Avenue E
# ============================================================================

SECTOR_2_CAMERAS = [
    RBPDMockCamera(
        name="Sector 2 - West 10th St Corridor",
        latitude=26.7650,
        longitude=-80.0720,
        assigned_sector="Sector 2",
        camera_type=RBPDCameraType.CCTV,
        description="West 10th St corridor surveillance",
    ),
    RBPDMockCamera(
        name="Sector 2 - Wells Recreation Center",
        latitude=26.7680,
        longitude=-80.0750,
        assigned_sector="Sector 2",
        camera_type=RBPDCameraType.PTZ,
        description="Wells Recreation Center exterior surveillance",
    ),
    RBPDMockCamera(
        name="Sector 2 - MLK Blvd @ Ave S",
        latitude=26.7620,
        longitude=-80.0700,
        assigned_sector="Sector 2",
        camera_type=RBPDCameraType.CCTV,
        description="MLK Blvd & Avenue S intersection",
    ),
]


# ============================================================================
# SECTOR 3 CAMERAS - Blue Heron West
# ============================================================================

SECTOR_3_CAMERAS = [
    RBPDMockCamera(
        name="Sector 3 - Blue Heron & Australian",
        latitude=26.7840,
        longitude=-80.0850,
        assigned_sector="Sector 3",
        camera_type=RBPDCameraType.PTZ,
        description="Blue Heron Blvd & Australian Ave intersection",
    ),
    RBPDMockCamera(
        name="Sector 3 - Avenue P & West 28th",
        latitude=26.7800,
        longitude=-80.0800,
        assigned_sector="Sector 3",
        camera_type=RBPDCameraType.CCTV,
        description="Avenue P & West 28th St intersection",
    ),
    RBPDMockCamera(
        name="Sector 3 - Congress Ave Apartments",
        latitude=26.7860,
        longitude=-80.0900,
        assigned_sector="Sector 3",
        camera_type=RBPDCameraType.PTZ,
        description="Congress Ave apartment complex surveillance",
    ),
]


# ============================================================================
# SECTOR 4 CAMERAS - Marina District
# ============================================================================

SECTOR_4_CAMERAS = [
    RBPDMockCamera(
        name="Sector 4 - Marina Event Lawn",
        latitude=26.7750,
        longitude=-80.0480,
        assigned_sector="Sector 4",
        camera_type=RBPDCameraType.PTZ,
        description="Marina Event Lawn public area surveillance",
    ),
    RBPDMockCamera(
        name="Sector 4 - Bicentennial Park",
        latitude=26.7780,
        longitude=-80.0500,
        assigned_sector="Sector 4",
        camera_type=RBPDCameraType.CCTV,
        description="Bicentennial Park surveillance",
    ),
    RBPDMockCamera(
        name="Sector 4 - Marina Boat Ramp",
        latitude=26.7720,
        longitude=-80.0460,
        assigned_sector="Sector 4",
        camera_type=RBPDCameraType.PTZ,
        description="Marina boat ramp and dock surveillance",
    ),
]


# ============================================================================
# SECTOR 5 CAMERAS - Singer Island
# ============================================================================

SECTOR_5_CAMERAS = [
    RBPDMockCamera(
        name="Sector 5 - Ocean Reef Park",
        latitude=26.8100,
        longitude=-80.0350,
        assigned_sector="Sector 5",
        camera_type=RBPDCameraType.CCTV,
        description="Ocean Reef Park beach surveillance",
    ),
    RBPDMockCamera(
        name="Sector 5 - Riviera Municipal Beach",
        latitude=26.8050,
        longitude=-80.0380,
        assigned_sector="Sector 5",
        camera_type=RBPDCameraType.PTZ,
        description="Riviera Municipal Beach surveillance",
    ),
    RBPDMockCamera(
        name="Sector 5 - Phil Foster Park Underwater Camera",
        latitude=26.7900,
        longitude=-80.0420,
        assigned_sector="Sector 5",
        camera_type=RBPDCameraType.CCTV,
        description="Phil Foster Park underwater camera (mock)",
    ),
]


# ============================================================================
# COMBINED CAMERA LIST
# ============================================================================

ALL_RBPD_MOCK_CAMERAS = (
    RBPD_HQ_CAMERAS +
    SECTOR_1_CAMERAS +
    SECTOR_2_CAMERAS +
    SECTOR_3_CAMERAS +
    SECTOR_4_CAMERAS +
    SECTOR_5_CAMERAS
)


def load_rbpd_mock_cameras() -> List[Dict[str, Any]]:
    """
    Load all RBPD mock cameras.
    
    Returns:
        List of camera dictionaries with all required metadata.
    """
    return [camera.to_dict() for camera in ALL_RBPD_MOCK_CAMERAS]


def get_rbpd_cameras_by_sector(sector: str) -> List[Dict[str, Any]]:
    """
    Get RBPD cameras filtered by sector.
    
    Args:
        sector: Sector name to filter by (e.g., "Sector 1", "HQ")
        
    Returns:
        List of camera dictionaries in the specified sector.
    """
    return [
        camera.to_dict() 
        for camera in ALL_RBPD_MOCK_CAMERAS 
        if camera.assigned_sector == sector
    ]


def get_rbpd_cameras_by_type(camera_type: str) -> List[Dict[str, Any]]:
    """
    Get RBPD cameras filtered by type.
    
    Args:
        camera_type: Camera type to filter by ("CCTV", "PTZ", "LPR")
        
    Returns:
        List of camera dictionaries of the specified type.
    """
    return [
        camera.to_dict() 
        for camera in ALL_RBPD_MOCK_CAMERAS 
        if camera.camera_type.value == camera_type
    ]


def get_rbpd_camera_stats() -> Dict[str, Any]:
    """
    Get statistics about RBPD mock cameras.
    
    Returns:
        Dictionary with camera statistics.
    """
    cameras = ALL_RBPD_MOCK_CAMERAS
    
    # Count by sector
    sectors = {}
    for camera in cameras:
        sector = camera.assigned_sector
        sectors[sector] = sectors.get(sector, 0) + 1
    
    # Count by type
    types = {}
    for camera in cameras:
        cam_type = camera.camera_type.value
        types[cam_type] = types.get(cam_type, 0) + 1
    
    return {
        "total_cameras": len(cameras),
        "by_sector": sectors,
        "by_type": types,
        "jurisdiction": "RBPD",
        "source": "rbpd_mock",
    }


# Singleton instance for caching
_rbpd_cameras_cache: Optional[List[Dict[str, Any]]] = None


def get_cached_rbpd_cameras() -> List[Dict[str, Any]]:
    """
    Get cached RBPD cameras (singleton pattern).
    
    Returns:
        List of camera dictionaries.
    """
    global _rbpd_cameras_cache
    if _rbpd_cameras_cache is None:
        _rbpd_cameras_cache = load_rbpd_mock_cameras()
    return _rbpd_cameras_cache


def refresh_rbpd_cameras() -> List[Dict[str, Any]]:
    """
    Refresh the RBPD cameras cache.
    
    Returns:
        List of camera dictionaries.
    """
    global _rbpd_cameras_cache
    _rbpd_cameras_cache = load_rbpd_mock_cameras()
    return _rbpd_cameras_cache
