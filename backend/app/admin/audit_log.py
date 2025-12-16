"""
Audit Log Module - Comprehensive audit logging for all admin operations
"""

from datetime import datetime, UTC
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
import uuid
import json


class AuditAction(str, Enum):
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    LOGOUT = "logout"
    EXPORT = "export"
    IMPORT = "import"
    APPROVE = "approve"
    REJECT = "reject"
    ENCRYPT = "encrypt"
    DECRYPT = "decrypt"


class AuditLogEntry(BaseModel):
    """Audit log entry model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    user_id: str
    username: Optional[str] = None
    action: AuditAction
    table_name: str
    record_id: Optional[str] = None
    before_snapshot: Optional[Dict[str, Any]] = None
    after_snapshot: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    session_id: Optional[str] = None
    success: bool = True
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class AuditLogger:
    """Centralized audit logging service"""
    
    _instance = None
    _logs: List[AuditLogEntry] = []
    _max_logs: int = 100000  # Maximum logs to keep in memory
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._logs = []
        self._initialized = True
    
    def log(
        self,
        user_id: str,
        action: AuditAction,
        table_name: str,
        record_id: Optional[str] = None,
        before: Optional[Any] = None,
        after: Optional[Any] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        session_id: Optional[str] = None,
        success: bool = True,
        error_message: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        username: Optional[str] = None,
    ) -> AuditLogEntry:
        """Log an audit event"""
        
        # Convert objects to dictionaries for snapshots
        before_snapshot = None
        after_snapshot = None
        
        if before is not None:
            if hasattr(before, 'model_dump'):
                before_snapshot = before.model_dump()
            elif isinstance(before, dict):
                before_snapshot = before
            else:
                before_snapshot = {"value": str(before)}
        
        if after is not None:
            if hasattr(after, 'model_dump'):
                after_snapshot = after.model_dump()
            elif isinstance(after, dict):
                after_snapshot = after
            else:
                after_snapshot = {"value": str(after)}
        
        # Sanitize sensitive data from snapshots
        before_snapshot = self._sanitize_snapshot(before_snapshot)
        after_snapshot = self._sanitize_snapshot(after_snapshot)
        
        entry = AuditLogEntry(
            user_id=user_id,
            username=username,
            action=action,
            table_name=table_name,
            record_id=record_id,
            before_snapshot=before_snapshot,
            after_snapshot=after_snapshot,
            ip_address=ip_address,
            user_agent=user_agent,
            session_id=session_id,
            success=success,
            error_message=error_message,
            metadata=metadata,
        )
        
        self._logs.append(entry)
        
        # Trim logs if exceeding max
        if len(self._logs) > self._max_logs:
            self._logs = self._logs[-self._max_logs:]
        
        return entry
    
    def _sanitize_snapshot(self, snapshot: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Remove sensitive data from snapshots"""
        if snapshot is None:
            return None
        
        sensitive_keys = [
            'password', 'password_hash', 'api_key', 'encrypted_key', 
            'mfa_secret', 'token', 'secret', 'credential'
        ]
        
        sanitized = {}
        for key, value in snapshot.items():
            if any(s in key.lower() for s in sensitive_keys):
                sanitized[key] = "[REDACTED]"
            elif isinstance(value, dict):
                sanitized[key] = self._sanitize_snapshot(value)
            else:
                sanitized[key] = value
        
        return sanitized
    
    def log_create(
        self,
        user_id: str,
        table_name: str,
        record_id: str,
        data: Any,
        **kwargs
    ) -> AuditLogEntry:
        """Log a create operation"""
        return self.log(
            user_id=user_id,
            action=AuditAction.CREATE,
            table_name=table_name,
            record_id=record_id,
            after=data,
            **kwargs
        )
    
    def log_update(
        self,
        user_id: str,
        table_name: str,
        record_id: str,
        before: Any,
        after: Any,
        **kwargs
    ) -> AuditLogEntry:
        """Log an update operation"""
        return self.log(
            user_id=user_id,
            action=AuditAction.UPDATE,
            table_name=table_name,
            record_id=record_id,
            before=before,
            after=after,
            **kwargs
        )
    
    def log_delete(
        self,
        user_id: str,
        table_name: str,
        record_id: str,
        data: Any,
        **kwargs
    ) -> AuditLogEntry:
        """Log a delete operation"""
        return self.log(
            user_id=user_id,
            action=AuditAction.DELETE,
            table_name=table_name,
            record_id=record_id,
            before=data,
            **kwargs
        )
    
    def log_read(
        self,
        user_id: str,
        table_name: str,
        record_id: Optional[str] = None,
        **kwargs
    ) -> AuditLogEntry:
        """Log a read operation"""
        return self.log(
            user_id=user_id,
            action=AuditAction.READ,
            table_name=table_name,
            record_id=record_id,
            **kwargs
        )
    
    def log_login(
        self,
        user_id: str,
        success: bool = True,
        error_message: Optional[str] = None,
        **kwargs
    ) -> AuditLogEntry:
        """Log a login attempt"""
        return self.log(
            user_id=user_id,
            action=AuditAction.LOGIN,
            table_name="users",
            success=success,
            error_message=error_message,
            **kwargs
        )
    
    def log_logout(self, user_id: str, **kwargs) -> AuditLogEntry:
        """Log a logout"""
        return self.log(
            user_id=user_id,
            action=AuditAction.LOGOUT,
            table_name="users",
            **kwargs
        )
    
    def get_logs(
        self,
        user_id: Optional[str] = None,
        action: Optional[AuditAction] = None,
        table_name: Optional[str] = None,
        record_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        success: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[AuditLogEntry]:
        """Query audit logs with filters"""
        filtered = self._logs
        
        if user_id:
            filtered = [l for l in filtered if l.user_id == user_id]
        
        if action:
            filtered = [l for l in filtered if l.action == action]
        
        if table_name:
            filtered = [l for l in filtered if l.table_name == table_name]
        
        if record_id:
            filtered = [l for l in filtered if l.record_id == record_id]
        
        if start_time:
            filtered = [l for l in filtered if l.timestamp >= start_time]
        
        if end_time:
            filtered = [l for l in filtered if l.timestamp <= end_time]
        
        if success is not None:
            filtered = [l for l in filtered if l.success == success]
        
        # Sort by timestamp descending (newest first)
        filtered.sort(key=lambda x: x.timestamp, reverse=True)
        
        return filtered[skip:skip + limit]
    
    def get_log_by_id(self, log_id: str) -> Optional[AuditLogEntry]:
        """Get a specific audit log entry"""
        for log in self._logs:
            if log.id == log_id:
                return log
        return None
    
    def get_user_activity(self, user_id: str, limit: int = 50) -> List[AuditLogEntry]:
        """Get recent activity for a specific user"""
        return self.get_logs(user_id=user_id, limit=limit)
    
    def get_record_history(self, table_name: str, record_id: str) -> List[AuditLogEntry]:
        """Get complete history for a specific record"""
        return self.get_logs(table_name=table_name, record_id=record_id, limit=1000)
    
    def get_failed_operations(self, limit: int = 100) -> List[AuditLogEntry]:
        """Get recent failed operations"""
        return self.get_logs(success=False, limit=limit)
    
    def count_logs(
        self,
        user_id: Optional[str] = None,
        action: Optional[AuditAction] = None,
        table_name: Optional[str] = None,
    ) -> int:
        """Count audit logs matching filters"""
        return len(self.get_logs(
            user_id=user_id,
            action=action,
            table_name=table_name,
            limit=self._max_logs
        ))
    
    def export_logs(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> str:
        """Export logs as JSON"""
        logs = self.get_logs(start_time=start_time, end_time=end_time, limit=self._max_logs)
        return json.dumps([l.model_dump() for l in logs], default=str, indent=2)
    
    def clear_old_logs(self, days: int = 90) -> int:
        """Clear logs older than specified days"""
        from datetime import timedelta
        cutoff = datetime.now(UTC) - timedelta(days=days)
        original_count = len(self._logs)
        self._logs = [l for l in self._logs if l.timestamp >= cutoff]
        return original_count - len(self._logs)


# Singleton instance
audit_logger = AuditLogger()
