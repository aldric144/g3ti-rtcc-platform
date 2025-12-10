"""
Tests for Ops Audit Log.

Tests CJIS-aligned audit logging, chain verification,
retention policies, and compliance reporting.
"""

import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

from app.ops_continuity.ops_audit_log import (
    OpsAuditLog,
    OpsAuditConfig,
    OpsAuditAction,
    OpsAuditSeverity,
    OpsAuditEntry,
)


class TestOpsAuditLog:
    """Tests for OpsAuditLog class."""

    def test_init_default_config(self):
        """Test initialization with default configuration."""
        audit_log = OpsAuditLog()
        assert audit_log.config is not None
        assert audit_log.config.retention_days == 365

    def test_init_custom_config(self):
        """Test initialization with custom configuration."""
        config = OpsAuditConfig(
            retention_days=730,
            max_entries_in_memory=5000,
            chain_verification_enabled=True,
        )
        audit_log = OpsAuditLog(config=config)
        assert audit_log.config.retention_days == 730
        assert audit_log.config.max_entries_in_memory == 5000

    def test_log_entry(self):
        """Test logging an audit entry."""
        audit_log = OpsAuditLog()
        entry = audit_log.log_entry(
            action=OpsAuditAction.HEALTH_CHECK,
            severity=OpsAuditSeverity.INFO,
            description="Routine health check completed",
            actor="system",
        )
        
        assert entry is not None
        assert entry.action == OpsAuditAction.HEALTH_CHECK
        assert entry.severity == OpsAuditSeverity.INFO

    def test_log_health_check(self):
        """Test logging a health check event."""
        audit_log = OpsAuditLog()
        entry = audit_log.log_health_check(
            service_id="neo4j-primary",
            status="healthy",
            latency_ms=45.0,
        )
        
        assert entry is not None
        assert entry.action == OpsAuditAction.HEALTH_CHECK

    def test_log_failover(self):
        """Test logging a failover event."""
        audit_log = OpsAuditLog()
        entry = audit_log.log_failover(
            service_type="neo4j",
            from_instance="primary",
            to_instance="secondary",
            reason="Primary unresponsive",
            auto_triggered=True,
        )
        
        assert entry is not None
        assert entry.action == OpsAuditAction.FAILOVER
        assert entry.severity == OpsAuditSeverity.WARNING

    def test_log_recovery(self):
        """Test logging a recovery event."""
        audit_log = OpsAuditLog()
        entry = audit_log.log_recovery(
            service_type="redis",
            from_instance="secondary",
            to_instance="primary",
            recovery_time_seconds=30.5,
        )
        
        assert entry is not None
        assert entry.action == OpsAuditAction.RECOVERY

    def test_log_redundancy_sync(self):
        """Test logging a redundancy sync event."""
        audit_log = OpsAuditLog()
        entry = audit_log.log_redundancy_sync(
            pool_id="neo4j-pool",
            from_instance="primary",
            to_instance="secondary",
            records_synced=1000,
            duration_ms=500.0,
        )
        
        assert entry is not None
        assert entry.action == OpsAuditAction.REDUNDANCY_SYNC

    def test_log_diagnostic_event(self):
        """Test logging a diagnostic event."""
        audit_log = OpsAuditLog()
        entry = audit_log.log_diagnostic_event(
            category="network",
            severity="error",
            message="Connection timeout",
            source="redis-client",
        )
        
        assert entry is not None
        assert entry.action == OpsAuditAction.DIAGNOSTIC

    def test_log_escalation(self):
        """Test logging an escalation event."""
        audit_log = OpsAuditLog()
        entry = audit_log.log_escalation(
            alert_id="alert-001",
            tier=1,
            reason="Multiple service failures",
            targets=["command-center", "tactical-dashboard"],
        )
        
        assert entry is not None
        assert entry.action == OpsAuditAction.ESCALATION
        assert entry.severity == OpsAuditSeverity.CRITICAL

    def test_get_recent_entries(self):
        """Test getting recent audit entries."""
        audit_log = OpsAuditLog()
        audit_log.log_entry(
            action=OpsAuditAction.HEALTH_CHECK,
            severity=OpsAuditSeverity.INFO,
            description="Test entry",
            actor="test",
        )
        
        entries = audit_log.get_recent_entries(limit=10)
        assert isinstance(entries, list)

    def test_get_entries_by_action(self):
        """Test getting entries by action type."""
        audit_log = OpsAuditLog()
        audit_log.log_health_check("test-service", "healthy", 50.0)
        
        entries = audit_log.get_entries_by_action(OpsAuditAction.HEALTH_CHECK)
        assert isinstance(entries, list)

    def test_get_entries_by_severity(self):
        """Test getting entries by severity."""
        audit_log = OpsAuditLog()
        audit_log.log_failover("neo4j", "primary", "secondary", "Test", True)
        
        entries = audit_log.get_entries_by_severity(OpsAuditSeverity.WARNING)
        assert isinstance(entries, list)

    def test_verify_chain_integrity(self):
        """Test chain integrity verification."""
        audit_log = OpsAuditLog()
        audit_log.log_entry(
            action=OpsAuditAction.HEALTH_CHECK,
            severity=OpsAuditSeverity.INFO,
            description="Entry 1",
            actor="system",
        )
        audit_log.log_entry(
            action=OpsAuditAction.HEALTH_CHECK,
            severity=OpsAuditSeverity.INFO,
            description="Entry 2",
            actor="system",
        )
        
        result = audit_log.verify_chain_integrity()
        assert isinstance(result, dict)
        assert "valid" in result

    def test_generate_compliance_report(self):
        """Test generating compliance report."""
        audit_log = OpsAuditLog()
        report = audit_log.generate_compliance_report(days=30)
        
        assert isinstance(report, dict)
        assert "period_days" in report
        assert "total_entries" in report
        assert "entries_by_action" in report

    def test_get_metrics(self):
        """Test getting audit log metrics."""
        audit_log = OpsAuditLog()
        metrics = audit_log.get_metrics()
        
        assert metrics is not None
        assert hasattr(metrics, "total_entries")
        assert hasattr(metrics, "entries_by_action")

    def test_get_status(self):
        """Test getting audit log status."""
        audit_log = OpsAuditLog()
        status = audit_log.get_status()
        
        assert isinstance(status, dict)
        assert "entries_stored" in status
        assert "chain_valid" in status


class TestOpsAuditEntry:
    """Tests for OpsAuditEntry model."""

    def test_entry_creation(self):
        """Test OpsAuditEntry creation."""
        entry = OpsAuditEntry(
            entry_id="audit-001",
            timestamp=datetime.now(timezone.utc),
            action=OpsAuditAction.HEALTH_CHECK,
            severity=OpsAuditSeverity.INFO,
            description="Health check completed",
            actor="system",
        )
        
        assert entry.entry_id == "audit-001"
        assert entry.action == OpsAuditAction.HEALTH_CHECK
        assert entry.actor == "system"

    def test_entry_with_metadata(self):
        """Test entry with additional metadata."""
        entry = OpsAuditEntry(
            entry_id="audit-002",
            timestamp=datetime.now(timezone.utc),
            action=OpsAuditAction.FAILOVER,
            severity=OpsAuditSeverity.WARNING,
            description="Failover activated",
            actor="failover-manager",
            metadata={
                "service_type": "neo4j",
                "from_instance": "primary",
                "to_instance": "secondary",
            },
        )
        
        assert entry.metadata is not None
        assert "service_type" in entry.metadata

    def test_entry_with_chain_hash(self):
        """Test entry with chain hash for verification."""
        entry = OpsAuditEntry(
            entry_id="audit-003",
            timestamp=datetime.now(timezone.utc),
            action=OpsAuditAction.RECOVERY,
            severity=OpsAuditSeverity.INFO,
            description="Service recovered",
            actor="system",
            previous_hash="abc123",
            entry_hash="def456",
        )
        
        assert entry.previous_hash == "abc123"
        assert entry.entry_hash == "def456"


class TestOpsAuditAction:
    """Tests for OpsAuditAction enum."""

    def test_audit_actions(self):
        """Test all audit actions exist."""
        assert OpsAuditAction.HEALTH_CHECK is not None
        assert OpsAuditAction.FAILOVER is not None
        assert OpsAuditAction.RECOVERY is not None
        assert OpsAuditAction.REDUNDANCY_SYNC is not None
        assert OpsAuditAction.DIAGNOSTIC is not None
        assert OpsAuditAction.ESCALATION is not None
        assert OpsAuditAction.CONFIG_CHANGE is not None
        assert OpsAuditAction.MANUAL_OVERRIDE is not None


class TestOpsAuditSeverity:
    """Tests for OpsAuditSeverity enum."""

    def test_audit_severities(self):
        """Test all audit severities exist."""
        assert OpsAuditSeverity.DEBUG is not None
        assert OpsAuditSeverity.INFO is not None
        assert OpsAuditSeverity.WARNING is not None
        assert OpsAuditSeverity.ERROR is not None
        assert OpsAuditSeverity.CRITICAL is not None


class TestOpsAuditConfig:
    """Tests for OpsAuditConfig model."""

    def test_default_config(self):
        """Test default configuration values."""
        config = OpsAuditConfig()
        
        assert config.retention_days == 365
        assert config.max_entries_in_memory == 10000
        assert config.chain_verification_enabled is True

    def test_custom_config(self):
        """Test custom configuration values."""
        config = OpsAuditConfig(
            retention_days=730,
            max_entries_in_memory=5000,
            chain_verification_enabled=False,
            mask_sensitive_data=True,
        )
        
        assert config.retention_days == 730
        assert config.chain_verification_enabled is False
        assert config.mask_sensitive_data is True
