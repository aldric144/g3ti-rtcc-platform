"""
G3TI RTCC-UIP Automated Bulletins Module.

Automatically generates and distributes RTCC-to-field bulletins:
- High-risk vehicles entering district
- Multi-incident suspect patterns
- Repeat violent locations
- Tactical zone changes (Phase 5 integration)
- Entities linked to recent investigations
- Officer safety intelligence packets

All bulletins are logged for CJIS compliance.
"""

import uuid
from datetime import UTC, datetime
from enum import Enum
from typing import Any

import structlog
from pydantic import BaseModel, Field

logger = structlog.get_logger(__name__)


class BulletinType(str, Enum):
    """Types of bulletins."""
    HIGH_RISK_VEHICLE = "high_risk_vehicle"
    SUSPECT_PATTERN = "suspect_pattern"
    REPEAT_LOCATION = "repeat_location"
    TACTICAL_ZONE = "tactical_zone"
    INVESTIGATION_LINK = "investigation_link"
    OFFICER_SAFETY = "officer_safety"
    BOLO = "bolo"
    INTELLIGENCE_SUMMARY = "intelligence_summary"
    SHIFT_BRIEFING = "shift_briefing"
    CRIME_TREND = "crime_trend"
    WARRANT_ALERT = "warrant_alert"
    CUSTOM = "custom"


class BulletinPriority(str, Enum):
    """Bulletin priority levels."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"


class BulletinStatus(str, Enum):
    """Bulletin status."""
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    PUBLISHED = "published"
    EXPIRED = "expired"
    ARCHIVED = "archived"


class LinkedEntity(BaseModel):
    """Schema for an entity linked to a bulletin."""
    entity_id: str
    entity_type: str  # person, vehicle, address, weapon, etc.
    name: str | None = None
    description: str | None = None
    risk_level: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class MapOverlay(BaseModel):
    """Schema for map overlay data."""
    type: str = "geojson"  # geojson, url, coordinates
    data: dict[str, Any] | str | None = None
    center: tuple[float, float] | None = None
    zoom: int = 14
    markers: list[dict[str, Any]] = Field(default_factory=list)
    polygons: list[dict[str, Any]] = Field(default_factory=list)


class Bulletin(BaseModel):
    """Schema for an RTCC bulletin."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    bulletin_type: BulletinType
    priority: BulletinPriority = BulletinPriority.NORMAL
    status: BulletinStatus = BulletinStatus.DRAFT

    # Content
    title: str
    summary: str
    body: str | None = None
    key_points: list[str] = Field(default_factory=list)

    # Linked data
    entities: list[LinkedEntity] = Field(default_factory=list)
    linked_incidents: list[str] = Field(default_factory=list)
    linked_cases: list[str] = Field(default_factory=list)
    linked_calls: list[str] = Field(default_factory=list)

    # Map data
    map_overlay: MapOverlay | None = None

    # Targeting
    target_shifts: list[str] = Field(default_factory=list)  # A, B, C
    target_districts: list[str] = Field(default_factory=list)
    target_units: list[str] = Field(default_factory=list)
    recommended_units: list[str] = Field(default_factory=list)
    broadcast_all: bool = False

    # Location context
    latitude: float | None = None
    longitude: float | None = None
    address: str | None = None
    area_name: str | None = None

    # Recommendations
    recommended_actions: list[str] = Field(default_factory=list)
    tactical_considerations: list[str] = Field(default_factory=list)

    # Attachments
    attachments: list[dict[str, Any]] = Field(default_factory=list)
    images: list[str] = Field(default_factory=list)

    # Metadata
    source: str = "rtcc"  # rtcc, ai_engine, tactical_engine, etc.
    auto_generated: bool = False
    created_by: str | None = None
    approved_by: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    published_at: datetime | None = None
    expires_at: datetime | None = None

    # Tracking
    view_count: int = 0
    acknowledged_by: list[str] = Field(default_factory=list)

    # CJIS compliance
    audit_id: str = Field(default_factory=lambda: str(uuid.uuid4()))


class BulletinTemplate(BaseModel):
    """Template for generating bulletins."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    bulletin_type: BulletinType
    priority: BulletinPriority = BulletinPriority.NORMAL
    title_template: str
    summary_template: str
    body_template: str | None = None
    key_points_template: list[str] = Field(default_factory=list)
    recommended_actions_template: list[str] = Field(default_factory=list)
    is_active: bool = True
    metadata: dict[str, Any] = Field(default_factory=dict)


class BulletinManager:
    """
    Central manager for RTCC bulletins.

    Handles bulletin creation, auto-generation, distribution, and tracking.
    """

    def __init__(
        self,
        redis_manager: Any | None = None,
        neo4j_manager: Any | None = None,
        tactical_manager: Any | None = None,
        alerts_manager: Any | None = None,
    ):
        """
        Initialize the bulletin manager.

        Args:
            redis_manager: Redis manager for caching and pub/sub
            neo4j_manager: Neo4j manager for entity queries
            tactical_manager: Phase 5 tactical engine
            alerts_manager: Alerts manager for push notifications
        """
        self.redis = redis_manager
        self.neo4j = neo4j_manager
        self.tactical = tactical_manager
        self.alerts = alerts_manager

        # In-memory stores
        self._bulletins: dict[str, Bulletin] = {}
        self._templates: dict[str, BulletinTemplate] = {}
        self._bulletin_history: list[Bulletin] = []

        # Initialize default templates
        self._initialize_templates()

        logger.info("bulletin_manager_initialized")

    def _initialize_templates(self) -> None:
        """Initialize default bulletin templates."""
        templates = [
            BulletinTemplate(
                id="high_risk_vehicle",
                name="High-Risk Vehicle Alert",
                bulletin_type=BulletinType.HIGH_RISK_VEHICLE,
                priority=BulletinPriority.HIGH,
                title_template="High-Risk Vehicle Alert: {plate}",
                summary_template="Vehicle {plate} ({make} {model} {color}) associated with {reason} has entered {area}.",
                body_template="A high-risk vehicle has been detected in your area. Exercise caution when approaching.",
                key_points_template=[
                    "Plate: {plate}",
                    "Vehicle: {year} {make} {model} {color}",
                    "Reason: {reason}",
                    "Last seen: {last_seen}",
                ],
                recommended_actions_template=[
                    "Do not approach alone",
                    "Request backup before contact",
                    "Verify plate and vehicle description",
                ],
            ),
            BulletinTemplate(
                id="suspect_pattern",
                name="Multi-Incident Suspect Pattern",
                bulletin_type=BulletinType.SUSPECT_PATTERN,
                priority=BulletinPriority.HIGH,
                title_template="Suspect Pattern Alert: {crime_type}",
                summary_template="Pattern identified: {incident_count} {crime_type} incidents linked to suspect matching {description}.",
                body_template="Intelligence analysis has identified a pattern of criminal activity that may be linked to a single suspect or group.",
                key_points_template=[
                    "Crime type: {crime_type}",
                    "Incident count: {incident_count}",
                    "Time pattern: {time_pattern}",
                    "Area: {area}",
                ],
                recommended_actions_template=[
                    "Increase patrol in identified areas",
                    "Review linked incidents for additional intelligence",
                    "Report any sightings to RTCC",
                ],
            ),
            BulletinTemplate(
                id="repeat_location",
                name="Repeat Violent Location",
                bulletin_type=BulletinType.REPEAT_LOCATION,
                priority=BulletinPriority.HIGH,
                title_template="Repeat Location Alert: {address}",
                summary_template="Location {address} has had {incident_count} violent incidents in the past {time_period}.",
                body_template="This location has been flagged as a repeat violent location. Exercise heightened awareness.",
                key_points_template=[
                    "Address: {address}",
                    "Incident count: {incident_count}",
                    "Incident types: {incident_types}",
                    "Last incident: {last_incident}",
                ],
                recommended_actions_template=[
                    "Approach with caution",
                    "Request backup for calls at this location",
                    "Review location history before responding",
                ],
            ),
            BulletinTemplate(
                id="tactical_zone",
                name="Tactical Zone Update",
                bulletin_type=BulletinType.TACTICAL_ZONE,
                priority=BulletinPriority.NORMAL,
                title_template="Tactical Zone Update: {zone_name}",
                summary_template="Zone {zone_name} risk level changed from {old_level} to {new_level}.",
                body_template="Tactical analysis has identified a change in risk level for this zone.",
                key_points_template=[
                    "Zone: {zone_name}",
                    "New risk level: {new_level}",
                    "Contributing factors: {factors}",
                ],
                recommended_actions_template=[
                    "Adjust patrol patterns accordingly",
                    "Review zone intelligence packet",
                ],
            ),
            BulletinTemplate(
                id="officer_safety",
                name="Officer Safety Intelligence",
                bulletin_type=BulletinType.OFFICER_SAFETY,
                priority=BulletinPriority.URGENT,
                title_template="Officer Safety Alert: {threat_type}",
                summary_template="Officer safety intelligence: {summary}",
                body_template="Critical officer safety information has been identified. Review immediately.",
                key_points_template=[
                    "Threat type: {threat_type}",
                    "Location: {location}",
                    "Details: {details}",
                ],
                recommended_actions_template=[
                    "Review threat indicators",
                    "Coordinate with RTCC",
                    "Follow officer safety protocols",
                ],
            ),
            BulletinTemplate(
                id="shift_briefing",
                name="Shift Briefing Summary",
                bulletin_type=BulletinType.SHIFT_BRIEFING,
                priority=BulletinPriority.NORMAL,
                title_template="Shift {shift} Briefing - {date}",
                summary_template="Intelligence summary for Shift {shift} on {date}.",
                body_template="Review the following intelligence items for your shift.",
                key_points_template=[
                    "Active BOLOs: {bolo_count}",
                    "Hot zones: {hot_zones}",
                    "Recent patterns: {patterns}",
                    "Officer safety notes: {safety_notes}",
                ],
                recommended_actions_template=[
                    "Review all active BOLOs",
                    "Check hot zone locations",
                    "Coordinate with RTCC for updates",
                ],
            ),
        ]

        for template in templates:
            self._templates[template.id] = template

        logger.info("bulletin_templates_initialized", count=len(templates))

    async def create_bulletin(
        self,
        bulletin_type: BulletinType,
        title: str,
        summary: str,
        body: str | None = None,
        priority: BulletinPriority = BulletinPriority.NORMAL,
        key_points: list[str] | None = None,
        entities: list[LinkedEntity] | None = None,
        linked_incidents: list[str] | None = None,
        linked_cases: list[str] | None = None,
        map_overlay: MapOverlay | None = None,
        target_shifts: list[str] | None = None,
        target_districts: list[str] | None = None,
        recommended_units: list[str] | None = None,
        broadcast_all: bool = False,
        latitude: float | None = None,
        longitude: float | None = None,
        address: str | None = None,
        recommended_actions: list[str] | None = None,
        tactical_considerations: list[str] | None = None,
        created_by: str | None = None,
        auto_generated: bool = False,
        metadata: dict[str, Any] | None = None,
        expires_at: datetime | None = None,
        auto_publish: bool = False,
    ) -> Bulletin:
        """
        Create a new bulletin.

        Args:
            bulletin_type: Type of bulletin
            title: Bulletin title
            summary: Brief summary
            body: Full body text
            priority: Bulletin priority
            key_points: Key points list
            entities: Linked entities
            linked_incidents: Linked incident IDs
            linked_cases: Linked case IDs
            map_overlay: Map overlay data
            target_shifts: Target shifts
            target_districts: Target districts
            recommended_units: Recommended units
            broadcast_all: Broadcast to all
            latitude: Location latitude
            longitude: Location longitude
            address: Location address
            recommended_actions: Recommended actions
            tactical_considerations: Tactical considerations
            created_by: Creator user ID
            auto_generated: Whether auto-generated
            metadata: Additional metadata
            expires_at: Expiration time
            auto_publish: Automatically publish

        Returns:
            The created bulletin
        """
        bulletin = Bulletin(
            bulletin_type=bulletin_type,
            priority=priority,
            title=title,
            summary=summary,
            body=body,
            key_points=key_points or [],
            entities=entities or [],
            linked_incidents=linked_incidents or [],
            linked_cases=linked_cases or [],
            map_overlay=map_overlay,
            target_shifts=target_shifts or [],
            target_districts=target_districts or [],
            recommended_units=recommended_units or [],
            broadcast_all=broadcast_all,
            latitude=latitude,
            longitude=longitude,
            address=address,
            recommended_actions=recommended_actions or [],
            tactical_considerations=tactical_considerations or [],
            created_by=created_by,
            auto_generated=auto_generated,
            metadata=metadata or {},
            expires_at=expires_at,
        )

        # Store bulletin
        self._bulletins[bulletin.id] = bulletin

        # Auto-publish if requested
        if auto_publish:
            await self.publish_bulletin(bulletin.id, created_by)

        # Log for CJIS compliance
        logger.info(
            "bulletin_created",
            bulletin_id=bulletin.id,
            bulletin_type=bulletin_type.value,
            priority=priority.value,
            auto_generated=auto_generated,
            audit_id=bulletin.audit_id,
        )

        return bulletin

    async def create_bulletin_from_template(
        self,
        template_id: str,
        variables: dict[str, Any],
        entities: list[LinkedEntity] | None = None,
        map_overlay: MapOverlay | None = None,
        target_shifts: list[str] | None = None,
        target_districts: list[str] | None = None,
        recommended_units: list[str] | None = None,
        created_by: str | None = None,
        auto_publish: bool = False,
        metadata: dict[str, Any] | None = None,
    ) -> Bulletin:
        """
        Create a bulletin from a template.

        Args:
            template_id: Template ID to use
            variables: Variables to substitute
            entities: Linked entities
            map_overlay: Map overlay data
            target_shifts: Target shifts
            target_districts: Target districts
            recommended_units: Recommended units
            created_by: Creator user ID
            auto_publish: Automatically publish
            metadata: Additional metadata

        Returns:
            The created bulletin
        """
        template = self._templates.get(template_id)
        if not template:
            raise ValueError(f"Template {template_id} not found")

        # Substitute variables
        def substitute(text: str) -> str:
            try:
                return text.format(**variables)
            except KeyError:
                return text

        title = substitute(template.title_template)
        summary = substitute(template.summary_template)
        body = substitute(template.body_template) if template.body_template else None
        key_points = [substitute(kp) for kp in template.key_points_template]
        recommended_actions = [substitute(ra) for ra in template.recommended_actions_template]

        return await self.create_bulletin(
            bulletin_type=template.bulletin_type,
            title=title,
            summary=summary,
            body=body,
            priority=template.priority,
            key_points=key_points,
            entities=entities,
            map_overlay=map_overlay,
            target_shifts=target_shifts,
            target_districts=target_districts,
            recommended_units=recommended_units,
            recommended_actions=recommended_actions,
            created_by=created_by,
            auto_generated=True,
            auto_publish=auto_publish,
            metadata=metadata,
        )

    async def publish_bulletin(
        self,
        bulletin_id: str,
        approved_by: str | None = None,
    ) -> Bulletin:
        """
        Publish a bulletin.

        Args:
            bulletin_id: Bulletin ID
            approved_by: User who approved

        Returns:
            Updated bulletin
        """
        bulletin = self._bulletins.get(bulletin_id)
        if not bulletin:
            raise ValueError(f"Bulletin {bulletin_id} not found")

        bulletin.status = BulletinStatus.PUBLISHED
        bulletin.published_at = datetime.now(UTC)
        bulletin.approved_by = approved_by

        # Send push alert if high priority
        if bulletin.priority in [BulletinPriority.HIGH, BulletinPriority.URGENT, BulletinPriority.CRITICAL]:
            if self.alerts:
                from .alerts import AlertPriority, AlertType
                await self.alerts.create_alert(
                    alert_type=AlertType.BULLETIN,
                    title=f"New Bulletin: {bulletin.title}",
                    body=bulletin.summary,
                    priority=AlertPriority(bulletin.priority.value),
                    target_shifts=bulletin.target_shifts,
                    target_districts=bulletin.target_districts,
                    broadcast_all=bulletin.broadcast_all,
                    latitude=bulletin.latitude,
                    longitude=bulletin.longitude,
                    metadata={"bulletin_id": bulletin.id},
                )

        logger.info(
            "bulletin_published",
            bulletin_id=bulletin_id,
            approved_by=approved_by,
            audit_id=bulletin.audit_id,
        )

        return bulletin

    async def get_bulletin(self, bulletin_id: str) -> Bulletin | None:
        """Get a bulletin by ID."""
        return self._bulletins.get(bulletin_id)

    async def get_bulletin_feed(
        self,
        bulletin_type: BulletinType | None = None,
        priority: BulletinPriority | None = None,
        shift: str | None = None,
        district: str | None = None,
        include_expired: bool = False,
        limit: int = 50,
    ) -> list[Bulletin]:
        """
        Get bulletin feed with filters.

        Args:
            bulletin_type: Filter by type
            priority: Filter by priority
            shift: Filter by target shift
            district: Filter by target district
            include_expired: Include expired bulletins
            limit: Maximum bulletins

        Returns:
            List of bulletins
        """
        now = datetime.now(UTC)
        bulletins = [
            b for b in self._bulletins.values()
            if b.status == BulletinStatus.PUBLISHED
        ]

        # Filter expired
        if not include_expired:
            bulletins = [
                b for b in bulletins
                if not b.expires_at or b.expires_at > now
            ]

        # Apply filters
        if bulletin_type:
            bulletins = [b for b in bulletins if b.bulletin_type == bulletin_type]
        if priority:
            bulletins = [b for b in bulletins if b.priority == priority]
        if shift:
            bulletins = [
                b for b in bulletins
                if b.broadcast_all or shift in b.target_shifts
            ]
        if district:
            bulletins = [
                b for b in bulletins
                if b.broadcast_all or district in b.target_districts
            ]

        # Sort by priority and time
        priority_order = {
            BulletinPriority.CRITICAL: 0,
            BulletinPriority.URGENT: 1,
            BulletinPriority.HIGH: 2,
            BulletinPriority.NORMAL: 3,
            BulletinPriority.LOW: 4,
        }
        bulletins.sort(
            key=lambda b: (priority_order.get(b.priority, 5), b.published_at or b.created_at),
            reverse=True,
        )

        return bulletins[:limit]

    async def acknowledge_bulletin(
        self,
        bulletin_id: str,
        badge: str,
    ) -> Bulletin:
        """
        Acknowledge a bulletin.

        Args:
            bulletin_id: Bulletin ID
            badge: Officer badge

        Returns:
            Updated bulletin
        """
        bulletin = self._bulletins.get(bulletin_id)
        if not bulletin:
            raise ValueError(f"Bulletin {bulletin_id} not found")

        if badge not in bulletin.acknowledged_by:
            bulletin.acknowledged_by.append(badge)

        logger.info(
            "bulletin_acknowledged",
            bulletin_id=bulletin_id,
            badge=badge,
        )

        return bulletin

    async def increment_view_count(self, bulletin_id: str) -> Bulletin:
        """Increment bulletin view count."""
        bulletin = self._bulletins.get(bulletin_id)
        if bulletin:
            bulletin.view_count += 1
        return bulletin

    async def archive_bulletin(self, bulletin_id: str) -> Bulletin:
        """Archive a bulletin."""
        bulletin = self._bulletins.get(bulletin_id)
        if not bulletin:
            raise ValueError(f"Bulletin {bulletin_id} not found")

        bulletin.status = BulletinStatus.ARCHIVED
        self._bulletin_history.append(bulletin)

        logger.info("bulletin_archived", bulletin_id=bulletin_id)

        return bulletin

    # Auto-generation methods

    async def generate_high_risk_vehicle_bulletin(
        self,
        plate: str,
        make: str,
        model: str,
        color: str,
        year: str | None,
        reason: str,
        area: str,
        last_seen: str,
        latitude: float | None = None,
        longitude: float | None = None,
        target_districts: list[str] | None = None,
    ) -> Bulletin:
        """Generate a high-risk vehicle bulletin."""
        variables = {
            "plate": plate,
            "make": make,
            "model": model,
            "color": color,
            "year": year or "Unknown",
            "reason": reason,
            "area": area,
            "last_seen": last_seen,
        }

        entity = LinkedEntity(
            entity_id=plate,
            entity_type="vehicle",
            name=f"{color} {make} {model}",
            description=f"Plate: {plate}, Reason: {reason}",
            risk_level="high",
        )

        return await self.create_bulletin_from_template(
            template_id="high_risk_vehicle",
            variables=variables,
            entities=[entity],
            target_districts=target_districts,
            auto_publish=True,
            metadata={"plate": plate, "reason": reason},
        )

    async def generate_suspect_pattern_bulletin(
        self,
        crime_type: str,
        incident_count: int,
        description: str,
        time_pattern: str,
        area: str,
        linked_incidents: list[str],
        latitude: float | None = None,
        longitude: float | None = None,
    ) -> Bulletin:
        """Generate a suspect pattern bulletin."""
        variables = {
            "crime_type": crime_type,
            "incident_count": incident_count,
            "description": description,
            "time_pattern": time_pattern,
            "area": area,
        }

        return await self.create_bulletin_from_template(
            template_id="suspect_pattern",
            variables=variables,
            auto_publish=True,
            metadata={
                "crime_type": crime_type,
                "incident_count": incident_count,
                "linked_incidents": linked_incidents,
            },
        )

    async def generate_repeat_location_bulletin(
        self,
        address: str,
        incident_count: int,
        incident_types: list[str],
        time_period: str,
        last_incident: str,
        latitude: float | None = None,
        longitude: float | None = None,
    ) -> Bulletin:
        """Generate a repeat location bulletin."""
        variables = {
            "address": address,
            "incident_count": incident_count,
            "incident_types": ", ".join(incident_types),
            "time_period": time_period,
            "last_incident": last_incident,
        }

        entity = LinkedEntity(
            entity_id=address,
            entity_type="address",
            name=address,
            description=f"{incident_count} incidents in {time_period}",
            risk_level="high",
        )

        map_overlay = None
        if latitude and longitude:
            map_overlay = MapOverlay(
                center=(latitude, longitude),
                markers=[{
                    "lat": latitude,
                    "lng": longitude,
                    "label": address,
                    "color": "red",
                }],
            )

        return await self.create_bulletin_from_template(
            template_id="repeat_location",
            variables=variables,
            entities=[entity],
            map_overlay=map_overlay,
            auto_publish=True,
            metadata={"address": address, "incident_count": incident_count},
        )

    async def generate_shift_briefing(
        self,
        shift: str,
        date: str,
        bolo_count: int,
        hot_zones: list[str],
        patterns: list[str],
        safety_notes: list[str],
    ) -> Bulletin:
        """Generate a shift briefing bulletin."""
        variables = {
            "shift": shift,
            "date": date,
            "bolo_count": bolo_count,
            "hot_zones": ", ".join(hot_zones) if hot_zones else "None",
            "patterns": ", ".join(patterns) if patterns else "None",
            "safety_notes": ", ".join(safety_notes) if safety_notes else "None",
        }

        return await self.create_bulletin_from_template(
            template_id="shift_briefing",
            variables=variables,
            target_shifts=[shift],
            auto_publish=True,
            metadata={"shift": shift, "date": date},
        )

    def get_template(self, template_id: str) -> BulletinTemplate | None:
        """Get a bulletin template."""
        return self._templates.get(template_id)

    def get_all_templates(self) -> list[BulletinTemplate]:
        """Get all bulletin templates."""
        return list(self._templates.values())


# Export classes
__all__ = [
    "BulletinManager",
    "Bulletin",
    "BulletinTemplate",
    "BulletinType",
    "BulletinPriority",
    "BulletinStatus",
    "LinkedEntity",
    "MapOverlay",
]
