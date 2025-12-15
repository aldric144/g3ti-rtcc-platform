"""
Tests for Streaming Adapter.
"""

import pytest
import asyncio

from app.camera_network.streaming_adapter import (
    StreamingAdapter,
    StreamType,
    StreamConfig,
    get_streaming_adapter,
)


class TestStreamingAdapter:
    """Test suite for StreamingAdapter class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.adapter = StreamingAdapter()
        self.adapter._stream_configs.clear()
        self.adapter._active_streams.clear()
    
    def test_register_stream(self):
        """Test registering a stream configuration."""
        config = StreamConfig(
            camera_id="test-001",
            stream_url="https://example.com/stream",
            stream_type=StreamType.MJPEG,
        )
        
        self.adapter.register_stream(config)
        
        assert "test-001" in self.adapter._stream_configs
    
    def test_register_camera(self):
        """Test registering a camera for streaming."""
        self.adapter.register_camera(
            camera_id="test-002",
            stream_url="https://example.com/stream",
            stream_type="snapshot",
        )
        
        assert "test-002" in self.adapter._stream_configs
        assert self.adapter._stream_configs["test-002"].stream_type == StreamType.SNAPSHOT
    
    def test_detect_stream_type_mjpeg(self):
        """Test detecting MJPEG stream type."""
        url = "https://example.com/camera/mjpeg"
        stream_type = self.adapter.detect_stream_type(url)
        
        assert stream_type == StreamType.MJPEG
    
    def test_detect_stream_type_rtsp(self):
        """Test detecting RTSP stream type."""
        url = "rtsp://example.com/camera/stream"
        stream_type = self.adapter.detect_stream_type(url)
        
        assert stream_type == StreamType.RTSP
    
    def test_detect_stream_type_snapshot(self):
        """Test detecting snapshot stream type."""
        url = "https://example.com/camera/snapshot.jpg"
        stream_type = self.adapter.detect_stream_type(url)
        
        assert stream_type == StreamType.SNAPSHOT
    
    def test_detect_stream_type_placeholder(self):
        """Test detecting placeholder stream type."""
        url = "https://via.placeholder.com/640x360"
        stream_type = self.adapter.detect_stream_type(url)
        
        assert stream_type == StreamType.PLACEHOLDER
    
    @pytest.mark.asyncio
    async def test_get_snapshot_demo_mode(self):
        """Test getting snapshot in demo mode."""
        self.adapter.register_camera(
            camera_id="test-003",
            stream_url="https://via.placeholder.com/640x360",
        )
        
        snapshot = await self.adapter.get_snapshot("test-003")
        
        assert snapshot is not None
        assert isinstance(snapshot, bytes)
    
    @pytest.mark.asyncio
    async def test_get_snapshot_unregistered(self):
        """Test getting snapshot for unregistered camera."""
        snapshot = await self.adapter.get_snapshot("unregistered")
        
        # Should return placeholder
        assert snapshot is not None
    
    @pytest.mark.asyncio
    async def test_get_thumbnail(self):
        """Test getting cached thumbnail."""
        self.adapter.register_camera(
            camera_id="test-004",
            stream_url="https://via.placeholder.com/640x360",
        )
        
        thumbnail = await self.adapter.get_thumbnail("test-004")
        
        assert thumbnail is not None
        assert isinstance(thumbnail, bytes)
    
    @pytest.mark.asyncio
    async def test_thumbnail_caching(self):
        """Test that thumbnails are cached."""
        self.adapter.register_camera(
            camera_id="test-005",
            stream_url="https://via.placeholder.com/640x360",
        )
        
        # First call
        await self.adapter.get_thumbnail("test-005")
        
        # Check cache
        assert "test-005" in self.adapter._thumbnail_cache
        assert "test-005" in self.adapter._thumbnail_timestamps
    
    def test_stop_stream(self):
        """Test stopping an active stream."""
        self.adapter._active_streams["test-006"] = True
        
        self.adapter.stop_stream("test-006")
        
        assert self.adapter._active_streams["test-006"] is False
    
    def test_get_stream_info(self):
        """Test getting stream configuration info."""
        config = StreamConfig(
            camera_id="test-007",
            stream_url="https://example.com/stream",
            stream_type=StreamType.MJPEG,
            refresh_interval=3.0,
            quality=90,
        )
        
        self.adapter.register_stream(config)
        info = self.adapter.get_stream_info("test-007")
        
        assert info is not None
        assert info["camera_id"] == "test-007"
        assert info["stream_type"] == "mjpeg"
        assert info["refresh_interval"] == 3.0
        assert info["quality"] == 90
    
    def test_get_stream_info_not_found(self):
        """Test getting info for unregistered stream."""
        info = self.adapter.get_stream_info("non-existent")
        assert info is None
    
    def test_get_all_stream_info(self):
        """Test getting info for all streams."""
        self.adapter.register_camera("cam-001", "https://example.com/1")
        self.adapter.register_camera("cam-002", "https://example.com/2")
        
        all_info = self.adapter.get_all_stream_info()
        
        assert len(all_info) == 2
    
    def test_singleton_pattern(self):
        """Test that get_streaming_adapter returns singleton."""
        adapter1 = get_streaming_adapter()
        adapter2 = get_streaming_adapter()
        
        assert adapter1 is adapter2
