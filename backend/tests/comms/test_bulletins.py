"""Tests for the Automated Bulletins module."""


import pytest

from app.comms.bulletins import (
    Bulletin,
    BulletinManager,
    BulletinPriority,
    BulletinStatus,
    BulletinType,
    LinkedEntity,
    MapOverlay,
)


@pytest.fixture
def bulletin_manager():
    """Create a bulletin manager instance."""
    return BulletinManager()


class TestBulletinManager:
    """Tests for BulletinManager."""

    @pytest.mark.asyncio
    async def test_create_bulletin(self, bulletin_manager):
        """Test creating a bulletin."""
        bulletin = await bulletin_manager.create_bulletin(
            bulletin_type=BulletinType.HIGH_RISK_VEHICLE,
            title="High-Risk Vehicle Alert",
            summary="Vehicle ABC123 associated with armed robbery",
            priority=BulletinPriority.HIGH,
        )

        assert bulletin is not None
        assert bulletin.bulletin_type == BulletinType.HIGH_RISK_VEHICLE
        assert bulletin.priority == BulletinPriority.HIGH
        assert bulletin.status == BulletinStatus.DRAFT
        assert bulletin.audit_id is not None

    @pytest.mark.asyncio
    async def test_create_bulletin_with_entities(self, bulletin_manager):
        """Test creating a bulletin with linked entities."""
        entity = LinkedEntity(
            entity_id="ABC123",
            entity_type="vehicle",
            name="Black Sedan",
            risk_level="high",
        )

        bulletin = await bulletin_manager.create_bulletin(
            bulletin_type=BulletinType.HIGH_RISK_VEHICLE,
            title="Vehicle Alert",
            summary="Suspect vehicle",
            entities=[entity],
        )

        assert len(bulletin.entities) == 1
        assert bulletin.entities[0].entity_id == "ABC123"

    @pytest.mark.asyncio
    async def test_create_bulletin_auto_publish(self, bulletin_manager):
        """Test creating and auto-publishing a bulletin."""
        bulletin = await bulletin_manager.create_bulletin(
            bulletin_type=BulletinType.OFFICER_SAFETY,
            title="Officer Safety Alert",
            summary="Critical safety information",
            priority=BulletinPriority.URGENT,
            auto_publish=True,
        )

        assert bulletin.status == BulletinStatus.PUBLISHED
        assert bulletin.published_at is not None

    @pytest.mark.asyncio
    async def test_create_bulletin_from_template(self, bulletin_manager):
        """Test creating a bulletin from a template."""
        bulletin = await bulletin_manager.create_bulletin_from_template(
            template_id="high_risk_vehicle",
            variables={
                "plate": "ABC123",
                "make": "Honda",
                "model": "Accord",
                "color": "Black",
                "year": "2020",
                "reason": "Armed robbery suspect",
                "area": "Central District",
                "last_seen": "10 minutes ago",
            },
        )

        assert bulletin is not None
        assert bulletin.auto_generated is True
        assert "ABC123" in bulletin.title

    @pytest.mark.asyncio
    async def test_publish_bulletin(self, bulletin_manager):
        """Test publishing a bulletin."""
        bulletin = await bulletin_manager.create_bulletin(
            bulletin_type=BulletinType.SUSPECT_PATTERN,
            title="Suspect Pattern",
            summary="Pattern identified",
        )

        published = await bulletin_manager.publish_bulletin(
            bulletin_id=bulletin.id,
            approved_by="supervisor1",
        )

        assert published.status == BulletinStatus.PUBLISHED
        assert published.approved_by == "supervisor1"
        assert published.published_at is not None

    @pytest.mark.asyncio
    async def test_get_bulletin_feed(self, bulletin_manager):
        """Test getting bulletin feed."""
        # Create and publish some bulletins
        for i in range(3):
            await bulletin_manager.create_bulletin(
                bulletin_type=BulletinType.INTELLIGENCE_SUMMARY,
                title=f"Bulletin {i}",
                summary=f"Summary {i}",
                auto_publish=True,
            )

        feed = await bulletin_manager.get_bulletin_feed()

        assert len(feed) >= 3

    @pytest.mark.asyncio
    async def test_get_bulletin_feed_by_type(self, bulletin_manager):
        """Test filtering bulletin feed by type."""
        await bulletin_manager.create_bulletin(
            bulletin_type=BulletinType.BOLO,
            title="BOLO Bulletin",
            summary="Be on lookout",
            auto_publish=True,
        )

        feed = await bulletin_manager.get_bulletin_feed(
            bulletin_type=BulletinType.BOLO
        )

        assert all(b.bulletin_type == BulletinType.BOLO for b in feed)

    @pytest.mark.asyncio
    async def test_acknowledge_bulletin(self, bulletin_manager):
        """Test acknowledging a bulletin."""
        bulletin = await bulletin_manager.create_bulletin(
            bulletin_type=BulletinType.OFFICER_SAFETY,
            title="Safety Bulletin",
            summary="Important safety info",
            auto_publish=True,
        )

        updated = await bulletin_manager.acknowledge_bulletin(
            bulletin_id=bulletin.id,
            badge="A1101",
        )

        assert "A1101" in updated.acknowledged_by

    @pytest.mark.asyncio
    async def test_increment_view_count(self, bulletin_manager):
        """Test incrementing view count."""
        bulletin = await bulletin_manager.create_bulletin(
            bulletin_type=BulletinType.CRIME_TREND,
            title="Crime Trend",
            summary="Trend analysis",
        )

        assert bulletin.view_count == 0

        await bulletin_manager.increment_view_count(bulletin.id)
        updated = await bulletin_manager.get_bulletin(bulletin.id)

        assert updated.view_count == 1

    @pytest.mark.asyncio
    async def test_archive_bulletin(self, bulletin_manager):
        """Test archiving a bulletin."""
        bulletin = await bulletin_manager.create_bulletin(
            bulletin_type=BulletinType.SHIFT_BRIEFING,
            title="Shift Briefing",
            summary="Briefing summary",
        )

        archived = await bulletin_manager.archive_bulletin(bulletin.id)

        assert archived.status == BulletinStatus.ARCHIVED

    @pytest.mark.asyncio
    async def test_generate_high_risk_vehicle_bulletin(self, bulletin_manager):
        """Test auto-generating high-risk vehicle bulletin."""
        bulletin = await bulletin_manager.generate_high_risk_vehicle_bulletin(
            plate="XYZ789",
            make="Toyota",
            model="Camry",
            color="White",
            year="2019",
            reason="Felony warrant",
            area="North District",
            last_seen="5 minutes ago",
        )

        assert bulletin is not None
        assert bulletin.bulletin_type == BulletinType.HIGH_RISK_VEHICLE
        assert bulletin.auto_generated is True

    @pytest.mark.asyncio
    async def test_generate_shift_briefing(self, bulletin_manager):
        """Test auto-generating shift briefing."""
        bulletin = await bulletin_manager.generate_shift_briefing(
            shift="A",
            date="2024-01-15",
            bolo_count=5,
            hot_zones=["Zone 3", "Zone 7"],
            patterns=["Burglary pattern in North"],
            safety_notes=["Officer safety alert active"],
        )

        assert bulletin is not None
        assert bulletin.bulletin_type == BulletinType.SHIFT_BRIEFING
        assert "A" in bulletin.target_shifts

    @pytest.mark.asyncio
    async def test_get_all_templates(self, bulletin_manager):
        """Test getting all bulletin templates."""
        templates = bulletin_manager.get_all_templates()

        assert len(templates) > 0
        assert any(t.id == "high_risk_vehicle" for t in templates)
        assert any(t.id == "shift_briefing" for t in templates)


class TestBulletinModel:
    """Tests for Bulletin model."""

    def test_bulletin_creation(self):
        """Test creating a bulletin."""
        bulletin = Bulletin(
            bulletin_type=BulletinType.BOLO,
            title="BOLO",
            summary="Be on lookout for suspect",
        )

        assert bulletin.id is not None
        assert bulletin.status == BulletinStatus.DRAFT
        assert bulletin.audit_id is not None

    def test_bulletin_with_map_overlay(self):
        """Test bulletin with map overlay."""
        overlay = MapOverlay(
            center=(33.7490, -84.3880),
            zoom=15,
            markers=[{"lat": 33.7490, "lng": -84.3880, "label": "Location"}],
        )

        bulletin = Bulletin(
            bulletin_type=BulletinType.TACTICAL_ZONE,
            title="Zone Update",
            summary="Zone status changed",
            map_overlay=overlay,
        )

        assert bulletin.map_overlay is not None
        assert bulletin.map_overlay.center == (33.7490, -84.3880)


class TestLinkedEntityModel:
    """Tests for LinkedEntity model."""

    def test_linked_entity_creation(self):
        """Test creating a linked entity."""
        entity = LinkedEntity(
            entity_id="PERSON-001",
            entity_type="person",
            name="John Doe",
            risk_level="high",
        )

        assert entity.entity_id == "PERSON-001"
        assert entity.entity_type == "person"
