"""
Camera Health Monitor for G3TI RTCC-UIP Platform.

Monitors camera health status by pinging snapshot URLs and RTSP endpoints.
Broadcasts health updates via WebSocket every 30 seconds.

Health Classification:
- GREEN (online): Camera responding normally
- YELLOW (degraded): Camera responding slowly or intermittently
- RED (offline): Camera not responding
"""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Set, Callable
from enum import Enum
import time

try:
    import httpx
except ImportError:
    httpx = None


class HealthStatus(str, Enum):
    """Camera health status enumeration."""
    GREEN = "online"
    YELLOW = "degraded"
    RED = "offline"
    UNKNOWN = "unknown"


@dataclass
class HealthCheckResult:
    """Result of a health check."""
    camera_id: str
    status: HealthStatus
    response_time_ms: float
    last_check: datetime
    error_message: Optional[str] = None
    consecutive_failures: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "camera_id": self.camera_id,
            "status": self.status.value,
            "response_time_ms": round(self.response_time_ms, 2),
            "last_check": self.last_check.isoformat(),
            "error_message": self.error_message,
            "consecutive_failures": self.consecutive_failures,
        }


class CameraHealthMonitor:
    """
    Camera health monitoring system.
    
    Periodically checks camera health and broadcasts updates via WebSocket.
    """
    
    _instance: Optional["CameraHealthMonitor"] = None
    
    def __new__(cls) -> "CameraHealthMonitor":
        """Singleton pattern implementation."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the health monitor."""
        if self._initialized:
            return
        
        self._health_results: Dict[str, HealthCheckResult] = {}
        self._check_interval: int = 30  # seconds
        self._timeout: float = 5.0  # seconds
        self._degraded_threshold_ms: float = 2000  # 2 seconds
        self._running: bool = False
        self._task: Optional[asyncio.Task] = None
        self._websocket_callbacks: List[Callable] = []
        self._initialized = True
    
    async def check_camera_health(
        self,
        camera_id: str,
        url: str,
    ) -> HealthCheckResult:
        """
        Check health of a single camera.
        
        Args:
            camera_id: Camera identifier.
            url: URL to check (snapshot or stream URL).
            
        Returns:
            HealthCheckResult with status and timing.
        """
        start_time = time.time()
        
        # Get previous result for consecutive failure tracking
        prev_result = self._health_results.get(camera_id)
        consecutive_failures = prev_result.consecutive_failures if prev_result else 0
        
        if httpx is None or not url or url.startswith("https://via.placeholder.com"):
            # Demo mode - simulate healthy cameras
            result = HealthCheckResult(
                camera_id=camera_id,
                status=HealthStatus.GREEN,
                response_time_ms=50.0 + (hash(camera_id) % 100),  # Simulated response time
                last_check=datetime.utcnow(),
                consecutive_failures=0,
            )
            self._health_results[camera_id] = result
            return result
        
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.head(url)
                
                elapsed_ms = (time.time() - start_time) * 1000
                
                if response.status_code == 200:
                    if elapsed_ms > self._degraded_threshold_ms:
                        status = HealthStatus.YELLOW
                    else:
                        status = HealthStatus.GREEN
                    
                    result = HealthCheckResult(
                        camera_id=camera_id,
                        status=status,
                        response_time_ms=elapsed_ms,
                        last_check=datetime.utcnow(),
                        consecutive_failures=0,
                    )
                else:
                    result = HealthCheckResult(
                        camera_id=camera_id,
                        status=HealthStatus.RED,
                        response_time_ms=elapsed_ms,
                        last_check=datetime.utcnow(),
                        error_message=f"HTTP {response.status_code}",
                        consecutive_failures=consecutive_failures + 1,
                    )
        except asyncio.TimeoutError:
            result = HealthCheckResult(
                camera_id=camera_id,
                status=HealthStatus.RED,
                response_time_ms=self._timeout * 1000,
                last_check=datetime.utcnow(),
                error_message="Timeout",
                consecutive_failures=consecutive_failures + 1,
            )
        except Exception as e:
            result = HealthCheckResult(
                camera_id=camera_id,
                status=HealthStatus.RED,
                response_time_ms=(time.time() - start_time) * 1000,
                last_check=datetime.utcnow(),
                error_message=str(e),
                consecutive_failures=consecutive_failures + 1,
            )
        
        self._health_results[camera_id] = result
        return result
    
    async def check_all_cameras(
        self,
        cameras: List[Dict[str, Any]],
    ) -> List[HealthCheckResult]:
        """
        Check health of all cameras.
        
        Args:
            cameras: List of camera dictionaries.
            
        Returns:
            List of health check results.
        """
        tasks = []
        for cam in cameras:
            camera_id = cam.get("id", "")
            url = cam.get("stream_url") or cam.get("snapshot_url", "")
            tasks.append(self.check_camera_health(camera_id, url))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions
        valid_results = [r for r in results if isinstance(r, HealthCheckResult)]
        
        # Broadcast updates
        await self._broadcast_health_update(valid_results)
        
        return valid_results
    
    async def _broadcast_health_update(
        self,
        results: List[HealthCheckResult],
    ):
        """
        Broadcast health updates to WebSocket subscribers.
        
        Args:
            results: List of health check results.
        """
        update = {
            "type": "health_update",
            "timestamp": datetime.utcnow().isoformat(),
            "cameras": [r.to_dict() for r in results],
            "summary": self.get_health_summary(),
        }
        
        for callback in self._websocket_callbacks:
            try:
                await callback(update)
            except Exception as e:
                print(f"[HEALTH] WebSocket callback error: {e}")
    
    def register_websocket_callback(self, callback: Callable):
        """Register a WebSocket callback for health updates."""
        self._websocket_callbacks.append(callback)
    
    def unregister_websocket_callback(self, callback: Callable):
        """Unregister a WebSocket callback."""
        if callback in self._websocket_callbacks:
            self._websocket_callbacks.remove(callback)
    
    def get_camera_health(self, camera_id: str) -> Optional[Dict[str, Any]]:
        """Get health status for a specific camera."""
        result = self._health_results.get(camera_id)
        return result.to_dict() if result else None
    
    def get_all_health(self) -> List[Dict[str, Any]]:
        """Get health status for all cameras."""
        return [r.to_dict() for r in self._health_results.values()]
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get summary of camera health."""
        results = list(self._health_results.values())
        
        online = sum(1 for r in results if r.status == HealthStatus.GREEN)
        degraded = sum(1 for r in results if r.status == HealthStatus.YELLOW)
        offline = sum(1 for r in results if r.status == HealthStatus.RED)
        unknown = sum(1 for r in results if r.status == HealthStatus.UNKNOWN)
        
        avg_response_time = 0.0
        if results:
            avg_response_time = sum(r.response_time_ms for r in results) / len(results)
        
        return {
            "total_cameras": len(results),
            "online": online,
            "degraded": degraded,
            "offline": offline,
            "unknown": unknown,
            "average_response_time_ms": round(avg_response_time, 2),
            "last_check": datetime.utcnow().isoformat(),
        }
    
    async def start_monitoring(self, cameras: List[Dict[str, Any]]):
        """
        Start continuous health monitoring.
        
        Args:
            cameras: List of cameras to monitor.
        """
        if self._running:
            return
        
        self._running = True
        
        while self._running:
            await self.check_all_cameras(cameras)
            await asyncio.sleep(self._check_interval)
    
    def stop_monitoring(self):
        """Stop continuous health monitoring."""
        self._running = False
        if self._task:
            self._task.cancel()
            self._task = None
    
    def set_check_interval(self, seconds: int):
        """Set the health check interval in seconds."""
        self._check_interval = max(5, seconds)  # Minimum 5 seconds
    
    def set_timeout(self, seconds: float):
        """Set the request timeout in seconds."""
        self._timeout = max(1.0, seconds)  # Minimum 1 second


# Singleton accessor
_monitor_instance: Optional[CameraHealthMonitor] = None


def get_health_monitor() -> CameraHealthMonitor:
    """
    Get the camera health monitor singleton.
    
    Returns:
        CameraHealthMonitor instance.
    """
    global _monitor_instance
    if _monitor_instance is None:
        _monitor_instance = CameraHealthMonitor()
    return _monitor_instance
