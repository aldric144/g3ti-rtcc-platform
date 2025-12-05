"""
Event services for the G3TI RTCC-UIP Backend.

This module provides real-time event processing including:
- WebSocket connection management
- Event broadcasting
- Event normalization from various sources
- Subscription management
"""

from app.services.events.event_processor import EventProcessor
from app.services.events.websocket_manager import WebSocketManager

__all__ = ["WebSocketManager", "EventProcessor"]
