"""
Entity Renderer.

Renders real-time positions of officers, drones, vehicles, and other
entities on the digital twin.
"""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Optional
from collections import deque
from pydantic import BaseModel, Field


class EntityType(str, Enum):
    """Types of entities that can be rendered."""
    OFFICER = "officer"
    PATROL_VEHICLE = "patrol_vehicle"
    UNMARKED_VEHICLE = "unmarked_vehicle"
    DRONE = "drone"
    SUSPECT = "suspect"
    VICTIM = "victim"
    WITNESS = "witness"
    CIVILIAN = "civilian"
    AMBULANCE = "ambulance"
    FIRE_TRUCK = "fire_truck"
    K9_UNIT = "k9_unit"
    SWAT_UNIT = "swat_unit"
    HELICOPTER = "helicopter"
    BOAT = "boat"
    INCIDENT = "incident"
    SENSOR = "sensor"
    CAMERA = "camera"
    PERIMETER = "perimeter"


class EntityStatus(str, Enum):
    """Status of an entity."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    RESPONDING = "responding"
    ON_SCENE = "on_scene"
    AVAILABLE = "available"
    BUSY = "busy"
    OFFLINE = "offline"
    EMERGENCY = "emergency"


class EntityPosition(BaseModel):
    """Position data for an entity."""
    latitude: float
    longitude: float
    altitude_m: float = 0.0
    heading_deg: Optional[float] = None
    speed_kmh: Optional[float] = None
    accuracy_m: float = 5.0
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    source: str = "gps"


class RenderedEntity(BaseModel):
    """Entity rendered on the digital twin."""
    entity_id: str
    entity_type: EntityType
    status: EntityStatus = EntityStatus.ACTIVE
    name: str
    call_sign: str = ""
    position: EntityPosition
    icon_url: Optional[str] = None
    color: str = "#3B82F6"
    size: float = 1.0
    rotation_deg: float = 0.0
    visible: bool = True
    selectable: bool = True
    label: str = ""
    tooltip: str = ""
    trail_enabled: bool = False
    trail_length: int = 10
    trail_positions: list[EntityPosition] = Field(default_factory=list)
    assigned_incident_id: Optional[str] = None
    unit_id: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class EntityGroup(BaseModel):
    """Group of entities."""
    group_id: str
    name: str
    entity_ids: list[str] = Field(default_factory=list)
    color: str = "#3B82F6"
    visible: bool = True
    metadata: dict[str, Any] = Field(default_factory=dict)


class RendererConfig(BaseModel):
    """Configuration for entity renderer."""
    max_entities: int = 10000
    max_trail_length: int = 100
    position_history_size: int = 1000
    stale_threshold_seconds: int = 300
    default_colors: dict[str, str] = Field(default_factory=lambda: {
        "officer": "#3B82F6",
        "patrol_vehicle": "#10B981",
        "drone": "#8B5CF6",
        "incident": "#EF4444",
        "suspect": "#F59E0B",
        "ambulance": "#EC4899",
        "fire_truck": "#DC2626",
    })


class RendererMetrics(BaseModel):
    """Metrics for entity renderer."""
    total_entities: int = 0
    entities_by_type: dict[str, int] = Field(default_factory=dict)
    entities_by_status: dict[str, int] = Field(default_factory=dict)
    active_entities: int = 0
    stale_entities: int = 0
    position_updates_per_minute: float = 0.0


class EntityRenderer:
    """
    Entity Renderer.
    
    Renders real-time positions of officers, drones, vehicles, and other
    entities on the digital twin.
    """
    
    def __init__(self, config: Optional[RendererConfig] = None):
        self.config = config or RendererConfig()
        self._entities: dict[str, RenderedEntity] = {}
        self._groups: dict[str, EntityGroup] = {}
        self._position_history: dict[str, deque[EntityPosition]] = {}
        self._callbacks: list[Callable] = []
        self._running = False
        self._metrics = RendererMetrics()
        self._update_count = 0
    
    async def start(self) -> None:
        """Start the entity renderer."""
        self._running = True
    
    async def stop(self) -> None:
        """Stop the entity renderer."""
        self._running = False
    
    def add_entity(
        self,
        entity_type: EntityType,
        name: str,
        latitude: float,
        longitude: float,
        altitude_m: float = 0.0,
        call_sign: str = "",
        status: EntityStatus = EntityStatus.ACTIVE,
        color: Optional[str] = None,
        unit_id: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> RenderedEntity:
        """Add an entity to the renderer."""
        entity_id = f"entity-{uuid.uuid4().hex[:12]}"
        
        position = EntityPosition(
            latitude=latitude,
            longitude=longitude,
            altitude_m=altitude_m,
        )
        
        entity_color = color or self.config.default_colors.get(entity_type.value, "#3B82F6")
        
        entity = RenderedEntity(
            entity_id=entity_id,
            entity_type=entity_type,
            status=status,
            name=name,
            call_sign=call_sign,
            position=position,
            color=entity_color,
            label=call_sign or name,
            unit_id=unit_id,
            metadata=metadata or {},
        )
        
        self._entities[entity_id] = entity
        self._position_history[entity_id] = deque(maxlen=self.config.position_history_size)
        self._position_history[entity_id].append(position)
        
        self._update_metrics()
        
        return entity
    
    def remove_entity(self, entity_id: str) -> bool:
        """Remove an entity from the renderer."""
        if entity_id not in self._entities:
            return False
        
        del self._entities[entity_id]
        if entity_id in self._position_history:
            del self._position_history[entity_id]
        
        for group in self._groups.values():
            if entity_id in group.entity_ids:
                group.entity_ids.remove(entity_id)
        
        self._update_metrics()
        return True
    
    def get_entity(self, entity_id: str) -> Optional[RenderedEntity]:
        """Get an entity by ID."""
        return self._entities.get(entity_id)
    
    def get_all_entities(self) -> list[RenderedEntity]:
        """Get all entities."""
        return list(self._entities.values())
    
    def get_entities_by_type(self, entity_type: EntityType) -> list[RenderedEntity]:
        """Get entities by type."""
        return [e for e in self._entities.values() if e.entity_type == entity_type]
    
    def get_entities_by_status(self, status: EntityStatus) -> list[RenderedEntity]:
        """Get entities by status."""
        return [e for e in self._entities.values() if e.status == status]
    
    def get_visible_entities(self) -> list[RenderedEntity]:
        """Get all visible entities."""
        return [e for e in self._entities.values() if e.visible]
    
    def get_entities_in_area(
        self,
        center_lat: float,
        center_lon: float,
        radius_km: float,
    ) -> list[RenderedEntity]:
        """Get entities within a geographic area."""
        result = []
        for entity in self._entities.values():
            distance = self._calculate_distance(
                center_lat, center_lon,
                entity.position.latitude, entity.position.longitude,
            )
            if distance <= radius_km:
                result.append(entity)
        return result
    
    async def update_position(
        self,
        entity_id: str,
        latitude: float,
        longitude: float,
        altitude_m: Optional[float] = None,
        heading_deg: Optional[float] = None,
        speed_kmh: Optional[float] = None,
        accuracy_m: float = 5.0,
    ) -> Optional[RenderedEntity]:
        """Update entity position."""
        entity = self._entities.get(entity_id)
        if not entity:
            return None
        
        position = EntityPosition(
            latitude=latitude,
            longitude=longitude,
            altitude_m=altitude_m if altitude_m is not None else entity.position.altitude_m,
            heading_deg=heading_deg,
            speed_kmh=speed_kmh,
            accuracy_m=accuracy_m,
        )
        
        entity.position = position
        entity.updated_at = datetime.now(timezone.utc)
        
        if heading_deg is not None:
            entity.rotation_deg = heading_deg
        
        self._position_history[entity_id].append(position)
        
        if entity.trail_enabled:
            entity.trail_positions = list(self._position_history[entity_id])[-entity.trail_length:]
        
        self._update_count += 1
        
        await self._notify_callbacks(entity, "position_update")
        
        return entity
    
    async def update_status(
        self,
        entity_id: str,
        status: EntityStatus,
    ) -> Optional[RenderedEntity]:
        """Update entity status."""
        entity = self._entities.get(entity_id)
        if not entity:
            return None
        
        entity.status = status
        entity.updated_at = datetime.now(timezone.utc)
        
        self._update_metrics()
        await self._notify_callbacks(entity, "status_update")
        
        return entity
    
    def set_visibility(
        self,
        entity_id: str,
        visible: bool,
    ) -> bool:
        """Set entity visibility."""
        entity = self._entities.get(entity_id)
        if not entity:
            return False
        
        entity.visible = visible
        entity.updated_at = datetime.now(timezone.utc)
        return True
    
    def set_trail_enabled(
        self,
        entity_id: str,
        enabled: bool,
        trail_length: int = 10,
    ) -> bool:
        """Enable or disable position trail for an entity."""
        entity = self._entities.get(entity_id)
        if not entity:
            return False
        
        entity.trail_enabled = enabled
        entity.trail_length = min(trail_length, self.config.max_trail_length)
        
        if enabled and entity_id in self._position_history:
            entity.trail_positions = list(self._position_history[entity_id])[-entity.trail_length:]
        else:
            entity.trail_positions = []
        
        return True
    
    def assign_to_incident(
        self,
        entity_id: str,
        incident_id: str,
    ) -> bool:
        """Assign an entity to an incident."""
        entity = self._entities.get(entity_id)
        if not entity:
            return False
        
        entity.assigned_incident_id = incident_id
        entity.updated_at = datetime.now(timezone.utc)
        return True
    
    def clear_incident_assignment(self, entity_id: str) -> bool:
        """Clear incident assignment for an entity."""
        entity = self._entities.get(entity_id)
        if not entity:
            return False
        
        entity.assigned_incident_id = None
        entity.updated_at = datetime.now(timezone.utc)
        return True
    
    def get_entities_for_incident(self, incident_id: str) -> list[RenderedEntity]:
        """Get all entities assigned to an incident."""
        return [e for e in self._entities.values() if e.assigned_incident_id == incident_id]
    
    def create_group(
        self,
        name: str,
        entity_ids: Optional[list[str]] = None,
        color: str = "#3B82F6",
    ) -> EntityGroup:
        """Create an entity group."""
        group_id = f"group-{uuid.uuid4().hex[:8]}"
        
        group = EntityGroup(
            group_id=group_id,
            name=name,
            entity_ids=entity_ids or [],
            color=color,
        )
        
        self._groups[group_id] = group
        return group
    
    def delete_group(self, group_id: str) -> bool:
        """Delete an entity group."""
        if group_id not in self._groups:
            return False
        
        del self._groups[group_id]
        return True
    
    def add_to_group(self, group_id: str, entity_id: str) -> bool:
        """Add an entity to a group."""
        group = self._groups.get(group_id)
        if not group or entity_id not in self._entities:
            return False
        
        if entity_id not in group.entity_ids:
            group.entity_ids.append(entity_id)
        
        return True
    
    def remove_from_group(self, group_id: str, entity_id: str) -> bool:
        """Remove an entity from a group."""
        group = self._groups.get(group_id)
        if not group:
            return False
        
        if entity_id in group.entity_ids:
            group.entity_ids.remove(entity_id)
        
        return True
    
    def get_group(self, group_id: str) -> Optional[EntityGroup]:
        """Get a group by ID."""
        return self._groups.get(group_id)
    
    def get_all_groups(self) -> list[EntityGroup]:
        """Get all groups."""
        return list(self._groups.values())
    
    def get_group_entities(self, group_id: str) -> list[RenderedEntity]:
        """Get all entities in a group."""
        group = self._groups.get(group_id)
        if not group:
            return []
        
        return [self._entities[eid] for eid in group.entity_ids if eid in self._entities]
    
    def set_group_visibility(self, group_id: str, visible: bool) -> bool:
        """Set visibility for all entities in a group."""
        group = self._groups.get(group_id)
        if not group:
            return False
        
        group.visible = visible
        for entity_id in group.entity_ids:
            if entity_id in self._entities:
                self._entities[entity_id].visible = visible
        
        return True
    
    def get_position_history(
        self,
        entity_id: str,
        limit: int = 100,
    ) -> list[EntityPosition]:
        """Get position history for an entity."""
        if entity_id not in self._position_history:
            return []
        
        history = list(self._position_history[entity_id])
        history.reverse()
        return history[:limit]
    
    def get_stale_entities(self) -> list[RenderedEntity]:
        """Get entities with stale positions."""
        now = datetime.now(timezone.utc)
        stale = []
        
        for entity in self._entities.values():
            age = (now - entity.position.timestamp).total_seconds()
            if age > self.config.stale_threshold_seconds:
                stale.append(entity)
        
        return stale
    
    def get_render_data(self) -> dict[str, Any]:
        """Get all data needed for rendering."""
        return {
            "entities": [e.model_dump() for e in self._entities.values() if e.visible],
            "groups": [g.model_dump() for g in self._groups.values() if g.visible],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    
    def get_metrics(self) -> RendererMetrics:
        """Get renderer metrics."""
        return self._metrics
    
    def get_status(self) -> dict[str, Any]:
        """Get renderer status."""
        return {
            "running": self._running,
            "total_entities": len(self._entities),
            "total_groups": len(self._groups),
            "metrics": self._metrics.model_dump(),
        }
    
    def register_callback(self, callback: Callable) -> None:
        """Register a callback for entity events."""
        if callback not in self._callbacks:
            self._callbacks.append(callback)
    
    def unregister_callback(self, callback: Callable) -> None:
        """Unregister a callback."""
        if callback in self._callbacks:
            self._callbacks.remove(callback)
    
    def _update_metrics(self) -> None:
        """Update renderer metrics."""
        type_counts: dict[str, int] = {}
        status_counts: dict[str, int] = {}
        active = 0
        stale = 0
        
        now = datetime.now(timezone.utc)
        
        for entity in self._entities.values():
            type_counts[entity.entity_type.value] = type_counts.get(entity.entity_type.value, 0) + 1
            status_counts[entity.status.value] = status_counts.get(entity.status.value, 0) + 1
            
            if entity.status == EntityStatus.ACTIVE:
                active += 1
            
            age = (now - entity.position.timestamp).total_seconds()
            if age > self.config.stale_threshold_seconds:
                stale += 1
        
        self._metrics.total_entities = len(self._entities)
        self._metrics.entities_by_type = type_counts
        self._metrics.entities_by_status = status_counts
        self._metrics.active_entities = active
        self._metrics.stale_entities = stale
    
    async def _notify_callbacks(self, entity: RenderedEntity, event_type: str) -> None:
        """Notify registered callbacks."""
        for callback in self._callbacks:
            try:
                if callable(callback):
                    result = callback(entity, event_type)
                    if hasattr(result, "__await__"):
                        await result
            except Exception:
                pass
    
    @staticmethod
    def _calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points in kilometers."""
        import math
        
        R = 6371.0
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = (
            math.sin(delta_lat / 2) ** 2
            + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
