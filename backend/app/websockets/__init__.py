"""
WebSocket handlers for RTCC-UIP modules.

Provides real-time communication channels for:
- Phase 15: Drones, sensor grid, digital twin, predictive AI
- Phase 25: AI City Constitution governance channels
"""

from app.websockets.drones import router as drones_ws_router
from app.websockets.sensor_grid import router as sensor_grid_ws_router
from app.websockets.digital_twin import router as digital_twin_ws_router
from app.websockets.predictive_ai import router as predictive_ai_ws_router
from app.websockets.city_constitution import (
    get_constitution_ws_manager,
    handle_decisions_websocket,
    handle_approvals_websocket,
    handle_policy_updates_websocket,
)

__all__ = [
    "drones_ws_router",
    "sensor_grid_ws_router",
    "digital_twin_ws_router",
    "predictive_ai_ws_router",
    "get_constitution_ws_manager",
    "handle_decisions_websocket",
    "handle_approvals_websocket",
    "handle_policy_updates_websocket",
]
