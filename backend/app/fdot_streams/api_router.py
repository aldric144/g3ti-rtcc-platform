"""
FDOT Streams API Router.

Provides REST API endpoints for FDOT live streaming:
- GET /api/fdot/list - List all FDOT stream cameras
- GET /api/fdot/stream/{camera_id} - Stream camera feed
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional

from app.fdot_streams.fdot_catalog import (
    get_all_cameras,
    get_camera_by_id,
)
from app.fdot_streams.fdot_proxy import (
    proxy_camera_stream,
    get_stream_content_type,
    fetch_snapshot,
)


router = APIRouter(prefix="/fdot", tags=["FDOT Streams"])


class FDOTStreamCamera(BaseModel):
    id: str
    name: str
    location: str
    lat: float
    lng: float
    stream_url: str
    description: str = ""


class FDOTStreamListResponse(BaseModel):
    cameras: List[dict]
    total: int


@router.get("/list", response_model=FDOTStreamListResponse)
async def list_fdot_streams() -> FDOTStreamListResponse:
    cameras = get_all_cameras()
    return FDOTStreamListResponse(
        cameras=cameras,
        total=len(cameras),
    )


@router.get("/stream/{camera_id}")
async def stream_fdot_camera(camera_id: str) -> StreamingResponse:
    camera = get_camera_by_id(camera_id)
    
    if not camera:
        raise HTTPException(
            status_code=404,
            detail=f"FDOT stream camera not found: {camera_id}"
        )
    
    content_type = await get_stream_content_type(camera_id)
    
    return StreamingResponse(
        proxy_camera_stream(camera_id),
        media_type=content_type,
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
            "Access-Control-Allow-Origin": "*",
        }
    )


@router.get("/snapshot/{camera_id}")
async def get_fdot_snapshot(camera_id: str) -> StreamingResponse:
    camera = get_camera_by_id(camera_id)
    
    if not camera:
        raise HTTPException(
            status_code=404,
            detail=f"FDOT stream camera not found: {camera_id}"
        )
    
    snapshot = await fetch_snapshot(camera_id)
    
    if not snapshot:
        raise HTTPException(
            status_code=503,
            detail=f"Snapshot not available for camera: {camera_id}"
        )
    
    return StreamingResponse(
        iter([snapshot]),
        media_type="image/jpeg",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Access-Control-Allow-Origin": "*",
        }
    )


@router.get("/{camera_id}")
async def get_fdot_camera(camera_id: str) -> dict:
    camera = get_camera_by_id(camera_id)
    
    if not camera:
        raise HTTPException(
            status_code=404,
            detail=f"FDOT stream camera not found: {camera_id}"
        )
    
    return camera
