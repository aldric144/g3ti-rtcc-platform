"""
API routers for the G3TI RTCC-UIP Backend.

This module contains all API endpoint routers organized by domain:
- auth: Authentication and user management
- entities: Entity CRUD operations
- investigations: Investigation management
- realtime: WebSocket and real-time events
- system: Health checks and system status
- ai: AI Intelligence Engine endpoints
- tactical: Tactical Analytics Engine endpoints
- admin: Admin portal modules (logs, shift, patrol, case tools)
"""

from fastapi import APIRouter

from app.api.ai import router as ai_router
from app.api.auth import router as auth_router
from app.api.entities import router as entities_router
from app.api.investigations import router as investigations_router
from app.api.realtime import router as realtime_router
from app.api.system import router as system_router
from app.api.tactical import router as tactical_router
from app.publicdata import router as publicdata_router

# Admin portal routers
from app.admin_logs.activity_log_api import router as activity_log_router
from app.shift_admin.shift_api import router as shift_router
from app.patrol_insights.patrol_insights_api import router as patrol_insights_router
from app.case_tools.case_tools_api import router as case_tools_router

# Create main API router
api_router = APIRouter()

# Include all sub-routers
api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_router.include_router(entities_router, prefix="/entities", tags=["Entities"])
api_router.include_router(investigations_router, prefix="/investigations", tags=["Investigations"])
api_router.include_router(realtime_router, prefix="/realtime", tags=["Real-time"])
api_router.include_router(system_router, prefix="/system", tags=["System"])
api_router.include_router(ai_router, tags=["AI Intelligence"])
api_router.include_router(tactical_router, tags=["Tactical Analytics"])
api_router.include_router(publicdata_router, tags=["Riviera Beach Public Data"])

# Admin portal routers (CJIS-compliant, internal-only)
api_router.include_router(activity_log_router, tags=["Admin Logs"])
api_router.include_router(shift_router, tags=["Shift Management"])
api_router.include_router(patrol_insights_router, tags=["Patrol Insights"])
api_router.include_router(case_tools_router, tags=["Case Tools"])

__all__ = ["api_router"]
