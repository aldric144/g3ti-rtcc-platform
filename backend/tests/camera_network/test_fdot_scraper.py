"""
Tests for FDOT Scraper integration.
"""

import pytest
from datetime import datetime

from app.camera_network.fdot_scraper import (
    FDOTScraper,
    get_fdot_scraper,
    FDOT_DEMO_CAMERAS,
)


class TestFDOTScraper:
    """Test suite for FDOTScraper class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.scraper = FDOTScraper()
    
    def test_get_all_cameras_demo_mode(self):
        """Test getting cameras in demo mode."""
        cameras = self.scraper.get_all_cameras()
        
        assert len(cameras) > 0
        assert len(cameras) == len(FDOT_DEMO_CAMERAS)
    
    def test_camera_structure(self):
        """Test that cameras have required fields."""
        cameras = self.scraper.get_all_cameras()
        
        for cam in cameras:
            assert "fdot_id" in cam
            assert "name" in cam
            assert "latitude" in cam
            assert "longitude" in cam
            assert "snapshot_url" in cam
            assert "camera_type" in cam
            assert "jurisdiction" in cam
            assert "status" in cam
    
    def test_get_camera_by_id(self):
        """Test getting a specific camera by ID."""
        cameras = self.scraper.get_all_cameras()
        first_camera_id = cameras[0]["fdot_id"]
        
        camera = self.scraper.get_camera(first_camera_id)
        
        assert camera is not None
        assert camera["fdot_id"] == first_camera_id
    
    def test_get_camera_not_found(self):
        """Test getting a non-existent camera."""
        camera = self.scraper.get_camera("non-existent-id")
        assert camera is None
    
    def test_is_demo_mode(self):
        """Test demo mode detection."""
        self.scraper.get_all_cameras()
        assert self.scraper.is_demo_mode() is True
    
    def test_get_status(self):
        """Test getting scraper status."""
        self.scraper.get_all_cameras()
        status = self.scraper.get_status()
        
        assert "total_cameras" in status
        assert "demo_mode" in status
        assert "last_fetch" in status
        assert "online_count" in status
        assert status["demo_mode"] is True
    
    def test_sector_computation(self):
        """Test that sectors are computed for cameras."""
        cameras = self.scraper.get_all_cameras()
        
        for cam in cameras:
            assert "sector" in cam
            assert cam["sector"].startswith("Sector")
    
    def test_singleton_pattern(self):
        """Test that get_fdot_scraper returns singleton."""
        scraper1 = get_fdot_scraper()
        scraper2 = get_fdot_scraper()
        
        assert scraper1 is scraper2
    
    def test_camera_coordinates_valid(self):
        """Test that camera coordinates are valid."""
        cameras = self.scraper.get_all_cameras()
        
        for cam in cameras:
            lat = cam["latitude"]
            lng = cam["longitude"]
            
            # Riviera Beach / Palm Beach area coordinates
            assert 26.0 < lat < 27.5
            assert -81.0 < lng < -79.5
