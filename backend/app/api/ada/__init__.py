"""
Phase 20: Autonomous Detective AI (ADA) API Router

Provides REST API endpoints for all ADA modules including crime scene analysis,
offender modeling, case theory generation, evidence graph, reporting, and
autonomous investigation.
"""

from fastapi import APIRouter

from .router import router as ada_router

__all__ = ["ada_router"]
