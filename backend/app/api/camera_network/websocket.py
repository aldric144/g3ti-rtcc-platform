"""
WebSocket endpoints for Camera Network real-time updates.

Provides WebSocket channels for:
- /ws/cameras/health - Real-time camera health status updates
- /ws/cameras/streams/{id} - Live camera stream updates
- /ws/cameras/video-wall - Video wall state synchronization
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, Set, Any
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.camera_network import (
    get_health_monitor,
    get_ingestion_engine,
    get_video_wall_manager,
)


router = APIRouter(prefix="/ws/cameras", tags=["camera-websocket"])


# Connection managers
class ConnectionManager:
    """Manages WebSocket connections for a specific channel."""
    
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)
    
    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast message to all connected clients."""
        disconnected = set()
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.add(connection)
        
        # Clean up disconnected clients
        for conn in disconnected:
            self.active_connections.discard(conn)
    
    async def send_personal(self, websocket: WebSocket, message: Dict[str, Any]):
        """Send message to a specific client."""
        try:
            await websocket.send_json(message)
        except Exception:
            self.disconnect(websocket)


# Connection managers for different channels
health_manager = ConnectionManager()
stream_managers: Dict[str, ConnectionManager] = {}
video_wall_manager_ws = ConnectionManager()


@router.websocket("/health")
async def camera_health_websocket(websocket: WebSocket):
    """
    WebSocket endpoint for real-time camera health updates.
    
    Broadcasts health status updates every 30 seconds.
    """
    await health_manager.connect(websocket)
    
    # Register callback with health monitor
    monitor = get_health_monitor()
    
    async def broadcast_health(update: Dict[str, Any]):
        await health_manager.broadcast(update)
    
    monitor.register_websocket_callback(broadcast_health)
    
    try:
        # Send initial health status
        await websocket.send_json({
            "type": "initial_health",
            "timestamp": datetime.utcnow().isoformat(),
            "summary": monitor.get_health_summary(),
            "cameras": monitor.get_all_health(),
        })
        
        # Keep connection alive and handle incoming messages
        while True:
            try:
                data = await asyncio.wait_for(
                    websocket.receive_text(),
                    timeout=60.0
                )
                
                # Handle ping/pong
                if data == "ping":
                    await websocket.send_text("pong")
                
                # Handle refresh request
                elif data == "refresh":
                    await websocket.send_json({
                        "type": "health_update",
                        "timestamp": datetime.utcnow().isoformat(),
                        "summary": monitor.get_health_summary(),
                        "cameras": monitor.get_all_health(),
                    })
            
            except asyncio.TimeoutError:
                # Send keepalive
                await websocket.send_json({
                    "type": "keepalive",
                    "timestamp": datetime.utcnow().isoformat(),
                })
    
    except WebSocketDisconnect:
        pass
    finally:
        health_manager.disconnect(websocket)
        monitor.unregister_websocket_callback(broadcast_health)


@router.websocket("/streams/{camera_id}")
async def camera_stream_websocket(websocket: WebSocket, camera_id: str):
    """
    WebSocket endpoint for live camera stream updates.
    
    Sends snapshot URLs or stream status updates for a specific camera.
    """
    # Get or create manager for this camera
    if camera_id not in stream_managers:
        stream_managers[camera_id] = ConnectionManager()
    
    manager = stream_managers[camera_id]
    await manager.connect(websocket)
    
    engine = get_ingestion_engine()
    camera = engine.get_camera(camera_id)
    
    try:
        # Send initial camera info
        await websocket.send_json({
            "type": "camera_info",
            "timestamp": datetime.utcnow().isoformat(),
            "camera": camera,
        })
        
        # Stream updates
        frame_count = 0
        while True:
            try:
                data = await asyncio.wait_for(
                    websocket.receive_text(),
                    timeout=5.0
                )
                
                if data == "ping":
                    await websocket.send_text("pong")
                
                elif data == "get_frame":
                    frame_count += 1
                    await websocket.send_json({
                        "type": "frame_info",
                        "timestamp": datetime.utcnow().isoformat(),
                        "camera_id": camera_id,
                        "frame_number": frame_count,
                        "stream_url": camera.get("stream_url") if camera else None,
                    })
            
            except asyncio.TimeoutError:
                # Send periodic update
                await websocket.send_json({
                    "type": "stream_status",
                    "timestamp": datetime.utcnow().isoformat(),
                    "camera_id": camera_id,
                    "status": "active",
                })
    
    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(websocket)


@router.websocket("/video-wall")
async def video_wall_websocket(websocket: WebSocket):
    """
    WebSocket endpoint for video wall state synchronization.
    
    Broadcasts video wall changes to all connected clients.
    """
    await video_wall_manager_ws.connect(websocket)
    
    wall_manager = get_video_wall_manager()
    
    try:
        # Send initial state
        await websocket.send_json({
            "type": "initial_state",
            "timestamp": datetime.utcnow().isoformat(),
            "layouts": wall_manager.get_available_layouts(),
            "presets": wall_manager.list_presets(),
        })
        
        while True:
            try:
                data = await asyncio.wait_for(
                    websocket.receive_text(),
                    timeout=60.0
                )
                
                message = json.loads(data)
                action = message.get("action")
                
                if action == "ping":
                    await websocket.send_text("pong")
                
                elif action == "get_state":
                    session_id = message.get("session_id")
                    state = wall_manager.get_wall_state(session_id)
                    await websocket.send_json({
                        "type": "wall_state",
                        "timestamp": datetime.utcnow().isoformat(),
                        "state": state,
                    })
                
                elif action == "add_camera":
                    session_id = message.get("session_id")
                    position = message.get("position")
                    camera_id = message.get("camera_id")
                    camera_name = message.get("camera_name", "")
                    stream_url = message.get("stream_url", "")
                    
                    success = wall_manager.add_camera_to_wall(
                        session_id, position, camera_id, camera_name, stream_url
                    )
                    
                    if success:
                        state = wall_manager.get_wall_state(session_id)
                        # Broadcast to all clients
                        await video_wall_manager_ws.broadcast({
                            "type": "wall_updated",
                            "timestamp": datetime.utcnow().isoformat(),
                            "session_id": session_id,
                            "state": state,
                        })
                
                elif action == "remove_camera":
                    session_id = message.get("session_id")
                    position = message.get("position")
                    
                    success = wall_manager.remove_camera_from_wall(session_id, position)
                    
                    if success:
                        state = wall_manager.get_wall_state(session_id)
                        await video_wall_manager_ws.broadcast({
                            "type": "wall_updated",
                            "timestamp": datetime.utcnow().isoformat(),
                            "session_id": session_id,
                            "state": state,
                        })
                
                elif action == "move_camera":
                    session_id = message.get("session_id")
                    from_pos = message.get("from_position")
                    to_pos = message.get("to_position")
                    
                    success = wall_manager.move_camera(session_id, from_pos, to_pos)
                    
                    if success:
                        state = wall_manager.get_wall_state(session_id)
                        await video_wall_manager_ws.broadcast({
                            "type": "wall_updated",
                            "timestamp": datetime.utcnow().isoformat(),
                            "session_id": session_id,
                            "state": state,
                        })
                
                elif action == "change_layout":
                    session_id = message.get("session_id")
                    layout = message.get("layout")
                    
                    success = wall_manager.change_layout(session_id, layout)
                    
                    if success:
                        state = wall_manager.get_wall_state(session_id)
                        await video_wall_manager_ws.broadcast({
                            "type": "layout_changed",
                            "timestamp": datetime.utcnow().isoformat(),
                            "session_id": session_id,
                            "state": state,
                        })
            
            except asyncio.TimeoutError:
                # Send keepalive
                await websocket.send_json({
                    "type": "keepalive",
                    "timestamp": datetime.utcnow().isoformat(),
                })
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON",
                })
    
    except WebSocketDisconnect:
        pass
    finally:
        video_wall_manager_ws.disconnect(websocket)
