"""
Tests for Camera Registry CRUD operations.
"""

import pytest
from datetime import datetime

from app.camera_network.camera_registry import (
    CameraRegistry,
    Camera,
    CameraType,
    CameraJurisdiction,
    CameraStatus,
    get_camera_registry,
)


class TestCameraRegistry:
    """Test suite for CameraRegistry class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.registry = CameraRegistry()
        self.registry.clear()
    
    def test_add_camera(self):
        """Test adding a camera to the registry."""
        camera = Camera(
            id="test-001",
            name="Test Camera",
            latitude=26.7841,
            longitude=-80.0722,
            stream_url="https://example.com/stream",
            camera_type=CameraType.CCTV,
            jurisdiction=CameraJurisdiction.RBPD,
        )
        
        result = self.registry.add_camera(camera)
        
        assert result.id == "test-001"
        assert result.name == "Test Camera"
        assert self.registry.count() == 1
    
    def test_get_camera(self):
        """Test retrieving a camera by ID."""
        camera = Camera(
            id="test-002",
            name="Test Camera 2",
            latitude=26.7841,
            longitude=-80.0722,
            stream_url="https://example.com/stream",
            camera_type=CameraType.PTZ,
            jurisdiction=CameraJurisdiction.FDOT,
        )
        
        self.registry.add_camera(camera)
        result = self.registry.get_camera("test-002")
        
        assert result is not None
        assert result.name == "Test Camera 2"
        assert result.camera_type == CameraType.PTZ
    
    def test_get_camera_not_found(self):
        """Test retrieving a non-existent camera."""
        result = self.registry.get_camera("non-existent")
        assert result is None
    
    def test_update_camera(self):
        """Test updating a camera."""
        camera = Camera(
            id="test-003",
            name="Original Name",
            latitude=26.7841,
            longitude=-80.0722,
            stream_url="https://example.com/stream",
            camera_type=CameraType.CCTV,
            jurisdiction=CameraJurisdiction.RBPD,
        )
        
        self.registry.add_camera(camera)
        result = self.registry.update_camera("test-003", {"name": "Updated Name"})
        
        assert result is not None
        assert result.name == "Updated Name"
    
    def test_delete_camera(self):
        """Test deleting a camera."""
        camera = Camera(
            id="test-004",
            name="To Delete",
            latitude=26.7841,
            longitude=-80.0722,
            stream_url="https://example.com/stream",
            camera_type=CameraType.CCTV,
            jurisdiction=CameraJurisdiction.RBPD,
        )
        
        self.registry.add_camera(camera)
        assert self.registry.count() == 1
        
        result = self.registry.delete_camera("test-004")
        
        assert result is True
        assert self.registry.count() == 0
    
    def test_list_by_jurisdiction(self):
        """Test filtering cameras by jurisdiction."""
        cameras = [
            Camera(
                id=f"test-{i}",
                name=f"Camera {i}",
                latitude=26.7841,
                longitude=-80.0722,
                stream_url="https://example.com/stream",
                camera_type=CameraType.CCTV,
                jurisdiction=CameraJurisdiction.RBPD if i % 2 == 0 else CameraJurisdiction.FDOT,
            )
            for i in range(10)
        ]
        
        for cam in cameras:
            self.registry.add_camera(cam)
        
        rbpd_cameras = self.registry.list_by_jurisdiction("RBPD")
        fdot_cameras = self.registry.list_by_jurisdiction("FDOT")
        
        assert len(rbpd_cameras) == 5
        assert len(fdot_cameras) == 5
    
    def test_list_by_type(self):
        """Test filtering cameras by type."""
        camera1 = Camera(
            id="ptz-001",
            name="PTZ Camera",
            latitude=26.7841,
            longitude=-80.0722,
            stream_url="https://example.com/stream",
            camera_type=CameraType.PTZ,
            jurisdiction=CameraJurisdiction.RBPD,
        )
        camera2 = Camera(
            id="lpr-001",
            name="LPR Camera",
            latitude=26.7841,
            longitude=-80.0722,
            stream_url="https://example.com/stream",
            camera_type=CameraType.LPR,
            jurisdiction=CameraJurisdiction.RBPD,
        )
        
        self.registry.add_camera(camera1)
        self.registry.add_camera(camera2)
        
        ptz_cameras = self.registry.list_by_type("ptz")
        lpr_cameras = self.registry.list_by_type("lpr")
        
        assert len(ptz_cameras) == 1
        assert len(lpr_cameras) == 1
    
    def test_list_nearby(self):
        """Test finding cameras within radius."""
        # Add cameras at different distances
        cameras = [
            Camera(
                id="near-001",
                name="Near Camera",
                latitude=26.7841,
                longitude=-80.0722,
                stream_url="https://example.com/stream",
                camera_type=CameraType.CCTV,
                jurisdiction=CameraJurisdiction.RBPD,
            ),
            Camera(
                id="far-001",
                name="Far Camera",
                latitude=27.0000,  # ~24km away
                longitude=-80.0722,
                stream_url="https://example.com/stream",
                camera_type=CameraType.CCTV,
                jurisdiction=CameraJurisdiction.RBPD,
            ),
        ]
        
        for cam in cameras:
            self.registry.add_camera(cam)
        
        nearby = self.registry.list_nearby(26.7841, -80.0722, radius_km=5.0)
        
        assert len(nearby) == 1
        assert nearby[0]["id"] == "near-001"
    
    def test_get_stats(self):
        """Test getting registry statistics."""
        cameras = [
            Camera(
                id=f"test-{i}",
                name=f"Camera {i}",
                latitude=26.7841,
                longitude=-80.0722,
                stream_url="https://example.com/stream",
                camera_type=CameraType.CCTV,
                jurisdiction=CameraJurisdiction.RBPD,
                status=CameraStatus.ONLINE,
            )
            for i in range(5)
        ]
        
        for cam in cameras:
            self.registry.add_camera(cam)
        
        stats = self.registry.get_stats()
        
        assert stats["total_cameras"] == 5
        assert stats["online_count"] == 5
    
    def test_singleton_pattern(self):
        """Test that get_camera_registry returns singleton."""
        registry1 = get_camera_registry()
        registry2 = get_camera_registry()
        
        assert registry1 is registry2
