"""
Cameras module for G3TI RTCC-UIP Platform.

Provides camera management, public camera catalog, FDOT integration, and video feed integration.
"""

from .public_camera_catalog import (
    PublicCamera,
    PublicCameraCatalog,
    get_public_camera_catalog,
    CameraType,
    CameraSource,
    PLACEHOLDER_STREAM_URL,
)

from .fdot_scraper import (
    FDOTCamera,
    FDOTScraper,
    get_fdot_scraper,
    generate_mjpeg_stream,
    CameraStatus,
)

__all__ = [
    "PublicCamera",
    "PublicCameraCatalog",
    "get_public_camera_catalog",
    "CameraType",
    "CameraSource",
    "PLACEHOLDER_STREAM_URL",
    "FDOTCamera",
    "FDOTScraper",
    "get_fdot_scraper",
    "generate_mjpeg_stream",
    "CameraStatus",
]
