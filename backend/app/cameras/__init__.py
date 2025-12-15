"""
Cameras module for G3TI RTCC-UIP Platform.

Provides camera management, public camera catalog, FDOT integration,
RBPD internal cameras, and video feed integration.
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

from .rbpd_mock_loader import (
    RBPDMockCamera,
    RBPDCameraType,
    load_rbpd_mock_cameras,
    get_rbpd_cameras_by_sector,
    get_rbpd_cameras_by_type,
    get_rbpd_camera_stats,
    get_cached_rbpd_cameras,
    refresh_rbpd_cameras,
)

from .camera_ingestion_engine import (
    CameraIngestionEngine,
    get_camera_ingestion_engine,
)

__all__ = [
    # Public camera catalog
    "PublicCamera",
    "PublicCameraCatalog",
    "get_public_camera_catalog",
    "CameraType",
    "CameraSource",
    "PLACEHOLDER_STREAM_URL",
    # FDOT scraper
    "FDOTCamera",
    "FDOTScraper",
    "get_fdot_scraper",
    "generate_mjpeg_stream",
    "CameraStatus",
    # RBPD mock cameras
    "RBPDMockCamera",
    "RBPDCameraType",
    "load_rbpd_mock_cameras",
    "get_rbpd_cameras_by_sector",
    "get_rbpd_cameras_by_type",
    "get_rbpd_camera_stats",
    "get_cached_rbpd_cameras",
    "refresh_rbpd_cameras",
    # Camera ingestion engine
    "CameraIngestionEngine",
    "get_camera_ingestion_engine",
]
