"""
Operations Audit Log Module for G3TI RTCC-UIP Operational Continuity.

Provides CJIS-aligned operational audit trail for all continuity events
with retention policy hooks and compliance reporting.
"""

import asyncio
from datetime import datetime, timezone, timedelta
from enum import Enum
from typing import Any, Optional
from collections import deque
import uuid
import hashlib
import json

from pydantic import BaseModel, Field


class OpsAuditAction(str, Enum):
    """Operations audit action types."""
    HEALTH_CHECK_STARTED = "health_check_started"
    HEALTH_CHECK_COMPLETED = "health_check_completed"
    HEALTH_CHECK_FAILED = "health_check_failed"

    SERVICE_HEALTHY = "service_healthy"
    SERVICE_DEGRADED = "service_degraded"
    SERVICE_UNHEALTHY = "service_unhealthy"
    SERVICE_OFFLINE = "service_offline"
    SERVICE_RECOVERED = "service_recovered"

    FAILOVER_TRIGGERED = "failover_triggered"
    FAILOVER_ACTIVATED = "failover_activated"
    FAILOVER_COMPLETED = "failover_completed"
    FAILOVER_FAILED = "failover_failed"
    RECOVERY_STARTED = "recovery_started"
    RECOVERY_COMPLETED = "recovery_completed"

    REDUNDANCY_SYNC_STARTED = "redundancy_sync_started"
    REDUNDANCY_SYNC_COMPLETED = "redundancy_sync_completed"
    REDUNDANCY_SYNC_FAILED = "redundancy_sync_failed"
    CONNECTION_POOL_CREATED = "connection_pool_created"
    CONNECTION_POOL_FAILOVER = "connection_pool_failover"

    DIAGNOSTIC_EVENT = "diagnostic_event"
    SLOW_QUERY_DETECTED = "slow_query_detected"
    PREDICTIVE_ALERT = "predictive_alert"
    ERROR_CLASSIFIED = "error_classified"

    ESCALATION_TRIGGERED = "escalation_triggered"
    ALERT_SENT = "alert_sent"
    ALERT_ACKNOWLEDGED = "alert_acknowledged"

    CONFIG_CHANGED = "config_changed"
    MANUAL_INTERVENTION = "manual_intervention"
    SYSTEM_STARTUP = "system_startup"
    SYSTEM_SHUTDOWN = "system_shutdown"
    GRACEFUL_SHUTDOWN = "graceful_shutdown"


class OpsAuditSeverity(str, Enum):
    """Audit entry severity levels."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class OpsAuditEntry(BaseModel):
    """A single operations audit entry."""
    entry_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    action: OpsAuditAction
    severity: OpsAuditSeverity = OpsAuditSeverity.INFO
    source: str
    target: Optional[str] = None
    user_id: Optional[str] = None
    user_name: Optional[str] = None
    description: str
    details: dict[str, Any] = Field(default_factory=dict)
    outcome: str = "success"
    duration_ms: Optional[float] = None
    correlation_id: Optional[str] = None
    session_id: Optional[str] = None
    entry_hash: Optional[str] = None
    previous_entry_hash: Optional[str] = None

    def calculate_hash(self) -> str:
        """Calculate hash for this entry."""
        data = {
            "entry_id": self.entry_id,
            "timestamp": self.timestamp.isoformat(),
            "action": self.action.value,
            "source": self.source,
            "description": self.description,
            "previous_hash": self.previous_entry_hash,
        }
        return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()


class OpsAuditConfig(BaseModel):
    """Configuration for operations audit log."""
    enabled: bool = True
    log_to_file: bool = True
    log_to_database: bool = True
    retention_days: int = 2555
    batch_size: int = 100
    flush_interval_seconds: float = 5.0
    enable_chain_verification: bool = True
    include_entry_hash: bool = True
    max_entries_in_memory: int = 10000

    log_file_path: str = "/var/log/rtcc/ops_audit.log"
    database_table: str = "ops_audit_log"

    sensitive_fields: list[str] = Field(default_factory=lambda: [
        "password", "token", "api_key", "secret", "credential",
    ])


class OpsAuditMetrics(BaseModel):
    """Metrics for operations audit log."""
    entries_logged: int = 0
    entries_by_action: dict[str, int] = Field(default_factory=dict)
    entries_by_severity: dict[str, int] = Field(default_factory=dict)
    entries_flushed: int = 0
    flush_errors: int = 0
    chain_verified: bool = True
    last_entry: Optional[datetime] = None
    last_flush: Optional[datetime] = None


class OpsAuditLog:
    """
    CJIS-aligned operations audit log for RTCC continuity events.

    Provides comprehensive logging of all operational events with
    chain verification, retention policies, and compliance reporting.
    """

    def __init__(self, config: Optional[OpsAuditConfig] = None):
        self.config = config or OpsAuditConfig()
        self.metrics = OpsAuditMetrics()
        self._running = False
        self._flush_task: Optional[asyncio.Task] = None
        self._entries: deque[OpsAuditEntry] = deque(maxlen=self.config.max_entries_in_memory)
        self._buffer: list[OpsAuditEntry] = []
        self._last_entry_hash: Optional[str] = None
        self._session_id = str(uuid.uuid4())

    async def start(self) -> None:
        """Start the audit log service."""
        if self._running:
            return

        self._running = True
        self._flush_task = asyncio.create_task(self._flush_loop())

        await self.log_entry(
            action=OpsAuditAction.SYSTEM_STARTUP,
            source="ops_audit_log",
            description="Operations audit log service started",
        )

    async def stop(self) -> None:
        """Stop the audit log service."""
        await self.log_entry(
            action=OpsAuditAction.SYSTEM_SHUTDOWN,
            source="ops_audit_log",
            description="Operations audit log service stopping",
        )

        self._running = False

        if self._flush_task:
            self._flush_task.cancel()
            try:
                await self._flush_task
            except asyncio.CancelledError:
                pass

        await self._flush_buffer()

    async def _flush_loop(self) -> None:
        """Background loop to flush buffered entries."""
        while self._running:
            try:
                await asyncio.sleep(self.config.flush_interval_seconds)
                await self._flush_buffer()
            except asyncio.CancelledError:
                break
            except Exception:
                self.metrics.flush_errors += 1

    async def _flush_buffer(self) -> None:
        """Flush buffered entries to storage."""
        if not self._buffer:
            return

        entries_to_flush = self._buffer.copy()
        self._buffer.clear()

        if self.config.log_to_file:
            await self._write_to_file(entries_to_flush)

        if self.config.log_to_database:
            await self._write_to_database(entries_to_flush)

        self.metrics.entries_flushed += len(entries_to_flush)
        self.metrics.last_flush = datetime.now(timezone.utc)

    async def _write_to_file(self, entries: list[OpsAuditEntry]) -> None:
        """Write entries to log file."""
        pass

    async def _write_to_database(self, entries: list[OpsAuditEntry]) -> None:
        """Write entries to database."""
        pass

    async def log_entry(
        self,
        action: OpsAuditAction,
        source: str,
        description: str,
        severity: OpsAuditSeverity = OpsAuditSeverity.INFO,
        target: Optional[str] = None,
        user_id: Optional[str] = None,
        user_name: Optional[str] = None,
        details: Optional[dict[str, Any]] = None,
        outcome: str = "success",
        duration_ms: Optional[float] = None,
        correlation_id: Optional[str] = None,
    ) -> OpsAuditEntry:
        """Log an operations audit entry."""
        if not self.config.enabled:
            return OpsAuditEntry(
                action=action,
                source=source,
                description=description,
            )

        masked_details = self._mask_sensitive_data(details or {})

        entry = OpsAuditEntry(
            action=action,
            severity=severity,
            source=source,
            target=target,
            user_id=user_id,
            user_name=user_name,
            description=description,
            details=masked_details,
            outcome=outcome,
            duration_ms=duration_ms,
            correlation_id=correlation_id,
            session_id=self._session_id,
            previous_entry_hash=self._last_entry_hash,
        )

        if self.config.include_entry_hash:
            entry.entry_hash = entry.calculate_hash()
            self._last_entry_hash = entry.entry_hash

        self._entries.append(entry)
        self._buffer.append(entry)
        self._update_metrics(entry)

        if len(self._buffer) >= self.config.batch_size:
            await self._flush_buffer()

        return entry

    async def log_health_check(
        self,
        service_name: str,
        status: str,
        latency_ms: float,
        details: Optional[dict[str, Any]] = None,
    ) -> OpsAuditEntry:
        """Log a health check result."""
        action = OpsAuditAction.HEALTH_CHECK_COMPLETED
        severity = OpsAuditSeverity.INFO

        if status == "unhealthy":
            action = OpsAuditAction.SERVICE_UNHEALTHY
            severity = OpsAuditSeverity.ERROR
        elif status == "degraded":
            action = OpsAuditAction.SERVICE_DEGRADED
            severity = OpsAuditSeverity.WARNING
        elif status == "offline":
            action = OpsAuditAction.SERVICE_OFFLINE
            severity = OpsAuditSeverity.CRITICAL

        return await self.log_entry(
            action=action,
            source="health_check_service",
            target=service_name,
            description=f"Health check for {service_name}: {status}",
            severity=severity,
            details={
                "status": status,
                "latency_ms": latency_ms,
                **(details or {}),
            },
            duration_ms=latency_ms,
        )

    async def log_failover(
        self,
        service_type: str,
        from_target: str,
        to_target: str,
        reason: str,
        auto_triggered: bool = True,
        user_id: Optional[str] = None,
    ) -> OpsAuditEntry:
        """Log a failover event."""
        return await self.log_entry(
            action=OpsAuditAction.FAILOVER_TRIGGERED,
            source="failover_manager",
            target=service_type,
            description=f"Failover triggered for {service_type}: {from_target} -> {to_target}",
            severity=OpsAuditSeverity.WARNING,
            user_id=user_id,
            details={
                "service_type": service_type,
                "from_target": from_target,
                "to_target": to_target,
                "reason": reason,
                "auto_triggered": auto_triggered,
            },
        )

    async def log_recovery(
        self,
        service_type: str,
        recovery_time_seconds: float,
        details: Optional[dict[str, Any]] = None,
    ) -> OpsAuditEntry:
        """Log a service recovery."""
        return await self.log_entry(
            action=OpsAuditAction.RECOVERY_COMPLETED,
            source="failover_manager",
            target=service_type,
            description=f"Service {service_type} recovered after {recovery_time_seconds:.1f}s",
            severity=OpsAuditSeverity.INFO,
            details={
                "service_type": service_type,
                "recovery_time_seconds": recovery_time_seconds,
                **(details or {}),
            },
            duration_ms=recovery_time_seconds * 1000,
        )

    async def log_redundancy_sync(
        self,
        pool_name: str,
        sync_type: str,
        success: bool,
        duration_ms: float,
        data_size_bytes: int = 0,
    ) -> OpsAuditEntry:
        """Log a redundancy sync operation."""
        action = OpsAuditAction.REDUNDANCY_SYNC_COMPLETED if success else OpsAuditAction.REDUNDANCY_SYNC_FAILED
        severity = OpsAuditSeverity.INFO if success else OpsAuditSeverity.ERROR

        return await self.log_entry(
            action=action,
            source="redundancy_manager",
            target=pool_name,
            description=f"Redundancy sync for {pool_name}: {'success' if success else 'failed'}",
            severity=severity,
            outcome="success" if success else "failure",
            details={
                "pool_name": pool_name,
                "sync_type": sync_type,
                "data_size_bytes": data_size_bytes,
            },
            duration_ms=duration_ms,
        )

    async def log_diagnostic_event(
        self,
        category: str,
        severity: str,
        source: str,
        message: str,
        error_code: Optional[str] = None,
    ) -> OpsAuditEntry:
        """Log a diagnostic event."""
        audit_severity = OpsAuditSeverity.INFO
        if severity == "error":
            audit_severity = OpsAuditSeverity.ERROR
        elif severity == "critical":
            audit_severity = OpsAuditSeverity.CRITICAL
        elif severity == "warning":
            audit_severity = OpsAuditSeverity.WARNING

        return await self.log_entry(
            action=OpsAuditAction.DIAGNOSTIC_EVENT,
            source=source,
            description=message,
            severity=audit_severity,
            details={
                "category": category,
                "diagnostic_severity": severity,
                "error_code": error_code,
            },
        )

    async def log_escalation(
        self,
        trigger: str,
        severity: str,
        destinations: list[str],
        details: Optional[dict[str, Any]] = None,
    ) -> OpsAuditEntry:
        """Log an escalation event."""
        return await self.log_entry(
            action=OpsAuditAction.ESCALATION_TRIGGERED,
            source="escalation_engine",
            description=f"Escalation triggered: {trigger}",
            severity=OpsAuditSeverity.WARNING,
            details={
                "trigger": trigger,
                "escalation_severity": severity,
                "destinations": destinations,
                **(details or {}),
            },
        )

    async def log_config_change(
        self,
        config_type: str,
        changed_by: str,
        old_value: Any,
        new_value: Any,
    ) -> OpsAuditEntry:
        """Log a configuration change."""
        return await self.log_entry(
            action=OpsAuditAction.CONFIG_CHANGED,
            source="config_manager",
            target=config_type,
            description=f"Configuration changed: {config_type}",
            severity=OpsAuditSeverity.WARNING,
            user_id=changed_by,
            details={
                "config_type": config_type,
                "old_value": str(old_value),
                "new_value": str(new_value),
            },
        )

    async def log_manual_intervention(
        self,
        action_type: str,
        user_id: str,
        user_name: str,
        description: str,
        details: Optional[dict[str, Any]] = None,
    ) -> OpsAuditEntry:
        """Log a manual intervention."""
        return await self.log_entry(
            action=OpsAuditAction.MANUAL_INTERVENTION,
            source="manual",
            description=description,
            severity=OpsAuditSeverity.WARNING,
            user_id=user_id,
            user_name=user_name,
            details={
                "action_type": action_type,
                **(details or {}),
            },
        )

    def _mask_sensitive_data(self, data: dict[str, Any]) -> dict[str, Any]:
        """Mask sensitive data in details."""
        masked = {}
        for key, value in data.items():
            if any(sensitive in key.lower() for sensitive in self.config.sensitive_fields):
                masked[key] = "***MASKED***"
            elif isinstance(value, dict):
                masked[key] = self._mask_sensitive_data(value)
            else:
                masked[key] = value
        return masked

    def _update_metrics(self, entry: OpsAuditEntry) -> None:
        """Update metrics from entry."""
        self.metrics.entries_logged += 1
        self.metrics.last_entry = entry.timestamp

        action = entry.action.value
        self.metrics.entries_by_action[action] = self.metrics.entries_by_action.get(action, 0) + 1

        severity = entry.severity.value
        self.metrics.entries_by_severity[severity] = self.metrics.entries_by_severity.get(severity, 0) + 1

    async def verify_chain_integrity(self) -> bool:
        """Verify the integrity of the audit chain."""
        if not self.config.enable_chain_verification:
            return True

        entries = list(self._entries)
        if len(entries) < 2:
            return True

        for i in range(1, len(entries)):
            current = entries[i]
            previous = entries[i - 1]

            if current.previous_entry_hash != previous.entry_hash:
                self.metrics.chain_verified = False
                return False

        self.metrics.chain_verified = True
        return True

    def get_entries(
        self,
        action: Optional[OpsAuditAction] = None,
        severity: Optional[OpsAuditSeverity] = None,
        source: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100,
    ) -> list[OpsAuditEntry]:
        """Get audit entries with optional filtering."""
        entries = list(self._entries)

        if action:
            entries = [e for e in entries if e.action == action]

        if severity:
            entries = [e for e in entries if e.severity == severity]

        if source:
            entries = [e for e in entries if e.source == source]

        if start_time:
            entries = [e for e in entries if e.timestamp >= start_time]

        if end_time:
            entries = [e for e in entries if e.timestamp <= end_time]

        return entries[-limit:]

    def generate_compliance_report(
        self,
        start_time: datetime,
        end_time: datetime,
        report_type: str = "cjis",
    ) -> dict[str, Any]:
        """Generate a compliance report."""
        entries = self.get_entries(
            start_time=start_time,
            end_time=end_time,
            limit=10000,
        )

        action_counts = {}
        severity_counts = {}
        source_counts = {}

        for entry in entries:
            action_counts[entry.action.value] = action_counts.get(entry.action.value, 0) + 1
            severity_counts[entry.severity.value] = severity_counts.get(entry.severity.value, 0) + 1
            source_counts[entry.source] = source_counts.get(entry.source, 0) + 1

        failover_events = [e for e in entries if "failover" in e.action.value.lower()]
        recovery_events = [e for e in entries if "recovery" in e.action.value.lower()]
        critical_events = [e for e in entries if e.severity == OpsAuditSeverity.CRITICAL]

        return {
            "report_type": report_type,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "period": {
                "start": start_time.isoformat(),
                "end": end_time.isoformat(),
            },
            "summary": {
                "total_entries": len(entries),
                "failover_events": len(failover_events),
                "recovery_events": len(recovery_events),
                "critical_events": len(critical_events),
                "chain_integrity_verified": self.metrics.chain_verified,
            },
            "entries_by_action": action_counts,
            "entries_by_severity": severity_counts,
            "entries_by_source": source_counts,
            "compliance_status": "compliant" if self.metrics.chain_verified else "review_required",
            "retention_policy": {
                "retention_days": self.config.retention_days,
                "entries_in_memory": len(self._entries),
            },
        }

    def get_status(self) -> dict[str, Any]:
        """Get audit log status."""
        return {
            "running": self._running,
            "entries_in_memory": len(self._entries),
            "buffer_size": len(self._buffer),
            "session_id": self._session_id,
            "chain_verified": self.metrics.chain_verified,
            "metrics": self.metrics.model_dump(),
            "config": {
                "retention_days": self.config.retention_days,
                "log_to_file": self.config.log_to_file,
                "log_to_database": self.config.log_to_database,
            },
        }

    def get_metrics(self) -> OpsAuditMetrics:
        """Get audit log metrics."""
        return self.metrics
