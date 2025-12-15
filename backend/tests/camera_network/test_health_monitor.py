"""
Tests for Camera Health Monitor.
"""

import pytest
import asyncio

from app.camera_network.camera_health_monitor import (
    CameraHealthMonitor,
    HealthStatus,
    HealthCheckResult,
    get_health_monitor,
)


class TestCameraHealthMonitor:
    """Test suite for CameraHealthMonitor class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.monitor = CameraHealthMonitor()
        self.monitor._health_results.clear()
    
    @pytest.mark.asyncio
    async def test_check_camera_health_demo_mode(self):
        """Test health check in demo mode."""
        result = await self.monitor.check_camera_health(
            "test-001",
            "https://via.placeholder.com/640x360"
        )
        
        assert result.camera_id == "test-001"
        assert result.status == HealthStatus.GREEN
        assert result.response_time_ms > 0
    
    @pytest.mark.asyncio
    async def test_check_camera_health_empty_url(self):
        """Test health check with empty URL."""
        result = await self.monitor.check_camera_health("test-002", "")
        
        assert result.camera_id == "test-002"
        assert result.status == HealthStatus.GREEN  # Demo mode fallback
    
    @pytest.mark.asyncio
    async def test_check_all_cameras(self):
        """Test checking health of multiple cameras."""
        cameras = [
            {"id": "cam-001", "stream_url": "https://via.placeholder.com/640x360"},
            {"id": "cam-002", "stream_url": "https://via.placeholder.com/640x360"},
            {"id": "cam-003", "stream_url": "https://via.placeholder.com/640x360"},
        ]
        
        results = await self.monitor.check_all_cameras(cameras)
        
        assert len(results) == 3
        for result in results:
            assert isinstance(result, HealthCheckResult)
    
    def test_get_camera_health(self):
        """Test getting health status for a camera."""
        # First, add a health result
        self.monitor._health_results["test-003"] = HealthCheckResult(
            camera_id="test-003",
            status=HealthStatus.GREEN,
            response_time_ms=50.0,
            last_check=asyncio.get_event_loop().time() if hasattr(asyncio, 'get_event_loop') else 0,
        )
        
        health = self.monitor.get_camera_health("test-003")
        
        assert health is not None
        assert health["camera_id"] == "test-003"
    
    def test_get_all_health(self):
        """Test getting health status for all cameras."""
        from datetime import datetime
        
        self.monitor._health_results["cam-001"] = HealthCheckResult(
            camera_id="cam-001",
            status=HealthStatus.GREEN,
            response_time_ms=50.0,
            last_check=datetime.utcnow(),
        )
        self.monitor._health_results["cam-002"] = HealthCheckResult(
            camera_id="cam-002",
            status=HealthStatus.YELLOW,
            response_time_ms=2500.0,
            last_check=datetime.utcnow(),
        )
        
        all_health = self.monitor.get_all_health()
        
        assert len(all_health) == 2
    
    def test_get_health_summary(self):
        """Test getting health summary."""
        from datetime import datetime
        
        self.monitor._health_results["cam-001"] = HealthCheckResult(
            camera_id="cam-001",
            status=HealthStatus.GREEN,
            response_time_ms=50.0,
            last_check=datetime.utcnow(),
        )
        self.monitor._health_results["cam-002"] = HealthCheckResult(
            camera_id="cam-002",
            status=HealthStatus.RED,
            response_time_ms=5000.0,
            last_check=datetime.utcnow(),
        )
        
        summary = self.monitor.get_health_summary()
        
        assert summary["total_cameras"] == 2
        assert summary["online"] == 1
        assert summary["offline"] == 1
    
    def test_set_check_interval(self):
        """Test setting check interval."""
        self.monitor.set_check_interval(60)
        assert self.monitor._check_interval == 60
        
        # Test minimum bound
        self.monitor.set_check_interval(1)
        assert self.monitor._check_interval == 5  # Minimum is 5
    
    def test_set_timeout(self):
        """Test setting timeout."""
        self.monitor.set_timeout(10.0)
        assert self.monitor._timeout == 10.0
        
        # Test minimum bound
        self.monitor.set_timeout(0.5)
        assert self.monitor._timeout == 1.0  # Minimum is 1.0
    
    def test_health_check_result_to_dict(self):
        """Test HealthCheckResult serialization."""
        from datetime import datetime
        
        result = HealthCheckResult(
            camera_id="test-004",
            status=HealthStatus.GREEN,
            response_time_ms=75.5,
            last_check=datetime.utcnow(),
            consecutive_failures=0,
        )
        
        data = result.to_dict()
        
        assert data["camera_id"] == "test-004"
        assert data["status"] == "online"
        assert data["response_time_ms"] == 75.5
        assert data["consecutive_failures"] == 0
    
    def test_singleton_pattern(self):
        """Test that get_health_monitor returns singleton."""
        monitor1 = get_health_monitor()
        monitor2 = get_health_monitor()
        
        assert monitor1 is monitor2
