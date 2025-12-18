"""
API routers for the G3TI RTCC-UIP Backend.

This module contains all API endpoint routers organized by domain:
- auth: Authentication and user management
- entities: Entity CRUD operations
- investigations: Investigation management
- realtime: WebSocket and real-time events
- system: Health checks and system status
- ai: AI Intelligence Engine endpoints
"""

from fastapi import APIRouter

from app.api.ai import router as ai_router
from app.api.auth import router as auth_router
from app.api.entities import router as entities_router
from app.api.investigations import router as investigations_router
from app.api.realtime import router as realtime_router
from app.api.system import router as system_router

# Camera network routers (Phase CAM-NET-ALL)
from app.cameras.marina_streams import router as marina_router
from app.cameras.pbc_traffic_scraper import router as pbc_router
from app.cameras.rtsp_adapter import router as rtsp_router
from app.camera_network.camera_registry import router as camera_registry_router
from app.cameras.health.extended_camera_health import router as camera_health_router
from app.fdot_streams.mjpeg_simulator import router as fdot_mjpeg_router

# Create main API router
api_router = APIRouter()

# Include all sub-routers
api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_router.include_router(entities_router, prefix="/entities", tags=["Entities"])
api_router.include_router(investigations_router, prefix="/investigations", tags=["Investigations"])
api_router.include_router(realtime_router, prefix="/realtime", tags=["Real-time"])
api_router.include_router(system_router, prefix="/system", tags=["System"])
api_router.include_router(ai_router, tags=["AI Intelligence"])

# Camera network routers (Phase CAM-NET-ALL)
api_router.include_router(marina_router, tags=["Marina Cameras"])
api_router.include_router(pbc_router, tags=["PBC Traffic Cameras"])
api_router.include_router(rtsp_router, tags=["RTSP Cameras"])
api_router.include_router(camera_registry_router, tags=["Camera Registry"])
api_router.include_router(camera_health_router, tags=["Camera Health"])
api_router.include_router(fdot_mjpeg_router, tags=["FDOT MJPEG Streams"])

__all__ = ["api_router"]
