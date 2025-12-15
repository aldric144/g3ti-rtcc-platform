"""
Streaming Adapter for G3TI RTCC-UIP Platform.

Supports multiple streaming formats:
- MJPEG: Motion JPEG streams
- Snapshot: Timed snapshot refresh
- RTSP: Real-Time Streaming Protocol (placeholder for WebRTC shim)
- HTTP: HTTP-based video streams
"""

import asyncio
from dataclasses import dataclass
from datetime import datetime
from typing import AsyncGenerator, Dict, Any, Optional, List
from enum import Enum
import time

try:
    import httpx
except ImportError:
    httpx = None


class StreamType(str, Enum):
    """Supported stream types."""
    MJPEG = "mjpeg"
    SNAPSHOT = "snapshot"
    RTSP = "rtsp"
    HTTP = "http"
    PLACEHOLDER = "placeholder"


# MJPEG boundary marker
MJPEG_BOUNDARY = b"--frame"

# Placeholder image for demo mode
PLACEHOLDER_IMAGE_URL = "https://via.placeholder.com/640x360?text=Camera+Feed"


@dataclass
class StreamConfig:
    """Configuration for a camera stream."""
    camera_id: str
    stream_url: str
    stream_type: StreamType
    refresh_interval: float = 2.0  # seconds for snapshot refresh
    quality: int = 80  # JPEG quality (1-100)
    width: int = 640
    height: int = 360


class StreamingAdapter:
    """
    Unified streaming adapter for multiple stream types.
    
    Provides consistent interface for accessing camera feeds
    regardless of underlying stream format.
    """
    
    _instance: Optional["StreamingAdapter"] = None
    
    def __new__(cls) -> "StreamingAdapter":
        """Singleton pattern implementation."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the streaming adapter."""
        if self._initialized:
            return
        
        self._stream_configs: Dict[str, StreamConfig] = {}
        self._active_streams: Dict[str, bool] = {}
        self._thumbnail_cache: Dict[str, bytes] = {}
        self._thumbnail_timestamps: Dict[str, datetime] = {}
        self._initialized = True
    
    def register_stream(self, config: StreamConfig):
        """
        Register a camera stream configuration.
        
        Args:
            config: Stream configuration.
        """
        self._stream_configs[config.camera_id] = config
    
    def register_camera(
        self,
        camera_id: str,
        stream_url: str,
        stream_type: str = "snapshot",
    ):
        """
        Register a camera for streaming.
        
        Args:
            camera_id: Camera identifier.
            stream_url: Stream URL.
            stream_type: Type of stream.
        """
        try:
            st = StreamType(stream_type.lower())
        except ValueError:
            st = StreamType.SNAPSHOT
        
        config = StreamConfig(
            camera_id=camera_id,
            stream_url=stream_url,
            stream_type=st,
        )
        self.register_stream(config)
    
    def detect_stream_type(self, url: str) -> StreamType:
        """
        Detect stream type from URL.
        
        Args:
            url: Stream URL.
            
        Returns:
            Detected StreamType.
        """
        url_lower = url.lower()
        
        if "placeholder.com" in url_lower:
            return StreamType.PLACEHOLDER
        elif url_lower.startswith("rtsp://"):
            return StreamType.RTSP
        elif "mjpeg" in url_lower or "mjpg" in url_lower:
            return StreamType.MJPEG
        elif url_lower.endswith((".jpg", ".jpeg", ".png")):
            return StreamType.SNAPSHOT
        else:
            return StreamType.SNAPSHOT
    
    async def get_snapshot(self, camera_id: str) -> Optional[bytes]:
        """
        Get a single snapshot from a camera.
        
        Args:
            camera_id: Camera identifier.
            
        Returns:
            JPEG image bytes or None.
        """
        config = self._stream_configs.get(camera_id)
        
        if not config:
            return await self._get_placeholder_image()
        
        if config.stream_type == StreamType.PLACEHOLDER:
            return await self._get_placeholder_image()
        
        if httpx is None:
            return await self._get_placeholder_image()
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(config.stream_url)
                
                if response.status_code == 200:
                    return response.content
                else:
                    return await self._get_placeholder_image()
        except Exception as e:
            print(f"[STREAM] Snapshot error for {camera_id}: {e}")
            return await self._get_placeholder_image()
    
    async def generate_mjpeg_stream(
        self,
        camera_id: str,
        refresh_interval: float = 2.0,
    ) -> AsyncGenerator[bytes, None]:
        """
        Generate MJPEG stream from snapshots.
        
        Args:
            camera_id: Camera identifier.
            refresh_interval: Seconds between frames.
            
        Yields:
            MJPEG frame bytes.
        """
        self._active_streams[camera_id] = True
        
        try:
            while self._active_streams.get(camera_id, False):
                # Get snapshot
                image_data = await self.get_snapshot(camera_id)
                
                if image_data:
                    # Format as MJPEG frame
                    frame = (
                        b"--frame\r\n"
                        b"Content-Type: image/jpeg\r\n"
                        b"Content-Length: " + str(len(image_data)).encode() + b"\r\n"
                        b"\r\n" + image_data + b"\r\n"
                    )
                    yield frame
                
                await asyncio.sleep(refresh_interval)
        finally:
            self._active_streams[camera_id] = False
    
    def stop_stream(self, camera_id: str):
        """Stop an active stream."""
        self._active_streams[camera_id] = False
    
    async def get_thumbnail(
        self,
        camera_id: str,
        max_age_seconds: float = 30.0,
    ) -> Optional[bytes]:
        """
        Get cached thumbnail for a camera.
        
        Args:
            camera_id: Camera identifier.
            max_age_seconds: Maximum age of cached thumbnail.
            
        Returns:
            JPEG thumbnail bytes or None.
        """
        # Check cache
        cached_time = self._thumbnail_timestamps.get(camera_id)
        if cached_time:
            age = (datetime.utcnow() - cached_time).total_seconds()
            if age < max_age_seconds and camera_id in self._thumbnail_cache:
                return self._thumbnail_cache[camera_id]
        
        # Fetch new thumbnail
        thumbnail = await self.get_snapshot(camera_id)
        
        if thumbnail:
            self._thumbnail_cache[camera_id] = thumbnail
            self._thumbnail_timestamps[camera_id] = datetime.utcnow()
        
        return thumbnail
    
    async def refresh_all_thumbnails(
        self,
        camera_ids: List[str],
    ) -> Dict[str, bool]:
        """
        Refresh thumbnails for multiple cameras.
        
        Args:
            camera_ids: List of camera IDs.
            
        Returns:
            Dictionary of camera_id -> success status.
        """
        results = {}
        
        for camera_id in camera_ids:
            try:
                thumbnail = await self.get_snapshot(camera_id)
                if thumbnail:
                    self._thumbnail_cache[camera_id] = thumbnail
                    self._thumbnail_timestamps[camera_id] = datetime.utcnow()
                    results[camera_id] = True
                else:
                    results[camera_id] = False
            except Exception as e:
                print(f"[STREAM] Thumbnail refresh error for {camera_id}: {e}")
                results[camera_id] = False
        
        return results
    
    async def _get_placeholder_image(self) -> bytes:
        """
        Get placeholder image for demo mode.
        
        Returns:
            Placeholder JPEG bytes.
        """
        # Return a minimal valid JPEG for demo mode
        # This is a 1x1 gray pixel JPEG
        return bytes([
            0xFF, 0xD8, 0xFF, 0xE0, 0x00, 0x10, 0x4A, 0x46, 0x49, 0x46, 0x00, 0x01,
            0x01, 0x00, 0x00, 0x01, 0x00, 0x01, 0x00, 0x00, 0xFF, 0xDB, 0x00, 0x43,
            0x00, 0x08, 0x06, 0x06, 0x07, 0x06, 0x05, 0x08, 0x07, 0x07, 0x07, 0x09,
            0x09, 0x08, 0x0A, 0x0C, 0x14, 0x0D, 0x0C, 0x0B, 0x0B, 0x0C, 0x19, 0x12,
            0x13, 0x0F, 0x14, 0x1D, 0x1A, 0x1F, 0x1E, 0x1D, 0x1A, 0x1C, 0x1C, 0x20,
            0x24, 0x2E, 0x27, 0x20, 0x22, 0x2C, 0x23, 0x1C, 0x1C, 0x28, 0x37, 0x29,
            0x2C, 0x30, 0x31, 0x34, 0x34, 0x34, 0x1F, 0x27, 0x39, 0x3D, 0x38, 0x32,
            0x3C, 0x2E, 0x33, 0x34, 0x32, 0xFF, 0xC0, 0x00, 0x0B, 0x08, 0x00, 0x01,
            0x00, 0x01, 0x01, 0x01, 0x11, 0x00, 0xFF, 0xC4, 0x00, 0x1F, 0x00, 0x00,
            0x01, 0x05, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08,
            0x09, 0x0A, 0x0B, 0xFF, 0xC4, 0x00, 0xB5, 0x10, 0x00, 0x02, 0x01, 0x03,
            0x03, 0x02, 0x04, 0x03, 0x05, 0x05, 0x04, 0x04, 0x00, 0x00, 0x01, 0x7D,
            0x01, 0x02, 0x03, 0x00, 0x04, 0x11, 0x05, 0x12, 0x21, 0x31, 0x41, 0x06,
            0x13, 0x51, 0x61, 0x07, 0x22, 0x71, 0x14, 0x32, 0x81, 0x91, 0xA1, 0x08,
            0x23, 0x42, 0xB1, 0xC1, 0x15, 0x52, 0xD1, 0xF0, 0x24, 0x33, 0x62, 0x72,
            0x82, 0x09, 0x0A, 0x16, 0x17, 0x18, 0x19, 0x1A, 0x25, 0x26, 0x27, 0x28,
            0x29, 0x2A, 0x34, 0x35, 0x36, 0x37, 0x38, 0x39, 0x3A, 0x43, 0x44, 0x45,
            0x46, 0x47, 0x48, 0x49, 0x4A, 0x53, 0x54, 0x55, 0x56, 0x57, 0x58, 0x59,
            0x5A, 0x63, 0x64, 0x65, 0x66, 0x67, 0x68, 0x69, 0x6A, 0x73, 0x74, 0x75,
            0x76, 0x77, 0x78, 0x79, 0x7A, 0x83, 0x84, 0x85, 0x86, 0x87, 0x88, 0x89,
            0x8A, 0x92, 0x93, 0x94, 0x95, 0x96, 0x97, 0x98, 0x99, 0x9A, 0xA2, 0xA3,
            0xA4, 0xA5, 0xA6, 0xA7, 0xA8, 0xA9, 0xAA, 0xB2, 0xB3, 0xB4, 0xB5, 0xB6,
            0xB7, 0xB8, 0xB9, 0xBA, 0xC2, 0xC3, 0xC4, 0xC5, 0xC6, 0xC7, 0xC8, 0xC9,
            0xCA, 0xD2, 0xD3, 0xD4, 0xD5, 0xD6, 0xD7, 0xD8, 0xD9, 0xDA, 0xE1, 0xE2,
            0xE3, 0xE4, 0xE5, 0xE6, 0xE7, 0xE8, 0xE9, 0xEA, 0xF1, 0xF2, 0xF3, 0xF4,
            0xF5, 0xF6, 0xF7, 0xF8, 0xF9, 0xFA, 0xFF, 0xDA, 0x00, 0x08, 0x01, 0x01,
            0x00, 0x00, 0x3F, 0x00, 0xFB, 0xD5, 0xDB, 0x20, 0xA8, 0xF1, 0x7E, 0xA9,
            0x00, 0x00, 0x00, 0x00, 0xFF, 0xD9
        ])
    
    def get_stream_info(self, camera_id: str) -> Optional[Dict[str, Any]]:
        """Get stream configuration info."""
        config = self._stream_configs.get(camera_id)
        if not config:
            return None
        
        return {
            "camera_id": config.camera_id,
            "stream_url": config.stream_url,
            "stream_type": config.stream_type.value,
            "refresh_interval": config.refresh_interval,
            "quality": config.quality,
            "width": config.width,
            "height": config.height,
            "is_active": self._active_streams.get(camera_id, False),
        }
    
    def get_all_stream_info(self) -> List[Dict[str, Any]]:
        """Get info for all registered streams."""
        return [
            self.get_stream_info(camera_id)
            for camera_id in self._stream_configs.keys()
        ]


# Singleton accessor
_adapter_instance: Optional[StreamingAdapter] = None


def get_streaming_adapter() -> StreamingAdapter:
    """
    Get the streaming adapter singleton.
    
    Returns:
        StreamingAdapter instance.
    """
    global _adapter_instance
    if _adapter_instance is None:
        _adapter_instance = StreamingAdapter()
    return _adapter_instance
