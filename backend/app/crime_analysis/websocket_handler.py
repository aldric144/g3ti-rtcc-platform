"""
Crime Analysis WebSocket Handler.

Path: /ws/crime/alerts

Pushes updates for:
- Crime spikes
- Anomalies
- New high-risk zones
- Repeat locations
"""

import asyncio
import json
from datetime import datetime
from typing import Optional, Set
from fastapi import WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from app.crime_analysis.crime_timeseries import get_timeseries_analyzer
from app.crime_analysis.sector_risk_analysis import get_risk_analyzer
from app.crime_analysis.repeat_location_detector import get_repeat_detector


class CrimeAlert(BaseModel):
    """Crime alert message."""
    alert_id: str
    alert_type: str  # "spike", "anomaly", "high_risk_zone", "repeat_location"
    severity: str  # "low", "medium", "high", "critical"
    title: str
    description: str
    location: Optional[dict] = None
    sector: Optional[str] = None
    timestamp: str
    data: Optional[dict] = None


class CrimeWebSocketManager:
    """Manages WebSocket connections for crime alerts."""
    
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self._alert_counter = 0
        self._running = False
        self._monitor_task: Optional[asyncio.Task] = None
    
    async def connect(self, websocket: WebSocket):
        """Accept a new WebSocket connection."""
        await websocket.accept()
        self.active_connections.add(websocket)
        
        # Send welcome message
        await self._send_to_client(websocket, {
            "type": "connected",
            "message": "Connected to Crime Analysis alerts",
            "timestamp": datetime.utcnow().isoformat(),
        })
        
        # Start monitoring if not already running
        if not self._running:
            self._running = True
            self._monitor_task = asyncio.create_task(self._monitor_loop())
    
    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection."""
        self.active_connections.discard(websocket)
        
        # Stop monitoring if no connections
        if not self.active_connections and self._monitor_task:
            self._running = False
            self._monitor_task.cancel()
            self._monitor_task = None
    
    async def _send_to_client(self, websocket: WebSocket, data: dict):
        """Send data to a specific client."""
        try:
            await websocket.send_json(data)
        except Exception:
            self.disconnect(websocket)
    
    async def broadcast(self, alert: CrimeAlert):
        """Broadcast an alert to all connected clients."""
        message = {
            "type": "alert",
            "alert": alert.model_dump(),
        }
        
        disconnected = set()
        for websocket in self.active_connections:
            try:
                await websocket.send_json(message)
            except Exception:
                disconnected.add(websocket)
        
        # Clean up disconnected clients
        for ws in disconnected:
            self.disconnect(ws)
    
    def _generate_alert_id(self) -> str:
        """Generate unique alert ID."""
        self._alert_counter += 1
        return f"alert-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{self._alert_counter:04d}"
    
    async def _check_for_spikes(self):
        """Check for crime spikes and anomalies."""
        try:
            analyzer = get_timeseries_analyzer()
            result = analyzer.analyze(days=7)
            
            for anomaly in result.anomalies:
                if anomaly.severity in ["high", "critical"]:
                    alert = CrimeAlert(
                        alert_id=self._generate_alert_id(),
                        alert_type="spike" if anomaly.deviation > 0 else "anomaly",
                        severity=anomaly.severity,
                        title=f"Crime {'Spike' if anomaly.deviation > 0 else 'Drop'} Detected",
                        description=anomaly.description,
                        timestamp=datetime.utcnow().isoformat(),
                        data={
                            "expected": anomaly.expected_count,
                            "actual": anomaly.actual_count,
                            "deviation": anomaly.deviation,
                        },
                    )
                    await self.broadcast(alert)
        except Exception:
            pass  # Silently handle errors in background task
    
    async def _check_high_risk_zones(self):
        """Check for new high-risk zones."""
        try:
            analyzer = get_risk_analyzer()
            result = analyzer.analyze_all_sectors(days=7)
            
            for sector in result.sectors:
                if sector.risk_level in ["high", "critical"]:
                    alert = CrimeAlert(
                        alert_id=self._generate_alert_id(),
                        alert_type="high_risk_zone",
                        severity=sector.risk_level,
                        title=f"High Risk Zone: {sector.sector}",
                        description=f"Sector {sector.sector} has elevated risk (score: {sector.overall_score})",
                        sector=sector.sector,
                        timestamp=datetime.utcnow().isoformat(),
                        data={
                            "score": sector.overall_score,
                            "violent_crimes": sector.violent_crimes,
                            "total_incidents": sector.total_incidents,
                        },
                    )
                    await self.broadcast(alert)
        except Exception:
            pass
    
    async def _check_repeat_locations(self):
        """Check for new repeat location hotspots."""
        try:
            detector = get_repeat_detector()
            result = detector.detect(days=7, min_incidents=3)
            
            for location in result.top_10_hotspots[:3]:  # Top 3 only
                if location.severity_score >= 3.0:
                    alert = CrimeAlert(
                        alert_id=self._generate_alert_id(),
                        alert_type="repeat_location",
                        severity="high" if location.severity_score >= 4.0 else "medium",
                        title=f"Repeat Location Hotspot",
                        description=f"{location.incident_count} incidents at {location.address or 'location'}",
                        location={
                            "latitude": location.latitude,
                            "longitude": location.longitude,
                        },
                        sector=location.sector,
                        timestamp=datetime.utcnow().isoformat(),
                        data={
                            "incident_count": location.incident_count,
                            "severity_score": location.severity_score,
                            "crime_types": location.crime_types,
                        },
                    )
                    await self.broadcast(alert)
        except Exception:
            pass
    
    async def _monitor_loop(self):
        """Background loop to check for alerts."""
        while self._running:
            try:
                # Check for various alert conditions
                await self._check_for_spikes()
                await self._check_high_risk_zones()
                await self._check_repeat_locations()
                
                # Wait before next check (60 seconds)
                await asyncio.sleep(60)
            except asyncio.CancelledError:
                break
            except Exception:
                await asyncio.sleep(60)


# Global WebSocket manager
_ws_manager: Optional[CrimeWebSocketManager] = None


def get_crime_ws_manager() -> CrimeWebSocketManager:
    """Get or create the global WebSocket manager."""
    global _ws_manager
    if _ws_manager is None:
        _ws_manager = CrimeWebSocketManager()
    return _ws_manager


async def crime_alerts_websocket(websocket: WebSocket):
    """WebSocket endpoint handler for crime alerts."""
    manager = get_crime_ws_manager()
    await manager.connect(websocket)
    
    try:
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            
            # Handle client messages (e.g., subscription preferences)
            try:
                message = json.loads(data)
                if message.get("type") == "ping":
                    await websocket.send_json({
                        "type": "pong",
                        "timestamp": datetime.utcnow().isoformat(),
                    })
                elif message.get("type") == "subscribe":
                    # Could implement subscription filtering here
                    await websocket.send_json({
                        "type": "subscribed",
                        "filters": message.get("filters", []),
                    })
            except json.JSONDecodeError:
                pass
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception:
        manager.disconnect(websocket)
