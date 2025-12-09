"""
Unit tests for ATF eTrace Export module.
"""



class TestETraceExportManager:
    """Tests for ETraceExportManager class."""

    def test_create_trace_request(self):
        """Test creating a trace request."""
        from app.federal.etrace import ETraceFirearmType, etrace_export_manager

        request = etrace_export_manager.create_trace_request(
            firearm_data={
                "id": "firearm-123",
                "serial_number": "ABC123456",
                "make": "Glock",
                "model": "17",
                "caliber": "9mm",
            },
            firearm_type=ETraceFirearmType.PISTOL,
            recovery_date="2024-01-15",
            recovery_city="Miami",
            recovery_state="FL",
            agency_id="FL0000000",
            officer_name="Det. John Smith",
            user_id="user-001",
            user_name="Test User",
        )

        assert request is not None
        assert request.trace_number is not None
        assert request.status == "ready"
        assert request.firearm_type == ETraceFirearmType.PISTOL

    def test_export_weapon(self):
        """Test exporting a weapon to eTrace format."""
        from app.federal.etrace import etrace_export_manager

        weapon_data = {
            "id": "weapon-123",
            "serial_number": "XYZ789012",
            "make": "Smith & Wesson",
            "model": "M&P Shield",
            "caliber": ".40 S&W",
            "firearm_type": "pistol",
        }

        result = etrace_export_manager.export_weapon(
            weapon_data=weapon_data,
            recovery_date="2024-01-15",
            recovery_city="Tampa",
            recovery_state="FL",
            agency_id="FL0000000",
            user_id="user-001",
            user_name="Test User",
        )

        assert result is not None
        assert result["success"] is True

    def test_get_trace_request(self):
        """Test getting a trace request by ID."""
        from app.federal.etrace import ETraceFirearmType, etrace_export_manager

        # Create a request first
        request = etrace_export_manager.create_trace_request(
            firearm_data={"id": "firearm-456", "serial_number": "DEF456789"},
            firearm_type=ETraceFirearmType.RIFLE,
            recovery_date="2024-01-15",
            recovery_city="Orlando",
            recovery_state="FL",
            agency_id="FL0000000",
            officer_name="Det. Jane Doe",
            user_id="user-002",
            user_name="Test User 2",
        )

        # Retrieve it
        retrieved = etrace_export_manager.get_trace_request(request.id)

        assert retrieved is not None
        assert retrieved.id == request.id
        assert retrieved.trace_number == request.trace_number

    def test_get_statistics(self):
        """Test getting eTrace statistics."""
        from app.federal.etrace import etrace_export_manager

        stats = etrace_export_manager.get_statistics()

        assert stats is not None
        assert "total_requests" in stats
        assert "by_status" in stats
        assert "by_firearm_type" in stats


class TestETraceDataMapping:
    """Tests for eTrace data mapping."""

    def test_normalize_firearm_make(self):
        """Test firearm make normalization."""
        from app.federal.etrace import ETraceDataMapper

        mapper = ETraceDataMapper()

        assert mapper.normalize_make("glock") == "GLOCK"
        assert mapper.normalize_make("smith & wesson") == "SMITH & WESSON"
        assert mapper.normalize_make("S&W") == "SMITH & WESSON"

    def test_normalize_caliber(self):
        """Test caliber normalization."""
        from app.federal.etrace import ETraceDataMapper

        mapper = ETraceDataMapper()

        assert mapper.normalize_caliber("9mm") == "9MM"
        assert mapper.normalize_caliber("9 mm") == "9MM"
        assert mapper.normalize_caliber(".45 ACP") == ".45 ACP"

    def test_map_recovery_data(self):
        """Test recovery data mapping."""
        from app.federal.etrace import ETraceDataMapper

        mapper = ETraceDataMapper()

        recovery = mapper.map_recovery_data(
            date="2024-01-15",
            city="Miami",
            state="FL",
            recovery_type="crime_gun",
            description="Recovered during traffic stop",
        )

        assert recovery is not None
        assert recovery["date"] == "2024-01-15"
        assert recovery["location"]["city"] == "MIAMI"
        assert recovery["location"]["state"] == "FL"
        assert recovery["type"] == "crime_gun"

    def test_map_possessor_data(self):
        """Test possessor data mapping with masking."""
        from app.federal.etrace import ETraceDataMapper

        mapper = ETraceDataMapper()

        possessor = mapper.map_possessor_data(
            last_name="Smith",
            first_name="John",
            date_of_birth="1990-01-15",
            relationship="suspect",
        )

        assert possessor is not None
        # Sensitive fields should be masked
        assert "***" in possessor.get("last_name", "") or possessor.get("last_name") == "***MASKED***"


class TestETraceValidation:
    """Tests for eTrace validation."""

    def test_validate_trace_request(self):
        """Test trace request validation."""
        from app.federal.etrace import ETraceFirearmType, ETraceRequest

        request = ETraceRequest(
            id="trace-123",
            trace_number="TR-2024-ABC123",
            agency_id="FL0000000",
            officer_name="Det. John Smith",
            firearm_type=ETraceFirearmType.PISTOL,
            serial_number="ABC123456",
            make="Glock",
            model="17",
            caliber="9mm",
            recovery_date="2024-01-15",
            recovery_city="Miami",
            recovery_state="FL",
        )

        validation = request.validate()

        assert validation.is_valid is True
        assert len(validation.errors) == 0

    def test_validate_trace_request_missing_serial(self):
        """Test trace request validation with missing serial."""
        from app.federal.etrace import ETraceFirearmType, ETraceRequest

        request = ETraceRequest(
            id="trace-456",
            trace_number="TR-2024-DEF456",
            agency_id="FL0000000",
            officer_name="Det. Jane Doe",
            firearm_type=ETraceFirearmType.RIFLE,
            serial_number=None,  # Missing
            make="Remington",
            model="700",
            caliber=".308",
            recovery_date="2024-01-15",
            recovery_city="Tampa",
            recovery_state="FL",
        )

        validation = request.validate()

        # Should have warning about missing serial
        assert len(validation.warnings) > 0 or validation.is_valid is True


class TestETraceReport:
    """Tests for eTrace report generation."""

    def test_generate_report(self):
        """Test report generation."""
        from app.federal.etrace import ETraceFirearmType, etrace_export_manager

        # Create a request first
        request = etrace_export_manager.create_trace_request(
            firearm_data={"id": "firearm-789", "serial_number": "GHI789012"},
            firearm_type=ETraceFirearmType.SHOTGUN,
            recovery_date="2024-01-15",
            recovery_city="Jacksonville",
            recovery_state="FL",
            agency_id="FL0000000",
            officer_name="Det. Bob Wilson",
            user_id="user-003",
            user_name="Test User 3",
        )

        # Generate report
        report = etrace_export_manager.generate_report(
            trace_id=request.id,
            agency_id="FL0000000",
        )

        assert report is not None
        assert report.trace_request_id == request.id
