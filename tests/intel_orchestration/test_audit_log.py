"""Tests for the Audit Log module."""

import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import sys
sys.path.insert(0, "/home/ubuntu/repos/g3ti-rtcc-platform/backend")

from app.intel_orchestration.audit_log import (
    AuditAction,
    AuditSeverity,
    AuditCategory,
    AuditConfig,
    AuditEntry,
    AuditMetrics,
    IntelAuditLog,
)


class TestAuditAction:
    """Tests for AuditAction enum."""

    def test_orchestration_actions_defined(self):
        """Test orchestration actions are defined."""
        expected_actions = [
            "ORCHESTRATOR_INITIALIZED", "ORCHESTRATOR_STARTED",
            "ORCHESTRATOR_STOPPED", "ORCHESTRATOR_PAUSED", "ORCHESTRATOR_RESUMED",
        ]
        
        for action in expected_actions:
            assert hasattr(AuditAction, action)

    def test_signal_actions_defined(self):
        """Test signal actions are defined."""
        expected_actions = [
            "SIGNAL_INGESTED", "SIGNAL_PROCESSED",
            "SIGNAL_DROPPED", "SIGNAL_ENRICHED",
        ]
        
        for action in expected_actions:
            assert hasattr(AuditAction, action)

    def test_fusion_actions_defined(self):
        """Test fusion actions are defined."""
        expected_actions = [
            "FUSION_CREATED", "FUSION_PROCESSED", "FUSION_ROUTED",
        ]
        
        for action in expected_actions:
            assert hasattr(AuditAction, action)

    def test_access_actions_defined(self):
        """Test access actions are defined."""
        expected_actions = [
            "DATA_ACCESSED", "DATA_EXPORTED", "DATA_QUERIED",
        ]
        
        for action in expected_actions:
            assert hasattr(AuditAction, action)


class TestAuditSeverity:
    """Tests for AuditSeverity enum."""

    def test_severity_values(self):
        """Test audit severity values."""
        assert AuditSeverity.DEBUG.value == "debug"
        assert AuditSeverity.INFO.value == "info"
        assert AuditSeverity.WARNING.value == "warning"
        assert AuditSeverity.ERROR.value == "error"
        assert AuditSeverity.CRITICAL.value == "critical"


class TestAuditCategory:
    """Tests for AuditCategory enum."""

    def test_category_values(self):
        """Test audit category values."""
        assert AuditCategory.SYSTEM.value == "system"
        assert AuditCategory.INTELLIGENCE.value == "intelligence"
        assert AuditCategory.SECURITY.value == "security"
        assert AuditCategory.ACCESS.value == "access"
        assert AuditCategory.CONFIGURATION.value == "configuration"
        assert AuditCategory.COMPLIANCE.value == "compliance"


class TestAuditConfig:
    """Tests for AuditConfig model."""

    def test_default_config(self):
        """Test default audit configuration."""
        config = AuditConfig()
        
        assert config.enabled is True
        assert config.log_to_file is True
        assert config.log_to_database is True
        assert config.retention_days == 2555  # 7 years for CJIS

    def test_custom_config(self):
        """Test custom audit configuration."""
        config = AuditConfig(
            enabled=False,
            retention_days=365,
            batch_size=50,
        )
        
        assert config.enabled is False
        assert config.retention_days == 365
        assert config.batch_size == 50

    def test_sensitive_fields_default(self):
        """Test default sensitive fields."""
        config = AuditConfig()
        
        assert "ssn" in config.sensitive_fields
        assert "password" in config.sensitive_fields
        assert "api_key" in config.sensitive_fields


class TestAuditEntry:
    """Tests for AuditEntry model."""

    def test_entry_creation(self):
        """Test creating an audit entry."""
        entry = AuditEntry(
            action=AuditAction.SIGNAL_INGESTED,
            severity=AuditSeverity.INFO,
            category=AuditCategory.INTELLIGENCE,
            target_type="signal",
            target_id="sig-123",
        )
        
        assert entry.id is not None
        assert entry.action == AuditAction.SIGNAL_INGESTED
        assert entry.timestamp is not None

    def test_entry_with_user(self):
        """Test entry with user information."""
        entry = AuditEntry(
            action=AuditAction.DATA_ACCESSED,
            user_id="user-123",
            user_name="John Doe",
            user_role="analyst",
        )
        
        assert entry.user_id == "user-123"
        assert entry.user_name == "John Doe"

    def test_entry_with_details(self):
        """Test entry with details."""
        entry = AuditEntry(
            action=AuditAction.FUSION_CREATED,
            details={
                "fusion_id": "fus-123",
                "tier": "tier2",
                "source_count": 3,
            },
        )
        
        assert entry.details["fusion_id"] == "fus-123"

    def test_entry_with_error(self):
        """Test entry with error message."""
        entry = AuditEntry(
            action=AuditAction.ERROR_OCCURRED,
            severity=AuditSeverity.ERROR,
            error_message="Connection timeout",
        )
        
        assert entry.error_message == "Connection timeout"


class TestAuditMetrics:
    """Tests for AuditMetrics model."""

    def test_default_metrics(self):
        """Test default audit metrics."""
        metrics = AuditMetrics()
        
        assert metrics.entries_logged == 0
        assert metrics.errors_logged == 0
        assert metrics.chain_verified is True

    def test_metrics_update(self):
        """Test updating metrics."""
        metrics = AuditMetrics()
        metrics.entries_logged = 1000
        metrics.errors_logged = 5
        
        assert metrics.entries_logged == 1000
        assert metrics.errors_logged == 5


class TestIntelAuditLog:
    """Tests for IntelAuditLog class."""

    def test_audit_log_initialization(self):
        """Test audit log initialization."""
        audit = IntelAuditLog()
        
        assert audit.config is not None
        assert audit.metrics is not None

    def test_audit_log_with_custom_config(self):
        """Test audit log with custom config."""
        config = AuditConfig(
            batch_size=200,
        )
        audit = IntelAuditLog(config=config)
        
        assert audit.config.batch_size == 200

    @pytest.mark.asyncio
    async def test_audit_log_start_stop(self):
        """Test starting and stopping audit log."""
        audit = IntelAuditLog()
        
        await audit.start()
        assert audit._running is True
        
        await audit.stop()
        assert audit._running is False

    @pytest.mark.asyncio
    async def test_log_action(self):
        """Test logging an action."""
        audit = IntelAuditLog()
        await audit.start()
        
        entry = await audit.log_action(
            action=AuditAction.SIGNAL_INGESTED,
            details={"signal_id": "sig-123"},
        )
        
        assert entry is not None
        assert entry.action == AuditAction.SIGNAL_INGESTED
        assert audit.metrics.entries_logged >= 1
        
        await audit.stop()

    @pytest.mark.asyncio
    async def test_log_signal_ingested(self):
        """Test logging signal ingestion."""
        audit = IntelAuditLog()
        await audit.start()
        
        entry = await audit.log_signal_ingested(
            signal_id="sig-123",
            source="ai_engine",
            category="pattern",
            jurisdiction="Metro PD",
        )
        
        assert entry.action == AuditAction.SIGNAL_INGESTED
        assert entry.details["signal_id"] == "sig-123"
        
        await audit.stop()

    @pytest.mark.asyncio
    async def test_log_fusion_created(self):
        """Test logging fusion creation."""
        audit = IntelAuditLog()
        await audit.start()
        
        entry = await audit.log_fusion_created(
            fusion_id="fus-123",
            tier="tier2",
            priority_score=75.0,
            source_signals=["sig-1", "sig-2"],
        )
        
        assert entry.action == AuditAction.FUSION_CREATED
        assert entry.details["tier"] == "tier2"
        
        await audit.stop()

    @pytest.mark.asyncio
    async def test_log_alert_routed(self):
        """Test logging alert routing."""
        audit = IntelAuditLog()
        await audit.start()
        
        entry = await audit.log_alert_routed(
            alert_id="alert-123",
            destinations=["rtcc_dashboard", "dispatch"],
            priority="high",
        )
        
        assert entry.action == AuditAction.ALERT_ROUTED
        assert entry.details["destination_count"] == 2
        
        await audit.stop()

    @pytest.mark.asyncio
    async def test_log_data_accessed(self):
        """Test logging data access for CJIS compliance."""
        audit = IntelAuditLog()
        await audit.start()
        
        entry = await audit.log_data_accessed(
            user_id="user-123",
            user_name="John Doe",
            data_type="person",
            data_id="person-456",
            access_reason="Investigation",
            case_number="2024-001",
        )
        
        assert entry.action == AuditAction.DATA_ACCESSED
        assert entry.category == AuditCategory.ACCESS
        assert entry.user_id == "user-123"
        assert entry.case_number == "2024-001"
        
        await audit.stop()

    @pytest.mark.asyncio
    async def test_log_error(self):
        """Test logging an error."""
        audit = IntelAuditLog()
        await audit.start()
        
        entry = await audit.log_error(
            error_message="Connection timeout",
            component="correlator",
            details={"retry_count": 3},
        )
        
        assert entry.action == AuditAction.ERROR_OCCURRED
        assert entry.severity == AuditSeverity.ERROR
        assert audit.metrics.errors_logged >= 1
        
        await audit.stop()

    @pytest.mark.asyncio
    async def test_log_config_change(self):
        """Test logging configuration change."""
        audit = IntelAuditLog()
        await audit.start()
        
        entry = await audit.log_config_change(
            user_id="admin-123",
            config_type="scoring_rules",
            old_value={"threshold": 0.5},
            new_value={"threshold": 0.7},
        )
        
        assert entry.action == AuditAction.CONFIG_CHANGED
        assert entry.severity == AuditSeverity.WARNING
        
        await audit.stop()

    @pytest.mark.asyncio
    async def test_sensitive_data_masking(self):
        """Test sensitive data is masked."""
        audit = IntelAuditLog()
        await audit.start()
        
        entry = await audit.log_action(
            action=AuditAction.DATA_ACCESSED,
            details={
                "name": "John Doe",
                "ssn": "123-45-6789",
                "password": "secret123",
            },
        )
        
        # SSN and password should be masked
        assert entry.details["ssn"] == "***MASKED***"
        assert entry.details["password"] == "***MASKED***"
        assert entry.details["name"] == "John Doe"  # Not sensitive
        
        await audit.stop()

    @pytest.mark.asyncio
    async def test_payload_hash(self):
        """Test payload hash is calculated."""
        config = AuditConfig(include_payload_hash=True)
        audit = IntelAuditLog(config=config)
        await audit.start()
        
        entry = await audit.log_action(
            action=AuditAction.SIGNAL_INGESTED,
            details={"test": "data"},
        )
        
        assert entry.payload_hash is not None
        
        await audit.stop()

    @pytest.mark.asyncio
    async def test_chain_verification(self):
        """Test entry chain verification."""
        config = AuditConfig(enable_chain_verification=True)
        audit = IntelAuditLog(config=config)
        await audit.start()
        
        entry1 = await audit.log_action(
            action=AuditAction.SIGNAL_INGESTED,
            details={"index": 1},
        )
        
        entry2 = await audit.log_action(
            action=AuditAction.SIGNAL_PROCESSED,
            details={"index": 2},
        )
        
        # Entry 2 should reference entry 1's hash
        assert entry2.previous_entry_hash == entry1.entry_hash
        
        await audit.stop()

    @pytest.mark.asyncio
    async def test_verify_chain_integrity(self):
        """Test chain integrity verification."""
        audit = IntelAuditLog()
        await audit.start()
        
        # Log some entries
        for i in range(5):
            await audit.log_action(
                action=AuditAction.SIGNAL_INGESTED,
                details={"index": i},
            )
        
        # Verify chain
        is_valid = await audit.verify_chain_integrity()
        
        assert is_valid is True
        assert audit.metrics.chain_verified is True
        
        await audit.stop()

    @pytest.mark.asyncio
    async def test_generate_compliance_report(self):
        """Test generating compliance report."""
        audit = IntelAuditLog()
        await audit.start()
        
        # Log some entries
        await audit.log_action(action=AuditAction.SIGNAL_INGESTED, details={})
        await audit.log_action(action=AuditAction.FUSION_CREATED, details={})
        
        report = await audit.generate_compliance_report(
            start_time=datetime(2024, 1, 1, tzinfo=timezone.utc),
            end_time=datetime.now(timezone.utc),
            report_type="cjis",
        )
        
        assert report is not None
        assert "report_type" in report
        assert "summary" in report
        
        await audit.stop()

    def test_get_status(self):
        """Test getting audit log status."""
        audit = IntelAuditLog()
        status = audit.get_status()
        
        assert "running" in status
        assert "buffer_size" in status
        assert "metrics" in status

    def test_get_metrics(self):
        """Test getting audit metrics."""
        audit = IntelAuditLog()
        metrics = audit.get_metrics()
        
        assert isinstance(metrics, AuditMetrics)

    @pytest.mark.asyncio
    async def test_disabled_audit_log(self):
        """Test disabled audit log."""
        config = AuditConfig(enabled=False)
        audit = IntelAuditLog(config=config)
        
        entry = await audit.log_action(
            action=AuditAction.SIGNAL_INGESTED,
            details={},
        )
        
        # Should return empty entry when disabled
        assert entry is not None
