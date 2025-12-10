"""
Operations Continuity API Module.

Provides REST API endpoints and WebSocket channels for
operational continuity monitoring and management.
"""

from app.api.ops_continuity.router import router
from app.api.ops_continuity.websocket import (
    broadcast_diagnostic_event,
    broadcast_failover_event,
    broadcast_health_update,
    websocket_router,
)

__all__ = [
    "router",
    "websocket_router",
    "broadcast_health_update",
    "broadcast_failover_event",
    "broadcast_diagnostic_event",
]
