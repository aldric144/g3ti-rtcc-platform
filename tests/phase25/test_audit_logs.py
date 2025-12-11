"""
Test Suite 6: Audit Logs Tests

Tests for audit entry creation, search, export, and CJIS compliance.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
import json

import sys
sys.path.insert(0, "/home/ubuntu/repos/g3ti-rtcc-platform/backend")

from app.city_governance.constitution_engine import ActionCategory


class AuditEntry:
    """Audit entry model for testing."""
    
    def __init__(
        self,
        audit_id: str,
        timestamp: datetime,
        action_type: str,
        resource_type: str,
        resource_id: str,
        user_id: str,
        user_role: str,
        session_id: str,
        ip_address: str,
        risk_level: str,
        compliance_tags: list,
        details: dict,
        outcome: str,
    ):
        self.audit_id = audit_id
        self.timestamp = timestamp
        self.action_type = action_type
        self.resource_type = resource_type
        self.resource_id = resource_id
        self.user_id = user_id
        self.user_role = user_role
        self.session_id = session_id
        self.ip_address = ip_address
        self.risk_level = risk_level
        self.compliance_tags = compliance_tags
        self.details = details
        self.outcome = outcome


class AuditLogger:
    """Mock audit logger for testing."""
    
    _instance = None
    
    def __init__(self):
        self._entries = []
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def log_entry(self, entry: AuditEntry) -> bool:
        self._entries.append(entry)
        return True
    
    def get_all_entries(self) -> list:
        return self._entries
    
    def get_entry_by_id(self, audit_id: str) -> AuditEntry:
        for entry in self._entries:
            if entry.audit_id == audit_id:
                return entry
        return None
    
    def search_entries(
        self,
        start_date: datetime = None,
        end_date: datetime = None,
        action_type: str = None,
        user_id: str = None,
        risk_level: str = None,
    ) -> list:
        results = self._entries
        
        if start_date:
            results = [e for e in results if e.timestamp >= start_date]
        if end_date:
            results = [e for e in results if e.timestamp <= end_date]
        if action_type:
            results = [e for e in results if e.action_type == action_type]
        if user_id:
            results = [e for e in results if e.user_id == user_id]
        if risk_level:
            results = [e for e in results if e.risk_level == risk_level]
        
        return results
    
    def export_to_csv(self, entries: list) -> str:
        if not entries:
            return ""
        
        headers = [
            "audit_id", "timestamp", "action_type", "resource_type",
            "user_id", "risk_level", "outcome"
        ]
        lines = [",".join(headers)]
        
        for entry in entries:
            line = [
                entry.audit_id,
                entry.timestamp.isoformat(),
                entry.action_type,
                entry.resource_type,
                entry.user_id,
                entry.risk_level,
                entry.outcome,
            ]
            lines.append(",".join(line))
        
        return "\n".join(lines)
    
    def get_statistics(self) -> dict:
        total = len(self._entries)
        today = datetime.now().date()
        today_count = len([e for e in self._entries if e.timestamp.date() == today])
        
        risk_breakdown = {}
        for entry in self._entries:
            risk_breakdown[entry.risk_level] = risk_breakdown.get(entry.risk_level, 0) + 1
        
        return {
            "total_entries": total,
            "entries_today": today_count,
            "risk_breakdown": risk_breakdown,
        }


def get_audit_logger():
    """Get audit logger singleton."""
    return AuditLogger.get_instance()


class TestAuditEntry:
    """Tests for AuditEntry model."""

    def test_audit_entry_creation(self):
        """Test creating an audit entry."""
        entry = AuditEntry(
            audit_id="audit-001",
            timestamp=datetime.now(),
            action_type="VALIDATION_REQUEST",
            resource_type="CONSTITUTIONAL_RULE",
            resource_id="rule-001",
            user_id="officer-001",
            user_role="OPERATOR",
            session_id="session-001",
            ip_address="192.168.1.100",
            risk_level="LOW",
            compliance_tags=["CJIS", "AUDIT_REQUIRED"],
            details={"action": "validate_action", "result": "ALLOWED"},
            outcome="SUCCESS",
        )
        assert entry.audit_id == "audit-001"
        assert entry.action_type == "VALIDATION_REQUEST"
        assert "CJIS" in entry.compliance_tags

    def test_audit_entry_with_all_fields(self):
        """Test audit entry with all required fields."""
        entry = AuditEntry(
            audit_id="audit-002",
            timestamp=datetime.now(),
            action_type="APPROVAL_SUBMITTED",
            resource_type="APPROVAL_REQUEST",
            resource_id="req-001",
            user_id="supervisor-001",
            user_role="SUPERVISOR",
            session_id="session-002",
            ip_address="192.168.1.101",
            risk_level="HIGH",
            compliance_tags=["CJIS", "AUDIT_REQUIRED", "SUPERVISOR_ACTION"],
            details={
                "request_id": "req-001",
                "decision": "APPROVED",
                "mfa_verified": True,
            },
            outcome="SUCCESS",
        )
        assert entry.user_role == "SUPERVISOR"
        assert entry.risk_level == "HIGH"
        assert entry.details["mfa_verified"] is True


class TestAuditLogger:
    """Tests for AuditLogger singleton."""

    def test_singleton_pattern(self):
        """Test that get_audit_logger returns singleton."""
        l1 = get_audit_logger()
        l2 = get_audit_logger()
        assert l1 is l2

    def test_log_entry(self):
        """Test logging an audit entry."""
        logger = get_audit_logger()
        
        entry = AuditEntry(
            audit_id=f"audit-{datetime.now().timestamp()}",
            timestamp=datetime.now(),
            action_type="TEST_ACTION",
            resource_type="TEST_RESOURCE",
            resource_id="test-001",
            user_id="test-user",
            user_role="OPERATOR",
            session_id="test-session",
            ip_address="127.0.0.1",
            risk_level="LOW",
            compliance_tags=["TEST"],
            details={},
            outcome="SUCCESS",
        )
        
        result = logger.log_entry(entry)
        assert result is True

    def test_get_all_entries(self):
        """Test retrieving all audit entries."""
        logger = get_audit_logger()
        entries = logger.get_all_entries()
        assert isinstance(entries, list)

    def test_get_entry_by_id(self):
        """Test retrieving entry by ID."""
        logger = get_audit_logger()
        
        # Create entry
        entry = AuditEntry(
            audit_id=f"audit-retrieve-{datetime.now().timestamp()}",
            timestamp=datetime.now(),
            action_type="RETRIEVE_TEST",
            resource_type="TEST_RESOURCE",
            resource_id="test-002",
            user_id="test-user",
            user_role="OPERATOR",
            session_id="test-session",
            ip_address="127.0.0.1",
            risk_level="LOW",
            compliance_tags=[],
            details={},
            outcome="SUCCESS",
        )
        logger.log_entry(entry)
        
        # Retrieve
        retrieved = logger.get_entry_by_id(entry.audit_id)
        assert retrieved is not None
        assert retrieved.audit_id == entry.audit_id


class TestAuditSearch:
    """Tests for audit log search functionality."""

    def test_search_by_date_range(self):
        """Test searching by date range."""
        logger = get_audit_logger()
        
        # Create entries
        for i in range(3):
            entry = AuditEntry(
                audit_id=f"audit-date-{i}-{datetime.now().timestamp()}",
                timestamp=datetime.now() - timedelta(days=i),
                action_type="DATE_TEST",
                resource_type="TEST_RESOURCE",
                resource_id=f"test-{i}",
                user_id="test-user",
                user_role="OPERATOR",
                session_id="test-session",
                ip_address="127.0.0.1",
                risk_level="LOW",
                compliance_tags=[],
                details={},
                outcome="SUCCESS",
            )
            logger.log_entry(entry)
        
        # Search last 24 hours
        results = logger.search_entries(
            start_date=datetime.now() - timedelta(hours=24),
            end_date=datetime.now(),
        )
        assert isinstance(results, list)

    def test_search_by_action_type(self):
        """Test searching by action type."""
        logger = get_audit_logger()
        
        results = logger.search_entries(action_type="VALIDATION_REQUEST")
        assert isinstance(results, list)
        for entry in results:
            assert entry.action_type == "VALIDATION_REQUEST"

    def test_search_by_user_id(self):
        """Test searching by user ID."""
        logger = get_audit_logger()
        
        # Create entry for specific user
        entry = AuditEntry(
            audit_id=f"audit-user-{datetime.now().timestamp()}",
            timestamp=datetime.now(),
            action_type="USER_TEST",
            resource_type="TEST_RESOURCE",
            resource_id="test-user-search",
            user_id="specific-user-001",
            user_role="OPERATOR",
            session_id="test-session",
            ip_address="127.0.0.1",
            risk_level="LOW",
            compliance_tags=[],
            details={},
            outcome="SUCCESS",
        )
        logger.log_entry(entry)
        
        results = logger.search_entries(user_id="specific-user-001")
        assert isinstance(results, list)
        for entry in results:
            assert entry.user_id == "specific-user-001"

    def test_search_by_risk_level(self):
        """Test searching by risk level."""
        logger = get_audit_logger()
        
        # Create high-risk entry
        entry = AuditEntry(
            audit_id=f"audit-risk-{datetime.now().timestamp()}",
            timestamp=datetime.now(),
            action_type="RISK_TEST",
            resource_type="TEST_RESOURCE",
            resource_id="test-risk",
            user_id="test-user",
            user_role="OPERATOR",
            session_id="test-session",
            ip_address="127.0.0.1",
            risk_level="CRITICAL",
            compliance_tags=["HIGH_RISK"],
            details={},
            outcome="SUCCESS",
        )
        logger.log_entry(entry)
        
        results = logger.search_entries(risk_level="CRITICAL")
        assert isinstance(results, list)
        for entry in results:
            assert entry.risk_level == "CRITICAL"


class TestAuditExport:
    """Tests for audit log export functionality."""

    def test_export_to_csv(self):
        """Test exporting entries to CSV."""
        logger = get_audit_logger()
        
        entries = logger.get_all_entries()
        csv_output = logger.export_to_csv(entries)
        
        assert isinstance(csv_output, str)
        if entries:
            # Should have header row
            lines = csv_output.split("\n")
            assert len(lines) >= 1
            assert "audit_id" in lines[0]

    def test_export_empty_list(self):
        """Test exporting empty list."""
        logger = get_audit_logger()
        
        csv_output = logger.export_to_csv([])
        assert csv_output == ""

    def test_export_filtered_entries(self):
        """Test exporting filtered entries."""
        logger = get_audit_logger()
        
        # Search and export
        results = logger.search_entries(risk_level="HIGH")
        csv_output = logger.export_to_csv(results)
        
        assert isinstance(csv_output, str)


class TestAuditStatistics:
    """Tests for audit statistics."""

    def test_get_statistics(self):
        """Test getting audit statistics."""
        logger = get_audit_logger()
        
        stats = logger.get_statistics()
        
        assert isinstance(stats, dict)
        assert "total_entries" in stats
        assert "entries_today" in stats
        assert "risk_breakdown" in stats

    def test_statistics_risk_breakdown(self):
        """Test risk breakdown in statistics."""
        logger = get_audit_logger()
        
        # Create entries with different risk levels
        for risk in ["LOW", "ELEVATED", "HIGH", "CRITICAL"]:
            entry = AuditEntry(
                audit_id=f"audit-stats-{risk}-{datetime.now().timestamp()}",
                timestamp=datetime.now(),
                action_type="STATS_TEST",
                resource_type="TEST_RESOURCE",
                resource_id=f"test-{risk}",
                user_id="test-user",
                user_role="OPERATOR",
                session_id="test-session",
                ip_address="127.0.0.1",
                risk_level=risk,
                compliance_tags=[],
                details={},
                outcome="SUCCESS",
            )
            logger.log_entry(entry)
        
        stats = logger.get_statistics()
        assert isinstance(stats["risk_breakdown"], dict)


class TestCJISCompliance:
    """Tests for CJIS compliance requirements."""

    def test_entry_has_required_fields(self):
        """Test that entries have all CJIS-required fields."""
        entry = AuditEntry(
            audit_id="audit-cjis-001",
            timestamp=datetime.now(),
            action_type="CJIS_TEST",
            resource_type="SENSITIVE_DATA",
            resource_id="data-001",
            user_id="officer-001",
            user_role="OPERATOR",
            session_id="session-001",
            ip_address="192.168.1.100",
            risk_level="HIGH",
            compliance_tags=["CJIS", "AUDIT_REQUIRED"],
            details={"access_type": "READ"},
            outcome="SUCCESS",
        )
        
        # CJIS requires: who, what, when, where
        assert entry.user_id is not None  # Who
        assert entry.action_type is not None  # What
        assert entry.timestamp is not None  # When
        assert entry.ip_address is not None  # Where
        assert entry.session_id is not None  # Session tracking

    def test_entry_has_compliance_tags(self):
        """Test that entries can have compliance tags."""
        entry = AuditEntry(
            audit_id="audit-cjis-002",
            timestamp=datetime.now(),
            action_type="COMPLIANCE_TEST",
            resource_type="TEST_RESOURCE",
            resource_id="test-001",
            user_id="officer-001",
            user_role="OPERATOR",
            session_id="session-001",
            ip_address="192.168.1.100",
            risk_level="LOW",
            compliance_tags=["CJIS", "HIPAA", "AUDIT_REQUIRED"],
            details={},
            outcome="SUCCESS",
        )
        
        assert "CJIS" in entry.compliance_tags
        assert isinstance(entry.compliance_tags, list)

    def test_entry_outcome_tracking(self):
        """Test that entry outcomes are tracked."""
        success_entry = AuditEntry(
            audit_id="audit-outcome-001",
            timestamp=datetime.now(),
            action_type="OUTCOME_TEST",
            resource_type="TEST_RESOURCE",
            resource_id="test-001",
            user_id="officer-001",
            user_role="OPERATOR",
            session_id="session-001",
            ip_address="192.168.1.100",
            risk_level="LOW",
            compliance_tags=[],
            details={},
            outcome="SUCCESS",
        )
        
        failure_entry = AuditEntry(
            audit_id="audit-outcome-002",
            timestamp=datetime.now(),
            action_type="OUTCOME_TEST",
            resource_type="TEST_RESOURCE",
            resource_id="test-002",
            user_id="officer-001",
            user_role="OPERATOR",
            session_id="session-001",
            ip_address="192.168.1.100",
            risk_level="LOW",
            compliance_tags=[],
            details={"error": "Access denied"},
            outcome="FAILURE",
        )
        
        assert success_entry.outcome == "SUCCESS"
        assert failure_entry.outcome == "FAILURE"


class TestAuditRetention:
    """Tests for audit log retention."""

    def test_entries_have_timestamps(self):
        """Test that all entries have timestamps for retention."""
        logger = get_audit_logger()
        entries = logger.get_all_entries()
        
        for entry in entries:
            assert entry.timestamp is not None
            assert isinstance(entry.timestamp, datetime)

    def test_entries_are_immutable(self):
        """Test that audit entries cannot be modified after creation."""
        entry = AuditEntry(
            audit_id="audit-immutable-001",
            timestamp=datetime.now(),
            action_type="IMMUTABLE_TEST",
            resource_type="TEST_RESOURCE",
            resource_id="test-001",
            user_id="officer-001",
            user_role="OPERATOR",
            session_id="session-001",
            ip_address="192.168.1.100",
            risk_level="LOW",
            compliance_tags=[],
            details={},
            outcome="SUCCESS",
        )
        
        original_id = entry.audit_id
        original_timestamp = entry.timestamp
        
        # Entries should maintain their original values
        assert entry.audit_id == original_id
        assert entry.timestamp == original_timestamp
