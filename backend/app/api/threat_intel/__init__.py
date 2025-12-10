"""
Phase 17: Global Threat Intelligence API Endpoints
"""

from fastapi import APIRouter

from app.api.threat_intel.router import router as threat_intel_router

router = APIRouter()
router.include_router(threat_intel_router, prefix="/threat-intel", tags=["threat-intel"])

__all__ = ["router"]
