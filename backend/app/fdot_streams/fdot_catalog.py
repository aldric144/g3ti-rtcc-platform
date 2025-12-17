"""
FDOT Camera Catalog for Live Streaming.

Contains hardcoded catalog of 10 FDOT cameras in the Riviera Beach / Palm Beach area.
Each camera includes id, name, location, lat, lng, and stream_url fields.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class FDOTStreamCamera:
    id: str
    name: str
    location: str
    lat: float
    lng: float
    stream_url: str
    description: str = ""


FDOT_STREAM_CAMERAS: List[Dict[str, Any]] = [
    {
        "id": "fdot-stream-001",
        "name": "I-95 @ Blue Heron Blvd",
        "location": "Blue Heron Blvd & I-95",
        "lat": 26.784945,
        "lng": -80.094221,
        "stream_url": "https://fl511.com/map/Cctv/CCTV-D4-I95-026.5-N--1",
        "description": "FDOT District 4 - I-95 Northbound at Blue Heron Blvd",
    },
    {
        "id": "fdot-stream-002",
        "name": "I-95 @ Palm Beach Lakes Blvd",
        "location": "Palm Beach Lakes Blvd & I-95",
        "lat": 26.7150,
        "lng": -80.0750,
        "stream_url": "https://fl511.com/map/Cctv/CCTV-D4-I95-021.0-N--1",
        "description": "FDOT District 4 - I-95 at Palm Beach Lakes Blvd",
    },
    {
        "id": "fdot-stream-003",
        "name": "Blue Heron @ Broadway (US-1)",
        "location": "Blue Heron Blvd & US-1",
        "lat": 26.7846,
        "lng": -80.0597,
        "stream_url": "https://fl511.com/map/Cctv/CCTV-D4-US1-076.0-N--1",
        "description": "FDOT District 4 - Blue Heron at Broadway (US-1)",
    },
    {
        "id": "fdot-stream-004",
        "name": "I-95 @ 45th Street",
        "location": "45th Street & I-95",
        "lat": 26.7950,
        "lng": -80.0680,
        "stream_url": "https://fl511.com/map/Cctv/CCTV-D4-I95-028.0-N--1",
        "description": "FDOT District 4 - I-95 at 45th Street",
    },
    {
        "id": "fdot-stream-005",
        "name": "Southern Blvd @ I-95",
        "location": "Southern Blvd & I-95",
        "lat": 26.6850,
        "lng": -80.0720,
        "stream_url": "https://fl511.com/map/Cctv/CCTV-D4-I95-018.0-N--1",
        "description": "FDOT District 4 - Southern Blvd at I-95",
    },
    {
        "id": "fdot-stream-006",
        "name": "I-95 @ PGA Blvd",
        "location": "PGA Blvd & I-95",
        "lat": 26.8334,
        "lng": -80.0889,
        "stream_url": "https://fl511.com/map/Cctv/CCTV-D4-I95-031.0-N--1",
        "description": "FDOT District 4 - I-95 at PGA Blvd",
    },
    {
        "id": "fdot-stream-007",
        "name": "Military Trail @ Blue Heron",
        "location": "Military Trail & Blue Heron Blvd",
        "lat": 26.785,
        "lng": -80.116,
        "stream_url": "https://fl511.com/map/Cctv/CCTV-D4-SR710-001.0-E--1",
        "description": "FDOT District 4 - Military Trail at Blue Heron",
    },
    {
        "id": "fdot-stream-008",
        "name": "Congress Ave @ Blue Heron",
        "location": "Congress Ave & Blue Heron Blvd",
        "lat": 26.7845,
        "lng": -80.0999,
        "stream_url": "https://fl511.com/map/Cctv/CCTV-D4-SR807-026.5-N--1",
        "description": "FDOT District 4 - Congress Ave at Blue Heron",
    },
    {
        "id": "fdot-stream-009",
        "name": "US-1 @ Silver Beach Rd",
        "location": "US-1 & Silver Beach Rd",
        "lat": 26.7929,
        "lng": -80.0569,
        "stream_url": "https://fl511.com/map/Cctv/CCTV-D4-US1-077.0-N--1",
        "description": "FDOT District 4 - US-1 at Silver Beach Rd",
    },
    {
        "id": "fdot-stream-010",
        "name": "I-95 @ Okeechobee Blvd",
        "location": "Okeechobee Blvd & I-95",
        "lat": 26.7150,
        "lng": -80.0750,
        "stream_url": "https://fl511.com/map/Cctv/CCTV-D4-I95-021.0-N--1",
        "description": "FDOT District 4 - I-95 at Okeechobee Blvd",
    },
]


def get_all_cameras() -> List[Dict[str, Any]]:
    return FDOT_STREAM_CAMERAS


def get_camera_by_id(camera_id: str) -> Optional[Dict[str, Any]]:
    for camera in FDOT_STREAM_CAMERAS:
        if camera["id"] == camera_id:
            return camera
    return None


def get_stream_url(camera_id: str) -> Optional[str]:
    camera = get_camera_by_id(camera_id)
    if camera:
        return camera["stream_url"]
    return None
