"""
Tests for RBPD Mock Camera Loader.
"""

import pytest

from app.camera_network.rbpd_mock_loader import (
    load_rbpd_mock_cameras,
    get_rbpd_camera_count,
    get_rbpd_cameras_by_sector,
    get_rbpd_cameras_by_type,
    get_rbpd_camera_stats,
    ALL_RBPD_CAMERAS,
)


class TestRBPDMockLoader:
    """Test suite for RBPD Mock Camera Loader."""
    
    def test_load_all_cameras(self):
        """Test loading all RBPD mock cameras."""
        cameras = load_rbpd_mock_cameras()
        
        assert len(cameras) > 0
        assert len(cameras) >= 25  # At least 25 cameras as specified
    
    def test_camera_count(self):
        """Test camera count function."""
        count = get_rbpd_camera_count()
        cameras = load_rbpd_mock_cameras()
        
        assert count == len(ALL_RBPD_CAMERAS)
        assert count == len(cameras)
    
    def test_camera_structure(self):
        """Test that cameras have required fields."""
        cameras = load_rbpd_mock_cameras()
        
        for cam in cameras:
            assert "id" in cam
            assert "name" in cam
            assert "latitude" in cam
            assert "longitude" in cam
            assert "stream_url" in cam
            assert "camera_type" in cam
            assert "jurisdiction" in cam
            assert "sector" in cam
            assert "status" in cam
    
    def test_camera_ids_unique(self):
        """Test that all camera IDs are unique."""
        cameras = load_rbpd_mock_cameras()
        ids = [cam["id"] for cam in cameras]
        
        assert len(ids) == len(set(ids))
    
    def test_jurisdiction_is_rbpd(self):
        """Test that all cameras have RBPD jurisdiction."""
        cameras = load_rbpd_mock_cameras()
        
        for cam in cameras:
            assert cam["jurisdiction"] == "RBPD"
    
    def test_source_priority(self):
        """Test that RBPD cameras have highest priority."""
        cameras = load_rbpd_mock_cameras()
        
        for cam in cameras:
            assert cam["source_priority"] == 100
    
    def test_get_cameras_by_sector(self):
        """Test filtering cameras by sector."""
        cameras = load_rbpd_mock_cameras()
        sectors = set(cam["sector"] for cam in cameras)
        
        for sector in sectors:
            sector_cameras = get_rbpd_cameras_by_sector(sector)
            assert len(sector_cameras) > 0
            for cam in sector_cameras:
                assert cam["sector"] == sector
    
    def test_get_cameras_by_type(self):
        """Test filtering cameras by type."""
        cameras = load_rbpd_mock_cameras()
        types = set(cam["camera_type"] for cam in cameras)
        
        for cam_type in types:
            type_cameras = get_rbpd_cameras_by_type(cam_type)
            assert len(type_cameras) > 0
            for cam in type_cameras:
                assert cam["camera_type"] == cam_type
    
    def test_camera_types_valid(self):
        """Test that camera types are valid."""
        cameras = load_rbpd_mock_cameras()
        valid_types = {"cctv", "ptz", "lpr"}
        
        for cam in cameras:
            assert cam["camera_type"] in valid_types
    
    def test_get_stats(self):
        """Test getting camera statistics."""
        stats = get_rbpd_camera_stats()
        
        assert "total_cameras" in stats
        assert "by_sector" in stats
        assert "by_type" in stats
        assert "jurisdiction" in stats
        assert stats["jurisdiction"] == "RBPD"
        assert stats["total_cameras"] >= 25
    
    def test_coordinates_in_riviera_beach(self):
        """Test that coordinates are in Riviera Beach area."""
        cameras = load_rbpd_mock_cameras()
        
        for cam in cameras:
            lat = cam["latitude"]
            lng = cam["longitude"]
            
            # Riviera Beach area bounds
            assert 26.7 < lat < 26.9
            assert -80.2 < lng < -80.0
    
    def test_hq_cameras_exist(self):
        """Test that RBPD HQ cameras exist."""
        cameras = load_rbpd_mock_cameras()
        hq_cameras = [c for c in cameras if "HQ" in c["name"]]
        
        assert len(hq_cameras) >= 4  # At least 4 HQ cameras
