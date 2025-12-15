"""
Activity Log Service - Business Logic for RTCC Logbook

Provides CRUD operations and search/export functionality for activity logs.
"""

from datetime import datetime, UTC
from typing import List, Optional, Dict, Any
import json
import csv
import io
import structlog

from .activity_log_model import (
    ActivityLog,
    ActivityLogCreate,
    ActivityLogUpdate,
    ActivityLogSearchParams,
    ActivityLogExportFormat,
    LogType,
    LogPriority,
)

logger = structlog.get_logger(__name__)


class ActivityLogService:
    """Service for managing RTCC activity logs."""
    
    def __init__(self):
        # In-memory storage for SAFE_MODE operation
        # Will be replaced with database storage when connected
        self._logs: Dict[str, ActivityLog] = {}
        self._audit_trail: List[Dict[str, Any]] = []
    
    def _add_audit_entry(self, action: str, log_id: str, editor: str, details: Optional[str] = None):
        """Add an entry to the audit trail."""
        self._audit_trail.append({
            "timestamp": datetime.now(UTC).isoformat(),
            "action": action,
            "log_id": log_id,
            "editor": editor,
            "details": details,
        })
    
    async def create_log(self, data: ActivityLogCreate, editor: str) -> ActivityLog:
        """Create a new activity log entry."""
        log = ActivityLog(
            log_type=data.log_type,
            priority=data.priority,
            notes=data.notes,
            tags=data.tags,
            editor=editor,
        )
        
        self._logs[log.id] = log
        self._add_audit_entry("CREATE", log.id, editor, f"Created {data.log_type.value} log")
        
        logger.info("activity_log_created", log_id=log.id, log_type=data.log_type.value, editor=editor)
        return log
    
    async def get_log(self, log_id: str) -> Optional[ActivityLog]:
        """Get a specific activity log by ID."""
        return self._logs.get(log_id)
    
    async def update_log(self, log_id: str, data: ActivityLogUpdate, editor: str) -> Optional[ActivityLog]:
        """Update an existing activity log entry."""
        log = self._logs.get(log_id)
        if not log:
            return None
        
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(log, field, value)
        
        log.updated_at = datetime.now(UTC)
        self._logs[log_id] = log
        
        self._add_audit_entry("UPDATE", log_id, editor, f"Updated fields: {list(update_data.keys())}")
        logger.info("activity_log_updated", log_id=log_id, editor=editor)
        
        return log
    
    async def archive_log(self, log_id: str, editor: str) -> Optional[ActivityLog]:
        """Archive an activity log entry."""
        log = self._logs.get(log_id)
        if not log:
            return None
        
        log.archived = True
        log.updated_at = datetime.now(UTC)
        self._logs[log_id] = log
        
        self._add_audit_entry("ARCHIVE", log_id, editor)
        logger.info("activity_log_archived", log_id=log_id, editor=editor)
        
        return log
    
    async def delete_log(self, log_id: str, editor: str) -> bool:
        """Permanently delete an activity log entry."""
        if log_id not in self._logs:
            return False
        
        del self._logs[log_id]
        self._add_audit_entry("DELETE", log_id, editor)
        logger.info("activity_log_deleted", log_id=log_id, editor=editor)
        
        return True
    
    async def search_logs(self, params: ActivityLogSearchParams) -> List[ActivityLog]:
        """Search activity logs with filters."""
        results = []
        
        for log in self._logs.values():
            # Filter by archived status
            if not params.include_archived and log.archived:
                continue
            
            # Filter by log type
            if params.log_type and log.log_type != params.log_type:
                continue
            
            # Filter by priority
            if params.priority and log.priority != params.priority:
                continue
            
            # Filter by editor
            if params.editor and log.editor != params.editor:
                continue
            
            # Filter by date range
            if params.start_date and log.created_at < params.start_date:
                continue
            if params.end_date and log.created_at > params.end_date:
                continue
            
            # Filter by keyword
            if params.keyword:
                keyword_lower = params.keyword.lower()
                if keyword_lower not in log.notes.lower():
                    # Check tags
                    if not any(keyword_lower in tag.lower() for tag in log.tags):
                        continue
            
            results.append(log)
        
        # Sort by created_at descending
        results.sort(key=lambda x: x.created_at, reverse=True)
        
        # Apply pagination
        return results[params.offset:params.offset + params.limit]
    
    async def get_all_logs(self, include_archived: bool = False) -> List[ActivityLog]:
        """Get all activity logs."""
        logs = list(self._logs.values())
        if not include_archived:
            logs = [log for log in logs if not log.archived]
        logs.sort(key=lambda x: x.created_at, reverse=True)
        return logs
    
    async def export_logs(
        self,
        format: ActivityLogExportFormat,
        params: Optional[ActivityLogSearchParams] = None
    ) -> str:
        """Export activity logs in the specified format."""
        if params:
            logs = await self.search_logs(params)
        else:
            logs = await self.get_all_logs()
        
        if format == ActivityLogExportFormat.JSON:
            return json.dumps([log.model_dump(mode="json") for log in logs], indent=2, default=str)
        
        elif format == ActivityLogExportFormat.CSV:
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Header
            writer.writerow([
                "ID", "Type", "Priority", "Notes", "Tags", "Editor",
                "Created At", "Updated At", "Archived"
            ])
            
            # Data rows
            for log in logs:
                writer.writerow([
                    log.id,
                    log.log_type.value,
                    log.priority.value,
                    log.notes,
                    ";".join(log.tags),
                    log.editor,
                    log.created_at.isoformat(),
                    log.updated_at.isoformat(),
                    log.archived,
                ])
            
            return output.getvalue()
        
        raise ValueError(f"Unsupported export format: {format}")
    
    async def get_audit_trail(self, log_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get audit trail entries, optionally filtered by log ID."""
        if log_id:
            return [entry for entry in self._audit_trail if entry["log_id"] == log_id]
        return self._audit_trail.copy()


# Singleton instance for SAFE_MODE operation
_activity_log_service: Optional[ActivityLogService] = None


def get_activity_log_service() -> ActivityLogService:
    """Get the activity log service instance."""
    global _activity_log_service
    if _activity_log_service is None:
        _activity_log_service = ActivityLogService()
    return _activity_log_service
