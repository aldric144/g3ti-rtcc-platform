"""
RBPD Internal Mock Camera Network Loader for G3TI RTCC-UIP Platform.

Loads 25+ mock RBPD cameras with realistic Riviera Beach locations.
Makes the RTCC look like a real live city system.
"""

import uuid
from datetime import datetime
from typing import List, Dict, Any


# Placeholder stream URL for mock cameras
PLACEHOLDER_STREAM_URL = "https://via.placeholder.com/640x360?text=RBPD+Camera"


# ============================================================================
# RBPD HEADQUARTERS CAMERAS - 600 W Blue Heron Blvd
# ============================================================================

RBPD_HQ_CAMERAS = [
    {
        "name": "RBPD HQ - Front Entrance",
        "latitude": 26.784110,
        "longitude": -80.072180,
        "camera_type": "ptz",
        "address": "600 W Blue Heron Blvd",
        "description": "Main entrance surveillance",
    },
    {
        "name": "RBPD HQ - Lobby",
        "latitude": 26.784120,
        "longitude": -80.072150,
        "camera_type": "cctv",
        "address": "600 W Blue Heron Blvd",
        "description": "Lobby interior surveillance",
    },
    {
        "name": "RBPD HQ - Sally Port",
        "latitude": 26.784270,
        "longitude": -80.072260,
        "camera_type": "cctv",
        "address": "600 W Blue Heron Blvd",
        "description": "Sally port vehicle entry",
    },
    {
        "name": "RBPD HQ - Detention Wing",
        "latitude": 26.784300,
        "longitude": -80.072300,
        "camera_type": "cctv",
        "address": "600 W Blue Heron Blvd",
        "description": "Detention wing corridor",
    },
    {
        "name": "RBPD HQ - Parking North",
        "latitude": 26.784350,
        "longitude": -80.072120,
        "camera_type": "cctv",
        "address": "600 W Blue Heron Blvd",
        "description": "North parking lot",
    },
    {
        "name": "RBPD HQ - Parking South",
        "latitude": 26.784010,
        "longitude": -80.072340,
        "camera_type": "cctv",
        "address": "600 W Blue Heron Blvd",
        "description": "South parking lot",
    },
]


# ============================================================================
# AVENUE E CAMERAS
# ============================================================================

AVENUE_E_CAMERAS = [
    {
        "name": "Avenue E @ 13th St",
        "latitude": 26.7680,
        "longitude": -80.0620,
        "camera_type": "lpr",
        "address": "Avenue E & 13th St",
        "description": "LPR camera at Avenue E intersection",
    },
    {
        "name": "Avenue E @ 21st St",
        "latitude": 26.7740,
        "longitude": -80.0615,
        "camera_type": "lpr",
        "address": "Avenue E & 21st St",
        "description": "LPR camera monitoring traffic",
    },
]


# ============================================================================
# BLUE HERON BLVD CAMERAS
# ============================================================================

BLUE_HERON_CAMERAS = [
    {
        "name": "Blue Heron @ Broadway",
        "latitude": 26.7841,
        "longitude": -80.0580,
        "camera_type": "ptz",
        "address": "Blue Heron Blvd & Broadway",
        "description": "PTZ camera at major intersection",
    },
    {
        "name": "Blue Heron @ Congress",
        "latitude": 26.7841,
        "longitude": -80.0950,
        "camera_type": "lpr",
        "address": "Blue Heron Blvd & Congress Ave",
        "description": "LPR camera westbound",
    },
    {
        "name": "Blue Heron @ Australian",
        "latitude": 26.7840,
        "longitude": -80.0850,
        "camera_type": "ptz",
        "address": "Blue Heron Blvd & Australian Ave",
        "description": "PTZ camera at intersection",
    },
]


# ============================================================================
# BROADWAY CAMERAS
# ============================================================================

BROADWAY_CAMERAS = [
    {
        "name": "Broadway @ Park Ave",
        "latitude": 26.7755,
        "longitude": -80.0580,
        "camera_type": "ptz",
        "address": "Broadway & Park Ave",
        "description": "PTZ camera at Park Ave intersection",
    },
    {
        "name": "Broadway @ 30th St",
        "latitude": 26.7820,
        "longitude": -80.0575,
        "camera_type": "cctv",
        "address": "Broadway & 30th St",
        "description": "Fixed camera monitoring Broadway",
    },
    {
        "name": "Broadway @ 13th St",
        "latitude": 26.7680,
        "longitude": -80.0590,
        "camera_type": "lpr",
        "address": "Broadway & 13th St",
        "description": "LPR camera southbound",
    },
]


# ============================================================================
# MLK BLVD CAMERAS
# ============================================================================

MLK_CAMERAS = [
    {
        "name": "MLK Blvd @ Avenue S",
        "latitude": 26.7620,
        "longitude": -80.0700,
        "camera_type": "cctv",
        "address": "MLK Blvd & Avenue S",
        "description": "Fixed camera at MLK intersection",
    },
    {
        "name": "MLK Blvd @ 10th St",
        "latitude": 26.7650,
        "longitude": -80.0720,
        "camera_type": "lpr",
        "address": "MLK Blvd & 10th St",
        "description": "LPR camera monitoring MLK corridor",
    },
]


# ============================================================================
# RIVIERA BEACH MARINA CAMERAS
# ============================================================================

MARINA_CAMERAS = [
    {
        "name": "Marina Event Lawn",
        "latitude": 26.7750,
        "longitude": -80.0480,
        "camera_type": "ptz",
        "address": "Riviera Beach Marina",
        "description": "PTZ camera at event lawn",
    },
    {
        "name": "Marina Boat Ramp",
        "latitude": 26.7720,
        "longitude": -80.0460,
        "camera_type": "ptz",
        "address": "Riviera Beach Marina",
        "description": "PTZ camera at boat ramp",
    },
    {
        "name": "Marina Parking Lot",
        "latitude": 26.7740,
        "longitude": -80.0490,
        "camera_type": "lpr",
        "address": "Riviera Beach Marina",
        "description": "LPR camera at marina parking",
    },
]


# ============================================================================
# 13TH STREET CAMERAS
# ============================================================================

THIRTEENTH_ST_CAMERAS = [
    {
        "name": "13th St Apartments",
        "latitude": 26.7680,
        "longitude": -80.0590,
        "camera_type": "cctv",
        "address": "13th St",
        "description": "Apartment complex surveillance",
    },
    {
        "name": "13th St @ Avenue D",
        "latitude": 26.7680,
        "longitude": -80.0640,
        "camera_type": "lpr",
        "address": "13th St & Avenue D",
        "description": "LPR camera at intersection",
    },
]


# ============================================================================
# WELLS RECREATION AREA CAMERAS
# ============================================================================

WELLS_REC_CAMERAS = [
    {
        "name": "Wells Recreation Center",
        "latitude": 26.7680,
        "longitude": -80.0750,
        "camera_type": "ptz",
        "address": "Wells Recreation Center",
        "description": "PTZ camera at recreation center",
    },
    {
        "name": "Wells Park Entrance",
        "latitude": 26.7685,
        "longitude": -80.0745,
        "camera_type": "cctv",
        "address": "Wells Recreation Center",
        "description": "Park entrance surveillance",
    },
]


# ============================================================================
# CITY HALL CAMERAS
# ============================================================================

CITY_HALL_CAMERAS = [
    {
        "name": "City Hall Main Entrance",
        "latitude": 26.7760,
        "longitude": -80.0560,
        "camera_type": "cctv",
        "address": "600 W Blue Heron Blvd",
        "description": "City Hall main entrance",
    },
    {
        "name": "City Hall Parking",
        "latitude": 26.7755,
        "longitude": -80.0565,
        "camera_type": "lpr",
        "address": "600 W Blue Heron Blvd",
        "description": "City Hall parking lot LPR",
    },
]


# ============================================================================
# FIRE STATION 87 CAMERAS
# ============================================================================

FIRE_STATION_CAMERAS = [
    {
        "name": "Fire Station 87",
        "latitude": 26.7800,
        "longitude": -80.0600,
        "camera_type": "cctv",
        "address": "Fire Station 87",
        "description": "Fire station exterior",
    },
]


# ============================================================================
# WAWA / COMMERCIAL CAMERAS
# ============================================================================

COMMERCIAL_CAMERAS = [
    {
        "name": "Wawa Blue Heron",
        "latitude": 26.7845,
        "longitude": -80.0700,
        "camera_type": "cctv",
        "address": "Blue Heron Blvd",
        "description": "Wawa convenience store area",
    },
    {
        "name": "Publix Plaza",
        "latitude": 26.7830,
        "longitude": -80.0650,
        "camera_type": "cctv",
        "address": "Blue Heron Blvd",
        "description": "Publix shopping plaza",
    },
]


# ============================================================================
# HATCHER PARK CAMERAS
# ============================================================================

HATCHER_PARK_CAMERAS = [
    {
        "name": "Hatcher Park Main",
        "latitude": 26.7700,
        "longitude": -80.0680,
        "camera_type": "cctv",
        "address": "Hatcher Park",
        "description": "Hatcher Park main area",
    },
    {
        "name": "Hatcher Park Playground",
        "latitude": 26.7705,
        "longitude": -80.0675,
        "camera_type": "cctv",
        "address": "Hatcher Park",
        "description": "Playground surveillance",
    },
]


# ============================================================================
# SINGER ISLAND / BEACH CAMERAS
# ============================================================================

SINGER_ISLAND_CAMERAS = [
    {
        "name": "Ocean Reef Park",
        "latitude": 26.8100,
        "longitude": -80.0350,
        "camera_type": "cctv",
        "address": "Singer Island",
        "description": "Ocean Reef Park beach",
    },
    {
        "name": "Riviera Municipal Beach",
        "latitude": 26.8050,
        "longitude": -80.0380,
        "camera_type": "ptz",
        "address": "Singer Island",
        "description": "Municipal beach PTZ",
    },
    {
        "name": "Phil Foster Park",
        "latitude": 26.7900,
        "longitude": -80.0420,
        "camera_type": "cctv",
        "address": "Phil Foster Park",
        "description": "Phil Foster Park surveillance",
    },
]


# ============================================================================
# BICENTENNIAL PARK CAMERAS
# ============================================================================

BICENTENNIAL_CAMERAS = [
    {
        "name": "Bicentennial Park Main",
        "latitude": 26.7780,
        "longitude": -80.0500,
        "camera_type": "cctv",
        "address": "Bicentennial Park",
        "description": "Main park area",
    },
    {
        "name": "Bicentennial Park Pavilion",
        "latitude": 26.7785,
        "longitude": -80.0505,
        "camera_type": "cctv",
        "address": "Bicentennial Park",
        "description": "Pavilion area",
    },
]


# ============================================================================
# COMBINED CAMERA LIST
# ============================================================================

ALL_RBPD_CAMERAS = (
    RBPD_HQ_CAMERAS +
    AVENUE_E_CAMERAS +
    BLUE_HERON_CAMERAS +
    BROADWAY_CAMERAS +
    MLK_CAMERAS +
    MARINA_CAMERAS +
    THIRTEENTH_ST_CAMERAS +
    WELLS_REC_CAMERAS +
    CITY_HALL_CAMERAS +
    FIRE_STATION_CAMERAS +
    COMMERCIAL_CAMERAS +
    HATCHER_PARK_CAMERAS +
    SINGER_ISLAND_CAMERAS +
    BICENTENNIAL_CAMERAS
)


def _compute_sector(lat: float, lng: float) -> str:
    """
    Compute patrol sector based on GPS coordinates.
    
    Args:
        lat: Latitude.
        lng: Longitude.
        
    Returns:
        Sector name.
    """
    if lat > 26.80:
        return "Sector 5"  # Singer Island / North
    elif lat > 26.78:
        if lng < -80.08:
            return "Sector 3"  # Blue Heron West
        elif lng < -80.05:
            return "HQ"  # RBPD HQ area
        else:
            return "Sector 4"  # Marina District
    elif lat > 26.76:
        if lng < -80.07:
            return "Sector 2"  # Avenue S / W10th
        else:
            return "Sector 1"  # Broadway / Park Ave
    else:
        return "Sector 1"  # Default


def load_rbpd_mock_cameras() -> List[Dict[str, Any]]:
    """
    Load all RBPD mock cameras.
    
    Returns:
        List of camera dictionaries with all required metadata.
    """
    cameras = []
    
    for i, cam in enumerate(ALL_RBPD_CAMERAS):
        camera = {
            "id": f"rbpd-{i+1:03d}",
            "name": cam["name"],
            "latitude": cam["latitude"],
            "longitude": cam["longitude"],
            "gps": {
                "latitude": cam["latitude"],
                "longitude": cam["longitude"],
            },
            "stream_url": PLACEHOLDER_STREAM_URL,
            "camera_type": cam["camera_type"],
            "type": cam["camera_type"],
            "jurisdiction": "RBPD",
            "address": cam.get("address", ""),
            "sector": _compute_sector(cam["latitude"], cam["longitude"]),
            "status": "online",
            "description": cam.get("description", ""),
            "source_priority": 100,  # Highest priority
            "created_at": datetime.utcnow().isoformat(),
        }
        cameras.append(camera)
    
    return cameras


def get_rbpd_camera_count() -> int:
    """Get total count of RBPD mock cameras."""
    return len(ALL_RBPD_CAMERAS)


def get_rbpd_cameras_by_sector(sector: str) -> List[Dict[str, Any]]:
    """Get RBPD cameras filtered by sector."""
    all_cameras = load_rbpd_mock_cameras()
    return [c for c in all_cameras if c.get("sector") == sector]


def get_rbpd_cameras_by_type(camera_type: str) -> List[Dict[str, Any]]:
    """Get RBPD cameras filtered by type."""
    all_cameras = load_rbpd_mock_cameras()
    return [c for c in all_cameras if c.get("camera_type") == camera_type]


def get_rbpd_camera_stats() -> Dict[str, Any]:
    """Get statistics about RBPD mock cameras."""
    cameras = load_rbpd_mock_cameras()
    
    by_sector = {}
    by_type = {}
    
    for cam in cameras:
        sector = cam.get("sector", "Unknown")
        by_sector[sector] = by_sector.get(sector, 0) + 1
        
        cam_type = cam.get("camera_type", "Unknown")
        by_type[cam_type] = by_type.get(cam_type, 0) + 1
    
    return {
        "total_cameras": len(cameras),
        "by_sector": by_sector,
        "by_type": by_type,
        "jurisdiction": "RBPD",
        "ptz_count": by_type.get("ptz", 0),
        "lpr_count": by_type.get("lpr", 0),
        "cctv_count": by_type.get("cctv", 0),
    }
