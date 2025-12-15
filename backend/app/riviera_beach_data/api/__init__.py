"""
API Module for Riviera Beach Public Data.

Provides REST API endpoints for accessing all Riviera Beach public data.
"""

from app.riviera_beach_data.api.router import router

__all__ = ["router"]
