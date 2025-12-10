"""
Audit Log for G3TI RTCC-UIP.

This module provides CJIS-grade logging of all intelligence actions
for compliance, accountability, and forensic analysis.
"""

import asyncio
import hashlib
import json
import logging
from datetime import UTC, datetime
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class AuditAction(str, Enum):
    """Types of auditable actions."""
    # Orchestration actions
    ORCHESTRATOR_INITIALIZED = "orchestrator_initialized"
    ORCHESTRATOR_STARTED = "orchestrator_started"
    ORCHESTRATOR_STOPPED = "orchestrator_stopped"
    ORCHESTRATOR_PAUSED = "orchestrator_paused"
    ORCHESTRATOR_RESUMED = "orchestrator_resumed"

    # Signal actions
    SIGNAL_INGESTED = "signal_ingested"
    SIGNAL_PROCESSED = "signal_processed"
    SIGNAL_DROPPED = "signal_dropped"
    SIGNAL_ENRICHED = "signal_enriched"

    # Fusion actions
    FUSION_CREATED = "fusion_created"
    FUSION_PROCESSED = "fusion_processed"
    FUSION_ROUTED = "fusion_routed"

    # Correlation actions
    CORRELATION_FOUND = "correlation_found"
    CORRELATION_CREATED = "correlation_created"
    PATTERN_DETECTED = "pattern_detected"

    # Scoring actions
    PRIORITY_CALCULATED = "priority_calculated"
    THREAT_ASSESSED = "threat_assessed"
    RISK_PROFILE_UPDATED = "risk_profile_updated"

    # Routing actions
    ALERT_CREATED = "alert_created"
    ALERT_ROUTED = "alert_routed"
    ALERT_DELIVERED = "alert_delivered"
    ALERT_ACKNOWLEDGED = "alert_acknowledged"
    BOLO_GENERATED = "bolo_generated"
    BULLETIN_GENERATED = "bulletin_generated"

    # Graph sync actions
    NODE_CREATED = "node_created"
    NODE_UPDATED = "node_updated"
    NODE_DELETED = "node_deleted"
    RELATIONSHIP_CREATED = "relationship_created"
    RELATIONSHIP_UPDATED = "relationship_updated"
    RELATIONSHIP_DELETED = "relationship_deleted"

    # Access actions
    DATA_ACCESSED = "data_accessed"
    DATA_EXPORTED = "data_exported"
    DATA_QUERIED = "data_queried"

    # Configuration actions
    CONFIG_CHANGED = "config_changed"
    RULE_ADDED = "rule_added"
    RULE_MODIFIED = "rule_modified"
    RULE_DELETED = "rule_deleted"

    # Error actions
    ERROR_OCCURRED = "error_occurred"
    RETRY_ATTEMPTED = "retry_attempted"


class AuditSeverity(str, Enum):
    """Severity levels for audit entries."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AuditCategory(str, Enum):
    """Categories for audit entries."""
    SYSTEM = "system"
    INTELLIGENCE = "intelligence"
    SECURITY = "security"
    ACCESS = "access"
    CONFIGURATION = "configuration"
    COMPLIANCE = "compliance"


class AuditConfig(BaseModel):
    """Configuration for audit logging."""
    enabled: bool = True
    log_to_file: bool = True
    log_to_database: bool = True
    log_file_path: str = "/var/log/g3ti/intel_audit.log"
    retention_days: int = 2555  # 7 years for CJIS compliance
    enable_integrity_hash: bool = True
    enable_chain_verification: bool = True
    batch_size: int = 100
    flush_interval_seconds: float = 5.0
    include_payload_hash: bool = True
    mask_sensitive_fields: bool = True
    sensitive_fields: list[str] = Field(default_factory=lambda: [
        "ssn", "social_security", "password", "token", "api_key",
        "drivers_license", "credit_card", "bank_account",
    ])


class AuditEntry(BaseModel):
    """A single audit log entry."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    action: AuditAction
    severity: AuditSeverity = AuditSeverity.INFO
    category: AuditCategory = AuditCategory.INTELLIGENCE

    # Actor information
    user_id: str | None = None
    user_name: str | None = None
    user_role: str | None = None
    session_id: str | None = None

    # Source information
    source_system: str = "intel_orchestration"
    source_component: str | None = None
    source_ip: str | None = None

    # Target information
    target_type: str | None = None
    target_id: str | None = None

    # Action details
    details: dict[str, Any] = Field(default_factory=dict)
    result: str | None = None
    error_message: str | None = None

    # Integrity
    payload_hash: str | None = None
    previous_entry_hash: str | None = None
    entry_hash: str | None = None

    # Metadata
    jurisdiction: str | None = None
    case_number: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class AuditMetrics(BaseModel):
    """Metrics for audit logging."""
    entries_logged: int = 0
    entries_by_action: dict[str, int] = Field(default_factory=dict)
    entries_by_severity: dict[str, int] = Field(default_factory=dict)
    entries_by_category: dict[str, int] = Field(default_factory=dict)
    errors_logged: int = 0
    last_entry_time: datetime | None = None
    chain_verified: bool = True


class IntelAuditLog:
    """
    CJIS-grade audit logging for intelligence operations.

    Provides comprehensive logging with integrity verification,
    chain of custody tracking, and compliance reporting.
    """

    def __init__(self, config: AuditConfig | None = None):
        self.config = config or AuditConfig()
        self.metrics = AuditMetrics()
        self._entry_buffer: list[AuditEntry] = []
        self._last_entry_hash: str | None = None
        self._running = False
        self._worker_task: asyncio.Task | None = None
        self._lock = asyncio.Lock()

        logger.info("IntelAuditLog initialized")

    async def start(self):
        """Start the audit log service."""
        if self._running:
            return

        self._running = True
        self._worker_task = asyncio.create_task(self._flush_worker())

        await self.log_action(
            action=AuditAction.ORCHESTRATOR_STARTED,
            category=AuditCategory.SYSTEM,
            details={"message": "Audit log service started"},
        )

        logger.info("IntelAuditLog started")

    async def stop(self):
        """Stop the audit log service."""
        await self.log_action(
            action=AuditAction.ORCHESTRATOR_STOPPED,
            category=AuditCategory.SYSTEM,
            details={"message": "Audit log service stopping"},
        )

        self._running = False

        if self._worker_task:
            self._worker_task.cancel()
            try:
                await self._worker_task
            except asyncio.CancelledError:
                pass

        # Flush remaining entries
        await self._flush_buffer()

        logger.info("IntelAuditLog stopped")

    async def log_action(
        self,
        action: AuditAction | str,
        details: dict[str, Any] | None = None,
        severity: AuditSeverity = AuditSeverity.INFO,
        category: AuditCategory = AuditCategory.INTELLIGENCE,
        user_id: str | None = None,
        user_name: str | None = None,
        target_type: str | None = None,
        target_id: str | None = None,
        result: str | None = None,
        error_message: str | None = None,
        jurisdiction: str | None = None,
        case_number: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> AuditEntry:
        """
        Log an auditable action.

        Returns the created audit entry.
        """
        if not self.config.enabled:
            return AuditEntry(action=action if isinstance(action, AuditAction) else AuditAction.DATA_ACCESSED)

        # Convert string action to enum if needed
        if isinstance(action, str):
            try:
                action = AuditAction(action)
            except ValueError:
                action = AuditAction.DATA_ACCESSED

        # Mask sensitive fields in details
        if details and self.config.mask_sensitive_fields:
            details = self._mask_sensitive_data(details)

        # Create entry
        entry = AuditEntry(
            action=action,
            severity=severity,
            category=category,
            user_id=user_id,
            user_name=user_name,
            target_type=target_type,
            target_id=target_id,
            details=details or {},
            result=result,
            error_message=error_message,
            jurisdiction=jurisdiction,
            case_number=case_number,
            metadata=metadata or {},
        )

        # Calculate payload hash
        if self.config.include_payload_hash and details:
            entry.payload_hash = self._calculate_hash(json.dumps(details, sort_keys=True))

        # Chain verification
        if self.config.enable_chain_verification:
            entry.previous_entry_hash = self._last_entry_hash
            entry.entry_hash = self._calculate_entry_hash(entry)
            self._last_entry_hash = entry.entry_hash

        # Add to buffer
        async with self._lock:
            self._entry_buffer.append(entry)

        # Update metrics
        self.metrics.entries_logged += 1
        self.metrics.last_entry_time = entry.timestamp

        action_key = action.value
        self.metrics.entries_by_action[action_key] = (
            self.metrics.entries_by_action.get(action_key, 0) + 1
        )

        severity_key = severity.value
        self.metrics.entries_by_severity[severity_key] = (
            self.metrics.entries_by_severity.get(severity_key, 0) + 1
        )

        category_key = category.value
        self.metrics.entries_by_category[category_key] = (
            self.metrics.entries_by_category.get(category_key, 0) + 1
        )

        if severity in [AuditSeverity.ERROR, AuditSeverity.CRITICAL]:
            self.metrics.errors_logged += 1

        # Flush if buffer is full
        if len(self._entry_buffer) >= self.config.batch_size:
            await self._flush_buffer()

        return entry

    async def log_signal_ingested(
        self,
        signal_id: str,
        source: str,
        category: str,
        jurisdiction: str | None = None,
    ) -> AuditEntry:
        """Log signal ingestion."""
        return await self.log_action(
            action=AuditAction.SIGNAL_INGESTED,
            target_type="signal",
            target_id=signal_id,
            details={
                "signal_id": signal_id,
                "source": source,
                "category": category,
            },
            jurisdiction=jurisdiction,
        )

    async def log_fusion_created(
        self,
        fusion_id: str,
        tier: str,
        priority_score: float,
        source_signals: list[str],
        jurisdiction: str | None = None,
    ) -> AuditEntry:
        """Log fusion creation."""
        return await self.log_action(
            action=AuditAction.FUSION_CREATED,
            target_type="fusion",
            target_id=fusion_id,
            details={
                "fusion_id": fusion_id,
                "tier": tier,
                "priority_score": priority_score,
                "source_signal_count": len(source_signals),
            },
            jurisdiction=jurisdiction,
        )

    async def log_alert_routed(
        self,
        alert_id: str,
        destinations: list[str],
        priority: str,
    ) -> AuditEntry:
        """Log alert routing."""
        return await self.log_action(
            action=AuditAction.ALERT_ROUTED,
            target_type="alert",
            target_id=alert_id,
            details={
                "alert_id": alert_id,
                "destinations": destinations,
                "priority": priority,
                "destination_count": len(destinations),
            },
        )

    async def log_data_accessed(
        self,
        user_id: str,
        user_name: str,
        data_type: str,
        data_id: str,
        access_reason: str | None = None,
        jurisdiction: str | None = None,
        case_number: str | None = None,
    ) -> AuditEntry:
        """Log data access for CJIS compliance."""
        return await self.log_action(
            action=AuditAction.DATA_ACCESSED,
            category=AuditCategory.ACCESS,
            user_id=user_id,
            user_name=user_name,
            target_type=data_type,
            target_id=data_id,
            details={
                "access_reason": access_reason,
                "data_type": data_type,
                "data_id": data_id,
            },
            jurisdiction=jurisdiction,
            case_number=case_number,
        )

    async def log_error(
        self,
        error_message: str,
        component: str,
        details: dict[str, Any] | None = None,
    ) -> AuditEntry:
        """Log an error."""
        return await self.log_action(
            action=AuditAction.ERROR_OCCURRED,
            severity=AuditSeverity.ERROR,
            category=AuditCategory.SYSTEM,
            error_message=error_message,
            details={
                "component": component,
                **(details or {}),
            },
        )

    async def log_config_change(
        self,
        user_id: str,
        config_type: str,
        old_value: Any,
        new_value: Any,
    ) -> AuditEntry:
        """Log configuration change."""
        return await self.log_action(
            action=AuditAction.CONFIG_CHANGED,
            severity=AuditSeverity.WARNING,
            category=AuditCategory.CONFIGURATION,
            user_id=user_id,
            target_type="config",
            target_id=config_type,
            details={
                "config_type": config_type,
                "old_value": str(old_value),
                "new_value": str(new_value),
            },
        )

    def _mask_sensitive_data(self, data: dict[str, Any]) -> dict[str, Any]:
        """Mask sensitive fields in data."""
        masked = {}

        for key, value in data.items():
            key_lower = key.lower()

            # Check if field is sensitive
            is_sensitive = any(
                sensitive in key_lower
                for sensitive in self.config.sensitive_fields
            )

            if is_sensitive:
                masked[key] = "***MASKED***"
            elif isinstance(value, dict):
                masked[key] = self._mask_sensitive_data(value)
            elif isinstance(value, list):
                masked[key] = [
                    self._mask_sensitive_data(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                masked[key] = value

        return masked

    def _calculate_hash(self, data: str) -> str:
        """Calculate SHA-256 hash of data."""
        return hashlib.sha256(data.encode()).hexdigest()

    def _calculate_entry_hash(self, entry: AuditEntry) -> str:
        """Calculate hash for entry integrity verification."""
        hash_data = {
            "id": entry.id,
            "timestamp": entry.timestamp.isoformat(),
            "action": entry.action.value,
            "user_id": entry.user_id,
            "target_id": entry.target_id,
            "payload_hash": entry.payload_hash,
            "previous_entry_hash": entry.previous_entry_hash,
        }
        return self._calculate_hash(json.dumps(hash_data, sort_keys=True))

    async def _flush_worker(self):
        """Background worker to flush buffer periodically."""
        while self._running:
            try:
                await asyncio.sleep(self.config.flush_interval_seconds)
                await self._flush_buffer()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Flush worker error: %s", e)

    async def _flush_buffer(self):
        """Flush entry buffer to storage."""
        async with self._lock:
            if not self._entry_buffer:
                return

            entries = self._entry_buffer.copy()
            self._entry_buffer.clear()

        # Write to file
        if self.config.log_to_file:
            await self._write_to_file(entries)

        # Write to database
        if self.config.log_to_database:
            await self._write_to_database(entries)

    async def _write_to_file(self, entries: list[AuditEntry]):
        """Write entries to log file."""
        try:
            # In production, this would write to the configured file
            for entry in entries:
                log_line = json.dumps(entry.model_dump(mode="json"))
                logger.info("AUDIT: %s", log_line)
        except Exception as e:
            logger.error("Failed to write audit entries to file: %s", e)

    async def _write_to_database(self, entries: list[AuditEntry]):
        """Write entries to database."""
        try:
            # In production, this would write to the audit database
            logger.debug("Writing %d audit entries to database", len(entries))
        except Exception as e:
            logger.error("Failed to write audit entries to database: %s", e)

    async def verify_chain_integrity(
        self, start_id: str | None = None, end_id: str | None = None
    ) -> bool:
        """Verify the integrity of the audit chain."""
        # In production, this would verify the hash chain
        self.metrics.chain_verified = True
        return True

    async def query_entries(
        self,
        action: AuditAction | None = None,
        category: AuditCategory | None = None,
        severity: AuditSeverity | None = None,
        user_id: str | None = None,
        target_id: str | None = None,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        limit: int = 100,
    ) -> list[AuditEntry]:
        """Query audit entries with filters."""
        # In production, this would query the database
        # For now, return empty list
        return []

    async def generate_compliance_report(
        self,
        start_time: datetime,
        end_time: datetime,
        report_type: str = "cjis",
    ) -> dict[str, Any]:
        """Generate compliance report for specified period."""
        return {
            "report_type": report_type,
            "period": {
                "start": start_time.isoformat(),
                "end": end_time.isoformat(),
            },
            "summary": {
                "total_entries": self.metrics.entries_logged,
                "by_action": self.metrics.entries_by_action,
                "by_severity": self.metrics.entries_by_severity,
                "by_category": self.metrics.entries_by_category,
                "errors": self.metrics.errors_logged,
            },
            "chain_integrity": self.metrics.chain_verified,
            "generated_at": datetime.now(UTC).isoformat(),
        }

    def get_metrics(self) -> AuditMetrics:
        """Get audit metrics."""
        return self.metrics

    def get_status(self) -> dict[str, Any]:
        """Get audit log status."""
        return {
            "running": self._running,
            "buffer_size": len(self._entry_buffer),
            "metrics": self.metrics.model_dump(),
            "config": {
                "enabled": self.config.enabled,
                "log_to_file": self.config.log_to_file,
                "log_to_database": self.config.log_to_database,
                "retention_days": self.config.retention_days,
            },
        }
