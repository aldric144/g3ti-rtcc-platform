"""
Live Strategy Map for G3TI RTCC-UIP Command Operations.

Provides real-time tactical overlays, drawing tools, and
visualization for incident command operations.
"""

import uuid
from datetime import UTC, datetime
from enum import Enum
from typing import Any

import structlog
from pydantic import BaseModel, Field

logger = structlog.get_logger(__name__)


class OverlayType(str, Enum):
    """Types of map overlays."""

    UNITS = "units"
    PERIMETER = "perimeter"
    CAMERAS = "cameras"
    VEHICLE_PATHS = "vehicle_paths"
    GUNFIRE = "gunfire"
    TACTICAL_HEATMAP = "tactical_heatmap"
    THREAT_ZONES = "threat_zones"
    SEARCH_GRID = "search_grid"
    EVACUATION_ROUTE = "evacuation_route"
    HOT_ZONE = "hot_zone"
    STAGING_AREA = "staging_area"
    COMMAND_POST = "command_post"
    MEDICAL_STAGING = "medical_staging"
    MEDIA_STAGING = "media_staging"
    CUSTOM = "custom"


class ShapeType(str, Enum):
    """Types of drawable shapes."""

    POLYGON = "polygon"
    CIRCLE = "circle"
    RECTANGLE = "rectangle"
    LINE = "line"
    POLYLINE = "polyline"
    MARKER = "marker"
    ARROW = "arrow"
    TEXT = "text"


class MarkerType(str, Enum):
    """Types of map markers."""

    UNIT = "unit"
    CAMERA = "camera"
    GUNFIRE = "gunfire"
    VEHICLE = "vehicle"
    SUSPECT = "suspect"
    VICTIM = "victim"
    HAZARD = "hazard"
    COMMAND_POST = "command_post"
    STAGING = "staging"
    ENTRY_POINT = "entry_point"
    EXIT_POINT = "exit_point"
    PERIMETER_POST = "perimeter_post"
    CUSTOM = "custom"


class GeoPoint(BaseModel):
    """Geographic point."""

    latitude: float
    longitude: float


class MapMarker(BaseModel):
    """Marker on the strategy map."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    marker_type: MarkerType
    position: GeoPoint
    label: str | None = None
    description: str | None = None
    icon: str | None = None
    color: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    created_by: str | None = None
    is_visible: bool = True

    class Config:
        """Pydantic config."""

        use_enum_values = True


class MapShape(BaseModel):
    """Shape drawn on the strategy map."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    shape_type: ShapeType
    overlay_type: OverlayType
    coordinates: list[GeoPoint] = Field(default_factory=list)
    center: GeoPoint | None = None
    radius_meters: float | None = None
    label: str | None = None
    description: str | None = None
    stroke_color: str = "#FF0000"
    stroke_width: int = 2
    fill_color: str | None = "#FF000033"
    fill_opacity: float = 0.2
    is_dashed: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    created_by: str | None = None
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    is_visible: bool = True
    is_locked: bool = False

    class Config:
        """Pydantic config."""

        use_enum_values = True


class UnitPosition(BaseModel):
    """Position of a unit on the map."""

    unit_id: str
    badge: str | None = None
    name: str | None = None
    position: GeoPoint
    heading: float | None = None
    speed: float | None = None
    status: str | None = None
    role: str | None = None
    safety_level: str | None = None
    last_updated: datetime = Field(default_factory=lambda: datetime.now(UTC))
    is_visible: bool = True


class CameraOverlay(BaseModel):
    """Camera position and coverage overlay."""

    camera_id: str
    name: str | None = None
    position: GeoPoint
    coverage_angle: float | None = None
    coverage_distance: float | None = None
    is_active: bool = True
    is_ptz: bool = False
    stream_url: str | None = None


class GunfireOverlay(BaseModel):
    """Gunfire detection overlay."""

    detection_id: str
    position: GeoPoint
    timestamp: datetime
    rounds_detected: int | None = None
    confidence: float | None = None
    audio_url: str | None = None


class VehiclePath(BaseModel):
    """Vehicle path from LPR data."""

    vehicle_id: str
    plate: str | None = None
    path: list[GeoPoint] = Field(default_factory=list)
    timestamps: list[datetime] = Field(default_factory=list)
    color: str = "#0000FF"
    is_target: bool = False


class ThreatZone(BaseModel):
    """Threat zone from officer safety analysis."""

    zone_id: str
    center: GeoPoint
    radius_meters: float
    threat_level: str
    threat_type: str | None = None
    description: str | None = None
    expires_at: datetime | None = None


class MapLayer(BaseModel):
    """Layer containing map elements."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    overlay_type: OverlayType
    is_visible: bool = True
    is_locked: bool = False
    opacity: float = 1.0
    z_index: int = 0
    markers: list[MapMarker] = Field(default_factory=list)
    shapes: list[MapShape] = Field(default_factory=list)

    class Config:
        """Pydantic config."""

        use_enum_values = True


class StrategyMap(BaseModel):
    """Complete strategy map for an incident."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    incident_id: str
    name: str = "Strategy Map"
    center: GeoPoint | None = None
    zoom: int = 15
    layers: list[MapLayer] = Field(default_factory=list)
    unit_positions: list[UnitPosition] = Field(default_factory=list)
    cameras: list[CameraOverlay] = Field(default_factory=list)
    gunfire_detections: list[GunfireOverlay] = Field(default_factory=list)
    vehicle_paths: list[VehiclePath] = Field(default_factory=list)
    threat_zones: list[ThreatZone] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    created_by: str | None = None
    audit_id: str = Field(default_factory=lambda: f"AUDIT-SM-{uuid.uuid4().hex[:12].upper()}")


class MapUpdateEvent(BaseModel):
    """Event for map updates."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    incident_id: str
    event_type: str
    layer_id: str | None = None
    element_id: str | None = None
    data: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    user_id: str | None = None
    audit_id: str = Field(default_factory=lambda: f"AUDIT-MU-{uuid.uuid4().hex[:12].upper()}")


class StrategyMapManager:
    """
    Manager for strategy map operations.

    Provides creation, updates, and real-time synchronization
    of tactical overlays for incident command.
    """

    def __init__(self) -> None:
        """Initialize the strategy map manager."""
        self._maps: dict[str, StrategyMap] = {}  # incident_id -> map
        self._events: list[MapUpdateEvent] = []

        logger.info("strategy_map_manager_initialized")

    async def create_map(
        self,
        incident_id: str,
        name: str = "Strategy Map",
        center: GeoPoint | None = None,
        zoom: int = 15,
        created_by: str | None = None,
    ) -> StrategyMap:
        """
        Create a new strategy map for an incident.

        Args:
            incident_id: ID of the incident
            name: Map name
            center: Initial center point
            zoom: Initial zoom level
            created_by: User creating the map

        Returns:
            Created StrategyMap
        """
        strategy_map = StrategyMap(
            incident_id=incident_id,
            name=name,
            center=center,
            zoom=zoom,
            created_by=created_by,
        )

        # Initialize default layers
        default_layers = [
            MapLayer(name="Units", overlay_type=OverlayType.UNITS, z_index=100),
            MapLayer(name="Perimeter", overlay_type=OverlayType.PERIMETER, z_index=50),
            MapLayer(name="Cameras", overlay_type=OverlayType.CAMERAS, z_index=40),
            MapLayer(name="Gunfire", overlay_type=OverlayType.GUNFIRE, z_index=90),
            MapLayer(name="Threat Zones", overlay_type=OverlayType.THREAT_ZONES, z_index=30),
            MapLayer(name="Custom", overlay_type=OverlayType.CUSTOM, z_index=60),
        ]
        strategy_map.layers = default_layers

        self._maps[incident_id] = strategy_map

        # Log event
        event = MapUpdateEvent(
            incident_id=incident_id,
            event_type="map_created",
            data={"name": name, "center": center.model_dump() if center else None},
            user_id=created_by,
        )
        self._events.append(event)

        logger.info(
            "strategy_map_created",
            incident_id=incident_id,
            map_id=strategy_map.id,
            created_by=created_by,
            audit_id=strategy_map.audit_id,
        )

        return strategy_map

    async def get_map(self, incident_id: str) -> StrategyMap | None:
        """Get strategy map for an incident."""
        return self._maps.get(incident_id)

    async def update_map_center(
        self,
        incident_id: str,
        center: GeoPoint,
        zoom: int | None = None,
        updated_by: str | None = None,
    ) -> StrategyMap | None:
        """
        Update map center and zoom.

        Args:
            incident_id: ID of the incident
            center: New center point
            zoom: New zoom level
            updated_by: User updating the map

        Returns:
            Updated StrategyMap or None
        """
        strategy_map = self._maps.get(incident_id)
        if not strategy_map:
            return None

        strategy_map.center = center
        if zoom is not None:
            strategy_map.zoom = zoom
        strategy_map.updated_at = datetime.now(UTC)

        # Log event
        event = MapUpdateEvent(
            incident_id=incident_id,
            event_type="map_center_updated",
            data={"center": center.model_dump(), "zoom": zoom},
            user_id=updated_by,
        )
        self._events.append(event)

        return strategy_map

    async def add_layer(
        self,
        incident_id: str,
        name: str,
        overlay_type: OverlayType,
        z_index: int = 50,
        created_by: str | None = None,
    ) -> MapLayer | None:
        """
        Add a new layer to the map.

        Args:
            incident_id: ID of the incident
            name: Layer name
            overlay_type: Type of overlay
            z_index: Layer z-index
            created_by: User creating the layer

        Returns:
            Created MapLayer or None
        """
        strategy_map = self._maps.get(incident_id)
        if not strategy_map:
            return None

        layer = MapLayer(
            name=name,
            overlay_type=overlay_type,
            z_index=z_index,
        )
        strategy_map.layers.append(layer)
        strategy_map.updated_at = datetime.now(UTC)

        # Log event
        event = MapUpdateEvent(
            incident_id=incident_id,
            event_type="layer_added",
            layer_id=layer.id,
            data={"name": name, "overlay_type": overlay_type},
            user_id=created_by,
        )
        self._events.append(event)

        logger.info(
            "map_layer_added",
            incident_id=incident_id,
            layer_id=layer.id,
            name=name,
            created_by=created_by,
        )

        return layer

    async def add_marker(
        self,
        incident_id: str,
        layer_id: str,
        marker_type: MarkerType,
        position: GeoPoint,
        label: str | None = None,
        description: str | None = None,
        color: str | None = None,
        metadata: dict[str, Any] | None = None,
        created_by: str | None = None,
    ) -> MapMarker | None:
        """
        Add a marker to a layer.

        Args:
            incident_id: ID of the incident
            layer_id: ID of the layer
            marker_type: Type of marker
            position: Marker position
            label: Marker label
            description: Marker description
            color: Marker color
            metadata: Additional metadata
            created_by: User creating the marker

        Returns:
            Created MapMarker or None
        """
        strategy_map = self._maps.get(incident_id)
        if not strategy_map:
            return None

        layer = next((lyr for lyr in strategy_map.layers if lyr.id == layer_id), None)
        if not layer:
            return None

        marker = MapMarker(
            marker_type=marker_type,
            position=position,
            label=label,
            description=description,
            color=color,
            metadata=metadata or {},
            created_by=created_by,
        )
        layer.markers.append(marker)
        strategy_map.updated_at = datetime.now(UTC)

        # Log event
        event = MapUpdateEvent(
            incident_id=incident_id,
            event_type="marker_added",
            layer_id=layer_id,
            element_id=marker.id,
            data={"marker_type": marker_type, "position": position.model_dump()},
            user_id=created_by,
        )
        self._events.append(event)

        logger.info(
            "map_marker_added",
            incident_id=incident_id,
            marker_id=marker.id,
            marker_type=marker_type,
            created_by=created_by,
        )

        return marker

    async def add_shape(
        self,
        incident_id: str,
        layer_id: str,
        shape_type: ShapeType,
        overlay_type: OverlayType,
        coordinates: list[GeoPoint] | None = None,
        center: GeoPoint | None = None,
        radius_meters: float | None = None,
        label: str | None = None,
        description: str | None = None,
        stroke_color: str = "#FF0000",
        stroke_width: int = 2,
        fill_color: str | None = "#FF000033",
        created_by: str | None = None,
    ) -> MapShape | None:
        """
        Add a shape to a layer.

        Args:
            incident_id: ID of the incident
            layer_id: ID of the layer
            shape_type: Type of shape
            overlay_type: Type of overlay
            coordinates: Shape coordinates (for polygon, line, etc.)
            center: Center point (for circle)
            radius_meters: Radius in meters (for circle)
            label: Shape label
            description: Shape description
            stroke_color: Stroke color
            stroke_width: Stroke width
            fill_color: Fill color
            created_by: User creating the shape

        Returns:
            Created MapShape or None
        """
        strategy_map = self._maps.get(incident_id)
        if not strategy_map:
            return None

        layer = next((lyr for lyr in strategy_map.layers if lyr.id == layer_id), None)
        if not layer:
            return None

        shape = MapShape(
            shape_type=shape_type,
            overlay_type=overlay_type,
            coordinates=coordinates or [],
            center=center,
            radius_meters=radius_meters,
            label=label,
            description=description,
            stroke_color=stroke_color,
            stroke_width=stroke_width,
            fill_color=fill_color,
            created_by=created_by,
        )
        layer.shapes.append(shape)
        strategy_map.updated_at = datetime.now(UTC)

        # Log event
        event = MapUpdateEvent(
            incident_id=incident_id,
            event_type="shape_added",
            layer_id=layer_id,
            element_id=shape.id,
            data={"shape_type": shape_type, "overlay_type": overlay_type},
            user_id=created_by,
        )
        self._events.append(event)

        logger.info(
            "map_shape_added",
            incident_id=incident_id,
            shape_id=shape.id,
            shape_type=shape_type,
            created_by=created_by,
        )

        return shape

    async def draw_perimeter(
        self,
        incident_id: str,
        coordinates: list[GeoPoint],
        label: str = "Perimeter",
        perimeter_type: str = "outer",
        created_by: str | None = None,
    ) -> MapShape | None:
        """
        Draw a perimeter on the map.

        Args:
            incident_id: ID of the incident
            coordinates: Perimeter coordinates
            label: Perimeter label
            perimeter_type: Type (inner, outer)
            created_by: User drawing the perimeter

        Returns:
            Created MapShape or None
        """
        strategy_map = self._maps.get(incident_id)
        if not strategy_map:
            return None

        # Find or create perimeter layer
        perimeter_layer = next(
            (lyr for lyr in strategy_map.layers if lyr.overlay_type == OverlayType.PERIMETER.value),
            None
        )
        if not perimeter_layer:
            perimeter_layer = await self.add_layer(
                incident_id=incident_id,
                name="Perimeter",
                overlay_type=OverlayType.PERIMETER,
                created_by=created_by,
            )

        if not perimeter_layer:
            return None

        # Set colors based on perimeter type
        colors = {
            "inner": ("#FF0000", "#FF000033"),
            "outer": ("#FFFF00", "#FFFF0033"),
            "hot": ("#FF0000", "#FF000055"),
            "warm": ("#FFA500", "#FFA50033"),
            "cold": ("#00FF00", "#00FF0033"),
        }
        stroke_color, fill_color = colors.get(perimeter_type, ("#FF0000", "#FF000033"))

        return await self.add_shape(
            incident_id=incident_id,
            layer_id=perimeter_layer.id,
            shape_type=ShapeType.POLYGON,
            overlay_type=OverlayType.PERIMETER,
            coordinates=coordinates,
            label=f"{label} ({perimeter_type})",
            stroke_color=stroke_color,
            fill_color=fill_color,
            created_by=created_by,
        )

    async def draw_hot_zone(
        self,
        incident_id: str,
        center: GeoPoint,
        radius_meters: float,
        label: str = "Hot Zone",
        created_by: str | None = None,
    ) -> MapShape | None:
        """
        Draw a hot zone circle on the map.

        Args:
            incident_id: ID of the incident
            center: Center of hot zone
            radius_meters: Radius in meters
            label: Zone label
            created_by: User drawing the zone

        Returns:
            Created MapShape or None
        """
        strategy_map = self._maps.get(incident_id)
        if not strategy_map:
            return None

        # Find or create custom layer
        custom_layer = next(
            (lyr for lyr in strategy_map.layers if lyr.overlay_type == OverlayType.CUSTOM.value),
            None
        )
        if not custom_layer:
            custom_layer = await self.add_layer(
                incident_id=incident_id,
                name="Custom",
                overlay_type=OverlayType.CUSTOM,
                created_by=created_by,
            )

        if not custom_layer:
            return None

        return await self.add_shape(
            incident_id=incident_id,
            layer_id=custom_layer.id,
            shape_type=ShapeType.CIRCLE,
            overlay_type=OverlayType.HOT_ZONE,
            center=center,
            radius_meters=radius_meters,
            label=label,
            stroke_color="#FF0000",
            fill_color="#FF000055",
            created_by=created_by,
        )

    async def draw_search_grid(
        self,
        incident_id: str,
        bounds: list[GeoPoint],
        grid_size_meters: float = 100,
        label: str = "Search Grid",
        created_by: str | None = None,
    ) -> MapShape | None:
        """
        Draw a search grid on the map.

        Args:
            incident_id: ID of the incident
            bounds: Grid boundary coordinates
            grid_size_meters: Size of each grid cell
            label: Grid label
            created_by: User drawing the grid

        Returns:
            Created MapShape or None
        """
        strategy_map = self._maps.get(incident_id)
        if not strategy_map:
            return None

        custom_layer = next(
            (lyr for lyr in strategy_map.layers if lyr.overlay_type == OverlayType.CUSTOM.value),
            None
        )
        if not custom_layer:
            custom_layer = await self.add_layer(
                incident_id=incident_id,
                name="Custom",
                overlay_type=OverlayType.CUSTOM,
                created_by=created_by,
            )

        if not custom_layer:
            return None

        return await self.add_shape(
            incident_id=incident_id,
            layer_id=custom_layer.id,
            shape_type=ShapeType.RECTANGLE,
            overlay_type=OverlayType.SEARCH_GRID,
            coordinates=bounds,
            label=label,
            description=f"Grid size: {grid_size_meters}m",
            stroke_color="#0000FF",
            fill_color="#0000FF22",
            created_by=created_by,
        )

    async def draw_evacuation_route(
        self,
        incident_id: str,
        coordinates: list[GeoPoint],
        label: str = "Evacuation Route",
        created_by: str | None = None,
    ) -> MapShape | None:
        """
        Draw an evacuation route on the map.

        Args:
            incident_id: ID of the incident
            coordinates: Route coordinates
            label: Route label
            created_by: User drawing the route

        Returns:
            Created MapShape or None
        """
        strategy_map = self._maps.get(incident_id)
        if not strategy_map:
            return None

        custom_layer = next(
            (lyr for lyr in strategy_map.layers if lyr.overlay_type == OverlayType.CUSTOM.value),
            None
        )
        if not custom_layer:
            custom_layer = await self.add_layer(
                incident_id=incident_id,
                name="Custom",
                overlay_type=OverlayType.CUSTOM,
                created_by=created_by,
            )

        if not custom_layer:
            return None

        return await self.add_shape(
            incident_id=incident_id,
            layer_id=custom_layer.id,
            shape_type=ShapeType.POLYLINE,
            overlay_type=OverlayType.EVACUATION_ROUTE,
            coordinates=coordinates,
            label=label,
            stroke_color="#00FF00",
            stroke_width=4,
            fill_color=None,
            created_by=created_by,
        )

    async def update_unit_position(
        self,
        incident_id: str,
        unit_id: str,
        position: GeoPoint,
        badge: str | None = None,
        name: str | None = None,
        status: str | None = None,
        role: str | None = None,
        safety_level: str | None = None,
        heading: float | None = None,
        speed: float | None = None,
    ) -> UnitPosition | None:
        """
        Update or add a unit position on the map.

        Args:
            incident_id: ID of the incident
            unit_id: Unit identifier
            position: Unit position
            badge: Officer badge
            name: Officer name
            status: Unit status
            role: Tactical role
            safety_level: Safety level
            heading: Direction of travel
            speed: Speed of travel

        Returns:
            Updated UnitPosition or None
        """
        strategy_map = self._maps.get(incident_id)
        if not strategy_map:
            return None

        # Find existing unit position
        existing = next(
            (u for u in strategy_map.unit_positions if u.unit_id == unit_id),
            None
        )

        if existing:
            existing.position = position
            existing.last_updated = datetime.now(UTC)
            if badge is not None:
                existing.badge = badge
            if name is not None:
                existing.name = name
            if status is not None:
                existing.status = status
            if role is not None:
                existing.role = role
            if safety_level is not None:
                existing.safety_level = safety_level
            if heading is not None:
                existing.heading = heading
            if speed is not None:
                existing.speed = speed
            unit_position = existing
        else:
            unit_position = UnitPosition(
                unit_id=unit_id,
                badge=badge,
                name=name,
                position=position,
                status=status,
                role=role,
                safety_level=safety_level,
                heading=heading,
                speed=speed,
            )
            strategy_map.unit_positions.append(unit_position)

        strategy_map.updated_at = datetime.now(UTC)

        # Log event
        event = MapUpdateEvent(
            incident_id=incident_id,
            event_type="unit_position_updated",
            element_id=unit_id,
            data={"position": position.model_dump(), "status": status},
        )
        self._events.append(event)

        return unit_position

    async def add_camera_overlay(
        self,
        incident_id: str,
        camera_id: str,
        position: GeoPoint,
        name: str | None = None,
        coverage_angle: float | None = None,
        coverage_distance: float | None = None,
        is_ptz: bool = False,
        stream_url: str | None = None,
    ) -> CameraOverlay | None:
        """
        Add a camera overlay to the map.

        Args:
            incident_id: ID of the incident
            camera_id: Camera identifier
            position: Camera position
            name: Camera name
            coverage_angle: Field of view angle
            coverage_distance: Coverage distance
            is_ptz: Whether camera is PTZ
            stream_url: Stream URL

        Returns:
            Created CameraOverlay or None
        """
        strategy_map = self._maps.get(incident_id)
        if not strategy_map:
            return None

        camera = CameraOverlay(
            camera_id=camera_id,
            name=name,
            position=position,
            coverage_angle=coverage_angle,
            coverage_distance=coverage_distance,
            is_ptz=is_ptz,
            stream_url=stream_url,
        )
        strategy_map.cameras.append(camera)
        strategy_map.updated_at = datetime.now(UTC)

        # Log event
        event = MapUpdateEvent(
            incident_id=incident_id,
            event_type="camera_added",
            element_id=camera_id,
            data={"position": position.model_dump(), "name": name},
        )
        self._events.append(event)

        return camera

    async def add_gunfire_detection(
        self,
        incident_id: str,
        detection_id: str,
        position: GeoPoint,
        timestamp: datetime | None = None,
        rounds_detected: int | None = None,
        confidence: float | None = None,
        audio_url: str | None = None,
    ) -> GunfireOverlay | None:
        """
        Add a gunfire detection overlay.

        Args:
            incident_id: ID of the incident
            detection_id: Detection identifier
            position: Detection position
            timestamp: Detection timestamp
            rounds_detected: Number of rounds
            confidence: Detection confidence
            audio_url: Audio clip URL

        Returns:
            Created GunfireOverlay or None
        """
        strategy_map = self._maps.get(incident_id)
        if not strategy_map:
            return None

        gunfire = GunfireOverlay(
            detection_id=detection_id,
            position=position,
            timestamp=timestamp or datetime.now(UTC),
            rounds_detected=rounds_detected,
            confidence=confidence,
            audio_url=audio_url,
        )
        strategy_map.gunfire_detections.append(gunfire)
        strategy_map.updated_at = datetime.now(UTC)

        # Log event
        event = MapUpdateEvent(
            incident_id=incident_id,
            event_type="gunfire_added",
            element_id=detection_id,
            data={"position": position.model_dump(), "rounds": rounds_detected},
        )
        self._events.append(event)

        logger.info(
            "gunfire_detection_added_to_map",
            incident_id=incident_id,
            detection_id=detection_id,
            rounds=rounds_detected,
        )

        return gunfire

    async def add_vehicle_path(
        self,
        incident_id: str,
        vehicle_id: str,
        plate: str | None = None,
        path: list[GeoPoint] | None = None,
        timestamps: list[datetime] | None = None,
        is_target: bool = False,
        color: str = "#0000FF",
    ) -> VehiclePath | None:
        """
        Add a vehicle path overlay.

        Args:
            incident_id: ID of the incident
            vehicle_id: Vehicle identifier
            plate: License plate
            path: Path coordinates
            timestamps: Timestamps for each point
            is_target: Whether this is a target vehicle
            color: Path color

        Returns:
            Created VehiclePath or None
        """
        strategy_map = self._maps.get(incident_id)
        if not strategy_map:
            return None

        vehicle_path = VehiclePath(
            vehicle_id=vehicle_id,
            plate=plate,
            path=path or [],
            timestamps=timestamps or [],
            is_target=is_target,
            color="#FF0000" if is_target else color,
        )
        strategy_map.vehicle_paths.append(vehicle_path)
        strategy_map.updated_at = datetime.now(UTC)

        # Log event
        event = MapUpdateEvent(
            incident_id=incident_id,
            event_type="vehicle_path_added",
            element_id=vehicle_id,
            data={"plate": plate, "is_target": is_target},
        )
        self._events.append(event)

        return vehicle_path

    async def add_threat_zone(
        self,
        incident_id: str,
        zone_id: str,
        center: GeoPoint,
        radius_meters: float,
        threat_level: str,
        threat_type: str | None = None,
        description: str | None = None,
        expires_at: datetime | None = None,
    ) -> ThreatZone | None:
        """
        Add a threat zone overlay.

        Args:
            incident_id: ID of the incident
            zone_id: Zone identifier
            center: Zone center
            radius_meters: Zone radius
            threat_level: Threat level (critical, high, medium, low)
            threat_type: Type of threat
            description: Zone description
            expires_at: Expiration time

        Returns:
            Created ThreatZone or None
        """
        strategy_map = self._maps.get(incident_id)
        if not strategy_map:
            return None

        threat_zone = ThreatZone(
            zone_id=zone_id,
            center=center,
            radius_meters=radius_meters,
            threat_level=threat_level,
            threat_type=threat_type,
            description=description,
            expires_at=expires_at,
        )
        strategy_map.threat_zones.append(threat_zone)
        strategy_map.updated_at = datetime.now(UTC)

        # Log event
        event = MapUpdateEvent(
            incident_id=incident_id,
            event_type="threat_zone_added",
            element_id=zone_id,
            data={"threat_level": threat_level, "radius": radius_meters},
        )
        self._events.append(event)

        logger.info(
            "threat_zone_added_to_map",
            incident_id=incident_id,
            zone_id=zone_id,
            threat_level=threat_level,
        )

        return threat_zone

    async def remove_element(
        self,
        incident_id: str,
        element_type: str,
        element_id: str,
        removed_by: str | None = None,
    ) -> bool:
        """
        Remove an element from the map.

        Args:
            incident_id: ID of the incident
            element_type: Type of element (marker, shape, unit, camera, etc.)
            element_id: ID of element to remove
            removed_by: User removing the element

        Returns:
            True if removed, False otherwise
        """
        strategy_map = self._maps.get(incident_id)
        if not strategy_map:
            return False

        removed = False

        if element_type == "marker":
            for layer in strategy_map.layers:
                layer.markers = [m for m in layer.markers if m.id != element_id]
            removed = True
        elif element_type == "shape":
            for layer in strategy_map.layers:
                layer.shapes = [s for s in layer.shapes if s.id != element_id]
            removed = True
        elif element_type == "unit":
            strategy_map.unit_positions = [
                u for u in strategy_map.unit_positions if u.unit_id != element_id
            ]
            removed = True
        elif element_type == "camera":
            strategy_map.cameras = [
                c for c in strategy_map.cameras if c.camera_id != element_id
            ]
            removed = True
        elif element_type == "gunfire":
            strategy_map.gunfire_detections = [
                g for g in strategy_map.gunfire_detections if g.detection_id != element_id
            ]
            removed = True
        elif element_type == "vehicle":
            strategy_map.vehicle_paths = [
                v for v in strategy_map.vehicle_paths if v.vehicle_id != element_id
            ]
            removed = True
        elif element_type == "threat_zone":
            strategy_map.threat_zones = [
                t for t in strategy_map.threat_zones if t.zone_id != element_id
            ]
            removed = True

        if removed:
            strategy_map.updated_at = datetime.now(UTC)

            # Log event
            event = MapUpdateEvent(
                incident_id=incident_id,
                event_type="element_removed",
                element_id=element_id,
                data={"element_type": element_type},
                user_id=removed_by,
            )
            self._events.append(event)

            logger.info(
                "map_element_removed",
                incident_id=incident_id,
                element_type=element_type,
                element_id=element_id,
                removed_by=removed_by,
            )

        return removed

    async def toggle_layer_visibility(
        self,
        incident_id: str,
        layer_id: str,
        is_visible: bool,
        updated_by: str | None = None,
    ) -> MapLayer | None:
        """
        Toggle layer visibility.

        Args:
            incident_id: ID of the incident
            layer_id: ID of the layer
            is_visible: Whether layer should be visible
            updated_by: User updating visibility

        Returns:
            Updated MapLayer or None
        """
        strategy_map = self._maps.get(incident_id)
        if not strategy_map:
            return None

        layer = next((lyr for lyr in strategy_map.layers if lyr.id == layer_id), None)
        if not layer:
            return None

        layer.is_visible = is_visible
        strategy_map.updated_at = datetime.now(UTC)

        # Log event
        event = MapUpdateEvent(
            incident_id=incident_id,
            event_type="layer_visibility_changed",
            layer_id=layer_id,
            data={"is_visible": is_visible},
            user_id=updated_by,
        )
        self._events.append(event)

        return layer

    async def get_events(
        self,
        incident_id: str,
        event_type: str | None = None,
        limit: int = 100,
    ) -> list[MapUpdateEvent]:
        """
        Get map update events.

        Args:
            incident_id: ID of the incident
            event_type: Filter by event type
            limit: Maximum number to return

        Returns:
            List of MapUpdateEvent
        """
        events = [e for e in self._events if e.incident_id == incident_id]

        if event_type:
            events = [e for e in events if e.event_type == event_type]

        events.sort(key=lambda x: x.timestamp, reverse=True)
        return events[:limit]

    async def export_map_data(self, incident_id: str) -> dict[str, Any] | None:
        """
        Export map data for an incident.

        Args:
            incident_id: ID of the incident

        Returns:
            Dictionary of map data or None
        """
        strategy_map = self._maps.get(incident_id)
        if not strategy_map:
            return None

        return strategy_map.model_dump()
