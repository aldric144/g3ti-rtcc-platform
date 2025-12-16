"""
G3TI RTCC Admin API Routers
Phase: RTCC-ADMIN-SUITE-X

This module provides API endpoints for all 15 admin modules with:
- Full CRUD operations
- Role-based access control
- Audit logging
- Validation
"""

from fastapi import APIRouter

from .cameras_router import router as cameras_router
from .drones_router import router as drones_router
from .robots_router import router as robots_router
from .lpr_zones_router import router as lpr_zones_router
from .sectors_router import router as sectors_router
from .fire_preplans_router import router as fire_preplans_router
from .infrastructure_router import router as infrastructure_router
from .schools_router import router as schools_router
from .dv_risk_homes_router import router as dv_risk_homes_router
from .incidents_router import router as incidents_router
from .api_connections_router import router as api_connections_router
from .events_router import router as events_router
from .hydrants_router import router as hydrants_router
from .users_router import router as users_router
from .system_settings_router import router as system_settings_router

# Main admin router
admin_router = APIRouter(prefix="/admin", tags=["Admin"])

# Include all sub-routers
admin_router.include_router(cameras_router, prefix="/cameras", tags=["Admin - Cameras"])
admin_router.include_router(drones_router, prefix="/drones", tags=["Admin - Drones"])
admin_router.include_router(robots_router, prefix="/robots", tags=["Admin - Robots"])
admin_router.include_router(lpr_zones_router, prefix="/lpr-zones", tags=["Admin - LPR Zones"])
admin_router.include_router(sectors_router, prefix="/sectors", tags=["Admin - Sectors"])
admin_router.include_router(fire_preplans_router, prefix="/fire-preplans", tags=["Admin - Fire Preplans"])
admin_router.include_router(infrastructure_router, prefix="/infrastructure", tags=["Admin - Infrastructure"])
admin_router.include_router(schools_router, prefix="/schools", tags=["Admin - Schools"])
admin_router.include_router(dv_risk_homes_router, prefix="/dv-risk-homes", tags=["Admin - DV Risk Homes"])
admin_router.include_router(incidents_router, prefix="/incidents", tags=["Admin - Incidents"])
admin_router.include_router(api_connections_router, prefix="/api-connections", tags=["Admin - API Connections"])
admin_router.include_router(events_router, prefix="/events", tags=["Admin - Events"])
admin_router.include_router(hydrants_router, prefix="/hydrants", tags=["Admin - Hydrants"])
admin_router.include_router(users_router, prefix="/users", tags=["Admin - Users"])
admin_router.include_router(system_settings_router, prefix="/settings", tags=["Admin - System Settings"])

__all__ = ["admin_router"]
