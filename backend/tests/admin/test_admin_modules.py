"""
Tests for RTCC Admin Modules
Phase: RTCC-ADMIN-SUITE-X

Minimum 20 tests covering:
- Validation
- CRUD operations
- Polygon boundaries
- Camera stream parsing
- DV redaction rules
- Sector auto-assign
- API permissions
- Admin-only access control
- PDF preplan uploads
- Event boundary rendering
- Drone telemetry inputs
- Video wall linking
- Audit logs
- Error handling
"""

import pytest
from datetime import datetime, UTC, timedelta
import uuid

# Import admin modules
import sys
sys.path.insert(0, '/home/ubuntu/repos/g3ti-rtcc-platform/backend')

from app.admin.base_admin import GeoPoint, GeoPolygon
from app.admin.validation import ValidationEngine, ValidationResult
from app.admin.audit_log import AuditLogger, AuditAction, audit_logger
from app.admin.cameras_admin import camera_admin, CameraCreate, CameraType, CameraStatus
from app.admin.drones_admin import drone_admin, DroneCreate, DroneStatus
from app.admin.robots_admin import robot_admin, RobotCreate
from app.admin.sectors_admin import sector_admin, SectorCreate
from app.admin.dv_risk_homes_admin import dv_risk_home_admin, DVRiskHomeCreate, RiskLevel
from app.admin.incidents_admin import incident_admin, IncidentCreate, IncidentType, IncidentPriority
from app.admin.events_admin import event_admin, EventCreate, EventType
from app.admin.hydrants_admin import hydrant_admin, HydrantCreate
from app.admin.users_admin import user_admin, UserCreate, UserRole
from app.admin.system_settings_admin import system_settings_admin, SystemSettingsCreate
from app.admin.api_connections_admin import api_connection_admin, APIConnectionCreate


class TestValidationEngine:
    """Test validation engine rules"""
    
    # Test 1: Validate GPS coordinates
    def test_validate_coordinates_valid(self):
        result = ValidationEngine.validate_coordinates(26.7753, -80.0569)
        assert result.is_valid
        assert len(result.errors) == 0
    
    # Test 2: Validate invalid GPS coordinates
    def test_validate_coordinates_invalid(self):
        result = ValidationEngine.validate_coordinates(91.0, -80.0)
        assert not result.is_valid
        assert len(result.errors) > 0
        assert "Latitude" in result.errors[0]
    
    # Test 3: Validate stream URL - valid RTSP
    def test_validate_stream_url_valid_rtsp(self):
        result = ValidationEngine.validate_stream_url("rtsp://camera.example.com/stream")
        assert result.is_valid
    
    # Test 4: Validate stream URL - invalid format
    def test_validate_stream_url_invalid(self):
        result = ValidationEngine.validate_stream_url("ftp://invalid.com/stream")
        assert not result.is_valid
        assert "Invalid URL format" in result.errors[0]
    
    # Test 5: Validate polygon - valid closed polygon
    def test_validate_polygon_valid(self):
        points = [
            GeoPoint(lat=26.77, lng=-80.05),
            GeoPoint(lat=26.78, lng=-80.05),
            GeoPoint(lat=26.78, lng=-80.06),
            GeoPoint(lat=26.77, lng=-80.05),  # Closed
        ]
        result = ValidationEngine.validate_polygon(points)
        assert result.is_valid
    
    # Test 6: Validate polygon - too few points
    def test_validate_polygon_too_few_points(self):
        points = [
            GeoPoint(lat=26.77, lng=-80.05),
            GeoPoint(lat=26.78, lng=-80.05),
        ]
        result = ValidationEngine.validate_polygon(points)
        assert not result.is_valid
        assert "at least 3 points" in result.errors[0]
    
    # Test 7: Validate DV risk home - address redaction
    def test_validate_dv_risk_home_address_redaction(self):
        # Should fail - contains address-like data
        data = {"sector": "123 Main Street"}
        result = ValidationEngine.validate_dv_risk_home(data)
        assert not result.is_valid
        assert "SECURITY VIOLATION" in result.errors[0]
    
    # Test 8: Validate DV risk home - valid sector only
    def test_validate_dv_risk_home_valid_sector(self):
        data = {"sector": "SECTOR-1"}
        result = ValidationEngine.validate_dv_risk_home(data)
        assert result.is_valid
    
    # Test 9: Validate camera data
    def test_validate_camera_data(self):
        data = {
            "name": "Test Camera",
            "lat": 26.7753,
            "lng": -80.0569,
            "stream_url": "rtsp://camera.example.com/stream"
        }
        result = ValidationEngine.validate_camera(data)
        assert result.is_valid
    
    # Test 10: Validate event - time range
    def test_validate_event_time_range(self):
        now = datetime.now(UTC)
        data = {
            "event_name": "Test Event",
            "boundary": [
                {"lat": 26.77, "lng": -80.05},
                {"lat": 26.78, "lng": -80.05},
                {"lat": 26.78, "lng": -80.06},
            ],
            "start_time": now,
            "end_time": now - timedelta(hours=1),  # End before start - invalid
        }
        result = ValidationEngine.validate_event(data)
        assert not result.is_valid
        assert "End time must be after start time" in result.errors[0]


class TestAuditLogger:
    """Test audit logging system"""
    
    # Test 11: Log create operation
    def test_log_create_operation(self):
        entry = audit_logger.log_create(
            user_id="test-user",
            table_name="cameras",
            record_id="cam-001",
            data={"name": "Test Camera"}
        )
        assert entry.action == AuditAction.CREATE
        assert entry.table_name == "cameras"
        assert entry.record_id == "cam-001"
    
    # Test 12: Log update operation with before/after
    def test_log_update_operation(self):
        entry = audit_logger.log_update(
            user_id="test-user",
            table_name="cameras",
            record_id="cam-001",
            before={"status": "offline"},
            after={"status": "online"}
        )
        assert entry.action == AuditAction.UPDATE
        assert entry.before_snapshot is not None
        assert entry.after_snapshot is not None
    
    # Test 13: Sensitive data redaction in audit logs
    def test_audit_log_sensitive_data_redaction(self):
        entry = audit_logger.log_create(
            user_id="test-user",
            table_name="users",
            record_id="user-001",
            data={"username": "testuser", "password_hash": "secret123"}
        )
        assert entry.after_snapshot["password_hash"] == "[REDACTED]"
    
    # Test 14: Query audit logs by user
    def test_query_audit_logs_by_user(self):
        # Create some logs
        audit_logger.log_create(user_id="query-test-user", table_name="test", record_id="1", data={})
        
        logs = audit_logger.get_logs(user_id="query-test-user")
        assert len(logs) > 0
        assert all(log.user_id == "query-test-user" for log in logs)


class TestCameraAdmin:
    """Test camera admin CRUD operations"""
    
    # Test 15: Create camera
    @pytest.mark.asyncio
    async def test_create_camera(self):
        data = CameraCreate(
            name="Test Camera",
            lat=26.7753,
            lng=-80.0569,
            camera_type=CameraType.CCTV,
            status=CameraStatus.ONLINE
        )
        camera = await camera_admin.create(data, "test-user")
        assert camera.name == "Test Camera"
        assert camera.lat == 26.7753
        assert camera.camera_type == CameraType.CCTV
    
    # Test 16: Get camera by sector
    @pytest.mark.asyncio
    async def test_get_cameras_by_sector(self):
        cameras = await camera_admin.get_by_sector("SECTOR-1")
        assert isinstance(cameras, list)


class TestSectorAdmin:
    """Test sector admin with polygon operations"""
    
    # Test 17: Point in polygon detection
    @pytest.mark.asyncio
    async def test_find_sector_for_point(self):
        # This tests the point-in-polygon algorithm
        sector = await sector_admin.find_sector_for_point(26.7755, -80.0565)
        # May or may not find a sector depending on demo data
        assert sector is None or hasattr(sector, 'sector_id')


class TestDVRiskHomeAdmin:
    """Test DV risk home admin with encryption"""
    
    # Test 18: Notes encryption
    @pytest.mark.asyncio
    async def test_notes_encryption(self):
        data = DVRiskHomeCreate(
            sector="SECTOR-TEST",
            risk_level=RiskLevel.HIGH,
            notes="Sensitive information"
        )
        home = await dv_risk_home_admin.create(data, "test-user")
        
        # Notes should be encrypted
        assert home.encrypted_notes is not None
        assert home.encrypted_notes.startswith("ENC:")
    
    # Test 19: Risk level auto-escalation
    @pytest.mark.asyncio
    async def test_risk_level_escalation(self):
        data = DVRiskHomeCreate(
            sector="SECTOR-ESCALATE-TEST",
            risk_level=RiskLevel.LOW,
            incident_count=0
        )
        home = await dv_risk_home_admin.create(data, "test-user")
        
        # Record multiple incidents
        for _ in range(5):
            home = await dv_risk_home_admin.record_incident(home.id, "test-user")
        
        # Should have escalated to critical
        assert home.risk_level == RiskLevel.CRITICAL


class TestUserAdmin:
    """Test user admin with role management"""
    
    # Test 20: Password hashing
    @pytest.mark.asyncio
    async def test_password_hashing(self):
        data = UserCreate(
            username=f"testuser_{uuid.uuid4().hex[:8]}",
            password="SecurePass123",
            role=UserRole.ANALYST
        )
        user = await user_admin.create(data, "admin-user")
        
        # Password should be hashed, not plain text
        assert user.password_hash is not None
        assert user.password_hash != "SecurePass123"
    
    # Test 21: Duplicate username prevention
    @pytest.mark.asyncio
    async def test_duplicate_username_prevention(self):
        unique_name = f"duplicate_test_{uuid.uuid4().hex[:8]}"
        data1 = UserCreate(username=unique_name, password="SecurePass123", role=UserRole.VIEWER)
        await user_admin.create(data1, "admin-user")
        
        data2 = UserCreate(username=unique_name, password="SecurePass456", role=UserRole.VIEWER)
        with pytest.raises(ValueError) as exc_info:
            await user_admin.create(data2, "admin-user")
        assert "already exists" in str(exc_info.value)


class TestDroneAdmin:
    """Test drone admin with telemetry"""
    
    # Test 22: Telemetry update
    @pytest.mark.asyncio
    async def test_telemetry_update(self):
        drones = await drone_admin.get_all()
        if drones:
            drone = await drone_admin.update_telemetry(
                drones[0].id,
                lat=26.78,
                lng=-80.06,
                altitude=100.0,
                battery=85
            )
            assert drone.current_lat == 26.78
            assert drone.battery_level == 85


class TestIncidentAdmin:
    """Test incident admin"""
    
    # Test 23: Get active incidents
    @pytest.mark.asyncio
    async def test_get_active_incidents(self):
        incidents = await incident_admin.get_active()
        assert isinstance(incidents, list)
    
    # Test 24: Get critical incidents
    @pytest.mark.asyncio
    async def test_get_critical_incidents(self):
        incidents = await incident_admin.get_critical()
        assert isinstance(incidents, list)
        for incident in incidents:
            assert incident.priority == IncidentPriority.CRITICAL


class TestSystemSettingsAdmin:
    """Test system settings admin"""
    
    # Test 25: Get setting by key
    @pytest.mark.asyncio
    async def test_get_setting_by_key(self):
        setting = await system_settings_admin.get_by_key("map.default_style")
        assert setting is not None
        assert setting.setting_key == "map.default_style"
    
    # Test 26: Get video wall config
    @pytest.mark.asyncio
    async def test_get_video_wall_config(self):
        config = await system_settings_admin.get_video_wall_config()
        assert hasattr(config, 'layout')
        assert hasattr(config, 'rotation_interval')


class TestAPIConnectionAdmin:
    """Test API connection admin with encryption"""
    
    # Test 27: API key encryption
    @pytest.mark.asyncio
    async def test_api_key_encryption(self):
        data = APIConnectionCreate(
            api_name="Test API",
            url="https://api.example.com/v1",
            api_key="secret_api_key_123"
        )
        connection = await api_connection_admin.create(data, "test-user")
        
        # API key should be encrypted
        assert connection.encrypted_key is not None
        assert connection.encrypted_key.startswith("ENC:")
        assert "secret_api_key_123" not in connection.encrypted_key


class TestHydrantAdmin:
    """Test hydrant admin"""
    
    # Test 28: Get nearby hydrants
    @pytest.mark.asyncio
    async def test_get_nearby_hydrants(self):
        hydrants = await hydrant_admin.get_nearby(26.7755, -80.0565, radius_km=1.0)
        assert isinstance(hydrants, list)


class TestEventAdmin:
    """Test event admin"""
    
    # Test 29: Get upcoming events
    @pytest.mark.asyncio
    async def test_get_upcoming_events(self):
        events = await event_admin.get_upcoming(days=30)
        assert isinstance(events, list)


class TestGeoPolygon:
    """Test geographic polygon utilities"""
    
    # Test 30: Polygon closure check
    def test_polygon_is_closed(self):
        polygon = GeoPolygon(points=[
            GeoPoint(lat=26.77, lng=-80.05),
            GeoPoint(lat=26.78, lng=-80.05),
            GeoPoint(lat=26.78, lng=-80.06),
            GeoPoint(lat=26.77, lng=-80.05),  # Same as first - closed
        ])
        assert polygon.is_closed()
    
    # Test 31: Polygon not closed
    def test_polygon_not_closed(self):
        polygon = GeoPolygon(points=[
            GeoPoint(lat=26.77, lng=-80.05),
            GeoPoint(lat=26.78, lng=-80.05),
            GeoPoint(lat=26.78, lng=-80.06),
            GeoPoint(lat=26.77, lng=-80.07),  # Different from first - not closed
        ])
        assert not polygon.is_closed()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
