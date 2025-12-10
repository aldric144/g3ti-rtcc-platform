"""
WebSocket handlers for Phase 15 modules.

Provides real-time communication channels for drones, sensor grid,
digital twin, and predictive AI.
"""

from app.websockets.drones import router as drones_ws_router
from app.websockets.sensor_grid import router as sensor_grid_ws_router
from app.websockets.digital_twin import router as digital_twin_ws_router
from app.websockets.predictive_ai import router as predictive_ai_ws_router

__all__ = [
    "drones_ws_router",
    "sensor_grid_ws_router",
    "digital_twin_ws_router",
    "predictive_ai_ws_router",
]
