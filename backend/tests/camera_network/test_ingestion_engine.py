"""
Tests for Camera Ingestion Engine.
"""

import pytest

from app.camera_network.camera_ingestion_engine import (
    CameraIngestionEngine,
    get_ingestion_engine,
)
from app.camera_network.camera_registry import get_camera_registry


class TestCameraIngestionEngine:
    """Test suite for CameraIngestionEngine class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.engine = CameraIngestionEngine()
        self.engine._registry.clear()
        self.engine._manual_cameras.clear()
    
    def test_ingest_all(self):
        """Test ingesting cameras from all sources."""
        stats = self.engine.ingest_all()
        
        assert "rbpd_count" in stats
        assert "fdot_count" in stats
        assert "total_count" in stats
        assert stats["total_count"] > 0
    
    def test_priority_ordering(self):
        """Test that RBPD cameras have highest priority."""
        self.engine.ingest_all()
        cameras = self.engine.get_all_cameras()
        
        # RBPD cameras should be present
        rbpd_cameras = [c for c in cameras if c.get("jurisdiction") == "RBPD"]
        assert len(rbpd_cameras) > 0
    
    def test_add_manual_camera(self):
        """Test adding a manual camera."""
        camera_data = {
            "name": "Manual Test Camera",
            "latitude": 26.7841,
            "longitude": -80.0722,
            "stream_url": "https://example.com/stream",
            "camera_type": "cctv",
        }
        
        result = self.engine.add_manual_camera(camera_data)
        
        assert result is not None
        assert result["name"] == "Manual Test Camera"
        assert result["jurisdiction"] == "Manual"
        assert result["source_priority"] == 80
    
    def test_remove_manual_camera(self):
        """Test removing a manual camera."""
        camera_data = {
            "id": "manual-test-001",
            "name": "To Remove",
            "latitude": 26.7841,
            "longitude": -80.0722,
            "stream_url": "https://example.com/stream",
            "camera_type": "cctv",
        }
        
        self.engine.add_manual_camera(camera_data)
        result = self.engine.remove_manual_camera("manual-test-001")
        
        assert result is True
    
    def test_get_camera(self):
        """Test getting a specific camera."""
        self.engine.ingest_all()
        cameras = self.engine.get_all_cameras()
        
        if cameras:
            first_id = cameras[0]["id"]
            camera = self.engine.get_camera(first_id)
            assert camera is not None
            assert camera["id"] == first_id
    
    def test_get_cameras_by_sector(self):
        """Test filtering cameras by sector."""
        self.engine.ingest_all()
        cameras = self.engine.get_all_cameras()
        
        sectors = set(c.get("sector") for c in cameras if c.get("sector"))
        
        for sector in list(sectors)[:3]:  # Test first 3 sectors
            sector_cameras = self.engine.get_cameras_by_sector(sector)
            for cam in sector_cameras:
                assert cam.get("sector") == sector
    
    def test_get_cameras_by_jurisdiction(self):
        """Test filtering cameras by jurisdiction."""
        self.engine.ingest_all()
        
        rbpd_cameras = self.engine.get_cameras_by_jurisdiction("RBPD")
        fdot_cameras = self.engine.get_cameras_by_jurisdiction("FDOT")
        
        for cam in rbpd_cameras:
            assert cam.get("jurisdiction") == "RBPD"
        
        for cam in fdot_cameras:
            assert cam.get("jurisdiction") == "FDOT"
    
    def test_get_cameras_nearby(self):
        """Test finding cameras within radius."""
        self.engine.ingest_all()
        
        # RBPD HQ coordinates
        nearby = self.engine.get_cameras_nearby(26.7841, -80.0722, radius_km=2.0)
        
        assert len(nearby) > 0
    
    def test_get_stats(self):
        """Test getting ingestion statistics."""
        self.engine.ingest_all()
        stats = self.engine.get_stats()
        
        assert "total_cameras" in stats
        assert "ingestion_stats" in stats
        assert "last_ingestion" in stats
    
    def test_refresh(self):
        """Test refreshing all camera sources."""
        stats1 = self.engine.ingest_all()
        stats2 = self.engine.refresh()
        
        assert stats1["total_count"] == stats2["total_count"]
    
    def test_deduplication(self):
        """Test that duplicate cameras are removed."""
        stats = self.engine.ingest_all()
        
        # Check that duplicates were tracked
        assert "duplicates_removed" in stats
    
    def test_singleton_pattern(self):
        """Test that get_ingestion_engine returns singleton."""
        engine1 = get_ingestion_engine()
        engine2 = get_ingestion_engine()
        
        assert engine1 is engine2
