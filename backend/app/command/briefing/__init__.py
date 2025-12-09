"""
Command Notes & Briefing Generator for G3TI RTCC-UIP.

Provides command note management, attachment handling, and
auto-generation of command briefings with export capabilities.
"""

import uuid
from datetime import UTC, datetime
from enum import Enum
from typing import Any

import structlog
from pydantic import BaseModel, Field

logger = structlog.get_logger(__name__)


class NoteType(str, Enum):
    """Types of command notes."""

    GENERAL = "general"
    TACTICAL = "tactical"
    INTELLIGENCE = "intelligence"
    SAFETY = "safety"
    LOGISTICS = "logistics"
    COMMUNICATIONS = "communications"
    MEDIA = "media"
    LEGAL = "legal"
    DECISION = "decision"
    ACTION_ITEM = "action_item"


class NotePriority(str, Enum):
    """Priority of command notes."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class AttachmentType(str, Enum):
    """Types of attachments."""

    IMAGE = "image"
    PDF = "pdf"
    DOCUMENT = "document"
    MAP = "map"
    VIDEO = "video"
    AUDIO = "audio"
    OTHER = "other"


class BriefingSection(str, Enum):
    """Sections of a command briefing."""

    EXECUTIVE_SUMMARY = "executive_summary"
    INCIDENT_OVERVIEW = "incident_overview"
    TIMELINE = "timeline"
    ICS_STRUCTURE = "ics_structure"
    RESOURCES = "resources"
    STRATEGY_MAP = "strategy_map"
    INTELLIGENCE = "intelligence"
    OFFICER_SAFETY = "officer_safety"
    COMMUNICATIONS = "communications"
    ACTION_ITEMS = "action_items"
    APPENDIX = "appendix"


class ExportFormat(str, Enum):
    """Export formats for briefings."""

    PDF = "pdf"
    DOCX = "docx"
    JSON = "json"
    HTML = "html"
    MARKDOWN = "markdown"


class Attachment(BaseModel):
    """Attachment model."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    attachment_type: AttachmentType
    filename: str
    url: str
    mime_type: str | None = None
    size_bytes: int | None = None
    description: str | None = None
    uploaded_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    uploaded_by: str | None = None

    class Config:
        """Pydantic config."""

        use_enum_values = True


class CommandNote(BaseModel):
    """Command note model."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    incident_id: str
    note_type: NoteType = NoteType.GENERAL
    priority: NotePriority = NotePriority.MEDIUM
    title: str | None = None
    content: str
    attachments: list[Attachment] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    created_by: str | None = None
    created_by_name: str | None = None
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    is_pinned: bool = False
    is_redacted: bool = False
    related_timeline_event_id: str | None = None
    audit_id: str = Field(default_factory=lambda: f"AUDIT-CN-{uuid.uuid4().hex[:12].upper()}")

    class Config:
        """Pydantic config."""

        use_enum_values = True


class BriefingSectionContent(BaseModel):
    """Content for a briefing section."""

    section: BriefingSection
    title: str
    content: str
    data: dict[str, Any] = Field(default_factory=dict)
    attachments: list[Attachment] = Field(default_factory=list)

    class Config:
        """Pydantic config."""

        use_enum_values = True


class CommandBriefing(BaseModel):
    """Command briefing model."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    incident_id: str
    title: str
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    generated_by: str | None = None
    sections: list[BriefingSectionContent] = Field(default_factory=list)
    version: int = 1
    is_final: bool = False
    approved_by: str | None = None
    approved_at: datetime | None = None
    export_urls: dict[str, str] = Field(default_factory=dict)
    audit_id: str = Field(default_factory=lambda: f"AUDIT-CB-{uuid.uuid4().hex[:12].upper()}")


class BriefingGenerator:
    """
    Generator for command briefings.

    Provides note management, attachment handling, and
    auto-generation of comprehensive command briefings.
    """

    def __init__(self) -> None:
        """Initialize the briefing generator."""
        self._notes: dict[str, list[CommandNote]] = {}  # incident_id -> notes
        self._briefings: dict[str, list[CommandBriefing]] = {}  # incident_id -> briefings

        logger.info("briefing_generator_initialized")

    async def add_note(
        self,
        incident_id: str,
        content: str,
        note_type: NoteType = NoteType.GENERAL,
        priority: NotePriority = NotePriority.MEDIUM,
        title: str | None = None,
        tags: list[str] | None = None,
        created_by: str | None = None,
        created_by_name: str | None = None,
        attachments: list[Attachment] | None = None,
    ) -> CommandNote:
        """
        Add a command note.

        Args:
            incident_id: ID of the incident
            content: Note content
            note_type: Type of note
            priority: Note priority
            title: Note title
            tags: Note tags
            created_by: User creating note
            created_by_name: Name of user
            attachments: List of attachments

        Returns:
            Created CommandNote
        """
        note = CommandNote(
            incident_id=incident_id,
            note_type=note_type,
            priority=priority,
            title=title,
            content=content,
            tags=tags or [],
            created_by=created_by,
            created_by_name=created_by_name,
            attachments=attachments or [],
        )

        if incident_id not in self._notes:
            self._notes[incident_id] = []
        self._notes[incident_id].append(note)

        logger.info(
            "command_note_added",
            incident_id=incident_id,
            note_id=note.id,
            note_type=note_type,
            created_by=created_by,
            audit_id=note.audit_id,
        )

        return note

    async def update_note(
        self,
        incident_id: str,
        note_id: str,
        content: str | None = None,
        title: str | None = None,
        priority: NotePriority | None = None,
        tags: list[str] | None = None,
        updated_by: str | None = None,
    ) -> CommandNote | None:
        """
        Update a command note.

        Args:
            incident_id: ID of the incident
            note_id: ID of note to update
            content: New content
            title: New title
            priority: New priority
            tags: New tags
            updated_by: User updating note

        Returns:
            Updated CommandNote or None
        """
        notes = self._notes.get(incident_id, [])
        note = next((n for n in notes if n.id == note_id), None)

        if not note:
            return None

        if content is not None:
            note.content = content
        if title is not None:
            note.title = title
        if priority is not None:
            note.priority = priority
        if tags is not None:
            note.tags = tags

        note.updated_at = datetime.now(UTC)

        logger.info(
            "command_note_updated",
            incident_id=incident_id,
            note_id=note_id,
            updated_by=updated_by,
        )

        return note

    async def add_attachment_to_note(
        self,
        incident_id: str,
        note_id: str,
        attachment: Attachment,
    ) -> CommandNote | None:
        """
        Add an attachment to a note.

        Args:
            incident_id: ID of the incident
            note_id: ID of note
            attachment: Attachment to add

        Returns:
            Updated CommandNote or None
        """
        notes = self._notes.get(incident_id, [])
        note = next((n for n in notes if n.id == note_id), None)

        if not note:
            return None

        note.attachments.append(attachment)
        note.updated_at = datetime.now(UTC)

        logger.info(
            "attachment_added_to_note",
            incident_id=incident_id,
            note_id=note_id,
            attachment_id=attachment.id,
        )

        return note

    async def pin_note(
        self,
        incident_id: str,
        note_id: str,
    ) -> CommandNote | None:
        """Pin a note."""
        notes = self._notes.get(incident_id, [])
        note = next((n for n in notes if n.id == note_id), None)

        if note:
            note.is_pinned = True
            note.updated_at = datetime.now(UTC)

        return note

    async def unpin_note(
        self,
        incident_id: str,
        note_id: str,
    ) -> CommandNote | None:
        """Unpin a note."""
        notes = self._notes.get(incident_id, [])
        note = next((n for n in notes if n.id == note_id), None)

        if note:
            note.is_pinned = False
            note.updated_at = datetime.now(UTC)

        return note

    async def delete_note(
        self,
        incident_id: str,
        note_id: str,
        deleted_by: str | None = None,
    ) -> bool:
        """
        Delete a note (soft delete via redaction).

        Args:
            incident_id: ID of the incident
            note_id: ID of note to delete
            deleted_by: User deleting note

        Returns:
            True if deleted
        """
        notes = self._notes.get(incident_id, [])
        note = next((n for n in notes if n.id == note_id), None)

        if not note:
            return False

        note.is_redacted = True
        note.updated_at = datetime.now(UTC)

        logger.info(
            "command_note_redacted",
            incident_id=incident_id,
            note_id=note_id,
            deleted_by=deleted_by,
        )

        return True

    async def get_notes(
        self,
        incident_id: str,
        note_type: NoteType | None = None,
        priority: NotePriority | None = None,
        pinned_only: bool = False,
        include_redacted: bool = False,
        limit: int = 100,
    ) -> list[CommandNote]:
        """
        Get notes for an incident.

        Args:
            incident_id: ID of the incident
            note_type: Filter by type
            priority: Filter by priority
            pinned_only: Only return pinned notes
            include_redacted: Include redacted notes
            limit: Maximum number to return

        Returns:
            List of CommandNote
        """
        notes = self._notes.get(incident_id, [])

        if not include_redacted:
            notes = [n for n in notes if not n.is_redacted]

        if note_type:
            type_value = note_type.value if isinstance(note_type, NoteType) else note_type
            notes = [n for n in notes if n.note_type == type_value]

        if priority:
            priority_value = priority.value if isinstance(priority, NotePriority) else priority
            notes = [n for n in notes if n.priority == priority_value]

        if pinned_only:
            notes = [n for n in notes if n.is_pinned]

        # Sort by created_at descending
        notes.sort(key=lambda x: x.created_at, reverse=True)

        return notes[:limit]

    async def get_note(
        self,
        incident_id: str,
        note_id: str,
    ) -> CommandNote | None:
        """Get a specific note."""
        notes = self._notes.get(incident_id, [])
        return next((n for n in notes if n.id == note_id), None)

    async def generate_briefing(
        self,
        incident_id: str,
        incident_data: dict[str, Any],
        ics_data: dict[str, Any] | None = None,
        timeline_data: list[dict[str, Any]] | None = None,
        resources_data: list[dict[str, Any]] | None = None,
        strategy_map_data: dict[str, Any] | None = None,
        intelligence_data: dict[str, Any] | None = None,
        safety_data: dict[str, Any] | None = None,
        generated_by: str | None = None,
    ) -> CommandBriefing:
        """
        Generate a command briefing.

        Args:
            incident_id: ID of the incident
            incident_data: Incident information
            ics_data: ICS structure data
            timeline_data: Timeline events
            resources_data: Resource assignments
            strategy_map_data: Strategy map data
            intelligence_data: Intelligence summary
            safety_data: Officer safety data
            generated_by: User generating briefing

        Returns:
            Generated CommandBriefing
        """
        sections = []

        # Executive Summary
        sections.append(self._generate_executive_summary(incident_data))

        # Incident Overview
        sections.append(self._generate_incident_overview(incident_data))

        # Timeline
        if timeline_data:
            sections.append(self._generate_timeline_section(timeline_data))

        # ICS Structure
        if ics_data:
            sections.append(self._generate_ics_section(ics_data))

        # Resources
        if resources_data:
            sections.append(self._generate_resources_section(resources_data))

        # Strategy Map
        if strategy_map_data:
            sections.append(self._generate_strategy_map_section(strategy_map_data))

        # Intelligence
        if intelligence_data:
            sections.append(self._generate_intelligence_section(intelligence_data))

        # Officer Safety
        if safety_data:
            sections.append(self._generate_safety_section(safety_data))

        # Action Items (from notes)
        notes = await self.get_notes(
            incident_id=incident_id,
            note_type=NoteType.ACTION_ITEM,
        )
        if notes:
            sections.append(self._generate_action_items_section(notes))

        # Determine version
        existing_briefings = self._briefings.get(incident_id, [])
        version = len(existing_briefings) + 1

        briefing = CommandBriefing(
            incident_id=incident_id,
            title=f"Command Briefing - {incident_data.get('title', 'Incident')}",
            generated_by=generated_by,
            sections=sections,
            version=version,
        )

        if incident_id not in self._briefings:
            self._briefings[incident_id] = []
        self._briefings[incident_id].append(briefing)

        logger.info(
            "command_briefing_generated",
            incident_id=incident_id,
            briefing_id=briefing.id,
            version=version,
            generated_by=generated_by,
            audit_id=briefing.audit_id,
        )

        return briefing

    def _generate_executive_summary(
        self,
        incident_data: dict[str, Any],
    ) -> BriefingSectionContent:
        """Generate executive summary section."""
        incident_type = incident_data.get("incident_type", "Unknown")
        status = incident_data.get("status", "Unknown")
        location = incident_data.get("location", {})
        address = location.get("address", "Unknown location") if location else "Unknown location"

        content = f"""
## Executive Summary

**Incident Type:** {incident_type.replace('_', ' ').title()}
**Status:** {status.replace('_', ' ').title()}
**Location:** {address}

**Incident Number:** {incident_data.get('incident_number', 'N/A')}
**Start Time:** {incident_data.get('start_time', 'N/A')}
**Commander:** {incident_data.get('assigned_commander', 'Not assigned')}
**RTCC Analyst:** {incident_data.get('assigned_rtcc_analyst', 'Not assigned')}

**Units Assigned:** {len(incident_data.get('assigned_units', []))}
**Agencies Involved:** {', '.join(incident_data.get('agencies_involved', ['Primary agency']))}
        """.strip()

        return BriefingSectionContent(
            section=BriefingSection.EXECUTIVE_SUMMARY,
            title="Executive Summary",
            content=content,
            data=incident_data,
        )

    def _generate_incident_overview(
        self,
        incident_data: dict[str, Any],
    ) -> BriefingSectionContent:
        """Generate incident overview section."""
        description = incident_data.get("description", "No description provided.")
        notes = incident_data.get("notes", [])

        content = f"""
## Incident Overview

{description}

### Key Notes
"""
        for note in notes[-5:]:  # Last 5 notes
            content += f"- {note}\n"

        return BriefingSectionContent(
            section=BriefingSection.INCIDENT_OVERVIEW,
            title="Incident Overview",
            content=content,
            data={"description": description, "notes": notes},
        )

    def _generate_timeline_section(
        self,
        timeline_data: list[dict[str, Any]],
    ) -> BriefingSectionContent:
        """Generate timeline section."""
        content = """
## Timeline of Events

| Time | Event | Priority | Source |
|------|-------|----------|--------|
"""
        for event in timeline_data[:20]:  # Last 20 events
            timestamp = event.get("timestamp", "")
            if isinstance(timestamp, datetime):
                timestamp = timestamp.strftime("%H:%M:%S")
            title = event.get("title", "")
            priority = event.get("priority", "medium")
            source = event.get("source", "")
            content += f"| {timestamp} | {title} | {priority} | {source} |\n"

        return BriefingSectionContent(
            section=BriefingSection.TIMELINE,
            title="Timeline of Events",
            content=content,
            data={"events": timeline_data},
        )

    def _generate_ics_section(
        self,
        ics_data: dict[str, Any],
    ) -> BriefingSectionContent:
        """Generate ICS structure section."""
        assignments = ics_data.get("assignments", [])

        content = """
## ICS Structure

### Command Staff
"""
        command_roles = ["incident_commander", "deputy_commander", "safety_officer", "public_info_officer", "liaison_officer"]
        for assignment in assignments:
            if assignment.get("role") in command_roles:
                role = assignment.get("role", "").replace("_", " ").title()
                name = assignment.get("name") or assignment.get("badge", "Unassigned")
                content += f"- **{role}:** {name}\n"

        content += "\n### Section Chiefs\n"
        section_roles = ["operations_chief", "planning_chief", "logistics_chief", "finance_chief", "intelligence_officer"]
        for assignment in assignments:
            if assignment.get("role") in section_roles:
                role = assignment.get("role", "").replace("_", " ").title()
                name = assignment.get("name") or assignment.get("badge", "Unassigned")
                content += f"- **{role}:** {name}\n"

        return BriefingSectionContent(
            section=BriefingSection.ICS_STRUCTURE,
            title="ICS Structure",
            content=content,
            data=ics_data,
        )

    def _generate_resources_section(
        self,
        resources_data: list[dict[str, Any]],
    ) -> BriefingSectionContent:
        """Generate resources section."""
        content = """
## Resources Assigned

| Resource | Type | Status | Role |
|----------|------|--------|------|
"""
        for resource in resources_data:
            name = resource.get("resource_name", "")
            rtype = resource.get("resource_type", "").replace("_", " ").title()
            status = "Active" if resource.get("is_active") else "Released"
            role = resource.get("role", "N/A")
            content += f"| {name} | {rtype} | {status} | {role} |\n"

        content += f"\n**Total Resources:** {len(resources_data)}"

        return BriefingSectionContent(
            section=BriefingSection.RESOURCES,
            title="Resources Assigned",
            content=content,
            data={"resources": resources_data},
        )

    def _generate_strategy_map_section(
        self,
        strategy_map_data: dict[str, Any],
    ) -> BriefingSectionContent:
        """Generate strategy map section."""
        unit_count = len(strategy_map_data.get("unit_positions", []))
        camera_count = len(strategy_map_data.get("cameras", []))
        gunfire_count = len(strategy_map_data.get("gunfire_detections", []))
        threat_zones = len(strategy_map_data.get("threat_zones", []))

        content = f"""
## Strategy Map Overview

**Units on Map:** {unit_count}
**Cameras:** {camera_count}
**Gunfire Detections:** {gunfire_count}
**Active Threat Zones:** {threat_zones}

### Layers
"""
        for layer in strategy_map_data.get("layers", []):
            name = layer.get("name", "")
            visible = "Visible" if layer.get("is_visible") else "Hidden"
            content += f"- {name}: {visible}\n"

        return BriefingSectionContent(
            section=BriefingSection.STRATEGY_MAP,
            title="Strategy Map Overview",
            content=content,
            data=strategy_map_data,
        )

    def _generate_intelligence_section(
        self,
        intelligence_data: dict[str, Any],
    ) -> BriefingSectionContent:
        """Generate intelligence section."""
        content = """
## Intelligence Summary

"""
        if intelligence_data.get("summary"):
            content += intelligence_data["summary"] + "\n\n"

        if intelligence_data.get("key_entities"):
            content += "### Key Entities\n"
            for entity in intelligence_data["key_entities"]:
                content += f"- {entity}\n"

        if intelligence_data.get("threats"):
            content += "\n### Known Threats\n"
            for threat in intelligence_data["threats"]:
                content += f"- {threat}\n"

        return BriefingSectionContent(
            section=BriefingSection.INTELLIGENCE,
            title="Intelligence Summary",
            content=content,
            data=intelligence_data,
        )

    def _generate_safety_section(
        self,
        safety_data: dict[str, Any],
    ) -> BriefingSectionContent:
        """Generate officer safety section."""
        content = """
## Officer Safety

"""
        if safety_data.get("alerts"):
            content += "### Active Alerts\n"
            for alert in safety_data["alerts"]:
                content += f"- {alert}\n"

        if safety_data.get("hazards"):
            content += "\n### Known Hazards\n"
            for hazard in safety_data["hazards"]:
                content += f"- {hazard}\n"

        if safety_data.get("recommendations"):
            content += "\n### Safety Recommendations\n"
            for rec in safety_data["recommendations"]:
                content += f"- {rec}\n"

        return BriefingSectionContent(
            section=BriefingSection.OFFICER_SAFETY,
            title="Officer Safety",
            content=content,
            data=safety_data,
        )

    def _generate_action_items_section(
        self,
        notes: list[CommandNote],
    ) -> BriefingSectionContent:
        """Generate action items section."""
        content = """
## Action Items

"""
        for i, note in enumerate(notes, 1):
            priority = note.priority.upper() if isinstance(note.priority, str) else note.priority
            content += f"{i}. [{priority}] {note.content}\n"
            if note.created_by_name:
                content += f"   - Assigned by: {note.created_by_name}\n"

        return BriefingSectionContent(
            section=BriefingSection.ACTION_ITEMS,
            title="Action Items",
            content=content,
            data={"notes": [n.model_dump() for n in notes]},
        )

    async def export_briefing(
        self,
        incident_id: str,
        briefing_id: str,
        format_type: ExportFormat,
    ) -> dict[str, Any]:
        """
        Export a briefing to a specific format.

        Args:
            incident_id: ID of the incident
            briefing_id: ID of briefing to export
            format_type: Export format

        Returns:
            Export result with content or URL
        """
        briefings = self._briefings.get(incident_id, [])
        briefing = next((b for b in briefings if b.id == briefing_id), None)

        if not briefing:
            raise ValueError(f"Briefing {briefing_id} not found")

        if format_type == ExportFormat.JSON:
            return {
                "format": "json",
                "content": briefing.model_dump(),
            }

        elif format_type == ExportFormat.MARKDOWN:
            content = f"# {briefing.title}\n\n"
            content += f"**Generated:** {briefing.generated_at.isoformat()}\n"
            content += f"**Version:** {briefing.version}\n\n"
            content += "---\n\n"

            for section in briefing.sections:
                content += section.content + "\n\n"

            return {
                "format": "markdown",
                "content": content,
            }

        elif format_type == ExportFormat.HTML:
            content = f"<html><head><title>{briefing.title}</title></head><body>"
            content += f"<h1>{briefing.title}</h1>"
            content += f"<p><strong>Generated:</strong> {briefing.generated_at.isoformat()}</p>"
            content += f"<p><strong>Version:</strong> {briefing.version}</p>"
            content += "<hr>"

            for section in briefing.sections:
                # Simple markdown to HTML conversion
                section_html = section.content.replace("\n", "<br>")
                section_html = section_html.replace("## ", "<h2>").replace("\n", "</h2>", 1)
                section_html = section_html.replace("### ", "<h3>").replace("\n", "</h3>", 1)
                content += section_html

            content += "</body></html>"

            return {
                "format": "html",
                "content": content,
            }

        else:
            # For PDF and DOCX, return placeholder
            # In production, this would use a document generation library
            logger.info(
                "briefing_export_requested",
                incident_id=incident_id,
                briefing_id=briefing_id,
                format=format_type,
            )

            return {
                "format": format_type,
                "message": f"Export to {format_type} would be generated here",
                "briefing_id": briefing_id,
            }

    async def get_briefings(
        self,
        incident_id: str,
        limit: int = 10,
    ) -> list[CommandBriefing]:
        """
        Get briefings for an incident.

        Args:
            incident_id: ID of the incident
            limit: Maximum number to return

        Returns:
            List of CommandBriefing
        """
        briefings = self._briefings.get(incident_id, [])
        briefings.sort(key=lambda x: x.generated_at, reverse=True)
        return briefings[:limit]

    async def get_briefing(
        self,
        incident_id: str,
        briefing_id: str,
    ) -> CommandBriefing | None:
        """Get a specific briefing."""
        briefings = self._briefings.get(incident_id, [])
        return next((b for b in briefings if b.id == briefing_id), None)

    async def approve_briefing(
        self,
        incident_id: str,
        briefing_id: str,
        approved_by: str,
    ) -> CommandBriefing | None:
        """
        Approve a briefing as final.

        Args:
            incident_id: ID of the incident
            briefing_id: ID of briefing
            approved_by: User approving

        Returns:
            Updated CommandBriefing or None
        """
        briefing = await self.get_briefing(incident_id, briefing_id)
        if not briefing:
            return None

        briefing.is_final = True
        briefing.approved_by = approved_by
        briefing.approved_at = datetime.now(UTC)

        logger.info(
            "command_briefing_approved",
            incident_id=incident_id,
            briefing_id=briefing_id,
            approved_by=approved_by,
        )

        return briefing

    async def get_note_statistics(
        self,
        incident_id: str,
    ) -> dict[str, Any]:
        """
        Get statistics about notes.

        Args:
            incident_id: ID of the incident

        Returns:
            Dictionary of statistics
        """
        notes = self._notes.get(incident_id, [])
        active_notes = [n for n in notes if not n.is_redacted]

        # Count by type
        by_type: dict[str, int] = {}
        for note in active_notes:
            by_type[note.note_type] = by_type.get(note.note_type, 0) + 1

        # Count by priority
        by_priority: dict[str, int] = {}
        for note in active_notes:
            by_priority[note.priority] = by_priority.get(note.priority, 0) + 1

        return {
            "total_notes": len(active_notes),
            "pinned_count": sum(1 for n in active_notes if n.is_pinned),
            "attachment_count": sum(len(n.attachments) for n in active_notes),
            "by_type": by_type,
            "by_priority": by_priority,
            "briefing_count": len(self._briefings.get(incident_id, [])),
        }
