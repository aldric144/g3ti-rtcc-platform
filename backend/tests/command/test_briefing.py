"""Tests for Command Notes & Briefing Generator."""


import pytest

from app.command.briefing import (
    BriefingManager,
    BriefingSection,
    ExportFormat,
    NotePriority,
    NoteType,
)


class TestBriefingManager:
    """Test cases for BriefingManager."""

    @pytest.fixture
    def manager(self):
        """Create a BriefingManager instance."""
        return BriefingManager()

    @pytest.mark.asyncio
    async def test_add_note(self, manager):
        """Test adding a command note."""
        note = await manager.add_note(
            incident_id="inc-001",
            content="Suspect described as male, 30s, wearing dark hoodie",
            note_type=NoteType.INTELLIGENCE,
            priority=NotePriority.HIGH,
            created_by="analyst-001",
        )

        assert note is not None
        assert note.content == "Suspect described as male, 30s, wearing dark hoodie"
        assert note.note_type == NoteType.INTELLIGENCE
        assert note.priority == NotePriority.HIGH

    @pytest.mark.asyncio
    async def test_get_notes(self, manager):
        """Test getting notes for an incident."""
        incident_id = "inc-002"

        await manager.add_note(
            incident_id=incident_id,
            content="Note 1",
            note_type=NoteType.GENERAL,
            priority=NotePriority.MEDIUM,
            created_by="user-001",
        )
        await manager.add_note(
            incident_id=incident_id,
            content="Note 2",
            note_type=NoteType.TACTICAL,
            priority=NotePriority.HIGH,
            created_by="user-002",
        )

        notes = await manager.get_notes(incident_id)

        assert len(notes) >= 2

    @pytest.mark.asyncio
    async def test_pin_note(self, manager):
        """Test pinning a note."""
        note = await manager.add_note(
            incident_id="inc-001",
            content="Important note",
            note_type=NoteType.SITUATION,
            priority=NotePriority.HIGH,
            created_by="commander-001",
        )

        pinned = await manager.pin_note(
            incident_id="inc-001",
            note_id=note.id,
            pinned_by="commander-001",
        )

        assert pinned.is_pinned is True

    @pytest.mark.asyncio
    async def test_update_note(self, manager):
        """Test updating a note."""
        note = await manager.add_note(
            incident_id="inc-001",
            content="Original content",
            note_type=NoteType.GENERAL,
            priority=NotePriority.LOW,
            created_by="user-001",
        )

        updated = await manager.update_note(
            incident_id="inc-001",
            note_id=note.id,
            content="Updated content",
            updated_by="user-001",
        )

        assert updated.content == "Updated content"

    @pytest.mark.asyncio
    async def test_generate_briefing(self, manager):
        """Test generating a command briefing."""
        incident_id = "inc-003"

        # Add some notes first
        await manager.add_note(
            incident_id=incident_id,
            content="Situation update",
            note_type=NoteType.SITUATION,
            priority=NotePriority.HIGH,
            created_by="commander-001",
        )

        briefing = await manager.generate_briefing(
            incident_id=incident_id,
            generated_by="commander-001",
            include_sections=[
                BriefingSection.EXECUTIVE_SUMMARY,
                BriefingSection.SITUATION,
                BriefingSection.ICS_STRUCTURE,
                BriefingSection.RESOURCES,
                BriefingSection.TIMELINE,
            ],
        )

        assert briefing is not None
        assert briefing.incident_id == incident_id
        assert len(briefing.sections) > 0

    @pytest.mark.asyncio
    async def test_export_briefing_pdf(self, manager):
        """Test exporting briefing as PDF."""
        incident_id = "inc-004"

        briefing = await manager.generate_briefing(
            incident_id=incident_id,
            generated_by="commander-001",
            include_sections=[BriefingSection.EXECUTIVE_SUMMARY],
        )

        export_result = await manager.export_briefing(
            incident_id=incident_id,
            briefing_id=briefing.id,
            format=ExportFormat.PDF,
            exported_by="commander-001",
        )

        assert export_result is not None
        assert export_result.format == ExportFormat.PDF

    @pytest.mark.asyncio
    async def test_export_briefing_docx(self, manager):
        """Test exporting briefing as DOCX."""
        incident_id = "inc-005"

        briefing = await manager.generate_briefing(
            incident_id=incident_id,
            generated_by="commander-001",
            include_sections=[BriefingSection.EXECUTIVE_SUMMARY],
        )

        export_result = await manager.export_briefing(
            incident_id=incident_id,
            briefing_id=briefing.id,
            format=ExportFormat.DOCX,
            exported_by="commander-001",
        )

        assert export_result is not None
        assert export_result.format == ExportFormat.DOCX

    @pytest.mark.asyncio
    async def test_export_briefing_json(self, manager):
        """Test exporting briefing as JSON."""
        incident_id = "inc-006"

        briefing = await manager.generate_briefing(
            incident_id=incident_id,
            generated_by="commander-001",
            include_sections=[BriefingSection.EXECUTIVE_SUMMARY],
        )

        export_result = await manager.export_briefing(
            incident_id=incident_id,
            briefing_id=briefing.id,
            format=ExportFormat.JSON,
            exported_by="commander-001",
        )

        assert export_result is not None
        assert export_result.format == ExportFormat.JSON

    @pytest.mark.asyncio
    async def test_note_types(self, manager):
        """Test all note types can be added."""
        incident_id = "inc-007"

        for note_type in NoteType:
            note = await manager.add_note(
                incident_id=incident_id,
                content=f"Test {note_type.value}",
                note_type=note_type,
                priority=NotePriority.MEDIUM,
                created_by="test-user",
            )
            assert note.note_type == note_type

    @pytest.mark.asyncio
    async def test_get_pinned_notes(self, manager):
        """Test getting pinned notes."""
        incident_id = "inc-008"

        note1 = await manager.add_note(
            incident_id=incident_id,
            content="Pinned note",
            note_type=NoteType.INTELLIGENCE,
            priority=NotePriority.HIGH,
            created_by="analyst-001",
        )
        await manager.pin_note(incident_id, note1.id, "commander-001")

        await manager.add_note(
            incident_id=incident_id,
            content="Regular note",
            note_type=NoteType.GENERAL,
            priority=NotePriority.LOW,
            created_by="user-001",
        )

        pinned = await manager.get_pinned_notes(incident_id)

        assert len(pinned) >= 1
        assert all(n.is_pinned for n in pinned)

    @pytest.mark.asyncio
    async def test_attach_file_to_note(self, manager):
        """Test attaching a file to a note."""
        note = await manager.add_note(
            incident_id="inc-001",
            content="Note with attachment",
            note_type=NoteType.INTELLIGENCE,
            priority=NotePriority.HIGH,
            created_by="analyst-001",
        )

        updated = await manager.attach_file(
            incident_id="inc-001",
            note_id=note.id,
            file_name="evidence.pdf",
            file_type="application/pdf",
            file_path="/uploads/evidence.pdf",
            attached_by="analyst-001",
        )

        assert len(updated.attachments) >= 1

    @pytest.mark.asyncio
    async def test_briefing_sections(self, manager):
        """Test all briefing sections can be included."""
        incident_id = "inc-009"

        briefing = await manager.generate_briefing(
            incident_id=incident_id,
            generated_by="commander-001",
            include_sections=list(BriefingSection),
        )

        assert briefing is not None
        # Should have content for requested sections
        assert len(briefing.sections) > 0

    @pytest.mark.asyncio
    async def test_approve_briefing(self, manager):
        """Test approving a briefing."""
        incident_id = "inc-010"

        briefing = await manager.generate_briefing(
            incident_id=incident_id,
            generated_by="analyst-001",
            include_sections=[BriefingSection.EXECUTIVE_SUMMARY],
        )

        approved = await manager.approve_briefing(
            incident_id=incident_id,
            briefing_id=briefing.id,
            approved_by="commander-001",
        )

        assert approved.is_approved is True
        assert approved.approved_by == "commander-001"
