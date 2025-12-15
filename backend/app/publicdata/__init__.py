"""
Public Data Module for Riviera Beach.

Provides REST API endpoints for publicly available Riviera Beach data including:
- City boundaries and districts
- Schools and infrastructure
- Public safety locations
- Environmental data
"""

from app.publicdata.router import router

__all__ = ["router"]
