"""
FDOT Live Streaming Module.

Provides HLS/MPEG-TS streaming support for FDOT traffic cameras.
This is an additive module that does not modify existing camera integrations.
"""

from app.fdot_streams.api_router import router

__all__ = ["router"]
