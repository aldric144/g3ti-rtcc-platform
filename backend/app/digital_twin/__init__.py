"""
City Digital Twin Engine.

Phase 15: Provides 3D real-time environment rendering with building models,
road networks, interior mapping, and real-time overlays for officers,
drones, vehicles, and events.
"""

from app.digital_twin.building_models import (
    BuildingModelsLoader,
    Building,
    BuildingType,
    Floor,
    Room,
)
from app.digital_twin.road_network import (
    RoadNetworkModel,
    Road,
    RoadType,
    Intersection,
    TrafficCondition,
)
from app.digital_twin.interior_mapping import (
    InteriorMappingService,
    InteriorMap,
    PointOfInterest,
    AccessPoint,
)
from app.digital_twin.entity_renderer import (
    EntityRenderer,
    EntityType,
    RenderedEntity,
    EntityPosition,
)
from app.digital_twin.overlay_engine import (
    OverlayEngine,
    OverlayType,
    WeatherOverlay,
    TrafficOverlay,
    IncidentOverlay,
)
from app.digital_twin.time_travel import (
    TimeTravelEngine,
    HistoricalSnapshot,
    PlaybackState,
)

__all__ = [
    "BuildingModelsLoader",
    "Building",
    "BuildingType",
    "Floor",
    "Room",
    "RoadNetworkModel",
    "Road",
    "RoadType",
    "Intersection",
    "TrafficCondition",
    "InteriorMappingService",
    "InteriorMap",
    "PointOfInterest",
    "AccessPoint",
    "EntityRenderer",
    "EntityType",
    "RenderedEntity",
    "EntityPosition",
    "OverlayEngine",
    "OverlayType",
    "WeatherOverlay",
    "TrafficOverlay",
    "IncidentOverlay",
    "TimeTravelEngine",
    "HistoricalSnapshot",
    "PlaybackState",
]
