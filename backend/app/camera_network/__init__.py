"""
Camera Network Module for G3TI RTCC-UIP Platform.

Complete Camera Intelligence Stack including:
- Camera Registry (CRUD operations)
- FDOT Traffic Camera Integration
- RBPD Internal Mock Camera Network
- Camera Ingestion Engine
- Camera Health Monitor
- Streaming Adapter (MJPEG, RTSP, Snapshot)
- Video Wall Manager
"""

from .camera_registry import (
    CameraRegistry,
    Camera,
    CameraType,
    CameraJurisdiction,
    CameraStatus,
    get_camera_registry,
)

from .fdot_scraper import (
    FDOTScraper,
    get_fdot_scraper,
)

from .rbpd_mock_loader import (
    load_rbpd_mock_cameras,
    get_rbpd_camera_count,
)

from .camera_ingestion_engine import (
    CameraIngestionEngine,
    get_ingestion_engine,
)

from .camera_health_monitor import (
    CameraHealthMonitor,
    HealthStatus,
    get_health_monitor,
)

from .streaming_adapter import (
    StreamingAdapter,
    StreamType,
    get_streaming_adapter,
)

from .video_wall_manager import (
    VideoWallManager,
    VideoWallLayout,
    get_video_wall_manager,
)

__all__ = [
    # Camera Registry
    "CameraRegistry",
    "Camera",
    "CameraType",
    "CameraJurisdiction",
    "CameraStatus",
    "get_camera_registry",
    # FDOT Scraper
    "FDOTScraper",
    "get_fdot_scraper",
    # RBPD Mock Loader
    "load_rbpd_mock_cameras",
    "get_rbpd_camera_count",
    # Ingestion Engine
    "CameraIngestionEngine",
    "get_ingestion_engine",
    # Health Monitor
    "CameraHealthMonitor",
    "HealthStatus",
    "get_health_monitor",
    # Streaming Adapter
    "StreamingAdapter",
    "StreamType",
    "get_streaming_adapter",
    # Video Wall Manager
    "VideoWallManager",
    "VideoWallLayout",
    "get_video_wall_manager",
]
