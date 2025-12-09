"""
G3TI RTCC-UIP IntelliSend Module
Mobile Intelligence Packet delivery system.
Delivers vehicle intel, person intel, location intel, bulletins, and command notes to mobile devices.
"""

import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class IntelPacketType(str, Enum):
    """Intelligence packet types."""
    VEHICLE = "vehicle"
    PERSON = "person"
    LOCATION = "location"
    OFFICER_SAFETY = "officer_safety"
    BULLETIN = "bulletin"
    COMMAND_NOTE = "command_note"
    BOLO = "bolo"
    WARRANT = "warrant"
    GUNFIRE = "gunfire"
    LPR_HIT = "lpr_hit"
    GENERAL = "general"


class IntelPriority(str, Enum):
    """Intelligence priority levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class DeliveryStatus(str, Enum):
    """Packet delivery status."""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    ACKNOWLEDGED = "acknowledged"
    FAILED = "failed"
    EXPIRED = "expired"


class EntityLink(BaseModel):
    """Link to a related entity."""
    entity_id: str
    entity_type: str
    entity_name: str | None = None
    relationship: str | None = None
    confidence: float | None = None


class CameraInfo(BaseModel):
    """Nearby camera information."""
    camera_id: str
    camera_name: str
    latitude: float
    longitude: float
    distance_meters: float
    has_live_feed: bool = False
    feed_url: str | None = None


class CADCallLink(BaseModel):
    """Link to a CAD call."""
    call_id: str
    call_number: str
    call_type: str
    location: str
    created_at: datetime


class SafetyNote(BaseModel):
    """Officer safety note."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    note_type: str
    content: str
    severity: str = "info"
    source: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class IntelPacket(BaseModel):
    """Intelligence packet for mobile delivery."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    packet_type: IntelPacketType
    priority: IntelPriority
    title: str
    summary: str
    details: dict[str, Any] = Field(default_factory=dict)
    images: list[str] = Field(default_factory=list)
    entity_links: list[EntityLink] = Field(default_factory=list)
    nearby_cameras: list[CameraInfo] = Field(default_factory=list)
    related_calls: list[CADCallLink] = Field(default_factory=list)
    safety_notes: list[SafetyNote] = Field(default_factory=list)
    location: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    source: str = "rtcc"
    source_id: str | None = None
    created_by: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime | None = None
    is_critical: bool = False

    class Config:
        use_enum_values = True


class PacketDelivery(BaseModel):
    """Packet delivery record."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    packet_id: str
    recipient_badge: str
    recipient_device_id: str | None = None
    status: DeliveryStatus = DeliveryStatus.PENDING
    sent_at: datetime | None = None
    delivered_at: datetime | None = None
    read_at: datetime | None = None
    acknowledged_at: datetime | None = None
    failed_reason: str | None = None

    class Config:
        use_enum_values = True


class IntelliSendManager:
    """
    IntelliSend Manager.
    Handles creation and delivery of intelligence packets to mobile devices.
    """

    def __init__(self) -> None:
        """Initialize the IntelliSend manager."""
        self._packets: dict[str, IntelPacket] = {}
        self._deliveries: dict[str, list[PacketDelivery]] = {}
        self._badge_packets: dict[str, list[str]] = {}

        # Configuration
        self._default_expiry_hours = 24
        self._critical_expiry_hours = 4

    async def create_vehicle_intel(
        self,
        plate: str,
        state: str | None = None,
        make: str | None = None,
        model: str | None = None,
        color: str | None = None,
        year: int | None = None,
        priority: IntelPriority = IntelPriority.MEDIUM,
        summary: str | None = None,
        images: list[str] | None = None,
        location: str | None = None,
        latitude: float | None = None,
        longitude: float | None = None,
        entity_links: list[EntityLink] | None = None,
        safety_notes: list[SafetyNote] | None = None,
        source: str = "rtcc",
        created_by: str | None = None,
    ) -> IntelPacket:
        """
        Create a vehicle intelligence packet.

        Args:
            plate: License plate
            state: State
            make: Vehicle make
            model: Vehicle model
            color: Vehicle color
            year: Vehicle year
            priority: Priority level
            summary: Summary text
            images: Image URLs
            location: Location description
            latitude: GPS latitude
            longitude: GPS longitude
            entity_links: Related entities
            safety_notes: Safety notes
            source: Intel source
            created_by: Creator badge

        Returns:
            Created packet
        """
        title = f"Vehicle Intel: {plate}"
        if not summary:
            parts = [p for p in [color, str(year) if year else None, make, model] if p]
            summary = f"{' '.join(parts)} - {plate}" if parts else f"Plate: {plate}"

        details = {
            "plate": plate,
            "state": state,
            "make": make,
            "model": model,
            "color": color,
            "year": year,
        }

        packet = IntelPacket(
            packet_type=IntelPacketType.VEHICLE,
            priority=priority,
            title=title,
            summary=summary,
            details=details,
            images=images or [],
            location=location,
            latitude=latitude,
            longitude=longitude,
            entity_links=entity_links or [],
            safety_notes=safety_notes or [],
            source=source,
            created_by=created_by,
            is_critical=priority == IntelPriority.CRITICAL,
        )

        self._packets[packet.id] = packet
        return packet

    async def create_person_intel(
        self,
        name: str,
        dob: str | None = None,
        ssn_last4: str | None = None,
        description: str | None = None,
        priority: IntelPriority = IntelPriority.MEDIUM,
        summary: str | None = None,
        images: list[str] | None = None,
        location: str | None = None,
        latitude: float | None = None,
        longitude: float | None = None,
        entity_links: list[EntityLink] | None = None,
        safety_notes: list[SafetyNote] | None = None,
        warrants: list[dict[str, Any]] | None = None,
        criminal_history: list[str] | None = None,
        source: str = "rtcc",
        created_by: str | None = None,
    ) -> IntelPacket:
        """
        Create a person intelligence packet.

        Args:
            name: Person name
            dob: Date of birth
            ssn_last4: Last 4 of SSN
            description: Physical description
            priority: Priority level
            summary: Summary text
            images: Image URLs
            location: Location description
            latitude: GPS latitude
            longitude: GPS longitude
            entity_links: Related entities
            safety_notes: Safety notes
            warrants: Active warrants
            criminal_history: Criminal history
            source: Intel source
            created_by: Creator badge

        Returns:
            Created packet
        """
        title = f"Person Intel: {name}"
        if not summary:
            summary = f"{name}"
            if dob:
                summary += f" (DOB: {dob})"

        details = {
            "name": name,
            "dob": dob,
            "ssn_last4": ssn_last4,
            "description": description,
            "warrants": warrants or [],
            "criminal_history": criminal_history or [],
        }

        packet = IntelPacket(
            packet_type=IntelPacketType.PERSON,
            priority=priority,
            title=title,
            summary=summary,
            details=details,
            images=images or [],
            location=location,
            latitude=latitude,
            longitude=longitude,
            entity_links=entity_links or [],
            safety_notes=safety_notes or [],
            source=source,
            created_by=created_by,
            is_critical=priority == IntelPriority.CRITICAL,
        )

        self._packets[packet.id] = packet
        return packet

    async def create_location_intel(
        self,
        address: str,
        location_type: str | None = None,
        priority: IntelPriority = IntelPriority.MEDIUM,
        summary: str | None = None,
        images: list[str] | None = None,
        latitude: float | None = None,
        longitude: float | None = None,
        entity_links: list[EntityLink] | None = None,
        safety_notes: list[SafetyNote] | None = None,
        premise_history: list[str] | None = None,
        hazards: list[str] | None = None,
        source: str = "rtcc",
        created_by: str | None = None,
    ) -> IntelPacket:
        """
        Create a location intelligence packet.

        Args:
            address: Location address
            location_type: Type of location
            priority: Priority level
            summary: Summary text
            images: Image URLs
            latitude: GPS latitude
            longitude: GPS longitude
            entity_links: Related entities
            safety_notes: Safety notes
            premise_history: Premise history
            hazards: Known hazards
            source: Intel source
            created_by: Creator badge

        Returns:
            Created packet
        """
        title = f"Location Intel: {address}"
        if not summary:
            summary = address
            if location_type:
                summary = f"{location_type}: {address}"

        details = {
            "address": address,
            "location_type": location_type,
            "premise_history": premise_history or [],
            "hazards": hazards or [],
        }

        packet = IntelPacket(
            packet_type=IntelPacketType.LOCATION,
            priority=priority,
            title=title,
            summary=summary,
            details=details,
            images=images or [],
            location=address,
            latitude=latitude,
            longitude=longitude,
            entity_links=entity_links or [],
            safety_notes=safety_notes or [],
            source=source,
            created_by=created_by,
            is_critical=priority == IntelPriority.CRITICAL,
        )

        self._packets[packet.id] = packet
        return packet

    async def create_officer_safety_packet(
        self,
        title: str,
        summary: str,
        threat_type: str,
        threat_level: str,
        location: str | None = None,
        latitude: float | None = None,
        longitude: float | None = None,
        images: list[str] | None = None,
        entity_links: list[EntityLink] | None = None,
        safety_notes: list[SafetyNote] | None = None,
        recommended_actions: list[str] | None = None,
        source: str = "rtcc",
        created_by: str | None = None,
    ) -> IntelPacket:
        """
        Create an officer safety critical packet.

        Args:
            title: Packet title
            summary: Summary text
            threat_type: Type of threat
            threat_level: Threat level
            location: Location description
            latitude: GPS latitude
            longitude: GPS longitude
            images: Image URLs
            entity_links: Related entities
            safety_notes: Safety notes
            recommended_actions: Recommended actions
            source: Intel source
            created_by: Creator badge

        Returns:
            Created packet
        """
        details = {
            "threat_type": threat_type,
            "threat_level": threat_level,
            "recommended_actions": recommended_actions or [],
        }

        packet = IntelPacket(
            packet_type=IntelPacketType.OFFICER_SAFETY,
            priority=IntelPriority.CRITICAL,
            title=title,
            summary=summary,
            details=details,
            images=images or [],
            location=location,
            latitude=latitude,
            longitude=longitude,
            entity_links=entity_links or [],
            safety_notes=safety_notes or [],
            source=source,
            created_by=created_by,
            is_critical=True,
            expires_at=datetime.utcnow() + timedelta(hours=self._critical_expiry_hours),
        )

        self._packets[packet.id] = packet
        return packet

    async def create_bulletin_packet(
        self,
        title: str,
        summary: str,
        bulletin_type: str,
        priority: IntelPriority = IntelPriority.MEDIUM,
        details: dict[str, Any] | None = None,
        images: list[str] | None = None,
        location: str | None = None,
        latitude: float | None = None,
        longitude: float | None = None,
        entity_links: list[EntityLink] | None = None,
        safety_notes: list[SafetyNote] | None = None,
        source: str = "rtcc",
        source_id: str | None = None,
        created_by: str | None = None,
    ) -> IntelPacket:
        """
        Create a bulletin packet (from Phase 7).

        Args:
            title: Bulletin title
            summary: Summary text
            bulletin_type: Type of bulletin
            priority: Priority level
            details: Additional details
            images: Image URLs
            location: Location description
            latitude: GPS latitude
            longitude: GPS longitude
            entity_links: Related entities
            safety_notes: Safety notes
            source: Intel source
            source_id: Source bulletin ID
            created_by: Creator badge

        Returns:
            Created packet
        """
        packet_details = details or {}
        packet_details["bulletin_type"] = bulletin_type

        packet = IntelPacket(
            packet_type=IntelPacketType.BULLETIN,
            priority=priority,
            title=title,
            summary=summary,
            details=packet_details,
            images=images or [],
            location=location,
            latitude=latitude,
            longitude=longitude,
            entity_links=entity_links or [],
            safety_notes=safety_notes or [],
            source=source,
            source_id=source_id,
            created_by=created_by,
            is_critical=priority == IntelPriority.CRITICAL,
        )

        self._packets[packet.id] = packet
        return packet

    async def create_command_note_packet(
        self,
        title: str,
        summary: str,
        incident_id: str,
        note_content: str,
        priority: IntelPriority = IntelPriority.MEDIUM,
        images: list[str] | None = None,
        location: str | None = None,
        latitude: float | None = None,
        longitude: float | None = None,
        source: str = "command",
        source_id: str | None = None,
        created_by: str | None = None,
    ) -> IntelPacket:
        """
        Create a command note packet (from Phase 8).

        Args:
            title: Note title
            summary: Summary text
            incident_id: Related incident ID
            note_content: Full note content
            priority: Priority level
            images: Image URLs
            location: Location description
            latitude: GPS latitude
            longitude: GPS longitude
            source: Intel source
            source_id: Source note ID
            created_by: Creator badge

        Returns:
            Created packet
        """
        details = {
            "incident_id": incident_id,
            "note_content": note_content,
        }

        packet = IntelPacket(
            packet_type=IntelPacketType.COMMAND_NOTE,
            priority=priority,
            title=title,
            summary=summary,
            details=details,
            images=images or [],
            location=location,
            latitude=latitude,
            longitude=longitude,
            source=source,
            source_id=source_id,
            created_by=created_by,
            is_critical=priority == IntelPriority.CRITICAL,
        )

        self._packets[packet.id] = packet
        return packet

    async def send_packet(
        self,
        packet_id: str,
        recipient_badges: list[str],
        device_ids: dict[str, str] | None = None,
    ) -> list[PacketDelivery]:
        """
        Send a packet to recipients.

        Args:
            packet_id: Packet ID
            recipient_badges: Recipient badge numbers
            device_ids: Mapping of badge to device ID

        Returns:
            List of delivery records
        """
        packet = self._packets.get(packet_id)
        if not packet:
            return []

        deliveries = []
        device_map = device_ids or {}

        for badge in recipient_badges:
            delivery = PacketDelivery(
                packet_id=packet_id,
                recipient_badge=badge,
                recipient_device_id=device_map.get(badge),
                status=DeliveryStatus.SENT,
                sent_at=datetime.utcnow(),
            )

            if packet_id not in self._deliveries:
                self._deliveries[packet_id] = []
            self._deliveries[packet_id].append(delivery)

            if badge not in self._badge_packets:
                self._badge_packets[badge] = []
            self._badge_packets[badge].append(packet_id)

            deliveries.append(delivery)

        return deliveries

    async def get_packet(self, packet_id: str) -> IntelPacket | None:
        """Get a packet by ID."""
        return self._packets.get(packet_id)

    async def get_packets_for_badge(
        self,
        badge_number: str,
        limit: int = 50,
        packet_type: IntelPacketType | None = None,
        unread_only: bool = False,
        since: datetime | None = None,
    ) -> list[IntelPacket]:
        """
        Get packets for a badge.

        Args:
            badge_number: Officer badge number
            limit: Maximum packets
            packet_type: Filter by type
            unread_only: Only unread packets
            since: Only packets after this time

        Returns:
            List of packets
        """
        packet_ids = self._badge_packets.get(badge_number, [])
        packets = []

        for packet_id in packet_ids:
            packet = self._packets.get(packet_id)
            if not packet:
                continue

            # Check expiration
            if packet.expires_at and datetime.utcnow() > packet.expires_at:
                continue

            # Filter by type
            if packet_type and packet.packet_type != packet_type:
                continue

            # Filter by time
            if since and packet.created_at < since:
                continue

            # Filter by read status
            if unread_only:
                deliveries = self._deliveries.get(packet_id, [])
                delivery = next((d for d in deliveries if d.recipient_badge == badge_number), None)
                if delivery and delivery.read_at:
                    continue

            packets.append(packet)

            if len(packets) >= limit:
                break

        return sorted(packets, key=lambda p: p.created_at, reverse=True)

    async def mark_delivered(
        self,
        packet_id: str,
        badge_number: str,
    ) -> PacketDelivery | None:
        """Mark a packet as delivered."""
        deliveries = self._deliveries.get(packet_id, [])
        for delivery in deliveries:
            if delivery.recipient_badge == badge_number:
                delivery.status = DeliveryStatus.DELIVERED
                delivery.delivered_at = datetime.utcnow()
                return delivery
        return None

    async def mark_read(
        self,
        packet_id: str,
        badge_number: str,
    ) -> PacketDelivery | None:
        """Mark a packet as read."""
        deliveries = self._deliveries.get(packet_id, [])
        for delivery in deliveries:
            if delivery.recipient_badge == badge_number:
                delivery.status = DeliveryStatus.READ
                delivery.read_at = datetime.utcnow()
                if not delivery.delivered_at:
                    delivery.delivered_at = datetime.utcnow()
                return delivery
        return None

    async def acknowledge_packet(
        self,
        packet_id: str,
        badge_number: str,
    ) -> PacketDelivery | None:
        """Acknowledge a packet."""
        deliveries = self._deliveries.get(packet_id, [])
        for delivery in deliveries:
            if delivery.recipient_badge == badge_number:
                delivery.status = DeliveryStatus.ACKNOWLEDGED
                delivery.acknowledged_at = datetime.utcnow()
                if not delivery.read_at:
                    delivery.read_at = datetime.utcnow()
                if not delivery.delivered_at:
                    delivery.delivered_at = datetime.utcnow()
                return delivery
        return None

    async def get_delivery_status(
        self,
        packet_id: str,
    ) -> list[PacketDelivery]:
        """Get delivery status for a packet."""
        return self._deliveries.get(packet_id, [])

    async def get_unread_count(self, badge_number: str) -> int:
        """Get count of unread packets for a badge."""
        packet_ids = self._badge_packets.get(badge_number, [])
        count = 0

        for packet_id in packet_ids:
            packet = self._packets.get(packet_id)
            if not packet:
                continue

            # Check expiration
            if packet.expires_at and datetime.utcnow() > packet.expires_at:
                continue

            deliveries = self._deliveries.get(packet_id, [])
            delivery = next((d for d in deliveries if d.recipient_badge == badge_number), None)
            if delivery and not delivery.read_at:
                count += 1

        return count

    async def add_nearby_cameras(
        self,
        packet_id: str,
        cameras: list[CameraInfo],
    ) -> IntelPacket | None:
        """Add nearby cameras to a packet."""
        packet = self._packets.get(packet_id)
        if packet:
            packet.nearby_cameras = cameras
        return packet

    async def add_related_calls(
        self,
        packet_id: str,
        calls: list[CADCallLink],
    ) -> IntelPacket | None:
        """Add related CAD calls to a packet."""
        packet = self._packets.get(packet_id)
        if packet:
            packet.related_calls = calls
        return packet

    async def add_safety_note(
        self,
        packet_id: str,
        note_type: str,
        content: str,
        severity: str = "info",
        source: str | None = None,
    ) -> IntelPacket | None:
        """Add a safety note to a packet."""
        packet = self._packets.get(packet_id)
        if packet:
            note = SafetyNote(
                note_type=note_type,
                content=content,
                severity=severity,
                source=source,
            )
            packet.safety_notes.append(note)
        return packet


# Global instance
intellisend = IntelliSendManager()
