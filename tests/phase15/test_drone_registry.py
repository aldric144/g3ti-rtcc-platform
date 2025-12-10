"""Tests for Drone Registry Service"""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

from app.drones.registry import (
    DroneRegistryService,
    Drone,
    DroneStatus,
    DroneType,
    DroneCapability,
)


class TestDroneRegistryService:
    """Test suite for DroneRegistryService"""

    @pytest.fixture
    def registry(self):
        """Create a fresh registry for each test"""
        return DroneRegistryService()

    @pytest.fixture
    def sample_drone(self):
        """Create a sample drone for testing"""
        return Drone(
            drone_id="drone-001",
            call_sign="EAGLE-1",
            drone_type=DroneType.SURVEILLANCE,
            status=DroneStatus.STANDBY,
            capabilities=[
                DroneCapability.HD_CAMERA,
                DroneCapability.THERMAL_CAMERA,
                DroneCapability.GPS_RTK,
            ],
            latitude=33.749,
            longitude=-84.388,
            altitude_m=0,
            battery_percent=100,
            max_altitude_m=400,
            max_speed_mps=20,
            max_flight_time_minutes=45,
        )

    def test_register_drone(self, registry, sample_drone):
        """Test drone registration"""
        result = registry.register_drone(sample_drone)
        assert result is True
        assert sample_drone.drone_id in registry._drones

    def test_register_duplicate_drone(self, registry, sample_drone):
        """Test that duplicate registration fails"""
        registry.register_drone(sample_drone)
        result = registry.register_drone(sample_drone)
        assert result is False

    def test_unregister_drone(self, registry, sample_drone):
        """Test drone unregistration"""
        registry.register_drone(sample_drone)
        result = registry.unregister_drone(sample_drone.drone_id)
        assert result is True
        assert sample_drone.drone_id not in registry._drones

    def test_unregister_nonexistent_drone(self, registry):
        """Test unregistering a drone that doesn't exist"""
        result = registry.unregister_drone("nonexistent")
        assert result is False

    def test_get_drone(self, registry, sample_drone):
        """Test getting a drone by ID"""
        registry.register_drone(sample_drone)
        drone = registry.get_drone(sample_drone.drone_id)
        assert drone is not None
        assert drone.drone_id == sample_drone.drone_id
        assert drone.call_sign == sample_drone.call_sign

    def test_get_nonexistent_drone(self, registry):
        """Test getting a drone that doesn't exist"""
        drone = registry.get_drone("nonexistent")
        assert drone is None

    def test_get_all_drones(self, registry, sample_drone):
        """Test getting all drones"""
        registry.register_drone(sample_drone)
        drones = registry.get_all_drones()
        assert len(drones) == 1
        assert drones[0].drone_id == sample_drone.drone_id

    def test_get_drones_by_status(self, registry, sample_drone):
        """Test filtering drones by status"""
        registry.register_drone(sample_drone)
        standby_drones = registry.get_drones_by_status(DroneStatus.STANDBY)
        assert len(standby_drones) == 1
        
        airborne_drones = registry.get_drones_by_status(DroneStatus.AIRBORNE)
        assert len(airborne_drones) == 0

    def test_get_drones_by_type(self, registry, sample_drone):
        """Test filtering drones by type"""
        registry.register_drone(sample_drone)
        surveillance_drones = registry.get_drones_by_type(DroneType.SURVEILLANCE)
        assert len(surveillance_drones) == 1
        
        tactical_drones = registry.get_drones_by_type(DroneType.TACTICAL)
        assert len(tactical_drones) == 0

    def test_get_available_drones(self, registry, sample_drone):
        """Test getting available drones"""
        registry.register_drone(sample_drone)
        available = registry.get_available_drones()
        assert len(available) == 1

    def test_get_drones_with_capability(self, registry, sample_drone):
        """Test filtering drones by capability"""
        registry.register_drone(sample_drone)
        thermal_drones = registry.get_drones_with_capability(DroneCapability.THERMAL_CAMERA)
        assert len(thermal_drones) == 1
        
        lpr_drones = registry.get_drones_with_capability(DroneCapability.LPR_CAMERA)
        assert len(lpr_drones) == 0

    def test_update_status(self, registry, sample_drone):
        """Test updating drone status"""
        registry.register_drone(sample_drone)
        result = registry.update_status(sample_drone.drone_id, DroneStatus.AIRBORNE)
        assert result is True
        
        drone = registry.get_drone(sample_drone.drone_id)
        assert drone.status == DroneStatus.AIRBORNE

    def test_update_position(self, registry, sample_drone):
        """Test updating drone position"""
        registry.register_drone(sample_drone)
        result = registry.update_position(
            sample_drone.drone_id,
            latitude=33.750,
            longitude=-84.390,
            altitude_m=100,
            heading_deg=45,
            speed_mps=15,
        )
        assert result is True
        
        drone = registry.get_drone(sample_drone.drone_id)
        assert drone.latitude == 33.750
        assert drone.longitude == -84.390
        assert drone.altitude_m == 100

    def test_update_battery(self, registry, sample_drone):
        """Test updating drone battery"""
        registry.register_drone(sample_drone)
        result = registry.update_battery(sample_drone.drone_id, 75)
        assert result is True
        
        drone = registry.get_drone(sample_drone.drone_id)
        assert drone.battery_percent == 75

    def test_assign_mission(self, registry, sample_drone):
        """Test assigning a mission to a drone"""
        registry.register_drone(sample_drone)
        result = registry.assign_mission(sample_drone.drone_id, "mission-001")
        assert result is True
        
        drone = registry.get_drone(sample_drone.drone_id)
        assert drone.current_mission_id == "mission-001"

    def test_clear_mission(self, registry, sample_drone):
        """Test clearing a mission from a drone"""
        registry.register_drone(sample_drone)
        registry.assign_mission(sample_drone.drone_id, "mission-001")
        result = registry.clear_mission(sample_drone.drone_id)
        assert result is True
        
        drone = registry.get_drone(sample_drone.drone_id)
        assert drone.current_mission_id is None

    def test_get_metrics(self, registry, sample_drone):
        """Test getting registry metrics"""
        registry.register_drone(sample_drone)
        metrics = registry.get_metrics()
        assert metrics.total_drones == 1
        assert metrics.drones_by_status[DroneStatus.STANDBY] == 1

    def test_callback_registration(self, registry, sample_drone):
        """Test callback registration and invocation"""
        callback = MagicMock()
        registry.register_callback("drone_registered", callback)
        registry.register_drone(sample_drone)
        callback.assert_called_once()
