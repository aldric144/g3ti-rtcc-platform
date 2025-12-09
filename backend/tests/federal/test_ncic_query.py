"""
Unit tests for NCIC Query Stub module.
"""



class TestNCICQueryManager:
    """Tests for NCICQueryManager class."""

    def test_query_vehicle_stub(self):
        """Test vehicle query stub."""
        from app.federal.ncic import ncic_query_manager

        result = ncic_query_manager.query_vehicle(
            vin="1HGBH41JXMN109186",
            license_plate="ABC123",
            license_state="FL",
            agency_id="FL0000000",
            user_id="user-001",
            user_name="Test User",
        )

        assert result is not None
        assert result.is_stub is True
        assert "non-operational" in result.message.lower()
        assert result.query_type == "vehicle"

    def test_query_person_stub(self):
        """Test person query stub."""
        from app.federal.ncic import ncic_query_manager

        result = ncic_query_manager.query_person(
            last_name="Smith",
            first_name="John",
            date_of_birth="1990-01-15",
            agency_id="FL0000000",
            user_id="user-001",
            user_name="Test User",
        )

        assert result is not None
        assert result.is_stub is True
        assert "non-operational" in result.message.lower()
        assert result.query_type == "person"

    def test_query_gun_stub(self):
        """Test gun query stub."""
        from app.federal.ncic import ncic_query_manager

        result = ncic_query_manager.query_gun(
            serial_number="ABC123456",
            make="Glock",
            model="17",
            agency_id="FL0000000",
            user_id="user-001",
            user_name="Test User",
        )

        assert result is not None
        assert result.is_stub is True
        assert "non-operational" in result.message.lower()
        assert result.query_type == "gun"

    def test_get_readiness_status(self):
        """Test readiness status."""
        from app.federal.ncic import ncic_query_manager

        status = ncic_query_manager.get_readiness_status()

        assert status is not None
        assert status["status"] == "stub"
        assert status["operational"] is False


class TestNCICQueryValidation:
    """Tests for NCIC query validation."""

    def test_vehicle_query_validation_vin(self):
        """Test vehicle query validation with VIN."""
        from app.federal.ncic import NCICVehicleQuery

        query = NCICVehicleQuery(
            vin="1HGBH41JXMN109186",
            agency_id="FL0000000",
        )

        validation = query.validate()
        assert validation.is_valid is True

    def test_vehicle_query_validation_plate(self):
        """Test vehicle query validation with plate."""
        from app.federal.ncic import NCICVehicleQuery

        query = NCICVehicleQuery(
            license_plate="ABC123",
            license_state="FL",
            agency_id="FL0000000",
        )

        validation = query.validate()
        assert validation.is_valid is True

    def test_vehicle_query_validation_no_params(self):
        """Test vehicle query validation with no params."""
        from app.federal.ncic import NCICVehicleQuery

        query = NCICVehicleQuery(agency_id="FL0000000")

        validation = query.validate()
        assert validation.is_valid is False
        assert len(validation.errors) > 0

    def test_person_query_validation_name_dob(self):
        """Test person query validation with name and DOB."""
        from app.federal.ncic import NCICPersonQuery

        query = NCICPersonQuery(
            last_name="Smith",
            first_name="John",
            date_of_birth="1990-01-15",
            agency_id="FL0000000",
        )

        validation = query.validate()
        assert validation.is_valid is True

    def test_person_query_validation_dl(self):
        """Test person query validation with driver's license."""
        from app.federal.ncic import NCICPersonQuery

        query = NCICPersonQuery(
            drivers_license="D123456789",
            drivers_license_state="FL",
            agency_id="FL0000000",
        )

        validation = query.validate()
        assert validation.is_valid is True

    def test_gun_query_validation(self):
        """Test gun query validation."""
        from app.federal.ncic import NCICGunQuery

        query = NCICGunQuery(
            serial_number="ABC123456",
            agency_id="FL0000000",
        )

        validation = query.validate()
        assert validation.is_valid is True

    def test_gun_query_validation_no_serial(self):
        """Test gun query validation without serial number."""
        from app.federal.ncic import NCICGunQuery

        query = NCICGunQuery(
            make="Glock",
            model="17",
            agency_id="FL0000000",
        )

        validation = query.validate()
        assert validation.is_valid is False


class TestNCICMessageFormatting:
    """Tests for NCIC message formatting."""

    def test_format_vehicle_query(self):
        """Test vehicle query message formatting."""
        from app.federal.ncic import NCICVehicleQuery

        query = NCICVehicleQuery(
            vin="1HGBH41JXMN109186",
            license_plate="ABC123",
            license_state="FL",
            agency_id="FL0000000",
        )

        formatted = query.format_message()

        assert "MKE/QV" in formatted
        assert "ORI/FL0000000" in formatted
        assert "VIN/1HGBH41JXMN109186" in formatted
        assert "LIC/ABC123" in formatted
        assert "LIS/FL" in formatted

    def test_format_person_query(self):
        """Test person query message formatting."""
        from app.federal.ncic import NCICPersonQuery

        query = NCICPersonQuery(
            last_name="Smith",
            first_name="John",
            date_of_birth="1990-01-15",
            agency_id="FL0000000",
        )

        formatted = query.format_message()

        assert "MKE/QW" in formatted
        assert "ORI/FL0000000" in formatted
        assert "NAM/SMITH,JOHN" in formatted

    def test_format_gun_query(self):
        """Test gun query message formatting."""
        from app.federal.ncic import NCICGunQuery

        query = NCICGunQuery(
            serial_number="ABC123456",
            make="Glock",
            caliber="9mm",
            gun_type="pistol",
            agency_id="FL0000000",
        )

        formatted = query.format_message()

        assert "MKE/QG" in formatted
        assert "ORI/FL0000000" in formatted
        assert "SER/ABC123456" in formatted
