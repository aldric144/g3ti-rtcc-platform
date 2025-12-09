"""
G3TI RTCC-UIP CAD Dispatch Overlay Engine.

Provides real-time CAD (Computer-Aided Dispatch) event tracking and overlay:
- Listen for CAD events (active calls, priority calls)
- Parse call type, priority, address, units assigned
- Track call status changes (en route, on scene, cleared)
- Auto-link calls to RMS history, tactical heatmaps, officer safety
- Publish call updates to WebSocket stream

Integrates with Phase 5 (Tactical) and Phase 6 (Officer Safety) engines.
"""

import uuid
from datetime import UTC, datetime
from enum import Enum
from typing import Any

import structlog
from pydantic import BaseModel, Field

logger = structlog.get_logger(__name__)


class CallPriority(str, Enum):
    """CAD call priority levels."""
    P1 = "P1"  # Emergency - immediate response
    P2 = "P2"  # Urgent - rapid response
    P3 = "P3"  # Routine - standard response
    P4 = "P4"  # Low priority - when available
    P5 = "P5"  # Administrative - scheduled


class CallStatus(str, Enum):
    """CAD call status values."""
    PENDING = "pending"  # Call received, not yet dispatched
    DISPATCHED = "dispatched"  # Units assigned
    EN_ROUTE = "en_route"  # Units responding
    ON_SCENE = "on_scene"  # Units arrived
    INVESTIGATING = "investigating"  # Active investigation
    CLEARED = "cleared"  # Call completed
    CANCELLED = "cancelled"  # Call cancelled


class UnitStatus(str, Enum):
    """Unit status values."""
    AVAILABLE = "available"
    DISPATCHED = "dispatched"
    EN_ROUTE = "en_route"
    ON_SCENE = "on_scene"
    BUSY = "busy"
    OUT_OF_SERVICE = "out_of_service"
    OFF_DUTY = "off_duty"


class CallType(str, Enum):
    """Common CAD call types."""
    SHOTS_FIRED = "shots_fired"
    ROBBERY = "robbery"
    BURGLARY = "burglary"
    ASSAULT = "assault"
    DOMESTIC = "domestic"
    TRAFFIC_STOP = "traffic_stop"
    TRAFFIC_ACCIDENT = "traffic_accident"
    SUSPICIOUS_PERSON = "suspicious_person"
    SUSPICIOUS_VEHICLE = "suspicious_vehicle"
    WELFARE_CHECK = "welfare_check"
    ALARM = "alarm"
    DISTURBANCE = "disturbance"
    MEDICAL = "medical"
    FIRE = "fire"
    PURSUIT = "pursuit"
    OFFICER_NEEDS_ASSISTANCE = "officer_needs_assistance"
    OTHER = "other"


class CADCall(BaseModel):
    """Schema for a CAD call."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    cad_id: str  # External CAD system ID
    call_type: CallType
    call_type_code: str  # Original CAD type code
    priority: CallPriority
    status: CallStatus = CallStatus.PENDING

    # Location information
    address: str
    city: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    location_notes: str | None = None
    beat: str | None = None
    district: str | None = None
    zone: str | None = None

    # Call details
    description: str | None = None
    caller_name: str | None = None
    caller_phone: str | None = None
    caller_type: str | None = None  # citizen, officer, alarm company

    # Assigned units
    assigned_units: list[str] = Field(default_factory=list)
    primary_unit: str | None = None

    # Timestamps
    received_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    dispatched_at: datetime | None = None
    en_route_at: datetime | None = None
    on_scene_at: datetime | None = None
    cleared_at: datetime | None = None

    # Linked data
    linked_incidents: list[str] = Field(default_factory=list)
    linked_entities: list[dict[str, Any]] = Field(default_factory=list)
    risk_indicators: list[str] = Field(default_factory=list)
    tactical_zone_id: str | None = None

    # Metadata
    disposition_code: str | None = None
    disposition_text: str | None = None
    notes: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    # CJIS compliance
    audit_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime | None = None


class DispatchUnit(BaseModel):
    """Schema for a dispatch unit."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    unit_id: str  # Unit identifier (e.g., "Charlie-21")
    badge: str | None = None
    officer_name: str | None = None
    status: UnitStatus = UnitStatus.AVAILABLE

    # Location
    latitude: float | None = None
    longitude: float | None = None
    last_location_update: datetime | None = None

    # Current assignment
    current_call_id: str | None = None
    current_call_priority: CallPriority | None = None

    # Shift info
    shift: str | None = None  # A, B, C
    beat: str | None = None
    district: str | None = None

    # Safety info (from Phase 6)
    safety_score: float | None = None
    threat_level: str | None = None

    # Metadata
    vehicle_id: str | None = None
    radio_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class CADEvent(BaseModel):
    """Schema for CAD events published to WebSocket."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str  # cad_call_created, cad_call_updated, cad_call_closed, unit_status_changed
    call_id: str | None = None
    unit_id: str | None = None
    data: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


class DispatchOverlayEngine:
    """
    CAD Dispatch Overlay Engine.

    Processes CAD events, tracks call status, links to intelligence data,
    and publishes updates for real-time dispatch overlay.
    """

    def __init__(
        self,
        redis_manager: Any | None = None,
        neo4j_manager: Any | None = None,
        elasticsearch_manager: Any | None = None,
        tactical_manager: Any | None = None,
        officer_safety_manager: Any | None = None,
    ):
        """
        Initialize the dispatch overlay engine.

        Args:
            redis_manager: Redis manager for caching and pub/sub
            neo4j_manager: Neo4j manager for entity relationships
            elasticsearch_manager: Elasticsearch for RMS search
            tactical_manager: Phase 5 tactical engine
            officer_safety_manager: Phase 6 officer safety engine
        """
        self.redis = redis_manager
        self.neo4j = neo4j_manager
        self.elasticsearch = elasticsearch_manager
        self.tactical = tactical_manager
        self.officer_safety = officer_safety_manager

        # In-memory stores
        self._calls: dict[str, CADCall] = {}
        self._units: dict[str, DispatchUnit] = {}
        self._call_history: list[CADCall] = []
        self._event_handlers: list[Any] = []

        logger.info("dispatch_overlay_engine_initialized")

    async def process_cad_event(
        self,
        event_type: str,
        event_data: dict[str, Any],
    ) -> CADEvent:
        """
        Process an incoming CAD event.

        Args:
            event_type: Type of CAD event
            event_data: Event data from CAD system

        Returns:
            Processed CAD event
        """
        logger.info(
            "processing_cad_event",
            event_type=event_type,
            cad_id=event_data.get("cad_id"),
        )

        if event_type == "new_call":
            return await self._handle_new_call(event_data)
        elif event_type == "call_update":
            return await self._handle_call_update(event_data)
        elif event_type == "call_closed":
            return await self._handle_call_closed(event_data)
        elif event_type == "unit_status":
            return await self._handle_unit_status(event_data)
        else:
            logger.warning("unknown_cad_event_type", event_type=event_type)
            return CADEvent(
                event_type="unknown",
                data=event_data,
            )

    async def _handle_new_call(self, event_data: dict[str, Any]) -> CADEvent:
        """Handle a new CAD call."""
        # Parse call type
        call_type = self._parse_call_type(event_data.get("call_type_code", ""))
        priority = self._parse_priority(event_data.get("priority", "P3"))

        # Create CAD call
        call = CADCall(
            cad_id=event_data.get("cad_id", str(uuid.uuid4())),
            call_type=call_type,
            call_type_code=event_data.get("call_type_code", ""),
            priority=priority,
            address=event_data.get("address", "Unknown"),
            city=event_data.get("city"),
            latitude=event_data.get("latitude"),
            longitude=event_data.get("longitude"),
            location_notes=event_data.get("location_notes"),
            beat=event_data.get("beat"),
            district=event_data.get("district"),
            zone=event_data.get("zone"),
            description=event_data.get("description"),
            caller_name=event_data.get("caller_name"),
            caller_phone=event_data.get("caller_phone"),
            caller_type=event_data.get("caller_type"),
        )

        # Auto-link to intelligence data
        await self._link_call_to_intelligence(call)

        # Store call
        self._calls[call.id] = call

        # Create event
        event = CADEvent(
            event_type="cad_call_created",
            call_id=call.id,
            data=call.model_dump(),
        )

        logger.info(
            "cad_call_created",
            call_id=call.id,
            cad_id=call.cad_id,
            call_type=call.call_type.value,
            priority=call.priority.value,
            audit_id=call.audit_id,
        )

        return event

    async def _handle_call_update(self, event_data: dict[str, Any]) -> CADEvent:
        """Handle a CAD call update."""
        cad_id = event_data.get("cad_id")
        call = self._get_call_by_cad_id(cad_id)

        if not call:
            logger.warning("call_not_found_for_update", cad_id=cad_id)
            # Create new call if not found
            return await self._handle_new_call(event_data)

        # Update status
        new_status = event_data.get("status")
        if new_status:
            call.status = CallStatus(new_status)

            # Update timestamps based on status
            now = datetime.now(UTC)
            if call.status == CallStatus.DISPATCHED and not call.dispatched_at:
                call.dispatched_at = now
            elif call.status == CallStatus.EN_ROUTE and not call.en_route_at:
                call.en_route_at = now
            elif call.status == CallStatus.ON_SCENE and not call.on_scene_at:
                call.on_scene_at = now
            elif call.status == CallStatus.CLEARED and not call.cleared_at:
                call.cleared_at = now

        # Update assigned units
        if "assigned_units" in event_data:
            call.assigned_units = event_data["assigned_units"]
        if "primary_unit" in event_data:
            call.primary_unit = event_data["primary_unit"]

        # Update notes
        if "note" in event_data:
            call.notes.append(event_data["note"])

        call.updated_at = datetime.now(UTC)

        # Create event
        event = CADEvent(
            event_type="cad_call_updated",
            call_id=call.id,
            data={
                "call": call.model_dump(),
                "changes": event_data,
            },
        )

        logger.info(
            "cad_call_updated",
            call_id=call.id,
            cad_id=call.cad_id,
            status=call.status.value,
        )

        return event

    async def _handle_call_closed(self, event_data: dict[str, Any]) -> CADEvent:
        """Handle a CAD call being closed."""
        cad_id = event_data.get("cad_id")
        call = self._get_call_by_cad_id(cad_id)

        if not call:
            logger.warning("call_not_found_for_close", cad_id=cad_id)
            return CADEvent(
                event_type="cad_call_closed",
                data={"cad_id": cad_id, "error": "Call not found"},
            )

        # Update call
        call.status = CallStatus.CLEARED
        call.cleared_at = datetime.now(UTC)
        call.disposition_code = event_data.get("disposition_code")
        call.disposition_text = event_data.get("disposition_text")
        call.updated_at = datetime.now(UTC)

        # Move to history
        self._call_history.append(call)

        # Free up assigned units
        for unit_id in call.assigned_units:
            unit = self._units.get(unit_id)
            if unit and unit.current_call_id == call.id:
                unit.status = UnitStatus.AVAILABLE
                unit.current_call_id = None
                unit.current_call_priority = None

        # Create event
        event = CADEvent(
            event_type="cad_call_closed",
            call_id=call.id,
            data=call.model_dump(),
        )

        logger.info(
            "cad_call_closed",
            call_id=call.id,
            cad_id=call.cad_id,
            disposition=call.disposition_code,
            audit_id=call.audit_id,
        )

        return event

    async def _handle_unit_status(self, event_data: dict[str, Any]) -> CADEvent:
        """Handle a unit status change."""
        unit_id = event_data.get("unit_id")

        # Get or create unit
        unit = self._units.get(unit_id)
        if not unit:
            unit = DispatchUnit(
                unit_id=unit_id,
                badge=event_data.get("badge"),
                officer_name=event_data.get("officer_name"),
                shift=event_data.get("shift"),
                beat=event_data.get("beat"),
                district=event_data.get("district"),
            )
            self._units[unit_id] = unit

        # Update status
        old_status = unit.status
        new_status = event_data.get("status")
        if new_status:
            unit.status = UnitStatus(new_status)

        # Update location
        if "latitude" in event_data and "longitude" in event_data:
            unit.latitude = event_data["latitude"]
            unit.longitude = event_data["longitude"]
            unit.last_location_update = datetime.now(UTC)

        # Update call assignment
        if "call_id" in event_data:
            call_id = event_data["call_id"]
            call = self._calls.get(call_id)
            if call:
                unit.current_call_id = call_id
                unit.current_call_priority = call.priority

        unit.updated_at = datetime.now(UTC)

        # Create event
        event = CADEvent(
            event_type="unit_status_changed",
            unit_id=unit_id,
            data={
                "unit": unit.model_dump(),
                "old_status": old_status.value if old_status else None,
                "new_status": unit.status.value,
            },
        )

        logger.info(
            "unit_status_changed",
            unit_id=unit_id,
            old_status=old_status.value if old_status else None,
            new_status=unit.status.value,
        )

        return event

    async def _link_call_to_intelligence(self, call: CADCall) -> None:
        """
        Auto-link a CAD call to intelligence data.

        Links to:
        - RMS history at the address
        - Tactical heatmaps and zones
        - Officer safety indicators
        - High-risk entity indicators
        """
        risk_indicators = []

        # Check for high-risk address (would query Neo4j in production)
        if call.latitude and call.longitude:
            # Simulate checking tactical zones
            if self.tactical:
                # Would call tactical engine to get zone info
                pass

            # Simulate checking officer safety
            if self.officer_safety:
                # Would call officer safety engine
                pass

        # Check call type for inherent risk
        high_risk_types = [
            CallType.SHOTS_FIRED,
            CallType.ROBBERY,
            CallType.ASSAULT,
            CallType.DOMESTIC,
            CallType.PURSUIT,
            CallType.OFFICER_NEEDS_ASSISTANCE,
        ]

        if call.call_type in high_risk_types:
            risk_indicators.append(f"high_risk_call_type:{call.call_type.value}")

        if call.priority == CallPriority.P1:
            risk_indicators.append("priority_1_call")

        call.risk_indicators = risk_indicators

        logger.debug(
            "call_linked_to_intelligence",
            call_id=call.id,
            risk_indicators=risk_indicators,
        )

    def _parse_call_type(self, call_type_code: str) -> CallType:
        """Parse CAD call type code to enum."""
        code_mapping = {
            "10-71": CallType.SHOTS_FIRED,
            "10-31": CallType.ROBBERY,
            "10-32": CallType.BURGLARY,
            "10-33": CallType.ASSAULT,
            "10-16": CallType.DOMESTIC,
            "10-38": CallType.TRAFFIC_STOP,
            "10-50": CallType.TRAFFIC_ACCIDENT,
            "10-37": CallType.SUSPICIOUS_PERSON,
            "10-36": CallType.SUSPICIOUS_VEHICLE,
            "10-10": CallType.WELFARE_CHECK,
            "10-14": CallType.ALARM,
            "10-15": CallType.DISTURBANCE,
            "10-52": CallType.MEDICAL,
            "10-70": CallType.FIRE,
            "10-80": CallType.PURSUIT,
            "10-99": CallType.OFFICER_NEEDS_ASSISTANCE,
        }

        return code_mapping.get(call_type_code, CallType.OTHER)

    def _parse_priority(self, priority_str: str) -> CallPriority:
        """Parse priority string to enum."""
        try:
            return CallPriority(priority_str.upper())
        except ValueError:
            return CallPriority.P3

    def _get_call_by_cad_id(self, cad_id: str) -> CADCall | None:
        """Get a call by its CAD system ID."""
        for call in self._calls.values():
            if call.cad_id == cad_id:
                return call
        return None

    async def get_active_calls(
        self,
        priority: CallPriority | None = None,
        call_type: CallType | None = None,
        district: str | None = None,
        beat: str | None = None,
    ) -> list[CADCall]:
        """
        Get active CAD calls with optional filters.

        Args:
            priority: Filter by priority
            call_type: Filter by call type
            district: Filter by district
            beat: Filter by beat

        Returns:
            List of active calls
        """
        calls = [
            c for c in self._calls.values()
            if c.status not in [CallStatus.CLEARED, CallStatus.CANCELLED]
        ]

        if priority:
            calls = [c for c in calls if c.priority == priority]
        if call_type:
            calls = [c for c in calls if c.call_type == call_type]
        if district:
            calls = [c for c in calls if c.district == district]
        if beat:
            calls = [c for c in calls if c.beat == beat]

        # Sort by priority and time
        priority_order = {
            CallPriority.P1: 0,
            CallPriority.P2: 1,
            CallPriority.P3: 2,
            CallPriority.P4: 3,
            CallPriority.P5: 4,
        }
        calls.sort(key=lambda c: (priority_order.get(c.priority, 5), c.received_at))

        return calls

    async def get_call(self, call_id: str) -> CADCall | None:
        """Get a specific call by ID."""
        return self._calls.get(call_id)

    async def get_call_by_cad_id(self, cad_id: str) -> CADCall | None:
        """Get a call by CAD system ID."""
        return self._get_call_by_cad_id(cad_id)

    async def get_unit(self, unit_id: str) -> DispatchUnit | None:
        """Get a specific unit by ID."""
        return self._units.get(unit_id)

    async def get_available_units(
        self,
        district: str | None = None,
        beat: str | None = None,
        shift: str | None = None,
    ) -> list[DispatchUnit]:
        """
        Get available units with optional filters.

        Args:
            district: Filter by district
            beat: Filter by beat
            shift: Filter by shift

        Returns:
            List of available units
        """
        units = [
            u for u in self._units.values()
            if u.status == UnitStatus.AVAILABLE
        ]

        if district:
            units = [u for u in units if u.district == district]
        if beat:
            units = [u for u in units if u.beat == beat]
        if shift:
            units = [u for u in units if u.shift == shift]

        return units

    async def get_all_units(self) -> list[DispatchUnit]:
        """Get all units."""
        return list(self._units.values())

    async def assign_unit_to_call(
        self,
        unit_id: str,
        call_id: str,
        is_primary: bool = False,
    ) -> tuple[DispatchUnit, CADCall]:
        """
        Assign a unit to a call.

        Args:
            unit_id: Unit ID to assign
            call_id: Call ID to assign to
            is_primary: Whether this is the primary unit

        Returns:
            Tuple of (updated unit, updated call)
        """
        unit = self._units.get(unit_id)
        call = self._calls.get(call_id)

        if not unit:
            raise ValueError(f"Unit {unit_id} not found")
        if not call:
            raise ValueError(f"Call {call_id} not found")

        # Update unit
        unit.status = UnitStatus.DISPATCHED
        unit.current_call_id = call_id
        unit.current_call_priority = call.priority
        unit.updated_at = datetime.now(UTC)

        # Update call
        if unit_id not in call.assigned_units:
            call.assigned_units.append(unit_id)
        if is_primary:
            call.primary_unit = unit_id
        if call.status == CallStatus.PENDING:
            call.status = CallStatus.DISPATCHED
            call.dispatched_at = datetime.now(UTC)
        call.updated_at = datetime.now(UTC)

        logger.info(
            "unit_assigned_to_call",
            unit_id=unit_id,
            call_id=call_id,
            is_primary=is_primary,
        )

        return unit, call

    async def get_call_statistics(self) -> dict[str, Any]:
        """Get dispatch statistics."""
        active_calls = [
            c for c in self._calls.values()
            if c.status not in [CallStatus.CLEARED, CallStatus.CANCELLED]
        ]

        # Count by priority
        by_priority = {}
        for priority in CallPriority:
            by_priority[priority.value] = len([
                c for c in active_calls if c.priority == priority
            ])

        # Count by status
        by_status = {}
        for status in CallStatus:
            by_status[status.value] = len([
                c for c in active_calls if c.status == status
            ])

        # Count by type
        by_type = {}
        for call_type in CallType:
            count = len([c for c in active_calls if c.call_type == call_type])
            if count > 0:
                by_type[call_type.value] = count

        # Unit statistics
        available_units = len([
            u for u in self._units.values()
            if u.status == UnitStatus.AVAILABLE
        ])
        busy_units = len([
            u for u in self._units.values()
            if u.status in [UnitStatus.DISPATCHED, UnitStatus.EN_ROUTE, UnitStatus.ON_SCENE]
        ])

        return {
            "active_calls": len(active_calls),
            "calls_by_priority": by_priority,
            "calls_by_status": by_status,
            "calls_by_type": by_type,
            "available_units": available_units,
            "busy_units": busy_units,
            "total_units": len(self._units),
            "calls_cleared_today": len([
                c for c in self._call_history
                if c.cleared_at and c.cleared_at.date() == datetime.now(UTC).date()
            ]),
        }


# Export classes
__all__ = [
    "DispatchOverlayEngine",
    "CADCall",
    "DispatchUnit",
    "CADEvent",
    "CallPriority",
    "CallStatus",
    "UnitStatus",
    "CallType",
]
