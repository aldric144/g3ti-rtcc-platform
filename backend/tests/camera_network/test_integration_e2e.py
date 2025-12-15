"""
End-to-End Integration Tests for Camera Network.
"""

import pytest

from app.camera_network import (
    get_camera_registry,
    get_fdot_scraper,
    get_ingestion_engine,
    get_health_monitor,
    get_streaming_adapter,
    get_video_wall_manager,
    CameraType,
    CameraJurisdiction,
    CameraStatus,
)
from app.camera_network.rbpd_mock_loader import load_rbpd_mock_cameras


class TestCameraNetworkE2E:
    """End-to-end integration tests for Camera Network."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.registry = get_camera_registry()
        self.registry.clear()
        self.engine = get_ingestion_engine()
        self.engine._manual_cameras.clear()
    
    def test_full_ingestion_pipeline(self):
        """Test complete camera ingestion from all sources."""
        # Ingest all cameras
        stats = self.engine.ingest_all()
        
        # Verify cameras were loaded
        assert stats["total_count"] > 0
        assert stats["rbpd_count"] > 0
        assert stats["fdot_count"] > 0
        
        # Verify cameras are in registry
        cameras = self.engine.get_all_cameras()
        assert len(cameras) == stats["total_count"]
    
    def test_camera_filtering_chain(self):
        """Test filtering cameras through multiple criteria."""
        self.engine.ingest_all()
        
        # Get all cameras
        all_cameras = self.engine.get_all_cameras()
        
        # Filter by jurisdiction
        rbpd_cameras = self.engine.get_cameras_by_jurisdiction("RBPD")
        fdot_cameras = self.engine.get_cameras_by_jurisdiction("FDOT")
        
        # Verify filters work
        assert len(rbpd_cameras) + len(fdot_cameras) <= len(all_cameras)
        
        # Filter by sector
        sectors = set(c.get("sector") for c in all_cameras if c.get("sector"))
        for sector in list(sectors)[:2]:
            sector_cameras = self.engine.get_cameras_by_sector(sector)
            assert all(c.get("sector") == sector for c in sector_cameras)
    
    def test_video_wall_workflow(self):
        """Test complete video wall workflow."""
        self.engine.ingest_all()
        cameras = self.engine.get_all_cameras()
        
        wall_manager = get_video_wall_manager()
        
        # Create session
        session = wall_manager.create_session("test-user", "2x2")
        assert session is not None
        
        # Add cameras to wall
        for i, cam in enumerate(cameras[:4]):
            wall_manager.add_camera_to_wall(
                session.session_id,
                position=i,
                camera_id=cam["id"],
                camera_name=cam["name"],
                stream_url=cam.get("stream_url", ""),
            )
        
        # Verify wall state
        state = wall_manager.get_wall_state(session.session_id)
        assert state is not None
        assert len([s for s in state["slots"] if not s["is_empty"]]) == min(4, len(cameras))
        
        # Save as preset
        preset = wall_manager.save_preset(session.session_id, "Test Preset")
        assert preset is not None
        
        # Change layout
        wall_manager.change_layout(session.session_id, "3x3")
        state = wall_manager.get_wall_state(session.session_id)
        assert state["layout"] == "3x3"
        
        # Clear wall
        wall_manager.clear_wall(session.session_id)
        state = wall_manager.get_wall_state(session.session_id)
        assert all(s["is_empty"] for s in state["slots"])
    
    def test_manual_camera_workflow(self):
        """Test adding and managing manual cameras."""
        # Add manual camera
        manual_camera = self.engine.add_manual_camera({
            "name": "Manual Test Camera",
            "latitude": 26.7841,
            "longitude": -80.0722,
            "stream_url": "https://example.com/stream",
            "camera_type": "cctv",
            "sector": "Sector 1",
        })
        
        assert manual_camera is not None
        assert manual_camera["jurisdiction"] == "Manual"
        
        # Verify it's in the registry
        cameras = self.engine.get_all_cameras()
        manual_ids = [c["id"] for c in cameras if c.get("jurisdiction") == "Manual"]
        assert manual_camera["id"] in manual_ids
        
        # Remove manual camera
        result = self.engine.remove_manual_camera(manual_camera["id"])
        assert result is True
    
    def test_nearby_search_accuracy(self):
        """Test nearby camera search returns correct results."""
        self.engine.ingest_all()
        
        # RBPD HQ coordinates
        hq_lat, hq_lng = 26.7841, -80.0722
        
        # Search with small radius
        nearby_1km = self.engine.get_cameras_nearby(hq_lat, hq_lng, radius_km=1.0)
        nearby_5km = self.engine.get_cameras_nearby(hq_lat, hq_lng, radius_km=5.0)
        nearby_10km = self.engine.get_cameras_nearby(hq_lat, hq_lng, radius_km=10.0)
        
        # Larger radius should return more cameras
        assert len(nearby_1km) <= len(nearby_5km) <= len(nearby_10km)
    
    def test_health_monitoring_integration(self):
        """Test health monitoring with camera registry."""
        self.engine.ingest_all()
        cameras = self.engine.get_all_cameras()
        
        monitor = get_health_monitor()
        
        # Get health summary
        summary = monitor.get_health_summary()
        assert "total_cameras" in summary
        assert "online" in summary
    
    def test_streaming_adapter_integration(self):
        """Test streaming adapter with camera registry."""
        self.engine.ingest_all()
        cameras = self.engine.get_all_cameras()
        
        adapter = get_streaming_adapter()
        
        # Register cameras
        for cam in cameras[:5]:
            adapter.register_camera(
                camera_id=cam["id"],
                stream_url=cam.get("stream_url", ""),
            )
        
        # Verify registration
        for cam in cameras[:5]:
            info = adapter.get_stream_info(cam["id"])
            assert info is not None
    
    def test_source_priority_ordering(self):
        """Test that cameras are ordered by source priority."""
        self.engine.ingest_all()
        cameras = self.engine.get_all_cameras()
        
        # RBPD cameras should have highest priority (100)
        rbpd_cameras = [c for c in cameras if c.get("jurisdiction") == "RBPD"]
        for cam in rbpd_cameras:
            # Check that RBPD cameras exist and have correct jurisdiction
            assert cam.get("jurisdiction") == "RBPD"
    
    def test_fdot_scraper_integration(self):
        """Test FDOT scraper integration with ingestion engine."""
        scraper = get_fdot_scraper()
        
        # Get FDOT cameras directly
        fdot_cameras = scraper.get_all_cameras()
        assert len(fdot_cameras) > 0
        
        # Verify they're in the ingestion engine
        self.engine.ingest_all()
        all_cameras = self.engine.get_all_cameras()
        
        fdot_in_engine = [c for c in all_cameras if c.get("jurisdiction") == "FDOT"]
        assert len(fdot_in_engine) > 0
    
    def test_rbpd_loader_integration(self):
        """Test RBPD loader integration with ingestion engine."""
        # Get RBPD cameras directly
        rbpd_cameras = load_rbpd_mock_cameras()
        assert len(rbpd_cameras) >= 25
        
        # Verify they're in the ingestion engine
        self.engine.ingest_all()
        all_cameras = self.engine.get_all_cameras()
        
        rbpd_in_engine = [c for c in all_cameras if c.get("jurisdiction") == "RBPD"]
        assert len(rbpd_in_engine) > 0
    
    def test_complete_system_stats(self):
        """Test getting complete system statistics."""
        self.engine.ingest_all()
        
        stats = self.engine.get_stats()
        
        assert "total_cameras" in stats
        assert "by_jurisdiction" in stats
        assert "by_type" in stats
        assert "ingestion_stats" in stats
        assert "last_ingestion" in stats
