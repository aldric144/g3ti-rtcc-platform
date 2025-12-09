"""
Unit tests for N-DEx Data Exchange module.
"""



class TestNDExDataMapper:
    """Tests for NDExDataMapper class."""

    def test_map_person_basic(self):
        """Test basic person mapping."""
        from app.federal.ndex import NDExDataMapper, NDExRoleType

        mapper = NDExDataMapper()
        person_data = {
            "id": "person-123",
            "last_name": "Smith",
            "first_name": "John",
            "middle_name": "William",
            "date_of_birth": "1990-01-15",
            "sex": "M",
            "race": "W",
        }

        result = mapper.map_person(person_data, NDExRoleType.SUBJECT)

        assert result is not None
        assert result["entity_type"] == "Person"
        assert result["role_type"] == "Subject"
        assert result["name"]["last_name"] == "SMITH"
        assert result["name"]["first_name"] == "JOHN"

    def test_map_person_with_sensitive_fields(self):
        """Test person mapping with sensitive field masking."""
        from app.federal.ndex import NDExDataMapper, NDExRoleType

        mapper = NDExDataMapper()
        person_data = {
            "id": "person-123",
            "last_name": "Smith",
            "first_name": "John",
            "date_of_birth": "1990-01-15",
            "ssn": "123-45-6789",
            "drivers_license": "D123456789",
        }

        result = mapper.map_person(person_data, NDExRoleType.SUBJECT)

        # Sensitive fields should be masked
        assert "ssn" not in result.get("identifiers", {}) or "***" in str(
            result["identifiers"].get("ssn", "")
        )

    def test_map_incident_basic(self):
        """Test basic incident mapping."""
        from app.federal.ndex import NDExDataMapper

        mapper = NDExDataMapper()
        incident_data = {
            "id": "incident-123",
            "incident_number": "2024-00001234",
            "incident_date": "2024-01-15",
            "incident_time": "14:30:00",
            "incident_type": "Criminal",
            "status": "Active",
            "reporting_agency_ori": "FL0000000",
        }

        result = mapper.map_incident(incident_data)

        assert result is not None
        assert result["entity_type"] == "Incident"
        assert result["incident_number"] == "2024-00001234"

    def test_map_vehicle(self):
        """Test vehicle mapping."""
        from app.federal.ndex import NDExDataMapper

        mapper = NDExDataMapper()
        vehicle_data = {
            "id": "vehicle-123",
            "vin": "1HGBH41JXMN109186",
            "license_plate": "ABC123",
            "license_state": "FL",
            "make": "Toyota",
            "model": "Camry",
            "year": "2020",
            "color": "Black",
        }

        result = mapper.map_vehicle(vehicle_data)

        assert result is not None
        assert result["entity_type"] == "Vehicle"
        assert result["make"] == "TOYOTA"

    def test_map_firearm(self):
        """Test firearm mapping."""
        from app.federal.ndex import NDExDataMapper

        mapper = NDExDataMapper()
        firearm_data = {
            "id": "firearm-123",
            "serial_number": "ABC123456",
            "make": "Glock",
            "model": "17",
            "caliber": "9mm",
            "firearm_type": "pistol",
        }

        result = mapper.map_firearm(firearm_data)

        assert result is not None
        assert result["entity_type"] == "Firearm"
        assert result["ncic_gun_type"] == "P"  # Pistol

    def test_normalize_offense_code(self):
        """Test NIBRS offense code normalization."""
        from app.federal.ndex import NDExDataMapper

        mapper = NDExDataMapper()

        # Test known offense codes
        assert mapper.normalize_offense_code("13A") == "13A"
        assert mapper.normalize_offense_code("aggravated assault") == "13A"
        assert mapper.normalize_offense_code("burglary") == "220"


class TestNDExExportManager:
    """Tests for NDExExportManager class."""

    def test_export_person(self):
        """Test person export."""
        from app.federal.ndex import NDExRoleType, ndex_export_manager

        person_data = {
            "id": "person-123",
            "last_name": "Smith",
            "first_name": "John",
        }

        package = ndex_export_manager.export_person(
            person_data=person_data,
            role_type=NDExRoleType.SUBJECT,
            agency_id="FL0000000",
            user_id="user-001",
            user_name="Test User",
        )

        assert package is not None
        assert package.export_type == "person"
        assert package.status == "ready"

    def test_export_incident(self):
        """Test incident export."""
        from app.federal.ndex import ndex_export_manager

        incident_data = {
            "id": "incident-123",
            "incident_number": "2024-00001234",
            "incident_date": "2024-01-15",
            "reporting_agency_ori": "FL0000000",
        }

        package = ndex_export_manager.export_incident(
            incident_data=incident_data,
            agency_id="FL0000000",
            user_id="user-001",
            user_name="Test User",
        )

        assert package is not None
        assert package.export_type == "incident"
        assert package.status == "ready"

    def test_validate_export(self):
        """Test export validation."""
        from app.federal.ndex import NDExRoleType, ndex_export_manager

        person_data = {
            "id": "person-123",
            "last_name": "Smith",
            "first_name": "John",
        }

        package = ndex_export_manager.export_person(
            person_data=person_data,
            role_type=NDExRoleType.SUBJECT,
            agency_id="FL0000000",
            user_id="user-001",
            user_name="Test User",
        )

        validation = ndex_export_manager.validate_export(package.id)

        assert validation is not None
        assert validation.is_valid is True

    def test_get_exports_by_agency(self):
        """Test getting exports by agency."""
        from app.federal.ndex import ndex_export_manager

        exports = ndex_export_manager.get_exports_by_agency("FL0000000")

        assert isinstance(exports, list)


class TestNDExSchemas:
    """Tests for N-DEx schema classes."""

    def test_person_schema(self):
        """Test NDExPersonSchema."""
        from app.federal.ndex import NDExPersonSchema

        schema = NDExPersonSchema()

        assert schema.schema_name == "NDEx_Person_v5"
        assert schema.schema_version == "5.0"
        assert "last_name" in schema.required_fields
        assert "ssn" in schema.sensitive_fields

    def test_incident_schema(self):
        """Test NDExIncidentSchema."""
        from app.federal.ndex import NDExIncidentSchema

        schema = NDExIncidentSchema()

        assert schema.schema_name == "NDEx_Incident_v5"
        assert "incident_id" in schema.required_fields

    def test_vehicle_schema(self):
        """Test NDExVehicleSchema."""
        from app.federal.ndex import NDExVehicleSchema

        schema = NDExVehicleSchema()

        assert schema.schema_name == "NDEx_Vehicle_v5"
        assert "vin" in schema.sensitive_fields

    def test_firearm_schema(self):
        """Test NDExFirearmSchema."""
        from app.federal.ndex import NDExFirearmSchema

        schema = NDExFirearmSchema()

        assert schema.schema_name == "NDEx_Firearm_v5"
        assert "serial_number" in schema.sensitive_fields
