"""
G3TI RTCC-UIP Communications Module.

Phase 7: Notifications, Dispatch & Communication Suite

This module provides the complete communications infrastructure for RTCC operations:
- In-app messaging between RTCC analysts and patrol officers
- CAD dispatch overlay and event tracking
- Push alerts for mobile and MDT devices
- Automated RTCC-to-field bulletins
- Multi-unit scene coordination tools
- Notification rules engine for automated alerts

All communications are CJIS-compliant with encryption at rest and comprehensive audit logging.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .alerts import AlertsManager
    from .bulletins import BulletinManager
    from .dispatch_overlay import DispatchOverlayEngine
    from .messaging import MessagingManager
    from .rules_engine import NotificationRulesEngine
    from .scene_coordination import SceneCoordinationManager

__all__ = [
    "MessagingManager",
    "DispatchOverlayEngine",
    "AlertsManager",
    "BulletinManager",
    "SceneCoordinationManager",
    "NotificationRulesEngine",
]
