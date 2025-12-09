"""
G3TI RTCC-UIP Command Operations Module.

Phase 8: Mission Management & Command Operations Suite
Provides incident command, ICS workflows, strategy mapping,
resource management, and multi-agency coordination.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .briefing import BriefingGenerator
    from .ics import ICSManager
    from .major_incident import MajorIncidentEngine
    from .multiagency import MultiAgencyCoordinator
    from .resources import ResourceManager
    from .strategy_map import StrategyMapManager
    from .timeline import TimelineEngine

__all__ = [
    "MajorIncidentEngine",
    "ICSManager",
    "StrategyMapManager",
    "ResourceManager",
    "TimelineEngine",
    "BriefingGenerator",
    "MultiAgencyCoordinator",
]
