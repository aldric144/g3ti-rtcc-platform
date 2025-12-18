"""
Extended Camera Health Monitor Module
PROTECTED MODE - Additive Only

Provides health monitoring for all camera networks:
- RTSP cameras
- Marina cameras
- Singer Island cameras
- PBC Traffic cameras
- FDOT MJPEG simulators

Includes WebSocket support for real-time health updates.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import httpx
import asyncio
from datetime import datetime
from typing import Dict, List, Set
import json

router = APIRouter(prefix="/api/cameras/health", tags=["Camera Health"])

# Import camera catalogs from other modules
# In production, these would be imported from the actual modules
CAMERA_NETWORKS = {
    "marina": {
        "marina-001": {"name": "Riviera Beach Marina HD Live", "check_url": "https://via.placeholder.com/1x1"},
        "marina-002": {"name": "Singer Island Marriott Beach Cam", "check_url": "https://via.placeholder.com/1x1"},
        "marina-003": {"name": "Port of Palm Beach - North Dock", "check_url": "https://via.placeholder.com/1x1"},
        "marina-004": {"name": "Port of Palm Beach - South Basin", "check_url": "https://via.placeholder.com/1x1"},
        "marina-005": {"name": "Peanut Island View", "check_url": "https://via.placeholder.com/1x1"},
    },
    "singer_island": {
        "singer-001": {"name": "Singer Island Beach North", "check_url": "https://via.placeholder.com/1x1"},
        "singer-002": {"name": "Singer Island Beach South", "check_url": "https://via.placeholder.com/1x1"},
    },
    "pbc_traffic": {
        "pbc-001": {"name": "I-95 @ Okeechobee Blvd", "check_url": "https://via.placeholder.com/1x1"},
        "pbc-002": {"name": "I-95 @ Palm Beach Lakes Blvd", "check_url": "https://via.placeholder.com/1x1"},
        "pbc-003": {"name": "I-95 @ 45th Street", "check_url": "https://via.placeholder.com/1x1"},
        "pbc-004": {"name": "Blue Heron Blvd @ I-95", "check_url": "https://via.placeholder.com/1x1"},
        "pbc-005": {"name": "PGA Blvd @ I-95", "check_url": "https://via.placeholder.com/1x1"},
        "pbc-006": {"name": "Northlake Blvd @ I-95", "check_url": "https://via.placeholder.com/1x1"},
        "pbc-007": {"name": "Southern Blvd @ I-95", "check_url": "https://via.placeholder.com/1x1"},
        "pbc-008": {"name": "Forest Hill Blvd @ I-95", "check_url": "https://via.placeholder.com/1x1"},
    },
    "rtsp": {
        "rtsp-001": {"name": "RBPD HQ - Main Entrance", "check_url": "https://via.placeholder.com/1x1"},
        "rtsp-002": {"name": "RBPD HQ - Parking Lot", "check_url": "https://via.placeholder.com/1x1"},
        "rtsp-003": {"name": "RBPD - Sector 1 Patrol", "check_url": "https://via.placeholder.com/1x1"},
        "rtsp-004": {"name": "RBPD - Sector 2 Intersection", "check_url": "https://via.placeholder.com/1x1"},
    },
    "fdot_mjpeg": {
        "fdot-stream-001": {"name": "I-95 @ Blue Heron Blvd", "check_url": "https://fl511.com/map/Cctv/CCTV-D4-I95-026.5-N--1"},
        "fdot-stream-002": {"name": "I-95 @ Palm Beach Lakes Blvd", "check_url": "https://fl511.com/map/Cctv/CCTV-D4-I95-021.0-N--1"},
        "fdot-stream-003": {"name": "Blue Heron @ Broadway (US-1)", "check_url": "https://fl511.com/map/Cctv/CCTV-D4-US1-076.0-N--1"},
        "fdot-stream-004": {"name": "I-95 @ 45th Street", "check_url": "https://fl511.com/map/Cctv/CCTV-D4-I95-028.0-N--1"},
        "fdot-stream-005": {"name": "Southern Blvd @ I-95", "check_url": "https://fl511.com/map/Cctv/CCTV-D4-I95-018.0-N--1"},
    }
}

# Global health status storage
health_status: Dict[str, Dict[str, dict]] = {
    network: {cam_id: {"status": "unknown", "last_check": None} for cam_id in cameras}
    for network, cameras in CAMERA_NETWORKS.items()
}

# WebSocket connections for real-time updates
active_connections: Set[WebSocket] = set()


async def check_camera_health(network: str, camera_id: str, check_url: str) -> dict:
    """Check health of a single camera"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            start = datetime.utcnow()
            response = await client.get(check_url, follow_redirects=True)
            latency = (datetime.utcnow() - start).total_seconds() * 1000
            
            if response.status_code == 200:
                status = "online"
            elif response.status_code in [301, 302, 307, 308]:
                status = "redirect"
            else:
                status = "degraded"
            
            return {
                "status": status,
                "last_check": datetime.utcnow().isoformat(),
                "latency_ms": int(latency),
                "http_status": response.status_code
            }
    except httpx.TimeoutException:
        return {
            "status": "timeout",
            "last_check": datetime.utcnow().isoformat(),
            "error": "Connection timeout"
        }
    except Exception as e:
        return {
            "status": "offline",
            "last_check": datetime.utcnow().isoformat(),
            "error": str(e)
        }


@router.get("/extended")
async def get_extended_health():
    """Get health status of all extended camera networks"""
    return {
        "networks": health_status,
        "summary": {
            network: {
                "total": len(cameras),
                "online": sum(1 for c in cameras.values() if c.get("status") == "online"),
                "offline": sum(1 for c in cameras.values() if c.get("status") == "offline"),
                "unknown": sum(1 for c in cameras.values() if c.get("status") == "unknown")
            }
            for network, cameras in health_status.items()
        },
        "last_updated": datetime.utcnow().isoformat()
    }


@router.get("/extended/{network}")
async def get_network_health(network: str):
    """Get health status of a specific camera network"""
    if network not in CAMERA_NETWORKS:
        return {"error": f"Unknown network: {network}", "available_networks": list(CAMERA_NETWORKS.keys())}
    
    return {
        "network": network,
        "cameras": health_status.get(network, {}),
        "summary": {
            "total": len(health_status.get(network, {})),
            "online": sum(1 for c in health_status.get(network, {}).values() if c.get("status") == "online"),
            "offline": sum(1 for c in health_status.get(network, {}).values() if c.get("status") == "offline")
        },
        "last_updated": datetime.utcnow().isoformat()
    }


@router.post("/extended/refresh")
async def refresh_extended_health():
    """Refresh health status of all extended camera networks"""
    results = {}
    
    for network, cameras in CAMERA_NETWORKS.items():
        results[network] = {}
        for cam_id, cam_info in cameras.items():
            health = await check_camera_health(network, cam_id, cam_info["check_url"])
            health_status[network][cam_id] = health
            results[network][cam_id] = health
    
    # Broadcast to WebSocket clients
    await broadcast_health_update(results)
    
    return {
        "message": "Health check completed",
        "results": results,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.post("/extended/refresh/{network}")
async def refresh_network_health(network: str):
    """Refresh health status of a specific camera network"""
    if network not in CAMERA_NETWORKS:
        return {"error": f"Unknown network: {network}", "available_networks": list(CAMERA_NETWORKS.keys())}
    
    results = {}
    for cam_id, cam_info in CAMERA_NETWORKS[network].items():
        health = await check_camera_health(network, cam_id, cam_info["check_url"])
        health_status[network][cam_id] = health
        results[cam_id] = health
    
    # Broadcast to WebSocket clients
    await broadcast_health_update({network: results})
    
    return {
        "network": network,
        "results": results,
        "timestamp": datetime.utcnow().isoformat()
    }


async def broadcast_health_update(data: dict):
    """Broadcast health update to all connected WebSocket clients"""
    if not active_connections:
        return
    
    message = json.dumps({
        "type": "health_update",
        "data": data,
        "timestamp": datetime.utcnow().isoformat()
    })
    
    disconnected = set()
    for connection in active_connections:
        try:
            await connection.send_text(message)
        except:
            disconnected.add(connection)
    
    # Remove disconnected clients
    active_connections.difference_update(disconnected)


@router.websocket("/ws/extended-health")
async def websocket_extended_health(websocket: WebSocket):
    """WebSocket endpoint for real-time camera health updates"""
    await websocket.accept()
    active_connections.add(websocket)
    
    try:
        # Send initial health status
        await websocket.send_text(json.dumps({
            "type": "initial_status",
            "data": health_status,
            "timestamp": datetime.utcnow().isoformat()
        }))
        
        # Keep connection alive and handle incoming messages
        while True:
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
                message = json.loads(data)
                
                if message.get("action") == "refresh":
                    network = message.get("network")
                    if network and network in CAMERA_NETWORKS:
                        results = {}
                        for cam_id, cam_info in CAMERA_NETWORKS[network].items():
                            health = await check_camera_health(network, cam_id, cam_info["check_url"])
                            health_status[network][cam_id] = health
                            results[cam_id] = health
                        await websocket.send_text(json.dumps({
                            "type": "refresh_result",
                            "network": network,
                            "data": results,
                            "timestamp": datetime.utcnow().isoformat()
                        }))
                    else:
                        # Refresh all networks
                        for net, cameras in CAMERA_NETWORKS.items():
                            for cam_id, cam_info in cameras.items():
                                health = await check_camera_health(net, cam_id, cam_info["check_url"])
                                health_status[net][cam_id] = health
                        await websocket.send_text(json.dumps({
                            "type": "refresh_result",
                            "data": health_status,
                            "timestamp": datetime.utcnow().isoformat()
                        }))
                
                elif message.get("action") == "ping":
                    await websocket.send_text(json.dumps({
                        "type": "pong",
                        "timestamp": datetime.utcnow().isoformat()
                    }))
                    
            except asyncio.TimeoutError:
                # Send heartbeat
                await websocket.send_text(json.dumps({
                    "type": "heartbeat",
                    "timestamp": datetime.utcnow().isoformat()
                }))
                
    except WebSocketDisconnect:
        pass
    finally:
        active_connections.discard(websocket)


@router.get("/summary")
async def get_health_summary():
    """Get summary of all camera network health"""
    total_cameras = 0
    total_online = 0
    total_offline = 0
    total_unknown = 0
    
    network_summaries = {}
    
    for network, cameras in health_status.items():
        online = sum(1 for c in cameras.values() if c.get("status") == "online")
        offline = sum(1 for c in cameras.values() if c.get("status") == "offline")
        unknown = sum(1 for c in cameras.values() if c.get("status") == "unknown")
        total = len(cameras)
        
        network_summaries[network] = {
            "total": total,
            "online": online,
            "offline": offline,
            "unknown": unknown,
            "health_percentage": round((online / total * 100) if total > 0 else 0, 1)
        }
        
        total_cameras += total
        total_online += online
        total_offline += offline
        total_unknown += unknown
    
    return {
        "overall": {
            "total_cameras": total_cameras,
            "online": total_online,
            "offline": total_offline,
            "unknown": total_unknown,
            "health_percentage": round((total_online / total_cameras * 100) if total_cameras > 0 else 0, 1)
        },
        "networks": network_summaries,
        "last_updated": datetime.utcnow().isoformat()
    }
