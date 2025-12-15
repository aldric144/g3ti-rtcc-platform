"""
Activity Log API - REST Endpoints for RTCC Logbook

Provides CJIS-compliant API endpoints for activity log management.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from fastapi.responses import PlainTextResponse

from .activity_log_model import (
    ActivityLog,
    ActivityLogCreate,
    ActivityLogUpdate,
    ActivityLogSearchParams,
    ActivityLogExportFormat,
    LogType,
    LogPriority,
)
from .activity_log_service import get_activity_log_service, ActivityLogService

router = APIRouter(prefix="/api/admin/logs", tags=["Admin Logs"])


def get_current_editor() -> str:
    """Get the current editor username from auth context."""
    # In production, this would come from JWT token
    # For SAFE_MODE, return demo user
    return "admin"


@router.get("", response_model=List[ActivityLog])
async def list_logs(
    keyword: Optional[str] = Query(None, description="Search keyword"),
    log_type: Optional[LogType] = Query(None, description="Filter by log type"),
    priority: Optional[LogPriority] = Query(None, description="Filter by priority"),
    editor: Optional[str] = Query(None, description="Filter by editor"),
    include_archived: bool = Query(False, description="Include archived logs"),
    limit: int = Query(50, ge=1, le=500, description="Maximum results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    service: ActivityLogService = Depends(get_activity_log_service),
):
    """List activity logs with optional filters."""
    params = ActivityLogSearchParams(
        keyword=keyword,
        log_type=log_type,
        priority=priority,
        editor=editor,
        include_archived=include_archived,
        limit=limit,
        offset=offset,
    )
    return await service.search_logs(params)


@router.post("", response_model=ActivityLog, status_code=201)
async def create_log(
    data: ActivityLogCreate,
    service: ActivityLogService = Depends(get_activity_log_service),
    editor: str = Depends(get_current_editor),
):
    """Create a new activity log entry."""
    return await service.create_log(data, editor)


@router.get("/export")
async def export_logs(
    format: ActivityLogExportFormat = Query(ActivityLogExportFormat.JSON, description="Export format"),
    keyword: Optional[str] = Query(None, description="Search keyword"),
    log_type: Optional[LogType] = Query(None, description="Filter by log type"),
    priority: Optional[LogPriority] = Query(None, description="Filter by priority"),
    include_archived: bool = Query(False, description="Include archived logs"),
    service: ActivityLogService = Depends(get_activity_log_service),
):
    """Export activity logs in JSON or CSV format."""
    params = ActivityLogSearchParams(
        keyword=keyword,
        log_type=log_type,
        priority=priority,
        include_archived=include_archived,
        limit=10000,  # Allow larger exports
    )
    
    content = await service.export_logs(format, params)
    
    if format == ActivityLogExportFormat.CSV:
        return Response(
            content=content,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=activity_logs.csv"}
        )
    
    return Response(
        content=content,
        media_type="application/json",
        headers={"Content-Disposition": "attachment; filename=activity_logs.json"}
    )


@router.get("/{log_id}", response_model=ActivityLog)
async def get_log(
    log_id: str,
    service: ActivityLogService = Depends(get_activity_log_service),
):
    """Get a specific activity log by ID."""
    log = await service.get_log(log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Activity log not found")
    return log


@router.patch("/{log_id}", response_model=ActivityLog)
async def update_log(
    log_id: str,
    data: ActivityLogUpdate,
    service: ActivityLogService = Depends(get_activity_log_service),
    editor: str = Depends(get_current_editor),
):
    """Update an existing activity log entry."""
    log = await service.update_log(log_id, data, editor)
    if not log:
        raise HTTPException(status_code=404, detail="Activity log not found")
    return log


@router.delete("/{log_id}", status_code=204)
async def delete_log(
    log_id: str,
    service: ActivityLogService = Depends(get_activity_log_service),
    editor: str = Depends(get_current_editor),
):
    """Delete an activity log entry."""
    success = await service.delete_log(log_id, editor)
    if not success:
        raise HTTPException(status_code=404, detail="Activity log not found")
    return None


@router.post("/{log_id}/archive", response_model=ActivityLog)
async def archive_log(
    log_id: str,
    service: ActivityLogService = Depends(get_activity_log_service),
    editor: str = Depends(get_current_editor),
):
    """Archive an activity log entry."""
    log = await service.archive_log(log_id, editor)
    if not log:
        raise HTTPException(status_code=404, detail="Activity log not found")
    return log


@router.get("/{log_id}/audit")
async def get_log_audit_trail(
    log_id: str,
    service: ActivityLogService = Depends(get_activity_log_service),
):
    """Get the audit trail for a specific log entry."""
    log = await service.get_log(log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Activity log not found")
    return await service.get_audit_trail(log_id)
