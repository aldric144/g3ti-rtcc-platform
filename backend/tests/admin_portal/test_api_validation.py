"""
Test Suite 9: API Validation Tests

Tests for API input validation and error handling.
"""

import pytest
from pydantic import ValidationError

from app.admin_logs.activity_log_model import (
    ActivityLogCreate,
    ActivityLogUpdate,
    ActivityLogSearchParams,
    LogType,
    LogPriority,
)
from app.shift_admin.shift_model import (
    ShiftCreate,
    ShiftClose,
    AddOperatorRequest,
    RecordMajorEventRequest,
    OperatorRole,
)
from app.case_tools.case_tools_model import (
    CaseNoteCreate,
    CaseFlagCreate,
    UnitRequestCreate,
    CaseShellCreate,
    BOLOZoneCreate,
    FlagType,
    CasePriority,
)
from app.patrol_insights.heatmap_engine import (
    PatrolZoneCreate,
    GeoPoint,
    ZoneType,
)


class TestActivityLogValidation:
    """Tests for activity log API validation."""
    
    def test_valid_log_create(self):
        """Test valid log creation data."""
        data = ActivityLogCreate(
            log_type=LogType.INCIDENT,
            priority=LogPriority.HIGH,
            notes="Valid notes",
        )
        assert data.log_type == LogType.INCIDENT
    
    def test_empty_notes_rejected(self):
        """Test that empty notes are rejected."""
        with pytest.raises(ValidationError):
            ActivityLogCreate(
                log_type=LogType.INCIDENT,
                priority=LogPriority.HIGH,
                notes="",
            )
    
    def test_notes_max_length(self):
        """Test notes maximum length validation."""
        # Should work with 5000 chars
        data = ActivityLogCreate(
            log_type=LogType.INCIDENT,
            priority=LogPriority.HIGH,
            notes="x" * 5000,
        )
        assert len(data.notes) == 5000
    
    def test_search_params_defaults(self):
        """Test search params have correct defaults."""
        params = ActivityLogSearchParams()
        assert params.limit == 50
        assert params.offset == 0
        assert params.include_archived is False
    
    def test_search_params_limit_bounds(self):
        """Test search params limit bounds."""
        # Valid limit
        params = ActivityLogSearchParams(limit=100)
        assert params.limit == 100
        
        # Invalid limit (too high)
        with pytest.raises(ValidationError):
            ActivityLogSearchParams(limit=1000)


class TestShiftValidation:
    """Tests for shift API validation."""
    
    def test_valid_shift_create(self):
        """Test valid shift creation data."""
        data = ShiftCreate(supervisor="Sgt. Johnson")
        assert data.supervisor == "Sgt. Johnson"
    
    def test_valid_shift_close(self):
        """Test valid shift close data."""
        data = ShiftClose(
            closing_notes="Shift ended normally",
            supervisor_signoff="Sgt. Johnson",
        )
        assert data.supervisor_signoff == "Sgt. Johnson"
    
    def test_valid_operator_request(self):
        """Test valid operator request data."""
        data = AddOperatorRequest(
            username="jsmith",
            name="John Smith",
            role=OperatorRole.OPERATOR,
        )
        assert data.role == OperatorRole.OPERATOR
    
    def test_valid_major_event_request(self):
        """Test valid major event request data."""
        data = RecordMajorEventRequest(
            event_type="10-33",
            description="Emergency situation",
        )
        assert data.event_type == "10-33"


class TestCaseToolsValidation:
    """Tests for case tools API validation."""
    
    def test_valid_case_note(self):
        """Test valid case note data."""
        data = CaseNoteCreate(
            content="Valid note content",
        )
        assert data.content == "Valid note content"
    
    def test_empty_note_content_rejected(self):
        """Test that empty note content is rejected."""
        with pytest.raises(ValidationError):
            CaseNoteCreate(content="")
    
    def test_valid_case_flag(self):
        """Test valid case flag data."""
        data = CaseFlagCreate(
            case_id="RTCC-2025-00001",
            flag_type=FlagType.RTCC_ASSISTED,
        )
        assert data.flag_type == FlagType.RTCC_ASSISTED
    
    def test_valid_unit_request(self):
        """Test valid unit request data."""
        data = UnitRequestCreate(
            case_id="RTCC-2025-00001",
            request_type="follow_up",
            priority=CasePriority.HIGH,
            details="Follow up with witness",
        )
        assert data.priority == CasePriority.HIGH
    
    def test_valid_case_shell(self):
        """Test valid case shell data."""
        data = CaseShellCreate(
            title="Test Case",
            priority=CasePriority.MEDIUM,
        )
        assert data.title == "Test Case"
    
    def test_empty_title_rejected(self):
        """Test that empty title is rejected."""
        with pytest.raises(ValidationError):
            CaseShellCreate(
                title="",
                priority=CasePriority.MEDIUM,
            )
    
    def test_valid_bolo_zone(self):
        """Test valid BOLO zone data."""
        data = BOLOZoneCreate(
            case_id="RTCC-2025-00001",
            zone_name="Test Zone",
            description="Test description",
            lat=26.7754,
            lng=-80.0583,
        )
        assert data.zone_name == "Test Zone"
    
    def test_bolo_zone_lat_bounds(self):
        """Test BOLO zone latitude bounds."""
        # Valid latitude
        data = BOLOZoneCreate(
            case_id="CASE-1",
            zone_name="Zone",
            description="Desc",
            lat=45.0,
            lng=-80.0,
        )
        assert data.lat == 45.0
        
        # Invalid latitude (too high)
        with pytest.raises(ValidationError):
            BOLOZoneCreate(
                case_id="CASE-1",
                zone_name="Zone",
                description="Desc",
                lat=100.0,
                lng=-80.0,
            )
    
    def test_bolo_zone_radius_bounds(self):
        """Test BOLO zone radius bounds."""
        # Valid radius
        data = BOLOZoneCreate(
            case_id="CASE-1",
            zone_name="Zone",
            description="Desc",
            lat=26.7754,
            lng=-80.0583,
            radius_meters=500,
        )
        assert data.radius_meters == 500


class TestPatrolInsightsValidation:
    """Tests for patrol insights API validation."""
    
    def test_valid_geo_point(self):
        """Test valid geographic point."""
        point = GeoPoint(lat=26.7754, lng=-80.0583)
        assert point.lat == 26.7754
    
    def test_geo_point_lat_bounds(self):
        """Test geographic point latitude bounds."""
        with pytest.raises(ValidationError):
            GeoPoint(lat=100.0, lng=-80.0)
    
    def test_geo_point_lng_bounds(self):
        """Test geographic point longitude bounds."""
        with pytest.raises(ValidationError):
            GeoPoint(lat=26.0, lng=-200.0)
    
    def test_valid_patrol_zone_create(self):
        """Test valid patrol zone creation data."""
        data = PatrolZoneCreate(
            zone_type=ZoneType.HOTSPOT,
            name="Test Zone",
            center=GeoPoint(lat=26.7754, lng=-80.0583),
        )
        assert data.zone_type == ZoneType.HOTSPOT
    
    def test_patrol_zone_radius_bounds(self):
        """Test patrol zone radius bounds."""
        # Valid radius
        data = PatrolZoneCreate(
            zone_type=ZoneType.HOTSPOT,
            name="Zone",
            center=GeoPoint(lat=26.7754, lng=-80.0583),
            radius_meters=500,
        )
        assert data.radius_meters == 500
    
    def test_patrol_zone_intensity_bounds(self):
        """Test patrol zone intensity bounds."""
        # Valid intensity
        data = PatrolZoneCreate(
            zone_type=ZoneType.HOTSPOT,
            name="Zone",
            center=GeoPoint(lat=26.7754, lng=-80.0583),
            intensity=0.5,
        )
        assert data.intensity == 0.5
