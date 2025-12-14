"""
Phase 34: AI Personas API

REST API endpoints for AI Personas (Apex AI Officers).
"""

from backend.app.api.personas.persona_router import router as persona_router

__all__ = ["persona_router"]
