"""
Unit tests for DHS SAR Submission module.
"""



class TestSARManager:
    """Tests for SARManager class."""

    def test_create_sar(self):
        """Test creating a SAR."""
        from app.federal.dhs_sar import (
            SARBehaviorCategory,
            SARThreatLevel,
            sar_manager,
        )

        sar = sar_manager.create_sar(
            behavior_category=SARBehaviorCategory.OBSERVATION_SURVEILLANCE,
            activity_date="2024-01-15",
            activity_time="14:30:00",
            city="Miami",
            state="FL",
            narrative="Subject observed photographing federal building for approximately 30 minutes.",
            threat_assessment=SARThreatLevel.MEDIUM,
            agency_id="FL0000000",
            officer_name="Officer Jane Doe",
            user_id="user-001",
            user_name="Test User",
        )

        assert sar is not None
        assert sar.sar_number is not None
        assert sar.status.value == "draft"
        assert sar.behavior_category == SARBehaviorCategory.OBSERVATION_SURVEILLANCE

    def test_create_sar_with_subject(self):
        """Test creating a SAR with subject information."""
        from app.federal.dhs_sar import (
            SARBehaviorCategory,
            SARSubject,
            SARThreatLevel,
            sar_manager,
        )

        subject = SARSubject(
            last_name="Smith",
            first_name="John",
            sex="M",
            race="W",
            height="5'10\"",
            weight="175",
        )

        sar = sar_manager.create_sar(
            behavior_category=SARBehaviorCategory.PHOTOGRAPHY,
            activity_date="2024-01-15",
            city="Tampa",
            state="FL",
            narrative="Subject observed taking photographs of critical infrastructure facility.",
            threat_assessment=SARThreatLevel.LOW,
            agency_id="FL0000000",
            officer_name="Officer Bob Wilson",
            user_id="user-002",
            user_name="Test User 2",
            subjects=[subject],
        )

        assert sar is not None
        assert len(sar.subjects) == 1

    def test_update_sar(self):
        """Test updating a SAR."""
        from app.federal.dhs_sar import (
            SARBehaviorCategory,
            SARThreatLevel,
            sar_manager,
        )

        # Create SAR first
        sar = sar_manager.create_sar(
            behavior_category=SARBehaviorCategory.ELICITATION,
            activity_date="2024-01-15",
            city="Orlando",
            state="FL",
            narrative="Subject asking questions about security procedures at government facility.",
            threat_assessment=SARThreatLevel.UNKNOWN,
            agency_id="FL0000000",
            officer_name="Officer Alice Johnson",
            user_id="user-003",
            user_name="Test User 3",
        )

        # Update it
        updated = sar_manager.update_sar(
            sar_id=sar.id,
            threat_assessment=SARThreatLevel.MEDIUM,
            narrative="Updated: Subject asking detailed questions about security procedures.",
        )

        assert updated is not None
        assert updated.threat_assessment == SARThreatLevel.MEDIUM

    def test_submit_sar(self):
        """Test submitting a SAR."""
        from app.federal.dhs_sar import (
            SARBehaviorCategory,
            SARStatus,
            SARThreatLevel,
            sar_manager,
        )

        # Create SAR first
        sar = sar_manager.create_sar(
            behavior_category=SARBehaviorCategory.TESTING_SECURITY,
            activity_date="2024-01-15",
            city="Jacksonville",
            state="FL",
            narrative="Subject observed testing security response times at federal building entrance.",
            threat_assessment=SARThreatLevel.HIGH,
            agency_id="FL0000000",
            officer_name="Sgt. John Smith",
            user_id="user-004",
            user_name="Test User 4",
        )

        # Submit it
        submitted = sar_manager.submit_sar(
            sar_id=sar.id,
            approver_name="Lt. Jane Doe",
        )

        assert submitted is not None
        assert submitted.status == SARStatus.SUBMITTED

    def test_get_sar(self):
        """Test getting a SAR by ID."""
        from app.federal.dhs_sar import (
            SARBehaviorCategory,
            SARThreatLevel,
            sar_manager,
        )

        # Create SAR first
        sar = sar_manager.create_sar(
            behavior_category=SARBehaviorCategory.BREACH_INTRUSION,
            activity_date="2024-01-15",
            city="Fort Lauderdale",
            state="FL",
            narrative="Subject attempted unauthorized access to restricted area of government facility.",
            threat_assessment=SARThreatLevel.CRITICAL,
            agency_id="FL0000000",
            officer_name="Officer Mike Brown",
            user_id="user-005",
            user_name="Test User 5",
        )

        # Retrieve it
        retrieved = sar_manager.get_sar(sar.id)

        assert retrieved is not None
        assert retrieved.id == sar.id
        assert retrieved.sar_number == sar.sar_number

    def test_get_statistics(self):
        """Test getting SAR statistics."""
        from app.federal.dhs_sar import sar_manager

        stats = sar_manager.get_statistics()

        assert stats is not None
        assert "total_sars" in stats
        assert "by_status" in stats
        assert "by_threat_level" in stats


class TestSARDataMapping:
    """Tests for SAR data mapping."""

    def test_map_behavior_category(self):
        """Test behavior category mapping."""
        from app.federal.dhs_sar import SARBehaviorCategory, SARDataMapper

        mapper = SARDataMapper()

        assert mapper.map_behavior_category("surveillance") == SARBehaviorCategory.OBSERVATION_SURVEILLANCE
        assert mapper.map_behavior_category("photography") == SARBehaviorCategory.PHOTOGRAPHY
        assert mapper.map_behavior_category("cyber") == SARBehaviorCategory.CYBER_ATTACK

    def test_map_threat_level(self):
        """Test threat level mapping."""
        from app.federal.dhs_sar import SARDataMapper, SARThreatLevel

        mapper = SARDataMapper()

        assert mapper.map_threat_level("critical") == SARThreatLevel.CRITICAL
        assert mapper.map_threat_level("high") == SARThreatLevel.HIGH
        assert mapper.map_threat_level("medium") == SARThreatLevel.MEDIUM
        assert mapper.map_threat_level("low") == SARThreatLevel.LOW

    def test_map_subject_with_masking(self):
        """Test subject mapping with sensitive field masking."""
        from app.federal.dhs_sar import SARDataMapper

        mapper = SARDataMapper()

        subject = mapper.map_subject(
            last_name="Smith",
            first_name="John",
            date_of_birth="1990-01-15",
            ssn="123-45-6789",
        )

        assert subject is not None
        # Sensitive fields should be masked
        assert "***" in subject.date_of_birth or subject.date_of_birth is None
        assert subject.ssn is None or "***" in subject.ssn

    def test_map_location(self):
        """Test location mapping."""
        from app.federal.dhs_sar import SARDataMapper

        mapper = SARDataMapper()

        location = mapper.map_location(
            street_address="123 Main St",
            city="Miami",
            state="FL",
            zip_code="33101",
            latitude=25.7617,
            longitude=-80.1918,
        )

        assert location is not None
        assert location.city == "MIAMI"
        assert location.state == "FL"


class TestSARValidation:
    """Tests for SAR validation."""

    def test_validate_sar_valid(self):
        """Test SAR validation with valid data."""
        from app.federal.dhs_sar import (
            SARBehaviorCategory,
            SARLocation,
            SARReport,
            SARStatus,
            SARThreatLevel,
        )

        sar = SARReport(
            id="sar-123",
            sar_number="SAR-20240115-ABC123",
            reporting_agency_ori="FL0000000",
            reporting_officer="Officer Jane Doe",
            behavior_category=SARBehaviorCategory.OBSERVATION_SURVEILLANCE,
            activity_date="2024-01-15",
            activity_time="14:30:00",
            location=SARLocation(city="Miami", state="FL"),
            narrative="Subject observed conducting surveillance of federal building for extended period.",
            threat_assessment=SARThreatLevel.MEDIUM,
            status=SARStatus.DRAFT,
        )

        validation = sar.validate()

        assert validation.is_valid is True
        assert len(validation.errors) == 0

    def test_validate_sar_short_narrative(self):
        """Test SAR validation with short narrative."""
        from app.federal.dhs_sar import (
            SARBehaviorCategory,
            SARLocation,
            SARReport,
            SARStatus,
            SARThreatLevel,
        )

        sar = SARReport(
            id="sar-456",
            sar_number="SAR-20240115-DEF456",
            reporting_agency_ori="FL0000000",
            reporting_officer="Officer Bob Wilson",
            behavior_category=SARBehaviorCategory.PHOTOGRAPHY,
            activity_date="2024-01-15",
            location=SARLocation(city="Tampa", state="FL"),
            narrative="Short",  # Too short
            threat_assessment=SARThreatLevel.LOW,
            status=SARStatus.DRAFT,
        )

        validation = sar.validate()

        # Should have warning or error about short narrative
        assert len(validation.warnings) > 0 or len(validation.errors) > 0


class TestSARBehaviorIndicators:
    """Tests for SAR behavior indicators."""

    def test_behavior_indicators(self):
        """Test behavior indicator enumeration."""
        from app.federal.dhs_sar import SARBehaviorIndicator

        # Check some key indicators exist
        assert SARBehaviorIndicator.PHOTOGRAPHING_FACILITIES is not None
        assert SARBehaviorIndicator.MONITORING_PERSONNEL is not None
        assert SARBehaviorIndicator.UNAUTHORIZED_ACCESS is not None
        assert SARBehaviorIndicator.TESTING_RESPONSE is not None

    def test_add_indicators_to_sar(self):
        """Test adding behavior indicators to SAR."""
        from app.federal.dhs_sar import (
            SARBehaviorCategory,
            SARBehaviorIndicator,
            SARThreatLevel,
            sar_manager,
        )

        sar = sar_manager.create_sar(
            behavior_category=SARBehaviorCategory.OBSERVATION_SURVEILLANCE,
            activity_date="2024-01-15",
            city="Miami",
            state="FL",
            narrative="Subject observed photographing and monitoring personnel at federal facility.",
            threat_assessment=SARThreatLevel.MEDIUM,
            agency_id="FL0000000",
            officer_name="Officer Test",
            user_id="user-006",
            user_name="Test User 6",
            behavior_indicators=[
                SARBehaviorIndicator.PHOTOGRAPHING_FACILITIES,
                SARBehaviorIndicator.MONITORING_PERSONNEL,
            ],
        )

        assert sar is not None
        assert len(sar.behavior_indicators) == 2
