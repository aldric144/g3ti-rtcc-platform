"""
G3TI RTCC-UIP Scene Coordination Module.

Provides multi-unit scene coordination capabilities:
- Assign officers to tactical roles (contact, cover, perimeter, ingress, egress)
- Reassign units dynamically
- RTCC visibility into which units are on scene
- Integration with Phase 5 tactical data and Phase 6 safety status
- Real-time unit positions and safety levels
- Tactical recommendations

All scene coordination actions are logged for CJIS compliance.
"""

import uuid
from datetime import UTC, datetime
from enum import Enum
from typing import Any

import structlog
from pydantic import BaseModel, Field

logger = structlog.get_logger(__name__)


class TacticalRole(str, Enum):
    """Tactical roles for scene coordination."""
    CONTACT = "contact"  # Primary contact with subject
    COVER = "cover"  # Cover/backup for contact
    PERIMETER = "perimeter"  # Perimeter security
    INGRESS = "ingress"  # Entry point control
    EGRESS = "egress"  # Exit point control
    TRAFFIC = "traffic"  # Traffic control
    SURVEILLANCE = "surveillance"  # Observation/surveillance
    COMMAND = "command"  # On-scene commander
    MEDICAL = "medical"  # Medical standby
    K9 = "k9"  # K9 unit
    NEGOTIATOR = "negotiator"  # Crisis negotiator
    SWAT = "swat"  # SWAT/tactical team
    UNASSIGNED = "unassigned"  # On scene but no role


class UnitSafetyLevel(str, Enum):
    """Unit safety level indicators."""
    GREEN = "green"  # Safe/normal
    YELLOW = "yellow"  # Caution/elevated risk
    ORANGE = "orange"  # High risk
    RED = "red"  # Critical/danger
    BLACK = "black"  # Officer down/emergency


class SceneStatus(str, Enum):
    """Scene status values."""
    ACTIVE = "active"
    CONTAINED = "contained"
    CLEARING = "clearing"
    SECURED = "secured"
    CLOSED = "closed"


class SceneUnit(BaseModel):
    """Schema for a unit assigned to a scene."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    unit_id: str
    badge: str | None = None
    officer_name: str | None = None

    # Role assignment
    role: TacticalRole = TacticalRole.UNASSIGNED
    role_assigned_at: datetime | None = None
    role_assigned_by: str | None = None

    # Position
    latitude: float | None = None
    longitude: float | None = None
    position_description: str | None = None  # e.g., "North perimeter", "Front door"
    last_position_update: datetime | None = None

    # Status
    status: str = "on_scene"  # on_scene, en_route, cleared
    safety_level: UnitSafetyLevel = UnitSafetyLevel.GREEN
    safety_score: float | None = None  # From Phase 6
    threat_indicators: list[str] = Field(default_factory=list)

    # Communication
    radio_channel: str | None = None
    last_check_in: datetime | None = None

    # Metadata
    arrived_at: datetime | None = None
    cleared_at: datetime | None = None
    notes: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class Scene(BaseModel):
    """Schema for a coordinated scene."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    incident_id: str
    incident_type: str

    # Location
    address: str
    latitude: float | None = None
    longitude: float | None = None

    # Status
    status: SceneStatus = SceneStatus.ACTIVE
    threat_level: str = "unknown"  # low, medium, high, critical

    # Units
    units: list[SceneUnit] = Field(default_factory=list)
    commander_unit_id: str | None = None

    # Perimeter (from Phase 6)
    inner_perimeter: list[tuple[float, float]] | None = None
    outer_perimeter: list[tuple[float, float]] | None = None

    # Tactical info
    tactical_notes: list[str] = Field(default_factory=list)
    recommended_actions: list[str] = Field(default_factory=list)
    hazards: list[str] = Field(default_factory=list)

    # Communication
    primary_radio_channel: str | None = None
    tactical_radio_channel: str | None = None

    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime | None = None
    closed_at: datetime | None = None

    # Metadata
    created_by: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    # CJIS compliance
    audit_id: str = Field(default_factory=lambda: str(uuid.uuid4()))


class SceneEvent(BaseModel):
    """Schema for scene coordination events."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    scene_id: str
    event_type: str  # unit_assigned, role_changed, status_update, etc.
    unit_id: str | None = None
    data: dict[str, Any] = Field(default_factory=dict)
    created_by: str | None = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


class SceneCoordinationManager:
    """
    Central manager for multi-unit scene coordination.

    Handles unit assignment, role management, position tracking,
    and tactical recommendations.
    """

    def __init__(
        self,
        redis_manager: Any | None = None,
        tactical_manager: Any | None = None,
        officer_safety_manager: Any | None = None,
        dispatch_engine: Any | None = None,
    ):
        """
        Initialize the scene coordination manager.

        Args:
            redis_manager: Redis manager for caching and pub/sub
            tactical_manager: Phase 5 tactical engine
            officer_safety_manager: Phase 6 officer safety engine
            dispatch_engine: CAD dispatch overlay engine
        """
        self.redis = redis_manager
        self.tactical = tactical_manager
        self.officer_safety = officer_safety_manager
        self.dispatch = dispatch_engine

        # In-memory stores
        self._scenes: dict[str, Scene] = {}
        self._scene_events: list[SceneEvent] = []
        self._event_handlers: list[Any] = []

        logger.info("scene_coordination_manager_initialized")

    async def create_scene(
        self,
        incident_id: str,
        incident_type: str,
        address: str,
        latitude: float | None = None,
        longitude: float | None = None,
        threat_level: str = "unknown",
        created_by: str | None = None,
        primary_radio_channel: str | None = None,
        tactical_radio_channel: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Scene:
        """
        Create a new coordinated scene.

        Args:
            incident_id: Associated incident ID
            incident_type: Type of incident
            address: Scene address
            latitude: Scene latitude
            longitude: Scene longitude
            threat_level: Initial threat level
            created_by: User who created the scene
            primary_radio_channel: Primary radio channel
            tactical_radio_channel: Tactical radio channel
            metadata: Additional metadata

        Returns:
            The created scene
        """
        scene = Scene(
            incident_id=incident_id,
            incident_type=incident_type,
            address=address,
            latitude=latitude,
            longitude=longitude,
            threat_level=threat_level,
            created_by=created_by,
            primary_radio_channel=primary_radio_channel,
            tactical_radio_channel=tactical_radio_channel,
            metadata=metadata or {},
        )

        # Get tactical recommendations if available
        if self.tactical and latitude and longitude:
            scene.recommended_actions = await self._get_tactical_recommendations(
                latitude, longitude, incident_type
            )

        # Store scene
        self._scenes[scene.id] = scene

        # Create event
        await self._create_event(
            scene_id=scene.id,
            event_type="scene_created",
            data={"incident_id": incident_id, "incident_type": incident_type},
            created_by=created_by,
        )

        logger.info(
            "scene_created",
            scene_id=scene.id,
            incident_id=incident_id,
            incident_type=incident_type,
            audit_id=scene.audit_id,
        )

        return scene

    async def assign_unit(
        self,
        scene_id: str,
        unit_id: str,
        role: TacticalRole = TacticalRole.UNASSIGNED,
        badge: str | None = None,
        officer_name: str | None = None,
        position_description: str | None = None,
        assigned_by: str | None = None,
    ) -> tuple[Scene, SceneUnit]:
        """
        Assign a unit to a scene.

        Args:
            scene_id: Scene ID
            unit_id: Unit ID to assign
            role: Tactical role
            badge: Officer badge
            officer_name: Officer name
            position_description: Position description
            assigned_by: User who assigned

        Returns:
            Tuple of (updated scene, assigned unit)
        """
        scene = self._scenes.get(scene_id)
        if not scene:
            raise ValueError(f"Scene {scene_id} not found")

        # Check if unit already assigned
        existing_unit = next(
            (u for u in scene.units if u.unit_id == unit_id),
            None
        )

        if existing_unit:
            # Update existing assignment
            existing_unit.role = role
            existing_unit.role_assigned_at = datetime.now(UTC)
            existing_unit.role_assigned_by = assigned_by
            existing_unit.position_description = position_description
            scene_unit = existing_unit
        else:
            # Create new assignment
            scene_unit = SceneUnit(
                unit_id=unit_id,
                badge=badge,
                officer_name=officer_name,
                role=role,
                role_assigned_at=datetime.now(UTC),
                role_assigned_by=assigned_by,
                position_description=position_description,
                arrived_at=datetime.now(UTC),
            )
            scene.units.append(scene_unit)

        # Get safety info from Phase 6 if available
        if self.officer_safety and badge:
            safety_info = await self._get_officer_safety_info(badge)
            if safety_info:
                scene_unit.safety_level = safety_info.get("level", UnitSafetyLevel.GREEN)
                scene_unit.safety_score = safety_info.get("score")
                scene_unit.threat_indicators = safety_info.get("indicators", [])

        scene.updated_at = datetime.now(UTC)

        # Create event
        await self._create_event(
            scene_id=scene_id,
            event_type="unit_assigned",
            unit_id=unit_id,
            data={
                "role": role.value,
                "badge": badge,
                "position": position_description,
            },
            created_by=assigned_by,
        )

        logger.info(
            "unit_assigned_to_scene",
            scene_id=scene_id,
            unit_id=unit_id,
            role=role.value,
            audit_id=scene.audit_id,
        )

        return scene, scene_unit

    async def update_unit_role(
        self,
        scene_id: str,
        unit_id: str,
        new_role: TacticalRole,
        position_description: str | None = None,
        updated_by: str | None = None,
    ) -> tuple[Scene, SceneUnit]:
        """
        Update a unit's role on a scene.

        Args:
            scene_id: Scene ID
            unit_id: Unit ID
            new_role: New tactical role
            position_description: New position description
            updated_by: User who updated

        Returns:
            Tuple of (updated scene, updated unit)
        """
        scene = self._scenes.get(scene_id)
        if not scene:
            raise ValueError(f"Scene {scene_id} not found")

        scene_unit = next(
            (u for u in scene.units if u.unit_id == unit_id),
            None
        )

        if not scene_unit:
            raise ValueError(f"Unit {unit_id} not found on scene {scene_id}")

        old_role = scene_unit.role
        scene_unit.role = new_role
        scene_unit.role_assigned_at = datetime.now(UTC)
        scene_unit.role_assigned_by = updated_by

        if position_description:
            scene_unit.position_description = position_description

        scene.updated_at = datetime.now(UTC)

        # Create event
        await self._create_event(
            scene_id=scene_id,
            event_type="role_changed",
            unit_id=unit_id,
            data={
                "old_role": old_role.value,
                "new_role": new_role.value,
                "position": position_description,
            },
            created_by=updated_by,
        )

        logger.info(
            "unit_role_changed",
            scene_id=scene_id,
            unit_id=unit_id,
            old_role=old_role.value,
            new_role=new_role.value,
        )

        return scene, scene_unit

    async def update_unit_position(
        self,
        scene_id: str,
        unit_id: str,
        latitude: float,
        longitude: float,
        position_description: str | None = None,
    ) -> SceneUnit:
        """
        Update a unit's position on a scene.

        Args:
            scene_id: Scene ID
            unit_id: Unit ID
            latitude: New latitude
            longitude: New longitude
            position_description: Position description

        Returns:
            Updated unit
        """
        scene = self._scenes.get(scene_id)
        if not scene:
            raise ValueError(f"Scene {scene_id} not found")

        scene_unit = next(
            (u for u in scene.units if u.unit_id == unit_id),
            None
        )

        if not scene_unit:
            raise ValueError(f"Unit {unit_id} not found on scene {scene_id}")

        scene_unit.latitude = latitude
        scene_unit.longitude = longitude
        scene_unit.last_position_update = datetime.now(UTC)

        if position_description:
            scene_unit.position_description = position_description

        return scene_unit

    async def update_unit_safety(
        self,
        scene_id: str,
        unit_id: str,
        safety_level: UnitSafetyLevel,
        safety_score: float | None = None,
        threat_indicators: list[str] | None = None,
    ) -> SceneUnit:
        """
        Update a unit's safety status.

        Args:
            scene_id: Scene ID
            unit_id: Unit ID
            safety_level: New safety level
            safety_score: Safety score
            threat_indicators: Threat indicators

        Returns:
            Updated unit
        """
        scene = self._scenes.get(scene_id)
        if not scene:
            raise ValueError(f"Scene {scene_id} not found")

        scene_unit = next(
            (u for u in scene.units if u.unit_id == unit_id),
            None
        )

        if not scene_unit:
            raise ValueError(f"Unit {unit_id} not found on scene {scene_id}")

        old_level = scene_unit.safety_level
        scene_unit.safety_level = safety_level
        scene_unit.safety_score = safety_score

        if threat_indicators:
            scene_unit.threat_indicators = threat_indicators

        # Create event if safety level changed significantly
        if old_level != safety_level:
            await self._create_event(
                scene_id=scene_id,
                event_type="safety_level_changed",
                unit_id=unit_id,
                data={
                    "old_level": old_level.value,
                    "new_level": safety_level.value,
                    "score": safety_score,
                    "indicators": threat_indicators,
                },
            )

        return scene_unit

    async def remove_unit(
        self,
        scene_id: str,
        unit_id: str,
        removed_by: str | None = None,
    ) -> Scene:
        """
        Remove a unit from a scene.

        Args:
            scene_id: Scene ID
            unit_id: Unit ID to remove
            removed_by: User who removed

        Returns:
            Updated scene
        """
        scene = self._scenes.get(scene_id)
        if not scene:
            raise ValueError(f"Scene {scene_id} not found")

        scene_unit = next(
            (u for u in scene.units if u.unit_id == unit_id),
            None
        )

        if scene_unit:
            scene_unit.status = "cleared"
            scene_unit.cleared_at = datetime.now(UTC)
            scene.units = [u for u in scene.units if u.unit_id != unit_id]

        scene.updated_at = datetime.now(UTC)

        # Create event
        await self._create_event(
            scene_id=scene_id,
            event_type="unit_removed",
            unit_id=unit_id,
            data={"removed_by": removed_by},
            created_by=removed_by,
        )

        logger.info(
            "unit_removed_from_scene",
            scene_id=scene_id,
            unit_id=unit_id,
        )

        return scene

    async def set_commander(
        self,
        scene_id: str,
        unit_id: str,
        set_by: str | None = None,
    ) -> Scene:
        """
        Set the on-scene commander.

        Args:
            scene_id: Scene ID
            unit_id: Commander unit ID
            set_by: User who set commander

        Returns:
            Updated scene
        """
        scene = self._scenes.get(scene_id)
        if not scene:
            raise ValueError(f"Scene {scene_id} not found")

        # Verify unit is on scene
        scene_unit = next(
            (u for u in scene.units if u.unit_id == unit_id),
            None
        )

        if not scene_unit:
            raise ValueError(f"Unit {unit_id} not found on scene {scene_id}")

        # Update commander
        old_commander = scene.commander_unit_id
        scene.commander_unit_id = unit_id
        scene_unit.role = TacticalRole.COMMAND
        scene.updated_at = datetime.now(UTC)

        # Create event
        await self._create_event(
            scene_id=scene_id,
            event_type="commander_set",
            unit_id=unit_id,
            data={"old_commander": old_commander},
            created_by=set_by,
        )

        logger.info(
            "scene_commander_set",
            scene_id=scene_id,
            unit_id=unit_id,
            audit_id=scene.audit_id,
        )

        return scene

    async def update_scene_status(
        self,
        scene_id: str,
        status: SceneStatus,
        updated_by: str | None = None,
    ) -> Scene:
        """
        Update scene status.

        Args:
            scene_id: Scene ID
            status: New status
            updated_by: User who updated

        Returns:
            Updated scene
        """
        scene = self._scenes.get(scene_id)
        if not scene:
            raise ValueError(f"Scene {scene_id} not found")

        old_status = scene.status
        scene.status = status
        scene.updated_at = datetime.now(UTC)

        if status == SceneStatus.CLOSED:
            scene.closed_at = datetime.now(UTC)

        # Create event
        await self._create_event(
            scene_id=scene_id,
            event_type="status_changed",
            data={
                "old_status": old_status.value,
                "new_status": status.value,
            },
            created_by=updated_by,
        )

        logger.info(
            "scene_status_changed",
            scene_id=scene_id,
            old_status=old_status.value,
            new_status=status.value,
            audit_id=scene.audit_id,
        )

        return scene

    async def add_tactical_note(
        self,
        scene_id: str,
        note: str,
        added_by: str | None = None,
    ) -> Scene:
        """Add a tactical note to a scene."""
        scene = self._scenes.get(scene_id)
        if not scene:
            raise ValueError(f"Scene {scene_id} not found")

        scene.tactical_notes.append(f"[{datetime.now(UTC).isoformat()}] {note}")
        scene.updated_at = datetime.now(UTC)

        await self._create_event(
            scene_id=scene_id,
            event_type="note_added",
            data={"note": note},
            created_by=added_by,
        )

        return scene

    async def add_hazard(
        self,
        scene_id: str,
        hazard: str,
        added_by: str | None = None,
    ) -> Scene:
        """Add a hazard to a scene."""
        scene = self._scenes.get(scene_id)
        if not scene:
            raise ValueError(f"Scene {scene_id} not found")

        if hazard not in scene.hazards:
            scene.hazards.append(hazard)
        scene.updated_at = datetime.now(UTC)

        await self._create_event(
            scene_id=scene_id,
            event_type="hazard_added",
            data={"hazard": hazard},
            created_by=added_by,
        )

        return scene

    async def get_scene(self, scene_id: str) -> Scene | None:
        """Get a scene by ID."""
        return self._scenes.get(scene_id)

    async def get_scene_by_incident(self, incident_id: str) -> Scene | None:
        """Get a scene by incident ID."""
        for scene in self._scenes.values():
            if scene.incident_id == incident_id:
                return scene
        return None

    async def get_active_scenes(self) -> list[Scene]:
        """Get all active scenes."""
        return [
            s for s in self._scenes.values()
            if s.status not in [SceneStatus.CLOSED]
        ]

    async def get_scene_status(self, scene_id: str) -> dict[str, Any]:
        """
        Get comprehensive scene status.

        Args:
            scene_id: Scene ID

        Returns:
            Scene status dictionary
        """
        scene = self._scenes.get(scene_id)
        if not scene:
            raise ValueError(f"Scene {scene_id} not found")

        # Count units by role
        units_by_role = {}
        for role in TacticalRole:
            units_by_role[role.value] = len([
                u for u in scene.units if u.role == role
            ])

        # Count units by safety level
        units_by_safety = {}
        for level in UnitSafetyLevel:
            units_by_safety[level.value] = len([
                u for u in scene.units if u.safety_level == level
            ])

        # Get commander info
        commander = None
        if scene.commander_unit_id:
            commander = next(
                (u for u in scene.units if u.unit_id == scene.commander_unit_id),
                None
            )

        return {
            "scene_id": scene.id,
            "incident_id": scene.incident_id,
            "incident_type": scene.incident_type,
            "status": scene.status.value,
            "threat_level": scene.threat_level,
            "address": scene.address,
            "total_units": len(scene.units),
            "units_by_role": units_by_role,
            "units_by_safety": units_by_safety,
            "commander": commander.model_dump() if commander else None,
            "hazards": scene.hazards,
            "tactical_notes": scene.tactical_notes[-5:],  # Last 5 notes
            "recommended_actions": scene.recommended_actions,
            "created_at": scene.created_at.isoformat(),
            "updated_at": scene.updated_at.isoformat() if scene.updated_at else None,
        }

    async def get_scene_events(
        self,
        scene_id: str,
        limit: int = 50,
    ) -> list[SceneEvent]:
        """Get events for a scene."""
        events = [e for e in self._scene_events if e.scene_id == scene_id]
        events.sort(key=lambda e: e.timestamp, reverse=True)
        return events[:limit]

    async def _create_event(
        self,
        scene_id: str,
        event_type: str,
        unit_id: str | None = None,
        data: dict[str, Any] | None = None,
        created_by: str | None = None,
    ) -> SceneEvent:
        """Create a scene event."""
        event = SceneEvent(
            scene_id=scene_id,
            event_type=event_type,
            unit_id=unit_id,
            data=data or {},
            created_by=created_by,
        )
        self._scene_events.append(event)
        return event

    async def _get_tactical_recommendations(
        self,
        latitude: float,
        longitude: float,
        incident_type: str,
    ) -> list[str]:
        """Get tactical recommendations from Phase 5 engine."""
        # Placeholder - would integrate with tactical engine
        recommendations = []

        # Default recommendations based on incident type
        if incident_type in ["shots_fired", "active_shooter"]:
            recommendations = [
                "Establish perimeter immediately",
                "Request additional units",
                "Coordinate with SWAT if available",
                "Identify cover positions",
            ]
        elif incident_type in ["domestic", "disturbance"]:
            recommendations = [
                "Approach with caution",
                "Identify exits and cover",
                "Request backup before contact",
            ]
        elif incident_type in ["robbery", "burglary"]:
            recommendations = [
                "Establish perimeter",
                "Check for suspects fleeing",
                "Coordinate with K9 if available",
            ]

        return recommendations

    async def _get_officer_safety_info(
        self,
        badge: str,
    ) -> dict[str, Any] | None:
        """Get officer safety info from Phase 6 engine."""
        # Placeholder - would integrate with officer safety engine
        return {
            "level": UnitSafetyLevel.GREEN,
            "score": 85.0,
            "indicators": [],
        }


# Export classes
__all__ = [
    "SceneCoordinationManager",
    "Scene",
    "SceneUnit",
    "SceneEvent",
    "TacticalRole",
    "UnitSafetyLevel",
    "SceneStatus",
]
